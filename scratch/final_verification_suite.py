"""Negative security regression suite — every legacy auth bypass must fail."""
import json
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://mangesh-nanopro.mangeshbagul15.workers.dev"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

results = []


def call(path, payload=None, method="POST"):
    time.sleep(0.8)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(BASE_URL + path, headers=HEADERS, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            body = json.loads(body)
        except Exception:
            pass
        return exc.code, body


def expect(name, path, payload=None, method="POST", codes=(400, 401, 403, 405), error_text=None):
    status, body = call(path, payload, method)
    ok = status in codes
    if isinstance(body, dict) and body.get("status") == "error" and status == 200:
        ok = True
    if error_text and isinstance(body, dict):
        ok = ok and error_text in str(body.get("error", ""))
    results.append((name, ok, status, body))
    print(("PASS" if ok else "FAIL"), name, status, body)


print("=" * 60)
print("NanoPro negative security regression —", BASE_URL)
print("=" * 60)

for username, password in [
    ("admin", "Admin@123"),
    ("nanopro", "nanopro"),
    ("admin", "admin"),
    ("nanopro", "123456"),
    ("admin", "NanoPro@2026"),
]:
    expect(f"reject legacy login {username}/{password}", "/api/auth/login",
           {"username": username, "password": password}, error_text="Invalid username or password")

expect("GET login route removed", "/api/auth/login?username=admin&password=Admin@123", method="GET", codes=(405,))

expect("admin users API requires session", "/api/admin/users/list", method="GET", codes=(401, 403))
expect("vault list requires session", "/api/vault/list", method="GET", codes=(401, 403))
expect("telegram diagnostics requires session", "/api/telegram/send_diagnostics_now", codes=(401, 403))
expect("amazon whatsapp test requires session", "/api/amazon/test_whatsapp_price_drop", codes=(401, 403))

expect("hardcoded OTP rejected", "/api/auth/otp/verify",
       {"identifier": "+918433755448", "otp_code": "123456", "channel": "whatsapp"},
       error_text="Invalid or expired OTP")

expect("google login without credential rejected", "/api/auth/google-login", {}, codes=(401, 400))

expect("clerk email-only rejected", "/api/auth/clerk-verify",
       {"email": "mangeshbagul15@gmail.com"}, error_text="Clerk session verification failed")

fake_req = urllib.request.Request(
    BASE_URL + "/api/admin/users/list",
    headers={**HEADERS, "Authorization": "Bearer np_sess_fake123"},
)
try:
    with urllib.request.urlopen(fake_req, timeout=20) as fake_resp:
        fake_status = fake_resp.status
except urllib.error.HTTPError as exc:
    fake_status = exc.code
fake_ok = fake_status in (401, 403)
results.append(("fake session rejected", fake_ok, fake_status, None))
print("PASS" if fake_ok else "FAIL", "fake session rejected", fake_status)

failed = [name for name, ok, _, _ in results if not ok]
print("=" * 60)
print(f"{len(results) - len(failed)}/{len(results)} checks passed")
if failed:
    print("FAILED:", failed)
    sys.exit(1)
print("ALL SECURITY CHECKS PASSED")
