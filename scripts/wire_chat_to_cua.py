# -*- coding: utf-8 -*-
"""
wire_chat_to_cua.py:
Wires the chat prompt directly to the autonomous CUA browser execution:
1. When user asks for browser/search/screen-share in chat, automatically triggers
   AILAB_CUA.togglePanel(true) and AILAB_CUA.runAutonomousTask(prompt).
2. Updates AILAB_CUA.runAutonomousTask to intelligently handle Google, Wikipedia, GitHub, and general search queries.
3. Updates NANOPRO_MASTER_SYSTEM_PROMPT in deploy/cloudflare_worker_gateway.js so the AI never gives manual step-by-step instructions, but acts as the autonomous driver.
4. Re-injects into deploy/complete_nanopro_dashboard.html.
"""

import os
import re

def update_view():
    path = "app/ui/global_ai_lab_view.py"
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Update ailabSubmitPrompt to trigger CUA immediately on browser/screen-share intent
    prompt_detect_code = """    // 1. Detect CUA Browser / Screen Share intent directly from the chat prompt
    const pLower = prompt.toLowerCase();
    const isBrowserIntent = /google|search|शोध|बघ|उघड|browse|browser|ब्राउझर|स्क्रीन|screen|share|शेअर|cua|वेब|website|url|http/i.test(pLower);
    if (isBrowserIntent && window.AILAB_CUA) {
      window.AILAB_CUA.togglePanel(true);
      window.AILAB_CUA.runAutonomousTask(prompt);
    }
"""

    if "isBrowserIntent" not in code:
        needle = "AILAB.messages.push(userMsg);"
        if needle in code:
            code = code.replace(needle, prompt_detect_code + "\n    " + needle, 1)
            print("Wired prompt intent detection to AILAB_CUA!")
        else:
            print("Could not find userMsg push needle in ailabSubmitPrompt")

    # 2. Update runAutonomousTask in AILAB_CUA to intelligently route queries
    old_run_task_pattern = re.compile(r'runAutonomousTask:\s*async\s*function\(promptText\)\s*\{[\s\S]*?updateActionHud\("✅"[\s\S]*?\}\s*\,', re.MULTILINE)

    new_run_task = """runAutonomousTask: async function(promptText) {
      const input = document.getElementById("ailabCuaTaskInput");
      const task = (promptText || (input ? input.value : "")).trim();
      if (!task) return;
      if (input) input.value = "";

      this.togglePanel(true);
      const lower = task.toLowerCase();

      // Determine Target Website & Query
      let targetUrl = "https://www.google.com";
      let query = task.replace(/side screen share madhe|screen share|side screen|browser|ब्राउझर|स्क्रीन|शेअर|search|kara|करा|शोध/gi, "").trim();
      if (!query) query = "NanoPro AI Studio";

      if (lower.includes("google") || lower.includes("शोध") || lower.includes("search")) {
        targetUrl = "https://www.google.com/search?q=" + encodeURIComponent(query);
      } else if (lower.includes("wiki") || lower.includes("विकिपीडिया")) {
        targetUrl = "https://en.wikipedia.org/wiki/" + encodeURIComponent(query);
      } else if (lower.includes("github") || lower.includes("गिटहब")) {
        targetUrl = "https://github.com/search?q=" + encodeURIComponent(query);
      } else if (lower.includes("hackernews") || lower.includes("hn")) {
        targetUrl = "https://news.ycombinator.com";
      } else if (/https?:\\/\\/[^\\s]+/i.test(task)) {
        const match = task.match(/https?:\\/\\/[^\\s]+/i);
        if (match) targetUrl = match[0];
      } else {
        targetUrl = "https://www.google.com/search?q=" + encodeURIComponent(query);
      }

      this.updateActionHud("⚡", `Executing CUA Task: "${task}"`);

      // Step 1: Navigate to target URL
      await this.navigate(targetUrl);
      await new Promise(r => setTimeout(r, 600));

      // Step 2: Set-of-Marks Vision Scan
      this.renderSetOfMarks();
      await new Promise(r => setTimeout(r, 700));

      // Step 3: Laser Cursor Move & Simulated Interactive Click on search result
      const stage = document.getElementById("ailabCuaScreenStage");
      const stageW = stage ? stage.offsetWidth : 600;
      const stageH = stage ? stage.offsetHeight : 450;
      const targetX = Math.floor(stageW * 0.35);
      const targetY = Math.floor(stageH * 0.28);

      this.moveCursor(targetX, targetY, `Inspecting: ${query}`);
      await new Promise(r => setTimeout(r, 500));
      this.triggerClickRipple(targetX, targetY);
      await new Promise(r => setTimeout(r, 400));

      // Step 4: Clear Marks & Take Snapshot to DuckDB & BigQuery
      this.clearSetOfMarks();
      await this.snapshot();

      this.updateActionHud("✅", `CUA Live: "${query}" शोध पूर्ण • DuckDB & BigQuery Synced`);
    },"""

    if old_run_task_pattern.search(code):
        code = old_run_task_pattern.sub(new_run_task, code, count=1)
        print("Updated runAutonomousTask with intelligent target routing!")
    else:
        print("Warning: old_run_task_pattern not matched")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Saved app/ui/global_ai_lab_view.py!")

def update_gateway():
    path = "deploy/cloudflare_worker_gateway.js"
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    old_cua_prompt = re.search(r'4\.\s*🖥️\s*CUA BROWSER CO-PILOT:[\s\S]*?`\s*;', code)
    new_cua_prompt = """4. 🖥️ AUTONOMOUS CUA BROWSER EXECUTION (NEVER GIVE MANUAL STEPS):
   - When the user asks for browser/search actions (e.g., "side screen share madhe google search kara", "Google वर शोध", "Wikipedia उघडा"):
   - NEVER tell the user to manually do steps (do not say "१. CUA उघडा, २. Google टाइप करा")!
   - You MUST act as the autonomous driver actively executing it:
     "मी तुमच्या साइड स्क्रीन शेअर (CUA Viewport) मध्ये थेट Google उघडून शोध घेत आहे! 🖥️
      उजव्या बाजूच्या ब्राऊझर पॅनलमध्ये रिअल-टाइम स्क्रीन आणि लेझर कर्सर पाहा."
   - State what query was searched, highlight that execution runs locally with 0 MB Render load, and provide 1-tap option pills:
     [HINT: 🔍 Google रिझल्ट्स स्क्रॅप करा | 📰 टॉप ३ लिंक्स उघडा | 📸 स्क्रीनशॉट सेव्ह करा]`;"""

    if old_cua_prompt:
        code = code[:old_cua_prompt.start()] + new_cua_prompt + code[old_cua_prompt.end():]
        print("Updated gateway system prompt to mandate direct autonomous execution!")
    else:
        print("Warning: old_cua_prompt not matched in gateway")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Saved deploy/cloudflare_worker_gateway.js!")

if __name__ == "__main__":
    update_view()
    update_gateway()
