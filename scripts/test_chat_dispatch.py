import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        # Load local dashboard file
        url = "file:///" + os.path.abspath("deploy/complete_nanopro_dashboard.html").replace("\\", "/")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)

        # Switch to global_ai_lab view
        await page.evaluate("""() => {
            if (typeof switchView === 'function') {
                switchView('global_ai_lab');
            } else {
                document.querySelectorAll('.workspace-view').forEach(v => v.classList.remove('active'));
                const lab = document.getElementById('view-global_ai_lab');
                if (lab) lab.classList.add('active');
            }
        }""")
        await page.wait_for_timeout(500)

        # Type message in prompt textarea
        textarea = page.locator("#ailabPromptInput")
        await textarea.fill("NanoPro architecture flow diagram dakhva")
        print("Filled textarea!")

        # Intercept network requests or check submit function
        # Click send button
        send_btn = page.locator("#ailabSendBtn")
        await send_btn.click()
        print("Clicked send button!")
        await page.wait_for_timeout(800)

        # Check if message appears in the chat message list
        msg_count = await page.locator(".ailab-msg").count()
        print(f"Message count in chat: {msg_count}")
        last_msg = await page.locator(".ailab-msg").last.inner_text()
        print(f"Last message snippet: {last_msg[:120]}...")

        await page.screenshot(path="artifacts/local_chat_sent.png")
        print("Screenshot saved to artifacts/local_chat_sent.png")

        await browser.close()

asyncio.run(main())
