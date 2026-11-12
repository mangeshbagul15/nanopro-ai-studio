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
        await page.wait_for_timeout(1200)

        # 1. Submit prompt in chat
        print("Submitting prompt from chat...")
        await page.fill("#ailabPromptInput", "side screen share madhe google search kara")
        await page.click("#ailabSendBtn")

        # 2. Wait for CUA execution & HITL collaborative card to appear
        print("Waiting for CUA search and HITL collaborative card...")
        await page.wait_for_timeout(4500)

        hitl_card = await page.query_selector(".ailab-hitl-card")
        print("HITL Collaboration card appeared in chat:", hitl_card is not None)

        rec_btn = await page.query_selector(".ailab-hitl-btn.recommended")
        print("Recommended option button found:", rec_btn is not None)
        if rec_btn:
            btn_text = await rec_btn.inner_text()
            print("Recommended button text:", btn_text.encode('ascii', 'backslashreplace').decode('ascii'))

            # 3. User clicks the Recommended Option!
            print("User clicks the recommended option [1]...")
            await rec_btn.click()
            await page.wait_for_timeout(2000)

            # Check approved banner in chat
            approved_banner = await page.query_selector(".ailab-hitl-approved")
            print("Approved banner rendered:", approved_banner is not None)
            if approved_banner:
                btext = await approved_banner.inner_text()
                print("Banner text:", btext.encode('ascii', 'backslashreplace').decode('ascii'))

            # Check HUD text in CUA
            hud_text = await page.text_content("#ailabCuaActionDesc")
            print("CUA HUD text after approval:", hud_text)

        # Take screenshot
        screenshot_path = "artifacts/hitl_collaboration_verified.png"
        await page.screenshot(path=screenshot_path)
        print(f"Saved screenshot to {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
