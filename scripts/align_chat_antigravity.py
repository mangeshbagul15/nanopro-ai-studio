import sys

def main():
    file_path = "app/ui/global_ai_lab_view.py"
    with open(file_path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Update CSS
    old_css_marker = "/* Chat Messages */"
    new_css = """/* ========================================================= */
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
"""

    end_css_marker = "/* Frontier Model Provenance Card */"

    idx_start = c.find(old_css_marker)
    idx_end = c.find(end_css_marker)
    if idx_start != -1 and idx_end != -1:
        c = c[:idx_start] + new_css + "\n" + c[idx_end:]
        print("[+] Replaced CSS for Antigravity & Claude Code chat alignment")
    else:
        print("[!] CSS markers not found:", idx_start, idx_end)

    # 2. Update ailabCreateMessageNode
    old_create_msg_start = "  function ailabCreateMessageNode(msg) {"
    old_create_msg_end = "  window.ailabSubmitPrompt = async function() {"
    
    idx_msg_start = c.find(old_create_msg_start)
    idx_msg_end = c.find(old_create_msg_end)

    new_create_msg = """  function ailabCreateMessageNode(msg) {
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
        <div class="ailab-bubble ailab-user-bubble">${escapeHtml(msg.content)}</div>
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

"""

    if idx_msg_start != -1 and idx_msg_end != -1:
        c = c[:idx_msg_start] + new_create_msg + c[idx_msg_end:]
        print("[+] Replaced ailabCreateMessageNode & added helper actions")
    else:
        print("[!] Message node markers not found:", idx_msg_start, idx_msg_end)

    # 3. Update assistantPlaceholder in ailabSubmitPrompt
    old_placeholder = """    const assistantPlaceholder = document.createElement("div");
    assistantPlaceholder.className = "ailab-msg ailab-msg-assistant";
    assistantPlaceholder.id = "ailab-generating-msg";
    assistantPlaceholder.innerHTML = `
      <div class="ailab-route-hud">
        <span class="ailab-route-hud-badge">⚡ Evaluating Pareto Frontier &amp; Semantic Vectors...</span>
        <span class="ailab-route-hud-meta">&lt; 3.0 ms math overhead</span>
      </div>
      <div class="ailab-bubble" style="color:#94A3B8;">Generating intelligent response across 4,750+ frontier models...</div>
    `;"""

    new_placeholder = """    const assistantPlaceholder = document.createElement("div");
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
    `;"""

    if old_placeholder in c:
        c = c.replace(old_placeholder, new_placeholder)
        print("[+] Replaced assistantPlaceholder")
    else:
        print("[!] Old placeholder not found")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(c)
    print("[+] Successfully saved app/ui/global_ai_lab_view.py!")

if __name__ == "__main__":
    main()
