import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://defapi.org/', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html)
print('All links:', [l for l in links if not l.startswith('#')][:25])

# Also check clerk or api routes in the html
api_refs = re.findall(r'["\'](/api/[^"\']+)["\']', html)
print('API refs:', set(api_refs))
