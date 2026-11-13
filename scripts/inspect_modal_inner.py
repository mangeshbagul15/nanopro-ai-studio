"""Check modal computed style and inner elements."""
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

    # Check modal visibility before and after click
    status = page.evaluate("""() => {
        const modal = document.getElementById('ailabAirflowModal');
        const btn = document.querySelector('button[onclick*="ailabOpenAirflowModal"]');
        return {
            hasModal: !!modal,
            modalDisplay: modal ? window.getComputedStyle(modal).display : null,
            hasBtn: !!btn,
            btnDisplay: btn ? window.getComputedStyle(btn).display : null
        };
    }""")
    print("Initial status:", status)

    page.click('button:has-text("Launch ➔")')
    page.wait_for_timeout(1000)

    status_after = page.evaluate("""() => {
        const modal = document.getElementById('ailabAirflowModal');
        const inner = modal ? modal.querySelector('.ailab-modal') : null;
        return {
            modalDisplay: modal ? window.getComputedStyle(modal).display : null,
            modalVisibility: modal ? window.getComputedStyle(modal).visibility : null,
            modalZIndex: modal ? window.getComputedStyle(modal).zIndex : null,
            innerDisplay: inner ? window.getComputedStyle(inner).display : null,
            innerRect: inner ? inner.getBoundingClientRect() : null,
            dagsListCount: modal ? modal.querySelectorAll('#airflowDagsList > div').length : 0
        };
    }""")
    print("Status after click:", status_after)

    browser.close()
