"""Check DOM content of live page."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    
    html = page.content()
    print("Page title:", page.title())
    print("Page URL:", page.url)
    print("Contains ailabOpenAirflowModal:", "ailabOpenAirflowModal" in html)
    print("Contains ailabExplorer:", "ailabExplorer" in html)
    print("Contains BANK_DB:", "BANK_DB" in html)
    print("Buttons count:", len(page.query_selector_all("button")))
    
    # Check if view is hidden or if #view-global_ai_lab is active
    view = page.query_selector("#view-global_ai_lab")
    if view:
        print("#view-global_ai_lab display:", view.evaluate("el => window.getComputedStyle(el).display"))
        print("#view-global_ai_lab class:", view.get_attribute("class"))
    else:
        print("#view-global_ai_lab NOT found in DOM!")

    browser.close()
