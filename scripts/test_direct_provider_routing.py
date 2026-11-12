import urllib.request
import json
import time

url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/api/ai/execute"

test_cases = [
    {
        "desc": "1. Direct DeepInfra Routing (deepinfra/meta-llama/Llama-3.3-70B-Instruct)",
        "payload": {
            "prompt": "Explain Snowflake clustering keys in 1 sentence.",
            "model": "deepinfra/meta-llama/Llama-3.3-70B-Instruct"
        }
    },
    {
        "desc": "2. Direct Mistral AI Routing (mistral/codestral-latest)",
        "payload": {
            "prompt": "Write a python one-liner to flatten a list of lists.",
            "model": "mistral/codestral-latest"
        }
    },
    {
        "desc": "3. Direct Groq LPU Routing (groq/qwen3.8-27b)",
        "payload": {
            "prompt": "What is the capital of Maharashtra?",
            "model": "groq/qwen3.8-27b"
        }
    },
    {
        "desc": "4. Direct DeepSeek Routing (deepseek/deepseek-chat)",
        "payload": {
            "prompt": "Define ACID properties in database management.",
            "model": "deepseek/deepseek-chat"
        }
    }
]

print("=== TESTING LIVE DIRECT PROVIDER ROUTING ON CLOUDFLARE WORKER ===")
for tc in test_cases:
    t0 = time.time()
    try:
        data = json.dumps(tc["payload"]).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "NanoPro-LiveTest/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read().decode("utf-8"))
            dur = (time.time() - t0) * 1000
            model_executed = res.get("model_executed")
            model_name = res.get("model_name", "")
            response_text = res.get("response", "").strip()
            
            print(f"\n[PASS] {tc['desc']}")
            print(f"       Status: {r.status} | Roundtrip: {dur:.1f}ms")
            print(f"       Executed Model: {model_executed}")
            print(f"       Live Output ({len(response_text)} chars):")
            print(f"       {response_text[:150].encode('ascii', 'backslashreplace').decode('ascii')}...\n")
    except Exception as e:
        print(f"\n[FAIL] {tc['desc']} failed: {e}\n")
