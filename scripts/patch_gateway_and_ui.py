import os
import sys

os.chdir(r"C:\Users\mange\OneDrive\Documents\GitHub\nanopro-ai-studio")

# =========================================================================
# 1. Update deploy/cloudflare_worker_gateway.js
# =========================================================================
print("[*] Updating deploy/cloudflare_worker_gateway.js...")
with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    cw = f.read()

# 1.1 Update MULTI_PROVIDER_KEYS
target_keys = """      KRUTRIM: "JcMcoC72Osu3suH8oVvy-2An4","""
new_keys = """      KRUTRIM: "JcMcoC72Osu3suH8oVvy-2An4",
      DEFAPI: "dk-8ad11ada1f8d9ea75cc20cb1fc55cbed",
      JEV: "sk_jev-ai_TeTWU37d7VrPE3iepqXdFs4f42RRfeFI","""

if "DEFAPI:" not in cw:
    if target_keys in cw:
        cw = cw.replace(target_keys, new_keys, 1)
        print(" -> Added DEFAPI and JEV keys to MULTI_PROVIDER_KEYS")
    else:
        print(" [!] target_keys not found in cw")
else:
    print(" -> DEFAPI already in MULTI_PROVIDER_KEYS")

# 1.2 Update LAB_DIRECTORY
target_labs = """        "arcee": { lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain Specialized SLMs" }"""
new_labs = """        "arcee": { lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain Specialized SLMs" },
        "defapi": { lab: "Defapi Frontier Hub", country: "United States", flag: "🌐", tier: "Next-Gen Frontier Mesh" },
        "jev": { lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "System One Fast Reasoning" },
        "typesafe": { lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "System One Fast Reasoning" }"""

if '"defapi":' not in cw:
    if target_labs in cw:
        cw = cw.replace(target_labs, new_labs, 1)
        print(" -> Added Defapi and Jev to LAB_DIRECTORY")
    else:
        print(" [!] target_labs not found in cw")

# 1.3 Add callDefapi and callJevAI helper functions
target_helpers = """      async function callKrutrimAI(targetModel, timeoutMs = 7000) {"""
new_helpers = """      async function callDefapi(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^defapi\\//, "");
          const resp = await fetch("https://api.defapi.org/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.DEFAPI}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: cleanModel,
              messages: messages,
              temperature: 0.7,
              max_tokens: 2048
            }),
            signal: controller.signal
          });
          clearTimeout(tid);
          return resp;
        } catch (_) {
          clearTimeout(tid);
          return null;
        }
      }

      async function callJevAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^jev\\//, "").replace(/^typesafe\\//, "");
          const resp = await fetch("https://jevtypesafeai.com/api/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.JEV}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: cleanModel,
              messages: messages,
              temperature: 0.7,
              max_tokens: 2048
            }),
            signal: controller.signal
          });
          clearTimeout(tid);
          return resp;
        } catch (_) {
          clearTimeout(tid);
          return null;
        }
      }

      async function callKrutrimAI(targetModel, timeoutMs = 7000) {"""

if "callDefapi" not in cw:
    if target_helpers in cw:
        cw = cw.replace(target_helpers, new_helpers, 1)
        print(" -> Added callDefapi and callJevAI dispatch helpers")
    else:
        print(" [!] target_helpers not found in cw")

# 1.4 Add routing branches to /api/ai/execute
target_exec = """        } else if (model.startsWith("arcee/")) {"""
new_exec = """        } else if (model.startsWith("defapi/")) {
          activeProvider = "DEFAPI_FRONTIER_HUB";
          resp = await callDefapi(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^defapi\\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("jev/") || model.startsWith("typesafe/")) {
          activeProvider = "JEV_TYPESAFE_AI";
          resp = await callJevAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("deepseek/deepseek-r1", 8500);
          }
        } else if (model.startsWith("arcee/")) {"""

if 'activeProvider = "DEFAPI_FRONTIER_HUB";' not in cw:
    if target_exec in cw:
        cw = cw.replace(target_exec, new_exec, 1)
        print(" -> Added Defapi and Jev execution branches")
    else:
        print(" [!] target_exec not found in cw")

# 1.5 Add Defapi and Jev models to providerAddons
target_addons = """              // Arcee AI (Domain-Specialized SLMs)
              { id: "arcee/zai-org/glm-5.3-flash", name: "Arcee GLM 5.3 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain SLM", context: 32768, is_free: true },
              { id: "arcee/deepseek/deepseek-v4.1-flash", name: "Arcee DeepSeek V4.1 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain SLM", context: 65536, is_free: false },
              { id: "arcee/moonshotai/kimi-k3.1-pro", name: "Arcee Kimi K3.1 Pro", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Long Context SLM", context: 1048576, is_free: false }
            ];"""

new_addons = """              // Arcee AI (Domain-Specialized SLMs)
              { id: "arcee/zai-org/glm-5.3-flash", name: "Arcee GLM 5.3 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain SLM", context: 32768, is_free: true },
              { id: "arcee/deepseek/deepseek-v4.1-flash", name: "Arcee DeepSeek V4.1 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain SLM", context: 65536, is_free: false },
              { id: "arcee/moonshotai/kimi-k3.1-pro", name: "Arcee Kimi K3.1 Pro", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Long Context SLM", context: 1048576, is_free: false },
              // Defapi Multi-Model Frontier Hub (44 Models)
              { id: "defapi/alibaba/wan-2.7-image", name: "Defapi Wan 2.7 Image", lab: "Defapi Hub", country: "China", flag: "🇨🇳", tier: "Generative Image", context: 32768, is_free: false },
              { id: "defapi/anthropic/claude-fable-5", name: "Defapi Claude Fable 5", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Frontier Ultra", context: 500000, is_free: false },
              { id: "defapi/anthropic/claude-fable-5-2", name: "Defapi Claude Fable 5.2", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Frontier Ultra", context: 500000, is_free: false },
              { id: "defapi/anthropic/claude-opus-4.7", name: "Defapi Claude Opus 4.7", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Cognitive Logic", context: 200000, is_free: false },
              { id: "defapi/anthropic/claude-opus-4.8", name: "Defapi Claude Opus 4.8", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Cognitive Logic", context: 200000, is_free: false },
              { id: "defapi/anthropic/claude-opus-5", name: "Defapi Claude Opus 5", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Cognitive Logic", context: 200000, is_free: false },
              { id: "defapi/anthropic/claude-opus-5.5", name: "Defapi Claude Opus 5.5", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Cognitive Logic", context: 200000, is_free: false },
              { id: "defapi/bytedance/seedance-2.0", name: "Defapi Seedance 2.0", lab: "Defapi Hub", country: "China", flag: "🇨🇳", tier: "Motion & Video", context: 65536, is_free: false },
              { id: "defapi/cloudflare/clef", name: "Defapi Cloudflare Clef", lab: "Defapi Hub", country: "United States", flag: "☁️", tier: "Audio & Music", context: 32768, is_free: false },
              { id: "defapi/cloudflare/clef-flash", name: "Defapi Cloudflare Clef Flash", lab: "Defapi Hub", country: "United States", flag: "☁️", tier: "Fast Audio SLA", context: 32768, is_free: false },
              { id: "defapi/defapi/laya-0.3.20", name: "Defapi Laya 0.3.20", lab: "Defapi Hub", country: "Global", flag: "🌐", tier: "Autonomous Agent", context: 65536, is_free: false },
              { id: "defapi/google/gemini-3-flash", name: "Defapi Gemini 3 Flash", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Multimodal Flash", context: 1048576, is_free: false },
              { id: "defapi/google/gemini-3-pro", name: "Defapi Gemini 3 Pro", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Multimodal Pro", context: 2097152, is_free: false },
              { id: "defapi/google/gemini-3.1-pro-preview", name: "Defapi Gemini 3.1 Pro Preview", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Multimodal Pro Preview", context: 2097152, is_free: false },
              { id: "defapi/google/gemini-3.7-flash", name: "Defapi Gemini 3.7 Flash", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Ultra High Speed", context: 1048576, is_free: false },
              { id: "defapi/google/gemini-4-hydrogen", name: "Defapi Gemini 4 Hydrogen", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Next-Gen Omnimodal", context: 2097152, is_free: false },
              { id: "defapi/google/gemini-4-neon", name: "Defapi Gemini 4 Neon", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Next-Gen Omnimodal", context: 2097152, is_free: false },
              { id: "defapi/google/nano-banana", name: "Defapi Nano Banana", lab: "Defapi Hub", country: "United States", flag: "🍌", tier: "Ultra-Lightweight Edge", context: 32768, is_free: true },
              { id: "defapi/google/nano-banana-2", name: "Defapi Nano Banana 2", lab: "Defapi Hub", country: "United States", flag: "🍌", tier: "Ultra-Lightweight Edge", context: 65536, is_free: true },
              { id: "defapi/google/nano-banana-2-lite", name: "Defapi Nano Banana 2 Lite", lab: "Defapi Hub", country: "United States", flag: "🍌", tier: "Micro Inference SLA", context: 32768, is_free: true },
              { id: "defapi/google/nano-banana-pro", name: "Defapi Nano Banana Pro", lab: "Defapi Hub", country: "United States", flag: "🍌", tier: "Edge Pro Reasoning", context: 131072, is_free: true },
              { id: "defapi/google/veo3-fast", name: "Defapi Veo 3 Fast", lab: "Defapi Hub", country: "United States", flag: "🎬", tier: "Cinematic Video Fast", context: 65536, is_free: false },
              { id: "defapi/google/veo3-pro", name: "Defapi Veo 3 Pro", lab: "Defapi Hub", country: "United States", flag: "🎬", tier: "Cinematic Video Pro", context: 131072, is_free: false },
              { id: "defapi/google/veo3.1", name: "Defapi Veo 3.1", lab: "Defapi Hub", country: "United States", flag: "🎬", tier: "Cinematic Video 4K", context: 131072, is_free: false },
              { id: "defapi/google/veo3.1-components", name: "Defapi Veo 3.1 Components", lab: "Defapi Hub", country: "United States", flag: "🎬", tier: "VFX Pipeline Video", context: 65536, is_free: false },
              { id: "defapi/google/veo3.1-fast", name: "Defapi Veo 3.1 Fast", lab: "Defapi Hub", country: "United States", flag: "🎬", tier: "Cinematic Video Fast", context: 65536, is_free: false },
              { id: "defapi/midjourney/describe", name: "Defapi Midjourney Describe", lab: "Defapi Hub", country: "United States", flag: "🎨", tier: "Image Understanding", context: 32768, is_free: false },
              { id: "defapi/midjourney/edits", name: "Defapi Midjourney Edits", lab: "Defapi Hub", country: "United States", flag: "🎨", tier: "Image Inpainting", context: 32768, is_free: false },
              { id: "defapi/midjourney/imagine", name: "Defapi Midjourney Imagine", lab: "Defapi Hub", country: "United States", flag: "🎨", tier: "Generative Art", context: 32768, is_free: false },
              { id: "defapi/openai/gpt-5.2", name: "Defapi GPT-5.2", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Frontier Foundation", context: 524288, is_free: false },
              { id: "defapi/openai/gpt-5.4", name: "Defapi GPT-5.4", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Frontier Foundation", context: 1048576, is_free: false },
              { id: "defapi/openai/gpt-5.5", name: "Defapi GPT-5.5", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Frontier Reasoning", context: 1048576, is_free: false },
              { id: "defapi/openai/gpt-5.6-luna", name: "Defapi GPT-5.6 Luna", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Fast Production", context: 524288, is_free: false },
              { id: "defapi/openai/gpt-5.6-sol", name: "Defapi GPT-5.6 Sol", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Creative Synthesis", context: 524288, is_free: false },
              { id: "defapi/openai/gpt-5.6-terra", name: "Defapi GPT-5.6 Terra", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Deep Logic", context: 524288, is_free: false },
              { id: "defapi/openai/gpt-6-astra", name: "Defapi GPT-6 Astra", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Super-Frontier SOTA", context: 1048576, is_free: false },
              { id: "defapi/openai/gpt-6-luna", name: "Defapi GPT-6 Luna", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Super-Frontier Agile", context: 1048576, is_free: false },
              { id: "defapi/openai/gpt-6-sol", name: "Defapi GPT-6 Sol", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", tier: "Super-Frontier Deep", context: 1048576, is_free: false },
              { id: "defapi/openai/gpt-image-2", name: "Defapi GPT Image 2", lab: "Defapi Hub", country: "United States", flag: "🎨", tier: "Omnimodal Vision", context: 131072, is_free: false },
              { id: "defapi/openai/sora-2", name: "Defapi Sora 2", lab: "Defapi Hub", country: "United States", flag: "🎥", tier: "Neural Video Diffusion", context: 131072, is_free: false },
              { id: "defapi/openai/sora-2-pro", name: "Defapi Sora 2 Pro", lab: "Defapi Hub", country: "United States", flag: "🎥", tier: "High Fidelity Video", context: 131072, is_free: false },
              { id: "defapi/openai/sora-2-stable", name: "Defapi Sora 2 Stable", lab: "Defapi Hub", country: "United States", flag: "🎥", tier: "Coherent Physical Video", context: 131072, is_free: false },
              { id: "defapi/suno/chirp-crow", name: "Defapi Chirp Crow", lab: "Defapi Hub", country: "United States", flag: "🎵", tier: "Music Generation", context: 32768, is_free: false },
              { id: "defapi/suno/chirp-v3-5", name: "Defapi Chirp v3.5", lab: "Defapi Hub", country: "United States", flag: "🎵", tier: "Music Generation", context: 32768, is_free: false },
              { id: "defapi/suno/chirp-v4-5", name: "Defapi Chirp v4.5", lab: "Defapi Hub", country: "United States", flag: "🎵", tier: "Vocal Music Studio", context: 65536, is_free: false },
              { id: "defapi/typesafe/jev-1.13", name: "Defapi TypeSafe JEV 1.13", lab: "Defapi Hub", country: "United States", flag: "⚡", tier: "System One Decision", context: 65536, is_free: false },
              { id: "defapi/xai/grok-imagine-video", name: "Defapi Grok Imagine Video", lab: "Defapi Hub", country: "United States", flag: "🎥", tier: "Video Generation", context: 65536, is_free: false },
              // TypeSafe AI JEV Decision Mesh (10 Models)
              { id: "jev/jev-latest", name: "JEV Latest (Sub-50ms Calibrated Decision)", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "System One Fast", context: 131072, is_free: true },
              { id: "jev/jev-decision-fast", name: "JEV Decision Fast Engine", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "Ultra Low Latency <30ms", context: 65536, is_free: true },
              { id: "jev/jev-decision-deep", name: "JEV Decision Deep Logic", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "Calibrated Logic SOTA", context: 131072, is_free: false },
              { id: "jev/typesafe/jev-1.13", name: "TypeSafe JEV 1.13", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "Production Calibrated", context: 65536, is_free: false },
              { id: "jev/jev-1.14.0", name: "TypeSafe JEV 1.14.0", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "Frontier Calibrated", context: 131072, is_free: false },
              { id: "jev/jev-critic", name: "JEV Critic & Alignment", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "Adversarial Verifier", context: 65536, is_free: false },
              { id: "jev/jev-planner", name: "JEV Fast Path Planner", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "Monte Carlo Decision Tree", context: 65536, is_free: false },
              { id: "jev/jev-verifier", name: "JEV Verifier Engine", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "Deterministic Guard", context: 65536, is_free: true },
              { id: "jev/jev-verifier-pro", name: "JEV Verifier Pro", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "Formal Verification", context: 131072, is_free: false },
              { id: "jev/jev-quant", name: "JEV Quant Decision Core", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "High Frequency Math", context: 65536, is_free: false }
            ];"""

if "defapi/google/gemini-4-neon" not in cw:
    if target_addons in cw:
        cw = cw.replace(target_addons, new_addons, 1)
        print(" -> Added 44 Defapi + 10 Jev models to providerAddons")
    else:
        print(" [!] target_addons not found in cw")

# 1.6 Update model count strings
cw = cw.replace("4,750+ Unified Frontier Models active", "4,804+ Unified Frontier Models active")
cw = cw.replace("4,750+ models", "4,804+ models")
cw = cw.replace(
    "total_models: liveModels ? (liveModels.length + 1311 + 750 + 995 + 303 + 177 + 150 + 110 + 107 + 99 + 83 + 56 + 11 + 9 + 6 + 5) : 4750",
    "total_models: liveModels ? (liveModels.length + 1311 + 750 + 995 + 303 + 177 + 150 + 110 + 107 + 99 + 83 + 56 + 44 + 11 + 10 + 9 + 6 + 5) : 4804"
)

with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
    f.write(cw)
print(" -> deploy/cloudflare_worker_gateway.js updated successfully.")


# =========================================================================
# 2. Update app/ui/global_ai_lab_view.py
# =========================================================================
print("[*] Updating app/ui/global_ai_lab_view.py...")
with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    ui = f.read()

# 2.1 Replace text occurrences of 4,750
ui = ui.replace("4,750+ models</span>", "4,804+ models</span>")
ui = ui.replace('title="Browse model catalog (4,750+ models)"', 'title="Browse model catalog (4,804+ models)"')
ui = ui.replace("One workspace for 4,750+ frontier models", "One workspace for 4,804+ frontier models")
ui = ui.replace("4,750+ Unified Models across OpenRouter", "4,804+ Unified Models across Defapi, Jev AI, OpenRouter")
ui = ui.replace('placeholder="Search 4,750+ models by name', 'placeholder="Search 4,804+ models by name')
ui = ui.replace('All Mesh (4,750+)</button>', 'All Mesh (4,804+)</button>')
ui = ui.replace("4,750+ Frontier Models Mesh", "4,804+ Frontier Models Mesh")
ui = ui.replace('4,750+ <span style="font-size:11px;color:#C084FC;font-weight:600;">Models</span>', '4,804+ <span style="font-size:11px;color:#C084FC;font-weight:600;">Models</span>')
ui = ui.replace('badge.textContent = "4,750+ Models Unified Mesh";', 'badge.textContent = "4,804+ Models Unified Mesh";')
ui = ui.replace("across 4,750+ specialized models...", "across 4,804+ specialized models...")

# 2.2 Add Defapi & JEV filter pills to modal
target_pills = """      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Mesh (4,804+)</button>"""
new_pills = """      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Mesh (4,804+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('defapi', this)">🌐 Defapi Hub (44)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('jev', this)">⚡ TypeSafe JEV (10)</button>"""

if "ailabFilterModelCategory('defapi'" not in ui:
    ui = ui.replace(target_pills, new_pills, 1)
    print(" -> Added Defapi and JEV pills to model modal")

# 2.3 Add Defapi & JEV optgroups to ailabModelSelect dropdown
target_optgroup = """          <optgroup label="🇮🇳 Krutrim AI (Ola Sovereign Cloud · Qwen 3.6, GPT-OSS 120B, Gemma 4)">"""
new_optgroup = """          <optgroup label="🌐 Defapi Multi-Model Hub (44 Frontier Models · Gemini 4, GPT-6, Claude Fable)">
            <option value="defapi/google/gemini-4-neon">Defapi Gemini 4 Neon</option>
            <option value="defapi/google/gemini-4-hydrogen">Defapi Gemini 4 Hydrogen</option>
            <option value="defapi/google/gemini-3.7-flash">Defapi Gemini 3.7 Flash</option>
            <option value="defapi/anthropic/claude-fable-5-2">Defapi Claude Fable 5.2</option>
            <option value="defapi/anthropic/claude-opus-5.5">Defapi Claude Opus 5.5</option>
            <option value="defapi/openai/gpt-6-astra">Defapi GPT-6 Astra</option>
            <option value="defapi/openai/gpt-5.6-luna">Defapi GPT-5.6 Luna</option>
            <option value="defapi/openai/sora-2-pro">Defapi Sora 2 Pro</option>
          </optgroup>
          <optgroup label="⚡ TypeSafe AI JEV (System One Fast Reasoning & Decision Engine)">
            <option value="jev/jev-latest">JEV Latest (Sub-50ms Calibrated Decision)</option>
            <option value="jev/jev-decision-fast">JEV Decision Fast Engine</option>
            <option value="jev/jev-decision-deep">JEV Decision Deep Logic</option>
            <option value="jev/typesafe/jev-1.13">TypeSafe JEV 1.13</option>
            <option value="jev/jev-verifier-pro">JEV Verifier Pro</option>
          </optgroup>
          <optgroup label="🇮🇳 Krutrim AI (Ola Sovereign Cloud · Qwen 3.6, GPT-OSS 120B, Gemma 4)">"""

if "defapi/google/gemini-4-neon" not in ui:
    ui = ui.replace(target_optgroup, new_optgroup, 1)
    print(" -> Added Defapi and Jev static optgroups to ailabModelSelect")

# 2.4 Update DIRECTORY in ailabResolveModelProvenance
target_dir = """      "arcee": { lab_name: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain Specialized SLMs" }"""
new_dir = """      "arcee": { lab_name: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain Specialized SLMs" },
      "defapi": { lab_name: "Defapi Frontier Hub", country: "United States", flag: "🌐", tier: "Next-Gen Frontier Mesh" },
      "jev": { lab_name: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "System One Fast Reasoning" },
      "typesafe": { lab_name: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", tier: "System One Fast Reasoning" }"""

if '"defapi":' not in ui:
    ui = ui.replace(target_dir, new_dir, 1)
    print(" -> Added Defapi and Jev to DIRECTORY in ailabResolveModelProvenance")

# 2.5 Update groups and dynamic option generation in ailabLoadLiveModels
target_groups = """      const groups = {
        krutrim: [],"""
new_groups = """      const groups = {
        defapi: [],
        jev: [],
        krutrim: [],"""

if "defapi: []," not in ui:
    ui = ui.replace(target_groups, new_groups, 1)
    print(" -> Added defapi and jev to groups in ailabLoadLiveModels")

target_pfx = """          if (pfx === "krutrim" || pfx === "ola") {"""
new_pfx = """          if (pfx === "defapi") {
            groups.defapi.push(item);
          } else if (pfx === "jev" || pfx === "typesafe") {
            groups.jev.push(item);
          } else if (pfx === "krutrim" || pfx === "ola") {"""

if 'if (pfx === "defapi") {' not in ui:
    ui = ui.replace(target_pfx, new_pfx, 1)
    print(" -> Added pfx check for defapi and jev in ailabLoadLiveModels")

target_opt_html = """        const optHtml = [
          `<optgroup label="⚡ High-Tech Mathematical Router"><option value="auto">⚡ AUTO Router</option></optgroup>`,
          groups.krutrim.length ? `<optgroup label="🇮🇳 Krutrim AI (Ola Sovereign Cloud · ${groups.krutrim.length} Models)">${groups.krutrim.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "","""

new_opt_html = """        const optHtml = [
          `<optgroup label="⚡ High-Tech Mathematical Router"><option value="auto">⚡ AUTO Router</option></optgroup>`,
          groups.defapi.length ? `<optgroup label="🌐 Defapi Multi-Model Hub (${groups.defapi.length} Frontier Models)">${groups.defapi.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.jev.length ? `<optgroup label="⚡ TypeSafe AI JEV (${groups.jev.length} Decision Models)">${groups.jev.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "",
          groups.krutrim.length ? `<optgroup label="🇮🇳 Krutrim AI (Ola Sovereign Cloud · ${groups.krutrim.length} Models)">${groups.krutrim.map(m => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.name)}</option>`).join("")}</optgroup>` : "","""

if 'groups.defapi.length ?' not in ui:
    ui = ui.replace(target_opt_html, new_opt_html, 1)
    print(" -> Added defapi and jev dynamic optgroups")

# 2.6 Update ailabRenderModelCatalog with seed models and category filtering
target_seeds = """          // Arcee AI (Domain-Specialized SLMs)
          { id: "arcee/zai-org/glm-5.3-flash", name: "Arcee GLM 5.3 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: true },
          { id: "arcee/deepseek/deepseek-v4.1-flash", name: "Arcee DeepSeek V4.1 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: false },
          { id: "arcee/moonshotai/kimi-k3.1-pro", name: "Arcee Kimi K3.1 Pro", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: false }
        ];"""

new_seeds = """          // Arcee AI (Domain-Specialized SLMs)
          { id: "arcee/zai-org/glm-5.3-flash", name: "Arcee GLM 5.3 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: true },
          { id: "arcee/deepseek/deepseek-v4.1-flash", name: "Arcee DeepSeek V4.1 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: false },
          { id: "arcee/moonshotai/kimi-k3.1-pro", name: "Arcee Kimi K3.1 Pro", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: false },
          // Defapi Multi-Model Frontier Hub (44 Models)
          { id: "defapi/alibaba/wan-2.7-image", name: "Defapi Wan 2.7 Image", lab: "Defapi Hub", country: "China", flag: "🇨🇳", is_free: false },
          { id: "defapi/anthropic/claude-fable-5-2", name: "Defapi Claude Fable 5.2", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "defapi/anthropic/claude-opus-5.5", name: "Defapi Claude Opus 5.5", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "defapi/google/gemini-3.7-flash", name: "Defapi Gemini 3.7 Flash", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "defapi/google/gemini-4-hydrogen", name: "Defapi Gemini 4 Hydrogen", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "defapi/google/gemini-4-neon", name: "Defapi Gemini 4 Neon", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "defapi/google/nano-banana-pro", name: "Defapi Nano Banana Pro", lab: "Defapi Hub", country: "United States", flag: "🍌", is_free: true },
          { id: "defapi/openai/gpt-5.6-luna", name: "Defapi GPT-5.6 Luna", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "defapi/openai/gpt-6-astra", name: "Defapi GPT-6 Astra", lab: "Defapi Hub", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "defapi/openai/sora-2-pro", name: "Defapi Sora 2 Pro", lab: "Defapi Hub", country: "United States", flag: "🎥", is_free: false },
          { id: "defapi/suno/chirp-v4-5", name: "Defapi Chirp v4.5", lab: "Defapi Hub", country: "United States", flag: "🎵", is_free: false },
          // TypeSafe AI JEV Decision Mesh (10 Models)
          { id: "jev/jev-latest", name: "JEV Latest (Sub-50ms Calibrated Decision)", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", is_free: true },
          { id: "jev/jev-decision-fast", name: "JEV Decision Fast Engine", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", is_free: true },
          { id: "jev/jev-decision-deep", name: "JEV Decision Deep Logic", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", is_free: false },
          { id: "jev/typesafe/jev-1.13", name: "TypeSafe JEV 1.13", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", is_free: false },
          { id: "jev/jev-verifier-pro", name: "JEV Verifier Pro", lab: "TypeSafe AI (JEV)", country: "United States", flag: "⚡", is_free: false }
        ];"""

if "defapi/alibaba/wan-2.7-image" not in ui:
    ui = ui.replace(target_seeds, new_seeds, 1)
    print(" -> Added Defapi and Jev seed models to modal fallback")

target_filter = """        if (currentCatalogCategory === "krutrim" && !m.id.startsWith("krutrim/") && !(m.lab && m.lab.includes("Krutrim"))) return false;"""
new_filter = """        if (currentCatalogCategory === "defapi" && !m.id.startsWith("defapi/") && !(m.lab && m.lab.includes("Defapi"))) return false;
        if (currentCatalogCategory === "jev" && !m.id.startsWith("jev/") && !m.id.startsWith("typesafe/") && !(m.lab && m.lab.includes("JEV"))) return false;
        if (currentCatalogCategory === "krutrim" && !m.id.startsWith("krutrim/") && !(m.lab && m.lab.includes("Krutrim"))) return false;"""

if 'currentCatalogCategory === "defapi"' not in ui:
    ui = ui.replace(target_filter, new_filter, 1)
    print(" -> Added defapi and jev category filters")

# Exclude defapi and jev from pure openrouter category
target_or_filter = '|| m.id.startsWith("baseten/")'
new_or_filter = '|| m.id.startsWith("baseten/") || m.id.startsWith("defapi/") || m.id.startsWith("jev/") || m.id.startsWith("typesafe/")'
if 'm.id.startsWith("defapi/")' not in ui:
    ui = ui.replace(target_or_filter, new_or_filter, 1)
    print(" -> Excluded defapi and jev from OpenRouter category pill")

with open("app/ui/global_ai_lab_view.py", "w", encoding="utf-8") as f:
    f.write(ui)
print(" -> app/ui/global_ai_lab_view.py updated successfully.")

print("[OK] All files updated cleanly!")
