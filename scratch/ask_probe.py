"""Ask the live shell a platform question and capture the answer + any 404s."""
import json
import os
import re
import time

from playwright.sync_api import sync_playwright

BASE = "https://mangesh-nanopro.mangeshbagul15.workers.dev"
OUT = os.path.join(os.path.dirname(__file__), "live_walkthrough")


def env_value(path, key):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


bad, errors = [], []
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
    page.on("response", lambda r: bad.append((r.status, r.url.split("?")[0])) if r.status >= 400 else None)
    page.on("console", lambda m: errors.append(m.text[:160]) if m.type == "error" else None)
    page.goto(BASE + "/login", wait_until="domcontentloaded", timeout=60000)
    page.fill("#loginUsername", env_value(".env", "NANOPRO_ADMIN_USERNAME") or "nanopro")
    page.fill("#loginPassword", env_value(".env", "NANOPRO_ADMIN_PASSWORD"))
    page.click("#loginBtn")
    try:
        page.wait_for_url(re.compile(r"/$|/legacy"), timeout=45000)
    except Exception:
        pass
    page.wait_for_timeout(5000)
    page.fill("#ask-input", "NanoPro platform kay karte? ekda sentence madhe sanga.")
    page.press("#ask-input", "Enter")
    end = time.time() + 80
    while time.time() < end:
        body = page.locator("#d-body").inner_text()
        if "Thinking" not in body and body.strip():
            break
        page.wait_for_timeout(1000)
    answer = page.locator("#d-body").inner_text().replace("\n", " | ")[:420]
    page.screenshot(path=os.path.join(OUT, "08_ask_platform.png"))
    page.locator("#d-close").click()
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(OUT, "09_shell_after.png"))
    browser.close()
print(json.dumps({"answer": answer, "bad_responses": bad, "console_errors": errors}, indent=1))
