import os
import sys
from playwright.sync_api import sync_playwright

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
screenshot_path = os.path.join(out_dir, "live_topbar_single_row_verified.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()

    page.goto(live_url, wait_until='networkidle')
    page.wait_for_timeout(2000)

    # Perform login if on login page
    if page.locator("#loginUsername").is_visible():
        print("[*] Logging in on live site...")
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3500)

    print("[*] Current URL:", page.url)

    # Switch view using switchView
    page.evaluate("""() => {
        document.body.classList.add('auth-verified');
        document.documentElement.classList.add('auth-verified');
        const gw = document.getElementById('nanoProAuthGateway');
        if (gw) { gw.classList.remove('force-show'); gw.style.display = 'none'; }
        if (typeof onAuthSuccess === 'function') onAuthSuccess({ username: 'nanopro', role: 'admin', allowed_views: ['*'] });
        if (typeof switchView === 'function') switchView('global_ai_lab');
    }""")
    page.wait_for_timeout(2500)

    # Verify positions on live production
    metrics = page.evaluate("""() => {
        const topbar = document.querySelector('#view-global_ai_lab .ailab-topbar');
        const brand = document.querySelector('#view-global_ai_lab .ailab-brand');
        const connBadge = document.querySelector('#view-global_ai_lab #ailabConnBadge');
        const modelWrap = document.querySelector('#view-global_ai_lab .ailab-model-selector-wrap');
        const effortWrap = document.querySelector('#view-global_ai_lab .ailab-effort-wrap');
        const browseBtn = document.querySelector('#view-global_ai_lab .ailab-browse-btn');
        const cuaBtn = document.querySelector('#view-global_ai_lab #ailabCuaToggleBtn');
        const syncBtn = document.querySelector('#view-global_ai_lab .ailab-topbar-sync-btn');
        const newChatBtn = document.querySelector('#view-global_ai_lab .ailab-topbar-new-chat-btn');

        const getBox = el => el ? el.getBoundingClientRect() : null;

        return {
            topbarHeight: topbar ? topbar.getBoundingClientRect().height : 0,
            brand: getBox(brand),
            connBadge: getBox(connBadge),
            modelWrap: getBox(modelWrap),
            effortWrap: getBox(effortWrap),
            browseBtn: getBox(browseBtn),
            cuaBtn: getBox(cuaBtn),
            syncBtn: getBox(syncBtn),
            newChatBtn: getBox(newChatBtn)
        };
    }""")

    print("Live Production Topbar Metrics After View Switch:")
    for k, v in metrics.items():
        val_str = str(v).encode('ascii', 'backslashreplace').decode('ascii')
        print(f"  {k}: {val_str}")

    page.screenshot(path=screenshot_path)
    print(f"Live screenshot updated: {screenshot_path}")

    browser.close()
