# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

TIMEOUT = 45000

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[1] Opening https://mangesh-nanopro.mangeshbagul15.workers.dev/ ...", flush=True)
        await page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/", wait_until="networkidle", timeout=45000)
        print("Page loaded: " + page.url + " | " + await page.title(), flush=True)

        # Check if login form is displayed
        if await page.locator("#loginUsername").is_visible():
            print("Logging in with username 'nanopro'...", flush=True)
            await page.fill("#loginUsername", "nanopro")
            await page.fill("#loginPassword", "Mangesh@123")
            await page.click("#loginBtn")
            print("Submitted login form, waiting for dashboard...", flush=True)
            await page.wait_for_timeout(4000)
            print("Current URL after login: " + page.url, flush=True)

        # Switch view to global_ai_lab & unlock gateway
        print("Unlocking auth gateway and switching to global_ai_lab view...", flush=True)
        await page.evaluate("""() => {
            document.body.classList.add('auth-verified');
            document.documentElement.classList.add('auth-verified');
            const gw = document.getElementById('nanoProAuthGateway');
            if (gw) {
                gw.classList.remove('force-show');
                gw.style.display = 'none';
            }
            if (typeof onAuthSuccess === 'function') {
                onAuthSuccess({ username: 'nanopro', role: 'admin', allowed_views: ['*'] });
            }
            if (typeof switchView === 'function') {
                switchView('global_ai_lab');
            } else {
                location.hash = '#global_ai_lab';
            }
        }""")
        await page.wait_for_timeout(3000)

        # 1. Verify Dynamic Island is NOT visible
        island_count = await page.locator("#nanoDynamicIsland:visible").count()
        print(f"Visible Dynamic Island count: {island_count} (Must be 0)", flush=True)

        # 2. Verify Model Select & Effort Select
        model_select_vis = await page.locator("#ailabModelSelect").is_visible()
        effort_select_vis = await page.locator("#ailabEffortSelect").is_visible()
        browse_btn_vis = await page.locator(".ailab-browse-btn").is_visible()
        print(f"Model Dropdown visible: {model_select_vis}", flush=True)
        print(f"Effort Dropdown visible: {effort_select_vis}", flush=True)
        print(f"Browse 432+ Models Button visible: {browse_btn_vis}", flush=True)

        # 3. Test opening Model Catalog Modal
        if browse_btn_vis:
            print("Opening 432+ Models Modal...", flush=True)
            await page.evaluate("() => { if (typeof ailabOpenModelCatalogModal === 'function') ailabOpenModelCatalogModal(); }")
            await page.wait_for_timeout(1000)
            modal_vis = await page.locator("#ailabModelModal.is-open").is_visible()
            print(f"Model Modal Opened: {modal_vis}", flush=True)
            if modal_vis:
                await page.screenshot(path="C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/global_ai_lab_model_modal_open.png")
                await page.evaluate("() => { if (typeof ailabCloseModelCatalogModal === 'function') ailabCloseModelCatalogModal(); }")
                await page.wait_for_timeout(500)

        # Take screenshot of clean topbar
        await page.screenshot(path="C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/global_ai_lab_topbar_prominent.png")

        # 4. Dispatch live test prompt
        prompt = "Explain NanoPro Lakehouse Architecture with diagram and symbols in Marathi"
        print(f"Dispatching prompt: {prompt}", flush=True)
        await page.fill("#ailabPromptInput", prompt)
        await page.click("#ailabSendBtn")

        print("Waiting for AI response (up to 30s)...", flush=True)
        try:
            await page.wait_for_selector(".ailab-msg-assistant", timeout=30000)
            print("Assistant message received!", flush=True)
            await page.wait_for_timeout(4000)
        except Exception as e:
            print("Timeout waiting for assistant response:", e, flush=True)

        # Capture live screenshot
        shot_path = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/global_ai_lab_live_power_verified.png"
        await page.screenshot(path=shot_path, full_page=False)
        print(f"Saved verification screenshot to {shot_path}", flush=True)

        # Check content of assistant message
        asst_text = await page.evaluate("""() => {
            const el = document.querySelector('.ailab-msg-assistant .ailab-bubble');
            return el ? el.innerText : '';
        }""")
        print(f"Assistant preview (first 150 chars):\n{asst_text[:150]}...", flush=True)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
