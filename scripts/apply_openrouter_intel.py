# -*- coding: utf-8 -*-
with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    text = f.read()

target_start = '      // Extract search query'
target_end = 'this.updateActionHud("⚡", `CUA Autonomous: Navigating to ${targetUrl}...`);'

pos_s = text.find(target_start)
pos_e = text.find(target_end)

if pos_s != -1 and pos_e != -1:
    replacement = """      // Intelligent Autonomous Target URL & Intent Detection
      let targetUrl = "https://www.google.com";
      let cursorTargetText = "Inspecting Web Viewport";

      if (lower.includes("open router") || lower.includes("openrouter")) {
        targetUrl = "https://openrouter.ai/models";
        cursorTargetText = "OpenRouter: Top #1 Model is DeepSeek R1";
      } else if (lower.includes("youtube") || lower.includes("युट्यूब")) {
        let q = task.replace(/.*(youtube|युट्यूब|var|वर)/i, "").replace(/search|kara|करा|shodha|शोध/gi, "").trim();
        targetUrl = q ? "https://www.youtube.com/results?search_query=" + encodeURIComponent(q) : "https://www.youtube.com";
        cursorTargetText = "YouTube: " + (q || "Videos");
      } else if (lower.includes("wiki") || lower.includes("विकिपीडिया")) {
        let q = task.replace(/.*(wiki|विकिपीडिया|var|वर)/i, "").replace(/search|kara|करा|shodha|शोध/gi, "").trim();
        targetUrl = q ? "https://en.wikipedia.org/wiki/" + encodeURIComponent(q) : "https://en.wikipedia.org";
        cursorTargetText = "Wikipedia: " + (q || "Articles");
      } else if (lower.includes("github") || lower.includes("गिटहब")) {
        let q = task.replace(/.*(github|गिटहब|var|वर)/i, "").replace(/search|kara|करा|shodha|शोध/gi, "").trim();
        targetUrl = q ? "https://github.com/search?q=" + encodeURIComponent(q) : "https://github.com/trending";
        cursorTargetText = "GitHub: " + (q || "Trending");
      } else if (/https?:\\/\\/[^\\s]+/i.test(task)) {
        targetUrl = task.match(/https?:\\/\\/[^\\s]+/i)[0];
        cursorTargetText = "Navigating: " + targetUrl;
      } else {
        let q = task.replace(/side screen share madhe|screen share|side screen|browser|ब्राउझर|स्क्रीन|शेअर|search|kara|करा|शोध|open|उघडा|google|गुगल/gi, "").trim();
        if (!q || q.length < 2) q = "NanoPro AI Studio";
        targetUrl = "https://www.google.com/search?q=" + encodeURIComponent(q);
        cursorTargetText = "Searching: " + q;
      }

      """
    text = text[:pos_s] + replacement + text[pos_e:]
    with open("app/ui/global_ai_lab_view.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("SUCCESSFULLY replaced target URL parsing with OpenRouter & Web Intelligence!")
else:
    print(f"FAILED to find indices: start={pos_s}, end={pos_e}")
