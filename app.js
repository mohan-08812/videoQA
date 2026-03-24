/* =========================================================
   app.js – VideoQA Core Application Logic
   ========================================================= */

// ── App State ──────────────────────────────────────────────
const state = {
  theme: 'dark',
  tab: 'ask',
  phase: 'idle',       // idle | uploading | processing | ready
  file: null,
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
  state.phase = 'uploading';

  // Show file info
  $('file-name-display').textContent = file.name;
  $('file-detail-display').textContent = `${formatFileSize(file.size)} · ${file.type || 'video'}`;
  $('file-info').classList.add('show');
  $('process-btn').disabled = false;

  // Video preview
  const url = URL.createObjectURL(file);
  const vp = $('video-preview');
  vp.src = url;
  vp.onloadedmetadata = () => {
    const dur = formatDuration(vp.duration);
    $('file-detail-display').textContent = `${formatFileSize(file.size)} · ${dur}`;
  };
  $('video-preview-wrap').classList.add('show');
  $('manual-selection-tools').style.display = 'flex';

  showToast(`"${file.name}" selected`, 'success');
}

function removeFile() {
  state.file = null;
  state.manualFrames = [];
  state.phase = 'idle';
  $('file-info').classList.remove('show');
  $('video-preview-wrap').classList.remove('show');
  $('manual-selection-tools').style.display = 'none';
  $('manual-start').value = '';
  $('manual-end').value = '';
  renderManualFrames();
  $('file-input').value = '';
  $('process-btn').disabled = true;
}

async function processVideo() {
  if (!state.file) return;

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
    const data = await apiProcessVideo(state.file, language, mode, startTime, endTime, manFrames, (stepLabel, pct) => {
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
  const safeAnswer = JSON.stringify(result.answer);
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
  < class="history-item ${i === 0 && state.historyIndex === 0 ? 'active' : ''}" onclick="restoreHistoryItem(${item.id})">
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
  < class="summarize-grid">
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
    out.innerHTML = `< style = "color:var(--error);"> Error: ${err.message}</span> `;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '✨ Generate Summary';
  }
}

function renderVideoSummaryOutput(data) {
  const out = $('video-sum-output');
  const mode = state.summarizeMode;

  if (mode === 'short') {
    out.innerHTML = `< style = "line-height:1.8;"> ${data.short}</> `;
  } else if (mode === 'detailed') {
    out.innerHTML = data.detailed.map(b =>
      `< class="summary-bullet"> <span>${b}</span></div> `
    ).join('');
  } else if (mode === 'chapters') {
    out.innerHTML = `< class="chapters-list">
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
  < style = "margin-bottom:var(--space-4);">
    <div class="evidence-title" style="margin-bottom:var(--space-3);">🎯 Key Points</div>
        ${data.key_points.map(p => `<div class="summary-bullet"><span>${p}</span></div>`).join('')}
      </div>
      <div style="margin-bottom:var(--space-4);">
        <div class="evidence-title" style="margin-bottom:var(--space-3);">✅ Action Items</div>
        <ul class="action-items">
          ${data.action_items.map(a => `<li>${a}</li>`).join('')}
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
    out.innerHTML = `< style = "color:var(--error);"> Error: ${err.message}</span> `;
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
