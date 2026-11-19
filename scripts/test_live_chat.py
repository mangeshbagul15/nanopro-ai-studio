import urllib.request
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def ask_live(prompt, model='auto'):
    data = json.dumps({'prompt': prompt, 'model': model}).encode('utf-8')
    req = urllib.request.Request('https://mangesh-nanopro.mangeshbagul15.workers.dev/api/ai/execute', data=data, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'NanoPro-LiveTester/1.0'
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
            res = json.loads(r.read().decode('utf-8'))
            print(f'=== PROMPT: "{prompt}" (Model: {model}) ===')
            print('Executed Model:', res.get('model_executed'))
            print('Duration:', res.get('duration_ms'), 'ms')
            print('Response:\n', res.get('response'))
            print('=' * 60 + '\n')
    except Exception as e:
        print('Error:', e)
        if hasattr(e, 'read'):
            print('Body:', e.read().decode('utf-8'))

print("1. Testing 'hi'...")
ask_live('hi')

print("2. Testing 'toral kiti report send hotata'...")
ask_live('toral kiti report send hotata')
