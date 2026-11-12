# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 950})
        page = await context.new_page()

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
            const v = document.getElementById('view-global_ai_lab');
            if (v) {
                document.querySelectorAll('.view-container').forEach(el => el.classList.remove('active'));
                v.classList.add('active');
                v.style.display = 'flex';
            }
        }""")
        await page.wait_for_timeout(1000)

        # 1. VERIFY REQUIREMENT 1: CUA is COLLAPSED by default on initial view!
        panel = await page.query_selector("#ailabCuaPanel")
        is_collapsed = await panel.evaluate("el => el.classList.contains('collapsed')")
        chats_visible = await page.query_selector("#ailabSidebar")
        is_chats_visible = await chats_visible.is_visible() if chats_visible else False
        print(f"CUA panel collapsed by default: {is_collapsed}")
        print(f"Chats & Projects visible by default: {is_chats_visible}")

        # Take screenshot of clean initial view
        await page.screenshot(path="artifacts/clean_initial_view_no_cua.png")
        print("Saved clean initial view screenshot to artifacts/clean_initial_view_no_cua.png")

        # 2. Test New Chat button
        chats_count_before = await page.evaluate("() => window.AILAB ? window.AILAB.chats.length : 0")
        print(f"Chats count before New Chat: {chats_count_before}")
        await page.click("button:has-text('New Chat')")
        await page.wait_for_timeout(300)
        chats_count_after = await page.evaluate("() => window.AILAB ? window.AILAB.chats.length : 0")
        print(f"Chats count after New Chat: {chats_count_after} (Increased: {chats_count_after > chats_count_before})")

        # 3. Test 432+ Models modal
        await page.click("button:has-text('432+ Models')")
        await page.wait_for_timeout(500)
        modal = await page.query_selector("#ailabModelModal")
        modal_open = await modal.evaluate("el => el.classList.contains('is-open')") if modal else False
        print(f"432+ Models modal opened: {modal_open}")
        await page.click("#ailabModelModal .ailab-modal-close")
        await page.wait_for_timeout(300)

        # 4. VERIFY REQUIREMENT 2: OpenRouter Prompt & Advanced CUA execution!
        prompt = "browser madhe open router open kara tyat top var konta model ahe te sanga"
        print(f"\nSubmitting prompt: '{prompt}'...")
        await page.fill("#ailabPromptInput", prompt)
        await page.click("#ailabSendBtn")

        # Wait for CUA execution
        print("Waiting for CUA OpenRouter navigation...")
        await page.wait_for_timeout(3500)

        # CUA panel should now be active!
        is_panel_active = await panel.evaluate("el => el.classList.contains('active')")
        url_text = await page.text_content("#ailabCuaUrlText")
        cursor_text = await page.text_content("#ailabCuaCursorLabel")
        print(f"CUA Panel active now: {is_panel_active}")
        print(f"CUA URL Bar text: {url_text}")
        print(f"Laser cursor text: {cursor_text}")

        # Screenshot of CUA with OpenRouter
        await page.screenshot(path="artifacts/openrouter_cua_verified.png")
        print("Saved screenshot to artifacts/openrouter_cua_verified.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
