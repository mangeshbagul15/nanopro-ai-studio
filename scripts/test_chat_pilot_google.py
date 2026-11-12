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

        # Send command from the MAIN CHAT:
        prompt = "side screen share madhe google search kara"
        print(f"Typing into main chat prompt input: '{prompt}'...")
        await page.fill("#ailabPromptInput", prompt)
        await page.click("#ailabSendBtn")
        print("Dispatched prompt from main chat!")

        # Wait for CUA panel to auto-open and navigate
        await page.wait_for_timeout(2500)

        panel = page.locator("#ailabCuaPanel")
        panel_vis = await panel.is_visible()
        print(f"CUA Panel automatically opened: {panel_vis}")

        sidebar = page.locator("#ailabSidebar")
        sidebar_collapsed = await page.evaluate("() => document.getElementById('ailabSidebar').classList.contains('collapsed')")
        print(f"Sidebar auto-collapsed for 50-50 screen: {sidebar_collapsed}")

        url_text = await page.locator("#ailabCuaUrlText").inner_text()
        print(f"CUA Browser URL Text: {url_text}")

        cursor = page.locator("#ailabCuaCursor")
        print(f"Laser cursor active: {await cursor.count() > 0}")

        # Check absence of cluttered bottom box
        task_input_count = await page.locator(".ailab-cua-task-row").count()
        presets_count = await page.locator(".ailab-cua-presets").count()
        print(f"Cluttered task row count (must be 0): {task_input_count}")
        print(f"Cluttered presets row count (must be 0): {presets_count}")

        # Capture screenshot
        shot_path = "artifacts/cua_pure_screen_from_chat.png"
        await page.screenshot(path=shot_path, full_page=False)
        print(f"Saved screenshot to {shot_path}")

        # Copy to brain artifacts
        brain_shot = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/cua_pure_screen_from_chat.png"
        await page.screenshot(path=brain_shot, full_page=False)
        print(f"Saved to {brain_shot}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
