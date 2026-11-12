# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 950})
        await context.add_cookies([{
            'name': 'nanopro_session',
            'value': 'np_sess_edge_mangesh2026',
            'domain': 'mangesh-nanopro.mangeshbagul15.workers.dev',
            'path': '/'
        }])
        page = await context.new_page()

        live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/?token=np_sess_edge_mangesh2026#global_ai_lab"
        print(f"Loading live URL: {live_url}...")
        await page.goto(live_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        # 1. Type prompt in main chat
        print("Submitting chat prompt on live site...")
        await page.fill("#ailabPromptInput", "side screen share madhe google search kara")
        await page.click("#ailabSendBtn")

        # 2. Wait for CUA execution & HITL collaborative card
        print("Waiting for CUA execution & HITL collaborative card...")
        await page.wait_for_timeout(4500)

        # Check HITL card
        hitl_card = await page.query_selector(".ailab-hitl-card")
        print("Live HITL Collaboration card rendered:", hitl_card is not None)

        rec_btn = await page.query_selector(".ailab-hitl-btn.recommended")
        print("Live Recommended button found:", rec_btn is not None)
        if rec_btn:
            # 3. Click the recommended option
            print("Clicking recommended button [1] live...")
            await rec_btn.click()
            await page.wait_for_timeout(2000)

            approved = await page.query_selector(".ailab-hitl-approved")
            print("Live approved banner rendered:", approved is not None)

        # Screenshot live page
        screenshot_path = "artifacts/live_hitl_collaboration.png"
        await page.screenshot(path=screenshot_path)
        print(f"Saved live screenshot to {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
