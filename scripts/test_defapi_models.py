import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    'google/gemini-4-neon',
    'google/gemini-4-hydrogen',
    'anthropic/claude-fable-5-2',
    'openai/gpt-4o',
    'openai/gpt-4o-mini',
    'google/gemini-2.0-flash',
    'deepseek/deepseek-r1',
    'deepseek/deepseek-v3',
    'anthropic/claude-3-5-sonnet',
]

for m in candidates:
    data = json.dumps({'model': m, 'messages': [{'role': 'user', 'content': 'hi'}]}).encode('utf-8')
    req = urllib.request.Request('https://api.defapi.org/v1/chat/completions', data=data, headers={
        'Authorization': 'Bearer dk-8ad11ada1f8d9ea75cc20cb1fc55cbed',
        'Content-Type': 'application/json',
        'User-Agent': 'NanoPro-Studio/1.0'
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            print('SUCCESS model:', m, resp.status)
            res = json.loads(resp.read().decode('utf-8'))
            print('Answer:', res)
            break
    except Exception as e:
        body = ''
        if hasattr(e, 'read'):
            try: body = e.read().decode('utf-8', errors='ignore')
            except: pass
        print(m, 'Error:', e, body[:120])
