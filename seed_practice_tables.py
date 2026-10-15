import sqlite3
import random
from datetime import datetime, timedelta

def seed_database():
    conn = sqlite3.connect('app/database/studio_memory.db')
    cur = conn.cursor()

    # 1. ACCOUNTS_MASTER
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ACCOUNTS_MASTER (
        acc_no TEXT PRIMARY KEY,
        cust_name TEXT NOT NULL,
        type TEXT NOT NULL,
        branch TEXT NOT NULL,
        status TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 0.0
    );
    """)

    # 2. TRANSACTIONS_LOG
    cur.execute("""
    CREATE TABLE IF NOT EXISTS TRANSACTIONS_LOG (
        txn_id TEXT PRIMARY KEY,
        acc_no TEXT,
        account_no TEXT,
        type TEXT,
        txn_type TEXT,
        amount REAL,
        amount_inr REAL,
        channel TEXT,
        txn_timestamp TEXT
    );
    """)

    # 3. STG_TRANSACTIONS_CDC
    cur.execute("""
    CREATE TABLE IF NOT EXISTS STG_TRANSACTIONS_CDC (
        txn_id TEXT NOT NULL,
        account_no TEXT NOT NULL,
        amount_inr REAL NOT NULL,
        ingestion_timestamp TEXT NOT NULL,
        payload TEXT
    );
    """)

    # 4. ACCOUNTS (400 rows)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ACCOUNTS (
        ACCOUNT_ID INTEGER PRIMARY KEY,
        CUSTOMER_ID INTEGER NOT NULL,
        ACCOUNT_NUMBER TEXT NOT NULL,
        ACCOUNT_TYPE TEXT NOT NULL,
        BALANCE REAL NOT NULL,
        CURRENCY TEXT NOT NULL,
        STATUS TEXT NOT NULL,
        OPENED_DATE TEXT NOT NULL
    );
    """)

    # 5. Populate ACCOUNTS_MASTER
    cur.execute("DELETE FROM ACCOUNTS_MASTER;")
    accounts_master_data = [
        ("ACC_1001", "Mangesh Bagul", "SAVINGS", "THN_01", "ACTIVE", 14250000.50),
        ("ACC_1002", "Aarav Patil", "CURRENT", "MUM_04", "ACTIVE", 2890000.00),
        ("ACC_1003", "Sneha Kulkarni", "SALARY", "PUN_02", "DORMANT", 75000.00),
        ("ACC_1004", "Rohan Deshmukh", "SAVINGS", "NSK_01", "ACTIVE", 345000.00),
        ("ACC_1005", "Pooja Shinde", "FIXED_DEP", "THN_01", "DORMANT", 1250000.00),
        ("ACC_1006", "Vikram Joshi", "CURRENT", "MUM_01", "ACTIVE", 19200000.00),
        ("ACC_1007", "Ananya Rao", "SAVINGS", "BLR_03", "ACTIVE", 850000.00),
        ("ACC_1008", "Karan Malhotra", "SALARY", "DEL_02", "ACTIVE", 420000.00),
        ("ACC_1009", "Priyanka Sen", "SAVINGS", "KOL_01", "ACTIVE", 610000.00),
        ("ACC_1010", "Aditya Verma", "CURRENT", "HYD_02", "ACTIVE", 5400000.00)
    ]
    cur.executemany("INSERT INTO ACCOUNTS_MASTER VALUES (?, ?, ?, ?, ?, ?);", accounts_master_data)

    # 6. Populate TRANSACTIONS_LOG
    cur.execute("DELETE FROM TRANSACTIONS_LOG;")
    txn_log_data = [
        ("TXN_901", "ACC_1001", "ACC_1001", "CR", "CR", 25000.0, 25000.0, "IMPS", "2026-10-12 09:15:00"),
        ("TXN_902", "ACC_1001", "ACC_1001", "DR", "DR", 8200.0, 8200.0, "UPI", "2026-10-12 10:45:00"),
        ("TXN_903", "ACC_1001", "ACC_1001", "DR", "DR", 65000.0, 65000.0, "NEFT", "2026-10-12 11:20:00"),
        ("TXN_904", "ACC_1001", "ACC_1001", "DR", "DR", 52000.0, 52000.0, "RTGS", "2026-10-12 11:25:00"),
        ("TXN_905", "ACC_1002", "ACC_1002", "CR", "CR", 150000.0, 150000.0, "NEFT", "2026-10-12 09:30:00"),
        ("TXN_906", "ACC_1002", "ACC_1002", "DR", "DR", 45000.0, 45000.0, "RTGS", "2026-10-12 14:10:00"),
        ("TXN_907", "ACC_1004", "ACC_1004", "DR", "DR", 3400.0, 3400.0, "ATM", "2026-10-12 12:05:00"),
        ("TXN_908", "ACC_1004", "ACC_1004", "CR", "CR", 12000.0, 12000.0, "UPI", "2026-10-12 15:40:00"),
        ("TXN_909", "ACC_1006", "ACC_1006", "CR", "CR", 500000.0, 500000.0, "RTGS", "2026-10-12 10:00:00"),
        ("TXN_910", "ACC_1006", "ACC_1006", "DR", "DR", 125000.0, 125000.0, "IMPS", "2026-10-12 16:20:00"),
        ("TXN_911", "ACC_1007", "ACC_1007", "CR", "CR", 35000.0, 35000.0, "UPI", "2026-10-12 11:00:00"),
        ("TXN_912", "ACC_1008", "ACC_1008", "CR", "CR", 85000.0, 85000.0, "SALARY_CREDIT", "2026-10-12 08:00:00"),
        ("TXN_913", "ACC_1009", "ACC_1009", "DR", "DR", 15000.0, 15000.0, "POS", "2026-10-12 13:15:00"),
        ("TXN_914", "ACC_1010", "ACC_1010", "CR", "CR", 250000.0, 250000.0, "NEFT", "2026-10-12 14:00:00"),
        ("TXN_999", "ACC_9999", "ACC_9999", "DR", "DR", 1200.0, 1200.0, "POS", "2026-10-12 17:00:00")
    ]
    cur.executemany("INSERT INTO TRANSACTIONS_LOG VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", txn_log_data)

    # 7. Populate STG_TRANSACTIONS_CDC
    cur.execute("DELETE FROM STG_TRANSACTIONS_CDC;")
    cdc_data = [
        ("TXN_901", "ACC_1001", 25000.0, "2026-10-12 09:15:01", '{"retry_count": 0, "status": "INITIATED"}'),
        ("TXN_901", "ACC_1001", 25000.0, "2026-10-12 09:15:05", '{"retry_count": 1, "status": "COMPLETED"}'),
        ("TXN_902", "ACC_1001", 8200.0, "2026-10-12 10:45:00", '{"retry_count": 0, "status": "COMPLETED"}'),
        ("TXN_903", "ACC_1001", 65000.0, "2026-10-12 11:20:00", '{"retry_count": 0, "status": "COMPLETED"}'),
        ("TXN_905", "ACC_1002", 150000.0, "2026-10-12 09:30:00", '{"retry_count": 0, "status": "PROCESSING"}'),
        ("TXN_905", "ACC_1002", 150000.0, "2026-10-12 09:30:03", '{"retry_count": 0, "status": "COMPLETED"}')
    ]
    cur.executemany("INSERT INTO STG_TRANSACTIONS_CDC VALUES (?, ?, ?, ?, ?);", cdc_data)

    # 8. Populate ACCOUNTS with exactly 400 rows
    cur.execute("DELETE FROM ACCOUNTS;")
    accounts_rows = []
    types = ["SAVINGS", "CURRENT", "SALARY", "FIXED_DEP", "NRI_NRE", "ESCROW"]
    statuses = ["ACTIVE", "ACTIVE", "ACTIVE", "DORMANT", "VERIFIED", "PENDING_KYC"]
    
    random.seed(42)
    start_date = datetime(2023, 1, 1)
    
    for i in range(1, 401):
        acc_id = 100 + i
        cust_id = 1000 + ((i - 1) % 150) + 1
        acc_num = f"ACC_{cust_id}_{types[i % len(types)][:4]}"
        acc_type = types[i % len(types)]
        bal = round(random.uniform(25000, 45000000), 2)
        status = statuses[i % len(statuses)]
        opened = (start_date + timedelta(days=i * 2)).strftime("%Y-%m-%d")
        accounts_rows.append((acc_id, cust_id, acc_num, acc_type, bal, "INR", status, opened))

    cur.executemany("INSERT INTO ACCOUNTS VALUES (?, ?, ?, ?, ?, ?, ?, ?);", accounts_rows)

    conn.commit()
    conn.close()
    print("Successfully seeded practice tables and 400 rows into ACCOUNTS!")

if __name__ == "__main__":
    seed_database()
