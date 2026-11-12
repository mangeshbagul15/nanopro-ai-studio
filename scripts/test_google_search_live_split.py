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
            
            // Switch to global_ai_lab view
            if (typeof switchView === 'function') switchView('global_ai_lab');
            const v = document.getElementById('view-global_ai_lab');
            if (v) {
                document.querySelectorAll('.view-container').forEach(el => el.classList.remove('active'));
                v.classList.add('active');
                v.style.display = 'flex';
            }
        }""")
        await page.wait_for_timeout(1200)

        # Verify CUA is initialized
        print("Checking initial state...")
        panel = await page.query_selector("#ailabCuaPanel")
        is_open = await panel.evaluate("el => el.classList.contains('active')")
        print("CUA Panel initially open:", is_open)

        # Now simulate typing in main chat: "side screen share madhe google search kara"
        print("Submitting chat prompt to trigger autonomous CUA Google Search...")
        prompt_input = await page.query_selector("#ailabPromptInput")
        await prompt_input.fill("side screen share madhe google search kara")
        
        # Click send button
        await page.click("#ailabSendBtn")

        # Wait for autonomous navigation and cursor animation
        print("Waiting for CUA autonomous Google Search to run...")
        await page.wait_for_timeout(3500)

        # Inspect state after autonomous execution
        url_text = await page.text_content("#ailabCuaUrlText")
        print("CUA Browser URL Text:", url_text)

        # Check if Google srcdoc or content is inside iframe
        iframe = await page.query_selector("#ailabCuaIframe")
        has_srcdoc = await iframe.evaluate("el => el.hasAttribute('srcdoc')")
        srcdoc_len = await iframe.evaluate("el => (el.srcdoc || '').length")
        print(f"Iframe has Google srcdoc: {has_srcdoc} (length: {srcdoc_len})")

        # Check shell collapsed status (50-50 split screen)
        shell_collapsed = await page.evaluate("() => document.getElementById('app-shell')?.classList.contains('sidebar-collapsed')")
        chats_collapsed = await page.evaluate("() => document.getElementById('ailabSidebar')?.classList.contains('collapsed')")
        print(f"Shell collapsed: {shell_collapsed}, Chats & Projects collapsed: {chats_collapsed}")

        # Laser cursor
        cursor_label = await page.text_content("#ailabCuaCursorLabel")
        print("Laser cursor label:", cursor_label)

        # HUD text
        hud_text = await page.text_content("#ailabCuaActionDesc")
        print("HUD text:", hud_text)

        # Take screenshot
        screenshot_path = "artifacts/cua_google_search_split_verified.png"
        await page.screenshot(path=screenshot_path)
        print(f"Saved screenshot to {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
