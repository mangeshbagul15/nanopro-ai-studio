with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    code = f.read()

loc = {}
exec(code, loc)
fresh_html = loc['get_global_ai_lab_html']()
print("fresh_html length:", len(fresh_html))

with open('deploy/complete_nanopro_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = '<!-- VIEW: GLOBAL AI LAB (FEATURE 53) -->'
s_idx = text.find(start_marker)
end_marker = '<!-- VIEW: 3. AI AGENT CONTROL CENTER -->'
e_idx = text.find(end_marker, s_idx)

if s_idx != -1 and e_idx != -1:
    replacement = f"{fresh_html}\n\n        "
    new_text = text[:s_idx] + replacement + text[e_idx:]
    with open('deploy/complete_nanopro_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Successfully replaced in deploy/complete_nanopro_dashboard.html!")
else:
    print(f"Error: s_idx={s_idx}, e_idx={e_idx}")
