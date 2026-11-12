with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'if\s*\(\s*path[^\)]+\)', text)
for m in matches:
    if 'model' in m or 'api' in m:
        print(m)
