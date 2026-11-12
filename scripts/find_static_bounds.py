with open('deploy/cloudflare_worker_gateway.js', 'r', encoding='utf-8') as f:
    text = f.read()

m3 = '// DOMAIN 3: ENTERPRISE DATA ENGINEERING & MEDALLION LAKEHOUSE'
m_tg = '// 1. TELEGRAM DISPATCH INTENT'

idx3 = text.find(m3)
idxtg = text.find(m_tg)

print(f"Static domains 3-5 start at {idx3}, Telegram starts at {idxtg}")
print("\nBefore static blocks:")
print(text[idx3-200:idx3].encode('ascii', 'backslashreplace').decode('ascii'))
print("\nAfter static blocks (Telegram):")
print(text[idxtg:idxtg+200].encode('ascii', 'backslashreplace').decode('ascii'))
