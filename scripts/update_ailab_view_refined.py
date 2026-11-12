# -*- coding: utf-8 -*-
"""
update_ailab_view_refined.py:
Applies clean UI, interactive hint pills, Mermaid error handling,
auto-collapsing sidebar, and sleek CUA browser window to app/ui/global_ai_lab_view.py.
"""

import os
import re

def update_view():
    path = "app/ui/global_ai_lab_view.py"
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Update formatMarkdown to parse [HINT: ... | ...] pills
    hint_parser = """    // 11. Parse Interactive Suggestion Chips / Hints: [HINT: Option 1 | Option 2 | Option 3]
    html = html.replace(/\\[HINT:\\s*([^\\]]+)\\]/gi, (match, hintStr) => {
      const options = hintStr.split('|').map(o => o.trim()).filter(Boolean);
      let chipsHtml = '<div class="ailab-hint-group"><span class="ailab-hint-lbl">💡 सुचवलेले पर्याय (1-Tap Suggestions):</span><div class="ailab-hint-chips">';
      options.forEach(opt => {
        const safeText = encodeURIComponent(opt);
        chipsHtml += `<button type="button" class="ailab-hint-chip" onclick="ailabSendHint(decodeURIComponent('${safeText}'))"><span>${opt}</span></button>`;
      });
      chipsHtml += '</div></div>';
      return chipsHtml;
    });
"""
    if "ailab-hint-group" not in code:
        # Insert before `return html;` in formatMarkdown
        needle = "return html;\n  }\n\n  function ailabRenderMermaidBlocks()"
        if needle in code:
            code = code.replace(needle, hint_parser + "\n    " + needle)
            print("Inserted hint pill parser into formatMarkdown!")
        else:
            print("Could not find formatMarkdown return needle")

    # 2. Update ailabRenderMermaidBlocks for graceful error handling
    old_mermaid_func = """  function ailabRenderMermaidBlocks() {
    try {
      if (window.mermaid) {
        window.mermaid.run({ querySelector: '.ailab-mermaid-container pre.mermaid' });
      } else {
        ailabEnsureMermaid();
      }
    } catch (_) {}
  }"""

    new_mermaid_func = """  function ailabRenderMermaidBlocks() {
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
  }"""

    if old_mermaid_func in code:
        code = code.replace(old_mermaid_func, new_mermaid_func)
        print("Updated ailabRenderMermaidBlocks with graceful fallback!")

    # 3. Add window.ailabSendHint function
    hint_func = """
  // Interactive Suggestion Hint Dispatcher
  window.ailabSendHint = function(hintText) {
    if (!hintText) return;
    const lower = hintText.toLowerCase();
    if (lower.includes("cua") || lower.includes("ब्राउझर") || lower.includes("browser") || lower.includes("search") || lower.includes("शोध")) {
      if (window.AILAB_CUA) {
        window.AILAB_CUA.togglePanel(true);
        window.AILAB_CUA.runAutonomousTask(hintText);
      }
    }
    const input = document.getElementById("ailabPromptInput");
    if (input) {
      input.value = hintText;
      if (window.ailabSubmitPrompt) window.ailabSubmitPrompt();
    }
  };
"""
    if "window.ailabSendHint =" not in code:
        insert_marker = "window.ailabChangeModel = function(modelKey) {"
        if insert_marker in code:
            code = code.replace(insert_marker, hint_func + "\n  " + insert_marker)
            print("Inserted window.ailabSendHint function!")

    # 4. Add Hint Chip CSS styles
    hint_css = """
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
"""
    if "#view-global_ai_lab .ailab-hint-group" not in code:
        css_anchor = "/* ---------------- Bottom Input Cockpit ---------------- */"
        if css_anchor in code:
            code = code.replace(css_anchor, hint_css + "\n" + css_anchor)
            print("Inserted Hint Chip CSS styles!")

    # 5. Update CUA togglePanel in JavaScript to auto-collapse sidebar
    old_toggle_panel = """    togglePanel: function(force) {
      const panel = document.getElementById("ailabCuaPanel");
      const grip = document.getElementById("ailabCuaGrip");
      const btn = document.getElementById("ailabCuaToggleBtn");
      if (!panel) return;

      const shouldOpen = force !== undefined ? force : panel.classList.contains("collapsed");
      if (shouldOpen) {
        panel.classList.remove("collapsed");
        panel.classList.add("active");
        if (grip) grip.style.display = "";
        if (btn) btn.classList.add("active");
        this.isOpen = true;
      } else {
        panel.classList.add("collapsed");
        panel.classList.remove("active");
        if (grip) grip.style.display = "none";
        if (btn) btn.classList.remove("active");
        this.isOpen = false;
      }
    },"""

    new_toggle_panel = """    togglePanel: function(force) {
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
        // Auto-collapse sidebar when CUA opens so chat & browser get full 50-50 split screen!
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
    },"""

    if old_toggle_panel in code:
        code = code.replace(old_toggle_panel, new_toggle_panel)
        print("Updated togglePanel to auto-collapse sidebar for spacious split screen!")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Saved app/ui/global_ai_lab_view.py!")

if __name__ == "__main__":
    update_view()
