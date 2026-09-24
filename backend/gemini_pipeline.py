"""
gemini_pipeline.py - Fast multimodal Video QA using Google Gemini 1.5 Flash
============================================================================
Pipeline steps:
  1. Download (YouTube -> 480p MP4 via yt-dlp) OR save uploaded file to temp.
  2. Upload the video to Google's File API (handles files up to 2 GB).
  3. Poll until the File API has finished processing the video.
  4. Prompt gemini-1.5-flash with the user's question + the video file reference.
  5. Return the text answer to the caller and clean up all temp files.

All heavy I/O operations run in asyncio.to_thread() so they never block the
FastAPI event loop.
"""

import os
import time
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Optional

import yt_dlp
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("gemini_pipeline")

# -- Client singleton -------------------------------------------------------
# Initialised once; the SDK reads GEMINI_API_KEY from the environment.
_client: Optional[genai.Client] = None

def _is_placeholder_key(key: str) -> bool:
    """Detect placeholder/example API keys that won't work at runtime."""
    if not key or not key.strip():
        return True
    k = key.strip().lower()
    placeholders = ["your_", "put_", "add_", "insert_", "replace_", "example",
                     "xxx", "placeholder", "todo", "fixme", "_here"]
    return any(p in k for p in placeholders)


def _get_client() -> genai.Client:
    """Return a cached google-genai client. Raises clearly if the key is missing or placeholder."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key or _is_placeholder_key(api_key):
            raise RuntimeError(
                "GEMINI_API_KEY is not set or is a placeholder. "
                "Get a free key at https://aistudio.google.com/apikey "
                "and add it to backend/.env as GEMINI_API_KEY=your_real_key"
            )
        _client = genai.Client(api_key=api_key)
    return _client


# -- Directories ------------------------------------------------------------
_TEMP_DIR = Path("uploads") / "gemini_temp"
_TEMP_DIR.mkdir(parents=True, exist_ok=True)


# -- Step 1a: YouTube download (480p MP4) -----------------------------------

def _download_youtube_sync(url: str, out_dir: Path) -> str:
    """
    Synchronous yt-dlp download - call via asyncio.to_thread().

    Format preference order:
      1. bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]  -> true 480p MP4
      2. best[height<=480][ext=mp4]                          -> single-stream 480p
      3. best[ext=mp4]                                       -> any MP4 (fallback)
      4. best                                                -> anything available

    nopart=True avoids .part temp files (prevents WinError 32 on Windows).
    """
    unique_name = f"yt_{uuid.uuid4().hex}"
    outtmpl = str(out_dir / f"{unique_name}.%(ext)s")

    ydl_opts: dict = {
        "format": (
            "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]"
            "/best[height<=480][ext=mp4]"
            "/best[ext=mp4]"
            "/best"
        ),
        "outtmpl":     outtmpl,
        "quiet":       True,
        "no_warnings": True,
        "nopart":      True,
        "merge_output_format": "mp4",
        "extractor_args": {"youtube": ["player_client=android,tv,ios"]},
    }

    # -- Cookie setup -------------------------------------------------------
    cookie_file = Path("cookies.txt")
    env_cookies = os.getenv("YOUTUBE_COOKIES_SECRET", "")
    if env_cookies and not cookie_file.exists():
        try:
            cookie_file.write_text(env_cookies, encoding="utf-8")
        except Exception as exc:
            logger.warning("Could not write cookies.txt: %s", exc)

    browser = os.getenv("YOUTUBE_BROWSER", "chrome")
    if cookie_file.exists():
        ydl_opts["cookiefile"] = str(cookie_file)
    elif browser and browser.lower() not in ("none", "false", ""):
        ydl_opts["cookiesfrombrowser"] = (browser,)

    def _run() -> str:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info.get("ext", "mp4")

    # Attempt 1: with cookies
    try:
        ext = _run()
    except yt_dlp.utils.DownloadError as exc:
        err = str(exc)
        if "cookiesfrombrowser" in ydl_opts and any(
            kw in err for kw in ("cookies", "browser", "profile")
        ):
            logger.warning("Cookie extraction failed (%s), retrying without cookies.", err)
            del ydl_opts["cookiesfrombrowser"]
            ext = _run()
        else:
            _raise_download_error(err, url)
            raise

    # -- Locate the downloaded file (Windows file-lock tolerant) -----------
    video_exts = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".m4v", ".flv", ".ts"}
    expected = out_dir / f"{unique_name}.{ext}"

    for _ in range(15):
        if expected.exists() and expected.stat().st_size > 0:
            return str(expected)
        for f in out_dir.iterdir():
            if (
                f.stem.startswith(unique_name)
                and f.suffix.lower() in video_exts
                and f.stat().st_size > 0
            ):
                if f != expected:
                    try:
                        f.rename(expected)
                        return str(expected)
                    except OSError:
                        return str(f)
                return str(f)
        time.sleep(0.3)

    raise RuntimeError(
        f"yt-dlp reported success but the output file was not found in {out_dir}. "
        "This is likely a Windows file-lock transient error - please retry."
    )


def _raise_download_error(err: str, url: str) -> None:
    """Convert yt-dlp errors into user-friendly messages."""
    is_youtube = "youtube.com" in url.lower() or "youtu.be" in url.lower()

    if is_youtube and any(
        kw in err for kw in ("Sign in", "bot", "nsig", "403", "confirm your age")
    ):
        raise ValueError(
            "YouTube has blocked the download (bot detection). "
            "Try uploading the video file directly, or export your YouTube cookies "
            "using the 'Get cookies.txt LOCALLY' browser extension and save the file "
            "as 'cookies.txt' in the backend/ directory."
        )
    if "WinError 32" in err or "used by another process" in err:
        raise ValueError(
            "Windows file-lock error during download. Please retry."
        )
    raise ValueError(f"Download failed: {err}")


async def download_youtube(url: str, out_dir: Optional[Path] = None) -> str:
    """
    Async wrapper: downloads a YouTube video at <=480p to out_dir
    and returns the absolute path to the downloaded MP4 file.
    """
    target = out_dir or _TEMP_DIR
    target.mkdir(parents=True, exist_ok=True)
    try:
        return await asyncio.to_thread(_download_youtube_sync, url, target)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Unexpected download error: {exc}") from exc


# -- Step 1b: Save uploaded file to temp ------------------------------------

async def save_upload(file_bytes: bytes, original_filename: str) -> str:
    """
    Save raw bytes from an uploaded file to the temp directory.
    Returns the absolute path to the saved file.
    """
    safe_name = Path(original_filename).name or "uploaded_video.mp4"
    unique_name = f"upload_{uuid.uuid4().hex}_{safe_name}"
    out_path = _TEMP_DIR / unique_name

    def _write():
        out_path.write_bytes(file_bytes)

    await asyncio.to_thread(_write)
    logger.info("Saved upload: %s (%.1f MB)", out_path.name, len(file_bytes) / 1_048_576)
    return str(out_path)


# -- Step 2: Upload to Google File API --------------------------------------

def _upload_file_sync(client: genai.Client, video_path: str) -> types.File:
    """
    Upload video_path to the Google File API and wait until it is ACTIVE.
    Polls every 5 seconds; times out after 10 minutes.
    """
    path = Path(video_path)
    file_size_mb = path.stat().st_size / 1_048_576
    logger.info("Uploading %s (%.1f MB) to File API...", path.name, file_size_mb)
    t0 = time.time()

    video_file = client.files.upload(
        file=path,
        config=types.UploadFileConfig(
            display_name=path.name,
            mime_type="video/mp4",
        ),
    )

    max_wait_secs = 600
    poll_interval = 5

    while True:
        video_file = client.files.get(name=video_file.name)
        state = video_file.state
        state_name = state.name if hasattr(state, "name") else str(state)

        if state_name == "ACTIVE":
            elapsed = round(time.time() - t0, 1)
            logger.info("File API ready in %ss: %s", elapsed, video_file.uri)
            return video_file

        if state_name == "FAILED":
            raise RuntimeError(
                f"Google File API rejected the video ({video_file.name}). "
                "Check that the file is a valid MP4 and under 2 GB."
            )

        waited = time.time() - t0
        if waited > max_wait_secs:
            raise TimeoutError(
                f"File API did not become ACTIVE within {max_wait_secs}s. "
                f"Last state: {state_name}"
            )

        logger.info("File state: %s - waiting %ss...", state_name, poll_interval)
        time.sleep(poll_interval)


async def upload_to_file_api(client: genai.Client, video_path: str) -> types.File:
    """Async wrapper around _upload_file_sync."""
    return await asyncio.to_thread(_upload_file_sync, client, video_path)


# -- Step 3: Delete file from File API --------------------------------------

async def delete_file_api_file(client: genai.Client, file_name: str) -> None:
    """Best-effort async delete of a File API object."""
    try:
        await asyncio.to_thread(client.files.delete, name=file_name)
        logger.info("Deleted File API object: %s", file_name)
    except Exception as exc:
        logger.warning("Could not delete File API object %s: %s", file_name, exc)


# -- Step 4: Ask Gemini -----------------------------------------------------

_DEFAULT_MODEL = "gemini-3.6-flash"

_SYSTEM_PROMPT = (
    "You are an expert multimodal video analyst. "
    "A video file has been provided. Watch it carefully and answer the user's question "
    "thoroughly, citing specific moments or visuals from the video where relevant. "
    "If the answer cannot be determined from the video, say so honestly. "
    "Format your response in clear, well-structured markdown."
)


def _call_gemini_sync(
    client: genai.Client,
    video_file: types.File,
    question: str,
    language: str = "English",
    model_name: str = _DEFAULT_MODEL,
    max_retries: int = 3,
) -> str:
    """
    Send the video + question to Gemini and return the text response.
    Synchronous - call via asyncio.to_thread().
    Includes retry with exponential backoff for transient failures.
    """
    import random

    user_content = (
        f"Please answer the following question about this video in {language}:\n\n"
        f"{question}"
    )

    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info("[Gemini] Calling %s (attempt %d/%d)", model_name, attempt + 1, max_retries)
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_uri(file_uri=video_file.uri, mime_type="video/mp4"),
                    types.Part.from_text(text=user_content),
                ],
                config=types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                    temperature=0.4,
                    max_output_tokens=4096,
                ),
            )

            try:
                return response.text.strip()
            except Exception:
                parts = []
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text:
                            parts.append(part.text)
                result = "\n".join(parts).strip()
                if result:
                    return result
                raise RuntimeError("Gemini returned empty response")

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            # Don't retry auth errors or invalid input
            if any(kw in err_str for kw in ("api_key", "permission", "invalid", "not found")):
                raise
            # Retry on transient errors (rate limit, timeout, server error)
            if attempt < max_retries - 1:
                delay = min(2.0 * (2 ** attempt), 30.0) + random.uniform(0, 1)
                logger.warning("[Gemini] Attempt %d failed: %s — retrying in %.1fs", attempt + 1, e, delay)
                time.sleep(delay)
            else:
                logger.error("[Gemini] All %d attempts failed. Last error: %s", max_retries, e)

    raise RuntimeError(f"Gemini call failed after {max_retries} attempts: {last_error}")


async def ask_gemini(
    client: genai.Client,
    video_file: types.File,
    question: str,
    language: str = "English",
    model_name: str = _DEFAULT_MODEL,
) -> str:
    """Async wrapper around _call_gemini_sync."""
    return await asyncio.to_thread(
        _call_gemini_sync, client, video_file, question, language, model_name
    )


# -- Step 5: Cleanup temp files ---------------------------------------------

async def cleanup_local_file(path: str) -> None:
    """Best-effort async deletion of a local temp file."""
    try:
        await asyncio.to_thread(Path(path).unlink, True)
        logger.info("Cleaned up local file: %s", path)
    except Exception as exc:
        logger.warning("Could not delete local file %s: %s", path, exc)


# -- High-level pipeline ----------------------------------------------------

async def run_gemini_pipeline(
    *,
    question: str,
    video_url: Optional[str] = None,
    video_bytes: Optional[bytes] = None,
    original_filename: str = "video.mp4",
    language: str = "English",
    model_name: str = _DEFAULT_MODEL,  # gemini-3.6-flash
) -> dict:
    """
    Full end-to-end pipeline. Exactly one of video_url or video_bytes must be set.

    Returns:
        {
            "answer":       str,   # Gemini markdown response
            "model":        str,   # model used
            "source":       str,   # "youtube" | "upload"
            "file_api_uri": str,   # File API URI (for debugging)
        }

    Raises:
        ValueError   - bad input / download failure  -> HTTP 400
        RuntimeError - pipeline failure              -> HTTP 500
    """
    if not video_url and not video_bytes:
        raise ValueError("Provide either a video_url (YouTube link) or video_bytes.")
    if video_url and video_bytes:
        raise ValueError("Provide either video_url or video_bytes, not both.")

    client = _get_client()
    local_path: Optional[str] = None
    file_api_obj: Optional[types.File] = None
    source = "youtube" if video_url else "upload"

    try:
        # Step 1: Obtain local video file
        if video_url:
            logger.info("[Gemini Pipeline] Downloading YouTube video: %s", video_url)
            local_path = await download_youtube(video_url)
        else:
            logger.info("[Gemini Pipeline] Saving uploaded file (%d bytes).", len(video_bytes))
            local_path = await save_upload(video_bytes, original_filename)

        # Step 2: Upload to File API
        logger.info("[Gemini Pipeline] Uploading to File API...")
        file_api_obj = await upload_to_file_api(client, local_path)

        # Step 3: Ask Gemini
        logger.info("[Gemini Pipeline] Sending question to %s...", model_name)
        answer = await ask_gemini(client, file_api_obj, question, language, model_name)
        logger.info("[Gemini Pipeline] Answer received (%d chars).", len(answer))

        return {
            "answer":       answer,
            "model":        model_name,
            "source":       source,
            "file_api_uri": file_api_obj.uri,
        }

    finally:
        # Always clean up, even if an exception occurred mid-pipeline
        if local_path:
            await cleanup_local_file(local_path)
        if file_api_obj:
            await delete_file_api_file(client, file_api_obj.name)
