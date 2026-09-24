# AI Model Comparisons for VideoQA Project

This document provides a comparison of the different Speech-to-Text (STT) and Large Language Models (LLMs) experimented with or implemented in this project so far. The comparison is based on the project's requirements for multimodal video analysis.

## Speech-to-Text (STT) Models

| Name of Model | Accuracy | Problem / Limitations |
| :--- | :--- | :--- |
| **faster-whisper (Base)**<br>*(Current Default)* | **Moderate to Good** (~85-90%). Very fast real-time transcription, highly optimized for CPU. | Can struggle with heavy accents, thick background noise, or overlapping speakers. Produces occasional "hallucinations" (repeated words) if audio is unclear. |
| **OpenAI Whisper (Medium)**<br>*(Previously Tested/Reported)* | **High** (~92-95%). Better language comprehension than base, handles varying accents well. | **Compute Intensive:** Requires significant RAM/VRAM to run locally. Transcription is very slow on low-end hardware or CPU-only setups. |

---

## Large Language Models (LLMs)

*Note: These models are accessed via cloud API routing (OpenRouter / Pollinations).*

| Name of Model | Accuracy | Problem / Limitations |
| :--- | :--- | :--- |
| **meta-llama/llama-3.3-70b-instruct**<br>*(Current Default)* | **Very High**. Excellent instruction following and reasoning for multimodal contextual prompts. | Subject to strict rate limiting on free API tiers (429 errors). Can sometimes be overly verbose in its reasoning. |
| **mistralai/mistral-7b-instruct** <br>*(Original Implementation)* | **Moderate**. Fast response times, adequate for basic summarization and direct questions. | Smaller parameter size means it occasionally lacks deep reasoning and struggles with very long or complex transcript+visual prompts. |
| **qwen/qwen-2.5-72b-instruct**<br>*(Primary Fallback)* | **High**. Strong performance on complex, long-context QA. | Can occasionally have different formatting quirks that break strict JSON parsing requirements compared to Llama. |
| **deepseek/deepseek-r1-0528**<br>*(Reasoning Fallback)* | **Very High**. Exceptional at step-by-step logic and identifying exact timestamps correctly. | Noticeably slower response times due to heavy "thinking" overhead. Hits OpenRouter rate limits very quickly out of the free tier. |
| **google/gemma-3-27b-it**<br>*(Fallback)* | **Good**. Efficient balance of speed and logical deduction. | Smaller context windows or worse performance on niche languages compared to OpenAI or LLaMA models. |
| **Pollinations AI (OpenAI/GPT-4o)**<br>*(Emergency Keyless Fallback)* | **Very High** (State-of-the-art). Highly robust at handling poorly formatted transcripts. | Relies on an undocumented third-party proxy wrapper. Lacks concrete guarantees on privacy, uptime, or consistent formatting compared to using an official authenticated API. |
| **meta-llama/llama-3.2-3b-instruct** &<br>**nvidia/nemotron-nano-9b**<br>*(Lightweight Fallbacks)* | **Low to Moderate**. Extremely fast generation speeds. | Frequently fails to follow strict JSON formatting instructions. Prone to hallucinating answers not found in the video context due to low parameter count. |
