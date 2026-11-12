with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for j in range(2640, 2665):
    print(f'{j+1}: {repr(lines[j])}')
