import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    text = f.read()

m_start = text.find('id="ailabModelModal"')
print('ailabModelModal at:', m_start)

# Let's see the lines around m_start
lines = text[m_start:m_start+1500].splitlines()
for i, l in enumerate(lines[:35]):
    print(f"{i:02d}: {l}")
