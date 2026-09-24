<div align="center">
  <h1>🎥 VideoQA: Multimodal Video Intelligence</h1>
  <p><strong>Chat with your videos: An advanced AI pipeline for instant video-based question answering, summarization, and clip extraction.</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-00a393.svg)](https://fastapi.tiangolo.com)
  [![Gemini](https://img.shields.io/badge/Gemini-3.6_Flash-orange.svg)](https://deepmind.google/technologies/gemini/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

## 📌 Overview

VideoQA transforms how you interact with long-form video content. Instead of scrubbing through hours of footage, simply ask a question. Using a state-of-the-art multimodal AI pipeline, VideoQA analyzes both the **audio transcript** and **visual frames** to provide highly accurate, grounded answers, complete with time-stamped evidence and automatically extracted video clips.

Designed for researchers, students, and content creators, VideoQA saves time by turning passive video watching into active, intelligent querying.

## ✨ Key Features

- **🧠 Multimodal Understanding**: Leverages Google's Gemini 3.6 Flash and OpenRouter LLMs to reason over both video and audio simultaneously.
- **🎙️ High-Fidelity Transcription**: Uses Whisper (int8 optimized) for lightning-fast, highly accurate speech-to-text.
- **🖼️ Smart Frame Extraction**: Intelligently samples keyframes based on scene changes, not just fixed intervals.
- **✂️ Auto-Clip Generation**: Automatically cuts and downloads the specific video segment containing the answer.
- **📝 Intelligent Summarization**: Generates short summaries, detailed bullet points, and logical chapters from any video.
- **⚡ Resilient Architecture**: Built-in exponential backoff, rate-limit tracking, and a 3-tier LLM fallback chain ensures the app stays online even during API outages.

## 🏗️ Tech Stack

- **Frontend**: Vanilla HTML/CSS/JS (Dynamic, responsive, and lightweight)
- **Backend**: Python, FastAPI, Uvicorn
- **AI/ML Models**: 
  - **Primary LLM**: Gemini 3.6 Flash (via `google-genai`)
  - **Fallback LLMs**: OpenRouter (LLaMA 3, Gemma, Mistral)
  - **Audio**: Faster-Whisper
  - **Vision**: BLIP-base (Salesforce)
- **Media Processing**: FFmpeg, OpenCV, yt-dlp

## 📸 Preview

*(Placeholder: Add a GIF or screenshot of the UI in action here!)*

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to your system PATH.

### 1. Clone the repository
```bash
git clone https://github.com/mohan-08812/videoQA.git
cd videoQA
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
LLM_MODEL=gemini-3.6-flash
WHISPER_MODEL=small
MAX_FRAMES=5
```
*(Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey))*

### 4. Run the Application
```bash
# From the backend directory, start the server:
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to `http://localhost:8000`.

## 💡 Usage Example

1. **Upload**: Drag and drop an MP4 file or paste a YouTube URL.
2. **Process**: The system will transcribe audio, extract visual keyframes, and process the video.
3. **Ask**: Type a question like *"What ingredients were added to the pan?"*
4. **Review**: Instantly receive a detailed text answer, transcript citations, and a downloadable video clip of the exact moment.

## 📂 Folder Structure

```
videoQA/
├── backend/
│   ├── main.py              # FastAPI application & endpoints
│   ├── llm.py               # LLM integration, retries, rate limiting
│   ├── gemini_pipeline.py   # Native multimodal Gemini integration
│   ├── models.py            # Whisper & BLIP model management
│   ├── video_utils.py       # FFmpeg/OpenCV processing logic
│   └── requirements.txt     # Python dependencies
├── index.html               # Main frontend interface
├── app.js                   # Frontend application logic
├── api.js                   # Client-server communication
└── style.css                # Application styling
```

## 🚧 Known Limitations & Future Work

- **YouTube Bot Detection**: `yt-dlp` occasionally triggers YouTube's anti-bot protections. Supplying a `cookies.txt` file mitigates this.
- **Large File Processing**: Very large videos (>1 hour) may take several minutes to process locally depending on CPU/GPU capabilities.
- **Future Improvements**:
  - Add semantic search across video chapters.
  - Implement WebSockets for real-time processing progress bars.
  - Add user authentication and history saving.

## 👨‍💻 Author

**Mohan**
- 🔗 LinkedIn: [*(Placeholder: Add your LinkedIn profile link here)*](#)
- 💻 GitHub: [@mohan-08812](https://github.com/mohan-08812)
- 📧 Contact: [*(Placeholder: Add your email here)*](#)

---
*If you found this project helpful, please consider giving it a ⭐ on GitHub!*
