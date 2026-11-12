with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    text = f.read()

target = '        "nvidia": { lab: "NVIDIA AI", country: "United States", flag: "🇺🇸", tier: "High-Speed Compute" },\n'
if target in text:
    text = text.replace(target, "")
    with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
        f.write(text)
    print("Removed duplicate nvidia key")
else:
    print("Target not found")
