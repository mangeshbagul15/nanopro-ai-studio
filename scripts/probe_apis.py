import urllib.request
import ssl
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 1. Probe Defapi.org
try:
    req = urllib.request.Request('https://defapi.org/', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    scripts = re.findall(r'src="(/_next/static/chunks/[^"]+)"', html)
    print('Found chunks:', len(scripts))
    found_urls = set()
    for s in scripts:
        try:
            s_req = urllib.request.Request('https://defapi.org' + s, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(s_req, context=ctx, timeout=5) as s_resp:
                js = s_resp.read().decode('utf-8', errors='ignore')
                urls = re.findall(r'https?://[a-zA-Z0-9\.\-_/]+', js)
                for u in urls:
                    if 'api' in u or 'v1' in u:
                        found_urls.add(u)
                if 'baseUrl' in js or 'base_url' in js or 'defapi' in js:
                    for m in re.finditer(r'(https?://[^\s"\'<>]+)', js):
                        found_urls.add(m.group(1))
        except Exception:
            pass
    print("Found Defapi endpoints/URLs:", list(found_urls)[:15])
except Exception as e:
    print("Defapi scrape error:", e)

# 2. Test candidate endpoints with the token
endpoints = [
    'https://defapi.org/api/v1/models',
    'https://defapi.org/v1/models',
    'https://defapi.org/api/models',
    'https://api.defapi.org/v1/models',
    'https://gateway.defapi.org/v1/models',
]
for ep in endpoints:
    try:
        req = urllib.request.Request(ep, headers={
            'Authorization': 'Bearer dk-8ad11ada1f8d9ea75cc20cb1fc55cbed',
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            print("SUCCESS endpoint:", ep, resp.status)
            body = resp.read().decode('utf-8')
            print("Response:", body[:300])
    except Exception as e:
        print("Failed endpoint:", ep, e)
