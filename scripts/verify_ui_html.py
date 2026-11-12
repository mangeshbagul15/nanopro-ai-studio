with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    code = f.read()
loc = {}
exec(code, loc)
html = loc['get_global_ai_lab_html']()
print('Length of html:', len(html))
print('Has ailabExplorer:', 'id="ailabExplorer"' in html)
print('Has ailabToggleExplorer:', 'ailabToggleExplorer' in html)
print('Has 2,150+:', '2,150+' in html)
