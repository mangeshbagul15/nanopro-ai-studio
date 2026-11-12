import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'DOMContentLoaded', text)]
for m in matches:
    print('--- MATCH ---')
    print(text[m-50:m+200])
