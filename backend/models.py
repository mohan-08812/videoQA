"""
models.py – Lazy-loaded AI model singletons + disk-persistent session store
Loads Whisper and BLIP only once on first use to avoid repeated startup cost.
Sessions are persisted to disk as JSON so they survive server restarts.
"""

import os
import json
import time
import torch
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")   # small = better accuracy, still fast
_whisper = None
_blip_processor = None
_blip_model = None
_model_status = {
    "whisper": "not_loaded",   # not_loaded | loading | ready | error
    "blip":    "not_loaded",
    "whisper_load_time": None,
    "blip_load_time": None,
}

# ── Session Storage Paths ─────────────────────────────────────
# Sessions are saved to disk so they survive server restarts/reloads
_SESSIONS_DIR = Path("uploads")   # sessions stored inside uploads/<session_id>/session.json
_SESSIONS_DIR.mkdir(exist_ok=True)


# ── Whisper ─────────────────────────────────────────────────
class _FasterWhisperWrapper:
    """Wraps faster-whisper to match openai-whisper's transcribe() output format."""
    def __init__(self, model):
        self._model = model

    def transcribe(self, audio_path, language=None, word_timestamps=False, **kwargs):
        segments_iter, info = self._model.transcribe(
            audio_path,
            language=language,
            word_timestamps=word_timestamps,
            beam_size=5,               # good balance of speed and accuracy
            vad_filter=True,           # skip silent segments -> faster
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        segments = []
        full_text_parts = []
        for seg in segments_iter:
            segments.append({
                "start": seg.start,
                "end":   seg.end,
                "text":  seg.text.strip(),
            })
            full_text_parts.append(seg.text.strip())
        return {
            "text": " ".join(full_text_parts),
            "segments": segments,
        }

def get_whisper():
    """Returns a loaded faster-whisper model wrapped in openai-whisper-compatible API."""
    global _whisper, _model_status
    if _whisper is None:
        _model_status["whisper"] = "loading"
        t0 = time.time()
        from faster_whisper import WhisperModel
        print(f"[VideoQA] Loading faster-whisper-{WHISPER_MODEL_SIZE}...")
        model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device="cpu",
            compute_type="int8",       # int8 quantization: 2x faster, minimal accuracy loss
            cpu_threads=max(4, os.cpu_count() or 4),  # use all available cores
            num_workers=1,
        )
        _whisper = _FasterWhisperWrapper(model)
        elapsed = round(time.time() - t0, 1)
        _model_status["whisper"] = "ready"
        _model_status["whisper_load_time"] = elapsed
        print(f"[VideoQA] faster-whisper-{WHISPER_MODEL_SIZE} loaded in {elapsed}s OK")
    return _whisper


# ── BLIP Vision Captioning ───────────────────────────────────
def get_blip():
    """Returns (processor, model) for BLIP-base (lazy singleton)."""
    global _blip_processor, _blip_model, _model_status
    if _blip_model is None:
        _model_status["blip"] = "loading"
        t0 = time.time()
        from transformers import BlipProcessor, BlipForConditionalGeneration
        # Use blip-base (~440MB) instead of blip-large (~900MB) — ~3× faster on CPU
        model_name = "Salesforce/blip-image-captioning-base"
        print(f"[VideoQA] Loading BLIP-base...")
        _blip_processor = BlipProcessor.from_pretrained(model_name)
        _blip_model = BlipForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _blip_model = _blip_model.to(device)
        _blip_model.eval()
        elapsed = round(time.time() - t0, 1)
        _model_status["blip"] = "ready"
        _model_status["blip_load_time"] = elapsed
        print(f"[VideoQA] BLIP-base loaded on {device} in {elapsed}s OK")
    return _blip_processor, _blip_model


def get_model_status() -> dict:
    """Returns current load status for all models — used by /status endpoint."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return {
        "device": device,
        "whisper": {
            "model":  WHISPER_MODEL_SIZE,
            "status": _model_status["whisper"],
            "load_time_sec": _model_status["whisper_load_time"],
        },
        "blip": {
            "model":  "blip-image-captioning-base",
            "status": _model_status["blip"],
            "load_time_sec": _model_status["blip_load_time"],
        },
    }


# ── Session Store (Disk-Persistent) ──────────────────────────
# Sessions are saved to uploads/<session_id>/session.json
# This means they survive server restarts and reloads.
# In-memory cache for speed (avoid re-reading disk on every request).
_session_cache: dict = {}


def _session_path(session_id: str) -> Path:
    return _SESSIONS_DIR / session_id / "session.json"


def save_session(session_id: str, data: dict):
    """Save session data to in-memory cache AND disk."""
    # Remove non-serializable objects before saving to disk
    serializable = {}
    for k, v in data.items():
        if k == "segments":
            # segments contain plain dicts — safe
            serializable[k] = v
        elif isinstance(v, (str, int, float, bool, list, dict, type(None))):
            serializable[k] = v
        else:
            serializable[k] = str(v)

    _session_cache[session_id] = data  # keep full data in memory cache

    try:
        path = _session_path(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[VideoQA] WARNING: Could not persist session {session_id[:8]} to disk: {e}")


def get_session(session_id: str) -> dict | None:
    """Get session: check in-memory cache first, then disk."""
    if not session_id:
        return None

    # 1. Fast path: in-memory cache
    if session_id in _session_cache:
        return _session_cache[session_id]

    # 2. Slow path: load from disk (e.g. after server restart)
    path = _session_path(session_id)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            _session_cache[session_id] = data
            print(f"[VideoQA] Session {session_id[:8]} restored from disk OK")
            return data
        except Exception as e:
            print(f"[VideoQA] WARNING: Could not load session {session_id[:8]} from disk: {e}")

    return None


def get_session_store() -> dict:
    return _session_cache
