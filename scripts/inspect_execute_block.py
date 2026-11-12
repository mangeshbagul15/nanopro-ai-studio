import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'callAIMLAPI|callHuggingFace|MULTI_PROVIDER_KEYS', text)]
for m in matches:
    print('--- MATCH ---')
    print(text[m-30:m+400])
