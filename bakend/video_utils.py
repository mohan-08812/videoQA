"""
video_utils.py – Video processing helpers
Covers: audio extraction, smart keyframe sampling, BLIP captioning, clip extraction.
"""

import os
import time
import subprocess
import cv2
import torch
import numpy as np
from PIL import Image

# ── MoviePy import (for clip extraction only – v1.x and v2.x) ──
try:
    from moviepy.editor import VideoFileClip   # moviepy v1.x
except ImportError:
    from moviepy import VideoFileClip          # moviepy v2.x

from models import get_blip

MAX_FRAMES = int(os.getenv("MAX_FRAMES", "3"))
CLIP_DURATION = float(os.getenv("CLIP_DURATION", "30"))


# ── FFMPEG helper ────────────────────────────────────────────

def _get_ffmpeg() -> str:
    """Return path to bundled ffmpeg binary (from imageio_ffmpeg/moviepy)."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"   # fall back to system PATH


# ── Audio ────────────────────────────────────────────────────

def extract_audio(video_path: str, out_path: str = "audio.wav", start_sec: float = None, end_sec: float = None) -> str:
    """
    Extract 16kHz mono WAV audio from video using ffmpeg subprocess.
    Much faster and more reliable than MoviePy's write_audiofile on Windows.
    """
    t0 = time.time()
    print(f"[VideoQA] Extracting audio from {os.path.basename(video_path)}...")
    ffmpeg = _get_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",                   # overwrite output
    ]
    if start_sec is not None:
        cmd.extend(["-ss", str(start_sec)])
    if end_sec is not None:
        duration = end_sec - (start_sec or 0.0)
        cmd.extend(["-t", str(duration)])
    cmd.extend([
        "-i", video_path,       # input video
        "-vn",                  # no video
        "-acodec", "pcm_s16le", # WAV format
        "-ar", "16000",         # 16kHz sample rate (required by Whisper)
        "-ac", "1",             # mono
        out_path,
    ])
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300,            # 5 min timeout
    )
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"ffmpeg audio extraction failed:\n{err}")
    print(f"[VideoQA] Audio extracted in {round(time.time()-t0,1)}s → {out_path}")
    return out_path


# ── Frame Extraction ─────────────────────────────────────────

def _compute_frame_diff(prev: np.ndarray, curr: np.ndarray) -> float:
    """Mean absolute pixel difference between two frames (grayscale)."""
    p = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY).astype(float)
    c = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY).astype(float)
    return float(np.mean(np.abs(p - c)))


def extract_keyframes(video_path: str, n: int = MAX_FRAMES, start_sec: float = None, end_sec: float = None) -> list[str]:
    """
    Smart keyframe extraction:
    1. Sample frames uniformly across the video.
    2. Additionally pick frames with high scene-change score.
    Returns up to `n` unique frame file paths.
    """
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps   = cap.get(cv2.CAP_PROP_FPS) or 25.0

    start_frame = int(start_sec * fps) if start_sec is not None else 0
    end_frame = int(end_sec * fps) if end_sec is not None else total

    saved_paths: list[str] = []
    os.makedirs("frames", exist_ok=True)

    if total <= 0 or start_frame >= end_frame:
        cap.release()
        return saved_paths

    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
    frames_to_process = end_frame - start_frame

    # Uniform sampling indices
    uniform_indices = set(
        start_frame + int(i * frames_to_process / n) for i in range(n)
    )

    prev_frame = None
    frame_scores: list[tuple[float, int, np.ndarray]] = []

    count = start_frame
    while cap.isOpened() and count < end_frame:
        ret, frame = cap.read()
        if not ret:
            break

        if prev_frame is not None:
            score = _compute_frame_diff(prev_frame, frame)
            frame_scores.append((score, count, frame.copy()))
        elif count == start_frame:
            # Always keep first frame
            frame_scores.append((999.0, count, frame.copy()))

        prev_frame = frame
        count += 1

    cap.release()

    if not frame_scores:
        return saved_paths

    # Pick top-n frames by scene-change score, prioritising uniform coverage
    # Combine: add uniform indices to the selection weighted by score
    uniform_frames = []
    scene_frames = []

    # Sort by score descending
    sorted_by_score = sorted(frame_scores, key=lambda x: x[0], reverse=True)

    # Collect top scene-change frames
    selected_indices: set[int] = set()
    for score, idx, frm in sorted_by_score:
        if len(selected_indices) >= n:
            break
        # avoid picking frames too close together (< 1 second)
        too_close = any(abs(idx - s) < fps for s in selected_indices)
        if not too_close:
            selected_indices.add(idx)

    # Pad with uniform indices if needed
    for ui in sorted(uniform_indices):
        if len(selected_indices) >= n:
            break
        selected_indices.add(ui)

    # Write selected frames to disk (sorted by index = chronological)
    frame_dict = {idx: frm for _, idx, frm in frame_scores}
    for idx in sorted(selected_indices):
        if idx in frame_dict:
            path = f"frames/frame_{idx:06d}.jpg"
            cv2.imwrite(path, frame_dict[idx])
            saved_paths.append(path)

    return saved_paths[:n]


def extract_specific_frames(video_path: str, timestamps: list[float]) -> list[str]:
    """
    Extract specific frames by timestamp.
    timestamps: list of floats in seconds.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    
    saved_paths = []
    os.makedirs("frames", exist_ok=True)
    
    for ts in sorted(set(timestamps)):
        frame_idx = int(ts * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            path = f"frames/frame_{frame_idx:06d}.jpg"
            cv2.imwrite(path, frame)
            saved_paths.append(path)
            
    cap.release()
    return saved_paths


# ── BLIP Captioning ──────────────────────────────────────────

def caption_frames(frame_paths: list[str]) -> list[dict]:
    """
    Generate captions for each frame using BLIP-base.
    Returns list of { path, caption, frame_index }.
    """
    print(f"[VideoQA] Captioning {len(frame_paths)} frame(s) with BLIP...")
    t_total = time.time()
    processor, model = get_blip()
    device = next(model.parameters()).device
    results = []

    for i, path in enumerate(frame_paths):
        t0 = time.time()
        try:
            image = Image.open(path).convert("RGB")
            inputs = processor(image, return_tensors="pt").to(device)

            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=60,
                    num_beams=4,
                )

            caption = processor.decode(out[0], skip_special_tokens=True)
            frame_idx = int(os.path.basename(path).replace("frame_", "").replace(".jpg", ""))
            results.append({
                "path": path,
                "caption": caption,
                "frame_index": frame_idx,
            })
            print(f"[VideoQA]   Frame {i+1}/{len(frame_paths)} captioned in {round(time.time()-t0,1)}s: {caption[:60]}")
        except Exception as e:
            print(f"[VideoQA]   Frame {i+1} failed: {e}")
            results.append({"path": path, "caption": "Frame could not be captioned.", "frame_index": 0})

    print(f"[VideoQA] All frames captioned in {round(time.time()-t_total,1)}s")
    return results


# ── Clip Extraction ──────────────────────────────────────────

def extract_clip(
    video_path: str,
    start_sec: float,
    end_sec: float,
    out_path: str = "relevant_clip.mp4"
) -> str:
    """
    Extract a sub-clip using ffmpeg subprocess.
    Much faster and more reliable than MoviePy on Windows.
    """
    t0 = time.time()
    duration_sec = max(1.0, end_sec - start_sec)
    start_sec = max(0.0, start_sec)
    print(f"[VideoQA] Extracting clip {start_sec:.1f}s → {end_sec:.1f}s...")
    ffmpeg = _get_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",
        "-ss", str(start_sec),       # seek to start (fast seek before -i)
        "-i", video_path,
        "-t", str(duration_sec),      # duration
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",    # web-compatible MP4
        out_path,
    ]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace")[-300:]
        raise RuntimeError(f"ffmpeg clip extraction failed:\n{err}")
    print(f"[VideoQA] Clip extracted in {round(time.time()-t0,1)}s → {out_path}")
    return out_path


# ── Transcript → Timestamp Mapping ───────────────────────────

def find_clip_timestamps(
    transcript_segments: list[dict],
    question: str,
    video_duration: float,
    clip_duration: float = CLIP_DURATION,
) -> tuple[float, float]:
    """
    Find the most relevant clip for a question.
    Uses simple keyword overlap over Whisper word-level segments.
    Falls back to 1/3 into the video if nothing found.

    transcript_segments: list of { start, end, text } dicts from Whisper.
    Returns (start_sec, end_sec).
    """
    if not transcript_segments:
        start = video_duration / 3
        return start, min(video_duration, start + clip_duration)

    q_words = set(question.lower().split())
    best_score = -1
    best_start = 0.0

    for seg in transcript_segments:
        seg_words = set(seg.get("text", "").lower().split())
        overlap = len(q_words & seg_words)
        if overlap > best_score:
            best_score = overlap
            best_start = seg.get("start", 0.0)

    end = min(video_duration, best_start + clip_duration)
    return best_start, end
