import sqlite3

conn = sqlite3.connect('app/database/studio_memory.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print(f"Total tables: {len(tables)}")
print("Tables with 'acc':", [t for t in tables if 'acc' in t.lower()])
for t in ['accounts', 'ACCOUNTS', 'bank_accounts']:
    if t in tables:
        cur.execute(f'SELECT count(*) FROM "{t}"')
        print(f"Count in {t}:", cur.fetchone()[0])
conn.close()
