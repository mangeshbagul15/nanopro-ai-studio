import os
import sys
import sqlite3
import time

db_path = r"app/database/studio_memory.db"
print(f"Initial size: {os.path.getsize(db_path)/(1024*1024):.2f} MB")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check row counts
cur.execute("SELECT COUNT(*) FROM data_engineer_records")
count = cur.fetchone()[0]
print(f"data_engineer_records count before: {count:,}")

# Keep top 10,000 clean records
cur.execute("""
CREATE TABLE IF NOT EXISTS data_engineer_records_clean AS
SELECT * FROM data_engineer_records LIMIT 10000;
""")
cur.execute("DROP TABLE data_engineer_records;")
cur.execute("ALTER TABLE data_engineer_records_clean RENAME TO data_engineer_records;")
conn.commit()

cur.execute("SELECT COUNT(*) FROM data_engineer_records")
print(f"data_engineer_records count after: {cur.fetchone()[0]:,}")

# Also clean any old temp tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables count:", len(tables))

conn.close()

# VACUUM to reclaim free space
print("Running VACUUM...")
t0 = time.time()
conn2 = sqlite3.connect(db_path)
conn2.execute("VACUUM;")
conn2.close()
print(f"VACUUM completed in {time.time()-t0:.2f}s")

final_size = os.path.getsize(db_path)/(1024*1024)
print(f"Final size: {final_size:.2f} MB")
