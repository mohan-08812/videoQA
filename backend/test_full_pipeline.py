"""
test_full_pipeline.py – End-to-end test of the VideoQA pipeline
================================================================
Tests the complete pipeline: LLM calls (Gemini 2.0 Flash), JSON parsing,
error handling, rate limiting, and fallback behavior.

Run from the backend/ directory:
    python test_full_pipeline.py
"""

import os
import sys
import json
import time
import traceback

# Ensure we can import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


# ══════════════════════════════════════════════════════════════
# TEST UTILITIES
# ══════════════════════════════════════════════════════════════

class TestResults:
    def __init__(self):
        self.results = []

    def record(self, name: str, passed: bool, detail: str = "", elapsed: float = 0.0):
        self.results.append({
            "name": name,
            "passed": passed,
            "detail": detail,
            "elapsed_sec": round(elapsed, 2),
        })
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}  ({elapsed:.2f}s)")
        if detail:
            # Truncate long details
            detail_preview = detail[:300] + "..." if len(detail) > 300 else detail
            print(f"         → {detail_preview}")

    def summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        print(f"\n{'='*60}")
        print(f"  TEST RESULTS: {passed}/{total} passed, {failed} failed")
        print(f"{'='*60}")
        if failed > 0:
            print("\n  Failed tests:")
            for r in self.results:
                if not r["passed"]:
                    print(f"    ❌ {r['name']}: {r['detail'][:200]}")
        print()
        return failed == 0


results = TestResults()


# ══════════════════════════════════════════════════════════════
# TEST 1: Configuration Validation
# ══════════════════════════════════════════════════════════════

def test_configuration():
    """Verify .env keys are loaded and not placeholders."""
    print("\n── Test 1: Configuration Validation ──")

    from llm import GEMINI_API_KEY, OPENROUTER_API_KEY, _is_placeholder_key

    t0 = time.time()

    # Check Gemini key
    gemini_ok = bool(GEMINI_API_KEY) and not _is_placeholder_key(GEMINI_API_KEY)
    results.record(
        "Gemini API key is valid (not placeholder)",
        gemini_ok,
        f"Key starts with: {GEMINI_API_KEY[:8]}..." if gemini_ok else "Key is missing or placeholder!",
        time.time() - t0,
    )

    # Check placeholder detection works
    t0 = time.time()
    assert _is_placeholder_key("your_gemini_api_key_here") == True
    assert _is_placeholder_key("") == True
    assert _is_placeholder_key("AIzaSyAbc123") == False
    results.record(
        "Placeholder detection logic works",
        True,
        "Correctly identifies placeholders vs real keys",
        time.time() - t0,
    )

    return gemini_ok


# ══════════════════════════════════════════════════════════════
# TEST 2: Gemini 2.0 Flash Direct Call
# ══════════════════════════════════════════════════════════════

def test_gemini_direct():
    """Test a direct call to Gemini 2.0 Flash API."""
    print("\n── Test 2: Gemini 2.0 Flash Direct Call ──")

    from llm import _call_gemini, RateLimitError, AuthError, SkipModelError

    t0 = time.time()
    try:
        response = _call_gemini(
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Reply concisely."},
                {"role": "user", "content": "What is 2 + 2? Reply with just the number."},
            ],
            model="gemini-3.6-flash",
            temperature=0.1,
            max_tokens=50,
        )
        elapsed = time.time() - t0
        has_4 = "4" in response
        results.record(
            "Gemini 2.0 Flash responds correctly",
            has_4,
            f"Response: '{response}'",
            elapsed,
        )
        return True

    except AuthError as e:
        results.record("Gemini 2.0 Flash responds correctly", False, f"Auth error: {e}", time.time() - t0)
        return False
    except RateLimitError as e:
        results.record("Gemini 2.0 Flash responds correctly", False, f"Rate limited: {e}", time.time() - t0)
        return False
    except Exception as e:
        results.record("Gemini 2.0 Flash responds correctly", False, f"Error: {e}", time.time() - t0)
        return False


# ══════════════════════════════════════════════════════════════
# TEST 3: call_llm with Full Fallback Chain
# ══════════════════════════════════════════════════════════════

def test_call_llm_fallback():
    """Test the full call_llm function with fallback chain."""
    print("\n── Test 3: call_llm with Fallback Chain ──")

    from llm import call_llm

    t0 = time.time()
    try:
        response = call_llm(
            messages=[
                {"role": "user", "content": "Name three primary colors. Reply briefly."},
            ],
            temperature=0.2,
            max_tokens=100,
        )
        elapsed = time.time() - t0
        has_content = len(response) > 10
        results.record(
            "call_llm returns a response (with fallback)",
            has_content,
            f"Response ({len(response)} chars): '{response[:150]}'",
            elapsed,
        )
        return True
    except Exception as e:
        results.record("call_llm returns a response", False, f"Error: {e}", time.time() - t0)
        return False


# ══════════════════════════════════════════════════════════════
# TEST 4: JSON Parsing Robustness
# ══════════════════════════════════════════════════════════════

def test_json_parsing():
    """Test the robust JSON parser with various LLM output formats."""
    print("\n── Test 4: JSON Parsing Robustness ──")

    from llm import _parse_llm_json

    fallback = {"answer": "", "confidence": "Low"}

    # Test 1: Clean JSON
    t0 = time.time()
    result = _parse_llm_json('{"answer": "Hello", "confidence": "High"}', fallback)
    results.record(
        "Parse clean JSON",
        result.get("answer") == "Hello",
        f"Got: {result}",
        time.time() - t0,
    )

    # Test 2: JSON in markdown code fence
    t0 = time.time()
    raw = '```json\n{"answer": "World", "confidence": "Medium"}\n```'
    result = _parse_llm_json(raw, fallback)
    results.record(
        "Parse JSON in markdown code fence",
        result.get("answer") == "World",
        f"Got: {result}",
        time.time() - t0,
    )

    # Test 3: JSON with surrounding text
    t0 = time.time()
    raw = 'Here is my response:\n{"answer": "Test", "confidence": "High"}\nHope that helps!'
    result = _parse_llm_json(raw, fallback)
    results.record(
        "Parse JSON embedded in text",
        result.get("answer") == "Test",
        f"Got: {result}",
        time.time() - t0,
    )

    # Test 4: JSON with trailing comma (common LLM mistake)
    t0 = time.time()
    raw = '{"answer": "Comma", "confidence": "High",}'
    result = _parse_llm_json(raw, fallback)
    results.record(
        "Parse JSON with trailing comma",
        result.get("answer") == "Comma",
        f"Got: {result}",
        time.time() - t0,
    )

    # Test 5: Completely non-JSON response
    t0 = time.time()
    raw = "This is just plain text, not JSON at all."
    result = _parse_llm_json(raw, fallback)
    results.record(
        "Fallback on non-JSON response",
        "answer" in result and len(result["answer"]) > 0,
        f"Got: {result}",
        time.time() - t0,
    )


# ══════════════════════════════════════════════════════════════
# TEST 5: Transcript Truncation
# ══════════════════════════════════════════════════════════════

def test_transcript_truncation():
    """Test transcript truncation for very long videos."""
    print("\n── Test 5: Transcript Truncation ──")

    from llm import truncate_transcript

    t0 = time.time()

    # Short text — no truncation
    short = "Hello world"
    result = truncate_transcript(short, max_chars=100)
    results.record(
        "Short text not truncated",
        result == short,
        f"Input: {len(short)} chars, Output: {len(result)} chars",
        time.time() - t0,
    )

    # Long text — should be truncated
    t0 = time.time()
    long_text = "A" * 50000
    result = truncate_transcript(long_text, max_chars=10000)
    results.record(
        "Long text truncated with markers",
        len(result) < len(long_text) and "omitted" in result,
        f"Input: {len(long_text)} chars, Output: {len(result)} chars",
        time.time() - t0,
    )


# ══════════════════════════════════════════════════════════════
# TEST 6: Rate Limit Tracking
# ══════════════════════════════════════════════════════════════

def test_rate_limit_tracking():
    """Test rate-limit tracking and quota management."""
    print("\n── Test 6: Rate Limit Tracking ──")

    from llm import get_rate_limit_status, _gemini_available, _block_gemini, _rate_state

    t0 = time.time()
    status = get_rate_limit_status()
    results.record(
        "Rate limit status returns valid data",
        "gemini_available" in status and "gemini_rpm_limit" in status,
        f"Status: {status}",
        time.time() - t0,
    )

    # Test blocking
    t0 = time.time()
    _block_gemini(2.0)  # Block for 2 seconds
    blocked = not _gemini_available()
    results.record(
        "Gemini correctly blocked after rate limit",
        blocked,
        "Gemini is blocked as expected",
        time.time() - t0,
    )

    # Unblock for remaining tests
    _rate_state["gemini_blocked_until"] = 0.0


# ══════════════════════════════════════════════════════════════
# TEST 7: answer_question (Full QA Pipeline)
# ══════════════════════════════════════════════════════════════

def test_answer_question():
    """Test the full answer_question function with realistic input."""
    print("\n── Test 7: answer_question (Full QA Pipeline) ──")

    from llm import answer_question

    # Simulated transcript from a cooking video
    transcript = """
    Welcome to today's cooking tutorial! Today we're making a classic Italian pasta dish - 
    Spaghetti Aglio e Olio. You'll need spaghetti, garlic, olive oil, red pepper flakes, 
    and fresh parsley. First, cook the spaghetti in salted boiling water until al dente, 
    about 8-10 minutes. While that's cooking, slice 6 cloves of garlic thinly and heat 
    olive oil in a large pan over medium heat. Add the garlic and cook until golden, about 
    2 minutes. Be careful not to burn it! Add red pepper flakes to taste. When the pasta 
    is done, reserve a cup of pasta water before draining. Add the pasta to the pan with 
    the garlic oil and toss well, adding pasta water as needed to create a silky sauce. 
    Finish with fresh parsley and a drizzle of good olive oil. Serve immediately!
    """

    visuals = """
    [0:00] A kitchen counter with ingredients laid out: spaghetti, garlic, olive oil
    [0:45] A pot of water boiling on the stove
    [1:30] Hands slicing garlic cloves thinly on a cutting board
    [2:15] Garlic sizzling in olive oil in a large pan
    [3:00] Finished pasta dish plated with parsley garnish
    """

    questions_and_checks = [
        (
            "What ingredients do I need for this recipe?",
            ["spaghetti", "garlic", "olive oil"],
            "Ingredient question",
        ),
        (
            "How long should I cook the pasta?",
            ["8", "10", "minute", "al dente"],
            "Time/duration question",
        ),
        (
            "What should I be careful about when cooking the garlic?",
            ["burn", "golden", "careful"],
            "Procedure/technique question",
        ),
    ]

    for question, expected_keywords, label in questions_and_checks:
        t0 = time.time()
        try:
            result = answer_question(
                question=question,
                transcript=transcript,
                visuals=visuals,
                language="English",
            )
            elapsed = time.time() - t0

            answer = result.get("answer", "").lower()
            has_answer = len(answer) > 20
            has_keyword = any(kw.lower() in answer for kw in expected_keywords)
            has_confidence = result.get("confidence", "") in ("High", "Medium", "Low")

            passed = has_answer and has_keyword and has_confidence
            results.record(
                f"QA: {label}",
                passed,
                f"Answer: '{result.get('answer', '')[:150]}' | Confidence: {result.get('confidence', 'N/A')}",
                elapsed,
            )
        except Exception as e:
            results.record(f"QA: {label}", False, f"Error: {e}", time.time() - t0)


# ══════════════════════════════════════════════════════════════
# TEST 8: summarize_video
# ══════════════════════════════════════════════════════════════

def test_summarize_video():
    """Test video summarization."""
    print("\n── Test 8: summarize_video ──")

    from llm import summarize_video

    transcript = """
    In this video we explore the basics of machine learning. Machine learning is a subset 
    of artificial intelligence that allows systems to learn from data without being explicitly 
    programmed. There are three main types: supervised learning, unsupervised learning, and 
    reinforcement learning. Supervised learning uses labeled data to train models. Common 
    applications include image recognition, natural language processing, and recommendation 
    systems. We demonstrate a simple linear regression example using Python and scikit-learn.
    """

    visuals = "[0:00] Title slide: Machine Learning Basics\n[1:00] Diagram of ML types\n[2:00] Python code on screen"

    t0 = time.time()
    try:
        result = summarize_video(
            transcript=transcript,
            visuals=visuals,
            length="short",
        )
        elapsed = time.time() - t0
        has_short = bool(result.get("short")) and len(result.get("short", "")) > 20
        results.record(
            "Video summary (short)",
            has_short,
            f"Summary: '{str(result.get('short', ''))[:200]}'",
            elapsed,
        )
    except Exception as e:
        results.record("Video summary (short)", False, f"Error: {e}", time.time() - t0)


# ══════════════════════════════════════════════════════════════
# TEST 9: summarize_transcript
# ══════════════════════════════════════════════════════════════

def test_summarize_transcript():
    """Test transcript summarization (key points, action items, keywords)."""
    print("\n── Test 9: summarize_transcript ──")

    from llm import summarize_transcript

    transcript = """
    Today we'll discuss five essential productivity tips for remote workers. 
    First, establish a dedicated workspace separate from your living area. 
    Second, maintain a consistent daily schedule with fixed start and end times. 
    Third, use the Pomodoro technique - work for 25 minutes, break for 5. 
    Fourth, minimize distractions by using website blockers during focus time. 
    Fifth, take regular exercise breaks to maintain physical and mental health. 
    Remember, productivity isn't about working more hours, it's about working smarter.
    """

    t0 = time.time()
    try:
        result = summarize_transcript(transcript=transcript)
        elapsed = time.time() - t0
        has_key_points = isinstance(result.get("key_points"), list) and len(result.get("key_points", [])) > 0
        has_keywords = isinstance(result.get("keywords"), list) and len(result.get("keywords", [])) > 0
        passed = has_key_points and has_keywords
        results.record(
            "Transcript summarization",
            passed,
            f"Key points: {len(result.get('key_points', []))}, Keywords: {len(result.get('keywords', []))}",
            elapsed,
        )
    except Exception as e:
        results.record("Transcript summarization", False, f"Error: {e}", time.time() - t0)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  VideoQA Pipeline – Full End-to-End Test Suite")
    print("=" * 60)

    t_total = time.time()

    # Run all tests
    gemini_ok = test_configuration()
    gemini_works = test_gemini_direct()
    test_call_llm_fallback()
    test_json_parsing()
    test_transcript_truncation()
    test_rate_limit_tracking()

    if gemini_works or True:  # Run QA tests even if Gemini fails (tests fallback)
        test_answer_question()
        test_summarize_video()
        test_summarize_transcript()

    total_time = time.time() - t_total
    print(f"\n  Total test time: {total_time:.1f}s")
    all_passed = results.summary()

    sys.exit(0 if all_passed else 1)
