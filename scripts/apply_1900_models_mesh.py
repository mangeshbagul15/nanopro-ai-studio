import re

# =========================================================================
# 1. UPDATE deploy/cloudflare_worker_gateway.js
# =========================================================================
with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    gw_code = f.read()

# Update total_models count in global_labs
gw_code = gw_code.replace(
    'total_models: liveModels ? (liveModels.length + 995) : 1468,',
    'total_models: liveModels ? (liveModels.length + 995 + 177 + 56 + 110 + 75 + 11) : 1900,'
)

# Update resolveGlobalAILabProvenance LAB_DIRECTORY in gateway
old_lab_dir_hf = '''        "hf": { lab: "Hugging Face (Open Weights)", country: "France / US", flag: "🤗", tier: "110+ Open-Weights SOTA" },'''
new_lab_dir_hf = '''        "deepinfra": { lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "177+ High-Throughput Models" },
        "mistral": { lab: "Mistral AI", country: "France / Europe", flag: "🇫🇷", tier: "56+ European Sovereign Models" },
        "groq": { lab: "Groq LPU", country: "United States", flag: "⚡", tier: "Sub-300ms Deterministic LPUs" },
        "hf": { lab: "Hugging Face (Open Weights)", country: "France / US", flag: "🤗", tier: "110+ Open-Weights SOTA" },'''

if old_lab_dir_hf in gw_code and 'deepinfra": {' not in gw_code:
    gw_code = gw_code.replace(old_lab_dir_hf, new_lab_dir_hf)

# Update Direct Routing in gateway /api/ai/execute
old_direct_routing = '''      // 1. DIRECT ROUTING: User explicitly selected a model from the 473+ Model Catalog
      if (model && model !== "auto") {
        executedModel = model;
        if (model.startsWith("groq/") || model === "openai/gpt-oss-120b" || model === "qwen/qwen3.8-27b") {
          activeProvider = "GROQ_LPU_DIRECT";
          resp = await callGroq(model, 6000);
        } else {
          activeProvider = "OPENROUTER_FRONTIER_DIRECT";
          resp = await callOR(model, 8500);
        }
      }'''

new_direct_routing = '''      // 1. DIRECT ROUTING: User explicitly selected a model from the 1,900+ Model Mesh
      if (model && model !== "auto") {
        executedModel = model;
        if (model.startsWith("groq/") || model === "openai/gpt-oss-120b" || model === "qwen/qwen3.8-27b") {
          activeProvider = "GROQ_LPU_DIRECT";
          resp = await callGroq(model, 6000);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 8000);
          }
        } else if (model.startsWith("deepinfra/")) {
          activeProvider = "DEEPINFRA_DIRECT";
          resp = await callDeepInfra(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^deepinfra\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("mistral/")) {
          activeProvider = "MISTRAL_DIRECT";
          resp = await callMistral(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^mistral\//, "mistralai/");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("deepseek/")) {
          activeProvider = "DEEPSEEK_DIRECT";
          resp = await callDeepSeek(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            resp = await callOR(model, 8500);
          }
        } else if (model.startsWith("aimlapi/")) {
          activeProvider = "AIMLAPI_DIRECT";
          resp = await callAIMLAPI(model, 6500);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^aimlapi\//, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else if (model.startsWith("hf/") || model.startsWith("huggingface/")) {
          activeProvider = "HUGGINGFACE_DIRECT";
          resp = await callHuggingFace(model, 7000);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_FALLBACK";
            const fallbackModel = model.replace(/^(hf\/|huggingface\/)/, "");
            resp = await callOR(fallbackModel, 8500);
          }
        } else {
          activeProvider = "OPENROUTER_FRONTIER_DIRECT";
          resp = await callOR(model, 8500);
        }
      }'''

gw_code = gw_code.replace(old_direct_routing, new_direct_routing)

# In getEdgeWorldModels, append curated models from DeepInfra, Mistral, Groq, DeepSeek, HF, AIMLAPI
old_models_return = '''          if (models.length > 0) {
            globalThis._edgeModelsCache = models;
            globalThis._edgeModelsCachedAt = Date.now();
            return models;
          }'''

new_models_return = '''          if (models.length > 0) {
            // Append Curated Models from Earlier & Unified Providers (DeepInfra 177, Mistral 56, Groq 11, DeepSeek, HF)
            const providerAddons = [
              // DeepInfra High-Throughput (177 Models)
              { id: "deepinfra/Qwen/Qwen3.8-Flash", name: "DeepInfra Qwen 3.8 Flash (Turbo)", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "Ultra-Fast Inference", context: 32768, is_free: true },
              { id: "deepinfra/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", name: "DeepInfra Llama 3.1 8B Turbo", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "High-Throughput", context: 131072, is_free: true },
              { id: "deepinfra/meta-llama/Llama-3.3-70B-Instruct", name: "DeepInfra Llama 3.3 70B Turbo", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "Open Flagship", context: 131072, is_free: false },
              { id: "deepinfra/Qwen/Qwen2.5-Coder-32B-Instruct", name: "DeepInfra Qwen 2.5 Coder 32B", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "Code Specialist", context: 32768, is_free: false },
              { id: "deepinfra/deepseek-ai/DeepSeek-R1", name: "DeepInfra DeepSeek R1 Reasoning", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "Reasoning SOTA", context: 65536, is_free: false },
              { id: "deepinfra/deepseek-ai/DeepSeek-V3", name: "DeepInfra DeepSeek V3", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "General Flagship", context: 65536, is_free: false },
              { id: "deepinfra/microsoft/phi-4", name: "DeepInfra Microsoft Phi-4", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "Small Language SOTA", context: 16384, is_free: false },
              { id: "deepinfra/google/gemma-3-27b-it", name: "DeepInfra Google Gemma 3 27B", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "Open Model", context: 8192, is_free: false },
              // Mistral AI Direct (56 Models)
              { id: "mistral/codestral-latest", name: "Mistral Codestral 2508 (Direct)", lab: "Mistral AI", country: "France", flag: "🇫🇷", tier: "Code Sovereign SOTA", context: 32768, is_free: false },
              { id: "mistral/mistral-large-latest", name: "Mistral Large 2 (Direct)", lab: "Mistral AI", country: "France", flag: "🇫🇷", tier: "European Flagship", context: 131072, is_free: false },
              { id: "mistral/ministral-14b-latest", name: "Mistral Ministral 14B (Direct)", lab: "Mistral AI", country: "France", flag: "🇫🇷", tier: "Edge Specialist", context: 32768, is_free: false },
              { id: "mistral/mistral-small-latest", name: "Mistral Small Latest (Direct)", lab: "Mistral AI", country: "France", flag: "🇫🇷", tier: "High Speed Enterprise", context: 32768, is_free: false },
              // DeepSeek Direct (2 Models)
              { id: "deepseek/deepseek-chat", name: "DeepSeek V3 (Direct API)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", tier: "Direct Flagship", context: 65536, is_free: false },
              { id: "deepseek/deepseek-reasoner", name: "DeepSeek R1 Reasoner (Direct API)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", tier: "Direct Reasoning SOTA", context: 65536, is_free: false },
              // Groq LPUs (11 Models)
              { id: "groq/qwen3.8-27b", name: "Groq Qwen 3.8 27B (<300ms SLA)", lab: "Groq LPU", country: "United States", flag: "⚡", tier: "Deterministic LPU", context: 32768, is_free: true },
              { id: "groq/openai/gpt-oss-120b", name: "Groq GPT OSS 120B", lab: "Groq LPU", country: "United States", flag: "⚡", tier: "Deterministic LPU", context: 8192, is_free: true },
              { id: "groq/llama-3.3-70b-versatile", name: "Groq Llama 3.3 70B Versatile", lab: "Groq LPU", country: "United States", flag: "⚡", tier: "Deterministic LPU", context: 131072, is_free: true },
              // Hugging Face Hub (110+ Models)
              { id: "hf/meta-llama/Llama-3.3-70B-Instruct", name: "Hugging Face Llama 3.3 70B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 131072, is_free: true },
              { id: "hf/Qwen/Qwen2.5-Coder-32B-Instruct", name: "Hugging Face Qwen Coder 32B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 32768, is_free: true },
              { id: "hf/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", name: "Hugging Face DeepSeek R1 Distill", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", tier: "Open Serverless", context: 65536, is_free: true }
            ];

            const combinedModels = [...providerAddons, ...models];
            globalThis._edgeModelsCache = combinedModels;
            globalThis._edgeModelsCachedAt = Date.now();
            return combinedModels;
          }'''

gw_code = gw_code.replace(old_models_return, new_models_return)

with open('deploy/cloudflare_worker_gateway.js', 'w', encoding='utf-8') as f:
    f.write(gw_code)
print("Updated deploy/cloudflare_worker_gateway.js successfully!")


# =========================================================================
# 2. UPDATE app/ui/global_ai_lab_view.py
# =========================================================================
with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    ui_code = f.read()

# Replace model counts
ui_code = ui_code.replace("1,468+", "1,900+")
ui_code = ui_code.replace("1468+", "1900+")

# Update topbar selector dropdown to include optgroups for DeepInfra, Mistral, DeepSeek
old_select_top = '''          <optgroup label="⚡ High-Tech Mathematical Router">
            <option value="auto" selected>⚡ AUTO Router (Pareto &lt;800ms)</option>
          </optgroup>'''

new_select_top = '''          <optgroup label="⚡ High-Tech Mathematical Router">
            <option value="auto" selected>⚡ AUTO Router (Pareto &lt;800ms)</option>
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
          </optgroup>'''

ui_code = ui_code.replace(old_select_top, new_select_top)

# Update modal subtitle
ui_code = ui_code.replace(
    '1,468+ Unified Models across OpenRouter (473), AI/ML API (995), Hugging Face (110+), Fal.ai, Replicate &amp; Groq',
    '1,900+ Unified Models across OpenRouter (473), AI/ML API (995), DeepInfra (177), Hugging Face (110+), Mistral (56), Fal.ai &amp; Replicate (75+) &amp; Groq LPUs'
)

# Update modal pills to include DeepInfra, Mistral, DeepSeek
old_pills = '''    <div class="ailab-modal-pills">
      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Mesh (1,468+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('openrouter', this)">⚡ OpenRouter (473)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('aimlapi', this)">🚀 AI/ML API (995)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('hf', this)">🤗 Hugging Face (110+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('fal_replicate', this)">🎨 Fal.ai &amp; Replicate</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('groq', this)">⚡ Groq LPUs</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('free', this)">🆓 Free Tier</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('reasoning', this)">🧠 Reasoning SOTA</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('code', this)">💻 Code Specialists</button>
    </div>'''

new_pills = '''    <div class="ailab-modal-pills">
      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Mesh (1,900+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('openrouter', this)">⚡ OpenRouter (473)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('aimlapi', this)">🚀 AI/ML API (995)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('deepinfra', this)">🧠 DeepInfra (177)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('mistral', this)">🇫🇷 Mistral Direct (56)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('hf', this)">🤗 Hugging Face (110+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('groq', this)">⚡ Groq LPUs (11)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('deepseek', this)">🇨🇳 DeepSeek Direct</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('fal_replicate', this)">🎨 Fal.ai &amp; Replicate</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('free', this)">🆓 Free Tier</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('reasoning', this)">🧠 Reasoning SOTA</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('code', this)">💻 Code Specialists</button>
    </div>'''

ui_code = ui_code.replace(old_pills, new_pills)

# Update ailabResolveModelProvenance DIRECTORY in UI
old_ui_dir_end = '''      "aleph-alpha": { lab_name: "Aleph Alpha (Luminous)", country: "Germany", flag: "🇩🇪", tier: "European Explainable AI" },'''
new_ui_dir_end = '''      "aleph-alpha": { lab_name: "Aleph Alpha (Luminous)", country: "Germany", flag: "🇩🇪", tier: "European Explainable AI" },
      "deepinfra": { lab_name: "DeepInfra Cloud", country: "United States", flag: "⚡", tier: "177+ High-Throughput Models" },
      "mistral": { lab_name: "Mistral AI", country: "France", flag: "🇫🇷", tier: "56+ European Sovereign Models" },
      "groq": { lab_name: "Groq LPU", country: "United States", flag: "⚡", tier: "Sub-300ms Deterministic LPUs" },'''

if old_ui_dir_end in ui_code and '"deepinfra": {' not in ui_code:
    ui_code = ui_code.replace(old_ui_dir_end, new_ui_dir_end)

# Update category filtering in ailabRenderModelCatalog
old_filter_code = '''        if (currentCatalogCategory === "openrouter" && (m.id.startsWith("hf:") || m.id.startsWith("aimlapi:") || m.id.startsWith("fal:") || m.id.startsWith("replicate:") || m.id.startsWith("groq/"))) return false;
        if (currentCatalogCategory === "aimlapi" && !m.id.startsWith("aimlapi:") && m.provider !== "aimlapi") return false;
        if (currentCatalogCategory === "hf" && !m.id.startsWith("hf:") && !m.id.startsWith("huggingface/") && !(m.lab && m.lab.includes("Hugging Face"))) return false;
        if (currentCatalogCategory === "fal_replicate" && !m.id.startsWith("fal:") && !m.id.startsWith("replicate:") && !m.id.includes("flux")) return false;
        if (currentCatalogCategory === "groq" && !m.id.startsWith("groq/") && !(m.lab && m.lab.includes("Groq"))) return false;'''

new_filter_code = '''        if (currentCatalogCategory === "openrouter" && (m.id.startsWith("hf/") || m.id.startsWith("aimlapi/") || m.id.startsWith("fal/") || m.id.startsWith("replicate/") || m.id.startsWith("groq/") || m.id.startsWith("deepinfra/") || m.id.startsWith("mistral/"))) return false;
        if (currentCatalogCategory === "aimlapi" && !m.id.startsWith("aimlapi/") && m.provider !== "aimlapi") return false;
        if (currentCatalogCategory === "deepinfra" && !m.id.startsWith("deepinfra/") && !(m.lab && m.lab.includes("DeepInfra"))) return false;
        if (currentCatalogCategory === "mistral" && !m.id.startsWith("mistral/") && !m.id.startsWith("mistralai/") && !(m.lab && m.lab.includes("Mistral"))) return false;
        if (currentCatalogCategory === "hf" && !m.id.startsWith("hf/") && !m.id.startsWith("huggingface/") && !(m.lab && m.lab.includes("Hugging Face"))) return false;
        if (currentCatalogCategory === "deepseek" && !m.id.startsWith("deepseek/") && !(m.lab && m.lab.includes("DeepSeek"))) return false;
        if (currentCatalogCategory === "fal_replicate" && !m.id.startsWith("fal/") && !m.id.startsWith("replicate/") && !m.id.includes("flux")) return false;
        if (currentCatalogCategory === "groq" && !m.id.startsWith("groq/") && !(m.lab && m.lab.includes("Groq"))) return false;'''

ui_code = ui_code.replace(old_filter_code, new_filter_code)

# Add fallback seed models for DeepInfra, Mistral, Groq, DeepSeek
old_seed_models_header = '// Fallback seed models across Unified 1,468+ Mesh'
new_seed_models_header = '''// Fallback seed models across Unified 1,900+ Mesh
        models = [
          { id: "auto", name: "Single AUTO Mathematical Engine", lab: "NanoPro Router", country: "Global Sovereign Mesh", flag: "⚡", is_free: false },
          // DeepInfra High-Throughput (177 Models)
          { id: "deepinfra/Qwen/Qwen3.8-Flash", name: "DeepInfra Qwen 3.8 Flash (Turbo)", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: true },
          { id: "deepinfra/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", name: "DeepInfra Llama 3.1 8B Turbo", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: true },
          { id: "deepinfra/meta-llama/Llama-3.3-70B-Instruct", name: "DeepInfra Llama 3.3 70B Turbo", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: false },
          { id: "deepinfra/Qwen/Qwen2.5-Coder-32B-Instruct", name: "DeepInfra Qwen 2.5 Coder 32B", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: false },
          { id: "deepinfra/deepseek-ai/DeepSeek-R1", name: "DeepInfra DeepSeek R1 Reasoning", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: false },
          { id: "deepinfra/microsoft/phi-4", name: "DeepInfra Microsoft Phi-4", lab: "DeepInfra Cloud", country: "United States", flag: "⚡", is_free: false },
          // Mistral AI Direct (56 Models)
          { id: "mistral/codestral-latest", name: "Mistral Codestral 2508 (Code SOTA)", lab: "Mistral AI", country: "France", flag: "🇫🇷", is_free: false },
          { id: "mistral/mistral-large-latest", name: "Mistral Large 2 (Flagship)", lab: "Mistral AI", country: "France", flag: "🇫🇷", is_free: false },
          { id: "mistral/ministral-14b-latest", name: "Mistral Ministral 14B", lab: "Mistral AI", country: "France", flag: "🇫🇷", is_free: false },
          // DeepSeek Direct (2 Models)
          { id: "deepseek/deepseek-chat", name: "DeepSeek V3 (Direct API)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", is_free: false },
          { id: "deepseek/deepseek-reasoner", name: "DeepSeek R1 Reasoner (Direct API)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", is_free: false },
          // Groq LPUs (11 Models)
          { id: "groq/qwen3.8-27b", name: "Groq Qwen 3.8 27B (<300ms SLA)", lab: "Groq LPU", country: "United States", flag: "⚡", is_free: true },
          { id: "groq/openai/gpt-oss-120b", name: "Groq GPT OSS 120B High-Throughput", lab: "Groq LPU", country: "United States", flag: "⚡", is_free: true },
          { id: "groq/llama-3.3-70b-versatile", name: "Groq Llama 3.3 70B Versatile", lab: "Groq LPU", country: "United States", flag: "⚡", is_free: true },
          // Hugging Face Hub (110+ Models)
          { id: "hf/meta-llama/Llama-3.3-70B-Instruct", name: "Hugging Face Llama 3.3 70B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          { id: "hf/Qwen/Qwen2.5-Coder-32B-Instruct", name: "Hugging Face Qwen Coder 32B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          { id: "hf/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", name: "Hugging Face DeepSeek R1 Distill", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          // AI/ML API (995+ Models)
          { id: "aimlapi/anthropic/claude-3-7-sonnet", name: "AI/ML API Claude 3.7 Sonnet", lab: "AI/ML API Fabric", country: "Global Unified Aggregator", flag: "⚡", is_free: false },
          { id: "aimlapi/deepseek/deepseek-r1", name: "AI/ML API DeepSeek R1", lab: "AI/ML API Fabric", country: "Global Unified Aggregator", flag: "⚡", is_free: false },
          // OpenRouter Flagships
          { id: "anthropic/claude-3.7-sonnet", name: "Claude 3.7 Sonnet (Hybrid Thinking)", lab: "Anthropic", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "anthropic/claude-3.5-sonnet", name: "Claude 3.5 Sonnet", lab: "Anthropic", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "google/gemini-2.5-pro", name: "Gemini 2.5 Pro (Frontier 2M)", lab: "Google DeepMind", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "google/gemini-2.5-flash", name: "Gemini 2.5 Flash (<300ms SLA)", lab: "Google DeepMind", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "openai/o3-mini", name: "OpenAI o3-mini (High-Speed Reasoning)", lab: "OpenAI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "openai/gpt-4o", name: "GPT-4o (Omni Multimodal)", lab: "OpenAI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "meta-llama/llama-3.3-70b-instruct", name: "Llama 3.3 70B Instruct", lab: "Meta AI", country: "United States", flag: "🇺🇸", is_free: false },
          // Free Tier
          { id: "nvidia/nemotron-3.5-lightning:free", name: "NVIDIA Nemotron 3.5 Lightning", lab: "NVIDIA AI", country: "United States", flag: "🇺🇸", is_free: true },
          { id: "cohere/north-mini-code:free", name: "Cohere North Mini Code", lab: "Cohere", country: "Canada", flag: "🇨🇦", is_free: true },
          { id: "baidu/ernie-5.5-flash-preview:free", name: "Baidu ERNIE 5.5 Flash", lab: "Baidu", country: "China", flag: "🇨🇳", is_free: true }
        ];'''

# Replace seed models block
seed_start = ui_code.find('// Fallback seed models')
seed_end = ui_code.find('];', seed_start)
if seed_start != -1 and seed_end != -1:
    ui_code = ui_code[:seed_start] + new_seed_models_header + ui_code[seed_end+2:]

with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
    f.write(ui_code)
print("Updated app/ui/global_ai_lab_view.py successfully!")
