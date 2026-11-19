import urllib.request
import ssl
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://defapi.org/search?sort=created_at&order=desc'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

models = re.findall(r'/model/([a-zA-Z0-9_\-\./]+)', html)
print('Unique models found on search page:', len(set(models)))
for m in sorted(list(set(models))):
    print(' -', m)
