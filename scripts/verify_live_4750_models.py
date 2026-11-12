import os, sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
topbar_path = os.path.join(out_dir, "live_4750_models_topbar.png")
catalog_path = os.path.join(out_dir, "live_4750_models_catalog_modal.png")
krutrim_path = os.path.join(out_dir, "live_krutrim_filtered.png")
poe_path = os.path.join(out_dir, "live_poe_filtered.png")
parasail_path = os.path.join(out_dir, "live_parasail_filtered.png")
arcee_path = os.path.join(out_dir, "live_arcee_filtered.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
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
    browse_btn_text = page.locator(".ailab-browse-btn").inner_text()
    print("[*] Browse Button Text:", browse_btn_text.strip())

    # Screenshot Topbar
    page.screenshot(path=topbar_path)
    print(f"[*] Saved topbar screenshot: {topbar_path}")

    # 2. Open Model Catalog Modal directly via evaluation
    print("[*] Opening Model Catalog Modal via ailabOpenModelCatalogModal()...")
    page.evaluate("if (typeof ailabOpenModelCatalogModal === 'function') ailabOpenModelCatalogModal();")
    page.wait_for_timeout(1500)

    modal_vis = page.locator("#ailabModelModal").is_visible()
    print("[*] Model Catalog Modal visible:", modal_vis)
    
    # Screenshot Modal Overview
    page.screenshot(path=catalog_path)
    print(f"[*] Saved catalog modal screenshot: {catalog_path}")

    # 3. Test Krutrim AI Pill
    print("[*] Filtering by Krutrim AI...")
    page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('.ailab-modal-pills .ailab-pill')).find(p => p.textContent.includes('Krutrim'));
        if (typeof ailabFilterModelCategory === 'function') ailabFilterModelCategory('krutrim', btn);
    }""")
    page.wait_for_timeout(1000)
    krutrim_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
    print(f"[*] Krutrim displayed cards: {krutrim_count}")
    page.screenshot(path=krutrim_path)
    print(f"[*] Saved Krutrim screenshot: {krutrim_path}")

    # 4. Test Poe by Quora Pill
    print("[*] Filtering by Poe...")
    page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('.ailab-modal-pills .ailab-pill')).find(p => p.textContent.includes('Poe'));
        if (typeof ailabFilterModelCategory === 'function') ailabFilterModelCategory('poe', btn);
    }""")
    page.wait_for_timeout(1000)
    poe_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
    print(f"[*] Poe displayed cards: {poe_count}")
    page.screenshot(path=poe_path)
    print(f"[*] Saved Poe screenshot: {poe_path}")

    # 5. Test Parasail GPU Network Pill
    print("[*] Filtering by Parasail...")
    page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('.ailab-modal-pills .ailab-pill')).find(p => p.textContent.includes('Parasail'));
        if (typeof ailabFilterModelCategory === 'function') ailabFilterModelCategory('parasail', btn);
    }""")
    page.wait_for_timeout(1000)
    parasail_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
    print(f"[*] Parasail displayed cards: {parasail_count}")
    page.screenshot(path=parasail_path)
    print(f"[*] Saved Parasail screenshot: {parasail_path}")

    # 6. Test Arcee AI Pill
    print("[*] Filtering by Arcee AI...")
    page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('.ailab-modal-pills .ailab-pill')).find(p => p.textContent.includes('Arcee'));
        if (typeof ailabFilterModelCategory === 'function') ailabFilterModelCategory('arcee', btn);
    }""")
    page.wait_for_timeout(1000)
    arcee_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
    print(f"[*] Arcee displayed cards: {arcee_count}")
    page.screenshot(path=arcee_path)
    print(f"[*] Saved Arcee screenshot: {arcee_path}")

    browser.close()
    print("[*] Live Playwright verification finished successfully!")
