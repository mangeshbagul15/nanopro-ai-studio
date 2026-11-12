import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
screenshot_path1 = os.path.join(out_dir, "live_explorer_integrated_verified.png")
screenshot_path2 = os.path.join(out_dir, "live_explorer_table_click_verified.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 820})
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
    page.wait_for_timeout(2500)

    # 1. Verify Topbar and Explorer Panel Visibility
    explorer = page.locator("#ailabExplorer")
    print("[*] Explorer panel visible:", explorer.is_visible())

    # Get Explorer tree items
    tree_text = page.locator("#ailabExplorerTree").inner_text()
    print("[*] Explorer Tree Preview:\n", "\n".join(tree_text.splitlines()[:12]))

    # Capture Explorer overview screenshot
    page.screenshot(path=screenshot_path1)
    print(f"[*] Explorer screenshot saved: {screenshot_path1}")

    # 2. Test Table Click: Click on a table in the tree (e.g. TRANSACTIONS_RAW or banking_transactions_cdc)
    table_row = page.locator("#ailabExplorerTree .ailab-tree-row:has-text('TRANSACTIONS_RAW')")
    if not table_row.is_visible():
        table_row = page.locator("#ailabExplorerTree .ailab-tree-row:has-text('banking_transactions_cdc')")

    if table_row.is_visible():
        print("[*] Clicking table row in Explorer...")
        table_row.click()
        page.wait_for_timeout(1000)
        prompt_val = page.locator("#ailabPromptInput").input_value()
        print(f"[*] Populated prompt value: {prompt_val}")

    # Capture table click & prompt populated screenshot
    page.screenshot(path=screenshot_path2)
    print(f"[*] Table click screenshot saved: {screenshot_path2}")

    # 3. Test Instant Chat Click in sidebar
    recent_chat = page.locator("#ailabRecentList .ailab-chat-item, #ailabPinnedList .ailab-chat-item").first
    if recent_chat.is_visible():
        print("[*] Clicking chat item in sidebar for instant load...")
        recent_chat.click()
        page.wait_for_timeout(500)
        active_title = page.locator("#ailabActiveTitle").text_content()
        print(f"[*] Instant active chat title: {active_title}")

    browser.close()
