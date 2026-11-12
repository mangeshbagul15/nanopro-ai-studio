# -*- coding: utf-8 -*-
"""
streamline_cua_ui.py:
Streamlines CUA Browser Studio to look like a clean, modern macOS/Arc browser window:
- Expands viewport stage to take maximum vertical space (min-height 500px, flex 1).
- Compacts header & omnibox with macOS dots (🔴 🟡 🟢) and clean URL bar.
- Streamlines bottom dock into a sleek, non-intrusive action bar.
- Replaces in app/ui/global_ai_lab_view.py and reinjects into deploy/complete_nanopro_dashboard.html.
"""

import os
import re

sleek_cua_css = """
/* =========================================================================
   SLEEK MODERN AUTONOMOUS BROWSER (CUA) STUDIO (MAC/ARC STYLE)
   ========================================================================= */
#view-global_ai_lab .ailab-cua-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: #0B132B;
  border: 1.5px solid #38BDF8;
  border-radius: 7px;
  color: #38BDF8;
  font-size: 11.5px;
  font-weight: 700;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
}
#view-global_ai_lab .ailab-cua-toggle-btn:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: #7DD3FC;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.4);
  transform: translateY(-1px);
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

/* CUA Right Panel */
#view-global_ai_lab .ailab-cua-panel {
  width: 50%;
  min-width: 420px;
  max-width: 65vw;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #080D14;
  border-left: 1.5px solid rgba(56, 189, 248, 0.3);
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

/* Browser Window Header Chrome (macOS Dots & Status) */
#view-global_ai_lab .ailab-cua-chrome-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #0F1724;
  border-bottom: 1px solid var(--al-line);
  flex-shrink: 0;
}
#view-global_ai_lab .ailab-window-dots {
  display: flex;
  align-items: center;
  gap: 6px;
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

#view-global_ai_lab .ailab-cua-chrome-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 700;
  color: #F8FAFC;
}
#view-global_ai_lab .ailab-badge-cua {
  font-size: 9px;
  font-weight: 700;
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.4);
  color: #38BDF8;
  padding: 1px 6px;
  border-radius: 4px;
}
#view-global_ai_lab .ailab-cua-chrome-right {
  display: flex;
  align-items: center;
  gap: 8px;
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
}

/* Modern Browser Omnibox Bar */
#view-global_ai_lab .ailab-cua-omnibox-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #0B1119;
  border-bottom: 1px solid var(--al-line);
  flex-shrink: 0;
}
#view-global_ai_lab .ailab-cua-nav-btns {
  display: flex;
  align-items: center;
  gap: 3px;
}
#view-global_ai_lab .ailab-nav-btn {
  background: transparent;
  border: 1px solid var(--al-line);
  border-radius: 5px;
  color: var(--al-muted);
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 11px;
}
#view-global_ai_lab .ailab-nav-btn:hover {
  background: var(--al-panel-2);
  color: #FFFFFF;
}
#view-global_ai_lab .ailab-cua-url-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  background: #080D14;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 6px;
  padding: 3px 8px;
}
#view-global_ai_lab .ailab-ssl-lock {
  font-size: 11px;
  color: #10B981;
}
#view-global_ai_lab .ailab-cua-url-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #F8FAFC;
  font-size: 11.5px;
  font-family: monospace;
}
#view-global_ai_lab .ailab-cua-go-btn {
  background: #38BDF8;
  border: none;
  color: #0B1119;
  font-weight: 800;
  font-size: 10px;
  padding: 2px 7px;
  border-radius: 4px;
  cursor: pointer;
}
#view-global_ai_lab .ailab-cua-chip {
  background: rgba(30, 43, 62, 0.6);
  border: 1px solid var(--al-line);
  border-radius: 4px;
  color: #94A3B8;
  font-size: 9.5px;
  padding: 2px 6px;
  cursor: pointer;
  white-space: nowrap;
}
#view-global_ai_lab .ailab-cua-chip:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: #38BDF8;
  color: #F8FAFC;
}

/* Full Height Live Screen Share Viewport Stage */
#view-global_ai_lab .ailab-cua-viewport-container {
  flex: 1 1 0% !important;
  width: 100%;
  height: 100%;
  position: relative;
  background: #FFFFFF;
  overflow: hidden;
  display: flex;
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

/* Visual Agent Cursor (Laser Pointer) */
#view-global_ai_lab .ailab-cua-cursor {
  position: absolute;
  top: 60px;
  left: 80px;
  width: 24px;
  height: 24px;
  z-index: 70;
  pointer-events: none;
  transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), top 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), left 0.35s cubic-bezier(0.2, 0.8, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 4px;
}
#view-global_ai_lab .ailab-cua-cursor-label {
  background: #EF4444;
  color: #FFFFFF;
  font-size: 9px;
  font-weight: 800;
  padding: 1px 5px;
  border-radius: 3px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.6);
  white-space: nowrap;
}

/* Click Ripple */
#view-global_ai_lab .ailab-cua-click-ripple {
  position: absolute;
  width: 32px;
  height: 32px;
  border: 2.5px solid #EF4444;
  border-radius: 50%;
  pointer-events: none;
  z-index: 69;
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.3);
}
#view-global_ai_lab .ailab-cua-click-ripple.pulsing {
  animation: cuaRippleAnim 0.5s ease-out forwards;
}
@keyframes cuaRippleAnim {
  0% { opacity: 1; transform: translate(-50%, -50%) scale(0.3); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(2.2); }
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

/* Floating Action HUD */
#view-global_ai_lab .ailab-cua-action-hud {
  position: absolute;
  bottom: 8px;
  left: 10px;
  right: 10px;
  background: rgba(11, 17, 25, 0.94);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 6px;
  padding: 5px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 60;
  font-size: 11px;
}
#view-global_ai_lab .ailab-action-icon { font-size: 13px; }
#view-global_ai_lab .ailab-action-desc {
  flex: 1;
  color: #E2E8F0;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Sleek Floating Bottom Control Dock */
#view-global_ai_lab .ailab-cua-bottom-dock {
  background: #0B1119;
  border-top: 1px solid var(--al-line);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  padding: 8px 12px;
  gap: 6px;
}
#view-global_ai_lab .ailab-cua-task-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
#view-global_ai_lab .ailab-cua-task-input {
  flex: 1;
  background: #080D14;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 5px;
  padding: 5px 8px;
  color: #F8FAFC;
  font-size: 11px;
  outline: none;
}
#view-global_ai_lab .ailab-cua-task-input:focus {
  border-color: #38BDF8;
}
#view-global_ai_lab .ailab-cua-exec-btn {
  background: linear-gradient(135deg, #38BDF8 0%, #2563EB 100%);
  border: none;
  border-radius: 5px;
  color: #FFFFFF;
  font-weight: 800;
  font-size: 10.5px;
  padding: 5px 11px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}
#view-global_ai_lab .ailab-cua-chips-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}
#view-global_ai_lab .ailab-cua-presets {
  display: flex;
  align-items: center;
  gap: 5px;
  overflow-x: auto;
}
#view-global_ai_lab .ailab-cua-telemetry-badge {
  font-size: 9px;
  color: #94A3B8;
  font-weight: 600;
  white-space: nowrap;
}
"""

sleek_cua_html = """
    <!-- Resizing Grip for CUA Panel -->
    <div class="ailab-grip-v ailab-grip-cua" id="ailabCuaGrip" title="Resize CUA Browser Panel"></div>

    <!-- Panel 3: Sleek Autonomous Browser Agent (CUA) Studio -->
    <aside class="ailab-cua-panel active" id="ailabCuaPanel">
      <!-- Browser Window Header Chrome (macOS Dots & Title) -->
      <div class="ailab-cua-chrome-header">
        <div class="ailab-window-dots">
          <span class="dot red" onclick="ailabToggleCuaPanel(false)" title="Close CUA Viewport"></span>
          <span class="dot yellow" onclick="ailabToggleCuaPanel()" title="Minimize"></span>
          <span class="dot green" onclick="ailabToggleCuaFullscreen()" title="Fullscreen"></span>
        </div>
        <div class="ailab-cua-chrome-title">
          <span>🖥️ Autonomous Browser (CUA)</span>
          <span class="ailab-badge-cua">Claude / Browser-Use MCP</span>
        </div>
        <div class="ailab-cua-chrome-right">
          <div class="ailab-cua-live-pill">
            <span class="ailab-live-pulse-dot"></span>
            <span>LIVE SCREEN SHARE</span>
          </div>
          <button class="ailab-iconbtn" onclick="ailabCuaSnapshot()" title="Capture Frame">📸</button>
          <button class="ailab-iconbtn" onclick="ailabToggleCuaFullscreen()" title="Fullscreen">⛶</button>
          <button class="ailab-iconbtn" onclick="ailabToggleCuaPanel(false)" title="Close">✕</button>
        </div>
      </div>

      <!-- Modern Browser Omnibox Bar -->
      <div class="ailab-cua-omnibox-bar">
        <div class="ailab-cua-nav-btns">
          <button class="ailab-nav-btn" onclick="ailabCuaBack()" title="Back">◀</button>
          <button class="ailab-nav-btn" onclick="ailabCuaForward()" title="Forward">▶</button>
          <button class="ailab-nav-btn" onclick="ailabCuaReload()" title="Reload">🔄</button>
        </div>
        <div class="ailab-cua-url-input-wrap">
          <span class="ailab-ssl-lock">🔒</span>
          <input type="text" class="ailab-cua-url-input" id="ailabCuaUrlInput" value="https://en.wikipedia.org" placeholder="Enter URL or search term..." onkeydown="if(event.key==='Enter')ailabCuaGoUrl()">
          <button class="ailab-cua-go-btn" onclick="ailabCuaGoUrl()">Go</button>
        </div>
        <button class="ailab-cua-chip" onclick="ailabCuaNavigate('https://en.wikipedia.org')">Wikipedia</button>
        <button class="ailab-cua-chip" onclick="ailabCuaNavigate('https://google.com')">Google</button>
        <button class="ailab-cua-chip" onclick="ailabCuaNavigate('https://news.ycombinator.com')">HN</button>
        <button class="ailab-cua-chip" onclick="ailabCuaNavigate('https://github.com/trending')">GitHub</button>
      </div>

      <!-- Full Height Live Screen Share Viewport Stage -->
      <div class="ailab-cua-viewport-container" id="ailabCuaViewportContainer">
        <iframe class="ailab-cua-iframe" id="ailabCuaIframe" src="https://en.wikipedia.org" sandbox="allow-same-origin allow-scripts allow-forms"></iframe>
        <img class="ailab-cua-screenshot-frame" id="ailabCuaScreenshotFrame" alt="Playwright Frame" style="display:none;">

        <!-- Visual Agent Laser Cursor -->
        <div class="ailab-cua-cursor" id="ailabCuaCursor">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="#EF4444" stroke="#FFFFFF" stroke-width="1.5">
            <path d="M3 3l7 18 3-7 7-3L3 3z"/>
          </svg>
          <span class="ailab-cua-cursor-label" id="ailabCuaCursorLabel">Agent CUA</span>
        </div>

        <!-- Click Ripple Layer -->
        <div class="ailab-cua-click-ripple" id="ailabCuaClickRipple"></div>

        <!-- Set-of-Marks Bounding Boxes Overlay -->
        <div class="ailab-cua-som-overlay" id="ailabCuaSomOverlay"></div>

        <!-- Floating Action HUD -->
        <div class="ailab-cua-action-hud" id="ailabCuaActionHud">
          <span class="ailab-action-icon" id="ailabCuaActionIcon">⚡</span>
          <span class="ailab-action-desc" id="ailabCuaActionDesc">CUA Ready • Screen share active on local laptop</span>
        </div>
      </div>

      <!-- Sleek Floating Bottom Control Dock -->
      <div class="ailab-cua-bottom-dock">
        <div class="ailab-cua-task-row">
          <input type="text" class="ailab-cua-task-input" id="ailabCuaTaskInput" placeholder="Ask browser agent to search, click or scrape web..." onkeydown="if(event.key==='Enter')ailabCuaRunTask()">
          <button class="ailab-cua-exec-btn" onclick="ailabCuaRunTask()">
            <span>Execute</span>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
        <div class="ailab-cua-chips-row">
          <div class="ailab-cua-presets">
            <button class="ailab-cua-chip" onclick="ailabCuaPresetScenario('wiki')">🔍 Wiki AI</button>
            <button class="ailab-cua-chip" onclick="ailabCuaPresetScenario('hn')">📰 HackerNews</button>
            <button class="ailab-cua-chip" onclick="ailabCuaPresetScenario('github')">🐙 GitHub Trend</button>
            <button class="ailab-cua-chip" onclick="ailabCuaPresetScenario('som')">🎯 Set-of-Marks</button>
          </div>
          <div class="ailab-cua-telemetry-badge" id="ailabCuaTelemetryBadge">
            <span>🦆 DuckDB • 🏛️ BigQuery • 💻 Local Laptop (0 MB Render RAM)</span>
          </div>
        </div>
      </div>
    </aside>
"""

def apply_sleek_cua():
    path = "app/ui/global_ai_lab_view.py"
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Replace CUA CSS
    css_start = "/* =========================================================================\n   AUTONOMOUS BROWSER AGENT (CUA) / COMPUTER USE STUDIO STYLES"
    css_end = "/* ---------------- Model Catalog Discovery Modal ---------------- */"
    s_idx = code.find(css_start)
    e_idx = code.find(css_end, s_idx)
    if s_idx != -1 and e_idx != -1:
        code = code[:s_idx] + sleek_cua_css.strip() + "\n\n" + code[e_idx:]
        print("Replaced with sleek CUA CSS!")
    else:
        print("CSS markers not matched; s_idx:", s_idx, "e_idx:", e_idx)

    # 2. Replace CUA HTML
    html_start = "<!-- Resizing Grip for CUA Panel -->"
    html_end = "<!-- Model Catalog Search & Discovery Modal -->"
    hs_idx = code.find(html_start)
    he_idx = code.find(html_end, hs_idx)
    if hs_idx != -1 and he_idx != -1:
        code = code[:hs_idx] + sleek_cua_html.strip() + "\n  </div>\n</div>\n\n\n" + code[he_idx:]
        print("Replaced with sleek CUA HTML!")
    else:
        print("HTML markers not matched; hs_idx:", hs_idx, "he_idx:", he_idx)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Saved app/ui/global_ai_lab_view.py!")

if __name__ == "__main__":
    apply_sleek_cua()
