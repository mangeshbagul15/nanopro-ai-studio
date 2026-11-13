"""Test REAL mouse click on the Airflow & SFTP button."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

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

    # Now let's try a REAL physical mouse click on the button!
    print("Attempting REAL page.click on button...")
    try:
        page.click('button[onclick*="ailabOpenAirflowModal"]', timeout=5000)
        print("REAL click succeeded!")
    except Exception as e:
        print("REAL click FAILED with error:", e)

    page.wait_for_timeout(2000)

    # Check if modal is open
    is_open = page.evaluate("() => document.getElementById('ailabAirflowModal')?.classList.contains('is-open')")
    print("Modal is-open after click:", is_open)

    browser.close()
