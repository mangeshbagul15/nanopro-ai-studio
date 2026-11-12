with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('// 5-Tier Dispatch Decision')
print(f"5-Tier Dispatch Decision starts around {idx}:")
print(text[idx:idx+2500].encode('ascii', 'backslashreplace').decode('ascii'))
