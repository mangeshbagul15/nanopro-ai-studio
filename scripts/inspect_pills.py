import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('class="ailab-modal-pills"')
print(text[s:s+1200])
