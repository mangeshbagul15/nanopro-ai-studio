with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    text = f.read()

target = '        "krutrim": { lab: "Krutrim AI", country: "India", flag: "🇮🇳", tier: "Indic Multilingual SOTA" },\n'
if target in text:
    text = text.replace(target, "")
    with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
        f.write(text)
    print("Removed earlier duplicate krutrim key")
else:
    print("Target not found")
