import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('path.startsWith("/api/ai/history/chats/')
print('Found path.startsWith(/api/ai/history/chats/):', s)
if s != -1:
    print(text[s:s+1000])
