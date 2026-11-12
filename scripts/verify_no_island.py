import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac")
URL = "https://mangesh-nanopro.mangeshbagul15.workers.dev/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    print("[*] Navigating to URL...")
    page.goto(URL, timeout=40000, wait_until="networkidle")

    # Login
    if page.locator("#loginUsername").is_visible():
        print("[*] Performing Login...")
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Divyam@123")
        page.click("#loginBtn")
        page.wait_for_timeout(4000)

    print(f"[*] Post-login URL: {page.url}")

    # Switch to Global AI Lab
    print("[*] Switching to Global AI Lab...")
    page.evaluate("if (typeof switchView === 'function') switchView('global_ai_lab');")
    page.wait_for_timeout(3000)

    # Check nanoDynamicIsland
    island = page.locator("#nanoDynamicIsland")
    is_visible = island.is_visible() if island.count() > 0 else False
    print(f"[*] nanoDynamicIsland is_visible: {is_visible}")
    if island.count() > 0:
        display_style = page.evaluate("window.getComputedStyle(document.getElementById('nanoDynamicIsland')).display")
        print(f"[*] nanoDynamicIsland computed display: {display_style}")

    # Check Global AI Lab topbar
    topbar = page.locator("#view-global_ai_lab .ailab-topbar")
    topbar_visible = topbar.is_visible() if topbar.count() > 0 else False
    print(f"[*] ailab-topbar is_visible: {topbar_visible}")

    # Check Model Selector
    model_sel = page.locator("#ailabModelSelect")
    model_sel_visible = model_sel.is_visible() if model_sel.count() > 0 else False
    print(f"[*] Model selector is_visible: {model_sel_visible}")

    # Take screenshot
    shot_path = str(ARTIFACTS_DIR / "global_ai_lab_clean_view.png")
    page.screenshot(path=shot_path)
    print(f"[+] Saved screenshot to: {shot_path}")

    browser.close()
