"""Verify live modal opens with proper dimensions after relocation."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    print("Navigating to live Cloudflare Worker...")
    page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # Login
    login_visible = page.evaluate("() => !!document.getElementById('loginUsername') && document.getElementById('loginUsername').offsetWidth > 0")
    if login_visible:
        print("Logging in via Security Gateway...")
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3000)

    page.evaluate("() => { if (typeof switchView === 'function') switchView('global_ai_lab'); }")
    page.wait_for_timeout(2000)

    # Test click on Explorer Launch button
    print("Clicking Launch ➔ button in Explorer...")
    page.click('button:has-text("Launch ➔")')
    page.wait_for_timeout(2000)

    # Verify modal layout
    res = page.evaluate("""() => {
        const modal = document.getElementById('ailabAirflowModal');
        const inner = modal ? modal.querySelector('.ailab-modal') : null;
        const rect = inner ? inner.getBoundingClientRect() : null;
        return {
            isOpen: modal ? modal.classList.contains('is-open') : false,
            modalDisplay: modal ? window.getComputedStyle(modal).display : null,
            modalZIndex: modal ? window.getComputedStyle(modal).zIndex : null,
            innerRect: rect ? { width: rect.width, height: rect.height, x: rect.x, y: rect.y } : null,
            dagsCount: modal ? modal.querySelectorAll('#airflowDagsList > div').length : 0
        };
    }""")
    print("Live Modal Layout Result:", res)

    # Take screenshot of open Airflow modal
    sc_path = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac\live_verified_modal_relocated.png"
    page.screenshot(path=sc_path)
    print("Saved screenshot to:", sc_path)

    # Switch to SFTP Tab
    print("Switching to SFTP tab...")
    page.click('#tabAirflowSftp')
    page.wait_for_timeout(1500)

    # Take screenshot of SFTP tab
    sc_sftp = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac\live_verified_sftp_tab_relocated.png"
    page.screenshot(path=sc_sftp)
    print("Saved SFTP screenshot to:", sc_sftp)

    browser.close()
    print("VERIFICATION COMPLETE!")
