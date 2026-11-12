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

        # 1. Verify default initial state: CUA is collapsed
        panel = await page.query_selector("#ailabCuaPanel")
        is_collapsed = await panel.evaluate("el => el.classList.contains('collapsed')")
        print(f"Live Initial State - CUA collapsed by default: {is_collapsed}")

        # 2. Submit prompt in chat: "browser madhe open router open kara tyat top var konta model ahe te sanga"
        prompt = "browser madhe open router open kara tyat top var konta model ahe te sanga"
        print(f"Submitting prompt: '{prompt}'...")
        await page.fill("#ailabPromptInput", prompt)
        await page.click("#ailabSendBtn")

        # 3. Wait for CUA execution & Live response
        print("Waiting for CUA OpenRouter navigation & edge response...")
        await page.wait_for_timeout(4500)

        # Check live response in chat
        msgs = await page.query_selector_all(".ailab-msg.assistant")
        print(f"Assistant messages count: {len(msgs)}")
        if msgs:
            text = await msgs[-1].inner_text()
            print("Live Assistant Response:\n", text[:350].encode('ascii', 'backslashreplace').decode('ascii'))

        # Check CUA panel state
        is_active = await panel.evaluate("el => el.classList.contains('active')")
        url_text = await page.text_content("#ailabCuaUrlText")
        cursor_text = await page.text_content("#ailabCuaCursorLabel")
        print(f"Live CUA Panel active: {is_active}")
        print(f"Live CUA URL Bar: {url_text}")
        print(f"Live Laser Cursor: {cursor_text}")

        # Screenshot live page
        screenshot_path = "artifacts/live_openrouter_autonomous_verified.png"
        await page.screenshot(path=screenshot_path)
        print(f"Saved live screenshot to {screenshot_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
