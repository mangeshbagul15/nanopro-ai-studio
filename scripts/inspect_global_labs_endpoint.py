with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('/api/ai/global_labs')
print(f"global_labs at index {idx}:")
print(text[idx-50:idx+1500].encode('ascii', 'backslashreplace').decode('ascii'))
