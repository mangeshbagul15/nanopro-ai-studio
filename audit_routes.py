import re
import os

with open('main.py', 'r', encoding='utf-8') as f:
    main_code = f.read()

with open('app/ui/dashboard.py', 'r', encoding='utf-8') as f:
    dash_code = f.read()

# Find all routes in main.py
api_routes = set(re.findall(r'@app\.(?:get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]', main_code))
print(f'Total FastAPI routes defined in main.py: {len(api_routes)}')

# Find all fetch calls in dashboard.py
# 1. Simple quotes: fetch('/api/...')
fetch_quotes = set(re.findall(r'fetch\([\'"]([^\'"?]+)', dash_code))
# 2. Template strings: fetch(`/api/...`)
fetch_templates = set(re.findall(r'fetch\(`([^`?]+)', dash_code))
# 3. Concatenations: fetch('/api/' + ...)
fetch_con_prefix = set(re.findall(r'fetch\([\'"]([^\'"]+)[\'"]\s*\+', dash_code))

all_fetches = fetch_quotes | fetch_templates | fetch_con_prefix
print(f'Total unique fetch patterns found: {len(all_fetches)}')

unmatched = []
for call in sorted(all_fetches):
    # Normalize call (replace ${...} with dummy param)
    norm_call = re.sub(r'\$\{[^}]+\}', '123', call)
    matched = False
    for r in api_routes:
        r_regex = '^' + re.sub(r'\{[^}]+\}', r'[^/]+', r) + '$'
        if re.match(r_regex, norm_call) or norm_call.startswith(r.rstrip('/')):
            matched = True
            break
    if not matched:
        unmatched.append(call)

print('\nUnmatched fetch calls in dashboard:')
for u in unmatched:
    print('  -', u)
