import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        # Load local dashboard file
        url = "file:///" + os.path.abspath("deploy/complete_nanopro_dashboard.html").replace("\\", "/")
        print(f"Loading {url}...")
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

        # 1. Check Dynamic Island
        island_count = await page.locator("#nanoDynamicIsland, .nano-dynamic-island").count()
        print(f"Dynamic Island count on DOM: {island_count}")

        # 2. Check Dropdowns
        model_select = page.locator("#ailabModelSelect")
        effort_select = page.locator("#ailabEffortSelect")
        model_visible = await model_select.is_visible()
        effort_visible = await effort_select.is_visible()
        print(f"Model select visible: {model_visible}")
        print(f"Effort select visible: {effort_visible}")

        # Check options count
        opts_count = await model_select.locator("option").count()
        print(f"Model options count: {opts_count}")

        # 3. Check functions defined on window
        fns = await page.evaluate("""() => {
            return {
                ailabOpenModelCatalogModal: typeof ailabOpenModelCatalogModal,
                ailabSubmitPrompt: typeof ailabSubmitPrompt,
                ailabNewChat: typeof ailabNewChat,
                mermaid: typeof window.mermaid
            };
        }""")
        print(f"Functions on window: {fns}")

        # 4. Try opening Model Modal
        await page.evaluate("() => { if (typeof ailabOpenModelCatalogModal === 'function') ailabOpenModelCatalogModal(); }")
        await page.wait_for_timeout(400)
        modal_visible = await page.locator("#ailabModelModal").is_visible()
        print(f"Model Modal visible: {modal_visible}")

        # Close modal
        await page.evaluate("() => { if (typeof ailabCloseModelCatalogModal === 'function') ailabCloseModelCatalogModal(); }")
        await page.wait_for_timeout(300)

        # 5. Take screenshot of topbar & chat
        os.makedirs("artifacts", exist_ok=True)
        await page.screenshot(path="artifacts/local_ailab_verified.png", full_page=False)
        print("Screenshot saved to artifacts/local_ailab_verified.png")

        await browser.close()

asyncio.run(main())
