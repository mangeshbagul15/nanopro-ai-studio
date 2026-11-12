import urllib.request
import json
import time

url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/api/ai/execute"

test_cases = [
    {
        "desc": "1. Live Data Engineering Pipeline (AUTO -> Llama 3.3 70B)",
        "payload": {
            "prompt": "How to handle Snowflake dynamic tables with CDC stream deduplication for core banking transactions?",
            "model": "auto"
        }
    },
    {
        "desc": "2. Live Python & DuckDB Coding (AUTO -> Qwen 2.5 Coder 32B)",
        "payload": {
            "prompt": "Write a Python script using duckdb to create a table from json data and calculate average transaction amount by branch.",
            "model": "auto"
        }
    },
    {
        "desc": "3. Live Direct Selection (Explicit openai/gpt-4o-mini)",
        "payload": {
            "prompt": "Explain the Pareto Frontier mathematical formulation in 2 clear sentences.",
            "model": "openai/gpt-4o-mini"
        }
    },
    {
        "desc": "4. Live Generative Visual Studio (Image Request)",
        "payload": {
            "prompt": "futuristic cyber ai lab chi mast image banva",
            "model": "auto"
        }
    }
]

print("=== TESTING LIVE REAL OPENROUTER INFERENCE ON CLOUDFLARE WORKER ===")
for tc in test_cases:
    t0 = time.time()
    try:
        data = json.dumps(tc["payload"]).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "NanoPro-LiveTest/1.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.loads(r.read().decode("utf-8"))
            dur = (time.time() - t0) * 1000
            model_executed = res.get("model_executed")
            model_name = res.get("model_name", "")
            response_text = res.get("response", "").strip()
            
            print(f"\n[PASS] {tc['desc']}")
            print(f"       Status: {r.status} | Roundtrip: {dur:.1f}ms")
            print(f"       Executed Model: {model_executed}")
            print(f"       Model Name: {model_name.encode('ascii', 'ignore').decode('ascii')}")
            print(f"       Live Output ({len(response_text)} chars):")
            print(f"       {response_text[:200].encode('ascii', 'backslashreplace').decode('ascii')}...\n")
    except Exception as e:
        print(f"\n[FAIL] {tc['desc']} failed: {e}\n")
