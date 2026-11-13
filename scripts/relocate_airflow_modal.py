"""Cleanly relocate ailabAirflowModal outside ailabModelModal."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'app/ui/global_ai_lab_view.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Locate ailabAirflowModal block
start_marker = '<!-- AIRFLOW ORCHESTRATOR & SFTP HUB MODAL -->'
end_marker = '</div>\n</div>\n\n    <div class="ailab-modal-search">'

s_idx = text.find(start_marker)
# Find the end of ailabAirflowModal
# ailabAirflowModal ends with:
#     <div class="ailab-modal-footer">
#       <div style="font-size:11.5px;color:#94A3B8;">
#         Central Command Pane • Snowflake BANK_DB • AWS S3 • Airflow • SFTP
#       </div>
#       <button type="button" class="ailab-btn-primary" onclick="ailabCloseAirflowModal()">Close</button>
#     </div>
#   </div>
# </div>

modal_footer_marker = '<button type="button" class="ailab-btn-primary" onclick="ailabCloseAirflowModal()">Close</button>\n    </div>\n  </div>\n</div>'
e_idx = text.find(modal_footer_marker, s_idx) + len(modal_footer_marker)

print("s_idx:", s_idx)
print("e_idx:", e_idx)

airflow_modal_html = text[s_idx:e_idx].strip()
print("airflow_modal_html length:", len(airflow_modal_html))

# Remove airflow_modal_html from its current trapped location
text_without_modal = text[:s_idx] + text[e_idx:]

# Find where ailabModelModal ends
# Lines 07-08:
#     <div class="ailab-modal-footer">
#       <span>⚡ Single AUTO Engine evaluates Pareto Frontier in < 3.0ms</span>
#       <span style="color:#10B981;">🛡️ 429 Shield Active • Render RAM: 0 MB</span>
#     </div>
#   </div>
# </div>

model_modal_end = '🛡️ 429 Shield Active • Render RAM: 0 MB</span>\n    </div>\n  </div>\n</div>'
end_pos = text_without_modal.find(model_modal_end)
if end_pos == -1:
    # Try alternate line endings
    model_modal_end = '🛡️ 429 Shield Active • Render RAM: 0 MB</span>\r\n    </div>\r\n  </div>\r\n</div>'
    end_pos = text_without_modal.find(model_modal_end)

print("model_modal_end found at:", end_pos)
insert_pos = end_pos + len(model_modal_end)

# Insert airflow_modal_html right after ailabModelModal closes!
final_text = text_without_modal[:insert_pos] + "\n\n" + airflow_modal_html + "\n\n" + text_without_modal[insert_pos:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(final_text)

print("SUCCESS: Relocated ailabAirflowModal to valid DOM position!")
