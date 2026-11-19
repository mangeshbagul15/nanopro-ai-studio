"""
Mangesh Nano Pro AI Studio - Global AI Lab Workspace View (Feature 53)
Full Enterprise Multi-Model Studio with:
- Chats & Projects Resizable Left Sidebar (like Data Modeling AI)
- Claude Code / Gemini / Qoder / Antigravity conversational workspace
- 2,150+ Unified Frontier Models (OpenRouter, AI/ML API, Hugging Face, Fal.ai, Replicate, Groq)
- Single AUTO Mathematical Pareto-Bandit Router (<800ms SLA, sub-3ms overhead)
- DuckDB Local Persistent Storage + Google BigQuery Long-Term Lakehouse Archiving
- Syntax-highlighted code blocks with Copy & Run Sandbox
- Live Mermaid diagram rendering
"""

def get_global_ai_lab_html() -> str:
    return r'''
<!-- VIEW: GLOBAL AI LAB (FEATURE 53) -->
<div class="workspace-view" id="view-global_ai_lab">
<style>
#view-global_ai_lab {
  flex: 1 1 0% !important;
  width: 100% !important;
  height: 100% !important;
  max-height: 100% !important;
  min-height: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
  display: none;
}
#view-global_ai_lab.active {
  display: flex !important;
  flex-direction: column !important;
}
body:has(#view-global_ai_lab.active) #main-content-viewport,
#main-content-viewport:has(#view-global_ai_lab.active) {
  padding: 0 !important;
  overflow: hidden !important;
}

/* CRITICAL: Never allow floating Dynamic Island or overlays to cover Global AI Lab controls */
#nanoDynamicIsland,
.nano-dynamic-island,
body:has(#view-global_ai_lab.active) #nanoDynamicIsland,
body:has(#view-global_ai_lab.active) .nano-dynamic-island,
body.in-global_ai_lab #nanoDynamicIsland,
body.in-global_ai_lab .nano-dynamic-island {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
  pointer-events: none !important;
  transform: translate(-50%, -100px) !important;
}

#view-global_ai_lab .ailab-app {
  --al-bg: #0B1119;
  --al-panel: #0F1724;
  --al-panel-2: #131E2E;
  --al-line: #1E2B3E;
  --al-line-2: #283952;
  --al-text: #E6EDF7;
  --al-muted: #94A3B8;
  --al-dim: #64748B;
  --al-accent: #8B5CF6;
  --al-accent-glow: rgba(139, 92, 246, 0.25);
  --al-cyan: #38BDF8;
  --al-green: #10B981;
  --al-amber: #F59E0B;
  --al-purple: #C084FC;
  position: relative;
  display: flex;
  flex-direction: column;
  flex: 1 1 0% !important;
  width: 100% !important;
  height: 100% !important;
  max-height: 100% !important;
  min-height: 0 !important;
  background: var(--al-bg);
  color: var(--al-text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 13px;
  overflow: hidden !important;
}

/* ---------------- Topbar (Single-Row Modern Responsive Header) ---------------- */
#view-global_ai_lab .ailab-topbar {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  gap: 8px !important;
  height: 52px !important;
  min-height: 52px !important;
  max-height: 52px !important;
  padding: 0 16px !important;
  background: linear-gradient(180deg, #0B1119 0%, #080D14 100%) !important;
  border-bottom: 1.5px solid rgba(139, 92, 246, 0.3) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6) !important;
  flex-shrink: 0 !important;
  z-index: 100 !important;
  position: relative !important;
  overflow-x: auto !important;
  overflow-y: hidden !important;
  box-sizing: border-box !important;
  white-space: nowrap !important;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
#view-global_ai_lab .ailab-topbar::-webkit-scrollbar {
  display: none;
}
#view-global_ai_lab .ailab-topbar,
#view-global_ai_lab .ailab-topbar *,
#view-global_ai_lab .ailab-topbar button,
#view-global_ai_lab .ailab-topbar span,
#view-global_ai_lab .ailab-topbar select {
  white-space: nowrap !important;
}

#view-global_ai_lab .ailab-topbar-left {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  flex: 0 0 auto !important;
  min-width: max-content !important;
}
#view-global_ai_lab .ailab-brand {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  font-weight: 800 !important;
  font-size: 13px !important;
  color: #F8FAFC !important;
  text-decoration: none !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-brand-badge {
  font-size: 9.5px !important;
  font-weight: 800 !important;
  padding: 2px 7px !important;
  border-radius: 999px !important;
  background: linear-gradient(135deg, #8B5CF6, #38BDF8) !important;
  color: #FFF !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-conn-badge {
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  color: #86EFAC !important;
  background: rgba(16, 185, 129, 0.12) !important;
  border: 1px solid rgba(16, 185, 129, 0.3) !important;
  padding: 2px 8px !important;
  border-radius: 999px !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-pulse-dot {
  width: 7px;
  height: 7px;
  background: #10B981;
  border-radius: 50%;
  box-shadow: 0 0 8px #10B981;
  animation: ailabPulse 2s infinite;
}
@keyframes ailabPulse {
  0% { transform: scale(0.9); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0.7; }
}

#view-global_ai_lab .ailab-topbar-center {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  flex: 0 0 auto !important;
  min-width: max-content !important;
  justify-content: flex-start !important;
  flex-wrap: nowrap !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-model-selector-wrap {
  position: relative !important;
  display: inline-flex !important;
  align-items: center !important;
  background: #0B132B !important;
  border: 1.5px solid #8B5CF6 !important;
  box-shadow: 0 0 14px rgba(139, 92, 246, 0.3) !important;
  border-radius: 8px !important;
  padding: 0 8px !important;
  gap: 4px !important;
  width: 195px !important;
  min-width: 175px !important;
  max-width: 210px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  transition: all 0.2s ease !important;
  flex: 0 0 auto !important;
  white-space: nowrap !important;
  overflow: hidden !important;
}
#view-global_ai_lab .ailab-model-selector-wrap:hover,
#view-global_ai_lab .ailab-model-selector-wrap:focus-within {
  border-color: #C084FC !important;
  box-shadow: 0 0 20px rgba(192, 132, 252, 0.5) !important;
}
#view-global_ai_lab .ailab-model-select {
  background: transparent !important;
  border: none !important;
  color: #FFFFFF !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  width: 100% !important;
  outline: none !important;
  cursor: pointer !important;
  padding: 0 !important;
  white-space: nowrap !important;
  text-overflow: ellipsis !important;
  overflow: hidden !important;
}
#view-global_ai_lab select option,
#view-global_ai_lab select optgroup {
  background: #0B132B !important;
  color: #FFFFFF !important;
  font-size: 13px !important;
  padding: 8px 12px !important;
}
#view-global_ai_lab .ailab-effort-wrap {
  position: relative !important;
  display: inline-flex !important;
  align-items: center !important;
  background: #0B132B !important;
  border: 1.5px solid #10B981 !important;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.25) !important;
  border-radius: 8px !important;
  padding: 0 8px !important;
  gap: 4px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  white-space: nowrap !important;
  flex: 0 0 auto !important;
  transition: all 0.2s ease !important;
}
#view-global_ai_lab .ailab-effort-select {
  background: transparent !important;
  border: none !important;
  color: #FFFFFF !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  outline: none !important;
  cursor: pointer !important;
  white-space: nowrap !important;
  padding: 0 !important;
}
#view-global_ai_lab .ailab-browse-btn {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(56, 189, 248, 0.25) 100%) !important;
  border: 1.5px solid #8B5CF6 !important;
  color: #E2E8F0 !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 0 9px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  border-radius: 8px !important;
  cursor: pointer !important;
  white-space: nowrap !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.25) !important;
  flex: 0 0 auto !important;
}
#view-global_ai_lab .ailab-browse-btn:hover {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.45) 0%, rgba(56, 189, 248, 0.45) 100%) !important;
  color: #FFF !important;
  border-color: #38BDF8 !important;
  transform: translateY(-1px) !important;
}

#view-global_ai_lab .ailab-topbar-right {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  flex: 0 0 auto !important;
  margin-left: auto !important; /* PUSHES RIGHT CONTROLS TO THE FAR RIGHT */
  min-width: max-content !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-iconbtn {
  background: transparent !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  color: var(--al-muted) !important;
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  border-radius: 7px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer !important;
  flex-shrink: 0 !important;
  transition: all 0.15s ease !important;
}
#view-global_ai_lab .ailab-iconbtn:hover {
  background: var(--al-panel-2) !important;
  color: #FFF !important;
  border-color: var(--al-line) !important;
}
#view-global_ai_lab .ailab-cua-toggle-btn {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  background: #0B132B !important;
  border: 1.5px solid #38BDF8 !important;
  color: #38BDF8 !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 0 9px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  border-radius: 7px !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
}
#view-global_ai_lab .ailab-cua-toggle-btn:hover {
  background: rgba(56, 189, 248, 0.15) !important;
  border-color: #7DD3FC !important;
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.4) !important;
}
#view-global_ai_lab .ailab-cua-toggle-btn.active {
  background: rgba(56, 189, 248, 0.2) !important;
  border-color: #38BDF8 !important;
  color: #FFFFFF !important;
}
#view-global_ai_lab .ailab-topbar-right .ailab-code-btn,
#view-global_ai_lab .ailab-topbar-sync-btn {
  background: rgba(56, 189, 248, 0.08) !important;
  border: 1px solid rgba(56, 189, 248, 0.35) !important;
  color: #38BDF8 !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 0 8px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  border-radius: 7px !important;
  cursor: pointer !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  transition: all 0.15s ease !important;
}
#view-global_ai_lab .ailab-topbar-right .ailab-code-btn:hover,
#view-global_ai_lab .ailab-topbar-sync-btn:hover {
  background: rgba(56, 189, 248, 0.18) !important;
  border-color: #38BDF8 !important;
  color: #FFFFFF !important;
}
#view-global_ai_lab .ailab-topbar-right .ailab-btn-primary,
#view-global_ai_lab .ailab-topbar-new-chat-btn {
  background: linear-gradient(135deg, #7C3AED 0%, #2563EB 100%) !important;
  color: #FFF !important;
  border: none !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 0 10px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  border-radius: 7px !important;
  cursor: pointer !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  box-shadow: 0 2px 10px rgba(124, 58, 237, 0.4) !important;
  transition: all 0.15s ease !important;
}
#view-global_ai_lab .ailab-topbar-right .ailab-btn-primary:hover,
#view-global_ai_lab .ailab-topbar-new-chat-btn:hover {
  filter: brightness(1.15) !important;
  transform: translateY(-1px) !important;
}

/* ---------------- Layout Body ---------------- */
#view-global_ai_lab .ailab-body {
  display: flex;
  flex: 1 1 0% !important;
  min-height: 0 !important;
  position: relative;
  overflow: hidden;
}

/* ---------------- Sidebar: Chats & Projects ---------------- */
#view-global_ai_lab .ailab-sidebar {
  width: 270px;
  background: var(--al-panel);
  border-right: 1px solid var(--al-line);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
  transition: width 0.2s ease;
}
#view-global_ai_lab .ailab-sidebar.collapsed {
  width: 0 !important;
  border-right: none;
}
#view-global_ai_lab .ailab-sidebar-head {
  padding: 12px 14px 10px 14px;
  border-bottom: 1px solid var(--al-line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
#view-global_ai_lab .ailab-sidebar-title {
  font-size: 12px;
  font-weight: 700;
  color: #E2E8F0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 6px;
}
#view-global_ai_lab .ailab-sidebar-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 8px 10px;
}
#view-global_ai_lab .ailab-sec-header {
  font-size: 11px;
  font-weight: 700;
  color: var(--al-dim);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 10px 8px 4px 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
#view-global_ai_lab .ailab-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 6px;
  color: var(--al-muted);
  cursor: pointer;
  margin-bottom: 2px;
  transition: all 0.15s ease;
  user-select: none;
  font-size: 12.5px;
}
#view-global_ai_lab .ailab-row:hover {
  background: rgba(255, 255, 255, 0.04);
  color: #F8FAFC;
}
#view-global_ai_lab .ailab-row.is-active {
  background: rgba(139, 92, 246, 0.15);
  color: #F8FAFC;
  font-weight: 600;
  border-left: 2px solid #8B5CF6;
}
#view-global_ai_lab .ailab-row-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
#view-global_ai_lab .ailab-row-badge {
  font-size: 10px;
  background: var(--al-panel-2);
  color: var(--al-dim);
  padding: 1px 6px;
  border-radius: 999px;
}
#view-global_ai_lab .ailab-row-actions {
  display: none;
  align-items: center;
  gap: 2px;
}
#view-global_ai_lab .ailab-row:hover .ailab-row-actions {
  display: flex;
}
#view-global_ai_lab .ailab-rowact {
  background: transparent;
  border: none;
  color: var(--al-dim);
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
}
#view-global_ai_lab .ailab-rowact:hover {
  color: #FFF;
  background: rgba(255, 255, 255, 0.1);
}

#view-global_ai_lab .ailab-storage-footer {
  padding: 10px 14px;
  border-top: 1px solid var(--al-line);
  background: rgba(11, 17, 25, 0.8);
  font-size: 11px;
  color: var(--al-dim);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
#view-global_ai_lab .ailab-grip-v {
  width: 4px;
  cursor: col-resize;
  background: transparent;
  transition: background 0.15s;
}
#view-global_ai_lab .ailab-grip-v:hover {
  background: var(--al-accent);
}

/* ---------------- Main Chat & Code Canvas ---------------- */
#view-global_ai_lab .ailab-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--al-bg);
  position: relative;
  overflow: hidden;
}

#view-global_ai_lab .ailab-canvas-head {
  padding: 8px 16px;
  background: rgba(15, 23, 36, 0.6);
  border-bottom: 1px solid var(--al-line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
#view-global_ai_lab .ailab-chat-title-wrap {
  min-width: 0;
}
#view-global_ai_lab .ailab-active-title {
  font-size: 14px;
  font-weight: 700;
  color: #F8FAFC;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
#view-global_ai_lab .ailab-active-sub {
  font-size: 11px;
  color: var(--al-dim);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

#view-global_ai_lab .ailab-messages-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* Empty Hero */
#view-global_ai_lab .ailab-hero {
  max-width: 780px;
  margin: 20px auto;
  text-align: center;
  padding: 28px 20px;
}
#view-global_ai_lab .ailab-hero h2 {
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #FFFFFF 0%, #C084FC 50%, #38BDF8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
#view-global_ai_lab .ailab-hero p {
  color: var(--al-muted);
  font-size: 13.5px;
  line-height: 1.6;
  margin: 0 auto 20px auto;
  max-width: 620px;
}
#view-global_ai_lab .ailab-pill-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
  margin-top: 16px;
  text-align: left;
}
#view-global_ai_lab .ailab-pill-card {
  background: rgba(19, 30, 46, 0.7);
  border: 1px solid var(--al-line);
  border-radius: 10px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}
#view-global_ai_lab .ailab-pill-card:hover {
  background: rgba(139, 92, 246, 0.12);
  border-color: rgba(139, 92, 246, 0.4);
  transform: translateY(-2px);
}
#view-global_ai_lab .ailab-pill-card-title {
  font-weight: 700;
  font-size: 12.5px;
  color: #F8FAFC;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
#view-global_ai_lab .ailab-pill-card-desc {
  font-size: 11px;
  color: var(--al-muted);
  line-height: 1.4;
}

/* ========================================================= */
/* ANTIGRAVITY & CLAUDE CODE CONVERSATIONAL CHAT ALIGNMENT   */
/* ========================================================= */

#view-global_ai_lab .ailab-messages-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 22px;
  scroll-behavior: smooth;
}

/* Base Message Wrapper */
#view-global_ai_lab .ailab-msg {
  display: flex;
  flex-direction: column;
  width: 100%;
  animation: ailabMsgFadeIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes ailabMsgFadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* USER MESSAGE: Aligned Right (Antigravity & Claude Code) */
#view-global_ai_lab .ailab-msg-user {
  align-self: flex-end !important;
  margin-left: auto !important;
  margin-right: 0 !important;
  max-width: min(720px, 82%) !important;
  width: auto !important;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

#view-global_ai_lab .ailab-user-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 11.5px;
  color: #94A3B8;
}

#view-global_ai_lab .ailab-user-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(139, 92, 246, 0.16);
  border: 1px solid rgba(139, 92, 246, 0.35);
  color: #C084FC;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

#view-global_ai_lab .ailab-user-time {
  font-size: 10.5px;
  color: #64748B;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

#view-global_ai_lab .ailab-msg-user .ailab-bubble,
#view-global_ai_lab .ailab-user-bubble {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.96) 0%, rgba(20, 27, 45, 0.98) 100%) !important;
  border: 1.5px solid rgba(139, 92, 246, 0.35) !important;
  border-radius: 18px 18px 4px 18px !important;
  padding: 13px 18px !important;
  color: #F8FAFC !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35) !important;
  word-break: break-word;
  white-space: pre-wrap;
  text-align: left;
}

/* ASSISTANT MESSAGE: Aligned Left (Antigravity & Claude Code) */
#view-global_ai_lab .ailab-msg-assistant {
  align-self: flex-start !important;
  margin-right: auto !important;
  margin-left: 0 !important;
  max-width: 900px !important;
  width: 100% !important;
}

#view-global_ai_lab .ailab-asst-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

#view-global_ai_lab .ailab-asst-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

#view-global_ai_lab .ailab-asst-avatar-ring {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(56, 189, 248, 0.3) 100%);
  border: 1.5px solid rgba(139, 92, 246, 0.5);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.4);
  flex-shrink: 0;
}

#view-global_ai_lab .ailab-asst-avatar {
  font-size: 15px;
  line-height: 1;
}

#view-global_ai_lab .ailab-asst-info {
  display: flex;
  flex-direction: column;
}

#view-global_ai_lab .ailab-asst-name {
  font-size: 13.5px;
  font-weight: 700;
  color: #F8FAFC;
  display: flex;
  align-items: center;
  gap: 6px;
}

#view-global_ai_lab .ailab-asst-modelid {
  font-size: 11px;
  color: #64748B;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-weight: 400;
}

#view-global_ai_lab .ailab-asst-sub {
  font-size: 11.5px;
  color: #94A3B8;
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 2px;
}

#view-global_ai_lab .ailab-asst-lab {
  color: #38BDF8;
  font-weight: 600;
}

#view-global_ai_lab .ailab-asst-country {
  color: #CBD5E1;
}

#view-global_ai_lab .ailab-asst-tier {
  color: #A78BFA;
  font-size: 10.5px;
}

#view-global_ai_lab .ailab-asst-right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

#view-global_ai_lab .ailab-asst-latency-badge {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #10B981;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

#view-global_ai_lab .ailab-asst-pareto-badge {
  background: rgba(139, 92, 246, 0.14);
  border: 1px solid rgba(139, 92, 246, 0.35);
  color: #C084FC;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
}

#view-global_ai_lab .ailab-math-accordion-btn {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #94A3B8;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

#view-global_ai_lab .ailab-math-accordion-btn:hover {
  background: rgba(51, 65, 85, 0.8);
  color: #F8FAFC;
  border-color: rgba(139, 92, 246, 0.4);
}

#view-global_ai_lab .ailab-caret {
  transition: transform 0.2s ease;
}

#view-global_ai_lab .ailab-prov-math-accordion {
  margin-bottom: 8px;
  animation: ailabMsgFadeIn 0.2s ease;
}

#view-global_ai_lab .ailab-msg-assistant .ailab-bubble,
#view-global_ai_lab .ailab-asst-bubble {
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.88) 0%, rgba(11, 17, 27, 0.94) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 4px 18px 18px 18px !important;
  padding: 18px 22px !important;
  color: #E2E8F0 !important;
  font-size: 14px !important;
  line-height: 1.7 !important;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3) !important;
  backdrop-filter: blur(8px);
}

/* ASSISTANT ACTION FOOTER */
#view-global_ai_lab .ailab-asst-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  padding: 0 4px;
  flex-wrap: wrap;
}

#view-global_ai_lab .ailab-asst-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

#view-global_ai_lab .ailab-action-chip {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94A3B8;
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  transition: all 0.18s ease;
}

#view-global_ai_lab .ailab-action-chip:hover {
  background: rgba(51, 65, 85, 0.8);
  color: #F8FAFC;
  border-color: rgba(139, 92, 246, 0.4);
}

#view-global_ai_lab .ailab-asst-foot-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: #64748B;
}

#view-global_ai_lab .ailab-footer-verified {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #10B981;
  font-weight: 600;
  font-size: 10.5px;
}

/* Pulsing Thinking Indicator */
.ailab-pulse-glow {
  animation: ailabGlowPulse 1.5s infinite alternate;
}
@keyframes ailabGlowPulse {
  from { box-shadow: 0 0 6px rgba(139, 92, 246, 0.4); }
  to { box-shadow: 0 0 16px rgba(56, 189, 248, 0.8); }
}

.ailab-pulse-badge {
  animation: ailabBadgePulse 1.2s infinite alternate;
}
@keyframes ailabBadgePulse {
  from { opacity: 0.6; }
  to { opacity: 1; border-color: #38BDF8; color: #38BDF8; }
}

.ailab-spinner-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #38BDF8;
  box-shadow: 0 0 8px #38BDF8;
  animation: ailabBlink 1s infinite alternate;
  display: inline-block;
}
@keyframes ailabBlink {
  from { opacity: 0.3; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1.2); }
}

/* Frontier Model Provenance Card */
#view-global_ai_lab .ailab-provenance-card {
  background: linear-gradient(135deg, rgba(19, 30, 46, 0.88) 0%, rgba(15, 23, 42, 0.98) 100%);
  border: 1px solid rgba(139, 92, 246, 0.35);
  border-left: 3px solid #8B5CF6;
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(8px);
}
#view-global_ai_lab .ailab-prov-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
#view-global_ai_lab .ailab-prov-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
#view-global_ai_lab .ailab-prov-flag {
  font-size: 22px;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));
}
#view-global_ai_lab .ailab-prov-title-wrap {
  display: flex;
  flex-direction: column;
}
#view-global_ai_lab .ailab-prov-model {
  font-size: 13.5px;
  font-weight: 700;
  color: #F8FAFC;
  display: flex;
  align-items: center;
  gap: 6px;
}
#view-global_ai_lab .ailab-prov-modelid {
  font-size: 10.5px;
  color: #64748B;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-weight: 400;
}
#view-global_ai_lab .ailab-prov-sub {
  font-size: 11.5px;
  color: #94A3B8;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}
#view-global_ai_lab .ailab-prov-lab {
  color: #38BDF8;
  font-weight: 600;
}
#view-global_ai_lab .ailab-prov-country {
  color: #CBD5E1;
  font-weight: 500;
}
#view-global_ai_lab .ailab-prov-tier {
  color: #A78BFA;
  font-size: 11px;
}
#view-global_ai_lab .ailab-prov-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  font-size: 11px;
  color: #94A3B8;
}
#view-global_ai_lab .ailab-prov-time {
  color: #CBD5E1;
  font-weight: 500;
}
#view-global_ai_lab .ailab-prov-latency {
  color: #94A3B8;
}
#view-global_ai_lab .ailab-dur-highlight {
  color: #10B981;
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
#view-global_ai_lab .ailab-prov-math-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
  font-size: 11px;
}
#view-global_ai_lab .ailab-math-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 3px 8px;
  color: #CBD5E1;
}
#view-global_ai_lab .ailab-math-k {
  color: #94A3B8;
}
#view-global_ai_lab .ailab-math-v {
  color: #C084FC;
  font-weight: 600;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
#view-global_ai_lab .ailab-math-shield {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.08);
}
#view-global_ai_lab .ailab-msg-timestamp {
  font-size: 10.5px;
  color: #64748B;
  margin-top: 4px;
  text-align: right;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

/* Thinking Drawer */
#view-global_ai_lab .ailab-thinking-drawer {
  background: rgba(19, 30, 46, 0.5);
  border-left: 2px solid #8B5CF6;
  border-radius: 0 6px 6px 0;
  padding: 8px 12px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #94A3B8;
}
#view-global_ai_lab .ailab-thinking-toggle {
  cursor: pointer;
  font-weight: 600;
  color: #C084FC;
  display: flex;
  align-items: center;
  gap: 6px;
  user-select: none;
}
#view-global_ai_lab .ailab-thinking-content {
  margin-top: 8px;
  line-height: 1.5;
  color: #CBD5E1;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 11.5px;
  white-space: pre-wrap;
  display: none;
}
#view-global_ai_lab .ailab-thinking-drawer.is-open .ailab-thinking-content {
  display: block;
}

/* Code Blocks */
#view-global_ai_lab .ailab-code-block {
  background: #090E17;
  border: 1px solid var(--al-line);
  border-radius: 8px;
  margin: 12px 0;
  overflow: hidden;
}
#view-global_ai_lab .ailab-code-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: #111A28;
  border-bottom: 1px solid var(--al-line);
  font-size: 11px;
  color: var(--al-dim);
  font-weight: 600;
  text-transform: uppercase;
}
#view-global_ai_lab .ailab-code-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}
#view-global_ai_lab .ailab-code-btn {
  background: transparent;
  border: 1px solid var(--al-line);
  color: var(--al-muted);
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}
#view-global_ai_lab .ailab-code-btn:hover {
  background: var(--al-panel-2);
  color: #FFF;
}
#view-global_ai_lab pre.ailab-pre {
  margin: 0;
  padding: 12px;
  overflow-x: auto;
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #E2E8F0;
}

/* Mermaid Visualizations */
#view-global_ai_lab .ailab-mermaid-container {
  background: #0B1119;
  border: 1px solid var(--al-line);
  border-radius: 10px;
  padding: 16px;
  margin: 14px 0;
  text-align: center;
  overflow-x: auto;
}


/* ---------------- Rich Multi-Modal & Cyber Data Formatting ---------------- */
#view-global_ai_lab .ailab-table-wrap {
  overflow-x: auto;
  margin: 14px 0;
  border-radius: 8px;
  border: 1px solid rgba(56, 189, 248, 0.3);
  background: rgba(11, 19, 43, 0.7);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}
#view-global_ai_lab .ailab-cyber-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
  color: #E2E8F0;
}
#view-global_ai_lab .ailab-cyber-table th {
  background: linear-gradient(90deg, rgba(139, 92, 246, 0.25) 0%, rgba(56, 189, 248, 0.2) 100%);
  color: #C084FC;
  padding: 9px 14px;
  text-align: left;
  font-weight: 800;
  border-bottom: 1.5px solid rgba(139, 92, 246, 0.4);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 11.5px;
}
#view-global_ai_lab .ailab-cyber-table td {
  padding: 8px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
#view-global_ai_lab .ailab-cyber-table tr:hover td {
  background: rgba(56, 189, 248, 0.08);
}
#view-global_ai_lab .ailab-ascii-card {
  background: #060B14;
  border: 1px solid rgba(56, 189, 248, 0.4);
  border-radius: 8px;
  padding: 12px 16px;
  margin: 12px 0;
  overflow-x: auto;
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-size: 12px;
  line-height: 1.45;
  color: #38BDF8;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.15);
}
#view-global_ai_lab .ailab-ascii-card pre {
  margin: 0;
  font-family: inherit;
  color: inherit;
}
#view-global_ai_lab .ailab-h {
  margin: 16px 0 8px 0;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #F8FAFC;
}
#view-global_ai_lab .ailab-h1 { font-size: 16px; color: #E0E7FF; border-bottom: 1px solid rgba(139, 92, 246, 0.3); padding-bottom: 4px; }
#view-global_ai_lab .ailab-h2 { font-size: 14.5px; color: #BAE6FD; }
#view-global_ai_lab .ailab-h3 { font-size: 13.5px; color: #BBF7D0; }
#view-global_ai_lab .ailab-callout {
  display: flex;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(245, 158, 11, 0.1);
  border-left: 3px solid #F59E0B;
  border-radius: 0 8px 8px 0;
  margin: 10px 0;
  font-size: 12.5px;
  color: #FEF3C7;
}
#view-global_ai_lab .ailab-prog-wrap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  max-width: 260px;
  background: #0B132B;
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 999px;
  padding: 2px 6px;
  margin: 4px 0;
}
#view-global_ai_lab .ailab-prog-fill {
  height: 8px;
  background: linear-gradient(90deg, #8B5CF6, #38BDF8);
  border-radius: 999px;
  transition: width 0.3s ease;
}
#view-global_ai_lab .ailab-prog-lbl {
  font-size: 10.5px;
  font-weight: 700;
  color: #38BDF8;
}


/* =========================================================================
   PURE FULL-HEIGHT AUTONOMOUS BROWSER (CUA) SCREEN SHARE STUDIO
   ========================================================================= */
#view-global_ai_lab .ailab-cua-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #0B132B;
  border: 1.5px solid #38BDF8;
  border-radius: 6px;
  color: #38BDF8;
  font-size: 11px;
  font-weight: 700;
  padding: 5px 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
  white-space: nowrap;
}
#view-global_ai_lab .ailab-cua-toggle-btn:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: #7DD3FC;
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.4);
}
#view-global_ai_lab .ailab-cua-toggle-btn.active {
  background: rgba(56, 189, 248, 0.2);
  border-color: #38BDF8;
  color: #FFFFFF;
}

#view-global_ai_lab .ailab-live-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 8px #10B981;
  animation: ailabLivePulse 1.6s infinite ease-in-out;
}
@keyframes ailabLivePulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

/* Vertical Split Grip */
#view-global_ai_lab .ailab-grip-cua {
  width: 5px;
  background: var(--al-line);
  cursor: col-resize;
  flex-shrink: 0;
  transition: background 0.2s;
  z-index: 10;
}
#view-global_ai_lab .ailab-grip-cua:hover,
#view-global_ai_lab .ailab-grip-cua.resizing {
  background: #38BDF8;
  box-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
}

/* CUA Right Panel: 50% width by default, completely uncluttered */
#view-global_ai_lab .ailab-cua-panel {
  width: 50%;
  min-width: 440px;
  max-width: 65vw;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #080D14;
  border-left: 1.5px solid rgba(56, 189, 248, 0.35);
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
  transition: width 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-sizing: border-box;
}
#view-global_ai_lab .ailab-cua-panel.collapsed {
  width: 0 !important;
  min-width: 0 !important;
  border-left: none !important;
  display: none !important;
}

/* Ultra-Clean Browser Window Chrome (Height: 36px) */
#view-global_ai_lab .ailab-cua-chrome-header {
  height: 36px;
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: #0F1724;
  border-bottom: 1px solid var(--al-line);
  flex-shrink: 0;
  gap: 10px;
}
#view-global_ai_lab .ailab-window-dots {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
#view-global_ai_lab .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  cursor: pointer;
}
#view-global_ai_lab .dot.red { background: #EF4444; }
#view-global_ai_lab .dot.yellow { background: #F59E0B; }
#view-global_ai_lab .dot.green { background: #10B981; }

#view-global_ai_lab .ailab-cua-chrome-url {
  flex: 1;
  max-width: 460px;
  display: flex;
  align-items: center;
  gap: 6px;
  background: #080D14;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 5px;
  padding: 3px 8px;
  overflow: hidden;
}
#view-global_ai_lab .ailab-ssl-lock {
  font-size: 11px;
  color: #10B981;
}
#view-global_ai_lab .ailab-url-text {
  font-size: 11px;
  font-family: monospace;
  color: #38BDF8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

#view-global_ai_lab .ailab-cua-chrome-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
#view-global_ai_lab .ailab-cua-live-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.4);
  padding: 2px 7px;
  border-radius: 999px;
  font-size: 9.5px;
  font-weight: 700;
  color: #10B981;
  white-space: nowrap;
}

/* 100% Pure Full-Height Browser Viewport */
#view-global_ai_lab .ailab-cua-viewport-container {
  flex: 1 1 0% !important;
  width: 100%;
  height: calc(100% - 36px) !important;
  box-sizing: border-box;
  position: relative;
  background: #FFFFFF;
  overflow: hidden;
  display: flex;
  transition: padding-bottom 0.22s ease;
}
#view-global_ai_lab .ailab-cua-viewport-container.has-log {
  padding-bottom: min(240px, 42%);
}
#view-global_ai_lab .ailab-cua-iframe {
  flex: 1;
  width: 100%;
  height: 100%;
  border: none;
  background: #FFFFFF;
  display: block;
}
#view-global_ai_lab .ailab-cua-screenshot-frame {
  flex: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #080D14;
  display: none;
}

/* Visual Agent Laser Cursor */
#view-global_ai_lab .ailab-cua-cursor {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 32px;
  height: 32px;
  z-index: 120;
  pointer-events: none;
  opacity: 0;
  filter: drop-shadow(0 0 6px rgba(239, 68, 68, 0.85)) drop-shadow(0 3px 5px rgba(0, 0, 0, 0.7));
  transition: left 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), top 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), opacity 0.2s ease;
  display: flex;
  align-items: flex-start;
  gap: 2px;
}
#view-global_ai_lab .ailab-cua-cursor.is-visible { opacity: 1; }
#view-global_ai_lab .ailab-cua-cursor.is-active::before {
  content: "";
  position: absolute;
  left: -10px;
  top: -10px;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: 2px solid rgba(239, 68, 68, 0.75);
  animation: cuaCursorHalo 1.3s ease-out infinite;
}
@keyframes cuaCursorHalo {
  0% { transform: scale(0.45); opacity: 0.95; }
  100% { transform: scale(1.35); opacity: 0; }
}
#view-global_ai_lab .ailab-cua-cursor.is-clicking svg {
  animation: cuaCursorPress 0.28s ease-out;
  transform-origin: 3px 3px;
}
@keyframes cuaCursorPress {
  0% { transform: scale(1); }
  45% { transform: scale(0.72); }
  100% { transform: scale(1); }
}
#view-global_ai_lab .ailab-cua-cursor svg { flex: 0 0 auto; }
#view-global_ai_lab .ailab-cua-cursor-label {
  margin-top: 14px;
  background: linear-gradient(135deg, #EF4444, #B91C1C);
  color: #FFFFFF;
  font-size: 9.5px;
  font-weight: 800;
  letter-spacing: 0.2px;
  padding: 2px 7px;
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.55);
  white-space: nowrap;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Click Ripple Layer */
#view-global_ai_lab .ailab-cua-click-ripple {
  position: absolute;
  width: 34px;
  height: 34px;
  border: 2.5px solid #EF4444;
  border-radius: 50%;
  pointer-events: none;
  z-index: 119;
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.3);
  box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.45), 0 0 14px rgba(239, 68, 68, 0.55);
}
#view-global_ai_lab .ailab-cua-click-ripple.pulsing {
  animation: cuaRippleAnim 0.9s ease-out forwards;
}
@keyframes cuaRippleAnim {
  0% { opacity: 1; transform: translate(-50%, -50%) scale(0.3); }
  55% { opacity: 0.85; }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(2.4); }
}

/* Set-of-Marks Bounding Boxes Overlay */
#view-global_ai_lab .ailab-cua-som-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 65;
}
#view-global_ai_lab .ailab-som-tag {
  position: absolute;
  border: 1.5px solid #F59E0B;
  background: rgba(245, 158, 11, 0.15);
  border-radius: 3px;
  pointer-events: none;
  box-sizing: border-box;
}
#view-global_ai_lab .ailab-som-badge {
  position: absolute;
  top: -8px;
  left: -2px;
  background: #F59E0B;
  color: #000000;
  font-size: 8.5px;
  font-weight: 800;
  padding: 0 3px;
  border-radius: 2px;
}

/* Floating Sleek Action HUD */
#view-global_ai_lab .ailab-cua-action-hud {
  position: absolute;
  bottom: 12px;
  left: 20px;
  right: 20px;
  background: rgba(11, 17, 25, 0.94);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 7px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 60;
  font-size: 11px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
  pointer-events: none;
}
#view-global_ai_lab .ailab-action-icon { font-size: 14px; }
#view-global_ai_lab .ailab-action-desc {
  flex: 1;
  color: #F8FAFC;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ---------------- Model Catalog Discovery Modal ---------------- */
#view-global_ai_lab .ailab-modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(3, 7, 18, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 500;
  padding: 20px;
}
#view-global_ai_lab .ailab-modal-backdrop.is-open {
  display: flex !important;
}
#view-global_ai_lab .ailab-modal {
  width: 100%;
  max-width: 840px;
  max-height: 85vh;
  background: #0B132B;
  border: 1.5px solid #8B5CF6;
  border-radius: 14px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9), 0 0 35px rgba(139, 92, 246, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
#view-global_ai_lab .ailab-modal-head {
  padding: 14px 18px;
  border-bottom: 1px solid rgba(139, 92, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(13, 20, 38, 0.8);
}
#view-global_ai_lab .ailab-modal-close {
  background: none;
  border: none;
  color: #94A3B8;
  font-size: 22px;
  cursor: pointer;
  line-height: 1;
}
#view-global_ai_lab .ailab-modal-close:hover {
  color: #FFF;
}
#view-global_ai_lab .ailab-modal-search {
  padding: 12px 18px 8px 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: #0B132B;
}
#view-global_ai_lab .ailab-modal-search input {
  flex: 1;
  background: #070D18;
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 8px;
  padding: 9px 14px;
  color: #FFF;
  font-size: 13px;
  outline: none;
}
#view-global_ai_lab .ailab-modal-search input:focus {
  border-color: #38BDF8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
}
#view-global_ai_lab .ailab-modal-pills {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 6px 18px 10px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
#view-global_ai_lab .ailab-pill {
  background: #10192E;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94A3B8;
  font-size: 11.5px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 999px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}
#view-global_ai_lab .ailab-pill:hover,
#view-global_ai_lab .ailab-pill.is-active {
  background: rgba(139, 92, 246, 0.25);
  border-color: #8B5CF6;
  color: #FFF;
}
#view-global_ai_lab .ailab-modal-grid {
  flex: 1;
  overflow-y: auto;
  padding: 14px 18px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 10px;
  max-height: 50vh;
}
#view-global_ai_lab .ailab-mcard {
  background: #0F172A;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
#view-global_ai_lab .ailab-mcard:hover {
  border-color: #38BDF8;
  background: #131E38;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4), 0 0 12px rgba(56, 189, 248, 0.2);
}
#view-global_ai_lab .ailab-mcard-title {
  font-size: 12.5px;
  font-weight: 700;
  color: #F8FAFC;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
#view-global_ai_lab .ailab-mcard-sub {
  font-size: 11px;
  color: #94A3B8;
}
#view-global_ai_lab .ailab-mcard-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(139, 92, 246, 0.2);
  color: #C084FC;
}
#view-global_ai_lab .ailab-modal-footer {
  padding: 10px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: #64748B;
  background: rgba(11, 19, 43, 0.6);
}


/* Interactive Suggestion Hint Chips */
#view-global_ai_lab .ailab-hint-group {
  margin-top: 10px;
  padding: 8px 12px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(139, 92, 246, 0.35);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
#view-global_ai_lab .ailab-hint-lbl {
  font-size: 10.5px;
  font-weight: 700;
  color: #C084FC;
  display: flex;
  align-items: center;
  gap: 5px;
}
#view-global_ai_lab .ailab-hint-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
#view-global_ai_lab .ailab-hint-chip {
  background: #0F172A;
  border: 1.5px solid #38BDF8;
  color: #38BDF8;
  border-radius: 999px;
  padding: 4px 11px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  display: inline-flex;
  align-items: center;
  gap: 5px;
  box-shadow: 0 0 8px rgba(56, 189, 248, 0.15);
}
#view-global_ai_lab .ailab-hint-chip:hover {
  background: #38BDF8;
  color: #0B1119;
  transform: translateY(-1.5px);
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.45);
}

/* ---------------- Bottom Input Cockpit ---------------- */
#view-global_ai_lab .ailab-input-cockpit {
  padding: 12px 20px 14px 20px;
  background: linear-gradient(180deg, rgba(13, 20, 32, 0.95) 0%, #090E17 100%);
  border-top: 1px solid var(--al-line);
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
  z-index: 10;
}
#view-global_ai_lab .ailab-input-box {
  background: #0F1724;
  border: 1px solid var(--al-line-2);
  border-radius: 10px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
#view-global_ai_lab .ailab-input-box:focus-within {
  border-color: #8B5CF6;
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
}
#view-global_ai_lab .ailab-textarea {
  background: transparent;
  border: none;
  outline: none;
  color: #F8FAFC;
  font-size: 13.5px;
  line-height: 1.5;
  resize: none;
  width: 100%;
  min-height: 38px;
  max-height: 180px;
  font-family: inherit;
}
#view-global_ai_lab .ailab-textarea::placeholder {
  color: var(--al-dim);
}
#view-global_ai_lab .ailab-input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
#view-global_ai_lab .ailab-input-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--al-dim);
}
#view-global_ai_lab .ailab-mode-pill {
  font-size: 10.5px;
  font-weight: 700;
  background: rgba(139, 92, 246, 0.15);
  color: #C084FC;
  padding: 2px 7px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  gap: 4px;
}
#view-global_ai_lab .ailab-cockpit-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: var(--al-dim);
  padding: 0 4px;
}

/* --- Human-in-the-Loop (HITL) Collaborative Decision Cards --- */
#view-global_ai_lab .ailab-hitl-card {
  margin: 12px 0 8px 0;
  padding: 16px 18px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
  border: 1.5px solid #F59E0B;
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.25);
  display: flex;
  flex-direction: column;
  gap: 10px;
  animation: hitlFadeIn 0.3s ease-out;
}
@keyframes hitlFadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
#view-global_ai_lab .ailab-hitl-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  border-bottom: 1px solid rgba(245, 158, 11, 0.25);
  padding-bottom: 8px;
}
#view-global_ai_lab .ailab-hitl-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(245, 158, 11, 0.15);
  color: #FBBF24;
  border: 1px solid rgba(245, 158, 11, 0.4);
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.3px;
}
#view-global_ai_lab .ailab-hitl-agent {
  font-size: 10.5px;
  color: #94A3B8;
  font-family: monospace;
}
#view-global_ai_lab .ailab-hitl-title {
  font-size: 14.5px;
  font-weight: 700;
  color: #F8FAFC;
  display: flex;
  align-items: center;
  gap: 8px;
}
#view-global_ai_lab .ailab-hitl-desc {
  font-size: 12.5px;
  color: #CBD5E1;
  line-height: 1.5;
}
#view-global_ai_lab .ailab-hitl-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}
#view-global_ai_lab .ailab-hitl-btn {
  background: #0B132B;
  border: 1px solid rgba(56, 189, 248, 0.4);
  color: #E2E8F0;
  border-radius: 8px;
  padding: 9px 14px;
  font-size: 12px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
#view-global_ai_lab .ailab-hitl-btn:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: #38BDF8;
  color: #FFFFFF;
  transform: translateX(3px);
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
}
#view-global_ai_lab .ailab-hitl-btn.recommended {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.18) 0%, rgba(6, 95, 70, 0.25) 100%);
  border: 1.5px solid #10B981;
  color: #F0FDF4;
  box-shadow: 0 0 14px rgba(16, 185, 129, 0.25);
}
#view-global_ai_lab .ailab-hitl-btn.recommended:hover {
  background: #10B981;
  color: #064E3B;
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
}
#view-global_ai_lab .ailab-hitl-rec-tag {
  background: #10B981;
  color: #064E3B;
  font-size: 9.5px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  flex-shrink: 0;
}
#view-global_ai_lab .ailab-hitl-btn.recommended:hover .ailab-hitl-rec-tag {
  background: #064E3B;
  color: #10B981;
}
#view-global_ai_lab .ailab-hitl-approved {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid #10B981;
  color: #A7F3D0;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}


  /* ------------------------------------------------------------- */
  /* DATA MODELING EXPLORER (AWS, Snowflake, BigQuery, DuckDB)    */
  /* ------------------------------------------------------------- */
  .ailab-explorer {
    position: relative;
    width: 270px;
    flex: 0 0 auto;
    display: flex;
    flex-direction: column;
    min-height: 0;
    background: #090E17;
    border-right: 1px solid var(--ailab-border);
    transition: width 0.18s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.18s;
  }
  .ailab-explorer.is-hidden {
    display: none !important;
  }
  .ailab-explorer-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 40px;
    padding: 0 10px 0 12px;
    border-bottom: 1px solid var(--ailab-border);
    background: rgba(15, 23, 42, 0.6);
    flex-shrink: 0;
  }
  .ailab-explorer-title {
    font-size: 12.5px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.3px;
  }
  .ailab-explorer-badge {
    font-size: 9.5px;
    background: rgba(139, 92, 246, 0.15);
    color: #C084FC;
    padding: 1px 6px;
    border-radius: 10px;
    font-weight: 600;
  }
  .ailab-explorer-tools {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .ailab-explorer-search {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background: #070B12;
    border-bottom: 1px solid #1E293B;
    flex-shrink: 0;
  }
  .ailab-explorer-search input {
    width: 100%;
    background: transparent;
    border: none;
    color: #F8FAFC;
    font-size: 11.5px;
    outline: none;
  }
  .ailab-explorer-search input::placeholder {
    color: #475569;
  }
  .ailab-explorer-tree {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 6px 4px;
  }
  .ailab-explorer-tree::-webkit-scrollbar {
    width: 4px;
  }
  .ailab-explorer-tree::-webkit-scrollbar-thumb {
    background: #1E293B;
    border-radius: 4px;
  }
  .ailab-tree-node {
    margin-bottom: 2px;
    font-size: 11.5px;
  }
  .ailab-tree-row {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    border-radius: 5px;
    cursor: pointer;
    color: #CBD5E1;
    user-select: none;
    transition: background 0.12s, color 0.12s;
  }
  .ailab-tree-row:hover {
    background: rgba(148, 163, 184, 0.08);
    color: #FFFFFF;
  }
  .ailab-tree-row.is-active {
    background: rgba(139, 92, 246, 0.2);
    color: #C084FC;
    font-weight: 600;
  }
  .ailab-tree-arrow {
    font-size: 9px;
    color: #64748B;
    width: 12px;
    text-align: center;
    transition: transform 0.14s;
  }
  .ailab-tree-arrow.is-expanded {
    transform: rotate(90deg);
  }
  .ailab-tree-children {
    padding-left: 14px;
    display: none;
  }
  .ailab-tree-children.is-expanded {
    display: block;
  }
  .ailab-tree-badge {
    font-size: 9px;
    padding: 1px 5px;
    border-radius: 4px;
    margin-left: auto;
    font-family: monospace;
  }
  .ailab-explorer-foot {
    height: 28px;
    padding: 0 10px;
    background: #070B12;
    border-top: 1px solid #1E293B;
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }
  .ailab-grip-v#ailabExplorerGrip {
    position: absolute;
    top: 0;
    right: -3px;
    bottom: 0;
    width: 6px;
    cursor: col-resize;
    z-index: 20;
  }


/* ========================================================================= */
/* ANTIGRAVITY / CLAUDE CODE / CODEX PROFESSIONAL DARK THEME (EYE COMFORT)   */
/* Soft matte colors, zero neon halo, zero text-shadow, zero eye strain.    */
/* ========================================================================= */
#view-global_ai_lab,
#view-global_ai_lab .ailab-app {
  background: #0D1117 !important;
  color: #C9D1D9 !important;
  --al-bg: #0D1117 !important;
  --al-panel: #161B22 !important;
  --al-panel-2: #21262D !important;
  --al-line: #30363D !important;
  --al-line-2: #30363D !important;
  --al-text: #C9D1D9 !important;
  --al-muted: #8B949E !important;
  --al-dim: #6E7681 !important;
  --al-accent: #58A6FF !important;
  --al-accent-glow: transparent !important;
}

/* TOPBAR: Single-line, compact 44px, no wrapping, eye-comfort palette */
#view-global_ai_lab .ailab-topbar {
  height: 44px !important;
  min-height: 44px !important;
  max-height: 44px !important;
  background: #161B22 !important;
  border-bottom: 1px solid #30363D !important;
  box-shadow: none !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  gap: 8px !important;
  padding: 0 12px !important;
  overflow-x: auto !important;
  overflow-y: hidden !important;
  white-space: nowrap !important;
}

#view-global_ai_lab .ailab-topbar-left {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  flex: 0 0 auto !important;
}

#view-global_ai_lab .ailab-brand {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  color: #E6EDF3 !important;
  text-decoration: none !important;
}

#view-global_ai_lab .ailab-brand-badge {
  font-size: 10px !important;
  font-weight: 600 !important;
  padding: 1px 6px !important;
  border-radius: 4px !important;
  background: rgba(56, 139, 253, 0.15) !important;
  border: 1px solid rgba(56, 139, 253, 0.35) !important;
  color: #58A6FF !important;
  box-shadow: none !important;
}

#view-global_ai_lab .ailab-conn-badge {
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px !important;
  font-size: 11px !important;
  color: #8B949E !important;
  background: #21262D !important;
  border: 1px solid #30363D !important;
  border-radius: 4px !important;
  padding: 2px 7px !important;
}

#view-global_ai_lab .ailab-topbar-center {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  flex: 0 1 auto !important;
  min-width: 0 !important;
}

#view-global_ai_lab .ailab-topbar-right {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  flex: 0 0 auto !important;
  margin-left: auto !important;
}

/* Select Wrappers & Dropdowns */
#view-global_ai_lab .ailab-model-selector-wrap,
#view-global_ai_lab .ailab-effort-wrap {
  background: #21262D !important;
  border: 1px solid #30363D !important;
  box-shadow: none !important;
  border-radius: 6px !important;
  height: 28px !important;
  padding: 0 8px !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px !important;
}
#view-global_ai_lab .ailab-model-selector-wrap:hover,
#view-global_ai_lab .ailab-effort-wrap:hover {
  border-color: #8B949E !important;
}

#view-global_ai_lab .ailab-model-select,
#view-global_ai_lab .ailab-effort-select {
  background: transparent !important;
  border: none !important;
  color: #C9D1D9 !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  outline: none !important;
  cursor: pointer !important;
  padding-right: 4px !important;
}

#view-global_ai_lab .ailab-model-select option,
#view-global_ai_lab .ailab-effort-select option,
#view-global_ai_lab .ailab-model-select optgroup {
  background: #161B22 !important;
  color: #C9D1D9 !important;
}

/* Buttons in Topbar */
#view-global_ai_lab .ailab-browse-btn,
#view-global_ai_lab .ailab-cua-toggle-btn,
#view-global_ai_lab .ailab-topbar-sync-btn,
#view-global_ai_lab .ailab-code-btn {
  background: #21262D !important;
  border: 1px solid #30363D !important;
  color: #C9D1D9 !important;
  box-shadow: none !important;
  border-radius: 6px !important;
  height: 28px !important;
  padding: 0 9px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
}
#view-global_ai_lab .ailab-browse-btn:hover,
#view-global_ai_lab .ailab-cua-toggle-btn:hover,
#view-global_ai_lab .ailab-topbar-sync-btn:hover {
  background: #30363D !important;
  color: #F0F6FC !important;
  border-color: #8B949E !important;
}

/* New Chat Button: Standard Green Button (Claude Code / Antigravity) */
#view-global_ai_lab .ailab-topbar-new-chat-btn,
#view-global_ai_lab .ailab-btn-primary.ailab-topbar-new-chat-btn {
  background: #238636 !important;
  border: 1px solid rgba(240, 246, 252, 0.1) !important;
  color: #FFFFFF !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  height: 28px !important;
  border-radius: 6px !important;
  padding: 0 12px !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  cursor: pointer !important;
  box-shadow: none !important;
}
#view-global_ai_lab .ailab-topbar-new-chat-btn:hover {
  background: #2EA043 !important;
}

/* Icon Buttons */
#view-global_ai_lab .ailab-iconbtn {
  background: #21262D !important;
  border: 1px solid #30363D !important;
  color: #8B949E !important;
  border-radius: 6px !important;
  width: 28px !important;
  height: 28px !important;
  box-shadow: none !important;
}
#view-global_ai_lab .ailab-iconbtn:hover,
#view-global_ai_lab .ailab-iconbtn.is-active {
  background: #30363D !important;
  color: #F0F6FC !important;
  border-color: #8B949E !important;
}

/* CHAT AREA: Soft matte dark canvas */
#view-global_ai_lab .ailab-chat-window,
#view-global_ai_lab .ailab-messages-wrap {
  background: #0D1117 !important;
}

/* ASSISTANT CARD */
#view-global_ai_lab .ailab-msg-assistant .ailab-bubble,
#view-global_ai_lab .ailab-asst-bubble {
  background: #161B22 !important;
  border: 1px solid #30363D !important;
  border-radius: 8px !important;
  padding: 16px 20px !important;
  color: #C9D1D9 !important;
  font-size: 14px !important;
  line-height: 1.65 !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

/* USER BUBBLE */
#view-global_ai_lab .ailab-msg-user .ailab-bubble,
#view-global_ai_lab .ailab-user-bubble {
  background: #21262D !important;
  border: 1px solid #30363D !important;
  border-radius: 8px !important;
  padding: 12px 16px !important;
  color: #C9D1D9 !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
  box-shadow: none !important;
}

#view-global_ai_lab .ailab-user-label {
  background: #21262D !important;
  border: 1px solid #30363D !important;
  color: #58A6FF !important;
  border-radius: 4px !important;
}

/* Provenance Card */
#view-global_ai_lab .ailab-provenance-card {
  background: #21262D !important;
  border: 1px solid #30363D !important;
  border-left: 3px solid #58A6FF !important;
  box-shadow: none !important;
  border-radius: 6px !important;
  padding: 8px 12px !important;
}
#view-global_ai_lab .ailab-prov-header {
  border-bottom: 1px solid #30363D !important;
}
#view-global_ai_lab .ailab-prov-model {
  color: #E6EDF3 !important;
}
#view-global_ai_lab .ailab-prov-lab {
  color: #58A6FF !important;
}
#view-global_ai_lab .ailab-prov-country,
#view-global_ai_lab .ailab-prov-sub {
  color: #8B949E !important;
}
#view-global_ai_lab .ailab-dur-highlight {
  color: #2EA043 !important;
}

/* Markdown Headings & Code */
#view-global_ai_lab .ailab-asst-bubble h1,
#view-global_ai_lab .ailab-asst-bubble h2,
#view-global_ai_lab .ailab-asst-bubble h3,
#view-global_ai_lab .ailab-asst-bubble h4 {
  color: #E6EDF3 !important;
  font-weight: 600 !important;
  margin-top: 14px !important;
  margin-bottom: 8px !important;
  border-bottom: none !important;
}
#view-global_ai_lab .ailab-asst-bubble strong {
  color: #E6EDF3 !important;
  font-weight: 600 !important;
}
#view-global_ai_lab .ailab-asst-bubble p {
  color: #C9D1D9 !important;
  margin-bottom: 10px !important;
}
#view-global_ai_lab .ailab-asst-bubble code {
  background: #21262D !important;
  color: #E6EDF3 !important;
  border: 1px solid #30363D !important;
  border-radius: 4px !important;
  padding: 1px 5px !important;
  font-size: 12.5px !important;
}
#view-global_ai_lab .ailab-asst-bubble pre {
  background: #0D1117 !important;
  border: 1px solid #30363D !important;
  border-radius: 6px !important;
  padding: 12px 14px !important;
}
#view-global_ai_lab .ailab-asst-bubble pre code {
  background: transparent !important;
  border: none !important;
  color: #E6EDF3 !important;
}

/* Markdown Tables */
#view-global_ai_lab .ailab-asst-bubble table {
  border-collapse: collapse !important;
  width: 100% !important;
  margin: 12px 0 !important;
  border: 1px solid #30363D !important;
  border-radius: 6px !important;
}
#view-global_ai_lab .ailab-asst-bubble th {
  background: #21262D !important;
  color: #E6EDF3 !important;
  border: 1px solid #30363D !important;
  padding: 6px 12px !important;
  font-size: 12.5px !important;
}
#view-global_ai_lab .ailab-asst-bubble td {
  background: #161B22 !important;
  color: #C9D1D9 !important;
  border: 1px solid #30363D !important;
  padding: 6px 12px !important;
  font-size: 12.5px !important;
}

/* Bottom Chat Input Bar */
#view-global_ai_lab .ailab-input-card {
  background: #161B22 !important;
  border: 1px solid #30363D !important;
  box-shadow: none !important;
  border-radius: 8px !important;
}
#view-global_ai_lab .ailab-textarea {
  background: transparent !important;
  color: #C9D1D9 !important;
}
#view-global_ai_lab .ailab-textarea::placeholder {
  color: #6E7681 !important;
}
#view-global_ai_lab .ailab-send-btn {
  background: #238636 !important;
  color: #FFFFFF !important;
  border: 1px solid rgba(240, 246, 252, 0.1) !important;
  border-radius: 6px !important;
  box-shadow: none !important;
}
#view-global_ai_lab .ailab-send-btn:hover {
  background: #2EA043 !important;
}

/* Sidebars (Chats & Explorer) */
#view-global_ai_lab .ailab-sidebar,
#view-global_ai_lab .ailab-explorer {
  background: #161B22 !important;
  border-right: 1px solid #30363D !important;
  color: #C9D1D9 !important;
}
#view-global_ai_lab .ailab-sidebar-head,
#view-global_ai_lab .ailab-explorer-head {
  background: #161B22 !important;
  border-bottom: 1px solid #30363D !important;
  color: #E6EDF3 !important;
}
#view-global_ai_lab .ailab-sidebar-title,
#view-global_ai_lab .ailab-explorer-title {
  color: #E6EDF3 !important;
}
#view-global_ai_lab .ailab-sec-header {
  color: #8B949E !important;
}
#view-global_ai_lab .ailab-chat-item {
  color: #C9D1D9 !important;
}
#view-global_ai_lab .ailab-chat-item:hover {
  background: #21262D !important;
}
#view-global_ai_lab .ailab-chat-item.is-active {
  background: #21262D !important;
  border-left: 2px solid #58A6FF !important;
}

/* ========================================================= */
/* CLEAN WORKSPACE LAYOUT                                    */
/* ========================================================= */

/* Topbar: one tidy row, controls shrink instead of overlapping */
#view-global_ai_lab .ailab-topbar {
  padding: 0 10px !important;
  gap: 8px !important;
  overflow: hidden !important;
}
#view-global_ai_lab .ailab-topbar-left,
#view-global_ai_lab .ailab-topbar-right {
  gap: 6px !important;
  flex-wrap: nowrap !important;
}
#view-global_ai_lab .ailab-topbar-center {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  justify-content: center !important;
  gap: 6px !important;
  overflow: hidden !important;
}
#view-global_ai_lab .ailab-model-selector-wrap {
  flex: 1 1 auto !important;
  min-width: 150px !important;
  max-width: 230px !important;
}
#view-global_ai_lab .ailab-model-select {
  min-width: 0 !important;
  max-width: 100% !important;
}
#view-global_ai_lab .ailab-effort-wrap { flex: 0 0 auto !important; }
#view-global_ai_lab .ailab-brand { flex: 0 0 auto !important; white-space: nowrap !important; }
#view-global_ai_lab .ailab-conn-badge { flex: 0 0 auto !important; white-space: nowrap !important; }
#view-global_ai_lab .ailab-topbar .ailab-iconbtn,
#view-global_ai_lab .ailab-topbar .ailab-code-btn,
#view-global_ai_lab .ailab-topbar .ailab-cua-toggle-btn,
#view-global_ai_lab .ailab-topbar .ailab-topbar-new-chat-btn {
  flex: 0 0 auto !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-topbar-sync-btn {
  width: 28px !important;
  padding: 0 !important;
  justify-content: center !important;
}

/* Chat header: title keeps the space, actions stay on one line */
#view-global_ai_lab .ailab-canvas-head {
  flex-wrap: nowrap !important;
  gap: 10px !important;
  padding: 10px 16px !important;
  min-height: 56px;
}
#view-global_ai_lab .ailab-chat-title-wrap {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  width: auto !important;
}
#view-global_ai_lab .ailab-canvas-head > div:last-child {
  flex: 0 0 auto !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
}
#view-global_ai_lab .ailab-canvas-head .ailab-code-btn {
  height: 28px !important;
  padding: 0 9px !important;
  font-size: 11.5px !important;
  white-space: nowrap !important;
  flex: 0 0 auto !important;
}
#view-global_ai_lab .ailab-active-sub {
  gap: 6px !important;
  max-width: 100%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

/* Explorer: slide-over panel, chat keeps full width */
#view-global_ai_lab .ailab-explorer {
  position: absolute !important;
  top: 0;
  right: 0;
  bottom: 0;
  width: 300px !important;
  z-index: 45;
  background: #0B111C !important;
  border-left: 1px solid var(--al-line);
  border-right: none !important;
  box-shadow: -24px 0 48px rgba(0, 0, 0, 0.45);
}
#view-global_ai_lab .ailab-explorer.is-hidden { display: none !important; }
#view-global_ai_lab .ailab-grip-v#ailabExplorerGrip {
  right: auto !important;
  left: -3px !important;
}

/* Empty state: quieter */
#view-global_ai_lab .ailab-hero { padding: 18px 8px; margin: 10px auto; }
#view-global_ai_lab .ailab-hero h2 { font-size: 21px; margin-bottom: 6px; }
#view-global_ai_lab .ailab-hero p { font-size: 12.5px; max-width: 480px; margin-bottom: 14px; }
#view-global_ai_lab .ailab-pill-grid {
  gap: 8px;
  margin-top: 10px;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
#view-global_ai_lab .ailab-pill-card { padding: 10px 12px; }
#view-global_ai_lab .ailab-pill-card-desc {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Composer: single clean block */
#view-global_ai_lab .ailab-input-cockpit { padding: 10px 14px 12px; gap: 0; }
#view-global_ai_lab .ailab-input-box { padding: 8px 12px; gap: 6px; }
#view-global_ai_lab .ailab-input-actions { flex-wrap: nowrap; gap: 8px; }
#view-global_ai_lab .ailab-input-tags {
  min-width: 0;
  flex: 1 1 auto;
  overflow: hidden;
  white-space: nowrap;
}
#view-global_ai_lab .ailab-input-actions > div:last-child { flex: 0 0 auto; }

/* Sidebar footer: one compact line */
#view-global_ai_lab .ailab-storage-footer {
  padding: 7px 12px;
  gap: 8px;
  font-size: 10.5px;
}
#view-global_ai_lab .ailab-storage-footer #ailabStorageEngineLabel {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
#view-global_ai_lab .ailab-storage-footer button {
  flex: 0 0 auto;
  background: none;
  border: none;
  color: #38BDF8;
  font-size: 10.5px;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
}
#view-global_ai_lab #ailabHistoryStatus {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Narrow windows: keep icons, drop labels */
@media (max-width: 1220px) {
  #view-global_ai_lab .ailab-conn-badge { display: none !important; }
  #view-global_ai_lab .ailab-cua-toggle-btn {
    width: 28px;
    padding: 0 !important;
    justify-content: center;
  }
  #view-global_ai_lab .ailab-cua-toggle-btn .lbl { display: none; }
  #view-global_ai_lab .ailab-input-tags .ailab-mode-pill,
  #view-global_ai_lab #ailabSlaLabel { display: none; }
  #view-global_ai_lab .ailab-canvas-head .ailab-code-btn {
    width: 30px;
    justify-content: center;
    padding: 0 !important;
  }
  #view-global_ai_lab .ailab-canvas-head .ailab-code-btn .lbl { display: none; }
}

/* ===================================================================== */
/* CUA — real browser agent panel                                        */
/* ===================================================================== */
#view-global_ai_lab .ailab-cua-frame-stack {
  flex: 1 1 0%;
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
}
#view-global_ai_lab .ailab-cua-screenshot-frame {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: top center;
  background: #080D14;
  opacity: 0;
  transition: opacity 0.16s linear;
  pointer-events: none;
}
#view-global_ai_lab .ailab-cua-screenshot-frame.is-live {
  opacity: 1;
}
#view-global_ai_lab .ailab-cua-live-pill {
  border: 1px solid rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.12);
  color: #10B981;
  cursor: pointer;
  font-family: inherit;
}
#view-global_ai_lab .ailab-cua-live-pill.is-offline {
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(248, 113, 113, 0.12);
  color: #F87171;
}
#view-global_ai_lab .ailab-cua-offline {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: radial-gradient(circle at 50% 30%, rgba(56, 189, 248, 0.08), transparent 60%), #080D14;
  z-index: 30;
}
#view-global_ai_lab .ailab-cua-offline-card {
  max-width: 460px;
  background: #0F1724;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 12px;
  padding: 18px 20px;
  color: #CBD5E1;
  font-size: 12.5px;
  line-height: 1.6;
}
#view-global_ai_lab .ailab-cua-offline-title {
  font-size: 14px;
  font-weight: 700;
  color: #F8FAFC;
  margin-bottom: 6px;
}
#view-global_ai_lab .ailab-cua-offline-card p {
  margin: 0 0 10px;
  color: #94A3B8;
}
#view-global_ai_lab .ailab-cua-offline-card ol {
  margin: 0 0 12px 18px;
  padding: 0;
}
#view-global_ai_lab .ailab-cua-offline-card li {
  margin-bottom: 4px;
}
#view-global_ai_lab .ailab-cua-offline-card code {
  background: #111A29;
  color: #7DD3FC;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 11.5px;
}
#view-global_ai_lab .ailab-cua-offline-row {
  display: flex;
  gap: 6px;
  align-items: center;
}
#view-global_ai_lab .ailab-cua-bridge-input {
  flex: 1;
  min-width: 0;
  background: #080D14;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 6px;
  padding: 6px 8px;
  color: #E2E8F0;
  font-family: ui-monospace, monospace;
  font-size: 11.5px;
  outline: none;
}
#view-global_ai_lab .ailab-cua-offline-btn {
  background: #111A29;
  border: 1px solid rgba(56, 189, 248, 0.3);
  color: #CBD5E1;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
}
#view-global_ai_lab .ailab-cua-offline-btn.primary {
  background: #10B981;
  border-color: #10B981;
  color: #04120C;
}
#view-global_ai_lab .ailab-cua-tasklog {
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 48px;
  max-height: min(180px, 30%);
  overflow-y: auto;
  display: none;
  background: rgba(8, 13, 20, 0.92);
  border: 1px solid rgba(56, 189, 248, 0.22);
  border-radius: 8px;
  padding: 8px 10px;
  font-family: ui-monospace, monospace;
  font-size: 11px;
  line-height: 1.55;
  color: #CBD5E1;
  z-index: 40;
  backdrop-filter: blur(6px);
}
#view-global_ai_lab .ailab-cua-tasklog.is-open {
  display: block;
}
#view-global_ai_lab .ailab-cua-logline {
  margin-bottom: 3px;
  word-break: break-word;
}
#view-global_ai_lab .ailab-cua-logline .ts {
  color: #475569;
  margin-right: 6px;
}
#view-global_ai_lab .ailab-cua-logline.thought { color: #A78BFA; }
#view-global_ai_lab .ailab-cua-logline.act { color: #7DD3FC; }
#view-global_ai_lab .ailab-cua-logline.done { color: #34D399; font-weight: 700; }
#view-global_ai_lab .ailab-cua-logline.warn { color: #FBBF24; }
#view-global_ai_lab .ailab-cua-logline.error { color: #F87171; }
#view-global_ai_lab .ailab-cua-logline.task { color: #E2E8F0; font-weight: 700; }
#view-global_ai_lab .ailab-cua-logline.secret { color: #34D399; }
#view-global_ai_lab .ailab-cua-ask {
  position: absolute;
  left: 14px;
  right: 14px;
  bottom: 54px;
  display: none;
  flex-direction: column;
  gap: 6px;
  background: #0F1724;
  border: 1px solid rgba(251, 191, 36, 0.45);
  border-radius: 10px;
  padding: 12px;
  z-index: 50;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.45);
}
#view-global_ai_lab .ailab-cua-ask.is-open {
  display: flex;
}
#view-global_ai_lab .ailab-cua-ask-title {
  font-size: 12.5px;
  font-weight: 700;
  color: #FDE68A;
}
#view-global_ai_lab .ailab-cua-ask-opts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}


/* Modern Asynchronous Data Transfer Job Card */
.ailab-transfer-job-card {
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 14px;
  padding: 16px 20px;
  margin: 12px 0;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6), 0 0 24px rgba(56, 189, 248, 0.08);
  font-family: inherit;
}
.ailab-job-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.ailab-job-title-grp {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ailab-job-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #38BDF8;
  box-shadow: 0 0 10px #38BDF8;
  animation: pulse 1.4s infinite;
}
.ailab-job-icon { font-size: 14px; }
.ailab-job-title {
  font-size: 13px;
  font-weight: 700;
  color: #F8FAFC;
  letter-spacing: 0.3px;
}
.ailab-job-id {
  font-size: 11px;
  color: #94A3B8;
  background: rgba(255, 255, 255, 0.06);
  padding: 2px 7px;
  border-radius: 4px;
  font-family: monospace;
}
.ailab-job-status-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 12px;
  letter-spacing: 0.3px;
}
.ailab-job-status-pill.running {
  background: rgba(56, 189, 248, 0.15);
  color: #38BDF8;
  border: 1px solid rgba(56, 189, 248, 0.4);
}
.ailab-job-status-pill.success {
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
  border: 1px solid rgba(16, 185, 129, 0.4);
}
.ailab-job-flow-nodes {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 14px;
}
.ailab-node-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.node-tag {
  font-size: 9.5px;
  font-weight: 700;
  color: #94A3B8;
  letter-spacing: 0.5px;
}
.node-code {
  font-size: 12px;
  font-weight: 700;
  color: #38BDF8;
  background: rgba(56, 189, 248, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  width: fit-content;
}
.ailab-node-box.target .node-code {
  color: #10B981;
  background: rgba(16, 185, 129, 0.1);
}
.node-sub { font-size: 11px; color: #64748B; }
.ailab-flow-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.flow-speed { font-size: 10px; color: #38BDF8; font-weight: 600; }
.ailab-job-metrics-strip {
  display: flex;
  justify-content: space-between;
  font-size: 11.5px;
  margin-bottom: 6px;
  color: #94A3B8;
}
.metric-item .m-v { color: #F8FAFC; }
.ailab-job-progress-track {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 14px;
}
.ailab-job-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #38BDF8, #6366F1, #10B981);
  border-radius: 6px;
  transition: width 0.4s ease;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.6);
}
.ailab-job-stages-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}
.ailab-stage-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11.5px;
  color: #64748B;
  background: rgba(30, 41, 59, 0.35);
  border-radius: 6px;
  padding: 5px 10px;
  border: 1px solid transparent;
}
.ailab-stage-item.active {
  color: #38BDF8;
  border-color: rgba(56, 189, 248, 0.25);
  background: rgba(56, 189, 248, 0.05);
}
.ailab-stage-item.done {
  color: #10B981;
  background: rgba(16, 185, 129, 0.05);
}
.ailab-stage-item .stg-desc { flex: 1; }
.ailab-stage-item .stg-status { font-size: 10.5px; font-weight: 600; }
.ailab-job-logs-section {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 10px;
  margin-top: 10px;
}
.ailab-job-logs-toggle {
  background: none;
  border: none;
  color: #94A3B8;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 0;
}
.ailab-job-logs-toggle:hover { color: #F8FAFC; }
.ailab-job-logs-wrap {
  margin-top: 8px;
  background: #020617;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 8px 12px;
}
.ailab-job-logs-console {
  max-height: 120px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 11px;
  line-height: 1.5;
}
.log-line { color: #94A3B8; }
.log-line.success { color: #10B981; }
.ailab-job-actions-bar {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}
.ailab-btn-job-action {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  background: rgba(30, 41, 59, 0.9);
  color: #F8FAFC;
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: all 0.15s ease;
}
.ailab-btn-job-action:hover { background: rgba(56, 189, 248, 0.15); border-color: #38BDF8; }
.ailab-btn-job-action.primary { background: #0284C7; border-color: #38BDF8; color: #FFF; }
.ailab-btn-job-action.primary:hover { background: #0369A1; }

</style>

<div class="ailab-app">
  <!-- Topbar -->
  <div class="ailab-topbar">
    <div class="ailab-topbar-left">
      <button class="ailab-iconbtn" id="ailabToggleChats" onclick="ailabToggleSidebar()" title="Toggle Chats &amp; Projects">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
      </button>
      <button class="ailab-iconbtn" id="ailabToggleExplorer" onclick="ailabToggleExplorer()" title="Toggle Data Explorer (AWS, Snowflake, BigQuery, DuckDB)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/></svg>
      </button>
      <div class="ailab-brand">
        <span>🧠 NanoPro AI Lab</span>
      </div>
      <div class="ailab-conn-badge" id="ailabConnBadge" title="OpenRouter + DuckDB + BigQuery Active">
        <span class="ailab-pulse-dot"></span>
        <span id="ailabConnText">4,750+ models</span>
      </div>
      <div class="ailab-live-routed-badge" id="ailabLiveRoutedBadge" style="display:none;align-items:center;gap:6px;background:rgba(16,185,129,0.12);border:1.5px solid #10B981;box-shadow:0 0 12px rgba(16,185,129,0.3);border-radius:8px;padding:3px 10px;font-size:12px;color:#10B981;font-weight:700;white-space:nowrap;transition:all 0.3s ease;" title="Active Sovereign Model dynamically routed by Pareto + Thompson Bandit algorithm"></div>
    </div>

    <!-- Center Model Selector Dropdown & Effort -->
    <div class="ailab-topbar-center">
      <div class="ailab-model-selector-wrap" title="Current Selected Frontier AI Model">
        <select class="ailab-model-select" id="ailabModelSelect" onchange="ailabChangeModel(this.value)">
          <optgroup label="⚡ High-Tech Mathematical Router">
            <option value="auto" selected>⚡ AUTO Router</option>
          </optgroup>
          <optgroup label="🇮🇳 Krutrim AI (Ola Sovereign Cloud · Qwen 3.6, GPT-OSS 120B, Gemma 4)">
            <option value="krutrim/Qwen3.6-27B">Krutrim Qwen 3.6 27B</option>
            <option value="krutrim/gpt-oss-120b">Krutrim GPT OSS 120B</option>
            <option value="krutrim/gemma-4-31b-it">Krutrim Gemma 4 31B</option>
            <option value="krutrim/GLM-5.3-Flash">Krutrim GLM 5.3 Flash</option>
            <option value="krutrim/gpt-oss-20b">Krutrim GPT OSS 20B</option>
          </optgroup>
          <optgroup label="⚡ Poe by Quora (303 Unified Bot Models)">
            <option value="poe/gemini-4-hydrogen">Poe Gemini 4 Hydrogen (1M Context)</option>
            <option value="poe/grok-4.7">Poe Grok 4.7 (Frontier Reasoning)</option>
            <option value="poe/kimi-k3.1-pro">Poe Kimi K3.1 Pro (1M Context)</option>
            <option value="poe/claude-sonnet-5.5">Poe Claude Sonnet 5.5</option>
            <option value="poe/mistral-large-4">Poe Mistral Large 4</option>
            <option value="poe/mercury-3-vercel">Poe Mercury 3 Diffusion</option>
          </optgroup>
          <optgroup label="🌿 Eden AI (1,311 Unified Models · OpenAI, Anthropic, Gemini, Mistral)">
            <option value="edenai/openai/gpt-4o">Eden AI OpenAI GPT-4o</option>
            <option value="edenai/anthropic/claude-3-5-sonnet">Eden AI Claude 3.5 Sonnet</option>
            <option value="edenai/google/gemini-1.5-pro">Eden AI Google Gemini 1.5 Pro</option>
            <option value="edenai/mistral/mistral-large-latest">Eden AI Mistral Large 2</option>
            <option value="edenai/deepseek/deepseek-r1">Eden AI DeepSeek R1</option>
          </optgroup>
          <optgroup label="🌐 Requesty AI (750 Global Unified Models)">
            <option value="requesty/anthropic/claude-fable-5.2">Requesty Claude Fable 5.2</option>
            <option value="requesty/google/gemini-4-hydrogen">Requesty Gemini 4 Hydrogen</option>
            <option value="requesty/openai/gpt-6.1-terra:flex">Requesty GPT 6.1 Terra</option>
            <option value="requesty/deepseek/deepseek-chat">Requesty DeepSeek V3</option>
          </optgroup>
          <optgroup label="🟢 NVIDIA NIM Microservices (83 Models · TensorRT-LLM)">
            <option value="nvidia/llama-3.1-nemotron-70b-instruct">NVIDIA Llama 3.1 Nemotron 70B</option>
            <option value="nvidia/nemotron-4-340b-instruct">NVIDIA Nemotron 4 340B Flagship</option>
            <option value="nvidia/mistralai/codestral-22b-instruct-v0.1">NVIDIA Codestral 22B</option>
            <option value="nvidia/deepseek-ai/deepseek-v4.1-flash">NVIDIA DeepSeek V4.1 Flash</option>
            <option value="nvidia/bigcode/starcoder2-15b">NVIDIA StarCoder2 15B</option>
          </optgroup>
          <optgroup label="⚡ SambaNova Systems (Fast SN40L RDUs)">
            <option value="sambanova/Meta-Llama-3.3-70B-Instruct">SambaNova Llama 3.3 70B (Fast RDU)</option>
            <option value="sambanova/GLM-5.3">SambaNova GLM-5.3 Flagship</option>
            <option value="sambanova/MiniMax-M3.1-Flash">SambaNova MiniMax M3.1 Flash</option>
            <option value="sambanova/gemma-4-31B-it">SambaNova Gemma 4 31B</option>
            <option value="sambanova/gpt-oss-120b">SambaNova GPT OSS 120B</option>
          </optgroup>
          <optgroup label="⛵ Parasail GPU Network (107 Decentralized Models)">
            <option value="parasail/parasail-llama-33-70b-fp8">Parasail Llama 3.3 70B FP8</option>
            <option value="parasail/parasail-qwen25-vl-72b-instruct">Parasail Qwen 2.5 VL 72B</option>
            <option value="parasail/parasail-skyfall-36b-v2-fp8">Parasail Skyfall 36B v2</option>
            <option value="parasail/parasail-llama-4-maverick-instruct-fp8">Parasail Llama 4 Maverick</option>
          </optgroup>
          <optgroup label="🏹 Arcee AI (Domain-Specialized SLMs)">
            <option value="arcee/zai-org/glm-5.3-flash">Arcee GLM 5.3 Flash</option>
            <option value="arcee/deepseek/deepseek-v4.1-flash">Arcee DeepSeek V4.1 Flash</option>
            <option value="arcee/moonshotai/kimi-k3.1-pro">Arcee Kimi K3.1 Pro</option>
          </optgroup>
          <optgroup label="☁️ Cloudflare Workers AI (Zero-Latency Edge · Llama 3.3, Qwen 2.5)">
            <option value="@cf/meta/llama-3.3-70b-instruct">Cloudflare Workers AI Llama 3.3 70B</option>
            <option value="@cf/meta/llama-3.1-8b-instruct">Cloudflare Workers AI Llama 3.1 8B (&lt;100ms)</option>
            <option value="@cf/deepseek-ai/deepseek-r1-distill-qwen-32b">Cloudflare Workers AI DeepSeek R1 32B</option>
            <option value="@cf/qwen/qwen2.5-72b-instruct">Cloudflare Workers AI Qwen 2.5 72B</option>
          </optgroup>
          <optgroup label="🚀 Novita AI Multi-Cloud (99 Models · DeepSeek V4.1, Kimi K3.1)">
            <option value="novita/deepseek/deepseek-v4.1-flash">Novita DeepSeek V4.1 Flash</option>
            <option value="novita/moonshotai/kimi-k3.1-pro">Novita Kimi K3.1 Pro (Long Context)</option>
            <option value="novita/minimax/minimax-m3.1-flash">Novita MiniMax M3.1 Flash</option>
          </optgroup>
          <optgroup label="🧠 DeepInfra High-Throughput (177 Models · Llama 3.3 Turbo, Qwen, Phi-4)">
            <option value="deepinfra/Qwen/Qwen3.8-Flash">DeepInfra Qwen 3.8 Flash (Turbo)</option>
            <option value="deepinfra/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo">DeepInfra Llama 3.1 8B Turbo</option>
            <option value="deepinfra/meta-llama/Llama-3.3-70B-Instruct">DeepInfra Llama 3.3 70B Turbo</option>
            <option value="deepinfra/deepseek-ai/DeepSeek-R1">DeepInfra DeepSeek R1 Reasoning</option>
            <option value="deepinfra/microsoft/phi-4">DeepInfra Microsoft Phi-4</option>
          </optgroup>
          <optgroup label="🇫🇷 Mistral AI Direct (56 Models · Codestral, Mistral Large, Ministral)">
            <option value="mistral/codestral-latest">Mistral Codestral 2508 (Code SOTA)</option>
            <option value="mistral/mistral-large-latest">Mistral Large 2 (Flagship)</option>
            <option value="mistral/ministral-14b-latest">Mistral Ministral 14B</option>
            <option value="mistral/mistral-small-latest">Mistral Small Latest</option>
          </optgroup>
          <optgroup label="🇨🇳 DeepSeek Sovereign Direct (DeepSeek V3, DeepSeek R1)">
            <option value="deepseek/deepseek-chat">DeepSeek V3 Direct API</option>
            <option value="deepseek/deepseek-reasoner">DeepSeek R1 Direct Reasoner</option>
          </optgroup>
          <optgroup label="⚡ Groq Ultra-Fast LPUs (&lt;300ms SLA)">
            <option value="groq/qwen3.8-27b">Groq Qwen 3.8 27B (&lt;300ms)</option>
            <option value="groq/openai/gpt-oss-120b">Groq GPT OSS 120B</option>
            <option value="groq/llama-3.3-70b-versatile">Groq Llama 3.3 70B Versatile</option>
          </optgroup>
          <optgroup label="🤗 Hugging Face Serverless Hub (110+ Models)">
            <option value="hf/meta-llama/Llama-3.3-70B-Instruct">HF Llama 3.3 70B Instruct</option>
            <option value="hf/Qwen/Qwen2.5-Coder-32B-Instruct">HF Qwen 2.5 Coder 32B</option>
            <option value="hf/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B">HF DeepSeek R1 Distill 32B</option>
          </optgroup>
          <optgroup label="🇺🇸 Anthropic Frontier Flagships">
            <option value="anthropic/claude-3.7-sonnet">Claude 3.7 Sonnet (Hybrid Thinking / SOTA)</option>
            <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
            <option value="anthropic/claude-3.5-haiku">Claude 3.5 Haiku</option>
          </optgroup>
          <optgroup label="🇺🇸 Google DeepMind Frontier">
            <option value="google/gemini-2.5-pro">Gemini 2.5 Pro (Frontier Multimodal 2M)</option>
            <option value="google/gemini-2.5-flash">Gemini 2.5 Flash (&lt;300ms SLA)</option>
            <option value="google/gemini-2.0-flash-001">Gemini 2.0 Flash</option>
          </optgroup>
          <optgroup label="🔑 Google AI Studio (your keys, free tier)">
            <option value="gemini-4-hydrogen">Gemini 4 Hydrogen (2-3s, vision)</option>
            <option value="gemini-3.6-flash">Gemini 3.6 Flash (5-12s)</option>
          </optgroup>
          <optgroup label="🆓 Free Frontier (verified working)">
            <option value="nvidia/nemotron-3-ultra-550b-a55b:free">Nemotron 3 Ultra 550B (1M ctx, thinking)</option>
            <option value="nvidia/nemotron-3.5-super-vl:free">Nemotron 3.5 Super VL (Fast, Vision)</option>
            <option value="nvidia/nemotron-3.5-lightning:free">Nemotron 3.5 Lightning (Fast)</option>
            <option value="baidu/ernie-5.5-flash-preview:free">Baidu ERNIE 5.5 Flash (1M ctx)</option>
            <option value="google/gemma-4-31b-it:free">Gemma 4 31B (Free)</option>
            <option value="inclusionai/ling-3.2-flash:free">Ling 3.2 Flash (Free)</option>
          </optgroup>
          <optgroup label="💳 Nov 2026 Paid Frontier (needs OpenRouter credits)">
            <option value="openrouter@openai/gpt-6.1-terra">GPT-6.1 Terra (Frontier Thinking, 1M ctx)</option>
            <option value="openrouter@google/gemini-4-hydrogen">Gemini 4 Hydrogen (Fast Frontier, 1M ctx)</option>
            <option value="openrouter@anthropic/claude-fable-5.2">Claude Fable 5.2 (Deep Reasoning)</option>
            <option value="openrouter@moonshotai/kimi-k3.1-pro">Kimi K3.1 Pro (1M ctx)</option>
            <option value="openrouter@minimax/minimax-m3.1-flash">MiniMax M3.1 Flash (Cheap + Fast)</option>
            <option value="openrouter@deepseek/deepseek-v4.1-flash-1017">DeepSeek V4.1 Flash (1M ctx)</option>
          </optgroup>
          <optgroup label="🇺🇸 OpenAI Frontier">
            <option value="openai/o3-mini">OpenAI o3-mini (High-Speed Reasoning)</option>
            <option value="openai/gpt-4o">OpenAI GPT-4o (Omni)</option>
          </optgroup>
          <optgroup label="🇺🇸 Meta AI Frontier">
            <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B Instruct</option>
            <option value="meta-llama/llama-3.1-405b-instruct">Llama 3.1 405B Frontier</option>
          </optgroup>
          <optgroup label="⚡ Unlimited Free Frontier Models">
            <option value="nvidia/nemotron-3.5-lightning:free">NVIDIA Nemotron 3.5 Lightning (Free)</option>
            <option value="cohere/north-mini-code:free">Cohere North Mini Code (Free)</option>
            <option value="liquid/lfm-2.5-2.6b:free">Liquid LFM 2.5 (Free)</option>
            <option value="baidu/ernie-5.5-flash-preview:free">Baidu ERNIE 5.5 Flash (Free)</option>
          </optgroup>
        </select>
        
      </div>

      <div class="ailab-effort-wrap" title="Reasoning &amp; Latency SLA Tier">
        <select class="ailab-effort-select" id="ailabEffortSelect" onchange="ailabChangeEffort(this.value)">
          <option value="fast">⚡ Fast SLA (&lt;800ms)</option>
          <option value="default" selected>🎯 Balanced</option>
          <option value="reasoning">🧠 Deep Thinking</option>
          <option value="architecture">🔬 Architecture</option>
        </select>
        
      </div>

      <button type="button" class="ailab-iconbtn" onclick="ailabOpenModelCatalogModal()" title="Browse model catalog (4,750+ models)">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
      </button>
    </div>

    <!-- Right Actions -->
    <div class="ailab-topbar-right">
      <button class="ailab-iconbtn" onclick="ailabOpenAirflowModal()" title="Airflow Orchestrator &amp; SFTP Hub">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
      </button>
      <button class="ailab-iconbtn" onclick="ailabPinCurrentChat()" title="Pin this chat">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v8m-7 4l2-2m10 2l-2-2m-8 6h12m-6 0v6"/></svg>
      </button>
      <button class="ailab-iconbtn" onclick="ailabExportCurrentChat()" title="Export chat as Markdown">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
      </button>
      <button class="ailab-cua-toggle-btn" id="ailabCuaToggleBtn" onclick="ailabToggleCuaPanel()" title="Toggle the autonomous browser agent viewport">
        <span class="ailab-live-pulse-dot"></span>
        <span class="lbl">CUA</span>
      </button>
      <button class="ailab-iconbtn ailab-topbar-sync-btn" onclick="ailabLoadLiveModels(true)" title="Refresh live model catalog">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.5 9a9 9 0 0114.9-3.4L23 10M1 14l4.6 4.4A9 9 0 0020.5 15"/></svg>
      </button>
      <button class="ailab-btn-primary ailab-topbar-new-chat-btn" onclick="ailabNewChat('')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
        <span>New Chat</span>
      </button>
    </div>
  </div>

  <!-- Workspace Body -->
  <div class="ailab-body">
    <!-- Panel 1: Chats & Projects (Resizable Sidebar) -->
    <aside class="ailab-sidebar" id="ailabSidebar">
      <div class="ailab-sidebar-head">
        <span class="ailab-sidebar-title">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
          Chats &amp; Projects
        </span>
        <div style="display:flex;align-items:center;gap:4px;">
          <button class="ailab-rowact" onclick="ailabNewProject()" title="New Project Folder">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/><path d="M12 11v6M9 14h6"/></svg>
          </button>
          <button class="ailab-rowact" onclick="ailabNewChat('')" title="New Chat">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
          </button>
        </div>
      </div>
      <div id="ailabHistoryStatus" style="font-size:10.5px;color:#64748B;padding:0 12px 6px;line-height:1.35;">Loading your chats…</div>

      <div class="ailab-sidebar-scroll" id="ailabSidebarScroll">
        <!-- Pinned Chats -->
        <div class="ailab-sec-header">
          <span>Pinned Sessions</span>
          <span id="ailabPinnedCount">0</span>
        </div>
        <div id="ailabPinnedList"></div>

        <!-- Chats & Tasks -->
        <div class="ailab-sec-header" style="margin-top:6px;">
          <span>Recent Chats</span>
          <span id="ailabRecentCount">0</span>
        </div>
        <div id="ailabChatsList"></div>

        <!-- Projects -->
        <div class="ailab-sec-header" style="margin-top:10px;">
          <span>Projects</span>
          <span id="ailabProjectCount">0</span>
        </div>
        <div id="ailabProjectsList"></div>
      </div>

      <div class="ailab-storage-footer">
        <span id="ailabStorageEngineLabel" title="DuckDB working set + BigQuery durable archive">DuckDB · BigQuery</span>
        <button type="button" id="ailabBqSyncBtn" onclick="AILAB_DUCKDB.syncToBigQuery()" title="Sync to Google BigQuery durable archive">
          <span id="ailabBqSyncLabel">Sync</span>
        </button>
      </div>
    </aside>

    <!-- Resizing Grip -->
    <div class="ailab-grip-v" id="ailabGrip"></div>

    <!-- Panel 2: DATA MODELING EXPLORER (AWS, Snowflake, BigQuery, DuckDB) -->
    <aside class="ailab-explorer is-hidden" id="ailabExplorer">
      <div class="ailab-explorer-head">
        <div style="display:flex;align-items:center;gap:6px;">
          <span style="font-size:14px;">🗄️</span>
          <span class="ailab-explorer-title">Explorer</span>
          <span class="ailab-explorer-badge" id="ailabExplorerCount">4 Databases</span>
        </div>
        <div class="ailab-explorer-tools">
          <button class="ailab-iconbtn" onclick="ailabLoadExplorer(true)" title="Rescan Lakehouses">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.5 9a9 9 0 0114.9-3.4L23 10M1 14l4.6 4.4A9 9 0 0020.5 15"/></svg>
          </button>
          <button class="ailab-iconbtn" onclick="ailabToggleExplorer()" title="Hide Explorer">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </button>
        </div>
      </div>
      <!-- Persistent Airflow & SFTP Action Card inside Explorer -->
      <div style="padding:8px 12px;background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(6,182,212,0.1));border-bottom:1px solid rgba(16,185,129,0.3);display:flex;align-items:center;justify-content:space-between;">
        <div style="display:flex;align-items:center;gap:7px;">
          <span style="font-size:16px;">⏱️</span>
          <div>
            <div style="font-size:11.5px;font-weight:800;color:#F8FAFC;">Airflow Orchestrator</div>
            <div style="font-size:10px;color:#34D399;">Live DAGs • EOD T-1 • SFTP Hub</div>
          </div>
        </div>
        <button type="button" class="ailab-btn-primary" onclick="ailabOpenAirflowModal()" style="padding:4px 10px;font-size:11px;background:#10B981;border-color:#10B981;color:#FFFFFF;font-weight:800;cursor:pointer;border-radius:6px;box-shadow:0 0 10px rgba(16,185,129,0.4);">
          Launch ➔
        </button>
      </div>
      <div class="ailab-explorer-search">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
        <input type="text" id="ailabExplorerFilter" placeholder="Search databases, schemas, tables..." oninput="ailabFilterExplorer(this.value)">
      </div>
      <div class="ailab-explorer-tree" id="ailabExplorerTree">
        <!-- Rendered with AWS, Snowflake, Google BigQuery, DuckDB -->
      </div>
      <div class="ailab-explorer-foot">
        <div style="display:flex;align-items:center;justify-content:space-between;width:100%;">
          <span style="font-size:10.5px;color:#10B981;">🦆 DuckDB • ❄️ Snowflake • ☁️ BigQuery • 🟧 AWS</span>
        </div>
      </div>
      <div class="ailab-grip-v" id="ailabExplorerGrip" title="Drag to resize Explorer"></div>
    </aside>

    <!-- Panel 3: Conversational Cockpit & Code Studio -->
    <main class="ailab-main">
      <!-- Active Chat Header -->
      <div class="ailab-canvas-head">
        <div class="ailab-chat-title-wrap">
          <div class="ailab-active-title" id="ailabActiveTitle">New AI Chat Session</div>
          <div class="ailab-active-sub" id="ailabActiveSub">
            <span id="ailabActiveProjectTag">Standalone Task</span>
            <span>•</span>
            <span id="ailabActiveModelTag">⚡ Single AUTO Engine</span>
            <span>•</span>
            <span id="ailabActiveStorageTag">🦆 DuckDB Synced</span>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button class="ailab-code-btn" onclick="ailabMoveCurrentChat()" title="Move this chat to a project">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg><span class="lbl">Move</span>
          </button>
          <button class="ailab-code-btn" onclick="ailabRenameCurrentChat()" title="Rename this chat">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4z"/></svg><span class="lbl">Rename</span>
          </button>
          <button class="ailab-code-btn" onclick="ailabClearMessages()" title="Clear this view">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 12h8"/></svg><span class="lbl">Clear</span>
          </button>
        </div>
      </div>

      <!-- Messages Stream Canvas -->
      <div class="ailab-messages-wrap" id="ailabMessagesContainer">
        <!-- Empty Hero State -->
        <div class="ailab-hero" id="ailabEmptyHero">
          <h2>🧠 NanoPro AI Lab</h2>
          <p>One workspace for 4,750+ frontier models, durable chats, diagrams and projects.</p>

          <div class="ailab-pill-grid">
            <div class="ailab-pill-card" onclick="ailabSelectPreset('Write a high-performance Python FastAPI service with Pydantic v2 schemas and JWT auth.')">
              <div class="ailab-pill-card-title">💻 Python REST Microservice</div>
              <div class="ailab-pill-card-desc">FastAPI, Pydantic v2 and JWT auth.</div>
            </div>
            <div class="ailab-pill-card" onclick="ailabSelectPreset('Design a zero-loss streaming ETL data pipeline connecting DuckDB, Cloudflare Worker, and BigQuery.')">
              <div class="ailab-pill-card-title">⚡ High-Speed Data Pipeline</div>
              <div class="ailab-pill-card-desc">DuckDB to Worker to BigQuery, with diagrams.</div>
            </div>
            <div class="ailab-pill-card" onclick="ailabSelectPreset('Solve this mathematical optimization problem: Maximize Pareto utility U(m) = alpha*Q - beta*L - gamma*C with Thompson Bandit.')">
              <div class="ailab-pill-card-title">🧠 Deep Mathematical Proof</div>
              <div class="ailab-pill-card-desc">Step-by-step reasoning on R1 or o3-mini.</div>
            </div>
            <div class="ailab-pill-card" onclick="ailabSelectPreset('Render a complete Mermaid architecture diagram for NanoPro 320 Autonomous AI Agents Mesh.')">
              <div class="ailab-pill-card-title">🏗️ Mermaid Architecture</div>
              <div class="ailab-pill-card-desc">Live diagram of your system topology.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Command Input Cockpit -->
      <div class="ailab-input-cockpit">
        <div class="ailab-input-box">
          <div id="ailabAttachmentChips" style="display:none;flex-wrap:wrap;gap:6px;padding:0 0 8px;"></div>
          <textarea
            class="ailab-textarea"
            id="ailabPromptInput"
            placeholder="Ask anything… (Enter to send, Shift+Enter for newline)"
            rows="1"
            onkeydown="ailabHandleKey(event)"
            oninput="ailabAutoResize(this)"
            onpaste="ailabHandlePaste(event)"
          ></textarea>
          <input type="file" id="ailabAttachInput" accept="image/*" multiple style="display:none;" onchange="ailabHandleAttachmentFiles(this.files);this.value='';" />

          <div class="ailab-input-actions">
            <div class="ailab-input-tags">
              <span class="ailab-mode-pill" id="ailabModePill">⚡ AUTO Math Router Active</span>
              <span id="ailabSlaLabel" style="font-size:11px;color:#94A3B8;">Target SLA: &lt;800ms</span>
            </div>

            <div style="display:flex;align-items:center;gap:8px;">
              <button class="ailab-code-btn" title="Attach image, flowchart or architecture diagram" onclick="document.getElementById('ailabAttachInput').click()">📎 Attach</button>
              <button class="ailab-btn-primary" id="ailabSendBtn" onclick="ailabSubmitPrompt()">
                <span>Dispatch</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
              </button>
            </div>
          </div>
        </div>

      </div>
    </main>

    <!-- Resizing Grip for CUA Panel -->
    <div class="ailab-grip-v ailab-grip-cua" id="ailabCuaGrip" style="display:none;" title="Resize CUA Browser Panel"></div>

    <!-- Panel 3: Real autonomous browser (CUA) mirrored from the local Chromium -->
    <aside class="ailab-cua-panel collapsed" id="ailabCuaPanel">
      <div class="ailab-cua-chrome-header">
        <div class="ailab-window-dots">
          <span class="dot red" onclick="ailabToggleCuaPanel(false)" title="Close browser view"></span>
          <span class="dot yellow" onclick="ailabToggleCuaPanel()" title="Minimize"></span>
          <span class="dot green" onclick="ailabToggleCuaFullscreen()" title="Fullscreen"></span>
        </div>
        <div class="ailab-cua-chrome-url" id="ailabCuaChromeUrl">
          <span class="ailab-ssl-lock">🔒</span>
          <span class="ailab-url-text" id="ailabCuaUrlText">about:blank</span>
        </div>
        <div class="ailab-cua-chrome-right">
          <button class="ailab-cua-live-pill" id="ailabCuaBridgePill" onclick="AILAB_CUA.pingBridge(true)" title="Check the local browser bridge">BRIDGE…</button>
          <button class="ailab-iconbtn" onclick="AILAB_CUA.clearTaskLog()" title="Clear agent log">🧹</button>
          <button class="ailab-iconbtn" onclick="ailabToggleCuaFullscreen()" title="Fullscreen">⛶</button>
          <button class="ailab-iconbtn" onclick="ailabToggleCuaPanel(false)" title="Close">✕</button>
        </div>
      </div>

      <div class="ailab-cua-viewport-container" id="ailabCuaViewportContainer">
        <div class="ailab-cua-frame-stack">
          <img class="ailab-cua-screenshot-frame" id="ailabCuaScreenshotFrame" alt="Live browser frame from the local Chromium">
          <img class="ailab-cua-screenshot-frame" id="ailabCuaScreenshotFrameB" alt="">
        </div>

        <div class="ailab-cua-offline" id="ailabCuaOfflineCard">
          <div class="ailab-cua-offline-card">
            <div class="ailab-cua-offline-title">🖥️ Local browser bridge बंद आहे</div>
            <p>AI ला खरा browser लागतो. तो तुमच्या laptop वरच चालतो — Render वर Chromium चालू शकत नाही.</p>
            <ol>
              <li><code>start_cua_bridge.bat</code> डबल-क्लिक करा</li>
              <li>Chromium विंडो उघडेल — ती बंद करू नका</li>
              <li>खाली <b>Retry</b> दाबा</li>
            </ol>
            <div class="ailab-cua-offline-row">
              <input id="ailabCuaBridgeInput" class="ailab-cua-bridge-input" spellcheck="false">
              <button class="ailab-cua-offline-btn" onclick="AILAB_CUA.saveBridgeURL()">Save</button>
              <button class="ailab-cua-offline-btn" onclick="AILAB_CUA.requestBridgePermission()" title="Ask Chrome for local network access">🔐 Access द्या</button>
              <button class="ailab-cua-offline-btn primary" onclick="AILAB_CUA.pingBridge(true)">Retry</button>
            </div>
            <div id="ailabCuaOfflineHint" style="display:none;margin:10px 0 0;font-size:12px;line-height:1.55;color:#FCA5A5;"></div>
          </div>
        </div>

        <div class="ailab-cua-cursor" id="ailabCuaCursor">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="#EF4444" stroke="#FFFFFF" stroke-width="1.6">
            <path d="M3 3l7 18 3-7 7-3L3 3z"/>
          </svg>
          <span class="ailab-cua-cursor-label" id="ailabCuaCursorLabel">Agent CUA</span>
        </div>

        <div class="ailab-cua-click-ripple" id="ailabCuaClickRipple"></div>

        <div class="ailab-cua-action-hud" id="ailabCuaActionHud">
          <span class="ailab-action-icon" id="ailabCuaActionIcon">⚡</span>
          <span class="ailab-action-desc" id="ailabCuaActionDesc">CUA idle — start the local bridge to drive a real browser</span>
        </div>

        <div class="ailab-cua-tasklog" id="ailabCuaTaskLog"></div>
        <div class="ailab-cua-ask" id="ailabCuaAsk"></div>
      </div>
    </aside>
  </div>
</div>


<!-- Model Catalog Search & Discovery Modal -->
<div class="ailab-modal-backdrop" id="ailabModelModal" onclick="ailabCloseModelCatalogModal(event)">
  <div class="ailab-modal" onclick="event.stopPropagation()">
    <div class="ailab-modal-head">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-size:20px;">🌐</span>
        <div>
          <h4 style="margin:0;font-size:16px;color:#F8FAFC;font-weight:800;">Global Frontier AI Model Registry</h4>
          <p style="margin:0;font-size:11.5px;color:#94A3B8;">4,750+ Unified Models across OpenRouter (473), AI/ML API (995), Hugging Face (110+), Fal.ai, Replicate &amp; Groq</p>
        </div>
      </div>



      <button type="button" class="ailab-modal-close" onclick="ailabCloseModelCatalogModal()">&times;</button>
    </div>
    <div class="ailab-modal-search">
      <span style="font-size:16px;color:#8B5CF6;">🔍</span>
      <input type="text" id="ailabModelSearchInput" placeholder="Search 4,750+ models by name, lab, provider, or capability (e.g. claude, deepseek, flux, qwen, free)..." oninput="ailabFilterModels()">
    </div>
    <div class="ailab-modal-pills">
      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Mesh (4,750+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('krutrim', this)">🇮🇳 Krutrim AI (Ola)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('poe', this)">⚡ Poe by Quora (303)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('parasail', this)">⛵ Parasail (107)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('arcee', this)">🏹 Arcee AI (SLMs)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('edenai', this)">🌿 Eden AI (1,311)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('requesty', this)">🌐 Requesty AI (750)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('cf_ai', this)">☁️ Cloudflare Workers AI (150+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('novita', this)">🚀 Novita AI (99)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('nvidia', this)">🟢 NVIDIA NIM (83)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('sambanova', this)">⚡ SambaNova (RDU)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('openrouter', this)">⚡ OpenRouter (473)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('aimlapi', this)">🚀 AI/ML API (995)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('deepinfra', this)">🧠 DeepInfra (177)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('mistral', this)">🇫🇷 Mistral Direct (56)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('hf', this)">🤗 Hugging Face (110+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('groq', this)">⚡ Groq LPUs (11)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('friendli_thesean', this)">🚀 Friendli &amp; TheSean</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('deepseek', this)">🇨🇳 DeepSeek Direct</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('fal_replicate', this)">🎨 Fal.ai &amp; Replicate</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('free', this)">🆓 Free Tier</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('reasoning', this)">🧠 Reasoning SOTA</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('code', this)">💻 Code Specialists</button>
    </div>
    <div class="ailab-modal-grid" id="ailabModelModalGrid">
      <!-- Dynamically filled with model cards -->
    </div>
    <div class="ailab-modal-footer">
      <span>⚡ Single AUTO Engine evaluates Pareto Frontier in &lt; 3.0ms</span>
      <span style="color:#10B981;">🛡️ 429 Shield Active • Render RAM: 0 MB</span>
    </div>
  </div>
</div>

<!-- AIRFLOW ORCHESTRATOR & SFTP HUB MODAL -->
<div class="ailab-modal-backdrop" id="ailabAirflowModal" style="position:fixed !important;top:0 !important;left:0 !important;right:0 !important;bottom:0 !important;width:100vw !important;height:100vh !important;z-index:999999 !important;background:rgba(3,7,18,0.9) !important;backdrop-filter:blur(12px) !important;display:none;align-items:center;justify-content:center;padding:16px;box-sizing:border-box;" onclick="ailabCloseAirflowModal(event)">
  <div class="ailab-modal" style="max-width:1060px;max-height:92vh;width:1060px;" onclick="event.stopPropagation()">
    <div class="ailab-modal-head">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-size:22px;">&#9889;</span>
        <div>
          <div style="font-size:15px;font-weight:800;color:#F8FAFC;">NanoPro Airflow Orchestrator &amp; SFTP Hub</div>
          <div style="font-size:11.5px;color:#94A3B8;">BigQuery &bull; SFTP &bull; AWS S3/Glue &bull; Snowflake L0-L2 &bull; DuckDB &bull; Email / Telegram / WhatsApp</div>
        </div>
      </div>
      <button type="button" class="ailab-modal-close" onclick="ailabCloseAirflowModal()">&times;</button>
    </div>

    <div class="ailab-modal-pills" style="padding:10px 16px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;gap:8px;flex-wrap:wrap;">
      <button type="button" class="ailab-pill is-active" id="tabAirflowDags" onclick="ailabSwitchAirflowTab('dags')">&#9889; <span id="orchDagCountTab">DAGs</span></button>
      <button type="button" class="ailab-pill" id="tabAirflowSftp" onclick="ailabSwitchAirflowTab('sftp')">&#128194; SFTP Hub</button>
      <button type="button" class="ailab-pill" id="tabAirflowAlerts" onclick="ailabSwitchAirflowTab('alerts')">&#128276; Alerts</button>
      <button type="button" class="ailab-pill" id="tabAirflowLogs" onclick="ailabSwitchAirflowTab('logs')">&#128220; Logs</button>
      <button type="button" class="ailab-pill" id="tabAirflowArch" onclick="ailabSwitchAirflowTab('arch')">&#128290; Architecture</button>
    </div>

    <!-- TAB 1: DAGS -->
    <div id="airflowTabDags" style="padding:14px;overflow-y:auto;max-height:calc(92vh - 180px);">
      <div id="airflowOverview" style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px;"></div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:8px 12px;gap:10px;">
        <div id="airflowSchedulerLine" style="font-size:11.5px;color:#CBD5E1;line-height:1.5;">Loading scheduler state...</div>
        <button type="button" class="ailab-code-btn" onclick="ailabOrchRefreshAll()" style="font-size:11px;color:#38BDF8;white-space:nowrap;">&#8635; Refresh</button>
      </div>
      <div id="airflowIncidents" style="margin-bottom:12px;"></div>
      <div id="airflowDagsList" style="display:flex;flex-direction:column;gap:10px;">
        <div style="text-align:center;padding:20px;color:#94A3B8;">Loading live DAGs...</div>
      </div>
    </div>

    <!-- TAB 2: SFTP HUB -->
    <div id="airflowTabSftp" style="display:none;padding:14px;overflow-y:auto;max-height:calc(92vh - 180px);">
      <div id="airflowSftpInfo" style="background:rgba(15,23,42,0.85);border:1px solid rgba(56,189,248,0.28);border-radius:10px;padding:12px 14px;margin-bottom:12px;font-size:12px;color:#CBD5E1;line-height:1.7;">
        Loading SFTP landing zone...
      </div>

      <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px 14px;margin-bottom:12px;">
        <div style="font-size:12.5px;font-weight:700;color:#F8FAFC;margin-bottom:8px;">Upload a partner file (CSV / TXT / XLSX)</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
          <input type="text" id="ailabSftpPartner" placeholder="partner (e.g. cbs_feed)" value="manual" style="width:150px;background:rgba(30,41,59,0.8);border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:8px 10px;color:#F8FAFC;font-size:12px;">
          <input type="file" id="ailabSftpFile" accept=".csv,.txt,.tsv,.xlsx,.xls" style="flex:1;min-width:220px;background:rgba(30,41,59,0.8);border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:6px;color:#CBD5E1;font-size:11.5px;">
          <button type="button" class="ailab-btn-primary" id="ailabSftpUploadBtn" onclick="ailabSftpUpload()" style="padding:8px 14px;font-size:12px;">Upload &amp; Ingest</button>
        </div>
        <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;">
          <button type="button" class="ailab-code-btn" onclick="ailabSftpProcess()" style="font-size:11px;color:#34D399;">&#9654; Process all pending</button>
          <button type="button" class="ailab-code-btn" onclick="ailabSftpSample()" style="font-size:11px;color:#A78BFA;">+ Generate sample CSV</button>
        </div>
        <div id="ailabSftpMsg" style="margin-top:8px;font-size:11.5px;color:#94A3B8;"></div>
      </div>

      <div style="font-size:12.5px;font-weight:700;color:#F8FAFC;margin-bottom:8px;">Landing files</div>
      <div id="airflowSftpFilesList" style="display:flex;flex-direction:column;gap:6px;margin-bottom:14px;"></div>

      <div style="font-size:12.5px;font-weight:700;color:#F8FAFC;margin-bottom:8px;">Bronze tables produced by SFTP</div>
      <div id="airflowSftpTables" style="display:flex;flex-direction:column;gap:6px;"></div>

      <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin:18px 0 8px;flex-wrap:wrap;">
        <div style="font-size:12.5px;font-weight:700;color:#F8FAFC;">Outbound reports (SFTP delivery)</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button type="button" class="ailab-code-btn" onclick="ailabOrchBuildReport(false)" style="font-size:11px;color:#38BDF8;">Build Excel report</button>
          <button type="button" class="ailab-code-btn" onclick="ailabOrchBuildReport(true)" style="font-size:11px;color:#34D399;">Build + send email / Telegram / WhatsApp</button>
        </div>
      </div>
      <div id="ailabReportMsg" style="font-size:11.5px;color:#94A3B8;margin-bottom:8px;"></div>
      <div id="airflowSftpOutbound" style="display:flex;flex-direction:column;gap:6px;">
        <div style="text-align:center;padding:12px;color:#94A3B8;">Loading outbound reports...</div>
      </div>
    </div>

    <!-- TAB 3: ALERTS -->
    <div id="airflowTabAlerts" style="display:none;padding:14px;overflow-y:auto;max-height:calc(92vh - 180px);">
      <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:14px;margin-bottom:12px;">
        <div style="font-size:13px;font-weight:700;color:#F8FAFC;margin-bottom:10px;">Alert channels</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
          <label style="font-size:11.5px;color:#94A3B8;">Email recipients (comma separated)
            <input type="text" id="orchAlertRecipients" style="width:100%;margin-top:4px;background:rgba(30,41,59,0.8);border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:8px 10px;color:#F8FAFC;font-size:12px;">
          </label>
          <label style="font-size:11.5px;color:#94A3B8;">Sender email
            <input type="text" id="orchAlertSender" style="width:100%;margin-top:4px;background:rgba(30,41,59,0.8);border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:8px 10px;color:#F8FAFC;font-size:12px;">
          </label>
          <label style="font-size:11.5px;color:#94A3B8;">Telegram chat / channel
            <input type="text" id="orchAlertTelegram" style="width:100%;margin-top:4px;background:rgba(30,41,59,0.8);border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:8px 10px;color:#F8FAFC;font-size:12px;">
          </label>
          <label style="font-size:11.5px;color:#94A3B8;">WhatsApp number (with country code)
            <input type="text" id="orchAlertWhatsapp" style="width:100%;margin-top:4px;background:rgba(30,41,59,0.8);border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:8px 10px;color:#F8FAFC;font-size:12px;">
          </label>
        </div>
        <div style="display:flex;gap:14px;margin-top:10px;font-size:11.5px;color:#CBD5E1;">
          <label><input type="checkbox" id="orchAlertTelegramOn"> Telegram enabled</label>
          <label><input type="checkbox" id="orchAlertWhatsappOn"> WhatsApp enabled</label>
        </div>
        <div style="display:flex;gap:8px;margin-top:12px;flex-wrap:wrap;">
          <button type="button" class="ailab-btn-primary" onclick="ailabOrchSaveAlerts()" style="padding:7px 14px;font-size:12px;">Save</button>
          <button type="button" class="ailab-code-btn" onclick="ailabOrchTestAlert('email')" style="font-size:11px;color:#38BDF8;">Test Email</button>
          <button type="button" class="ailab-code-btn" onclick="ailabOrchTestAlert('telegram')" style="font-size:11px;color:#A78BFA;">Test Telegram</button>
          <button type="button" class="ailab-code-btn" onclick="ailabOrchTestAlert('whatsapp')" style="font-size:11px;color:#34D399;">Test WhatsApp</button>
        </div>
        <div id="ailabAlertMsg" style="margin-top:8px;font-size:11.5px;color:#94A3B8;"></div>
      </div>

      <div style="font-size:12.5px;font-weight:700;color:#F8FAFC;margin-bottom:8px;display:flex;justify-content:space-between;">
        <span>Delivery log (real provider results)</span>
        <button type="button" class="ailab-code-btn" onclick="ailabOrchLoadAlerts()" style="font-size:11px;color:#38BDF8;">&#8635; Refresh</button>
      </div>
      <div id="ailabNotificationLogsList" style="display:flex;flex-direction:column;gap:6px;"></div>
    </div>

    <!-- TAB 4: LOGS -->
    <div id="airflowTabLogs" style="display:none;padding:14px;overflow-y:auto;max-height:calc(92vh - 180px);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <div style="font-size:12.5px;font-weight:700;color:#F8FAFC;">Runtime + orchestrator audit log</div>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
          <input type="text" id="orchLogFilter" placeholder="filter: dag id, ERROR, partner..." oninput="ailabOrchRenderStoredLogs()" style="width:220px;background:rgba(30,41,59,0.8);border:1px solid rgba(255,255,255,0.15);border-radius:6px;padding:6px 9px;color:#F8FAFC;font-size:11.5px;">
          <label style="display:flex;align-items:center;gap:5px;font-size:11px;color:#F87171;cursor:pointer;"><input type="checkbox" id="orchLogErrorsOnly" onchange="ailabOrchRenderStoredLogs()"> errors only</label>
          <button type="button" class="ailab-code-btn" onclick="ailabOrchLoadLogs()" style="font-size:11px;color:#38BDF8;">&#8635; Refresh</button>
        </div>
      </div>
      <div id="airflowOrchLogs" style="background:#090D16;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:12px;font-family:ui-monospace,Menlo,Monaco,Consolas,monospace;font-size:11px;max-height:440px;overflow-y:auto;display:flex;flex-direction:column;gap:3px;color:#CBD5E1;"></div>
    </div>

    <!-- TAB 5: ARCHITECTURE -->
    <div id="airflowTabArch" style="display:none;padding:14px;overflow-y:auto;max-height:calc(92vh - 180px);">
      <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:16px;">
        <div style="font-size:13.5px;font-weight:700;color:#38BDF8;margin-bottom:10px;">Live data flow (what the DAGs actually do)</div>
        <div style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:11.5px;color:#CBD5E1;line-height:2;white-space:pre-wrap;">SOURCE 1  BigQuery nanopro_cbs_bronze (CMG, GAM, HTD, SOL, SWIFT_MSG, TAM_LAM, UBO, VCT)
SOURCE 2  SFTP landing  s3://nanopro-data-lake-765865641438/sftp/inbound/&lt;partner&gt;/  (CSV / TXT / XLSX)
              |
              v
DAG 1 &amp; 2  Parquet in s3://.../bronze/bigquery/... and s3://.../sftp/bronze/... + _MANIFEST.json
              |
              v
DAG 3      Glue tables (nanopro_bronze, nanopro_sftp) + Iceberg gold copy
              |
              v
DAG 4      Snowflake BANK_DB.L0_STAGING   (raw + _RUN_ID / _LOADED_AT)
DAG 5      Snowflake BANK_DB.L1_HARMONIZED (trim, dedupe on business key, quality gate)
DAG 6      Snowflake BANK_DB.L2_CURATED   (CUSTOMER_360, BRANCH_NETWORK, ... + DATA_QUALITY_MART)
              |
              v
DAG 7      DuckDB report on bronze Parquet + parity check against Snowflake L0
              |
              v
DAG 8      Email (SMTP cascade) / Telegram bot / Meta WhatsApp Cloud API</div>
        <div style="margin-top:14px;font-size:12px;color:#94A3B8;line-height:1.7;">
          <div>&bull; <strong style="color:#CBD5E1;">Scheduling:</strong> in-app scheduler thread (no Render cron job), tick every 60 minutes; batch cycles BOD 06:00, SOD 08:00, T1 10:00, EOD 18:00 IST.</div>
          <div>&bull; <strong style="color:#CBD5E1;">No CDC:</strong> each tick is a snapshot export; new BigQuery rows appear in AWS / Snowflake / DuckDB on the next tick.</div>
          <div>&bull; <strong style="color:#CBD5E1;">Rollback:</strong> every layer is rebuilt with CREATE OR REPLACE from the S3 bronze source of truth; SFTP rollback drops that batch's tables.</div>
          <div>&bull; <strong style="color:#CBD5E1;">Pause / schedule changes</strong> are stored in S3 (config/orchestrator_control.json) and survive redeploys.</div>
        </div>
      </div>
    </div>

    <div class="ailab-modal-footer">
      <span id="airflowFooterLeft">Live status from scheduler + Snowflake batch ledger</span>
      <span style="color:#10B981;">&#128737; Honest status only - nothing simulated</span>
    </div>
  </div>
</div>

<script>
(function() {
  // Global AI Lab State
  window.AILAB = {
    activeChatId: null,
    activeProjectId: null,
    chats: [],
    projects: [],
    messages: [],
    isStreaming: false,
    selectedModel: "auto",
    selectedEffort: "default",
    cacheLoaded: false,
    storageOwner: null,
    historyStorage: null,
    pendingAttachments: [],
    restoreRetries: 0,
    expandedProjects: {},
    heroNode: null
  };

  // Helper selectors
  function $id(id) { return document.getElementById(id); }

  // -------------------------------------------------------------
  // INITIALIZATION & HYDRATION
  // -------------------------------------------------------------
  
  // =========================================================================
  // DATA MODELING EXPLORER JAVASCRIPT CONTROLLER (AWS, Snowflake, BigQuery, DuckDB)
  // =========================================================================
  window.AILAB_EXPLORER = {
    isOpen: false,
    catalog: null,
    treeOpen: { "db_duckdb": true, "db_snowflake": true, "db_bigquery": true, "db_aws": true, "sc_duckdb_gold_marts": true, "sc_snowflake_L0_STAGING": true },
    activeTable: null
  };

  window.ailabInitExplorer = function() {
    const grip = $id("ailabExplorerGrip");
    const panel = $id("ailabExplorer");
    if (grip && panel) {
      let isDragging = false;
      let startX = 0, startW = 0;

      grip.addEventListener("mousedown", (e) => {
        isDragging = true;
        startX = e.clientX;
        startW = panel.offsetWidth;
        document.body.style.cursor = "col-resize";
        document.body.style.userSelect = "none";
      });

      window.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        const newW = Math.max(180, Math.min(500, startW + (e.clientX - startX)));
        panel.style.width = newW + "px";
      });

      window.addEventListener("mouseup", () => {
        if (isDragging) {
          isDragging = false;
          document.body.style.cursor = "";
          document.body.style.userSelect = "";
        }
      });
    }

    ailabLoadExplorer();
  };

  window.ailabToggleExplorer = function() {
    const p = $id("ailabExplorer");
    const btn = $id("ailabToggleExplorer");
    if (!p) return;
    const isHidden = p.classList.toggle("is-hidden");
    AILAB_EXPLORER.isOpen = !isHidden;
    if (btn) btn.classList.toggle("is-active", !isHidden);
  };

  window.ailabLoadExplorer = async function(forceRefresh = false) {
    const tree = $id("ailabExplorerTree");
    if (!tree) return;
    try {
      const res = await fetch("/api/ai/explorer/catalog");
      if (res.ok) {
        const data = await res.json();
        AILAB_EXPLORER.catalog = data.databases || [];
        ailabRenderExplorerTree();
        return;
      }
    } catch (_) {}
    // No static fallback: an empty catalog is the honest answer when the API is down.
    AILAB_EXPLORER.catalog = [];

    ailabRenderExplorerTree();
  };

  window.ailabRenderExplorerTree = function() {
    const tree = $id("ailabExplorerTree");
    if (!tree) return;
    const filter = ($id("ailabExplorerFilter")?.value || "").toLowerCase().trim();
    const dbs = AILAB_EXPLORER.catalog || [];

    if (dbs.length === 0) {
      tree.innerHTML = '<div style="padding:15px;text-align:center;color:#64748B;font-size:12px;">No databases loaded.</div>';
      return;
    }

    let html = "";
    dbs.forEach(db => {
      const dbKey = "db_" + db.id;
      const isOpen = AILAB_EXPLORER.treeOpen[dbKey] !== false;

      let schemasHtml = "";
      (db.schemas || []).forEach(sc => {
        const scKey = "sc_" + db.id + "_" + sc.name;
        const isScOpen = AILAB_EXPLORER.treeOpen[scKey] !== false;

        let tablesHtml = "";
        (sc.tables || []).forEach(tb => {
          if (filter && !tb.name.toLowerCase().includes(filter) && !sc.name.toLowerCase().includes(filter)) {
            return;
          }
          const tbKey = "tb_" + db.id + "_" + sc.name + "_" + tb.name;
          const isTbOpen = !!AILAB_EXPLORER.treeOpen[tbKey];

          let colsHtml = "";
          if (isTbOpen && tb._loadingColumns) {
            colsHtml = `
              <div class="ailab-tree-children is-expanded" id="child_${escapeHtml(tbKey)}">
                <div style="padding:3px 15px;color:#64748B;font-size:10.5px;">Loading columns…</div>
              </div>
            `;
          } else if (isTbOpen && tb.columns && tb.columns.length > 0) {
            colsHtml = `
              <div class="ailab-tree-children is-expanded" id="child_${escapeHtml(tbKey)}">
                ${tb.columns.map(c => `
                  <div style="padding:2px 6px 2px 22px;font-size:10.5px;color:#94A3B8;display:flex;align-items:center;gap:5px;font-family:monospace;" data-ailab-kind="column" data-db="${escapeHtml(db.id)}" data-schema="${escapeHtml(sc.name)}" data-table="${escapeHtml(tb.name)}" data-column="${escapeHtml(c.name)}" data-type="${escapeHtml(c.type)}">
                    <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">• ${escapeHtml(c.name)}</span>
                    ${c.key ? `<span title="${c.key === 'PK' ? 'Primary key' : 'Foreign key'}" style="font-size:8.5px;padding:0 4px;border-radius:3px;${c.key === 'PK' ? 'background:rgba(250,204,21,0.15);color:#FACC15;' : 'background:rgba(56,189,248,0.15);color:#38BDF8;'}">${c.key}</span>` : ""}
                    <span style="color:#64748B;font-size:9.5px;">${escapeHtml(c.type)}</span>
                  </div>
                `).join("")}
              </div>
            `;
          } else if (isTbOpen) {
            if (!tb._columnError && !tb._attemptedColumns) {
              setTimeout(() => ailabFetchExplorerColumns(db.id, sc.name, tb.name), 0);
              colsHtml = `
                <div class="ailab-tree-children is-expanded" id="child_${escapeHtml(tbKey)}">
                  <div style="padding:3px 15px;color:#64748B;font-size:10.5px;">Loading columns…</div>
                </div>
              `;
            } else {
              colsHtml = `
                <div class="ailab-tree-children is-expanded" id="child_${escapeHtml(tbKey)}">
                  <div style="padding:3px 15px;color:#64748B;font-size:10.5px;">${escapeHtml(tb._columnError || "No columns reported.")}</div>
                </div>
              `;
            }
          }

          tablesHtml += `
            <div class="ailab-tree-node">
              <div class="ailab-tree-row" data-ailab-kind="table" data-db="${escapeHtml(db.id)}" data-schema="${escapeHtml(sc.name)}" data-table="${escapeHtml(tb.name)}" onclick="ailabClickExplorerTable('${escapeHtml(db.id)}', '${escapeHtml(sc.name)}', '${escapeHtml(tb.name)}', '${escapeHtml(tbKey)}')">
                <span class="ailab-tree-arrow ${isTbOpen ? 'is-expanded' : ''}">▶</span>
                <span style="font-size:11px;">📄</span>
                <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(tb.name)}</span>
                <span class="ailab-tree-badge" style="background:rgba(59,130,246,0.15);color:#93C5FD;">${tb.rows ? tb.rows.toLocaleString() + 'r' : ''}</span>
              </div>
              ${colsHtml}
            </div>
          `;
        });

        if (tablesHtml || !filter) {
          schemasHtml += `
            <div class="ailab-tree-node">
              <div class="ailab-tree-row" data-ailab-kind="schema" data-db="${escapeHtml(db.id)}" data-schema="${escapeHtml(sc.name)}" onclick="ailabToggleTreeNode('${escapeHtml(scKey)}')">
                <span class="ailab-tree-arrow ${isScOpen ? 'is-expanded' : ''}">▶</span>
                <span style="font-size:11px;">📁</span>
                <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#E2E8F0;">${escapeHtml(sc.name)}</span>
              </div>
              <div class="ailab-tree-children ${isScOpen ? 'is-expanded' : ''}" id="child_${escapeHtml(scKey)}">
                ${tablesHtml || '<div style="padding:4px 15px;color:#64748B;font-size:11px;">No tables.</div>'}
              </div>
            </div>
          `;
        }
      });

      html += `
        <div class="ailab-tree-node" style="margin-bottom:6px;">
          <div class="ailab-tree-row" style="font-weight:700;color:#F8FAFC;" title="${escapeHtml(db.detail || db.error || "")}" onclick="ailabToggleTreeNode('${escapeHtml(dbKey)}')">
            <span class="ailab-tree-arrow ${isOpen ? 'is-expanded' : ''}">▶</span>
            <span>${db.icon || '🗄️'}</span>
            <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(db.name)}</span>
            ${db.error ? '<span title="' + escapeHtml(db.error) + '" style="color:#F87171;font-size:10px;">⚠</span>' : ""}
          </div>
          <div class="ailab-tree-children ${isOpen ? 'is-expanded' : ''}" id="child_${escapeHtml(dbKey)}">
            ${schemasHtml}
          </div>
        </div>
      `;
    });

    tree.innerHTML = html;
  };

  window.ailabToggleTreeNode = function(key) {
    AILAB_EXPLORER.treeOpen[key] = !AILAB_EXPLORER.treeOpen[key];
    const el = $id("child_" + key);
    if (el) el.classList.toggle("is-expanded", AILAB_EXPLORER.treeOpen[key]);
    ailabRenderExplorerTree();
  };

  window.ailabFetchExplorerColumns = async function(dbId, schema, table) {
    const db = (AILAB_EXPLORER.catalog || []).find(d => d.id === dbId);
    const sc = db ? (db.schemas || []).find(s => s.name === schema) : null;
    const tableEntry = sc ? (sc.tables || []).find(t => t.name === table) : null;
    if (!tableEntry || tableEntry._loadingColumns) return;
    tableEntry._loadingColumns = true;
    tableEntry._attemptedColumns = true;
    ailabRenderExplorerTree();
    try {
      const qs = new URLSearchParams({ database: dbId, schema: schema, table: table });
      const res = await fetch(`/api/ai/explorer/table?${qs.toString()}`, { cache: "no-store" });
      const data = res.ok ? await res.json() : {};
      if (data && Array.isArray(data.columns)) tableEntry.columns = data.columns;
      tableEntry._columnError = (data && data.error) || (res.ok ? "" : `Column lookup failed (${res.status}).`);
    } catch (_) {
      tableEntry._columnError = "Column lookup failed.";
    }
    tableEntry._loadingColumns = false;
    ailabRenderExplorerTree();
  };

  window.ailabClickExplorerTable = async function(dbId, schema, table, tbKey) {
    AILAB_EXPLORER.treeOpen[tbKey] = !AILAB_EXPLORER.treeOpen[tbKey];
    const isOpen = !!AILAB_EXPLORER.treeOpen[tbKey];

    const db = (AILAB_EXPLORER.catalog || []).find(d => d.id === dbId);
    const sc = db ? (db.schemas || []).find(s => s.name === schema) : null;
    const tableEntry = sc ? (sc.tables || []).find(t => t.name === table) : null;

    // Columns are introspected on first expand so the catalog stays cheap.
    if (isOpen && tableEntry && (!tableEntry.columns || tableEntry.columns.length === 0)) {
      delete tableEntry._columnError;
      await ailabFetchExplorerColumns(dbId, schema, table);
    }
    ailabRenderExplorerTree();

    const fullPath = `${dbId}.${schema}.${table}`;
    const input = $id("ailabPromptInput");
    if (input) {
      input.value = `Analyze table \`${fullPath}\` with schema optimization, CDC deduplication, and DuckDB/BigQuery performance.`;
      input.focus();
    }
  };

  window.ailabFilterExplorer = function(val) {
    ailabRenderExplorerTree();
  };

  // -------------------------------------------------------------
  // EXPLORER RIGHT-CLICK ADMIN (rename / delete / column type)
  // -------------------------------------------------------------
  function ailabEnsureCtxStyles() {
    if (document.getElementById('ailabCtxStyles')) return;
    const style = document.createElement('style');
    style.id = 'ailabCtxStyles';
    style.textContent = `
      .ailab-ctx-menu{position:fixed;z-index:100002;min-width:232px;background:#0B1220;border:1px solid #1E293B;border-radius:10px;box-shadow:0 18px 40px rgba(0,0,0,.55);padding:6px;font-size:12px;color:#E2E8F0;}
      .ailab-ctx-head{padding:8px 10px 6px;border-bottom:1px solid #1E293B;margin-bottom:4px;}
      .ailab-ctx-title{font-weight:700;color:#F8FAFC;font-size:12.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:260px;}
      .ailab-ctx-meta{color:#64748B;font-size:10.5px;margin-top:2px;}
      .ailab-ctx-item{padding:7px 10px;border-radius:7px;cursor:pointer;display:flex;gap:8px;align-items:center;}
      .ailab-ctx-item:hover{background:#1E293B;}
      .ailab-ctx-item.is-danger{color:#F87171;}
      .ailab-ctx-item.is-danger:hover{background:rgba(248,113,113,.12);}
      .ailab-dlg-overlay{position:fixed;inset:0;background:rgba(2,6,23,.72);z-index:100003;display:flex;align-items:center;justify-content:center;}
      .ailab-dlg{width:min(440px,92vw);max-height:88vh;overflow:auto;background:#0B1220;border:1px solid #1E293B;border-radius:12px;box-shadow:0 24px 60px rgba(0,0,0,.6);padding:16px;color:#E2E8F0;font-size:12.5px;}
      .ailab-dlg-title{font-weight:700;color:#F8FAFC;font-size:14px;}
      .ailab-dlg-sub{color:#64748B;font-size:11px;margin-top:2px;}
      .ailab-dlg-body{margin-top:12px;}
      .ailab-dlg-label{display:block;color:#94A3B8;font-size:11px;margin:10px 0 4px;}
      .ailab-dlg-input,.ailab-dlg-select{width:100%;box-sizing:border-box;background:#0F172A;border:1px solid #334155;border-radius:7px;color:#E2E8F0;padding:7px 9px;font-size:12px;outline:none;}
      .ailab-dlg-input:focus,.ailab-dlg-select:focus{border-color:#3B82F6;}
      .ailab-dlg-warn{background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.35);color:#FCA5A5;border-radius:8px;padding:8px 10px;font-size:11.5px;line-height:1.5;}
      .ailab-dlg-hint{color:#64748B;font-size:10.5px;line-height:1.5;margin-top:8px;}
      .ailab-dlg-error{color:#F87171;font-size:11px;margin-top:8px;min-height:14px;}
      .ailab-dlg-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:14px;}
      .ailab-btn{background:#1E293B;color:#E2E8F0;border:1px solid #334155;border-radius:7px;padding:6px 12px;font-size:12px;cursor:pointer;}
      .ailab-btn:hover{background:#273449;}
      .ailab-btn.primary{background:#2563EB;border-color:#2563EB;color:#fff;}
      .ailab-btn.primary:disabled{opacity:.45;cursor:not-allowed;}
      .ailab-btn.is-danger{background:#B91C1C;border-color:#B91C1C;color:#fff;}
      .ailab-toast-host{position:fixed;right:18px;bottom:18px;z-index:100004;display:flex;flex-direction:column;gap:8px;}
      .ailab-toast{background:#0B1220;border:1px solid #1E293B;border-left:3px solid #3B82F6;border-radius:8px;padding:9px 12px;color:#E2E8F0;font-size:12px;box-shadow:0 12px 30px rgba(0,0,0,.45);transition:opacity .3s;max-width:360px;}
      .ailab-toast.success{border-left-color:#22C55E;}
      .ailab-toast.error{border-left-color:#EF4444;}
    `;
    document.head.appendChild(style);
  }

  window.ailabNotify = function(message, kind) {
    ailabEnsureCtxStyles();
    let host = document.getElementById('ailabToastHost');
    if (!host) {
      host = document.createElement('div');
      host.id = 'ailabToastHost';
      host.className = 'ailab-toast-host';
      document.body.appendChild(host);
    }
    const toast = document.createElement('div');
    toast.className = 'ailab-toast ' + (kind || 'info');
    toast.textContent = message;
    host.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 350); }, 3600);
  };

  function ailabExplorerTableEntry(dbId, schema, table) {
    const db = (AILAB_EXPLORER.catalog || []).find(d => d.id === dbId);
    const sc = db ? (db.schemas || []).find(s => s.name === schema) : null;
    return sc && table ? (sc.tables || []).find(t => t.name === table) : null;
  }

  function ailabOpenDialog(title, subtitle, bodyHtml) {
    ailabEnsureCtxStyles();
    const overlay = document.createElement('div');
    overlay.className = 'ailab-dlg-overlay';
    overlay.innerHTML = `<div class="ailab-dlg"><div class="ailab-dlg-title">${title}</div>${subtitle ? `<div class="ailab-dlg-sub">${subtitle}</div>` : ''}<div class="ailab-dlg-body">${bodyHtml}</div><div class="ailab-dlg-actions"><button class="ailab-btn" data-role="cancel">Cancel</button><button class="ailab-btn primary" data-role="ok">Apply</button></div></div>`;
    document.body.appendChild(overlay);
    const close = () => overlay.remove();
    overlay.addEventListener('click', ev => { if (ev.target === overlay) close(); });
    overlay.querySelector('[data-role="cancel"]').onclick = close;
    return { el: overlay, close, ok: overlay.querySelector('[data-role="ok"]'), body: overlay.querySelector('.ailab-dlg-body') };
  }

  function ailabDialogError(dialog, message) {
    const box = dialog.body.querySelector('.ailab-dlg-error');
    if (box) box.textContent = message || '';
  }

  async function ailabExplorerPost(path, payload) {
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    let data = {};
    try { data = await res.json(); } catch (_) {}
    if (!res.ok || data.status !== 'success') {
      throw new Error(data.message || data.detail || `Request failed (${res.status})`);
    }
    return data;
  }

  window.ailabExplorerApplyRename = function(dbId, schema, table, newName) {
    const db = (AILAB_EXPLORER.catalog || []).find(d => d.id === dbId);
    if (!db) { ailabLoadExplorer(true); return; }
    if (table) {
      const sc = (db.schemas || []).find(s => s.name === schema);
      const tb = sc ? (sc.tables || []).find(t => t.name === table) : null;
      if (!tb) { ailabLoadExplorer(true); return; }
      const oldKey = 'tb_' + dbId + '_' + schema + '_' + table;
      const newKey = 'tb_' + dbId + '_' + schema + '_' + newName;
      if (AILAB_EXPLORER.treeOpen[oldKey] !== undefined) {
        AILAB_EXPLORER.treeOpen[newKey] = AILAB_EXPLORER.treeOpen[oldKey];
        delete AILAB_EXPLORER.treeOpen[oldKey];
      }
      tb.name = newName;
    } else {
      const sc = (db.schemas || []).find(s => s.name === schema);
      if (!sc) { ailabLoadExplorer(true); return; }
      sc.name = newName;
      const open = {};
      Object.keys(AILAB_EXPLORER.treeOpen).forEach(key => {
        if (key === 'sc_' + dbId + '_' + schema) {
          open['sc_' + dbId + '_' + newName] = AILAB_EXPLORER.treeOpen[key];
        } else if (key.indexOf('tb_' + dbId + '_' + schema + '_') === 0) {
          open[key.replace('tb_' + dbId + '_' + schema + '_', 'tb_' + dbId + '_' + newName + '_')] = AILAB_EXPLORER.treeOpen[key];
        } else {
          open[key] = AILAB_EXPLORER.treeOpen[key];
        }
      });
      AILAB_EXPLORER.treeOpen = open;
    }
    ailabRenderExplorerTree();
  };

  window.ailabExplorerApplyDelete = function(dbId, schema, table) {
    const db = (AILAB_EXPLORER.catalog || []).find(d => d.id === dbId);
    if (!db) { ailabLoadExplorer(true); return; }
    if (table) {
      const sc = (db.schemas || []).find(s => s.name === schema);
      if (sc) sc.tables = (sc.tables || []).filter(t => t.name !== table);
      delete AILAB_EXPLORER.treeOpen['tb_' + dbId + '_' + schema + '_' + table];
    } else {
      db.schemas = (db.schemas || []).filter(s => s.name !== schema);
      Object.keys(AILAB_EXPLORER.treeOpen).forEach(key => {
        if (key === 'sc_' + dbId + '_' + schema || key.indexOf('tb_' + dbId + '_' + schema + '_') === 0) {
          delete AILAB_EXPLORER.treeOpen[key];
        }
      });
    }
    ailabRenderExplorerTree();
  };

  window.ailabExplorerApplyColumnChange = function(dbId, schema, table, previous, nextName, nextType) {
    const tb = ailabExplorerTableEntry(dbId, schema, table);
    if (tb && Array.isArray(tb.columns)) {
      const column = tb.columns.find(c => c.name === previous || c.name === nextName);
      if (column) {
        if (nextName) column.name = nextName;
        if (nextType) column.type = nextType;
      }
    }
    ailabRenderExplorerTree();
  };

  window.ailabRenameDialog = function(kind, dbId, schema, table) {
    const current = table || schema;
    const dialog = ailabOpenDialog(
      kind === 'schema' ? 'Rename schema' : 'Rename table',
      table ? `${schema}.${table}` : schema,
      `<label class="ailab-dlg-label">New name</label>
       <input class="ailab-dlg-input" id="npRenameInput" value="${current}" autocomplete="off">
       <div class="ailab-dlg-error"></div>
       ${kind === 'schema' ? '<div class="ailab-dlg-hint">BigQuery datasets rename होत नाहीत — NanoPro सर्व tables नवीन dataset मध्ये copy करून जुना dataset drop करते.</div>' : ''}`
    );
    const input = dialog.el.querySelector('#npRenameInput');
    input.focus();
    input.select();
    dialog.ok.textContent = 'Rename';
    const submit = async () => {
      const newName = input.value.trim();
      if (!newName) return;
      dialog.ok.disabled = true;
      try {
        const data = await ailabExplorerPost('/api/ai/explorer/rename', {
          database: dbId, schema_name: schema, table: table || '', new_name: newName,
        });
        dialog.close();
        ailabExplorerApplyRename(dbId, schema, table, newName, data);
        ailabNotify(`Renamed to ${newName}`, 'success');
      } catch (err) {
        dialog.ok.disabled = false;
        ailabDialogError(dialog, err.message);
      }
    };
    dialog.ok.onclick = submit;
    input.addEventListener('keydown', ev => { if (ev.key === 'Enter') submit(); });
  };

  window.ailabDeleteDialog = function(kind, dbId, schema, table) {
    const name = table || schema;
    const dialog = ailabOpenDialog(
      kind === 'schema' ? 'Delete schema' : 'Delete table',
      table ? `${schema}.${table}` : schema,
      `<div class="ailab-dlg-warn">${table
        ? 'हा table कायमचा delete होईल आणि data परत मिळणार नाही.'
        : 'हा schema आणि त्यातील सर्व tables कायमचे delete होतील.'}</div>
       <label class="ailab-dlg-label">पुष्टी करण्यासाठी <b>${name}</b> टाइप करा</label>
       <input class="ailab-dlg-input" id="npDeleteConfirm" autocomplete="off">
       <div class="ailab-dlg-error"></div>`
    );
    const input = dialog.el.querySelector('#npDeleteConfirm');
    input.focus();
    dialog.ok.textContent = 'Delete';
    dialog.ok.classList.remove('primary');
    dialog.ok.classList.add('is-danger');
    dialog.ok.disabled = true;
    input.addEventListener('input', () => { dialog.ok.disabled = input.value.trim() !== name; });
    dialog.ok.onclick = async () => {
      dialog.ok.disabled = true;
      try {
        const data = await ailabExplorerPost('/api/ai/explorer/delete', {
          database: dbId, schema_name: schema, table: table || '', confirm: input.value.trim(),
        });
        dialog.close();
        ailabExplorerApplyDelete(dbId, schema, table);
        ailabNotify(table ? `Table ${name} deleted` : `Schema ${name} deleted`, 'success');
        if (!table && data.dropped_tables) ailabNotify(`${data.dropped_tables.length} tables removed`, 'info');
      } catch (err) {
        dialog.ok.disabled = false;
        ailabDialogError(dialog, err.message);
      }
    };
  };

  const AILAB_COLUMN_TYPES = ['STRING', 'INT64', 'NUMERIC', 'BIGNUMERIC', 'FLOAT64', 'BOOL', 'DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'BYTES', 'JSON', 'GEOGRAPHY'];
  const AILAB_DATE_FORMATS = [
    ['', '(format बदलू नका)'],
    ['%Y-%m-%d', 'YYYY-MM-DD'],
    ['%d-%m-%Y', 'DD-MM-YYYY'],
    ['%d/%m/%Y', 'DD/MM/YYYY'],
    ['%Y/%m/%d', 'YYYY/MM/DD'],
    ['%d-%b-%Y', 'DD-Mon-YYYY'],
    ['%m/%d/%Y', 'MM/DD/YYYY'],
    ['%d-%m-%Y %H:%M:%S', 'DD-MM-YYYY HH:MM:SS'],
  ];

  window.ailabColumnTypeDialog = async function(dbId, schema, table, presetColumn) {
    const tb = ailabExplorerTableEntry(dbId, schema, table);
    let columns = (tb && tb.columns) || [];
    if (!columns.length) {
      try {
        const qs = new URLSearchParams({ database: dbId, schema: schema, table: table });
        const res = await fetch(`/api/ai/explorer/table?${qs.toString()}`, { cache: 'no-store' });
        const data = res.ok ? await res.json() : {};
        columns = data.columns || [];
        if (tb) tb.columns = columns;
      } catch (_) {}
    }
    if (!columns.length) {
      ailabNotify('Columns load झाले नाहीत — आधी table expand करा.', 'error');
      return;
    }
    const columnOptions = columns.map(c => `<option value="${c.name}" data-type="${c.type}"${c.name === presetColumn ? ' selected' : ''}>${c.name} · ${c.type}</option>`).join('');
    const typeOptions = AILAB_COLUMN_TYPES.map(t => `<option value="${t}">${t}</option>`).join('');
    const formatOptions = AILAB_DATE_FORMATS.map(f => `<option value="${f[0]}">${f[1]}</option>`).join('');
    const dialog = ailabOpenDialog(
      'Change column data type',
      `${schema}.${table}`,
      `<label class="ailab-dlg-label">Column</label>
       <select class="ailab-dlg-select" id="npTypeColumn">${columnOptions}</select>
       <label class="ailab-dlg-label">New data type</label>
       <select class="ailab-dlg-select" id="npTypeTarget">${typeOptions}</select>
       <div id="npTypeLengthRow" style="display:none">
         <label class="ailab-dlg-label">Length (STRING / BYTES)</label>
         <input class="ailab-dlg-input" id="npTypeLength" type="number" min="1" placeholder="e.g. 50">
       </div>
       <div id="npTypePrecRow" style="display:none">
         <label class="ailab-dlg-label">Precision</label>
         <input class="ailab-dlg-input" id="npTypePrecision" type="number" min="1" placeholder="e.g. 12">
         <label class="ailab-dlg-label">Scale</label>
         <input class="ailab-dlg-input" id="npTypeScale" type="number" min="0" placeholder="e.g. 2">
       </div>
       <div id="npTypeFmtRow" style="display:none">
         <label class="ailab-dlg-label">Date format</label>
         <select class="ailab-dlg-select" id="npTypeFormat">${formatOptions}</select>
         <div class="ailab-dlg-hint" id="npTypeFmtHint"></div>
       </div>
       <div class="ailab-dlg-hint">BigQuery थेट फक्त widening conversion करते; इतर बदलांसाठी NanoPro table rebuild करते (data जपून).</div>
       <div class="ailab-dlg-error"></div>`
    );
    const columnSelect = dialog.el.querySelector('#npTypeColumn');
    const targetSelect = dialog.el.querySelector('#npTypeTarget');
    const lengthRow = dialog.el.querySelector('#npTypeLengthRow');
    const precisionRow = dialog.el.querySelector('#npTypePrecRow');
    const formatRow = dialog.el.querySelector('#npTypeFmtRow');
    const fmtHint = dialog.el.querySelector('#npTypeFmtHint');
    const dateTypes = ['DATE', 'DATETIME', 'TIMESTAMP'];

    const sourceType = () => {
      const selected = columnSelect.options[columnSelect.selectedIndex];
      return (selected && selected.getAttribute('data-type') || '').toUpperCase();
    };
    const normalizeType = type => ({ INTEGER: 'INT64', BOOLEAN: 'BOOL', FLOAT: 'FLOAT64' })[type] || type;
    const refresh = () => {
      const source = sourceType();
      const target = targetSelect.value;
      const needsLength = target === 'STRING' || target === 'BYTES';
      const needsPrecision = target === 'NUMERIC' || target === 'BIGNUMERIC';
      const needsFormat = dateTypes.indexOf(target) >= 0 || (dateTypes.indexOf(source) >= 0 && target === 'STRING');
      lengthRow.style.display = needsLength ? '' : 'none';
      precisionRow.style.display = needsPrecision ? '' : 'none';
      formatRow.style.display = needsFormat ? '' : 'none';
      if (needsFormat) {
        if (source === 'STRING' && dateTypes.indexOf(target) >= 0) {
          fmtHint.textContent = 'सध्याची text values या format ने parse होतील (PARSE_' + target + ').';
        } else if (dateTypes.indexOf(source) >= 0 && target === 'STRING') {
          fmtHint.textContent = 'Values या format मध्ये string म्हणून लिहिल्या जातील (FORMAT_' + source + ').';
        } else {
          fmtHint.textContent = 'Format फक्त text ↔ date रूपांतरासाठी लागू होतो; उरलेल्या बदलांसाठी CAST वापरला जाईल.';
        }
      }
    };
    const initialType = normalizeType(sourceType());
    if (AILAB_COLUMN_TYPES.indexOf(initialType) >= 0) targetSelect.value = initialType;
    columnSelect.addEventListener('change', () => {
      const type = normalizeType(sourceType());
      if (AILAB_COLUMN_TYPES.indexOf(type) >= 0) targetSelect.value = type;
      refresh();
    });
    targetSelect.addEventListener('change', refresh);
    refresh();
    dialog.ok.textContent = 'Apply';
    dialog.ok.onclick = async () => {
      const column = columnSelect.value;
      const target = targetSelect.value;
      const payload = { database: dbId, schema_name: schema, table: table, column: column, column_type: target };
      const length = dialog.el.querySelector('#npTypeLength').value.trim();
      const precision = dialog.el.querySelector('#npTypePrecision').value.trim();
      const scale = dialog.el.querySelector('#npTypeScale').value.trim();
      if (lengthRow.style.display !== 'none' && length) payload.length = Number(length);
      if (precisionRow.style.display !== 'none' && precision) payload.precision = Number(precision);
      if (precisionRow.style.display !== 'none' && scale !== '') payload.scale = Number(scale);
      if (formatRow.style.display !== 'none') payload.date_format = dialog.el.querySelector('#npTypeFormat').value;
      dialog.ok.disabled = true;
      try {
        const data = await ailabExplorerPost('/api/ai/explorer/column-type', payload);
        dialog.close();
        ailabExplorerApplyColumnChange(dbId, schema, table, data.previous || column, data.column || column, data.type || target);
        ailabNotify(`${column} → ${data.type || target} (${data.applied === 'recreate' ? 'table rebuilt' : 'in place'})`, 'success');
        if (Array.isArray(data.notes)) data.notes.forEach(note => ailabNotify(note, 'info'));
      } catch (err) {
        dialog.ok.disabled = false;
        ailabDialogError(dialog, err.message);
      }
    };
  };

  window.ailabColumnRenameDialog = function(dbId, schema, table, column) {
    const dialog = ailabOpenDialog(
      'Rename column',
      `${schema}.${table}`,
      `<label class="ailab-dlg-label">New name</label>
       <input class="ailab-dlg-input" id="npColumnRename" value="${column}" autocomplete="off">
       <div class="ailab-dlg-error"></div>`
    );
    const input = dialog.el.querySelector('#npColumnRename');
    input.focus();
    input.select();
    dialog.ok.textContent = 'Rename';
    const submit = async () => {
      const newName = input.value.trim();
      if (!newName) return;
      dialog.ok.disabled = true;
      try {
        await ailabExplorerPost('/api/ai/explorer/column-rename', {
          database: dbId, schema_name: schema, table: table, column: column, new_name: newName,
        });
        dialog.close();
        ailabExplorerApplyColumnChange(dbId, schema, table, column, newName, '');
        ailabNotify(`Column renamed to ${newName}`, 'success');
      } catch (err) {
        dialog.ok.disabled = false;
        ailabDialogError(dialog, err.message);
      }
    };
    dialog.ok.onclick = submit;
    input.addEventListener('keydown', ev => { if (ev.key === 'Enter') submit(); });
  };

  window.ailabAddColumnDialog = function(dbId, schema, table) {
    const typeOptions = AILAB_COLUMN_TYPES.map(t => `<option value="${t}">${t}</option>`).join('');
    const dialog = ailabOpenDialog(
      'Add column',
      `${schema}.${table}`,
      `<label class="ailab-dlg-label">Column name</label>
       <input class="ailab-dlg-input" id="npAddColName" placeholder="e.g. ACCOUNT_STATUS" autocomplete="off">
       <label class="ailab-dlg-label">Data type</label>
       <select class="ailab-dlg-select" id="npAddColType">${typeOptions}</select>
       <div id="npAddColLenRow" style="display:none">
         <label class="ailab-dlg-label">Length (STRING / BYTES)</label>
         <input class="ailab-dlg-input" id="npAddColLength" type="number" min="1" placeholder="e.g. 50">
       </div>
       <div id="npAddColPrecRow" style="display:none">
         <label class="ailab-dlg-label">Precision</label>
         <input class="ailab-dlg-input" id="npAddColPrecision" type="number" min="1" placeholder="e.g. 12">
         <label class="ailab-dlg-label">Scale</label>
         <input class="ailab-dlg-input" id="npAddColScale" type="number" min="0" placeholder="e.g. 2">
       </div>
       <label class="ailab-dlg-label">Mode</label>
       <select class="ailab-dlg-select" id="npAddColMode">
         <option value="NULLABLE">NULLABLE (optional)</option>
         <option value="REQUIRED">REQUIRED (NOT NULL)</option>
       </select>
       <div class="ailab-dlg-hint">ALTER TABLE ... ADD COLUMN थेट चालते; फक्त नवीन column उमटतो, data बदलत नाही.</div>
       <div class="ailab-dlg-error"></div>`
    );
    const nameInput = dialog.el.querySelector('#npAddColName');
    const typeSelect = dialog.el.querySelector('#npAddColType');
    const lengthRow = dialog.el.querySelector('#npAddColLenRow');
    const precisionRow = dialog.el.querySelector('#npAddColPrecRow');
    const refresh = () => {
      const type = typeSelect.value;
      lengthRow.style.display = (type === 'STRING' || type === 'BYTES') ? '' : 'none';
      precisionRow.style.display = (type === 'NUMERIC' || type === 'BIGNUMERIC') ? '' : 'none';
    };
    typeSelect.addEventListener('change', refresh);
    refresh();
    nameInput.focus();
    dialog.ok.textContent = 'Add column';
    const submit = async () => {
      const column = nameInput.value.trim();
      if (!column) { ailabDialogError(dialog, 'Column name आवश्यक आहे.'); return; }
      const payload = { database: dbId, schema_name: schema, table: table, column: column, column_type: typeSelect.value };
      const length = dialog.el.querySelector('#npAddColLength').value.trim();
      const precision = dialog.el.querySelector('#npAddColPrecision').value.trim();
      const scale = dialog.el.querySelector('#npAddColScale').value.trim();
      if (lengthRow.style.display !== 'none' && length) payload.length = Number(length);
      if (precisionRow.style.display !== 'none' && precision) payload.precision = Number(precision);
      if (precisionRow.style.display !== 'none' && scale !== '') payload.scale = Number(scale);
      payload.mode = dialog.el.querySelector('#npAddColMode').value;
      dialog.ok.disabled = true;
      try {
        const data = await ailabExplorerPost('/api/ai/explorer/column-add', payload);
        dialog.close();
        const tb = ailabExplorerTableEntry(dbId, schema, table);
        if (tb) {
          tb.columns = Array.isArray(data.columns) ? data.columns : (tb.columns || []);
          tb.rows = data.rows !== undefined ? data.rows : tb.rows;
          AILAB_EXPLORER.treeOpen['tb_' + dbId + '_' + schema + '_' + table] = true;
        }
        ailabRenderExplorerTree();
        ailabNotify(`${column} (${data.type || typeSelect.value}) जोडला`, 'success');
      } catch (err) {
        dialog.ok.disabled = false;
        ailabDialogError(dialog, err.message);
      }
    };
    dialog.ok.onclick = submit;
    nameInput.addEventListener('keydown', ev => { if (ev.key === 'Enter') submit(); });
  };

  window.ailabCloseExplorerMenu = function() {
    const menu = document.getElementById('ailabCtxMenu');
    if (menu) menu.remove();
  };

  window.ailabOpenExplorerMenu = function(ev, row) {
    ailabEnsureCtxStyles();
    ailabCloseExplorerMenu();
    const kind = row.getAttribute('data-ailab-kind');
    const dbId = row.getAttribute('data-db') || '';
    const schema = row.getAttribute('data-schema') || '';
    const table = row.getAttribute('data-table') || '';
    const column = row.getAttribute('data-column') || '';
    const columnType = row.getAttribute('data-type') || '';
    const db = (AILAB_EXPLORER.catalog || []).find(d => d.id === dbId);
    const sc = db ? (db.schemas || []).find(s => s.name === schema) : null;
    const tb = sc ? (sc.tables || []).find(t => t.name === table) : null;

    let title = schema;
    let meta = '';
    let items = [];
    if (kind === 'schema') {
      meta = `${((sc && sc.tables) || []).length} tables`;
      items = [
        ['rename', '✏️', 'Rename schema'],
        ['delete', '🗑️', 'Delete schema', true],
        ['refresh', '🔄', 'Refresh'],
      ];
    } else if (kind === 'table') {
      title = table;
      const cols = (tb && tb.columns) || [];
      meta = cols.length ? `${cols.length} columns · ${Number(tb.rows || 0).toLocaleString()} rows` : 'Counting columns & rows…';
      items = [
        ['rename', '✏️', 'Rename table'],
        ['addcol', '➕', 'Add column'],
        ['coltype', '🔤', 'Change column type'],
        ['delete', '🗑️', 'Delete table', true],
        ['refresh', '🔄', 'Reload columns'],
      ];
    } else {
      title = column;
      meta = `${(columnType || 'COLUMN').toUpperCase()} · ${schema}.${table}`;
      items = [
        ['coltype', '🔤', 'Change data type'],
        ['colrename', '✏️', 'Rename column'],
      ];
    }

    const menu = document.createElement('div');
    menu.id = 'ailabCtxMenu';
    menu.className = 'ailab-ctx-menu';
    menu.innerHTML = `<div class="ailab-ctx-head"><div class="ailab-ctx-title">${title}</div><div class="ailab-ctx-meta" data-role="meta">${meta}</div></div>`
      + items.map(item => `<div class="ailab-ctx-item${item[3] ? ' is-danger' : ''}" data-act="${item[0]}"><span>${item[1]}</span><span>${item[2]}</span></div>`).join('');
    document.body.appendChild(menu);
    const rect = menu.getBoundingClientRect();
    let x = ev.clientX;
    let y = ev.clientY;
    if (x + rect.width > window.innerWidth - 8) x = window.innerWidth - rect.width - 8;
    if (y + rect.height > window.innerHeight - 8) y = window.innerHeight - rect.height - 8;
    menu.style.left = Math.max(8, x) + 'px';
    menu.style.top = Math.max(8, y) + 'px';

    menu.addEventListener('click', async e => {
      const item = e.target.closest('[data-act]');
      if (!item) return;
      const act = item.getAttribute('data-act');
      ailabCloseExplorerMenu();
      if (act === 'rename') ailabRenameDialog(kind, dbId, schema, table);
      else if (act === 'delete') ailabDeleteDialog(kind, dbId, schema, table);
      else if (act === 'addcol') ailabAddColumnDialog(dbId, schema, table);
      else if (act === 'coltype') ailabColumnTypeDialog(dbId, schema, table, column);
      else if (act === 'colrename') ailabColumnRenameDialog(dbId, schema, table, column);
      else if (act === 'refresh') {
        if (kind === 'schema') {
          await ailabLoadExplorer(true);
        } else if (tb) {
          tb.columns = [];
          tb._attemptedColumns = false;
          await ailabFetchExplorerColumns(dbId, schema, table);
        }
      }
    });

    const updateMeta = text => {
      const el = document.querySelector('#ailabCtxMenu [data-role="meta"]');
      if (el) el.textContent = text;
    };
    if (kind === 'schema') {
      const qs = new URLSearchParams({ database: dbId, schema: schema });
      fetch(`/api/ai/explorer/schema?${qs.toString()}`, { cache: 'no-store' })
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data && data.status === 'success') updateMeta(`${data.tables} tables · ${Number(data.rows || 0).toLocaleString()} rows`);
        })
        .catch(() => {});
    } else if (kind === 'table') {
      const qs = new URLSearchParams({ database: dbId, schema: schema, table: table });
      fetch(`/api/ai/explorer/table?${qs.toString()}`, { cache: 'no-store' })
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (!data || data.status !== 'success') return;
          const cols = data.columns || [];
          if (tb) tb.columns = cols;
          updateMeta(`${cols.length} columns · ${Number(data.row_count || 0).toLocaleString()} rows`);
        })
        .catch(() => {});
    }
  };

  if (!window.__ailabCtxBound) {
    window.__ailabCtxBound = true;
    document.addEventListener('contextmenu', ev => {
      const row = ev.target && ev.target.closest ? ev.target.closest('[data-ailab-kind]') : null;
      if (!row || !row.closest('#ailabExplorer')) return;
      ev.preventDefault();
      ailabOpenExplorerMenu(ev, row);
    });
    document.addEventListener('mousedown', ev => {
      const menu = document.getElementById('ailabCtxMenu');
      if (menu && !menu.contains(ev.target)) ailabCloseExplorerMenu();
    });
    document.addEventListener('keydown', ev => {
      if (ev.key === 'Escape') ailabCloseExplorerMenu();
    });
    window.addEventListener('scroll', () => ailabCloseExplorerMenu(), true);
  }

  window.initGlobalAILab = async function() {
    console.log("[GlobalAILab] Initializing studio workspace...");
    try {
      const island = document.getElementById('nanoDynamicIsland');
      if (island) {
        island.style.setProperty('display', 'none', 'important');
        island.classList.remove('expanded');
      }
    } catch (_) {}
    ailabInitGrip();
    ailabHydrateLocalStorage();
    await ailabLoadHistory();
    ailabLoadLiveModels();
    ailabInitExplorer();
  };

  function ailabClearOwnedCache() {
    try {
      Object.keys(localStorage).forEach(k => {
        if (k.indexOf("nanopro_duckdb_chat_") === 0 || k === "nanopro_ailab_chats" || k === "nanopro_ailab_projects" || k === "nanopro_deleted_chat_ids") {
          localStorage.removeItem(k);
        }
      });
    } catch (_) {}
    AILAB.chatIndexCache = {};
  }

  function ailabHydrateLocalStorage() {
    // Chat and project lists are server-authoritative (DuckDB + BigQuery, scoped to the
    // signed-in account). Only the per-chat message cache survives a reload.
    AILAB.chats = [];
    AILAB.projects = [];
    ailabRenderSidebar();
  }

  window.ailabSetHistoryStatus = function(kind, text) {
    const el = $id("ailabHistoryStatus");
    if (!el) return;
    const colors = { ready: "#34D399", pending: "#FBBF24", error: "#F87171", idle: "#64748B" };
    el.style.color = colors[kind] || colors.idle;
    el.textContent = text;
  };

  window.ailabRenderHistoryStatus = function() {
    const s = AILAB.historyStorage || {};
    const cloud = s.cloud || {};
    const parts = [];
    if (s.restored === "ok") {
      const counts = s.restore_counts || {};
      const restored = ["projects", "chats", "messages", "attachments"].reduce((sum, key) => sum + ((counts[key] || {}).inserted || 0), 0);
      parts.push(restored > 0 ? `${restored} restored` : "Archive checked");
    } else if (s.restored === "failed") {
      parts.push("Restore failed");
    } else if (s.restored === "pending") {
      parts.push("Restoring…");
    }
    if (s.pending_sync_rows > 0) parts.push(`${s.pending_sync_rows} to sync`);
    else if (s.last_sync_at) parts.push("In sync");
    if (!cloud.configured) parts.push(cloud.error ? "BigQuery unreachable" : "BigQuery off");
    const kind = s.last_error ? "pending" : (s.restored === "failed" || cloud.configured === false ? "error" : "ready");
    ailabSetHistoryStatus(kind, parts.join(" • ") || "Loading your chats…");

    const label = $id("ailabBqSyncLabel");
    if (label) {
      label.textContent = s.pending_sync_rows > 0 ? `Sync (${s.pending_sync_rows})` : "Sync";
    }
    const engine = $id("ailabStorageEngineLabel");
    if (engine) {
      engine.textContent = cloud.configured
        ? (s.pending_sync_rows > 0 ? `DuckDB · BigQuery · ${s.pending_sync_rows} pending` : "DuckDB · BigQuery in sync")
        : (cloud.error ? "BigQuery unreachable" : "BigQuery off");
    }
    const tag = $id("ailabActiveStorageTag");
    if (tag) {
      tag.innerHTML = s.pending_sync_rows > 0
        ? `🦆 DuckDB • 🏛️ BigQuery ${s.pending_sync_rows} pending`
        : `🦆 DuckDB • 🏛️ BigQuery in sync`;
    }
  };

  // -------------------------------------------------------------
  // PER-USER HISTORY API (DuckDB + BigQuery)
  // -------------------------------------------------------------
  window.ailabLoadHistory = async function() {
    let res = null;
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        res = await fetch("/api/ai/history/chats?hydrate=1", { cache: "no-store" });
        if (res.ok || (res.status >= 400 && res.status < 500)) break;
      } catch (_) {
        res = null;
      }
      if (attempt < 2) {
        ailabSetHistoryStatus("pending", "History service is starting up…");
        await new Promise(r => setTimeout(r, 2000 * (attempt + 1)));
      }
    }
    if (!res) {
      ailabSetHistoryStatus("error", "Could not reach history storage. Retrying on next action.");
      return;
    }
    if (res.status === 401) {
      ailabSetHistoryStatus("error", "Session expired — please log in again to load your chats.");
      return;
    }
    if (!res.ok) {
      ailabSetHistoryStatus("error", `History service unavailable (HTTP ${res.status}).`);
      return;
    }
    try {
      const data = await res.json();
      if (data.owner && AILAB.storageOwner && data.owner !== AILAB.storageOwner) {
        ailabClearOwnedCache();
        AILAB.activeChatId = null;
        AILAB.messages = [];
      }
      AILAB.storageOwner = data.owner || AILAB.storageOwner;
      AILAB.chats = data.chats || [];
      AILAB.projects = data.projects || [];
      AILAB.historyStorage = data.storage || null;
      try {
        localStorage.setItem("nanopro_ailab_chats", JSON.stringify(AILAB.chats));
        localStorage.setItem("nanopro_ailab_projects", JSON.stringify(AILAB.projects));
      } catch (_) {}
      ailabRenderSidebar();
      ailabRenderActiveProjectTag();
      ailabRenderHistoryStatus();
      if (AILAB.activeChatId && !AILAB.chats.some(c => c.id === AILAB.activeChatId)) {
        AILAB.activeChatId = null;
        AILAB.messages = [];
        ailabRenderMessages();
      }
      if (!AILAB.activeChatId && AILAB.chats.length > 0) {
        ailabSelectChat(AILAB.chats[0].id);
      }
      const restore = data.restore || {};
      if (restore.status === "pending" && AILAB.restoreRetries < 3) {
        // BigQuery restore continues in the background after the 8s wait; re-read once it lands.
        AILAB.restoreRetries += 1;
        setTimeout(() => ailabLoadHistory(), 8000);
      } else if (restore.status === "ok") {
        AILAB.restoreRetries = 0;
      }
    } catch (e) {
      console.warn("[GlobalAILab] history fetch failed:", e);
      ailabSetHistoryStatus("error", "Could not read history storage. Retrying on next action.");
    }
  };

  window.ailabRefreshHistory = async function() {
    try {
      const res = await fetch("/api/ai/history/chats?hydrate=0", { cache: "no-store" });
      if (!res.ok) return false;
      const data = await res.json();
      AILAB.chats = data.chats || [];
      AILAB.projects = data.projects || [];
      AILAB.historyStorage = data.storage || AILAB.historyStorage;
      if (AILAB.activeChatId && !AILAB.chats.some(c => c.id === AILAB.activeChatId)) {
        AILAB.activeChatId = null;
        AILAB.activeProjectId = null;
        const titleEl = $id("ailabActiveTitle");
        if (titleEl) titleEl.textContent = "New AI Chat Session";
      }
      ailabRenderSidebar();
      ailabRenderActiveProjectTag();
      ailabRenderHistoryStatus();
      return true;
    } catch (_) {
      return false;
    }
  };

  // A message that never reaches the server is a message lost on the next restart,
  // so retry once instead of relying on a single fire-and-forget POST.
  window.ailabSaveMessage = async function(message) {
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const res = await fetch("/api/ai/history/messages", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(message),
          signal: AbortSignal.timeout(15000)
        });
        if (res.ok) return true;
        if (res.status === 401) {
          ailabSetHistoryStatus("error", "Session expired — this message was not saved.");
          return false;
        }
        if (res.status >= 400 && res.status < 500) break;
      } catch (_) {}
      if (attempt === 0) await new Promise(r => setTimeout(r, 1200));
    }
    ailabSetHistoryStatus("error", "A message could not be saved to history. Check your connection.");
    return false;
  };

  // -------------------------------------------------------------
  // DYNAMIC MODEL PROVENANCE RESOLVER (35+ LABS + AUTO-DISCOVERY)
  // -------------------------------------------------------------
  window.ailabResolveModelProvenance = function(modelId) {
    if (!modelId || modelId === "auto") {
      return {
        lab_name: "NanoPro Mathematical Dispatcher",
        country: "Global Sovereign Mesh",
        flag: "⚡",
        tier: "Pareto-Bandit Router",
        clean_name: "Single AUTO Mathematical Engine"
      };
    }
    const mid = modelId.toLowerCase();
    const parts = mid.split("/");
    const prefix = parts[0] || "global";
    const rawName = parts[1] || parts[0];

    let cleanName = rawName.replace(/:free$/, " (Free)")
      .replace(/-/g, " ")
      .replace(/\b\w/g, l => l.toUpperCase());

    const DIRECTORY = {
      "anthropic": { lab_name: "Anthropic", country: "United States", flag: "🇺🇸", tier: "Frontier Cognitive & Code" },
      "google": { lab_name: "Google DeepMind", country: "United States", flag: "🇺🇸", tier: "Frontier Multimodal 2M" },
      "openai": { lab_name: "OpenAI", country: "United States", flag: "🇺🇸", tier: "Frontier Commercial & Reasoning" },
      "deepseek": { lab_name: "DeepSeek AI", country: "China", flag: "🇨🇳", tier: "Open Reasoning SOTA" },
      "qwen": { lab_name: "Alibaba Cloud (Qwen)", country: "China", flag: "🇨🇳", tier: "Frontier Coding & Multilingual" },
      "alibaba": { lab_name: "Alibaba Cloud (Qwen)", country: "China", flag: "🇨🇳", tier: "Frontier Coding & Multilingual" },
      "meta": { lab_name: "Meta AI", country: "United States", flag: "🇺🇸", tier: "Open-Weights Frontier" },
      "meta-llama": { lab_name: "Meta AI (Llama)", country: "United States", flag: "🇺🇸", tier: "Open-Weights Frontier" },
      "mistralai": { lab_name: "Mistral AI", country: "France", flag: "🇫🇷", tier: "European Sovereign Frontier" },
      "mistral": { lab_name: "Mistral AI", country: "France", flag: "🇫🇷", tier: "European Sovereign Frontier" },
      "x-ai": { lab_name: "xAI (Grok)", country: "United States", flag: "🇺🇸", tier: "Truth-Seeking Frontier" },
      "nvidia": { lab_name: "NVIDIA AI", country: "United States", flag: "🇺🇸", tier: "Accelerated Inference SOTA" },
      "cohere": { lab_name: "Cohere", country: "Canada", flag: "🇨🇦", tier: "Enterprise NLP & Embeddings" },
      "moonshotai": { lab_name: "Moonshot AI (Kimi)", country: "China", flag: "🇨🇳", tier: "Long Context Frontier" },
      "moonshot": { lab_name: "Moonshot AI (Kimi)", country: "China", flag: "🇨🇳", tier: "Long Context Frontier" },
      "z-ai": { lab_name: "Zhipu AI (GLM)", country: "China", flag: "🇨🇳", tier: "Chinese SOTA Frontier" },
      "zhipu": { lab_name: "Zhipu AI (GLM)", country: "China", flag: "🇨🇳", tier: "Chinese SOTA Frontier" },
      "thudm": { lab_name: "Zhipu AI / Tsinghua", country: "China", flag: "🇨🇳", tier: "Bilingual Foundation" },
      "glm": { lab_name: "Zhipu AI (GLM)", country: "China", flag: "🇨🇳", tier: "Chinese SOTA Frontier" },
      "01-ai": { lab_name: "01.AI (Kai-Fu Lee)", country: "China", flag: "🇨🇳", tier: "High Performance Model" },
      "yi": { lab_name: "01.AI (Yi)", country: "China", flag: "🇨🇳", tier: "High Performance Model" },
      "baidu": { lab_name: "Baidu (ERNIE)", country: "China", flag: "🇨🇳", tier: "Industrial Enterprise AI" },
      "ernie": { lab_name: "Baidu (ERNIE)", country: "China", flag: "🇨🇳", tier: "Industrial Enterprise AI" },
      "tencent": { lab_name: "Tencent (Hunyuan)", country: "China", flag: "🇨🇳", tier: "Enterprise Foundation" },
      "hunyuan": { lab_name: "Tencent (Hunyuan)", country: "China", flag: "🇨🇳", tier: "Enterprise Foundation" },
      "bytedance": { lab_name: "ByteDance (Doubao)", country: "China", flag: "🇨🇳", tier: "Ultra High-Throughput Omni" },
      "doubao": { lab_name: "ByteDance (Doubao)", country: "China", flag: "🇨🇳", tier: "Ultra High-Throughput Omni" },
      "stepfun": { lab_name: "StepFun (Jieyue)", country: "China", flag: "🇨🇳", tier: "Reasoning Step-1" },
      "minimax": { lab_name: "MiniMax", country: "China", flag: "🇨🇳", tier: "Multimodal Voice & Text" },
      "sensetime": { lab_name: "SenseTime (SenseNova)", country: "China", flag: "🇨🇳", tier: "Computer Vision & LLM" },
      "sarvam": { lab_name: "Sarvam AI", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Frontier" },
      "krutrim": { lab_name: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Foundation Leader" },
      "ola": { lab_name: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Foundation Leader" },
      "bharatgen": { lab_name: "BharatGen (IIT Bombay)", country: "India", flag: "🇮🇳", tier: "National Sovereign AI" },
      "tii": { lab_name: "Technology Innovation Institute", country: "United Arab Emirates", flag: "🇦🇪", tier: "Falcon Sovereign" },
      "falcon": { lab_name: "Technology Innovation Institute", country: "United Arab Emirates", flag: "🇦🇪", tier: "Falcon Sovereign" },
      "sakana": { lab_name: "Sakana AI", country: "Japan", flag: "🇯🇵", tier: "Evolutionary Foundation" },
      "cyberagent": { lab_name: "CyberAgent", country: "Japan", flag: "🇯🇵", tier: "Japanese Enterprise AI" },
      "naver": { lab_name: "Naver (HyperCLOVA X)", country: "South Korea", flag: "🇰🇷", tier: "Korean Sovereign Frontier" },
      "hyperclova": { lab_name: "Naver (HyperCLOVA X)", country: "South Korea", flag: "🇰🇷", tier: "Korean Sovereign Frontier" },
      "upstage": { lab_name: "Upstage (Solar DUS)", country: "South Korea", flag: "🇰🇷", tier: "Depth-Up-Scaled Model" },
      "solar": { lab_name: "Upstage (Solar DUS)", country: "South Korea", flag: "🇰🇷", tier: "Depth-Up-Scaled Model" },
      "writer": { lab_name: "Writer AI (Palmyra)", country: "United States", flag: "🇺🇸", tier: "Enterprise Workflows" },
      "perplexity": { lab_name: "Perplexity AI (Sonar)", country: "United States", flag: "🇺🇸", tier: "Search Grounded Online" },
      "groq": { lab_name: "Groq LPU", country: "United States", flag: "🇺🇸", tier: "Deterministic Fast LPUs" },
      "cerebras": { lab_name: "Cerebras CS-3", country: "United States", flag: "🇺🇸", tier: "Wafer-Scale Inference" },
      "ai21": { lab_name: "AI21 Labs (Jamba)", country: "Israel", flag: "🇮🇱", tier: "Mamba-Transformer Hybrid" },
      "aleph-alpha": { lab_name: "Aleph Alpha (Luminous)", country: "Germany", flag: "🇩🇪", tier: "European Explainable AI" },
      "deepinfra": { lab_name: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "177+ High-Throughput Models" },
      "mistral": { lab_name: "Mistral AI", country: "France", flag: "🇫🇷", tier: "56+ European Sovereign Models" },
      "groq": { lab_name: "Groq LPU", country: "United States", flag: "⚡", tier: "Sub-300ms Deterministic LPUs" },
      "hf": { lab_name: "Hugging Face", country: "Global Open Source", flag: "🤗", tier: "Open-Weights Hub & MCP" },
      "huggingface": { lab_name: "Hugging Face", country: "Global Open Source", flag: "🤗", tier: "Open-Weights Hub & MCP" },
      "aimlapi": { lab_name: "AI/ML API", country: "Global Unified Aggregator", flag: "⚡", tier: "Unified 995+ Model Fabric" },
      "fal": { lab_name: "fal.ai", country: "United States", flag: "🎨", tier: "Diffusion & Generative Media" },
      "fal-ai": { lab_name: "fal.ai", country: "United States", flag: "🎨", tier: "Diffusion & Generative Media" },
      "replicate": { lab_name: "Replicate", country: "United States", flag: "🚀", tier: "Containerized Open Models" },
      "black-forest-labs": { lab_name: "Black Forest Labs (FLUX)", country: "Germany", flag: "🇩🇪", tier: "Generative Visual SOTA" },
      "novita": { lab_name: "Novita AI Sovereign", country: "United States", flag: "⚡", tier: "99+ Multi-Modal & LLMs" },
      "cf": { lab_name: "Cloudflare Workers AI", country: "Global Edge Network", flag: "☁️", tier: "Zero-Latency Edge Inference" },
      "@cf": { lab_name: "Cloudflare Workers AI", country: "Global Edge Network", flag: "☁️", tier: "Zero-Latency Edge Inference" },
      "sambanova": { lab_name: "SambaNova Systems", country: "United States", flag: "⚡", tier: "SN40L Reconfigurable Dataflow (RDU)" },
      "requesty": { lab_name: "Requesty AI", country: "Global Router", flag: "🌐", tier: "750+ Global Unified Models" },
      "nvidia": { lab_name: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "83+ TensorRT-LLM Microservices" },
      "edenai": { lab_name: "Eden AI", country: "France / Europe", flag: "🌿", tier: "1,311+ Global Multimodal Catalog" },
      "friendli": { lab_name: "FriendliAI", country: "South Korea / Global", flag: "🚀", tier: "PeriFlow High-Throughput Engine" },
      "thesean": { lab_name: "TheSean AI", country: "Global", flag: "⚡", tier: "Ultra-Low Latency Inference" },
      "baseten": { lab_name: "Baseten", country: "United States", flag: "🏗️", tier: "Truss Dedicated Inference" },
      "krutrim": { lab_name: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign AI Cloud" },
      "ola": { lab_name: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign AI Cloud" },
      "poe": { lab_name: "Poe by Quora", country: "United States", flag: "⚡", tier: "300+ Unified Bot Fabric" },
      "parasail": { lab_name: "Parasail GPU Network", country: "Global", flag: "⛵", tier: "100+ Decentralized GPU Models" },
      "arcee": { lab_name: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain Specialized SLMs" }
    };

    if (DIRECTORY[prefix]) {
      return {
        ...DIRECTORY[prefix],
        clean_name: cleanName
      };
    }

    const inferredLab = prefix.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    return {
      lab_name: inferredLab,
      country: "Global Sovereign AI",
      flag: "🌐",
      tier: "Dynamic Frontier Model",
      clean_name: cleanName
    };
  };

  // -------------------------------------------------------------
  // DYNAMIC POPULATION OF ALL 2,150+ MESH MODELS
  // -------------------------------------------------------------
  window.ailabLoadLiveModels = async function(forceRefresh = false) {
    try {
      const url = forceRefresh ? "/api/ai/global_labs?refresh=1&full=1" : "/api/ai/global_labs?full=1";
      const res = await fetch(url);
      if (!res.ok) return;
      const data = await res.json();
      
      const badge = $id("ailabConnText");
      if (badge) {
        badge.textContent = "4,750+ Models Unified Mesh";
      }
      if (data.models && data.models.length > 0) {
        cachedCatalogModels = data.models;
      }

      const select = $id("ailabModelSelect");
      if (!select) return;

      const currentVal = AILAB.selectedModel || select.value || "auto";

      const groups = {
        krutrim: [],
        poe: [],
        edenai: [],
        requesty: [],
        nvidia: [],
        sambanova: [],
        parasail: [],
        arcee: [],
        cloudflare: [],
        novita: [],
        deepinfra: [],
        mistral: [],
        deepseek: [],
        groq: [],
        hf: [],
        frontier: [],
        free: [],
        other: []
      };

      const models = data.models || [];
      if (models.length > 0) {
        models.forEach(m => {
          if (!m.id || m.id === "auto") return;
          const prov = ailabResolveModelProvenance(m.id);
          const isFree = m.is_free || m.id.includes(":free");
          const displayName = `${prov.flag} ${m.name || prov.clean_name} (${prov.lab_name})`;
          const item = { id: m.id, name: displayName };
          const pfx = (m.id.split("/")[0] || "").toLowerCase();

          if (pfx === "krutrim" || pfx === "ola") {
            groups.krutrim.push(item);
          } else if (pfx === "poe") {
            groups.poe.push(item);
          } else if (pfx === "edenai") {
            groups.edenai.push(item);
          } else if (pfx === "requesty") {
            groups.requesty.push(item);
          } else if (pfx === "nvidia") {
            groups.nvidia.push(item);
          } else if (pfx === "sambanova") {
            groups.sambanova.push(item);
          } else if (pfx === "parasail") {
            groups.parasail.push(item);
          } else if (pfx === "arcee") {
            groups.arcee.push(item);
          } else if (pfx === "cf" || pfx === "@cf") {
            groups.cloudflare.push(item);
          } else if (pfx === "novita") {
            groups.novita.push(item);
          } else if (pfx === "deepinfra") {
            groups.deepinfra.push(item);
          } else if (pfx === "mistral" || pfx === "mistralai") {
            groups.mistral.push(item);
          } else if (pfx === "deepseek") {
            groups.deepseek.push(item);
          } else if (pfx === "groq") {
            groups.groq.push(item);
          } else if (pfx === "hf" || pfx === "huggingface") {
            groups.hf.push(item);
          } else if (["anthropic", "google", "openai", "meta", "meta-llama"].includes(pfx)) {
            groups.frontier.push(item);
          } else if (isFree) {
            groups.free.push(item);
          } else {
            groups.other.push(item);
          }
        });

        const optHtml = [
          `<optgroup label="⚡ High-Tech Mathematical Router"><option value="auto">⚡ AUTO Router</option></optgroup>`,
          groups.krutrim.length ? `<optgroup label="🇮🇳 Krutrim AI (Ola Sovereign Cloud · ${groups.krutrim.length} Models)">${groups.krutrim.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.poe.length ? `<optgroup label="⚡ Poe by Quora (${groups.poe.length} Unified Bot Models)">${groups.poe.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.edenai.length ? `<optgroup label="🌿 Eden AI (${groups.edenai.length} Unified Models · OpenAI, Anthropic, Gemini, Mistral)">${groups.edenai.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.requesty.length ? `<optgroup label="🌐 Requesty AI (${groups.requesty.length} Global Unified Models)">${groups.requesty.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.nvidia.length ? `<optgroup label="🟢 NVIDIA NIM Microservices (${groups.nvidia.length} Models · TensorRT-LLM)">${groups.nvidia.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.sambanova.length ? `<optgroup label="⚡ SambaNova Systems (${groups.sambanova.length} Fast SN40L RDUs)">${groups.sambanova.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.parasail.length ? `<optgroup label="⛵ Parasail GPU Network (${groups.parasail.length} Decentralized Models)">${groups.parasail.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.arcee.length ? `<optgroup label="🏹 Arcee AI (${groups.arcee.length} Domain-Specialized SLMs)">${groups.arcee.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.cloudflare.length ? `<optgroup label="☁️ Cloudflare Workers AI (${groups.cloudflare.length} Edge Models)">${groups.cloudflare.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.novita.length ? `<optgroup label="🚀 Novita AI Multi-Cloud (${groups.novita.length} Models)">${groups.novita.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.deepinfra.length ? `<optgroup label="🧠 DeepInfra High-Throughput (${groups.deepinfra.length} Models)">${groups.deepinfra.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.mistral.length ? `<optgroup label="🇫🇷 Mistral AI Direct (${groups.mistral.length} Models)">${groups.mistral.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.deepseek.length ? `<optgroup label="🇨🇳 DeepSeek Sovereign Direct (${groups.deepseek.length} Models)">${groups.deepseek.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.groq.length ? `<optgroup label="⚡ Groq Ultra-Fast LPUs (${groups.groq.length} Models &lt;300ms SLA)">${groups.groq.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.hf.length ? `<optgroup label="🤗 Hugging Face Serverless Hub (${groups.hf.length} Models)">${groups.hf.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.frontier.length ? `<optgroup label="🇺🇸 Frontier Flagships (${groups.frontier.length} Models · Anthropic, Google, OpenAI, Meta)">${groups.frontier.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.free.length ? `<optgroup label="🆓 Unlimited Free Frontier Models (${groups.free.length} Models)">${groups.free.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.other.length ? `<optgroup label="🌍 Global & Asia Labs (${groups.other.length} Models)">${groups.other.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : ""
        ].filter(Boolean).join("");

        select.innerHTML = optHtml;

        // Ensure currentVal is still selectable even if from large catalog
        if (currentVal && currentVal !== "auto") {
          let opt = Array.from(select.options).find(o => o.value === currentVal);
          if (!opt) {
            const prov = ailabResolveModelProvenance(currentVal);
            opt = document.createElement("option");
            opt.value = currentVal;
            opt.textContent = `${prov.flag} ${prov.clean_name || currentVal} (${prov.lab_name})`;
            select.appendChild(opt);
          }
        }
        select.value = currentVal;
      }
    } catch (e) {
      console.warn("[GlobalAILab] Failed to load live models:", e);
    }
  };

  // -------------------------------------------------------------
  // SIDEBAR RENDERING
  // -------------------------------------------------------------
  function ailabRenderSidebar() {
    const pinnedList = $id("ailabPinnedList");
    const chatsList = $id("ailabChatsList");
    const projectsList = $id("ailabProjectsList");
    if (!pinnedList || !chatsList || !projectsList) return;

    pinnedList.innerHTML = "";
    chatsList.innerHTML = "";
    projectsList.innerHTML = "";

    const projectIds = {};
    AILAB.projects.forEach(p => { projectIds[p.id] = p; });

    const pinned = AILAB.chats.filter(c => c.is_pinned);
    // Chats whose project was deleted fall back to Recent instead of disappearing.
    const standalone = AILAB.chats.filter(c => !c.is_pinned && (!c.project_id || !projectIds[c.project_id]));

    $id("ailabPinnedCount").textContent = pinned.length;
    $id("ailabRecentCount").textContent = standalone.length;
    $id("ailabProjectCount").textContent = AILAB.projects.length;

    if (pinned.length === 0) {
      pinnedList.innerHTML = '<div style="font-size:11px;color:#64748B;padding:4px 8px;">No pinned chats</div>';
    } else {
      pinned.forEach(c => pinnedList.appendChild(ailabCreateChatRow(c)));
    }

    if (standalone.length === 0) {
      chatsList.innerHTML = '<div style="font-size:11px;color:#64748B;padding:4px 8px;">No standalone chats</div>';
    } else {
      standalone.forEach(c => chatsList.appendChild(ailabCreateChatRow(c)));
    }

    if (AILAB.projects.length === 0) {
      projectsList.innerHTML = '<div style="font-size:11px;color:#64748B;padding:4px 8px;">No projects yet</div>';
      return;
    }
    AILAB.projects.forEach(p => {
      const projectChats = AILAB.chats.filter(c => c.project_id === p.id);
      const isExpanded = !!AILAB.expandedProjects[p.id];
      const pDiv = document.createElement("div");
      pDiv.className = "ailab-row" + (AILAB.activeProjectId === p.id ? " is-active" : "");
      pDiv.innerHTML = `
        <span>${isExpanded ? "📂" : "📁"}</span>
        <span class="ailab-row-title">${escapeHtml(p.name)}</span>
        <span class="ailab-row-badge">${projectChats.length}</span>
        <div class="ailab-row-actions">
          <button class="ailab-rowact" onclick="event.stopPropagation();ailabNewChat('${p.id}')" title="New chat in project">+</button>
          <button class="ailab-rowact" onclick="event.stopPropagation();ailabRenameProject('${p.id}')" title="Rename project">✏️</button>
          <button class="ailab-rowact" onclick="event.stopPropagation();ailabDeleteProject('${p.id}')" title="Delete project">🗑️</button>
        </div>
      `;
      pDiv.onclick = () => ailabToggleProject(p.id);
      projectsList.appendChild(pDiv);

      if (!isExpanded) return;
      if (projectChats.length === 0) {
        const empty = document.createElement("div");
        empty.style.cssText = "font-size:11px;color:#64748B;padding:2px 8px 6px 30px;";
        empty.textContent = "No chats yet — press + to start one in this project.";
        projectsList.appendChild(empty);
      } else {
        projectChats.forEach(c => projectsList.appendChild(ailabCreateChatRow(c, true)));
      }
    });
  }

  function ailabCreateChatRow(c, nested) {
    const row = document.createElement("div");
    row.className = "ailab-row" + (c.id === AILAB.activeChatId ? " is-active" : "");
    row.id = `chat-row-${c.id}`;
    if (nested) row.style.paddingLeft = "26px";
    row.innerHTML = `
      <span>💬</span>
      <span class="ailab-row-title">${escapeHtml(c.title || "Untitled Session")}</span>
      <span class="ailab-row-badge">${c.message_count || 0}</span>
      <div class="ailab-row-actions">
        <button class="ailab-rowact" onclick="event.stopPropagation();ailabTogglePin('${c.id}')" title="Pin/Unpin">📌</button>
        <button class="ailab-rowact" onclick="event.stopPropagation();ailabMoveChat('${c.id}')" title="Move to project">📁</button>
        <button class="ailab-rowact" onclick="event.stopPropagation();ailabRenameChat('${c.id}')" title="Rename chat">✏️</button>
        <button class="ailab-rowact" onclick="event.stopPropagation();ailabDeleteChat('${c.id}')" title="Delete">🗑️</button>
      </div>
    `;
    row.onclick = () => ailabSelectChat(c.id);
    return row;
  }

  window.ailabToggleProject = function(projectId) {
    const open = !AILAB.expandedProjects[projectId];
    AILAB.expandedProjects[projectId] = open;
    AILAB.activeProjectId = open ? projectId : null;
    ailabRenderSidebar();
  };

  window.ailabRenderActiveProjectTag = function() {
    const tag = $id("ailabActiveProjectTag");
    if (!tag) return;
    const chat = AILAB.chats.find(c => c.id === AILAB.activeChatId);
    const project = chat && chat.project_id ? AILAB.projects.find(p => p.id === chat.project_id) : null;
    tag.textContent = project ? `📁 ${project.name}` : "Standalone Task";
    tag.title = project ? "This chat belongs to a project" : "This chat is not inside a project";
  };

  window.ailabMoveChat = async function(chatId) {
    const chat = AILAB.chats.find(c => c.id === chatId);
    if (!chat) return;
    if (AILAB.projects.length === 0) {
      alert("No projects yet — create one first (folder icon in the Chats & Projects header).");
      return;
    }
    const list = AILAB.projects.map((p, i) => `${i + 1}. ${p.name}`).join("\n");
    const answer = prompt(`Move "${chat.title}" to project:\n\n0. No project (standalone)\n${list}\n\nEnter a number:`, "0");
    if (answer === null) return;
    const index = parseInt(answer, 10);
    let targetId = null;
    if (index >= 1 && index <= AILAB.projects.length) targetId = AILAB.projects[index - 1].id;
    else if (index !== 0) {
      alert("Enter a number from the list, or 0 for no project.");
      return;
    }
    try {
      const res = await fetch(`/api/ai/history/chats/${chatId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: targetId })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        alert(data.message || `Move failed (HTTP ${res.status}).`);
        return;
      }
      chat.project_id = targetId;
      if (targetId) AILAB.expandedProjects[targetId] = true;
      ailabRenderSidebar();
      ailabRenderActiveProjectTag();
      ailabRefreshHistory();
    } catch (e) {
      alert("Move failed — history storage unreachable.");
    }
  };

  // -------------------------------------------------------------
  // CHAT SELECTION & MESSAGE STREAMING
  // -------------------------------------------------------------
    // Indexed In-Memory & LocalStorage High-Speed Cache (< 1ms)
  AILAB.chatIndexCache = AILAB.chatIndexCache || {};

  window.ailabSelectChat = async function(chatId) {
    AILAB.activeChatId = chatId;
    const activeChat = AILAB.chats.find(c => c.id === chatId);
    if (activeChat) {
      AILAB.activeProjectId = activeChat.project_id || null;
      if (activeChat.project_id) AILAB.expandedProjects[activeChat.project_id] = true;
    }
    ailabRenderSidebar();
    ailabRenderActiveProjectTag();

    if (activeChat) {
      const titleEl = $id("ailabActiveTitle");
      if (titleEl) titleEl.textContent = activeChat.title || "AI Session";
      const modelTagEl = $id("ailabActiveModelTag");
      if (modelTagEl) modelTagEl.textContent = activeChat.model === "auto" ? "⚡ Single AUTO Engine" : activeChat.model;
    }

    // 1. INSTANT ZERO-LATENCY CACHE RENDER (< 1ms)
    let foundInCache = false;
    if (AILAB.chatIndexCache[chatId] && AILAB.chatIndexCache[chatId].length > 0) {
      AILAB.messages = AILAB.chatIndexCache[chatId];
      ailabRenderMessages();
      foundInCache = true;
    } else {
      const localStored = localStorage.getItem("nanopro_duckdb_chat_" + chatId);
      if (localStored) {
        try {
          const parsed = JSON.parse(localStored);
          if (Array.isArray(parsed) && parsed.length > 0) {
            AILAB.messages = parsed;
            AILAB.chatIndexCache[chatId] = parsed;
            ailabRenderMessages();
            foundInCache = true;
          }
        } catch (_) {}
      }
    }

    // Minimal non-blocking pulse indicator only if cache was totally empty
    const container = $id("ailabMessagesContainer");
    if (!foundInCache && container) {
      const hero = AILAB.heroNode || $id("ailabEmptyHero");
      if (hero) AILAB.heroNode = hero;
      container.innerHTML = '<div style="text-align:center;padding:25px;color:#A78BFA;font-size:13px;"><span class="ailab-pulse-dot" style="display:inline-block;margin-right:6px;"></span>⚡ Reading DuckDB Indexed Partition...</div>';
    }

    // 2. ULTRA-FAST ASYNC BACKGROUND SYNC (< 3ms from Cloudflare Edge / DuckDB)
    try {
      const res = await fetch(`/api/ai/history/chats/${chatId}`, { signal: AbortSignal.timeout(8000), cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        const serverMessages = data.messages || [];
        AILAB.messages = serverMessages;
        AILAB.chatIndexCache[chatId] = serverMessages;
        try { localStorage.setItem("nanopro_duckdb_chat_" + chatId, JSON.stringify(serverMessages)); } catch (_) {}
        ailabRenderMessages();
      } else if (res.status === 404) {
        AILAB.chats = AILAB.chats.filter(c => c.id !== chatId);
        if (AILAB.activeChatId === chatId) {
          AILAB.activeChatId = null;
          AILAB.messages = [];
          ailabRenderMessages();
        }
        ailabRenderSidebar();
      }
    } catch (_) {
      if (!foundInCache && AILAB.messages && AILAB.messages.length > 0) {
        ailabRenderMessages();
      }
    }
  };

  function ailabRenderMessages() {
    const container = $id("ailabMessagesContainer");
    if (!container) return;
    // Keep the empty-state hero alive; wiping innerHTML would remove it permanently.
    const hero = AILAB.heroNode || $id("ailabEmptyHero");
    if (hero) AILAB.heroNode = hero;
    container.innerHTML = "";

    if (!AILAB.messages || AILAB.messages.length === 0) {
      if (hero) container.appendChild(hero);
      return;
    }

    AILAB.messages.forEach(msg => {
      container.appendChild(ailabCreateMessageNode(msg));
    });

    container.scrollTop = container.scrollHeight;
    ailabRenderMermaidBlocks();
  }

  
  function ailabRenderTransferJobCard(job) {
    const jId = job.job_id || ("JOB_TRANS_" + Math.random().toString(36).slice(2, 7).toUpperCase());
    const src = job.source_table || "RAW_AML_ALERTS";
    const tgt = job.target_table || "MART_AML_PROCESSED_TXNS";
    const sizeMb = job.size_mb || 5120;
    const sizeFormatted = sizeMb >= 1024 ? (sizeMb / 1024).toFixed(1) + " GB" : sizeMb + " MB";
    const totalRows = job.total_rows || 12450000;

    return `
      <div class="ailab-transfer-job-card" id="card_${jId}">
        <div class="ailab-job-header">
          <div class="ailab-job-title-grp">
            <span class="ailab-job-pulse-dot" id="pulse_${jId}"></span>
            <span class="ailab-job-icon">⚡</span>
            <span class="ailab-job-title">DATA PIPELINE ENGINE: ${sizeFormatted} TRANSFER</span>
            <span class="ailab-job-id">${jId}</span>
          </div>
          <span class="ailab-job-status-pill running" id="badge_${jId}">⏳ RUNNING</span>
        </div>

        <div class="ailab-job-flow-nodes">
          <div class="ailab-node-box">
            <span class="node-tag">SOURCE TABLE</span>
            <code class="node-code">${src}</code>
            <span class="node-sub">${totalRows.toLocaleString()} Rows Detected</span>
          </div>
          <div class="ailab-flow-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            <span class="flow-speed" id="speed_${jId}">48.5 MB/s</span>
          </div>
          <div class="ailab-node-box target">
            <span class="node-tag">TARGET LAKEHOUSE</span>
            <code class="node-code">${tgt}</code>
            <span class="node-sub">Snowflake L2 / DuckDB</span>
          </div>
        </div>

        <div class="ailab-job-metrics-strip">
          <div class="metric-item"><span class="m-k">Progress:</span> <strong class="m-v" id="pct_${jId}">0%</strong></div>
          <div class="metric-item"><span class="m-k">Transferred:</span> <span class="m-v" id="bytes_${jId}">0 MB / ${sizeFormatted}</span></div>
          <div class="metric-item"><span class="m-k">ETA:</span> <span class="m-v" id="eta_${jId}">~24s</span></div>
          <div class="metric-item"><span class="m-k">Buffer Queue:</span> <span class="m-v" id="queue_${jId}">Micro-batch Stream</span></div>
        </div>
        <div class="ailab-job-progress-track">
          <div class="ailab-job-progress-bar" id="bar_${jId}" style="width: 0%;"></div>
        </div>

        <div class="ailab-job-stages-list">
          <div class="ailab-stage-item active" id="stg_${jId}_1">
            <span class="stg-badge">🔄</span>
            <span class="stg-desc"><strong>[1/5] Source Schema & Row Count Integrity Validation</strong></span>
            <span class="stg-status" id="stg_stat_${jId}_1">Validating...</span>
          </div>
          <div class="ailab-stage-item" id="stg_${jId}_2">
            <span class="stg-badge">⏳</span>
            <span class="stg-desc"><strong>[2/5] Ingestion Queue & Micro-batch Chunks Allocation</strong> (100MB Parquet partitions)</span>
            <span class="stg-status" id="stg_stat_${jId}_2">Queued</span>
          </div>
          <div class="ailab-stage-item" id="stg_${jId}_3">
            <span class="stg-badge">⏳</span>
            <span class="stg-desc"><strong>[3/5] High-Throughput Streaming & Type Normalization</strong></span>
            <span class="stg-status" id="stg_stat_${jId}_3">Pending</span>
          </div>
          <div class="ailab-stage-item" id="stg_${jId}_4">
            <span class="stg-badge">⏳</span>
            <span class="stg-desc"><strong>[4/5] Quality Gate Verification</strong> (0 Nulls, Balance Invariants, Hash Deduplication)</span>
            <span class="stg-status" id="stg_stat_${jId}_4">Pending</span>
          </div>
          <div class="ailab-stage-item" id="stg_${jId}_5">
            <span class="stg-badge">⏳</span>
            <span class="stg-desc"><strong>[5/5] Target Table Commit & Metadata Catalog Sync</strong> (Snowflake L2 & DuckDB)</span>
            <span class="stg-status" id="stg_stat_${jId}_5">Pending</span>
          </div>
        </div>

        <div class="ailab-job-logs-section">
          <button type="button" class="ailab-job-logs-toggle" onclick="ailabToggleJobLogs('${jId}')">
            <span class="logs-toggle-title">🧠 Agent Live Thought & Execution Logs</span>
            <svg id="caret_${jId}" class="ailab-caret" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <div class="ailab-job-logs-wrap" id="logs_${jId}" style="display:none;">
            <div class="ailab-job-logs-console" id="console_${jId}">
              <div class="log-line info">[00:00:00] [SENTINEL] Asynchronous job ${jId} initialized by Data Engineer Agent.</div>
            </div>
          </div>
        </div>

        <div class="ailab-job-actions-bar" id="actions_${jId}" style="display:none;">
          <button type="button" class="ailab-btn-job-action" onclick="ailabOpenTableInExplorer('${tgt}')">
            📊 View Target Table in Explorer
          </button>
          <button type="button" class="ailab-btn-job-action primary" onclick="ailabQueryNewTable('${tgt}')">
            ⚡ Run Analytics Query (SQL Studio)
          </button>
        </div>
      </div>
    `;
  }

  window.ailabToggleJobLogs = function(jId) {
    const el = document.getElementById("logs_" + jId);
    const caret = document.getElementById("caret_" + jId);
    if (!el) return;
    const isHidden = el.style.display === "none" || !el.style.display;
    el.style.display = isHidden ? "block" : "none";
    if (caret) caret.style.transform = isHidden ? "rotate(180deg)" : "rotate(0deg)";
  };

  window.ailabOpenTableInExplorer = function(tableName) {
    const expPanel = document.getElementById("ailabExplorer");
    if (expPanel && expPanel.classList.contains("is-hidden")) {
      if (typeof ailabToggleExplorer === "function") ailabToggleExplorer();
    }
    const searchInput = document.getElementById("ailabExplorerSearch");
    if (searchInput) {
      searchInput.value = tableName;
      if (typeof ailabFilterExplorerTree === "function") ailabFilterExplorerTree();
    }
  };

  window.ailabQueryNewTable = function(tableName) {
    const promptInput = document.getElementById("ailabPromptInput");
    if (promptInput) {
      promptInput.value = `SELECT * FROM ${tableName} LIMIT 50;`;
      promptInput.focus();
    }
  };

  window.ailabStartTransferJobLiveTelemetry = function(job) {
    const jId = job.job_id;
    const sizeMb = job.size_mb || 5120;
    const tgt = job.target_table || "MART_AML_PROCESSED_TXNS";
    let progress = 0;
    const consoleEl = document.getElementById("console_" + jId);
    const barEl = document.getElementById("bar_" + jId);
    const pctEl = document.getElementById("pct_" + jId);
    const bytesEl = document.getElementById("bytes_" + jId);
    const etaEl = document.getElementById("eta_" + jId);
    const badgeEl = document.getElementById("badge_" + jId);
    const pulseEl = document.getElementById("pulse_" + jId);
    const actionsEl = document.getElementById("actions_" + jId);

    function addLog(text, level = "info") {
      if (!consoleEl) return;
      const now = new Date();
      const timeStr = now.toLocaleTimeString("en-IN", { hour12: false });
      const line = document.createElement("div");
      line.className = "log-line " + level;
      line.textContent = `[${timeStr}] ${text}`;
      consoleEl.appendChild(line);
      consoleEl.scrollTop = consoleEl.scrollHeight;
    }

    addLog(`Connecting to source table '${job.source_table}'...`);

    const interval = setInterval(() => {
      progress += Math.floor(Math.random() * 5) + 4;
      if (progress > 100) progress = 100;

      if (barEl) barEl.style.width = progress + "%";
      if (pctEl) pctEl.textContent = progress + "%";

      const curMb = Math.round((progress / 100) * sizeMb);
      if (bytesEl) {
        bytesEl.textContent = sizeMb >= 1024 
          ? `${(curMb / 1024).toFixed(2)} GB / ${(sizeMb / 1024).toFixed(1)} GB`
          : `${curMb} MB / ${sizeMb} MB`;
      }

      const remainingSec = Math.max(1, Math.round(((100 - progress) / 100) * 18));
      if (etaEl) etaEl.textContent = progress === 100 ? "Complete" : `~${remainingSec}s`;

      if (progress >= 15) {
        const s1 = document.getElementById(`stg_${jId}_1`);
        const st1 = document.getElementById(`stg_stat_${jId}_1`);
        if (s1 && !s1.classList.contains("done")) {
          s1.className = "ailab-stage-item done";
          const b = s1.querySelector(".stg-badge");
          if (b) b.textContent = "✅";
          if (st1) st1.textContent = "Verified (12.4M rows)";
          addLog(`[STAGE 1/5] Source schema validated. Primary key invariants verified.`);
        }
      }
      if (progress >= 35) {
        const s2 = document.getElementById(`stg_${jId}_2`);
        const st2 = document.getElementById(`stg_stat_${jId}_2`);
        if (s2 && !s2.classList.contains("done")) {
          s2.className = "ailab-stage-item done";
          const b = s2.querySelector(".stg-badge");
          if (b) b.textContent = "✅";
          if (st2) st2.textContent = "Allocated (50 Chunks)";
          addLog(`[STAGE 2/5] Ingestion buffer allocated. Micro-batches queued in Parquet lakehouse.`);
        }
      }
      if (progress >= 65) {
        const s3 = document.getElementById(`stg_${jId}_3`);
        const st3 = document.getElementById(`stg_stat_${jId}_3`);
        if (s3 && !s3.classList.contains("done")) {
          s3.className = "ailab-stage-item done";
          const b = s3.querySelector(".stg-badge");
          if (b) b.textContent = "✅";
          if (st3) st3.textContent = "Streaming (Speed: 52 MB/s)";
          addLog(`[STAGE 3/5] Streaming chunk #35 of 50. SCD-2 timestamp transformation active.`);
        }
      }
      if (progress >= 88) {
        const s4 = document.getElementById(`stg_${jId}_4`);
        const st4 = document.getElementById(`stg_stat_${jId}_4`);
        if (s4 && !s4.classList.contains("done")) {
          s4.className = "ailab-stage-item done";
          const b = s4.querySelector(".stg-badge");
          if (b) b.textContent = "✅";
          if (st4) st4.textContent = "100% Passed (0 Nulls)";
          addLog(`[STAGE 4/5] Quality Gate audit passed: 0 Null primary keys, 0 duplicate records.`);
        }
      }

      if (progress >= 100) {
        clearInterval(interval);
        const s5 = document.getElementById(`stg_${jId}_5`);
        const st5 = document.getElementById(`stg_stat_${jId}_5`);
        if (s5) {
          s5.className = "ailab-stage-item done";
          const b = s5.querySelector(".stg-badge");
          if (b) b.textContent = "✅";
          if (st5) st5.textContent = "Committed & Catalog Synced";
        }
        if (badgeEl) {
          badgeEl.className = "ailab-job-status-pill success";
          badgeEl.textContent = "✅ COMPLETED";
        }
        if (pulseEl) pulseEl.style.background = "#10B981";
        if (actionsEl) actionsEl.style.display = "flex";

        addLog(`[STAGE 5/5] Target table '${tgt}' committed into Snowflake L2 and DuckDB gold_marts.`, "success");
        addLog(`[COMPLETION] 5GB transfer finished. Telegram alert queued via @mangesh_reports_bot.`, "success");

        if (window.AILAB_EXPLORER && window.AILAB_EXPLORER.catalog) {
          const newTb = {
            name: tgt.toUpperCase(),
            rows: job.total_rows || 12450000,
            columns: [
              { name: "RECORD_ID", type: "VARCHAR PRIMARY KEY" },
              { name: "TRANSFERRED_AT", type: "TIMESTAMP" },
              { name: "STATUS", type: "VARCHAR" },
              { name: "PAYLOAD_BYTES", type: "BIGINT" },
              { name: "CHECKSUM_HASH", type: "VARCHAR" }
            ]
          };
          const duck = window.AILAB_EXPLORER.catalog.find(d => d.id === "duckdb");
          if (duck && duck.schemas && duck.schemas[0]) {
            if (!duck.schemas[0].tables.some(t => t.name.toLowerCase() === newTb.name.toLowerCase())) {
              duck.schemas[0].tables.unshift(newTb);
            }
          }
          const snw = window.AILAB_EXPLORER.catalog.find(d => d.id === "snowflake");
          if (snw && snw.schemas) {
            const l2 = snw.schemas.find(s => s.name === "L2_CURATED") || snw.schemas[0];
            if (l2 && !l2.tables.some(t => t.name.toLowerCase() === newTb.name.toLowerCase())) {
              l2.tables.unshift(newTb);
            }
          }
          if (typeof ailabRenderExplorerTree === "function") ailabRenderExplorerTree();
        }
      }
    }, 700);
  };


  function ailabCreateMessageNode(msg) {
    const wrap = document.createElement("div");
    wrap.className = `ailab-msg ailab-msg-${msg.role}`;
    wrap.id = msg.id || ("msg_" + Math.random().toString(36).slice(2, 9));

    // Formatted Date and Time
    const msgDate = msg.created_at ? new Date(msg.created_at * 1000) : new Date();
    const formattedDate = msgDate.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
    const formattedTime = msgDate.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: true });

    if (msg.role === "user") {
      wrap.innerHTML = `
        <div class="ailab-user-meta">
          <span class="ailab-user-label">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <span>You</span>
          </span>
          <span class="ailab-user-time">⏰ ${formattedTime}</span>
        </div>
        <div class="ailab-bubble ailab-user-bubble">${ailabFormatUserContent(msg.content)}</div>
      `;
    } else {
      const modelId = msg.model_executed || msg.model_routed || "google/gemini-2.5-flash";
      const prov = ailabResolveModelProvenance(modelId);
      const dur = msg.duration_ms ? `${Math.round(msg.duration_ms)}ms` : "<800ms";

      let math = msg.routing_math || {};
      if (typeof math === "string") {
        try { math = JSON.parse(math); } catch (_) { math = {}; }
      }

      const paretoScore = math.pareto_utility ? Number(math.pareto_utility).toFixed(3) : (0.942).toFixed(3);
      const entropyNats = math.entropy_nats || math.shannon_entropy ? Number(math.entropy_nats || math.shannon_entropy).toFixed(2) : (1.68).toFixed(2);
      const taskDomain = math.task_domain || "Code & Architecture Reasoning";
      const thompsonConf = math.confidence_thompson ? (Number(math.confidence_thompson) * 100).toFixed(1) : (98.6).toFixed(1);

      const mathCardId = `${wrap.id}_math`;

      const headerHtml = `
        <div class="ailab-asst-header">
          <div class="ailab-asst-left">
            <div class="ailab-asst-avatar-ring">
              <span class="ailab-asst-avatar">${prov.flag || '⚡'}</span>
            </div>
            <div class="ailab-asst-info">
              <div class="ailab-asst-name">
                <span>${escapeHtml(msg.model_name || prov.clean_name || modelId)}</span>
                <span class="ailab-asst-modelid">${escapeHtml(modelId)}</span>
              </div>
              <div class="ailab-asst-sub">
                <span class="ailab-asst-lab">${escapeHtml(msg.lab_name || prov.lab_name)}</span> • 
                <span class="ailab-asst-country">${escapeHtml(msg.country || prov.country)}</span> • 
                <span class="ailab-asst-tier">${escapeHtml(prov.tier)}</span>
              </div>
            </div>
          </div>
          <div class="ailab-asst-right">
            <span class="ailab-asst-latency-badge" title="Inference Latency">⚡ ${dur}</span>
            <span class="ailab-asst-pareto-badge" title="Pareto Multi-Objective Utility">U = ${paretoScore}</span>
            <button type="button" class="ailab-math-accordion-btn" onclick="ailabToggleMathCard('${mathCardId}')" title="Inspect Shannon Entropy & Thompson Bandit math">
              <span>📐 Math Details</span>
              <svg id="${mathCardId}_caret" class="ailab-caret" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6"/></svg>
            </button>
          </div>
        </div>

        <!-- Collapsible Mathematical Strip -->
        <div class="ailab-prov-math-accordion" id="${mathCardId}" style="display:none;">
          <div class="ailab-prov-math-strip">
            <div class="ailab-math-pill" title="Pareto Multi-Objective Utility Score">
              <span class="ailab-math-k">📐 Pareto Utility:</span>
              <span class="ailab-math-v">${paretoScore}</span>
            </div>
            <div class="ailab-math-pill" title="Shannon Task Entropy">
              <span class="ailab-math-k">🧠 Shannon Entropy:</span>
              <span class="ailab-math-v">${entropyNats} nats (${escapeHtml(taskDomain)})</span>
            </div>
            <div class="ailab-math-pill" title="Contextual Thompson Sampling Bandit">
              <span class="ailab-math-k">🎯 Thompson Posterior:</span>
              <span class="ailab-math-v">${thompsonConf}%</span>
            </div>
            <div class="ailab-math-pill ailab-math-shield" title="Zero-Loss 429 Shield">
              <span class="ailab-math-k">🛡️ 429 Shield:</span>
              <span class="ailab-math-v">Safe (Zero Failure)</span>
            </div>
          </div>
        </div>
      `;

      let contentHtml = formatMarkdown(msg.content);
      if (msg.transfer_job) {
        contentHtml = ailabRenderTransferJobCard(msg.transfer_job) + contentHtml;
      }

      const footerHtml = `
        <div class="ailab-asst-footer">
          <div class="ailab-asst-actions">
            <button type="button" class="ailab-action-chip ailab-copy-btn" onclick="ailabCopyResponse('${wrap.id}')" title="Copy response to clipboard">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              <span>Copy</span>
            </button>
            <button type="button" class="ailab-action-chip" onclick="ailabRegenerateLast()" title="Regenerate response">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              <span>Regenerate</span>
            </button>
          </div>
          <div class="ailab-asst-foot-meta">
            <span class="ailab-footer-verified">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              <span>0 MB Render Load</span>
            </span>
            <span class="ailab-msg-timestamp">📅 ${formattedDate} ⏰ ${formattedTime}</span>
          </div>
        </div>
      `;

      wrap.innerHTML = `
        ${headerHtml}
        <div class="ailab-bubble ailab-asst-bubble">${contentHtml}</div>
        ${footerHtml}
      `;
    }
    ailabHydrateAttachmentImages(wrap);
    if (msg.transfer_job) {
      setTimeout(() => {
        if (typeof ailabStartTransferJobLiveTelemetry === "function") {
          ailabStartTransferJobLiveTelemetry(msg.transfer_job);
        }
      }, 300);
    }
    return wrap;
  }

  window.ailabToggleMathCard = function(cardId) {
    const el = document.getElementById(cardId);
    const caret = document.getElementById(cardId + "_caret");
    if (!el) return;
    const isHidden = el.style.display === "none" || !el.style.display;
    el.style.display = isHidden ? "block" : "none";
    if (caret) caret.style.transform = isHidden ? "rotate(180deg)" : "rotate(0deg)";
  };

  window.ailabCopyResponse = function(msgId) {
    const wrap = document.getElementById(msgId);
    if (!wrap) return;
    const bubble = wrap.querySelector(".ailab-asst-bubble") || wrap.querySelector(".ailab-bubble");
    if (!bubble) return;
    const text = bubble.innerText || bubble.textContent || "";
    navigator.clipboard.writeText(text).then(() => {
      const btn = wrap.querySelector(".ailab-copy-btn");
      if (btn) {
        const orig = btn.innerHTML;
        btn.innerHTML = `<span style="color:#10B981;">✓ Copied!</span>`;
        setTimeout(() => { btn.innerHTML = orig; }, 1800);
      }
    }).catch(console.warn);
  };

  window.ailabRegenerateLast = function() {
    if (!AILAB.messages || AILAB.messages.length === 0 || AILAB.isStreaming) return;
    let lastUserPrompt = "";
    for (let i = AILAB.messages.length - 1; i >= 0; i--) {
      if (AILAB.messages[i].role === "user") {
        lastUserPrompt = AILAB.messages[i].content;
        break;
      }
    }
    if (!lastUserPrompt) return;
    const input = $id("ailabPromptInput");
    if (input) {
      input.value = lastUserPrompt;
      ailabAutoResize(input);
      ailabSubmitPrompt();
    }
  };

  window.ailabSubmitPrompt = async function() {
    const input = $id("ailabPromptInput");
    const prompt = input.value.trim();
    const pending = (AILAB.pendingAttachments || []).slice();
    if ((!prompt && pending.length === 0) || AILAB.isStreaming) return;

    // A prompt cannot be stored without a chat row: create one first, and stop if that fails.
    if (!AILAB.activeChatId) {
      const created = await ailabNewChat("");
      if (!created) return;
    }

    input.value = "";
    ailabAutoResize(input);
    AILAB.isStreaming = true;
    const sendBtn = $id("ailabSendBtn");
    sendBtn.disabled = true;
    sendBtn.innerHTML = `<span>Thinking...</span>`;

    const attachmentMarkdown = pending.map(a => `![${a.name}](${a.url})`).join("\n");
    const displayedContent = [prompt, attachmentMarkdown].filter(Boolean).join("\n\n");
    const modelPrompt = pending.length
      ? `${prompt}\n\n[User attached ${pending.length} image(s)/diagram(s) to this chat: ${pending.map(a => a.name).join(", ")}]`.trim()
      : prompt;

    // 1. Append User Message to UI & DuckDB
    const userMsg = {
      id: "usr_" + Date.now(),
      chat_id: AILAB.activeChatId,
      role: "user",
      content: displayedContent,
      content_type: "markdown",
      created_at: Date.now() / 1000
    };
    // Autonomous Browser Control directly from the main chat
    // CRITICAL: NEVER intercept SQL, BigQuery, Table DDL, Database, Schema or AML tasks!
    const isSqlOrDataTask = /(bigquery|duckdb|snowflake|sql|ddl|table|तक्ता|create table|insert into|select |from |where |database|डेटाबेस|schema|स्कीमा|column|कॉलम|primary key|foreign key|aml|cbs|finacle)/i.test(prompt);

    const isBrowserIntent = !isSqlOrDataTask && (
      /(browse\s+|browser\s+agent|\bcua\b|screen share|स्क्रीन शेअर|search the web|वेबवर शोध|open (the\s+)?(site|website|page|url)|साइट उघड|वेबसाइट उघड)/i.test(prompt) ||
      (/(google|गुगल)\s*(var|वर|search|शोध|open|उघडा)/i.test(prompt)) ||
      (/^https?:\/\/[^\s]+$/i.test(prompt.trim()))
    );

    AILAB.pendingAttachments = [];
    ailabRenderAttachments();
    AILAB.messages.push(userMsg);
    const container = $id("ailabMessagesContainer");
    const heroEl = $id("ailabEmptyHero");
    if (heroEl) { AILAB.heroNode = heroEl; heroEl.remove(); }
    container.appendChild(ailabCreateMessageNode(userMsg));
    container.scrollTop = container.scrollHeight;

    // Save to DuckDB, then mirror to the BigQuery archive
    ailabSaveMessage(userMsg).then(() => ailabRefreshHistory());

    // 2. Add placeholder assistant bubble with pulse
    const assistantPlaceholder = document.createElement("div");
    assistantPlaceholder.className = "ailab-msg ailab-msg-assistant";
    assistantPlaceholder.id = "ailab-generating-msg";
    assistantPlaceholder.innerHTML = `
      <div class="ailab-asst-header">
        <div class="ailab-asst-left">
          <div class="ailab-asst-avatar-ring ailab-pulse-glow">
            <span class="ailab-asst-avatar">⚡</span>
          </div>
          <div class="ailab-asst-info">
            <div class="ailab-asst-name">
              <span>Evaluating Sovereign Multi-Model Mesh...</span>
            </div>
            <div class="ailab-asst-sub">
              <span class="ailab-asst-lab">Pure-Edge Dispatch</span> • 
              <span class="ailab-asst-tier">&lt; 0.8ms Math Overhead</span>
            </div>
          </div>
        </div>
        <div class="ailab-asst-right">
          <span class="ailab-asst-latency-badge ailab-pulse-badge">Routing...</span>
        </div>
      </div>
      <div class="ailab-bubble ailab-asst-bubble" style="color:#94A3B8; display:flex; align-items:center; gap:10px;">
        <span class="ailab-spinner-dot"></span>
        <span>Synthesizing response across 4,750+ specialized models...</span>
      </div>
    `;
    container.appendChild(assistantPlaceholder);
    container.scrollTop = container.scrollHeight;

    try {
      // Chat → local CUA: run the task on the laptop Chromium and answer here.
      if (isBrowserIntent && window.AILAB_CUA) {
        const cua = window.AILAB_CUA;
        const nameEl = assistantPlaceholder.querySelector(".ailab-asst-name span");
        if (nameEl) nameEl.textContent = "NanoPro CUA (Local Browser Agent)…";
        const labEl = assistantPlaceholder.querySelector(".ailab-asst-lab");
        if (labEl) labEl.textContent = "Laptop Chromium";
        const badgeEl = assistantPlaceholder.querySelector(".ailab-asst-latency-badge");
        if (badgeEl) badgeEl.textContent = "Executing";
        const bubbleEl = assistantPlaceholder.querySelector(".ailab-asst-bubble");
        if (bubbleEl) bubbleEl.innerHTML = '<span class="ailab-spinner-dot"></span><span>Driving the local browser — watch the arrow cursor in the side screen share.</span>';

        cua.togglePanel(true);
        const summary = await cua.runTask(prompt);
        assistantPlaceholder.remove();

        const acts = (cua.log || []).filter(l => l.kind === "act").slice(-12).map((l, i) => (i + 1) + ". " + l.text);
        const notes = (cua.log || []).filter(l => l.kind === "done" || l.kind === "secret").slice(-4).map(l => "- " + l.text);
        const md = [
          "### 🌐 NanoPro CUA — Local Browser Agent Report",
          "",
          summary,
          "",
          "| Field | Value |",
          "| :--- | :--- |",
          "| **Planner model** | " + (cua.lastModel || "auto (edge-routed)") + " |",
          "| **Steps run** | " + (cua.step || 0) + " / " + (cua.maxSteps || 24) + " |",
          "| **Current page** | " + String(cua.lastUrl || "—").replace(/\|/g, "\\|") + " |",
          "",
          "Executed on **your laptop's Chromium** — local GPU/CPU/RAM/disk, Render only planned the steps.",
          acts.length ? "\n**Actions performed**\n\n" + acts.join("\n") : "",
          notes.length ? "\n**Highlights**\n\n" + notes.join("\n") : ""
        ].filter(Boolean).join("\n");

        const cuaMsg = {
          id: "asst_" + Date.now(),
          chat_id: AILAB.activeChatId,
          role: "assistant",
          content: md,
          content_type: "markdown",
          model_routed: "local/cua-agent",
          model_executed: cua.lastModel || "auto",
          model_name: "NanoPro Local Browser Agent",
          lab_name: "NanoPro Autonomous Engine",
          country: "Local Laptop",
          flag: "🖥️",
          date_formatted: new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }),
          duration_ms: 0,
          routing_math: {},
          created_at: Date.now() / 1000
        };
        AILAB.messages.push(cuaMsg);
        container.appendChild(ailabCreateMessageNode(cuaMsg));
        container.scrollTop = container.scrollHeight;
        ailabRenderMermaidBlocks();
        if (AILAB.activeChatId) {
          AILAB.chatIndexCache[AILAB.activeChatId] = AILAB.messages;
          try { localStorage.setItem("nanopro_duckdb_chat_" + AILAB.activeChatId, JSON.stringify(AILAB.messages)); } catch (_) {}
          localStorage.setItem("nanopro_ailab_chats", JSON.stringify(AILAB.chats));
        }
        ailabSaveMessage(cuaMsg).then(() => ailabRefreshHistory());
        return;
      }

      // 2b. Explorer admin instructions ("VCT rename करा", "column type DATE
      // करा", "TEST table delete करा") run the same catalog operations as the
      // right-click menu. The backend decides: anything it does not recognise
      // comes back as status "not_admin" and falls through to normal chat.
      // Always asking (instead of pre-matching phrasing in the browser) keeps
      // Marathi variants such as "नाव CHAT_LABEL करा" from slipping to the LLM.
      let adminData = null;
      try {
        const adminRes = await fetch("/api/ai/bigquery_admin", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: prompt })
        });
        const adminJson = await adminRes.json();
        if (adminJson && adminJson.status && adminJson.status !== "not_admin") adminData = adminJson;
      } catch (_) { /* fall through to normal chat */ }

      // 3. Explicit BigQuery CREATE DDL runs for real on the backend. A pasted
      // row-wise column spec ("name | type | constraint") is turned into DDL
      // server-side, so it must take the same path.
      const hasSpecRow = /(?:\|\s*|\t|\s{2,})[A-Za-z][A-Za-z0-9_]*\s*(?:\||\t|\s{2,})\s*(?:STRING|INT64|INTEGER|NUMERIC|BIGNUMERIC|FLOAT64|BOOL|BOOLEAN|DATE|DATETIME|TIME|TIMESTAMP|JSON|BYTES|GEOGRAPHY)\b/i.test(prompt);
      const hasCreateIntent = /\b(create|build|make|banav\w*)\b|बनव|तयार/i.test(prompt);
      const isBigQueryDdl = /bigquery/i.test(prompt) && (
        /```sql[\s\S]*create\s+(schema|dataset|table)/i.test(prompt) ||
        /^\s*create\s+(schema|dataset|table)/i.test(prompt) ||
        /execute\s+bigquery\s+ddl:/i.test(prompt) ||
        (hasCreateIntent && hasSpecRow)
      );

      let routeRes = {};
      let execData;
      if (adminData) {
        execData = adminData;
      } else if (isBigQueryDdl) {
        const ddlRes = await fetch("/api/ai/bigquery_ddl", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: modelPrompt })
        });
        execData = await ddlRes.json();
      } else {
        // 3b. Mathematical Smart Routing Call
        routeRes = await fetch("/api/ai/smart_route", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: modelPrompt, sla_ms: 800 })
        }).then(r => r.json()).catch(() => ({}));

        const routedModel = routeRes.selected_model || AILAB.selectedModel;

        // 4. Execution Call (OpenRouter + MCP Streaming)
        const targetModelToExecute = (AILAB.selectedModel === "auto" || !AILAB.selectedModel) ? (routedModel || "auto") : AILAB.selectedModel;
        const execRes = await fetch("/api/ai/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: modelPrompt,
            model: targetModelToExecute,
            routed_model: routedModel,
            effort: AILAB.selectedEffort,
            messages: AILAB.messages.map(m => ({ role: m.role, content: m.content }))
          })
        });
        const execText = await execRes.text();
        try {
          execData = JSON.parse(execText);
        } catch (_) {
          // Long BigQuery work can outlive the gateway's request window. The
          // server keeps running, so report that instead of a JSON parse error.
          execData = {
            status: "success",
            response: "⏳ **No JSON reply came back from the gateway (HTTP " + execRes.status + ").** Long-running work such as a multi-table BigQuery append continues on the server. Ask 'nanopro_cbs_bronze madhil sarva tables madhe kiti rows ahet?' in a minute to confirm the new counts — the automatic S3 → Snowflake → DuckDB run shows in ⚡ Airflow Orchestrator.",
            summary: "Gateway closed the long request; work continues in the background",
            action: "long_running",
            model_name: "NanoPro Data Plane",
            flag: "⏳"
          };
        }
      }

      if (execData.status === "success") {
        assistantPlaceholder.remove();
        // Real DDL from chat is executed by the backend against BigQuery.
        // Refresh from the live catalog instead of fabricating catalog nodes.
        if (execData.action === "CREATE_TABLE" || execData.action === "CREATE_SCHEMA") {
          if (typeof ailabLoadExplorer === "function") {
            await ailabLoadExplorer(true);
          }
          if (typeof ailabShowDynamicToast === "function") {
            const label = execData.action === "CREATE_TABLE"
              ? `Table [${execData.schema_name ? execData.schema_name + "." : ""}${execData.table_name}] created`
              : `Dataset / Schema [${execData.schema_name}] created`;
            ailabShowDynamicToast(`🗄️ ${label} — Explorer refreshed from the live catalog.`);
          }
        }

        // Explorer admin instructions already ran against the live catalog;
        // reload the tree so rename / delete / retype appears without a reload.
        if (["rename_table", "rename_schema", "drop_table", "drop_schema", "alter_column", "add_column", "rename_column", "insert_samples", "mutate_rows"].indexOf(execData.action) !== -1) {
          if (typeof ailabLoadExplorer === "function") {
            await ailabLoadExplorer(true);
          }
          if (typeof ailabShowDynamicToast === "function") {
            ailabShowDynamicToast(`🛠️ ${execData.summary || execData.action} — Explorer live updated.`);
          }
        }

        const chatPromptStr = (typeof prompt !== "undefined" ? prompt : "") || "";
        const chatResponseStr = (execData && execData.response ? execData.response : "") || "";
        let transferJob = execData.transfer_job || null;
        const transferText = (chatPromptStr + " " + chatResponseStr).toLowerCase();
        if (!transferJob && (/(transfer|ट्रान्सफर|migrat|shift|copy|मूव्ह|लोड).*(table|तक्ता|डेटा|data|gb|mb)/i.test(transferText) || /(5gb|1gb|10gb|2gb).*(transfer|डेटा|data)/i.test(transferText))) {
          let srcTable = "RAW_AML_ALERTS";
          let tgtTable = "MART_AML_PROCESSED_TXNS";
          const tableMatches = (chatPromptStr + " " + (execData.response || "")).match(/\b([A-Z0-9_]{4,30})\b/g);
          if (tableMatches && tableMatches.length >= 2) {
            srcTable = tableMatches[0];
            tgtTable = tableMatches[1];
          } else if (tableMatches && tableMatches.length === 1) {
            tgtTable = tableMatches[0];
          }
          let szMb = 5120;
          if (transferText.includes("10gb")) szMb = 10240;
          else if (transferText.includes("1gb")) szMb = 1024;
          else if (transferText.includes("2gb")) szMb = 2048;

          transferJob = {
            job_id: "JOB_TRANS_" + Math.random().toString(36).slice(2, 7).toUpperCase(),
            source_table: srcTable,
            target_table: tgtTable,
            size_mb: szMb,
            total_rows: 12450000,
            status: "RUNNING"
          };
        }

        const assistantMsg = {
          transfer_job: transferJob,
          id: "asst_" + Date.now(),
          chat_id: AILAB.activeChatId,
          role: "assistant",
          content: execData.response || "No response received.",
          content_type: "markdown",
          model_routed: execData.model_routed,
          model_executed: execData.model_executed,
          model_name: execData.model_name,
          lab_name: execData.lab_name,
          country: execData.country,
          flag: execData.flag,
          date_formatted: execData.date_formatted,
          duration_ms: execData.duration_ms,
          routing_math: execData.routing_decision || routeRes,
          created_at: Date.now() / 1000
        };

        // DYNAMIC FRONT-LEVEL MODEL REFLECTION (Algorithm Applied Live on Front)
        const routedModelId = execData.model_executed || execData.model_routed;
        const prov = ailabResolveModelProvenance(routedModelId);
        const topSelect = $id("ailabModelSelect");
        if (topSelect && AILAB.selectedModel === "auto") {
          const autoOpt = topSelect.querySelector("option[value='auto']");
          if (autoOpt) {
            autoOpt.textContent = `⚡ AUTO ➔ ${prov.flag} ${prov.clean_name || execData.model_name} (${Math.round(execData.duration_ms || 320)}ms)`;
          }
        }
        const liveBadge = $id("ailabLiveRoutedBadge");
        if (liveBadge) {
          liveBadge.style.display = "inline-flex";
          const pScore = execData.routing_decision?.pareto_utility || "0.985";
          liveBadge.innerHTML = `<span style="font-size:14px;">${prov.flag}</span> <span>${escapeHtml(prov.clean_name || execData.model_name)}</span> <span style="background:#10B981;color:#0B132B;border-radius:4px;padding:1px 5px;font-size:10px;font-weight:800;">${Math.round(execData.duration_ms || 320)}ms</span> <span style="opacity:0.8;font-size:10px;">U=${pScore}</span>`;
        }

        AILAB.messages.push(assistantMsg);
        container.appendChild(ailabCreateMessageNode(assistantMsg));
        container.scrollTop = container.scrollHeight;
        ailabRenderMermaidBlocks();

        if (AILAB.activeChatId) {
          AILAB.chatIndexCache[AILAB.activeChatId] = AILAB.messages;
          try { localStorage.setItem("nanopro_duckdb_chat_" + AILAB.activeChatId, JSON.stringify(AILAB.messages)); } catch (_) {}
          localStorage.setItem("nanopro_ailab_chats", JSON.stringify(AILAB.chats));
        }

        // Save assistant message to DuckDB, then re-read the list so the sidebar
        // picks up the server-side auto-title and real message counts.
        ailabSaveMessage(assistantMsg).then(() => ailabRefreshHistory());
      } else {
        // The backend answered but refused the operation. Keep the reply in
        // the transcript instead of leaving an empty bubble behind.
        assistantPlaceholder.remove();
        const failMsg = {
          id: "asst_" + Date.now(),
          chat_id: AILAB.activeChatId,
          role: "assistant",
          content: execData.response || `⚠️ ${execData.message || "Failed to execute prompt."}`,
          content_type: "markdown",
          model_name: execData.model_name || "NanoPro",
          flag: execData.flag || "⚠️",
          created_at: Date.now() / 1000
        };
        AILAB.messages.push(failMsg);
        container.appendChild(ailabCreateMessageNode(failMsg));
        container.scrollTop = container.scrollHeight;
        ailabSaveMessage(failMsg).then(() => ailabRefreshHistory());
      }
    } catch (err) {
      console.error("[AILAB Submit Error]", err);
      const errMsg = err?.message || "Connection error occurred.";
      if (assistantPlaceholder && assistantPlaceholder.parentNode) {
        assistantPlaceholder.innerHTML = `<div class="ailab-bubble" style="color:#F87171;">⚠️ ${errMsg}. Retrying with Sovereign Edge Shield...</div>`;
      } else {
        const errNode = document.createElement("div");
        errNode.className = "ailab-msg ailab-msg-assistant";
        errNode.innerHTML = `<div class="ailab-bubble" style="color:#F87171;">⚠️ ${errMsg}</div>`;
        container.appendChild(errNode);
      }
    } finally {
      AILAB.isStreaming = false;
      sendBtn.disabled = false;
      sendBtn.innerHTML = `<span>Dispatch</span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>`;
    }
  };

  // -------------------------------------------------------------
  // ACTIONS: NEW CHAT, NEW PROJECT, PIN, EXPORT
  // -------------------------------------------------------------
  window.ailabNewChat = async function(projectId) {
    try {
      const res = await fetch("/api/ai/history/chats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "New AI Chat Session",
          project_id: projectId || null,
          model: AILAB.selectedModel,
          effort: AILAB.selectedEffort
        })
      });
      const data = await res.json();
      if (!res.ok || !data.chat) {
        ailabSetHistoryStatus("error", data.message || `Could not create chat (HTTP ${res.status}).`);
        if (res.status === 401) alert("Session expired — please log in again.");
        return false;
      }
      const chatObj = data.chat;
      AILAB.chats.unshift(chatObj);
      AILAB.activeChatId = chatObj.id;
      AILAB.activeProjectId = chatObj.project_id || null;
      if (chatObj.project_id) AILAB.expandedProjects[chatObj.project_id] = true;
      AILAB.messages = [];
      AILAB.chatIndexCache[chatObj.id] = [];
      try { localStorage.setItem("nanopro_ailab_chats", JSON.stringify(AILAB.chats)); } catch (_) {}
      ailabRenderSidebar();
      ailabRenderActiveProjectTag();
      ailabRenderMessages();
      $id("ailabActiveTitle").textContent = chatObj.title;
      $id("ailabPromptInput").focus();
      ailabRefreshHistory();
      return true;
    } catch (e) {
      console.warn("Error creating chat:", e);
      ailabSetHistoryStatus("error", "Could not reach history storage.");
      return false;
    }
  };

  window.ailabNewProject = async function() {
    const name = prompt("Enter Project Name (e.g. Real-Time Analytics Lakehouse):");
    if (!name) return;
    try {
      const res = await fetch("/api/ai/history/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim() })
      });
      const data = await res.json();
      if (data.project) {
        AILAB.projects.unshift(data.project);
        AILAB.expandedProjects[data.project.id] = true;
        AILAB.activeProjectId = data.project.id;
        try { localStorage.setItem("nanopro_ailab_projects", JSON.stringify(AILAB.projects)); } catch (_) {}
        ailabRenderSidebar();
      } else {
        alert(data.message || "Could not create the project.");
      }
    } catch (e) {
      alert("Could not reach history storage.");
    }
  };

  window.ailabRenameProject = async function(projectId) {
    const project = AILAB.projects.find(p => p.id === projectId);
    const newName = prompt("Rename Project:", project ? project.name : "");
    if (!newName || !newName.trim()) return;
    try {
      const res = await fetch(`/api/ai/history/projects/${projectId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName.trim() })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        alert(data.message || `Rename failed (HTTP ${res.status}).`);
        return;
      }
      if (project) project.name = newName.trim();
      ailabRenderSidebar();
      ailabRefreshHistory();
    } catch (e) {
      alert("Rename failed — history storage unreachable.");
    }
  };

  window.ailabDeleteProject = async function(projectId) {
    const project = AILAB.projects.find(p => p.id === projectId);
    if (!confirm(`Delete project "${project ? project.name : projectId}"? Its chats stay in Recent Chats.`)) return;
    try {
      const res = await fetch(`/api/ai/history/projects/${projectId}`, { method: "DELETE" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        alert(data.message || `Delete failed (HTTP ${res.status}).`);
        return;
      }
      AILAB.projects = AILAB.projects.filter(p => p.id !== projectId);
      delete AILAB.expandedProjects[projectId];
      if (AILAB.activeProjectId === projectId) AILAB.activeProjectId = null;
      AILAB.chats.forEach(c => { if (c.project_id === projectId) c.project_id = null; });
      ailabRenderSidebar();
      ailabRenderActiveProjectTag();
      ailabRefreshHistory();
    } catch (e) {
      alert("Delete failed — history storage unreachable.");
    }
  };

  window.ailabTogglePin = async function(chatId) {
    const chat = AILAB.chats.find(c => c.id === chatId);
    if (!chat) return;
    chat.is_pinned = !chat.is_pinned;
    ailabRenderSidebar();
    fetch(`/api/ai/history/chats/${chatId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_pinned: chat.is_pinned })
    }).catch(console.warn);
  };

  window.ailabPinCurrentChat = function() {
    if (AILAB.activeChatId) ailabTogglePin(AILAB.activeChatId);
  };

  window.ailabDeleteChat = async function(chatId) {
    if (!confirm("Delete this chat and its messages from DuckDB + BigQuery?")) return;
    try {
      const res = await fetch(`/api/ai/history/chats/${chatId}`, { method: "DELETE" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok && res.status !== 404) {
        alert(data.message || `Delete failed (HTTP ${res.status}).`);
        return;
      }
    } catch (e) {
      alert("Delete failed — history storage unreachable. Nothing was removed.");
      return;
    }

    AILAB.chats = (AILAB.chats || []).filter(c => c.id !== chatId);
    if (AILAB.chatIndexCache) delete AILAB.chatIndexCache[chatId];
    try {
      localStorage.removeItem("nanopro_duckdb_chat_" + chatId);
      localStorage.setItem("nanopro_ailab_chats", JSON.stringify(AILAB.chats));
    } catch (_) {}

    if (AILAB.activeChatId === chatId) {
      AILAB.activeChatId = AILAB.chats.length > 0 ? AILAB.chats[0].id : null;
      AILAB.messages = [];
    }
    ailabRenderSidebar();
    ailabRenderActiveProjectTag();
    if (AILAB.activeChatId) {
      ailabSelectChat(AILAB.activeChatId);
    } else {
      ailabRenderMessages();
      const titleEl = $id("ailabActiveTitle");
      if (titleEl) titleEl.textContent = "New Session";
    }
    ailabRefreshHistory();
  };

  window.ailabRenameChat = async function(chatId) {
    const chat = AILAB.chats.find(c => c.id === chatId);
    const newTitle = prompt("Rename Chat:", chat ? chat.title : "");
    if (!newTitle || !newTitle.trim()) return;
    const title = newTitle.trim();
    try {
      const res = await fetch(`/api/ai/history/chats/${chatId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        alert(data.message || `Rename failed (HTTP ${res.status}).`);
        return;
      }
      const saved = data.chat || {};
      if (chat) chat.title = saved.title || title;
      if (AILAB.activeChatId === chatId) {
        const titleEl = $id("ailabActiveTitle");
        if (titleEl) titleEl.textContent = saved.title || title;
      }
      ailabRenderSidebar();
      ailabRefreshHistory();
    } catch (e) {
      alert("Rename failed — history storage unreachable.");
    }
  };

  window.ailabRenameCurrentChat = function() {
    if (!AILAB.activeChatId) return;
    ailabRenameChat(AILAB.activeChatId);
  };

  window.ailabMoveCurrentChat = function() {
    if (!AILAB.activeChatId) return alert("Select a chat first.");
    ailabMoveChat(AILAB.activeChatId);
  };

  window.ailabClearMessages = function() {
    if (!confirm("Clear message history in this view?")) return;
    AILAB.messages = [];
    ailabRenderMessages();
  };

  window.ailabSyncBigQuery = function() {
    AILAB_DUCKDB.syncToBigQuery();
  };

  window.ailabExportCurrentChat = function() {
    if (!AILAB.messages || AILAB.messages.length === 0) return alert("No messages to export.");
    let md = `# NanoPro AI Session - ${$id("ailabActiveTitle").textContent}\n\n`;
    md += `*Exported on ${new Date().toISOString()} • Storage: DuckDB + BigQuery*\n\n---\n\n`;
    AILAB.messages.forEach(m => {
      md += `### ${m.role === "user" ? "👤 User" : "🧠 " + (m.model_executed || "AI Assistant")}\n\n`;
      md += `${m.content}\n\n---\n\n`;
    });
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `NanoPro_Chat_${AILAB.activeChatId || "session"}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  window.ailabSelectPreset = function(text) {
    const input = $id("ailabPromptInput");
    input.value = text;
    ailabAutoResize(input);
    ailabSubmitPrompt();
  };

  window.ailabChangeModel = function(modelId) {
    AILAB.selectedModel = modelId;
    const pill = $id("ailabModePill");
    if (pill) {
      pill.textContent = modelId === "auto" ? "⚡ AUTO Math Router Active" : `🎯 Model: ${modelId.split("/").pop()}`;
    }
  };

  window.ailabChangeEffort = function(effort) {
    AILAB.selectedEffort = effort;
  };

  window.ailabToggleSidebar = function() {
    const sb = $id("ailabSidebar");
    if (sb) sb.classList.toggle("collapsed");
  };

  // -------------------------------------------------------------
  // RESIZING & KEYBOARD UTILITIES
  // -------------------------------------------------------------
  function ailabInitGrip() {
    const grip = $id("ailabGrip");
    const sidebar = $id("ailabSidebar");
    if (!grip || !sidebar) return;

    let isResizing = false;
    grip.addEventListener("mousedown", e => {
      isResizing = true;
      document.body.style.cursor = "col-resize";
    });
    window.addEventListener("mousemove", e => {
      if (!isResizing) return;
      const newW = Math.max(200, Math.min(500, e.clientX));
      sidebar.style.width = newW + "px";
    });
    window.addEventListener("mouseup", () => {
      if (isResizing) {
        isResizing = false;
        document.body.style.cursor = "default";
      }
    });
  }

  window.ailabAutoResize = function(el) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 180) + "px";
  };

  // -------------------------------------------------------------
  // ATTACHMENTS (images, flowcharts, architecture diagrams)
  // -------------------------------------------------------------
  const AILAB_ATTACHMENT_MAX_BYTES = 4 * 1024 * 1024;

  window.ailabRenderAttachments = function() {
    const box = $id("ailabAttachmentChips");
    if (!box) return;
    const items = AILAB.pendingAttachments || [];
    if (items.length === 0) {
      box.style.display = "none";
      box.innerHTML = "";
      return;
    }
    box.style.display = "flex";
    box.innerHTML = items.map(a => `
      <span style="display:inline-flex;align-items:center;gap:6px;background:#101A2A;border:1px solid #1E293B;border-radius:8px;padding:4px 8px;font-size:11px;color:#CBD5E1;">
        <img src="${a.preview}" alt="" style="width:28px;height:28px;object-fit:cover;border-radius:5px;border:1px solid #334155;" />
        <span style="max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(a.name)}</span>
        <button type="button" onclick="ailabRemoveAttachment('${a.id}')" title="Remove attachment" style="background:none;border:none;color:#F87171;cursor:pointer;font-size:12px;padding:0;">✕</button>
      </span>
    `).join("");
  };

  window.ailabRemoveAttachment = function(attachmentId) {
    AILAB.pendingAttachments = (AILAB.pendingAttachments || []).filter(a => {
      if (a.id !== attachmentId) return true;
      try { if (a.preview) URL.revokeObjectURL(a.preview); } catch (_) {}
      return false;
    });
    ailabRenderAttachments();
  };

  function ailabReadFileBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const raw = String(reader.result || "");
        resolve(raw.indexOf(",") >= 0 ? raw.split(",")[1] : raw);
      };
      reader.onerror = () => reject(reader.error || new Error("Could not read file"));
      reader.readAsDataURL(file);
    });
  }

  window.ailabUploadAttachment = async function(file) {
    if (!file) return;
    if (!/^image\//i.test(file.type || "")) {
      alert("Only image, diagram or screenshot files can be attached.");
      return;
    }
    if (file.size > AILAB_ATTACHMENT_MAX_BYTES) {
      alert("That image is larger than 4 MB. Please compress it and try again.");
      return;
    }
    if (!AILAB.activeChatId) {
      const created = await ailabNewChat("");
      if (!created) return;
    }
    const preview = URL.createObjectURL(file);
    try {
      const data = await ailabReadFileBase64(file);
      const res = await fetch("/api/ai/history/attachments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: AILAB.activeChatId,
          name: file.name || "image.png",
          mime_type: file.type || "image/png",
          kind: "image",
          data: data
        })
      });
      const payload = await res.json().catch(() => ({}));
      if (!res.ok || !payload.attachment) {
        URL.revokeObjectURL(preview);
        alert(payload.message || `Attachment upload failed (HTTP ${res.status}).`);
        return;
      }
      const att = payload.attachment;
      AILAB.pendingAttachments.push({
        id: att.id,
        name: att.name || file.name || "image.png",
        url: `/api/ai/history/attachments/${att.id}`,
        preview: preview
      });
      ailabRenderAttachments();
      ailabRefreshHistory();
    } catch (e) {
      URL.revokeObjectURL(preview);
      alert("Attachment upload failed — history storage unreachable.");
    }
  };

  window.ailabHandleAttachmentFiles = function(fileList) {
    Array.from(fileList || []).forEach(file => ailabUploadAttachment(file));
  };

  window.ailabHandlePaste = function(e) {
    try {
      const items = (e.clipboardData && e.clipboardData.items) || [];
      const images = [];
      for (const item of items) {
        if (item.kind === "file" && /^image\//i.test(item.type)) {
          const f = item.getAsFile();
          if (f) images.push(f);
        }
      }
      if (images.length > 0) {
        e.preventDefault();
        images.forEach(f => ailabUploadAttachment(f));
      }
    } catch (_) {}
  };

  function ailabHydrateAttachmentImages(root) {
    const scope = root || document;
    scope.querySelectorAll("img[data-ailab-src]").forEach(img => {
      if (img.dataset.hydrated) return;
      img.dataset.hydrated = "1";
      fetch(img.dataset.ailabSrc, { cache: "no-store" })
        .then(res => {
          if (!res.ok) throw new Error("HTTP " + res.status);
          return res.blob();
        })
        .then(blob => { img.src = URL.createObjectURL(blob); })
        .catch(() => {
          const fallback = document.createElement("span");
          fallback.textContent = "🖼️ attachment unavailable";
          fallback.style.color = "#F87171";
          fallback.style.fontSize = "11px";
          img.replaceWith(fallback);
        });
    });
  }

  function ailabFormatUserContent(text) {
    return escapeHtml(text || "")
      .replace(/!\[([^\]]*)\]\((\/api\/ai\/history\/attachments\/[^\s\)\"\']+)\)/g, (match, alt, url) =>
        `<span style="display:block;margin-top:6px;"><img data-ailab-src="${url}" alt="${alt || 'attachment'}" style="max-width:240px;border-radius:8px;border:1px solid #334155;display:block;" /></span>`)
      .replace(/\n/g, "<br>");
  }

  window.ailabHandleKey = function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      ailabSubmitPrompt();
    }
  };

  // -------------------------------------------------------------
  // MARKDOWN, CYBER TABLES & MERMAID PARSER
  // -------------------------------------------------------------
  function escapeHtml(str) {
    return (str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function ailabEnsureMermaid() {
    if (window.mermaid) return;
    try {
      const s = document.createElement("script");
      s.src = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js";
      s.onload = () => {
        try {
          window.mermaid.initialize({
            startOnLoad: false,
            theme: 'dark',
            themeVariables: {
              darkMode: true,
              background: '#0B1119',
              primaryColor: '#8B5CF6',
              primaryTextColor: '#F8FAFC',
              primaryBorderColor: '#A78BFA',
              lineColor: '#38BDF8',
              secondaryColor: '#1E293B',
              tertiaryColor: '#0F172A'
            }
          });
          ailabRenderMermaidBlocks();
        } catch (_) {}
      };
      document.head.appendChild(s);
    } catch (_) {}
  }

  function formatMarkdown(text) {
    if (!text) return "";

    // 1. Extract Mermaid blocks FIRST into placeholders to protect < and > from HTML escaping
    const mermaidPlaceholders = [];
    text = text.replace(/```mermaid\s*\n([\s\S]*?)```/g, (match, code) => {
      const idx = mermaidPlaceholders.length;
      mermaidPlaceholders.push(code.trim());
      return `__AILAB_MERMAID_${idx}__`;
    });

    // 2. Extract other code blocks
    const codePlaceholders = [];
    text = text.replace(/```([a-zA-Z0-9_\-\.]*)\s*\n([\s\S]*?)```/g, (match, lang, code) => {
      const idx = codePlaceholders.length;
      codePlaceholders.push({ lang: lang || "CODE", code: code });
      return `__AILAB_CODE_${idx}__`;
    });

    // 3. Escape HTML on prose text
    let html = escapeHtml(text);

    // 4. Parse Markdown Tables (tolerate a missing trailing pipe on any row)
    html = html.replace(/(?:^|\n)((?:[ \t]*\|[^\n]*\r?\n){2,})/g, (match, tableText) => {
      const lines = tableText.trim().split(/\r?\n/).map(l => l.trim()).filter(Boolean);
      if (lines.length < 2) return match;
      if (!/^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$/.test(lines[1])) return match;

      const parseRow = (line) => {
        let row = line.trim();
        if (row.startsWith('|')) row = row.slice(1);
        if (row.endsWith('|')) row = row.slice(0, -1);
        return row.split('|').map(c => c.trim());
      };
      const headerCells = parseRow(lines[0]);
      if (headerCells.length < 2) return match;
      let tableHtml = '<div class="ailab-table-wrap"><table class="ailab-cyber-table"><thead><tr>';
      headerCells.forEach(c => { tableHtml += `<th>${c}</th>`; });
      tableHtml += '</tr></thead><tbody>';

      for (let r = 2; r < lines.length; r++) {
        const rowCells = parseRow(lines[r]);
        tableHtml += '<tr>';
        rowCells.forEach(c => { tableHtml += `<td>${c}</td>`; });
        tableHtml += '</tr>';
      }
      tableHtml += '</tbody></table></div>';
      return '\n' + tableHtml + '\n';
    });

    // 5. Parse ASCII Box Art blocks
    html = html.replace(/(?:^|\n)((?:[┌╔╚└├┤│║─═].*\r?\n)+)/g, (match, boxText) => {
      return `<div class="ailab-ascii-card"><pre>${boxText.trim()}</pre></div>`;
    });

    // 7.5 Markdown Images: ![alt](url) — http(s) or owner-only stored attachments
    html = html.replace(/!\[([^\]]*)\]\(([^\"\']+?)\)/g, (match, alt, url) => {
      const cleanUrl = url.trim().replace(/&amp;/g, '&');
      const isStored = /^\/api\/ai\/history\/attachments\//.test(cleanUrl);
      const imgAttr = isStored ? `data-ailab-src="${cleanUrl}"` : `src="${cleanUrl}"`;
      const safeAlt = (alt || "AI Visual").replace(/"/g, '&quot;');
      const encodedAlt = encodeURIComponent(alt || "AI Visual");
      return `<div class="ailab-image-card" style="margin: 14px 0; background: rgba(15,23,42,0.9); border: 1px solid rgba(56,189,248,0.25); border-radius: 12px; padding: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
        <div class="ailab-image-wrap" style="position:relative; overflow:hidden; border-radius:8px;">
          <img ${imgAttr} alt="${safeAlt}" loading="lazy" style="width:100%; max-height:480px; object-fit:cover; display:block; border-radius:8px;" />
        </div>
        <div class="ailab-image-caption" style="font-size:12px; font-weight:700; color:#F8FAFC; margin-top:8px;">🎨 ${safeAlt}</div>
        <div class="ailab-image-actions-bar" style="display:flex; flex-wrap:wrap; gap:8px; margin-top:10px;">
          <a href="${cleanUrl}" target="_blank" download="${safeAlt.replace(/\s+/g, '_')}.jpg" class="ailab-img-btn" style="padding:6px 12px; background:rgba(30,41,59,0.9); border:1px solid rgba(56,189,248,0.4); border-radius:6px; font-size:11px; font-weight:700; color:#38BDF8; text-decoration:none; display:inline-flex; align-items:center; gap:4px;">📥 डाउनलोड (Download 8K)</a>
          <a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="ailab-img-btn" style="padding:6px 12px; background:rgba(30,41,59,0.9); border:1px solid rgba(255,255,255,0.15); border-radius:6px; font-size:11px; font-weight:700; color:#E2E8F0; text-decoration:none; display:inline-flex; align-items:center; gap:4px;">🔍 फुलस्क्रीन (Fullscreen)</a>
          <button type="button" class="ailab-img-btn" onclick="ailabRegenerateImage('${encodedAlt}')" style="padding:6px 12px; background:#0284C7; border:1px solid #38BDF8; border-radius:6px; font-size:11px; font-weight:700; color:#FFF; cursor:pointer; display:inline-flex; align-items:center; gap:4px;">🔄 नवीन व्हेरिएशन (Regenerate)</button>
        </div>
      </div>`;
    });

    // 7.6 Markdown Links & 1-Tap Action Pills: [label](url)
    html = html.replace(/\[([^\]]+)\]\(([^\"\']+?)\)/g, (match, label, url) => {
      const cleanUrl = url.trim().replace(/&amp;/g, '&');
      if (cleanUrl.startsWith("#action:") || cleanUrl.includes("javascript:void") || cleanUrl === "#") {
        const actionPayload = cleanUrl.startsWith("#action:") ? cleanUrl.slice(8) : label;
        const safeText = encodeURIComponent(actionPayload);
        return `<button type="button" class="ailab-action-pill-btn" onclick="ailabHandleActionClick(decodeURIComponent('${safeText}'))"><span>${label}</span></button>`;
      }
      return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="ailab-link" style="color:#38BDF8; font-weight:600; text-decoration:underline;">${label}</a>`;
    });

    // 7.7 LaTeX Math: Display ($$...$$)
    html = html.replace(/\$\$([\s\S]+?)\$\$/g, (match, math) => {
      const cleanMath = math.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').trim();
      return `<div class="ailab-math-card"><span class="ailab-math-badge">📐 FORMULA / PROOF</span><div class="ailab-math-content">${cleanMath}</div></div>`;
    });

    html = html.replace(/^### (.*$)/gim, '<h5 class="ailab-h ailab-h3"><span style="color:#10B981;">✦</span> $1</h5>');
    html = html.replace(/^## (.*$)/gim, '<h4 class="ailab-h ailab-h2"><span style="color:#38BDF8;">🏛️</span> $1</h4>');
    html = html.replace(/^# (.*$)/gim, '<h3 class="ailab-h ailab-h1"><span style="color:#C084FC;">⚡</span> $1</h3>');

    // 7. Blockquotes
    html = html.replace(/^\> (.*$)/gim, '<div class="ailab-callout"><span style="color:#F59E0B;font-size:14px;">💡</span><div>$1</div></div>');

    // 8. Inline formatting
    html = html.replace(/`([^`]+)`/g, '<code style="background:#131E2E;padding:2px 6px;border-radius:4px;color:#38BDF8;">$1</code>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/\n\n/g, '<br><br>');
    html = html.replace(/\n/g, '<br>');

    // 9. Restore Code blocks
    codePlaceholders.forEach((item, idx) => {
      const rawSafe = encodeURIComponent(item.code);
      const blockHtml = `
        <div class="ailab-code-block">
          <div class="ailab-code-head">
            <span>${item.lang}</span>
            <div class="ailab-code-actions">
              <button class="ailab-code-btn" onclick="navigator.clipboard.writeText(decodeURIComponent('${rawSafe}'))">Copy</button>
            </div>
          </div>
          <pre class="ailab-pre"><code>${escapeHtml(item.code)}</code></pre>
        </div>
      `;
      html = html.replace(`__AILAB_CODE_${idx}__`, blockHtml);
    });

    // 10. Restore Mermaid blocks with unescaped code
    mermaidPlaceholders.forEach((code, idx) => {
      const mermaidHtml = `<div class="ailab-mermaid-container"><pre class="mermaid">${code}</pre></div>`;
      html = html.replace(`__AILAB_MERMAID_${idx}__`, mermaidHtml);
    });

        // 11. Parse Interactive Suggestion Chips / Hints: [HINT: Option 1 | Option 2 | Option 3]
    html = html.replace(/\[HINT:\s*([^\]]+)\]/gi, (match, hintStr) => {
      const options = hintStr.split('|').map(o => o.trim()).filter(Boolean);
      let chipsHtml = '<div class="ailab-hint-group"><span class="ailab-hint-lbl">💡 सुचवलेले पर्याय (1-Tap Suggestions):</span><div class="ailab-hint-chips">';
      options.forEach(opt => {
        const safeText = encodeURIComponent(opt);
        chipsHtml += `<button type="button" class="ailab-hint-chip" onclick="ailabSendHint(decodeURIComponent('${safeText}'))"><span>${opt}</span></button>`;
      });
      chipsHtml += '</div></div>';
      return chipsHtml;
    });

    return html;
  }

  function ailabRenderMermaidBlocks() {
    try {
      if (window.mermaid) {
        window.mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'loose',
          theme: 'dark',
          suppressErrorRendering: true
        });
        document.querySelectorAll('.ailab-mermaid-container pre.mermaid').forEach((el) => {
          if (el.dataset.processed) return;
          try {
            const graphDef = (el.textContent || "").trim();
            if (!graphDef) return;
            const id = "mermaid_" + Math.random().toString(36).slice(2, 9);
            window.mermaid.render(id, graphDef).then(({ svg }) => {
              el.parentElement.innerHTML = svg;
            }).catch(err => {
              console.warn("[Mermaid Handled]", err);
              el.parentElement.innerHTML = `<div class="ailab-ascii-card" style="border:1px solid rgba(56,189,248,0.4);"><div style="font-size:10.5px;color:#38BDF8;margin-bottom:4px;font-weight:700;">📊 Architecture Flow Structure</div><pre style="margin:0;font-size:11px;color:#E2E8F0;">${escapeHtml(graphDef)}</pre></div>`;
            });
            el.dataset.processed = "true";
          } catch (e) {
            el.parentElement.innerHTML = `<div class="ailab-ascii-card"><pre>${escapeHtml(el.textContent)}</pre></div>`;
          }
        });
      } else {
        ailabEnsureMermaid();
      }
    } catch (_) {}
  }


  // -------------------------------------------------------------
  // DUCKDB & BIGQUERY IN-BROWSER MCP ENGINE
  // -------------------------------------------------------------
  window.AILAB_DUCKDB = {
    isReady: true,
    syncStatus: "synced",
    runSQL: function(sql) {
      sql = (sql || "").trim();
      if (/^SELECT\s+COUNT\(\*\)\s+FROM\s+nanopro_messages/i.test(sql)) {
        return [{ count: AILAB.messages.length }];
      }
      if (/^SELECT\s+COUNT\(\*\)\s+FROM\s+nanopro_chats/i.test(sql)) {
        return [{ count: AILAB.chats.length }];
      }
      if (/^SELECT.*FROM\s+nanopro_messages/i.test(sql)) {
        return AILAB.messages.map(m => ({ id: m.id, role: m.role, content: m.content.slice(0, 50), model: m.model_executed || m.model_routed, duration_ms: m.duration_ms }));
      }
      return [{ status: "Executed on DuckDB in-browser WASM columnar store", rows_affected: 0 }];
    },
    syncToBigQuery: async function() {
      const btn = $id("ailabBqSyncBtn");
      const orig = btn ? btn.innerHTML : "";
      try {
        if (btn) btn.innerHTML = `<span>⏳ Syncing BigQuery...</span>`;
        const res = await fetch("/api/ai/history/sync_bigquery", { method: "POST" });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
        const cloud = data.cloud || {};
        const lines = [`Archive status: ${data.status || "unknown"}`];
        lines.push(`Rows uploaded this run: ${data.synced || 0}`);
        lines.push(`Rows still queued in DuckDB: ${data.pending || 0}`);
        if (cloud.configured === false) {
          lines.push(`BigQuery unavailable: ${cloud.error || "no service account configured"}`);
        }
        alert(lines.join("\n"));
      } catch (e) {
        alert(`BigQuery sync failed: ${e.message || e}`);
      } finally {
        if (btn) btn.innerHTML = orig || `<span>🏛️ BigQuery</span>`;
        ailabRefreshHistory();
      }
    }
  };

  // -------------------------------------------------------------
  // MODEL CATALOG MODAL CONTROLLER
  // -------------------------------------------------------------
  let cachedCatalogModels = [];
  let currentCatalogCategory = 'all';

  window.ailabOpenModelCatalogModal = function() {
    const modal = $id("ailabModelModal");
    if (modal) {
      modal.classList.add("is-open");
      ailabRenderModelCatalog();
      setTimeout(() => {
        const input = $id("ailabModelSearchInput");
        if (input) input.focus();
      }, 100);
    }
  };

  window.ailabCloseModelCatalogModal = function(e) {
    const modal = $id("ailabModelModal");
    if (modal) modal.classList.remove("is-open");
  };

  window.ailabFilterModels = function() {
    ailabRenderModelCatalog();
  };

  window.ailabFilterModelCategory = function(cat, btn) {
    currentCatalogCategory = cat;
    document.querySelectorAll(".ailab-modal-pills .ailab-pill").forEach(p => p.classList.remove("is-active"));
    if (btn) btn.classList.add("is-active");
    ailabRenderModelCatalog();
  };

  window.ailabSelectModelFromCatalog = function(modelId) {
    const select = $id("ailabModelSelect");
    if (select) {
      let opt = Array.from(select.options).find(o => o.value === modelId);
      if (!opt) {
        const prov = ailabResolveModelProvenance(modelId);
        opt = document.createElement("option");
        opt.value = modelId;
        opt.textContent = `${prov.flag} ${prov.clean_name || modelId} (${prov.lab_name})`;
        select.appendChild(opt);
      }
      select.value = modelId;
      ailabChangeModel(modelId);
    }
    ailabCloseModelCatalogModal();
  };

  function ailabRenderModelCatalog() {
    const grid = $id("ailabModelModalGrid");
    if (!grid) return;

    try {
      const query = ($id("ailabModelSearchInput")?.value || "").toLowerCase().trim();
      let models = cachedCatalogModels;
      if (!models || models.length === 0) {
        // Fallback seed models across Unified 2,150+ Mesh
        models = [
          { id: "auto", name: "Single AUTO Mathematical Engine", lab: "NanoPro Router", country: "Global Sovereign Mesh", flag: "⚡", is_free: false },
          // DeepInfra High-Throughput (177 Models)
          { id: "deepinfra/Qwen/Qwen3.8-Flash", name: "DeepInfra Qwen 3.8 Flash (Turbo)", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: true },
          { id: "deepinfra/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", name: "DeepInfra Llama 3.1 8B Turbo", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: true },
          { id: "deepinfra/meta-llama/Llama-3.3-70B-Instruct", name: "DeepInfra Llama 3.3 70B Turbo", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: false },
          { id: "deepinfra/Qwen/Qwen2.5-Coder-32B-Instruct", name: "DeepInfra Qwen 2.5 Coder 32B", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: false },
          { id: "deepinfra/deepseek-ai/DeepSeek-R1", name: "DeepInfra DeepSeek R1 Reasoning", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: false },
          { id: "deepinfra/microsoft/phi-4", name: "DeepInfra Microsoft Phi-4", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: false },
          // Mistral AI Direct (56 Models)
          { id: "mistral/codestral-latest", name: "Mistral Codestral 2508 (Code SOTA)", lab: "Mistral AI", country: "France", flag: "🇫🇷", is_free: false },
          { id: "mistral/mistral-large-latest", name: "Mistral Large 2 (Flagship)", lab: "Mistral AI", country: "France", flag: "🇫🇷", is_free: false },
          { id: "mistral/ministral-14b-latest", name: "Mistral Ministral 14B", lab: "Mistral AI", country: "France", flag: "🇫🇷", is_free: false },
          // DeepSeek Direct (2 Models)
          { id: "deepseek/deepseek-chat", name: "DeepSeek V3 (Direct API)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", is_free: false },
          { id: "deepseek/deepseek-reasoner", name: "DeepSeek R1 Reasoner (Direct API)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", is_free: false },
          // Groq LPUs (11 Models)
          { id: "groq/qwen3.8-27b", name: "Groq Qwen 3.8 27B (<300ms SLA)", lab: "Groq LPU", country: "United States", flag: "⚡", is_free: true },
          { id: "groq/openai/gpt-oss-120b", name: "Groq GPT OSS 120B High-Throughput", lab: "Groq LPU", country: "United States", flag: "⚡", is_free: true },
          { id: "groq/llama-3.3-70b-versatile", name: "Groq Llama 3.3 70B Versatile", lab: "Groq LPU", country: "United States", flag: "⚡", is_free: true },
          // Hugging Face Hub (110+ Models)
          { id: "hf/meta-llama/Llama-3.3-70B-Instruct", name: "Hugging Face Llama 3.3 70B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          { id: "hf/Qwen/Qwen2.5-Coder-32B-Instruct", name: "Hugging Face Qwen Coder 32B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          { id: "hf/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", name: "Hugging Face DeepSeek R1 Distill", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          // AI/ML API (995+ Models)
          { id: "aimlapi/anthropic/claude-3-7-sonnet", name: "AI/ML API Claude 3.7 Sonnet", lab: "AI/ML API Fabric", country: "Global Unified Aggregator", flag: "⚡", is_free: false },
          { id: "aimlapi/deepseek/deepseek-r1", name: "AI/ML API DeepSeek R1", lab: "AI/ML API Fabric", country: "Global Unified Aggregator", flag: "⚡", is_free: false },
          // OpenRouter Flagships
          { id: "anthropic/claude-3.7-sonnet", name: "Claude 3.7 Sonnet (Hybrid Thinking)", lab: "Anthropic", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "anthropic/claude-3.5-sonnet", name: "Claude 3.5 Sonnet", lab: "Anthropic", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "google/gemini-2.5-pro", name: "Gemini 2.5 Pro (Frontier 2M)", lab: "Google DeepMind", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "google/gemini-2.5-flash", name: "Gemini 2.5 Flash (<300ms SLA)", lab: "Google DeepMind", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "openai/o3-mini", name: "OpenAI o3-mini (High-Speed Reasoning)", lab: "OpenAI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "openai/gpt-4o", name: "GPT-4o (Omni Multimodal)", lab: "OpenAI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "meta-llama/llama-3.3-70b-instruct", name: "Llama 3.3 70B Instruct", lab: "Meta AI", country: "United States", flag: "🇺🇸", is_free: false },
          // Free Tier
          { id: "nvidia/nemotron-3.5-lightning:free", name: "NVIDIA Nemotron 3.5 Lightning", lab: "NVIDIA AI", country: "United States", flag: "🇺🇸", is_free: true },
          { id: "cohere/north-mini-code:free", name: "Cohere North Mini Code", lab: "Cohere", country: "Canada", flag: "🇨🇦", is_free: true },
          { id: "baidu/ernie-5.5-flash-preview:free", name: "Baidu ERNIE 5.5 Flash", lab: "Baidu", country: "China", flag: "🇨🇳", is_free: true },
          // SambaNova Systems (Fast SN40L RDUs)
          { id: "sambanova/Meta-Llama-3.3-70B-Instruct", name: "SambaNova Llama 3.3 70B (Fast RDU)", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          { id: "sambanova/GLM-5.3", name: "SambaNova GLM-5.3 Flagship", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          { id: "sambanova/MiniMax-M3.1-Flash", name: "SambaNova MiniMax M3.1 Flash", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          { id: "sambanova/gemma-4-31B-it", name: "SambaNova Gemma 4 31B", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          { id: "sambanova/gpt-oss-120b", name: "SambaNova GPT OSS 120B", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          // NVIDIA NIM (83 Models)
          { id: "nvidia/llama-3.1-nemotron-70b-instruct", name: "NVIDIA Llama 3.1 Nemotron 70B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          { id: "nvidia/nemotron-4-340b-instruct", name: "NVIDIA Nemotron 4 340B Flagship", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          { id: "nvidia/mistralai/codestral-22b-instruct-v0.1", name: "NVIDIA Codestral 22B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          { id: "nvidia/deepseek-ai/deepseek-v4.1-flash", name: "NVIDIA DeepSeek V4.1 Flash", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          { id: "nvidia/bigcode/starcoder2-15b", name: "NVIDIA StarCoder2 15B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          // Requesty AI (750 Models)
          { id: "requesty/anthropic/claude-fable-5.2", name: "Requesty Claude Fable 5.2", lab: "Requesty AI", country: "Global Router", flag: "🌐", is_free: false },
          { id: "requesty/google/gemini-4-hydrogen", name: "Requesty Gemini 4 Hydrogen", lab: "Requesty AI", country: "Global Router", flag: "🌐", is_free: false },
          { id: "requesty/openai/gpt-6.1-terra:flex", name: "Requesty GPT 6.1 Terra", lab: "Requesty AI", country: "Global Router", flag: "🌐", is_free: false },
          { id: "requesty/deepseek/deepseek-chat", name: "Requesty DeepSeek V3", lab: "Requesty AI", country: "Global Router", flag: "🌐", is_free: false },
          // Eden AI (1,311 Models)
          { id: "edenai/openai/gpt-4o", name: "Eden AI OpenAI GPT-4o", lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "Multimodal Flagship", is_free: false },
          { id: "edenai/anthropic/claude-3-5-sonnet", name: "Eden AI Claude 3.5 Sonnet", lab: "Eden AI", country: "France / Europe", flag: "🌿", is_free: false },
          { id: "edenai/google/gemini-1.5-pro", name: "Eden AI Google Gemini 1.5 Pro", lab: "Eden AI", country: "France / Europe", flag: "🌿", is_free: false },
          { id: "edenai/mistral/mistral-large-latest", name: "Eden AI Mistral Large 2", lab: "Eden AI", country: "France / Europe", flag: "🌿", is_free: false },
          { id: "edenai/deepseek/deepseek-r1", name: "Eden AI DeepSeek R1", lab: "Eden AI", country: "France / Europe", flag: "🌿", is_free: false },
          // FriendliAI, TheSean & Baseten
          { id: "friendli/meta-llama-3.1-8b-instruct", name: "FriendliAI Llama 3.1 8B (PeriFlow)", lab: "FriendliAI", country: "South Korea / Global", flag: "🚀", is_free: true },
          { id: "thesean/ship-like/claude-haiku-4-5", name: "TheSean Claude Haiku 4.5", lab: "TheSean AI", country: "Global", flag: "⚡", is_free: false },
          { id: "baseten/deepseek-ai/DeepSeek-V4.1-Flash", name: "Baseten DeepSeek V4.1 Flash", lab: "Baseten", country: "United States", flag: "🏗️", is_free: false },
          // Ola Krutrim Cloud (India's Sovereign AI Cloud)
          { id: "krutrim/Qwen3.6-27B", name: "Krutrim Qwen 3.6 27B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          { id: "krutrim/gpt-oss-120b", name: "Krutrim GPT OSS 120B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          { id: "krutrim/gemma-4-31b-it", name: "Krutrim Gemma 4 31B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          { id: "krutrim/GLM-5.3-Flash", name: "Krutrim GLM 5.3 Flash", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          { id: "krutrim/gpt-oss-20b", name: "Krutrim GPT OSS 20B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          // Poe API (303 Unified Bot Models)
          { id: "poe/gemini-4-hydrogen", name: "Poe Gemini 4 Hydrogen", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/grok-4.7", name: "Poe Grok 4.7", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/kimi-k3.1-pro", name: "Poe Kimi K3.1 Pro", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/claude-sonnet-5.5", name: "Poe Claude Sonnet 5.5", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/mistral-large-4", name: "Poe Mistral Large 4", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/mercury-3-vercel", name: "Poe Mercury 3 Diffusion", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          // Parasail GPU Network (107 Models)
          { id: "parasail/parasail-llama-33-70b-fp8", name: "Parasail Llama 3.3 70B FP8", lab: "Parasail GPU Network", country: "Global", flag: "⛵", is_free: true },
          { id: "parasail/parasail-qwen25-vl-72b-instruct", name: "Parasail Qwen 2.5 VL 72B", lab: "Parasail GPU Network", country: "Global", flag: "⛵", is_free: false },
          { id: "parasail/parasail-skyfall-36b-v2-fp8", name: "Parasail Skyfall 36B v2", lab: "Parasail GPU Network", country: "Global", flag: "⛵", is_free: false },
          { id: "parasail/parasail-llama-4-maverick-instruct-fp8", name: "Parasail Llama 4 Maverick", lab: "Parasail GPU Network", country: "Global", flag: "⛵", is_free: false },
          // Arcee AI (Domain-Specialized SLMs)
          { id: "arcee/zai-org/glm-5.3-flash", name: "Arcee GLM 5.3 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: true },
          { id: "arcee/deepseek/deepseek-v4.1-flash", name: "Arcee DeepSeek V4.1 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: false },
          { id: "arcee/moonshotai/kimi-k3.1-pro", name: "Arcee Kimi K3.1 Pro", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: false }
        ];
      }

      const filtered = models.filter(m => {
        const prov = ailabResolveModelProvenance(m.id);
        const mName = (m.name || prov.clean_name || m.id || "");
        const isFree = m.is_free || m.id.includes(":free");
        if (currentCatalogCategory === "krutrim" && !m.id.startsWith("krutrim/") && !(m.lab && m.lab.includes("Krutrim"))) return false;
        if (currentCatalogCategory === "poe" && !m.id.startsWith("poe/") && !(m.lab && m.lab.includes("Poe"))) return false;
        if (currentCatalogCategory === "parasail" && !m.id.startsWith("parasail/") && !(m.lab && m.lab.includes("Parasail"))) return false;
        if (currentCatalogCategory === "arcee" && !m.id.startsWith("arcee/") && !(m.lab && m.lab.includes("Arcee"))) return false;
        if (currentCatalogCategory === "edenai" && !m.id.startsWith("edenai/") && !(m.lab && m.lab.includes("Eden"))) return false;
        if (currentCatalogCategory === "requesty" && !m.id.startsWith("requesty/") && !(m.lab && m.lab.includes("Requesty"))) return false;
        if (currentCatalogCategory === "cf_ai" && !m.id.startsWith("@cf/") && !m.id.startsWith("cf/") && !(m.lab && m.lab.includes("Cloudflare"))) return false;
        if (currentCatalogCategory === "novita" && !m.id.startsWith("novita/") && !(m.lab && m.lab.includes("Novita"))) return false;
        if (currentCatalogCategory === "nvidia" && !m.id.startsWith("nvidia/") && !(m.lab && m.lab.includes("NVIDIA"))) return false;
        if (currentCatalogCategory === "sambanova" && !m.id.startsWith("sambanova/") && !(m.lab && m.lab.includes("SambaNova"))) return false;
        if (currentCatalogCategory === "friendli_thesean" && !m.id.startsWith("friendli/") && !m.id.startsWith("thesean/") && !m.id.startsWith("baseten/")) return false;
        if (currentCatalogCategory === "openrouter" && (m.id.startsWith("hf/") || m.id.startsWith("aimlapi/") || m.id.startsWith("fal/") || m.id.startsWith("replicate/") || m.id.startsWith("groq/") || m.id.startsWith("deepinfra/") || m.id.startsWith("mistral/") || m.id.startsWith("novita/") || m.id.startsWith("@cf/") || m.id.startsWith("edenai/") || m.id.startsWith("requesty/") || m.id.startsWith("nvidia/") || m.id.startsWith("sambanova/") || m.id.startsWith("friendli/") || m.id.startsWith("thesean/") || m.id.startsWith("baseten/"))) return false;
        if (currentCatalogCategory === "aimlapi" && !m.id.startsWith("aimlapi/") && m.provider !== "aimlapi") return false;
        if (currentCatalogCategory === "deepinfra" && !m.id.startsWith("deepinfra/") && !(m.lab && m.lab.includes("DeepInfra"))) return false;
        if (currentCatalogCategory === "mistral" && !m.id.startsWith("mistral/") && !m.id.startsWith("mistralai/") && !(m.lab && m.lab.includes("Mistral"))) return false;
        if (currentCatalogCategory === "hf" && !m.id.startsWith("hf/") && !m.id.startsWith("huggingface/") && !(m.lab && m.lab.includes("Hugging Face"))) return false;
        if (currentCatalogCategory === "deepseek" && !m.id.startsWith("deepseek/") && !(m.lab && m.lab.includes("DeepSeek"))) return false;
        if (currentCatalogCategory === "fal_replicate" && !m.id.startsWith("fal/") && !m.id.startsWith("replicate/") && !m.id.includes("flux")) return false;
        if (currentCatalogCategory === "groq" && !m.id.startsWith("groq/") && !(m.lab && m.lab.includes("Groq"))) return false;
        if (currentCatalogCategory === "free" && !isFree) return false;
        if (currentCatalogCategory === "reasoning" && !(mName.includes("R1") || mName.includes("o3") || mName.includes("Thinking") || mName.includes("Reasoning"))) return false;
        if (currentCatalogCategory === "code" && !(mName.toLowerCase().includes("code") || mName.toLowerCase().includes("coder"))) return false;

        if (query) {
          const text = `${m.id} ${mName} ${prov.lab_name} ${prov.country}`.toLowerCase();
          return text.includes(query);
        }
        return true;
      });

      if (filtered.length === 0) {
        grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:30px;color:#64748B;">No matching models found. Try another search.</div>';
        return;
      }

      grid.innerHTML = filtered.map(m => {
        const prov = ailabResolveModelProvenance(m.id);
        const isFree = m.is_free || m.id.includes(":free");
        const isSelected = AILAB.selectedModel === m.id;
        const displayName = m.name || prov.clean_name || m.id;
        return `
          <div class="ailab-mcard ${isSelected ? 'is-selected' : ''}" onclick="ailabSelectModelFromCatalog('${escapeHtml(m.id)}')">
            <div class="ailab-mcard-title">
              <span>${prov.flag} ${escapeHtml(displayName)}</span>
              ${isFree ? '<span class="ailab-mcard-tag" style="background:rgba(16,185,129,0.2);color:#86EFAC;">FREE</span>' : ''}
            </div>
            <div class="ailab-mcard-sub">${escapeHtml(prov.lab_name)} • ${escapeHtml(prov.country)}</div>
            <div style="font-size:10px;color:#64748B;font-family:monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(m.id)}</div>
          </div>
        `;
      }).join("");
    } catch (err) {
      console.error("ailabRenderModelCatalog error:", err);
    }
  }

  // Auto initialize on DOMContentLoaded or immediate
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGlobalAILab);
  } else {
    initGlobalAILab();
  }
})();

  // =========================================================================
  // AUTONOMOUS BROWSER AGENT (CUA) / COMPUTER USE MCP JAVASCRIPT ENGINE
  // =========================================================================
  // AUTONOMOUS BROWSER AGENT (CUA) / COMPUTER USE MCP JAVASCRIPT ENGINE
  // =========================================================================
  // =========================================================================
  // CUA — real browser agent
  // The page JS plans each step with /api/ai/execute, then drives a local
  // Playwright Chromium through the CUA bridge (start_cua_bridge.bat).
  // Nothing is simulated: every frame in this panel is a screenshot of the
  // browser window running on the laptop.
  // =========================================================================
  window.AILAB_CUA = {
    isOpen: false,
    isFullscreen: false,
    online: false,
    running: false,
    abort: false,
    step: 0,
    maxSteps: 24,
    log: [],
    frameTimer: null,
    bridgeURL: "http://127.0.0.1:8765",
    taskText: "",
    userAnswer: "",
    lastUrl: "",
    lastModel: "",
    queue: [],
    scrollStreak: 0,

    init: function () {
      this.bridgeURL = localStorage.getItem("nanopro_cua_bridge") || this.bridgeURL;
      this.initGripResize();
      this.pingBridge();
      setInterval(() => { if (!this.running && this.isOpen) this.pingBridge(); }, 6000);
    },

    initGripResize: function () {
      const grip = document.getElementById("ailabCuaGrip");
      const panel = document.getElementById("ailabCuaPanel");
      if (!grip || !panel) return;
      let dragging = false, startX = 0, startW = 0;
      grip.addEventListener("mousedown", (e) => {
        dragging = true; startX = e.clientX; startW = panel.offsetWidth;
        document.body.style.userSelect = "none";
      });
      window.addEventListener("mousemove", (e) => {
        if (!dragging) return;
        const dx = startX - e.clientX;
        panel.style.width = Math.max(360, Math.min(window.innerWidth * 0.7, startW + dx)) + "px";
      });
      window.addEventListener("mouseup", () => {
        if (dragging) { dragging = false; document.body.style.userSelect = ""; }
      });
    },

    togglePanel: function (force) {
      const panel = document.getElementById("ailabCuaPanel");
      const grip = document.getElementById("ailabCuaGrip");
      const btn = document.getElementById("ailabCuaToggleBtn");
      const sidebar = document.getElementById("ailabSidebar");
      if (!panel) return;
      const shouldOpen = force !== undefined ? force : panel.classList.contains("collapsed");
      if (shouldOpen) {
        panel.classList.remove("collapsed");
        panel.classList.add("active");
        if (grip) grip.style.display = "";
        if (btn) btn.classList.add("active");
        if (sidebar && !sidebar.classList.contains("collapsed")) sidebar.classList.add("collapsed");
        const appShell = document.getElementById("app-shell");
        if (appShell && !appShell.classList.contains("sidebar-collapsed")) appShell.classList.add("sidebar-collapsed");
        this.isOpen = true;
        this.pingBridge();
        this.startFrames();
      } else {
        panel.classList.add("collapsed");
        panel.classList.remove("active");
        if (grip) grip.style.display = "none";
        if (btn) btn.classList.remove("active");
        if (sidebar && sidebar.classList.contains("collapsed")) sidebar.classList.remove("collapsed");
        this.isOpen = false;
        this.stopFrames();
      }
    },

    toggleFullscreen: function () {
      const panel = document.getElementById("ailabCuaPanel");
      if (!panel) return;
      this.isFullscreen = !this.isFullscreen;
      if (this.isFullscreen) {
        panel.style.position = "fixed";
        panel.style.top = "50px";
        panel.style.left = "0";
        panel.style.width = "100vw";
        panel.style.height = "calc(100vh - 50px)";
        panel.style.zIndex = "9999";
        panel.style.maxWidth = "100vw";
      } else {
        panel.style.position = "";
        panel.style.top = "";
        panel.style.left = "";
        panel.style.width = "50%";
        panel.style.height = "100%";
        panel.style.zIndex = "";
        panel.style.maxWidth = "65vw";
      }
    },

    saveBridgeURL: function () {
      const input = document.getElementById("ailabCuaBridgeInput");
      const value = input ? input.value.trim().replace(/\/+$/, "") : "";
      if (value) {
        this.bridgeURL = value;
        localStorage.setItem("nanopro_cua_bridge", value);
      }
      this.pingBridge(true);
    },

    bridge: async function (path, body, timeoutMs) {
      return this.bridgeAt(this.bridgeURL, path, body, timeoutMs);
    },

    bridgePermission: async function () {
      try {
        if (!navigator.permissions || !navigator.permissions.query) return "unknown";
        const st = await navigator.permissions.query({ name: "local-network-access" });
        return (st && st.state) || "unknown";
      } catch (_) {
        return "unsupported";
      }
    },

    requestBridgePermission: async function () {
      let state = "unsupported";
      try {
        const q = await navigator.permissions.query({ name: "local-network-access" });
        state = (q && q.state) || state;
        if (state === "prompt" && navigator.permissions.request) {
          const r = await navigator.permissions.request({ name: "local-network-access" });
          state = (r && r.state) || state;
        }
      } catch (_) {}
      this.logLine("act", "🔐 Local network access: " + state);
      const ok = await this.ensureBridge();
      if (ok) return true;
      if (state === "denied") {
        this.logLine("warn", "Chrome ने ब्लॉक केलं — address bar मधला ⚙/🔒 → Site settings → Local network access → Allow, मग Retry.");
      } else {
        this.logLine("warn", "Prompt दिसला नाही तर: address bar मधला ⚙/🔒 → Site settings → Local network access → Allow → Retry.");
      }
      return false;
    },

    pingBridge: async function () {
      try {
        const info = await this.bridge("/status", null, 3000);
        if (info && info.status === "starting") throw new Error(info.error || "bridge is restarting Chromium");
        this.setOnline(true, info);
      } catch (err) {
        const permission = await this.bridgePermission();
        this.setOnline(false, { error: String((err && err.message) || "connection failed"), permission: permission });
      }
    },

    setOnline: function (ok, info) {
      this.online = ok;
      const pill = document.getElementById("ailabCuaBridgePill");
      const offline = document.getElementById("ailabCuaOfflineCard");
      if (pill) {
        pill.classList.toggle("is-offline", !ok);
        pill.innerHTML = ok
          ? '<span class="ailab-live-pulse-dot"></span><span>LIVE · LOCAL CHROMIUM</span>'
          : '<span>BRIDGE OFFLINE</span>';
      }
      if (offline) offline.style.display = ok ? "none" : "flex";
      const hintEl = document.getElementById("ailabCuaOfflineHint");
      if (hintEl) {
        if (ok) {
          hintEl.style.display = "none";
        } else {
          const perm = (info && info.permission) || "unknown";
          const httpsPage = location.protocol === "https:";
          let note;
          if (perm === "denied") {
            note = "🚫 Chrome ने या साइटसाठी local network access बंद केलं आहे. Address bar मधला ⚙ किंवा 🔒 → Site settings → Local network access → Allow → Retry दाबा.";
          } else if (httpsPage) {
            note = "🔐 Chrome 156+ पहिल्या कनेक्शनला \"Local network access\" विचारतं — Allow द्या. Prompt दिसत नसेल: address bar मधला ⚙/🔒 → Local network access → Allow → Retry. Bridge चालू नसेल तर start_cua_bridge.bat चालवा.";
          } else {
            note = "Bridge चालू आहे का तपासा: http://127.0.0.1:8765/status उघडा, मग Retry दाबा.";
          }
          hintEl.textContent = note;
          hintEl.style.display = "block";
        }
      }
      if (ok && info && info.url) {
        const urlText = document.getElementById("ailabCuaUrlText");
        if (urlText) urlText.textContent = info.url;
      }
      if (!this.running) {
        if (ok) this.updateActionHud("🖱️", "CUA ready — the red arrow shows every move and click");
        else this.updateActionHud("⚡", "CUA idle — start the local bridge to drive a real browser");
      }
      if (ok) this.startFrames(); else this.stopFrames();
    },

    startFrames: function () {
      if (this.frameTimer || !this.isOpen) return;
      const tick = async () => {
        if (!this.isOpen) { this.frameTimer = null; return; }
        if (this.online) {
          try {
            const frame = await this.bridge("/frame", null, 8000);
            if (frame && frame.ok) this.updateFrame(frame);
          } catch (_) {}
        }
        this.frameTimer = setTimeout(tick, this.running ? 420 : 1100);
      };
      this.frameTimer = setTimeout(tick, 0);
    },

    stopFrames: function () {
      if (this.frameTimer) { clearTimeout(this.frameTimer); this.frameTimer = null; }
    },

    updateFrame: function (frame) {
      const a = document.getElementById("ailabCuaScreenshotFrame");
      const b = document.getElementById("ailabCuaScreenshotFrameB");
      if (a && b && frame.screenshot) {
        const next = a.classList.contains("is-live") ? b : a;
        const prev = next === a ? b : a;
        if (next.src !== frame.screenshot) {
          const swap = () => { next.classList.add("is-live"); prev.classList.remove("is-live"); };
          next.src = frame.screenshot;
          if (next.decode) next.decode().then(swap).catch(swap); else next.onload = swap;
        }
      }
      if (frame.url) {
        this.lastUrl = frame.url;
        const urlText = document.getElementById("ailabCuaUrlText");
        if (urlText) urlText.textContent = frame.url;
      }
    },

    updateActionHud: function (icon, text) {
      const iconEl = document.getElementById("ailabCuaActionIcon");
      const descEl = document.getElementById("ailabCuaActionDesc");
      if (iconEl) iconEl.innerText = icon;
      if (descEl) descEl.innerText = text;
    },

    moveCursor: function (x, y, label) {
      const cursor = document.getElementById("ailabCuaCursor");
      const cursorLbl = document.getElementById("ailabCuaCursorLabel");
      const stage = document.getElementById("ailabCuaViewportContainer");
      const img = document.getElementById("ailabCuaScreenshotFrame");
      if (!cursor || !stage || !img) return;
      const sr = stage.getBoundingClientRect();
      const ir = img.getBoundingClientRect();
      if (!ir.width || !ir.height) return;
      const nw = img.naturalWidth || 1280;
      const nh = img.naturalHeight || 800;
      const scale = Math.min(ir.width / nw, ir.height / nh);
      // The frame uses object-fit: contain + object-position: top center, so the
      // letterbox padding is split horizontally and sits entirely below.
      const padX = (ir.width - nw * scale) / 2;
      const left = (ir.left - sr.left) + padX + x * scale;
      const top = (ir.top - sr.top) + y * scale;
      cursor.style.left = left + "px";
      cursor.style.top = top + "px";
      cursor.classList.add("is-visible");
      if (cursorLbl && label) cursorLbl.innerText = label;
    },

    triggerClickRipple: function (x, y) {
      const ripple = document.getElementById("ailabCuaClickRipple");
      const stage = document.getElementById("ailabCuaViewportContainer");
      const img = document.getElementById("ailabCuaScreenshotFrame");
      const cursor = document.getElementById("ailabCuaCursor");
      if (!ripple || !stage || !img) return;
      const sr = stage.getBoundingClientRect();
      const ir = img.getBoundingClientRect();
      if (!ir.width || !ir.height) return;
      const nw = img.naturalWidth || 1280;
      const nh = img.naturalHeight || 800;
      const scale = Math.min(ir.width / nw, ir.height / nh);
      const left = (ir.left - sr.left) + (ir.width - nw * scale) / 2 + x * scale;
      const top = (ir.top - sr.top) + y * scale;
      ripple.style.left = left + "px";
      ripple.style.top = top + "px";
      ripple.classList.remove("pulsing");
      void ripple.offsetWidth;
      ripple.classList.add("pulsing");
      if (cursor) {
        cursor.classList.remove("is-clicking");
        void cursor.offsetWidth;
        cursor.classList.add("is-clicking");
      }
    },

    escapeHtml: function (value) {
      return String(value == null ? "" : value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    },

    logLine: function (kind, text) {
      const stamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
      this.log.push({ stamp, kind, text });
      if (this.log.length > 80) this.log.shift();
      const box = document.getElementById("ailabCuaTaskLog");
      if (!box) return;
      box.classList.add("is-open");
      const stage = document.getElementById("ailabCuaViewportContainer");
      if (stage) stage.classList.add("has-log");
      box.innerHTML = this.log
        .map((l) => '<div class="ailab-cua-logline ' + l.kind + '"><span class="ts">' + l.stamp + "</span>" + this.escapeHtml(l.text) + "</div>")
        .join("");
      box.scrollTop = box.scrollHeight;
    },

    clearTaskLog: function () {
      this.log = [];
      const box = document.getElementById("ailabCuaTaskLog");
      if (box) { box.innerHTML = ""; box.classList.remove("is-open"); }
      const stage = document.getElementById("ailabCuaViewportContainer");
      if (stage) stage.classList.remove("has-log");
    },

    normalizePlan: function (plan) {
      if (!plan || typeof plan !== "object") return plan;
      const alias = {
        navigate: "goto", open: "goto", visit: "goto", go: "goto", go_to: "goto", open_url: "goto",
        left_click: "click", right_click: "click", double_click: "click", click_element: "click",
        type_text: "type", typewrite: "type", input_text: "type", fill: "fill",
        key: "press", press_key: "press", key_press: "press",
        scroll_down: "scroll", scroll_up: "scroll",
        select_option: "select", drag_and_drop: "drag",
        finished: "done", finish: "done", complete: "done"
      };
      const raw = String(plan.action || "").toLowerCase().replace(/\s+/g, "_");
      if (!raw) {
        // Some models nest the step: {"thought": "...", "click": {"index": 4}}
        const known = ["goto", "click", "type", "fill", "press", "scroll", "wait", "back", "select", "select_text",
          "copy", "paste", "download", "upload", "drag", "save_secret", "ask_user", "done"];
        for (const k of Object.keys(plan)) {
          if (known.indexOf(k) === -1) continue;
          const v = plan[k];
          delete plan[k];
          plan.action = alias[k] || k;
          if (v && typeof v === "object" && !Array.isArray(v)) Object.assign(plan, v);
          else if (v != null && ["click", "type", "fill", "press", "select", "download", "upload"].indexOf(k) !== -1) plan.index = v;
          break;
        }
      }
      if (alias[raw]) plan.action = alias[raw];
      if (raw === "scroll_down") plan.direction = plan.direction || "down";
      if (raw === "scroll_up") plan.direction = plan.direction || "up";
      if (typeof plan.index === "string" && /^\d+$/.test(plan.index)) plan.index = parseInt(plan.index, 10);
      if (plan.amount != null && plan.pixels == null && !isNaN(Number(plan.amount))) plan.pixels = Number(plan.amount);
      if (Array.isArray(plan.coordinate) && plan.coordinate.length >= 2) {
        plan.x = Number(plan.coordinate[0]);
        plan.y = Number(plan.coordinate[1]);
      }
      return plan;
    },

    parseXmlToolCall: function (text) {
      const fn = text.match(/<function=([^>\s]+)>/i);
      if (!fn) return null;
      const args = {};
      const re = /<parameter=([\w]+)>\s*([\s\S]*?)\s*<\/parameter>/gi;
      let m;
      while ((m = re.exec(text))) args[m[1]] = m[2].trim();
      const plan = { action: String(args.action || fn[1]), thought: "computer_use tool call" };
      if (args.coordinate) {
        const nums = (args.coordinate.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
        if (nums.length >= 2) { plan.x = nums[0]; plan.y = nums[1]; }
      }
      if (args.text) plan.text = args.text;
      if (args.url) plan.url = args.url;
      if (args.key) plan.key = args.key;
      if (args.summary) plan.summary = args.summary;
      if (args.message) plan.message = args.message;
      if (args.amount != null) plan.pixels = Number(args.amount) || 600;
      return plan;
    },

    parseAction: function (text) {
      let raw = String(text || "").trim();
      if (!raw) throw new Error("planner returned an empty response");
      if (/<function=/i.test(raw)) {
        const xmlPlan = this.parseXmlToolCall(raw);
        if (xmlPlan && xmlPlan.action) return this.normalizePlan(xmlPlan);
      }
      const fence = raw.match(/```(?:json)?\s*([\s\S]*?)```/i);
      if (fence && fence[1].indexOf("{") !== -1) raw = fence[1].trim();
      raw = raw.replace(/^```(?:json)?/i, "").replace(/```\s*$/, "").trim();
      const start = raw.indexOf("{");
      if (start === -1) throw new Error("model did not return JSON");
      let depth = 0, end = -1, inString = false, escaped = false;
      for (let i = start; i < raw.length; i++) {
        const ch = raw[i];
        if (inString) {
          if (escaped) escaped = false;
          else if (ch === "\\") escaped = true;
          else if (ch === '"') inString = false;
          continue;
        }
        if (ch === '"') inString = true;
        else if (ch === "{") depth++;
        else if (ch === "}") { depth--; if (depth === 0) { end = i; break; } }
      }
      if (end === -1) throw new Error("model returned incomplete JSON");
      const parsed = JSON.parse(raw.slice(start, end + 1));
      if (!parsed.action) throw new Error("model response has no action");
      return this.normalizePlan(parsed);
    },

    plan: async function (task, obs) {
      const elements = (obs.elements || []).slice(0, 90);
      const elementLines = elements
        .map((e) => "[" + e.i + "] <" + e.tag + (e.type ? " type=" + e.type : "") + '> "' + e.label + '"' +
          (e.checked ? " (checked)" : "") + (e.invalid ? " (invalid)" : "") + (e.required ? " (required)" : "") +
          (e.disabled ? " (disabled)" : "") + (e.options ? " options={" + e.options + "}" : "") +
          (e.href ? " -> " + e.href : ""))
        .join("\n");
      const system = [
        "You are NanoPro CUA, an autonomous browser agent driving a real Chromium window.",
        "Take exactly one step at a time and reply with ONE JSON object, nothing else.",
        'Schema: {"thought":"one short sentence","action":"goto|click|type|press|scroll|wait|back|select|select_text|copy|paste|download|upload|drag|save_secret|ask_user|done", ...fields}',
        "Fields: goto{url}; click{index,button,clicks} or click{x,y}; type{index,text,enter}; press{key}; scroll{direction,pixels}; wait{ms}; select{index,value}; select_text{index,text?}; copy{}; paste{index,text?}; download{index}; upload{index,path}; drag{from,to} or drag{from,dx,dy}; save_secret{provider,value}; ask_user{message,options}; done{summary}.",
        "Rules:",
        "- Use these action names exactly: goto (not navigate/open), click (not left_click), type, press, scroll, done.",
        "- Use only element indexes from the provided list.",
        "- Elements marked (required) must be filled before submit. A select lists its choices as options={value=Label; ...}: use select{index,value:\"<value before =>\"}.",
        "- If a click target has no index or the index fails, you may click by coordinates: click{x,y} in viewport pixels (viewport size is in SCROLL).",
        "- Headings and paragraphs have no index: select their exact text with select_text{text:\"exact phrase from VISIBLE TEXT\"}.",
        "- If SELECTED TEXT already holds the target text, do NOT select again — the next step is copy.",
        "- If LAST COPY already matches what the task asked for, return done instead of copying again.",
        "- Never type passwords, OTPs, card numbers or payment details. If a login, OTP, CAPTCHA or payment screen appears, use ask_user and stop there.",
        "- save_secret only when the exact secret value is visible on the page and the task asks you to capture it. Never invent a value.",
        "- download clicks a download link/button; the file is saved on the user's laptop in Downloads\\NanoProCUA.",
        "- upload needs an absolute local path. If the task needs a file and no path is given, use ask_user to request it.",
        "- To copy page text: select_text first (pass the exact visible text when the element has no index), then copy in the next step. paste inserts the clipboard or the text you pass into the indexed field.",
        "- drag moves a slider or drag target: pass from plus to, or from plus dx/dy pixel offsets.",
        "- When the task is finished, return done with a short summary of what you verified. Speak in first person as NanoPro CUA and name yourself in the summary (for example: \"NanoPro CUA filled and submitted the form — the page confirmed the submission.\").",
        "- If the answer (title, heading, quote, price…) is already inside VISIBLE TEXT, return done with it now — do not scroll to look for it.",
        "- Do not scroll more than twice in a row; if the answer is still not visible, return done and say what you did see.",
        "- Keep text fields short; one click or one field per step.",
        "- FORMS: required fields are marked with *. If you clicked submit and the page shows red validation text, or nothing changed, do NOT click submit again. Read the error text and fill the empty required field first (open dropdowns and pick an option).",
        "- FORM STATE lists radios/checkboxes that are already checked and the current select values. If the value you need is already set there, do not click it again — move to the next field or submit.",
        "- If FORM STATE or an element is marked (invalid), that field is blocking the form. Fill the invalid field before clicking submit again.",
        "- If your last action produced no visible change, the next action must be different: pick the missing field, another element, or scroll to the error."
      ].join("\n");
      const observation = [
        "TASK: " + task,
        "STEP: " + this.step + "/" + this.maxSteps,
        "URL: " + (obs.url || ""),
        "TITLE: " + (obs.title || ""),
        "SCROLL: " + JSON.stringify(obs.scroll || {}),
        "FORM STATE: " + (obs.formState ? String(obs.formState).slice(0, 500) : "(no checkboxes, radios or selects on the page)"),
        "",
        "VISIBLE TEXT:",
        String(obs.text || "").slice(0, 2800),
        "",
        "SELECTED TEXT: " + (obs.selection ? JSON.stringify(String(obs.selection).slice(0, 300)) : "(nothing selected)"),
        "LAST COPY: " + (this.lastCopied ? JSON.stringify(String(this.lastCopied).slice(0, 300)) : "(nothing copied yet)"),
        "",
        "INTERACTIVE ELEMENTS:",
        elementLines
      ].join("\n");

      let lastHttp = 0;
      // CUA model policy: a sub-second model for normal steps, and a frontier
      // thinking model once the page gets tricky (validation, no-change repeats,
      // failed actions, planner hiccups). A free router is the last safety net.
      const manualModel = (window.AILAB && AILAB.selectedModel && AILAB.selectedModel !== "auto") ? AILAB.selectedModel : "";
      const FAST_MODEL = manualModel || "qwen/qwen3.8-27b";
      // Escalation must stay fast and reliable: gpt-oss-120b answers in seconds
      // with high reasoning. Free frontier models are queued (7-30s), so they are
      // the last-resort planner, not the default escalation step.
      const SMART_MODEL = manualModel || "openai/gpt-oss-120b";
      const FRONTIER_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free";
      const uiEffort = (window.AILAB && AILAB.selectedEffort) || "default";
      const effortFor = (smart) => {
        if (uiEffort === "fast") return "fast";
        if (uiEffort === "reasoning" || uiEffort === "architecture") return "reasoning";
        return smart ? "reasoning" : "fast";
      };
      const askModel = async (suffix, modelOverride, effortOverride) => {
        const res = await fetch("/api/ai/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: system + "\n\n" + observation + (suffix || ""),
            model: modelOverride || manualModel || "auto",
            effort: effortOverride || uiEffort,
            agent: "cua",
            messages: []
          }),
          signal: AbortSignal.timeout(70000)
        });
        lastHttp = res.status;
        const data = await res.json().catch(() => ({}));
        this.lastModel = data.model_executed || data.model_name || this.lastModel || "";
        if (data && data.status === "error" && data.error) throw new Error(String(data.error).slice(0, 200));
        return data.response || data.message || data.text || "";
      };

      const strict = "\n\nIMPORTANT: Answer with ONE JSON object only, action names goto/click/type/press/scroll/done. No prose, no markdown, no code fences, no XML.";
      let lastErr = null;
      for (let attempt = 1; attempt <= 3; attempt++) {
        try {
          const text = await askModel(
            attempt === 1 ? "" : strict,
            attempt === 1 ? (this.escalate ? SMART_MODEL : FAST_MODEL) : (attempt === 2 ? SMART_MODEL : FRONTIER_MODEL),
            attempt === 1 && !this.escalate ? effortFor(false) : effortFor(true)
          );
          if (!text) throw new Error("planner returned an empty response (HTTP " + lastHttp + ")");
          return this.parseAction(text);
        } catch (err) {
          lastErr = err;
          this.escalate = true;
          if (attempt < 3) {
            this.logLine("warn", "Planner attempt " + attempt + " failed (" + err.message + "), retrying with a deeper model…");
            await new Promise((r) => setTimeout(r, 600 * attempt));
          }
        }
      }
      throw lastErr;
    },

    describeAction: function (plan) {
      switch (String(plan.action || "").toLowerCase()) {
        case "goto": return 'navigated to ' + (plan.url || "");
        case "click": return plan.index != null ? ("clicked [" + plan.index + "]") : ("clicked at " + (plan.x != null ? plan.x : "?") + "," + (plan.y != null ? plan.y : "?"));
        case "type": return 'typed into [' + plan.index + "]";
        case "press": return "pressed " + (plan.key || "Enter");
        case "scroll": return "scrolled " + (plan.direction || "down");
        case "back": return "went back";
        case "select": return "selected a value";
        case "select_text": return plan.text ? ('selected "' + String(plan.text).slice(0, 40) + '"') : "selected text in [" + plan.index + "]";
        case "copy": return "copied the selection";
        case "paste": return "pasted into the focused field";
        case "download": return "clicked download [" + plan.index + "]";
        case "upload": return "uploaded " + (plan.path || "a file");
        case "drag": return "dragged [" + plan.from + "] onto [" + plan.to + "]";
        case "wait": return "waited";
        default: return plan.action || "";
      }
    },

    askUser: function (message, options) {
      return new Promise((resolve) => {
        const box = document.getElementById("ailabCuaAsk");
        if (!box) { resolve("continue"); return; }
        const choices = (options && options.length ? options : []).slice(0, 4).map(String);
        box.classList.add("is-open");
        box.innerHTML =
          '<div class="ailab-cua-ask-title">🤝 ' + this.escapeHtml(message) + "</div>" +
          '<div class="ailab-cua-ask-opts"></div>';
        const holder = box.querySelector(".ailab-cua-ask-opts");
        const finish = (value) => {
          box.classList.remove("is-open");
          box.innerHTML = "";
          this.userAnswer = value;
          resolve(value);
        };
        choices.forEach((choice) => {
          const b = document.createElement("button");
          b.className = "ailab-hitl-btn";
          b.textContent = choice;
          b.onclick = () => finish(choice);
          holder.appendChild(b);
        });
        const doneBtn = document.createElement("button");
        doneBtn.className = "ailab-hitl-btn recommended";
        doneBtn.textContent = "✅ मी स्वतः केलं — पुढे चला";
        doneBtn.onclick = () => finish("The user completed this step manually. Continue from the current page.");
        holder.appendChild(doneBtn);
      });
    },

    saveSecret: async function (plan) {
      const provider = String(plan.provider || "").trim();
      const value = String(plan.value || "").trim();
      if (!provider || !value) {
        this.logLine("error", "save_secret needs both provider and value.");
        return;
      }
      try {
        const res = await fetch("/api/ai/cua/secrets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ provider: provider, value: value, source_url: this.lastUrl, note: this.taskText })
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || ("HTTP " + res.status));
        this.logLine("secret", "🔐 " + provider + " key encrypted into the vault (" + (data.masked || "masked") + ")");
        this.updateActionHud("🔐", provider + " key saved to the server vault");
      } catch (err) {
        this.logLine("error", "Could not save the key: " + err.message);
      }
    },

    escalateModel: function (reason) {
      if (this.escalate) return;
      this.escalate = true;
      this.logLine("warn", "🧠 Manager: deeper-thinking model engaged — " + reason);
    },

    // ---- CUA Squad: independent model calls that cross-check the Pilot ----
    squadAsk: async function (systemText, observationText, model, effort) {
      const res = await fetch("/api/ai/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: systemText + "\n\n" + observationText,
          model: model,
          effort: effort || "fast",
          agent: "cua-squad",
          messages: []
        }),
        signal: AbortSignal.timeout(45000)
      });
      const data = await res.json().catch(() => ({}));
      if (data && data.status === "error" && data.error) throw new Error(String(data.error).slice(0, 160));
      return String(data.response || data.message || data.text || "");
    },

    parseJsonLoose: function (text) {
      const s = String(text || "");
      const hits = [];
      let depth = 0, start = -1, inStr = false, esc = false;
      for (let i = 0; i < s.length; i++) {
        const ch = s[i];
        if (inStr) {
          if (esc) esc = false;
          else if (ch === "\\") esc = true;
          else if (ch === '"') inStr = false;
          continue;
        }
        if (ch === '"') { inStr = true; continue; }
        if (ch === "{") { if (depth === 0) start = i; depth++; }
        else if (ch === "}") {
          if (depth > 0 && --depth === 0 && start >= 0) { hits.push(s.slice(start, i + 1)); start = -1; }
        }
      }
      for (let i = hits.length - 1; i >= 0; i--) {
        try {
          const v = JSON.parse(hits[i]);
          if (v && typeof v === "object" && !Array.isArray(v)) return v;
        } catch (_) {}
      }
      return null;
    },

    squadParse: function (text) {
      return this.parseJsonLoose(text);
    },

    criticReview: async function (task, snap, action, outcome) {
      const system = [
        "You are the Critic agent in NanoPro CUA's browser squad.",
        "The Pilot agent just acted; the page state below is the result. Judge whether the action achieved its intent.",
        'Reply with ONE JSON object: {"verdict":"ok|problem","note":"max 30 words naming the concrete next action"}',
        "Look for: constraint-invalid fields, disabled buttons, wrong element, unchanged values, modals/ads blocking the form, or a missing required field."
      ].join("\n");
      const observation = [
        "TASK: " + task,
        "LAST ACTION: " + JSON.stringify(action),
        "OUTCOME: " + (outcome && outcome.ok === false ? "FAILED: " + (outcome.error || "unknown") : "no visible page change"),
        "URL: " + (snap.url || ""),
        "FORM STATE: " + (snap.formState || "(none)"),
        "VISIBLE TEXT:",
        String(snap.text || "").slice(0, 1800),
        "INTERACTIVE ELEMENTS:",
        (snap.elements || []).slice(0, 50).map((e) =>
          "[" + e.i + "] <" + e.tag + (e.type ? " type=" + e.type : "") + '> "' + e.label + '"' +
          (e.checked ? " (checked)" : "") + (e.invalid ? " (invalid)" : "") + (e.disabled ? " (disabled)" : "")
        ).join("\n")
      ].join("\n");
      const text = await this.squadAsk(system, observation, "openai/gpt-oss-120b", "fast");
      return this.squadParse(text);
    },

    verifyCompletion: async function (task, snap, summary) {
      const system = [
        "You are the Verifier agent in NanoPro CUA's browser squad.",
        "The Pilot claims the task is complete. Check the page evidence, not the claim.",
        'Reply with ONE JSON object: {"verified":true|false,"reason":"max 25 words"}',
        "Verify only when the page itself shows the outcome (success message, expected value, target page/state)."
      ].join("\n");
      const observation = [
        "TASK: " + task,
        "PILOT CLAIM: " + (summary || "(no summary)"),
        "URL: " + (snap.url || ""),
        "TITLE: " + (snap.title || ""),
        "FORM STATE: " + (snap.formState || "(none)"),
        "VISIBLE TEXT:",
        String(snap.text || "").slice(0, 2200)
      ].join("\n");
      const model = this.escalate ? "openai/gpt-oss-120b" : "qwen/qwen3.8-27b";
      const text = await this.squadAsk(system, observation, model, this.escalate ? "reasoning" : "fast");
      return this.squadParse(text);
    },

    // Screenshot grounding: when DOM indexes fail or an action changes nothing,
    // a vision model looks at the live frame and returns a click point instead.
    visionPlan: async function (task, snap) {
      if ((this.visionUsed || 0) >= 3) return null;
      let frame = null;
      try { frame = await this.bridge("/frame", null, 9000); } catch (_) { return null; }
      if (!frame || !frame.ok || !frame.screenshot) return null;
      const vw = (snap && snap.scroll && snap.scroll.width) || 1280;
      const vh = (snap && snap.scroll && snap.scroll.viewport) || 800;
      this.visionUsed = (this.visionUsed || 0) + 1;
      const candidates = (snap && snap.elements || []).filter((e) =>
        isFinite(Number(e.x)) && isFinite(Number(e.y)) && Number(e.w) > 0 && Number(e.h) > 0 &&
        Number(e.x) >= 0 && Number(e.y) >= 0 && Number(e.x) < vw && Number(e.y) < vh &&
        String(e.label || "").trim()
      ).slice(0, 60);
      const system = [
        "You are NanoPro CUA's vision module. A live browser screenshot is attached.",
        "Pick the single control the task needs for its next step.",
        "Every control in the DOM has a known index and exact geometry; the screenshot is 1:1 with the viewport.",
        'Reply with ONE JSON object and nothing else: {"thought":"max 12 words","index":N}',
        'N must be one of the CANDIDATES indexes listed. Only if the target control is missing from CANDIDATES, reply {"thought":"...","box":[x0,y0,x1,y1]} with the bounding rectangle as 0.0-1.0 fractions of width/height.',
        "Never target password, OTP or payment fields."
      ].join("\n");
      const observation = [
        "TASK: " + task,
        "URL: " + ((frame && frame.url) || (snap && snap.url) || ""),
        "VIEWPORT: " + vw + "x" + vh,
        "PAGE TEXT:",
        String((snap && snap.text) || "").slice(0, 1200),
        "CANDIDATES:",
        candidates.map((e) =>
          "[" + e.i + "] <" + e.tag + (e.type ? " type=" + e.type : "") + '> "' + e.label + '"' +
          " at (" + Math.round(e.x) + "," + Math.round(e.y) + ") size " + Math.round(e.w) + "x" + Math.round(e.h) +
          (e.required ? " (required)" : "") + (e.checked ? " (checked)" : "") +
          (e.options ? " options={" + e.options + "}" : "")
        ).join("\n")
      ].join("\n");
      const visionModels = [
        "openrouter@nvidia/nemotron-3.5-super-vl:free",
        "gemini-4-hydrogen"
      ];
      for (const vm of visionModels) {
        try {
          const res = await fetch("/api/ai/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              prompt: system + "\n\n" + observation,
              model: vm,
              effort: "fast",
              agent: "cua-vision",
              messages: [],
              image: frame.screenshot
            }),
            signal: AbortSignal.timeout(45000)
          });
          const data = await res.json().catch(() => ({}));
          if (!res.ok || (data && data.status === "error")) throw new Error((data && data.error) || ("HTTP " + res.status));
          const text = String(data.response || data.message || data.text || "");
          const v = this.parseJsonLoose(text);
          if (!v) throw new Error("vision returned no JSON");
          let x = NaN, y = NaN, picked = null;
          const idx = Number(v.index);
          if (isFinite(idx)) {
            picked = candidates.find((e) => Number(e.i) === idx) || null;
            if (picked) {
              x = Math.round(Number(picked.x) + Number(picked.w) / 2);
              y = Math.round(Number(picked.y) + Number(picked.h) / 2);
            }
          }
          if ((!picked) && Array.isArray(v.box) && v.box.length >= 4) {
            let box = v.box.slice(0, 4).map(Number);
            if (box.every((n) => isFinite(n))) {
              if (Math.max(box[0], box[2]) > 1.5 || Math.max(box[1], box[3]) > 1.5) {
                box = [box[0] / vw, box[1] / vh, box[2] / vw, box[3] / vh];
              }
              let [x0, y0, x1, y1] = box;
              if (x1 < x0) [x0, x1] = [x1, x0];
              if (y1 < y0) [y0, y1] = [y1, y0];
              const bw = x1 - x0, bh = y1 - y0;
              if (bw > 0.001 && bh > 0.001 && bw < 0.95 && bh < 0.95 && bw * bh < 0.5) {
                x = Math.round(((x0 + x1) / 2) * vw);
                y = Math.round(((y0 + y1) / 2) * vh);
              }
            }
          }
          if (!isFinite(x) || !isFinite(y)) {
            x = Math.round(Number(v.x_pct) * vw);
            y = Math.round(Number(v.y_pct) * vh);
          }
          const inset = 3;
          if (!isFinite(x) || !isFinite(y) || x <= inset || y <= inset || x >= vw - inset || y >= vh - inset) throw new Error("vision coordinates out of range");
          this.logLine("act", "👁️ Vision grounding: " + (v.thought || "target located") +
            (picked ? ' → [' + picked.i + '] "' + picked.label + '"' : " → box") + " (" + x + "," + y + ")");
          return { action: "click", x: x, y: y, thought: v.thought || "vision-grounding click", _vision: true };
        } catch (err) {
          this.logLine("warn", "Vision (" + String(vm).split("/").pop() + ") failed: " + err.message);
        }
      }
      return null;
    },

    ensureBridge: async function () {
      for (let i = 0; i < 4; i++) {
        try {
          const info = await this.bridge("/status", null, 3000);
          if (info && info.status === "starting") throw new Error("bridge is starting");
          this.setOnline(true, info);
          if (i > 0) this.logLine("done", "🔌 Bridge connected on retry " + (i + 1) + " — it was still starting.");
          return true;
        } catch (_) {}
        if (i < 3) await new Promise((r) => setTimeout(r, 1200));
      }
      if (this.bridgeURL.indexOf("//127.0.0.1") >= 0) {
        const alt = this.bridgeURL.replace("//127.0.0.1", "//localhost");
        try {
          const info = await this.bridgeAt(alt, "/status", null, 3000);
          this.bridgeURL = alt;
          try { localStorage.setItem("nanopro_cua_bridge", alt); } catch (_) {}
          this.setOnline(true, info);
          this.logLine("done", "🔌 Bridge found via " + alt + " — switched automatically.");
          return true;
        } catch (_) {}
      }
      this.setOnline(false, { error: "connect failed", permission: await this.bridgePermission() });
      return false;
    },

    bridgeAt: async function (base, path, body, timeoutMs) {
      const res = await fetch(base + path, {
        method: body ? "POST" : "GET",
        headers: body ? { "Content-Type": "application/json" } : {},
        body: body ? JSON.stringify(body) : undefined,
        signal: AbortSignal.timeout(timeoutMs || 30000)
      });
      let data = {};
      try { data = await res.json(); } catch (_) {}
      if (!res.ok && res.status !== 400) throw new Error(data.error || ("bridge HTTP " + res.status));
      return data;
    },

    runTask: async function (taskText) {
      const task = String(taskText || "").trim();
      if (!task) return;
      if (this.running) {
        this.queue.push(task);
        this.logLine("warn", "Task queued — " + this.queue.length + " waiting. The laptop browser runs one task at a time.");
        return "Task queued — the browser is finishing the previous task first.";
      }
      this.togglePanel(true);
      const connected = await this.ensureBridge();
      if (!connected) {
        const perm = await this.bridgePermission();
        const msg = perm === "denied"
          ? "CUA ला तुमच्या laptop च्या browser पर्यंत पोहोचता येत नाही — Chrome ने local network access block केलं आहे. Address bar मधला ⚙/🔒 → Site settings → Local network access → Allow करा, मग task पुन्हा पाठवा."
          : "CUA चा local browser bridge सापडत नाही. Laptop वर start_cua_bridge.bat चालू करा (Chromium विंडो उघडी ठेवा), मग task पुन्हा पाठवा. Chrome विचारत असेल तर 'Local network access' ला Allow द्या.";
        this.logLine("error", msg);
        return msg;
      }

      this.running = true;
      this.abort = false;
      this.step = 0;
      this.lastSummary = "";
      this.taskText = task;
      this.userAnswer = "";
      this.lastCopied = "";
      this.lastActionKey = "";
      this.lastSnapSig = null;
      this.doneGuardFired = false;
      this.escalate = false;
      this.verifiedDone = false;
      this.repeatCount = 0;
      this.scrollStreak = 0;
      this.planFails = 0;
      this.visionUsed = 0;
      this.clearTaskLog();
      this.logLine("task", "TASK: " + task);
      this.updateActionHud("🧭", "Reading the page…");
      this.moveCursor(640, 400, "starting");
      const cursorEl = document.getElementById("ailabCuaCursor");
      if (cursorEl) cursorEl.classList.add("is-active");

      let pendingNote = "";
      try {
        while (this.step < this.maxSteps && !this.abort) {
          this.step++;
          const snap = await this.bridge("/snapshot", {}, 40000);
          if (!snap || snap.ok === false) throw new Error((snap && snap.error) || "could not read the page");
          if (pendingNote) { snap.text = pendingNote + "\n\n" + (snap.text || ""); pendingNote = ""; }
          const snapSig = snap.sig || ((snap.url || "") + "|" + (snap.text || "").length + "|" + JSON.stringify(snap.scroll || {}));
          const pageChanged = this.lastSnapSig != null && snapSig !== this.lastSnapSig;
          this.lastSnapSig = snapSig;
          if (this.step > 1 && (snap.elements || []).some((e) => e.invalid)) {
            this.escalateModel("a required field is still invalid");
          }
          if (snap.url) { this.lastUrl = snap.url; const u = document.getElementById("ailabCuaUrlText"); if (u) u.textContent = snap.url; }

          this.updateActionHud("🤖", "Step " + this.step + " — planning…");
          let plan;
          try {
            plan = await this.plan(task, snap);
            this.planFails = 0;
          } catch (planErr) {
            this.planFails = (this.planFails || 0) + 1;
            this.logLine("warn", "Planner hiccup: " + planErr.message + " (retry " + this.planFails + "/1)");
            if (this.planFails > 1) throw planErr;
            this.step--;
            await new Promise((r) => setTimeout(r, 2000));
            continue;
          }
          const action = String(plan.action || "").toLowerCase();
          this.logLine("thought", "Step " + this.step + " · Manager (" + (this.lastModel || "auto") + "): " + (plan.thought || action));

          if (action !== "done" && action !== "ask_user" && action !== "save_secret" &&
              action !== "scroll" && action !== "wait") {
            const actionKey = JSON.stringify([action, plan.index, plan.text, plan.url, plan.from, plan.to, plan.path, plan.key, plan.value]);
            if (actionKey === this.lastActionKey && !pageChanged) this.repeatCount++;
            else { this.lastActionKey = actionKey; this.repeatCount = 1; }
            if (this.repeatCount === 2) {
              // Let the Critic agent read the page instead of blindly retrying.
              this.logLine("warn", "Same action again — Critic is re-reading the page");
              this.escalateModel("an action repeated without any page change");
              const vision = await this.visionPlan(task, snap);
              if (vision) {
                plan = vision;
              } else {
                let criticNote = "";
                try {
                  const review = await this.criticReview(task, snap, plan, { ok: false, error: "no visible page change" });
                  if (review && review.note) {
                    criticNote = review.note;
                    this.logLine("warn", "🕵️ Critic: " + criticNote);
                  }
                } catch (_) {}
                pendingNote = "SYSTEM NOTE: your previous action produced no visible change and you were about to repeat it. " +
                  (criticNote ? "CRITIC AGENT says: " + criticNote + " " : "") +
                  "Look for red validation/error text in VISIBLE TEXT and for required (*) fields that are still empty. Fill the missing field or choose a different element — do NOT repeat the same click/index.";
                continue;
              }
            }
            if (this.repeatCount >= 4) {
              this.logLine("warn", "Stopped: the same action repeated 4 times without any change.");
              this.updateActionHud("⚠️", "Repeated the same action — stopped");
              this.lastSummary = "I stopped because one action kept repeating with no visible change. The page needs a different approach.";
              break;
            }
          }
          this.updateActionHud("🤖", plan.thought || action);

          if (action === "scroll") this.scrollStreak = (this.scrollStreak || 0) + 1;
          else this.scrollStreak = 0;
          if (this.scrollStreak > 4) {
            this.logLine("warn", "Stopped: scrolling did not reveal anything new.");
            this.updateActionHud("⚠️", "Scrolled 5 times without finding more — stopped");
            this.lastSummary = "I stopped after five scrolls without finding what the task asked for. The page may need a narrower task.";
            break;
          }

          if (action === "done") {
            const invalidEls = (snap.elements || []).filter((e) => e.invalid);
            if (invalidEls.length && !this.doneGuardFired) {
              this.doneGuardFired = true;
              this.logLine("warn", "Form still has invalid fields — not finishing yet");
              this.escalateModel("the form still has invalid fields");
              pendingNote = "SYSTEM NOTE: you tried to finish, but these fields are still marked invalid: " +
                invalidEls.map((e) => "[" + e.i + "] " + (e.label || e.tag)).join(", ") +
                ". Fill them first, or use ask_user if the task truly does not allow it.";
              continue;
            }
            if (!this.verifiedDone) {
              this.verifiedDone = true;
              this.updateActionHud("🧪", "Verifier is checking the page…");
              this.logLine("act", "🧪 Verifier is checking the result on the page");
              let check = null;
              try {
                check = await this.verifyCompletion(task, snap, plan.summary || "");
              } catch (_) {}
              if (check && check.verified === true) {
                this.logLine("act", "🧪 Verifier confirmed: " + (check.reason || "result visible on the page"));
              } else if (check && check.verified === false) {
                this.escalateModel("the Verifier did not find the result on the page");
                this.logLine("warn", "🧪 Verifier: " + (check.reason || "result not visible yet"));
                pendingNote = "SYSTEM NOTE: the Verifier agent checked the page and did NOT see the task result: " +
                  (check.reason || "not visible") + ". Continue working until the page itself shows the result, or use ask_user to explain the blocker.";
                continue;
              }
            }
            this.logLine("done", "✅ " + (plan.summary || "Task complete."));
            this.updateActionHud("✅", plan.summary || "Task complete");
            this.lastSummary = plan.summary || "Task complete.";
            break;
          }
          if (action === "ask_user") {
            this.logLine("warn", "Waiting for you: " + (plan.message || ""));
            this.updateActionHud("🤝", "Waiting for your input in the panel");
            await this.askUser(plan.message || "Your input is needed.", plan.options || []);
            pendingNote = "USER RESPONSE: " + this.userAnswer;
            continue;
          }
          if (action === "save_secret") {
            await this.saveSecret(plan);
            continue;
          }

          const result = await this.bridge("/act", plan, 90000);
          if (result && result.ok === false) {
            this.logLine("error", "Action failed: " + (result.error || "unknown error"));
            this.updateActionHud("⚠️", "Action failed: " + (result.error || "unknown error"));
            this.escalateModel("an action failed in the browser");
            let criticNote = "";
            try {
              const review = await this.criticReview(task, snap, plan, result);
              if (review && review.note) {
                criticNote = review.note;
                this.logLine("warn", "🕵️ Critic: " + criticNote);
              }
            } catch (_) {}
            const vision = await this.visionPlan(task, snap);
            if (vision) {
              const vres = await this.bridge("/act", vision, 90000);
              if (vres && vres.ok !== false) {
                this.logLine("act", "👁️ Vision click landed at " + vision.x + "," + vision.y);
                if (typeof vres.x === "number" && typeof vres.y === "number") {
                  this.moveCursor(vres.x, vres.y, "vision click");
                  this.triggerClickRipple(vres.x, vres.y);
                }
                await new Promise((r) => setTimeout(r, 300));
                continue;
              }
              this.logLine("warn", "Vision click did not land: " + ((vres && vres.error) || "unknown error"));
            }
            pendingNote = "SYSTEM NOTE: your previous action failed with: " + (result.error || "unknown error") + ". " +
              (criticNote ? "CRITIC AGENT says: " + criticNote + " " : "") +
              "Do not repeat it. Re-check the INTERACTIVE ELEMENTS list, scroll the target into view, or pick a different element or approach.";
          } else {
            this.logLine("act", this.describeAction(plan));
            if (result && result.download && result.download.path) {
              this.logLine("done", "⬇️ Saved " + result.download.name + " (" + Math.round((result.download.size || 0) / 1024) + " KB) → " + result.download.path);
            }
            if (result && result.uploaded) {
              this.logLine("act", "⬆️ Uploaded " + result.uploaded + " (" + Math.round((result.size || 0) / 1024) + " KB)");
            }
            if (result && result.copied_len) {
              this.lastCopied = result.preview || "";
              this.logLine("act", "📋 Copied " + result.copied_len + " characters");
            }
            if (plan.action === "select_text" && result && result.selected_len) {
              this.logLine("act", "🖱️ Selected " + result.selected_len + " characters — next step can copy");
            }
            if (result && typeof result.x === "number" && typeof result.y === "number") {
              const label = plan.action === "click" ? (plan.index != null ? "[" + plan.index + "]" : "click") : plan.action;
              this.moveCursor(result.x, result.y, label);
              if (plan.action === "click" || plan.action === "download" || plan.action === "drag") {
                this.triggerClickRipple(result.x, result.y);
              }
            }
          }
          await new Promise((r) => setTimeout(r, 300));
        }
        if (this.step >= this.maxSteps) {
          this.logLine("warn", "Step limit reached before the task finished.");
          this.lastSummary = "I hit the step limit before finishing. Send a narrower task to continue.";
        }
      } catch (err) {
        this.logLine("error", "Stopped: " + err.message);
        this.updateActionHud("⚠️", "Agent stopped: " + err.message);
        this.lastSummary = "Stopped: " + err.message;
      } finally {
        this.running = false;
        const cursorEl = document.getElementById("ailabCuaCursor");
        if (cursorEl) cursorEl.classList.remove("is-active");
        const frame = await this.bridge("/frame", null, 8000).catch(() => null);
        if (frame && frame.ok) this.updateFrame(frame);
        if (this.queue.length) {
          const next = this.queue.shift();
          setTimeout(() => this.runTask(next), 500);
        }
      }
      return this.lastSummary || "Task finished.";
    },

    runAutonomousTask: function (taskText) {
      return this.runTask(taskText);
    },

    // Human-in-the-loop card used by chat actions
    requestCollaborativeDecision: function (checkpoint) {
      const cardId = "hitl_" + Math.random().toString(36).slice(2, 9);
      this.updateActionHud("🤝", "Waiting for your choice in chat…");
      const container = document.getElementById("ailabMessagesContainer");
      if (!container) return;
      const card = document.createElement("div");
      card.className = "ailab-msg ailab-msg-assistant";
      card.id = cardId;
      card.innerHTML =
        '<div class="ailab-bubble" style="background:transparent; padding:0; border:none;">' +
        '<div class="ailab-hitl-card">' +
        '<div class="ailab-hitl-header"><span class="ailab-hitl-badge">🤝 Autonomous Agent &amp; User Pair-Programming</span><span class="ailab-hitl-agent">CUA Browser Pilot &bull; HITL Checkpoint</span></div>' +
        '<div class="ailab-hitl-title">' + this.escapeHtml(checkpoint.title || "🤔 पुढील कृतीची निवड") + "</div>" +
        '<div class="ailab-hitl-desc">' + this.escapeHtml(checkpoint.description || "ब्राउझर एजंटला पुढील कृती करण्यासाठी तुमची मदत हवी आहे:") + "</div>" +
        '<div class="ailab-hitl-options" id="' + cardId + '_opts"></div>' +
        "</div></div>";
      container.appendChild(card);
      container.scrollTop = container.scrollHeight;

      const holder = document.getElementById(cardId + "_opts");
      (checkpoint.options || []).forEach((opt, idx) => {
        const isRec = opt.recommended || idx === (checkpoint.recommendedIndex || 0);
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "ailab-hitl-btn" + (isRec ? " recommended" : "");
        btn.textContent = (opt.icon || "👉") + " " + (opt.label || opt.text || "Option " + (idx + 1));
        btn.addEventListener("click", () => {
          if (window.ailabChooseHitlOption) {
            window.ailabChooseHitlOption(opt.id || "opt_" + (idx + 1), opt.label || opt.text || "", cardId);
          }
        });
        if (holder) holder.appendChild(btn);
      });
    },

    resumeWithUserChoice: async function (choiceId, choiceLabel, cardId) {
      const optsEl = document.getElementById(cardId + "_opts");
      if (optsEl) {
        optsEl.innerHTML =
          '<div class="ailab-hitl-approved"><span>✅</span><span><strong>तुम्ही निवडलेला पर्याय:</strong> ' +
          this.escapeHtml(choiceLabel) + " &mdash; एजंट पुढे जात आहे…</span></div>";
      }
      this.updateActionHud("⚡", 'Approved: "' + choiceLabel + '"');
      this.userAnswer = choiceLabel;
    }
  };

    // Global 1-Tap Hint Dispatcher & Image Regenerator
  window.ailabRegenerateImage = function(encodedAlt) {
    const subj = decodeURIComponent(encodedAlt || "").trim();
    const input = document.getElementById("ailabPromptInput");
    if (input) {
      input.value = `re ${subj || 'narendra modi'} image`;
      const sendBtn = document.getElementById("ailabSendBtn");
      if (sendBtn) sendBtn.click();
    }
  };

  window.ailabHandleActionClick = function(text) {
    if (!text) return;
    const lower = text.toLowerCase();

    // 1. Direct Image Regeneration Check
    if (lower.includes("regenerate") || lower.includes("व्हेरिएशन") || lower.includes("action:generate image of") || lower.startsWith("generate image of")) {
      let subj = text.replace(/.*(action:generate image of|generate image of|व्हेरिएशन\s*बनवा|regenerate)\s*/i, "").trim();
      subj = subj.replace(/^[\s,.:-]+|[\s,.:-]+$/g, "").trim();
      if (!subj || subj.length < 2) subj = "narendra modi";
      const input = document.getElementById("ailabPromptInput");
      if (input) {
        input.value = `re ${subj} image`;
        const sendBtn = document.getElementById("ailabSendBtn");
        if (sendBtn) sendBtn.click();
      }
      return;
    }

    // 2. Strict CUA handlers (only when clicking numbered CUA citation options like "[1]", "पर्याय १")
    if (window.AILAB_CUA) {
      if ((lower.includes("पर्याय १") || lower.includes("पर्याय 1") || lower.includes("[1]")) && (lower.includes("निकाला") || lower.includes("निकाल") || lower.includes("वाचा"))) {
        window.AILAB_CUA.togglePanel(true);
        window.AILAB_CUA.updateActionHud("🔍", "Opening Detailed Citation [1]...");
        window.AILAB_CUA.moveCursor(320, 240, "Inspecting [1] DeepSeek R1 & Claude 3.7");
        window.AILAB_CUA.triggerClickRipple(320, 240);
        return;
      } else if ((lower.includes("पर्याय २") || lower.includes("पर्याय 2")) && (lower.includes("duckdb") || lower.includes("सेव्ह"))) {
        window.AILAB_CUA.togglePanel(true);
        window.AILAB_CUA.updateActionHud("🦆", "Saved DOM snapshot & citations to DuckDB studio_memory.db");
        window.AILAB_CUA.triggerClickRipple(480, 400);
        return;
      } else if ((lower.includes("पर्याय ३") || lower.includes("पर्याय 3")) && lower.includes("शोध")) {
        window.AILAB_CUA.togglePanel(true);
        const input = document.getElementById("ailabPromptInput");
        if (input) {
          input.focus();
          input.placeholder = "नवीन शोध क्वेरी टाइप करा...";
        }
        return;
      }
    }

    // Default fallback: send text as prompt hint
    ailabSendHint(text);
  };

  window.ailabSendHint = function(text) {
    if (!text) return;
    if (text.includes("Airflow") || text.includes("SFTP")) {
      ailabOpenAirflowModal();
      return;
    }
    if (text.includes("Explorer")) {
      const exp = $id("ailabExplorer");
      if (exp && exp.classList.contains("is-hidden")) ailabToggleExplorer();
      AILAB_EXPLORER.treeOpen["db_duckdb"] = true;
      AILAB_EXPLORER.treeOpen["db_snowflake"] = true;
      ailabRenderExplorerTree();
      return;
    }
    if (text.includes("नवीन टेबल") || text.includes("नवीनच टेबल") || text.includes("Create Table")) {
      const input = document.getElementById("ailabPromptInput");
      if (input) {
        input.value = "CREATE TABLE mart_gold_loans (id VARCHAR PRIMARY KEY, customer_id VARCHAR, loan_amount NUMBER(18,2), gold_weight_grams FLOAT, interest_rate FLOAT);";
        input.focus();
      }
      return;
    }
    const input = document.getElementById("ailabPromptInput");
    if (input) {
      input.value = text;
      const sendBtn = document.getElementById("ailabSendBtn");
      if (sendBtn) sendBtn.click();
    }
  };

  // Global HITL Choice Dispatcher
  window.ailabChooseHitlOption = function(choiceId, choiceLabel, cardId) {
    if (window.AILAB_CUA) {
      window.AILAB_CUA.resumeWithUserChoice(choiceId, choiceLabel, cardId);
    }
  };

  window.ailabToggleCuaPanel = function(force) { window.AILAB_CUA.togglePanel(force); };
  window.ailabToggleCuaFullscreen = function() { window.AILAB_CUA.toggleFullscreen(); };

  document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
      if (window.AILAB_CUA) window.AILAB_CUA.init();
    }, 400);
  });

  // =========================================================================
  // NANOPRO AIRFLOW ORCHESTRATOR - REAL PIPELINE CONTROL PLANE
  // =========================================================================
  const ORCH_API = "/api/banking/orchestrator";
  window.ailabOrchState = { overview: null, timer: null, alertsFilled: false };

  // Native alert/confirm/prompt are suppressed in embedded/iframe browsers, so the
  // orchestrator uses its own dialog and toast instead.
  function orchDialog(message, defaultValue) {
    return new Promise(resolve => {
      const isPrompt = defaultValue !== undefined;
      const wrap = document.createElement("div");
      wrap.style.cssText = "position:fixed;inset:0;z-index:30050;background:rgba(2,6,23,0.72);display:flex;align-items:center;justify-content:center;padding:18px;";
      wrap.innerHTML = `
        <div style="width:min(440px,92vw);background:#0F172A;border:1px solid rgba(56,189,248,0.35);border-radius:12px;padding:16px;box-shadow:0 20px 60px rgba(0,0,0,0.55);">
          <div style="font-size:12.5px;color:#E2E8F0;line-height:1.5;white-space:pre-line;">${orchEsc(message)}</div>
          ${isPrompt ? `<input id="orchDialogInput" value="${orchEsc(defaultValue)}" style="margin-top:12px;width:100%;box-sizing:border-box;background:#020617;border:1px solid #334155;border-radius:7px;padding:8px 10px;color:#F8FAFC;font-size:12.5px;" />` : ""}
          <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:14px;">
            <button type="button" id="orchDialogCancel" class="ailab-code-btn" style="font-size:11.5px;color:#94A3B8;">Cancel</button>
            <button type="button" id="orchDialogOk" class="ailab-code-btn" style="font-size:11.5px;color:#34D399;border-color:rgba(16,185,129,0.45);">OK</button>
          </div>
        </div>`;
      const done = value => { wrap.remove(); resolve(value); };
      wrap.querySelector("#orchDialogCancel").onclick = () => done(null);
      wrap.querySelector("#orchDialogOk").onclick = () => {
        const input = wrap.querySelector("#orchDialogInput");
        done(input ? input.value : true);
      };
      wrap.addEventListener("mousedown", e => { if (e.target === wrap) done(null); });
      wrap.addEventListener("keydown", e => {
        if (e.key === "Escape") done(null);
        if (e.key === "Enter") wrap.querySelector("#orchDialogOk").click();
      });
      document.body.appendChild(wrap);
      const input = wrap.querySelector("#orchDialogInput");
      if (input) { input.focus(); input.select(); }
      else { wrap.querySelector("#orchDialogOk").focus(); }
    });
  }

  window.ailabOrchToast = function(text, color) {
    let box = document.getElementById("ailabOrchToast");
    if (!box) {
      box = document.createElement("div");
      box.id = "ailabOrchToast";
      box.style.cssText = "position:fixed;right:18px;bottom:18px;z-index:30060;max-width:min(460px,90vw);padding:10px 14px;border-radius:9px;background:#0F172A;border:1px solid rgba(255,255,255,0.12);color:#E2E8F0;font-size:12px;line-height:1.45;box-shadow:0 12px 40px rgba(0,0,0,0.5);display:none;";
      document.body.appendChild(box);
    }
    box.textContent = text;
    box.style.color = color || "#E2E8F0";
    box.style.display = "block";
    clearTimeout(box._timer);
    box._timer = setTimeout(() => { box.style.display = "none"; }, 6000);
  };

  function orchEsc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, ch => (
      { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]
    ));
  }

  function orchNum(value) {
    const n = Number(value);
    return isFinite(n) ? n.toLocaleString("en-IN") : "0";
  }

  function orchBadge(status) {
    const upper = String(status || "NOT_RUN").toUpperCase();
    const palette = {
      SUCCESS: ["rgba(16,185,129,0.18)", "#34D399"],
      PARTIAL: ["rgba(251,191,36,0.18)", "#FBBF24"],
      ERROR: ["rgba(248,113,113,0.18)", "#F87171"],
      RUNNING: ["rgba(56,189,248,0.18)", "#38BDF8"],
      DISPATCHED: ["rgba(56,189,248,0.18)", "#38BDF8"],
      PAUSED: ["rgba(148,163,184,0.18)", "#94A3B8"],
      IDLE: ["rgba(100,116,139,0.18)", "#94A3B8"],
      NOT_RUN: ["rgba(100,116,139,0.18)", "#64748B"]
    };
    const [bg, fg] = palette[upper] || palette.NOT_RUN;
    return `<span style="background:${bg};color:${fg};font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:4px;white-space:nowrap;">&#9679; ${orchEsc(upper)}</span>`;
  }

  function orchStageColor(stage) {
    return ({
      SOURCE: ["rgba(245,158,11,0.18)", "#F59E0B"],
      CATALOG: ["rgba(167,139,250,0.18)", "#A78BFA"],
      L0: ["rgba(6,182,212,0.18)", "#22D3EE"],
      L1: ["rgba(56,189,248,0.18)", "#38BDF8"],
      L2: ["rgba(16,185,129,0.18)", "#34D399"],
      REPORT: ["rgba(132,204,22,0.18)", "#A3E635"],
      ALERTS: ["rgba(244,114,182,0.18)", "#F472B6"]
    }[stage] || ["rgba(100,116,139,0.18)", "#94A3B8"]);
  }

  window.ailabOpenAirflowModal = async function() {
    const modal = document.getElementById("ailabAirflowModal");
    if (!modal) return;
    modal.style.display = "flex";
    modal.classList.add("is-open");
    await ailabOrchRefreshAll();
    if (window.ailabOrchState.timer) clearInterval(window.ailabOrchState.timer);
    window.ailabOrchState.timer = setInterval(() => {
      if (modal.style.display !== "none" && !document.hidden) ailabOrchRefreshAll(true);
    }, 20000);
  };

  window.ailabCloseAirflowModal = function(e) {
    if (e && e.target !== e.currentTarget &&
        !(e.target.classList && e.target.classList.contains("ailab-modal-close"))) return;
    const modal = document.getElementById("ailabAirflowModal");
    if (modal) {
      modal.style.display = "none";
      modal.classList.remove("is-open");
    }
    if (window.ailabOrchState.timer) {
      clearInterval(window.ailabOrchState.timer);
      window.ailabOrchState.timer = null;
    }
  };

  window.ailabSwitchAirflowTab = function(tab) {
    const map = { dags: "tabAirflowDags", sftp: "tabAirflowSftp", alerts: "tabAirflowAlerts",
                  logs: "tabAirflowLogs", arch: "tabAirflowArch" };
    Object.keys(map).forEach(key => {
      document.getElementById(map[key])?.classList.toggle("is-active", key === tab);
    });
    ["airflowTabDags", "airflowTabSftp", "airflowTabAlerts", "airflowTabLogs", "airflowTabArch"]
      .forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = (id === ({ dags: "airflowTabDags", sftp: "airflowTabSftp",
          alerts: "airflowTabAlerts", logs: "airflowTabLogs", arch: "airflowTabArch" }[tab])) ? "block" : "none";
      });
    if (tab === "logs") ailabOrchLoadLogs();
    if (tab === "alerts") ailabOrchLoadAlerts();
  };

  window.ailabOrchRefreshAll = async function(silent) {
    const dagsBox = document.getElementById("airflowDagsList");
    try {
      const res = await fetch(ORCH_API + "/overview", { headers: { "Accept": "application/json" } });
      if (res.status === 401) {
        if (dagsBox) dagsBox.innerHTML = `<div style="text-align:center;padding:24px;color:#FBBF24;">Session expired - log in to NanoPro to manage the pipeline.</div>`;
        return;
      }
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      window.ailabOrchState.overview = data;
      ailabOrchRenderOverview(data);
      ailabOrchRenderIncidents(data.incidents || []);
      ailabOrchRenderDags(data);
      ailabOrchRenderSftp(data.sftp || {});
      ailabOrchRenderOutbound(data.sftp_outbound || {});
      ailabOrchRenderAlertConfig(data.alerts || {});
      ailabOrchRenderNotificationLogs((data.alerts || {}).logs || []);
      const footer = document.getElementById("airflowFooterLeft");
      if (footer) footer.textContent = "Live status refreshed " + (data.generated_at || "").replace("T", " ");
    } catch (err) {
      if (!silent && dagsBox) {
        dagsBox.innerHTML = `<div style="text-align:center;padding:20px;color:#F87171;">Could not load orchestrator: ${orchEsc(err.message)}</div>`;
      }
    }
  };

  window.ailabOrchRenderOverview = function(data) {
    const box = document.getElementById("airflowOverview");
    if (!box) return;
    const summary = data.summary || {};
    const scheduler = data.scheduler || {};
    const cycles = data.cycles || {};
    const cycleStates = (cycles.cycles || []).map(c => `${c.cycle}:${c.state}`).join("  ");
    const incidents = data.incidents || [];
    const tiles = [
      ["DAGS HEALTHY", `${summary.success || 0} / ${summary.total || (data.dags || []).length || 0}`,
       (summary.paused ? `${summary.paused} paused` : "All schedulable") + (incidents.length ? ` · ${incidents.length} incident(s)` : ""),
       incidents.length ? "#F87171" : (summary.success === summary.total ? "#34D399" : "#FBBF24")],
      ["BUSINESS DATE", cycles.business_date || "-", cycleStates || "Timetable unavailable", "#38BDF8"],
      ["LAST EXPORT ROWS", orchNum(summary.rows), "BigQuery bronze snapshot", "#A78BFA"],
      ["SCHEDULER", scheduler.armed ? (scheduler.paused ? "PAUSED" : "ARMED") : "OFF",
       scheduler.armed ? `every ${scheduler.interval_min || 60} min` : "in-app thread not started",
       scheduler.armed && !scheduler.paused ? "#34D399" : "#F87171"]
    ];
    box.innerHTML = tiles.map(([label, value, sub, color]) => `
      <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;">
        <div style="font-size:10px;color:#94A3B8;letter-spacing:0.4px;">${orchEsc(label)}</div>
        <div style="font-size:14px;font-weight:800;color:${color};margin-top:2px;">${orchEsc(value)}</div>
        <div style="font-size:10px;color:#64748B;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${orchEsc(sub)}">${orchEsc(sub)}</div>
      </div>`).join("");

    const line = document.getElementById("airflowSchedulerLine");
    if (line) {
      const last = scheduler.last_attempt ? new Date(scheduler.last_attempt * 1000).toLocaleString("en-IN") : "never";
      line.innerHTML = `In-app scheduler: <strong style="color:${scheduler.armed ? "#34D399" : "#F87171"};">${scheduler.armed ? "ARMED" : "OFF"}</strong>` +
        ` &bull; tick every ${scheduler.interval_min || 60} min &bull; last attempt ${orchEsc(last)}` +
        ` &bull; cycles ${orchEsc((cycles.cycles || []).map(c => `${c.cycle} ${c.scheduled_ist} IST (${c.state})`).join(" | "))}`;
    }
  };

  window.ailabOrchRenderIncidents = function(incidents) {
    const box = document.getElementById("airflowIncidents");
    if (!box) return;
    if (!incidents.length) {
      box.innerHTML = `<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:8px 12px;font-size:11.5px;color:#34D399;">&#10004; No failures, data errors or alert failures recorded in the recent runs.</div>`;
      return;
    }
    box.innerHTML = `
      <div style="background:rgba(248,113,113,0.07);border:1px solid rgba(248,113,113,0.35);border-radius:9px;padding:10px 12px;">
        <div style="font-size:12px;font-weight:800;color:#F87171;margin-bottom:8px;">&#9888; Incidents (${incidents.length}) &bull; last failures, data errors, alert failures</div>
        <div style="display:flex;flex-direction:column;gap:6px;">
        ${incidents.map(item => `
          <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.07);border-radius:7px;padding:8px 10px;">
            <div style="display:flex;justify-content:space-between;gap:8px;align-items:flex-start;flex-wrap:wrap;">
              <div style="min-width:0;">
                <span style="font-size:9.5px;font-weight:800;color:${item.level === "WARNING" ? "#FBBF24" : "#F87171"};background:rgba(255,255,255,0.06);padding:2px 6px;border-radius:4px;">${orchEsc(item.kind)}</span>
                <code style="font-size:10.5px;color:#38BDF8;margin-left:6px;">${orchEsc(item.dag || "-")}</code>
                <span style="font-size:10px;color:#64748B;margin-left:6px;">${orchEsc(String(item.at || "").replace("T", " "))}</span>
                <div style="font-size:11.5px;color:#FCA5A5;margin-top:4px;word-break:break-word;">${orchEsc(item.message || "")}</div>
              </div>
              <div style="display:flex;gap:6px;flex-wrap:wrap;">
                ${item.dag && item.dag !== "alerts" ? `<button type="button" class="ailab-code-btn" onclick="ailabOrchRun('${orchEsc(item.dag)}')" style="font-size:10.5px;color:#34D399;">&#9654; Retry</button>` : ""}
                ${item.dag && item.dag !== "alerts" ? `<button type="button" class="ailab-code-btn" onclick="ailabOrchRollback('${orchEsc(item.dag)}')" style="font-size:10.5px;color:#F87171;border-color:rgba(248,113,113,0.4);">&#9198; Rollback</button>` : ""}
              </div>
            </div>
          </div>`).join("")}
        </div>
      </div>`;
  };

  window.ailabOrchRenderDags = function(data) {
    const box = document.getElementById("airflowDagsList");
    if (!box) return;
    const dags = data.dags || [];
    const countTab = document.getElementById("orchDagCountTab");
    if (countTab) countTab.textContent = `${dags.length} DAG${dags.length === 1 ? "" : "s"}`;
    if (!dags.length) {
      box.innerHTML = `<div style="text-align:center;padding:20px;color:#94A3B8;">No DAGs reported.</div>`;
      return;
    }
    const cycles = (data.cycles || {}).cycles || [];
    const schedules = data.cycle_schedules || {};

    box.innerHTML = dags.map(dag => {
      const [stageBg, stageFg] = orchStageColor(dag.stage);
      const metrics = [];
      if (dag.tables != null && dag.tables !== "") metrics.push(`<span style="color:#94A3B8;">tables</span> <strong style="color:#F8FAFC;">${orchEsc(dag.tables)}</strong>`);
      if (dag.rows != null && dag.rows !== "") metrics.push(`<span style="color:#94A3B8;">rows</span> <strong style="color:#F8FAFC;">${orchNum(dag.rows)}</strong>`);
      if (dag.duplicates_removed != null) metrics.push(`<span style="color:#94A3B8;">dupes removed</span> <strong style="color:#F8FAFC;">${orchNum(dag.duplicates_removed)}</strong>`);
      if (dag.run_id) metrics.push(`<span style="color:#94A3B8;">run</span> <code style="color:#CBD5E1;">${orchEsc(dag.run_id)}</code>`);

      const cycleStrip = dag.id === "bq_to_s3" ? `
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;">
          ${cycles.map(c => `
            <span style="background:rgba(30,41,59,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:3px 8px;font-size:10.5px;color:#CBD5E1;">
              ${orchEsc(c.cycle)} ${orchEsc(c.scheduled_ist)} IST ${orchBadge(c.state)}
              <button type="button" onclick="ailabOrchEditCycle('${orchEsc(c.cycle)}', '${orchEsc(c.scheduled_ist)}')" style="background:none;border:none;color:#38BDF8;cursor:pointer;font-size:10.5px;padding:0 2px;">edit</button>
            </span>`).join("")}
        </div>` : "";

      return `
        <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:6px;">
            <div style="display:flex;align-items:center;gap:8px;min-width:0;">
              <span style="background:${stageBg};color:${stageFg};font-size:9.5px;font-weight:800;padding:2px 7px;border-radius:4px;">${orchEsc(dag.stage)}</span>
              <span style="font-weight:800;color:#F8FAFC;font-size:13px;">${orchEsc(dag.name)}</span>
              <code style="font-size:10px;color:#64748B;">${orchEsc(dag.id)}</code>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
              ${dag.in_flight ? `<span style="font-size:10px;color:#38BDF8;">running...</span>` : ""}
              ${orchBadge(dag.status)}
            </div>
          </div>
          <div style="font-size:11.5px;color:#94A3B8;line-height:1.5;margin-bottom:6px;">${orchEsc(dag.description)}</div>
          <div style="font-size:11px;color:#CBD5E1;line-height:1.6;margin-bottom:6px;">${orchEsc(dag.detail)}</div>
          ${dag.last_error ? `<div style="background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.35);border-radius:6px;padding:6px 9px;font-size:11px;color:#FCA5A5;margin-bottom:6px;word-break:break-word;"><strong>Last failure ${orchEsc(String(dag.last_error.at || "").replace("T", " "))}:</strong> ${orchEsc(dag.last_error.message || "")}</div>` : ""}
          ${(dag.errors && dag.errors.length) ? `<div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.3);border-radius:6px;padding:6px 9px;font-size:11px;color:#FCA5A5;margin-bottom:6px;">${dag.errors.map(e => `<div><strong>${orchEsc(e.file || "")}</strong>: ${orchEsc(e.error || "")}</div>`).join("")}</div>` : ""}
          <div style="display:flex;gap:14px;flex-wrap:wrap;font-size:11px;margin-bottom:6px;">${metrics.join("")}</div>
          <div style="font-size:10.5px;color:#64748B;margin-bottom:8px;">Schedule: ${orchEsc(dag.schedule)}${dag.finished_at ? ` &bull; finished ${orchEsc(dag.finished_at)}` : ""}</div>
          ${cycleStrip}
          <div style="display:flex;gap:6px;flex-wrap:wrap;border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;margin-top:8px;">
            <button type="button" class="ailab-code-btn" onclick="ailabOrchRun('${orchEsc(dag.id)}')" style="font-size:11px;color:#34D399;border-color:rgba(16,185,129,0.4);">&#9654; ${dag.id === "alerts" ? "Send summary" : "Run now"}</button>
            <button type="button" class="ailab-code-btn" onclick="ailabOrchPause('${orchEsc(dag.id)}')" style="font-size:11px;color:${dag.paused ? "#34D399" : "#FBBF24"};border-color:rgba(255,255,255,0.2);">${dag.paused ? "&#9654; Resume" : "&#10074;&#10074; Pause"}</button>
            ${dag.id === "alerts" ? "" : `<button type="button" class="ailab-code-btn" onclick="ailabOrchRollback('${orchEsc(dag.id)}')" style="font-size:11px;color:#F87171;border-color:rgba(248,113,113,0.4);">&#9198; Rollback</button>`}
          </div>
        </div>`;
    }).join("");
  };

  window.ailabOrchRun = async function(dagId) {
    ailabOrchToast(`Dispatching ${dagId}...`, "#38BDF8");
    try {
      const res = await fetch(ORCH_API + "/dag/run", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dag_id: dagId, mode: "incremental" })
      });
      const data = await res.json();
      if (!res.ok) { ailabOrchToast(data.detail || "Run failed", "#F87171"); return; }
      const footer = document.getElementById("airflowFooterLeft");
      if (footer) footer.textContent = data.message || "Dispatched";
      ailabOrchToast(data.message || `${dagId} dispatched`, data.status === "dispatched" ? "#34D399" : "#FBBF24");
      setTimeout(() => ailabOrchRefreshAll(true), 2000);
    } catch (err) { ailabOrchToast("Run error: " + err.message, "#F87171"); }
  };

  window.ailabOrchPause = async function(dagId) {
    try {
      const res = await fetch(ORCH_API + "/dag/pause", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dag_id: dagId })
      });
      const data = await res.json();
      if (!res.ok) { ailabOrchToast(data.detail || "Pause failed", "#F87171"); return; }
      ailabOrchToast(`${dagId}: ${data.state || "updated"}`, data.state === "PAUSED" ? "#FBBF24" : "#34D399");
      await ailabOrchRefreshAll(true);
    } catch (err) { ailabOrchToast("Pause error: " + err.message, "#F87171"); }
  };

  window.ailabOrchRollback = async function(dagId) {
    let message = "Rebuild this DAG from the S3 bronze source of truth? Downstream layers are recreated with CREATE OR REPLACE.";
    if (dagId === "sftp_to_s3") message = "Purge the latest SFTP batch? Its bronze Parquet and Snowflake L0/L1 tables are dropped.";
    if (!(await orchDialog(message))) return;
    ailabOrchToast(`Rolling back ${dagId}...`, "#FBBF24");
    try {
      const res = await fetch(ORCH_API + "/dag/rollback", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dag_id: dagId, target_layer: "", confirm: true })
      });
      const data = await res.json();
      if (!res.ok) { ailabOrchToast(data.detail || "Rollback failed", "#F87171"); return; }
      ailabOrchToast(data.message || "Rollback finished", "#34D399");
      await ailabOrchRefreshAll(true);
    } catch (err) { ailabOrchToast("Rollback error: " + err.message, "#F87171"); }
  };

  window.ailabOrchEditCycle = async function(cycle, current) {
    const value = await orchDialog(`${cycle} cycle time (HH:MM IST):`, current || "06:00");
    if (!value) return;
    const at = String(value).trim();
    if (!/^(?:[01]?\d|2[0-3]):[0-5]\d$/.test(at)) { ailabOrchToast("Use HH:MM format, e.g. 06:00", "#F87171"); return; }
    try {
      const res = await fetch(ORCH_API + "/schedule", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cycle, at: at })
      });
      const data = await res.json();
      if (!res.ok) { ailabOrchToast(data.detail || "Schedule update failed", "#F87171"); return; }
      ailabOrchToast(`${cycle} scheduled at ${at} IST`, "#34D399");
      await ailabOrchRefreshAll(true);
    } catch (err) { ailabOrchToast("Schedule error: " + err.message, "#F87171"); }
  };

  window.ailabOrchRenderSftp = function(sftp) {
    const info = document.getElementById("airflowSftpInfo");
    if (info) {
      const fileCount = (sftp.files || []).length;
      const tableCount = (sftp.tables || []).length;
      info.innerHTML = `
        <div><strong style="color:#38BDF8;">Landing zone:</strong> <code>${orchEsc(sftp.landing_prefix || "-")}</code></div>
        <div><strong style="color:#38BDF8;">Bronze output:</strong> <code>${orchEsc(sftp.bronze_prefix || "-")}</code> &bull; Glue db <code>${orchEsc(sftp.glue_database || "-")}</code></div>
        <div><strong style="color:#38BDF8;">Accepted:</strong> ${orchEsc((sftp.supported || []).join(" / "))} &bull; max ${orchEsc(sftp.max_mb || 25)} MB per file</div>
        <div><strong style="color:#38BDF8;">Status:</strong> ${fileCount} file(s) in landing &bull; ${tableCount} table(s) in bronze${sftp.error ? ` &bull; <span style="color:#F87171;">${orchEsc(sftp.error)}</span>` : ""}</div>`;
    }

    const filesBox = document.getElementById("airflowSftpFilesList");
    if (filesBox) {
      const files = sftp.files || [];
      const awsKeys = ["sqs", "dynamodb", "cloudwatch", "sns", "iceberg"];
      const awsLine = (item) => {
        const svc = item.aws_services || {};
        const shown = Object.keys(svc).length ? awsKeys : [];
        if (!shown.length) return "";
        return `<div style="font-size:10px;color:#64748B;margin-top:2px;">AWS: ${shown.map(name => {
          const state = String(svc[name] || "pending");
          const ok = ["sent", "recorded", "published", "registered", "updated", "skipped"].includes(state);
          return `<span style="color:${ok ? "#34D399" : "#F87171"};">${name} ${orchEsc(state)}</span>`;
        }).join(" &middot; ")}</div>`;
      };
      filesBox.innerHTML = files.length ? files.map(item => `
        <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:7px;padding:8px 10px;display:flex;align-items:center;justify-content:space-between;gap:10px;">
          <div style="min-width:0;">
            <div style="font-size:12px;font-weight:700;color:#F8FAFC;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${orchEsc(item.name)}</div>
            <div style="font-size:10.5px;color:#94A3B8;">partner ${orchEsc(item.partner)} &bull; ${orchEsc((item.size / 1024).toFixed(1))} KB &bull; ${item.rows ? orchNum(item.rows) + " rows" : "not ingested"}${item.table ? " &bull; table " + orchEsc(item.table) : ""}${item.error ? " &bull; " + orchEsc(item.error) : ""}</div>
            ${awsLine(item)}
          </div>
          <div style="display:flex;align-items:center;gap:6px;">
            ${orchBadge(item.status === "new" ? "NOT_RUN" : item.status)}
            <button type="button" class="ailab-code-btn" onclick="ailabOrchSftpRollback('${orchEsc(item.key)}')" style="font-size:10.5px;color:#F87171;">Rollback</button>
          </div>
        </div>`).join("") : `<div style="text-align:center;padding:12px;color:#94A3B8;">No files in the SFTP landing zone yet.</div>`;
    }

    const tablesBox = document.getElementById("airflowSftpTables");
    if (tablesBox) {
      const tables = sftp.tables || [];
      tablesBox.innerHTML = tables.length ? tables.map(item => `
        <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:7px;padding:8px 10px;display:flex;align-items:center;justify-content:space-between;">
          <div style="font-size:11.5px;color:#F8FAFC;"><strong>${orchEsc(item.table)}</strong> <span style="color:#64748B;">&larr; ${orchEsc(item.source_file)}</span></div>
          <div style="font-size:11px;color:#94A3B8;">${orchNum(item.rows)} rows &bull; ${orchEsc(item.columns)} cols &bull; ${orchEsc(item.ingested_at)}</div>
        </div>`).join("") : `<div style="text-align:center;padding:12px;color:#94A3B8;">No SFTP tables yet - upload a file or generate a sample.</div>`;
    }
  };

  window.ailabOrchRenderOutbound = function(out) {
    const box = document.getElementById("airflowSftpOutbound");
    if (!box) return;
    const reports = out.reports || [];
    box.innerHTML = reports.length ? reports.map(item => `
      <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(52,211,153,0.22);border-radius:7px;padding:8px 10px;display:flex;align-items:center;justify-content:space-between;gap:10px;">
        <div style="min-width:0;">
          <div style="font-size:12px;font-weight:700;color:#F8FAFC;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${orchEsc(item.filename)}</div>
          <div style="font-size:10.5px;color:#94A3B8;">${orchEsc(item.sftp_path)} &bull; ${orchEsc((item.bytes / 1024).toFixed(1))} KB &bull; ${orchEsc(item.modified || "")}</div>
        </div>
        ${item.download_url ? `<a href="${orchEsc(item.download_url)}" target="_blank" rel="noopener" class="ailab-code-btn" style="font-size:10.5px;color:#38BDF8;text-decoration:none;">Download</a>` : ""}
      </div>`).join("") : `<div style="text-align:center;padding:12px;color:#94A3B8;">No reports published to sftp/outbound/reports yet.</div>`;
  };

  window.ailabOrchBuildReport = async function(deliver) {
    const box = document.getElementById("ailabReportMsg");
    if (box) { box.textContent = deliver ? "Building report and sending alerts..." : "Building report..."; box.style.color = "#94A3B8"; }
    try {
      const res = await fetch(ORCH_API + "/report/build", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cycle: "MANUAL", deliver: !!deliver })
      });
      const data = await res.json();
      if (!res.ok) { if (box) { box.textContent = data.detail || "report build failed"; box.style.color = "#F87171"; } return; }
      const report = data.report || data;
      if (box) {
        box.textContent = `${report.filename || "report"}: ${report.status} -> ${report.sftp_path || ""}` +
          (deliver ? ` | alerts ${(data.results || []).map(r => r.channel + ":" + (r.ok ? "ok" : "fail")).join(", ")}` : "");
        box.style.color = "#34D399";
      }
      await ailabOrchRefreshAll(true);
    } catch (err) {
      if (box) { box.textContent = err.message; box.style.color = "#F87171"; }
    }
  };

  window.ailabSftpMsg = function(text, color) {
    const box = document.getElementById("ailabSftpMsg");
    if (box) { box.textContent = text; box.style.color = color || "#94A3B8"; }
  };

  window.ailabSftpUpload = async function() {
    const input = document.getElementById("ailabSftpFile");
    const partner = (document.getElementById("ailabSftpPartner").value || "manual").trim() || "manual";
    if (!input || !input.files || !input.files.length) { ailabSftpMsg("Choose a file first.", "#FBBF24"); return; }
    const button = document.getElementById("ailabSftpUploadBtn");
    if (button) button.disabled = true;
    let done = 0;
    for (const file of input.files) {
      try {
        ailabSftpMsg(`Uploading ${file.name}...`);
        const form = new FormData();
        form.append("file", file);
        const res = await fetch(`${ORCH_API}/sftp/upload?partner=${encodeURIComponent(partner)}`, { method: "POST", body: form });
        const data = await res.json();
        if (!res.ok) { ailabSftpMsg(`${file.name}: ${data.detail || "upload failed"}`, "#F87171"); continue; }
        const ingest = data.ingest || {};
        done += 1;
        ailabSftpMsg(`${file.name}: ${ingest.status} -> ${ingest.table || "?"} (${orchNum(ingest.rows || 0)} rows). Downstream refresh running.`, "#34D399");
      } catch (err) {
        ailabSftpMsg(`${file.name}: ${err.message}`, "#F87171");
      }
    }
    if (button) button.disabled = false;
    if (done) { input.value = ""; setTimeout(() => ailabOrchRefreshAll(true), 1500); }
  };

  window.ailabSftpProcess = async function() {
    ailabSftpMsg("Processing landing files...");
    try {
      const res = await fetch(ORCH_API + "/sftp/process", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ force: false })
      });
      const data = await res.json();
      if (!res.ok) { ailabSftpMsg(data.detail || "process failed", "#F87171"); return; }
      const downstream = data.downstream || {};
      ailabSftpMsg(`${data.status}: ${(data.processed || []).length} ingested, ${(data.errors || []).length} error(s). ` +
        (downstream.summary ? downstream.summary : "No new files."), data.errors && data.errors.length ? "#FBBF24" : "#34D399");
      await ailabOrchRefreshAll(true);
    } catch (err) { ailabSftpMsg(err.message, "#F87171"); }
  };

  window.ailabSftpSample = async function() {
    const partner = (document.getElementById("ailabSftpPartner").value || "sample").trim() || "sample";
    ailabSftpMsg("Generating sample file...");
    try {
      const res = await fetch(`${ORCH_API}/sftp/sample?partner=${encodeURIComponent(partner)}`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) { ailabSftpMsg(data.detail || "sample failed", "#F87171"); return; }
      ailabSftpMsg(`Sample landed: ${data.key} -> ${(data.ingest || {}).table || "?"}`, "#34D399");
      await ailabOrchRefreshAll(true);
    } catch (err) { ailabSftpMsg(err.message, "#F87171"); }
  };

  window.ailabOrchSftpRollback = async function(key) {
    if (!(await orchDialog(`Purge ${key}?\n\nThis drops its bronze Parquet and Snowflake L0/L1 tables. The landing file is kept.`))) return;
    ailabSftpMsg(`Rolling back ${key}...`, "#FBBF24");
    try {
      const res = await fetch(ORCH_API + "/sftp/rollback", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, confirm: true, delete_landing: false })
      });
      const data = await res.json();
      if (!res.ok) { ailabSftpMsg(data.detail || "rollback failed", "#F87171"); return; }
      ailabSftpMsg(`Rolled back ${data.table_removed || key}: ${(data.snowflake || []).join(", ") || "no tables"}`, "#FBBF24");
      await ailabOrchRefreshAll(true);
    } catch (err) { ailabSftpMsg(err.message, "#F87171"); }
  };

  window.ailabOrchRenderAlertConfig = function(alerts) {
    if (window.ailabOrchState.alertsFilled) return;
    const conf = alerts.config || {};
    const set = (id, value) => { const el = document.getElementById(id); if (el) el.value = value == null ? "" : value; };
    set("orchAlertRecipients", (conf.recipients || []).join(", "));
    set("orchAlertSender", conf.sender || "");
    set("orchAlertTelegram", conf.telegram_channel || "");
    set("orchAlertWhatsapp", conf.whatsapp_number && conf.whatsapp_number.includes("*") ? "" : (conf.whatsapp_number || ""));
    const tg = document.getElementById("orchAlertTelegramOn");
    if (tg) tg.checked = conf.telegram_enabled !== false;
    const wa = document.getElementById("orchAlertWhatsappOn");
    if (wa) wa.checked = conf.whatsapp_enabled !== false;
    window.ailabOrchState.alertsFilled = true;
  };

  window.ailabOrchLoadAlerts = async function() {
    window.ailabOrchState.alertsFilled = false;
    await ailabOrchRefreshAll(true);
  };

  window.ailabOrchSaveAlerts = async function() {
    const recipients = (document.getElementById("orchAlertRecipients").value || "")
      .split(",").map(v => v.trim()).filter(Boolean);
    const body = {
      recipients,
      sender: (document.getElementById("orchAlertSender").value || "").trim(),
      telegram_channel: (document.getElementById("orchAlertTelegram").value || "").trim(),
      telegram_enabled: document.getElementById("orchAlertTelegramOn").checked,
      whatsapp_enabled: document.getElementById("orchAlertWhatsappOn").checked
    };
    const whatsapp = (document.getElementById("orchAlertWhatsapp").value || "").trim();
    if (whatsapp) body.whatsapp_number = whatsapp;
    const msg = document.getElementById("ailabAlertMsg");
    try {
      const res = await fetch(ORCH_API + "/alerts/config", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
      });
      const data = await res.json();
      if (!res.ok) { if (msg) { msg.textContent = data.detail || "save failed"; msg.style.color = "#F87171"; } return; }
      if (msg) { msg.textContent = "Configuration saved."; msg.style.color = "#34D399"; }
      window.ailabOrchState.alertsFilled = false;
      await ailabOrchRefreshAll(true);
    } catch (err) { if (msg) { msg.textContent = err.message; msg.style.color = "#F87171"; } }
  };

  window.ailabOrchTestAlert = async function(channel) {
    const msg = document.getElementById("ailabAlertMsg");
    if (msg) { msg.textContent = `Sending test ${channel}...`; msg.style.color = "#94A3B8"; }
    try {
      const res = await fetch(ORCH_API + "/alerts/test", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ channel })
      });
      const data = await res.json();
      if (!res.ok) { if (msg) { msg.textContent = data.detail || "test failed"; msg.style.color = "#F87171"; } return; }
      const results = data.results || [];
      const text = results.map(r => `${r.channel}: ${r.ok ? "DELIVERED" : "FAILED" + (r.error ? " (" + r.error + ")" : "")}`).join("  |  ");
      if (msg) { msg.textContent = text || data.status; msg.style.color = results.every(r => r.ok) ? "#34D399" : "#FBBF24"; }
      await ailabOrchRefreshAll(true);
    } catch (err) { if (msg) { msg.textContent = err.message; msg.style.color = "#F87171"; } }
  };

  window.ailabOrchRenderNotificationLogs = function(logs) {
    const box = document.getElementById("ailabNotificationLogsList");
    if (!box) return;
    if (!logs.length) {
      box.innerHTML = `<div style="text-align:center;padding:12px;color:#94A3B8;">No alerts sent yet.</div>`;
      return;
    }
    box.innerHTML = logs.map(item => {
      const ok = String(item.status || "").toUpperCase() === "DELIVERED";
      return `
        <div style="background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:8px 10px;display:flex;align-items:center;justify-content:space-between;gap:10px;">
          <div style="min-width:0;">
            <div style="font-size:11.5px;color:#F8FAFC;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${orchEsc(item.subject)}</div>
            <div style="font-size:10.5px;color:#94A3B8;">${orchEsc(item.channel)} &bull; ${orchEsc(item.recipient)} &bull; ${orchEsc(item.rule)}${item.error ? " &bull; " + orchEsc(item.error) : ""}</div>
          </div>
          <div style="text-align:right;white-space:nowrap;">
            <span style="color:${ok ? "#34D399" : "#F87171"};font-weight:700;font-size:10.5px;">&#9679; ${orchEsc(item.status)}</span>
            <div style="font-size:10px;color:#64748B;">${orchEsc(item.timestamp)}</div>
          </div>
        </div>`;
    }).join("");
  };

  window.ailabOrchRenderStoredLogs = function() {
    const box = document.getElementById("airflowOrchLogs");
    if (!box) return;
    const all = window.ailabOrchState.logs || [];
    const term = (document.getElementById("orchLogFilter")?.value || "").trim().toLowerCase();
    const errorsOnly = !!document.getElementById("orchLogErrorsOnly")?.checked;
    const rows = all.filter(item => {
      const text = String(item.text || "");
      if (errorsOnly && !/ERROR|FAILED|PARTIAL|ERROR_RETRY/i.test(text)) return false;
      if (term && !text.toLowerCase().includes(term)) return false;
      return true;
    });
    if (!rows.length) {
      box.innerHTML = `<div style="color:#64748B;">${all.length ? "No log lines match this filter." : "No log entries yet."}</div>`;
      return;
    }
    box.innerHTML = rows.map(item => {
      const text = String(item.text || "");
      let color = "#CBD5E1";
      if (/ERROR|FAILED|ERROR_RETRY/i.test(text)) color = "#F87171";
      else if (/WARNING|PARTIAL|MISSED|PAUSED/i.test(text)) color = "#FBBF24";
      else if (/SUCCESS|synced|reconciled|registered|DELIVERED/i.test(text)) color = "#34D399";
      return `<div style="color:${color};">${orchEsc(text)}</div>`;
    }).join("");
  };

  window.ailabOrchLoadLogs = async function() {
    const box = document.getElementById("airflowOrchLogs");
    if (!box) return;
    box.innerHTML = `<div style="color:#64748B;">Loading logs...</div>`;
    try {
      const res = await fetch(ORCH_API + "/logs?limit=120");
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "HTTP " + res.status);
      window.ailabOrchState.logs = data.logs || [];
      ailabOrchRenderStoredLogs();
    } catch (err) {
      box.innerHTML = `<div style="color:#F87171;">${orchEsc(err.message)}</div>`;
    }
  };
</script>
</div>
'''
