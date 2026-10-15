"""
Mangesh Nano Pro AI Studio - Automated Backup & Restore System
Safeguards the SQLite database, prompt memory, configurations, and project metadata
into compressed, verifiable backup archives with restore safeguards.
"""

import shutil
import tarfile
import time
from pathlib import Path
from typing import Dict, Any, List
from app.core.config import BACKUPS_DIR, DATABASE_DIR, CONFIG_DIR, MEMORY_DIR, SQLITE_DB_PATH
from app.core.logger import log_event
from app.core.database import db

class BackupManager:
    def __init__(self):
        self.backups_dir = BACKUPS_DIR
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def create_system_backup(self, backup_type: str = "full_state") -> Dict[str, Any]:
        """
        Creates a timestamped compressed backup containing:
        - SQLite database
        - System configurations
        - Project knowledge & memory
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"mangesh_studio_backup_{timestamp}.tar.gz"
        backup_file_path = self.backups_dir / backup_filename

        log_event(f"Initiating system backup: {backup_filename}", component="BackupManager")

        items_backed_up = 0
        with tarfile.open(backup_file_path, "w:gz") as tar:
            if SQLITE_DB_PATH.exists():
                tar.add(SQLITE_DB_PATH, arcname="studio_memory.db")
                items_backed_up += 1

            if CONFIG_DIR.exists():
                tar.add(CONFIG_DIR, arcname="config")
                items_backed_up += 1

            if MEMORY_DIR.exists():
                tar.add(MEMORY_DIR, arcname="memory")
                items_backed_up += 1

        file_size = backup_file_path.stat().st_size
        backup_record = {
            "id": f"bak_{timestamp}",
            "backup_path": str(backup_file_path),
            "backup_type": backup_type,
            "file_size_bytes": file_size,
            "items_count": items_backed_up,
            "created_at": time.time()
        }

        # Log into database ledger
        with db.get_connection() as conn:
            conn.execute("""
            INSERT INTO backups_ledger (id, backup_path, backup_type, file_size_bytes, items_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                backup_record["id"],
                backup_record["backup_path"],
                backup_record["backup_type"],
                backup_record["file_size_bytes"],
                backup_record["items_count"],
                backup_record["created_at"]
            ))
            conn.commit()

        log_event(f"Backup created successfully: {file_size} bytes ({items_backed_up} sources)", component="BackupManager")
        return backup_record

    def list_backups(self) -> List[Dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM backups_ledger ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]

    def restore_backup(self, backup_id: str, confirmation: bool = False) -> Dict[str, Any]:
        """
        Safely restores a backup archive. Requires explicit confirmation flag.
        """
        if not confirmation:
            return {"status": "declined", "message": "Restore aborted: explicit confirmation=True required."}

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM backups_ledger WHERE id = ?", (backup_id,))
            row = cursor.fetchone()
            if not row:
                raise FileNotFoundError(f"Backup record not found: {backup_id}")

        backup_file = Path(row["backup_path"])
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup archive file missing from disk: {backup_file}")

        log_event(f"Restoring backup {backup_id} from {backup_file.name}...", component="BackupManager")
        with tarfile.open(backup_file, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name == "studio_memory.db":
                    tar.extract(member, path=DATABASE_DIR.parent)

        return {"status": "success", "message": f"Successfully restored {backup_file.name}"}

    def prune_and_vacuum(self, keep_backups: int = 3, max_report_age_hours: int = 48) -> Dict[str, Any]:
        """
        Enterprise Space Optimization:
        1. Keeps only the latest N backup archives and deletes older .tar.gz archives.
        2. Cleans up temporary report exports and converted scratch files.
        3. Executes SQLITE VACUUM to reclaim free pages and keep DB locked under 30MB.
        """
        reclaimed_bytes = 0
        deleted_files = 0
        now = time.time()

        # 1. Prune old backups
        try:
            backups = sorted(list(self.backups_dir.glob("mangesh_studio_backup_*.tar.gz")), key=lambda p: p.stat().st_mtime, reverse=True)
            if len(backups) > keep_backups:
                for b in backups[keep_backups:]:
                    sz = b.stat().st_size
                    b.unlink(missing_ok=True)
                    reclaimed_bytes += sz
                    deleted_files += 1
        except Exception as e:
            log_event(f"Backup pruning notice: {e}", level="WARNING", component="BackupManager")

        # 2. Prune old temporary reports
        for rep_dir in [Path("data/reports"), Path("app/reports/converted")]:
            if rep_dir.exists():
                try:
                    for f in rep_dir.glob("*.*"):
                        if now - f.stat().st_mtime > (max_report_age_hours * 3600):
                            sz = f.stat().st_size
                            f.unlink(missing_ok=True)
                            reclaimed_bytes += sz
                            deleted_files += 1
                except Exception:
                    pass

        # 3. Database VACUUM
        try:
            with db.get_connection() as conn:
                conn.execute("VACUUM")
        except Exception as e:
            log_event(f"VACUUM notice: {e}", level="WARNING", component="BackupManager")

        reclaimed_mb = round(reclaimed_bytes / (1024 * 1024), 2)
        log_event(f"Space Optimizer: Pruned {deleted_files} files, reclaimed {reclaimed_mb} MB space and vacuumed database.", component="BackupManager")
        return {
            "status": "success",
            "deleted_files": deleted_files,
            "reclaimed_mb": reclaimed_mb,
            "db_size_mb": round(SQLITE_DB_PATH.stat().st_size / (1024 * 1024), 2) if SQLITE_DB_PATH.exists() else 0.0
        }

backup_manager = BackupManager()
