import os
import sys
import shutil
import sqlite3

ws_db = r"c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio\app\database\studio_memory.db"
prod_db = r"C:\Mangesh\AI video\NanoPro_Made_By_Mangesh_Bagul_AI_v1\Mangesh_Nano_Pro_AI_Studio_v7_FINAL_PRODUCTION\Mangesh_Nano_Pro_AI_Studio\app\database\studio_memory.db"

print("1. Checkpointing WAL and converting workspace DB to standard DELETE journal mode...")
conn = sqlite3.connect(ws_db)
conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
conn.execute("PRAGMA journal_mode=DELETE;")
cur = conn.cursor()
cur.execute("PRAGMA integrity_check;")
res = cur.fetchone()[0]
print(f"Workspace DB integrity: {res}")
conn.close()

# Remove any lingering wal / shm files
for base_path in [ws_db, prod_db]:
    db_dir = os.path.dirname(base_path)
    for ext in ["-wal", "-shm"]:
        f = os.path.join(db_dir, "studio_memory.db" + ext)
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"Removed {f}")
            except Exception as e:
                print(f"Could not remove {f}: {e}")

print("\n2. Safely copying clean database to production...")
os.makedirs(os.path.dirname(prod_db), exist_ok=True)
shutil.copy2(ws_db, prod_db)
print(f"Copied {ws_db} -> {prod_db} ({os.path.getsize(prod_db):,} bytes)")

print("\n3. Testing production DB integrity...")
conn_prod = sqlite3.connect(prod_db)
cur_prod = conn_prod.cursor()
cur_prod.execute("PRAGMA integrity_check;")
res_prod = cur_prod.fetchone()[0]
print(f"Production DB integrity: {res_prod}")
cur_prod.execute("SELECT count(*) FROM credentials;")
print(f"Credentials count: {cur_prod.fetchone()[0]}")
cur_prod.execute("SELECT count(*) FROM tasks;")
print(f"Tasks count: {cur_prod.fetchone()[0]}")
conn_prod.close()

print("\nDATABASE REPAIR & SYNC COMPLETED SUCCESSFULLY!")
