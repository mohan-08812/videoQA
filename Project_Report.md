# Project Report: Intelligent Video Question Answering (VideoQA) System

## Abstract
The rapid growth of video content across various platforms has created a significant need for intelligent systems capable of understanding and extracting specific information from videos. This project presents a multimodal Video Question Answering (VideoQA) system designed to allow users to interactively query video content using natural language. The proposed system leverages state-of-the-art artificial intelligence models, including OpenAI's Whisper for Speech-to-Text (STT) transcription, Salesforce's BLIP for visual captioning, and Mistral-7B (via OpenRouter) for Large Language Model (LLM) reasoning. A FastAPI backend orchestrates the processing pipeline, utilizing OpenCV and MoviePy for intelligent keyframe extraction and video clipping. The frontend provides a premium, user-friendly interface with voice input capabilities and read-aloud functionality. This report details the architecture, methodology, implementation, and evaluation of the VideoQA system, demonstrating its effectiveness in providing accurate answers and relevant video clips based on user queries.

## List of Figures
1. System Architecture Diagram
2. Data Flow Diagram (DFD) 
3. Use Case Diagram
4. System Workflow Diagram
5. Frontend User Interface Screenshot
6. Video Processing Pipeline

## List of Tables
1. AI Models Used and their Specifications
2. API Endpoints
3. Performance Analysis of Different LLMs
4. System Testing Results

## List of Abbreviations
*   **VideoQA:** Video Question Answering
*   **AI:** Artificial Intelligence
*   **LLM:** Large Language Model
*   **STT:** Speech-to-Text
*   **TTS:** Text-to-Speech
*   **API:** Application Programming Interface
*   **UI:** User Interface
*   **DFD:** Data Flow Diagram
*   **REST:** Representational State Transfer

---

## Chapter 1: Introduction

### 1.1 Background of the Study
With the exponential increase in video data generation in fields ranging from education to entertainment, manually searching for specific information within videos has become highly inefficient. Traditional search methods rely primarily on metadata or user-provided tags, which often fail to capture the nuanced content of the video. VideoQA systems bridge this gap by enabling users to ask natural language questions and receive precise answers based on the video's audio and visual content.

### 1.2 Problem Statement
Existing video search mechanisms are limited to keyword matching against titles or descriptions. They do not comprehend the actual multimodal content (audio transcript plus visual frames) of the video. Users waste significant time scanning through long videos to find specific segments or answers. There is a need for an intelligent system that can "watch" and "listen" to a video, understand the context, and answer user queries while pinpointing the exact timestamp of the relevant information.

### 1.3 Objectives of the Project
1.  To develop a multimodal pipeline that extracts both audio transcripts and visual captions from a given video.
2.  To integrate a Large Language Model (LLM) capable of reasoning over the extracted text to answer user queries accurately.
3.  To provide relevant video clips corresponding to the generated answers.
4.  To create an intuitive web interface supporting manual frame/time selection, voice input (speech-to-text), and read-aloud (text-to-speech) features.

### 1.4 Scope of the System
The system is scoped to process uploaded video files (e.g., MP4). It will transcribe the audio, extract keyframes at specified intervals, generate captions for these frames, and allow continuous Q&A interaction regarding the uploaded video. The system operates via a web application and is designed to handle short to medium-length videos efficiently.

### 1.5 Significance of the Project
This project provides a robust solution for content creators, students, and researchers who need to analyze video data quickly. By automating the extraction of key information and providing a conversational interface, the system significantly reduces the time and effort required for video analysis, improving productivity and accessibility.

### 1.6 Organization of the Report
Chapter 1 introduces the project. Chapter 2 reviews the existing literature on VideoQA and multimodal AI. Chapter 3 details the system architecture and design. Chapter 4 explains the methodology and algorithms used. Chapter 5 discusses the implementation details of both the frontend and backend. Chapter 6 presents the results and performance analysis. Chapter 7 concludes the report and discusses future enhancements.

---

## Chapter 2: Literature Review

*(Note: The headings below have been adapted from the sample index to align with the VideoQA domain while maintaining the structural intent).*

### 2.1 Overview of Video Question Answering Systems
VideoQA involves understanding both the visual frames and the accompanying audio/textual dialogue to answer natural language questions. Early systems relied heavily on handcrafted features and shallow machine learning models, which struggled to capture temporal dynamics and complex multimodal interactions.

### 2.2 Multimodal AI-Based Analysis Systems
Recent advancements in Deep Learning have shifted the paradigm towards multimodal AI. Models like CLIP (Contrastive Language-Image Pretraining) align visual and text representations. By combining temporal visual features with audio transcripts, modern systems can achieve a holistic understanding of the video content.

### 2.3 Existing Video Analysis and Retrieval Technologies
Current commercial platforms often use Automatic Speech Recognition (ASR) to index videos based on spoken words (e.g., YouTube's auto-generated transcripts). However, these platforms rarely allow users to query the aggregate visual context of the video. 

### 2.4 Machine Learning Applications in Video Analysis
Large Language Models (LLMs) and Vision-Language Models (VLMs) like BLIP (Bootstrapping Language-Image Pre-training) have proven highly effective in generating rich image captions. Similarly, models like OpenAI's Whisper have set new benchmarks in Speech-to-Text accuracy.

### 2.5 Limitations of Existing Systems
1.  **Computational Overhead:** Processing video frame-by-frame is highly resource-intensive.
2.  **Context Loss:** Fusing audio transcripts with visual captions without losing temporal context remains a challenge.
3.  **Lack of Interactivity:** Most systems do not provide an interactive chat interface with voice inputs and outputs.

### 2.6 Research Gap
While individual models for STT, visual captioning, and text generation exist, there is a lack of integrated, lightweight, and accessible web-based solutions that combine these models specifically for interactive VideoQA, featuring sub-clip generation and voice accessibility.

---

## Chapter 3: System Architecture and Design

### 3.1 Overview of the Proposed System
The proposed VideoQA system operates on a client-server architecture. The user uploads a video via the frontend web interface, which is sent to the FastAPI backend. The backend processes the video using Whisper (for audio) and BLIP (for visual keyframes), compiles a comprehensive context prompt, and uses the Mistral-7B LLM to answer subsequent user questions. 

### 3.2 System Architecture Diagram
*(A block diagram representing the interaction between the User Interface, FastAPI Server, Whisper Model, BLIP Model, OpenCV Video Processor, and OpenRouter LLM API.)*

### 3.3 Backend Components Description
*   **FastAPI Web Server:** Handles RESTful API requests.
*   **Video Processor (OpenCV/MoviePy):** Extracts an optimal number of keyframes and generates answer clips.
*   **Speech-to-Text Engine:** Utilizes OpenAI's `whisper-medium` model.
*   **Vision Engine:** Utilizes Salesforce's `BLIP-large` for image captioning.
*   **LLM Controller:** Manages API calls to OpenRouter (using `mistralai/mistral-7b-instruct`) for reasoning.

### 3.4 Frontend Components Description
*   **User Interface (HTML/CSS):** A premium, responsive design.
*   **Client Logic (Vanilla JS - app.js & api.js):** Handles API interactions, state management, and updates the DOM.
*   **Accessibility Modules:** Implements browser-based Speech Recognition (Voice Input) and Speech Synthesis (Read Aloud).

### 3.5 Data Flow Diagram (DFD)
1.  **Level 0:** User -> Video/Query -> VideoQA System -> Answer/Clip -> User.
2.  **Level 1:** Video Upload -> Video Splitting (Audio & Frames). Audio -> STT -> Transcript. Frames -> BLIP -> Visual Context. Query + Transcript + Context -> LLM -> Answer.

### 3.6 Use Case Diagram
*   **Actor:** User
*   **Use Cases:** Upload Video, Set Manual Selection (Frames/Time), Ask Question via Text, Ask Question via Voice, View Answer, Play Answer Clip, Listen to Answer (Read Aloud).

### 3.7 System Workflow
1. User uploads a video.
2. System extracts audio and transcribes it.
3. System extracts keyframes and generates captions.
4. User asks a question.
5. System prompts the LLM with the transcript, captions, and question.
6. LLM generates an answer and identifies relevant timestamps.
7. System cuts a video clip based on the timestamp and returns it to the UI.

---

## Chapter 4: Methodology

### 4.1 Data Acquisition from Video Inputs
When a video is uploaded, it is saved securely on the backend in the `uploads` directory. The system supports various video formats (e.g., MP4) and immediately validates the file integrity.

### 4.2 Video Processing and Frame Extraction Mechanism
To avoid processing every single frame, the system uses a smart keyframe extraction mechanism. Depending on configuration (`MAX_FRAMES`, default 6), OpenCV samples frames evenly across the video duration or focuses on significant scene changes. The user can also manually define start/end times and specific frames for processing through the UI.

### 4.3 Multimodal Feature Extraction (Audio/Visual)
1.  **Audio:** The extracted audio track is fed into the Whisper model, which provides highly accurate transcription along with timestamps.
2.  **Visual:** The extracted keyframes are passed to the BLIP model, which returns descriptive text captions representing the visual content of each frame.

### 4.4 Answer Generation via LLM
The transcript, visual captions, and their corresponding timestamps are structured into a prompt. This prompt is sent to the Mistral-7B LLM via OpenRouter. The LLM is instructed to answer the user's question based *only* on the provided context and to specify the timestamp where the answer is found.

### 4.5 Cloud Integration and APIs
The system integrates with OpenRouter APIs to access powerful cloud-based LLMs without requiring high-end local GPU resources for text generation. It also utilizes standard HTTP REST methodologies to communicate between the frontend and the local backend server.

### 4.6 Algorithms and Models Used
*   **ASR Algorithm:** Transformers-based sequence-to-sequence model (Whisper).
*   **Image Captioning:** Vision-Language Pre-training model (BLIP).
*   **Text Generation:** Autoregressive Language Model (Mistral 7B).
*   **Video Slicing:** FFmpeg-based library algorithms via MoviePy.

---

## Chapter 5: Implementation

### 5.1 Backend Implementation
The backend is built in Python using the FastAPI framework. It includes modules such as `main.py` (routing), `video_utils.py` (video manipulation with MoviePy and OpenCV), `llm.py` (OpenRouter API integration and prompt engineering), and `models.py` (Pydantic schemas for data validation).

### 5.2 Frontend Implementation
The frontend is constructed using plain HTML, CSS, and JavaScript, eschewing heavy frameworks for faster loading. The `app.js` file handles UI events, such as the drag-and-drop file upload, chatting interface, and the voice input logic using the Web Speech API. The `api.js` script manages the `fetch` calls to the backend endpoints (`/process_video`, `/ask`).

### 5.3 AI Model Integration
Models are integrated primarily through the `transformers` and `whisper` Python libraries. A virtual environment (`venv`) manages the dependencies defined in `requirements.txt` to ensure consistent execution.

### 5.4 Web Application Interface
The UI features a split-pane layout: a video player and setup panel on one side, and a conversational chat interface on the other. It includes features like customizable model selection, transcript viewing, and manual selection tools.

### 5.5 Integration of Processing and Communication Modules
When the user submits a Voice Input, the browser's SpeechRecognition API converts it to text, populates the input field, and triggers the API call. Upon receiving the response, the Web Speech Synthesis interface reads the answer aloud, while the UI simultaneously displays the generated video clip inline with the chat message.

---

## Chapter 6: Results and Discussion

### 6.1 Experimental Setup
The system was tested on a machine running Windows OS, utilizing Python 3.10. Testing involved videos ranging from 30 seconds to 5 minutes, encompassing instructional videos, news clips, and general dialogues.

### 6.2 System Testing
*   **Unit Testing:** Individual components (Whisper extraction, BLIP captioning) were tested for accuracy and execution time.
*   **Integration Testing:** The full pipeline from upload to VideoQA response was verified. Edge cases like uploading audio-only files or videos with no clear visuals were tested.
*   **Fallback Mechanism:** The LLM integration includes a fallback mechanism to automatically try secondary OpenRouter models if the primary model fails or rate-limits.

### 6.3 Performance Analysis
1.  **Transcription:** `whisper-medium` provided high accuracy, successfully handling moderate background noise.
2.  **Captioning:** `BLIP-large` accurately identified key objects and actions in keyframes.
3.  **Processing Time:** Video processing time scaled linearly with video length, largely dependent on local compute power for Whisper and BLIP. Answer generation was highly responsive (under 3 seconds) due to efficient cloud APIs.

### 6.4 Real-Time Query Results
The system successfully answered complex queries. For example, in an instructional video, asking "What tool is being used at the 2-minute mark?" yielded the correct textual answer (e.g., "A soldering iron") and returned the specific 5-second video clip showing the action.

### 6.5 Discussion of Results
The fusion of visual captions and audio transcripts into a unified LLM prompt proved highly effective. The addition of manual frame selection allowed users to correct the system if the automatic keyframe extraction missed nuanced visual details. The Voice Input and Read Aloud features significantly enhanced accessibility. 

---

## Chapter 7: Conclusion and Future Work

### 7.1 Conclusion
The developed VideoQA system successfully demonstrates a highly interactive, intelligent approach to video analysis. By utilizing state-of-the-art multimodal AI tools (Whisper, BLIP, and Mistral-7B), the project solves the problem of tedious manual video searching. The resultant web application is intuitive, accessible, and provides precise text and video-clip answers to temporal natural language queries.

### 7.2 Limitations of the System
1.  **Local Compute Heavy:** Running Whisper medium and BLIP large locally requires significant RAM/VRAM, making it slow on lower-end hardware.
2.  **Keyframe Density:** Rapid scene changes might be missed if the `MAX_FRAMES` parameter is set too low.
3.  **Context Window Limits:** Very long videos result in massive prompts that may exceed the context window limits of the LLM.

### 7.3 Future Enhancements
1.  **Cloud Offloading:** Moving Whisper and BLIP processing to cloud endpoints to reduce local hardware requirements.
2.  **Vector Database Integration:** Implementing embeddings and a vector database (like ChromaDB or Pinecone) to chunk and store long video transcripts, allowing the system to handle multi-hour videos via Retrieval-Augmented Generation (RAG).
3.  **Speaker Diarization:** Enhancing the audio transcription to identify and label different speakers in the video.

---

## References
1.  Radford, A., et al. (2022). Robust Speech Recognition via Large-Scale Weak Supervision (Whisper). OpenAI.
2.  Li, J., et al. (2022). BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation. Salesforce Research.
3.  Jiang, A. Q., et al. (2023). Mistral 7B. Mistral AI.
4.  Zulko, E. (2014). MoviePy: Video Editing with Python.
5.  FastAPI Documentation: https://fastapi.tiangolo.com/

---

## Appendices

### Appendix A – Source Code
*(Available in the project repository. Key files include `backend/main.py`, `backend/video_utils.py`, `frontend/app.js`, and `frontend/api.js`.)*

### Appendix B – Software/Hardware Specifications
*   **OS:** Windows 10/11
*   **Language:** Python 3.10+, JavaScript, HTML/CSS
*   **Libraries:** FastAPI, Uvicorn, transformers, whisper, moviepy, opencv-python, python-dotenv
*   **Hardware (Recommended):** 8GB RAM, Multi-core CPU, dedicated GPU (optional but recommended for faster local inference).

### Appendix C – User Manual / Screenshots
**User Workflow:**
1.  Open the application (`index.html` in browser).
2.  Drag and drop an MP4 video into the upload zone.
3.  (Optional) Specify Manual Frames or Time Selection.
4.  Click "Process Video". Wait for the success notification.
5.  Type a question or use the Microphone icon for Voice Input.
6.  Click "Ask" to receive the answer, view the video clip, and optionally hear it spoken aloud via TTS.
*(Include screenshots of the UI here).*

### Appendix D – Project Publications (if any)
*Not Applicable for this version.*
