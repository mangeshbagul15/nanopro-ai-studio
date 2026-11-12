import os, sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
topbar_path = os.path.join(out_dir, "live_4330_models_topbar.png")
catalog_path = os.path.join(out_dir, "live_4330_models_catalog_modal.png")
eden_path = os.path.join(out_dir, "live_eden_ai_filtered.png")
samba_path = os.path.join(out_dir, "live_sambanova_filtered.png")
nvidia_path = os.path.join(out_dir, "live_nvidia_nim_filtered.png")
requesty_path = os.path.join(out_dir, "live_requesty_filtered.png")

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

    # 3. Test Eden AI Pill (1,311 models)
    print("[*] Filtering by Eden AI...")
    page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('.ailab-modal-pills .ailab-pill')).find(p => p.textContent.includes('Eden AI'));
        if (typeof ailabFilterModelCategory === 'function') ailabFilterModelCategory('edenai', btn);
    }""")
    page.wait_for_timeout(1000)
    eden_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
    print(f"[*] Eden AI displayed cards: {eden_count}")
    page.screenshot(path=eden_path)
    print(f"[*] Saved Eden AI screenshot: {eden_path}")

    # 4. Test SambaNova Pill (RDU)
    print("[*] Filtering by SambaNova...")
    page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('.ailab-modal-pills .ailab-pill')).find(p => p.textContent.includes('SambaNova'));
        if (typeof ailabFilterModelCategory === 'function') ailabFilterModelCategory('sambanova', btn);
    }""")
    page.wait_for_timeout(1000)
    samba_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
    print(f"[*] SambaNova displayed cards: {samba_count}")
    page.screenshot(path=samba_path)
    print(f"[*] Saved SambaNova screenshot: {samba_path}")

    # 5. Test NVIDIA NIM Pill (83 models)
    print("[*] Filtering by NVIDIA NIM...")
    page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('.ailab-modal-pills .ailab-pill')).find(p => p.textContent.includes('NVIDIA NIM'));
        if (typeof ailabFilterModelCategory === 'function') ailabFilterModelCategory('nvidia', btn);
    }""")
    page.wait_for_timeout(1000)
    nv_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
    print(f"[*] NVIDIA NIM displayed cards: {nv_count}")
    page.screenshot(path=nvidia_path)
    print(f"[*] Saved NVIDIA NIM screenshot: {nvidia_path}")

    # 6. Test Requesty AI Pill (750 models)
    print("[*] Filtering by Requesty AI...")
    page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('.ailab-modal-pills .ailab-pill')).find(p => p.textContent.includes('Requesty AI'));
        if (typeof ailabFilterModelCategory === 'function') ailabFilterModelCategory('requesty', btn);
    }""")
    page.wait_for_timeout(1000)
    req_count = page.locator("#ailabModelModalGrid .ailab-mcard").count()
    print(f"[*] Requesty AI displayed cards: {req_count}")
    page.screenshot(path=requesty_path)
    print(f"[*] Saved Requesty screenshot: {requesty_path}")

    browser.close()
    print("[*] Live Playwright verification finished successfully!")
