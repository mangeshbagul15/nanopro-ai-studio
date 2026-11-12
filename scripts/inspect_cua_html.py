with open("deploy/complete_nanopro_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'id=["\']ailabCua', text)]
print("id=ailabCua matches:", len(matches))
for m in matches:
    print(text[m:m+150].encode("ascii", "backslashreplace").decode("ascii"))
