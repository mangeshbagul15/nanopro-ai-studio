import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('window.ailabLoadHistory')
if s != -1:
    print(text[s:s+1500])
else:
    print('ailabLoadHistory not found')
