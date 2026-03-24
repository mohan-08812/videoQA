"""
llm.py – OpenRouter LLM integration
Supports multiple free models with automatic fallback on rate-limit (429) errors.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Fallback chain: tried in order when a model is rate-limited or unavailable ──
FREE_MODEL_FALLBACKS = [
    "meta-llama/llama-3.3-70b-instruct:free",           # LLaMA 3.3 70B       – best quality
    "google/gemma-3-27b-it:free",                        # Gemma 3 27B         – Google
    "qwen/qwen-2.5-72b-instruct:free",                   # Qwen 2.5 72B        – Alibaba
    "mistralai/mistral-small-3.1-24b-instruct:free",     # Mistral Small 24B   – fast
    "nousresearch/hermes-3-llama-3.1-405b:free",         # Hermes 3 405B       – powerful
    "nvidia/nemotron-nano-9b-v2:free",                   # Nemotron 9B         – NVIDIA
    "deepseek/deepseek-r1-0528:free",                    # DeepSeek R1         – reasoning
    "microsoft/phi-4:free",                              # Phi-4               – Microsoft
    "openai/gpt-oss-20b:free",                           # GPT-OSS 20B         – OpenAI open
    "meta-llama/llama-3.2-3b-instruct:free",             # LLaMA 3.2 3B        – lightest
]

# ── Available open-source models (all free on OpenRouter) ────
SUPPORTED_MODELS = {
    "llama-3.3-70b":    FREE_MODEL_FALLBACKS[0],
    "gemma-3-27b":      FREE_MODEL_FALLBACKS[1],
    "qwen-2.5-72b":     FREE_MODEL_FALLBACKS[2],
    "mistral-small":    FREE_MODEL_FALLBACKS[3],
    "hermes-405b":      FREE_MODEL_FALLBACKS[4],
    "nemotron-9b":      FREE_MODEL_FALLBACKS[5],
    "deepseek-r1":      FREE_MODEL_FALLBACKS[6],
    "phi-4":            FREE_MODEL_FALLBACKS[7],
    "gpt-oss-20b":      FREE_MODEL_FALLBACKS[8],
    "llama-3.2-3b":     FREE_MODEL_FALLBACKS[9],
}


# ── Single model call ────────────────────────────────────────

def _call_single(messages: list[dict], model: str, temperature: float) -> str:
    """Call one specific model. Raises RateLimitError on 429, SkipModelError on 404, RuntimeError otherwise."""
    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  "https://videoqa.local",
            "X-Title":       "VideoQA",
        },
        json={
            "model":       model,
            "messages":    messages,
            "temperature": temperature,
            "max_tokens":  1024,
        },
        timeout=60,
    )
    if resp.status_code == 429:
        raise RateLimitError(f"Rate-limited on {model}")
    if resp.status_code == 404:
        raise SkipModelError(f"Model not found: {model}")
    if resp.status_code != 200:
        raise SkipModelError(f"OpenRouter error {resp.status_code} on {model}: {resp.text[:200]}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected OpenRouter response: {data}") from e


class RateLimitError(Exception):
    pass

class SkipModelError(Exception):
    pass


# ── Core LLM call with fallback chain ───────────────────────

def call_llm(messages: list[dict], model: str = DEFAULT_MODEL, temperature: float = 0.4) -> str:
    """
    Call OpenRouter with automatic fallback across FREE_MODEL_FALLBACKS.
    Skips models that return 429 (rate-limit) or 404 (not found) and tries the next.
    """
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY is not set in .env")

    # Requested model first, then remaining fallbacks (deduped)
    chain = [model] + [m for m in FREE_MODEL_FALLBACKS if m != model]

    last_error = None
    for attempt_model in chain:
        try:
            print(f"[LLM] Trying: {attempt_model}")
            result = _call_single(messages, attempt_model, temperature)
            if attempt_model != model:
                print(f"[LLM] ✅ Used fallback: {attempt_model}")
            return result
        except (RateLimitError, SkipModelError) as e:
            print(f"[LLM] ⚠️  Skipping {attempt_model}: {e}")
            last_error = e
            continue
        except Exception as e:
            print(f"[LLM] ❌ Unexpected error on {attempt_model}: {e}")
            last_error = e
            continue

    raise RuntimeError(f"All {len(chain)} models exhausted. Last error: {last_error}")


# ── QA ────────────────────────────────────────────────────────

def answer_question(
    question: str,
    transcript: str,
    visuals: str,
    language: str = "English",
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Generate a detailed answer grounded in transcript + visual captions.
    Returns { answer, transcript_excerpts, visual_captions_used, confidence }.
    """
    system_msg = (
        "You are an expert multimodal video analyst. "
        "You will be given a video transcript and visual frame descriptions. "
        "Answer the user's question thoroughly and accurately, citing specific parts of the transcript. "
        "If the answer is not clearly in the video, say so honestly."
    )

    user_msg = f"""VIDEO TRANSCRIPT:
{transcript}

VISUAL FRAME DESCRIPTIONS:
{visuals}

QUESTION: {question}

Instructions:
- Answer in {language}.
- Be detailed but concise (3-6 sentences).
- Bold key terms using **term** markdown.
- Extract 1-2 most relevant transcript sentences as evidence.
- Extract 1-2 most relevant visual captions as evidence.
- Rate your confidence as: High / Medium / Low.

Format your response as valid JSON:
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
    )

    # Parse JSON from response
    try:
        # Strip markdown code fences if present
        clean = raw.strip()
        if clean.startswith("```"):
            clean = "\n".join(clean.split("\n")[1:])
            if clean.endswith("```"):
                clean = clean[:-3]
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        # Fallback: return raw text as answer
        return {
            "answer": raw,
            "transcript_excerpts": [],
            "visual_captions": [],
            "confidence": "Medium",
            "confidence_reason": "Based on transcript + visual frames",
        }


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
    length_instructions = {
        "short":    "Write a single concise paragraph (4-6 sentences) summarizing the video.",
        "detailed": "Write 5-8 bullet-point key takeaways from the video.",
        "chapters": "Identify 4-6 logical chapters/sections. For each provide a timestamp estimate and title.",
    }

    user_msg = f"""VIDEO TRANSCRIPT:
{transcript}

VISUAL FRAME DESCRIPTIONS:
{visuals}

{length_instructions.get(length, length_instructions['short'])}

Format as JSON:
{{
  "short": "One paragraph summary...",
  "detailed": ["Point 1", "Point 2", ...],
  "chapters": [{{"time": "0:00", "title": "Introduction"}}, ...]
}}"""

    raw = call_llm(
        messages=[{"role": "user", "content": user_msg}],
        model=model or DEFAULT_MODEL,
        temperature=0.4,
    )

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = "\n".join(clean.split("\n")[1:]).rstrip("` \n")
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        return {
            "short": raw[:400],
            "detailed": [raw],
            "chapters": [{"time": "0:00", "title": "Full Video"}],
        }


# ── Transcript Summarization ────────────────────────────────────

def summarize_transcript(transcript: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Extract key points, action items, and keywords from the transcript.
    Returns { key_points, action_items, keywords }.
    """
    user_msg = f"""VIDEO TRANSCRIPT:
{transcript}

Extract the following from the transcript:
1. 5-7 key points (main ideas discussed)
2. 2-4 action items (things the viewer might do based on the content)
3. 10-15 important keywords or topics

Format as JSON:
{{
  "key_points": ["...", ...],
  "action_items": ["...", ...],
  "keywords": ["...", ...]
}}"""

    raw = call_llm(
        messages=[{"role": "user", "content": user_msg}],
        model=model or DEFAULT_MODEL,
        temperature=0.3,
    )

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = "\n".join(clean.split("\n")[1:]).rstrip("` \n")
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        return {
            "key_points":   [raw[:200]],
            "action_items": [],
            "keywords":     [],
        }
