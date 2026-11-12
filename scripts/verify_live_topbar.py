import os
from playwright.sync_api import sync_playwright

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
screenshot_path = os.path.join(out_dir, "live_topbar_single_row_verified.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()

    page.goto(live_url, wait_until='networkidle')
    page.wait_for_timeout(3000)

    # Ensure view is active
    page.evaluate("""() => {
        if (typeof showView === 'function') showView('global_ai_lab');
    }""")
    page.wait_for_timeout(1500)

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

    print("Live Production Topbar Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    page.screenshot(path=screenshot_path)
    print(f"Live screenshot saved to: {screenshot_path}")

    browser.close()
