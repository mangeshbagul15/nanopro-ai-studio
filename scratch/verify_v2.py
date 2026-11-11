"""Live check for the v2 shell. Never prints secrets or session tokens."""
import json
import os
import sys
import time
import urllib.request

BASE = "https://nanopro-studio.onrender.com"


def env_value(path, key):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return os.environ.get(key, "")


def call(path, data=None, cookie=None, method=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(BASE + path, data=body, method=method or ("POST" if data else "GET"))
    req.add_header("User-Agent", "NanoProVerify/1.0")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore"), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "ignore"), dict(exc.headers)


def main():
    password = env_value(".env", "NANOPRO_ADMIN_PASSWORD")
    if not password:
        print("NO_ADMIN_PASSWORD")
        return 2
    status, _, _ = call("/api/health")
    print("health", status)
    if status != 200:
        return 3
    status, body, _ = call("/api/auth/login", {"username": "nanopro", "password": password})
    token = (json.loads(body or "{}") or {}).get("session_token")
    print("login", status, "token_present", bool(token))
    if status != 200 or not token:
        return 4
    cookie = "nanopro_session=" + token
    status, html, _ = call("/", cookie=cookie)
    is_v2 = "NANOPRO OS" in html and "Control tower" in html
    print("root", status, "is_v2", is_v2, "ask_bar", 'id="ask"' in html)
    if not is_v2:
        return 5
    status, legacy, _ = call("/legacy", cookie=cookie)
    print("legacy", status, "old_ui", ("Universal Tech Video" in legacy) or ("data-modeling" in legacy), "bytes", len(legacy))
    status, _, headers = call("/legacy")
    print("legacy_anon", status, "location", headers.get("Location") or headers.get("location"))

    status, anon_body, _ = call("/api/v2/chat", {"message": "status"})
    print("chat_anon", status, "gated", status == 401)
    if status == 404:
        print("chat_route_not_deployed_yet")
        return 5

    status, body, _ = call("/api/v2/chat", {"message": "status"}, cookie=cookie)
    data = json.loads(body or "{}")
    print("chat_status", status, "intent", data.get("intent"), "model", data.get("model"),
          "chain", data.get("chain"), "answer", (data.get("answer") or "")[:90])
    if "chain" not in data:
        print("chain_field_not_deployed_yet")
        return 5

    status, body, _ = call("/api/v2/chat", {"message": "Explain what the security guards protect."}, cookie=cookie)
    data = json.loads(body or "{}")
    print("chat_ai", status, "intent", data.get("intent"), "model", data.get("model"),
          "chain", data.get("chain"), "latency_ms", data.get("latency_ms"),
          "answer_chars", len(data.get("answer") or ""))
    return 0


if __name__ == "__main__":
    for attempt in range(20):
        code = main()
        if code in (0, 2, 4):
            break
        time.sleep(20)
    sys.exit(code)
