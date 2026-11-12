import sys, json

print("Checking configured multi-provider keys...")
with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    cf_code = f.read()

required_keys = [
    "SAMBANOVA", "REQUESTY", "NVIDIA", "NVIDIA_ID",
    "BASETEN", "FRIENDLI", "THESEAN", "EDENAI_1", "EDENAI_2",
    "NOVITA", "CF_AI", "CF_ACCOUNT", "OPENROUTER", "GROQ"
]

all_found = True
for k in required_keys:
    if f"{k}:" in cf_code:
        print(f"  [OK] {k}")
    else:
        print(f"  [MISSING] {k}")
        all_found = False

print("\nChecking dispatch functions...")
functions = [
    "callSambaNova", "callRequestyAI", "callNvidiaNIM",
    "callEdenAI", "callFriendliAI", "callTheSeanAI", "callBaseten"
]
for fn in functions:
    if f"async function {fn}" in cf_code:
        print(f"  [OK] {fn}")
    else:
        print(f"  [MISSING] {fn}")
        all_found = False

print("\nChecking routing branches in /api/ai/execute...")
prefixes = [
    'model.startsWith("sambanova/")',
    'model.startsWith("requesty/")',
    'model.startsWith("nvidia/")',
    'model.startsWith("edenai/")',
    'model.startsWith("friendli/")',
    'model.startsWith("thesean/")',
    'model.startsWith("baseten/")'
]
for p in prefixes:
    if p in cf_code:
        print(f"  [OK] {p}")
    else:
        print(f"  [MISSING] {p}")
        all_found = False

if all_found:
    print("\nAll Cloudflare Worker Gateway additions verified successfully!")
else:
    print("\nSome items missing!")
    sys.exit(1)
