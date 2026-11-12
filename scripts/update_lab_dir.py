with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    text = f.read()

target = '        "replicate": { lab: "Replicate Cloud", country: "United States", flag: "🚀", tier: "Containerized Models" }\n      };'

replacement = """        "replicate": { lab: "Replicate Cloud", country: "United States", flag: "🚀", tier: "Containerized Models" },
        "sambanova": { lab: "SambaNova Systems", country: "United States", flag: "⚡", tier: "SN40L Reconfigurable Dataflow (RDU)" },
        "requesty": { lab: "Requesty AI", country: "Global Router", flag: "🌐", tier: "750+ Global Unified Models" },
        "nvidia": { lab: "NVIDIA DGX Cloud", country: "United States", flag: "🟢", tier: "83+ TensorRT-LLM Microservices" },
        "edenai": { lab: "Eden AI", country: "France / Europe", flag: "🌿", tier: "1,311+ Global Multimodal Catalog" },
        "friendli": { lab: "FriendliAI", country: "South Korea / Global", flag: "🚀", tier: "PeriFlow High-Throughput Engine" },
        "thesean": { lab: "TheSean AI", country: "Global", flag: "⚡", tier: "Ultra-Low Latency Inference" },
        "baseten": { lab: "Baseten", country: "United States", flag: "🏗️", tier: "Truss Dedicated Inference" }
      };"""

if target in text:
    text = text.replace(target, replacement)
    with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully added new labs to LAB_DIRECTORY in deploy/cloudflare_worker_gateway.js")
else:
    print("Target not found for LAB_DIRECTORY replacement")
