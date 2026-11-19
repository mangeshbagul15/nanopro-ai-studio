import os
import sys

os.chdir(r"C:\Users\mange\OneDrive\Documents\GitHub\nanopro-ai-studio")

# 1. Update render.yaml
print("[*] Updating render.yaml...")
with open("render.yaml", "r", encoding="utf-8") as f:
    render_yaml = f.read()

defapi_render_entry = """      - key: POE_API_KEY
        value: sk-poe-Q_PHEUPo8oUxy-FGHxCy4y2cMbtJSx5y0hprJLGDXcY
      - key: DEFAPI_API_KEY
        value: dk-8ad11ada1f8d9ea75cc20cb1fc55cbed
      - key: DEFAPI_BASE_URL
        value: https://api.defapi.org/v1
      - key: JEV_API_KEY
        value: sk_jev-ai_TeTWU37d7VrPE3iepqXdFs4f42RRfeFI
      - key: JEV_BASE_URL
        value: https://jevtypesafeai.com/api/v1"""

if "DEFAPI_API_KEY" not in render_yaml:
    render_yaml = render_yaml.replace(
        """      - key: POE_API_KEY\n        value: sk-poe-Q_PHEUPo8oUxy-FGHxCy4y2cMbtJSx5y0hprJLGDXcY""",
        defapi_render_entry
    )
    with open("render.yaml", "w", encoding="utf-8") as f:
        f.write(render_yaml)
    print(" -> render.yaml updated successfully.")
else:
    print(" -> render.yaml already contains DEFAPI_API_KEY.")

# 2. Update .env.example
print("[*] Updating .env.example...")
with open(".env.example", "r", encoding="utf-8") as f:
    env_example = f.read()

defapi_env_example_entry = """# === DEFAPI & JEV AI (4,804+ MODELS UNIFIED MESH) ===
DEFAPI_API_KEY=your_defapi_key_here
DEFAPI_BASE_URL=https://api.defapi.org/v1
JEV_API_KEY=your_jev_api_key_here
JEV_BASE_URL=https://jevtypesafeai.com/api/v1
"""

if "DEFAPI_API_KEY" not in env_example:
    env_example += "\n" + defapi_env_example_entry
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_example)
    print(" -> .env.example updated successfully.")
else:
    print(" -> .env.example already contains DEFAPI_API_KEY.")

# 3. Update app/core/config.py
print("[*] Updating app/core/config.py...")
with open("app/core/config.py", "r", encoding="utf-8") as f:
    cfg = f.read()

defapi_cfg_entry = """
# Defapi & Jev AI Mesh (4,804+ Models)
DEFAPI_API_KEY = os.environ.get("DEFAPI_API_KEY", "dk-8ad11ada1f8d9ea75cc20cb1fc55cbed").strip()
DEFAPI_BASE_URL = os.environ.get("DEFAPI_BASE_URL", "https://api.defapi.org/v1").strip()
JEV_API_KEY = os.environ.get("JEV_API_KEY", "sk_jev-ai_TeTWU37d7VrPE3iepqXdFs4f42RRfeFI").strip()
JEV_BASE_URL = os.environ.get("JEV_BASE_URL", "https://jevtypesafeai.com/api/v1").strip()
"""

if "DEFAPI_API_KEY" not in cfg:
    cfg += defapi_cfg_entry
    with open("app/core/config.py", "w", encoding="utf-8") as f:
        f.write(cfg)
    print(" -> app/core/config.py updated successfully.")
else:
    print(" -> app/core/config.py already contains DEFAPI_API_KEY.")

# 4. Update app/core/global_ai_catalog.py
print("[*] Updating app/core/global_ai_catalog.py...")
with open("app/core/global_ai_catalog.py", "r", encoding="utf-8") as f:
    cat = f.read()

# Add to lab_map
target_lab_map = '"anthropic": ("Anthropic", "United States", "🇺🇸", "Frontier Cognitive & Code"),'
new_lab_map = '''"defapi": ("Defapi Frontier Hub", "United States", "🌐", "Frontier Multimodal SOTA"),
        "jev": ("TypeSafe AI (JEV)", "United States", "⚡", "System One Fast Reasoning"),
        "typesafe": ("TypeSafe AI (JEV)", "United States", "⚡", "System One Fast Reasoning"),
        "anthropic": ("Anthropic", "United States", "🇺🇸", "Frontier Cognitive & Code"),'''

if "defapi" not in cat:
    cat = cat.replace(target_lab_map, new_lab_map, 1)

# Add to GLOBAL_AI_CREATORS
target_creators = 'GLOBAL_AI_CREATORS: Dict[str, Dict[str, Any]] = {'
new_creators = '''GLOBAL_AI_CREATORS: Dict[str, Dict[str, Any]] = {
    "defapi": {
        "id": "defapi",
        "name": "Defapi Frontier Hub",
        "country": "USA",
        "flag": "🌐",
        "category": "Frontier Multimodal Aggregator",
        "description": "Unified frontier access for Gemini 4 Neon, GPT-6 Astra, Claude Fable 5.2, Sora 2 Pro, and Veo 3.1.",
        "website": "https://defapi.org",
        "status": "OPERATIONAL",
        "models": [
            {"id": "defapi/google/gemini-4-neon", "name": "Gemini 4 Neon", "tier": "Frontier", "context": "2M", "elo": 1425, "latency_ms": 1100, "type": "Multimodal Frontier"},
            {"id": "defapi/google/gemini-4-hydrogen", "name": "Gemini 4 Hydrogen", "tier": "Frontier", "context": "2M", "elo": 1415, "latency_ms": 1050, "type": "Multimodal Frontier"},
            {"id": "defapi/google/gemini-3.7-flash", "name": "Gemini 3.7 Flash", "tier": "High", "context": "1M", "elo": 1360, "latency_ms": 280, "type": "Ultra Fast Flash"},
            {"id": "defapi/anthropic/claude-fable-5-2", "name": "Claude Fable 5.2", "tier": "Frontier", "context": "500k", "elo": 1430, "latency_ms": 2200, "type": "Deep Reasoning"},
            {"id": "defapi/anthropic/claude-opus-5.5", "name": "Claude Opus 5.5", "tier": "Frontier", "context": "200k", "elo": 1410, "latency_ms": 1900, "type": "Cognitive SOTA"},
            {"id": "defapi/openai/gpt-6-astra", "name": "GPT-6 Astra", "tier": "Frontier", "context": "1M", "elo": 1420, "latency_ms": 1300, "type": "Frontier Reasoning"},
            {"id": "defapi/openai/gpt-5.6-luna", "name": "GPT-5.6 Luna", "tier": "High", "context": "512k", "elo": 1375, "latency_ms": 850, "type": "Production Frontier"},
            {"id": "defapi/openai/sora-2-pro", "name": "Sora 2 Pro", "tier": "Media", "context": "128k", "elo": 1390, "latency_ms": 3500, "type": "Video Synthesis"}
        ]
    },
    "typesafe": {
        "id": "typesafe",
        "name": "TypeSafe AI (JEV)",
        "country": "USA",
        "flag": "⚡",
        "category": "System One Calibrated Reasoning",
        "description": "Creators of the JEV sub-50ms calibrated decision and fast reasoning models.",
        "website": "https://jevtypesafeai.com",
        "status": "OPERATIONAL",
        "models": [
            {"id": "jev/jev-latest", "name": "JEV Latest", "tier": "Frontier", "context": "128k", "elo": 1380, "latency_ms": 45, "type": "System One Decision"},
            {"id": "jev/jev-decision-fast", "name": "JEV Decision Fast", "tier": "High", "context": "64k", "elo": 1350, "latency_ms": 30, "type": "Ultra Low Latency"},
            {"id": "jev/jev-decision-deep", "name": "JEV Decision Deep Logic", "tier": "Frontier", "context": "128k", "elo": 1395, "latency_ms": 120, "type": "Calibrated Logic"},
            {"id": "jev/typesafe/jev-1.13", "name": "TypeSafe JEV 1.13", "tier": "High", "context": "64k", "elo": 1365, "latency_ms": 50, "type": "Production Decision"}
        ]
    },'''

if '"defapi": {' not in cat:
    cat = cat.replace(target_creators, new_creators, 1)

with open("app/core/global_ai_catalog.py", "w", encoding="utf-8") as f:
    f.write(cat)
print(" -> app/core/global_ai_catalog.py updated successfully.")

# 5. Update app/core/mcp_server.py
print("[*] Updating app/core/mcp_server.py...")
with open("app/core/mcp_server.py", "r", encoding="utf-8") as f:
    mcp = f.read()

mcp = mcp.replace(
    "4,750+ models across 23 sovereign providers including Krutrim, Poe, Parasail, Arcee, Eden AI, Requesty, NVIDIA NIM, SambaNova, Cloudflare Workers AI, Novita, DeepInfra, Mistral, DeepSeek, Groq, Hugging Face, OpenRouter",
    "4,804+ models across 25 sovereign providers including Defapi, Jev AI, Krutrim, Poe, Parasail, Arcee, Eden AI, Requesty, NVIDIA NIM, SambaNova, Cloudflare Workers AI, Novita, DeepInfra, Mistral, DeepSeek, Groq, Hugging Face, OpenRouter"
)
with open("app/core/mcp_server.py", "w", encoding="utf-8") as f:
    f.write(mcp)
print(" -> app/core/mcp_server.py updated successfully.")

print("[✓] Step 1-5 completed!")
