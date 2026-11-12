import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '"novita":' in l:
        for j in range(max(0, i-2), min(len(lines), i+8)):
            print(f'{j+1}: {repr(lines[j])}')
        break
