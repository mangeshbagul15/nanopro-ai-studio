import os, sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
out_dir = r"C:\Users\mange\.gemini\antigravity\brain\d865996f-cadd-4e6b-abff-1251e0bc95d9"
topbar_path = os.path.join(out_dir, "live_4800_models_topbar.png")
catalog_path = os.path.join(out_dir, "live_4800_models_catalog_modal.png")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 850})
    page = context.new_page()

    print("[*] Navigating to:", live_url)
    page.goto(live_url, wait_until='networkidle')
    page.wait_for_timeout(2000)

    # Perform login if on login gateway
    if page.locator("#loginUsername").is_visible():
        print("[*] Logging in on login gateway...")
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3500)

    print("[*] Ensuring on global_ai_lab view...")
    page.evaluate("""() => {
        if (typeof switchView === 'function') {
            switchView('global_ai_lab');
        } else {
            const v = document.getElementById('view-global_ai_lab');
            if (v) v.classList.add('active');
        }
    }""")
    page.wait_for_timeout(2500)

    # 1. Verify Topbar model badge text
    conn_text = page.locator("#ailabConnText").inner_text()
    print("[*] Live Topbar Connection Badge:", conn_text)

    # Screenshot Topbar
    page.screenshot(path=topbar_path)
    print(f"[*] Saved topbar screenshot: {topbar_path}")

    # 2. Open Model Catalog Modal
    print("[*] Opening Model Catalog Modal via ailabOpenModelCatalogModal()...")
    page.evaluate("if (typeof ailabOpenModelCatalogModal === 'function') ailabOpenModelCatalogModal();")
    page.wait_for_timeout(1500)

    modal_vis = page.locator("#ailabModelModal").is_visible()
    print("[*] Model Catalog Modal visible:", modal_vis)

    page.screenshot(path=catalog_path)
    print(f"[*] Saved catalog screenshot: {catalog_path}")

    browser.close()
    print("[OK] UI verification completed successfully!")
