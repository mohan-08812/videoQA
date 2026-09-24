## Chapter 3: System Architecture and Design

### 3.1 Overview of the Proposed System
The proposed VideoQA system operates on a client-server architecture. The user uploads a video or provides a video URL via the frontend web interface, which is sent to the FastAPI backend. For URLs, the backend uses `yt-dlp` to download the video. It then processes the video using Whisper (for audio) and BLIP (for visual keyframes), compiles a comprehensive context prompt, and uses the Mistral-7B LLM to answer subsequent user questions. 

### 3.2 System Architecture Diagram
*(A block diagram representing the interaction between the User Interface, FastAPI Server, yt-dlp Video Downloader, Whisper Model, BLIP Model, OpenCV Video Processor, and OpenRouter LLM API.)*

```mermaid
graph TD
    UI[Frontend: User Interface]
    URL[(External URL/YouTube)]
    
    subgraph Backend[Backend FastAPI Server]
        API[API Endpoints]
        YTDLP[yt-dlp Downloader]
        VP[OpenCV/MoviePy Processor]
        STT[Whisper Audio Engine]
        BLIP[BLIP Vision Engine]
    end
    
    LLM[OpenRouter/Mistral-7B]
    
    UI -- "Upload MP4 / Provide URL" --> API
    API -- "Extract via URL" --> YTDLP
    YTDLP -- "Download stream" --> URL
    URL -- "Media Data" --> YTDLP
    YTDLP -- "Video File" --> VP
    API -- "Direct Upload" --> VP
    VP -- "Audio" --> STT
    VP -- "Keyframes" --> BLIP
    STT -- "Transcript" --> API
    BLIP -- "Captions" --> API
    API -- "Context + Query" --> LLM
    LLM -- "Answer + Timestamp" --> API
    API -- "Return Output & Clip" --> UI
```

### 3.3 Backend Components Description
*   **FastAPI Web Server:** Handles RESTful API requests.
*   **Video Downloader (yt-dlp):** Extracts and downloads videos from provided URLs.
*   **Video Processor (OpenCV/MoviePy):** Extracts an optimal number of keyframes and generates answer clips.
*   **Speech-to-Text Engine:** Utilizes OpenAI's `whisper-medium` model.
*   **Vision Engine:** Utilizes Salesforce's `BLIP-large` for image captioning.
*   **LLM Controller:** Manages API calls to OpenRouter (using `mistralai/mistral-7b-instruct`) for reasoning.

### 3.4 Frontend Components Description
*   **User Interface (HTML/CSS):** A premium, responsive design.
*   **Client Logic (Vanilla JS - app.js & api.js):** Handles API interactions, state management, and updates the DOM.
*   **Accessibility Modules:** Implements browser-based Speech Recognition (Voice Input) and Speech Synthesis (Read Aloud).

### 3.5 Data Flow Diagram (DFD)
**Level 0:**
```mermaid
graph LR
    User([User]) -- "Video File or URL + Question" --> VideoQA((VideoQA System))
    VideoQA -- "Answer & Sub-clip" --> User
```

**Level 1:**
```mermaid
graph TD
    I[Input Video/URL] --> D{Is URL?}
    D -- Yes --> Y[yt-dlp Processing]
    Y --> V[Video File]
    D -- No --> V
    V --> S[Video Splitting]
    S --> A[Audio Stream]
    S --> F[Visual Frames]
    A --> STT[Whisper STT]
    F --> BL[BLIP Captioning]
    STT --> T[Transcript]
    BL --> C[Captions]
    Q[User Question] --> LLM[LLM Prompting]
    T --> LLM
    C --> LLM
    LLM --> Ans[Answer Generation]
    Ans --> Clip[Clip Extraction]
    Clip --> Out[Final Response]
```

### 3.6 Use Case Diagram
*   **Actor:** User
*   **Use Cases:** Upload Video, Provide Video URL, Set Manual Selection (Frames/Time), Ask Question via Text, Ask Question via Voice, View Answer, Play Answer Clip, Listen to Answer (Read Aloud).

```mermaid
flowchart LR
    User((User))
    
    subgraph System[VideoQA System]
        UC1([Upload Local Video])
        UC2([Provide Video URL])
        UC3([Set Manual Configuration])
        UC4([Ask Question Text/Voice])
        UC5([View Answer & Sub-clip])
        UC6([Listen via Read Aloud])
    end
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
```

### 3.7 System Workflow
1. User uploads a video or submits a video URL.
2. If a URL is provided, the system downloads the video using `yt-dlp`.
3. System extracts audio and transcribes it.
4. System extracts keyframes and generates captions.
5. User asks a question.
6. System prompts the LLM with the transcript, captions, and question.
7. LLM generates an answer and identifies relevant timestamps.
8. System cuts a video clip based on the timestamp and returns it to the UI.

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend Interface
    participant API as FastAPI Backend
    participant YTDLP as yt-dlp Module
    participant Pipeline as ML Pipeline (Whisper/BLIP)
    participant LLM as OpenRouter API
    
    User->>UI: Upload Video / Enter URL
    UI->>API: POST /process_video | /process_url
    alt If URL is provided
        API->>YTDLP: Download video content
        YTDLP-->>API: Video File saved locally
    end
    API->>Pipeline: Extract frames & audio
    Pipeline-->>API: Transcripts & Visual Captions
    API-->>UI: Processing Complete Message
    
    User->>UI: Ask Question
    UI->>API: POST /ask
    API->>LLM: Prompt (Transcript + Captions + Question)
    LLM-->>API: Generated Answer + Timestamp
    API->>API: Trim video to Timestamp
    API-->>UI: Answer Text + Clip URL
    UI-->>User: Display Answer & Play Clip
```
