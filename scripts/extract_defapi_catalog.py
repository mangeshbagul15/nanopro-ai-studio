import urllib.request
import ssl
import json
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Let's inspect the static chunks to extract all model IDs defined in Defapi
req = urllib.request.Request('https://defapi.org/', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

chunk_urls = re.findall(r'src="(/_next/static/chunks/[^"]+)"', html)
print('Found chunks:', len(chunk_urls))

all_models = set()
for c in chunk_urls:
    try:
        s_req = urllib.request.Request('https://defapi.org' + c, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(s_req, context=ctx, timeout=5) as s_resp:
            js = s_resp.read().decode('utf-8', errors='ignore')
            # Look for model path patterns like /model/<org>/<name> or "id":"..."
            found = re.findall(r'/model/([a-zA-Z0-9_\-\./]+)', js)
            for f in found:
                all_models.add(f.strip('/'))
            # Also find strings like "provider/model"
            found_ids = re.findall(r'["\']((?:google|anthropic|openai|meta|mistral|deepseek|midjourney|flux|kling|sora|runway)/[a-zA-Z0-9_\-\.]+)["\']', js)
            for f in found_ids:
                all_models.add(f)
    except Exception:
        pass

print('Extracted Defapi models count:', len(all_models))
for m in sorted(list(all_models)):
    print('Defapi Model:', m)
