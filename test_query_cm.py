from app.core.connection_manager import connection_manager

r1 = connection_manager.execute_query("STUDIO_MEMORY_DB", "SELECT * FROM TRANSACTIONS_LOG LIMIT 5;")
print("TRANSACTIONS_LOG query success:", r1.get("success"), "row_count:", r1.get("row_count"))
if r1.get("rows"):
    print("Sample row:", r1["rows"][0])

r2 = connection_manager.execute_query("STUDIO_MEMORY_DB", "SELECT * FROM BANK_DB.L0_STAGING.ACCOUNTS LIMIT 10;")
print("BANK_DB.L0_STAGING.ACCOUNTS query success:", r2.get("success"), "row_count:", r2.get("row_count"))

r3 = connection_manager.execute_query("STUDIO_MEMORY_DB", "SELECT COUNT(*) AS total_accounts FROM ACCOUNTS;")
print("ACCOUNTS total count:", r3.get("rows"))
