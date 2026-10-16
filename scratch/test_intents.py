import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.agents.extended_intents import handle_extended_intents

tests = [
    {
        "name": "Cross-DB ETL Data Movement & Append with Email",
        "prompt": "Host: 127.0.0.1:1521 ha db ahe oracle cha CUSTOMERS ha table name ahe ha snowflake cha ahe Database: BANK_DB | Schema: L0 STAGING ahe tithe pn CUSTOMERS table ahe tithe data insert append kara and confirm kara . and report generate kara and mail pn jayla pahije",
        "expected_in_reply": ["Cross-Database ETL Pipeline Executed", "CUSTOMERS", "MY_ORACLE_XE_LOCAL", "BANK_DB.L0_STAGING", "500 records", "Snowflake_L0_CUSTOMERS_Data_Append_Report.xlsx", "nanoproaistudio@gmail.com"],
        "forbidden_in_reply": ["As requested, here is the verified SQL query to fetch the first 5 records", "SELECT * FROM CUSTOMERS FETCH FIRST 5 ROWS ONLY"]
    },
    {
        "name": "Fetch from Oracle and push into L0 with report",
        "prompt": "fetch data from oracle db and push into l0 layer and after snowflake sent daily report",
        "expected_in_reply": ["Cross-Database ETL Pipeline Executed", "BANK_DB.L0_STAGING", "CUSTOMERS"],
        "forbidden_in_reply": ["I searched GitHub"]
    },
    {
        "name": "L0 Table Inventory (Marathi)",
        "prompt": "BANK_DB ya db madhe L0 layer madhe konte tables ahet?",
        "expected_in_reply": ["BANK_DB", "L0_STAGING", "ACCOUNTS", "CUSTOMERS", "TRANSACTIONS", "BRANCHES", "LOANS", "DEPARTMENTS", "EMPLOYEES", "INGESTION_METADATA_LOG"],
        "forbidden_in_reply": ["MY_ORACLE_XE", "studio_memory.db", "AWSS3"]
    },
    {
        "name": "which tables in there?",
        "prompt": "which tables in there?",
        "expected_in_reply": ["BANK_DB", "L0_STAGING", "ACCOUNTS", "CUSTOMERS", "TRANSACTIONS"],
        "forbidden_in_reply": []
    },
    {
        "name": "BANKDB.L0STAGING ya madhe konte tables ahet?",
        "prompt": "BANKDB.L0STAGING ya madhe konte tables ahet?",
        "expected_in_reply": ["BANK_DB", "L0_STAGING", "ACCOUNTS", "CUSTOMERS"],
        "forbidden_in_reply": []
    },
    {
        "name": "Actual DB clarification",
        "prompt": "actual database is BANK_DB",
        "expected_in_reply": ["BANK_DB", "L0_STAGING", "COMPUTE_WH"],
        "forbidden_in_reply": ["snowflake.acme.com", "MySecretPassword123"]
    },
    {
        "name": "Oracle DB inventory",
        "prompt": "oracle madhe konte db ahet",
        "expected_in_reply": ["MY_ORACLE_XE_LOCAL", "MY_ORACLE_XE_REMOTE", "MY_ORACLE_XE_REMOTE_New", "ORCL_LAN_240"],
        "forbidden_in_reply": ["NANOPROSNOWFLAKE", "STUDIOMEMORYDB"]
    },
    {
        "name": "Main Oracle DB",
        "prompt": "main oracle db konta ahe?",
        "expected_in_reply": ["MY_ORACLE_XE_LOCAL", "127.0.0.1:1521", "XEPDB1"],
        "forbidden_in_reply": []
    },
    {
        "name": "Snowflake to Oracle connection check",
        "prompt": "check snowflake to oracle db connection?",
        "expected_in_reply": ["Snowflake ⟷ Oracle Cross-Database Connectivity Verified", "BANK_DB.L0_STAGING"],
        "forbidden_in_reply": []
    },
    {
        "name": "SQL query for Snowflake ACCOUNTS first 5 records",
        "prompt": "ek table ahe ACCOUNTS to BANK_DB chya L0 layer madhe ahe so tya table che first 5 record fetch karun pahujet so procide SQL query for snowflake",
        "expected_in_reply": ["SELECT * FROM BANK_DB.L0_STAGING.ACCOUNTS LIMIT 5;", "BANK_DB", "L0_STAGING", "ACCOUNTS"],
        "forbidden_in_reply": ["BANKDB.L0STAGING"]
    },
    {
        "name": "same for CUSTOMERS",
        "prompt": "same for CUSTOMERS",
        "expected_in_reply": ["SELECT * FROM BANK_DB.L0_STAGING.CUSTOMERS LIMIT 5;", "CUSTOMERS"],
        "forbidden_in_reply": ["ACCOUNTS LIMIT 5"]
    },
    {
        "name": "SAME fot TRANSACTION",
        "prompt": "SAME fot TRANSACTION",
        "expected_in_reply": ["SELECT * FROM BANK_DB.L0_STAGING.TRANSACTIONS LIMIT 5;", "TRANSACTIONS"],
        "forbidden_in_reply": ["CUSTOMERS LIMIT 5"]
    }
]

failed = 0
for t in tests:
    p = t["prompt"]
    res = handle_extended_intents(p.lower(), p, session_id="test_session")
    if not res or not res.get("handled"):
        print(f"❌ FAIL: {t['name']} - NOT HANDLED by extended_intents")
        failed += 1
        continue
    
    reply = res.get("reply", "")
    ok = True
    for exp in t["expected_in_reply"]:
        if exp not in reply:
            print(f"❌ FAIL: {t['name']} - Missing expected: '{exp}'")
            ok = False
    
    for forb in t["forbidden_in_reply"]:
        if forb in reply:
            print(f"❌ FAIL: {t['name']} - Found forbidden: '{forb}'")
            ok = False
            
    if ok:
        print(f"✅ PASS: {t['name']}")
    else:
        failed += 1
        print(f"--- Reply was:\n{reply[:300]}...\n")

if failed > 0:
    print(f"\n❌ {failed} tests failed!")
    sys.exit(1)
else:
    print(f"\n🎉 ALL {len(tests)} TESTS PASSED PERFECTLY!")
