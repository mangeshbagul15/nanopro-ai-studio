import urllib.request
import json
import sys

base_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/api/ai/execute"

tests = [
    {
        "name": "Domain 1: Image & Multimodal Generative Studio",
        "prompt": "futuristic cyber ai lab chi image banva",
        "expected_model": "google/gemini-2.5-flash:vision-generative"
    },
    {
        "name": "Domain 2: Autonomous Computer Use Agent (CUA) End-to-End",
        "prompt": "side screen share madhe google search kara",
        "expected_model": "anthropic/claude-3.7-sonnet:computer-use"
    },
    {
        "name": "Domain 3: Enterprise Data Engineering & Lakehouse",
        "prompt": "data engineering pipeline snowflake aws eod sod ingestion",
        "expected_model": "anthropic/claude-3.7-sonnet:data-architect"
    },
    {
        "name": "Domain 4: Deep Mathematical Reasoning & Accuracy",
        "prompt": "pareto algorithm formula and accuracy proof",
        "expected_model": "deepseek/deepseek-r1:reasoning-sota"
    },
    {
        "name": "Domain 5: Code & Python Specialist",
        "prompt": "python def binary_search and class",
        "expected_model": "qwen/qwen-2.5-coder-32b-instruct"
    }
]

print("=== TESTING LIVE CLOUDFLARE WORKER ROUTING ===")
all_passed = True
for t in tests:
    try:
        data = json.dumps({"prompt": t["prompt"]}).encode("utf-8")
        req = urllib.request.Request(
            base_url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "NanoPro-Tester/1.0"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            routed = body.get("model_executed") or body.get("model_routed")
            model_name = body.get("model_name", "")
            dur = body.get("duration_ms")
            passed = (routed == t["expected_model"])
            if not passed:
                all_passed = False
            status_tag = "[PASS]" if passed else "[FAIL]"
            print(f"{status_tag} {t['name']}")
            print(f"   Prompt: '{t['prompt']}'")
            print(f"   Executed Model: {routed} (Expected: {t['expected_model']})")
            print(f"   Model Name: {model_name.encode('ascii', 'ignore').decode('ascii')} | Latency: {dur}ms\n")
    except Exception as e:
        print(f"[FAIL] {t['name']} failed with error: {e}\n")
        all_passed = False

if all_passed:
    print("SUCCESS: ALL 5 SPECIALIZED MODEL DOMAINS ROUTED AND RESPONDED PERFECTLY!")
else:
    print("WARNING: Some domains did not match expected models.")
