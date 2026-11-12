with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'fetch\([^\)]+\)', text)
for m in matches:
    if 'api' in m or 'model' in m:
        print(m)
