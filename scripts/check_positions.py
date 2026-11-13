with open('deploy/complete_nanopro_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

view_start = text.find('id="view-global_ai_lab"')
view_end = text.find('<!-- VIEW: 3. AI AGENT CONTROL CENTER -->')
modal_pos = text.find('id="ailabAirflowModal"')
btn_pos = text.find('ailabOpenAirflowModal()')

print('view_start:', view_start)
print('view_end:', view_end)
print('modal_pos:', modal_pos)
print('btn_pos:', btn_pos)
print('Is modal inside view?', view_start < modal_pos < view_end)
print('Is btn inside view?', view_start < btn_pos < view_end)
