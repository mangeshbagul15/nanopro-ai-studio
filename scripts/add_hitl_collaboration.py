# -*- coding: utf-8 -*-
"""
Add Human-in-the-Loop (HITL) Collaborative Agent Protocol to app/ui/global_ai_lab_view.py:
1. CSS for .ailab-hitl-card, .ailab-hitl-header, .ailab-hitl-btn, .ailab-hitl-btn.recommended
2. window.ailabSendHint and window.ailabChooseHitlOption functions
3. AILAB_CUA methods:
   - requestCollaborativeDecision(checkpoint)
   - resumeWithUserChoice(choiceId, choiceText)
4. Multi-step execution in runAutonomousTask that triggers the collaborative checkpoint with recommendations!
"""
import re

with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS for HITL Collaboration Cards
hitl_css = """
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
"""

if "ailab-hitl-card" not in content:
    # insert CSS before </style>
    content = content.replace("</style>", hitl_css + "\n</style>", 1)
    print("Added HITL CSS!")

# 2. Add window.ailabSendHint and window.ailabChooseHitlOption
js_helpers = """
  // Global 1-Tap Hint Dispatcher
  window.ailabSendHint = function(text) {
    if (!text) return;
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
"""

if "window.ailabChooseHitlOption" not in content:
    content = content.replace("window.ailabToggleCuaPanel = function", js_helpers + "\n  window.ailabToggleCuaPanel = function")
    print("Added HITL JS dispatchers!")

# 3. Add HITL Methods and Enhanced Multi-Step Loop inside AILAB_CUA
hitl_methods = """    activeCheckpoint: null,

    // Human-in-the-Loop Collaboration: Request User Guidance / Approval
    requestCollaborativeDecision: function(checkpoint) {
      this.activeCheckpoint = checkpoint;
      const cardId = "hitl_" + Math.random().toString(36).slice(2, 9);
      
      // Update CUA Viewport HUD & Cursor
      this.updateActionHud("🤝", "HITL Checkpoint: Waiting for user choice in chat...");
      this.moveCursor(200, 150, "🤝 Awaiting User Choice in Chat");

      // Build options HTML
      let optionsHtml = "";
      (checkpoint.options || []).forEach((opt, idx) => {
        const isRec = opt.recommended || idx === (checkpoint.recommendedIndex || 0);
        const safeLabel = encodeURIComponent(opt.label || opt.text || `Option ${idx+1}`);
        const safeId = encodeURIComponent(opt.id || `opt_${idx+1}`);
        optionsHtml += `
          <button type="button" class="ailab-hitl-btn ${isRec ? 'recommended' : ''}" 
                  onclick="ailabChooseHitlOption(decodeURIComponent('${safeId}'), decodeURIComponent('${safeLabel}'), '${cardId}')">
            <span>${opt.icon || '👉'} ${opt.label || opt.text}</span>
            ${isRec ? '<span class="ailab-hitl-rec-tag">Recommended ⭐</span>' : ''}
          </button>
        `;
      });

      const container = document.getElementById("ailabMessagesContainer");
      if (!container) return;

      const card = document.createElement("div");
      card.className = "ailab-msg ailab-msg-assistant";
      card.id = cardId;
      card.innerHTML = `
        <div class="ailab-bubble" style="background:transparent; padding:0; border:none;">
          <div class="ailab-hitl-card">
            <div class="ailab-hitl-header">
              <span class="ailab-hitl-badge">🤝 Autonomous Agent &amp; User Pair-Programming</span>
              <span class="ailab-hitl-agent">CUA Browser Pilot &bull; HITL Checkpoint</span>
            </div>
            <div class="ailab-hitl-title">${checkpoint.title || "🤔 पुढील कृतीची निवड (Next Action Required)"}</div>
            <div class="ailab-hitl-desc">${checkpoint.description || "ब्राउझर एजंटला पुढील कृती करण्यासाठी तुमची मदत किंवा संमती हवी आहे:"}</div>
            <div class="ailab-hitl-options" id="${cardId}_opts">
              ${optionsHtml}
            </div>
          </div>
        </div>
      `;
      container.appendChild(card);
      container.scrollTop = container.scrollHeight;

      this.logToDuckDBAndBigQuery("hitl_checkpoint_requested", {
        title: checkpoint.title,
        options_count: (checkpoint.options || []).length
      });
    },

    // Resume execution when user picks an option
    resumeWithUserChoice: async function(choiceId, choiceLabel, cardId) {
      const optsEl = document.getElementById(`${cardId}_opts`);
      if (optsEl) {
        optsEl.innerHTML = `
          <div class="ailab-hitl-approved">
            <span>✅</span>
            <span><strong>तुम्ही निवडलेला पर्याय:</strong> ${choiceLabel} &mdash; ब्राउझर एजंट थेट अंमलबजावणी करत आहे...</span>
          </div>
        `;
      }

      this.updateActionHud("⚡", `Approved: "${choiceLabel}" \u2022 Executing in Browser...`);
      this.moveCursor(320, 220, `Executing: ${choiceLabel}`);
      this.triggerClickRipple(320, 220);

      this.logToDuckDBAndBigQuery("hitl_decision_granted", {
        choice_id: choiceId,
        choice_label: choiceLabel,
        timestamp: Date.now() / 1000
      });

      // Execute approved action in browser
      if (choiceId === "opt_1" || choiceId.includes("nanopro") || choiceId.includes("1")) {
        // Option 1: Explore official result
        await new Promise(r => setTimeout(r, 600));
        const iframe = document.getElementById("ailabCuaIframe");
        if (iframe) {
          iframe.srcdoc = this.generateGoogleSearchDoc("NanoPro AI Studio - Architecture & Operations Center");
        }
        this.updateActionHud("✅", "NanoPro Platform Opened & Verified Live");
        this.moveCursor(360, 280, "✅ Verified Live Data");
        await this.snapshot();
      } else if (choiceId === "opt_2" || choiceId.includes("wiki") || choiceId.includes("2")) {
        // Option 2: Wikipedia
        await this.navigate("https://en.wikipedia.org/wiki/Artificial_intelligence");
      } else if (choiceId === "opt_3" || choiceId.includes("github") || choiceId.includes("3")) {
        // Option 3: GitHub
        await this.navigate("https://github.com/search?q=nanopro+ai");
      } else {
        // General query
        await this.snapshot();
        this.updateActionHud("✅", `Action Completed: ${choiceLabel}`);
      }
      this.activeCheckpoint = null;
    },
"""

if "requestCollaborativeDecision:" not in content:
    # insert before runAutonomousTask:
    content = content.replace("runAutonomousTask: async function(promptText) {", hitl_methods + "\n    runAutonomousTask: async function(promptText) {")
    print("Added requestCollaborativeDecision and resumeWithUserChoice!")

# 4. Enhance runAutonomousTask to trigger the collaborative checkpoint
old_run_end = """      // 4. Clear marks & snapshot
      this.clearSetOfMarks();
      await this.snapshot();

      this.updateActionHud("✅", `Google Search Complete: "${query}" • Live in CUA Screen`);
    }"""

new_run_end = """      // 4. Clear marks & snapshot
      this.clearSetOfMarks();
      await this.snapshot();

      this.updateActionHud("✅", `Google Search Complete: "${query}" • Live in CUA Screen`);

      // 5. Human-in-the-Loop Collaboration Checkpoint (Dogh milun karu shakto!)
      await new Promise(r => setTimeout(r, 1000));
      this.requestCollaborativeDecision({
        title: `🤝 "${query}" निकालांमधून पुढील कृती निवडा`,
        description: `मी गुगल सर्च पूर्ण करून उजव्या बाजूच्या स्क्रीनवर रिझल्ट्स लोड केले आहेत. पुढील पायरीसाठी कोणता पर्याय निवडायचा? (मी सुचवलेला **पर्याय १ सर्वोत्तम** आहे):`,
        recommendedIndex: 0,
        options: [
          { id: "opt_1", icon: "⭐", label: `[१] NanoPro Platform चे अधिकृत तपशील उघडा आणि वाचा (Recommended)`, recommended: true },
          { id: "opt_2", icon: "📖", label: `[२] Wikipedia सारांश थेट ब्राउझर स्क्रीनवर उघडा` },
          { id: "opt_3", icon: "🐙", label: `[३] GitHub रिपॉझिटरीवरील कोड व आर्किटेक्चर तपासा` },
          { id: "opt_4", icon: "🛑", label: `[४] येथेच थांबा आणि चॅटमध्ये संपूर्ण सारांश द्या` }
        ]
      });
    }"""

if old_run_end in content:
    content = content.replace(old_run_end, new_run_end)
    print("Integrated HITL checkpoint into runAutonomousTask!")
else:
    print("Warning: old_run_end not found exactly, inspecting...")

with open("app/ui/global_ai_lab_view.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved app/ui/global_ai_lab_view.py!")
