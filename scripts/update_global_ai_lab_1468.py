import re

with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Docstring
content = content.replace(
    "- 432+ OpenRouter Live Models + 32 Global Foundational Labs",
    "- 1,468+ Unified Frontier Models (OpenRouter, AI/ML API, Hugging Face, Fal.ai, Replicate, Groq)"
)

# 2. Topbar badge
content = content.replace(
    '<span id="ailabConnText">432+ Models Live</span>',
    '<span id="ailabConnText">1,468+ Models Unified Mesh</span>'
)

# 3. Browse button in topbar
content = re.sub(
    r'<button type="button" class="ailab-browse-btn" onclick="ailabOpenModelCatalogModal\(\)" title="Search &amp; Filter 432\+ Models across 35\+ Global Labs">\s*<span>🔍 432\+ Models</span>\s*</button>',
    '''<button type="button" class="ailab-browse-btn" onclick="ailabOpenModelCatalogModal()" title="Search &amp; Filter 1,468+ Models across OpenRouter, AI/ML API, Hugging Face, Fal.ai, Replicate &amp; Groq">
        <span>🔍 1,468+ Models</span>
      </button>''',
    content
)

# 4. Empty hero state
content = content.replace(
    "<p>World Foundational AI Creators • 32+ Global Labs • 432+ Live Frontier Models • Sub-5ms Mathematical Dispatch</p>",
    "<p>World Foundational AI Creators • 1,468+ Unified Models • OpenRouter, AI/ML API, Hugging Face, Fal.ai, Replicate &amp; Groq • Pareto Engine</p>"
)

# 5. Modal subtitle
content = content.replace(
    '<p style="margin:0;font-size:11.5px;color:#94A3B8;">432+ Live Frontier Models across 35+ Global Foundational Labs</p>',
    '<p style="margin:0;font-size:11.5px;color:#94A3B8;">1,468+ Unified Models across OpenRouter (473), AI/ML API (995), Hugging Face (110+), Fal.ai, Replicate &amp; Groq</p>'
)

# 6. Modal search placeholder
content = content.replace(
    'placeholder="Search by model name, lab, country, or capability (e.g. claude, deepseek, qwen, free)..."',
    'placeholder="Search 1,468+ models by name, lab, provider, or capability (e.g. claude, deepseek, flux, qwen, free)..."'
)

# 7. Modal pills
old_pills = '''    <div class="ailab-modal-pills">
      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Models (432+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('free', this)">⚡ Free Tier</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('us', this)">🇺🇸 USA (12 Labs)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('cn', this)">🇨🇳 China (11 Labs)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('eu', this)">🇫🇷 Europe (3 Labs)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('in', this)">🇮🇳 India (2 Labs)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('reasoning', this)">🧠 Reasoning SOTA</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('code', this)">💻 Code Specialists</button>
    </div>'''

new_pills = '''    <div class="ailab-modal-pills">
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

content = content.replace(old_pills, new_pills)

# 8. Add Directory Providers to ailabResolveModelProvenance
old_dir_end = '''      "aleph-alpha": { lab_name: "Aleph Alpha (Luminous)", country: "Germany", flag: "🇩🇪", tier: "European Explainable AI" }
    };'''

new_dir_end = '''      "aleph-alpha": { lab_name: "Aleph Alpha (Luminous)", country: "Germany", flag: "🇩🇪", tier: "European Explainable AI" },
      "hf": { lab_name: "Hugging Face", country: "Global Open Source", flag: "🤗", tier: "Open-Weights Hub & MCP" },
      "huggingface": { lab_name: "Hugging Face", country: "Global Open Source", flag: "🤗", tier: "Open-Weights Hub & MCP" },
      "aimlapi": { lab_name: "AI/ML API", country: "Global Unified Aggregator", flag: "⚡", tier: "Unified 995+ Model Fabric" },
      "fal": { lab_name: "fal.ai", country: "United States", flag: "🎨", tier: "Diffusion & Generative Media" },
      "fal-ai": { lab_name: "fal.ai", country: "United States", flag: "🎨", tier: "Diffusion & Generative Media" },
      "replicate": { lab_name: "Replicate", country: "United States", flag: "🚀", tier: "Containerized Open Models" },
      "black-forest-labs": { lab_name: "Black Forest Labs (FLUX)", country: "Germany", flag: "🇩🇪", tier: "Generative Visual SOTA" }
    };'''

content = content.replace(old_dir_end, new_dir_end)

# 9. Dynamic population comment & live count update
content = content.replace(
    "// DYNAMIC POPULATION OF ALL 433+ WORLD MODELS",
    "// DYNAMIC POPULATION OF ALL 1,468+ MESH MODELS"
)

old_badge_update = '''      const badge = $id("ailabConnText");
      if (badge) {
        badge.textContent = `${data.total_models || 433}+ Models Live`;
      }'''

new_badge_update = '''      const badge = $id("ailabConnText");
      if (badge) {
        badge.textContent = `${data.total_models || 1468}+ Models Unified Mesh`;
      }
      if (data.models && data.models.length > 0) {
        cachedCatalogModels = data.models;
      }'''

content = content.replace(old_badge_update, new_badge_update)

# 10. Generating bubble
content = content.replace(
    'Generating intelligent response across 432+ frontier models...',
    'Generating intelligent response across 1,468+ frontier models...'
)

# 11. Seed models and filtering in ailabRenderModelCatalog
old_seed = '''        // Fallback seed models
        models = [
          { id: "auto", name: "Single AUTO Mathematical Engine", lab: "NanoPro Router", country: "Global Sovereign Mesh", flag: "⚡", is_free: false },
          { id: "anthropic/claude-3.7-sonnet", name: "Claude 3.7 Sonnet (Hybrid Thinking)", lab: "Anthropic", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "anthropic/claude-3.5-sonnet", name: "Claude 3.5 Sonnet", lab: "Anthropic", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "google/gemini-2.5-pro", name: "Gemini 2.5 Pro (Frontier 2M)", lab: "Google DeepMind", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "google/gemini-2.5-flash", name: "Gemini 2.5 Flash (<300ms SLA)", lab: "Google DeepMind", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "deepseek/deepseek-r1", name: "DeepSeek R1 (Open Reasoning SOTA)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", is_free: false },
          { id: "deepseek/deepseek-chat", name: "DeepSeek V3 (General Flagship)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", is_free: false },
          { id: "qwen/qwen-2.5-coder-32b-instruct", name: "Qwen 2.5 Coder 32B", lab: "Alibaba Cloud", country: "China", flag: "🇨🇳", is_free: false },
          { id: "openai/o3-mini", name: "OpenAI o3-mini (Reasoning)", lab: "OpenAI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "openai/gpt-4o", name: "GPT-4o (Omni)", lab: "OpenAI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "mistralai/mistral-large-2411", name: "Mistral Large 2411", lab: "Mistral AI", country: "France", flag: "🇫🇷", is_free: false },
          { id: "meta-llama/llama-3.3-70b-instruct", name: "Llama 3.3 70B Instruct", lab: "Meta AI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "sarvam/sarvam-2b", name: "Sarvam 2B Indic", lab: "Sarvam AI", country: "India", flag: "🇮🇳", is_free: false },
          { id: "nvidia/nemotron-3.5-lightning:free", name: "NVIDIA Nemotron 3.5 Lightning", lab: "NVIDIA AI", country: "United States", flag: "🇺🇸", is_free: true },
          { id: "cohere/north-mini-code:free", name: "Cohere North Mini Code", lab: "Cohere", country: "Canada", flag: "🇨🇦", is_free: true },
          { id: "baidu/ernie-5.5-flash-preview:free", name: "Baidu ERNIE 5.5 Flash", lab: "Baidu", country: "China", flag: "🇨🇳", is_free: true }
        ];'''

new_seed = '''        // Fallback seed models across Unified 1,468+ Mesh
        models = [
          { id: "auto", name: "Single AUTO Mathematical Engine", lab: "NanoPro Router", country: "Global Sovereign Mesh", flag: "⚡", is_free: false },
          // OpenRouter Flagships
          { id: "anthropic/claude-3.7-sonnet", name: "Claude 3.7 Sonnet (Hybrid Thinking)", lab: "Anthropic", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "anthropic/claude-3.5-sonnet", name: "Claude 3.5 Sonnet", lab: "Anthropic", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "google/gemini-2.5-pro", name: "Gemini 2.5 Pro (Frontier 2M)", lab: "Google DeepMind", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "google/gemini-2.5-flash", name: "Gemini 2.5 Flash (<300ms SLA)", lab: "Google DeepMind", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "deepseek/deepseek-r1", name: "DeepSeek R1 (Open Reasoning SOTA)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", is_free: false },
          { id: "deepseek/deepseek-chat", name: "DeepSeek V3 (General Flagship)", lab: "DeepSeek AI", country: "China", flag: "🇨🇳", is_free: false },
          { id: "qwen/qwen-2.5-coder-32b-instruct", name: "Qwen 2.5 Coder 32B (Coding SOTA)", lab: "Alibaba Cloud", country: "China", flag: "🇨🇳", is_free: false },
          { id: "openai/o3-mini", name: "OpenAI o3-mini (High-Speed Reasoning)", lab: "OpenAI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "openai/gpt-4o", name: "GPT-4o (Omni Multimodal)", lab: "OpenAI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "meta-llama/llama-3.3-70b-instruct", name: "Llama 3.3 70B Instruct", lab: "Meta AI", country: "United States", flag: "🇺🇸", is_free: false },
          { id: "mistralai/mistral-large-2411", name: "Mistral Large 2411", lab: "Mistral AI", country: "France", flag: "🇫🇷", is_free: false },
          // Groq LPUs
          { id: "groq/qwen3.8-27b", name: "Qwen 3.8 27B (LPU Sub-300ms)", lab: "Groq LPU", country: "United States", flag: "⚡", is_free: true },
          { id: "groq/gpt-oss-120b", name: "GPT OSS 120B High-Throughput", lab: "Groq LPU", country: "United States", flag: "⚡", is_free: true },
          // Hugging Face Open-Weights
          { id: "hf:meta-llama/Llama-3.3-70B-Instruct", name: "Hugging Face Llama 3.3 70B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          { id: "hf:Qwen/Qwen2.5-Coder-32B-Instruct", name: "Hugging Face Qwen Coder 32B", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          { id: "hf:deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", name: "Hugging Face DeepSeek R1 Distill", lab: "Hugging Face Hub", country: "Global Open Source", flag: "🤗", is_free: true },
          // AI/ML API (995+ Models Fabric)
          { id: "aimlapi:anthropic/claude-3-7-sonnet", name: "AI/ML API Claude 3.7 Sonnet", lab: "AI/ML API Fabric", country: "Global Unified Aggregator", flag: "⚡", is_free: false },
          { id: "aimlapi:deepseek/deepseek-r1", name: "AI/ML API DeepSeek R1", lab: "AI/ML API Fabric", country: "Global Unified Aggregator", flag: "⚡", is_free: false },
          { id: "aimlapi:openai/o3-mini", name: "AI/ML API OpenAI o3-mini", lab: "AI/ML API Fabric", country: "Global Unified Aggregator", flag: "⚡", is_free: false },
          // Fal.ai & Replicate Generative Media
          { id: "fal:fal-ai/flux-schnell", name: "FLUX.1 Schnell Ultra Fast", lab: "fal.ai Generative", country: "United States", flag: "🎨", is_free: false },
          { id: "fal:fal-ai/flux-pro/v1.1", name: "FLUX.1 Pro v1.1 Photoreal", lab: "fal.ai Generative", country: "United States", flag: "🎨", is_free: false },
          { id: "replicate:black-forest-labs/flux-schnell", name: "Replicate FLUX Schnell", lab: "Replicate Cloud", country: "United States", flag: "🚀", is_free: false },
          // Free Tier
          { id: "nvidia/nemotron-3.5-lightning:free", name: "NVIDIA Nemotron 3.5 Lightning", lab: "NVIDIA AI", country: "United States", flag: "🇺🇸", is_free: true },
          { id: "cohere/north-mini-code:free", name: "Cohere North Mini Code", lab: "Cohere", country: "Canada", flag: "🇨🇦", is_free: true },
          { id: "liquid/lfm-2.5-2.6b:free", name: "Liquid LFM 2.5", lab: "Liquid AI", country: "United States", flag: "🇺🇸", is_free: true },
          { id: "baidu/ernie-5.5-flash-preview:free", name: "Baidu ERNIE 5.5 Flash", lab: "Baidu", country: "China", flag: "🇨🇳", is_free: true }
        ];'''

content = content.replace(old_seed, new_seed)

# 12. Filter categories in ailabRenderModelCatalog
old_filters = '''        if (currentCatalogCategory === "free" && !isFree) return false;
        if (currentCatalogCategory === "us" && prov.country !== "United States") return false;
        if (currentCatalogCategory === "cn" && prov.country !== "China") return false;
        if (currentCatalogCategory === "eu" && !["France", "Germany", "Europe"].includes(prov.country)) return false;
        if (currentCatalogCategory === "in" && prov.country !== "India") return false;
        if (currentCatalogCategory === "reasoning" && !(mName.includes("R1") || mName.includes("o3") || mName.includes("Thinking"))) return false;
        if (currentCatalogCategory === "code" && !(mName.toLowerCase().includes("code") || mName.toLowerCase().includes("coder"))) return false;'''

new_filters = '''        if (currentCatalogCategory === "openrouter" && (m.id.startsWith("hf:") || m.id.startsWith("aimlapi:") || m.id.startsWith("fal:") || m.id.startsWith("replicate:") || m.id.startsWith("groq/"))) return false;
        if (currentCatalogCategory === "aimlapi" && !m.id.startsWith("aimlapi:") && m.provider !== "aimlapi") return false;
        if (currentCatalogCategory === "hf" && !m.id.startsWith("hf:") && !m.id.startsWith("huggingface/") && !(m.lab && m.lab.includes("Hugging Face"))) return false;
        if (currentCatalogCategory === "fal_replicate" && !m.id.startsWith("fal:") && !m.id.startsWith("replicate:") && !m.id.includes("flux")) return false;
        if (currentCatalogCategory === "groq" && !m.id.startsWith("groq/") && !(m.lab && m.lab.includes("Groq"))) return false;
        if (currentCatalogCategory === "free" && !isFree) return false;
        if (currentCatalogCategory === "reasoning" && !(mName.includes("R1") || mName.includes("o3") || mName.includes("Thinking") || mName.includes("Reasoning"))) return false;
        if (currentCatalogCategory === "code" && !(mName.toLowerCase().includes("code") || mName.toLowerCase().includes("coder"))) return false;'''

content = content.replace(old_filters, new_filters)

with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app/ui/global_ai_lab_view.py successfully!")
