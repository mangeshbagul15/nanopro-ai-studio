import os

os.chdir(r"C:\Users\mange\OneDrive\Documents\GitHub\nanopro-ai-studio")

with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    cw = f.read()

# Fix unescaped backticks in line 4031 and line 4092
cw = cw.replace(
    "using ```mermaid ... ``` code fences",
    "using \\`\\`\\`mermaid ... \\`\\`\\` code fences"
)

cw = cw.replace(
    "in ```mermaid ... ``` code fences.",
    "in \\`\\`\\`mermaid ... \\`\\`\\` code fences.`;"
)

with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
    f.write(cw)

print("Fixed syntax in deploy/cloudflare_worker_gateway.js!")
