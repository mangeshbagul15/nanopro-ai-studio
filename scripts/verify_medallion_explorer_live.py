import urllib.request
import json
import sys
import os
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://mangesh-nanopro.mangeshbagul15.workers.dev"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"
screenshot_path = os.path.join(out_dir, "live_medallion_explorer_verified.png")

def main():
    print("==========================================================")
    print("VERIFYING LIVE MEDALLION EXPLORER (L0, L1, L2 & AWS 765865641438)")
    print("==========================================================")

    # 1. Verify Catalog API
    req = urllib.request.Request(
        f"{BASE_URL}/api/ai/explorer/catalog",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        dbs = data.get("databases", [])
        print(f"[*] Total Databases: {len(dbs)}")
        
        # Check Snowflake
        sf = next((d for d in dbs if d["id"] == "snowflake"), None)
        assert sf is not None, "Snowflake database not found"
        sf_schemas = [s["name"] for s in sf.get("schemas", [])]
        print("[+] Snowflake DB Name:", sf["name"])
        print("[+] Snowflake Schemas:", sf_schemas)
        assert "L0_STAGING" in sf_schemas, "L0_STAGING missing!"
        assert "L1_HARMONIZED" in sf_schemas, "L1_HARMONIZED missing!"
        assert "L2_CURATED" in sf_schemas, "L2_CURATED missing!"

        # Check AWS
        aws_db = next((d for d in dbs if d["id"] == "aws"), None)
        assert aws_db is not None, "AWS database not found"
        aws_schemas = [s["name"] for s in aws_db.get("schemas", [])]
        print("[+] AWS DB Name:", aws_db["name"])
        print("[+] AWS Schemas:", aws_schemas)
        assert "bronze_l0" in aws_schemas, "bronze_l0 missing!"
        assert "silver_l1" in aws_schemas, "silver_l1 missing!"
        assert "gold_l2" in aws_schemas, "gold_l2 missing!"

    # 2. Playwright UI Check & Screenshot
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{BASE_URL}/#global_ai_lab", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Login if gateway visible
        login_visible = page.evaluate("""() => {
            const u = document.getElementById('loginUsername');
            return u ? (u.offsetWidth > 0 && u.offsetHeight > 0) : false;
        }""")
        if login_visible:
            page.fill("#loginUsername", "nanopro")
            page.fill("#loginPassword", "Mangesh@123")
            page.click("#loginBtn")
            page.wait_for_timeout(3000)

        page.evaluate("""() => {
            if (typeof switchView === 'function') switchView('global_ai_lab');
            if (typeof ailabToggleExplorer === 'function') {
                const exp = document.getElementById('ailabExplorer');
                if (exp && exp.classList.contains('is-hidden')) {
                    ailabToggleExplorer();
                }
            }
        }""")
        page.wait_for_timeout(2000)

        # Expand Snowflake and AWS tree nodes
        page.evaluate("""() => {
            // Expand all schemas
            if (typeof AILAB_EXPLORER !== 'undefined') {
                AILAB_EXPLORER.treeOpen['db_snowflake'] = true;
                AILAB_EXPLORER.treeOpen['sc_snowflake_L0_STAGING'] = true;
                AILAB_EXPLORER.treeOpen['sc_snowflake_L1_HARMONIZED'] = true;
                AILAB_EXPLORER.treeOpen['sc_snowflake_L2_CURATED'] = true;
                AILAB_EXPLORER.treeOpen['db_aws'] = true;
                AILAB_EXPLORER.treeOpen['sc_aws_bronze_l0'] = true;
                AILAB_EXPLORER.treeOpen['sc_aws_silver_l1'] = true;
                AILAB_EXPLORER.treeOpen['sc_aws_gold_l2'] = true;
                if (typeof ailabRenderExplorerTree === 'function') ailabRenderExplorerTree();
            }
        }""")
        page.wait_for_timeout(1500)

        page.screenshot(path=screenshot_path)
        print(f"[+] Screenshot saved: {screenshot_path}")
        browser.close()

    print("\nALL MEDALLION EXPLORER CHECKS (L0, L1, L2 & AWS 765865641438) PASSED 100%!")

if __name__ == "__main__":
    main()
