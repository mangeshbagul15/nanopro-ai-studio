"""Find exact 401 request URLs."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    responses = []
    page.on("response", lambda r: responses.append((r.status, r.url)) if r.status >= 400 else None)

    page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # Login
    login_visible = page.evaluate("() => !!document.getElementById('loginUsername') && document.getElementById('loginUsername').offsetWidth > 0")
    if login_visible:
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3000)

    page.evaluate("() => { if (typeof switchView === 'function') switchView('global_ai_lab'); }")
    page.wait_for_timeout(2000)

    responses.clear()
    print("Calling window.ailabOpenAirflowModal()...")
    page.evaluate("() => window.ailabOpenAirflowModal()")
    page.wait_for_timeout(2500)

    print("HTTP responses >= 400:")
    for status, u in responses:
        print(f"  [{status}] {u}")

    browser.close()
