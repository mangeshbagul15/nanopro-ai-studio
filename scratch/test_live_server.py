import urllib.request
import json

test_prompts = [
    'today wether/',
    'why heat',
    '\'mangesh " ccha fakt e find karaychay provide python code',
    'Write a Python code to find and print the substring \'eg\' from the string \'mangesh'
]

print("=== TESTING LIVE SERVER AT HTTP://LOCALHOST:8000/API/MANAGER/CHAT ===")
for p in test_prompts:
    req_data = json.dumps({'message': p, 'session_id': 'live_test_session'}).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request('http://localhost:8000/api/manager/chat', data=req_data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            rep = data.get('response', '')
            first_line = rep.split('\n')[0]
            print(f"PROMPT: {p}")
            print(f"  STATUS: {data.get('status')} | AGENT: {data.get('agent_id')}")
            print(f"  FIRST LINE: {first_line}\n")
    except Exception as e:
        print(f"ERROR on {p}: {e}\n")
