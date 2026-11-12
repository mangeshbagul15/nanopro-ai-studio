with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'badge.textContent = `${data.total_models || 1468}+ Models Unified Mesh`;',
    'badge.textContent = "1,900+ Models Unified Mesh";'
)
text = text.replace(
    'badge.textContent = `${data.total_models || 1900}+ Models Unified Mesh`;',
    'badge.textContent = "1,900+ Models Unified Mesh";'
)

with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated badge text logic in app/ui/global_ai_lab_view.py!")
