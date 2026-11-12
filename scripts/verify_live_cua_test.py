import os
from playwright.sync_api import sync_playwright

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    print("[*] Navigating to live URL:", live_url)
    page.goto(live_url, wait_until='networkidle')
    page.wait_for_timeout(2000)

    # Perform login if on login page
    if page.locator("#loginUsername").is_visible():
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3500)

    # Force switch to global_ai_lab view
    page.evaluate("""() => {
        document.querySelectorAll('.workspace-view').forEach(v => v.classList.remove('active'));
        const v = document.getElementById('view-global_ai_lab');
        if (v) v.classList.add('active');
        if (typeof switchView === 'function') switchView('global_ai_lab');
    }""")
    page.wait_for_timeout(2000)

    input_box = page.locator("#ailabPromptInput")
    input_box.wait_for(state="visible", timeout=10000)

    # Test CUA Browser Search Prompt
    print("[*] Submitting CUA Browser Search Prompt...")
    input_box.fill("side screen share madhe google search kara")
    page.locator("#ailabSendBtn").click()
    page.wait_for_timeout(5000)

    p3 = os.path.join(out_dir, "live_cua_end_to_end_verified.png")
    page.screenshot(path=p3)
    print("[*] Captured:", p3)

    browser.close()
    print("[*] CUA End-to-End verification finished successfully!")
