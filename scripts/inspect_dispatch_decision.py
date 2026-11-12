with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

m_dispatch = '// 5-Tier Dispatch Decision'
m_resp_ok = 'if (resp && resp.ok) {'

idx_d = text.find(m_dispatch)
idx_ok = text.find(m_resp_ok, idx_d)

print(f"Dispatch Decision from {idx_d} to {idx_ok}")
print(text[idx_d:idx_ok].encode('ascii', 'backslashreplace').decode('ascii'))
