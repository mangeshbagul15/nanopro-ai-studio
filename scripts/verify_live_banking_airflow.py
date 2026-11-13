"""Verify live Cloudflare Worker Explorer, Airflow Orchestrator, and SFTP Hub."""
import json
import urllib.request
from playwright.sync_api import sync_playwright

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# 1. Verify Catalog API
cat_req = urllib.request.Request("https://mangesh-nanopro.mangeshbagul15.workers.dev/api/ai/explorer/catalog", headers=headers)
with urllib.request.urlopen(cat_req) as resp:
    cat_data = json.loads(resp.read().decode('utf-8'))
    print("Catalog status:", cat_data.get("status"))
    dbs = cat_data.get("databases", [])
    print("Databases count:", len(dbs))
    for db in dbs:
        print(f" - {db['name']} ({db['id']}) schemas: {[s['name'] for s in db.get('schemas', [])]}")

# 2. Verify Airflow DAGs API
dag_req = urllib.request.Request("https://mangesh-nanopro.mangeshbagul15.workers.dev/api/banking/dag/list", headers=headers)
with urllib.request.urlopen(dag_req) as resp:
    dag_data = json.loads(resp.read().decode('utf-8'))
    print("Airflow DAGs status:", dag_data.get("status"))
    print("DAGs count:", len(dag_data.get("dags", [])))
    for d in dag_data.get("dags", []):
        print(f"   * {d['dag_id']}: {d['project_name']} -> {d['schedule']} ({d['status']})")

# 3. Verify SFTP Reports API
sftp_req = urllib.request.Request("https://mangesh-nanopro.mangeshbagul15.workers.dev/api/sftp/reports/list", headers=headers)
with urllib.request.urlopen(sftp_req) as resp:
    sftp_data = json.loads(resp.read().decode('utf-8'))
    print("SFTP Reports count:", len(sftp_data.get("reports", [])))

# 4. Playwright Browser Visual Verification
print("Launching Playwright...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    print("Navigating to https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab ...")
    page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    # Screenshot 1: Cleaned Banking Explorer
    explorer_path = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/live_cleaned_banking_explorer.png"
    page.screenshot(path=explorer_path)
    print("Saved explorer screenshot:", explorer_path)

    # Click the Airflow & SFTP button
    print("Clicking Airflow & SFTP button...")
    page.click('button:has-text("Airflow & SFTP")')
    page.wait_for_timeout(2000)

    # Screenshot 2: Airflow Orchestrator DAGs Modal
    airflow_path = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/live_airflow_orchestrator_modal.png"
    page.screenshot(path=airflow_path)
    print("Saved Airflow modal screenshot:", airflow_path)

    # Switch to SFTP Reports tab
    print("Clicking SFTP Reports & WinSCP tab...")
    page.click('#tabAirflowSftp')
    page.wait_for_timeout(1500)

    # Screenshot 3: SFTP Reports & WinSCP tab
    sftp_modal_path = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/live_sftp_reports_winscp_modal.png"
    page.screenshot(path=sftp_modal_path)
    print("Saved SFTP modal screenshot:", sftp_modal_path)

    browser.close()
    print("All live verifications completed successfully!")
