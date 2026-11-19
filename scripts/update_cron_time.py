import os
os.chdir(r"C:\Users\mange\OneDrive\Documents\GitHub\nanopro-ai-studio")

with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    cw = f.read()

cw = cw.replace('"30 14 * * *": "T-1",  // 20:00 IST - T-1 evening brief', '"30 5 * * *": "T-1",   // 11:00 IST - T-1 Statutory Banking Report run')

with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
    f.write(cw)

print("Updated T-1 cron schedule in deploy/cloudflare_worker_gateway.js!")
