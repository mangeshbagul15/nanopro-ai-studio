import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/ui/data_modeling_ai.py', 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('window.dmRenderTree = function')
print(text[s:s+3000])
