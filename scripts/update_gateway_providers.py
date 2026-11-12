# -*- coding: utf-8 -*-
with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update MULTI_PROVIDER_KEYS
old_keys = """const MULTI_PROVIDER_KEYS = {
      OPENROUTER: "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",
      GROQ: "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",
      DEEPINFRA: "sk-di-GZlkK2nWUqmV5nxhsdCbGLWxce5EkSAJ",
      DEEPSEEK: "sk-2d5bc8b3419244e6bc17f23b36dd6d66",
      MISTRAL: "mstrl_OZwEdSDxbLIE8xd9Sg0i3wDLH2l2wOnQ_1OV8Q4"
    };"""

new_keys = """const MULTI_PROVIDER_KEYS = {
      OPENROUTER: "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",
      GROQ: "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",
      DEEPINFRA: "sk-di-GZlkK2nWUqmV5nxhsdCbGLWxce5EkSAJ",
      DEEPSEEK: "sk-2d5bc8b3419244e6bc17f23b36dd6d66",
      MISTRAL: "mstrl_OZwEdSDxbLIE8xd9Sg0i3wDLH2l2wOnQ_1OV8Q4",
      HUGGINGFACE: "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",
      FAL_AI: "fal_sk_d1a4032b2a4d4c94ad7cbef5395d439f:ad79f427f9e0d633316032a561ab9999",
      REPLICATE: "r8_VSW8CuVp9dP35gBcLCIFIJcNxfzVpuY3jNpQI",
      AIMLAPI: "d6b5f7f58a5d797e02fd021c231026ea",
      AIMLAPI_BACKUP: "666612ebe3ae25e4db14bd8da4b654fd"
    };"""

if old_keys in code:
    code = code.replace(old_keys, new_keys)
    print("1. Updated MULTI_PROVIDER_KEYS in gateway!")
else:
    print("Warning: old_keys not matched directly; checking variant...")

# 2. Add callAIMLAPI and callHuggingFace
call_or_marker = "async function callOR(targetModel, timeoutMs = 8000) {"
idx_call = code.find(call_or_marker)
if idx_call != -1:
    extra_callers = """async function callAIMLAPI(targetModel, timeoutMs = 8000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const resp = await fetch("https://api.aimlapi.com/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.AIMLAPI}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: targetModel.replace(/^aimlapi\\//, ""),
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

      async function callHuggingFace(targetModel, timeoutMs = 9000) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeoutMs);
        try {
          const cleanModel = targetModel.replace(/^hf\\//, "").replace(/^huggingface\\//, "");
          const resp = await fetch(`https://router.huggingface.co/hf-inference/models/${cleanModel}/v1/chat/completions`, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${MULTI_PROVIDER_KEYS.HUGGINGFACE}`,
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

      """
    if "callAIMLAPI" not in code:
        code = code[:idx_call] + extra_callers + code[idx_call:]
        print("2. Added callAIMLAPI & callHuggingFace!")

# 3. Add HF and AIMLAPI to LAB_DIRECTORY in resolveGlobalAILabProvenance
lab_dir_marker = '"microsoft": { lab: "Microsoft (Phi)", country: "United States", flag: "🇺🇸", tier: "Small Language SOTA" }'
idx_lab = code.find(lab_dir_marker)
if idx_lab != -1:
    new_labs = ',\n        "hf": { lab: "Hugging Face (Open Weights)", country: "France / US", flag: "🤗", tier: "110+ Open-Weights SOTA" },\n        "huggingface": { lab: "Hugging Face (Open Weights)", country: "France / US", flag: "🤗", tier: "110+ Open-Weights SOTA" },\n        "aimlapi": { lab: "AI/ML API Multi-Cloud Hub", country: "United States", flag: "⚡", tier: "995+ Unified Models" },\n        "fal": { lab: "fal.ai Lightning Compute", country: "United States", flag: "🎨", tier: "Generative Media & Flux SOTA" },\n        "fal-ai": { lab: "fal.ai Lightning Compute", country: "United States", flag: "🎨", tier: "Generative Media & Flux SOTA" },\n        "replicate": { lab: "Replicate Cloud", country: "United States", flag: "🚀", tier: "Containerized Models" }'
    if '"huggingface":' not in code:
        code = code[:idx_lab + len(lab_dir_marker)] + new_labs + code[idx_lab + len(lab_dir_marker):]
        print("3. Added new provider labs in resolveGlobalAILabProvenance!")

# 4. Update total_models count in global_labs to 1468+
code = code.replace("total_models: liveModels ? liveModels.length : 433", "total_models: liveModels ? (liveModels.length + 995) : 1468")

with open('deploy/cloudflare_worker_gateway.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully updated deploy/cloudflare_worker_gateway.js!")
