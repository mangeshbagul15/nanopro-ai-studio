import urllib.request
import json

novita_key = "sk_YEp9ZyBhTK7uPVd1qPtfCFVt4p2vjVIABJxmLIJB07E"
cf_token = "cfut_DqwcZt8S50UIJlhXqYDRilqEF2zzdOwGV9SxMmkWeea8d73a"

print("--- 1. Testing Novita AI Models ---")
try:
    req = urllib.request.Request(
        "https://api.novita.ai/v3/openai/models",
        headers={"Authorization": f"Bearer {novita_key}", "User-Agent": "NanoPro/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode("utf-8"))
        models = res.get("data", [])
        print(f"Novita models count: {len(models)}")
        print("Sample Novita models:", [m.get("id") for m in models[:10]])
except Exception as e:
    print("Novita error:", e)

print("\n--- 2. Testing Cloudflare Workers AI Token Verification ---")
try:
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/user/tokens/verify",
        headers={"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode("utf-8"))
        print("CF Token Verify status:", res.get("success"), res.get("messages"), res.get("result"))
except Exception as e:
    print("CF Token error:", e)

print("\n--- 3. Testing Cloudflare Accounts for Workers AI ---")
try:
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/accounts",
        headers={"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode("utf-8"))
        accounts = res.get("result", [])
        print(f"CF Accounts count: {len(accounts)}")
        for acc in accounts:
            print(f"  Account ID: {acc.get('id')}, Name: {acc.get('name')}")
except Exception as e:
    print("CF Accounts error:", e)
