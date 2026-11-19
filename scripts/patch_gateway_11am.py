import os

path = os.path.join("deploy", "cloudflare_worker_gateway.js")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace('"T1", scheduled_ist: "10:00"', '"T1", scheduled_ist: "11:00"')
text = text.replace("T1 10:00", "T1 11:00")
text = text.replace('path === "/api/cron/10am"', 'path === "/api/cron/10am" || path === "/api/cron/11am" || path === "/api/cron/daily_11am_dashboard"')
text = text.replace("DAILY 10:00 AM IST DISPATCH", "DAILY 11:00 AM IST DISPATCH")
text = text.replace("Daily 10:00 AM Banking Executive Dashboard", "Daily 11:00 AM Banking Executive Dashboard")
text = text.replace('"10:00 AM IST Daily"', '"11:00 AM IST Daily"')

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated gateway with 11:00 AM IST schedule successfully!")
