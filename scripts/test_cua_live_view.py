# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 950})
        page = await context.new_page()

        # Load local dashboard file
        url = "file:///" + os.path.abspath("deploy/complete_nanopro_dashboard.html").replace("\\", "/")
        print(f"Loading {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)

        # Switch to global_ai_lab view & simulate auth
        await page.evaluate("""() => {
            document.body.classList.add('auth-verified');
            document.documentElement.classList.add('auth-verified');
            const gw = document.getElementById('nanoProAuthGateway');
            if (gw) { gw.classList.remove('force-show'); gw.style.display = 'none'; }
            if (typeof switchView === 'function') switchView('global_ai_lab');
        }""")
        await page.wait_for_timeout(800)

        # 1. Verify CUA Toggle Button
        toggle_btn = page.locator("#ailabCuaToggleBtn")
        btn_vis = await toggle_btn.is_visible()
        print(f"CUA Toggle Button visible: {btn_vis}")

        # 2. Verify CUA Right Panel
        panel = page.locator("#ailabCuaPanel")
        panel_vis = await panel.is_visible()
        print(f"CUA Right Panel visible: {panel_vis}")

        # 3. Check CUA sub-elements
        url_input = page.locator("#ailabCuaUrlInput")
        print(f"CUA URL Input visible: {await url_input.is_visible()}")

        cursor = page.locator("#ailabCuaCursor")
        print(f"CUA Laser Cursor present: {await cursor.count() > 0}")

        exec_btn = page.locator(".ailab-cua-exec-btn")
        print(f"CUA Exec Button visible: {await exec_btn.is_visible()}")

        # 4. Trigger an autonomous CUA scenario
        print("Triggering preset scenario 'wiki' (Set-of-Marks, Cursor movement, Navigation)...")
        await page.evaluate("() => { if (window.AILAB_CUA) window.AILAB_CUA.presetScenario('wiki'); }")
        await page.wait_for_timeout(2500)

        # Check step timeline count
        step_items = await page.locator(".ailab-step-item").count()
        print(f"Step timeline items count: {step_items}")

        # Take screenshot of the full split-screen view
        shot_path = "artifacts/cua_split_screen_live_verified.png"
        await page.screenshot(path=shot_path, full_page=False)
        print(f"Saved screenshot to {shot_path}")

        # Also copy to brain artifacts directory
        brain_shot = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/cua_split_screen_live_verified.png"
        await page.screenshot(path=brain_shot, full_page=False)
        print(f"Saved to {brain_shot}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
