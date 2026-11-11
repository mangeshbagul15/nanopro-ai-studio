"""Check what the live Render and Worker actually serve at / for an authenticated session."""
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def env_value(path, key):
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith(key + "="):
                val = line.split("=", 1)[1].strip()
                if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                    val = val[1:-1]
                return val
    return ""


PASSWORD = env_value(os.path.join(ROOT, ".env"), "NANOPRO_ADMIN_PASSWORD")
assert PASSWORD, "admin password missing from .env"


def post_json(url, payload, headers=None):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        return exc.code, {"error": body[:200]}


def get(url, token=None):
    req = urllib.request.Request(url)
    if token:
        req.add_header("X-Session-Token", token)
    req.add_header("Accept", "text/html,application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()


BASES = {
    "render": "https://nanopro-studio.onrender.com",
    "worker": "https://mangesh-nanopro.mangeshbagul15.workers.dev",
    "local": "http://127.0.0.1:8000",
}

for name, base in BASES.items():
    status, payload = post_json(base + "/api/auth/login", {"username": "nanopro", "password": PASSWORD})
    token = payload.get("session_token") or ""
    print(f"{name} login status={status} token={'yes' if token.startswith('np_sess_') else 'no'}")
    if not token:
        continue

    st, headers, body = get(base + "/", token)
    text = body.decode("utf-8", "replace")
    markers = {
        "session_bridge": "X-Session-Token" in text,
        "isTaskOn": "isTaskOn" in text,
        "v2_cards": 'id="cards"' in text or "agent station" in text.lower(),
        "legacy_marker": "complete_nanopro" in text,
        "g_state_clear": "Max-Age=0" in text and "g_state" in text,
    }
    print(f"  / status={st} bytes={len(body)} mode={headers.get('X-NanoPro-Mode')} etag={headers.get('ETag')}")
    print(f"  markers={markers}")

    st2, h2, b2 = get(base + "/api/runtime/profile", token)
    prof = {}
    try:
        prof = json.loads(b2.decode("utf-8", "replace"))
    except Exception:
        pass
    keep = {k: prof.get(k) for k in ("runtime_mode", "host", "cloud", "profile", "service", "boot_time", "commit", "git_sha") if k in prof}
    print(f"  profile status={st2} keys={keep}")
    print()
