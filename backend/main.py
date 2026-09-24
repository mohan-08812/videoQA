"""
main.py – VideoQA FastAPI Backend
Endpoints: /process_video, /ask, /summarize_video, /summarize_transcript, /download/{type}

Windows fixes applied:
  - WinError 32: yt-dlp uses nopart=True + post-download file scan with retry
  - Filename safety: Path(video.filename).name strips unsafe paths
  - Async: yt-dlp wrapped in asyncio.to_thread() (non-blocking)
  - Frames: session-scoped directories (no cross-session conflicts)
  - Sessions: disk-persistent (survive server restarts)
"""

import os
import time
import uuid
import shutil
import asyncio
from pathlib import Path
from typing import Optional
import yt_dlp

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
from llm import answer_question, summarize_video, summarize_transcript, get_rate_limit_status
from gemini_pipeline import run_gemini_pipeline

load_dotenv()

# ── App Setup ────────────────────────────────────────────────
app = FastAPI(
    title="VideoQA API",
    description="Multimodal Video Question Answering – Whisper + BLIP + LLM",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Startup: pre-warm models ──────────────────────────────────
@app.on_event("startup")
async def _warmup_models():
    """
    Pre-load Whisper and BLIP in background threads at startup
    so the first request is not slow.
    """
    async def _load():
        try:
            await asyncio.to_thread(_do_warmup)
        except Exception as e:
            print(f"[VideoQA] WARNING: Model warmup failed: {e}")

    async def _do_warmup_async():
        await _load()

    asyncio.create_task(_do_warmup_async())

def _do_warmup():
    from models import get_whisper, get_blip
    print("[VideoQA] Pre-warming models in background...")
    get_whisper()
    get_blip()
    print("[VideoQA] Models warm and ready!")


# ── Pydantic models ──────────────────────────────────────────

class AskRequest(BaseModel):
    question: str
    session_id: str
    language: Optional[str] = "English"
    model: Optional[str] = None

class SummarizeVideoRequest(BaseModel):
    session_id: str
    length: Optional[str] = "short"
    model: Optional[str] = None

class SummarizeTranscriptRequest(BaseModel):
    session_id: str
    model: Optional[str] = None


class GeminiAskRequest(BaseModel):
    question: str
    video_url: Optional[str] = None          # YouTube or direct video URL
    language: Optional[str] = "English"
    model: Optional[str] = "gemini-3.6-flash"


# ── Health Check ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "VideoQA API", "version": "2.1.0"}


@app.get("/rate_limit_status")
def rate_limit_status():
    """Returns current LLM rate-limit and quota status for monitoring."""
    return get_rate_limit_status()


# ── Model Status ──────────────────────────────────────────────

@app.get("/status")
def status():
    """Returns the load status of AI models (Whisper, BLIP)."""
    model_info = get_model_status()
    all_ready = all(
        v["status"] == "ready"
        for k, v in model_info.items()
        if isinstance(v, dict) and "status" in v
    )
    return {"ready": all_ready, "models": model_info}


# ── POST /process_video ──────────────────────────────────────

@app.post("/process_video")
async def process_video(
    video:         Optional[UploadFile] = File(None),
    video_url:     Optional[str]        = Form(None),
    language:      str                  = Form("English"),
    mode:          str                  = Form("fast"),
    start_time:    Optional[float]      = Form(None),
    end_time:      Optional[float]      = Form(None),
    manual_frames: Optional[str]        = Form(None),
):
    """
    1. Save/download the video
    2. Extract audio -> transcribe with Whisper
    3. Extract keyframes -> caption with BLIP (batched)
    4. Store session data to disk
    Returns: { session_id, duration, transcript, visuals, status }
    """
    t_pipeline = time.time()
    session_id  = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    frames_dir  = str(session_dir / "frames")

    if not video and not video_url:
        raise HTTPException(
            status_code=400,
            detail="Please provide either a video file upload or a video URL.",
        )

    print(f"\n[VideoQA] ── New session: {session_id[:8]} | lang={language} | mode={mode}")
    t0 = time.time()

    # ── Step 0: Get Video ────────────────────────────────────
    if video_url:
        video_path = await _download_video(video_url, session_dir)
        print(f"[VideoQA] Video ready in {round(time.time()-t0,1)}s")
    else:
        # Safe filename extraction (strips Windows path separators)
        safe_name = Path(video.filename).name if video.filename else "uploaded_video.mp4"
        video_path = str(session_dir / safe_name)
        content = await video.read()
        with open(video_path, "wb") as f:
            f.write(content)
        print(f"[VideoQA] Video saved ({len(content)/1024/1024:.1f} MB) in {round(time.time()-t0,1)}s")

    try:
        # ── Step 1: Audio -> Transcript ──────────────────────
        audio_path = str(session_dir / "audio.wav")
        extract_audio(video_path, audio_path, start_time, end_time)

        from models import get_whisper
        model_wh = get_whisper()

        lang_code = _lang_code(language)
        print(f"[VideoQA] Transcribing (lang={lang_code}, model=whisper-{os.getenv('WHISPER_MODEL','small')})...")
        t0 = time.time()
        result = model_wh.transcribe(audio_path, language=lang_code, word_timestamps=False)
        print(f"[VideoQA] Transcription done in {round(time.time()-t0,1)}s")

        full_text = result["text"].strip()
        segments  = result.get("segments", [])
        print(f"[VideoQA] Transcript: {len(segments)} segments, {len(full_text)} chars")

        # Format transcript for frontend
        transcript_lines = []
        offset = start_time or 0.0
        for seg in segments:
            seg["start"] = seg.get("start", 0) + offset
            seg["end"]   = seg.get("end", 0) + offset
            text = seg.get("text", "").strip()
            if text:
                transcript_lines.append({
                    "time":    _fmt_time(seg["start"]),
                    "start":   seg["start"],
                    "end":     seg["end"],
                    "speaker": "Speaker",
                    "text":    text,
                })

        duration = segments[-1]["end"] if segments else (end_time or 0.0)

        # ── Step 2: Keyframes -> Visual Captions ────────────
        t0 = time.time()
        if manual_frames and manual_frames.strip():
            timestamps = [float(x.strip()) for x in manual_frames.split(",") if x.strip()]
            print(f"[VideoQA] Extracting {len(timestamps)} manual frames...")
            frame_paths = extract_specific_frames(video_path, timestamps, frames_dir=frames_dir)
        else:
            max_frames = int(os.getenv("MAX_FRAMES", "3"))
            # In fast mode use 2 frames, full mode uses all
            n_frames = max_frames if mode == "full" else max(2, max_frames - 1)
            print(f"[VideoQA] Extracting {n_frames} keyframes (mode={mode})...")
            frame_paths = extract_keyframes(
                video_path, n=n_frames,
                start_sec=start_time, end_sec=end_time,
                frames_dir=frames_dir,
            )

        print(f"[VideoQA] Frames extracted in {round(time.time()-t0,1)}s")
        captioned = caption_frames(frame_paths)

        visuals = []
        for item in captioned:
            ts = item.get("timestamp_sec", 0.0)
            visuals.append({
                "time":    _fmt_time(ts),
                "caption": item["caption"],
            })

        # ── Save Session ─────────────────────────────────────
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

        print(f"[VideoQA] Pipeline complete in {round(time.time()-t_pipeline,1)}s total\n")

        return {
            "status":     "success",
            "session_id": session_id,
            "duration":   duration,
            "transcript": transcript_lines,
            "visuals":    visuals,
            "language":   language,
        }

    except HTTPException:
        shutil.rmtree(str(session_dir), ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(str(session_dir), ignore_errors=True)
        print(f"[VideoQA] FAILED: Pipeline failed after {round(time.time()-t_pipeline,1)}s: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# ── Video Download Helper (async, non-blocking) ───────────────

async def _download_video(video_url: str, session_dir: Path) -> str:
    """
    Download video via yt-dlp. Runs in a thread to avoid blocking the async event loop.
    Robust Windows fix: nopart=True + retry loop + directory scan fallback.
    """
    def _do_download():
        browser = os.getenv("YOUTUBE_BROWSER", "chrome")
        ydl_opts = {
            'format':     'best[ext=mp4]/best',
            'outtmpl':    str(session_dir / 'downloaded_video.%(ext)s'),
            'quiet':      True,
            'no_warnings': True,
            'nopart':     True,   # <- KEY FIX: no .part temp file, writes directly to final name
            'extractor_args': {'youtube': ['player_client=android,tv,ios']},
        }

        # Cookie setup
        cookie_file = Path("cookies.txt")
        env_cookies = os.getenv("YOUTUBE_COOKIES_SECRET")
        if env_cookies and not cookie_file.exists():
            try:
                cookie_file.write_text(env_cookies, encoding="utf-8")
            except Exception:
                pass

        if cookie_file.exists():
            ydl_opts['cookiefile'] = str(cookie_file)
        elif browser and browser.lower() not in ("none", "false"):
            ydl_opts['cookiesfrombrowser'] = (browser,)

        def _run_ydl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                ext  = info.get('ext', 'mp4')
                return ext

        # Attempt 1: with cookies
        try:
            ext = _run_ydl()
        except Exception as e:
            if 'cookiesfrombrowser' in ydl_opts:
                print(f"[VideoQA] Cookie extraction failed ({e}), retrying without cookies...")
                del ydl_opts['cookiesfrombrowser']
                ext = _run_ydl()
            else:
                raise

        # ── Windows file-lock fix: scan session_dir for the downloaded file ──
        # Even with nopart=True, Windows may need a moment to release the file handle.
        expected = session_dir / f"downloaded_video.{ext}"
        video_extensions = {'.mp4', '.webm', '.mkv', '.avi', '.mov', '.m4v', '.flv', '.ts'}

        for attempt in range(10):
            if expected.exists() and expected.stat().st_size > 0:
                return str(expected)
            # Scan for any valid video file in the session directory
            for f in session_dir.iterdir():
                if f.suffix.lower() in video_extensions and f.stat().st_size > 0:
                    # Rename to standard name if it isn't already
                    if f != expected:
                        try:
                            f.rename(expected)
                            return str(expected)
                        except Exception:
                            pass
                    return str(f)
            time.sleep(0.3)

        raise RuntimeError(
            f"Download appeared to complete but the output file was not found in {session_dir}. "
            "This is a Windows file-lock issue. Please try again."
        )

    try:
        return await asyncio.to_thread(_do_download)
    except Exception as e:
        err_msg = str(e)
        is_youtube = "youtube.com" in video_url.lower() or "youtu.be" in video_url.lower()

        if is_youtube and any(kw in err_msg for kw in ("Sign in to confirm", "bot", "nsig", "403")):
            raise HTTPException(
                status_code=400,
                detail=(
                    "YouTube has blocked the download (bot detection). "
                    "Try uploading the video file directly instead, OR export your YouTube cookies "
                    "using the 'Get cookies.txt LOCALLY' browser extension and save as "
                    "'cookies.txt' in the backend/ folder."
                ),
            )
        elif "huggingface.co" in video_url.lower():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Hugging Face download failed — the file may be in a private repository. "
                    "Please download the video manually and upload the file directly."
                ),
            )
        elif "WinError 32" in err_msg or "used by another process" in err_msg:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Windows file lock error during download. Please try again — "
                    "this is a transient issue that usually resolves on retry."
                ),
            )
        else:
            raise HTTPException(status_code=400, detail=f"Download failed: {err_msg}")


# ── POST /ask_gemini (new Gemini 1.5 Flash pipeline) ────────────────────────

@app.post("/ask_gemini")
async def ask_gemini_endpoint(
    video: Optional[UploadFile] = File(None),
    video_url: Optional[str]   = Form(None),
    question:  str              = Form(...),
    language:  str              = Form("English"),
    model:     str              = Form("gemini-3.6-flash"),
):
    """
    Gemini 1.5 Flash multimodal pipeline.
    - Accepts a YouTube URL (video_url) OR a direct file upload (video).
    - Downloads 480p MP4 via yt-dlp OR saves the upload to a temp file.
    - Uploads the video to the Google File API.
    - Answers the question using gemini-1.5-flash via the File API reference.
    - Cleans up local temp file and File API object after responding.
    """
    if not video and not video_url:
        raise HTTPException(
            status_code=400,
            detail="Provide either a video file upload or a video_url.",
        )

    video_bytes: Optional[bytes] = None
    original_filename = "video.mp4"

    if video:
        video_bytes = await video.read()
        original_filename = Path(video.filename).name if video.filename else "video.mp4"

    try:
        result = await run_gemini_pipeline(
            question=question,
            video_url=video_url or None,
            video_bytes=video_bytes,
            original_filename=original_filename,
            language=language,
            model_name=model,
        )
        return {
            "status":       "success",
            "question":     question,
            "answer":       result["answer"],
            "model":        result["model"],
            "source":       result["source"],
            "file_api_uri": result["file_api_uri"],
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gemini pipeline failed: {exc}")


# ── POST /ask ────────────────────────────────────────────────

@app.post("/ask")
async def ask(req: AskRequest):
    """Answer a question grounded in the video's transcript + visuals."""
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please process a video first, or the session may have expired.",
        )

    full_text = session["full_text"]
    visuals   = session["visuals"]
    segments  = session["segments"]
    duration  = session["duration"]
    language  = req.language or session.get("language", "English")
    language_display = _CODE_TO_NAME.get(language.lower(), language)

    visuals_text = "\n".join(f"[{v['time']}] {v['caption']}" for v in visuals)

    try:
        result = answer_question(
            question=req.question,
            transcript=full_text,
            visuals=visuals_text,
            language=language_display,
            model=req.model,
        )

        clip_start, clip_end = find_clip_timestamps(
            transcript_segments=segments,
            question=req.question,
            video_duration=duration,
        )
        clip_label    = f"{_fmt_time(clip_start)} – {_fmt_time(clip_end)}"
        clip_filename = f"clip_{req.session_id[:8]}.mp4"
        clip_out_path = str(OUTPUT_DIR / clip_filename)

        try:
            extract_clip(session["video_path"], clip_start, clip_end, clip_out_path)
            clip_url = f"/download/clip/{clip_filename}"
        except Exception as clip_err:
            print(f"[VideoQA] WARNING: Clip extraction failed: {clip_err}")
            clip_url = None

        return {
            "status":   "success",
            "question": req.question,
            "answer":   result.get("answer", ""),
            "confidence": (
                f"{result.get('confidence', 'Medium')} – "
                f"{result.get('confidence_reason', 'Based on transcript + visual frames')}"
            ),
            "evidence": {
                "transcript_excerpts": result.get("transcript_excerpts", []),
                "visual_captions":     result.get("visual_captions", []),
            },
            "clip": {
                "start": clip_start,
                "end":   clip_end,
                "url":   clip_url,
                "label": clip_label,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA failed: {str(e)}")


# ── POST /summarize_video ─────────────────────────────────────

@app.post("/summarize_video")
async def summarize_video_endpoint(req: SummarizeVideoRequest):
    """Summarize the video (short / detailed / chapters)."""
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
    """Extract key points, action items, and keywords from the transcript."""
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


# ── GET /download/{type}/{...} ────────────────────────────────

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

    lines    = session.get("transcript", [])
    text     = "\n".join(f"[{l['time']}] {l['speaker']}: {l['text']}" for l in lines)
    out_path = OUTPUT_DIR / f"transcript_{session_id[:8]}.txt"
    out_path.write_text(text, encoding="utf-8")
    return FileResponse(str(out_path), media_type="text/plain", filename="transcript.txt")


@app.get("/download/summary/{session_id}")
def download_summary(session_id: str, length: str = "short"):
    raise HTTPException(
        status_code=400,
        detail="Please generate summary first via /summarize_video, then download from the frontend.",
    )


# ── Helpers ───────────────────────────────────────────────────

def _fmt_time(seconds: float) -> str:
    s = int(seconds)
    m, s = divmod(s, 60)
    return f"{m}:{s:02d}"


_CODE_TO_NAME = {
    "en": "English",  "hi": "Hindi",   "te": "Telugu",  "ta": "Tamil",
    "kn": "Kannada",  "ml": "Malayalam","mr": "Marathi", "bn": "Bengali",
    "pa": "Punjabi",  "gu": "Gujarati", "ur": "Urdu",    "es": "Spanish",
    "fr": "French",   "de": "German",   "zh": "Chinese", "ar": "Arabic",
    "ja": "Japanese", "ko": "Korean",   "pt": "Portuguese","ru": "Russian",
    "it": "Italian",
}

_LANG_MAP = {
    "english": "en",    "hindi": "hi",     "telugu": "te",    "tamil": "ta",
    "kannada": "kn",    "malayalam": "ml", "marathi": "mr",   "bengali": "bn",
    "punjabi": "pa",    "gujarati": "gu",  "urdu": "ur",      "spanish": "es",
    "french": "fr",     "german": "de",    "chinese": "zh",   "arabic": "ar",
    "japanese": "ja",   "korean": "ko",    "portuguese": "pt","russian": "ru",
    "italian": "it",
}

_VALID_SHORT_CODES = set(_LANG_MAP.values())

def _lang_code(language: str) -> str | None:
    lang = language.strip()
    if lang.lower() in _VALID_SHORT_CODES:
        return lang.lower()
    return _LANG_MAP.get(lang.lower())


# ── Frontend Static Files ──────────────────────────────────────
STATIC_DIR = Path(__file__).parent.parent
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")


# ── Entry Point ────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"\n{'='*55}")
    print(f"  VideoQA v2.0 – starting on http://{host}:{port}")
    print(f"  Docs:  http://localhost:{port}/docs")
    print(f"  {'='*55}\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)
