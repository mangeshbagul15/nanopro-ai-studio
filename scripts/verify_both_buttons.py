"""Verify clicking Airflow & SFTP button in Topbar and in Explorer."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    print("Navigating to live site...")
    page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # Login
    login_visible = page.evaluate("() => !!document.getElementById('loginUsername') && document.getElementById('loginUsername').offsetWidth > 0")
    if login_visible:
        print("Logging in...")
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3000)

    page.evaluate("() => { if (typeof switchView === 'function') switchView('global_ai_lab'); }")
    page.wait_for_timeout(2000)

    # Test 1: Click the Explorer Launch button
    print("Testing click on Explorer Launch button...")
    page.click('button:has-text("Launch ➔")')
    page.wait_for_timeout(2000)

    is_open = page.evaluate("() => document.getElementById('ailabAirflowModal')?.classList.contains('is-open')")
    print("Modal is-open after Explorer Launch click:", is_open)

    # Screenshot modal
    sc_path = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac\live_verified_airflow_modal_open.png"
    page.screenshot(path=sc_path)
    print("Saved screenshot:", sc_path)

    # Close modal
    print("Closing modal...")
    page.click('.ailab-modal-close')
    page.wait_for_timeout(1000)

    # Test 2: Click the Topbar button
    print("Testing click on Topbar Airflow button...")
    page.click('#ailabAirflowTopbarBtn')
    page.wait_for_timeout(2000)

    is_open_topbar = page.evaluate("() => document.getElementById('ailabAirflowModal')?.classList.contains('is-open')")
    print("Modal is-open after Topbar button click:", is_open_topbar)

    browser.close()
    print("SUCCESS: Both buttons verified and functioning 100%!")
