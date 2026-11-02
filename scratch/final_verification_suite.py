import urllib.request, json, sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'https://mangesh-nanopro.mangeshbagul15.workers.dev'
HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("==================================================")
print("RUNNING FINAL END-TO-END VERIFICATION SUITE")
print("Target:", BASE_URL)
print("==================================================")

# 1. Test Password Login with various identifiers
identifiers = [
    ('nanopro', 'Divyam@123'),
    ('mangeshbagul15@gmail.com', 'Divyam@123'),
    ('+918433755448', 'Divyam@123'),
    ('8433755448', 'Divyam@123'),
    ('nanopro', 'Admin@123')
]

for ident, pwd in identifiers:
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login",
        headers=HEADERS,
        data=json.dumps({'username': ident, 'password': pwd}).encode('utf-8'))
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
        status = data.get('status')
        uname = data.get('user', {}).get('username')
        role = data.get('user', {}).get('role')
        assert status == 'success', f"Failed login for {ident}: {data}"
        assert role == 'admin', f"Role not admin for {ident}: {role}"
        print(f"✅ Password Login [{ident}]: {status} (User: {uname}, Role: {role})")

# 2. Test WhatsApp OTP flow
print("\n--- WhatsApp OTP Flow ---")
req = urllib.request.Request(f"{BASE_URL}/api/auth/otp/send",
    headers=HEADERS,
    data=json.dumps({'identifier': '+918433755448', 'channel': 'whatsapp'}).encode('utf-8'))
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    assert data.get('status') == 'success', f"Send OTP failed: {data}"
    print(f"✅ WhatsApp Send OTP: {data.get('status')} to {data.get('identifier')}")

# Retrieve OTP from DB
conn = sqlite3.connect('app/database/studio_memory.db')
c = conn.cursor()
c.execute('SELECT otp_code FROM auth_otps WHERE identifier = ? ORDER BY created_at DESC LIMIT 1', ('+918433755448',))
otp = c.fetchone()[0]
print(f"🔍 Latest OTP in SQLite DB: {otp}")

# Verify OTP
req = urllib.request.Request(f"{BASE_URL}/api/auth/otp/verify",
    headers=HEADERS,
    data=json.dumps({'identifier': '+918433755448', 'otp_code': otp, 'channel': 'whatsapp'}).encode('utf-8'))
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    assert data.get('status') == 'success', f"Verify OTP failed: {data}"
    print(f"✅ WhatsApp Verify OTP: {data.get('status')} (User: {data.get('user', {}).get('username')}, Role: {data.get('user', {}).get('role')})")

# 3. Test Direct Google Official Sign-In
print("\n--- Direct Google Official Sign-In ---")
req = urllib.request.Request(f"{BASE_URL}/api/auth/google-login",
    headers=HEADERS,
    data=json.dumps({
        'email': 'mangeshbagul15@gmail.com',
        'full_name': 'Mangesh Bagul'
    }).encode('utf-8'))
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    assert data.get('status') == 'success', f"Google login failed: {data}"
    print(f"✅ Google Official Login: {data.get('status')} (User: {data.get('user', {}).get('username')}, Role: {data.get('user', {}).get('role')})")

# 4. Test Clerk Google Verification
print("\n--- Clerk Google SSO Verification ---")
req = urllib.request.Request(f"{BASE_URL}/api/auth/clerk-verify",
    headers=HEADERS,
    data=json.dumps({
        'user_id': 'user_live_clerk_test',
        'email': 'mangeshbagul15@gmail.com',
        'full_name': 'Mangesh Bagul'
    }).encode('utf-8'))
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
    assert data.get('status') == 'success', f"Clerk verify failed: {data}"
    print(f"✅ Clerk Google SSO: {data.get('status')} (User: {data.get('user', {}).get('username')}, Role: {data.get('user', {}).get('role')})")

# 5. Test Authenticated Dashboard Retrieval
print("\n--- Authenticated Dashboard Gating ---")
token = data.get('session_token')
req = urllib.request.Request(f"{BASE_URL}/?token={token}", headers=HEADERS)
with urllib.request.urlopen(req, timeout=15) as resp:
    dash_html = resp.read().decode('utf-8', errors='ignore')
    assert len(dash_html) > 1000000, f"Dashboard HTML too short: {len(dash_html)}"
    print(f"✅ Dashboard Loaded Successfully: {len(dash_html)} bytes (Full 2.9 MB Studio)")

print("\n==================================================")
print("🎉 ALL TESTS PASSED WITH 100% SUCCESS!")
print("==================================================")
