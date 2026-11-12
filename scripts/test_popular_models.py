import urllib.request
import json

key = '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'

# Fetch available models list to get active valid IDs
req = urllib.request.Request('https://openrouter.ai/api/v1/models')
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read().decode('utf-8'))
    all_models = {m['id']: m for m in data['data']}

test_candidates = [
    'openai/gpt-4o-mini',
    'openai/gpt-4o',
    'meta-llama/llama-3.3-70b-instruct',
    'meta-llama/llama-3.1-8b-instruct',
    'qwen/qwen-2.5-coder-32b-instruct',
    'qwen/qwen-2.5-72b-instruct',
    'deepseek/deepseek-chat',
    'mistralai/mistral-small-24b-instruct-2501',
    'nvidia/nemotron-3.5-lightning:free',
    'google/gemini-2.0-flash-exp:free',
    'google/gemini-flash-1.5'
]

print("=== TESTING OPENROUTER MODEL AVAILABILITY WITH CURRENT KEY ===")
for mid in test_candidates:
    if mid not in all_models:
        # Check closest match
        closest = [k for k in all_models if mid.split('/')[1] in k]
        print(f"[SKIP] '{mid}' not in catalog. Closest: {closest[:2]}")
        continue

    try:
        payload = json.dumps({
            'model': mid,
            'messages': [{'role': 'user', 'content': 'Respond with only: OK'}]
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://openrouter.ai/api/v1/chat/completions',
            data=payload,
            headers={
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://nanopro-studio.onrender.com',
                'X-Title': 'NanoPro Global AI Lab'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode('utf-8'))
            reply = res['choices'][0]['message']['content'].strip()
            pricing = all_models[mid].get('pricing', {})
            print(f"[PASS] {mid} -> Status {r.status} | Reply: '{reply}' | In: ${pricing.get('prompt', 0)}/1M, Out: ${pricing.get('completion', 0)}/1M")
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')[:100]
        print(f"[FAIL] {mid} -> HTTP {e.code}: {err}")
    except Exception as e:
        print(f"[FAIL] {mid} -> Error: {e}")
