import re

with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace CSS from /* ---------------- Topbar ---------------- */ down to /* ---------------- Layout Body ---------------- */
new_css = """/* ---------------- Topbar (Single-Row Modern Responsive Header) ---------------- */
#view-global_ai_lab .ailab-topbar {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  gap: 10px !important;
  height: 52px !important;
  min-height: 52px !important;
  max-height: 52px !important;
  padding: 0 16px !important;
  background: linear-gradient(180deg, #0B1119 0%, #080D14 100%) !important;
  border-bottom: 1.5px solid rgba(139, 92, 246, 0.3) !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6) !important;
  flex-shrink: 0 !important;
  z-index: 100 !important;
  position: relative !important;
  overflow-x: auto !important;
  overflow-y: hidden !important;
  box-sizing: border-box !important;
  white-space: nowrap !important;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
#view-global_ai_lab .ailab-topbar::-webkit-scrollbar {
  display: none;
}
#view-global_ai_lab .ailab-topbar,
#view-global_ai_lab .ailab-topbar *,
#view-global_ai_lab .ailab-topbar button,
#view-global_ai_lab .ailab-topbar span,
#view-global_ai_lab .ailab-topbar select {
  white-space: nowrap !important;
}

#view-global_ai_lab .ailab-topbar-left {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  flex-shrink: 0 !important;
  min-width: max-content !important;
}
#view-global_ai_lab .ailab-brand {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  font-weight: 800 !important;
  font-size: 13.5px !important;
  color: #F8FAFC !important;
  text-decoration: none !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-brand-badge {
  font-size: 9.5px !important;
  font-weight: 800 !important;
  padding: 2px 7px !important;
  border-radius: 999px !important;
  background: linear-gradient(135deg, #8B5CF6, #38BDF8) !important;
  color: #FFF !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-conn-badge {
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  color: #86EFAC !important;
  background: rgba(16, 185, 129, 0.12) !important;
  border: 1px solid rgba(16, 185, 129, 0.3) !important;
  padding: 3px 9px !important;
  border-radius: 999px !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-pulse-dot {
  width: 7px;
  height: 7px;
  background: #10B981;
  border-radius: 50%;
  box-shadow: 0 0 8px #10B981;
  animation: ailabPulse 2s infinite;
}
@keyframes ailabPulse {
  0% { transform: scale(0.9); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0.7; }
}

#view-global_ai_lab .ailab-topbar-center {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  flex: 0 1 auto !important;
  min-width: 0 !important;
  justify-content: center !important;
  flex-wrap: nowrap !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-model-selector-wrap {
  position: relative !important;
  display: inline-flex !important;
  align-items: center !important;
  background: #0B132B !important;
  border: 1.5px solid #8B5CF6 !important;
  box-shadow: 0 0 14px rgba(139, 92, 246, 0.3) !important;
  border-radius: 8px !important;
  padding: 0 10px !important;
  gap: 6px !important;
  flex: 0 1 240px !important;
  min-width: 170px !important;
  max-width: 260px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  transition: all 0.2s ease !important;
  flex-shrink: 1 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
}
#view-global_ai_lab .ailab-model-selector-wrap:hover,
#view-global_ai_lab .ailab-model-selector-wrap:focus-within {
  border-color: #C084FC !important;
  box-shadow: 0 0 20px rgba(192, 132, 252, 0.5) !important;
}
#view-global_ai_lab .ailab-model-select {
  background: transparent !important;
  border: none !important;
  color: #FFFFFF !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  width: 100% !important;
  outline: none !important;
  cursor: pointer !important;
  padding: 0 !important;
  white-space: nowrap !important;
  text-overflow: ellipsis !important;
  overflow: hidden !important;
}
#view-global_ai_lab select option,
#view-global_ai_lab select optgroup {
  background: #0B132B !important;
  color: #FFFFFF !important;
  font-size: 13px !important;
  padding: 8px 12px !important;
}
#view-global_ai_lab .ailab-effort-wrap {
  position: relative !important;
  display: inline-flex !important;
  align-items: center !important;
  background: #0B132B !important;
  border: 1.5px solid #10B981 !important;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.25) !important;
  border-radius: 8px !important;
  padding: 0 10px !important;
  gap: 6px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  transition: all 0.2s ease !important;
}
#view-global_ai_lab .ailab-effort-select {
  background: transparent !important;
  border: none !important;
  color: #FFFFFF !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  outline: none !important;
  cursor: pointer !important;
  white-space: nowrap !important;
  padding: 0 !important;
}
#view-global_ai_lab .ailab-browse-btn {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(56, 189, 248, 0.25) 100%) !important;
  border: 1.5px solid #8B5CF6 !important;
  color: #E2E8F0 !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 0 12px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  border-radius: 8px !important;
  cursor: pointer !important;
  white-space: nowrap !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.25) !important;
  flex-shrink: 0 !important;
}
#view-global_ai_lab .ailab-browse-btn:hover {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.45) 0%, rgba(56, 189, 248, 0.45) 100%) !important;
  color: #FFF !important;
  border-color: #38BDF8 !important;
  transform: translateY(-1px) !important;
}

#view-global_ai_lab .ailab-topbar-right {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  flex-shrink: 0 !important;
  min-width: max-content !important;
  white-space: nowrap !important;
}
#view-global_ai_lab .ailab-iconbtn {
  background: transparent !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  color: var(--al-muted) !important;
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  border-radius: 7px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer !important;
  flex-shrink: 0 !important;
  transition: all 0.15s ease !important;
}
#view-global_ai_lab .ailab-iconbtn:hover {
  background: var(--al-panel-2) !important;
  color: #FFF !important;
  border-color: var(--al-line) !important;
}
#view-global_ai_lab .ailab-cua-toggle-btn {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  background: #0B132B !important;
  border: 1.5px solid #38BDF8 !important;
  color: #38BDF8 !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 0 12px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  border-radius: 7px !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
}
#view-global_ai_lab .ailab-cua-toggle-btn:hover {
  background: rgba(56, 189, 248, 0.15) !important;
  border-color: #7DD3FC !important;
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.4) !important;
}
#view-global_ai_lab .ailab-cua-toggle-btn.active {
  background: rgba(56, 189, 248, 0.2) !important;
  border-color: #38BDF8 !important;
  color: #FFFFFF !important;
}
#view-global_ai_lab .ailab-topbar-right .ailab-code-btn,
#view-global_ai_lab .ailab-topbar-sync-btn {
  background: rgba(56, 189, 248, 0.08) !important;
  border: 1px solid rgba(56, 189, 248, 0.35) !important;
  color: #38BDF8 !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 0 11px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  border-radius: 7px !important;
  cursor: pointer !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  transition: all 0.15s ease !important;
}
#view-global_ai_lab .ailab-topbar-right .ailab-code-btn:hover,
#view-global_ai_lab .ailab-topbar-sync-btn:hover {
  background: rgba(56, 189, 248, 0.18) !important;
  border-color: #38BDF8 !important;
  color: #FFFFFF !important;
}
#view-global_ai_lab .ailab-topbar-right .ailab-btn-primary,
#view-global_ai_lab .ailab-topbar-new-chat-btn {
  background: linear-gradient(135deg, #7C3AED 0%, #2563EB 100%) !important;
  color: #FFF !important;
  border: none !important;
  font-size: 11.5px !important;
  font-weight: 700 !important;
  padding: 0 13px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  border-radius: 7px !important;
  cursor: pointer !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  box-shadow: 0 2px 10px rgba(124, 58, 237, 0.4) !important;
  transition: all 0.15s ease !important;
}
#view-global_ai_lab .ailab-topbar-right .ailab-btn-primary:hover,
#view-global_ai_lab .ailab-topbar-new-chat-btn:hover {
  filter: brightness(1.15) !important;
  transform: translateY(-1px) !important;
}
"""

css_start = content.find("/* ---------------- Topbar ---------------- */")
css_end = content.find("/* ---------------- Layout Body ---------------- */")

if css_start != -1 and css_end != -1:
    content = content[:css_start] + new_css + "\n" + content[css_end:]
    print("CSS replaced successfully!")
else:
    print(f"Error finding CSS markers: {css_start}, {css_end}")

# 2. Update the dynamic JS in ailabLoadLiveModels
old_dyn_opt = '<option value="auto">⚡ Single AUTO Engine (Pareto + Thompson Bandit, &lt;800ms SLA)</option>'
new_dyn_opt = '<option value="auto">⚡ AUTO Router (Pareto &lt;800ms)</option>'
if old_dyn_opt in content:
    content = content.replace(old_dyn_opt, new_dyn_opt)
    print("Dynamic option label updated!")
else:
    print("Dynamic option label already updated or not found.")

# 3. Update the static HTML in the topbar
old_static_opt = '<option value="auto" selected>⚡ AUTO Engine (Pareto &lt;800ms)</option>'
new_static_opt = '<option value="auto" selected>⚡ AUTO Router (Pareto &lt;800ms)</option>'
if old_static_opt in content:
    content = content.replace(old_static_opt, new_static_opt)
    print("Static option label updated!")

# Also check for previous variants
content = content.replace(
    '<option value="auto" selected>⚡ Single AUTO Engine (Pareto &lt;800ms)</option>',
    '<option value="auto" selected>⚡ AUTO Router (Pareto &lt;800ms)</option>'
)
content = content.replace(
    '<option value="auto" selected>⚡ Single AUTO Engine (Pareto + Thompson Bandit, &lt;800ms SLA)</option>',
    '<option value="auto" selected>⚡ AUTO Router (Pareto &lt;800ms)</option>'
)

# 4. Add helper classes to topbar right buttons
old_sync_btn = '<button class="ailab-code-btn" onclick="ailabLoadLiveModels(true)" title="Auto-discover new world labs & models in real-time" style="color:#38BDF8;border-color:rgba(56,189,248,0.3);">'
new_sync_btn = '<button class="ailab-code-btn ailab-topbar-sync-btn" onclick="ailabLoadLiveModels(true)" title="Auto-discover new world labs & models in real-time" style="color:#38BDF8;border-color:rgba(56,189,248,0.3);">'
if old_sync_btn in content:
    content = content.replace(old_sync_btn, new_sync_btn)
    print("Sync button class updated!")

old_newchat_btn = '<button class="ailab-btn-primary" onclick="ailabNewChat(\'\')">'
new_newchat_btn = '<button class="ailab-btn-primary ailab-topbar-new-chat-btn" onclick="ailabNewChat(\'\')">'
if old_newchat_btn in content:
    content = content.replace(old_newchat_btn, new_newchat_btn)
    print("New chat button class updated!")

with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Finished writing app/ui/global_ai_lab_view.py!")
