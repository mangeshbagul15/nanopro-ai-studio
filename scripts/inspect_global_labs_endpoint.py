import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('path === "/api/ai/global_labs"')
if s != -1:
    print(text[s:s+2500])
else:
    print('Not found')
