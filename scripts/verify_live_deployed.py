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
        await page.wait_for_timeout(2000)

        # Type in main chat: "side screen share madhe google search kara"
        print("Submitting prompt from main chat...")
        await page.fill("#ailabPromptInput", "side screen share madhe google search kara")
        await page.click("#ailabSendBtn")

        # Wait for live response & CUA autonomous execution
        print("Waiting for CUA navigation & edge response...")
        await page.wait_for_timeout(4000)

        url_text = await page.text_content("#ailabCuaUrlText")
        print("Live CUA Browser URL:", url_text)

        # Check last assistant message in chat
        msgs = await page.query_selector_all(".ailab-msg.assistant")
        print(f"Assistant messages count: {len(msgs)}")
        if msgs:
            last_text = await msgs[-1].inner_text()
            print("Last assistant response snippet:\n", last_text[:250])

        # Screenshot live page
        screenshot_path = "artifacts/live_deployed_cua_google_search.png"
        await page.screenshot(path=screenshot_path)
        print(f"Saved live screenshot to {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
