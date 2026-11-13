with open('deploy/complete_nanopro_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()
idx = text.find('id="ailabAirflowModal"')
print(text[idx-50:idx+450])
