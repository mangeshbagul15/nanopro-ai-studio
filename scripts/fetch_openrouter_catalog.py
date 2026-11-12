import urllib.request
import json

req = urllib.request.Request('https://openrouter.ai/api/v1/models')
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read().decode('utf-8'))
    models = data['data']
    print(f"Total OpenRouter Models Available: {len(models)}")
    
    for query in ['claude', 'deepseek', 'gemini', 'gpt-4o', 'qwen', 'llama-3.3']:
        matches = [m['id'] for m in models if query in m['id'].lower()]
        print(f"Query '{query}' ({len(matches)} models): {matches[:6]}")
