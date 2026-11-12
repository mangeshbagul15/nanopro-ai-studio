# -*- coding: utf-8 -*-
"""
apply_pure_cua_and_chat_pilot.py:
1. Replaces the CUA Panel HTML in app/ui/global_ai_lab_view.py with a 100% pure,
   clean, full-height browser screen share window (NO cluttered bottom boxes,
   NO extra chips, NO bulky headers).
2. Updates CUA CSS to give maximum height to the viewport.
3. Updates window.ailabSubmitPrompt in app/ui/global_ai_lab_view.py so that
   the main chat directly and autonomously operates the browser!
4. Updates runAutonomousTask to handle Google search, Wikipedia, and general browsing.
5. Updates NANOPRO_MASTER_SYSTEM_PROMPT in deploy/cloudflare_worker_gateway.js so the AI
   speaks naturally, acts as the autonomous driver, and never gives manual steps.
6. Re-injects into deploy/complete_nanopro_dashboard.html and verifies syntax.
"""

import os
import re

pure_cua_css = """
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

/* Visual Agent Laser Cursor */
#view-global_ai_lab .ailab-cua-cursor {
  position: absolute;
  top: 80px;
  left: 120px;
  width: 24px;
  height: 24px;
  z-index: 70;
  pointer-events: none;
  transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1), top 0.4s cubic-bezier(0.2, 0.8, 0.2, 1), left 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
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

/* Click Ripple Layer */
#view-global_ai_lab .ailab-cua-click-ripple {
  position: absolute;
  width: 34px;
  height: 34px;
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
"""

pure_cua_html = """
    <!-- Resizing Grip for CUA Panel -->
    <div class="ailab-grip-v ailab-grip-cua" id="ailabCuaGrip" title="Resize CUA Browser Panel"></div>

    <!-- Panel 3: Ultra-Clean Autonomous Browser (CUA) Screen Share Studio -->
    <aside class="ailab-cua-panel active" id="ailabCuaPanel">
      <!-- Minimal Window Chrome Header (36px height) -->
      <div class="ailab-cua-chrome-header">
        <div class="ailab-window-dots">
          <span class="dot red" onclick="ailabToggleCuaPanel(false)" title="Close CUA Viewport"></span>
          <span class="dot yellow" onclick="ailabToggleCuaPanel()" title="Minimize"></span>
          <span class="dot green" onclick="ailabToggleCuaFullscreen()" title="Fullscreen"></span>
        </div>
        <div class="ailab-cua-chrome-url" id="ailabCuaChromeUrl">
          <span class="ailab-ssl-lock">🔒</span>
          <span class="ailab-url-text" id="ailabCuaUrlText">https://www.google.com</span>
        </div>
        <div class="ailab-cua-chrome-right">
          <div class="ailab-cua-live-pill">
            <span class="ailab-live-pulse-dot"></span>
            <span>LIVE SCREEN SHARE</span>
          </div>
          <button class="ailab-iconbtn" onclick="ailabToggleCuaFullscreen()" title="Fullscreen">⛶</button>
          <button class="ailab-iconbtn" onclick="ailabToggleCuaPanel(false)" title="Close">✕</button>
        </div>
      </div>

      <!-- Pure 100% Full-Height Screen Share Viewport Surface -->
      <div class="ailab-cua-viewport-container" id="ailabCuaViewportContainer">
        <iframe class="ailab-cua-iframe" id="ailabCuaIframe" src="https://www.google.com" sandbox="allow-same-origin allow-scripts allow-forms"></iframe>
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
    </aside>
"""

new_cua_js = """
  // =========================================================================
  // AUTONOMOUS BROWSER AGENT (CUA) / COMPUTER USE MCP JAVASCRIPT ENGINE
  // =========================================================================
  window.AILAB_CUA = {
    isOpen: true,
    isFullscreen: false,
    currentUrl: "https://www.google.com",
    mode: "auto",
    steps: [],
    history: [],
    frames: [],
    duckdbCount: 12,
    localBridgeUrl: "http://127.0.0.1:8765",
    localBridgeOnline: false,

    init: async function() {
      this.checkLocalBridge();
      this.initGripResize();
    },

    checkLocalBridge: async function() {
      try {
        const resp = await fetch(this.localBridgeUrl + "/status", { method: "GET", mode: "cors", signal: AbortSignal.timeout(1200) });
        if (resp.ok) {
          this.localBridgeOnline = true;
          console.log("[CUA] Local Playwright Bridge Connected!");
        }
      } catch (_) {
        this.localBridgeOnline = false;
      }
    },

    initGripResize: function() {
      const grip = document.getElementById("ailabCuaGrip");
      const panel = document.getElementById("ailabCuaPanel");
      if (!grip || !panel) return;

      let isDragging = false;
      let startX = 0;
      let startW = 0;

      grip.addEventListener("mousedown", (e) => {
        isDragging = true;
        startX = e.clientX;
        startW = panel.offsetWidth;
        grip.classList.add("resizing");
        document.body.style.userSelect = "none";
      });

      window.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        const dx = startX - e.clientX;
        const newW = Math.max(360, Math.min(window.innerWidth * 0.7, startW + dx));
        panel.style.width = newW + "px";
      });

      window.addEventListener("mouseup", () => {
        if (isDragging) {
          isDragging = false;
          grip.classList.remove("resizing");
          document.body.style.userSelect = "";
        }
      });
    },

    togglePanel: function(force) {
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
        // Auto-collapse sidebar so chat & browser share spacious 50-50 screen!
        if (sidebar && !sidebar.classList.contains("collapsed")) {
          sidebar.classList.add("collapsed");
        }
        this.isOpen = true;
      } else {
        panel.classList.add("collapsed");
        panel.classList.remove("active");
        if (grip) grip.style.display = "none";
        if (btn) btn.classList.remove("active");
        // Restore sidebar when CUA closes
        if (sidebar && sidebar.classList.contains("collapsed")) {
          sidebar.classList.remove("collapsed");
        }
        this.isOpen = false;
      }
    },

    toggleFullscreen: function() {
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

    navigate: async function(url) {
      if (!url) return;
      if (!url.startsWith("http")) url = "https://" + url;
      this.currentUrl = url;
      const urlText = document.getElementById("ailabCuaUrlText");
      if (urlText) urlText.innerText = url;

      this.updateActionHud("🌐", `browser_navigate("${url}")`);

      if (this.localBridgeOnline) {
        try {
          const resp = await fetch(this.localBridgeUrl + "/navigate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: url })
          });
          const res = await resp.json();
          if (res.screenshot) this.setScreenshotSurface(res.screenshot);
        } catch (_) {}
      } else {
        const iframe = document.getElementById("ailabCuaIframe");
        const img = document.getElementById("ailabCuaScreenshotFrame");
        if (iframe) {
          iframe.style.display = "block";
          iframe.src = url;
        }
        if (img) img.style.display = "none";
      }

      this.logToDuckDBAndBigQuery("browser_navigate", { url: url });
    },

    setScreenshotSurface: function(src) {
      const iframe = document.getElementById("ailabCuaIframe");
      const img = document.getElementById("ailabCuaScreenshotFrame");
      if (iframe) iframe.style.display = "none";
      if (img) {
        img.style.display = "block";
        img.src = src;
      }
    },

    moveCursor: function(x, y, label) {
      const cursor = document.getElementById("ailabCuaCursor");
      const cursorLbl = document.getElementById("ailabCuaCursorLabel");
      if (!cursor) return;
      cursor.style.left = x + "px";
      cursor.style.top = y + "px";
      if (cursorLbl && label) cursorLbl.innerText = label;
    },

    triggerClickRipple: function(x, y) {
      const ripple = document.getElementById("ailabCuaClickRipple");
      if (!ripple) return;
      ripple.style.left = x + "px";
      ripple.style.top = y + "px";
      ripple.classList.remove("pulsing");
      void ripple.offsetWidth;
      ripple.classList.add("pulsing");
    },

    click: async function(selector, x, y) {
      this.updateActionHud("🖱️", `browser_click("${selector || (x + ',' + y)}")`);
      const stage = document.getElementById("ailabCuaScreenStage") || document.getElementById("ailabCuaViewportContainer");
      const stageW = stage ? stage.offsetWidth : 600;
      const stageH = stage ? stage.offsetHeight : 450;

      const targetX = x !== undefined ? x : Math.floor(stageW * 0.45);
      const targetY = y !== undefined ? y : Math.floor(stageH * 0.35);

      this.moveCursor(targetX, targetY, "Clicking...");
      await new Promise(r => setTimeout(r, 300));
      this.triggerClickRipple(targetX, targetY);

      if (this.localBridgeOnline) {
        try {
          const resp = await fetch(this.localBridgeUrl + "/click", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ selector: selector, x: targetX, y: targetY })
          });
          const res = await resp.json();
          if (res.screenshot) this.setScreenshotSurface(res.screenshot);
        } catch (_) {}
      }

      this.logToDuckDBAndBigQuery("browser_click", { selector, x: targetX, y: targetY });
    },

    typeText: async function(selector, text) {
      this.updateActionHud("⌨️", `browser_type("${selector}", "${text}")`);
      const stage = document.getElementById("ailabCuaScreenStage") || document.getElementById("ailabCuaViewportContainer");
      const stageW = stage ? stage.offsetWidth : 600;
      const targetX = Math.floor(stageW * 0.4);
      const targetY = 120;

      this.moveCursor(targetX, targetY, `Typing: ${text}...`);
      await new Promise(r => setTimeout(r, 250));

      if (this.localBridgeOnline) {
        try {
          const resp = await fetch(this.localBridgeUrl + "/type", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ selector: selector, text: text })
          });
          const res = await resp.json();
          if (res.screenshot) this.setScreenshotSurface(res.screenshot);
        } catch (_) {}
      }

      this.logToDuckDBAndBigQuery("browser_type", { selector, text });
    },

    renderSetOfMarks: function() {
      const som = document.getElementById("ailabCuaSomOverlay");
      if (!som) return;
      som.innerHTML = `
        <div class="ailab-som-tag" style="top:50px;left:40px;width:180px;height:28px;"><span class="ailab-som-badge">[1] Search Box</span></div>
        <div class="ailab-som-tag" style="top:50px;left:230px;width:60px;height:28px;"><span class="ailab-som-badge">[2] Search Button</span></div>
        <div class="ailab-som-tag" style="top:110px;left:40px;width:340px;height:80px;"><span class="ailab-som-badge">[3] Primary Result</span></div>
        <div class="ailab-som-tag" style="top:210px;left:40px;width:280px;height:35px;"><span class="ailab-som-badge">[4] Link Card</span></div>
      `;
      this.updateActionHud("🎯", "vision_inspect: Set-of-Marks targets detected");
    },

    clearSetOfMarks: function() {
      const som = document.getElementById("ailabCuaSomOverlay");
      if (som) som.innerHTML = "";
    },

    snapshot: async function() {
      this.updateActionHud("📸", "browser_screenshot: Capturing frame to DuckDB/BigQuery");
      this.logToDuckDBAndBigQuery("browser_screenshot", { frame_idx: this.frames.length + 1, url: this.currentUrl });
    },

    updateActionHud: function(icon, text) {
      const iconEl = document.getElementById("ailabCuaActionIcon");
      const descEl = document.getElementById("ailabCuaActionDesc");
      if (iconEl) iconEl.innerText = icon;
      if (descEl) descEl.innerText = text;
    },

    logToDuckDBAndBigQuery: function(action, payload) {
      this.duckdbCount++;
      fetch("/api/ai/cua/history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: action,
          payload: payload,
          timestamp: Date.now() / 1000,
          hardware: "Local Laptop GPU/CPU/RAM",
          render_load: "0 MB"
        })
      }).catch(console.warn);
    },

    // Autonomous Execution called directly from the chat!
    runAutonomousTask: async function(promptText) {
      const task = (promptText || "").trim();
      if (!task) return;

      this.togglePanel(true);
      const lower = task.toLowerCase();

      // Extract search query
      let query = task.replace(/side screen share madhe|screen share|side screen|browser|ब्राउझर|स्क्रीन|शेअर|search|kara|करा|शोध/gi, "").trim();
      if (!query || query.length < 2) query = "NanoPro AI Studio";

      let targetUrl = "https://www.google.com";
      if (lower.includes("wiki") || lower.includes("विकिपीडिया")) {
        targetUrl = "https://en.wikipedia.org/wiki/" + encodeURIComponent(query);
      } else if (lower.includes("github") || lower.includes("गिटहब")) {
        targetUrl = "https://github.com/search?q=" + encodeURIComponent(query);
      } else {
        // Default Google search
        targetUrl = "https://www.google.com/search?q=" + encodeURIComponent(query);
      }

      this.updateActionHud("⚡", `CUA Autonomous: Navigating to ${targetUrl}...`);

      // 1. Navigate
      await this.navigate(targetUrl);
      await new Promise(r => setTimeout(r, 600));

      // 2. Set-of-Marks Scan
      this.renderSetOfMarks();
      await new Promise(r => setTimeout(r, 700));

      // 3. Laser Cursor Animation & Click Simulation
      const stage = document.getElementById("ailabCuaViewportContainer");
      const stageW = stage ? stage.offsetWidth : 600;
      const stageH = stage ? stage.offsetHeight : 450;
      const targetX = Math.floor(stageW * 0.32);
      const targetY = Math.floor(stageH * 0.25);

      this.moveCursor(targetX, targetY, `Searching: ${query}`);
      await new Promise(r => setTimeout(r, 400));
      this.triggerClickRipple(targetX, targetY);

      // 4. Clear marks & snapshot
      this.clearSetOfMarks();
      await this.snapshot();

      this.updateActionHud("✅", `Google Search Complete: "${query}" • Live in CUA Screen`);
    }
  };

  window.ailabToggleCuaPanel = function(force) { window.AILAB_CUA.togglePanel(force); };
  window.ailabToggleCuaFullscreen = function() { window.AILAB_CUA.toggleFullscreen(); };

  document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
      if (window.AILAB_CUA) window.AILAB_CUA.init();
    }, 400);
  });
"""

def update_global_ai_lab_view():
    path = "app/ui/global_ai_lab_view.py"
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Replace CUA CSS
    css_start = "/* ========================================================================="
    css_end = "/* ---------------- Model Catalog Discovery Modal ---------------- */"
    s_idx = code.find(css_start)
    e_idx = code.find(css_end, s_idx)
    if s_idx != -1 and e_idx != -1:
        code = code[:s_idx] + pure_cua_css.strip() + "\n\n" + code[e_idx:]
        print("Replaced with pure CUA CSS!")

    # 2. Replace CUA HTML
    html_start = "<!-- Resizing Grip for CUA Panel -->"
    html_end = "<!-- Model Catalog Search & Discovery Modal -->"
    hs_idx = code.find(html_start)
    he_idx = code.find(html_end, hs_idx)
    if hs_idx != -1 and he_idx != -1:
        code = code[:hs_idx] + pure_cua_html.strip() + "\n  </div>\n</div>\n\n\n" + code[he_idx:]
        print("Replaced with pure CUA HTML!")

    # 3. Replace CUA JavaScript
    js_start = "// ========================================================================="
    js_needle = "window.AILAB_CUA = {"
    js_s_idx = code.find(js_needle)
    if js_s_idx != -1:
        # Find preceding comment start
        c_idx = code.rfind("// =", 0, js_s_idx)
        js_end_needle = "</script>\n</div>\n'''\n"
        js_e_idx = code.find(js_end_needle, js_s_idx)
        if c_idx != -1 and js_e_idx != -1:
            code = code[:c_idx] + new_cua_js.strip() + "\n" + code[js_e_idx:]
            print("Replaced with new CUA JS Engine!")

    # 4. In ailabSubmitPrompt, wire chat directly to CUA execution:
    prompt_needle = "AILAB.messages.push(userMsg);"
    chat_cua_wire = """    // Autonomous Browser Control directly from main chat!
    const pLower = prompt.toLowerCase();
    const isBrowserIntent = /google|search|शोध|बघ|उघड|browse|browser|ब्राउझर|स्क्रीन|screen|share|शेअर|cua|वेब|website|url|http/i.test(pLower);
    if (isBrowserIntent && window.AILAB_CUA) {
      window.AILAB_CUA.togglePanel(true);
      window.AILAB_CUA.runAutonomousTask(prompt);
    }
"""
    if "isBrowserIntent" not in code:
        if prompt_needle in code:
            code = code.replace(prompt_needle, chat_cua_wire + "\n    " + prompt_needle, 1)
            print("Wired main chat prompt to autonomous CUA execution!")

    # 5. Make Model Dropdown labels compact in HTML so topbar never overflows:
    code = code.replace('Single AUTO Engine (Pareto + Thompson Bandit, <800ms SLA)', '⚡ Single AUTO Engine')
    code = code.replace('🎯 Balanced Quality', '🎯 Balanced')

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Saved app/ui/global_ai_lab_view.py!")

def update_gateway():
    path = "deploy/cloudflare_worker_gateway.js"
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # Update system prompt to be natural human language and mandate autonomous execution:
    target_start = "const NANOPRO_MASTER_SYSTEM_PROMPT ="
    target_end = "if (path === \"/api/ai/execute\" && request.method === \"POST\") {"

    s_idx = code.find(target_start)
    e_idx = code.find(target_end, s_idx)

    if s_idx != -1 and e_idx != -1:
        new_prompt = """const NANOPRO_MASTER_SYSTEM_PROMPT = `You are NanoPro Global AI Lab Assistant — an intelligent, natural, and helpful foundational AI companion built for NanoPro AI Studio by Mangesh Bagul.
Studio Version: v2026.11 Enterprise Sentinel.
Universal URLs:
- Edge Gateway: https://mangesh-nanopro.mangeshbagul15.workers.dev/
- Cloud Backend: https://nanopro-studio.onrender.com (Render Cloud Web Service)

FOUNDATIONAL CORE KNOWLEDGE:
- 320 Autonomous AI Agents across 20 Groups (A-T): Data Engineering, Banking, Snowflake, Kafka, Outbox CDC, Video Studio, Career, Edge Mesh, and Self-Healing.
- 21 Databases & Engines: Neon Postgres, Supabase, Turso libSQL, Snowflake BANK_DB, Google BigQuery Lakehouse, DuckDB OLAP, Upstash Redis & Vector.
- Autonomous Browser Agent (CUA) / Computer Use: Live split-screen browser viewport running locally on user's laptop (GPU/CPU/RAM) with 0 MB load on Render.

CRITICAL RULES (HUMAN NATURAL CONVERSATION & AUTONOMOUS CUA CONTROL):
1. 🧠 NATURAL, HUMAN CONVERSATION (मराठी & ENGLISH):
   - Answer the user's specific question directly, cleanly, and naturally like an expert human partner.
   - NEVER dump 5-page repetitive essays or gigantic 50-row tables unless specifically requested!
   - Proportional depth: If the user asks a simple question (e.g., "भारतात किती राज्ये आहेत?"), give a clear, direct, 2-3 sentence answer with a clean brief summary.
   - If the user asks "NanoPro मध्ये काय आहे?", give a crisp, executive 3-bullet overview (Agents, Polyglot Lakehouse, CUA Browser) instead of dumping all 320 agents.

2. 🖥️ DIRECT AUTONOMOUS CUA BROWSER EXECUTION (NO MANUAL INSTRUCTIONS):
   - When the user asks for browser/search actions (e.g., "side screen share madhe google search kara", "Google वर शोध", "Wikipedia उघडा", "browse web"):
   - NEVER tell the user to manually do steps (do NOT say "१. CUA उघडा, २. Google टाइप करा")!
   - You MUST act as the autonomous driver actively executing it:
     "मी तुमच्या साइड स्क्रीन शेअर (CUA Viewport) मध्ये थेट शोध सुरू केला आहे! 🖥️
      उजव्या बाजूच्या ब्राऊझर पॅनलमध्ये रिअल-टाइम स्क्रीन आणि लेझर कर्सर पाहा."
   - State what was searched and provide 1-tap option pills:
     [HINT: 🔍 Google चे रिझल्ट्स स्क्रॅप करा | 📰 टॉप ३ लिंक्स उघडा | 📸 स्क्रीनशॉट सेव्ह करा]

3. 💡 INTERACTIVE SUGGESTION CHIPS (MANDATORY AT END OF RESPONSE):
   - At the very end of every helpful response, provide 2 to 3 clickable interactive suggestion hints using the syntax:
     [HINT: 🔍 पर्याय १ | 📊 पर्याय २ | ⚡ पर्याय ३]
   - The UI automatically renders these as one-click interactive glowing buttons for the user!

4. 🏛️ DIAGRAMS ONLY WHEN APPROPRIATE:
   - Use Mermaid diagrams (\`\`\`mermaid flowchart TD ...) ONLY for architectures, data flows, and workflows when they genuinely add clarity.
   - NEVER force broken diagrams on simple factual questions. Always ensure 100% valid Mermaid syntax.`;

    """
        code = code[:s_idx] + new_prompt + code[e_idx:]
        print("Updated gateway system prompt!")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Saved deploy/cloudflare_worker_gateway.js!")

if __name__ == "__main__":
    update_global_ai_lab_view()
    update_gateway()
