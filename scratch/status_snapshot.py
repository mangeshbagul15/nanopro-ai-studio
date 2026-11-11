"""Read-only live status snapshot. Never prints tokens, keys, or phone numbers."""
import json
import urllib.error
import urllib.request

BASE = "https://nanopro-studio.onrender.com"
SENSITIVE = ("token", "secret", "key", "password", "phone", "chat_id", "mobile", "email")


def env_value(path, key):
    try:
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def get(path, cookie=None, timeout=45):
    req = urllib.request.Request(BASE + path)
    req.add_header("User-Agent", "NanoProStatus/1.0")
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "ignore") or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, {"error": str(exc.code)}
    except Exception as exc:
        return 0, {"error": type(exc).__name__}


def slim(value, depth=0):
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        return value[:48]
    if isinstance(value, list):
        return {"len": len(value)}
    if isinstance(value, dict):
        if depth > 1:
            return {"keys": len(value)}
        out = {}
        for i, (k, v) in enumerate(value.items()):
            if i > 10:
                out["..."] = len(value) - 10
                break
            if any(s in k.lower() for s in SENSITIVE):
                out[k] = "set" if v else "unset"
            else:
                out[k] = slim(v, depth + 1)
        return out
    return type(value).__name__


def main():
    password = env_value(".env", "NANOPRO_ADMIN_PASSWORD")
    body = json.dumps({"username": "nanopro", "password": password}).encode()
    req = urllib.request.Request(BASE + "/api/auth/login", data=body,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "NanoProStatus/1.0"})
    token = json.loads(urllib.request.urlopen(req, timeout=45).read().decode()).get("session_token") or ""
    if not token:
        print("login_failed")
        return 1
    cookie = "nanopro_session=" + token

    checks = [
        ("health", "/api/health"),
        ("profile", "/api/runtime/profile"),
        ("monitoring", "/api/monitoring/health"),
        ("agents", "/api/agents/list"),
        ("tasks", "/api/scheduler/tasks"),
        ("data_modeling", "/api/data_modeling/status"),
        ("payments_config", "/api/payments/config"),
        ("payments_plans", "/api/payments/plans"),
        ("payments_history", "/api/payments/history?limit=5"),
        ("telegram", "/api/telegram/diagnose"),
        ("whatsapp_status", "/api/communication/whatsapp/status"),
        ("whatsapp_diag", "/api/whatsapp/diagnostics"),
        ("email_history", "/api/emails/delivery-history"),
        ("rca", "/api/rca/incidents"),
    ]
    for name, path in checks:
        status, data = get(path, cookie)
        print(name, status, json.dumps(slim(data))[:420])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
