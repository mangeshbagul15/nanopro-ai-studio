from playwright.sync_api import sync_playwright

live_url = "https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(live_url, wait_until='networkidle')
    if page.locator("#loginUsername").is_visible():
        page.fill("#loginUsername", "nanopro")
        page.fill("#loginPassword", "Mangesh@123")
        page.click("#loginBtn")
        page.wait_for_timeout(3500)
    page.evaluate("""() => {
        if (typeof switchView === 'function') switchView('global_ai_lab');
    }""")
    page.wait_for_timeout(3000)

    # Check console errors
    res = page.evaluate("""() => {
        try {
            if (window.ailabLoadExplorer) {
                window.ailabLoadExplorer();
                return "called ailabLoadExplorer, catalog: " + JSON.stringify(window.AILAB_EXPLORER.catalog);
            }
            return "no window.ailabLoadExplorer";
        } catch(e) {
            return "err: " + e.message;
        }
    }""")
    print("Eval result:", res)
    page.wait_for_timeout(1000)
    tree_html = page.locator("#ailabExplorerTree").inner_html()
    print("Content:", repr(tree_html))

    browser.close()
