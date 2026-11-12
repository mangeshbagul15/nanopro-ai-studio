from playwright.sync_api import sync_playwright
import os

html_path = os.path.abspath('deploy/complete_nanopro_dashboard.html').replace('\\', '/')
file_url = f'file:///{html_path}#global_ai_lab'

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={'width': 1366, 'height': 768})
    page.goto(file_url)
    page.wait_for_timeout(1500)
    
    sections = page.evaluate("""() => {
        const left = document.querySelector('#view-global_ai_lab .ailab-topbar-left').getBoundingClientRect();
        const center = document.querySelector('#view-global_ai_lab .ailab-topbar-center').getBoundingClientRect();
        const right = document.querySelector('#view-global_ai_lab .ailab-topbar-right').getBoundingClientRect();
        return {
            left: { x: left.x, width: left.width, right: left.right },
            center: { x: center.x, width: center.width, right: center.right },
            right: { x: right.x, width: right.width, right: right.right },
            overlap_left_center: left.right > center.x,
            overlap_center_right: center.right > right.x
        };
    }""")
    print('Sections:', sections)
    b.close()
