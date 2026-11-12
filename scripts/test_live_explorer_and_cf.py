import urllib.request
import json
import time

base_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev"

print("--- 1. Testing High-Speed Indexed Chat History Lookup (< 5ms) ---")
t0 = time.time()
try:
    req = urllib.request.Request(f"{base_url}/api/ai/history/chats/chat_core_seed", headers={"User-Agent": "NanoPro/1.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        dur = (time.time() - t0) * 1000
        data = json.loads(r.read().decode("utf-8"))
        print(f"Status: {r.status} | Latency: {dur:.1f}ms")
        print(f"Storage Engine: {data.get('storage_engine')}")
        print(f"Messages count: {len(data.get('messages', []))}")
        print(f"First message preview: {data.get('messages', [{}])[0].get('content')[:60]}...")
except Exception as e:
    print("History error:", e)

print("\n--- 2. Testing Data Modeling Explorer Catalog (AWS, Snowflake, BigQuery, DuckDB) ---")
t0 = time.time()
try:
    req = urllib.request.Request(f"{base_url}/api/ai/explorer/catalog", headers={"User-Agent": "NanoPro/1.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        dur = (time.time() - t0) * 1000
        data = json.loads(r.read().decode("utf-8"))
        dbs = data.get("databases", [])
        print(f"Status: {r.status} | Latency: {dur:.1f}ms")
        print(f"Databases count: {len(dbs)}")
        for db in dbs:
            schemas = db.get("schemas", [])
            total_tables = sum(len(s.get("tables", [])) for s in schemas)
            print(f"  • {db.get('icon')} {db.get('name')}: {len(schemas)} schemas, {total_tables} tables")
except Exception as e:
    print("Explorer error:", e)

print("\n--- 3. Testing Cloudflare Workers AI Direct Edge Inference ---")
t0 = time.time()
try:
    payload = json.dumps({
        "prompt": "Explain Snowflake vs BigQuery partition pruning in 1 sentence.",
        "model": "@cf/meta/llama-3.1-8b-instruct"
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/api/ai/execute",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "NanoPro/1.0"}
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        dur = (time.time() - t0) * 1000
        res = json.loads(r.read().decode("utf-8"))
        print(f"Status: {r.status} | Roundtrip: {dur:.1f}ms")
        print(f"Model executed: {res.get('model_executed')} | Lab: {res.get('lab_name')}")
        print(f"Output: {res.get('response', '')[:120].strip()}...")
except Exception as e:
    print("CF Workers AI error:", e)
