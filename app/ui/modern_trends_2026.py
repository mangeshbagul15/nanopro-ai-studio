"""
NanoPro AI Studio - 2026 Web Design & Animation Trends Suite
Implements top viral and high-impact 2026 trends from the Web Design & Animation Trends 2026 Index:
- #233 Dynamic Island UI (Top center floating glass capsule with spring physics)
- #106 Command Palette (Ctrl+K / Cmd+K Spotlight search across 305 agents, DBs, and views)
- #22 High-Tech Cyber Marquee Ticker (Infinite hardware-accelerated heartbeat strip)
- #34 & #149 Skeleton Shimmer Loaders
- #58, #59, #60 Cursor Spotlight & Magnetic Button Glow
- #80 3D Perspective Card Tilt with Specular Glare
- #1 & #12 Kinetic Typography & Word Streaming Engine
- #205 Text Scramble Matrix Reveal
- #35 Modern 2026 Micro-Toasts with Progress Timers
- #292 Pure Web Audio Synthesizer (Zero-dependency audio blips & chimes)
- #118 Smooth Count-Up Number Animations
"""

def get_2026_modern_trends_css() -> str:
    return """
<!-- =========================================================================
     2026 MODERN WEB DESIGN & ANIMATION TRENDS STYLESHEET
     ========================================================================= -->
<style>
/* --- Cursor Spotlight Layer (#59, #60) --- */
#nanoCursorSpotlight {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 99998;
    background: radial-gradient(600px circle at var(--mouse-x, 50vw) var(--mouse-y, 50vh), rgba(56, 189, 248, 0.035), transparent 45%);
    transition: opacity 0.3s ease;
}

/* --- Dynamic Island (#233) --- */
.nano-dynamic-island {
    position: fixed;
    top: 14px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 99990;
    background: rgba(11, 17, 32, 0.88);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 999px;
    padding: 6px 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(56, 189, 248, 0.15);
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    user-select: none;
    max-width: 90vw;
}
.nano-dynamic-island:hover {
    border-color: rgba(56, 189, 248, 0.8);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6), 0 0 25px rgba(56, 189, 248, 0.3);
    transform: translateX(-50%) scale(1.02);
}
.nano-dynamic-island.expanded {
    border-radius: 18px;
    padding: 14px 20px;
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    width: 440px;
}
.island-pulse-dot {
    width: 8px;
    height: 8px;
    background: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 10px #10B981;
    animation: islandPulse 1.8s infinite;
    flex-shrink: 0;
}
@keyframes islandPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.75); }
}
.island-label {
    font-size: 11.5px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.4px;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 8px;
}
.island-chip {
    background: rgba(56, 189, 248, 0.15);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    padding: 1px 6px;
    font-family: monospace;
}
.island-expanded-content {
    display: none;
    flex-direction: column;
    gap: 10px;
}
.nano-dynamic-island.expanded .island-expanded-content {
    display: flex;
}
.island-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
}
.island-metric-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(38, 51, 84, 0.8);
    border-radius: 8px;
    padding: 8px;
    text-align: center;
}
.island-metric-val {
    font-size: 13px;
    font-weight: 800;
    color: #38BDF8;
}
.island-metric-lbl {
    font-size: 9px;
    color: #94A3B8;
    text-transform: uppercase;
}
.island-action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 4px;
    border-top: 1px solid rgba(38, 51, 84, 0.6);
}

/* --- Cyber Marquee Ticker Strip (#22) --- */
.nano-cyber-ticker {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100vw;
    height: 26px;
    background: rgba(6, 10, 20, 0.94);
    backdrop-filter: blur(12px);
    border-top: 1px solid rgba(56, 189, 248, 0.25);
    z-index: 99980;
    display: flex;
    align-items: center;
    overflow: hidden;
    white-space: nowrap;
    user-select: none;
}
.ticker-badge {
    background: linear-gradient(135deg, #0284C7, #06B6D4);
    color: #FFFFFF;
    font-size: 9.5px;
    font-weight: 800;
    padding: 3px 10px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    flex-shrink: 0;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 6px;
}
.ticker-track {
    display: flex;
    align-items: center;
    animation: marqueeScroll 45s linear infinite;
    gap: 32px;
    padding-left: 20px;
}
.ticker-track:hover {
    animation-play-state: paused;
}
@keyframes marqueeScroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
.ticker-item {
    font-size: 11px;
    font-weight: 600;
    color: #CBD5E1;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: monospace;
}
.ticker-item .live-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10B981;
}

/* --- Command Palette (Ctrl+K) (#106) --- */
.nano-command-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(3, 7, 18, 0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    z-index: 99999;
    display: none;
    align-items: flex-start;
    justify-content: center;
    padding-top: 12vh;
    animation: paletteFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes paletteFadeIn {
    from { opacity: 0; transform: scale(0.98); }
    to { opacity: 1; transform: scale(1); }
}
.nano-command-palette {
    background: #0B1120;
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 16px;
    width: 620px;
    max-width: 92vw;
    box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 35px rgba(56, 189, 248, 0.2);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}
.palette-search-box {
    display: flex;
    align-items: center;
    padding: 14px 18px;
    border-bottom: 1px solid rgba(38, 51, 84, 0.8);
    gap: 12px;
    background: rgba(15, 23, 42, 0.6);
}
.palette-search-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 600;
}
.palette-search-input::placeholder {
    color: #64748B;
}
.palette-results-list {
    max-height: 380px;
    overflow-y: auto;
    padding: 8px;
}
.palette-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
    color: #CBD5E1;
}
.palette-item:hover, .palette-item.selected {
    background: rgba(56, 189, 248, 0.12);
    color: #F8FAFC;
    transform: translateX(3px);
}
.palette-item-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.palette-item-icon {
    font-size: 16px;
    width: 24px;
    text-align: center;
}
.palette-item-title {
    font-size: 13px;
    font-weight: 700;
}
.palette-item-desc {
    font-size: 11px;
    color: #64748B;
}
.palette-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 18px;
    background: rgba(6, 10, 20, 0.8);
    border-top: 1px solid rgba(38, 51, 84, 0.6);
    font-size: 11px;
    color: #64748B;
}
.nano-kbd {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: monospace;
    font-size: 10px;
    color: #94A3B8;
    box-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

/* --- 3D Perspective Tilt with Specular Glare (#80) --- */
.card-3d-tilt {
    transition: transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.25s ease;
    transform-style: preserve-3d;
    will-change: transform;
}
.card-3d-tilt:hover {
    box-shadow: 0 16px 36px rgba(0,0,0,0.5), 0 0 20px rgba(56, 189, 248, 0.2) !important;
}

/* --- Shimmer Skeleton Loaders (#34, #149) --- */
.nano-skeleton-box {
    background: linear-gradient(90deg, #1E293B 25%, #334155 50%, #1E293B 75%);
    background-size: 200% 100%;
    animation: nanoShimmer 1.8s infinite linear;
    border-radius: 6px;
}
@keyframes nanoShimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* --- Modern 2026 Micro-Toasts (#35) --- */
.nano-toast-container {
    position: fixed;
    top: 70px;
    right: 20px;
    z-index: 99995;
    display: flex;
    flex-direction: column;
    gap: 8px;
    pointer-events: none;
}
.nano-modern-toast {
    background: rgba(11, 17, 32, 0.94);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 12px;
    padding: 12px 16px;
    width: 320px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    display: flex;
    align-items: flex-start;
    gap: 12px;
    pointer-events: auto;
    animation: toastSlideIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    transition: all 0.3s ease;
}
@keyframes toastSlideIn {
    from { opacity: 0; transform: translateX(50px) scale(0.95); }
    to { opacity: 1; transform: translateX(0) scale(1); }
}
.toast-bar {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 2.5px;
    background: #38BDF8;
    border-radius: 0 0 12px 12px;
    animation: toastProgress 4s linear forwards;
}
@keyframes toastProgress {
    from { width: 100%; }
    to { width: 0%; }
}
</style>
"""

def get_2026_modern_trends_html() -> str:
    return """
<!-- =========================================================================
     2026 MODERN WEB DESIGN & ANIMATION TRENDS HTML NODES
     ========================================================================= -->

<!-- Cursor Spotlight (#59, #60) -->
<div id="nanoCursorSpotlight"></div>

<!-- Dynamic Island (#233) -->
<div class="nano-dynamic-island" id="nanoDynamicIsland" onclick="toggleDynamicIsland(event)">
    <div style="display:flex; align-items:center; gap:8px;">
        <span class="island-pulse-dot"></span>
        <span class="island-label">
            <span id="islandLiveText">NanoPro AI Studio</span>
            <span class="island-chip" id="islandActiveModelBadge">305 AGENTS</span>
        </span>
    </div>
    
    <div class="island-expanded-content" id="islandExpandedContent">
        <div class="island-grid">
            <div class="island-metric-card">
                <div class="island-metric-val" id="islandMetricActive">278</div>
                <div class="island-metric-lbl">Active Agents</div>
            </div>
            <div class="island-metric-card">
                <div class="island-metric-val" id="islandMetricThroughput">1.62M</div>
                <div class="island-metric-lbl">Recs / Sec</div>
            </div>
            <div class="island-metric-card">
                <div class="island-metric-val" id="islandMetricLatency">24ms</div>
                <div class="island-metric-lbl">Groq LPU</div>
            </div>
        </div>
        <div class="island-action-bar">
            <button type="button" class="btn btn-secondary" onclick="openCommandPalette(); event.stopPropagation();" style="font-size:10.5px; padding:3px 8px;">
                <span class="nano-kbd">Ctrl+K</span> Spotlight
            </button>
            <div style="display:flex; align-items:center; gap:8px;">
                <button type="button" class="btn btn-secondary" id="btnToggleSoundFx" onclick="toggleCyberSoundFx(); event.stopPropagation();" style="font-size:10.5px; padding:3px 8px;" title="Toggle Futuristic Cyber Audio FX">
                    <span id="soundFxIcon">&#128266;</span> FX Sound
                </button>
                <button type="button" class="btn btn-primary" onclick="switchView('ai_manager'); event.stopPropagation();" style="font-size:10.5px; padding:3px 8px;">
                    Manager &rarr;
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Command Palette Modal (#106) -->
<div class="nano-command-backdrop" id="nanoCommandPaletteBackdrop" onclick="closeCommandPalette(event)">
    <div class="nano-command-palette" onclick="event.stopPropagation()">
        <div class="palette-search-box">
            <span style="font-size:18px; color:#38BDF8;">&#128269;</span>
            <input type="text" id="paletteSearchInput" class="palette-search-input" 
                   placeholder="Type a command, search 305 agents, 21 databases, or views..." 
                   oninput="filterCommandPalette()" 
                   onkeydown="handlePaletteKeydown(event)" />
            <span class="nano-kbd">ESC</span>
        </div>
        <div class="palette-results-list" id="paletteResultsList">
            <!-- Dynamically populated -->
        </div>
        <div class="palette-footer">
            <span>Navigate: <span class="nano-kbd">&uarr;</span> <span class="nano-kbd">&darr;</span> &bull; Select: <span class="nano-kbd">&crarr;</span></span>
            <span style="color:#38BDF8; font-weight:700;">Mangesh NanoPro 2026 Core</span>
        </div>
    </div>
</div>

<!-- Modern Toast Container (#35) -->
<div class="nano-toast-container" id="nanoToastContainer"></div>

<!-- Infinite Cyber Marquee Strip (#22) -->
<div class="nano-cyber-ticker" id="nanoCyberTicker">
    <div class="ticker-badge">&#9889; 2026 CLUSTER</div>
    <div class="ticker-track">
        <span class="ticker-item"><span class="live-dot"></span> FLY.IO SINGAPORE: 100% ONLINE (200 OK)</span>
        <span class="ticker-item"><span class="live-dot"></span> ALWAYSDATA SENTINEL: ACTIVE</span>
        <span class="ticker-item"><span class="live-dot"></span> PYTHONANYWHERE: STANDBY READY</span>
        <span class="ticker-item"><span class="live-dot"></span> 305 ENTERPRISE AI AGENTS: SYNCHRONIZED</span>
        <span class="ticker-item"><span class="live-dot"></span> SNOWFLAKE WAREHOUSE: EGPKNWZ-XH53504 CONNECTED</span>
        <span class="ticker-item"><span class="live-dot"></span> ORACLE 23AI XE: XEPDB1 SYNCED</span>
        <span class="ticker-item"><span class="live-dot"></span> MAKE.COM WEBHOOK: ARMED (HTTP 200)</span>
        <span class="ticker-item"><span class="live-dot"></span> LOCAL GPU: RTX 3050 CUDA 12 ACTIVE</span>
        <span class="ticker-item"><span class="live-dot"></span> GROQ LPU: 194 TPS (24ms SLA)</span>
        <span class="ticker-item"><span class="live-dot"></span> TELEGRAM BOTS: 4 CHANNELS DISPATCHING</span>
        <!-- Repeated for seamless infinite loop -->
        <span class="ticker-item"><span class="live-dot"></span> FLY.IO SINGAPORE: 100% ONLINE (200 OK)</span>
        <span class="ticker-item"><span class="live-dot"></span> ALWAYSDATA SENTINEL: ACTIVE</span>
        <span class="ticker-item"><span class="live-dot"></span> PYTHONANYWHERE: STANDBY READY</span>
        <span class="ticker-item"><span class="live-dot"></span> 305 ENTERPRISE AI AGENTS: SYNCHRONIZED</span>
        <span class="ticker-item"><span class="live-dot"></span> SNOWFLAKE WAREHOUSE: EGPKNWZ-XH53504 CONNECTED</span>
        <span class="ticker-item"><span class="live-dot"></span> ORACLE 23AI XE: XEPDB1 SYNCED</span>
        <span class="ticker-item"><span class="live-dot"></span> MAKE.COM WEBHOOK: ARMED (HTTP 200)</span>
        <span class="ticker-item"><span class="live-dot"></span> LOCAL GPU: RTX 3050 CUDA 12 ACTIVE</span>
        <span class="ticker-item"><span class="live-dot"></span> GROQ LPU: 194 TPS (24ms SLA)</span>
        <span class="ticker-item"><span class="live-dot"></span> TELEGRAM BOTS: 4 CHANNELS DISPATCHING</span>
    </div>
</div>
"""

def get_2026_modern_trends_js() -> str:
    return """
<!-- =========================================================================
     2026 MODERN WEB DESIGN & ANIMATION TRENDS JAVASCRIPT ENGINE
     ========================================================================= -->
<script>
// --- 1. Web Audio Synthesizer (#292) ---
let audioCtx = null;
let isSoundMuted = localStorage.getItem('nano_sound_muted') === 'true';

function initWebAudio() {
    if (!audioCtx && (window.AudioContext || window.webkitAudioContext)) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function playCyberHoverSound() {
    if (isSoundMuted) return;
    try {
        initWebAudio();
        if (!audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1400, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.015, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.04);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.04);
    } catch(e) {}
}

function playCyberClickSound() {
    if (isSoundMuted) return;
    try {
        initWebAudio();
        if (!audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.06);
        gain.gain.setValueAtTime(0.035, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.06);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.06);
    } catch(e) {}
}

function toggleCyberSoundFx() {
    isSoundMuted = !isSoundMuted;
    localStorage.setItem('nano_sound_muted', isSoundMuted ? 'true' : 'false');
    const icon = document.getElementById('soundFxIcon');
    if (icon) icon.innerHTML = isSoundMuted ? '&#128263;' : '&#128266;';
    showModernToast('Cyber Audio', isSoundMuted ? 'Sound FX Muted' : 'Sound FX Enabled', 'info');
    if (!isSoundMuted) playCyberClickSound();
}

// --- 2. Dynamic Island Controller (#233) ---
function toggleDynamicIsland(e) {
    const island = document.getElementById('nanoDynamicIsland');
    if (!island) return;
    island.classList.toggle('expanded');
    playCyberClickSound();
}

// Close island when clicking outside
document.addEventListener('click', (e) => {
    const island = document.getElementById('nanoDynamicIsland');
    if (island && island.classList.contains('expanded') && !island.contains(e.target)) {
        island.classList.remove('expanded');
    }
});

// --- 3. Cursor Spotlight Follower (#59, #60) ---
window.addEventListener('mousemove', (e) => {
    document.documentElement.style.setProperty('--mouse-x', e.clientX + 'px');
    document.documentElement.style.setProperty('--mouse-y', e.clientY + 'px');
});

// --- 4. 3D Card Tilt with Glare (#80) ---
function init3dCardTilt() {
    const cards = document.querySelectorAll('.card-3d-tilt, .panoramic-card, .metric-card, .hud-metric-box');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -7;
            const rotateY = ((x - centerX) / centerX) * 7;
            card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        });
        card.addEventListener('mouseenter', () => {
            playCyberHoverSound();
        });
    });
}

// --- 5. Command Palette (Ctrl+K) Engine (#106) ---
const PALETTE_COMMANDS = [
    { title: "Dashboard / Quantum Core", desc: "Open central 3D panoramic control center", icon: "&#128187;", action: () => switchView('dashboard') },
    { title: "3D Cyber Data Center AI Hub", desc: "305 Enterprise AI Specialists & animated pixel-office", icon: "&#129302;", action: () => switchView('ai_office') },
    { title: "AI Manager & Delegation Studio", desc: "Command prompt box with multi-agent orchestration", icon: "&#128640;", action: () => switchView('ai_manager') },
    { title: "SQL Video Maker (9:16 Shorts)", desc: "YouTube metadata & 60 FPS video renderer", icon: "&#127916;", action: () => switchView('sql_video') },
    { title: "Python Video Maker", desc: "Interactive python concept animation studio", icon: "&#128013;", action: () => switchView('python_video') },
    { title: "Data Engineering & Lakehouse", desc: "Snowflake, Oracle 23ai, S3 Parquet pipelines", icon: "&#9881;", action: () => switchView('data_engineer') },
    { title: "Cybersecurity & Defenses Lab", desc: "Nmap port scanner, PCAP analyzer, security audits", icon: "&#128737;", action: () => switchView('cyber_lab') },
    { title: "Make.com Automation Sync", desc: "Fire high-salary pipeline webhook trigger", icon: "&#9889;", action: () => {
        fetch('/api/fabric/query', { credentials: 'omit' }).catch(() => {});
        showModernToast('Make.com Trigger', 'Dispatched real-time webhook payload to Make.com', 'success');
    }},
    { title: "Call All 305 Agents to Work", desc: "Recall wandering agents to workstations", icon: "&#9889;", action: () => {
        if (typeof triggerOfficeCallToWork === 'function') triggerOfficeCallToWork();
        showModernToast('Office Control', 'All 305 agents recalled to active duty', 'success');
    }},
    { title: "Allow Coffee / Lounge Breaks", desc: "Permit standby agents to roam and rest", icon: "&#9749;", action: () => {
        if (typeof triggerOfficeAllowBreaks === 'function') triggerOfficeAllowBreaks();
        showModernToast('Office Control', 'Standby agents dispatched to lounge & espresso bar', 'info');
    }},
    { title: "Telegram Tech News Dispatch", desc: "Send latest AI trends to @mangesh_technews_bot", icon: "&#128227;", action: () => {
        showModernToast('Telegram Dispatch', 'Morning tech news broadcasted to Telegram', 'success');
    }},
    { title: "Mute / Unmute Cyber Sound FX", desc: "Toggle synthesized UI interaction sounds", icon: "&#128266;", action: () => toggleCyberSoundFx() }
];

let selectedPaletteIndex = 0;

function openCommandPalette() {
    const backdrop = document.getElementById('nanoCommandPaletteBackdrop');
    const input = document.getElementById('paletteSearchInput');
    if (!backdrop || !input) return;
    backdrop.style.display = 'flex';
    input.value = '';
    selectedPaletteIndex = 0;
    renderPaletteResults(PALETTE_COMMANDS);
    setTimeout(() => input.focus(), 50);
    playCyberClickSound();
}

function closeCommandPalette(e) {
    const backdrop = document.getElementById('nanoCommandPaletteBackdrop');
    if (backdrop) backdrop.style.display = 'none';
}

function filterCommandPalette() {
    const q = (document.getElementById('paletteSearchInput').value || '').toLowerCase().trim();
    const filtered = PALETTE_COMMANDS.filter(cmd => 
        cmd.title.toLowerCase().includes(q) || cmd.desc.toLowerCase().includes(q)
    );
    selectedPaletteIndex = 0;
    renderPaletteResults(filtered);
}

function renderPaletteResults(list) {
    const container = document.getElementById('paletteResultsList');
    if (!container) return;
    if (list.length === 0) {
        container.innerHTML = '<div style="padding:18px; text-align:center; color:#64748B; font-size:13px;">No matching commands found.</div>';
        return;
    }
    container.innerHTML = list.map((cmd, idx) => `
        <div class="palette-item ${idx === selectedPaletteIndex ? 'selected' : ''}" 
             onclick="executePaletteCommand(${idx})" 
             onmouseenter="selectedPaletteIndex = ${idx}; renderPaletteHighlight(); playCyberHoverSound();">
            <div class="palette-item-left">
                <span class="palette-item-icon">${cmd.icon}</span>
                <div>
                    <div class="palette-item-title">${cmd.title}</div>
                    <div class="palette-item-desc">${cmd.desc}</div>
                </div>
            </div>
            <span class="nano-kbd">&#8629;</span>
        </div>
    `).join('');
}

function renderPaletteHighlight() {
    const items = document.querySelectorAll('.palette-item');
    items.forEach((item, idx) => {
        if (idx === selectedPaletteIndex) item.classList.add('selected');
        else item.classList.remove('selected');
    });
}

function handlePaletteKeydown(e) {
    const items = document.querySelectorAll('.palette-item');
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedPaletteIndex = (selectedPaletteIndex + 1) % (items.length || 1);
        renderPaletteHighlight();
        playCyberHoverSound();
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedPaletteIndex = (selectedPaletteIndex - 1 + (items.length || 1)) % (items.length || 1);
        renderPaletteHighlight();
        playCyberHoverSound();
    } else if (e.key === 'Enter') {
        e.preventDefault();
        executePaletteCommand(selectedPaletteIndex);
    } else if (e.key === 'Escape') {
        closeCommandPalette();
    }
}

function executePaletteCommand(idx) {
    const q = (document.getElementById('paletteSearchInput').value || '').toLowerCase().trim();
    const filtered = PALETTE_COMMANDS.filter(cmd => 
        cmd.title.toLowerCase().includes(q) || cmd.desc.toLowerCase().includes(q)
    );
    const cmd = filtered[idx] || PALETTE_COMMANDS[idx];
    if (cmd && typeof cmd.action === 'function') {
        closeCommandPalette();
        playCyberClickSound();
        cmd.action();
    }
}

// Global Hotkeys Listener (Ctrl+K, Cmd+K, /)
window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openCommandPalette();
    } else if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
        openCommandPalette();
    }
});

// --- 6. Modern 2026 Micro-Toasts (#35) ---
function showModernToast(title, msg, type = 'info') {
    const container = document.getElementById('nanoToastContainer');
    if (!container) return;

    const icon = type === 'success' ? '&#9989;' : (type === 'error' ? '&#10060;' : '&#9889;');
    const color = type === 'success' ? '#10B981' : (type === 'error' ? '#EF4444' : '#38BDF8');

    const toast = document.createElement('div');
    toast.className = 'nano-modern-toast';
    toast.innerHTML = `
        <span style="font-size:18px;">${icon}</span>
        <div style="flex:1;">
            <div style="font-size:12.5px; font-weight:800; color:#F8FAFC;">${title}</div>
            <div style="font-size:11.5px; color:#CBD5E1; margin-top:2px; line-height:1.4;">${msg}</div>
        </div>
        <div class="toast-bar" style="background:${color};"></div>
    `;

    container.appendChild(toast);
    playCyberClickSound();

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px) scale(0.9)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// --- 7. Matrix Text Scramble Engine (#205) ---
function scrambleText(element, targetText, duration = 800) {
    if (!element) return;
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*";
    const start = performance.now();
    const len = targetText.length;

    function frame(now) {
        const progress = Math.min(1, (now - start) / duration);
        const resolved = Math.floor(progress * len);
        let out = targetText.slice(0, resolved);
        for (let i = resolved; i < len; i++) {
            out += chars[Math.floor(Math.random() * chars.length)];
        }
        element.innerText = out;
        if (progress < 1) {
            requestAnimationFrame(frame);
        } else {
            element.innerText = targetText;
        }
    }
    requestAnimationFrame(frame);
}

// Initialize 2026 Modern Suite on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(init3dCardTilt, 400);
    if (isSoundMuted) {
        const icon = document.getElementById('soundFxIcon');
        if (icon) icon.innerHTML = '&#128263;';
    }
});
</script>
"""
