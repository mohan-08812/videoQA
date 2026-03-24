"""
models.py – Lazy-loaded AI model singletons
Loads Whisper and BLIP only once on first use to avoid repeated startup cost.
"""

import os
import time
import torch
from dotenv import load_dotenv

load_dotenv()

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")   # base = fast, 140MB
_whisper = None
_blip_processor = None
_blip_model = None
_model_status = {
    "whisper": "not_loaded",   # not_loaded | loading | ready | error
    "blip":    "not_loaded",
    "whisper_load_time": None,
    "blip_load_time": None,
}

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
        model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        _whisper = _FasterWhisperWrapper(model)
        elapsed = round(time.time() - t0, 1)
        _model_status["whisper"] = "ready"
        _model_status["whisper_load_time"] = elapsed
        print(f"[VideoQA] faster-whisper-{WHISPER_MODEL_SIZE} loaded in {elapsed}s ✓")
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
        print(f"[VideoQA] BLIP-base loaded on {device} in {elapsed}s ✓")
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


# ── Session Store ────────────────────────────────────────────
# Maps session_id → { transcript, visuals, video_path, transcript_lines }
_sessions: dict = {}

def get_session_store() -> dict:
    return _sessions

def save_session(session_id: str, data: dict):
    _sessions[session_id] = data

def get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)

