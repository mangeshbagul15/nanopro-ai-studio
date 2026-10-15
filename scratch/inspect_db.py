import sys
import sqlite3
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from app.core.config import SQLITE_DB_PATH

print(f"DB Path: {SQLITE_DB_PATH}")
print(f"File Size: {SQLITE_DB_PATH.stat().st_size / (1024*1024):.2f} MB")

conn = sqlite3.connect(SQLITE_DB_PATH)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]

counts = {}
for t in tables:
    try:
        c.execute(f"SELECT count(*) FROM [{t}]")
        counts[t] = c.fetchone()[0]
    except Exception as e:
        counts[t] = str(e)

for t, cnt in sorted(counts.items(), key=lambda x: (isinstance(x[1], int), x[1]), reverse=True):
    print(f"  {t}: {cnt}")
