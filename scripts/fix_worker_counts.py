import os

os.chdir(r"C:\Users\mange\OneDrive\Documents\GitHub\nanopro-ai-studio")

with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    cw = f.read()

# Update line 3799
cw = cw.replace(
    "total_models: liveModels ? (liveModels.length + 995 + 177 + 110 + 99 + 150 + 56 + 75 + 11) : 2150,",
    "total_models: liveModels ? (liveModels.length + 1311 + 750 + 995 + 303 + 177 + 150 + 110 + 107 + 99 + 83 + 56 + 44 + 11 + 10 + 9 + 6 + 5) : 4804,"
)

cw = cw.replace(
    'total_models: "4,750+ Unified Mesh across 23 Sovereign Providers",',
    'total_models: "4,804+ Unified Mesh across 25 Sovereign Providers",'
)

cw = cw.replace(
    'name: "World Foundational AI Catalog (4,750+ Models)",',
    'name: "World Foundational AI Catalog (4,804+ Models)",'
)

cw = cw.replace(
    '// 1. TOOL: nanopro_global_ai_execute (All 4,750+ Models via Edge)',
    '// 1. TOOL: nanopro_global_ai_execute (All 4,804+ Models via Edge)'
)

cw = cw.replace(
    '// 3. TOOL: nanopro_global_ai_list (4,750+ Models Catalog)',
    '// 3. TOOL: nanopro_global_ai_list (4,804+ Models Catalog)'
)

cw = cw.replace(
    "total_models: liveModels ? (liveModels.length + 995 + 177 + 110 + 99 + 83 + 56 + 1311 + 750 + 303 + 107 + 6 + 9) : 4750,",
    "total_models: liveModels ? (liveModels.length + 1311 + 750 + 995 + 303 + 177 + 150 + 110 + 107 + 99 + 83 + 56 + 44 + 11 + 10 + 9 + 6 + 5) : 4804,"
)

cw = cw.replace(
    'active_providers: 23,',
    'active_providers: 25,'
)

cw = cw.replace(
    'total_models: 4750\n            };',
    'total_models: 4804\n            };'
)

cw = cw.replace(
    'providers: ["Ola Krutrim", "Poe by Quora", "Parasail", "Arcee AI", "Eden AI", "Requesty", "NVIDIA NIM", "SambaNova", "Cloudflare Workers AI", "Novita", "DeepInfra", "Mistral", "DeepSeek", "Groq", "Hugging Face", "OpenRouter"]',
    'providers: ["Defapi Hub", "TypeSafe AI JEV", "Ola Krutrim", "Poe by Quora", "Parasail", "Arcee AI", "Eden AI", "Requesty", "NVIDIA NIM", "SambaNova", "Cloudflare Workers AI", "Novita", "DeepInfra", "Mistral", "DeepSeek", "Groq", "Hugging Face", "OpenRouter"]'
)

with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
    f.write(cw)

print("Updated deploy/cloudflare_worker_gateway.js counts successfully!")
