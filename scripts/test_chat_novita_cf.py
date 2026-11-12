import urllib.request
import json

novita_key = "sk_YEp9ZyBhTK7uPVd1qPtfCFVt4p2vjVIABJxmLIJB07E"
cf_token = "cfut_DqwcZt8S50UIJlhXqYDRilqEF2zzdOwGV9SxMmkWeea8d73a"
cf_account_id = "ccd6c0bc1765868497170623a66e6ec1"

print("--- Testing Novita AI Chat Completion ---")
try:
    payload = json.dumps({
        "model": "deepseek/deepseek-r1",
        "messages": [{"role": "user", "content": "Respond with: Novita AI Connected"}],
        "max_tokens": 20
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.novita.ai/v3/openai/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {novita_key}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode("utf-8"))
        print("Novita Chat Success:", res["choices"][0]["message"]["content"])
except Exception as e:
    print("Novita Chat error:", e)

print("\n--- Testing Cloudflare Workers AI Inference ---")
try:
    # CF Workers AI endpoint: https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-3.1-8b-instruct
    cf_url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account_id}/ai/run/@cf/meta/llama-3.1-8b-instruct"
    payload = json.dumps({
        "messages": [{"role": "user", "content": "Respond with: Cloudflare Workers AI Live"}]
    }).encode("utf-8")
    req = urllib.request.Request(
        cf_url,
        data=payload,
        headers={"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode("utf-8"))
        print("CF Workers AI Success:", res.get("result", {}).get("response"))
except Exception as e:
    print("CF Workers AI error:", e)
