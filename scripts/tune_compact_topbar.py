with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's tune sizes slightly so everything fits comfortably even on smaller laptop viewports
replacements = [
    # Topbar gap
    ('gap: 12px !important;', 'gap: 8px !important;'),
    # Brand font-size
    ('font-size: 13.5px !important;', 'font-size: 13px !important;'),
    # Conn badge padding
    ('padding: 3px 9px !important;', 'padding: 2px 8px !important;'),
    # Model selector width
    ('width: 220px !important;\n  min-width: 200px !important;\n  max-width: 240px !important;', 'width: 195px !important;\n  min-width: 175px !important;\n  max-width: 210px !important;'),
    # Effort wrap padding
    ('padding: 0 10px !important;\n  gap: 6px !important;', 'padding: 0 8px !important;\n  gap: 4px !important;'),
    # Browse btn padding
    ('padding: 0 12px !important;', 'padding: 0 9px !important;'),
    # CUA btn padding
    ('padding: 0 12px !important;\n  height: 32px !important;\n  box-sizing: border-box !important;\n  border-radius: 7px !important;\n  cursor: pointer !important;\n  transition: all 0.15s ease !important;\n  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;\n  white-space: nowrap !important;\n  flex-shrink: 0 !important;', 'padding: 0 9px !important;\n  height: 30px !important;\n  box-sizing: border-box !important;\n  border-radius: 6px !important;\n  cursor: pointer !important;\n  transition: all 0.15s ease !important;\n  box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;\n  white-space: nowrap !important;\n  flex-shrink: 0 !important;'),
    # Sync btn padding
    ('padding: 0 11px !important;', 'padding: 0 8px !important;'),
    # New chat btn padding
    ('padding: 0 13px !important;', 'padding: 0 10px !important;'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print("Replaced:", old[:30], "...")
    else:
        print("Not found:", old[:30])

with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Tuning complete in app/ui/global_ai_lab_view.py!")
