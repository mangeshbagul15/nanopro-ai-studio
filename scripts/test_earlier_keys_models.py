import urllib.request
import json

keys = {
    'DEEPINFRA': 'sk-di-GZlkK2nWUqmV5nxhsdCbGLWxce5EkSAJ',
    'MISTRAL': 'mstrl_OZwEdSDxbLIE8xd9Sg0i3wDLH2l2wOnQ_1OV8Q4',
    'DEEPSEEK': 'sk-2d5bc8b3419244e6bc17f23b36dd6d66',
    'GROQ': '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'
}

print('--- Testing DeepInfra Models ---')
try:
    req = urllib.request.Request(
        'https://api.deepinfra.com/v1/openai/models',
        headers={'Authorization': f'Bearer {keys["DEEPINFRA"]}', 'User-Agent': 'NanoPro/1.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        models = res.get('data', [])
        print(f'DeepInfra models count: {len(models)}')
        print('Sample DeepInfra models:', [m['id'] for m in models[:10]])
except Exception as e:
    print('DeepInfra error:', e)

print('\n--- Testing Mistral Models ---')
try:
    req = urllib.request.Request(
        'https://api.mistral.ai/v1/models',
        headers={'Authorization': f'Bearer {keys["MISTRAL"]}', 'User-Agent': 'NanoPro/1.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        models = res.get('data', [])
        print(f'Mistral models count: {len(models)}')
        print('Sample Mistral models:', [m['id'] for m in models[:10]])
except Exception as e:
    print('Mistral error:', e)

print('\n--- Testing Groq Models ---')
try:
    req = urllib.request.Request(
        'https://api.groq.com/openai/v1/models',
        headers={'Authorization': f'Bearer {keys["GROQ"]}', 'User-Agent': 'NanoPro/1.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        models = res.get('data', [])
        print(f'Groq models count: {len(models)}')
        print('Sample Groq models:', [m['id'] for m in models[:10]])
except Exception as e:
    print('Groq error:', e)

print('\n--- Testing DeepSeek Models ---')
try:
    req = urllib.request.Request(
        'https://api.deepseek.com/models',
        headers={'Authorization': f'Bearer {keys["DEEPSEEK"]}', 'User-Agent': 'NanoPro/1.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        models = res.get('data', [])
        print(f'DeepSeek models count: {len(models)}')
        print('Sample DeepSeek models:', [m['id'] for m in models[:10]])
except Exception as e:
    print('DeepSeek error:', e)
