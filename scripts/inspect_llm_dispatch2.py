import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'async function (call\w+)', text)
print('Defined caller functions:', matches)
