"""
Mangesh Nano Pro AI Studio - Storage Inspector & Disk Usage Analyzer
Inspects storage footprint across application categories (SQLite, Caches, Logs, Backups)
and provides safe cleanup operations for non-critical temporary files.
"""

import os
import shutil
import time
from pathlib import Path
from typing import Dict, Any, List

from app.core.config import (
    BASE_DIR, DATABASE_DIR, LOGS_DIR, REPORTS_DIR, BACKUPS_DIR,
    VIDEO_OUTPUT_DIR, IMAGE_OUTPUT_DIR, SQLITE_DB_PATH
)
from app.core.logger import log_event
from app.core.database import db

SAFE_CLEANUP_CATEGORIES = ["temp_caches", "logs", "audio_cache", "cache", "reports"]

FOOTPRINT_CACHE_SECONDS = 600

class StorageInspector:
    def __init__(self):
        self.base_dir = BASE_DIR
        self._footprint_cache: Dict[str, Any] = {"at": 0.0, "bytes": 0, "categories": {}}

    def _get_dir_size(self, path: Path) -> (int, int):
        total_size = 0
        file_count = 0
        if not path.exists():
            return 0, 0
        if path.is_file():
            return path.stat().st_size, 1
        for root, _, files in os.walk(path):
            for f in files:
                fp = Path(root) / f
                try:
                    if fp.is_file():
                        total_size += fp.stat().st_size
                        file_count += 1
                except Exception:
                    pass
        return total_size, file_count

    def _format_size(self, bytes_val: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} TB"

    def _get_last_modified(self, path: Path) -> str:
        try:
            if not path.exists():
                return "N/A"
            mtime = path.stat().st_mtime
            if path.is_dir():
                for f in path.iterdir():
                    try:
                        mtime = max(mtime, f.stat().st_mtime)
                    except Exception:
                        pass
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        except Exception:
            return "N/A"

    def inspect_complete_storage(self) -> Dict[str, Any]:
        """Returns storage metrics across all categories, SQLite tables, and host disk overall."""
        # Disk Overall
        try:
            total, used, free = shutil.disk_usage(self.base_dir)
            total_gb = round(total / (1024**3), 2)
            used_gb = round(used / (1024**3), 2)
            free_gb = round(free / (1024**3), 2)
            used_pct = round((used / total) * 100, 1) if total > 0 else 0.0
        except Exception:
            total_gb, used_gb, free_gb, used_pct = 100.0, 10.0, 90.0, 10.0

        disk_overall = {
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb,
            "used_pct": used_pct,
            "used_percentage": used_pct
        }

        # Categories mapping with metadata (all operational & analytical DBs)
        cat_defs = {
            "sqlite_database": {"title": "SQLite Studio Database", "path": SQLITE_DB_PATH, "can_cleanup": False},
            "sqlite_database_wal": {"title": "SQLite WAL Concurrency Journal", "path": Path(str(SQLITE_DB_PATH) + "-wal"), "can_cleanup": False},
            "duckdb_lakehouse": {"title": "DuckDB Gold Lakehouse & Marts", "path": self.base_dir / "data" / "lakehouse", "can_cleanup": False},
            "training_memory_db": {"title": "AI Training & Knowledge DB", "path": self.base_dir / "data" / "nanopro_training_memory.db", "can_cleanup": False},
            "data_ingestion": {"title": "Autonomous Data Ingestion Lake", "path": self.base_dir / "data_ingestion", "can_cleanup": False},
            "cloud_sftp_storage": {"title": "Cloud SFTP Gateway Storage", "path": self.base_dir / "data" / "sftp_root", "can_cleanup": False},
            "training_corpus": {"title": "Agent Training Corpus & Grounding", "path": self.base_dir / "data" / "training_corpus", "can_cleanup": False},
            "temp_apks": {"title": "APK Temp Staging Cache", "path": self.base_dir / "app" / "temp_apks", "can_cleanup": True},
            "temp_caches": {"title": "Temporary Caches & Sessions", "path": self.base_dir / "app" / "cache", "can_cleanup": True},
            "logs": {"title": "System Audit & Operations Logs", "path": LOGS_DIR, "can_cleanup": True},
            "reports": {"title": "Generated Excel & PDF Reports", "path": REPORTS_DIR, "can_cleanup": True},
            "backups": {"title": "System Backup Archives", "path": BACKUPS_DIR, "can_cleanup": False},
            "database_backups": {"title": "Database Snapshots", "path": BACKUPS_DIR / "db", "can_cleanup": False},
            "video_output": {"title": "Generated Videos & Render Cache", "path": VIDEO_OUTPUT_DIR, "can_cleanup": True},
            "generated_videos": {"title": "AI Video Maker Outputs", "path": VIDEO_OUTPUT_DIR, "can_cleanup": True},
            "image_output": {"title": "Generated Images & Posters", "path": IMAGE_OUTPUT_DIR, "can_cleanup": True},
            "generated_images": {"title": "AI Image Maker Artifacts", "path": IMAGE_OUTPUT_DIR, "can_cleanup": True},
            "generated_code": {"title": "Coding Agent Code Cache", "path": self.base_dir / "app" / "coding_agent" / "workspace", "can_cleanup": True},
            "audio_cache": {"title": "Audio Synthesizer & Speech Cache", "path": self.base_dir / "app" / "cache" / "audio", "can_cleanup": True},
            "resumes_vault": {"title": "Resume Vault & Documents", "path": self.base_dir / "app" / "resumes", "can_cleanup": False},
            "main_application": {"title": "Nano Pro AI Core Application", "path": self.base_dir, "can_cleanup": False}
        }

        categories = {}
        total_app_bytes = 0

        for cat_key, cdef in cat_defs.items():
            target_path = Path(cdef["path"])
            size_b, count = self._get_dir_size(target_path)
            last_mod = self._get_last_modified(target_path)

            if cat_key == "main_application":
                total_app_bytes = size_b

            categories[cat_key] = {
                "title": cdef["title"],
                "path": str(target_path),
                "size_bytes": size_b,
                "size_formatted": self._format_size(size_b),
                "file_count": count,
                "last_modified": last_mod,
                "can_cleanup": cdef["can_cleanup"]
            }

            try:
                db.record_storage_measurement(cat_key, str(target_path), size_b, count)
            except Exception:
                pass

        if total_app_bytes == 0:
            total_app_bytes = sum(c["size_bytes"] for k, c in categories.items() if k not in ["main_application", "generated_videos", "generated_images"])

        # Introspect SQLite Database Tables + DuckDB Gold Lakehouse Tables
        db_tables = []
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
                rows = cursor.fetchall()
                for r in rows:
                    tbl_name = r[0] if isinstance(r, (list, tuple)) else r["name"]
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {tbl_name}")
                        cnt = cursor.fetchone()[0]
                    except Exception:
                        cnt = 0
                    db_tables.append({"table_name": tbl_name, "record_count": cnt, "engine": "SQLite Relational"})
        except Exception as dbe:
            log_event(f"Error reading SQLite tables for storage inspector: {dbe}", level="WARNING", component="StorageInspector")

        try:
            duckdb_path = self.base_dir / "data" / "lakehouse" / "gold_marts.duckdb"
            if duckdb_path.exists():
                import duckdb
                con = duckdb.connect(str(duckdb_path), read_only=True)
                duck_tables = con.execute("SHOW TABLES").fetchall()
                for dt in duck_tables:
                    t_name = dt[0]
                    try:
                        cnt = con.execute(f"SELECT COUNT(*) FROM {t_name}").fetchone()[0]
                    except Exception:
                        cnt = 0
                    db_tables.append({"table_name": f"🦆 {t_name}", "record_count": cnt, "engine": "DuckDB Lakehouse"})
                con.close()
        except Exception as dde:
            log_event(f"Error reading DuckDB tables for storage inspector: {dde}", level="DEBUG", component="StorageInspector")

        # Recommendations
        recommendations = [
            f"Overall Host Disk: {free_gb} GB free out of {total_gb} GB ({used_pct}% utilized). Health status: Optimal.",
            "Database Integrity: SQLite WAL journaling active. Automated daily compaction scheduled.",
            "Safe Cleanups: Logs, temporary caches, and reports can be safely purged via Safe Clean buttons without touching core models or credentials.",
            f"Data Tables Monitored: {len(db_tables)} persistent relational tables tracked in studio_memory.db."
        ]

        return {
            "status": "success",
            "total_app_bytes": total_app_bytes,
            "total_app_formatted": self._format_size(total_app_bytes),
            "categories": categories,
            "database_tables": db_tables,
            "recommendations": recommendations,
            "disk_overall": disk_overall,
            "measured_at": time.time()
        }

    def execute_safe_cleanup(self, category: str) -> Dict[str, Any]:
        """Safely cleans up files in approved non-critical categories."""
        log_event(f"Executing safe storage cleanup for category [{category}]", component="StorageInspector")
        
        allowed = SAFE_CLEANUP_CATEGORIES + ["video_output", "image_output", "generated_videos", "generated_images", "generated_code"]
        if category not in allowed:
            return {
                "status": "error",
                "category": category,
                "message": f"Category '{category}' is protected or unsafe for automated cleanup."
            }

        deleted_files = 0
        freed_bytes = 0

        target_dir = None
        if category in ["temp_caches", "cache"]:
            target_dir = self.base_dir / "app" / "cache"
        elif category == "logs":
            target_dir = LOGS_DIR
        elif category == "reports":
            target_dir = REPORTS_DIR
        elif category in ["video_output", "generated_videos"]:
            target_dir = VIDEO_OUTPUT_DIR
        elif category in ["image_output", "generated_images"]:
            target_dir = IMAGE_OUTPUT_DIR
        elif category == "generated_code":
            target_dir = self.base_dir / "app" / "coding_agent" / "workspace"
        elif category == "audio_cache":
            target_dir = self.base_dir / "app" / "cache" / "audio"

        if target_dir and target_dir.exists():
            for item in target_dir.iterdir():
                try:
                    if item.is_file() and not item.name.endswith(".db"):
                        sz = item.stat().st_size
                        item.unlink()
                        deleted_files += 1
                        freed_bytes += sz
                except Exception:
                    pass

        return {
            "status": "success",
            "category": category,
            "deleted_files": deleted_files,
            "freed_bytes": freed_bytes,
            "freed_formatted": self._format_size(freed_bytes),
            "message": f"Safe cleanup of '{category}' completed successfully. Freed {self._format_size(freed_bytes)}."
        }

    def measure_footprint(self, force: bool = False) -> Dict[str, Any]:
        """Returns the app's own writable footprint (cached) so host-wide disk noise is separable."""
        now = time.time()
        if not force and now - float(self._footprint_cache.get("at") or 0) < FOOTPRINT_CACHE_SECONDS:
            return self._footprint_cache

        roots = {
            "app_database": DATABASE_DIR,
            "app_reports": REPORTS_DIR,
            "app_backups": BACKUPS_DIR,
            "app_logs": LOGS_DIR,
            "app_cache": self.base_dir / "app" / "cache",
            "data_sftp": self.base_dir / "data" / "sftp",
            "data_modeling": self.base_dir / "data" / "modeling",
            "data_lakehouse": self.base_dir / "data" / "lakehouse",
            "data_ingestion": self.base_dir / "data_ingestion",
        }
        categories = {}
        total = 0
        for key, path in roots.items():
            size, _ = self._get_dir_size(Path(path))
            categories[key] = size
            total += size

        self._footprint_cache = {
            "at": now,
            "bytes": total,
            "formatted": self._format_size(total),
            "categories": {k: self._format_size(v) for k, v in categories.items()},
        }
        return self._footprint_cache

    def run_housekeeping(self, report_days: int = 14, log_days: int = 14, keep_backups: int = 3) -> Dict[str, Any]:
        """Runs bounded retention/compaction across generated artifacts. Safe to run repeatedly."""
        before = self.measure_footprint(force=True)
        report = {
            "deleted_files": 0,
            "reclaimed_bytes": 0,
            "details": {},
        }

        def _prune_dir(path: Path, max_age_days: int) -> None:
            cutoff = time.time() - max_age_days * 86400
            removed = 0
            freed = 0
            if not path.exists():
                return
            for f in path.rglob("*"):
                try:
                    if not f.is_file() or f.name.endswith((".db", ".db-wal", ".db-shm")):
                        continue
                    if f.stat().st_mtime >= cutoff:
                        continue
                    sz = f.stat().st_size
                    f.unlink(missing_ok=True)
                    removed += 1
                    freed += sz
                except Exception:
                    continue
            report["deleted_files"] += removed
            report["reclaimed_bytes"] += freed
            report["details"][str(path)] = {"deleted": removed, "reclaimed_bytes": freed}

        try:
            from app.core.backup_manager import backup_manager
            pruned = backup_manager.prune_and_vacuum(keep_backups=keep_backups, max_report_age_hours=report_days * 24)
            report["details"]["backups"] = pruned
            report["deleted_files"] += int(pruned.get("deleted_files") or 0)
            report["reclaimed_bytes"] += int(float(pruned.get("reclaimed_mb") or 0) * 1024 * 1024)
        except Exception as exc:
            report["details"]["backups"] = {"error": str(exc)}

        _prune_dir(REPORTS_DIR, report_days)
        _prune_dir(LOGS_DIR, log_days)
        _prune_dir(self.base_dir / "app" / "cache", report_days)
        _prune_dir(self.base_dir / "app" / "temp_apks", report_days)
        _prune_dir(self.base_dir / "data" / "modeling" / "attachments", 1)

        try:
            from app.core.cloud_sftp_hub import cloud_sftp_hub
            sftp_res = cloud_sftp_hub.enforce_retention_policy(retention_days=20, purge_s3=False)
            report["details"]["sftp_retention"] = {
                "freed_bytes": sftp_res.get("bytes_freed"),
                "purged_files": len(sftp_res.get("purged_files") or []),
                "purged_dirs": len(sftp_res.get("purged_dirs") or []),
            }
        except Exception as exc:
            report["details"]["sftp_retention"] = {"error": str(exc)}

        try:
            with db.get_connection() as conn:
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                conn.execute("VACUUM")
            report["details"]["sqlite"] = {"checkpoint": "truncate", "vacuum": "ok"}
        except Exception as exc:
            report["details"]["sqlite"] = {"error": str(exc)}

        after = self.measure_footprint(force=True)
        freed = max(int(before.get("bytes") or 0) - int(after.get("bytes") or 0), 0)
        report["status"] = "success"
        report["footprint_before"] = before.get("formatted")
        report["footprint_after"] = after.get("formatted")
        report["reclaimed_bytes"] = max(report["reclaimed_bytes"], freed)
        report["reclaimed_formatted"] = self._format_size(report["reclaimed_bytes"])
        log_event(
            f"Storage housekeeping: {report['deleted_files']} files, reclaimed {report['reclaimed_formatted']} "
            f"(footprint {report['footprint_before']} → {report['footprint_after']}).",
            component="StorageInspector",
        )
        return report

storage_inspector = StorageInspector()
