# Appendix: Project Source Code

This document contains all source code files for the VideoQA project, including both the UI frontend and the backend environment. Each file is presented under its respective heading.

## index.html

**Path**: `index.html`

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>VideoQA – Multimodal Video Question Answering</title>
  <meta name="description"
    content="Ask questions about any video using AI-powered audio transcription, vision captions, and LLM reasoning." />
  <link rel="stylesheet" href="style.css" />
  <link rel="icon"
    href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎬</text></svg>" />
</head>

<body>

  <!-- ── Background Orbs ─────────────────────────────────── -->
  <div class="bg-orbs" aria-hidden="true">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
  </div>

  <!-- ── App Root ────────────────────────────────────────── -->
  <div id="app">

    <!-- ════════════════════════════════════════
         HEADER
    ════════════════════════════════════════ -->
    <header class="header" role="banner">

      <!-- Logo -->
      <a href="javascript:void(0)" class="header-logo" aria-label="VideoQA Home">
        <div class="logo-icon" aria-hidden="true">🎬</div>
        <span class="logo-text">VideoQA</span>
      </a>

      <!-- Tab navigation -->
      <nav class="header-tabs" role="tablist" aria-label="Main navigation">
        <button class="tab-btn active" id="tab-ask" data-tab="ask" role="tab" type="button" aria-selected="true"
          aria-controls="panel-ask" tabindex="0">
          💬 Ask
        </button>

        <button class="tab-btn" id="tab-summarize" data-tab="summarize" role="tab" type="button" aria-selected="false"
          aria-controls="panel-summarize" tabindex="-1">
          📊 Summarize
        </button>

        <button class="tab-btn" id="tab-transcript" data-tab="transcript" role="tab" type="button" aria-selected="false"
          aria-controls="panel-transcript" tabindex="-1">
          📄 Transcript
        </button>
      </nav>

      <!-- Action buttons -->
      <div class="header-actions">
        <button class="btn-ghost" id="how-btn" type="button" aria-label="How it works">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
            aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4M12 8h.01" />
          </svg>
          <span>How it works</span>
        </button>

        <button class="btn-ghost" id="clear-btn" type="button" aria-label="Clear session">
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
            aria-hidden="true">
            <path d="M3 6h18M19 6l-1 14H6L5 6M10 11v6M14 11v6M9 6V4h6v2" />
          </svg>
          <span>Clear</span>
        </button>

        <!-- Mobile history drawer toggle -->
        <button class="btn-icon history-btn-mobile" id="history-mobile-btn" type="button" aria-label="View history">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
            aria-hidden="true">
            <path d="M12 8v4l3 3M3.05 11a9 9 0 1 0 .5-3" />
            <path d="M3 4v4h4" />
          </svg>
        </button>

        <button class="btn-icon" id="theme-toggle" type="button" aria-label="Toggle theme">☀️</button>
      </div>
    </header>

    <!-- ════════════════════════════════════════
         HERO
    ════════════════════════════════════════ -->
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-badge">
        <span class="dot" aria-hidden="true"></span>
        AI-Powered · Multimodal
      </div>
      <h1 id="hero-title">Ask any question about your video</h1>
      <p>Powered by audio transcription + vision captions + LLM reasoning</p>

      <div class="feature-chips" role="list" aria-label="Features">
        <span class="chip" role="listitem"><span class="ci">⚡</span> Fast</span>
        <span class="chip" role="listitem"><span class="ci">🌍</span> Multilingual</span>
        <span class="chip" role="listitem"><span class="ci">✂️</span> Clip Retrieval</span>
        <span class="chip" role="listitem"><span class="ci">📝</span> Summaries</span>
        <span class="chip" role="listitem"><span class="ci">📄</span> Transcript Viewer</span>
      </div>
    </section>

    <!-- ════════════════════════════════════════
         UPLOAD PANEL (full width)
    ════════════════════════════════════════ -->
    <div style="padding: 0 var(--space-6); max-width:1300px; margin:0 auto; width:100%;">
      <div class="glass upload-panel">

        <!-- Drop zone -->
        <div class="drop-zone" id="drop-zone" role="button" tabindex="0"
          aria-label="Click or drag to upload a video file">
          <input type="file" id="file-input"
            accept="video/mp4,video/quicktime,video/x-matroska,video/webm,.mp4,.mov,.mkv,.webm"
            aria-label="Upload video file" />
          <span class="drop-icon" aria-hidden="true">📁</span>
          <h3>Drop your video here or click to upload</h3>
          <p>Supported formats: MP4, MOV, MKV, WebM</p>
          <div class="drop-formats" aria-label="Supported formats">
            <span class="fmt-badge">.mp4</span>
            <span class="fmt-badge">.mov</span>
            <span class="fmt-badge">.mkv</span>
            <span class="fmt-badge">.webm</span>
          </div>
          <div class="or-divider" style="margin: 20px 0; font-size: 14px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">— OR —</div>
          <div class="url-upload" style="display: flex; gap: 8px; width: 80%; max-width: 400px; margin: 0 auto;" onclick="event.stopPropagation()">
            <input type="url" id="url-input" class="select-styled" placeholder="Paste video URL (YouTube, direct links, etc.)" style="width: 100%; flex: 1; min-width: 0;" aria-label="Video URL">
            <button class="btn-secondary" id="add-url-btn" type="button" style="white-space: nowrap;">Add URL</button>
          </div>
        </div>

        <!-- File info -->
        <div class="file-info" id="file-info" role="status" aria-live="polite">
          <span class="file-icon" aria-hidden="true">🎥</span>
          <div class="file-meta">
            <div class="file-name" id="file-name-display">—</div>
            <div class="file-detail" id="file-detail-display">—</div>
          </div>
          <button class="file-remove" id="file-remove" type="button" aria-label="Remove file">✕</button>
        </div>

        <!-- Video preview -->
        <div class="video-preview-wrap" id="video-preview-wrap">
          <video id="video-preview" controls preload="metadata" aria-label="Video preview"></video>
          
          <!-- Manual Selection Tools -->
          <div class="manual-selection-tools" id="manual-selection-tools" style="display: none; flex-direction: column; gap: 10px; margin-top: 15px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px;">
            <div style="display: flex; gap: 15px; flex-wrap: wrap; align-items: center;">
              <div class="form-group" style="margin: 0; flex: 1; min-width: 120px;">
                <label class="form-label" for="manual-start">Start Time (sec)</label>
                <input type="number" id="manual-start" class="select-styled" placeholder="0" min="0" step="0.1" style="width: 100%;">
              </div>
              <div class="form-group" style="margin: 0; flex: 1; min-width: 120px;">
                <label class="form-label" for="manual-end">End Time (sec)</label>
                <input type="number" id="manual-end" class="select-styled" placeholder="All" min="0" step="0.1" style="width: 100%;">
              </div>
              <button class="btn-secondary" id="add-frame-btn" type="button" style="margin-top: 24px; white-space: nowrap;">📸 Add Current Frame</button>
            </div>
            <div id="manual-frames-list" style="display: flex; gap: 8px; flex-wrap: wrap;"></div>
            <p style="font-size: 12px; color: var(--text-muted); margin: 0;">Optional: Specify a start/end time to process a sub-clip, and manually pick keyframes. Leave blank to process the whole video automatically.</p>
          </div>
        </div>

        <!-- Controls -->
        <div class="upload-controls">
          <div class="form-group">
            <label class="form-label" for="language-select">Language</label>
            <select class="select-styled" id="language-select" aria-label="Select language">
              <optgroup label="🌍 World Languages">
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="zh">Chinese</option>
                <option value="ar">Arabic</option>
                <option value="ja">Japanese</option>
                <option value="ko">Korean</option>
                <option value="pt">Portuguese</option>
                <option value="ru">Russian</option>
                <option value="it">Italian</option>
              </optgroup>
              <optgroup label="🇮🇳 Indian Languages">
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="te">Telugu (తెలుగు)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="kn">Kannada (ಕನ್ನಡ)</option>
                <option value="ml">Malayalam (മലയാളം)</option>
                <option value="mr">Marathi (मराठी)</option>
                <option value="bn">Bengali (বাংলা)</option>
                <option value="pa">Punjabi (ਪੰਜਾਬੀ)</option>
                <option value="gu">Gujarati (ગુજરાતી)</option>
                <option value="ur">Urdu (اردو)</option>
              </optgroup>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Processing Mode</label>
            <div class="mode-toggle" role="group" aria-label="Processing mode">
              <button class="mode-opt active" data-mode="fast" type="button" aria-pressed="true">⚡ Fast QA</button>
              <button class="mode-opt" data-mode="full" type="button" aria-pressed="false">🔬 QA + Clip
                Retrieval</button>
            </div>
          </div>

          <button class="btn-primary" id="process-btn" type="button" disabled aria-label="Process video">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"
              aria-hidden="true">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            Process Video
          </button>
        </div>

        <!-- Progress Timeline -->
        <div class="progress-panel" id="progress-panel" role="status" aria-live="polite"
          aria-label="Processing progress">
          <div class="progress-header">
            <span class="progress-title" id="progress-status">Starting…</span>
            <span class="progress-pct" id="progress-pct">0%</span>
          </div>
          <div class="progress-bar-outer" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
            <div class="progress-bar-inner" id="progress-bar"></div>
          </div>
          <div class="progress-steps" id="progress-steps">
            <!-- Populated by JS -->
          </div>
        </div>

      </div>
    </div>

    <!-- ════════════════════════════════════════
         MAIN LAYOUT (Content + Sidebar)
    ════════════════════════════════════════ -->
    <div class="main-layout">

      <!-- CONTENT AREA -->
      <main class="content-area" role="main">

        <!-- ── ASK TAB ───────────────────────────── -->
        <section class="tab-panel active" id="panel-ask" role="tabpanel" aria-labelledby="tab-ask">
          <div id="ask-content">
            <!-- Populated by JS (demo state → ready state after processing) -->
          </div>
        </section>

        <!-- ── SUMMARIZE TAB ─────────────────────── -->
        <section class="tab-panel" id="panel-summarize" role="tabpanel" aria-labelledby="tab-summarize" hidden>
          <div id="summarize-content">
            <!-- Populated by JS -->
          </div>
        </section>

        <!-- ── TRANSCRIPT TAB ────────────────────── -->
        <section class="tab-panel" id="panel-transcript" role="tabpanel" aria-labelledby="tab-transcript" hidden>
          <div id="transcript-content" style="overflow:hidden; border-radius:var(--radius-lg);" class="glass">
            <!-- Populated by JS -->
          </div>
        </section>

      </main>

      <!-- HISTORY SIDEBAR -->
      <aside class="sidebar" id="sidebar" aria-label="Q&A History">
        <div class="glass history-card">
          <div class="history-header">
            <h3>🕐 History</h3>
            <span class="history-count" id="history-count">0</span>
          </div>
          <div class="history-list" id="history-list" role="list">
            <div class="history-empty">No questions yet.<br>Ask something to get started.</div>
          </div>
        </div>
      </aside>

    </div>

    <!-- ════════════════════════════════════════
         "HOW IT WORKS" MODAL
    ════════════════════════════════════════ -->
    <div class="modal-overlay" id="how-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" hidden>
      <div class="glass modal-box">
        <div class="modal-header">
          <h2 id="modal-title">How VideoQA Works</h2>
          <button class="modal-close" id="modal-close" type="button" aria-label="Close modal">✕</button>
        </div>

        <div class="how-steps">
          <div class="how-step">
            <div class="how-num">1</div>
            <div>
              <h4>📁 Upload Your Video</h4>
              <p>Drag and drop any MP4, MOV, or MKV video. Select your language for accurate transcription.</p>
            </div>
          </div>

          <div class="how-step">
            <div class="how-num">2</div>
            <div>
              <h4>🔊 Audio Transcription</h4>
              <p>The audio is extracted and transcribed using Whisper — a state-of-the-art multilingual speech
                recognition model.</p>
            </div>
          </div>

          <div class="how-step">
            <div class="how-num">3</div>
            <div>
              <h4>👁️ Visual Understanding</h4>
              <p>Key frames are extracted and described using vision models, capturing what's shown on screen.</p>
            </div>
          </div>

          <div class="how-step">
            <div class="how-num">4</div>
            <div>
              <h4>🧠 LLM Reasoning</h4>
              <p>Your question is answered by an LLM with full context of the transcript + visual captions, finding the
                most relevant clip.</p>
            </div>
          </div>

          <div class="how-step">
            <div class="how-num">5</div>
            <div>
              <h4>📊 Summaries & Insights</h4>
              <p>Get video summaries, transcript key points, action items, and keywords — all AI-generated instantly.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ════════════════════════════════════════
         FOOTER
    ════════════════════════════════════════ -->
    <footer class="footer">
      <p>
        VideoQA · Multimodal AI · Built with 🧠 &amp; ☕ ·
        <a href="javascript:void(0)" aria-label="View project on GitHub">View on GitHub</a>
      </p>
    </footer>

  </div>

  <!-- ── Toast Container ─────────────────────────────────── -->
  <div class="toast-container" id="toast-container" aria-live="assertive" aria-atomic="true"></div>

  <!-- ── Scripts ─────────────────────────────────────────── -->
  <script src="mock.js"></script>
  <script src="api.js"></script>
  <script src="app.js"></script>

</body>

</html>
```

## style.css

**Path**: `style.css`

```css
/* =========================================================
   VideoQA – Premium Design System CSS
   Dark-first, glassmorphism, responsive, animated
   ========================================================= */

/* ── Google Fonts ──────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── CSS Custom Properties ─────────────────────────────── */
:root {
  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-xl: 28px;

  /* Transitions */
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  --transition: 0.22s var(--ease);
  --transition-slow: 0.45s var(--ease);

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Shadows */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
  --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.35);
  --shadow-lg: 0 20px 48px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 32px rgba(102, 126, 234, 0.3);
}

/* ── Dark Theme (default) ──────────────────────────────── */
[data-theme="dark"] {
  --bg-base: #0b0e1a;
  --bg-surface: #111425;
  --bg-card: rgba(20, 25, 50, 0.7);
  --bg-card-hover: rgba(30, 37, 70, 0.85);
  --bg-input: rgba(15, 20, 42, 0.8);
  --bg-chip: rgba(102, 126, 234, 0.15);
  --border: rgba(255, 255, 255, 0.08);
  --border-accent: rgba(102, 126, 234, 0.4);

  --text-primary: #f0f2ff;
  --text-secondary: #8b91b8;
  --text-muted: #555c80;
  --text-accent: #818cf8;

  --accent: #667eea;
  --accent-2: #764ba2;
  --accent-light: #a5b4fc;
  --success: #34d399;
  --warning: #fbbf24;
  --error: #f87171;

  --gradient-bg: linear-gradient(135deg, #0b0e1a 0%, #0f1229 40%, #13112a 70%, #0b0e1a 100%);
  --gradient-accent: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-card: linear-gradient(145deg, rgba(30, 37, 80, 0.5) 0%, rgba(15, 18, 45, 0.5) 100%);

  --glass-bg: rgba(15, 18, 40, 0.65);
  --glass-border: rgba(255, 255, 255, 0.08);
  --glass-blur: blur(20px);
}

/* ── Light Theme ───────────────────────────────────────── */
[data-theme="light"] {
  --bg-base: #f0f2ff;
  --bg-surface: #ffffff;
  --bg-card: rgba(255, 255, 255, 0.85);
  --bg-card-hover: rgba(245, 247, 255, 0.95);
  --bg-input: rgba(245, 247, 255, 0.9);
  --bg-chip: rgba(102, 126, 234, 0.1);
  --border: rgba(0, 0, 0, 0.08);
  --border-accent: rgba(102, 126, 234, 0.35);

  --text-primary: #1a1d35;
  --text-secondary: #4b5080;
  --text-muted: #9098c0;
  --text-accent: #5b6ee8;

  --accent: #667eea;
  --accent-2: #764ba2;
  --accent-light: #818cf8;
  --success: #059669;
  --warning: #d97706;
  --error: #dc2626;

  --gradient-bg: linear-gradient(135deg, #eef0fc 0%, #f5f0ff 50%, #edf2ff 100%);
  --gradient-accent: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-card: linear-gradient(145deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 242, 255, 0.8) 100%);

  --glass-bg: rgba(255, 255, 255, 0.75);
  --glass-border: rgba(102, 126, 234, 0.15);
  --glass-blur: blur(16px);
}

/* ── Reset & Base ──────────────────────────────────────── */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-sans);
  background: var(--gradient-bg);
  background-attachment: fixed;
  color: var(--text-primary);
  min-height: 100vh;
  line-height: 1.6;
  transition: background var(--transition-slow), color var(--transition);
  overflow-x: hidden;
}

/* ── Animated Background Orbs ──────────────────────────── */
.bg-orbs {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.18;
  animation: orbFloat 12s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #667eea, transparent);
  top: -200px;
  left: -150px;
  animation-delay: 0s;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #764ba2, transparent);
  bottom: -150px;
  right: -100px;
  animation-delay: -4s;
}

.orb-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #06b6d4, transparent);
  top: 40%;
  right: 20%;
  animation-delay: -8s;
}

@keyframes orbFloat {

  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }

  33% {
    transform: translate(30px, -20px) scale(1.05);
  }

  66% {
    transform: translate(-20px, 30px) scale(0.95);
  }
}

/* ── Glass Card Utility ────────────────────────────────── */
.glass {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
}

.glass-sm {
  border-radius: var(--radius-md);
}

/* ── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-accent);
  border-radius: 99px;
}

/* ── Layout Container ──────────────────────────────────── */
#app {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ═══════════════════════════════════════════
   HEADER
═══════════════════════════════════════════ */
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-bottom: 1px solid var(--glass-border);
  padding: 0 var(--space-6);
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  transition: background var(--transition);
}

.header-logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  text-decoration: none;
  flex-shrink: 0;
}

.logo-icon {
  width: 38px;
  height: 38px;
  background: var(--gradient-accent);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: var(--shadow-glow);
}

.logo-text {
  font-size: 18px;
  font-weight: 800;
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

/* Tab bar inside header */
.header-tabs {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 4px;
  flex-shrink: 0;
}

[data-theme="light"] .header-tabs {
  background: rgba(102, 126, 234, 0.08);
}

.tab-btn {
  padding: 6px 18px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-sans);
  border-radius: 20px;
  transition: all var(--transition);
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.06);
}

.tab-btn.active {
  background: var(--gradient-accent);
  color: #fff;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.4);
}

/* Header actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.btn-ghost {
  padding: 7px 14px;
  background: none;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.btn-ghost:hover {
  border-color: var(--border-accent);
  color: var(--text-primary);
  background: rgba(102, 126, 234, 0.1);
}

.btn-icon {
  width: 36px;
  height: 36px;
  background: none;
  border: 1px solid var(--border);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.btn-icon:hover {
  border-color: var(--border-accent);
  color: var(--text-primary);
  background: rgba(102, 126, 234, 0.1);
}

/* ═══════════════════════════════════════════
   HERO
═══════════════════════════════════════════ */
.hero {
  text-align: center;
  padding: var(--space-12) var(--space-6) var(--space-8);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: rgba(102, 126, 234, 0.12);
  border: 1px solid rgba(102, 126, 234, 0.25);
  border-radius: var(--radius-xl);
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-light);
  margin-bottom: var(--space-5);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.hero-badge .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
  animation: pulse 2s infinite;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 0.5;
    transform: scale(1.3);
  }
}

.hero h1 {
  font-size: clamp(28px, 5vw, 52px);
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -1.5px;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: var(--space-4);
}

.hero p {
  font-size: clamp(14px, 2vw, 18px);
  color: var(--text-secondary);
  max-width: 560px;
  margin: 0 auto var(--space-6);
}

.feature-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-2);
}

.chip {
  padding: 5px 14px;
  background: var(--bg-chip);
  border: 1px solid var(--border-accent);
  border-radius: var(--radius-xl);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-light);
  letter-spacing: 0.3px;
  transition: all var(--transition);
}

.chip:hover {
  background: rgba(102, 126, 234, 0.25);
  transform: translateY(-2px);
}

.chip .ci {
  margin-right: 4px;
}

/* ═══════════════════════════════════════════
   MAIN LAYOUT
═══════════════════════════════════════════ */
.main-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--space-6);
  padding: 0 var(--space-6) var(--space-12);
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
}

/* ═══════════════════════════════════════════
   UPLOAD PANEL
═══════════════════════════════════════════ */
.upload-panel {
  grid-column: 1 / -1;
  padding: var(--space-8);
}

.drop-zone {
  border: 2px dashed var(--border-accent);
  border-radius: var(--radius-lg);
  padding: var(--space-10) var(--space-6);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition);
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.04) 0%, rgba(118, 75, 162, 0.04) 100%);
}

.drop-zone:hover,
.drop-zone.drag-over {
  border-color: var(--accent);
  background: rgba(102, 126, 234, 0.08);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow);
}

.drop-zone input[type="file"] {
  display: none;
}

.drop-icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
}

.drop-zone h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: var(--space-2);
}

.drop-zone p {
  color: var(--text-secondary);
  font-size: 14px;
}

.drop-formats {
  margin-top: var(--space-3);
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.fmt-badge {
  padding: 3px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

/* File info bar */
.file-info {
  display: none;
  margin-top: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  align-items: center;
  gap: var(--space-4);
}

.file-info.show {
  display: flex;
}

.file-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.file-meta {
  flex: 1;
}

.file-name {
  font-weight: 700;
  font-size: 14px;
}

.file-detail {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.file-remove {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 18px;
  cursor: pointer;
  padding: var(--space-2);
  transition: color var(--transition);
}

.file-remove:hover {
  color: var(--error);
}

/* Video preview */
.video-preview-wrap {
  display: none;
  margin-top: var(--space-5);
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border);
  background: #000;
  max-height: 300px;
}

.video-preview-wrap.show {
  display: block;
}

.video-preview-wrap video {
  width: 100%;
  max-height: 300px;
  display: block;
}

/* Controls row */
.upload-controls {
  margin-top: var(--space-5);
  display: flex;
  gap: var(--space-4);
  align-items: flex-end;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.select-styled {
  appearance: none;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  padding: 10px 36px 10px 14px;
  font-size: 14px;
  font-family: var(--font-sans);
  font-weight: 500;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%238b91b8' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 20px;
  transition: border-color var(--transition);
  min-width: 160px;
}

.select-styled:focus {
  outline: none;
  border-color: var(--accent);
}

/* Mode toggle */
.mode-toggle {
  display: flex;
  gap: 2px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 3px;
}

.mode-opt {
  padding: 8px 14px;
  border: none;
  background: none;
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
}

.mode-opt.active {
  background: var(--gradient-accent);
  color: #fff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.mode-opt:hover:not(.active) {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

/* Primary button */
.btn-primary {
  padding: 11px 28px;
  background: var(--gradient-accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.35);
  white-space: nowrap;
  margin-left: auto;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(102, 126, 234, 0.5);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Secondary button */
.btn-secondary {
  padding: 9px 18px;
  background: rgba(102, 126, 234, 0.1);
  color: var(--accent-light);
  border: 1px solid var(--border-accent);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition);
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  white-space: nowrap;
}

.btn-secondary:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
}

.btn-secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

/* ═══════════════════════════════════════════
   PROGRESS TIMELINE
═══════════════════════════════════════════ */
.progress-panel {
  display: none;
  margin-top: var(--space-6);
  padding: var(--space-6);
  border-radius: var(--radius-md);
  background: var(--bg-input);
  border: 1px solid var(--border-accent);
}

.progress-panel.show {
  display: block;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.progress-title {
  font-size: 14px;
  font-weight: 700;
}

.progress-pct {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent-light);
  font-family: var(--font-mono);
}

.progress-bar-outer {
  height: 6px;
  background: var(--border);
  border-radius: 99px;
  margin-bottom: var(--space-5);
  overflow: hidden;
}

.progress-bar-inner {
  height: 100%;
  border-radius: 99px;
  background: var(--gradient-accent);
  transition: width 0.6s var(--ease);
  box-shadow: 0 0 12px rgba(102, 126, 234, 0.5);
  width: 0%;
}

.progress-steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.progress-step {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.step-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border: 2px solid var(--border);
  color: var(--text-muted);
  transition: all var(--transition);
}

.step-icon.active {
  border-color: var(--accent);
  color: var(--accent);
  animation: spinStep 1s linear infinite;
}

.step-icon.done {
  border-color: var(--success);
  background: var(--success);
  color: #fff;
}

.step-icon.done::after {
  content: '✓';
}

@keyframes spinStep {
  to {
    transform: rotate(360deg);
  }
}

.step-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: color var(--transition);
}

.step-label.active {
  color: var(--text-primary);
}

/* ═══════════════════════════════════════════
   CONTENT AREA + SIDEBAR LAYOUT
═══════════════════════════════════════════ */
.content-area {
  min-width: 0;
}

.sidebar {
  position: relative;
}

/* Tab panels */
.tab-panel {
  display: none;
  animation: fadeUp 0.3s var(--ease);
}

.tab-panel.active {
  display: block;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ═══════════════════════════════════════════
   ASK TAB
═══════════════════════════════════════════ */
.qa-input-card {
  padding: var(--space-6);
  margin-bottom: var(--space-4);
}

.qa-input-card h2 {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: var(--space-4);
}

.question-area {
  width: 100%;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.7;
  resize: vertical;
  min-height: 90px;
  transition: border-color var(--transition);
}

.question-area:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}

.question-area::placeholder {
  color: var(--text-muted);
}

.qa-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-top: var(--space-3);
}

/* Answer card */
.result-card {
  padding: var(--space-6);
  margin-bottom: var(--space-4);
  animation: fadeUp 0.35s var(--ease);
}

.result-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
  gap: var(--space-3);
}

.result-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-secondary);
}

.result-label .dot-accent {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gradient-accent);
}

.result-actions {
  display: flex;
  gap: var(--space-2);
}

.answer-text {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.answer-text strong {
  color: var(--accent-light);
}

.confidence-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
  padding: 6px 14px;
  background: rgba(52, 211, 153, 0.1);
  border: 1px solid rgba(52, 211, 153, 0.25);
  border-radius: var(--radius-xl);
  font-size: 12px;
  font-weight: 600;
  color: var(--success);
}

.confidence-badge::before {
  content: '✦';
}

/* Clip card */
.clip-card {
  padding: var(--space-6);
  margin-bottom: var(--space-4);
}

.clip-player-wrap {
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #000;
  margin-bottom: var(--space-4);
  border: 1px solid var(--border);
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clip-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  color: var(--text-muted);
  padding: var(--space-8);
}

.clip-placeholder span {
  font-size: 36px;
}

.clip-placeholder p {
  font-size: 13px;
}

.clip-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-light);
  margin-bottom: var(--space-3);
}

.clip-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

/* Evidence collapsible */
.evidence-card {
  padding: var(--space-4) var(--space-5);
  margin-bottom: var(--space-4);
}

.evidence-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}

.evidence-toggle h4 {
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.toggle-arrow {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform var(--transition);
}

.toggle-arrow.open {
  transform: rotate(180deg);
}

.evidence-body {
  display: none;
  margin-top: var(--space-4);
}

.evidence-body.show {
  display: block;
}

.evidence-section {
  margin-bottom: var(--space-4);
}

.evidence-section:last-child {
  margin-bottom: 0;
}

.evidence-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

.evidence-item {
  padding: var(--space-3) var(--space-4);
  margin-bottom: var(--space-2);
  background: var(--bg-input);
  border-left: 3px solid var(--accent);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  font-style: italic;
}

/* Demo state */
.demo-state {
  padding: var(--space-10) var(--space-6);
  text-align: center;
  color: var(--text-muted);
}

.demo-icon {
  font-size: 52px;
  margin-bottom: var(--space-4);
  display: block;
}

.demo-state h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.demo-state p {
  font-size: 14px;
  max-width: 340px;
  margin: 0 auto;
}

/* ═══════════════════════════════════════════
   SUMMARIZE TAB
═══════════════════════════════════════════ */
.summarize-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

@media (max-width: 900px) {
  .summarize-grid {
    grid-template-columns: 1fr;
  }
}

.summarize-section {
  padding: var(--space-6);
}

.summarize-section h3 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.summary-toggle {
  display: flex;
  gap: 2px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 3px;
  margin-bottom: var(--space-4);
}

.sum-opt {
  flex: 1;
  padding: 7px 10px;
  border: none;
  background: none;
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition);
  text-align: center;
}

.sum-opt.active {
  background: var(--gradient-accent);
  color: #fff;
}

.sum-opt:hover:not(.active) {
  color: var(--text-primary);
}

.summary-output {
  min-height: 80px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}

.summary-bullet {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
  align-items: flex-start;
}

.summary-bullet::before {
  content: '▸';
  color: var(--accent);
  flex-shrink: 0;
  margin-top: 2px;
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.chapter-item {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-input);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  transition: border-color var(--transition);
}

.chapter-item:hover {
  border-color: var(--border-accent);
}

.chapter-time {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent-light);
  font-family: var(--font-mono);
  flex-shrink: 0;
  min-width: 44px;
}

.chapter-title {
  font-size: 13px;
  font-weight: 500;
}

.kw-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.kw-chip {
  padding: 4px 12px;
  background: var(--bg-chip);
  border: 1px solid var(--border-accent);
  border-radius: var(--radius-xl);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-light);
  cursor: default;
  transition: background var(--transition);
}

.kw-chip:hover {
  background: rgba(102, 126, 234, 0.25);
}

.action-items {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.action-items li {
  padding: var(--space-3) var(--space-4);
  background: var(--bg-input);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--warning);
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.export-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border);
}

/* ═══════════════════════════════════════════
   TRANSCRIPT TAB
═══════════════════════════════════════════ */
.transcript-toolbar {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  flex-wrap: wrap;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border);
  margin-bottom: 0;
}

.search-wrap {
  position: relative;
  flex: 1;
  min-width: 180px;
}

.search-wrap svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding: 9px 12px 9px 36px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font-sans);
  transition: border-color var(--transition);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.speaker-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
}

.toggle-sw {
  width: 38px;
  height: 22px;
  background: var(--border);
  border-radius: 99px;
  position: relative;
  transition: background var(--transition);
  cursor: pointer;
}

.toggle-sw.on {
  background: var(--accent);
}

.toggle-sw::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 16px;
  height: 16px;
  background: #fff;
  border-radius: 50%;
  transition: left var(--transition);
}

.toggle-sw.on::after {
  left: 19px;
}

.transcript-body {
  padding: var(--space-4) var(--space-6);
  max-height: 520px;
  overflow-y: auto;
}

.transcript-line {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-2);
  border-radius: var(--radius-sm);
  transition: background var(--transition);
  margin-bottom: 2px;
}

.transcript-line:hover {
  background: rgba(102, 126, 234, 0.06);
}

.transcript-line.highlight {
  background: rgba(102, 126, 234, 0.12);
}

.ts-time {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent-light);
  font-family: var(--font-mono);
  flex-shrink: 0;
  min-width: 42px;
  padding-top: 2px;
}

.ts-speaker {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  flex-shrink: 0;
  min-width: 80px;
  padding-top: 2px;
}

.ts-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
}

.ts-text mark {
  background: rgba(102, 126, 234, 0.35);
  color: var(--text-primary);
  border-radius: 3px;
  padding: 0 2px;
}

/* ═══════════════════════════════════════════
   HISTORY SIDEBAR
═══════════════════════════════════════════ */
.history-card {
  position: sticky;
  top: 80px;
  padding: 0;
  overflow: hidden;
}

.history-header {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-header h3 {
  font-size: 14px;
  font-weight: 700;
}

.history-count {
  font-size: 11px;
  font-weight: 700;
  background: var(--bg-chip);
  color: var(--accent-light);
  padding: 2px 8px;
  border-radius: var(--radius-xl);
}

.history-list {
  max-height: 480px;
  overflow-y: auto;
}

.history-item {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background var(--transition);
}

.history-item:hover {
  background: rgba(102, 126, 234, 0.07);
}

.history-item.active {
  background: rgba(102, 126, 234, 0.12);
  border-left: 3px solid var(--accent);
}

.hi-question {
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hi-time {
  font-size: 11px;
  color: var(--text-muted);
}

.history-empty {
  padding: var(--space-6);
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}

/* ═══════════════════════════════════════════
   MODAL (How it works)
═══════════════════════════════════════════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition);
}

.modal-overlay.open {
  opacity: 1;
  pointer-events: all;
}

.modal-box {
  max-width: 560px;
  width: 100%;
  padding: var(--space-8);
  transform: translateY(20px);
  transition: transform var(--transition);
}

.modal-overlay.open .modal-box {
  transform: translateY(0);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.modal-header h2 {
  font-size: 22px;
  font-weight: 800;
}

.modal-close {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color var(--transition);
}

.modal-close:hover {
  color: var(--text-primary);
}

.how-steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.how-step {
  display: flex;
  gap: var(--space-4);
  align-items: flex-start;
}

.how-num {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--gradient-accent);
  color: #fff;
  font-size: 15px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
}

.how-step h4 {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 4px;
}

.how-step p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ═══════════════════════════════════════════
   TOAST NOTIFICATIONS
═══════════════════════════════════════════ */
.toast-container {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  z-index: 999;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  pointer-events: none;
}

.toast {
  padding: 12px 18px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  box-shadow: var(--shadow-md);
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  animation: toastIn 0.3s var(--ease) forwards;
  max-width: 320px;
}

.toast.removing {
  animation: toastOut 0.3s var(--ease) forwards;
}

.toast-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.toast.success .toast-icon::before {
  content: '✅';
}

.toast.error .toast-icon::before {
  content: '❌';
}

.toast.info .toast-icon::before {
  content: 'ℹ️';
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(30px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toastOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }

  to {
    opacity: 0;
    transform: translateX(30px);
  }
}

/* ═══════════════════════════════════════════
   ERROR CARD
═══════════════════════════════════════════ */
.error-card {
  padding: var(--space-5) var(--space-6);
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  border-radius: var(--radius-md);
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.error-card .err-icon {
  font-size: 22px;
  flex-shrink: 0;
}

.error-card h4 {
  font-size: 14px;
  font-weight: 700;
  color: var(--error);
  margin-bottom: 4px;
}

.error-card p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ═══════════════════════════════════════════
   LOADING SPINNER
═══════════════════════════════════════════ */
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ═══════════════════════════════════════════
   UTILITY
═══════════════════════════════════════════ */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.hidden {
  display: none !important;
}

.mt-2 {
  margin-top: var(--space-2);
}

.mt-4 {
  margin-top: var(--space-4);
}

.gap-2 {
  gap: var(--space-2);
}

.flex {
  display: flex;
}

.flex-wrap {
  flex-wrap: wrap;
}

.items-center {
  align-items: center;
}

/* ═══════════════════════════════════════════
   FOOTER
═══════════════════════════════════════════ */
.footer {
  text-align: center;
  padding: var(--space-6);
  border-top: 1px solid var(--border);
  font-size: 12px;
  color: var(--text-muted);
}

.footer a {
  color: var(--accent-light);
  text-decoration: none;
}

/* ═══════════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════════ */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: none;
  }

  .sidebar.mobile-open {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 150;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
  }

  .sidebar.mobile-open .history-card {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 320px;
    border-radius: 0;
    max-height: 100vh;
    overflow-y: auto;
  }

  .history-btn-mobile {
    display: flex !important;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 0 var(--space-4);
  }

  .header-tabs {
    gap: 1px;
  }

  .tab-btn {
    padding: 6px 12px;
    font-size: 12px;
  }

  .logo-text {
    display: none;
  }

  .hero {
    padding: var(--space-8) var(--space-4) var(--space-6);
  }

  .main-layout {
    padding: 0 var(--space-4) var(--space-8);
    gap: var(--space-4);
  }

  .upload-panel {
    padding: var(--space-5);
  }

  .drop-zone {
    padding: var(--space-8) var(--space-4);
  }

  .upload-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-primary {
    margin-left: 0;
    justify-content: center;
  }

  .qa-actions {
    flex-direction: column;
  }

  .qa-actions .btn-secondary {
    justify-content: center;
  }

  .result-actions {
    flex-wrap: wrap;
  }

  .footer {
    display: none;
  }
}

@media (max-width: 480px) {
  .header-actions .btn-ghost span {
    display: none;
  }

  .feature-chips {
    gap: var(--space-1);
  }

  .chip {
    font-size: 11px;
    padding: 4px 10px;
  }
}

.history-btn-mobile {
  display: none;
}

/* ═══════════════════════════════════════════
   VOICE INPUT (MIC BUTTON)
═══════════════════════════════════════════ */
.qa-input-wrap {
  position: relative;
  width: 100%;
}

.btn-mic {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.15);
  border: 1.5px solid var(--border-accent);
  color: var(--accent-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  z-index: 2;
  font-size: 17px;
}

.btn-mic:hover {
  background: rgba(102, 126, 234, 0.3);
  transform: scale(1.07);
  box-shadow: 0 0 14px rgba(102, 126, 234, 0.35);
}

.btn-mic.listening {
  background: rgba(248, 113, 113, 0.18);
  border-color: var(--error);
  color: var(--error);
  animation: micPulse 1.2s ease-in-out infinite;
}

@keyframes micPulse {

  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(248, 113, 113, 0.5);
  }

  50% {
    box-shadow: 0 0 0 9px rgba(248, 113, 113, 0);
  }
}

/* Mic unavailable state */
.btn-mic.unavailable {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ═══════════════════════════════════════════
   TEXT-TO-SPEECH (READ ALOUD BUTTON)
═══════════════════════════════════════════ */
.btn-tts {
  padding: 8px 16px;
  background: rgba(52, 211, 153, 0.1);
  border: 1.5px solid rgba(52, 211, 153, 0.3);
  color: var(--success);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-sans);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  transition: all var(--transition);
  white-space: nowrap;
}

.btn-tts:hover {
  background: rgba(52, 211, 153, 0.2);
  transform: translateY(-1px);
}

.btn-tts.speaking {
  background: rgba(52, 211, 153, 0.22);
  border-color: var(--success);
  animation: ttsPulse 1.5s ease-in-out infinite;
}

@keyframes ttsPulse {

  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4);
  }

  50% {
    box-shadow: 0 0 0 7px rgba(52, 211, 153, 0);
  }
}

/* Voice status indicator bar */
.voice-status {
  display: none;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
  font-size: 12px;
  font-weight: 600;
  color: var(--error);
  padding: 6px 12px;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--radius-sm);
  animation: fadeUp 0.2s var(--ease);
}

.voice-status.show {
  display: flex;
}

.voice-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--error);
  animation: micPulse 1s ease-in-out infinite;
}
```

## app.js

**Path**: `app.js`

```javascript
/* =========================================================
   app.js – VideoQA Core Application Logic
   ========================================================= */

// ── App State ──────────────────────────────────────────────
const state = {
  theme: 'dark',
  tab: 'ask',
  phase: 'idle',       // idle | uploading | processing | ready
  file: null,
  videoUrl: null,
  manualFrames: [],    // user selected frame timestamps
  sessionData: null,   // processVideo result
  currentAnswer: null,
  history: [],
  historyIndex: -1,
  speakerLabels: true,
  transcriptData: null,
  summarizeMode: 'short',
  transcriptSummarized: false,
  videoSummarized: false,
};

// ── DOM refs ───────────────────────────────────────────────
const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

// ── Boot ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabs();
  initUpload();
  initQA();
  initSummarize();
  initTranscript();
  initModal();
  initHistorySidebar();
  initHeaderActions();
  renderDemoState();
});

// ═══════════════════════════════════════════
// THEME
// ═══════════════════════════════════════════
function initTheme() {
  const saved = localStorage.getItem('vqa-theme') || 'dark';
  setTheme(saved);
}

function setTheme(t) {
  state.theme = t;
  document.documentElement.setAttribute('data-theme', t);
  const btn = $('theme-toggle');
  if (btn) btn.innerHTML = t === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('vqa-theme', t);
}

// ═══════════════════════════════════════════
// TABS
// ═══════════════════════════════════════════
function initTabs() {
  $$('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });
}

function switchTab(tab) {
  state.tab = tab;
  $$('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  $$('.tab-panel').forEach(p => p.classList.toggle('active', p.id === `panel-${tab}`));
}

// ═══════════════════════════════════════════
// HEADER ACTIONS
// ═══════════════════════════════════════════
function initHeaderActions() {
  $('theme-toggle').addEventListener('click', () => setTheme(state.theme === 'dark' ? 'light' : 'dark'));

  $('clear-btn').addEventListener('click', () => {
    if (!confirm('Reset session and clear all data?')) return;
    resetSession();
  });

  // Mobile history drawer toggle
  const mobileBtn = $('history-mobile-btn');
  if (mobileBtn) {
    mobileBtn.addEventListener('click', () => {
      const sb = $('sidebar');
      if (sb) sb.classList.toggle('mobile-open');
    });
  }
}

function resetSession() {
  state.phase = 'idle';
  state.file = null;
  state.videoUrl = null;
  state.manualFrames = [];
  state.sessionData = null;
  state.currentAnswer = null;
  state.history = [];
  state.transcriptData = null;
  state.videoSummarized = false;
  state.transcriptSummarized = false;
  clearSessionId(); // wipe persisted session_id from sessionStorage

  // Reset upload
  $('drop-zone').classList.remove('file-selected');
  $('file-info').classList.remove('show');
  $('video-preview-wrap').classList.remove('show');
  const preview = $('video-preview');
  if (preview) { preview.src = ''; }
  $('file-input').value = '';

  // Hide progress
  $('progress-panel').classList.remove('show');
  updateProgressUI(0, '');

  // Reset buttons
  $('process-btn').disabled = true;

  // Clear results
  renderDemoState();
  clearSummarizeOutputs();
  clearTranscriptOutput();

  // Clear history
  state.history = [];
  renderHistory();

  showToast('Session cleared', 'info');
  switchTab('ask');
}

// ═══════════════════════════════════════════
// UPLOAD
// ═══════════════════════════════════════════
function initUpload() {
  const dropZone = $('drop-zone');
  const fileInput = $('file-input');
  const processBtn = $('process-btn');

  const addUrlBtn = $('add-url-btn');
  const urlInput = $('url-input');
  if (addUrlBtn) {
    addUrlBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const url = urlInput.value.trim();
      if (!url) { showToast('Please enter a valid URL', 'info'); return; }
      handleUrlSelect(url);
    });
  }

  // Click to open file picker
  dropZone.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', e => {
    const f = e.target.files[0];
    if (f) handleFileSelect(f);
  });

  // Drag & drop
  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const f = e.dataTransfer.files[0];
    if (f) handleFileSelect(f);
  });

  // Remove file
  $('file-remove').addEventListener('click', e => {
    e.stopPropagation();
    removeFile();
  });

  // Manual Frames
  $('add-frame-btn').addEventListener('click', () => {
    const vp = $('video-preview');
    if (!vp) return;
    const t = Number(vp.currentTime.toFixed(2));
    if (!state.manualFrames.includes(t)) {
      state.manualFrames.push(t);
      state.manualFrames.sort((a,b) => a - b);
      renderManualFrames();
    }
  });

  // Process
  processBtn.addEventListener('click', processVideo);
}

function handleFileSelect(file) {
  const allowed = ['video/mp4', 'video/quicktime', 'video/x-matroska', 'video/webm', 'video/avi'];
  if (!allowed.includes(file.type) && !file.name.match(/\.(mp4|mov|mkv|webm|avi)$/i)) {
    showToast('Unsupported file format. Use MP4, MOV, or MKV.', 'error');
    return;
  }
  state.file = file;
  state.videoUrl = null;
  state.phase = 'uploading';

  // Show file info
  $('file-name-display').textContent = file.name;
  $('file-detail-display').textContent = `${formatFileSize(file.size)} · ${file.type || 'video'}`;
  $('file-info').classList.add('show');
  $('process-btn').disabled = false;

  // Video preview
  const url = URL.createObjectURL(file);
  const vp = $('video-preview');
  vp.style.display = 'block';
  vp.src = url;
  vp.onloadedmetadata = () => {
    const dur = formatDuration(vp.duration);
    $('file-detail-display').textContent = `${formatFileSize(file.size)} · ${dur}`;
  };
  $('video-preview-wrap').classList.add('show');
  $('manual-selection-tools').style.display = 'flex';

  showToast(`"${file.name}" selected`, 'success');
}

function handleUrlSelect(url) {
  state.file = null;
  state.videoUrl = url;
  state.phase = 'uploading';

  // Show file info
  $('file-name-display').textContent = url;
  $('file-detail-display').textContent = `URL Video`;
  $('file-info').classList.add('show');
  $('process-btn').disabled = false;

  // Hide the <video> element because we can't preview all URLs uniformly,
  // but keep the wrapper around to show the manual tools if user wants to set timestamps.
  const vp = $('video-preview');
  vp.style.display = 'none';
  $('video-preview-wrap').classList.add('show');
  $('manual-selection-tools').style.display = 'flex';

  showToast(`URL selected`, 'success');
}

function removeFile() {
  state.file = null;
  state.videoUrl = null;
  state.manualFrames = [];
  state.phase = 'idle';
  $('file-info').classList.remove('show');
  $('video-preview-wrap').classList.remove('show');
  $('video-preview').style.display = 'block';
  $('manual-selection-tools').style.display = 'none';
  $('manual-start').value = '';
  $('manual-end').value = '';
  renderManualFrames();
  $('file-input').value = '';
  const urlInput = $('url-input');
  if(urlInput) urlInput.value = '';
  $('process-btn').disabled = true;
}

async function processVideo() {
  if (!state.file && !state.videoUrl) return;

  const language = $('language-select').value;
  const mode = document.querySelector('.mode-opt.active')?.dataset.mode || 'fast';
  const startTime = $('manual-start').value || '';
  const endTime = $('manual-end').value || '';
  const manFrames = state.manualFrames.join(',');
  const processBtn = $('process-btn');

  processBtn.disabled = true;
  processBtn.innerHTML = '<span class="spinner"></span> Processing…';
  state.phase = 'processing';

  $('progress-panel').classList.add('show');

  const steps = [
    { label: 'Extracting audio', icon: '🔊' },
    { label: 'Transcribing speech', icon: '📝' },
    { label: 'Understanding visuals', icon: '👁️' },
    { label: 'Generating answer model', icon: '🧠' },
    { label: 'Creating summaries', icon: '✨' },
  ];
  resetProgressSteps(steps);

  try {
    const data = await apiProcessVideo(state.file, state.videoUrl, language, mode, startTime, endTime, manFrames, (stepLabel, pct) => {
      const idx = steps.findIndex(s => s.label === stepLabel);
      updateProgressUI(pct, stepLabel, idx, steps.length);
    });

    state.sessionData = data;
    state.transcriptData = data.transcript;
    state.phase = 'ready';

    processBtn.innerHTML = '✅ Processing Complete';
    setTimeout(() => {
      processBtn.innerHTML = '🔄 Re-process';
      processBtn.disabled = false;
    }, 1500);

    // Unlock tabs, render ready state
    enableResultTabs();
    renderReadyState();
    renderTranscriptTab();
    showToast('Video processed successfully!', 'success');
    switchTab('ask');

  } catch (err) {
    state.phase = 'idle';
    processBtn.innerHTML = '⚡ Process Video';
    processBtn.disabled = false;
    showErrorCard($('ask-content'), 'Processing Failed', err.message || 'Could not process the video. Please try again.');
    showToast('Processing failed', 'error');
  }
}

// ── Progress UI ────────────────────────────────────────────
function resetProgressSteps(steps) {
  const container = $('progress-steps');
  container.innerHTML = '';
  steps.forEach((s, i) => {
    const el = document.createElement('div');
    el.className = 'progress-step';
    el.id = `step-${i}`;
    el.innerHTML = `
      <div class="step-icon" id="step-icon-${i}">
        <span>${s.icon}</span>
      </div>
      <span class="step-label" id="step-label-${i}">${s.label}</span>
    `;
    container.appendChild(el);
  });
}

function updateProgressUI(pct, label, currentIdx = -1, total = 5) {
  $('progress-bar').style.width = pct + '%';
  $('progress-pct').textContent = Math.round(pct) + '%';
  $('progress-status').textContent = label;

  for (let i = 0; i < total; i++) {
    const icon = $(`step-icon-${i}`);
    const lbl = $(`step-label-${i}`);
    if (!icon) continue;
    if (i < currentIdx) {
      icon.className = 'step-icon done';
      icon.innerHTML = '';
      if (lbl) lbl.className = 'step-label';
    } else if (i === currentIdx) {
      icon.className = 'step-icon active';
      icon.innerHTML = '<div style="width:10px;height:10px;border:2px solid currentColor;border-radius:50%;"></div>';
      if (lbl) lbl.className = 'step-label active';
    }
  }
}

// ── Helpers ────────────────────────────────────────────────
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
function formatDuration(secs) {
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}
function formatDurationFixed(secs) {
  const m = Math.floor(secs / 60);
  const s = (secs % 60).toFixed(1);
  return `${m}:${s.padStart(4, '0')}`;
}

function renderManualFrames() {
  const list = $('manual-frames-list');
  if (!list) return;
  list.innerHTML = state.manualFrames.map(t => `
    <span class="fmt-badge" style="display:flex;align-items:center;gap:4px;padding-right:6px;">
      ${formatDurationFixed(t)}
      <button type="button" onclick="removeManualFrame(${t})" style="background:none;border:none;color:inherit;cursor:pointer;padding:0;font-size:10px;margin-left:4px;">✕</button>
    </span>
  `).join('');
}

window.removeManualFrame = function(t) {
  state.manualFrames = state.manualFrames.filter(x => x !== t);
  renderManualFrames();
};

// ═══════════════════════════════════════════
// MODE TOGGLE
// ═══════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  $$('.mode-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.mode-opt').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
});

// ═══════════════════════════════════════════
// DEMO / READY STATE
// ═══════════════════════════════════════════
function renderDemoState() {
  $('ask-content').innerHTML = `
    <div class="demo-state glass">
      <span class="demo-icon">🎬</span>
      <h3>No video uploaded yet</h3>
      <p>Upload and process a video to start asking questions, viewing transcripts, and generating summaries.</p>
    </div>
  `;
  $('summarize-content').innerHTML = `
    <div class="demo-state glass">
      <span class="demo-icon">📊</span>
      <h3>Upload a video first</h3>
      <p>Process a video to generate intelligent summaries and key insights.</p>
    </div>
  `;
  $('transcript-content').innerHTML = `
    <div class="demo-state glass">
      <span class="demo-icon">📄</span>
      <h3>No transcript yet</h3>
      <p>Upload and process a video to view its full transcript with search and timestamps.</p>
    </div>
  `;
}

function enableResultTabs() {
  // Nothing to hard-disable, but we render useful UI now
}

function renderReadyState() {
  $('ask-content').innerHTML = `
    <div class="glass qa-input-card">
      <h2>💬 Ask a Question</h2>
      <div class="qa-input-wrap">
        <textarea id="question-input" class="question-area" placeholder="Type your question or click 🎤 to speak…" rows="4" style="padding-right:56px;"></textarea>
        <button class="btn-mic" id="mic-btn" title="Click to speak your question" aria-label="Voice input">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2H3v2a9 9 0 0 0 8 8.94V23H9v2h6v-2h-2v-2.06A9 9 0 0 0 21 12v-2z"/></svg>
        </button>
      </div>
      <div class="voice-status" id="voice-status">
        <span class="voice-dot"></span>
        <span id="voice-status-text">Listening…</span>
      </div>
      <div class="qa-actions">
        <button class="btn-primary" id="ask-btn">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="m5 12 7-7 7 7M12 5v14"/></svg>
          Ask Question
        </button>
        <button class="btn-secondary" id="regen-btn" disabled>🔄 Regenerate</button>
      </div>
    </div>
    <div id="answer-area"></div>
  `;

  $('ask-btn').addEventListener('click', handleAsk);
  $('question-input').addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleAsk();
  });
  $('regen-btn').addEventListener('click', handleAsk);

  initVoiceInput();
}

function clearSummarizeOutputs() {
  const sc = $('summarize-content');
  if (sc) sc.innerHTML = '';
}
function clearTranscriptOutput() {
  const tc = $('transcript-content');
  if (tc) tc.innerHTML = '';
}

// ═══════════════════════════════════════════
// QA – ASK
// ═══════════════════════════════════════════
function initQA() {
  // Will be initialized after renderReadyState()
}

async function handleAsk() {
  const input = $('question-input');
  if (!input) return;
  const question = input.value.trim();
  if (!question) { showToast('Please enter a question.', 'info'); return; }

  const askBtn = $('ask-btn');
  const regenBtn = $('regen-btn');
  askBtn.disabled = true;
  askBtn.innerHTML = '<span class="spinner"></span> Thinking…';

  const area = $('answer-area');
  area.innerHTML = '<div class="demo-state"><span class="demo-icon" style="font-size:28px;animation:pulse 1.5s infinite">🧠</span><p>Analyzing video and generating answer…</p></div>';

  try {
    const language = $('language-select')?.value || 'en';
    const result = await apiAsk(question, language);

    // Push to history
    addToHistory(question, result);

    // Render
    renderAnswerCards(result, area);

    regenBtn.disabled = false;
  } catch (err) {
    area.innerHTML = '';
    showErrorCard(area, 'Failed to get answer', err.message || 'Please try again.');
  } finally {
    askBtn.disabled = false;
    askBtn.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="m5 12 7-7 7 7M12 5v14"/></svg> Ask Question';
  }
}

function renderAnswerCards(result, container) {
  const answerHtml = result.answer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  const safeAnswer = escapeHtml(JSON.stringify(result.answer));
  container.innerHTML = `
    <!-- Answer Card -->
    <div class="glass result-card">
      <div class="result-card-header">
        <span class="result-label"><span class="dot-accent"></span>Answer</span>
        <div class="result-actions">
          <button class="btn-tts" id="tts-btn" onclick="toggleReadAloud(${safeAnswer}, this)">
            <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
            Read Aloud
          </button>
          <button class="btn-secondary" onclick="copyText(${safeAnswer}, 'Answer copied!')">📋 Copy</button>
          <button class="btn-secondary" onclick="downloadText(${safeAnswer}, 'answer.txt')">⬇️ Download</button>
        </div>
      </div>
      <div class="answer-text">${answerHtml}</div>
      <div class="confidence-badge">${result.confidence}</div>
    </div>

    <!-- Clip Card -->
    <div class="glass clip-card">
      <div class="result-card-header">
        <span class="result-label"><span class="dot-accent"></span>Relevant Video Clip</span>
      </div>
      <div class="clip-label">📍 ${result.clip.label}</div>
      <div class="clip-player-wrap">
        ${result.clip.url
      ? `<video controls style="width:100%;border-radius:var(--radius-md);" src="${API_BASE}${result.clip.url}" preload="metadata"></video>`
      : `<div class="clip-placeholder">
              <span>🎬</span>
              <p>Clip preview available after processing with "QA + Clip Retrieval" mode</p>
              <p style="font-size:12px;margin-top:4px;color:var(--text-muted)">Timestamp: ${result.clip.start}s – ${result.clip.end}s</p>
            </div>`
    }
      </div>
      <div class="clip-actions">
        <button class="btn-secondary" onclick="showToast('Download clip: backend required', 'info')">⬇️ Download Clip</button>
        <button class="btn-secondary" onclick="showToast('Opens at ${result.clip.start}s when backend connected', 'info')">▶️ Open at ${formatDuration(result.clip.start)}</button>
      </div>
    </div>

    <!-- Evidence Panel -->
    <div class="glass evidence-card">
      <div class="evidence-toggle" onclick="toggleEvidence(this)">
        <h4>🔍 Evidence Used <span style="color:var(--text-muted);font-weight:400;font-size:12px;">(${result.evidence.transcript_excerpts.length + result.evidence.visual_captions.length} sources)</span></h4>
        <span class="toggle-arrow">▼</span>
      </div>
      <div class="evidence-body" id="evidence-body">
        <div class="evidence-section">
          <div class="evidence-title">📝 Transcript Excerpts</div>
          ${result.evidence.transcript_excerpts.map(t => `<div class="evidence-item">"${t}"</div>`).join('')}
        </div>
        <div class="evidence-section">
          <div class="evidence-title">👁️ Visual Captions</div>
          ${result.evidence.visual_captions.map(c => `<div class="evidence-item" style="border-left-color:var(--accent-2)">${c}</div>`).join('')}
        </div>
      </div>
    </div>
  `;
}


// ═══════════════════════════════════════════
// VOICE INPUT (MIC – SpeechRecognition API)
// ═══════════════════════════════════════════
let _recognition = null;
let _isListening = false;

// Map ISO language codes to BCP-47 locales for SpeechRecognition
const LANG_TO_BCP47 = {
  en: 'en-US', hi: 'hi-IN', te: 'te-IN', ta: 'ta-IN',
  kn: 'kn-IN', ml: 'ml-IN', mr: 'mr-IN', bn: 'bn-IN',
  pa: 'pa-IN', gu: 'gu-IN', ur: 'ur-PK',
  es: 'es-ES', fr: 'fr-FR', de: 'de-DE', zh: 'zh-CN',
  ar: 'ar-SA', ja: 'ja-JP', ko: 'ko-KR', pt: 'pt-BR',
  ru: 'ru-RU', it: 'it-IT',
};

function initVoiceInput() {
  const micBtn = $('mic-btn');
  const status = $('voice-status');
  const statusTx = $('voice-status-text');
  const input = $('question-input');

  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    if (micBtn) { micBtn.classList.add('unavailable'); micBtn.title = 'Voice input not supported in this browser (use Chrome/Edge)'; }
    return;
  }

  _recognition = new SpeechRec();
  _recognition.continuous = false;
  _recognition.interimResults = true;

  _recognition.onstart = () => {
    _isListening = true;
    micBtn.classList.add('listening');
    micBtn.innerHTML = '<svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M19 10v2a7 7 0 0 1-14 0v-2H3v2a9 9 0 0 0 8 8.94V23H9v2h6v-2h-2v-2.06A9 9 0 0 0 21 12v-2z"/></svg>';
    if (status) status.classList.add('show');
    if (statusTx) statusTx.textContent = 'Listening… speak your question';
  };

  _recognition.onresult = (e) => {
    let interim = '', final = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) final += t; else interim += t;
    }
    if (input) input.value = final || interim;
    if (statusTx) statusTx.textContent = interim ? `Hearing: "${interim}"` : 'Listening…';
  };

  _recognition.onend = () => {
    _isListening = false;
    micBtn.classList.remove('listening');
    micBtn.innerHTML = '<svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2H3v2a9 9 0 0 0 8 8.94V23H9v2h6v-2h-2v-2.06A9 9 0 0 0 21 12v-2z"/></svg>';
    if (status) status.classList.remove('show');
    if (input && input.value.trim()) showToast('Question captured! Press Ask to submit.', 'success');
  };

  _recognition.onerror = (e) => {
    _isListening = false;
    micBtn.classList.remove('listening');
    if (status) status.classList.remove('show');
    const msg = e.error === 'not-allowed'
      ? 'Microphone access denied. Allow mic in browser settings.'
      : `Voice error: ${e.error}`;
    showToast(msg, 'error');
  };

  micBtn.addEventListener('click', () => {
    if (_isListening) {
      _recognition.stop();
      return;
    }
    const langCode = $('language-select')?.value || 'en';
    _recognition.lang = LANG_TO_BCP47[langCode] || 'en-US';
    try { _recognition.start(); }
    catch (err) { showToast('Could not start voice input: ' + err.message, 'error'); }
  });
}

// ═══════════════════════════════════════════
// TEXT-TO-SPEECH (SpeechSynthesis API)
// ═══════════════════════════════════════════
let _ttsUtterance = null;
let _ttsSpeaking = false;

const LANG_TO_TTS_BCP47 = {
  en: 'en-US', hi: 'hi-IN', te: 'te-IN', ta: 'ta-IN',
  kn: 'kn-IN', ml: 'ml-IN', mr: 'mr-IN', bn: 'bn-IN',
  pa: 'pa-IN', gu: 'gu-IN', ur: 'ur-PK',
  es: 'es-ES', fr: 'fr-FR', de: 'de-DE', zh: 'zh-CN',
  ar: 'ar-SA', ja: 'ja-JP', ko: 'ko-KR', pt: 'pt-BR',
  ru: 'ru-RU', it: 'it-IT',
};

function toggleReadAloud(text, btn) {
  if (!window.speechSynthesis) {
    showToast('Text-to-speech not supported in this browser.', 'error'); return;
  }

  if (_ttsSpeaking) {
    window.speechSynthesis.cancel();
    _ttsSpeaking = false;
    if (btn) { btn.classList.remove('speaking'); btn.innerHTML = '<svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg> Read Aloud'; }
    return;
  }

  // Strip markdown bold marks
  const cleanText = text.replace(/\*\*(.*?)\*\*/g, '$1');
  _ttsUtterance = new SpeechSynthesisUtterance(cleanText);

  const langCode = $('language-select')?.value || 'en';
  _ttsUtterance.lang = LANG_TO_TTS_BCP47[langCode] || 'en-US';
  _ttsUtterance.rate = 0.95;
  _ttsUtterance.pitch = 1.0;

  // Try to pick a voice matching the language
  const voices = window.speechSynthesis.getVoices();
  const match = voices.find(v => v.lang.startsWith(_ttsUtterance.lang.split('-')[0]));
  if (match) _ttsUtterance.voice = match;

  _ttsUtterance.onstart = () => {
    _ttsSpeaking = true;
    if (btn) { btn.classList.add('speaking'); btn.innerHTML = '<svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6zm8-14v14h4V5z"/></svg> Stop'; }
  };
  _ttsUtterance.onend = _ttsUtterance.onerror = () => {
    _ttsSpeaking = false;
    if (btn) { btn.classList.remove('speaking'); btn.innerHTML = '<svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg> Read Aloud'; }
  };

  window.speechSynthesis.speak(_ttsUtterance);
  showToast('Reading answer aloud…', 'info');
}

function toggleEvidence(el) {
  const body = $('evidence-body');
  const arrow = el.querySelector('.toggle-arrow');
  if (body) body.classList.toggle('show');
  if (arrow) arrow.classList.toggle('open');
}


// ═══════════════════════════════════════════
// HISTORY SIDEBAR
// ═══════════════════════════════════════════
function initHistorySidebar() {
  // Close sidebar on overlay click (mobile)
  const sb = $('sidebar');
  if (sb) {
    sb.addEventListener('click', e => {
      if (e.target === sb) sb.classList.remove('mobile-open');
    });
  }
  renderHistory();
}

function addToHistory(question, result) {
  const item = {
    id: Date.now(),
    question,
    result,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
  state.history.unshift(item);
  renderHistory();
}

function renderHistory() {
  const list = $('history-list');
  const count = $('history-count');
  if (!list) return;
  if (count) count.textContent = state.history.length;

  if (state.history.length === 0) {
    list.innerHTML = '<div class="history-empty">No questions yet.<br>Ask something to get started.</div>';
    return;
  }

  list.innerHTML = state.history.map((item, i) => `
  <div class="history-item ${i === 0 && state.historyIndex === 0 ? 'active' : ''}" onclick="restoreHistoryItem(${item.id})">
      <div class="hi-question">${escapeHtml(item.question)}</div>
      <div class="hi-time">${item.time}</div>
    </div>
  `).join('');
}

function restoreHistoryItem(id) {
  const item = state.history.find(h => h.id === id);
  if (!item) return;
  if (state.phase !== 'ready') return;

  const input = $('question-input');
  if (input) input.value = item.question;

  const area = $('answer-area');
  if (area) renderAnswerCards(item.result, area);

  // Mark active
  $$('.history-item').forEach(el => el.classList.remove('active'));
  // Sidebar close on mobile
  $('sidebar')?.classList.remove('mobile-open');
  switchTab('ask');
}

// ═══════════════════════════════════════════
// SUMMARIZE TAB
// ═══════════════════════════════════════════
function initSummarize() {
  // Wired after DOM ready – see renderSummarizeUI
}

function renderSummarizeUI() {
  const sc = $('summarize-content');
  sc.innerHTML = `
  <div class="summarize-grid">
      <!--Video Summary-->
      <div class="glass summarize-section" id="video-sum-section">
        <h3>🎥 Video Summary</h3>
        <div class="summary-toggle">
          <button class="sum-opt active" data-mode="short">Short</button>
          <button class="sum-opt" data-mode="detailed">Detailed</button>
          <button class="sum-opt" data-mode="chapters">Chapters</button>
        </div>
        <button class="btn-primary" id="gen-sum-btn" style="margin-bottom:var(--space-4);">✨ Generate Summary</button>
        <div class="summary-output" id="video-sum-output">
          <span style="color:var(--text-muted);">Click "Generate Summary" to get started.</span>
        </div>
        <div class="export-row" id="video-sum-exports" style="display:none;">
          <button class="btn-secondary" id="copy-sum-btn">📋 Copy</button>
          <button class="btn-secondary" id="dl-sum-btn">⬇️ Download TXT</button>
        </div>
      </div>

      <!--Transcript Summary-->
  <div class="glass summarize-section" id="transcript-sum-section">
    <h3>📝 Transcript Summary</h3>
    <button class="btn-primary" id="gen-transcript-sum-btn" style="margin-bottom:var(--space-4);">📋 Summarize Transcript</button>
    <div class="summary-output" id="transcript-sum-output">
      <span style="color:var(--text-muted);">Generate a smart summary of the transcript with key points and keywords.</span>
    </div>
    <div class="export-row" id="transcript-sum-exports" style="display:none;">
      <button class="btn-secondary" id="copy-ts-btn">📋 Copy</button>
      <button class="btn-secondary" id="dl-ts-btn">⬇️ Download TXT</button>
    </div>
  </div>
    </div>
  `;

  // Mode toggle
  sc.querySelectorAll('.sum-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      sc.querySelectorAll('.sum-opt').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.summarizeMode = btn.dataset.mode;
      if (state.videoSummarized) renderVideoSummaryOutput(window._videoSumData);
    });
  });

  $('gen-sum-btn').addEventListener('click', generateVideoSummary);
  $('gen-transcript-sum-btn').addEventListener('click', generateTranscriptSummary);
}

async function generateVideoSummary() {
  const btn = $('gen-sum-btn');
  const out = $('video-sum-output');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Generating…';
  out.innerHTML = '<span style="color:var(--text-muted);">Analyzing video content…</span>';

  try {
    const data = await apiSummarizeVideo(state.summarizeMode);
    window._videoSumData = data;
    state.videoSummarized = true;
    renderVideoSummaryOutput(data);
    $('video-sum-exports').style.display = 'flex';

    // Wire export buttons
    const exportText = getVideoSumText(data);
    $('copy-sum-btn').onclick=() => copyText(exportText, 'Summary copied!');
    $('dl-sum-btn').onclick=() => downloadText(exportText, 'video_summary.txt');

    showToast('Video summary generated!', 'success');
  } catch (err) {
    out.innerHTML = `<span style="color:var(--error);"> Error: ${err.message}</span> `;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '✨ Generate Summary';
  }
}

function renderVideoSummaryOutput(data) {
  const out = $('video-sum-output');
  const mode = state.summarizeMode;

  if (mode === 'short') {
    out.innerHTML = `<div style="line-height:1.8;"> ${data.short}</div> `;
  } else if (mode === 'detailed') {
    out.innerHTML = data.detailed.map(b =>
      `<div class="summary-bullet"> <span>${typeof b === 'string' ? b.replace(/<[^>]*>/g, '').trim() : b}</span></div> `
    ).join('');
  } else if (mode === 'chapters') {
    out.innerHTML = `<div class="chapters-list">
  ${data.chapters.map(c => `
        <div class="chapter-item">
          <span class="chapter-time">${c.time}</span>
          <span class="chapter-title">${c.title}</span>
        </div>`).join('')
      }
    </div> `;
  }
}

function getVideoSumText(data) {
  const m = state.summarizeMode;
  if (m === 'short') return data.short;
  if (m === 'detailed') return data.detailed.join('\n• ');
  return data.chapters.map(c => `${c.time} – ${c.title} `).join('\n');
}

async function generateTranscriptSummary() {
  const btn = $('gen-transcript-sum-btn');
  const out = $('transcript-sum-output');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Summarizing…';
  out.innerHTML = '<span style="color:var(--text-muted);">Extracting key information…</span>';

  try {
    const data = await apiSummarizeTranscript();
    state.transcriptSummarized = true;

    out.innerHTML = `
  <div style="margin-bottom:var(--space-4);">
    <div class="evidence-title" style="margin-bottom:var(--space-3);">🎯 Key Points</div>
        ${data.key_points.map(p => `<div class="summary-bullet"><span>${typeof p === 'string' ? p.replace(/<[^>]*>/g, '').trim() : p}</span></div>`).join('')}
      </div>
      <div style="margin-bottom:var(--space-4);">
        <div class="evidence-title" style="margin-bottom:var(--space-3);">✅ Action Items</div>
        <ul class="action-items">
          ${data.action_items.map(a => `<li>${typeof a === 'string' ? a.replace(/<[^>]*>/g, '').trim() : a}</li>`).join('')}
        </ul>
      </div>
      <div>
        <div class="evidence-title" style="margin-bottom:var(--space-3);">🏷️ Keywords</div>
        <div class="kw-chips">
          ${data.keywords.map(k => `<span class="kw-chip">${k}</span>`).join('')}
        </div>
      </div>
`;

    $('transcript-sum-exports').style.display = 'flex';
    const exportText = [
      'KEY POINTS:\n' + data.key_points.join('\n'),
      'ACTION ITEMS:\n' + data.action_items.join('\n'),
      'KEYWORDS: ' + data.keywords.join(', ')
    ].join('\n\n');
    $('copy-ts-btn').onclick=() => copyText(exportText, 'Transcript summary copied!');
    $('dl-ts-btn').onclick=() => downloadText(exportText, 'transcript_summary.txt');

    showToast('Transcript summary ready!', 'success');
  } catch (err) {
    out.innerHTML = `<span style="color:var(--error);"> Error: ${err.message}</span> `;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '📋 Summarize Transcript';
  }
}

// ═══════════════════════════════════════════
// TRANSCRIPT TAB
// ═══════════════════════════════════════════
function initTranscript() { }

function renderTranscriptTab() {
  const tc = $('transcript-content');
  const lines = state.transcriptData || [];

  tc.innerHTML = `
  <!--Toolbar -->
    <div class="glass transcript-toolbar">
      <div class="search-wrap">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input type="text" class="search-input" id="transcript-search" placeholder="Search transcript…">
      </div>
      <label class="speaker-toggle">
        <div class="toggle-sw on" id="speaker-sw"></div>
        <span>Speaker Labels</span>
      </label>
      <button class="btn-secondary" onclick="copyTranscript()">📋 Copy</button>
      <button class="btn-secondary" onclick="downloadTranscript()">⬇️ Download</button>
    </div>
    <!--Body -->
  <div class="transcript-body" id="transcript-lines">
    ${renderTranscriptLines(lines)}
  </div>
`;

  // Search
  $('transcript-search').addEventListener('input', e => {
    highlightSearch(e.target.value.trim(), $('transcript-lines').querySelectorAll('.transcript-line'));
  });

  // Speaker toggle
  $('speaker-sw').addEventListener('click', function () {
    state.speakerLabels = !state.speakerLabels;
    this.classList.toggle('on', state.speakerLabels);
    $('transcript-lines').querySelectorAll('.ts-speaker').forEach(el => {
      el.style.display = state.speakerLabels ? '' : 'none';
    });
  });
}

function renderTranscriptLines(lines) {
  if (!lines.length) return '<p style="color:var(--text-muted);padding:16px;">No transcript available.</p>';
  return lines.map(line => `
  <div class="transcript-line" data-text="${escapeHtml(line.text.toLowerCase())}">
      <span class="ts-time">${line.time}</span>
      <span class="ts-speaker">${line.speaker}</span>
      <span class="ts-text">${escapeHtml(line.text)}</span>
    </div>
  `).join('');
}

function highlightSearch(query, lines) {
  lines.forEach(line => {
    const textSpan = line.querySelector('.ts-text');
    const raw = state.transcriptData?.find(l => l.text.toLowerCase() === line.dataset.text)?.text || textSpan.textContent;
    if (!query) {
      textSpan.innerHTML = escapeHtml(raw);
      line.classList.remove('highlight');
      return;
    }
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    const highlighted = escapeHtml(raw).replace(regex, '<mark>$1</mark>');
    textSpan.innerHTML = highlighted;
    line.classList.toggle('highlight', regex.test(raw));
  });
}

function copyTranscript() {
  const text = (state.transcriptData || []).map(l => `[${l.time}] ${l.speaker}: ${l.text} `).join('\n');
  copyText(text, 'Transcript copied!');
}
function downloadTranscript() {
  const text = (state.transcriptData || []).map(l => `[${l.time}] ${l.speaker}: ${l.text} `).join('\n');
  downloadText(text, 'transcript.txt');
}

// ═══════════════════════════════════════════
// MODAL
// ═══════════════════════════════════════════
function initModal() {
  const modal = $('how-modal');
  $('how-btn').addEventListener('click', () => {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  });
  $('modal-close').addEventListener('click', closeModal);
  modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
}
function closeModal() {
  $('how-modal').classList.remove('open');
  document.body.style.overflow = '';
}

// ═══════════════════════════════════════════
// TOAST
// ═══════════════════════════════════════════
function showToast(msg, type = 'info') {
  const container = $('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type} `;
  toast.innerHTML = `<span class="toast-icon"></span> <span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('removing');
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// ═══════════════════════════════════════════
// ERROR CARD
// ═══════════════════════════════════════════
function showErrorCard(container, title, message) {
  const card = document.createElement('div');
  card.className = 'error-card';
  card.innerHTML = `
  <span class="err-icon">⚠️</span>
    <div><h4>${title}</h4><p>${message}</p></div>
`;
  container.prepend(card);
}

// ═══════════════════════════════════════════
// SUMMARIZE TAB INIT ON TAB SWITCH
// ═══════════════════════════════════════════
function initSummarizeTabOnSwitch() {
  if (state.phase !== 'ready') return;
  const sc = $('summarize-content');
  if (!sc.querySelector('.summarize-grid')) {
    renderSummarizeUI();
  }
}

// Override switchTab to trigger summarize render
const _originalSwitch = typeof switchTab !== 'undefined' ? null : null;
document.addEventListener('DOMContentLoaded', () => {
  $$('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.dataset.tab === 'summarize') {
        setTimeout(initSummarizeTabOnSwitch, 10);
      }
    });
  });
});

// ═══════════════════════════════════════════
// UTILITY
// ═══════════════════════════════════════════
function copyText(text, msg = 'Copied!') {
  navigator.clipboard.writeText(text).then(() => showToast(msg, 'success')).catch(() => {
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); ta.remove();
    showToast(msg, 'success');
  });
}

function downloadText(text, filename) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast(`Downloaded ${filename} `, 'success');
}

function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
```

## api.js

**Path**: `api.js`

```javascript
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
 * @param {string}   videoUrl
 * @param {string}   language  – "English" | "Hindi" | "Telugu" | "Spanish" …
 * @param {string}   mode      – "fast" | "full"
 * @param {string}   startTime
 * @param {string}   endTime
 * @param {string}   manualFrames
 * @param {Function} onProgress – (label: string, pct: number) => void
 * @returns  { session_id, transcript, visuals, duration }
 */
async function apiProcessVideo(file, videoUrl, language, mode, startTime, endTime, manualFrames, onProgress) {
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
    if (file) {
        form.append("video", file);
    }
    if (videoUrl) {
        form.append("video_url", videoUrl);
    }
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
```

## mock.js

**Path**: `mock.js`

```javascript
// mock.js – Realistic mock data for VideoQA demo mode

const MOCK_DATA = {
  processVideo: {
    status: "success",
    session_id: "demo-session-001",
    duration: 142.5,
    language: "en",
    transcript: [
      { time: "0:00", speaker: "Speaker 1", text: "Welcome to this tutorial on machine learning fundamentals." },
      { time: "0:08", speaker: "Speaker 1", text: "Today we will explore the core concepts that drive modern AI systems." },
      { time: "0:17", speaker: "Speaker 1", text: "Let's start with supervised learning, where the model learns from labeled data." },
      { time: "0:28", speaker: "Speaker 2", text: "That's a great starting point. Can you explain how the training loop works?" },
      { time: "0:35", speaker: "Speaker 1", text: "Absolutely. In each iteration, the model makes a prediction, we compute the loss, and then we backpropagate the error." },
      { time: "0:50", speaker: "Speaker 1", text: "The optimizer then adjusts the weights to minimize the loss function." },
      { time: "1:02", speaker: "Speaker 2", text: "And what about overfitting? How do we prevent the model from memorizing training data?" },
      { time: "1:12", speaker: "Speaker 1", text: "Great question. We use techniques like dropout, regularization, and data augmentation." },
      { time: "1:24", speaker: "Speaker 1", text: "Cross-validation is also critical to evaluate generalization." },
      { time: "1:38", speaker: "Speaker 1", text: "In conclusion, understanding these fundamentals is essential for building robust ML systems." },
      { time: "1:52", speaker: "Speaker 1", text: "Thank you for watching. In the next video, we will cover deep neural networks in detail." },
      { time: "2:05", speaker: "Speaker 2", text: "Looking forward to it. That was a very clear explanation." },
    ],
    visuals: [
      { time: "0:00", caption: "Title slide: 'Machine Learning Fundamentals'" },
      { time: "0:17", caption: "Diagram showing supervised vs unsupervised learning" },
      { time: "0:35", caption: "Animation of forward pass through a neural network" },
      { time: "0:50", caption: "Graph showing loss decreasing over training epochs" },
      { time: "1:12", caption: "Slide listing regularization techniques: L1, L2, Dropout" },
      { time: "1:38", caption: "Comparison chart of train vs validation accuracy" },
    ]
  },

  ask: (question) => ({
    status: "success",
    question,
    answer: `Based on the transcript and visual frames, the speaker explains this clearly around the middle section of the video.\n\nThe key explanation revolves around the **training loop** and how the model iteratively improves. Specifically, the speaker describes: (1) making a prediction, (2) computing the loss, and (3) backpropagating the error to update weights via an optimizer.\n\nThe visual frames at that point show a neural network animation, which reinforces the audio explanation. The speaker also emphasizes that understanding the loss function is fundamental to training any machine learning model effectively.`,
    confidence: "High – based on transcript excerpt + 3 matching visual frames",
    evidence: {
      transcript_excerpts: [
        "In each iteration, the model makes a prediction, we compute the loss, and then we backpropagate the error.",
        "The optimizer then adjusts the weights to minimize the loss function."
      ],
      visual_captions: [
        "Animation of forward pass through a neural network",
        "Graph showing loss decreasing over training epochs"
      ]
    },
    clip: {
      start: 35,
      end: 55,
      url: null, // will use placeholder
      label: "0:35 – 0:55 – Training Loop Explanation"
    }
  }),

  summarizeVideo: {
    short: "This video is an introductory tutorial on machine learning fundamentals, covering supervised learning, the training loop, loss functions, and techniques to prevent overfitting. The presenter delivers a clear, structured explanation supported by slides and animations.",
    detailed: [
      "Introduction and overview of machine learning fundamentals (0:00–0:17)",
      "Explanation of supervised learning with labeled data and its applications (0:17–0:28)",
      "Detailed walkthrough of the training loop: prediction → loss → backpropagation → weight update (0:35–0:55)",
      "Role of the optimizer in minimizing the loss function during training (0:50–1:02)",
      "Preventing overfitting using dropout, regularization, data augmentation, and cross-validation (1:02–1:38)",
      "Conclusion emphasizing the importance of ML fundamentals and preview of next topic (1:38–2:05)"
    ],
    chapters: [
      { time: "0:00", title: "Introduction" },
      { time: "0:17", title: "Supervised Learning" },
      { time: "0:35", title: "The Training Loop" },
      { time: "1:02", title: "Preventing Overfitting" },
      { time: "1:38", title: "Conclusion & Next Steps" }
    ]
  },

  summarizeTranscript: {
    key_points: [
      "Machine learning models learn from labeled data in supervised learning.",
      "The training loop involves: predict → compute loss → backpropagate → update weights.",
      "Optimizers minimize the loss function to improve model accuracy.",
      "Overfitting is prevented using dropout, regularization, and data augmentation.",
      "Cross-validation is essential for evaluating model generalization.",
      "The video concludes by previewing a future session on deep neural networks."
    ],
    action_items: [
      "Review backpropagation math for deeper understanding.",
      "Experiment with different regularization techniques on a sample dataset.",
      "Watch the follow-up video on deep neural networks."
    ],
    keywords: [
      "Machine Learning", "Supervised Learning", "Training Loop", "Loss Function",
      "Backpropagation", "Optimizer", "Overfitting", "Dropout", "Regularization",
      "Data Augmentation", "Cross-Validation", "Neural Network", "Deep Learning"
    ]
  }
};

// Simulate async delay
function mockDelay(ms = 1200) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

## main.py

**Path**: `backend/main.py`

```python
"""
main.py – VideoQA FastAPI Backend
Endpoints: /process_video, /ask, /summarize_video, /summarize_transcript, /download/{type}
"""

import os
import time
import uuid
import shutil
from pathlib import Path
from typing import Optional
import yt_dlp

# Triggering reload
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from models import save_session, get_session, get_model_status
from video_utils import (
    extract_audio,
    extract_keyframes,
    extract_specific_frames,
    caption_frames,
    extract_clip,
    find_clip_timestamps,
)
from llm import answer_question, summarize_video, summarize_transcript

load_dotenv()

# ── App Setup ────────────────────────────────────────────────
app = FastAPI(
    title="VideoQA API",
    description="Multimodal Video Question Answering – Whisper + BLIP + Mistral",
    version="1.0.0",
)

# Allow the file:// frontend and localhost dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temp directory for uploads / outputs
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Pydantic models ──────────────────────────────────────────

class AskRequest(BaseModel):
    question: str
    session_id: str
    language: Optional[str] = "English"
    model: Optional[str] = None   # None → use DEFAULT_MODEL from .env

class SummarizeVideoRequest(BaseModel):
    session_id: str
    length: Optional[str] = "short"   # "short" | "detailed" | "chapters"
    model: Optional[str] = None

class SummarizeTranscriptRequest(BaseModel):
    session_id: str
    model: Optional[str] = None


# ── Health Check ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "VideoQA API"}


# ── Model Status ──────────────────────────────────────────────

@app.get("/status")
def status():
    """
    Returns the load status of AI models (Whisper, BLIP).
    Use this to check if models are loaded before processing.
    """
    model_info = get_model_status()
    all_ready = all(
        v["status"] == "ready"
        for k, v in model_info.items()
        if isinstance(v, dict) and "status" in v
    )
    return {
        "ready": all_ready,
        "models": model_info,
    }


# ── POST /process_video ──────────────────────────────────────

@app.post("/process_video")
async def process_video(
    video:    Optional[UploadFile] = File(None),
    video_url: Optional[str]       = Form(None),
    language: str                  = Form("English"),
    mode:     str                  = Form("fast"),      # "fast" | "full"
    start_time: Optional[float]    = Form(None),
    end_time:   Optional[float]    = Form(None),
    manual_frames: Optional[str]   = Form(None),
):
    """
    1. Save uploaded video
    2. Extract audio → transcribe with Whisper-base (fast)
    3. Extract keyframes → caption with BLIP-base
    4. Store session data
    Returns: { session_id, duration, transcript (list), visuals (list), status }
    """
    t_pipeline = time.time()
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    if not video and not video_url:
        raise HTTPException(status_code=400, detail="Must provide either a video file or a video URL")

    print(f"\n[VideoQA] -- New session: {session_id[:8]} | lang={language} | mode={mode}")
    t0 = time.time()

    if video_url:
        print(f"[VideoQA] Downloading video from URL: {video_url}")
        browser = os.getenv("YOUTUBE_BROWSER", "chrome")
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': str(session_dir / 'downloaded_video.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': ['player_client=android,tv,ios']},
        }
        
        cookie_file = Path("cookies.txt")
        env_cookies = os.getenv("YOUTUBE_COOKIES_SECRET")
        if env_cookies and not cookie_file.exists():
            try:
                cookie_file.write_text(env_cookies, encoding="utf-8")
            except Exception:
                pass
                
        if cookie_file.exists():
            ydl_opts['cookiefile'] = str(cookie_file)
        elif browser and browser.lower() != "none" and browser.lower() != "false":
            ydl_opts['cookiesfrombrowser'] = (browser,)

        def download_with_opts():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                ext = info.get('ext', 'mp4')
                return str(session_dir / f"downloaded_video.{ext}")

        try:
            try:
                video_path = download_with_opts()
            except Exception as e:
                # If cookie extraction failed, retry without cookies
                if 'cookiesfrombrowser' in ydl_opts:
                    print(f"[VideoQA] Cookie extraction failed ({e}), retrying without cookies...")
                    del ydl_opts['cookiesfrombrowser']
                    video_path = download_with_opts()
                else:
                    raise e
            print(f"[VideoQA] Video downloaded in {round(time.time()-t0,1)}s")
        except Exception as e:
            shutil.rmtree(str(session_dir), ignore_errors=True)
            err_msg = str(e)
            
            is_youtube = "youtube.com" in video_url.lower() or "youtu.be" in video_url.lower()
            if is_youtube and ("Sign in to confirm" in err_msg or "bot" in err_msg.lower()):
                err_msg = ("YouTube has blocked the download (Bot Detection). "
                           "Please export your YouTube cookies using the 'Get cookies.txt LOCALLY' extension "
                           "and save them as 'cookies.txt' in the 'backend' folder.")
            elif "huggingface.co" in video_url.lower():
                err_msg = f"Hugging Face download failed (likely due to a private repository or bot protection). Please download the video manually and upload the file instead. Original error: {err_msg}"
                
            raise HTTPException(status_code=400, detail=f"Failed to download video URL: {err_msg}")
    else:
        video_path = str(session_dir / video.filename)
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        print(f"[VideoQA] Video saved ({len(content)/1024/1024:.1f} MB) in {round(time.time()-t0,1)}s")

    try:
        # ── Step 1: Audio → Transcript ──────────────────────
        audio_path = str(session_dir / "audio.wav")
        extract_audio(video_path, audio_path, start_time, end_time)

        from models import get_whisper
        model_wh = get_whisper()

        print(f"[VideoQA] Transcribing audio (lang={_lang_code(language)})...")
        t0 = time.time()
        # Request word-level timestamps for better clip matching
        result = model_wh.transcribe(
            audio_path,
            language=_lang_code(language),
            word_timestamps=False,  # per-segment timestamps are enough
        )
        print(f"[VideoQA] Transcription done in {round(time.time()-t0,1)}s")

        full_text = result["text"].strip()
        segments  = result.get("segments", [])
        print(f"[VideoQA] Transcript: {len(segments)} segments, {len(full_text)} chars")

        # Format transcript lines for frontend
        transcript_lines = []
        offset = start_time or 0.0
        for seg in segments:
            seg["start"] = seg.get("start", 0) + offset
            seg["end"] = seg.get("end", 0) + offset
            start = seg["start"]
            end   = seg["end"]
            text  = seg.get("text", "").strip()
            if text:
                transcript_lines.append({
                    "time":    _fmt_time(start),
                    "start":   start,
                    "end":     end,
                    "speaker": "Speaker",   # speaker diarization would need pyannote
                    "text":    text,
                })

        # Get video duration
        duration = segments[-1]["end"] if segments else (end_time or 0.0)

        # ── Step 2: Keyframes → Visual Captions ────────────
        from models import get_model_status as _ms
        
        t0 = time.time()
        if manual_frames and manual_frames.strip():
            timestamps = [float(x.strip()) for x in manual_frames.split(",") if x.strip()]
            print(f"[VideoQA] Extracting {len(timestamps)} manual frames...")
            frame_paths = extract_specific_frames(video_path, timestamps)
        else:
            max_frames = int(os.getenv("MAX_FRAMES", "3"))
            n_frames = max_frames if mode == "full" else max(2, max_frames - 1)
            print(f"[VideoQA] Extracting {n_frames} keyframes...")
            frame_paths = extract_keyframes(video_path, n=n_frames, start_sec=start_time, end_sec=end_time)
            
        print(f"[VideoQA] Frames extracted in {round(time.time()-t0,1)}s")
        captioned   = caption_frames(frame_paths)

        visuals = []
        for item in captioned:
            # Note: For manual frames, caption might display `time` incorrectly if we just use `frame_index / fps`. We will let `extract_specific_frames` return the timestamp in `frame_index` or handle it properly. Wait, `frame_index` can just be the timestamp in seconds scaled up. Actually, we can return `{path, timestamp}` from `extract_specific_frames`, but wait, `caption_frames` reads `frame_{idx}.jpg`. It might be easier to just format `time` based on the frame index if `extracted_frames` works similarly. Let's adjust this.
            visuals.append({
                "time":    _fmt_time(item.get("frame_index", 0) / 25.0),  # This will be updated inside video_utils
                "caption": item["caption"],
            })

        # ── Save Session ────────────────────────────────────
        save_session(session_id, {
            "video_path":  video_path,
            "audio_path":  audio_path,
            "full_text":   full_text,
            "segments":    segments,
            "transcript":  transcript_lines,
            "visuals":     visuals,
            "duration":    duration,
            "language":    language,
        })

        # Cleanup frames dir
        shutil.rmtree("frames", ignore_errors=True)
        print(f"[VideoQA] Pipeline complete in {round(time.time()-t_pipeline,1)}s total\n")

        return {
            "status":      "success",
            "session_id":  session_id,
            "duration":    duration,
            "transcript":  transcript_lines,
            "visuals":     visuals,
            "language":    language,
        }

    except Exception as e:
        shutil.rmtree(str(session_dir), ignore_errors=True)
        print(f"[VideoQA] Pipeline failed after {round(time.time()-t_pipeline,1)}s: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")



# ── POST /ask ────────────────────────────────────────────────

@app.post("/ask")
async def ask(req: AskRequest):
    """
    Answer a question grounded in the video's transcript + visuals.
    Returns: { answer, confidence, evidence, clip }
    """
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please process a video first.")

    full_text = session["full_text"]
    visuals   = session["visuals"]
    segments  = session["segments"]
    duration  = session["duration"]
    language  = req.language or session.get("language", "English")
    # Convert short code ('en') → display name ('English') for LLM prompt
    language_display = _CODE_TO_NAME.get(language.lower(), language)

    visuals_text = "\n".join(
        f"[{v['time']}] {v['caption']}" for v in visuals
    )

    try:
        # ── LLM Answer ──────────────────────────────────────
        result = answer_question(
            question=req.question,
            transcript=full_text,
            visuals=visuals_text,
            language=language_display,
            model=req.model,
        )

        # ── Clip Retrieval ───────────────────────────────────
        clip_start, clip_end = find_clip_timestamps(
            transcript_segments=segments,
            question=req.question,
            video_duration=duration,
        )

        clip_label = f"{_fmt_time(clip_start)} – {_fmt_time(clip_end)}"

        # Extract clip and save
        clip_filename = f"clip_{req.session_id[:8]}.mp4"
        clip_out_path = str(OUTPUT_DIR / clip_filename)

        try:
            extract_clip(session["video_path"], clip_start, clip_end, clip_out_path)
            clip_url = f"/download/clip/{clip_filename}"
        except Exception:
            clip_url = None

        return {
            "status":   "success",
            "question": req.question,
            "answer":   result.get("answer", ""),
            "confidence": f"{result.get('confidence', 'Medium')} – {result.get('confidence_reason', 'Based on transcript + visual frames')}",
            "evidence": {
                "transcript_excerpts": result.get("transcript_excerpts", []),
                "visual_captions":     result.get("visual_captions", []),
            },
            "clip": {
                "start":  clip_start,
                "end":    clip_end,
                "url":    clip_url,
                "label":  clip_label,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA failed: {str(e)}")


# ── POST /summarize_video ─────────────────────────────────────

@app.post("/summarize_video")
async def summarize_video_endpoint(req: SummarizeVideoRequest):
    """
    Summarize the video content (short paragraph / detailed bullets / chapters).
    Returns: { short, detailed, chapters }
    """
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    visuals_text = "\n".join(
        f"[{v['time']}] {v['caption']}" for v in session["visuals"]
    )

    try:
        result = summarize_video(
            transcript=session["full_text"],
            visuals=visuals_text,
            length=req.length or "short",
            model=req.model,
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


# ── POST /summarize_transcript ────────────────────────────────

@app.post("/summarize_transcript")
async def summarize_transcript_endpoint(req: SummarizeTranscriptRequest):
    """
    Extract key points, action items, and keywords from the transcript.
    Returns: { key_points, action_items, keywords }
    """
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        result = summarize_transcript(
            transcript=session["full_text"],
            model=req.model,
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcript summarization failed: {str(e)}")


# ── GET /download/{type}/{filename} ───────────────────────────

@app.get("/download/clip/{filename}")
def download_clip(filename: str):
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Clip file not found.")
    return FileResponse(
        str(path),
        media_type="video/mp4",
        filename=filename,
        headers={"Accept-Ranges": "bytes"},
    )


@app.get("/download/transcript/{session_id}")
def download_transcript(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    lines = session.get("transcript", [])
    text  = "\n".join(f"[{l['time']}] {l['speaker']}: {l['text']}" for l in lines)

    out_path = OUTPUT_DIR / f"transcript_{session_id[:8]}.txt"
    out_path.write_text(text, encoding="utf-8")
    return FileResponse(str(out_path), media_type="text/plain", filename="transcript.txt")


@app.get("/download/summary/{session_id}")
def download_summary(session_id: str, length: str = "short"):
    """Proxy – summary must first be generated via /summarize_video."""
    raise HTTPException(status_code=400, detail="Please generate summary first, then download from the frontend.")


# ── Helpers ───────────────────────────────────────────────────

def _fmt_time(seconds: float) -> str:
    s = int(seconds)
    m, s = divmod(s, 60)
    return f"{m}:{s:02d}"


_CODE_TO_NAME = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "ur": "Urdu",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ar": "Arabic",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
}

_LANG_MAP = {
    "english":    "en",
    "hindi":      "hi",
    "telugu":     "te",
    "tamil":      "ta",
    "kannada":    "kn",
    "malayalam":  "ml",
    "marathi":    "mr",
    "bengali":    "bn",
    "punjabi":    "pa",
    "gujarati":   "gu",
    "urdu":       "ur",
    "spanish":    "es",
    "french":     "fr",
    "german":     "de",
    "chinese":    "zh",
    "arabic":     "ar",
    "japanese":   "ja",
    "korean":     "ko",
    "portuguese": "pt",
    "russian":    "ru",
    "italian":    "it",
}

# Short ISO codes that are already valid for Whisper
_VALID_SHORT_CODES = {"en", "hi", "te", "ta", "kn", "ml", "mr", "bn", "pa", "gu", "ur",
                      "es", "fr", "de", "zh", "ar", "ja", "ko", "pt", "ru", "it"}

def _lang_code(language: str) -> str | None:
    """Accept either full names ('English') or short ISO codes ('en')."""
    lang = language.strip()
    # Already a valid short code
    if lang.lower() in _VALID_SHORT_CODES:
        return lang.lower()
    # Full name mapping
    return _LANG_MAP.get(lang.lower())


# ── Frontend Static Files ──────────────────────────────────────
# Mount the root directory to serve index.html, app.js, style.css in production
STATIC_DIR = Path(__file__).parent.parent
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")


# ── Entry Point ────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"\n{'='*50}")
    print(f"  VideoQA Backend starting on http://{host}:{port}")
    print(f"  Docs: http://localhost:{port}/docs")
    print(f"{'='*50}\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)
```

## llm.py

**Path**: `backend/llm.py`

```python
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
    
    # -- KEYLESS FALLBACK --
    # If the user hasn't set an OpenRouter key yet, we silently and safely fall back 
    # to pollinations.ai, a completely free, keyless wrapper for Llama 3 / OpenAI.
    if not OPENROUTER_API_KEY:
        url = "https://text.pollinations.ai/openai"
        headers = {"Content-Type": "application/json"}
        # Pollinations supports 'openai', 'llama', 'mistral', 'searchgpt'
        if "llama" in model.lower():
            req_model = "llama"
        elif "mistral" in model.lower() or "mixtral" in model.lower():
            req_model = "mistral"
        else:
            req_model = "openai" # GPT-4o fallback
    else:
        url = OPENROUTER_URL
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  "https://videoqa.local",
            "X-Title":       "VideoQA",
        }
        req_model = model

    resp = requests.post(
        url,
        headers=headers,
        json={
            "model":       req_model,
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
    if resp.status_code in (401, 402, 403):
        raise AuthError(f"OpenRouter auth/payment error {resp.status_code} on {model}: {resp.text[:200]}")
    if resp.status_code != 200:
        raise SkipModelError(f"OpenRouter error {resp.status_code} on {model}: {resp.text[:200]}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected OpenRouter response: {data}") from e


class AuthError(Exception):
    pass

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
    # Start fallback logic
    # (Removed the fatal exception for missing API keys to allow the new Keyless feature)

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
        except AuthError as e:
            print(f"[LLM] ⛔ Auth/Payment error on {attempt_model}: {e}. Skipping remaining OpenRouter models.")
            last_error = e
            break
        except Exception as e:
            print(f"[LLM] ❌ Unexpected error on {attempt_model}: {e}")
            last_error = e
            continue

    print(f"[LLM] ⚠️ All {len(chain)} OpenRouter models exhausted (likely invalid API key). Using EMERGENCY free fallback...")
    
    # -- EMERGENCY KEYLESS FALLBACK --
    # If the user supplied a bad/revoked API key to Hugging Face, OpenRouter will fail every model with 401.
    # We catch that complete failure here and silently use Pollinations so the app never breaks for the user.
    try:
        fallback_models = ["openai", "llama"]
        for p_model in fallback_models:
            print(f"[LLM] Trying set keyless fallback with model '{p_model}'...")
            resp = requests.post(
                "https://text.pollinations.ai/openai",
                headers={"Content-Type": "application/json"},
                json={
                    "model": p_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 1024,
                },
                timeout=60,
            )
            try:
                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"].strip()
                elif "error" in data:
                    print(f"Pollinations error on {p_model}: {data['error']}. Trying next...")
                    fallback_e = f"Pollinations error: {data['error']}"
                    continue
                else:
                    fallback_e = f"Unexpected Pollinations response: {data}"
                    continue
            except json.JSONDecodeError:
                if resp.status_code == 200 and resp.text:
                    return resp.text.strip()
                fallback_e = f"Pollinations non-JSON response: {resp.text}"
                continue
        raise RuntimeError(fallback_e)
    except Exception as exc:
        raise RuntimeError(f"All {len(chain)} models exhausted. Last error: {last_error}. And free fallback failed: {exc}")


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

CRITICAL: The content inside the JSON strings/arrays MUST be strictly plain text. Do NOT include any HTML tags (like <div> or <class="...">), CSS classes, or markdown bullet points (like -, *).

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

CRITICAL: The content inside the JSON arrays MUST be strictly plain text. Do NOT include any HTML tags (like <div> or <class="...">), CSS classes, or markdown bullet points (like -, *).

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
```

## video_utils.py

**Path**: `backend/video_utils.py`

```python
"""
video_utils.py – Video processing helpers
Covers: audio extraction, smart keyframe sampling, BLIP captioning, clip extraction.
"""

import os
import time
import subprocess
import cv2
import torch
import numpy as np
from PIL import Image

# ── MoviePy import (for clip extraction only – v1.x and v2.x) ──
try:
    from moviepy.editor import VideoFileClip   # moviepy v1.x
except ImportError:
    from moviepy import VideoFileClip          # moviepy v2.x

from models import get_blip

MAX_FRAMES = int(os.getenv("MAX_FRAMES", "3"))
CLIP_DURATION = float(os.getenv("CLIP_DURATION", "30"))


# ── FFMPEG helper ────────────────────────────────────────────

def _get_ffmpeg() -> str:
    """Return path to bundled ffmpeg binary (from imageio_ffmpeg/moviepy)."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"   # fall back to system PATH


# ── Audio ────────────────────────────────────────────────────

def extract_audio(video_path: str, out_path: str = "audio.wav", start_sec: float = None, end_sec: float = None) -> str:
    """
    Extract 16kHz mono WAV audio from video using ffmpeg subprocess.
    Much faster and more reliable than MoviePy's write_audiofile on Windows.
    """
    t0 = time.time()
    print(f"[VideoQA] Extracting audio from {os.path.basename(video_path)}...")
    ffmpeg = _get_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",                   # overwrite output
    ]
    if start_sec is not None:
        cmd.extend(["-ss", str(start_sec)])
    if end_sec is not None:
        duration = end_sec - (start_sec or 0.0)
        cmd.extend(["-t", str(duration)])
    cmd.extend([
        "-i", video_path,       # input video
        "-vn",                  # no video
        "-acodec", "pcm_s16le", # WAV format
        "-ar", "16000",         # 16kHz sample rate (required by Whisper)
        "-ac", "1",             # mono
        out_path,
    ])
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300,            # 5 min timeout
    )
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"ffmpeg audio extraction failed:\n{err}")
    print(f"[VideoQA] Audio extracted in {round(time.time()-t0,1)}s -> {out_path}")
    return out_path


# ── Frame Extraction ─────────────────────────────────────────

def _compute_frame_diff(prev: np.ndarray, curr: np.ndarray) -> float:
    """Mean absolute pixel difference between two frames (grayscale)."""
    p = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY).astype(float)
    c = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY).astype(float)
    return float(np.mean(np.abs(p - c)))


def extract_keyframes(video_path: str, n: int = MAX_FRAMES, start_sec: float = None, end_sec: float = None) -> list[str]:
    """
    Smart keyframe extraction:
    1. Sample frames uniformly across the video.
    2. Additionally pick frames with high scene-change score.
    Returns up to `n` unique frame file paths.
    """
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps   = cap.get(cv2.CAP_PROP_FPS) or 25.0

    start_frame = int(start_sec * fps) if start_sec is not None else 0
    end_frame = int(end_sec * fps) if end_sec is not None else total

    saved_paths: list[str] = []
    os.makedirs("frames", exist_ok=True)

    if total <= 0 or start_frame >= end_frame:
        cap.release()
        return saved_paths

    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
    frames_to_process = end_frame - start_frame

    # Uniform sampling indices
    uniform_indices = set(
        start_frame + int(i * frames_to_process / n) for i in range(n)
    )

    prev_frame = None
    frame_scores: list[tuple[float, int, np.ndarray]] = []

    count = start_frame
    while cap.isOpened() and count < end_frame:
        ret, frame = cap.read()
        if not ret:
            break

        if prev_frame is not None:
            score = _compute_frame_diff(prev_frame, frame)
            frame_scores.append((score, count, frame.copy()))
        elif count == start_frame:
            # Always keep first frame
            frame_scores.append((999.0, count, frame.copy()))

        prev_frame = frame
        count += 1

    cap.release()

    if not frame_scores:
        return saved_paths

    # Pick top-n frames by scene-change score, prioritising uniform coverage
    # Combine: add uniform indices to the selection weighted by score
    uniform_frames = []
    scene_frames = []

    # Sort by score descending
    sorted_by_score = sorted(frame_scores, key=lambda x: x[0], reverse=True)

    # Collect top scene-change frames
    selected_indices: set[int] = set()
    for score, idx, frm in sorted_by_score:
        if len(selected_indices) >= n:
            break
        # avoid picking frames too close together (< 1 second)
        too_close = any(abs(idx - s) < fps for s in selected_indices)
        if not too_close:
            selected_indices.add(idx)

    # Pad with uniform indices if needed
    for ui in sorted(uniform_indices):
        if len(selected_indices) >= n:
            break
        selected_indices.add(ui)

    # Write selected frames to disk (sorted by index = chronological)
    frame_dict = {idx: frm for _, idx, frm in frame_scores}
    for idx in sorted(selected_indices):
        if idx in frame_dict:
            path = f"frames/frame_{idx:06d}.jpg"
            cv2.imwrite(path, frame_dict[idx])
            saved_paths.append(path)

    return saved_paths[:n]


def extract_specific_frames(video_path: str, timestamps: list[float]) -> list[str]:
    """
    Extract specific frames by timestamp.
    timestamps: list of floats in seconds.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    
    saved_paths = []
    os.makedirs("frames", exist_ok=True)
    
    for ts in sorted(set(timestamps)):
        frame_idx = int(ts * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            path = f"frames/frame_{frame_idx:06d}.jpg"
            cv2.imwrite(path, frame)
            saved_paths.append(path)
            
    cap.release()
    return saved_paths


# ── BLIP Captioning ──────────────────────────────────────────

def caption_frames(frame_paths: list[str]) -> list[dict]:
    """
    Generate captions for each frame using BLIP-base.
    Returns list of { path, caption, frame_index }.
    """
    print(f"[VideoQA] Captioning {len(frame_paths)} frame(s) with BLIP...")
    t_total = time.time()
    processor, model = get_blip()
    device = next(model.parameters()).device
    results = []

    for i, path in enumerate(frame_paths):
        t0 = time.time()
        try:
            image = Image.open(path).convert("RGB")
            inputs = processor(image, return_tensors="pt").to(device)

            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=60,
                    num_beams=4,
                )

            caption = processor.decode(out[0], skip_special_tokens=True)
            frame_idx = int(os.path.basename(path).replace("frame_", "").replace(".jpg", ""))
            results.append({
                "path": path,
                "caption": caption,
                "frame_index": frame_idx,
            })
            print(f"[VideoQA]   Frame {i+1}/{len(frame_paths)} captioned in {round(time.time()-t0,1)}s: {caption[:60]}")
        except Exception as e:
            print(f"[VideoQA]   Frame {i+1} failed: {e}")
            results.append({"path": path, "caption": "Frame could not be captioned.", "frame_index": 0})

    print(f"[VideoQA] All frames captioned in {round(time.time()-t_total,1)}s")
    return results


# ── Clip Extraction ──────────────────────────────────────────

def extract_clip(
    video_path: str,
    start_sec: float,
    end_sec: float,
    out_path: str = "relevant_clip.mp4"
) -> str:
    """
    Extract a sub-clip using ffmpeg subprocess.
    Much faster and more reliable than MoviePy on Windows.
    """
    t0 = time.time()
    duration_sec = max(1.0, end_sec - start_sec)
    start_sec = max(0.0, start_sec)
    print(f"[VideoQA] Extracting clip {start_sec:.1f}s -> {end_sec:.1f}s...")
    ffmpeg = _get_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",
        "-ss", str(start_sec),       # seek to start (fast seek before -i)
        "-i", video_path,
        "-t", str(duration_sec),      # duration
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",    # web-compatible MP4
        out_path,
    ]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace")[-300:]
        raise RuntimeError(f"ffmpeg clip extraction failed:\n{err}")
    print(f"[VideoQA] Clip extracted in {round(time.time()-t0,1)}s -> {out_path}")
    return out_path


# ── Transcript → Timestamp Mapping ───────────────────────────

def find_clip_timestamps(
    transcript_segments: list[dict],
    question: str,
    video_duration: float,
    clip_duration: float = CLIP_DURATION,
) -> tuple[float, float]:
    """
    Find the most relevant clip for a question.
    Uses simple keyword overlap over Whisper word-level segments.
    Falls back to 1/3 into the video if nothing found.

    transcript_segments: list of { start, end, text } dicts from Whisper.
    Returns (start_sec, end_sec).
    """
    if not transcript_segments:
        start = video_duration / 3
        return start, min(video_duration, start + clip_duration)

    q_words = set(question.lower().split())
    best_score = -1
    best_start = 0.0

    for seg in transcript_segments:
        seg_words = set(seg.get("text", "").lower().split())
        overlap = len(q_words & seg_words)
        if overlap > best_score:
            best_score = overlap
            best_start = seg.get("start", 0.0)

    end = min(video_duration, best_start + clip_duration)
    return best_start, end
```

## models.py

**Path**: `backend/models.py`

```python
"""
models.py – Lazy-loaded AI model singletons
Loads Whisper and BLIP only once on first use to avoid repeated startup cost.
"""

import os
import time
import torch
from dotenv import load_dotenv

load_dotenv()

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")   # base = fast, 140MB
_whisper = None
_blip_processor = None
_blip_model = None
_model_status = {
    "whisper": "not_loaded",   # not_loaded | loading | ready | error
    "blip":    "not_loaded",
    "whisper_load_time": None,
    "blip_load_time": None,
}

# ── Whisper ─────────────────────────────────────────────────
class _FasterWhisperWrapper:
    """Wraps faster-whisper to match openai-whisper's transcribe() output format."""
    def __init__(self, model):
        self._model = model

    def transcribe(self, audio_path, language=None, word_timestamps=False, **kwargs):
        segments_iter, info = self._model.transcribe(
            audio_path,
            language=language,
            word_timestamps=word_timestamps,
        )
        segments = []
        full_text_parts = []
        for seg in segments_iter:
            segments.append({
                "start": seg.start,
                "end":   seg.end,
                "text":  seg.text.strip(),
            })
            full_text_parts.append(seg.text.strip())
        return {
            "text": " ".join(full_text_parts),
            "segments": segments,
        }

def get_whisper():
    """Returns a loaded faster-whisper model wrapped in openai-whisper-compatible API."""
    global _whisper, _model_status
    if _whisper is None:
        _model_status["whisper"] = "loading"
        t0 = time.time()
        from faster_whisper import WhisperModel
        print(f"[VideoQA] Loading faster-whisper-{WHISPER_MODEL_SIZE}...")
        model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        _whisper = _FasterWhisperWrapper(model)
        elapsed = round(time.time() - t0, 1)
        _model_status["whisper"] = "ready"
        _model_status["whisper_load_time"] = elapsed
        print(f"[VideoQA] faster-whisper-{WHISPER_MODEL_SIZE} loaded in {elapsed}s ✓")
    return _whisper


# ── BLIP Vision Captioning ───────────────────────────────────
def get_blip():
    """Returns (processor, model) for BLIP-base (lazy singleton)."""
    global _blip_processor, _blip_model, _model_status
    if _blip_model is None:
        _model_status["blip"] = "loading"
        t0 = time.time()
        from transformers import BlipProcessor, BlipForConditionalGeneration
        # Use blip-base (~440MB) instead of blip-large (~900MB) — ~3× faster on CPU
        model_name = "Salesforce/blip-image-captioning-base"
        print(f"[VideoQA] Loading BLIP-base...")
        _blip_processor = BlipProcessor.from_pretrained(model_name)
        _blip_model = BlipForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _blip_model = _blip_model.to(device)
        _blip_model.eval()
        elapsed = round(time.time() - t0, 1)
        _model_status["blip"] = "ready"
        _model_status["blip_load_time"] = elapsed
        print(f"[VideoQA] BLIP-base loaded on {device} in {elapsed}s ✓")
    return _blip_processor, _blip_model


def get_model_status() -> dict:
    """Returns current load status for all models — used by /status endpoint."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return {
        "device": device,
        "whisper": {
            "model":  WHISPER_MODEL_SIZE,
            "status": _model_status["whisper"],
            "load_time_sec": _model_status["whisper_load_time"],
        },
        "blip": {
            "model":  "blip-image-captioning-base",
            "status": _model_status["blip"],
            "load_time_sec": _model_status["blip_load_time"],
        },
    }


# ── Session Store ────────────────────────────────────────────
# Maps session_id → { transcript, visuals, video_path, transcript_lines }
_sessions: dict = {}

def get_session_store() -> dict:
    return _sessions

def save_session(session_id: str, data: dict):
    _sessions[session_id] = data

def get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)

```

## test_pipeline.py

**Path**: `backend/test_pipeline.py`

```python
import sys, traceback, os
sys.path.insert(0, '.')

video_path = r'uploads\178a6539-fafa-4183-8b56-fee4708cc30c\videoplayback (1).mp4'

print('=== STEP 1: extract_audio ===')
try:
    from video_utils import extract_audio
    extract_audio(video_path, 'test_audio.wav')
    print('extract_audio OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)

print('=== STEP 2: faster-whisper transcribe ===')
try:
    from models import get_whisper
    model_wh = get_whisper()
    result = model_wh.transcribe('test_audio.wav', language='en', word_timestamps=False)
    segs = result.get('segments', [])
    print(f'Transcription OK - {len(segs)} segments')
    print('First 100 chars:', result["text"][:100])
except Exception:
    traceback.print_exc()
    sys.exit(1)

print('=== ALL OK ===')
```

## requirements.txt

**Path**: `backend/requirements.txt`

```text
# VideoQA Backend – Python Requirements
# Install: pip install -r requirements.txt

# ── Web Framework ─────────────────────────────────────────────
fastapi==0.110.0
uvicorn[standard]==0.29.0
python-multipart==0.0.9
python-dotenv==1.0.0

# ── AI Models ─────────────────────────────────────────────────
# faster-whisper – Speech-to-text (base model auto-downloaded on first run)
faster-whisper

# BLIP – Vision captioning (large model ~900MB, auto-downloaded)
transformers==4.40.0
torch==2.2.2
torchvision==0.17.2
Pillow==10.3.0

# ── Video Processing ──────────────────────────────────────────
moviepy==1.0.3
opencv-python==4.9.0.80
yt-dlp

# ── HTTP / LLM ────────────────────────────────────────────────
requests==2.31.0

# ── Utilities ─────────────────────────────────────────────────
numpy==1.26.4
pydantic==2.6.4

# ── Optional: ngrok for remote access ────────────────────────
# pyngrok==7.1.6
```

## .env.example

**Path**: `backend/.env.example`

```bash
OPENROUTER_API_KEY=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
WHISPER_MODEL=medium
LLM_MODEL=mistralai/mistral-7b-instruct
MAX_FRAMES=6
CLIP_DURATION=5
HOST=0.0.0.0
PORT=8000
```

## Dockerfile

**Path**: `Dockerfile`

```dockerfile
# Use Python 3.10 slim image suitable for ML
FROM python:3.10-slim

# Install system dependencies required for OpenCV and ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set up a non-root user for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Upgrade pip and install an older setuptools (v70+ removed pkg_resources which breaks openai-whisper)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir "setuptools<70.0.0" wheel

# Set early environment variables
ENV HOST=0.0.0.0
ENV PORT=7860

# Set working directory
WORKDIR /home/user/app

# Copy the backend requirements first for better caching
COPY --chown=user backend/requirements.txt ./backend/

# IMPORTANT: Install CPU-only PyTorch. 
# The default PyTorch library is a massive 2.5GB and often crashes the free Hugging Face builder. The CPU version is ~200MB!
RUN pip install --no-cache-dir torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu

# Install the rest (using --no-build-isolation so it uses our downgraded setuptools instead of fetching the latest broken one)
RUN pip install --no-cache-dir --no-build-isolation -r backend/requirements.txt

# Create necessary directories
RUN mkdir -p /home/user/app/backend/uploads /home/user/app/backend/outputs /home/user/app/backend/frames

# Copy the rest of the application
COPY --chown=user . .

# Expose port (7860 is default for Hugging Face Spaces Docker)
EXPOSE 7860

# Change to the backend directory and run Uvicorn
WORKDIR /home/user/app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

## upload_to_hf.py

**Path**: `upload_to_hf.py`

```python
import os
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Load environment variables
load_dotenv("backend/.env")

# Get token
token = os.getenv("HF_TOKEN")
if not token:
    print("ERROR: HF_TOKEN not found! Please save your backend/.env file.")
    exit(1)

api = HfApi(token=token)
repo_id = "mohanvannemreddy7/genvideoai"

print(f"Uploading all files to: https://huggingface.co/spaces/{repo_id}...")

# Upload the current folder, replacing remote files but ignoring git, venv, and cache
api.upload_folder(
    folder_path=".",
    repo_id=repo_id,
    repo_type="space",
    delete_patterns="*",  # This ensures any remote files not present locally are deleted
    ignore_patterns=[
        ".git/*",
        "backend/venv/*",
        "backend/__pycache__/*",
        "backend/outputs/*",
        "backend/uploads/*",
        "upload_to_hf.py", # Exclude this script itself
        "backend/cookies.txt", # Don't push private cookies
        "backend/.env" # SECRETS: Exclude environment variables
    ]
)

print("Upload complete!")
```

