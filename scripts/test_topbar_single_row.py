import sys
import os
import time
from playwright.sync_api import sync_playwright

html_path = os.path.abspath('deploy/complete_nanopro_dashboard.html')
file_url = f"file:///{html_path.replace(os.sep, '/')}#global_ai_lab"

out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
screenshot_path = os.path.join(out_dir, "topbar_clean_single_row_verified.png")

with sync_playwright() as p:
    # Test on a 1366x768 laptop viewport (standard common resolution where wrapping occurred)
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1366, "height": 768})
    page = context.new_page()

    page.goto(file_url, wait_until='networkidle')
    page.wait_for_timeout(2000)

    # Make sure global_ai_lab is active
    page.evaluate("""() => {
        if (typeof showView === 'function') {
            showView('global_ai_lab');
        } else {
            const v = document.getElementById('view-global_ai_lab');
            if (v) {
                v.classList.add('active');
                v.style.display = 'flex';
            }
        }
    }""")
    page.wait_for_timeout(1000)

    # Evaluate topbar bounding box and element positions
    topbar_info = page.evaluate("""() => {
        const topbar = document.querySelector('#view-global_ai_lab .ailab-topbar');
        if (!topbar) return { error: 'topbar not found' };

        const tbBox = topbar.getBoundingClientRect();
        
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
            topbar_height: tbBox.height,
            topbar_top: tbBox.top,
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

    print("Topbar Metrics:")
    for k, v in topbar_info.items():
        print(f"  {k}: {v}")

    # Take screenshot of full page
    page.screenshot(path=screenshot_path)
    print(f"Screenshot successfully saved to: {screenshot_path}")

    # Also test with CUA open to ensure topbar stays single-row even when CUA is toggled!
    page.evaluate("() => { if (typeof ailabToggleCuaPanel === 'function') ailabToggleCuaPanel(); }")
    page.wait_for_timeout(1000)
    cua_screenshot = os.path.join(out_dir, "topbar_with_cua_open_verified.png")
    page.screenshot(path=cua_screenshot)
    print(f"CUA open screenshot saved to: {cua_screenshot}")

    browser.close()
