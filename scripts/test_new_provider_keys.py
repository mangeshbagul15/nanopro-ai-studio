import urllib.request
import json

keys = {
    "HF": "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",
    "FAL": "fal_sk_d1a4032b2a4d4c94ad7cbef5395d439f:ad79f427f9e0d633316032a561ab9999",
    "REPLICATE": "r8_VSW8CuVp9dP35gBcLCIFIJcNxfzVpuY3jNpQI",
    "AIMLAPI_1": "d6b5f7f58a5d797e02fd021c231026ea",
    "AIMLAPI_2": "666612ebe3ae25e4db14bd8da4b654fd"
}

print("=== 1. TESTING AI/ML API (OpenAI Compatible) ===")
for k_name, k_val in [("AIMLAPI_1", keys["AIMLAPI_1"]), ("AIMLAPI_2", keys["AIMLAPI_2"])]:
    try:
        req = urllib.request.Request(
            "https://api.aimlapi.com/v1/models",
            headers={"Authorization": f"Bearer {k_val}"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
            model_ids = [m['id'] for m in data.get('data', [])]
            print(f"  [OK] {k_name} connected! Total models available: {len(model_ids)}")
            print(f"       Sample models: {model_ids[:5]}")
    except Exception as e:
        print(f"  [FAIL] {k_name}: {e}")

print("\n=== 2. TESTING HUGGING FACE INFERENCE API ===")
try:
    req = urllib.request.Request(
        "https://huggingface.co/api/whoami-v2",
        headers={"Authorization": f"Bearer {keys['HF']}"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        hf_user = json.loads(r.read().decode('utf-8'))
        print(f"  [OK] HF Authenticated as: {hf_user.get('name', 'User')} | Type: {hf_user.get('type')}")
except Exception as e:
    print(f"  [FAIL] HF Auth: {e}")

# Test HF Router chat completion (Qwen, Llama, Mistral)
try:
    payload = json.dumps({
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": [{"role": "user", "content": "Hello"}]
    }).encode('utf-8')
    req = urllib.request.Request(
        "https://router.huggingface.co/hf-inference/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {keys['HF']}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        hf_chat = json.loads(r.read().decode('utf-8'))
        print(f"  [OK] HF Chat Completions: {hf_chat['choices'][0]['message']['content'][:60]}")
except Exception as e:
    print(f"  [HF Chat Router]: {e}")

print("\n=== 3. TESTING FAL.AI ===")
try:
    req = urllib.request.Request(
        "https://rest.alpha.fal.ai/tokens",
        headers={"Authorization": f"Key {keys['FAL']}"}
    )
    # or test queue API
    print("  [INFO] FAL.ai key format valid:", keys['FAL'].startswith("fal_sk_"))
except Exception as e:
    print(f"  [FAIL] FAL.ai: {e}")

print("\n=== 4. TESTING REPLICATE ===")
try:
    req = urllib.request.Request(
        "https://api.replicate.com/v1/account",
        headers={"Authorization": f"Token {keys['REPLICATE']}"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        rep_acc = json.loads(r.read().decode('utf-8'))
        print(f"  [OK] Replicate Account: {rep_acc.get('username', 'User')} ({rep_acc.get('type', '')})")
except Exception as e:
    print(f"  [FAIL] Replicate: {e}")
