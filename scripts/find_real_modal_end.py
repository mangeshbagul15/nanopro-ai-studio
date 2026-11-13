import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find ailabModelModalGrid
grid_pos = text.find('id="ailabModelModalGrid"')
print('grid_pos at:', grid_pos)

# Look at lines after grid_pos
lines = text[grid_pos:grid_pos+1000].splitlines()
for i, l in enumerate(lines[:25]):
    print(f"{i:02d}: {l}")
