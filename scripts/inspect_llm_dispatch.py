with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('// LLM DISPATCH WITH DEEP NANOPRO KNOWLEDGE INJECTION')
if idx == -1:
    idx = text.find('const messages = [')

print(f"LLM Dispatch starts around {idx}:")
print(text[idx:idx+2000].encode('ascii', 'backslashreplace').decode('ascii'))
