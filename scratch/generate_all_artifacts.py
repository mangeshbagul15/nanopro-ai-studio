import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import pandas as pd

def generate_artifacts():
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    backups_dir = Path("backups")
    backups_dir.mkdir(parents=True, exist_ok=True)

    # 1. daily_lakehouse_audit.xlsx
    f1 = data_dir / "daily_lakehouse_audit.xlsx"
    with pd.ExcelWriter(f1, engine='openpyxl') as writer:
        df_summary = pd.DataFrame([{
            "Total_Ingested_Records": 150000,
            "Cleaned_Count": 149950,
            "Error_Rate_Pct": 0.033,
            "Execution_Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        
        df_alerts = pd.DataFrame([
            {"TxID": "TXN_9011", "Customer_Name": "Tata Sons Private Ltd", "Amount": 15000000.0, "Risk_Flag": "HIGH_VALUE_SETTLEMENT"},
            {"TxID": "TXN_9012", "Customer_Name": "Reliance Industries Ltd", "Amount": 28000000.0, "Risk_Flag": "HIGH_VALUE_SETTLEMENT"},
            {"TxID": "TXN_9013", "Customer_Name": "Infosys Technologies", "Amount": 7500000.0, "Risk_Flag": "HIGH_VALUE_SETTLEMENT"},
            {"TxID": "TXN_9014", "Customer_Name": "Larsen & Toubro Ltd", "Amount": 12000000.0, "Risk_Flag": "HIGH_VALUE_SETTLEMENT"},
            {"TxID": "TXN_9015", "Customer_Name": "HDFC Life Insurance", "Amount": 9500000.0, "Risk_Flag": "HIGH_VALUE_SETTLEMENT"}
        ])
        df_alerts.to_excel(writer, sheet_name="High_Value_Alerts", index=False)
    print(f"Generated {f1}: {f1.stat().st_size} bytes")

    # 2. daily_master_lakehouse_audit.xlsx
    f2 = data_dir / "daily_master_lakehouse_audit.xlsx"
    with pd.ExcelWriter(f2, engine='openpyxl') as writer:
        df_master = pd.DataFrame([
            {"tx_id": "TX101", "customer_name": "Mangesh Bagul", "amount": 45000.50, "tx_date": "2026-10-14", "priority": "RETAIL", "dense_rank": 3},
            {"tx_id": "TX102", "customer_name": "Rahul Sharma", "amount": 12000.00, "tx_date": "2026-10-14", "priority": "RETAIL", "dense_rank": 4},
            {"tx_id": "TX103", "customer_name": "Sneha Patil", "amount": 85000.00, "tx_date": "2026-10-13", "priority": "HIGH_PRIORITY_HNI", "dense_rank": 2},
            {"tx_id": "TX105", "customer_name": "Amit Deshmukh", "amount": 150000.00, "tx_date": "2026-10-12", "priority": "HIGH_PRIORITY_HNI", "dense_rank": 1}
        ])
        df_master.to_excel(writer, sheet_name="MasterAudit", index=False)
    print(f"Generated {f2}: {f2.stat().st_size} bytes")

    # 3. tata_steel_rsi_signals.csv
    f3 = data_dir / "tata_steel_rsi_signals.csv"
    df_quant = pd.DataFrame([
        {"Date": "2026-10-10", "Ticker": "TATA_STEEL", "Close": 158.2, "SMA_5": 157.0, "RSI_14": 62.4, "Signal": "NEUTRAL"},
        {"Date": "2026-10-11", "Ticker": "TATA_STEEL", "Close": 160.5, "SMA_5": 158.3, "RSI_14": 66.8, "Signal": "NEUTRAL"},
        {"Date": "2026-10-12", "Ticker": "TATA_STEEL", "Close": 162.0, "SMA_5": 159.5, "RSI_14": 69.1, "Signal": "NEUTRAL"},
        {"Date": "2026-10-13", "Ticker": "TATA_STEEL", "Close": 164.5, "SMA_5": 160.8, "RSI_14": 72.3, "Signal": "OVERBOUGHT (SELL SIGNAL)"},
        {"Date": "2026-10-14", "Ticker": "TATA_STEEL", "Close": 165.0, "SMA_5": 161.4, "RSI_14": 74.8, "Signal": "OVERBOUGHT (SELL SIGNAL)"}
    ])
    df_quant.to_csv(f3, index=False)
    print(f"Generated {f3}: {f3.stat().st_size} bytes")

    # 4. reconciliation_discrepancy_report.csv
    f4 = data_dir / "reconciliation_discrepancy_report.csv"
    df_recon = pd.DataFrame([
        {"tx_id": "TX01", "internal_amt": 5000.0, "settled_amt": 5000.0, "diff": 0.0, "status": "MATCHED"},
        {"tx_id": "TX02", "internal_amt": 12500.0, "settled_amt": 12450.0, "diff": 50.0, "status": "AMOUNT_MISMATCH"},
        {"tx_id": "TX03", "internal_amt": 8000.0, "settled_amt": 8000.0, "diff": 0.0, "status": "MATCHED"},
        {"tx_id": "TX04", "internal_amt": 1200.0, "settled_amt": None, "diff": 1200.0, "status": "UNSETTLED_ORPHAN"},
        {"tx_id": "TX05", "internal_amt": 50000.0, "settled_amt": None, "diff": 50000.0, "status": "UNSETTLED_ORPHAN"},
        {"tx_id": "TX06", "internal_amt": None, "settled_amt": 3000.0, "diff": -3000.0, "status": "UNSETTLED_ORPHAN"}
    ])
    df_recon.to_csv(f4, index=False)
    print(f"Generated {f4}: {f4.stat().st_size} bytes")

    # 5. employees_data.parquet, employees_data.json, employees_data.xml
    emp_rows = [
        {"EmployeeID": 101, "Name": "Anand Verma", "Department": "Data Engineering", "Salary": 2400000, "City": "Mumbai"},
        {"EmployeeID": 102, "Name": "Priya Nair", "Department": "Risk Analytics", "Salary": 1850000, "City": "Pune"},
        {"EmployeeID": 103, "Name": "Siddharth Joshi", "Department": "CBS Operations", "Salary": 2100000, "City": "Thane"},
        {"EmployeeID": 104, "Name": "Meera Rao", "Department": "AML Compliance", "Salary": 1950000, "City": "Bengaluru"},
        {"EmployeeID": 105, "Name": "Karan Malhotra", "Department": "Cloud Security", "Salary": 2600000, "City": "New Delhi"}
    ]
    df_emp = pd.DataFrame(emp_rows)

    f5 = data_dir / "employees_data.parquet"
    df_emp.to_parquet(f5, compression="snappy", index=False)
    print(f"Generated {f5}: {f5.stat().st_size} bytes")

    f6 = data_dir / "employees_data.json"
    df_emp.to_json(f6, orient="records", indent=2)
    print(f"Generated {f6}: {f6.stat().st_size} bytes")

    f7 = data_dir / "employees_data.xml"
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<Employees>']
    for r in emp_rows:
        xml_lines.append(f'  <Employee id="{r["EmployeeID"]}">')
        for k, v in r.items():
            xml_lines.append(f'    <{k}>{v}</{k}>')
        xml_lines.append('  </Employee>')
    xml_lines.append('</Employees>')
    with open(f7, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(xml_lines))
    print(f"Generated {f7}: {f7.stat().st_size} bytes")

    # 8. backups/db_snapshot_today.db
    f8 = backups_dir / "db_snapshot_today.db"
    src_db = Path("data/nanopro_training_memory.db")
    if src_db.exists():
        shutil.copy2(src_db, f8)
    else:
        # Create valid sqlite db
        import sqlite3
        conn = sqlite3.connect(f8)
        cur = conn.cursor()
        cur.execute("CREATE TABLE snapshot_meta (backup_time TEXT, status TEXT)")
        cur.execute("INSERT INTO snapshot_meta VALUES (?, ?)", (datetime.now().isoformat(), "HEALTHY_RESTORE_READY"))
        conn.commit()
        conn.close()
    
    sha256 = hashlib.sha256()
    with open(f8, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256.update(byte_block)
    checksum = sha256.hexdigest()
    print(f"Generated {f8}: {f8.stat().st_size} bytes (SHA-256: {checksum})")

if __name__ == "__main__":
    generate_artifacts()
