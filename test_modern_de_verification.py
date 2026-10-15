import sys
from fastapi.testclient import TestClient

try:
    from main import app
    client = TestClient(app)
except Exception as e:
    print(f"Error importing main app: {e}")
    sys.exit(1)

def test_endpoints():
    print("=== STARTING FULL END-TO-END VERIFICATION TEST SUITE ===")
    
    # 1. CatLog Schemas & Tables for Multiple Databases
    dbs_to_test = ["BANK_DB", "MY_ORACLE_XE_LOCAL", "MY_POSTGRES_LOCAL", "studio_memory.db", "AWS_S3_DATA_LAKE"]
    for db in dbs_to_test:
        r = client.get(f"/api/de_modern/catlog/schemas?db_name={db}")
        assert r.status_code == 200, f"Schemas failed for {db}: {r.status_code}"
        schemas = r.json()
        print(f"✔ Schemas for {db}: {schemas}")
        
        # Test Tables for first schema
        if schemas:
            schema = schemas[0]
            r_tbl = client.get(f"/api/de_modern/catlog/tables?db_name={db}&schema_name={schema}")
            assert r_tbl.status_code == 200, f"Tables failed for {db}.{schema}: {r_tbl.status_code}"
            tables = r_tbl.json()
            print(f"  ✔ Tables in {db}.{schema}: {[t['name'] for t in tables]}")
            
    # 2. Table Profiling
    r_prof = client.get("/api/de_modern/catlog/profile?db_name=BANK_DB&schema_name=L0_STAGING&table_name=ACCOUNTS&limit=10")
    assert r_prof.status_code == 200, f"Profiling failed: {r_prof.status_code}"
    prof_data = r_prof.json()
    assert prof_data["status"] == "success"
    print(f"✔ Profiling ACCOUNTS: {prof_data['profiling']['total_rows']} rows, {prof_data['profiling']['total_columns']} cols")

    # 3. Multi-Format Exporter with db_name & schema_name (CSV, XLSX, TXT, JSON, SQL, XML)
    formats = ["csv", "xlsx", "txt", "json", "sql", "xml"]
    for fmt in formats:
        payload = {
            "db_name": "BANK_DB",
            "schema_name": "L0_STAGING",
            "table_name": "ACCOUNTS",
            "format_type": fmt,
            "delimiter": "pipe"
        }
        r_exp = client.post("/api/de_modern/lab/export_dataset", json=payload)
        assert r_exp.status_code == 200, f"Export {fmt} failed: {r_exp.status_code}"
        res = r_exp.json()
        assert res["status"] == "success", f"Export {fmt} failed with response: {res}"
        print(f"✔ Multi-format Export [{fmt.upper()}]: {res['filename']} ({res['file_size_kb']} KB, {res['total_records_exported']} rows)")

    # 4. Project Portfolio List
    r_projs = client.get("/api/de_modern/projects/list")
    assert r_projs.status_code == 200
    projs = r_projs.json()
    print(f"✔ Project Portfolio: {len(projs)} active banking projects: {[p['id'] for p in projs]}")

    # 5. IT SecOps Diagnostics
    r_diag = client.get("/api/de_modern/secops/diagnostics")
    assert r_diag.status_code == 200
    diag = r_diag.json()
    print(f"✔ IT SecOps Diagnostics: {len(diag.get('diagnostics', []))} monitored sockets")

    # 6. Task Schedule Matrix
    r_tasks = client.get("/api/de_modern/tasks/matrix")
    assert r_tasks.status_code == 200
    tasks = r_tasks.json()
    print(f"✔ Task Schedule Matrix: {len(tasks.get('tasks', []))} active jobs")

    # 7. Lakehouse Maintain Overview
    r_maint = client.get("/api/de_modern/maintain/overview")
    assert r_maint.status_code == 200
    maint = r_maint.json()
    print(f"✔ Lakehouse Maintain Overview: {list(maint.get('tiers', {}).keys())}")

    # 8. Data Analyst Query execution (Multi-engine lab)
    r_code = client.post("/api/de_modern/lab/execute_code", json={
        "language": "snowsql",
        "code": "SELECT * FROM BANK_DB.L0_STAGING.ACCOUNTS LIMIT 5;",
        "target_db": "BANK_DB",
        "target_schema": "L0_STAGING",
        "limit": 5
    })
    assert r_code.status_code == 200
    code_res = r_code.json()
    print(f"✔ Lab Code Execution: {code_res['status']} with {len(code_res.get('rows', []))} rows")

    print("\n=======================================================")
    print(">>> ALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100%) <<<")
    print("=======================================================\n")

if __name__ == "__main__":
    test_endpoints()
