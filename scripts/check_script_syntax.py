# -*- coding: utf-8 -*-
import os, re, subprocess

with open("deploy/complete_nanopro_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find("id=\"view-global_ai_lab\"")
idx2 = text.find("id=\"view-models_hub\"")
sub = text[idx1:idx2]
scripts = re.findall(r'<script>([\s\S]*?)</script>', sub)
print("Found script tags:", len(scripts))

for i, s in enumerate(scripts):
    fname = f"scratch/ailab_script_{i}.js"
    os.makedirs("scratch", exist_ok=True)
    with open(fname, "w", encoding="utf-8") as out:
        out.write(s)
    print(f"Checking {fname}...")
    res = subprocess.run(["node", "--check", fname], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"{fname}: Clean valid JavaScript!")
    else:
        print(f"{fname}: Syntax Error:\n{res.stderr}")
