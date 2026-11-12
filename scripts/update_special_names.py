# -*- coding: utf-8 -*-

special_dict_str = """      const SPECIAL_NAMES = {
        "meta-llama/llama-3.3-70b-instruct": "Meta Llama 3.3 70B Instruct",
        "openai/gpt-4o-mini": "OpenAI GPT-4o Mini",
        "openai/gpt-4o": "OpenAI GPT-4o (Omni)",
        "qwen/qwen-2.5-coder-32b-instruct": "Qwen 2.5 Coder 32B SOTA",
        "deepseek/deepseek-chat": "DeepSeek V3 Flagship",
        "deepseek/deepseek-r1": "DeepSeek R1 (Open Reasoning SOTA)",
        "nvidia/nemotron-3.5-lightning:free": "NVIDIA Nemotron 3.5 Lightning (Free)",
        "groq/qwen3.8-27b": "Qwen 3.8 27B (Groq Deterministic LPU)",
        "google/gemini-2.5-flash:vision-generative": "Gemini 2.5 Flash Multimodal & Generative Studio",
        "anthropic/claude-3.7-sonnet:computer-use": "Autonomous Computer Use Agent (CUA) — Claude 3.7",
        "anthropic/claude-3.7-sonnet:data-architect": "Claude 3.7 Sonnet (Hybrid Thinking · Data Architect)"
      };
      let rawName = modelId.split("/").pop().replace(/:free$/, " (Free)").replace(/-/g, " ");
      const modelName = SPECIAL_NAMES[modelId] || rawName.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");"""

target_pattern = """      let rawName = modelId.split("/").pop().replace(/:free$/, " (Free)").replace(/-/g, " ");
      const modelName = rawName.charAt(0).toUpperCase() + rawName.slice(1);"""

# Update gateway.js
with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    gw = f.read()

if target_pattern in gw:
    gw = gw.replace(target_pattern, special_dict_str)
    with open('deploy/cloudflare_worker_gateway.js', 'w', encoding='utf-8') as f:
        f.write(gw)
    print("Updated deploy/cloudflare_worker_gateway.js with SPECIAL_NAMES!")

# Update global_ai_lab_view.py
with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    view = f.read()

view_target = """      let cleanName = modelId.split("/").pop().replace(/:free$/, " (Free)").replace(/-/g, " ");
      cleanName = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);"""

view_replace = """      const SPECIAL_NAMES = {
        "meta-llama/llama-3.3-70b-instruct": "Meta Llama 3.3 70B Instruct",
        "openai/gpt-4o-mini": "OpenAI GPT-4o Mini",
        "openai/gpt-4o": "OpenAI GPT-4o (Omni)",
        "qwen/qwen-2.5-coder-32b-instruct": "Qwen 2.5 Coder 32B SOTA",
        "deepseek/deepseek-chat": "DeepSeek V3 Flagship",
        "deepseek/deepseek-r1": "DeepSeek R1 (Open Reasoning SOTA)",
        "nvidia/nemotron-3.5-lightning:free": "NVIDIA Nemotron 3.5 Lightning (Free)",
        "groq/qwen3.8-27b": "Qwen 3.8 27B (Groq Deterministic LPU)",
        "google/gemini-2.5-flash:vision-generative": "Gemini 2.5 Flash Multimodal & Generative Studio",
        "anthropic/claude-3.7-sonnet:computer-use": "Autonomous Computer Use Agent (CUA) — Claude 3.7",
        "anthropic/claude-3.7-sonnet:data-architect": "Claude 3.7 Sonnet (Hybrid Thinking · Data Architect)"
      };
      let rawName = modelId.split("/").pop().replace(/:free$/, " (Free)").replace(/-/g, " ");
      const cleanName = SPECIAL_NAMES[modelId] || rawName.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");"""

if view_target in view:
    view = view.replace(view_target, view_replace)
    with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
        f.write(view)
    print("Updated app/ui/global_ai_lab_view.py with SPECIAL_NAMES!")
else:
    print("view_target not matched; searching ailabResolveModelProvenance...")
    idx = view.find('function ailabResolveModelProvenance')
    if idx != -1:
        print(view[idx:idx+800].encode('ascii', 'backslashreplace').decode('ascii'))
