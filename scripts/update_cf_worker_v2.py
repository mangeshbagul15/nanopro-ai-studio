import sys

with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update MULTI_PROVIDER_KEYS
old_keys = """      DEEPSEEK: "sk-2d5bc8b3419244e6bc17f23b36dd6d66","""
new_keys = """      DEEPSEEK: "sk-d633fc52cbe041e2a87372a8c2639615",
      ARCEE: "rcai-c472ef2f4f2ad7362f6decf31f65c047",
      PARASAIL: "psk-nano6dc5de4t-PtQ50R9kBFZAbECjwk6W",
      KRUTRIM: "JcMcoC72Osu3suH8oVvy-2An4",
      POE: "sk-poe-Q_PHEUPo8oUxy-FGHxCy4y2cMbtJSx5y0hprJLGDXcY",
      BASETEN_2: "b10_opZ4nBmj.wzha2FItX9WeW0bgaQAlSqSXOsV2v0XY","""

if old_keys in content:
    content = content.replace(old_keys, new_keys)
    print("1. Updated MULTI_PROVIDER_KEYS")
else:
    print("1. Old keys not found")

# 2. Update LAB_DIRECTORY
target_labs = """        "baseten": { lab: "Baseten", country: "United States", flag: "🏗️", tier: "Truss Dedicated Inference" }
      };"""

replacement_labs = """        "baseten": { lab: "Baseten", country: "United States", flag: "🏗️", tier: "Truss Dedicated Inference" },
        "krutrim": { lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign AI Cloud" },
        "ola": { lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign AI Cloud" },
        "poe": { lab: "Poe by Quora", country: "United States", flag: "⚡", tier: "300+ Unified Bot Fabric" },
        "parasail": { lab: "Parasail GPU Network", country: "Global", flag: "⛵", tier: "100+ Decentralized GPU Models" },
        "arcee": { lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain Specialized SLMs" }
      };"""

if target_labs in content:
    content = content.replace(target_labs, replacement_labs)
    print("2. Updated LAB_DIRECTORY")
else:
    print("2. target_labs not found")

# 3. Update providerAddons in getEdgeWorldModels
target_addons = """              { id: "baseten/deepseek-ai/DeepSeek-V4.1-Flash", name: "Baseten DeepSeek V4.1 Flash", lab: "Baseten", country: "United States", flag: "🏗️", tier: "Dedicated Truss Inference", context: 65536, is_free: false }
            ];"""

replacement_addons = """              { id: "baseten/deepseek-ai/DeepSeek-V4.1-Flash", name: "Baseten DeepSeek V4.1 Flash", lab: "Baseten", country: "United States", flag: "🏗️", tier: "Dedicated Truss Inference", context: 65536, is_free: false },
              // Ola Krutrim Cloud (India's Sovereign AI Cloud)
              { id: "krutrim/Qwen3.6-27B", name: "Krutrim Qwen 3.6 27B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", context: 32768, is_free: true },
              { id: "krutrim/gpt-oss-120b", name: "Krutrim GPT OSS 120B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", context: 8192, is_free: true },
              { id: "krutrim/gemma-4-31b-it", name: "Krutrim Gemma 4 31B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", context: 16384, is_free: true },
              { id: "krutrim/GLM-5.3-Flash", name: "Krutrim GLM 5.3 Flash", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", context: 32768, is_free: true },
              { id: "krutrim/gpt-oss-20b", name: "Krutrim GPT OSS 20B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", context: 8192, is_free: true },
              // Poe API (303 Unified Bot Models)
              { id: "poe/gemini-4-hydrogen", name: "Poe Gemini 4 Hydrogen", lab: "Poe by Quora", country: "United States", flag: "⚡", tier: "Unified Bot Fabric", context: 1048576, is_free: false },
              { id: "poe/grok-4.7", name: "Poe Grok 4.7", lab: "Poe by Quora", country: "United States", flag: "⚡", tier: "Frontier Knowledge", context: 500000, is_free: false },
              { id: "poe/kimi-k3.1-pro", name: "Poe Kimi K3.1 Pro", lab: "Poe by Quora", country: "United States", flag: "⚡", tier: "Ultra Long Context 1M", context: 1048576, is_free: false },
              { id: "poe/claude-sonnet-5.5", name: "Poe Claude Sonnet 5.5", lab: "Poe by Quora", country: "United States", flag: "⚡", tier: "Coding & Reasoning SOTA", context: 200000, is_free: false },
              { id: "poe/mistral-large-4", name: "Poe Mistral Large 4", lab: "Poe by Quora", country: "United States", flag: "⚡", tier: "European Flagship", context: 131072, is_free: false },
              { id: "poe/mercury-3-vercel", name: "Poe Mercury 3 Diffusion", lab: "Poe by Quora", country: "United States", flag: "⚡", tier: "Diffusion LLM", context: 1000000, is_free: false },
              // Parasail GPU Network (107 Models)
              { id: "parasail/parasail-llama-33-70b-fp8", name: "Parasail Llama 3.3 70B FP8", lab: "Parasail GPU Network", country: "Global", flag: "⛵", tier: "Decentralized GPU", context: 131072, is_free: true },
              { id: "parasail/parasail-qwen25-vl-72b-instruct", name: "Parasail Qwen 2.5 VL 72B", lab: "Parasail GPU Network", country: "Global", flag: "⛵", tier: "Vision-Language SOTA", context: 32768, is_free: false },
              { id: "parasail/parasail-skyfall-36b-v2-fp8", name: "Parasail Skyfall 36B v2", lab: "Parasail GPU Network", country: "Global", flag: "⛵", tier: "Creative & Coding", context: 65536, is_free: false },
              { id: "parasail/parasail-llama-4-maverick-instruct-fp8", name: "Parasail Llama 4 Maverick", lab: "Parasail GPU Network", country: "Global", flag: "⛵", tier: "Next-Gen Open Weights", context: 131072, is_free: false },
              // Arcee AI (Domain-Specialized SLMs)
              { id: "arcee/zai-org/glm-5.3-flash", name: "Arcee GLM 5.3 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain SLM", context: 32768, is_free: true },
              { id: "arcee/deepseek/deepseek-v4.1-flash", name: "Arcee DeepSeek V4.1 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain SLM", context: 65536, is_free: false },
              { id: "arcee/moonshotai/kimi-k3.1-pro", name: "Arcee Kimi K3.1 Pro", lab: "Arcee AI", country: "United States", flag: "🏹", tier: "Long Context SLM", context: 1048576, is_free: false }
            ];"""

if target_addons in content:
    content = content.replace(target_addons, replacement_addons)
    print("3. Updated providerAddons")
else:
    print("3. target_addons not found")

# 4. Add dispatch helper functions
target_helpers = """      async function callNovitaAI(targetModel, timeoutMs = 8000) {"""

replacement_helpers = """      async function callKrutrimAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^krutrim\//, "");
          const resp = await fetch("https://cloud.olakrutrim.com/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.KRUTRIM}`,
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

      async function callPoeAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^poe\//, "");
          const resp = await fetch("https://api.poe.com/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.POE}`,
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

      async function callParasailAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^parasail\//, "");
          const resp = await fetch("https://api.parasail.io/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.PARASAIL}`,
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

      async function callArceeAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^arcee\//, "");
          const resp = await fetch("https://api.arcee.ai/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.ARCEE}`,
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

      async function callNovitaAI(targetModel, timeoutMs = 8000) {"""

if target_helpers in content:
    content = content.replace(target_helpers, replacement_helpers)
    print("4. Added dispatch helpers for Krutrim, Poe, Parasail, Arcee")
else:
    print("4. target_helpers not found")

# 5. Add execution routing branches to /api/ai/execute
target_exec = """        } else if (model.startsWith("baseten/")) {
          activeProvider = "BASETEN";
          resp = await callBaseten(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("deepseek/deepseek-chat", 8500);
          }"""

replacement_exec = """        } else if (model.startsWith("baseten/")) {
          activeProvider = "BASETEN";
          resp = await callBaseten(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("deepseek/deepseek-chat", 8500);
          }
        } else if (model.startsWith("krutrim/")) {
          activeProvider = "KRUTRIM_AI_CLOUD";
          resp = await callKrutrimAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 8500);
          }
        } else if (model.startsWith("poe/")) {
          activeProvider = "POE_API_FABRIC";
          resp = await callPoeAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^poe\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("parasail/")) {
          activeProvider = "PARASAIL_GPU_NETWORK";
          resp = await callParasailAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 8500);
          }
        } else if (model.startsWith("arcee/")) {
          activeProvider = "ARCEE_AI_SLM";
          resp = await callArceeAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("qwen/qwen-2.5-72b-instruct", 8500);
          }"""

if target_exec in content:
    content = content.replace(target_exec, replacement_exec)
    print("5. Added routing branches to /api/ai/execute")
else:
    print("5. target_exec not found")

# 6. Update total model count and edgeCatalog
content = content.replace("4,330+ Unified Frontier Models active", "4,750+ Unified Frontier Models active")
content = content.replace(
    "total_models: liveModels ? (liveModels.length + 1311 + 750 + 995 + 177 + 150 + 110 + 99 + 83 + 56 + 11 + 5) : 4330",
    "total_models: liveModels ? (liveModels.length + 1311 + 750 + 995 + 303 + 177 + 150 + 110 + 107 + 99 + 83 + 56 + 11 + 9 + 6 + 5) : 4750"
)

with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved updated deploy/cloudflare_worker_gateway.js")
