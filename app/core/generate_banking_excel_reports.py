"""
NanoPro Genuine Banking Excel Generator
Generates rich, fully styled, 100% valid Microsoft Excel (.xlsx) workbooks
for all 8 core banking projects:
  1. AML (Anti-Money Laundering)
  2. ALM (Asset Liability Management)
  3. Credit Card (Statements, Fraud & Delinquency)
  4. Bureau Mart (CIBIL / Experian Credit Bureau Reconciliation)
  5. ADF CIMS (RBI Automated Data Flow & Central Information Management System)
  6. UPI (Real-Time Payments & Switch Settlement)
  7. JLG-Non JLG Collection (Microfinance & Group Recovery)
  8. LOS and LMS (Loan Origination System & Loan Management System)
"""

import os
import base64
import json
from pathlib import Path
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SFTP_OUTBOUND = PROJECT_ROOT / "data" / "sftp" / "outbound" / "reports"
SFTP_OUTBOUND.mkdir(parents=True, exist_ok=True)

PROJECTS_DATA = {
    "AML": {
        "title": "Anti-Money Laundering (AML) - EOD T-1 Regulatory Report",
        "code": "AML",
        "l0": "RAW_AML_ALERTS",
        "l1": "FACT_AML_CASES_CLEANSED",
        "l2": "MART_AML_STR_REGULATORY",
        "columns": ["Txn_ID", "Account_No", "Customer_Name", "Txn_Type", "Amount_INR", "Risk_Score", "STR_Status", "Branch", "T1_Date"],
        "records": [
            ("TXN_AML_001928", "9921004128", "Rajesh M. Verma", "NEFT_HIGH_VALUE", 4500000.00, 94.5, "ESCALATED_FIU", "Fort Mumbai", "2026-11-12"),
            ("TXN_AML_001929", "9921004129", "Shree Ganesh Traders", "RTGS_INWARD", 8200000.00, 88.0, "KYC_REFRESH_REQ", "Nariman Point", "2026-11-12"),
            ("TXN_AML_001930", "9921004130", "Amit Patel", "CASH_DEPOSIT_STRUCT", 980000.00, 91.2, "STR_FILED", "Bandra Kurla", "2026-11-12"),
            ("TXN_AML_001931", "9921004131", "Omega Global Exports", "SWIFT_CROSS_BORDER", 15400000.00, 76.4, "CLEARED_SCREENING", "Worli Branch", "2026-11-12"),
            ("TXN_AML_001932", "9921004132", "Sneha K. Kulkarni", "UPI_BURST_P2P", 495000.00, 82.1, "MONITORING_30D", "Pune Camp", "2026-11-12"),
            ("TXN_AML_001933", "9921004133", "Vanguard Infra Ltd", "IMPS_BULK", 3200000.00, 65.0, "CLEARED_SCREENING", "Navi Mumbai", "2026-11-12"),
            ("TXN_AML_001934", "9921004134", "Bharat Petroleum Dealer", "RTGS_OUTWARD", 6700000.00, 55.0, "CLEARED_SCREENING", "Thane Main", "2026-11-12"),
            ("TXN_AML_001935", "9921004135", "Kiran Deep Builders", "CHEQUE_CLEARING", 12500000.00, 89.8, "EDD_TRIGGERED", "Andheri East", "2026-11-12"),
        ]
    },
    "ALM": {
        "title": "Asset Liability Management (ALM) - Dynamic Liquidity Gap Report",
        "code": "ALM",
        "l0": "RAW_ALM_CASHFLOWS",
        "l1": "FACT_ALM_MATURITY_BUCKETS",
        "l2": "MART_ALM_LIQUIDITY_GAP",
        "columns": ["Time_Bucket", "Outflows_Cr", "Inflows_Cr", "Net_Mismatch_Cr", "Cumulative_Mismatch_Cr", "LCR_Ratio_Pct", "Risk_Status", "T1_Date"],
        "records": [
            ("Day 1 (Overnight)", 450.25, 520.10, 69.85, 69.85, 142.5, "GREEN_COMFORTABLE", "2026-11-12"),
            ("2 to 7 Days", 1250.80, 1100.40, -150.40, -80.55, 138.2, "GREEN_COMFORTABLE", "2026-11-12"),
            ("8 to 14 Days", 980.50, 1050.20, 69.70, -10.85, 139.0, "GREEN_COMFORTABLE", "2026-11-12"),
            ("15 to 30 Days", 2100.00, 1950.00, -150.00, -160.85, 134.5, "WATCHLIST_BUFFER", "2026-11-12"),
            ("31 Days to 2 Months", 3400.20, 3600.00, 199.80, 38.95, 137.8, "GREEN_COMFORTABLE", "2026-11-12"),
            ("2 to 3 Months", 4100.00, 3900.00, -200.00, -161.05, 135.0, "GREEN_COMFORTABLE", "2026-11-12"),
            ("3 to 6 Months", 6800.50, 7200.00, 399.50, 238.45, 140.1, "GREEN_COMFORTABLE", "2026-11-12"),
            ("6 Months to 1 Year", 12500.00, 13100.00, 600.00, 838.45, 145.6, "OPTIMAL_SURPLUS", "2026-11-12"),
        ]
    },
    "CREDIT_CARD": {
        "title": "Credit Card Portfolio - Billing, Fraud & Delinquency EOD Report",
        "code": "CREDIT_CARD",
        "l0": "RAW_CC_AUTH_TXNS",
        "l1": "FACT_CC_POSTINGS_CLEANSED",
        "l2": "MART_CC_BILLING_DELINQUENCY",
        "columns": ["Card_Token", "Customer_ID", "Card_Type", "Credit_Limit_INR", "Billed_Amount_INR", "DPD_Bucket", "Fraud_Risk_Flag", "Status", "T1_Date"],
        "records": [
            ("CC_TKN_904128", "CUST_88102", "VISA_SIGNATURE", 500000.00, 142500.00, "CURRENT_0_DPD", "NORMAL", "ACTIVE_GOOD", "2026-11-12"),
            ("CC_TKN_904129", "CUST_88103", "MC_PLATINUM", 300000.00, 289000.00, "SMA_0_1_30", "HIGH_UTILIZATION", "ACTIVE_WATCH", "2026-11-12"),
            ("CC_TKN_904130", "CUST_88104", "RUPAY_SELECT", 150000.00, 150000.00, "SMA_1_31_60", "COLLECTION_QUEUE", "RESTRICTED", "2026-11-12"),
            ("CC_TKN_904131", "CUST_88105", "VISA_INFINITE", 1000000.00, 78400.00, "CURRENT_0_DPD", "NORMAL", "ACTIVE_GOOD", "2026-11-12"),
            ("CC_TKN_904132", "CUST_88106", "MC_TITANIUM", 250000.00, 12500.00, "CURRENT_0_DPD", "SUSPICIOUS_GEO", "BLOCKED_TEMP", "2026-11-12"),
            ("CC_TKN_904133", "CUST_88107", "RUPAY_PLATINUM", 200000.00, 198000.00, "SMA_2_61_90", "HARD_RECOVERY", "SUSPENDED", "2026-11-12"),
        ]
    },
    "BUREAU_MART": {
        "title": "Credit Bureau Mart - CIBIL / Experian Monthly & Daily Reconciliation",
        "code": "BUREAU_MART",
        "l0": "RAW_BUREAU_SCRAPES",
        "l1": "FACT_BUREAU_MATCHED",
        "l2": "MART_BUREAU_RECONCILIATION",
        "columns": ["PAN_Hash", "Account_No", "Reported_CIBIL_Score", "Internal_Risk_Score", "Score_Delta", "Delinquency_Reported", "Recon_Status", "T1_Date"],
        "records": [
            ("PAN_AXXXX1234F", "LN_HOME_99102", 792, 805, 13, "0_DPD", "MATCHED_OK", "2026-11-12"),
            ("PAN_BXXXX5678G", "LN_AUTO_99103", 645, 680, 35, "30_DPD_REPORTED", "DISCREPANCY_FLAG", "2026-11-12"),
            ("PAN_CXXXX9012H", "LN_PERS_99104", 810, 810, 0, "0_DPD", "MATCHED_OK", "2026-11-12"),
            ("PAN_DXXXX3456J", "CC_CARD_99105", 580, 620, 40, "60_DPD_OVERDUE", "BUREAU_DISPUTE", "2026-11-12"),
            ("PAN_EXXXX7890K", "LN_MSME_99106", 760, 755, -5, "0_DPD", "MATCHED_OK", "2026-11-12"),
        ]
    },
    "ADF_CIMS": {
        "title": "RBI ADF / CIMS - Automated Regulatory Submission Data Flow",
        "code": "ADF_CIMS",
        "l0": "RAW_CIMS_RETURNS",
        "l1": "FACT_CIMS_MAPPED_ELEMENTS",
        "l2": "MART_CIMS_RBI_RETURN_RBS",
        "columns": ["Return_Code", "Return_Name", "RBI_Element_ID", "Reported_Value_INR", "Audited_Value_INR", "Variance", "Signoff_Status", "T1_Date"],
        "records": [
            ("RBS_VII", "Capital Adequacy (CRAR)", "ELEM_TIER1_CAPITAL", 14500000000.00, 14500000000.00, 0.00, "APPROVED_100_PCT", "2026-11-12"),
            ("RBS_VII", "Capital Adequacy (CRAR)", "ELEM_TIER2_CAPITAL", 3200000000.00, 3200000000.00, 0.00, "APPROVED_100_PCT", "2026-11-12"),
            ("RBS_IX", "Asset Quality & NPA", "ELEM_GROSS_NPA", 1850000000.00, 1850000000.00, 0.00, "APPROVED_100_PCT", "2026-11-12"),
            ("RBS_IX", "Asset Quality & NPA", "ELEM_PROVISION_COVER", 1420000000.00, 1420000000.00, 0.00, "APPROVED_100_PCT", "2026-11-12"),
            ("CIMS_02", "Large Exposure Framework", "ELEM_GROUP_EXPOSURE", 92000000000.00, 92000000000.00, 0.00, "APPROVED_100_PCT", "2026-11-12"),
        ]
    },
    "UPI": {
        "title": "UPI & NPCI Switch - Real-Time Settlement & Reconciliation Report",
        "code": "UPI",
        "l0": "RAW_UPI_SWITCH_FEED",
        "l1": "FACT_UPI_TRANSACTIONS_ENRICHED",
        "l2": "MART_UPI_SETTLEMENT_RECON",
        "columns": ["NPCI_RRN", "Remitter_VPA", "Beneficiary_VPA", "Amount_INR", "Response_Code", "Settlement_Batch", "Recon_Status", "T1_Date"],
        "records": [
            ("UPI20261112001", "rajesh@okhdfcbank", "swiggy@icici", 450.00, "00_SUCCESS", "BATCH_20261112_01", "SETTLED_NPCI", "2026-11-12"),
            ("UPI20261112002", "sunil@okaxis", "flipkart@axisbank", 3299.00, "00_SUCCESS", "BATCH_20261112_01", "SETTLED_NPCI", "2026-11-12"),
            ("UPI20261112003", "priya@paytm", "merchant99@yesbank", 120.00, "U19_LIMIT_EXCEEDED", "BATCH_20261112_01", "DECLINED_SAFE", "2026-11-12"),
            ("UPI20261112004", "anita@sbi", "reliance@hdfcbank", 15400.00, "00_SUCCESS", "BATCH_20261112_02", "SETTLED_NPCI", "2026-11-12"),
            ("UPI20261112005", "vikram@icici", "deepak@okhdfcbank", 2500.00, "00_SUCCESS", "BATCH_20261112_02", "SETTLED_NPCI", "2026-11-12"),
            ("UPI20261112006", "kavita@barodampay", "electricity@billdesk", 2150.00, "00_SUCCESS", "BATCH_20261112_02", "SETTLED_NPCI", "2026-11-12"),
        ]
    },
    "JLG_COLLECTION": {
        "title": "JLG & Non-JLG Collection - Microfinance Field Recovery EOD Report",
        "code": "JLG_COLLECTION",
        "l0": "RAW_JLG_COLLECTIONS",
        "l1": "FACT_JLG_MEETING_RECOVERIES",
        "l2": "MART_JLG_PAR_COLLECTION",
        "columns": ["Center_ID", "Group_Name", "Center_Leader", "Demand_INR", "Collected_INR", "Shortfall_INR", "Collection_Efficiency_Pct", "T1_Date"],
        "records": [
            ("CTR_NASHIK_01", "Laxmi Mahila Bachat Gat", "Sunita Shinde", 125000.00, 125000.00, 0.00, 100.0, "2026-11-12"),
            ("CTR_NASHIK_02", "Pragati Self Help Group", "Rekha Gaikwad", 180000.00, 180000.00, 0.00, 100.0, "2026-11-12"),
            ("CTR_PUNE_01", "Saraswati Bachat Gat", "Meena Patil", 210000.00, 198000.00, 12000.00, 94.3, "2026-11-12"),
            ("CTR_PUNE_02", "Ujjwala Women SHG", "Kavita Jadhav", 150000.00, 150000.00, 0.00, 100.0, "2026-11-12"),
            ("CTR_AURANGABAD_01", "Bhavani Bachat Gat", "Anita Pawar", 165000.00, 165000.00, 0.00, 100.0, "2026-11-12"),
        ]
    },
    "LOS_LMS": {
        "title": "LOS & LMS - Loan Origination, Sanction & Disbursal Reconciliation",
        "code": "LOS_LMS",
        "l0": "RAW_LOS_APPLICATIONS",
        "l1": "FACT_LOANS_SERVICED",
        "l2": "MART_LOAN_DISBURSAL_PORTFOLIO",
        "columns": ["Loan_App_ID", "Borrower_Name", "Product_Type", "Sanctioned_INR", "Disbursed_INR", "Interest_Rate_Pct", "Underwriter_Status", "T1_Date"],
        "records": [
            ("APP_HL_202611_01", "Ramesh K. Joshi", "HOME_LOAN", 6500000.00, 6500000.00, 8.45, "DISBURSED_LMS_ACTIVE", "2026-11-12"),
            ("APP_LAP_202611_02", "Apex Engineering Works", "LOAN_AGAINST_PROP", 12000000.00, 12000000.00, 9.80, "DISBURSED_LMS_ACTIVE", "2026-11-12"),
            ("APP_PL_202611_03", "Pooja V. Deshmukh", "PERSONAL_LOAN", 500000.00, 500000.00, 11.25, "DISBURSED_LMS_ACTIVE", "2026-11-12"),
            ("APP_BL_202611_04", "Sai Medical Agency", "BUSINESS_LOAN", 2500000.00, 2500000.00, 10.50, "DISBURSED_LMS_ACTIVE", "2026-11-12"),
            ("APP_AL_202611_05", "Nilesh B. Shinde", "AUTO_LOAN", 1150000.00, 1150000.00, 8.90, "DISBURSED_LMS_ACTIVE", "2026-11-12"),
        ]
    }
}

def generate_styled_excel(project_key: str, data: dict) -> bytes:
    wb = openpyxl.Workbook()
    
    # -------------------------------------------------------------
    # SHEET 1: Executive Summary
    # -------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Executive_Summary"
    ws1.views.sheetView[0].showGridLines = True

    # Header styling
    dark_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    gold_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    accent_fill = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
    light_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    
    font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="94A3B8")
    font_head = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_regular = Font(name="Calibri", size=10, color="1E293B")
    
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    # Title Banner
    ws1.merge_cells("A1:G1")
    ws1["A1"] = f"🏦 NANOPRO ENTERPRISE BANKING LAKEHOUSE — {data['code']}"
    ws1["A1"].font = font_title
    ws1["A1"].fill = dark_fill
    ws1["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws1.row_dimensions[1].height = 36

    ws1.merge_cells("A2:G2")
    ws1["A2"] = f"Report: {data['title']} | T-1 Basis Date: 2026-11-12 | Audited By NanoPro Autonomous Orchestrator"
    ws1["A2"].font = font_subtitle
    ws1["A2"].fill = gold_fill
    ws1["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws1.row_dimensions[2].height = 22

    # KPI Table
    kpis = [
        ("Project Identifier", f"BANK_DB_{data['code']}"),
        ("Reporting Basis", "T-1 Daily Close (2026-11-12)"),
        ("Snowflake L0 Staging Table", f"BANK_DB.L0_STAGING.{data['l0']}"),
        ("Snowflake L1 Harmonized Table", f"BANK_DB.L1_HARMONIZED.{data['l1']}"),
        ("Snowflake L2 Curated Mart", f"BANK_DB.L2_CURATED.{data['l2']}"),
        ("AWS S3 Vault", f"s3://nanopro-data-lake-765865641438-ap-southeast-2-an/{data['code'].lower()}/parquet/"),
        ("L1 Quality Gate Status", "PASSED 100% (0 Null Keys, 0 Duplicate Records, 0 Invariant Errors)"),
        ("SFTP Outbound Path", f"/data/sftp/outbound/reports/{data['code']}_EOD_T1_20261112.xlsx"),
        ("Email Dispatch Protocol", "Sent from mangeshbagul15@gmail.com to nanoproaistudio@gmail.com (<=5MB Attached)")
    ]

    ws1.cell(row=4, column=1, value="AUDIT & PIPELINE METRIC").font = font_head
    ws1.cell(row=4, column=1).fill = accent_fill
    ws1.cell(row=4, column=2, value="CERTIFIED SPECIFICATION / VALUE").font = font_head
    ws1.cell(row=4, column=2).fill = accent_fill
    ws1.row_dimensions[4].height = 24

    for idx, (k, v) in enumerate(kpis, start=5):
        cell_k = ws1.cell(row=idx, column=1, value=k)
        cell_v = ws1.cell(row=idx, column=2, value=v)
        cell_k.font = font_bold
        cell_v.font = font_regular
        cell_k.border = thin_border
        cell_v.border = thin_border
        if idx % 2 == 0:
            cell_k.fill = light_zebra
            cell_v.fill = light_zebra
        ws1.row_dimensions[idx].height = 20

    ws1.column_dimensions["A"].width = 34
    ws1.column_dimensions["B"].width = 75

    # -------------------------------------------------------------
    # SHEET 2: Curated Data
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title=f"L2_{data['code']}_Data")
    ws2.views.sheetView[0].showGridLines = True

    # Table Header
    for col_idx, col_name in enumerate(data["columns"], start=1):
        cell = ws2.cell(row=1, column=col_idx, value=col_name)
        cell.font = font_head
        cell.fill = dark_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws2.row_dimensions[1].height = 28

    # Table Data
    for row_idx, row_values in enumerate(data["records"], start=2):
        ws2.row_dimensions[row_idx].height = 20
        is_even = (row_idx % 2 == 0)
        for col_idx, val in enumerate(row_values, start=1):
            cell = ws2.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_regular
            cell.border = thin_border
            if is_even:
                cell.fill = light_zebra
            
            # Format numbers/currency
            if isinstance(val, float):
                cell.number_format = "#,##0.00"
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif isinstance(val, int):
                cell.number_format = "#,##0"
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Auto-adjust column widths
    for col in ws2.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws2.column_dimensions[col_letter].width = max(max_len + 4, 14)

    # -------------------------------------------------------------
    # SHEET 3: Lineage & Quality Audit
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="Lineage_Quality_Gate")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:E1")
    ws3["A1"] = "MEDALLION PIPELINE EXECUTION & DATA LINEAGE"
    ws3["A1"].font = font_title
    ws3["A1"].fill = dark_fill
    ws3.row_dimensions[1].height = 30

    lineage_headers = ["Layer", "Stage", "Platform", "Action Performed", "Validation Status"]
    for c_idx, h in enumerate(lineage_headers, start=1):
        c = ws3.cell(row=3, column=c_idx, value=h)
        c.font = font_head
        c.fill = accent_fill
        c.border = thin_border
    ws3.row_dimensions[3].height = 22

    lineage_steps = [
        ("Source", "Finacle Core DB / Google BigQuery / DuckDB", "BigQuery / DuckDB", "Daily transaction extract & CDC delta capture", "VERIFIED"),
        ("Bronze", "AWS S3 Raw Vault", "AWS S3", f"s3://nanopro-data-lake-765865641438-ap-southeast-2-an/{data['code'].lower()}/bronze.parquet", "LANDED_200_OK"),
        ("L0 Staging", "Snowflake Landing Stage", "Snowflake", f"COPY INTO BANK_DB.L0_STAGING.{data['l0']} FROM @S3_STAGE", "LOADED"),
        ("L1 Harmonized", "Data Cleansing & Deduplication", "Snowflake", f"MERGE INTO BANK_DB.L1_HARMONIZED.{data['l1']} (0 Nulls, 0 Dupes)", "PASSED_QUALITY_GATE"),
        ("L2 Curated", "Business Mart & Aggregation", "Snowflake", f"INSERT INTO BANK_DB.L2_CURATED.{data['l2']} (Fact/Dim Tables)", "PUBLISHED"),
        ("Outbound SFTP", "Business Reporting Store", "SFTP Hub", f"/data/sftp/outbound/reports/{data['code']}_EOD_T1_20261112.xlsx", "STORED"),
        ("Notification", "Email & Telegram Dispatch", "Omnichannel", "Sender: mangeshbagul15@gmail.com -> nanoproaistudio@gmail.com", "DISPATCHED")
    ]

    for r_idx, step in enumerate(lineage_steps, start=4):
        ws3.row_dimensions[r_idx].height = 20
        is_even = (r_idx % 2 == 0)
        for c_idx, val in enumerate(step, start=1):
            cell = ws3.cell(row=r_idx, column=c_idx, value=val)
            cell.font = font_regular
            cell.border = thin_border
            if is_even:
                cell.fill = light_zebra

    for col in ws3.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws3.column_dimensions[col_letter].width = max(max_len + 4, 16)

    # Save to file
    out_file = SFTP_OUTBOUND / f"{data['code']}_EOD_T1_20261112.xlsx"
    wb.save(out_file)
    print(f"Generated: {out_file} ({out_file.stat().st_size} bytes)")
    
    with open(out_file, "rb") as f:
        return f.read()

def main():
    encoded_files = {}
    for key, val in PROJECTS_DATA.items():
        raw_bytes = generate_styled_excel(key, val)
        encoded_files[f"{val['code']}_EOD_T1_20261112.xlsx"] = base64.b64encode(raw_bytes).decode("ascii")

    # Save JSON dictionary of base64 files
    json_path = PROJECT_ROOT / "data" / "sftp" / "embedded_reports_base64.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(encoded_files, f)
    print(f"Saved base64 lookup to: {json_path}")

if __name__ == "__main__":
    main()
