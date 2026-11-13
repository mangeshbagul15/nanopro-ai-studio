"""Diagnose button click and javascript errors on live page."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    console_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: console_logs.append(f"[PAGE_ERROR] {err}"))

    page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # Login
    login_visible = page.evaluate("() => !!document.getElementById('loginUsername') && document.getElementById('loginUsername').offsetWidth > 0")
    if login_visible:
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3000)

    page.evaluate("() => { if (typeof switchView === 'function') switchView('global_ai_lab'); }")
    page.wait_for_timeout(2000)

    # Inspect button
    btn_info = page.evaluate("""() => {
        const btn = document.querySelector('button[onclick*="ailabOpenAirflowModal"]');
        if (!btn) return { found: false };
        const rect = btn.getBoundingClientRect();
        const style = window.getComputedStyle(btn);
        return {
            found: true,
            rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
            display: style.display,
            visibility: style.visibility,
            opacity: style.opacity,
            pointerEvents: style.pointerEvents,
            zIndex: style.zIndex,
            text: btn.innerText
        };
    }""")
    print("Button Info:", btn_info)

    # Check function existence
    fn_info = page.evaluate("""() => {
        return {
            hasFn: typeof window.ailabOpenAirflowModal === 'function',
            hasModal: !!document.getElementById('ailabAirflowModal')
        };
    }""")
    print("Function & Modal Info:", fn_info)

    # Try calling ailabOpenAirflowModal() via page.evaluate
    print("Executing window.ailabOpenAirflowModal()...")
    res = page.evaluate("""async () => {
        try {
            await window.ailabOpenAirflowModal();
            const modal = document.getElementById('ailabAirflowModal');
            return {
                called: true,
                isOpen: modal ? modal.classList.contains('is-open') : false,
                display: modal ? window.getComputedStyle(modal).display : null,
                opacity: modal ? window.getComputedStyle(modal).opacity : null,
                visibility: modal ? window.getComputedStyle(modal).visibility : null,
                zIndex: modal ? window.getComputedStyle(modal).zIndex : null
            };
        } catch (e) {
            return { called: false, error: e.toString() };
        }
    }""")
    print("Execution Result:", res)

    # Print console logs
    print("\n--- Browser Console Logs ---")
    for log in console_logs[-20:]:
        print(log)

    browser.close()
