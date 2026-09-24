"""
video_utils.py – Video processing helpers
Covers: audio extraction, smart keyframe sampling, BLIP captioning (batched), clip extraction.
All frame files are stored in session-scoped directories to avoid cross-session conflicts.
"""

import os
import time
import subprocess
import cv2
import torch
import numpy as np
from pathlib import Path
from PIL import Image

# ── MoviePy import (for clip extraction only – v1.x and v2.x) ──
try:
    from moviepy.editor import VideoFileClip   # moviepy v1.x
except ImportError:
    from moviepy import VideoFileClip          # moviepy v2.x

from models import get_blip

MAX_FRAMES   = int(os.getenv("MAX_FRAMES", "3"))
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

def extract_audio(
    video_path: str,
    out_path: str = "audio.wav",
    start_sec: float = None,
    end_sec: float = None,
) -> str:
    """
    Extract 16kHz mono WAV audio from video using ffmpeg subprocess.
    Much faster and more reliable than MoviePy's write_audiofile on Windows.
    """
    t0 = time.time()
    print(f"[VideoQA] Extracting audio from {os.path.basename(video_path)}...")
    ffmpeg = _get_ffmpeg()
    cmd = [ffmpeg, "-y"]
    if start_sec is not None:
        cmd.extend(["-ss", str(start_sec)])
    if end_sec is not None:
        duration = end_sec - (start_sec or 0.0)
        cmd.extend(["-t", str(duration)])
    cmd.extend([
        "-i", video_path,
        "-vn",                   # no video stream
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "16000",          # 16kHz (required by Whisper)
        "-ac", "1",              # mono
        out_path,
    ])
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300,
    )
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"ffmpeg audio extraction failed:\n{err}")
    print(f"[VideoQA] Audio extracted in {round(time.time()-t0,1)}s -> {out_path}")
    return out_path


# ── Frame Extraction ─────────────────────────────────────────

def _compute_frame_diff(prev: np.ndarray, curr: np.ndarray) -> float:
    """Mean absolute pixel difference between two frames (grayscale)."""
    p = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY).astype(float)
    c = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY).astype(float)
    return float(np.mean(np.abs(p - c)))


def extract_keyframes(
    video_path: str,
    n: int = MAX_FRAMES,
    start_sec: float = None,
    end_sec: float = None,
    frames_dir: str = None,          # <- NEW: session-scoped directory
) -> list[str]:
    """
    Smart keyframe extraction:
    1. Sample frames uniformly across the video.
    2. Additionally pick frames with high scene-change score.
    Returns up to `n` unique frame file paths with their timestamps.
    """
    cap   = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps   = cap.get(cv2.CAP_PROP_FPS) or 25.0

    start_frame = int(start_sec * fps) if start_sec is not None else 0
    end_frame   = int(end_sec * fps)   if end_sec   is not None else total

    # Use session-scoped frames dir; fall back to legacy global dir
    out_dir = Path(frames_dir) if frames_dir else Path("frames")
    out_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[str] = []

    if total <= 0 or start_frame >= end_frame:
        cap.release()
        return saved_paths

    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frames_to_process = end_frame - start_frame

    # Uniform sampling indices
    uniform_indices = set(
        start_frame + int(i * frames_to_process / max(n, 1)) for i in range(n)
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
            frame_scores.append((999.0, count, frame.copy()))

        prev_frame = frame
        count += 1

    cap.release()

    if not frame_scores:
        return saved_paths

    # Pick top-n frames by scene-change score, with minimum spacing
    sorted_by_score = sorted(frame_scores, key=lambda x: x[0], reverse=True)
    selected_indices: set[int] = set()

    for score, idx, frm in sorted_by_score:
        if len(selected_indices) >= n:
            break
        too_close = any(abs(idx - s) < fps for s in selected_indices)
        if not too_close:
            selected_indices.add(idx)

    # Pad with uniform indices if needed
    for ui in sorted(uniform_indices):
        if len(selected_indices) >= n:
            break
        selected_indices.add(ui)

    # Write selected frames sorted chronologically
    frame_dict = {idx: frm for _, idx, frm in frame_scores}
    for idx in sorted(selected_indices):
        if idx in frame_dict:
            # Filename encodes the actual video timestamp in ms for accurate display
            timestamp_ms = int((idx / fps) * 1000)
            path = str(out_dir / f"frame_{idx:06d}_t{timestamp_ms}.jpg")
            cv2.imwrite(path, frame_dict[idx])
            saved_paths.append(path)

    return saved_paths[:n]


def extract_specific_frames(
    video_path: str,
    timestamps: list[float],
    frames_dir: str = None,          # <- NEW: session-scoped directory
) -> list[str]:
    """
    Extract specific frames by timestamp (seconds).
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    out_dir = Path(frames_dir) if frames_dir else Path("frames")
    out_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []

    for ts in sorted(set(timestamps)):
        frame_idx = int(ts * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            timestamp_ms = int(ts * 1000)
            path = str(out_dir / f"frame_{frame_idx:06d}_t{timestamp_ms}.jpg")
            cv2.imwrite(path, frame)
            saved_paths.append(path)

    cap.release()
    return saved_paths


# ── BLIP Captioning (Batched for Speed) ──────────────────────

def caption_frames(frame_paths: list[str]) -> list[dict]:
    """
    Generate captions for all frames using BLIP-base.
    Uses BATCHED inference for speed — all frames processed together.
    Returns list of { path, caption, timestamp_sec }.
    """
    if not frame_paths:
        return []

    print(f"[VideoQA] Captioning {len(frame_paths)} frame(s) with BLIP (batched)...")
    t_total = time.time()

    processor, model = get_blip()
    device = next(model.parameters()).device

    results = []

    # Load all images first
    images = []
    valid_paths = []
    for path in frame_paths:
        try:
            img = Image.open(path).convert("RGB")
            images.append(img)
            valid_paths.append(path)
        except Exception as e:
            print(f"[VideoQA]   Could not open {path}: {e}")
            results.append({
                "path": path,
                "caption": "Frame could not be loaded.",
                "timestamp_sec": 0.0,
            })

    if not images:
        return results

    try:
        # Batched inference — process all frames at once
        inputs = processor(images=images, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=50,    # shorter captions are faster
                num_beams=2,          # reduced from 4 -> 2: ~2x faster with minimal quality loss
            )
        captions = processor.batch_decode(out, skip_special_tokens=True)

        for path, caption in zip(valid_paths, captions):
            # Extract timestamp from filename: frame_XXXXXX_tYYYYYY.jpg
            filename = Path(path).stem   # e.g. "frame_001234_t4936"
            try:
                t_ms = int(filename.split("_t")[-1])
                timestamp_sec = t_ms / 1000.0
            except (ValueError, IndexError):
                # Legacy filename format: frame_XXXXXX.jpg
                try:
                    frame_idx = int(filename.replace("frame_", "").split("_")[0])
                    timestamp_sec = frame_idx / 25.0
                except ValueError:
                    timestamp_sec = 0.0

            results.append({
                "path": path,
                "caption": caption.strip(),
                "timestamp_sec": timestamp_sec,
            })
            print(f"[VideoQA]   [{_fmt_time(timestamp_sec)}] {caption.strip()[:70]}")

    except Exception as e:
        # Batched inference failed — fall back to sequential
        print(f"[VideoQA]   Batched captioning failed ({e}), falling back to sequential...")
        for path in valid_paths:
            try:
                img = Image.open(path).convert("RGB")
                inputs = processor(images=img, return_tensors="pt").to(device)
                with torch.no_grad():
                    out = model.generate(**inputs, max_new_tokens=50, num_beams=2)
                caption = processor.decode(out[0], skip_special_tokens=True)

                filename = Path(path).stem
                try:
                    t_ms = int(filename.split("_t")[-1])
                    timestamp_sec = t_ms / 1000.0
                except (ValueError, IndexError):
                    timestamp_sec = 0.0

                results.append({
                    "path": path,
                    "caption": caption.strip(),
                    "timestamp_sec": timestamp_sec,
                })
            except Exception as frame_e:
                print(f"[VideoQA]   Frame {path} failed: {frame_e}")
                results.append({
                    "path": path,
                    "caption": "Frame could not be captioned.",
                    "timestamp_sec": 0.0,
                })

    print(f"[VideoQA] All {len(results)} frames captioned in {round(time.time()-t_total,1)}s")
    return results


def _fmt_time(seconds: float) -> str:
    s = int(seconds)
    m, s = divmod(s, 60)
    return f"{m}:{s:02d}"


# ── Clip Extraction ──────────────────────────────────────────

def extract_clip(
    video_path: str,
    start_sec: float,
    end_sec: float,
    out_path: str = "relevant_clip.mp4",
) -> str:
    """
    Extract a sub-clip using ffmpeg subprocess.
    Much faster and more reliable than MoviePy on Windows.
    """
    t0 = time.time()
    duration_sec = max(1.0, end_sec - start_sec)
    start_sec    = max(0.0, start_sec)
    print(f"[VideoQA] Extracting clip {start_sec:.1f}s -> {end_sec:.1f}s...")
    ffmpeg = _get_ffmpeg()
    cmd = [
        ffmpeg, "-y",
        "-ss", str(start_sec),
        "-i", video_path,
        "-t", str(duration_sec),
        "-c:v", "libx264",
        "-preset", "ultrafast",       # faster encoding
        "-crf", "28",                 # slightly lower quality for speed
        "-c:a", "aac",
        "-movflags", "+faststart",
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
    print(f"[VideoQA] Clip extracted in {round(time.time()-t0,1)}s -> {out_path}")
    return out_path


# ── Transcript -> Timestamp Mapping ───────────────────────────

def find_clip_timestamps(
    transcript_segments: list[dict],
    question: str,
    video_duration: float,
    clip_duration: float = CLIP_DURATION,
) -> tuple[float, float]:
    """
    Find the most relevant clip for a question using keyword overlap.
    Falls back to 1/3 into the video if nothing found.
    """
    if not transcript_segments:
        start = video_duration / 3
        return start, min(video_duration, start + clip_duration)

    # Remove common stopwords for better matching
    stopwords = {"the", "a", "an", "is", "in", "it", "of", "to", "and", "or",
                 "what", "how", "why", "when", "where", "who", "which", "does",
                 "do", "did", "was", "were", "has", "have", "had", "be", "been",
                 "this", "that", "these", "those", "can", "could", "would", "should"}

    q_words = {w for w in question.lower().split() if w not in stopwords and len(w) > 2}
    best_score = -1
    best_start = 0.0

    for seg in transcript_segments:
        seg_words = {w for w in seg.get("text", "").lower().split() if w not in stopwords}
        overlap = len(q_words & seg_words)
        if overlap > best_score:
            best_score = overlap
            best_start = seg.get("start", 0.0)

    # If no keyword match found, use middle of video
    if best_score <= 0:
        best_start = video_duration / 3

    end = min(video_duration, best_start + clip_duration)
    return best_start, end
