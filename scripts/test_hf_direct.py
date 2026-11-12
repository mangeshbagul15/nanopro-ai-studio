import urllib.request
import json

hf_key = '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'

models = [
    'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B',
    'facebook/bart-large-cnn',
    'distilbert/distilbert-base-uncased-finetuned-sst-2-english',
    'openai-community/gpt2'
]

for m in models:
    try:
        payload = json.dumps({'inputs': 'Today is a great day'}).encode('utf-8')
        req = urllib.request.Request(
            f'https://api-inference.huggingface.co/models/{m}',
            data=payload,
            headers={'Authorization': f'Bearer {hf_key}', 'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=12) as r:
            res = json.loads(r.read().decode('utf-8'))
            print(f"[OK] HF {m} -> {str(res)[:80]}")
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')[:80]
        print(f"[FAIL] HF {m} -> HTTP {e.code}: {err}")
    except Exception as e:
        print(f"[FAIL] HF {m} -> {e}")
