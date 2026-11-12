import urllib.request
import json

keys = {
    'DEEPINFRA': 'sk-di-GZlkK2nWUqmV5nxhsdCbGLWxce5EkSAJ',
    'MISTRAL': 'mstrl_OZwEdSDxbLIE8xd9Sg0i3wDLH2l2wOnQ_1OV8Q4',
    'DEEPSEEK': 'sk-2d5bc8b3419244e6bc17f23b36dd6d66'
}

print('Testing DeepInfra chat completion...')
try:
    payload = json.dumps({
        'model': 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
        'messages': [{'role': 'user', 'content': 'Respond with 1 word: Ready'}],
        'max_tokens': 10
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.deepinfra.com/v1/openai/chat/completions',
        data=payload,
        headers={'Authorization': f'Bearer {keys["DEEPINFRA"]}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        print('DeepInfra Response:', res['choices'][0]['message']['content'])
except Exception as e:
    print('DeepInfra error:', e)

print('\nTesting Mistral chat completion...')
try:
    payload = json.dumps({
        'model': 'mistral-small-latest',
        'messages': [{'role': 'user', 'content': 'Respond with 1 word: Ready'}],
        'max_tokens': 10
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.mistral.ai/v1/chat/completions',
        data=payload,
        headers={'Authorization': f'Bearer {keys["MISTRAL"]}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        print('Mistral Response:', res['choices'][0]['message']['content'])
except Exception as e:
    print('Mistral error:', e)

print('\nTesting DeepSeek chat completion...')
try:
    payload = json.dumps({
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': 'Respond with 1 word: Ready'}],
        'max_tokens': 10
    }).encode('utf-8')
    req = urllib.request.Request(
        'https://api.deepseek.com/chat/completions',
        data=payload,
        headers={'Authorization': f'Bearer {keys["DEEPSEEK"]}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read().decode('utf-8'))
        print('DeepSeek Response:', res['choices'][0]['message']['content'])
except Exception as e:
    print('DeepSeek error:', e)
