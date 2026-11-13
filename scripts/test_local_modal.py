"""Verify modal layout on local file:// before deploy."""
import os
from playwright.sync_api import sync_playwright

file_url = "file:///" + os.path.abspath("deploy/complete_nanopro_dashboard.html").replace("\\", "/")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(file_url, wait_until="networkidle")
    page.wait_for_timeout(1000)

    # Switch to view-global_ai_lab
    page.evaluate("() => { if (typeof switchView === 'function') switchView('global_ai_lab'); }")
    page.wait_for_timeout(1000)

    # Click Launch Airflow button in Explorer
    print("Clicking Launch Airflow button in Explorer...")
    page.click('button:has-text("Launch ➔")')
    page.wait_for_timeout(1000)

    res = page.evaluate("""() => {
        const modal = document.getElementById('ailabAirflowModal');
        const inner = modal ? modal.querySelector('.ailab-modal') : null;
        const rect = inner ? inner.getBoundingClientRect() : null;
        return {
            modalDisplay: modal ? window.getComputedStyle(modal).display : null,
            modalZIndex: modal ? window.getComputedStyle(modal).zIndex : null,
            innerRect: rect ? { width: rect.width, height: rect.height, x: rect.x, y: rect.y } : null,
            isOpen: modal ? modal.classList.contains('is-open') : false
        };
    }""")
    print("Local Layout Result:", res)

    # Take screenshot of local verification
    sc_local = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac\local_verified_modal_visible.png"
    page.screenshot(path=sc_local)
    print("Screenshot saved to:", sc_local)

    browser.close()
