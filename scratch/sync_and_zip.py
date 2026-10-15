import os
import sys
import shutil
import zipfile
import time

sys.stdout.reconfigure(encoding='utf-8')

ws_dir = r"c:\Mangesh\AI video\Mangesh_Nano_Pro_AI_Studio_COMPLETE (34)\Mangesh_Nano_Pro_AI_Studio"
prod_base = r"C:\Mangesh\AI video\NanoPro_Made_By_Mangesh_Bagul_AI_v1\Mangesh_Nano_Pro_AI_Studio_v7_FINAL_PRODUCTION"
prod_studio = os.path.join(prod_base, "Mangesh_Nano_Pro_AI_Studio")
out_zip = r"C:\Mangesh\AI video\NanoPro_Made_By_Mangesh_Bagul_AI_v1\Mangesh_Nano_Pro_AI_Studio_v7_FINAL_PRODUCTION.zip"

files_to_sync = [
    "main.py",
    "app/core/model_adapter.py",
    "app/core/conversational_intelligence.py",
    "app/core/dynamic_stem_engine.py",
    "app/core/dynamic_db_engine.py",
    "app/core/enterprise_knowledge_engine.py",
    "app/core/enterprise_metadata_catalog.py",
    "app/agents/__init__.py",
    "app/agents/extended_intents.py",
    "app/agents/manager_agent.py",
    "app/agents/benchmark_and_drills.py",
    "app/agents/scientific_solvers.py",
    "app/agents/interview_challenges.py",
    "app/agents/lakehouse_drills.py",
    "app/video_maker/sql/sql_core.py",
    "app/video_maker/python/python_core.py",
    "scratch/test_dynamic_intelligence.py",
    "scratch/test_all_new_drills.py",
    "scratch/test_conversational_speed.py",
    "scratch/test_human_predictions.py",
    "scratch/verify_all_fixes.py",
    "app/reports/Cross_DB_Reconciliation_ORACLE_SNOWFLAKE_ACCOUNTS.xlsx",
    "data/sales_q4_summary.xlsx",
    "data/daily_lakehouse_audit.xlsx",
    "data/daily_master_lakehouse_audit.xlsx",
    "data/tata_steel_rsi_signals.csv",
    "data/reconciliation_discrepancy_report.csv",
    "data/employees_data.parquet",
    "data/employees_data.json",
    "data/employees_data.xml",
    "backups/db_snapshot_today.db",
    ".env",
    "app/database/studio_memory.db"
]

print("=== STEP 1: SYNCING WORKSPACE FILES TO PRODUCTION DIRECTORY ===")
for rel_path in files_to_sync:
    src_f = os.path.join(ws_dir, rel_path.replace("/", os.sep))
    dst_f = os.path.join(prod_studio, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst_f), exist_ok=True)
    if os.path.exists(src_f):
        shutil.copy2(src_f, dst_f)
        print(f"✅ Synced: {rel_path} ({os.path.getsize(dst_f):,} bytes)")
    else:
        print(f"❌ Source missing: {src_f}")

print("\n=== STEP 2: CREATING PRODUCTION ZIP ===")
t0 = time.time()
exclude_dirs = {"__pycache__", ".git", ".venv", "venv", ".idea", ".vscode", "tmp"}
exclude_extensions = {".pyc", ".pyo"}

count = 0
with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(prod_base):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in exclude_extensions:
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, prod_base)
            z.write(full_path, rel_path)
            count += 1
            if count % 100 == 0:
                print(f"  Archived {count} files...")

elapsed = time.time() - t0
size_mb = os.path.getsize(out_zip) / (1024 * 1024)
print(f"\n🎉 ZIP COMPLETE: {out_zip}")
print(f"Total Files Archived: {count:,}")
print(f"Archive Size: {size_mb:.2f} MB")
print(f"Time Taken: {elapsed:.2f} seconds")
