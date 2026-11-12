import urllib.request
import json

keys = {
    'OPENROUTER': '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',
    'GROQ': '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',
    'DEEPSEEK': 'sk-2d5bc8b3419244e6bc17f23b36dd6d66',
    'MISTRAL': 'mstrl_OZwEdSDxbLIE8xd9Sg0i3wDLH2l2wOnQ_1OV8Q4',
    'DEEPINFRA': 'sk-di-GZlkK2nWUqmV5nxhsdCbGLWxce5EkSAJ'
}

print("Testing OpenRouter...")
try:
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/auth/key',
        headers={'Authorization': f'Bearer {keys["OPENROUTER"]}'}
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        info = json.loads(r.read().decode('utf-8'))
        print("  OpenRouter Key Info:", json.dumps(info['data'], indent=2))
except Exception as e:
    print("  OpenRouter error:", e)

print("\nTesting Groq...")
try:
    data = json.dumps({'model': 'llama-3.1-8b-instant', 'messages': [{'role': 'user', 'content': 'hi'}]}).encode('utf-8')
    req = urllib.request.Request(
        'https://api.groq.com/openai/v1/chat/completions',
        data=data,
        headers={'Authorization': f'Bearer {keys["GROQ"]}', 'Content-Type': 'application/json', 'User-Agent': 'NanoPro/1.0'}
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        print("  Groq Status: 200 OK!")
except Exception as e:
    print("  Groq error:", e)

print("\nTesting Mistral...")
try:
    data = json.dumps({'model': 'mistral-small-latest', 'messages': [{'role': 'user', 'content': 'hi'}]}).encode('utf-8')
    req = urllib.request.Request(
        'https://api.mistral.ai/v1/chat/completions',
        data=data,
        headers={'Authorization': f'Bearer {keys["MISTRAL"]}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        print("  Mistral Status: 200 OK!")
except Exception as e:
    print("  Mistral error:", e)

print("\nTesting DeepSeek Direct...")
try:
    data = json.dumps({'model': 'deepseek-chat', 'messages': [{'role': 'user', 'content': 'hi'}]}).encode('utf-8')
    req = urllib.request.Request(
        'https://api.deepseek.com/chat/completions',
        data=data,
        headers={'Authorization': f'Bearer {keys["DEEPSEEK"]}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        print("  DeepSeek Status: 200 OK!")
except Exception as e:
    print("  DeepSeek error:", e)
