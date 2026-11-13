import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('deploy/complete_nanopro_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function ailabEnsureMermaid')
print(text[idx-50:idx+600])
