from playwright.sync_api import sync_playwright
import os

html_path = os.path.abspath('deploy/complete_nanopro_dashboard.html').replace('\\', '/')
file_url = f'file:///{html_path}#global_ai_lab'

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={'width': 1366, 'height': 768})
    page.goto(file_url)
    page.wait_for_timeout(1500)
    
    details = page.evaluate("""() => {
        const center = document.querySelector('#view-global_ai_lab .ailab-topbar-center');
        const children = Array.from(center.children).map(c => ({
            tag: c.tagName,
            cls: c.className,
            box: c.getBoundingClientRect()
        }));
        return {
            centerBox: center.getBoundingClientRect(),
            children
        };
    }""")
    print("Center Details:")
    print("  centerBox:", details['centerBox'])
    for c in details['children']:
        print("  child:", c['cls'], c['box'])
    b.close()
