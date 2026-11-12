import sys

# 1. Create render.yaml
render_yaml_content = """# Render Infrastructure-as-Code Blueprint
# NanoPro Sovereign Global AI Lab & Core Banking Studio
services:
  - type: web
    name: nanopro-studio
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    plan: free
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: OPENROUTER_API_KEY
        value: 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
      - key: GROQ_API_KEY
        value: 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
      - key: DEEPINFRA_API_KEY
        value: sk-di-GZlkK2nWUqmV5nxhsdCbGLWxce5EkSAJ
      - key: DEEPSEEK_API_KEY
        value: sk-d633fc52cbe041e2a87372a8c2639615
      - key: MISTRAL_API_KEY
        value: mstrl_OZwEdSDxbLIE8xd9Sg0i3wDLH2l2wOnQ_1OV8Q4
      - key: HUGGINGFACE_API_KEY
        value: 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
      - key: FAL_AI_API_KEY
        value: fal_sk_d1a4032b2a4d4c94ad7cbef5395d439f:ad79f427f9e0d633316032a561ab9999
      - key: REPLICATE_API_TOKEN
        value: r8_VSW8CuVp9dP35gBcLCIFIJcNxfzVpuY3jNpQI
      - key: AIMLAPI_KEY
        value: d6b5f7f58a5d797e02fd021c231026ea
      - key: AIMLAPI_BACKUP_KEY
        value: 666612ebe3ae25e4db14bd8da4b654fd
      - key: NOVITA_AI_KEY
        value: sk_YEp9ZyBhTK7uPVd1qPtfCFVt4p2vjVIABJxmLIJB07E
      - key: CLOUDFLARE_AI_TOKEN
        value: cfut_DqwcZt8S50UIJlhXqYDRilqEF2zzdOwGV9SxMmkWeea8d73a
      - key: CLOUDFLARE_ACCOUNT_ID
        value: ccd6c0bc1765868497170623a66e6ec1
      - key: SAMBANOVA_API_KEY
        value: d5e98adf-2b3c-477a-8d80-d26c242548c4
      - key: REQUESTY_API_KEY
        value: rqsty-sk-NgcuVBmxQdq1H1u8nqYg6UaUzQKPnR6PJScxuLv3bUh5Lpj0nWFBxrQD5KQvKpe1nVikk2N8DfjHnON0pvKEaeCsPuWF5lDC1sS9rb4UwA0=
      - key: NVIDIA_NIM_API_KEY
        value: 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
      - key: NVIDIA_NIM_ID
        value: cee2aada-2aca-43ff-a351-161e20ee8977
      - key: BASETEN_API_KEY
        value: b10_fJMWbc5R.2e2dU9BmpkOsyLwhU8Wrn0e8TCSSJJfR
      - key: BASETEN_API_KEY_2
        value: b10_opZ4nBmj.wzha2FItX9WeW0bgaQAlSqSXOsV2v0XY
      - key: FRIENDLI_API_KEY
        value: flp_TofgBoyBBXyGzuYjkQDrL8yh0UrS4lMkxSFnuu0wfma26
      - key: THESEAN_API_KEY
        value: sk-b4d2af78341948d49280a2e8742af6d2
      - key: EDEN_AI_KEY_1
        value: sk-eden-live-rXdRorWgt7qBrIGT_sRZVcU_yWVyE53ZOhuPv-znZwo71f74d72
      - key: EDEN_AI_KEY_2
        value: sk-eden-live-iY3xqwWPDt90FfaoReckFnymjdRqK3zTPEgjkOPNFWQ96107a35
      - key: ARCEE_API_KEY
        value: rcai-c472ef2f4f2ad7362f6decf31f65c047
      - key: PARASAIL_API_KEY
        value: psk-nano6dc5de4t-PtQ50R9kBFZAbECjwk6W
      - key: KRUTRIM_API_KEY
        value: JcMcoC72Osu3suH8oVvy-2An4
      - key: POE_API_KEY
        value: sk-poe-Q_PHEUPo8oUxy-FGHxCy4y2cMbtJSx5y0hprJLGDXcY
"""

with open("render.yaml", "w", encoding="utf-8") as f:
    f.write(render_yaml_content.strip() + "\n")
print("1. Created render.yaml with all 28 API keys and parameters")

# 2. Update HTML select in app/ui/global_ai_lab_view.py
with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    text = f.read()

old_select_start = '<select class="ailab-model-select" id="ailabModelSelect" onchange="ailabChangeModel(this.value)">'
old_select_end = '</select>'
pos_start = text.find(old_select_start)
pos_end = text.find(old_select_end, pos_start)

if pos_start != -1 and pos_end != -1:
    new_select_inner = """<select class="ailab-model-select" id="ailabModelSelect" onchange="ailabChangeModel(this.value)">
          <optgroup label="⚡ High-Tech Mathematical Router">
            <option value="auto" selected>⚡ AUTO Router (Pareto &lt;800ms)</option>
          </optgroup>
          <optgroup label="🇮🇳 Krutrim AI (Ola Sovereign Cloud · Qwen 3.6, GPT-OSS 120B, Gemma 4)">
            <option value="krutrim/Qwen3.6-27B">Krutrim Qwen 3.6 27B</option>
            <option value="krutrim/gpt-oss-120b">Krutrim GPT OSS 120B</option>
            <option value="krutrim/gemma-4-31b-it">Krutrim Gemma 4 31B</option>
            <option value="krutrim/GLM-5.3-Flash">Krutrim GLM 5.3 Flash</option>
            <option value="krutrim/gpt-oss-20b">Krutrim GPT OSS 20B</option>
          </optgroup>
          <optgroup label="⚡ Poe by Quora (303 Unified Bot Models)">
            <option value="poe/gemini-4-hydrogen">Poe Gemini 4 Hydrogen (1M Context)</option>
            <option value="poe/grok-4.7">Poe Grok 4.7 (Frontier Reasoning)</option>
            <option value="poe/kimi-k3.1-pro">Poe Kimi K3.1 Pro (1M Context)</option>
            <option value="poe/claude-sonnet-5.5">Poe Claude Sonnet 5.5</option>
            <option value="poe/mistral-large-4">Poe Mistral Large 4</option>
            <option value="poe/mercury-3-vercel">Poe Mercury 3 Diffusion</option>
          </optgroup>
          <optgroup label="🌿 Eden AI (1,311 Unified Models · OpenAI, Anthropic, Gemini, Mistral)">
            <option value="edenai/openai/gpt-4o">Eden AI OpenAI GPT-4o</option>
            <option value="edenai/anthropic/claude-3-5-sonnet">Eden AI Claude 3.5 Sonnet</option>
            <option value="edenai/google/gemini-1.5-pro">Eden AI Google Gemini 1.5 Pro</option>
            <option value="edenai/mistral/mistral-large-latest">Eden AI Mistral Large 2</option>
            <option value="edenai/deepseek/deepseek-r1">Eden AI DeepSeek R1</option>
          </optgroup>
          <optgroup label="🌐 Requesty AI (750 Global Unified Models)">
            <option value="requesty/anthropic/claude-fable-5.2">Requesty Claude Fable 5.2</option>
            <option value="requesty/google/gemini-4-hydrogen">Requesty Gemini 4 Hydrogen</option>
            <option value="requesty/openai/gpt-6.1-terra:flex">Requesty GPT 6.1 Terra</option>
            <option value="requesty/deepseek/deepseek-chat">Requesty DeepSeek V3</option>
          </optgroup>
          <optgroup label="🟢 NVIDIA NIM Microservices (83 Models · TensorRT-LLM)">
            <option value="nvidia/llama-3.1-nemotron-70b-instruct">NVIDIA Llama 3.1 Nemotron 70B</option>
            <option value="nvidia/nemotron-4-340b-instruct">NVIDIA Nemotron 4 340B Flagship</option>
            <option value="nvidia/mistralai/codestral-22b-instruct-v0.1">NVIDIA Codestral 22B</option>
            <option value="nvidia/deepseek-ai/deepseek-v4.1-flash">NVIDIA DeepSeek V4.1 Flash</option>
            <option value="nvidia/bigcode/starcoder2-15b">NVIDIA StarCoder2 15B</option>
          </optgroup>
          <optgroup label="⚡ SambaNova Systems (Fast SN40L RDUs)">
            <option value="sambanova/Meta-Llama-3.3-70B-Instruct">SambaNova Llama 3.3 70B (Fast RDU)</option>
            <option value="sambanova/GLM-5.3">SambaNova GLM-5.3 Flagship</option>
            <option value="sambanova/MiniMax-M3.1-Flash">SambaNova MiniMax M3.1 Flash</option>
            <option value="sambanova/gemma-4-31B-it">SambaNova Gemma 4 31B</option>
            <option value="sambanova/gpt-oss-120b">SambaNova GPT OSS 120B</option>
          </optgroup>
          <optgroup label="⛵ Parasail GPU Network (107 Decentralized Models)">
            <option value="parasail/parasail-llama-33-70b-fp8">Parasail Llama 3.3 70B FP8</option>
            <option value="parasail/parasail-qwen25-vl-72b-instruct">Parasail Qwen 2.5 VL 72B</option>
            <option value="parasail/parasail-skyfall-36b-v2-fp8">Parasail Skyfall 36B v2</option>
            <option value="parasail/parasail-llama-4-maverick-instruct-fp8">Parasail Llama 4 Maverick</option>
          </optgroup>
          <optgroup label="🏹 Arcee AI (Domain-Specialized SLMs)">
            <option value="arcee/zai-org/glm-5.3-flash">Arcee GLM 5.3 Flash</option>
            <option value="arcee/deepseek/deepseek-v4.1-flash">Arcee DeepSeek V4.1 Flash</option>
            <option value="arcee/moonshotai/kimi-k3.1-pro">Arcee Kimi K3.1 Pro</option>
          </optgroup>
          <optgroup label="☁️ Cloudflare Workers AI (Zero-Latency Edge · Llama 3.3, Qwen 2.5)">
            <option value="@cf/meta/llama-3.3-70b-instruct">Cloudflare Workers AI Llama 3.3 70B</option>
            <option value="@cf/meta/llama-3.1-8b-instruct">Cloudflare Workers AI Llama 3.1 8B (&lt;100ms)</option>
            <option value="@cf/deepseek-ai/deepseek-r1-distill-qwen-32b">Cloudflare Workers AI DeepSeek R1 32B</option>
            <option value="@cf/qwen/qwen2.5-72b-instruct">Cloudflare Workers AI Qwen 2.5 72B</option>
          </optgroup>
          <optgroup label="🚀 Novita AI Multi-Cloud (99 Models · DeepSeek V4.1, Kimi K3.1)">
            <option value="novita/deepseek/deepseek-v4.1-flash">Novita DeepSeek V4.1 Flash</option>
            <option value="novita/moonshotai/kimi-k3.1-pro">Novita Kimi K3.1 Pro (Long Context)</option>
            <option value="novita/minimax/minimax-m3.1-flash">Novita MiniMax M3.1 Flash</option>
          </optgroup>
          <optgroup label="🧠 DeepInfra High-Throughput (177 Models · Llama 3.3 Turbo, Qwen, Phi-4)">
            <option value="deepinfra/Qwen/Qwen3.8-Flash">DeepInfra Qwen 3.8 Flash (Turbo)</option>
            <option value="deepinfra/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo">DeepInfra Llama 3.1 8B Turbo</option>
            <option value="deepinfra/meta-llama/Llama-3.3-70B-Instruct">DeepInfra Llama 3.3 70B Turbo</option>
            <option value="deepinfra/deepseek-ai/DeepSeek-R1">DeepInfra DeepSeek R1 Reasoning</option>
            <option value="deepinfra/microsoft/phi-4">DeepInfra Microsoft Phi-4</option>
          </optgroup>
          <optgroup label="🇫🇷 Mistral AI Direct (56 Models · Codestral, Mistral Large, Ministral)">
            <option value="mistral/codestral-latest">Mistral Codestral 2508 (Code SOTA)</option>
            <option value="mistral/mistral-large-latest">Mistral Large 2 (Flagship)</option>
            <option value="mistral/ministral-14b-latest">Mistral Ministral 14B</option>
            <option value="mistral/mistral-small-latest">Mistral Small Latest</option>
          </optgroup>
          <optgroup label="🇨🇳 DeepSeek Sovereign Direct (DeepSeek V3, DeepSeek R1)">
            <option value="deepseek/deepseek-chat">DeepSeek V3 Direct API</option>
            <option value="deepseek/deepseek-reasoner">DeepSeek R1 Direct Reasoner</option>
          </optgroup>
          <optgroup label="⚡ Groq Ultra-Fast LPUs (&lt;300ms SLA)">
            <option value="groq/qwen3.8-27b">Groq Qwen 3.8 27B (&lt;300ms)</option>
            <option value="groq/openai/gpt-oss-120b">Groq GPT OSS 120B</option>
            <option value="groq/llama-3.3-70b-versatile">Groq Llama 3.3 70B Versatile</option>
          </optgroup>
          <optgroup label="🤗 Hugging Face Serverless Hub (110+ Models)">
            <option value="hf/meta-llama/Llama-3.3-70B-Instruct">HF Llama 3.3 70B Instruct</option>
            <option value="hf/Qwen/Qwen2.5-Coder-32B-Instruct">HF Qwen 2.5 Coder 32B</option>
            <option value="hf/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B">HF DeepSeek R1 Distill 32B</option>
          </optgroup>
          <optgroup label="🇺🇸 Anthropic Frontier Flagships">
            <option value="anthropic/claude-3.7-sonnet">Claude 3.7 Sonnet (Hybrid Thinking / SOTA)</option>
            <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
            <option value="anthropic/claude-3.5-haiku">Claude 3.5 Haiku</option>
          </optgroup>
          <optgroup label="🇺🇸 Google DeepMind Frontier">
            <option value="google/gemini-2.5-pro">Gemini 2.5 Pro (Frontier Multimodal 2M)</option>
            <option value="google/gemini-2.5-flash">Gemini 2.5 Flash (&lt;300ms SLA)</option>
            <option value="google/gemini-2.0-flash-001">Gemini 2.0 Flash</option>
          </optgroup>
          <optgroup label="🇺🇸 OpenAI Frontier">
            <option value="openai/o3-mini">OpenAI o3-mini (High-Speed Reasoning)</option>
            <option value="openai/gpt-4o">OpenAI GPT-4o (Omni)</option>
          </optgroup>
          <optgroup label="🇺🇸 Meta AI Frontier">
            <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B Instruct</option>
            <option value="meta-llama/llama-3.1-405b-instruct">Llama 3.1 405B Frontier</option>
          </optgroup>
          <optgroup label="⚡ Unlimited Free Frontier Models">
            <option value="nvidia/nemotron-3.5-lightning:free">NVIDIA Nemotron 3.5 Lightning (Free)</option>
            <option value="cohere/north-mini-code:free">Cohere North Mini Code (Free)</option>
            <option value="liquid/lfm-2.5-2.6b:free">Liquid LFM 2.5 (Free)</option>
            <option value="baidu/ernie-5.5-flash-preview:free">Baidu ERNIE 5.5 Flash (Free)</option>
          </optgroup>
        </select>"""
    text = text[:pos_start] + new_select_inner + text[pos_end + len(old_select_end):]
    print("2. Updated HTML #ailabModelSelect with all 18 optgroups")
else:
    print("2. HTML #ailabModelSelect not found")

# 3. Update window.ailabSelectModelFromCatalog to dynamically create option if missing
target_select_fn = """  window.ailabSelectModelFromCatalog = function(modelId) {
    const select = $id("ailabModelSelect");
    if (select) {
      select.value = modelId;
      ailabChangeModel(modelId);
    }
    ailabCloseModelCatalogModal();
  };"""

replacement_select_fn = """  window.ailabSelectModelFromCatalog = function(modelId) {
    const select = $id("ailabModelSelect");
    if (select) {
      let opt = Array.from(select.options).find(o => o.value === modelId);
      if (!opt) {
        const prov = ailabResolveModelProvenance(modelId);
        opt = document.createElement("option");
        opt.value = modelId;
        opt.textContent = `${prov.flag} ${prov.clean_name || modelId} (${prov.lab_name})`;
        select.appendChild(opt);
      }
      select.value = modelId;
      ailabChangeModel(modelId);
    }
    ailabCloseModelCatalogModal();
  };"""

if target_select_fn in text:
    text = text.replace(target_select_fn, replacement_select_fn)
    print("3. Updated window.ailabSelectModelFromCatalog to ensure option is always appended to dropdown")
else:
    print("3. target_select_fn not found")

with open("app/ui/global_ai_lab_view.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved app/ui/global_ai_lab_view.py")
