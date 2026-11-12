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
        print("[*] Logging in on live site...")
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

    # Verify input exists
    input_box = page.locator("#ailabPromptInput")
    input_box.wait_for(state="visible", timeout=10000)
    print("[*] #ailabPromptInput is visible!")

    # 1. Test Data Engineering Prompt
    print("[*] Submitting Data Engineering Prompt...")
    input_box.fill("data engineering pipeline snowflake aws eod sod ingestion")
    page.locator("#ailabSendBtn").click()
    page.wait_for_timeout(4000)

    p1 = os.path.join(out_dir, "live_data_engineering_verified.png")
    page.screenshot(path=p1)
    print("[*] Captured:", p1)

    # 2. Test Image Generation Prompt
    print("[*] Submitting Image Generation Prompt...")
    input_box.fill("futuristic cyber ai lab chi mast image banva")
    page.locator("#ailabSendBtn").click()
    page.wait_for_timeout(4000)

    p2 = os.path.join(out_dir, "live_image_generation_verified.png")
    page.screenshot(path=p2)
    print("[*] Captured:", p2)

    browser.close()
    print("[*] All verifications finished successfully!")
