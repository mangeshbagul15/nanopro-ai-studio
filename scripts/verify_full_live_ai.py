import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[1] Opening live site...", flush=True)
        await page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/", wait_until="networkidle", timeout=45000)

        # Login if needed
        if await page.locator("#loginUsername").is_visible():
            print("Logging in...", flush=True)
            await page.fill("#loginUsername", "nanopro")
            await page.fill("#loginPassword", "Mangesh@123")
            await page.click("#loginBtn")
            await page.wait_for_timeout(3500)

        # Switch to global_ai_lab view
        await page.evaluate("""() => {
            document.body.classList.add('auth-verified');
            document.documentElement.classList.add('auth-verified');
            const gw = document.getElementById('nanoProAuthGateway');
            if (gw) { gw.classList.remove('force-show'); gw.style.display = 'none'; }
            if (typeof switchView === 'function') switchView('global_ai_lab');
        }""")
        await page.wait_for_timeout(2000)

        # Check existing messages if any or dispatch prompt
        msg_count = await page.locator(".ailab-msg-assistant").count()
        if msg_count == 0:
            prompt = "Explain NanoPro Lakehouse Architecture with diagram and symbols in Marathi"
            print(f"Dispatching prompt: {prompt}", flush=True)
            await page.fill("#ailabPromptInput", prompt)
            await page.click("#ailabSendBtn")
            try:
                await page.wait_for_selector("#ailab-generating-msg", state="detached", timeout=45000)
                print("AI generation finished!", flush=True)
            except Exception as e:
                print("Timeout:", e, flush=True)
            await page.wait_for_timeout(2000)

        # Extract assistant message
        asst_text = await page.evaluate("""() => {
            const els = document.querySelectorAll('.ailab-msg-assistant .ailab-bubble');
            return els.length > 0 ? els[els.length - 1].innerText : 'None';
        }""")
        
        with open("artifacts/assistant_live_response.txt", "w", encoding="utf-8") as f:
            f.write(asst_text)
        print("Saved assistant response to artifacts/assistant_live_response.txt!")

        # Check mermaid container
        mermaid_count = await page.locator(".ailab-mermaid-container").count()
        svg_count = await page.locator(".ailab-mermaid-container svg").count()
        print(f"Mermaid containers: {mermaid_count}, Rendered SVGs: {svg_count}")

        # Capture live screenshot
        shot_path = "artifacts/global_ai_lab_full_mermaid_verified.png"
        await page.screenshot(path=shot_path, full_page=False)
        print(f"Saved screenshot to {shot_path}")

        # Also copy to brain artifacts directory
        brain_shot = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/global_ai_lab_full_mermaid_verified.png"
        await page.screenshot(path=brain_shot, full_page=False)
        print(f"Saved to {brain_shot}")

        await browser.close()

asyncio.run(main())
