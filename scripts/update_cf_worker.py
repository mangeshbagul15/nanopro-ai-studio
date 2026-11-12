import sys, re

with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update MULTI_PROVIDER_KEYS
old_keys_target = """      NOVITA: "sk_YEp9ZyBhTK7uPVd1qPtfCFVt4p2vjVIABJxmLIJB07E",
      CF_AI: "cfut_DqwcZt8S50UIJlhXqYDRilqEF2zzdOwGV9SxMmkWeea8d73a",
      CF_ACCOUNT: "ccd6c0bc1765868497170623a66e6ec1"
    };"""

new_keys_replacement = """      NOVITA: "sk_YEp9ZyBhTK7uPVd1qPtfCFVt4p2vjVIABJxmLIJB07E",
      CF_AI: "cfut_DqwcZt8S50UIJlhXqYDRilqEF2zzdOwGV9SxMmkWeea8d73a",
      CF_ACCOUNT: "ccd6c0bc1765868497170623a66e6ec1",
      SAMBANOVA: "d5e98adf-2b3c-477a-8d80-d26c242548c4",
      REQUESTY: "rqsty-sk-NgcuVBmxQdq1H1u8nqYg6UaUzQKPnR6PJScxuLv3bUh5Lpj0nWFBxrQD5KQvKpe1nVikk2N8DfjHnON0pvKEaeCsPuWF5lDC1sS9rb4UwA0=",
      NVIDIA: "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",
      NVIDIA_ID: "cee2aada-2aca-43ff-a351-161e20ee8977",
      BASETEN: "b10_fJMWbc5R.2e2dU9BmpkOsyLwhU8Wrn0e8TCSSJJfR",
      FRIENDLI: "flp_TofgBoyBBXyGzuYjkQDrL8yh0UrS4lMkxSFnuu0wfma26",
      THESEAN: "sk-b4d2af78341948d49280a2e8742af6d2",
      EDENAI_1: "sk-eden-live-rXdRorWgt7qBrIGT_sRZVcU_yWVyE53ZOhuPv-znZwo71f74d72",
      EDENAI_2: "sk-eden-live-iY3xqwWPDt90FfaoReckFnymjdRqK3zTPEgjkOPNFWQ96107a35"
    };"""

if old_keys_target in content:
    content = content.replace(old_keys_target, new_keys_replacement)
    print("1. MULTI_PROVIDER_KEYS updated")
else:
    print("1. MULTI_PROVIDER_KEYS target not found")

# 2. Add new labs to resolveGlobalAILabProvenance
old_lab_target = """        "cf": { lab: "Cloudflare Workers AI", country: "Global Edge Network", flag: "☁️", tier: "Zero-Latency Edge Inference" }
      };"""

new_lab_replacement = """        "cf": { lab: "Cloudflare Workers AI", country: "Global Edge Network", flag: "☁️", tier: "Zero-Latency Edge Inference" },
        "sambanova": { lab: "SambaNova Systems", country: "United States", flag: "⚡", tier: "SN40L Reconfigurable Dataflow (RDU)" },
        "requesty": { lab: "Requesty AI", country: "Global Router", flag: "🌐", tier: "750+ Global Unified Models" },
        "nvidia": { lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "83+ TensorRT-LLM Microservices" },
        "edenai": { lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "1,311+ Global Multimodal Catalog" },
        "friendli": { lab: "FriendliAI", country: "South Korea / Global", flag: "🚀", tier: "PeriFlow High-Throughput Engine" },
        "thesean": { lab: "TheSean AI", country: "Global", flag: "⚡", tier: "Ultra-Low Latency Inference" },
        "baseten": { lab: "Baseten", country: "United States", flag: "🏗️", tier: "Truss Dedicated Inference" }
      };"""

if old_lab_target in content:
    content = content.replace(old_lab_target, new_lab_replacement)
    print("2. LAB_DIRECTORY updated")
else:
    print("2. LAB_DIRECTORY target not found")

# 3. Add new models to providerAddons
old_addons_target = """              // Hugging Face Hub (110+ Models)
              { id: "hf/meta-llama/Llama-3.3-70B-Instruct", name: "Hugging Face Llama 3.3 70B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 131072, is_free: true },
              { id: "hf/Qwen/Qwen2.5-Coder-32B-Instruct", name: "Hugging Face Qwen Coder 32B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 32768, is_free: true },
              { id: "hf/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", name: "Hugging Face DeepSeek R1 Distill", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 65536, is_free: true }
            ];"""

new_addons_replacement = """              // Hugging Face Hub (110+ Models)
              { id: "hf/meta-llama/Llama-3.3-70B-Instruct", name: "Hugging Face Llama 3.3 70B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 131072, is_free: true },
              { id: "hf/Qwen/Qwen2.5-Coder-32B-Instruct", name: "Hugging Face Qwen Coder 32B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 32768, is_free: true },
              { id: "hf/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", name: "Hugging Face DeepSeek R1 Distill", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 65536, is_free: true },
              // SambaNova Systems (Fast SN40L RDUs)
              { id: "sambanova/Meta-Llama-3.3-70B-Instruct", name: "SambaNova Llama 3.3 70B (Fast RDU)", lab: "SambaNova Systems", country: "United States", flag: "⚡", tier: "Deterministic Fast RDU", context: 131072, is_free: true },
              { id: "sambanova/GLM-5.3", name: "SambaNova GLM-5.3 Flagship", lab: "SambaNova Systems", country: "United States", flag: "⚡", tier: "Bilingual SOTA", context: 32768, is_free: true },
              { id: "sambanova/MiniMax-M3.1-Flash", name: "SambaNova MiniMax M3.1 Flash", lab: "SambaNova Systems", country: "United States", flag: "⚡", tier: "Ultra-Fast Inference", context: 32768, is_free: true },
              { id: "sambanova/gemma-4-31B-it", name: "SambaNova Gemma 4 31B", lab: "SambaNova Systems", country: "United States", flag: "⚡", tier: "Open Model", context: 16384, is_free: true },
              { id: "sambanova/gpt-oss-120b", name: "SambaNova GPT OSS 120B", lab: "SambaNova Systems", country: "United States", flag: "⚡", tier: "Open Weights Flagship", context: 8192, is_free: true },
              // NVIDIA NIM (83 Models)
              { id: "nvidia/llama-3.1-nemotron-70b-instruct", name: "NVIDIA Llama 3.1 Nemotron 70B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "TensorRT-LLM Microservice", context: 131072, is_free: false },
              { id: "nvidia/nemotron-4-340b-instruct", name: "NVIDIA Nemotron 4 340B Flagship", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "Enterprise Flagship", context: 4096, is_free: false },
              { id: "nvidia/mistralai/codestral-22b-instruct-v0.1", name: "NVIDIA Codestral 22B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "Code Specialist", context: 32768, is_free: false },
              { id: "nvidia/deepseek-ai/deepseek-v4.1-flash", name: "NVIDIA DeepSeek V4.1 Flash", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "High Throughput", context: 65536, is_free: false },
              { id: "nvidia/bigcode/starcoder2-15b", name: "NVIDIA StarCoder2 15B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "Code Specialist", context: 16384, is_free: false },
              // Requesty AI (750 Models)
              { id: "requesty/anthropic/claude-fable-5.2", name: "Requesty Claude Fable 5.2", lab: "Requesty AI", country: "Global Router", flag: "🌐", tier: "Frontier Hybrid", context: 200000, is_free: false },
              { id: "requesty/google/gemini-4-hydrogen", name: "Requesty Gemini 4 Hydrogen", lab: "Requesty AI", country: "Global Router", flag: "🌐", tier: "Next-Gen Multimodal", context: 2000000, is_free: false },
              { id: "requesty/openai/gpt-6.1-terra:flex", name: "Requesty GPT 6.1 Terra", lab: "Requesty AI", country: "Global Router", flag: "🌐", tier: "Reasoning SOTA", context: 128000, is_free: false },
              { id: "requesty/deepseek/deepseek-chat", name: "Requesty DeepSeek V3", lab: "Requesty AI", country: "Global Router", flag: "🌐", tier: "Open Flagship", context: 65536, is_free: false },
              // Eden AI (1,311 Models)
              { id: "edenai/openai/gpt-4o", name: "Eden AI OpenAI GPT-4o", lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "Multimodal Flagship", context: 128000, is_free: false },
              { id: "edenai/anthropic/claude-3-5-sonnet", name: "Eden AI Claude 3.5 Sonnet", lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "Reasoning & Code SOTA", context: 200000, is_free: false },
              { id: "edenai/google/gemini-1.5-pro", name: "Eden AI Google Gemini 1.5 Pro", lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "Long Context 2M", context: 2000000, is_free: false },
              { id: "edenai/mistral/mistral-large-latest", name: "Eden AI Mistral Large 2", lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "European Flagship", context: 131072, is_free: false },
              { id: "edenai/deepseek/deepseek-r1", name: "Eden AI DeepSeek R1", lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "Reasoning SOTA", context: 65536, is_free: false },
              // FriendliAI, TheSean & Baseten
              { id: "friendli/meta-llama-3.1-8b-instruct", name: "FriendliAI Llama 3.1 8B (PeriFlow)", lab: "FriendliAI", country: "South Korea / Global", flag: "🚀", tier: "High-Throughput Serverless", context: 131072, is_free: true },
              { id: "thesean/ship-like/claude-haiku-4-5", name: "TheSean Claude Haiku 4.5", lab: "TheSean AI", country: "Global", flag: "⚡", tier: "Ultra-Low Latency", context: 200000, is_free: false },
              { id: "baseten/deepseek-ai/DeepSeek-V4.1-Flash", name: "Baseten DeepSeek V4.1 Flash", lab: "Baseten", country: "United States", flag: "🏗️", tier: "Dedicated Truss Inference", context: 65536, is_free: false }
            ];"""

if old_addons_target in content:
    content = content.replace(old_addons_target, new_addons_replacement)
    print("3. providerAddons updated")
else:
    print("3. providerAddons target not found")

# 4. Add dispatch helper functions
old_dispatch_target = """      async function callNovitaAI(targetModel, timeoutMs = 8000) {"""

new_dispatch_functions = """      async function callSambaNova(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^sambanova\//, "");
          const resp = await fetch("https://api.sambanova.ai/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.SAMBANOVA}`,
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

      async function callRequestyAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^requesty\//, "");
          const resp = await fetch("https://router.requesty.ai/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.REQUESTY}`,
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

      async function callNvidiaNIM(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^nvidia\//, "");
          const resp = await fetch("https://integrate.api.nvidia.com/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.NVIDIA}`,
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

      async function callEdenAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^edenai\//, "");
          let resp = await fetch("https://api.edenai.run/v3/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.EDENAI_1}`,
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
          if (!resp.ok && (resp.status === 402 || resp.status === 401 || resp.status === 429)) {
            resp = await fetch("https://api.edenai.run/v3/chat/completions", {
              method: "POST",
              headers: {
                "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.EDENAI_2}`,
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
          }
          clearTimeout(tid);
          return resp;
        } catch (_) {
          clearTimeout(tid);
          return null;
        }
      }

      async function callFriendliAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^friendli\//, "");
          const resp = await fetch("https://api.friendli.ai/serverless/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.FRIENDLI}`,
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

      async function callTheSeanAI(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^thesean\//, "");
          const resp = await fetch("https://api.thesean.ai/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.THESEAN}`,
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

      async function callBaseten(targetModel, timeoutMs = 7000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^baseten\//, "");
          const resp = await fetch("https://inference.baseten.co/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.BASETEN}`,
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

if old_dispatch_target in content:
    content = content.replace(old_dispatch_target, new_dispatch_functions)
    print("4. Dispatch helper functions added")
else:
    print("4. Dispatch helper functions target not found")

# 5. Add routing branches to /api/ai/execute
old_exec_target = """        } else if (model.startsWith("novita/")) {
          activeProvider = "NOVITA_AI_DIRECT";
          resp = await callNovitaAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^novita\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("@cf/") || model.startsWith("cf/")) {"""

new_exec_replacement = """        } else if (model.startsWith("novita/")) {
          activeProvider = "NOVITA_AI_DIRECT";
          resp = await callNovitaAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^novita\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("sambanova/")) {
          activeProvider = "SAMBANOVA_RDU";
          resp = await callSambaNova(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 8500);
          }
        } else if (model.startsWith("requesty/")) {
          activeProvider = "REQUESTY_ROUTER";
          resp = await callRequestyAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^requesty\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("nvidia/")) {
          activeProvider = "NVIDIA_NIM";
          resp = await callNvidiaNIM(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^nvidia\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("edenai/")) {
          activeProvider = "EDEN_AI_AGGREGATOR";
          resp = await callEdenAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^edenai\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("friendli/")) {
          activeProvider = "FRIENDLI_AI";
          resp = await callFriendliAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("meta-llama/llama-3.1-8b-instruct", 8500);
          }
        } else if (model.startsWith("thesean/")) {
          activeProvider = "THESEAN_AI";
          resp = await callTheSeanAI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("anthropic/claude-3.5-haiku", 8500);
          }
        } else if (model.startsWith("baseten/")) {
          activeProvider = "BASETEN";
          resp = await callBaseten(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("deepseek/deepseek-chat", 8500);
          }
        } else if (model.startsWith("@cf/") || model.startsWith("cf/")) {"""

if old_exec_target in content:
    content = content.replace(old_exec_target, new_exec_replacement)
    print("5. Execute routing branches added")
else:
    print("5. Execute routing branches target not found")

# 6. Update seed message count
content = content.replace("2,150+ Unified Frontier Models active", "4,330+ Unified Frontier Models active")

with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved updated deploy/cloudflare_worker_gateway.js")
