import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
screenshot_path1 = os.path.join(out_dir, "live_1468_models_mesh_topbar.png")
screenshot_path2 = os.path.join(out_dir, "live_1468_models_catalog_modal.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()

    print("[*] Navigating to:", live_url)
    page.goto(live_url, wait_until='networkidle')
    page.wait_for_timeout(2000)

    # Perform login if on login page
    if page.locator("#loginUsername").is_visible():
        print("[*] Logging in on login gateway...")
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(4000)

    print("[*] Current URL after login:", page.url)

    # Ensure on global_ai_lab view
    page.evaluate("""() => {
        if (typeof switchView === 'function') {
            switchView('global_ai_lab');
        } else {
            const v = document.getElementById('view-global_ai_lab');
            if (v) v.classList.add('active');
        }
    }""")
    page.wait_for_timeout(2000)

    # Read topbar info
    conn_badge = page.locator("#ailabConnText")
    conn_text = conn_badge.text_content() if conn_badge.is_visible() else "not visible"
    browse_btn = page.locator(".ailab-browse-btn")
    browse_text = browse_btn.text_content() if browse_btn.is_visible() else "not visible"
    print(f"[*] Live Topbar Badge: {conn_text}")
    print(f"[*] Live Browse Button: {browse_text}")

    page.screenshot(path=screenshot_path1)
    print(f"[*] Topbar screenshot saved: {screenshot_path1}")

    # Open model catalog modal
    print("[*] Opening 1,468+ Model Catalog Modal...")
    if browse_btn.is_visible():
        browse_btn.click()
        page.wait_for_timeout(1500)

        modal_subtitle = page.locator("#ailabModelModal .ailab-modal-head p").text_content()
        print(f"[*] Modal Subtitle: {modal_subtitle}")

        pills = page.locator("#ailabModelModal .ailab-modal-pills button").all_text_contents()
        print(f"[*] Modal Filter Pills ({len(pills)}): {pills}")

        cards_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
        print(f"[*] Rendered Model Cards: {cards_count}")

        page.screenshot(path=screenshot_path2)
        print(f"[*] Modal screenshot saved: {screenshot_path2}")

    browser.close()
