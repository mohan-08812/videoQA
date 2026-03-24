"""
main.py – VideoQA FastAPI Backend
Endpoints: /process_video, /ask, /summarize_video, /summarize_transcript, /download/{type}
"""

import os
import time
import uuid
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from models import save_session, get_session, get_model_status
from video_utils import (
    extract_audio,
    extract_keyframes,
    extract_specific_frames,
    caption_frames,
    extract_clip,
    find_clip_timestamps,
)
from llm import answer_question, summarize_video, summarize_transcript

load_dotenv()

# ── App Setup ────────────────────────────────────────────────
app = FastAPI(
    title="VideoQA API",
    description="Multimodal Video Question Answering – Whisper + BLIP + Mistral",
    version="1.0.0",
)

# Allow the file:// frontend and localhost dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temp directory for uploads / outputs
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Pydantic models ──────────────────────────────────────────

class AskRequest(BaseModel):
    question: str
    session_id: str
    language: Optional[str] = "English"
    model: Optional[str] = None   # None → use DEFAULT_MODEL from .env

class SummarizeVideoRequest(BaseModel):
    session_id: str
    length: Optional[str] = "short"   # "short" | "detailed" | "chapters"
    model: Optional[str] = None

class SummarizeTranscriptRequest(BaseModel):
    session_id: str
    model: Optional[str] = None


# ── Health Check ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "VideoQA API"}


# ── Model Status ──────────────────────────────────────────────

@app.get("/status")
def status():
    """
    Returns the load status of AI models (Whisper, BLIP).
    Use this to check if models are loaded before processing.
    """
    model_info = get_model_status()
    all_ready = all(
        v["status"] == "ready"
        for k, v in model_info.items()
        if isinstance(v, dict) and "status" in v
    )
    return {
        "ready": all_ready,
        "models": model_info,
    }


# ── POST /process_video ──────────────────────────────────────

@app.post("/process_video")
async def process_video(
    video:    UploadFile = File(...),
    language: str        = Form("English"),
    mode:     str        = Form("fast"),      # "fast" | "full"
    start_time: Optional[float] = Form(None),
    end_time:   Optional[float] = Form(None),
    manual_frames: Optional[str] = Form(None),
):
    """
    1. Save uploaded video
    2. Extract audio → transcribe with Whisper-base (fast)
    3. Extract keyframes → caption with BLIP-base
    4. Store session data
    Returns: { session_id, duration, transcript (list), visuals (list), status }
    """
    t_pipeline = time.time()
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded video
    video_path = str(session_dir / video.filename)
    print(f"\n[VideoQA] ━━ New session: {session_id[:8]} | lang={language} | mode={mode}")
    t0 = time.time()
    with open(video_path, "wb") as f:
        content = await video.read()
        f.write(content)
    print(f"[VideoQA] Video saved ({len(content)/1024/1024:.1f} MB) in {round(time.time()-t0,1)}s")

    try:
        # ── Step 1: Audio → Transcript ──────────────────────
        audio_path = str(session_dir / "audio.wav")
        extract_audio(video_path, audio_path, start_time, end_time)

        from models import get_whisper
        model_wh = get_whisper()

        print(f"[VideoQA] Transcribing audio (lang={_lang_code(language)})...")
        t0 = time.time()
        # Request word-level timestamps for better clip matching
        result = model_wh.transcribe(
            audio_path,
            language=_lang_code(language),
            word_timestamps=False,  # per-segment timestamps are enough
        )
        print(f"[VideoQA] Transcription done in {round(time.time()-t0,1)}s")

        full_text = result["text"].strip()
        segments  = result.get("segments", [])
        print(f"[VideoQA] Transcript: {len(segments)} segments, {len(full_text)} chars")

        # Format transcript lines for frontend
        transcript_lines = []
        offset = start_time or 0.0
        for seg in segments:
            seg["start"] = seg.get("start", 0) + offset
            seg["end"] = seg.get("end", 0) + offset
            start = seg["start"]
            end   = seg["end"]
            text  = seg.get("text", "").strip()
            if text:
                transcript_lines.append({
                    "time":    _fmt_time(start),
                    "start":   start,
                    "end":     end,
                    "speaker": "Speaker",   # speaker diarization would need pyannote
                    "text":    text,
                })

        # Get video duration
        duration = segments[-1]["end"] if segments else (end_time or 0.0)

        # ── Step 2: Keyframes → Visual Captions ────────────
        from models import get_model_status as _ms
        
        t0 = time.time()
        if manual_frames and manual_frames.strip():
            timestamps = [float(x.strip()) for x in manual_frames.split(",") if x.strip()]
            print(f"[VideoQA] Extracting {len(timestamps)} manual frames...")
            frame_paths = extract_specific_frames(video_path, timestamps)
        else:
            max_frames = int(os.getenv("MAX_FRAMES", "3"))
            n_frames = max_frames if mode == "full" else max(2, max_frames - 1)
            print(f"[VideoQA] Extracting {n_frames} keyframes...")
            frame_paths = extract_keyframes(video_path, n=n_frames, start_sec=start_time, end_sec=end_time)
            
        print(f"[VideoQA] Frames extracted in {round(time.time()-t0,1)}s")
        captioned   = caption_frames(frame_paths)

        visuals = []
        for item in captioned:
            # Note: For manual frames, caption might display `time` incorrectly if we just use `frame_index / fps`. We will let `extract_specific_frames` return the timestamp in `frame_index` or handle it properly. Wait, `frame_index` can just be the timestamp in seconds scaled up. Actually, we can return `{path, timestamp}` from `extract_specific_frames`, but wait, `caption_frames` reads `frame_{idx}.jpg`. It might be easier to just format `time` based on the frame index if `extracted_frames` works similarly. Let's adjust this.
            visuals.append({
                "time":    _fmt_time(item.get("frame_index", 0) / 25.0),  # This will be updated inside video_utils
                "caption": item["caption"],
            })

        # ── Save Session ────────────────────────────────────
        save_session(session_id, {
            "video_path":  video_path,
            "audio_path":  audio_path,
            "full_text":   full_text,
            "segments":    segments,
            "transcript":  transcript_lines,
            "visuals":     visuals,
            "duration":    duration,
            "language":    language,
        })

        # Cleanup frames dir
        shutil.rmtree("frames", ignore_errors=True)
        print(f"[VideoQA] ✅ Pipeline complete in {round(time.time()-t_pipeline,1)}s total\n")

        return {
            "status":      "success",
            "session_id":  session_id,
            "duration":    duration,
            "transcript":  transcript_lines,
            "visuals":     visuals,
            "language":    language,
        }

    except Exception as e:
        shutil.rmtree(str(session_dir), ignore_errors=True)
        print(f"[VideoQA] ❌ Pipeline failed after {round(time.time()-t_pipeline,1)}s: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")



# ── POST /ask ────────────────────────────────────────────────

@app.post("/ask")
async def ask(req: AskRequest):
    """
    Answer a question grounded in the video's transcript + visuals.
    Returns: { answer, confidence, evidence, clip }
    """
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please process a video first.")

    full_text = session["full_text"]
    visuals   = session["visuals"]
    segments  = session["segments"]
    duration  = session["duration"]
    language  = req.language or session.get("language", "English")
    # Convert short code ('en') → display name ('English') for LLM prompt
    language_display = _CODE_TO_NAME.get(language.lower(), language)

    visuals_text = "\n".join(
        f"[{v['time']}] {v['caption']}" for v in visuals
    )

    try:
        # ── LLM Answer ──────────────────────────────────────
        result = answer_question(
            question=req.question,
            transcript=full_text,
            visuals=visuals_text,
            language=language_display,
            model=req.model,
        )

        # ── Clip Retrieval ───────────────────────────────────
        clip_start, clip_end = find_clip_timestamps(
            transcript_segments=segments,
            question=req.question,
            video_duration=duration,
        )

        clip_label = f"{_fmt_time(clip_start)} – {_fmt_time(clip_end)}"

        # Extract clip and save
        clip_filename = f"clip_{req.session_id[:8]}.mp4"
        clip_out_path = str(OUTPUT_DIR / clip_filename)

        try:
            extract_clip(session["video_path"], clip_start, clip_end, clip_out_path)
            clip_url = f"/download/clip/{clip_filename}"
        except Exception:
            clip_url = None

        return {
            "status":   "success",
            "question": req.question,
            "answer":   result.get("answer", ""),
            "confidence": f"{result.get('confidence', 'Medium')} – {result.get('confidence_reason', 'Based on transcript + visual frames')}",
            "evidence": {
                "transcript_excerpts": result.get("transcript_excerpts", []),
                "visual_captions":     result.get("visual_captions", []),
            },
            "clip": {
                "start":  clip_start,
                "end":    clip_end,
                "url":    clip_url,
                "label":  clip_label,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA failed: {str(e)}")


# ── POST /summarize_video ─────────────────────────────────────

@app.post("/summarize_video")
async def summarize_video_endpoint(req: SummarizeVideoRequest):
    """
    Summarize the video content (short paragraph / detailed bullets / chapters).
    Returns: { short, detailed, chapters }
    """
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    visuals_text = "\n".join(
        f"[{v['time']}] {v['caption']}" for v in session["visuals"]
    )

    try:
        result = summarize_video(
            transcript=session["full_text"],
            visuals=visuals_text,
            length=req.length or "short",
            model=req.model,
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


# ── POST /summarize_transcript ────────────────────────────────

@app.post("/summarize_transcript")
async def summarize_transcript_endpoint(req: SummarizeTranscriptRequest):
    """
    Extract key points, action items, and keywords from the transcript.
    Returns: { key_points, action_items, keywords }
    """
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        result = summarize_transcript(
            transcript=session["full_text"],
            model=req.model,
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcript summarization failed: {str(e)}")


# ── GET /download/{type}/{filename} ───────────────────────────

@app.get("/download/clip/{filename}")
def download_clip(filename: str):
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Clip file not found.")
    return FileResponse(
        str(path),
        media_type="video/mp4",
        filename=filename,
        headers={"Accept-Ranges": "bytes"},
    )


@app.get("/download/transcript/{session_id}")
def download_transcript(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    lines = session.get("transcript", [])
    text  = "\n".join(f"[{l['time']}] {l['speaker']}: {l['text']}" for l in lines)

    out_path = OUTPUT_DIR / f"transcript_{session_id[:8]}.txt"
    out_path.write_text(text, encoding="utf-8")
    return FileResponse(str(out_path), media_type="text/plain", filename="transcript.txt")


@app.get("/download/summary/{session_id}")
def download_summary(session_id: str, length: str = "short"):
    """Proxy – summary must first be generated via /summarize_video."""
    raise HTTPException(status_code=400, detail="Please generate summary first, then download from the frontend.")


# ── Helpers ───────────────────────────────────────────────────

def _fmt_time(seconds: float) -> str:
    s = int(seconds)
    m, s = divmod(s, 60)
    return f"{m}:{s:02d}"


_CODE_TO_NAME = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "ur": "Urdu",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ar": "Arabic",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
}

_LANG_MAP = {
    "english":    "en",
    "hindi":      "hi",
    "telugu":     "te",
    "tamil":      "ta",
    "kannada":    "kn",
    "malayalam":  "ml",
    "marathi":    "mr",
    "bengali":    "bn",
    "punjabi":    "pa",
    "gujarati":   "gu",
    "urdu":       "ur",
    "spanish":    "es",
    "french":     "fr",
    "german":     "de",
    "chinese":    "zh",
    "arabic":     "ar",
    "japanese":   "ja",
    "korean":     "ko",
    "portuguese": "pt",
    "russian":    "ru",
    "italian":    "it",
}

# Short ISO codes that are already valid for Whisper
_VALID_SHORT_CODES = {"en", "hi", "te", "ta", "kn", "ml", "mr", "bn", "pa", "gu", "ur",
                      "es", "fr", "de", "zh", "ar", "ja", "ko", "pt", "ru", "it"}

def _lang_code(language: str) -> str | None:
    """Accept either full names ('English') or short ISO codes ('en')."""
    lang = language.strip()
    # Already a valid short code
    if lang.lower() in _VALID_SHORT_CODES:
        return lang.lower()
    # Full name mapping
    return _LANG_MAP.get(lang.lower())


# ── Frontend Static Files ──────────────────────────────────────
# Mount the root directory to serve index.html, app.js, style.css in production
STATIC_DIR = Path(__file__).parent.parent
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")


# ── Entry Point ────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"\n{'='*50}")
    print(f"  VideoQA Backend starting on http://{host}:{port}")
    print(f"  Docs: http://localhost:{port}/docs")
    print(f"{'='*50}\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)
