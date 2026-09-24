"""
llm.py – LLM integration for VideoQA
=====================================
Primary model  : Google Gemini 2.0 Flash (free tier: 15 RPM, 1500 RPD, 1M tokens)
Fallback model : OpenRouter free-tier models (text-only)
Emergency      : Pollinations.ai (keyless, best-effort)

Features:
  - Exponential backoff with jitter for transient failures (429, 5xx)
  - Rate-limit / quota tracking so the app doesn't exceed free-tier limits
  - Automatic transcript truncation for very long videos
  - Structured logging for easy debugging
  - Graceful degradation: Gemini → OpenRouter chain → Pollinations
"""

import os
import re
import json
import time
import random
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Logging ──────────────────────────────────────────────────
logger = logging.getLogger("videoqa.llm")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ── Configuration ────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini-3.6-flash")

# Transcript safety: truncate very long transcripts to avoid context overflow
MAX_TRANSCRIPT_CHARS = int(os.getenv("MAX_TRANSCRIPT_CHARS", "30000"))

# API endpoints
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Retry configuration ─────────────────────────────────────
MAX_RETRIES = 3
INITIAL_BACKOFF_SEC = 2.0
MAX_BACKOFF_SEC = 30.0

# ── Rate limit tracking ─────────────────────────────────────
_rate_state = {
    "gemini_blocked_until": 0.0,
    "gemini_req_count": 0,
    "gemini_minute_start": 0.0,
}
GEMINI_RPM_LIMIT = 14  # Conservative: stay under 15 RPM free-tier cap

# ── OpenRouter fallback chain (tried in order) ───────────────
FREE_MODEL_FALLBACKS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "deepseek/deepseek-r1-0528:free",
    "microsoft/phi-4:free",
    "meta-llama/llama-3.2-3b-instruct:free",
]

# ── Available models (displayed in frontend) ─────────────────
SUPPORTED_MODELS = {
    "gemini-3.6-flash":  "gemini-3.6-flash",
    "gemini-1.5-flash":  "gemini-1.5-flash",
    "llama-3.3-70b":     FREE_MODEL_FALLBACKS[0],
    "gemma-3-27b":       FREE_MODEL_FALLBACKS[1],
    "qwen-2.5-72b":      FREE_MODEL_FALLBACKS[2],
    "mistral-small":     FREE_MODEL_FALLBACKS[3],
    "deepseek-r1":       FREE_MODEL_FALLBACKS[4],
    "phi-4":             FREE_MODEL_FALLBACKS[5],
    "llama-3.2-3b":      FREE_MODEL_FALLBACKS[6],
}


# ── Custom Exceptions ────────────────────────────────────────

class RateLimitError(Exception):
    """Raised when a model returns HTTP 429 (rate-limited)."""
    pass

class SkipModelError(Exception):
    """Raised when a model should be skipped (404, non-retryable error)."""
    pass

class AuthError(Exception):
    """Raised on authentication/payment failures (401/402/403)."""
    pass


# ── Helpers ──────────────────────────────────────────────────

def _is_placeholder_key(key: str) -> bool:
    """Detect placeholder/example API keys that won't work at runtime."""
    if not key or not key.strip():
        return True
    k = key.strip().lower()
    placeholders = [
        "your_", "put_", "add_", "insert_", "replace_", "example",
        "xxx", "placeholder", "todo", "fixme", "change_me",
        "your_gemini", "your_api", "sk-xxx", "_here",
    ]
    return any(p in k for p in placeholders)


def truncate_transcript(text: str, max_chars: int = MAX_TRANSCRIPT_CHARS) -> str:
    """
    Truncate a long transcript to fit within LLM context windows.
    Preserves the beginning and end (most semantically important parts).
    """
    if not text or len(text) <= max_chars:
        return text
    half = max_chars // 2
    omitted = len(text) - max_chars
    logger.info(
        "Truncating text from %d to %d chars (%d omitted)",
        len(text), max_chars, omitted,
    )
    return (
        text[:half]
        + f"\n\n[... {omitted} characters omitted for brevity ...]\n\n"
        + text[-half:]
    )


def _backoff_delay(attempt: int) -> float:
    """Exponential backoff with jitter to avoid thundering herd."""
    delay = min(INITIAL_BACKOFF_SEC * (2 ** attempt), MAX_BACKOFF_SEC)
    jitter = random.uniform(0, delay * 0.3)
    return delay + jitter


# ── Rate Limit Management ───────────────────────────────────

def _gemini_available() -> bool:
    """Check if Gemini is available (valid key + within rate limits)."""
    if _is_placeholder_key(GEMINI_API_KEY):
        return False
    now = time.time()
    if now < _rate_state["gemini_blocked_until"]:
        return False
    # Reset per-minute counter if a minute has elapsed
    if now - _rate_state["gemini_minute_start"] > 60:
        _rate_state["gemini_req_count"] = 0
        _rate_state["gemini_minute_start"] = now
    return _rate_state["gemini_req_count"] < GEMINI_RPM_LIMIT


def _record_gemini_request():
    """Track a successful Gemini request for rate-limit accounting."""
    _rate_state["gemini_req_count"] += 1
    logger.debug(
        "Gemini requests this minute: %d/%d",
        _rate_state["gemini_req_count"], GEMINI_RPM_LIMIT,
    )


def _block_gemini(seconds: float = 60.0):
    """Temporarily block Gemini after a rate-limit (429) hit."""
    _rate_state["gemini_blocked_until"] = time.time() + seconds
    logger.warning("Gemini rate-limited — blocking for %.0fs", seconds)


def get_rate_limit_status() -> dict:
    """Return current rate-limit state for the /rate_limit endpoint."""
    now = time.time()
    return {
        "gemini_available": _gemini_available(),
        "gemini_requests_this_minute": _rate_state["gemini_req_count"],
        "gemini_rpm_limit": GEMINI_RPM_LIMIT,
        "gemini_blocked_for_sec": round(max(0, _rate_state["gemini_blocked_until"] - now), 1),
        "openrouter_key_set": bool(OPENROUTER_API_KEY and not _is_placeholder_key(OPENROUTER_API_KEY)),
        "gemini_key_set": bool(GEMINI_API_KEY and not _is_placeholder_key(GEMINI_API_KEY)),
    }


# ══════════════════════════════════════════════════════════════
# MODEL CALLS
# ══════════════════════════════════════════════════════════════

# ── Gemini 2.0 Flash (via REST API) ─────────────────────────

def _call_gemini(
    messages: list[dict],
    model: str = "gemini-3.6-flash",
    temperature: float = 0.4,
    max_tokens: int = 4096,
) -> str:
    """
    Call Google Gemini via the public REST API.
    Converts OpenAI-style messages to Gemini format.
    Raises RateLimitError, AuthError, or SkipModelError on failure.
    """
    # ── Convert OpenAI messages → Gemini format ──
    system_instruction = None
    contents = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            system_instruction = content
        elif role == "user":
            contents.append({"role": "user", "parts": [{"text": content}]})
        elif role == "assistant":
            contents.append({"role": "model", "parts": [{"text": content}]})

    body = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    url = f"{GEMINI_API_URL}/{model}:generateContent?key={GEMINI_API_KEY}"

    resp = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=body,
        timeout=90,
    )

    # ── Error handling ──
    if resp.status_code == 429:
        _block_gemini(60.0)
        raise RateLimitError(f"Gemini {model} rate-limited (429)")
    if resp.status_code == 503:
        # Server overloaded — transient, should be retried with backoff
        raise RateLimitError(f"Gemini {model} overloaded (503) — will retry")
    if resp.status_code in (400,):
        raise SkipModelError(f"Gemini bad request (400): {resp.text[:300]}")
    if resp.status_code in (401, 403):
        raise AuthError(f"Gemini API key error ({resp.status_code}): {resp.text[:200]}")
    if resp.status_code != 200:
        raise SkipModelError(f"Gemini error {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    try:
        _record_gemini_request()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        # Check for safety blocks or empty responses
        if "candidates" in data and data["candidates"]:
            candidate = data["candidates"][0]
            finish_reason = candidate.get("finishReason", "")
            if finish_reason == "SAFETY":
                raise SkipModelError("Gemini blocked response (safety filters)")
            if finish_reason == "MAX_TOKENS":
                # Return whatever partial content we got
                try:
                    partial = data["candidates"][0]["content"]["parts"][0]["text"]
                    logger.warning("Gemini response truncated at max_tokens")
                    return partial.strip()
                except Exception:
                    pass
        # Check for prompt-level blocks
        if "promptFeedback" in data:
            block_reason = data["promptFeedback"].get("blockReason", "unknown")
            raise SkipModelError(f"Gemini blocked prompt: {block_reason}")
        raise RuntimeError(
            f"Unexpected Gemini response format: {json.dumps(data)[:500]}"
        ) from e


# ── OpenRouter (text-only fallback) ──────────────────────────

def _call_openrouter(
    messages: list[dict],
    model: str,
    temperature: float = 0.4,
    max_tokens: int = 4096,
) -> str:
    """
    Call OpenRouter API with the given model.
    Raises RateLimitError, SkipModelError, or AuthError on failure.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://videoqa.local",
        "X-Title":       "VideoQA",
    }

    resp = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=90,
    )

    if resp.status_code == 429:
        raise RateLimitError(f"OpenRouter rate-limited on {model}")
    if resp.status_code == 404:
        raise SkipModelError(f"Model not found on OpenRouter: {model}")
    if resp.status_code in (401, 402, 403):
        raise AuthError(f"OpenRouter auth error {resp.status_code}: {resp.text[:200]}")
    if resp.status_code != 200:
        raise SkipModelError(f"OpenRouter error {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected OpenRouter response: {data}") from e


# ── Pollinations.ai (emergency keyless fallback) ─────────────

def _call_pollinations(
    messages: list[dict],
    temperature: float = 0.4,
    max_tokens: int = 2048,
) -> str:
    """
    Keyless emergency fallback via Pollinations.ai.
    No API key required — best-effort only, no SLA guarantees.
    """
    logger.info("Using Pollinations.ai keyless emergency fallback")

    for p_model in ["openai", "llama"]:
        try:
            resp = requests.post(
                "https://text.pollinations.ai/openai",
                headers={"Content-Type": "application/json"},
                json={
                    "model": p_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=90,
            )
            try:
                data = resp.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"].strip()
            except json.JSONDecodeError:
                if resp.status_code == 200 and resp.text.strip():
                    return resp.text.strip()
            logger.warning("Pollinations '%s' failed, trying next...", p_model)
        except Exception as exc:
            logger.warning("Pollinations '%s' exception: %s", p_model, exc)
            continue

    raise RuntimeError("All Pollinations models exhausted")


# ══════════════════════════════════════════════════════════════
# CORE LLM CALL WITH RETRY + FALLBACK CHAIN
# ══════════════════════════════════════════════════════════════

def call_llm(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.4,
    max_tokens: int = 4096,
) -> str:
    """
    Call the best available LLM with automatic retry and fallback:

      Phase 1 — Gemini 2.0 Flash (primary, with retries + backoff)
      Phase 2 — OpenRouter free models (fallback chain)
      Phase 3 — Pollinations.ai (emergency keyless fallback)

    Retries transient errors (429, 5xx) with exponential backoff.
    Skips permanently unavailable models (404, bad auth) immediately.

    Returns the LLM's text response.
    Raises RuntimeError only if ALL providers are exhausted.
    """
    last_error = None
    t_start = time.time()

    # ── Phase 1: Gemini 2.0 Flash with retries ──────────────
    if _gemini_available():
        gemini_model = model if model.startswith("gemini-") else "gemini-3.6-flash"
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(
                    "[Phase 1] Gemini %s — attempt %d/%d",
                    gemini_model, attempt + 1, MAX_RETRIES,
                )
                result = _call_gemini(messages, gemini_model, temperature, max_tokens)
                elapsed = round(time.time() - t_start, 2)
                logger.info(
                    "✓ Gemini %s responded (%d chars) in %.2fs",
                    gemini_model, len(result), elapsed,
                )
                return result

            except RateLimitError as e:
                delay = _backoff_delay(attempt)
                logger.warning("Gemini rate-limited, backing off %.1fs...", delay)
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    time.sleep(delay)
                continue

            except AuthError as e:
                logger.error("✗ Gemini auth failed: %s", e)
                last_error = e
                break  # Auth errors won't resolve with retries

            except SkipModelError as e:
                logger.warning("✗ Gemini skipped: %s", e)
                last_error = e
                break  # Model-level issue, don't retry

            except requests.exceptions.Timeout:
                logger.warning("Gemini request timed out (attempt %d)", attempt + 1)
                last_error = TimeoutError("Gemini timed out")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(_backoff_delay(attempt))
                continue

            except Exception as e:
                logger.error("✗ Gemini unexpected error: %s", e)
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    time.sleep(_backoff_delay(attempt))
                continue
    else:
        reason = "no valid API key" if _is_placeholder_key(GEMINI_API_KEY) else "rate-limited"
        logger.info("[Phase 1] Gemini unavailable (%s), skipping to fallback", reason)

    # ── Phase 2: OpenRouter fallback chain ───────────────────
    if OPENROUTER_API_KEY and not _is_placeholder_key(OPENROUTER_API_KEY):
        # Build chain: requested model first (if it's an OpenRouter model), then fallbacks
        if "/" in model or ":free" in model:
            openrouter_model = model
        else:
            openrouter_model = FREE_MODEL_FALLBACKS[0]
        chain = [openrouter_model] + [m for m in FREE_MODEL_FALLBACKS if m != openrouter_model]

        for fallback_model in chain:
            try:
                logger.info("[Phase 2] OpenRouter: %s", fallback_model)
                result = _call_openrouter(messages, fallback_model, temperature, max_tokens)
                elapsed = round(time.time() - t_start, 2)
                logger.info(
                    "✓ OpenRouter %s responded (%d chars) in %.2fs",
                    fallback_model, len(result), elapsed,
                )
                return result

            except RateLimitError as e:
                logger.warning("OpenRouter rate-limited on %s, trying next...", fallback_model)
                last_error = e
                continue

            except SkipModelError as e:
                logger.warning("OpenRouter skipping %s: %s", fallback_model, e)
                last_error = e
                continue

            except AuthError as e:
                logger.error("✗ OpenRouter auth failed: %s", e)
                last_error = e
                break  # All OpenRouter models will fail with bad auth

            except Exception as e:
                logger.error("✗ OpenRouter error on %s: %s", fallback_model, e)
                last_error = e
                continue
    else:
        logger.info("[Phase 2] OpenRouter unavailable (no valid API key), skipping")

    # ── Phase 3: Emergency Pollinations fallback ─────────────
    logger.warning("[Phase 3] All primary models exhausted — trying Pollinations emergency fallback")
    try:
        result = _call_pollinations(messages, temperature, min(max_tokens, 2048))
        elapsed = round(time.time() - t_start, 2)
        logger.info("✓ Pollinations emergency fallback responded (%d chars) in %.2fs", len(result), elapsed)
        return result
    except Exception as e:
        logger.error("✗ Pollinations emergency fallback also failed: %s", e)

    # ── All providers exhausted ──────────────────────────────
    raise RuntimeError(
        f"All LLM providers exhausted after {round(time.time() - t_start, 1)}s. "
        f"Last error: {last_error}. "
        "Please check your API keys in backend/.env — "
        "get a free Gemini key at https://aistudio.google.com/apikey"
    )


# ══════════════════════════════════════════════════════════════
# JSON PARSING HELPER
# ══════════════════════════════════════════════════════════════

def _parse_llm_json(raw: str, fallback_fields: dict) -> dict:
    """
    Robustly parse JSON from LLM response.

    Handles:
      - Markdown code fences (```json ... ```)
      - JSON embedded in surrounding text
      - Trailing commas (common LLM mistake)
      - Completely non-JSON responses (returns fallback)
    """
    clean = raw.strip()

    # ── Strip markdown code fences ──
    if clean.startswith("```"):
        lines = clean.split("\n")
        clean = "\n".join(lines[1:])
        if clean.rstrip().endswith("```"):
            clean = clean.rstrip()[:-3]
        clean = clean.strip()

    # ── Try 1: Direct parse ──
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    # ── Try 2: Extract JSON object from surrounding text ──
    json_match = re.search(r'\{[\s\S]*\}', clean)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # ── Try 3: Fix trailing commas and re-parse ──
    try:
        fixed = re.sub(r',\s*([}\]])', r'\1', clean)
        return json.loads(fixed)
    except (json.JSONDecodeError, Exception):
        pass

    # ── Try 4: Extract from surrounding text + fix commas ──
    if json_match:
        try:
            fixed = re.sub(r',\s*([}\]])', r'\1', json_match.group())
            return json.loads(fixed)
        except (json.JSONDecodeError, Exception):
            pass

    # ── Give up — return raw text in the expected structure ──
    logger.warning(
        "Could not parse JSON from LLM response (%d chars), using raw text fallback",
        len(raw),
    )
    result = dict(fallback_fields)
    # Insert raw text into the first empty-string field
    for key, val in result.items():
        if isinstance(val, str) and not val:
            result[key] = raw
            break
    return result


# ══════════════════════════════════════════════════════════════
# PUBLIC API — Called by main.py endpoints
# ══════════════════════════════════════════════════════════════

def answer_question(
    question: str,
    transcript: str,
    visuals: str,
    language: str = "English",
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Generate a detailed answer grounded in transcript + visual captions.
    Returns { answer, transcript_excerpts, visual_captions, confidence, confidence_reason }.
    """
    # Truncate to avoid exceeding context limits on long videos
    safe_transcript = truncate_transcript(transcript)
    safe_visuals = truncate_transcript(visuals, max_chars=5000)

    system_msg = (
        "You are an expert multimodal video analyst. "
        "You will be given a video transcript and visual frame descriptions. "
        "Answer the user's question thoroughly and accurately, citing specific parts of the transcript. "
        "If the answer is not clearly in the video, say so honestly."
    )

    user_msg = f"""VIDEO TRANSCRIPT:
{safe_transcript}

VISUAL FRAME DESCRIPTIONS:
{safe_visuals}

QUESTION: {question}

Instructions:
- Answer in {language}.
- Be detailed but concise (3-6 sentences).
- Bold key terms using **term** markdown.
- Extract 1-2 most relevant transcript sentences as evidence.
- Extract 1-2 most relevant visual captions as evidence.
- Rate your confidence as: High / Medium / Low.

IMPORTANT: Respond ONLY with valid JSON, no other text before or after. Format:
{{
  "answer": "...",
  "transcript_excerpts": ["...", "..."],
  "visual_captions": ["...", "..."],
  "confidence": "High|Medium|Low",
  "confidence_reason": "..."
}}"""

    raw = call_llm(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ],
        model=model or DEFAULT_MODEL,
        temperature=0.3,
        max_tokens=4096,
    )

    return _parse_llm_json(raw, {
        "answer": raw,
        "transcript_excerpts": [],
        "visual_captions": [],
        "confidence": "Medium",
        "confidence_reason": "Based on transcript + visual frames",
    })


# ── Video Summarization ────────────────────────────────────────

def summarize_video(
    transcript: str,
    visuals: str,
    length: str = "short",
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Summarize the video content.
    length: "short" | "detailed" | "chapters"
    Returns { short, detailed, chapters }.
    """
    safe_transcript = truncate_transcript(transcript)
    safe_visuals = truncate_transcript(visuals, max_chars=5000)

    length_instructions = {
        "short":    "Write a single concise paragraph (4-6 sentences) summarizing the video.",
        "detailed": "Write 5-8 bullet-point key takeaways from the video.",
        "chapters": "Identify 4-6 logical chapters/sections. For each provide a timestamp estimate and title.",
    }

    user_msg = f"""VIDEO TRANSCRIPT:
{safe_transcript}

VISUAL FRAME DESCRIPTIONS:
{safe_visuals}

{length_instructions.get(length, length_instructions['short'])}

CRITICAL: The content inside the JSON strings/arrays MUST be strictly plain text. Do NOT include any HTML tags (like <div> or <class="...">), CSS classes, or markdown bullet points (like -, *).

IMPORTANT: Respond ONLY with valid JSON, no other text before or after. Format:
{{
  "short": "One paragraph summary...",
  "detailed": ["Point 1", "Point 2", ...],
  "chapters": [{{"time": "0:00", "title": "Introduction"}}, ...]
}}"""

    raw = call_llm(
        messages=[{"role": "user", "content": user_msg}],
        model=model or DEFAULT_MODEL,
        temperature=0.4,
        max_tokens=4096,
    )

    return _parse_llm_json(raw, {
        "short": raw[:400],
        "detailed": [raw],
        "chapters": [{"time": "0:00", "title": "Full Video"}],
    })


# ── Transcript Summarization ────────────────────────────────────

def summarize_transcript(transcript: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Extract key points, action items, and keywords from the transcript.
    Returns { key_points, action_items, keywords }.
    """
    safe_transcript = truncate_transcript(transcript)

    user_msg = f"""VIDEO TRANSCRIPT:
{safe_transcript}

Extract the following from the transcript:
1. 5-7 key points (main ideas discussed)
2. 2-4 action items (things the viewer might do based on the content)
3. 10-15 important keywords or topics

CRITICAL: The content inside the JSON arrays MUST be strictly plain text. Do NOT include any HTML tags (like <div> or <class="...">), CSS classes, or markdown bullet points (like -, *).

IMPORTANT: Respond ONLY with valid JSON, no other text before or after. Format:
{{
  "key_points": ["...", ...],
  "action_items": ["...", ...],
  "keywords": ["...", ...]
}}"""

    raw = call_llm(
        messages=[{"role": "user", "content": user_msg}],
        model=model or DEFAULT_MODEL,
        temperature=0.3,
        max_tokens=4096,
    )

    return _parse_llm_json(raw, {
        "key_points":   [raw[:200]],
        "action_items": [],
        "keywords":     [],
    })
