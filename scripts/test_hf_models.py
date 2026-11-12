import urllib.request
import json

hf_key = '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'

models = [
    'meta-llama/Llama-3.2-3B-Instruct',
    'mistralai/Mistral-7B-Instruct-v0.3',
    'google/gemma-2-9b-it',
    'microsoft/Phi-3.5-mini-instruct',
    'Qwen/Qwen2.5-Coder-32B-Instruct'
]

print("=== TESTING HUGGING FACE INFERENCE API ===")
for m in models:
    try:
        # Standard v1 chat completions endpoint on HuggingFace router
        payload = json.dumps({
            "model": m,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 50
        }).encode('utf-8')
        req = urllib.request.Request(
            f"https://router.huggingface.co/hf-inference/models/{m}/v1/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {hf_key}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=12) as r:
            res = json.loads(r.read().decode('utf-8'))
            reply = res.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"[OK] HF {m} -> {reply.strip()[:60]}")
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')[:120]
        print(f"[FAIL] HF {m} -> HTTP {e.code}: {err}")
    except Exception as e:
        print(f"[FAIL] HF {m} -> Error: {e}")
