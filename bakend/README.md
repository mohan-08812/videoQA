# VideoQA – Backend Setup

## What It Does
A **FastAPI** REST server powering the VideoQA premium UI.

| Step | Technology |
|------|------------|
| 🔊 Speech-to-Text | **Whisper-medium** (OpenAI) – ~50% better than `base` |
| 👁️ Vision Captions | **BLIP-large** (Salesforce) – rich visual understanding |
| 🧠 LLM Reasoning | **Mistral-7B-Instruct** via OpenRouter (free, open-weight) |
| 🎬 Clip Extraction | **MoviePy** + smart keyframe detection (OpenCV) |

---

## Quick Start (Windows)

```bash
# 1. Navigate to backend folder
cd c:\Users\mohan\OneDrive\Desktop\videoqa\backend

# 2. Run the startup script (creates venv, installs deps, starts server)
start.bat
```

Or manually:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The server starts at **http://localhost:8000**
API docs (interactive): **http://localhost:8000/docs**

---

## Configuration (`.env`)

| Variable | Default | Notes |
|----------|---------|-------|
| `OPENROUTER_API_KEY` | _(required)_ | Get free key at [openrouter.ai](https://openrouter.ai) |
| `WHISPER_MODEL` | `medium` | Options: `tiny`, `base`, `small`, `medium`, `large` |
| `LLM_MODEL` | `mistralai/mistral-7b-instruct` | Any OpenRouter model ID |
| `MAX_FRAMES` | `6` | Keyframes to extract per video |
| `CLIP_DURATION` | `5` | Seconds for each answer clip |

---

## Alternative LLM Models (change `LLM_MODEL` in `.env`)

| Model | OpenRouter ID | Speed | Quality |
|-------|--------------|-------|---------|
| **Mistral 7B** *(default)* | `mistralai/mistral-7b-instruct` | ⚡⚡⚡ | ★★★★ |
| LLaMA 3 8B | `meta-llama/llama-3-8b-instruct` | ⚡⚡⚡ | ★★★★ |
| Gemma 2 9B | `google/gemma-2-9b-it` | ⚡⚡ | ★★★★ |
| Qwen 2 72B | `qwen/qwen-2-72b-instruct` | ⚡ | ★★★★★ |
| Phi-3 Medium | `microsoft/phi-3-medium-128k-instruct` | ⚡⚡ | ★★★★ |

---

## Connect Frontend to Backend

Open `api.js` in the `videoqa/` folder and change:

```js
// Before (demo mode)
const MOCK_MODE = true;

// After (real backend)
const MOCK_MODE = false;
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/process_video` | Upload video → transcript + visuals |
| `POST` | `/ask` | Ask question → answer + clip |
| `POST` | `/summarize_video` | Generate video summary |
| `POST` | `/summarize_transcript` | Extract key points + keywords |
| `GET`  | `/download/clip/{file}` | Stream the relevant clip |
| `GET`  | `/download/transcript/{session}` | Download full transcript |
| `GET`  | `/health` | Health check |
| `GET`  | `/docs` | Interactive Swagger UI |

---

## System Requirements

- Python 3.10+
- 4 GB RAM minimum (8 GB recommended for BLIP-large)
- GPU optional but recommended for BLIP (CUDA auto-detected)
- FFmpeg installed (required by MoviePy) → `choco install ffmpeg` or download from ffmpeg.org
