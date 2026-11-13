"""Check parent element and computed styles of modal."""
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

    page.evaluate("() => window.ailabOpenAirflowModal()")
    page.wait_for_timeout(1000)

    res = page.evaluate("""() => {
        const modal = document.getElementById('ailabAirflowModal');
        if (!modal) return 'NO_MODAL';
        const inner = modal.querySelector('.ailab-modal');
        const parent = modal.parentElement;
        return {
            modalTag: modal.tagName,
            parentTag: parent ? parent.tagName : null,
            parentId: parent ? parent.id : null,
            parentClass: parent ? parent.className : null,
            parentDisplay: parent ? window.getComputedStyle(parent).display : null,
            modalStyleWidth: modal.style.width,
            modalStyleHeight: modal.style.height,
            modalOffsetWidth: modal.offsetWidth,
            modalOffsetHeight: modal.offsetHeight,
            innerOffsetWidth: inner ? inner.offsetWidth : null,
            innerOffsetHeight: inner ? inner.offsetHeight : null,
            innerStyle: inner ? inner.getAttribute('style') : null
        };
    }""")
    print("Modal layout info:", res)

    browser.close()
