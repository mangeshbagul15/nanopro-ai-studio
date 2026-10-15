"""
Mangesh Nano Pro AI Studio - UI CSS Stylesheet
Global Design System:
- Navy & Charcoal backgrounds (#070B16, #0E1528, #151D36, #1A2342)
- White & Soft-Grey typography (#F8FAFC, #94A3B8, #64748B)
- Restrained Cyan, Cobalt, Emerald, and Amber accents (#38BDF8, #6366F1, #10B981, #F59E0B)
- 3D-styled depth, subtle lighting, and responsive panels
- Single AI Manager Symbol with 8 dynamic visual states
- Interactive Tables, Canvas Charts, and Step Progress Panels
- Animated 3D AI Agent Office & Workstations
- Task Scheduler Timeline & Status Badges
- News Center Dual-Language Cards & Floating Banner
- Entertainment Discovery Cards with Hover Zoom
- Book Reader & Learning Assistant TOC & Controls
"""

DASHBOARD_UPGRADE_CSS = r"""
/* === GLOBAL DESIGN SYSTEM ENHANCEMENTS === */
:root {
    --bg-base: #070B16;
    --bg-sidebar: #0E1528;
    --bg-card: #151D36;
    --bg-panel: #1A2342;
    --border: #263354;
    --border-highlight: #38BDF8;
    --accent-blue: #38BDF8;
    --accent-indigo: #6366F1;
    --accent-purple: #8B5CF6;
    --accent-emerald: #10B981;
    --accent-amber: #F59E0B;
    --accent-rose: #F43F5E;
    --text-main: #F8FAFC;
    --text-muted: #94A3B8;
    --text-sub: #64748B;
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --shadow-3d: 0 8px 24px -4px rgba(0, 0, 0, 0.45), 0 2px 6px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

/* === SINGLE AI MANAGER SYMBOL (TOPBAR & SYSTEM) === */
.ai-manager-symbol-container {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, rgba(21, 29, 54, 0.95), rgba(26, 35, 66, 0.85));
    border: 1px solid var(--border);
    padding: 5px 12px 5px 8px;
    border-radius: 30px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    user-select: none;
}
.ai-manager-symbol-container:hover {
    border-color: var(--accent-blue);
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.35);
    transform: translateY(-1px);
}
.manager-core-orb {
    position: relative;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #0E1528;
}
.orb-inner {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--accent-blue);
    box-shadow: 0 0 10px var(--accent-blue);
    transition: all 0.4s ease;
}
.orb-ring {
    position: absolute;
    border-radius: 50%;
    border: 1.5px solid rgba(56, 189, 248, 0.4);
    pointer-events: none;
}
.orb-ring.ring-1 {
    width: 22px;
    height: 22px;
    border-top-color: transparent;
    animation: orbSpin 6s linear infinite;
}
.orb-ring.ring-2 {
    width: 28px;
    height: 28px;
    border-bottom-color: transparent;
    border-left-color: transparent;
    animation: orbSpinRev 9s linear infinite;
}
@keyframes orbSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
@keyframes orbSpinRev {
    from { transform: rotate(360deg); }
    to { transform: rotate(0deg); }
}

/* AI Manager Dynamic States */
.state-ready .orb-inner { background: #38BDF8; box-shadow: 0 0 10px #38BDF8; }
.state-listening .orb-inner { background: #10B981; box-shadow: 0 0 14px #10B981; animation: pulseListen 1.2s infinite; }
.state-thinking .orb-inner { background: #8B5CF6; box-shadow: 0 0 14px #8B5CF6; }
.state-thinking .orb-ring.ring-1 { animation: orbSpin 1.5s linear infinite; border-color: #8B5CF6; }
.state-planning .orb-inner { background: #6366F1; box-shadow: 0 0 12px #6366F1; }
.state-delegating .orb-inner { background: #06B6D4; box-shadow: 0 0 14px #06B6D4; }
.state-executing .orb-inner { background: #F59E0B; box-shadow: 0 0 14px #F59E0B; }
.state-executing .orb-ring.ring-1 { animation: orbSpin 1s linear infinite; border-color: #F59E0B; }
.state-speaking .orb-inner { background: #EC4899; box-shadow: 0 0 14px #EC4899; animation: pulseSpeak 0.8s infinite; }
.state-waiting .orb-inner { background: #FBBF24; box-shadow: 0 0 8px #FBBF24; }
.state-error .orb-inner { background: #EF4444; box-shadow: 0 0 14px #EF4444; }

@keyframes pulseListen {
    0% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.25); opacity: 1; box-shadow: 0 0 18px #10B981; }
    100% { transform: scale(1); opacity: 0.9; }
}
@keyframes pulseSpeak {
    0% { transform: scale(0.9); }
    50% { transform: scale(1.2); box-shadow: 0 0 18px #EC4899; }
    100% { transform: scale(0.9); }
}

.manager-symbol-label {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
}
.symbol-name {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.6px;
    color: #F8FAFC;
}
.symbol-state {
    font-size: 9.5px;
    font-weight: 700;
    color: var(--accent-blue);
    text-transform: uppercase;
}

/* === MANAGER CONVERSATION STREAM & MESSAGE CARDS === */
.manager-chat-container {
    display: flex;
    flex-direction: column;
    height: 520px;
    background: #0A0F1E;
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-3d);
}
.chat-stream-box {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    scroll-behavior: smooth;
}
.chat-msg {
    display: flex;
    gap: 12px;
    max-width: 88%;
    animation: fadeInMsg 0.3s ease-out;
}
@keyframes fadeInMsg {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.chat-msg.user {
    align-self: flex-end;
    flex-direction: row-reverse;
}
.chat-msg.manager {
    align-self: flex-start;
}
.msg-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
}
.chat-msg.user .msg-avatar {
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    color: #FFF;
    border: 1px solid #3B82F6;
}
.chat-msg.manager .msg-avatar {
    background: linear-gradient(135deg, #1E1B4B, #312E81);
    color: #38BDF8;
    border: 1px solid #4F46E5;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
}
.msg-bubble {
    background: #151D36;
    border: 1px solid #263354;
    border-radius: 14px;
    padding: 14px 16px;
    color: var(--text-main);
    font-size: 13.5px;
    line-height: 1.6;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    position: relative;
    word-break: break-word;
}
.chat-msg.user .msg-bubble {
    background: linear-gradient(135deg, #1E293B, #0F172A);
    border-color: #334155;
    border-top-right-radius: 4px;
}
.chat-msg.manager .msg-bubble {
    background: #141B33;
    border-color: #2D3B62;
    border-top-left-radius: 4px;
}
.msg-meta {
    font-size: 10.5px;
    color: var(--text-sub);
    margin-top: 6px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.msg-tools {
    display: flex;
    gap: 8px;
    margin-top: 6px;
}
.msg-tool-btn {
    background: transparent;
    border: 1px solid #334155;
    color: var(--text-muted);
    font-size: 11px;
    border-radius: 4px;
    padding: 2px 7px;
    cursor: pointer;
    transition: all 0.2s;
}
.msg-tool-btn:hover {
    color: var(--accent-blue);
    border-color: var(--accent-blue);
}

/* Smart Component: KPI Cards Grid */
.kpi-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
    margin: 12px 0;
}
.kpi-metric-card {
    background: #0E1528;
    border: 1px solid #263354;
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    flex-direction: column;
}
.kpi-metric-label {
    font-size: 11px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.kpi-metric-val {
    font-size: 18px;
    font-weight: 800;
    color: #F8FAFC;
    margin: 3px 0;
}
.kpi-metric-change {
    font-size: 10.5px;
    color: #10B981;
    font-weight: 600;
}

/* Smart Component: Real-time Execution Card */
.execution-steps-card {
    background: #0B1120;
    border: 1px solid #1E293B;
    border-left: 3px solid var(--accent-blue);
    border-radius: 8px;
    padding: 12px;
    margin: 12px 0;
    font-family: inherit;
}
.exec-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 12px;
    font-weight: 700;
    color: var(--accent-blue);
}
.exec-step-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11.5px;
    color: #CBD5E1;
    margin-bottom: 4px;
}
.exec-step-num {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #1E293B;
    color: #38BDF8;
    font-size: 10px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
}
.exec-code-snippet {
    background: #050811;
    border: 1px solid #1E293B;
    border-radius: 6px;
    padding: 8px 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11.5px;
    color: #38BDF8;
    overflow-x: auto;
    margin-top: 8px;
    white-space: pre-wrap;
}

/* Smart Component: Interactive Sortable Table */
.interactive-table-wrapper {
    background: #0B1120;
    border: 1px solid var(--border);
    border-radius: 8px;
    margin: 12px 0;
    overflow: hidden;
}
.table-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: #11192E;
    border-bottom: 1px solid #263354;
    gap: 10px;
}
.table-search-input {
    background: #0A0F1E;
    border: 1px solid #263354;
    color: #F8FAFC;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11.5px;
    max-width: 220px;
}
.table-btn-export {
    background: #1E293B;
    border: 1px solid #334155;
    color: #E2E8F0;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: 0.2s;
}
.table-btn-export:hover {
    background: #334155;
    color: #38BDF8;
}
.table-scroll-area {
    max-height: 280px;
    overflow-x: auto;
    overflow-y: auto;
}
.studio-data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    text-align: left;
}
.studio-data-table th {
    background: #111A30;
    color: #94A3B8;
    font-weight: 700;
    padding: 8px 12px;
    border-bottom: 1px solid #263354;
    cursor: pointer;
    white-space: nowrap;
    user-select: none;
}
.studio-data-table th:hover {
    color: #38BDF8;
}
.studio-data-table td {
    padding: 7px 12px;
    border-bottom: 1px solid #1A2342;
    color: #F8FAFC;
    white-space: nowrap;
}
.studio-data-table tr:hover {
    background: rgba(56, 189, 248, 0.04);
}
.table-pagination-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    background: #11192E;
    border-top: 1px solid #263354;
    font-size: 11px;
    color: var(--text-muted);
}

/* Smart Component: Canvas Chart Container */
.chart-container-box {
    background: #0B1120;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    margin: 12px 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.chart-title {
    font-size: 12.5px;
    font-weight: 700;
    color: #F8FAFC;
}
.chart-toggles {
    display: flex;
    gap: 4px;
}
.chart-toggle-btn {
    background: #1E293B;
    border: 1px solid #334155;
    color: var(--text-muted);
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 4px;
    cursor: pointer;
}
.chart-toggle-btn.active {
    background: #2563EB;
    color: #FFF;
    border-color: #3B82F6;
}

/* Chat Prompt Chips */
.quick-prompt-chips-bar {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding: 8px 12px;
    background: #0C1224;
    border-top: 1px solid #1E293B;
}
.action-chip {
    background: #151D36;
    border: 1px solid #2A385E;
    color: #CBD5E1;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 14px;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s ease;
}
.action-chip:hover {
    background: #1E293B;
    border-color: var(--accent-blue);
    color: #38BDF8;
    transform: translateY(-1px);
}

/* Message Composer */
.chat-composer-box {
    display: flex;
    gap: 8px;
    padding: 12px;
    background: #0E1528;
    border-top: 1px solid var(--border);
    align-items: flex-end;
}
.chat-composer-input {
    flex: 1;
    background: #070B16;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: #F8FAFC;
    font-size: 13.5px;
    padding: 10px 12px;
    resize: none;
    height: 48px;
    outline: none;
    font-family: inherit;
    line-height: 1.4;
    transition: border-color 0.2s;
}
.chat-composer-input:focus {
    border-color: var(--accent-blue);
    box-shadow: 0 0 8px rgba(56, 189, 248, 0.25);
}

/* === ANIMATED 3D AI AGENT OFFICE === */
.office-3d-viewport {
    background: linear-gradient(180deg, #070B16 0%, #0F172A 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    min-height: 580px;
    box-shadow: var(--shadow-3d);
    position: relative;
    overflow: hidden;
}
.office-floor-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    position: relative;
    z-index: 2;
}
.manager-central-desk {
    grid-column: 1 / -1;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
    border: 1px solid #38BDF8;
    border-radius: var(--radius-md);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    position: relative;
}
.desk-hologram-core {
    display: flex;
    align-items: center;
    gap: 14px;
}
.hologram-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: radial-gradient(circle, #38BDF8 20%, #1D4ED8 80%);
    box-shadow: 0 0 16px #38BDF8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    animation: hologramPulse 2s ease-in-out infinite alternate;
}
@keyframes hologramPulse {
    from { transform: scale(1); box-shadow: 0 0 12px #38BDF8; }
    to { transform: scale(1.08); box-shadow: 0 0 22px #60A5FA; }
}

.agent-pod-card {
    background: #11192E;
    border: 1px solid #1E293B;
    border-radius: var(--radius-md);
    padding: 14px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
.agent-pod-card:hover {
    border-color: #38BDF8;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4), 0 0 12px rgba(56, 189, 248, 0.2);
}
.agent-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}
.agent-title {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
    display: flex;
    align-items: center;
    gap: 6px;
}
.agent-status-pill {
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 10px;
    text-transform: uppercase;
}
.pill-working { background: rgba(56, 189, 248, 0.2); color: #38BDF8; border: 1px solid #38BDF8; }
.pill-standby { background: rgba(100, 116, 139, 0.2); color: #94A3B8; border: 1px solid #475569; }
.pill-completed { background: rgba(16, 185, 129, 0.2); color: #10B981; border: 1px solid #10B981; }
.pill-failed { background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid #EF4444; }
.pill-paused { background: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid #F59E0B; }

.agent-task-text {
    font-size: 11.5px;
    color: #CBD5E1;
    min-height: 32px;
    line-height: 1.4;
    margin-bottom: 8px;
}
.agent-progress-track {
    height: 4px;
    background: #1E293B;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 8px;
}
.agent-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #38BDF8, #6366F1);
    transition: width 0.4s ease;
}
.agent-meta-row {
    display: flex;
    justify-content: space-between;
    font-size: 10.5px;
    color: var(--text-sub);
}

/* === NEWS CENTER CARDS & FLOATING ALERT === */
.news-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    margin-top: 14px;
}
.news-article-card {
    background: #11192E;
    border: 1px solid #1E293B;
    border-radius: var(--radius-md);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: transform 0.2s, border-color 0.2s;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
}
.news-article-card:hover {
    border-color: #38BDF8;
    transform: translateY(-2px);
}
.news-card-thumb {
    width: 100%;
    height: 140px;
    object-fit: cover;
    background: #0E1528;
}
.news-card-body {
    padding: 14px;
    display: flex;
    flex-direction: column;
    flex: 1;
}
.news-badges-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
}
.badge-publisher {
    font-size: 10.5px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
}
.pub-abp { background: #DC2626; color: #FFF; }
.pub-aajtak { background: #EA580C; color: #FFF; }
.badge-category {
    font-size: 10px;
    font-weight: 700;
    background: #1E293B;
    color: #94A3B8;
    padding: 2px 6px;
    border-radius: 4px;
}
.badge-breaking {
    font-size: 10px;
    font-weight: 800;
    background: #EF4444;
    color: #FFF;
    padding: 2px 6px;
    border-radius: 4px;
    animation: pulseListen 1s infinite;
}
.news-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.4;
    margin-bottom: 8px;
}
.news-summary-mr {
    font-size: 12px;
    color: #CBD5E1;
    line-height: 1.5;
    margin-bottom: 6px;
}
.news-summary-en {
    font-size: 11.5px;
    color: #94A3B8;
    line-height: 1.4;
    margin-bottom: 12px;
    font-style: italic;
}
.news-footer-actions {
    margin-top: auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 8px;
    border-top: 1px solid #1E293B;
}

/* Floating Non-Blocking News Banner */
.floating-news-alert-banner {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 360px;
    background: linear-gradient(135deg, #11192E, #0E1528);
    border: 1px solid #DC2626;
    border-left: 4px solid #EF4444;
    border-radius: 10px;
    padding: 14px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(239, 68, 68, 0.25);
    z-index: 9999;
    display: none;
    animation: slideUpAlert 0.4s ease-out;
}
@keyframes slideUpAlert {
    from { transform: translateY(40px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

/* === ENTERTAINMENT & LIFESTYLE CARDS === */
.ent-discovery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
    margin-top: 14px;
}
.ent-card {
    background: #11192E;
    border: 1px solid #1E293B;
    border-radius: var(--radius-md);
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    display: flex;
    flex-direction: column;
}
.ent-card:hover {
    border-color: #38BDF8;
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.45);
}
.ent-card-thumb-wrap {
    width: 100%;
    height: 180px;
    overflow: hidden;
    position: relative;
}
.ent-card-thumb {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}
.ent-card:hover .ent-card-thumb {
    transform: scale(1.08);
}
.ent-card-content {
    padding: 14px;
    display: flex;
    flex-direction: column;
    flex: 1;
}
.ent-card-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 4px;
}
.ent-card-creator {
    font-size: 11px;
    color: var(--accent-blue);
    margin-bottom: 8px;
    font-weight: 600;
}
.ent-card-desc {
    font-size: 11.5px;
    color: #94A3B8;
    line-height: 1.4;
    margin-bottom: 12px;
}

/* === BOOK READER & LEARNING CENTER === */
.reader-workspace {
    display: grid;
    grid-template-columns: 260px 1fr;
    gap: 16px;
    min-height: 560px;
}
.reader-toc-panel {
    background: #0E1528;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px;
    display: flex;
    flex-direction: column;
}
.toc-chapter-item {
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 12px;
    color: #CBD5E1;
    cursor: pointer;
    transition: 0.2s;
    margin-bottom: 4px;
    border-left: 2px solid transparent;
}
.toc-chapter-item:hover {
    background: #1E293B;
    color: #38BDF8;
}
.toc-chapter-item.active {
    background: #1A2342;
    border-left-color: #38BDF8;
    color: #F8FAFC;
    font-weight: 700;
}
.reader-content-panel {
    background: #0F172A;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 20px;
    display: flex;
    flex-direction: column;
    position: relative;
}
.reader-text-area {
    font-size: 14px;
    line-height: 1.8;
    color: #E2E8F0;
    max-height: 440px;
    overflow-y: auto;
    padding-right: 12px;
}

/* === WINDOWS-STYLE TASK SCHEDULER WIZARD & DASHBOARD === */
.scheduler-metrics-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
    margin-bottom: 14px;
}
.metric-box-sched {
    background: #11192E;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 10px 12px;
    text-align: center;
}
.sched-wizard-tabs {
    display: flex;
    gap: 6px;
    border-bottom: 1px solid #263354;
    padding-bottom: 8px;
    margin-bottom: 14px;
}
.sched-tab-btn {
    background: transparent;
    border: none;
    color: #94A3B8;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
}
.sched-tab-btn.active {
    background: #2563EB;
    color: #FFF;
}
"""
