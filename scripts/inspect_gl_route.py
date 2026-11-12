import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('path === "/api/ai/global_labs"')
print(text[pos:pos+1500])
