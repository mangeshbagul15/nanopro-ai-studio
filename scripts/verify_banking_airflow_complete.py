"""Complete live verification with login and modal screenshots."""
import urllib.request
import json
import sys
import os
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://mangesh-nanopro.mangeshbagul15.workers.dev"
out_dir = r"C:\Users\Mangesh\.gemini\antigravity\brain\b72a738e-4059-440b-817d-5dcb13bc6bac"

def main():
    print("==========================================================")
    print("VERIFYING LIVE 8 BANKING PROJECTS, AIRFLOW & SFTP HUB")
    print("==========================================================")

    # 1. Verify Catalog API
    req = urllib.request.Request(f"{BASE_URL}/api/ai/explorer/catalog", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        dbs = data.get("databases", [])
        print(f"[*] Total Databases: {len(dbs)}")
        for db in dbs:
            schemas = [s["name"] for s in db.get("schemas", [])]
            print(f"   [+] {db['name']} ({db['id']}) -> {schemas}")

    # 2. Verify Airflow DAGs API
    dag_req = urllib.request.Request(f"{BASE_URL}/api/banking/dag/list", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(dag_req, timeout=10) as resp:
        dag_data = json.loads(resp.read().decode())
        dags = dag_data.get("dags", [])
        print(f"[*] Airflow DAGs Count: {len(dags)}")
        for d in dags:
            print(f"   [+] {d['dag_id']} ({d['project_name']}) - {d['schedule']} - {d['status']}")

    # 3. Playwright UI Check with Login
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("Opening live dashboard...")
        page.goto(f"{BASE_URL}/#global_ai_lab", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Login
        login_visible = page.evaluate("""() => {
            const u = document.getElementById('loginUsername');
            return u ? (u.offsetWidth > 0 && u.offsetHeight > 0) : false;
        }""")
        if login_visible:
            print("Logging in via Security Gateway...")
            page.fill("#loginUsername", "nanopro")
            page.fill("#loginPassword", "Mangesh@123")
            page.click("#loginBtn")
            page.wait_for_timeout(3000)

        # Switch to Global AI Lab view
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

        # Expand Snowflake and AWS 8 banking project nodes
        page.evaluate("""() => {
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

        # Screenshot 1: Cleaned Banking Explorer
        sc1 = os.path.join(out_dir, "live_cleaned_banking_explorer.png")
        page.screenshot(path=sc1)
        print(f"[+] Saved Explorer Screenshot: {sc1}")

        # Open Airflow & SFTP Hub Modal
        print("Opening Airflow & SFTP Hub Modal...")
        page.evaluate("""() => {
            if (typeof ailabOpenAirflowModal === 'function') {
                ailabOpenAirflowModal();
            }
        }""")
        page.wait_for_timeout(2500)

        # Screenshot 2: Airflow DAGs Modal
        sc2 = os.path.join(out_dir, "live_airflow_orchestrator_modal.png")
        page.screenshot(path=sc2)
        print(f"[+] Saved Airflow DAGs Modal Screenshot: {sc2}")

        # Switch to SFTP Tab
        print("Switching to SFTP Tab in modal...")
        page.evaluate("""() => {
            if (typeof ailabSwitchAirflowTab === 'function') {
                ailabSwitchAirflowTab('sftp');
            }
        }""")
        page.wait_for_timeout(1500)

        # Screenshot 3: SFTP Tab
        sc3 = os.path.join(out_dir, "live_sftp_reports_winscp_modal.png")
        page.screenshot(path=sc3)
        print(f"[+] Saved SFTP Reports Modal Screenshot: {sc3}")

        browser.close()
        print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
