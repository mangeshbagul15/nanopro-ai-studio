# Prototype script for updating cloudflare_worker_gateway.js
with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

print("File length:", len(text))
idx = text.find("if (path === \"/api/ai/execute\" && request.method === \"POST\") {")
print("execute endpoint index:", idx)
