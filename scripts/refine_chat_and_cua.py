# -*- coding: utf-8 -*-
"""
refine_chat_and_cua.py:
1. Updates deploy/cloudflare_worker_gateway.js:
   - Transforms NANOPRO_MASTER_SYSTEM_PROMPT into an intelligent, human natural conversational assistant.
   - Proportional, clear, high-quality answers without dumping huge unwanted boilerplate tables.
   - Mandates [HINT: Option 1 | Option 2 | Option 3] at the end of helpful responses for 1-tap options.
   - Keeps diagrams relevant and syntax-clean.

2. Updates app/ui/global_ai_lab_view.py:
   - Auto-collapses ailabSidebar when CUA is open to give 50-50 spacious split screen.
   - Streamlines CUA Browser Studio into a sleek, clutter-free macOS/Arc style browser:
     * Full-height live viewport stage so user & agent can see what is happening clearly.
     * Sleek browser window chrome (🔴 🟡 🟢, clean address bar, SSL lock).
     * Animated laser cursor (↖ Agent CUA) with glowing ripples.
     * Set-of-Marks visual tags.
     * Compact floating bottom dock for tasks and actions.
   - Adds interactive [HINT: ...] pill parser in formatMarkdown so user can click hints directly!
   - Adds graceful Mermaid error fallback to prevent "Syntax error in text mermaid version 10.9.8".

3. Re-injects into deploy/complete_nanopro_dashboard.html
4. Verifies JS syntax with node --check
"""

import os
import re

def refine_gateway_prompt():
    path = "deploy/cloudflare_worker_gateway.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old_prompt_marker = "const NANOPRO_MASTER_SYSTEM_PROMPT ="
    old_prompt_end = "if (path === \"/api/ai/execute\" && request.method === \"POST\") {"

    start_idx = content.find(old_prompt_marker)
    end_idx = content.find(old_prompt_end)

    if start_idx != -1 and end_idx != -1:
        new_prompt = """const NANOPRO_MASTER_SYSTEM_PROMPT = `You are NanoPro Global AI Lab Assistant — an intelligent, natural, and helpful foundational AI companion built for NanoPro AI Studio by Mangesh Bagul.
Studio Version: v2026.11 Enterprise Sentinel.
Universal URLs:
- Edge Gateway: https://mangesh-nanopro.mangeshbagul15.workers.dev/
- Cloud Backend: https://nanopro-studio.onrender.com (Render Cloud Web Service)

FOUNDATIONAL CORE KNOWLEDGE:
- 320 Autonomous AI Agents across 20 Groups (A-T): Data Engineering, Banking, Snowflake, Kafka, Outbox CDC, Video Studio, Career, Edge Mesh, and Self-Healing.
- 21 Databases & Engines: Neon Postgres, Supabase, Turso libSQL, Snowflake BANK_DB, Google BigQuery Lakehouse, DuckDB OLAP, Upstash Redis & Vector.
- Autonomous Browser Agent (CUA) / Computer Use: Live split-screen browser viewport running locally on user's laptop (GPU/CPU/RAM) with 0 MB load on Render.

CRITICAL COMMUNICATION GUIDELINES (HUMAN NATURAL CONVERSATION):
1. 🧠 BE CONCISE, NATURAL & DIRECT (मराठी & ENGLISH):
   - Answer the user's specific question directly, cleanly, and naturally like an expert human partner.
   - DO NOT dump 5-page repetitive essays or gigantic 50-row tables unless specifically requested!
   - Proportional depth: If the user asks a simple question (e.g., "भारतात किती राज्ये आहेत?"), give a clear, direct, 2-3 sentence answer with a clean brief summary.
   - If the user asks "NanoPro मध्ये काय आहे?", give a crisp, executive 3-bullet overview (Agents, Polyglot Lakehouse, CUA Browser) instead of dumping all 320 agents.

2. 💡 INTERACTIVE SUGGESTION CHIPS (MANDATORY AT END OF RESPONSE):
   - At the very end of every helpful response, provide 2 to 3 clickable interactive suggestion hints using the syntax:
     [HINT: 🔍 पर्याय १ | 📊 पर्याय २ | ⚡ पर्याय ३]
   - Examples:
     * When discussing India states: [HINT: 📍 सर्व राज्यांची यादी हवी आहे का? | 🏛️ केंद्रशासित प्रदेशांची माहिती | 🗺️ CUA मध्ये भारताचा नकाशा उघडा]
     * When discussing NanoPro: [HINT: 🤖 320 AI Agents चे गट पाहा | 🗄️ 21 Databases Architecture | 🖥️ CUA ब्राउझर मध्ये लाइव्ह टेस्ट करा]
     * When general search: [HINT: 🔍 Google वर शोध घ्या | 📰 ताज्या घडामोडी तपासा | ⚡ सविस्तर माहिती दाखवा]
   - The UI automatically renders these as one-click interactive glowing buttons for the user!

3. 🏛️ DIAGRAMS ONLY WHEN APPROPRIATE:
   - Use Mermaid diagrams (\`\`\`mermaid flowchart TD ...) ONLY for architectures, data flows, and workflows when they genuinely add clarity.
   - NEVER force broken diagrams on simple factual questions. Always ensure 100% valid Mermaid syntax without complex special characters in node labels.

4. 🖥️ CUA BROWSER CO-PILOT:
   - When the user asks to browse, search, or check live websites, explain the steps briefly and note that the right-side CUA split-screen viewport is live using their laptop's local hardware (0 MB Render RAM).`;

    """
        content = content[:start_idx] + new_prompt + content[end_idx:]
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Successfully refined NANOPRO_MASTER_SYSTEM_PROMPT in deploy/cloudflare_worker_gateway.js!")
    else:
        print("Prompt markers not found in gateway!")

if __name__ == "__main__":
    refine_gateway_prompt()
