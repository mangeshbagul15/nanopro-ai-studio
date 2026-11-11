"""Read-only feature probe through the Worker with header auth. Prints no secrets."""
import json
import sys
import urllib.error
import urllib.request

BASE = "https://mangesh-nanopro.mangeshbagul15.workers.dev"


def env_value(path, key):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def call(path, token=None, body=None, method=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body else None,
                                 method=method or ("POST" if body else "GET"))
    req.add_header("User-Agent", "NanoProAudit/1.0")
    req.add_header("Accept", "application/json")
    if body:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("X-Session-Token", token)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "ignore")
    except Exception as exc:
        return 0, type(exc).__name__


def brief(raw, limit=220):
    try:
        d = json.loads(raw)
    except Exception:
        return raw[:limit].replace("\n", " ")
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            if isinstance(v, list):
                out[k] = f"list[{len(v)}]"
            elif isinstance(v, dict):
                out[k] = f"dict[{len(v)}]"
            else:
                out[k] = str(v)[:60]
        return json.dumps(out)[:limit]
    return str(d)[:limit]


def main():
    user = env_value(".env", "NANOPRO_ADMIN_USERNAME") or "nanopro"
    status, raw = call("/api/auth/login", body={"username": user,
                                                "password": env_value(".env", "NANOPRO_ADMIN_PASSWORD")})
    token = (json.loads(raw or "{}") or {}).get("session_token")
    print("login", status, "token", bool(token))
    if not token:
        return 2
    paths = [
        "/api/auth/google-config",
        "/api/auth/clerk-config",
        "/api/communication/whatsapp/status",
        "/api/communication/smtp/senders",
        "/api/emails/delivery-history",
        "/api/communication/telegram/test",
        "/api/data_modeling/status",
        "/api/operations/state",
        "/api/video/2026_matrix_catalog",
        "/api/payments/config",
        "/api/payments/plans",
        "/api/rca/incidents",
        "/api/agents/list",
        "/api/scheduler/tasks",
        "/api/database/databases",
        "/api/news/articles",
    ]
    for p in paths:
        s, b = call(p, token)
        print(f"{s} {p} :: {brief(b)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
