import os, sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 850})
    page.goto(live_url, wait_until='networkidle')
    page.wait_for_timeout(2000)

    if page.locator("#loginUsername").is_visible():
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3500)

    page.evaluate("if (typeof switchView === 'function') switchView('global_ai_lab');")
    page.wait_for_timeout(2000)

    # Open modal
    page.evaluate("if (typeof ailabOpenModelCatalogModal === 'function') ailabOpenModelCatalogModal();")
    page.wait_for_timeout(1000)

    # Check grid html
    grid_html = page.locator("#ailabModelModalGrid").inner_html()
    print("Grid HTML length:", len(grid_html))
    print("Sample HTML:", grid_html[:500])

    # Check what classes the cards have
    cards = page.locator("#ailabModelModalGrid > *").count()
    print("Direct children count in grid:", cards)

    # Check cachedCatalogModels in browser window
    cached_len = page.evaluate("window.cachedCatalogModels ? window.cachedCatalogModels.length : 'undefined'")
    print("window.cachedCatalogModels length in browser:", cached_len)

    browser.close()
