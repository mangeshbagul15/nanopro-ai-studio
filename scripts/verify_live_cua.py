# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 950})
        page = await context.new_page()

        print("[1] Opening live site https://mangesh-nanopro.mangeshbagul15.workers.dev/ ...")
        await page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/", wait_until="networkidle", timeout=45000)

        # Handle login
        if await page.locator("#loginUsername").is_visible():
            print("Logging in with nanopro...")
            await page.fill("#loginUsername", "nanopro")
            await page.fill("#loginPassword", "Mangesh@123")
            await page.click("#loginBtn")
            await page.wait_for_timeout(3500)

        # Switch to global_ai_lab view & simulate auth
        await page.evaluate("""() => {
            document.body.classList.add('auth-verified');
            document.documentElement.classList.add('auth-verified');
            const gw = document.getElementById('nanoProAuthGateway');
            if (gw) { gw.classList.remove('force-show'); gw.style.display = 'none'; }
            if (typeof switchView === 'function') switchView('global_ai_lab');
        }""")
        await page.wait_for_timeout(1000)

        # Verify CUA toggle button and panel
        toggle_btn = page.locator("#ailabCuaToggleBtn")
        panel = page.locator("#ailabCuaPanel")
        print(f"Live CUA Toggle Button visible: {await toggle_btn.is_visible()}")
        print(f"Live CUA Right Panel visible: {await panel.is_visible()}")

        # Run CUA scenario
        print("Running live CUA Scenario 'wiki'...")
        await page.evaluate("() => { if (window.AILAB_CUA) window.AILAB_CUA.presetScenario('wiki'); }")
        await page.wait_for_timeout(2500)

        # Capture live screenshot
        shot_path = "artifacts/cua_live_split_screen_verified.png"
        await page.screenshot(path=shot_path, full_page=False)
        print(f"Saved live screenshot to {shot_path}")

        # Also copy to brain artifacts directory
        brain_shot = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/cua_live_split_screen_verified.png"
        await page.screenshot(path=brain_shot, full_page=False)
        print(f"Saved to {brain_shot}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
