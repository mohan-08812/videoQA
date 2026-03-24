// api.js – API integration layer with mock fallback
// ─────────────────────────────────────────────────────────────────────────────
// MOCK_MODE: Set to `true`  → uses realistic demo data (no backend needed)
//            Set to `false` → calls the real FastAPI backend at API_BASE
// ─────────────────────────────────────────────────────────────────────────────

const MOCK_MODE = false;             // ← Set to true to use demo data without backend
// For cloud deployment, use the current host. For local dev, use localhost:8000
const API_BASE = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1") 
    ? "http://localhost:8000" 
    : window.location.origin;

let _sessionId = sessionStorage.getItem('vqa-session-id') || null;

// ── Internal helpers ─────────────────────────────────────────

async function apiFetch(path, options = {}) {
    const res = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json", ...options.headers },
        ...options,
    });
    if (!res.ok) {
        const text = await res.text().catch(() => "Unknown error");
        throw new Error(`API ${res.status}: ${text}`);
    }
    return res.json();
}

// ── processVideo ─────────────────────────────────────────────
/**
 * Upload and process a video.
 * @param {File}     file
 * @param {string}   language  – "English" | "Hindi" | "Telugu" | "Spanish" …
 * @param {string}   mode      – "fast" | "full"
 * @param {string}   startTime
 * @param {string}   endTime
 * @param {string}   manualFrames
 * @param {Function} onProgress – (label: string, pct: number) => void
 * @returns  { session_id, transcript, visuals, duration }
 */
async function apiProcessVideo(file, language, mode, startTime, endTime, manualFrames, onProgress) {
    if (MOCK_MODE) {
        const steps = [
            { label: "Extracting audio", pct: 20 },
            { label: "Transcribing speech", pct: 40 },
            { label: "Understanding visuals", pct: 60 },
            { label: "Generating answer model", pct: 80 },
            { label: "Creating summaries", pct: 100 },
        ];
        for (const step of steps) {
            await mockDelay(700 + Math.random() * 500);
            if (onProgress) onProgress(step.label, step.pct);
        }
        _sessionId = MOCK_DATA.processVideo.session_id;
        return MOCK_DATA.processVideo;
    }

    // ── Real backend ──────────────────────────────────────────
    if (onProgress) onProgress("Uploading video…", 5);

    const form = new FormData();
    form.append("video", file);
    form.append("language", language);
    form.append("mode", mode);
    if (startTime) form.append("start_time", startTime);
    if (endTime) form.append("end_time", endTime);
    if (manualFrames) form.append("manual_frames", manualFrames);

    if (onProgress) onProgress("Extracting audio", 15);

    const res = await fetch(`${API_BASE}/process_video`, {
        method: "POST",
        body: form,
        // Note: do NOT set Content-Type here – browser sets multipart boundary
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `Server error ${res.status}`);
    }

    if (onProgress) onProgress("Finalising…", 95);
    const data = await res.json();

    _sessionId = data.session_id;
    sessionStorage.setItem('vqa-session-id', _sessionId);
    if (onProgress) onProgress("Complete", 100);
    return data;
}

// ── askQuestion ───────────────────────────────────────────────
/**
 * Ask a question about the processed video.
 * @returns { answer, confidence, evidence, clip }
 */
async function apiAsk(question, language = "English") {
    if (MOCK_MODE) {
        await mockDelay(1400);
        return MOCK_DATA.ask(question);
    }
    return apiFetch("/ask", {
        method: "POST",
        body: JSON.stringify({
            question,
            session_id: _sessionId,
            language,
        }),
    });
}

// ── summarizeVideo ────────────────────────────────────────────
/**
 * Summarize the video.
 * @param {string} length – "short" | "detailed" | "chapters"
 * @returns { short, detailed, chapters }
 */
async function apiSummarizeVideo(length = "short") {
    if (MOCK_MODE) {
        await mockDelay(1200);
        return MOCK_DATA.summarizeVideo;
    }
    return apiFetch("/summarize_video", {
        method: "POST",
        body: JSON.stringify({ session_id: _sessionId, length }),
    });
}

// ── summarizeTranscript ───────────────────────────────────────
/**
 * Summarize the transcript into key points, action items, and keywords.
 * @returns { key_points, action_items, keywords }
 */
async function apiSummarizeTranscript() {
    if (MOCK_MODE) {
        await mockDelay(1000);
        return MOCK_DATA.summarizeTranscript;
    }
    return apiFetch("/summarize_transcript", {
        method: "POST",
        body: JSON.stringify({ session_id: _sessionId }),
    });
}

// ── download helpers ──────────────────────────────────────────
/**
 * Returns the full download URL for a clip or transcript.
 * In mock mode, returns null (handled client-side).
 */
function apiClipUrl(filename) {
    if (MOCK_MODE || !filename) return null;
    return `${API_BASE}/download/clip/${filename}`;
}

function apiTranscriptDownloadUrl() {
    if (MOCK_MODE || !_sessionId) return null;
    return `${API_BASE}/download/transcript/${_sessionId}`;
}

// ── Session helpers ───────────────────────────────────────────
function getSessionId() { return _sessionId; }
function clearSessionId() { _sessionId = null; sessionStorage.removeItem('vqa-session-id'); }
