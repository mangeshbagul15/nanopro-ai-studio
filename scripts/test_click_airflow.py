"""Verify clicking Airflow modal with exact selector."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    print("Navigating to https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab ...")
    page.goto("https://mangesh-nanopro.mangeshbagul15.workers.dev/#global_ai_lab", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    # Click the Airflow button via exact attribute
    print("Clicking button[onclick*='ailabOpenAirflowModal']...")
    page.click('button[onclick*="ailabOpenAirflowModal"]')
    page.wait_for_timeout(2500)

    # Screenshot: Airflow Orchestrator DAGs Modal
    airflow_path = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/live_airflow_orchestrator_modal.png"
    page.screenshot(path=airflow_path)
    print("Saved Airflow modal screenshot:", airflow_path)

    # Switch to SFTP Reports tab
    print("Clicking #tabAirflowSftp...")
    page.click('#tabAirflowSftp')
    page.wait_for_timeout(1500)

    # Screenshot: SFTP Reports & WinSCP tab
    sftp_modal_path = "C:/Users/Mangesh/.gemini/antigravity/brain/b72a738e-4059-440b-817d-5dcb13bc6bac/live_sftp_reports_winscp_modal.png"
    page.screenshot(path=sftp_modal_path)
    print("Saved SFTP modal screenshot:", sftp_modal_path)

    browser.close()
    print("DONE! All screenshots saved successfully.")
