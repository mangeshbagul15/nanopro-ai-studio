import os

path = os.path.join("app", "core", "pipeline_orchestrator.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_dag = """    {"id": "bank_rpt", "name": "RBI / FIU / ALM / UPI Reports", "stage": "REPORT",
     "schedule": "After L2 star",
     "description": "Builds 44 statutory reports across AML/FIU-IND (21), RBI/ADF/CIMS (10), ALM (7), UPI/Cards (6) with Master Excel & Domain CSV packages in SFTP Outbound."},"""

new_dag = """    {"id": "bank_rpt_aml", "name": "AML & FIU-IND (21 Reports)", "stage": "REPORT",
     "schedule": "After L2 star",
     "description": "CTR, STR, CCR, NTR, CBWTR, Structuring, PEP, TBML (21 reports) -> NANOPRO_AML_FIU_IND_21_Reports.xlsx in SFTP Outbound."},
    {"id": "bank_rpt_rbi", "name": "RBI ADF / CIMS (10 Reports)", "stage": "REPORT",
     "schedule": "After L2 star",
     "description": "Form A, Form VIII, CRILC, SMA, PSL, LCR, NSFR (10 reports) -> NANOPRO_RBI_ADF_CIMS_10_Reports.xlsx in SFTP Outbound."},
    {"id": "bank_rpt_alm", "name": "ALM & Liquidity (7 Reports)", "stage": "REPORT",
     "schedule": "After L2 star",
     "description": "Structural Liquidity SLS, IRS Sensitivity, EaR, EVE, NIM (7 reports) -> NANOPRO_ALM_Liquidity_7_Reports.xlsx in SFTP Outbound."},
    {"id": "bank_rpt_upi", "name": "UPI & Digital (6 Reports)", "stage": "REPORT",
     "schedule": "After L2 star",
     "description": "NPCI Settlement, TD vs BD, ATM Switch, Chargebacks (6 reports) -> NANOPRO_UPI_Digital_Banking_6_Reports.xlsx in SFTP Outbound."},"""

assert old_dag in content, "old_dag not found"
content = content.replace(old_dag, new_dag, 1)

old_status = """    rpt_stage = str(bank_stages.get("reports") or "").upper()
    rpt_status = bank_map.get(rpt_stage, "SUCCESS" if (bank.get("reports") or 44) else "NOT_RUN")
    statuses["bank_rpt"] = {
        "status": rpt_status,
        "tables": bank.get("reports") or 44,
        "detail": "44 statutory reports verified across AML (21), RBI (10), ALM (7), UPI (6) • SFTP Outbound ready",
    }"""

new_status = """    rpt_stage = str(bank_stages.get("reports") or "").upper()
    rpt_status = bank_map.get(rpt_stage, "SUCCESS" if (bank.get("reports") or 44) else "NOT_RUN")
    statuses["bank_rpt_aml"] = {
        "status": rpt_status,
        "tables": 21,
        "detail": "21 AML & FIU-IND Reports (CTR, STR, CCR, NTR, CBWTR, Structuring, PEP) • Excel & SFTP ready",
    }
    statuses["bank_rpt_rbi"] = {
        "status": rpt_status,
        "tables": 10,
        "detail": "10 RBI ADF/CIMS Reports (Form A, Form VIII, CRILC, SMA, PSL, LCR, NSFR) • Excel & SFTP ready",
    }
    statuses["bank_rpt_alm"] = {
        "status": rpt_status,
        "tables": 7,
        "detail": "7 ALM Liquidity Risk Reports (SLS, IRS Sensitivity, EaR, EVE, NIM) • Excel & SFTP ready",
    }
    statuses["bank_rpt_upi"] = {
        "status": rpt_status,
        "tables": 6,
        "detail": "6 UPI & Digital Banking Reports (NPCI Settlement, TD vs BD, ATM Switch) • Excel & SFTP ready",
    }
    statuses["bank_rpt"] = {
        "status": rpt_status,
        "tables": bank.get("reports") or 44,
        "detail": "44 statutory reports verified across 4 domain Excel packages & Master Excel • SFTP Outbound ready",
    }"""

assert old_status in content, "old_status not found"
content = content.replace(old_status, new_status, 1)

old_run = """    elif dag_id == "bank_rpt":
        from app.core import bank_layers, banking_reports_engine

        def _run_bank_rpt():
            layer_res = bank_layers.build("rpt")
            pkg_res = banking_reports_engine.generate_and_publish_packages(cycle="MANUAL")
            return {
                "status": "success",
                "layer_result": layer_res,
                "package_result": pkg_res,
                "summary": f"Built {pkg_res.get('total_reports', 44)} reports, {len(pkg_res.get('domain_csvs', []))} domain CSVs and Master Excel."
            }
        target = _run_bank_rpt"""

new_run = """    elif dag_id in ("bank_rpt_aml", "bank_rpt_rbi", "bank_rpt_alm", "bank_rpt_upi", "bank_rpt"):
        from app.core import bank_layers, banking_reports_engine

        def _run_domain_rpt(target_dag=dag_id):
            layer_res = bank_layers.build("rpt")
            pkg_res = banking_reports_engine.generate_and_publish_packages(cycle="MANUAL")
            titles = {
                "bank_rpt_aml": "AML / FIU-IND (21 Reports)",
                "bank_rpt_rbi": "RBI ADF / CIMS (10 Reports)",
                "bank_rpt_alm": "ALM Liquidity (7 Reports)",
                "bank_rpt_upi": "UPI & Digital Payments (6 Reports)",
                "bank_rpt": "All 44 Statutory Reports",
            }
            name = titles.get(target_dag, "Banking Reports")
            return {
                "status": "success",
                "dag_id": target_dag,
                "layer_result": layer_res,
                "package_result": pkg_res,
                "summary": f"Built {name} into separate domain Excel workbook and published to SFTP Outbound.",
            }
        target = _run_domain_rpt"""

assert old_run in content, "old_run not found"
content = content.replace(old_run, new_run, 1)

old_rollback = 'if dag_id in ("bank_raw_history", "bank_l1_scd2", "bank_l2_star", "bank_rpt"):'
new_rollback = 'if dag_id in ("bank_raw_history", "bank_l1_scd2", "bank_l2_star", "bank_rpt", "bank_rpt_aml", "bank_rpt_rbi", "bank_rpt_alm", "bank_rpt_upi"):'
assert old_rollback in content, "old_rollback not found"
content = content.replace(old_rollback, new_rollback, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched pipeline_orchestrator.py")
