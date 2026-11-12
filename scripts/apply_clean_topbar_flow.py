import re

with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update .ailab-topbar CSS:
# - justify-content: flex-start !important
# - .ailab-topbar-center: flex: 0 0 auto !important; margin: 0 auto;
# - .ailab-topbar-right: margin-left: auto !important; flex: 0 0 auto !important;
# - .ailab-topbar-left: flex: 0 0 auto !important;

css_replacement = """/* ---------------- Topbar (Single-Row Modern Responsive Header) ---------------- */
#view-global_ai_lab .ailab-topbar {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  gap: 12px !important;
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
  flex: 0 0 auto !important;
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
  flex: 0 0 auto !important;
  min-width: max-content !important;
  justify-content: flex-start !important;
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
  width: 220px !important;
  min-width: 200px !important;
  max-width: 240px !important;
  height: 32px !important;
  box-sizing: border-box !important;
  transition: all 0.2s ease !important;
  flex: 0 0 auto !important;
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
  flex: 0 0 auto !important;
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
  flex: 0 0 auto !important;
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
  flex: 0 0 auto !important;
  margin-left: auto !important; /* PUSHES RIGHT CONTROLS TO THE FAR RIGHT */
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

css_start = content.find("/* ---------------- Topbar (Single-Row Modern Responsive Header) ---------------- */")
css_end = content.find("/* ---------------- Layout Body ---------------- */")

if css_start != -1 and css_end != -1:
    content = content[:css_start] + css_replacement + "\n" + content[css_end:]
    print("Topbar CSS updated with margin-left: auto and no-overlap flow!")
else:
    print(f"Could not find markers: {css_start}, {css_end}")

# Clean up effort options to keep it compact
content = content.replace(
    '<option value="architecture">🔬 Architecture &amp; Diagrams</option>',
    '<option value="architecture">🔬 Architecture</option>'
)

with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app/ui/global_ai_lab_view.py!")
