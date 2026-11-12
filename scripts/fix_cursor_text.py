# -*- coding: utf-8 -*-
with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'this.moveCursor(targetX, targetY, `Searching: ${query}`);',
    'this.moveCursor(targetX, targetY, cursorTargetText);'
)
text = text.replace(
    'this.updateActionHud("✅", `Google Search Complete: "${query}" • Live in CUA Screen`);',
    'this.updateActionHud("✅", `${cursorTargetText} • Live in CUA Screen`);'
)

with open("app/ui/global_ai_lab_view.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated cursorTargetText and updateActionHud in app/ui/global_ai_lab_view.py!")
