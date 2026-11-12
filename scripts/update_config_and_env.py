import os

config_addition = """
# Expanded Multi-Provider AI Mesh (4,330+ Models)
NOVITA_AI_KEY = os.environ.get("NOVITA_AI_KEY", "sk_YEp9ZyBhTK7uPVd1qPtfCFVt4p2vjVIABJxmLIJB07E").strip()
CLOUDFLARE_AI_TOKEN = os.environ.get("CLOUDFLARE_AI_TOKEN", "cfut_DqwcZt8S50UIJlhXqYDRilqEF2zzdOwGV9SxMmkWeea8d73a").strip()
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "ccd6c0bc1765868497170623a66e6ec1").strip()

SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY", "d5e98adf-2b3c-477a-8d80-d26c242548c4").strip()
REQUESTY_API_KEY = os.environ.get("REQUESTY_API_KEY", "rqsty-sk-NgcuVBmxQdq1H1u8nqYg6UaUzQKPnR6PJScxuLv3bUh5Lpj0nWFBxrQD5KQvKpe1nVikk2N8DfjHnON0pvKEaeCsPuWF5lDC1sS9rb4UwA0=").strip()
NVIDIA_NIM_API_KEY = os.environ.get("NVIDIA_NIM_API_KEY", "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").strip()
NVIDIA_NIM_ID = os.environ.get("NVIDIA_NIM_ID", "cee2aada-2aca-43ff-a351-161e20ee8977").strip()
BASETEN_API_KEY = os.environ.get("BASETEN_API_KEY", "b10_fJMWbc5R.2e2dU9BmpkOsyLwhU8Wrn0e8TCSSJJfR").strip()
FRIENDLI_API_KEY = os.environ.get("FRIENDLI_API_KEY", "flp_TofgBoyBBXyGzuYjkQDrL8yh0UrS4lMkxSFnuu0wfma26").strip()
THESEAN_API_KEY = os.environ.get("THESEAN_API_KEY", "sk-b4d2af78341948d49280a2e8742af6d2").strip()
EDEN_AI_KEY_1 = os.environ.get("EDEN_AI_KEY_1", "sk-eden-live-rXdRorWgt7qBrIGT_sRZVcU_yWVyE53ZOhuPv-znZwo71f74d72").strip()
EDEN_AI_KEY_2 = os.environ.get("EDEN_AI_KEY_2", "sk-eden-live-iY3xqwWPDt90FfaoReckFnymjdRqK3zTPEgjkOPNFWQ96107a35").strip()
"""

with open("app/core/config.py", "r", encoding="utf-8") as f:
    orig = f.read()

if "SAMBANOVA_API_KEY" not in orig:
    with open("app/core/config.py", "a", encoding="utf-8") as f:
        f.write(config_addition)
    print("Added expanded keys to app/core/config.py")
else:
    print("Already in app/core/config.py")
