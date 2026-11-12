import sys

with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update text occurrences of 4,330+
text = text.replace("4,330+ Models Unified Mesh", "4,750+ Models Unified Mesh")
text = text.replace("4,330+ Models", "4,750+ Models")
text = text.replace("4,330+ models", "4,750+ models")
text = text.replace("4,330+ Unified Models", "4,750+ Unified Models")
text = text.replace("across 4,330+ frontier models", "across 4,750+ frontier models")
text = text.replace("Search &amp; Filter 4,330+ Models across 19 Unified Providers",
                    "Search &amp; Filter 4,750+ Models across 23 Sovereign Providers")
text = text.replace("World Foundational AI Creators • 4,330+ Unified Models • 19 Sovereign Frontier Providers • Pareto Engine",
                    "World Foundational AI Creators • 4,750+ Unified Models • 23 Sovereign Frontier Providers • Pareto Engine")
text = text.replace("4,330+ Unified Models across Eden AI (1,311), AI/ML API (995), Requesty (750), OpenRouter (473), Cloudflare (150+), DeepInfra (177), Hugging Face (110+), Novita (99), NVIDIA (83), SambaNova &amp; Groq",
                    "4,750+ Unified Models across Eden AI (1,311), AI/ML API (995), Requesty (750), OpenRouter (473), Poe (303), DeepInfra (177), Cloudflare (150+), Hugging Face (110+), Parasail (107), Novita (99), NVIDIA (83), SambaNova, Krutrim &amp; Groq")
text = text.replace("Search 4,330+ models by name, lab, provider, or capability (e.g. claude, deepseek, eden, sambanova, flux, qwen, free)...",
                    "Search 4,750+ models by name, lab, provider, or capability (e.g. claude, deepseek, krutrim, poe, parasail, arcee, free)...")

# 2. Update ailab-modal-pills
old_pills = """    <div class="ailab-modal-pills">
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

new_pills = """    <div class="ailab-modal-pills">
      <button type="button" class="ailab-pill is-active" onclick="ailabFilterModelCategory('all', this)">All Mesh (4,750+)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('krutrim', this)">🇮🇳 Krutrim AI (Ola)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('poe', this)">⚡ Poe by Quora (303)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('parasail', this)">⛵ Parasail (107)</button>
      <button type="button" class="ailab-pill" onclick="ailabFilterModelCategory('arcee', this)">🏹 Arcee AI (SLMs)</button>
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

# 3. Update DIRECTORY in window.ailabResolveModelProvenance
target_prov = """      "baseten": { lab_name: "Baseten", country: "United States", flag: "🏗️", tier: "Truss Dedicated Inference" }
    };"""

replacement_prov = """      "baseten": { lab_name: "Baseten", country: "United States", flag: "🏗️", tier: "Truss Dedicated Inference" },
      "krutrim": { lab_name: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign AI Cloud" },
      "ola": { lab_name: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign AI Cloud" },
      "poe": { lab_name: "Poe by Quora", country: "United States", flag: "⚡", tier: "300+ Unified Bot Fabric" },
      "parasail": { lab_name: "Parasail GPU Network", country: "Global", flag: "⛵", tier: "100+ Decentralized GPU Models" },
      "arcee": { lab_name: "Arcee AI", country: "United States", flag: "🏹", tier: "Domain Specialized SLMs" }
    };"""

if target_prov in text:
    text = text.replace(target_prov, replacement_prov)
    print("Updated window.ailabResolveModelProvenance DIRECTORY")
else:
    print("target_prov not matched")

# 4. Add fallback seed models in ailabRenderModelCatalog()
target_seed = """          { id: "baseten/deepseek-ai/DeepSeek-V4.1-Flash", name: "Baseten DeepSeek V4.1 Flash", lab: "Baseten", country: "United States", flag: "🏗️", is_free: false }
        ];"""

replacement_seed = """          { id: "baseten/deepseek-ai/DeepSeek-V4.1-Flash", name: "Baseten DeepSeek V4.1 Flash", lab: "Baseten", country: "United States", flag: "🏗️", is_free: false },
          // Ola Krutrim Cloud (India's Sovereign AI Cloud)
          { id: "krutrim/Qwen3.6-27B", name: "Krutrim Qwen 3.6 27B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          { id: "krutrim/gpt-oss-120b", name: "Krutrim GPT OSS 120B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          { id: "krutrim/gemma-4-31b-it", name: "Krutrim Gemma 4 31B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          { id: "krutrim/GLM-5.3-Flash", name: "Krutrim GLM 5.3 Flash", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          { id: "krutrim/gpt-oss-20b", name: "Krutrim GPT OSS 20B", lab: "Krutrim AI (Ola)", country: "India", flag: "🇮🇳", tier: "Indic Sovereign Cloud", is_free: true },
          // Poe API (303 Unified Bot Models)
          { id: "poe/gemini-4-hydrogen", name: "Poe Gemini 4 Hydrogen", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/grok-4.7", name: "Poe Grok 4.7", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/kimi-k3.1-pro", name: "Poe Kimi K3.1 Pro", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/claude-sonnet-5.5", name: "Poe Claude Sonnet 5.5", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/mistral-large-4", name: "Poe Mistral Large 4", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          { id: "poe/mercury-3-vercel", name: "Poe Mercury 3 Diffusion", lab: "Poe by Quora", country: "United States", flag: "⚡", is_free: false },
          // Parasail GPU Network (107 Models)
          { id: "parasail/parasail-llama-33-70b-fp8", name: "Parasail Llama 3.3 70B FP8", lab: "Parasail GPU Network", country: "Global", flag: "⛵", is_free: true },
          { id: "parasail/parasail-qwen25-vl-72b-instruct", name: "Parasail Qwen 2.5 VL 72B", lab: "Parasail GPU Network", country: "Global", flag: "⛵", is_free: false },
          { id: "parasail/parasail-skyfall-36b-v2-fp8", name: "Parasail Skyfall 36B v2", lab: "Parasail GPU Network", country: "Global", flag: "⛵", is_free: false },
          { id: "parasail/parasail-llama-4-maverick-instruct-fp8", name: "Parasail Llama 4 Maverick", lab: "Parasail GPU Network", country: "Global", flag: "⛵", is_free: false },
          // Arcee AI (Domain-Specialized SLMs)
          { id: "arcee/zai-org/glm-5.3-flash", name: "Arcee GLM 5.3 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: true },
          { id: "arcee/deepseek/deepseek-v4.1-flash", name: "Arcee DeepSeek V4.1 Flash", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: false },
          { id: "arcee/moonshotai/kimi-k3.1-pro", name: "Arcee Kimi K3.1 Pro", lab: "Arcee AI", country: "United States", flag: "🏹", is_free: false }
        ];"""

if target_seed in text:
    text = text.replace(target_seed, replacement_seed)
    print("Updated fallback seed models in ailabRenderModelCatalog")
else:
    print("target_seed not matched")

# 5. Update category filters in ailabRenderModelCatalog
target_cat_filters = """        if (currentCatalogCategory === "edenai" && !m.id.startsWith("edenai/") && !(m.lab && m.lab.includes("Eden"))) return false;"""

replacement_cat_filters = """        if (currentCatalogCategory === "krutrim" && !m.id.startsWith("krutrim/") && !(m.lab && m.lab.includes("Krutrim"))) return false;
        if (currentCatalogCategory === "poe" && !m.id.startsWith("poe/") && !(m.lab && m.lab.includes("Poe"))) return false;
        if (currentCatalogCategory === "parasail" && !m.id.startsWith("parasail/") && !(m.lab && m.lab.includes("Parasail"))) return false;
        if (currentCatalogCategory === "arcee" && !m.id.startsWith("arcee/") && !(m.lab && m.lab.includes("Arcee"))) return false;
        if (currentCatalogCategory === "edenai" && !m.id.startsWith("edenai/") && !(m.lab && m.lab.includes("Eden"))) return false;"""

if target_cat_filters in text:
    text = text.replace(target_cat_filters, replacement_cat_filters)
    print("Updated category filters in ailabRenderModelCatalog")
else:
    print("target_cat_filters not matched")

with open("app/ui/global_ai_lab_view.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved app/ui/global_ai_lab_view.py successfully")
