import sys

with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update text occurrences of 2,150+
text = text.replace("2,150+ Models Unified Mesh", "4,330+ Models Unified Mesh")
text = text.replace("2,150+ Models", "4,330+ Models")
text = text.replace("2,150+ models", "4,330+ models")
text = text.replace("2,150+ Unified Models", "4,330+ Unified Models")
text = text.replace("across 2,150+ frontier models", "across 4,330+ frontier models")
text = text.replace("Search &amp; Filter 2,150+ Models across OpenRouter, AI/ML API, Hugging Face, Fal.ai, Replicate &amp; Groq",
                    "Search &amp; Filter 4,330+ Models across 19 Unified Providers")
text = text.replace("World Foundational AI Creators • 2,150+ Unified Models • OpenRouter, AI/ML API, Hugging Face, Fal.ai, Replicate &amp; Groq • Pareto Engine",
                    "World Foundational AI Creators • 4,330+ Unified Models • 19 Sovereign Frontier Providers • Pareto Engine")
text = text.replace("2,150+ Unified Models across OpenRouter (473), AI/ML API (995), Hugging Face (110+), Fal.ai, Replicate &amp; Groq",
                    "4,330+ Unified Models across Eden AI (1,311), AI/ML API (995), Requesty (750), OpenRouter (473), Cloudflare (150+), DeepInfra (177), Hugging Face (110+), Novita (99), NVIDIA (83), SambaNova &amp; Groq")
text = text.replace("Search 2,150+ models by name, lab, provider, or capability (e.g. claude, deepseek, flux, qwen, free)...",
                    "Search 4,330+ models by name, lab, provider, or capability (e.g. claude, deepseek, eden, sambanova, flux, qwen, free)...")

# 2. Update ailab-modal-pills
old_pills = """    <div class="ailab-modal-pills">
      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Mesh (2,150+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('cf_ai', this)">☁️ Cloudflare Workers AI (150+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('novita', this)">🚀 Novita AI (99)</button>
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
    </div>"""

new_pills = """    <div class="ailab-modal-pills">
      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Mesh (4,330+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('edenai', this)">🌿 Eden AI (1,311)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('requesty', this)">🌐 Requesty AI (750)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('cf_ai', this)">☁️ Cloudflare Workers AI (150+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('novita', this)">🚀 Novita AI (99)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('nvidia', this)">🟢 NVIDIA NIM (83)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('sambanova', this)">⚡ SambaNova (RDU)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('openrouter', this)">⚡ OpenRouter (473)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('aimlapi', this)">🚀 AI/ML API (995)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('deepinfra', this)">🧠 DeepInfra (177)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('mistral', this)">🇫🇷 Mistral Direct (56)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('hf', this)">🤗 Hugging Face (110+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('groq', this)">⚡ Groq LPUs (11)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('friendli_thesean', this)">🚀 Friendli &amp; TheSean</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('deepseek', this)">🇨🇳 DeepSeek Direct</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('fal_replicate', this)">🎨 Fal.ai &amp; Replicate</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('free', this)">🆓 Free Tier</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('reasoning', this)">🧠 Reasoning SOTA</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('code', this)">💻 Code Specialists</button>
    </div>"""

if old_pills in text:
    text = text.replace(old_pills, new_pills)
    print("Updated ailab-modal-pills")
else:
    print("old_pills not matched")

# 3. Add new labs to window.ailabResolveModelProvenance DIRECTORY
target_prov = '      "black-forest-labs": { lab_name: "Black Forest Labs (FLUX)", country: "Germany", flag: "🇩🇪", tier: "Generative Visual SOTA" }\n    };'

replacement_prov = """      "black-forest-labs": { lab_name: "Black Forest Labs (FLUX)", country: "Germany", flag: "🇩🇪", tier: "Generative Visual SOTA" },
      "novita": { lab_name: "Novita AI Sovereign", country: "United States", flag: "⚡", tier: "99+ Multi-Modal & LLMs" },
      "cf": { lab_name: "Cloudflare Workers AI", country: "Global Edge Network", flag: "☁️", tier: "Zero-Latency Edge Inference" },
      "@cf": { lab_name: "Cloudflare Workers AI", country: "Global Edge Network", flag: "☁️", tier: "Zero-Latency Edge Inference" },
      "sambanova": { lab_name: "SambaNova Systems", country: "United States", flag: "⚡", tier: "SN40L Reconfigurable Dataflow (RDU)" },
      "requesty": { lab_name: "Requesty AI", country: "Global Router", flag: "🌐", tier: "750+ Global Unified Models" },
      "nvidia": { lab_name: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "83+ TensorRT-LLM Microservices" },
      "edenai": { lab_name: "Eden AI", country: "France / Europe", flag: "🌿", tier: "1,311+ Global Multimodal Catalog" },
      "friendli": { lab_name: "FriendliAI", country: "South Korea / Global", flag: "🚀", tier: "PeriFlow High-Throughput Engine" },
      "thesean": { lab_name: "TheSean AI", country: "Global", flag: "⚡", tier: "Ultra-Low Latency Inference" },
      "baseten": { lab_name: "Baseten", country: "United States", flag: "🏗️", tier: "Truss Dedicated Inference" }
    };"""

if target_prov in text:
    text = text.replace(target_prov, replacement_prov)
    print("Updated window.ailabResolveModelProvenance DIRECTORY")
else:
    print("target_prov not matched")

# 4. Add seed models and category filtering in ailabRenderModelCatalog()
target_seed_end = """          // Free Tier
          { id: "nvidia/nemotron-3.5-lightning:free", name: "NVIDIA Nemotron 3.5 Lightning", lab: "NVIDIA AI", country: "United States", flag: "🇺🇸", is_free: true },
          { id: "cohere/north-mini-code:free", name: "Cohere North Mini Code", lab: "Cohere", country: "Canada", flag: "🇨🇦", is_free: true },
          { id: "baidu/ernie-5.5-flash-preview:free", name: "Baidu ERNIE 5.5 Flash", lab: "Baidu", country: "China", flag: "🇨🇳", is_free: true }
        ];"""

replacement_seed_end = """          // Free Tier
          { id: "nvidia/nemotron-3.5-lightning:free", name: "NVIDIA Nemotron 3.5 Lightning", lab: "NVIDIA AI", country: "United States", flag: "🇺🇸", is_free: true },
          { id: "cohere/north-mini-code:free", name: "Cohere North Mini Code", lab: "Cohere", country: "Canada", flag: "🇨🇦", is_free: true },
          { id: "baidu/ernie-5.5-flash-preview:free", name: "Baidu ERNIE 5.5 Flash", lab: "Baidu", country: "China", flag: "🇨🇳", is_free: true },
          // SambaNova Systems (Fast SN40L RDUs)
          { id: "sambanova/Meta-Llama-3.3-70B-Instruct", name: "SambaNova Llama 3.3 70B (Fast RDU)", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          { id: "sambanova/GLM-5.3", name: "SambaNova GLM-5.3 Flagship", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          { id: "sambanova/MiniMax-M3.1-Flash", name: "SambaNova MiniMax M3.1 Flash", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          { id: "sambanova/gemma-4-31B-it", name: "SambaNova Gemma 4 31B", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          { id: "sambanova/gpt-oss-120b", name: "SambaNova GPT OSS 120B", lab: "SambaNova Systems", country: "United States", flag: "⚡", is_free: true },
          // NVIDIA NIM (83 Models)
          { id: "nvidia/llama-3.1-nemotron-70b-instruct", name: "NVIDIA Llama 3.1 Nemotron 70B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          { id: "nvidia/nemotron-4-340b-instruct", name: "NVIDIA Nemotron 4 340B Flagship", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          { id: "nvidia/mistralai/codestral-22b-instruct-v0.1", name: "NVIDIA Codestral 22B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          { id: "nvidia/deepseek-ai/deepseek-v4.1-flash", name: "NVIDIA DeepSeek V4.1 Flash", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          { id: "nvidia/bigcode/starcoder2-15b", name: "NVIDIA StarCoder2 15B", lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", is_free: false },
          // Requesty AI (750 Models)
          { id: "requesty/anthropic/claude-fable-5.2", name: "Requesty Claude Fable 5.2", lab: "Requesty AI", country: "Global Router", flag: "🌐", is_free: false },
          { id: "requesty/google/gemini-4-hydrogen", name: "Requesty Gemini 4 Hydrogen", lab: "Requesty AI", country: "Global Router", flag: "🌐", is_free: false },
          { id: "requesty/openai/gpt-6.1-terra:flex", name: "Requesty GPT 6.1 Terra", lab: "Requesty AI", country: "Global Router", flag: "🌐", is_free: false },
          { id: "requesty/deepseek/deepseek-chat", name: "Requesty DeepSeek V3", lab: "Requesty AI", country: "Global Router", flag: "🌐", is_free: false },
          // Eden AI (1,311 Models)
          { id: "edenai/openai/gpt-4o", name: "Eden AI OpenAI GPT-4o", lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "Multimodal Flagship", is_free: false },
          { id: "edenai/anthropic/claude-3-5-sonnet", name: "Eden AI Claude 3.5 Sonnet", lab: "Eden AI", country: "France / Europe", flag: "🌿", is_free: false },
          { id: "edenai/google/gemini-1.5-pro", name: "Eden AI Google Gemini 1.5 Pro", lab: "Eden AI", country: "France / Europe", flag: "🌿", is_free: false },
          { id: "edenai/mistral/mistral-large-latest", name: "Eden AI Mistral Large 2", lab: "Eden AI", country: "France / Europe", flag: "🌿", is_free: false },
          { id: "edenai/deepseek/deepseek-r1", name: "Eden AI DeepSeek R1", lab: "Eden AI", country: "France / Europe", flag: "🌿", is_free: false },
          // FriendliAI, TheSean & Baseten
          { id: "friendli/meta-llama-3.1-8b-instruct", name: "FriendliAI Llama 3.1 8B (PeriFlow)", lab: "FriendliAI", country: "South Korea / Global", flag: "🚀", is_free: true },
          { id: "thesean/ship-like/claude-haiku-4-5", name: "TheSean Claude Haiku 4.5", lab: "TheSean AI", country: "Global", flag: "⚡", is_free: false },
          { id: "baseten/deepseek-ai/DeepSeek-V4.1-Flash", name: "Baseten DeepSeek V4.1 Flash", lab: "Baseten", country: "United States", flag: "🏗️", is_free: false }
        ];"""

if target_seed_end in text:
    text = text.replace(target_seed_end, replacement_seed_end)
    print("Updated fallback seed models in ailabRenderModelCatalog")
else:
    print("target_seed_end not matched")

# 5. Update category filters in ailabRenderModelCatalog
old_filters = """        if (currentCatalogCategory === "cf_ai" && !m.id.startsWith("@cf/") && !m.id.startsWith("cf/") && !(m.lab && m.lab.includes("Cloudflare"))) return false;
        if (currentCatalogCategory === "novita" && !m.id.startsWith("novita/") && !(m.lab && m.lab.includes("Novita"))) return false;
        if (currentCatalogCategory === "openrouter" && (m.id.startsWith("hf/") || m.id.startsWith("aimlapi/") || m.id.startsWith("fal/") || m.id.startsWith("replicate/") || m.id.startsWith("groq/") || m.id.startsWith("deepinfra/") || m.id.startsWith("mistral/") || m.id.startsWith("novita/") || m.id.startsWith("@cf/"))) return false;"""

new_filters = """        if (currentCatalogCategory === "edenai" && !m.id.startsWith("edenai/") && !(m.lab && m.lab.includes("Eden"))) return false;
        if (currentCatalogCategory === "requesty" && !m.id.startsWith("requesty/") && !(m.lab && m.lab.includes("Requesty"))) return false;
        if (currentCatalogCategory === "cf_ai" && !m.id.startsWith("@cf/") && !m.id.startsWith("cf/") && !(m.lab && m.lab.includes("Cloudflare"))) return false;
        if (currentCatalogCategory === "novita" && !m.id.startsWith("novita/") && !(m.lab && m.lab.includes("Novita"))) return false;
        if (currentCatalogCategory === "nvidia" && !m.id.startsWith("nvidia/") && !(m.lab && m.lab.includes("NVIDIA"))) return false;
        if (currentCatalogCategory === "sambanova" && !m.id.startsWith("sambanova/") && !(m.lab && m.lab.includes("SambaNova"))) return false;
        if (currentCatalogCategory === "friendli_thesean" && !m.id.startsWith("friendli/") && !m.id.startsWith("thesean/") && !m.id.startsWith("baseten/")) return false;
        if (currentCatalogCategory === "openrouter" && (m.id.startsWith("hf/") || m.id.startsWith("aimlapi/") || m.id.startsWith("fal/") || m.id.startsWith("replicate/") || m.id.startsWith("groq/") || m.id.startsWith("deepinfra/") || m.id.startsWith("mistral/") || m.id.startsWith("novita/") || m.id.startsWith("@cf/") || m.id.startsWith("edenai/") || m.id.startsWith("requesty/") || m.id.startsWith("nvidia/") || m.id.startsWith("sambanova/") || m.id.startsWith("friendli/") || m.id.startsWith("thesean/") || m.id.startsWith("baseten/"))) return false;"""

if old_filters in text:
    text = text.replace(old_filters, new_filters)
    print("Updated category filters in ailabRenderModelCatalog")
else:
    print("old_filters not matched")

with open("app/ui/global_ai_lab_view.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved app/ui/global_ai_lab_view.py successfully")
