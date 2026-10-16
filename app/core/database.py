import re
"""
Mangesh Nano Pro AI Studio - SQLite Persistent Storage & Credentials Vault
Provides persistent schema for Tasks, Reminders, Knowledge Base, Prompts, Backups,
Approvals, Credentials Vault, Audit History, Conversations, and Automation Pipelines.
"""

import os
import sqlite3
import json
import time
import base64
import hashlib
import threading
from functools import wraps
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from app.core.config import SQLITE_DB_PATH
from app.core.logger import log_event
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def sqlite_retry(max_retries: int = 5, initial_backoff: float = 0.25):
    """
    Thread-safe retry decorator with exponential backoff for SQLite write operations.
    Catches sqlite3.OperationalError: database is locked / database is busy.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            backoff = initial_backoff
            while True:
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    err_msg = str(e).lower()
                    if "locked" in err_msg or "busy" in err_msg:
                        retries += 1
                        if retries >= max_retries:
                            log_event(f"SQLite lock retry limit exceeded ({max_retries} attempts) on {func.__name__}: {e}", level="ERROR", component="Database")
                            raise
                        time.sleep(backoff)
                        backoff *= 2.0  # Exponential backoff
                    else:
                        raise
        return wrapper
    return decorator

_thread_local = threading.local()

def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    High-Concurrency SQLite WAL Engine:
    Initializes thread-safe connection with 30-second busy timeout, in-memory temp store,
    64MB dedicated cache, and Write-Ahead Logging (WAL) mode.
    Caches connections per thread to eliminate per-query connection open and PRAGMA execution overhead.
    """
    target = str(db_path or SQLITE_DB_PATH)
    connections = getattr(_thread_local, "connections", None)
    if connections is None:
        connections = {}
        _thread_local.connections = connections

    conn = connections.get(target)
    if conn is not None:
        try:
            conn.execute("SELECT 1;")
            return conn
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            connections.pop(target, None)

    conn = sqlite3.connect(target, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA busy_timeout = 30000;")       # 30-second lock queue threshold
        cursor.execute("PRAGMA synchronous = NORMAL;")
        cursor.execute("PRAGMA temp_store = MEMORY;")
        cursor.execute("PRAGMA cache_size = -64000;")         # 64MB dedicated cache
        cursor.execute("PRAGMA wal_autocheckpoint = 1000;")
        cursor.close()
    except Exception:
        pass
    connections[target] = conn
    return conn

def close_thread_connection(db_path: Optional[Path] = None):
    """Closes and removes the current thread's cached connection."""
    target = str(db_path or SQLITE_DB_PATH)
    connections = getattr(_thread_local, "connections", None)
    if connections and target in connections:
        conn = connections.pop(target, None)
        if conn:
            try:
                conn.close()
            except Exception:
                pass

class DatabaseManager:
    def __init__(self, db_path: Path = SQLITE_DB_PATH):
        self.db_path = db_path
        self._task_cache: Dict[str, Dict[str, Any]] = {}
        self._task_cache_lock = threading.Lock()
        self._init_db()

    def stage_task(self, task: Dict[str, Any]):
        """Updates in-memory task cache immediately for zero-latency consistency."""
        task_id = task.get("id")
        if not task_id:
            return
        with self._task_cache_lock:
            cached = self._task_cache.get(task_id)
            updated_at = task.get("updated_at", time.time())
            if cached and cached.get("updated_at", 0) > updated_at:
                return
            self._task_cache[task_id] = dict(task)

    def get_connection(self) -> sqlite3.Connection:
        """
        Returns thread-safe SQLite connection initialized with Write-Ahead Logging (WAL)
        and enterprise high-concurrency pragmas.
        """
        return get_db_connection(self.db_path)

    @contextmanager
    def connection_scope(self):
        """Safe context manager guaranteeing transaction commit/rollback."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode = WAL;")
            
            # Tasks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                plan TEXT,
                agent_id TEXT,
                status TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                result_data TEXT,
                error_message TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                completed_at REAL
            )""")

            # Reminders & Scheduled automation
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                due_time TEXT NOT NULL,
                recurrence TEXT,
                status TEXT DEFAULT 'pending',
                created_at REAL NOT NULL,
                completed_at REAL
            )""")

            # Knowledge base and persistent memory
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )""")

            # Prompt History & Conversations
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                agent_assigned TEXT,
                response_summary TEXT,
                rating INTEGER DEFAULT 0,
                created_at REAL NOT NULL
            )""")

            # Backups ledger
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups_ledger (
                id TEXT PRIMARY KEY,
                backup_path TEXT NOT NULL,
                backup_type TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                items_count INTEGER NOT NULL,
                created_at REAL NOT NULL
            )""")

            # Generated Artifacts (Videos, Thumbnails, Code Patches)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                artifact_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                metadata TEXT,
                created_at REAL NOT NULL
            )""")

            # Approvals Queue (Risk governance)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                action_name TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                target_system TEXT NOT NULL,
                risk_level TEXT NOT NULL, -- LOW, MEDIUM, HIGH
                reason TEXT NOT NULL,
                expected_impact TEXT NOT NULL,
                is_reversible INTEGER DEFAULT 1,
                parameters TEXT,
                status TEXT DEFAULT 'pending', -- pending, approved, rejected
                created_at REAL NOT NULL,
                decided_at REAL
            )""")

            # Credentials Vault (Encrypted secrets)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id TEXT PRIMARY KEY,
                service_name TEXT NOT NULL,
                credential_type TEXT NOT NULL, -- database, api_key, cloud, email, sftp, web
                username TEXT,
                encrypted_secret TEXT NOT NULL,
                host TEXT,
                port TEXT,
                database_name TEXT,
                email TEXT,
                mobile_number TEXT,
                additional_metadata TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )""")

            # Chat Conversation History (Persistent multi-turn chat)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                sender TEXT NOT NULL, -- user, manager, agent
                message TEXT NOT NULL,
                metadata TEXT,
                created_at REAL NOT NULL
            )""")

            # Automation Pipelines & Schedules
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipelines (
                id TEXT PRIMARY KEY,
                pipeline_name TEXT NOT NULL,
                source_type TEXT NOT NULL, -- snowflake, oracle, sftp, local_folder, csv
                target_type TEXT NOT NULL, -- database, report, local_file, email
                schedule_cron TEXT,
                status TEXT DEFAULT 'active',
                last_run_at REAL,
                last_status TEXT,
                config TEXT,
                created_at REAL NOT NULL
            )""")

            
            # 11. Free APIs Directory
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS free_apis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id TEXT UNIQUE NOT NULL,
                provider_name TEXT NOT NULL,
                service_name TEXT NOT NULL,
                category TEXT NOT NULL,
                official_url TEXT NOT NULL,
                documentation_url TEXT,
                pricing_url TEXT,
                registration_url TEXT,
                free_tier_type TEXT NOT NULL,
                free_quota TEXT,
                rate_limit TEXT,
                credit_card_required INTEGER DEFAULT 0,
                phone_verification INTEGER DEFAULT 0,
                authentication_type TEXT DEFAULT 'API Key',
                commercial_use_notes TEXT,
                languages_supported TEXT,
                availability_status TEXT DEFAULT 'Active',
                quality_score REAL DEFAULT 9.5,
                research_summary TEXT,
                last_verified_at REAL NOT NULL,
                created_at REAL NOT NULL
            )''')

            # 12. GitHub AI Projects
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS github_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                repo_url TEXT UNIQUE NOT NULL,
                short_description TEXT,
                language TEXT,
                category TEXT NOT NULL,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                last_update_date TEXT,
                latest_release TEXT,
                license TEXT DEFAULT 'MIT',
                dependencies TEXT,
                setup_complexity TEXT DEFAULT 'Low',
                local_execution_support INTEGER DEFAULT 1,
                api_requirements TEXT,
                supported_languages TEXT,
                speech_approach TEXT,
                tts_approach TEXT,
                potential_use TEXT,
                security_notes TEXT,
                last_checked_at REAL NOT NULL
            )''')

            # 13. AI Research Library
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                source_url TEXT,
                summary TEXT NOT NULL,
                technical_requirements TEXT,
                user_notes TEXT,
                is_favorite INTEGER DEFAULT 0,
                tags TEXT,
                verified_at REAL NOT NULL,
                created_at REAL NOT NULL
            )''')

            # 14. Discovery Schedules
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS discovery_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                query TEXT NOT NULL,
                category TEXT NOT NULL,
                frequency TEXT NOT NULL, -- 6h, 12h, daily, weekly, on_demand
                status TEXT DEFAULT 'active', -- active, paused, completed
                last_run REAL,
                next_run REAL,
                results_count INTEGER DEFAULT 0,
                last_status TEXT DEFAULT 'Ready'
            )''')

            # 15. Live Discovery Jobs
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_discovery_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                query TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL, -- QUEUED, SEARCHING, FETCHING, ANALYZING, VERIFYING, SAVING, COMPLETED, FAILED, PAUSED
                results_processed INTEGER DEFAULT 0,
                new_resources INTEGER DEFAULT 0,
                duplicates_skipped INTEGER DEFAULT 0,
                error_message TEXT,
                started_at REAL NOT NULL,
                completed_at REAL
            )''')

            conn.commit()
            
            # 16. Communication Logs (Email & Telegram dispatch ledger)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS communication_logs (
                id TEXT PRIMARY KEY,
                channel TEXT NOT NULL, -- email, telegram
                recipient TEXT NOT NULL,
                subject TEXT,
                content TEXT NOT NULL,
                status TEXT NOT NULL, -- sent, draft, pending_approval, failed
                response_data TEXT,
                error_message TEXT,
                created_at REAL NOT NULL,
                sent_at REAL
            )''')
            conn.commit()

            
            # 17. Amazon Tracked Products
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS amazon_products (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                asin TEXT NOT NULL,
                title TEXT NOT NULL,
                currency TEXT DEFAULT 'INR',
                target_price REAL,
                monitoring_frequency TEXT DEFAULT 'daily',
                latest_price REAL,
                previous_price REAL,
                lowest_price REAL,
                highest_price REAL,
                status TEXT DEFAULT 'active',
                data_source TEXT DEFAULT 'verified_catalog',
                last_checked_at REAL,
                created_at REAL NOT NULL
            )''')

            # 18. Amazon Price History (Immutable historical observations)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS amazon_price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'INR',
                difference REAL DEFAULT 0.0,
                pct_change REAL DEFAULT 0.0,
                data_source TEXT DEFAULT 'verified_catalog',
                observation_time REAL NOT NULL
            )''')

            # 19. Job Postings & Career Opportunities
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_postings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                source_url TEXT,
                skills_required TEXT,
                salary_info TEXT,
                experience_level TEXT,
                application_status TEXT DEFAULT 'discovered',
                follow_up_date TEXT,
                notes TEXT,
                discovered_at REAL NOT NULL
            )''')

            # 20. Learning & Interview Practice Sessions
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT DEFAULT 'medium',
                questions_json TEXT NOT NULL,
                answers_json TEXT,
                score INTEGER DEFAULT 0,
                weak_areas TEXT,
                status TEXT DEFAULT 'completed',
                completed_at REAL,
                created_at REAL NOT NULL
            )''')

            # 21. Startup Recovery History
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                discovered_interrupted INTEGER DEFAULT 0,
                discovered_overdue INTEGER DEFAULT 0,
                recovered_tasks INTEGER DEFAULT 0,
                coalesced_reminders INTEGER DEFAULT 0,
                failed_retries INTEGER DEFAULT 0,
                summary_log TEXT,
                recovered_at REAL NOT NULL
            )''')

            # 22. Scheduled System Discoveries
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_discoveries (
                id TEXT PRIMARY KEY,
                cycle_id TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL, -- CRITICAL, WARNING, INFO, OPPORTUNITY
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                evidence TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                status TEXT DEFAULT 'unresolved', -- unresolved, acknowledged, resolved
                acknowledged_at REAL,
                resolved_at REAL,
                detected_at REAL NOT NULL
            )''')

            # 23. Scheduled Discovery Cycles
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_discovery_cycles (
                id TEXT PRIMARY KEY,
                overall_status TEXT NOT NULL, -- HEALTHY, WARNING, CRITICAL
                duration_sec REAL NOT NULL,
                categories_checked TEXT NOT NULL,
                total_issues INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                info_count INTEGER DEFAULT 0,
                resolved_since_last INTEGER DEFAULT 0,
                summary_report TEXT NOT NULL,
                telegram_sent INTEGER DEFAULT 0,
                telegram_error TEXT,
                executed_at REAL NOT NULL
            )''')

            # 24. Hourly & Alert Notification History
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_history (
                id TEXT PRIMARY KEY,
                notification_type TEXT NOT NULL, -- hourly_summary, critical_alert, warning, test, resolution
                channel TEXT NOT NULL, -- telegram, ui, email
                recipient TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL, -- sent, failed, pending
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                cycle_id TEXT,
                created_at REAL NOT NULL,
                sent_at REAL
            )''')

            # 26. Scheduled Automation Tasks (Task Scheduler)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_automation_tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                task_type TEXT NOT NULL,
                script_content TEXT,
                file_path TEXT,
                db_connection TEXT,
                schedule_type TEXT NOT NULL,
                recurrence_expr TEXT,
                start_time TEXT,
                end_time TEXT,
                timezone TEXT DEFAULT 'Asia/Kolkata',
                timeout_sec INTEGER DEFAULT 300,
                retry_policy TEXT,
                working_dir TEXT,
                env_vars TEXT,
                notification_pref TEXT,
                is_enabled INTEGER DEFAULT 1,
                is_paused INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Ready',
                next_run_at TEXT,
                last_run_at TEXT,
                last_status TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )""")

            # 27. Task Execution Runs (Task Scheduler History)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_execution_runs (
                run_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                task_name TEXT NOT NULL,
                trigger_type TEXT DEFAULT 'Scheduled',
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_sec REAL,
                status TEXT NOT NULL,
                exit_code INTEGER,
                stdout TEXT,
                stderr TEXT,
                error_details TEXT,
                created_at REAL NOT NULL
            )""")

            # 28. News Articles (ABP Majha & Aaj Tak)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                article_id TEXT PRIMARY KEY,
                publisher TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                summary_en TEXT,
                summary_mr TEXT,
                category TEXT NOT NULL,
                importance TEXT DEFAULT 'Normal',
                published_at TEXT NOT NULL,
                retrieved_at REAL NOT NULL,
                thumbnail_url TEXT,
                is_new INTEGER DEFAULT 1,
                is_notified INTEGER DEFAULT 0
            )""")

            # 29. Entertainment & Modern Lifestyle Items
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entertainment_items (
                item_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                creator TEXT,
                description TEXT,
                thumbnail_url TEXT,
                media_url TEXT,
                source TEXT,
                published_at TEXT,
                metadata_json TEXT,
                is_favorite INTEGER DEFAULT 0,
                created_at REAL NOT NULL
            )""")

            # 30. Uploaded Books & Documents
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_books (
                book_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                total_pages INTEGER DEFAULT 1,
                total_chapters INTEGER DEFAULT 1,
                chapters_json TEXT,
                reading_progress_pct REAL DEFAULT 0.0,
                current_chapter_idx INTEGER DEFAULT 0,
                bookmarks_json TEXT,
                notes_json TEXT,
                processed_at REAL NOT NULL
            )""")

            # 31. Book Text Chunks for Semantic & Chapter Retrieval
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS book_chunks (
                chunk_id TEXT PRIMARY KEY,
                book_id TEXT NOT NULL,
                chapter_index INTEGER DEFAULT 0,
                chapter_title TEXT,
                page_number INTEGER DEFAULT 1,
                chunk_text TEXT NOT NULL,
                created_at REAL NOT NULL
            )""")

            # 25. Daily Storage Growth Measurements
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS storage_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_date TEXT NOT NULL,
                category TEXT NOT NULL,
                path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                file_count INTEGER NOT NULL,
                measured_at REAL NOT NULL
            )''')

            # Performance & Concurrency Optimization Indexes (F12)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id, id ASC);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_credentials_service ON credentials(service_name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at DESC, status);")

            self._seed_verified_research(cursor)
            conn.commit()
            log_event(f"Database initialized successfully at {self.db_path}", component="Database")

    # --- Database Maintenance & Vacuuming (F14) ---
    @sqlite_retry()
    def vacuum_and_checkpoint(self) -> Dict[str, Any]:
        """
        Executes WAL checkpoint truncation and full database vacuuming (F14).
        Flushes all WAL transactions back to studio_memory.db, truncates the WAL file,
        reclaims free pages, and verifies database integrity.
        Ensures database file size remains optimized below the 15 MB SLA.
        """
        initial_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT count(*) FROM data_engineer_records")
                cnt_row = cursor.fetchone()
                if cnt_row and cnt_row[0] > 10000:
                    cursor.execute("""
                    DELETE FROM data_engineer_records WHERE rowid NOT IN (
                        SELECT rowid FROM data_engineer_records ORDER BY rowid DESC LIMIT 10000
                    )
                    """)
                    conn.commit()
            except Exception:
                pass

            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            cursor.execute("VACUUM;")
            cursor.execute("PRAGMA integrity_check;")
            integrity_row = cursor.fetchone()
            integrity_status = integrity_row[0] if integrity_row else "unknown"
            cursor.execute("PRAGMA page_count;")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size;")
            page_size = cursor.fetchone()[0]
            calculated_size = page_count * page_size

        final_size = self.db_path.stat().st_size if self.db_path.exists() else calculated_size
        log_event(
            f"Database vacuum & checkpoint complete: initial={initial_size}B, final={final_size}B, integrity={integrity_status}",
            component="Database"
        )
        return {
            "initial_size_bytes": initial_size,
            "final_size_bytes": final_size,
            "final_size_mb": round(final_size / (1024 * 1024), 2),
            "page_count": page_count,
            "page_size": page_size,
            "integrity": integrity_status,
            "is_optimized": final_size < 15 * 1024 * 1024 and integrity_status.lower() == "ok"
        }

    # --- Task Operations ---
    @sqlite_retry()
    def save_task(self, task: Dict[str, Any]):
        task_id = task["id"]
        task_copy = dict(task)
        now = time.time()
        updated_at = task_copy.get("updated_at", now)
        created_at = task_copy.get("created_at", now)

        with self._task_cache_lock:
            cached = self._task_cache.get(task_id)
            if cached and cached.get("updated_at", 0) > updated_at:
                # Stale snapshot: do not overwrite newer in-memory state
                return
            self._task_cache[task_id] = task_copy

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO tasks (
                id, prompt, plan, agent_id, status, progress, result_data, error_message, created_at, updated_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                prompt = excluded.prompt,
                plan = excluded.plan,
                agent_id = excluded.agent_id,
                status = excluded.status,
                progress = excluded.progress,
                result_data = excluded.result_data,
                error_message = excluded.error_message,
                updated_at = excluded.updated_at,
                completed_at = COALESCE(excluded.completed_at, tasks.completed_at)
            WHERE excluded.updated_at >= tasks.updated_at
            """, (
                task_id,
                task_copy["prompt"],
                json.dumps(task_copy.get("plan", [])),
                task_copy.get("agent_id", "manager"),
                task_copy.get("status", "pending"),
                task_copy.get("progress", 0),
                json.dumps(task_copy.get("result_data", {})),
                task_copy.get("error_message", None),
                created_at,
                updated_at,
                task_copy.get("completed_at", None)
            ))
            conn.commit()
            cursor.close()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._task_cache_lock:
            cached = self._task_cache.get(task_id)
            if cached is not None:
                d = dict(cached)
                if isinstance(d.get("plan"), str):
                    try:
                        d["plan"] = json.loads(d["plan"])
                    except Exception:
                        d["plan"] = []
                elif d.get("plan") is None:
                    d["plan"] = []
                if isinstance(d.get("result_data"), str):
                    try:
                        d["result_data"] = json.loads(d["result_data"])
                    except Exception:
                        d["result_data"] = {}
                elif d.get("result_data") is None:
                    d["result_data"] = {}
                return d

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            d = dict(row)
            d["plan"] = json.loads(d["plan"]) if d["plan"] else []
            d["result_data"] = json.loads(d["result_data"]) if d["result_data"] else {}
            with self._task_cache_lock:
                self._task_cache[task_id] = dict(d)
            return d

    def list_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            cursor.close()
            results = []
            seen_ids = set()
            for r in rows:
                d = dict(r)
                d["plan"] = json.loads(d["plan"]) if d["plan"] else []
                d["result_data"] = json.loads(d["result_data"]) if d["result_data"] else {}
                task_id = d["id"]
                seen_ids.add(task_id)
                with self._task_cache_lock:
                    cached = self._task_cache.get(task_id)
                    if cached and cached.get("updated_at", 0) > d.get("updated_at", 0):
                        d = dict(cached)
                results.append(d)

            with self._task_cache_lock:
                for tid, ctask in self._task_cache.items():
                    if tid not in seen_ids:
                        results.append(dict(ctask))

            results.sort(key=lambda t: t.get("created_at", 0), reverse=True)
            return results[:limit]

    # --- Reminders Operations ---
    @sqlite_retry()
    def add_reminder(self, title: str, description: str, due_time: str, recurrence: str = None) -> str:
        reminder_id = f"rem_{int(time.time()*1000)}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO reminders (id, title, description, due_time, recurrence, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """, (reminder_id, title, description, due_time, recurrence, time.time()))
            conn.commit()
        return reminder_id

    def list_reminders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM reminders WHERE status = ? ORDER BY due_time ASC", (status,))
            else:
                cursor.execute("SELECT * FROM reminders ORDER BY due_time ASC")
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def update_reminder_status(self, reminder_id: str, status: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE reminders SET status = ?, completed_at = ? WHERE id = ?
            """, (status, time.time() if status == 'completed' else None, reminder_id))
            conn.commit()

    # --- Knowledge Base Operations ---
    @sqlite_retry()
    def add_knowledge(self, category: str, title: str, content: str, metadata: dict = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = time.time()
            cursor.execute("""
            INSERT INTO project_knowledge (category, title, content, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (category, title, content, json.dumps(metadata or {}), now, now))
            conn.commit()
            return cursor.lastrowid

    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            like_query = f"%{query}%"
            cursor.execute("""
            SELECT * FROM project_knowledge 
            WHERE title LIKE ? OR content LIKE ? OR category LIKE ?
            ORDER BY updated_at DESC LIMIT 20
            """, (like_query, like_query, like_query))
            res = []
            for r in cursor.fetchall():
                d = dict(r)
                d["metadata"] = json.loads(d["metadata"]) if d["metadata"] else {}
                res.append(d)
            return res

    # --- Approvals Queue Operations ---
    @sqlite_retry()
    def create_approval(
        self,
        action_name: str,
        agent_id: str,
        target_system: str,
        risk_level: str,
        reason: str,
        expected_impact: str,
        parameters: Dict[str, Any] = None,
        task_id: Optional[str] = None,
        is_reversible: bool = True
    ) -> str:
        approval_id = f"appr_{int(time.time()*1000)}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO approvals (
                id, task_id, action_name, agent_id, target_system,
                risk_level, reason, expected_impact, is_reversible, parameters, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (
                approval_id, task_id, action_name, agent_id, target_system,
                risk_level.upper(), reason, expected_impact, 1 if is_reversible else 0,
                json.dumps(parameters or {}), time.time()
            ))
            conn.commit()
        log_event(f"Created approval request [{approval_id}]: {action_name} ({risk_level}) for {agent_id}", component="ApprovalQueue")
        
        # Dispatch 1-Click WhatsApp & Telegram Security Approval Alert
        try:
            self._notify_approval_requested(approval_id, action_name, target_system, risk_level, reason)
        except Exception as e:
            log_event(f"Approval dispatch notice: {e}", level="WARNING", component="ApprovalQueue")

        return approval_id

    def _notify_approval_requested(self, approval_id: str, action_name: str, target_system: str, risk_level: str, reason: str):
        """Sends WhatsApp and Telegram alert for pending security approval."""
        msg = (
            f"🛡️ [NanoPro Security & Approvals Queue]\n\n"
            f"⚠️ New Action Requires Your 1-Click Approval!\n"
            f"• Action: {action_name}\n"
            f"• Target System: {target_system}\n"
            f"• Risk Level: {risk_level.upper()}\n"
            f"• Reason: {reason}\n"
            f"• Approval ID: {approval_id}\n\n"
            f"👉 1-Click Decisions:\n"
            f"✅ Approve: https://mangesh-nanopro-studio.onrender.com/api/approvals/quick_decide?id={approval_id}&decision=approved\n\n"
            f"🛑 Reject: https://mangesh-nanopro-studio.onrender.com/api/approvals/quick_decide?id={approval_id}&decision=rejected"
        )
        # 1. Dispatch to Meta WhatsApp Business Cloud API
        try:
            from app.core.communication_center import communication_center
            communication_center.send_whatsapp_cloud_api(
                phone="+918433755448",
                message=msg
            )
        except Exception:
            pass

        # 2. Dispatch to Health & Security Monitor Bot on Telegram
        try:
            from app.core.telegram_router import send_telegram_routed_message
            send_telegram_routed_message(category="health", text=msg)
        except Exception:
            pass

    def list_approvals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM approvals WHERE status = ? ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM approvals ORDER BY created_at DESC")
            results = []
            for r in cursor.fetchall():
                d = dict(r)
                d["parameters"] = json.loads(d["parameters"]) if d["parameters"] else {}
                results.append(d)
            return results

    @sqlite_retry()
    def decide_approval(self, approval_id: str, decision: str) -> bool:
        """Sets approval status to 'approved' or 'rejected'."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE approvals SET status = ?, decided_at = ? WHERE id = ?
            """, (decision.lower(), time.time(), approval_id))
            conn.commit()
        log_event(f"Approval [{approval_id}] decided: {decision.upper()}", component="ApprovalQueue")
        return True

    def get_approval(self, approval_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single approval record by its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["parameters"] = json.loads(d["parameters"]) if d["parameters"] else {}
                return d
            return None

    @sqlite_retry()
    def delete_approval(self, approval_id: str) -> bool:
        """Deletes a specific approval record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM approvals WHERE id = ?", (approval_id,))
            conn.commit()
        log_event(f"Deleted approval request [{approval_id}]", component="ApprovalQueue")
        return True

    @sqlite_retry()
    def delete_all_approvals(self, status: Optional[str] = None) -> int:
        """Deletes all approvals or all matching given status (e.g. 'pending')."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("DELETE FROM approvals WHERE status = ?", (status.lower(),))
            else:
                cursor.execute("DELETE FROM approvals")
            deleted_count = cursor.rowcount
            conn.commit()
        log_event(f"Bulk deleted {deleted_count} approvals (status={status})", component="ApprovalQueue")
        return deleted_count

    @sqlite_retry()
    def delete_selective_approvals(self, approval_ids: List[str]) -> int:
        """Deletes multiple selected approval IDs."""
        if not approval_ids:
            return 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(approval_ids))
            cursor.execute(f"DELETE FROM approvals WHERE id IN ({placeholders})", tuple(approval_ids))
            deleted_count = cursor.rowcount
            conn.commit()
        log_event(f"Selectively deleted {deleted_count} approvals", component="ApprovalQueue")
        return deleted_count

    @sqlite_retry()
    def approve_all_pending(self, exclude_extreme_risk: bool = False) -> int:
        """Approves all pending requests (optionally preserving EXTREME risk for manual review)."""
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if exclude_extreme_risk:
                cursor.execute("""
                UPDATE approvals SET status = 'approved', decided_at = ? 
                WHERE status = 'pending' AND UPPER(risk_level) NOT IN ('EXTREME', 'CRITICAL')
                """, (now,))
            else:
                cursor.execute("UPDATE approvals SET status = 'approved', decided_at = ? WHERE status = 'pending'", (now,))
            approved_count = cursor.rowcount
            conn.commit()
        log_event(f"Bulk approved {approved_count} pending requests (exclude_extreme={exclude_extreme_risk})", component="ApprovalQueue")
        return approved_count

    @sqlite_retry()
    def deduplicate_pending_approvals(self) -> Dict[str, Any]:
        """
        Deduplicates pending approval requests with identical action_name and target_system.
        Low & Medium risk duplicates are auto-approved; High & Extreme duplicates are pruned to keep the latest single pending item.
        """
        pending = self.list_approvals(status="pending")
        if not pending:
            return {"status": "success", "deduplicated_count": 0, "removed_count": 0, "auto_approved": 0, "remaining_pending": 0, "remaining_count": 0}

        groups = {}
        for a in pending:
            key = (a.get("action_name", ""), a.get("target_system", ""), a.get("risk_level", "").upper())
            groups.setdefault(key, []).append(a)

        auto_approved = 0
        deleted_duplicates = 0

        for key, items in groups.items():
            if len(items) <= 1:
                continue
            risk = key[2]
            # Sort newest first
            items.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            keep_item = items[0]
            redundant = items[1:]
            redundant_ids = [r["id"] for r in redundant]

            if risk in ["LOW", "MEDIUM"]:
                # Auto-approve all
                for it in items:
                    self.decide_approval(it["id"], "approved")
                    auto_approved += 1
            else:
                # Keep newest single pending, delete older redundant duplicates
                self.delete_selective_approvals(redundant_ids)
                deleted_duplicates += len(redundant_ids)

        remaining = len(self.list_approvals(status="pending"))
        log_event(f"Deduplicated approvals: {deleted_duplicates} pruned, {auto_approved} auto-approved, {remaining} remaining", component="ApprovalQueue")
        return {
            "status": "success",
            "deduplicated_count": deleted_duplicates,
            "removed_count": deleted_duplicates,
            "auto_approved": auto_approved,
            "remaining_pending": remaining,
            "remaining_count": remaining,
            "message": f"Deduplication complete: {deleted_duplicates} redundant requests purged, {auto_approved} low-risk auto-approved. {remaining} unique high-priority items remain."
        }

    # --- Chat Conversation Operations ---
    @sqlite_retry()
    def add_chat_message(self, session_id: str, sender: str, message: str, metadata: Dict[str, Any] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO conversations (session_id, sender, message, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (session_id, sender, message, json.dumps(metadata or {}), time.time()))
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id

    def get_chat_history(self, session_id: str = "default", limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM conversations WHERE session_id = ? ORDER BY id ASC LIMIT ?
            """, (session_id, limit))
            results = []
            for r in cursor.fetchall():
                d = dict(r)
                d["metadata"] = json.loads(d["metadata"]) if d["metadata"] else {}
                results.append(d)
            cursor.close()
            return results

    # --- Pipelines Operations ---
    @sqlite_retry()
    def save_pipeline(self, pipeline: Dict[str, Any]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO pipelines (
                id, pipeline_name, source_type, target_type, schedule_cron, status, last_run_at, last_status, config, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pipeline["id"], pipeline["pipeline_name"], pipeline["source_type"], pipeline["target_type"],
                pipeline.get("schedule_cron", ""), pipeline.get("status", "active"), pipeline.get("last_run_at", None),
                pipeline.get("last_status", "pending"), json.dumps(pipeline.get("config", {})), pipeline.get("created_at", time.time())
            ))
            conn.commit()

    def list_pipelines(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pipelines ORDER BY created_at DESC")
            results = []
            for r in cursor.fetchall():
                d = dict(r)
                d["config"] = json.loads(d["config"]) if d["config"] else {}
                results.append(d)
            return results


    def _seed_verified_research(self, cursor):
        """Seeds verified free APIs, GitHub AI projects, and research items if empty."""
        cursor.execute("SELECT COUNT(*) FROM free_apis")
        if cursor.fetchone()[0] == 0:
            now = time.time()
            apis = [
                ("api_groq", "Groq Cloud", "Groq LPU Inference Engine", "AI Coding, Chat & Fast Inference", "https://groq.com", "https://console.groq.com/docs", "https://groq.com/pricing", "https://console.groq.com", "Permanently Free Tier", "30 RPM / 14,400 Requests/day free", "30 RPM", 0, 0, "API Key", "Allowed for prototyping & evaluation", "Multilingual, Marathi, Hindi, English", "Active", 9.8, "Ultra-fast hardware-accelerated coding (Qwen 2.5 Coder, Llama 3.3 70B) & Whisper Large v3 inference at 500+ tokens/sec.", now, now),
                ("api_gemini", "Google Cloud", "Gemini 2.0 & 1.5 Flash API", "Document Summarization, Text Generation & Coding", "https://ai.google.dev", "https://ai.google.dev/docs", "https://ai.google.dev/pricing", "https://aistudio.google.com", "Permanently Free Tier", "15 RPM / 1,500 Requests/day free", "15 RPM", 0, 0, "API Key", "Free tier non-commercial, enterprise upgrade available", "Native Marathi, Hindi, English, 100+ languages", "Active", 9.9, "1M+ token context window ideal for document summarization, PDF extraction, coding, and direct Marathi comprehension.", now, now),
                ("api_openrouter", "OpenRouter", "OpenRouter Free Model Tier", "AI Chat & Reasoning", "https://openrouter.ai", "https://openrouter.ai/docs", "https://openrouter.ai/models?q=free", "https://openrouter.ai/keys", "Permanently Free Tier", "Free models tagged :free with zero credit card required", "20 RPM", 0, 0, "API Key", "Depends on specific open model license", "Multilingual, Marathi, Hindi, English", "Active", 9.6, "Unified API aggregating free LLaMA 3.2, Gemini Flash, and DeepSeek R1 community endpoints.", now, now),
                ("api_ai4bharat", "AI4Bharat / IIT Madras", "Bhashini & Indic ASR/TTS", "Speech-to-text", "https://ai4bharat.iitm.ac.in", "https://bhashini.gov.in/en/apis", "https://bhashini.gov.in/ulca", "https://bhashini.gov.in", "Open Research Free Tier", "Generous free research tier for Indian languages", "60 RPM", 0, 0, "API Key / Open Research", "Permitted for academic, research, and national development", "Marathi, Hindi, Bengali, Tamil, Telugu, 22 Indian languages", "Active", 9.7, "State-of-the-art Marathi speech recognition and neural voice synthesis created by IIT Madras.", now, now),
                ("api_huggingface", "Hugging Face", "Serverless Inference API", "Embeddings & Models", "https://huggingface.co", "https://huggingface.co/docs/api-inference", "https://huggingface.co/pricing", "https://huggingface.co/join", "Permanently Free Tier", "Rate-limited free tier across thousands of community models", "1000 req/mo free", 0, 0, "API Key", "Subject to model license", "Multilingual", "Active", 9.5, "Instant access to open-source embeddings, Whisper models, and classification pipelines.", now, now),
                ("api_open_meteo", "Open-Meteo", "Open-Meteo Weather API", "Weather", "https://open-meteo.com", "https://open-meteo.com/en/docs", "https://open-meteo.com/en/pricing", "https://open-meteo.com", "Permanently Free Tier", "Up to 10,000 calls/day free for non-commercial", "10,000 / day", 0, 0, "None / Public (No Key Required)", "Free for non-commercial use", "Global", "Active", 9.9, "100% free open-source weather API requiring zero keys or registration.", now, now),
                ("api_jina", "Jina AI", "Jina Reader & Web Search", "Web Search & Reader", "https://jina.ai", "https://jina.ai/reader", "https://jina.ai/pricing", "https://jina.ai", "Free Developer Tier", "10,000,000 free tokens upon signup", "200 RPM", 0, 0, "API Key / Public", "Permitted under terms", "Global", "Active", 9.6, "Converts any web URL into clean markdown suitable for real-time autonomous research.", now, now),
                ("api_github_rest", "GitHub", "GitHub REST & GraphQL API", "Developer Tools", "https://github.com", "https://docs.github.com/en/rest", "https://github.com/pricing", "https://github.com/signup", "Permanently Free Tier", "5,000 req/hr authenticated, 60 req/hr unauthenticated", "5,000 / hr", 0, 0, "Personal Access Token / Public", "Standard developer terms", "Global", "Active", 9.9, "Full repository, commit, release, and stargazers discovery across all open-source projects.", now, now)
            ]
            cursor.executemany("""
            INSERT INTO free_apis (
                resource_id, provider_name, service_name, category, official_url, documentation_url, pricing_url,
                registration_url, free_tier_type, free_quota, rate_limit, credit_card_required, phone_verification,
                authentication_type, commercial_use_notes, languages_supported, availability_status, quality_score,
                research_summary, last_verified_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, apis)

        cursor.execute("SELECT COUNT(*) FROM github_projects")
        if cursor.fetchone()[0] == 0:
            now = time.time()
            projects = [
                ("proj_indicwhisper", "IndicWhisper (AI4Bharat)", "https://github.com/AI4Bharat/IndicWhisper", "State-of-the-art multilingual ASR models for 22 Indian languages including Marathi based on Whisper.", "Python", "Speech Recognition", 1280, 240, "2026-03", "v1.2", "MIT", "PyTorch, Transformers, SoundFile", "Medium", 1, "None (Local Weights)", "Marathi, Hindi, 22 Indian languages", "Fine-tuned Whisper on Indian language speech corpora", "N/A (ASR)", "Native Marathi speech-to-text engine for NanoPro voice assistant.", "Clean code, actively maintained by IIT Madras.", now),
                ("proj_indictts", "Indic-TTS (AI4Bharat)", "https://github.com/AI4Bharat/Indic-TTS", "Text-to-Speech models for Indian languages supporting natural human synthesis in Marathi & Hindi.", "Python/C++", "Text-to-Speech", 990, 185, "2026-02", "v2.0", "MIT", "PyTorch, FastSpeech2, HiFi-GAN", "Medium", 1, "None (Local Weights)", "Marathi, Hindi, Tamil, Telugu", "N/A (TTS)", "FastSpeech2 & VITS acoustic models with HiFi-GAN", "Natural Marathi and Hindi voice response generation.", "Open weights, low inference latency.", now),
                ("proj_piper", "Piper TTS (Rhasspy)", "https://github.com/rhasspy/piper", "Fast, local neural text-to-speech system that sounds great and runs on modest hardware.", "C++/Python", "Text-to-Speech", 5620, 480, "2026-04", "v1.2.0", "MIT", "ONNX Runtime, espeak-ng", "Low", 1, "None (Self-Contained)", "Multilingual, Hindi, English", "N/A (TTS)", "VITS real-time neural voice generation", "Real-time speech feedback for local AI operating centers.", "Zero cloud latency, highly optimized for desktop.", now),
                ("proj_whisper_cpp", "whisper.cpp (Gerganov)", "https://github.com/ggerganov/whisper.cpp", "High-performance inference of OpenAI Whisper in C/C++ with zero dependencies and AVX support.", "C/C++", "Speech Recognition", 34500, 3900, "2026-04", "v1.7.4", "MIT", "Pure C/C++, optional CUDA/Metal", "Low", 1, "None (Self-Contained)", "Marathi, Hindi, English, 99 languages", "Quantized Whisper weights running locally", "N/A (ASR)", "Local speech-to-text without internet or cloud billing.", "Extremely lightweight, runs seamlessly on Windows.", now),
                ("proj_ollama", "Ollama", "https://github.com/ollama/ollama", "Get up and running with Llama 3.2, Mistral, Qwen, and DeepSeek large language models locally.", "Go/Python", "Local AI Models", 112500, 9200, "2026-04", "v0.6.3", "MIT", "Go, C++ llama.cpp backends", "Low", 1, "None (Self-Contained)", "Multilingual", "Local GGUF models", "N/A", "Core LLM execution engine for Mangesh Nano Pro AI Studio.", "Official engine currently powering the studio.", now),
                ("proj_prefect", "Prefect", "https://github.com/PrefectHQ/prefect", "Workflow orchestration framework for building resilient data pipelines and scheduled jobs.", "Python", "Data Engineering & ETL", 17900, 1800, "2026-03", "v3.1", "Apache-2.0", "FastAPI, Pydantic, SQLAlchemy", "Medium", 1, "None (Local SQLite/Server)", "English", "N/A", "N/A", "Enterprise scheduling architecture for Data Engineer agent.", "Robust background execution engine.", now)
            ]
            cursor.executemany("""
            INSERT INTO github_projects (
                project_id, name, repo_url, short_description, language, category, stars, forks,
                last_update_date, latest_release, license, dependencies, setup_complexity,
                local_execution_support, api_requirements, supported_languages, speech_approach,
                tts_approach, potential_use, security_notes, last_checked_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, projects)

        cursor.execute("SELECT COUNT(*) FROM research_library")
        if cursor.fetchone()[0] == 0:
            now = time.time()
            library_items = [
                ("res_marathi_voice", "Marathi & Hindi AI Voice Assistant Architecture", "tutorial", "https://ai4bharat.iitm.ac.in", "Comprehensive guide on building local multilingual voice assistants using IndicWhisper (ASR) + Qwen/LLaMA (Reasoning) + Piper/IndicTTS (Voice). Supports both cloud and 100% offline local execution.", "Python 3.10+, PyTorch/ONNX, Web Speech API fallback", "Tested and verified for NanoPro Marathi integration.", 1, "marathi, voice, asr, tts, local_ai", now, now),
                ("res_free_llms", "Verified Free Tier LLMs Comparison Guide (2026)", "free_api", "https://console.groq.com", "Analysis of verified free LLM APIs: Groq (30 RPM, fast Llama 3.3), Google Gemini 2.0 Flash (1,500 RPD free), and OpenRouter (:free tags). None require credit card verification for starter tiers.", "HTTP REST, API Key", "Keep Groq and Gemini as primary cloud fallbacks.", 1, "free_api, llm, groq, gemini", now, now),
                ("res_data_etl", "Modern Local ETL Pipeline Engineering Best Practices", "data_engineering", "https://github.com/PrefectHQ/prefect", "Reference design for 6-stage ETL (Extraction, Schema Validation, Null Cleaning, Deduplication, Database Loading, Analytical Reporting) on SQLite, Oracle, and Snowflake.", "Python, SQLite/DuckDB, openpyxl", "Core architecture utilized in DataEngineerAgent.", 1, "etl, data_engineering, sqlite, snowflake", now, now)
            ]
            cursor.executemany("""
            INSERT INTO research_library (
                resource_id, title, category, source_url, summary, technical_requirements,
                user_notes, is_favorite, tags, verified_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, library_items)

        cursor.execute("SELECT COUNT(*) FROM discovery_schedules")
        if cursor.fetchone()[0] == 0:
            now_t = time.time()
            schedules = [
                ("Multi-Domain Telegram Broadcast (Movies, GitHub, APIs, News)", "all", "telegram_broadcast", "10m", "active", now_t, now_t + 600, 5, "Success"),
                ("Live News & Critical System Alerts Monitor", "all_news", "news_monitor", "5m", "active", now_t, now_t + 300, 3, "Success"),
                ("Amazon Price Watch Live Monitor", "B0G6DVB6DG", "amazon_price_watch", "10m", "active", now_t, now_t + 600, 1, "Success"),
                ("Data Engineering Auto-Ingestion Scan", "data_ingestion", "data_ingestion", "10m", "active", now_t, now_t + 600, 3, "Success"),
                ("Free AI APIs Monitor", "free AI API developer tier", "free_api", "6h", "active", now_t, now_t + 21600, 8, "Completed"),
                ("Marathi Speech & Voice Projects", "marathi speech voice recognition github", "github_project", "daily", "active", now_t, now_t + 86400, 4, "Completed"),
                ("Data Engineering & ETL Tools", "python etl snowflake pipeline", "github_project", "daily", "active", now_t, now_t + 86400, 6, "Completed")
            ]
            cursor.executemany("""
            INSERT INTO discovery_schedules (
                task_name, query, category, frequency, status, last_run, next_run, results_count, last_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, schedules)

    # --- Free APIs CRUD ---
    def list_free_apis(self, category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM free_apis WHERE 1=1"
            params = []
            if category and category.lower() != "all":
                query += " AND category LIKE ?"
                params.append(f"%{category}%")
            if search and search.strip():
                terms = [t for t in re.findall(r'[a-zA-Z0-9_\-]+', search) if len(t) > 1]
                and_query = query
                and_params = list(params)
                for t in terms:
                    tp = f"%{t}%"
                    and_query += " AND (service_name LIKE ? OR provider_name LIKE ? OR category LIKE ? OR research_summary LIKE ? OR languages_supported LIKE ?)"
                    and_params.extend([tp, tp, tp, tp, tp])
                cursor.execute(and_query + " ORDER BY quality_score DESC, last_verified_at DESC", and_params)
                rows = cursor.fetchall()
                if rows:
                    return [dict(r) for r in rows]
                
                # Fallback to OR matching across terms
                or_clauses = []
                or_params = list(params)
                for t in terms:
                    tp = f"%{t}%"
                    or_clauses.append("(service_name LIKE ? OR provider_name LIKE ? OR category LIKE ? OR research_summary LIKE ? OR languages_supported LIKE ?)")
                    or_params.extend([tp, tp, tp, tp, tp])
                if or_clauses:
                    or_query = query + " AND (" + " OR ".join(or_clauses) + ") ORDER BY quality_score DESC, last_verified_at DESC"
                    cursor.execute(or_query, or_params)
                    return [dict(r) for r in cursor.fetchall()]
            
            cursor.execute(query + " ORDER BY quality_score DESC, last_verified_at DESC", params)
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def add_free_api(self, api_data: Dict[str, Any]) -> str:
        res_id = api_data.get("resource_id") or f"api_{int(time.time()*1000)}"
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO free_apis (
                resource_id, provider_name, service_name, category, official_url, documentation_url,
                pricing_url, registration_url, free_tier_type, free_quota, rate_limit, credit_card_required,
                phone_verification, authentication_type, commercial_use_notes, languages_supported,
                availability_status, quality_score, research_summary, last_verified_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                res_id, api_data.get("provider_name", "Open Provider"), api_data.get("service_name", "AI Service"),
                api_data.get("category", "General AI"), api_data.get("official_url", ""),
                api_data.get("documentation_url", ""), api_data.get("pricing_url", ""),
                api_data.get("registration_url", ""), api_data.get("free_tier_type", "Free Tier"),
                api_data.get("free_quota", "Documented Free Quota"), api_data.get("rate_limit", "Standard"),
                1 if api_data.get("credit_card_required") else 0, 1 if api_data.get("phone_verification") else 0,
                api_data.get("authentication_type", "API Key"), api_data.get("commercial_use_notes", ""),
                api_data.get("languages_supported", "Multilingual"), api_data.get("availability_status", "Active"),
                float(api_data.get("quality_score", 9.0)), api_data.get("research_summary", ""),
                api_data.get("last_verified_at", now), now
            ))
            conn.commit()
            return res_id

    # --- GitHub Projects CRUD ---
    def list_github_projects(self, category: Optional[str] = None, search: Optional[str] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM github_projects WHERE 1=1"
            params = []
            if category and category.lower() != "all":
                query += " AND category LIKE ?"
                params.append(f"%{category}%")
            if language and language.lower() != "all":
                query += " AND language LIKE ?"
                params.append(f"%{language}%")
            if search and search.strip():
                terms = [t for t in re.findall(r'[a-zA-Z0-9_\-]+', search) if len(t) > 1]
                for t in terms:
                    term_pattern = f"%{t}%"
                    query += " AND (name LIKE ? OR short_description LIKE ? OR category LIKE ? OR supported_languages LIKE ? OR potential_use LIKE ?)"
                    params.extend([term_pattern, term_pattern, term_pattern, term_pattern, term_pattern])
            query += " ORDER BY stars DESC, last_checked_at DESC"
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def add_github_project(self, proj_data: Dict[str, Any]) -> str:
        pid = proj_data.get("project_id") or f"proj_{int(time.time()*1000)}"
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO github_projects (
                project_id, name, repo_url, short_description, language, category, stars, forks,
                last_update_date, latest_release, license, dependencies, setup_complexity,
                local_execution_support, api_requirements, supported_languages, speech_approach,
                tts_approach, potential_use, security_notes, last_checked_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, proj_data.get("name", "GitHub Project"), proj_data.get("repo_url", ""),
                proj_data.get("short_description", ""), proj_data.get("language", "Python"),
                proj_data.get("category", "AI Tools"), int(proj_data.get("stars", 0)),
                int(proj_data.get("forks", 0)), proj_data.get("last_update_date", "2026"),
                proj_data.get("latest_release", "latest"), proj_data.get("license", "License not identified"),
                proj_data.get("dependencies", ""), proj_data.get("setup_complexity", "Medium"),
                1 if proj_data.get("local_execution_support", True) else 0,
                proj_data.get("api_requirements", "None"), proj_data.get("supported_languages", "English"),
                proj_data.get("speech_approach", ""), proj_data.get("tts_approach", ""),
                proj_data.get("potential_use", ""), proj_data.get("security_notes", "Verified repository"),
                now
            ))
            conn.commit()
            return pid

    # --- AI Research Library CRUD ---
    def list_research_library(self, category: Optional[str] = None, search: Optional[str] = None, is_favorite: Optional[bool] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM research_library WHERE 1=1"
            params = []
            if category and category.lower() != "all":
                query += " AND category = ?"
                params.append(category)
            if is_favorite is not None:
                query += " AND is_favorite = ?"
                params.append(1 if is_favorite else 0)
            if search and search.strip():
                terms = [t for t in re.findall(r'[a-zA-Z0-9_\-]+', search) if len(t) > 1]
                for t in terms:
                    term_pattern = f"%{t}%"
                    query += " AND (title LIKE ? OR summary LIKE ? OR category LIKE ? OR tags LIKE ? OR user_notes LIKE ?)"
                    params.extend([term_pattern, term_pattern, term_pattern, term_pattern, term_pattern])
            query += " ORDER BY is_favorite DESC, verified_at DESC"
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def add_research_item(self, item: Dict[str, Any]) -> str:
        res_id = item.get("resource_id") or f"res_{int(time.time()*1000)}"
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO research_library (
                resource_id, title, category, source_url, summary, technical_requirements,
                user_notes, is_favorite, tags, verified_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                res_id, item.get("title", "Research Summary"), item.get("category", "general"),
                item.get("source_url", ""), item.get("summary", ""),
                item.get("technical_requirements", ""), item.get("user_notes", ""),
                1 if item.get("is_favorite") else 0, item.get("tags", ""),
                item.get("verified_at", now), now
            ))
            conn.commit()
            return res_id

    @sqlite_retry()
    def update_research_item(self, resource_id: str, updates: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fields = []
            params = []
            for k in ["title", "summary", "technical_requirements", "user_notes", "tags", "is_favorite", "category"]:
                if k in updates:
                    fields.append(f"{k} = ?")
                    params.append(1 if (k == "is_favorite" and updates[k]) else updates[k])
            if not fields:
                return False
            fields.append("verified_at = ?")
            params.append(time.time())
            params.append(resource_id)
            cursor.execute(f"UPDATE research_library SET {', '.join(fields)} WHERE resource_id = ?", params)
            conn.commit()
            return True

    @sqlite_retry()
    def delete_research_item(self, resource_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM research_library WHERE resource_id = ?", (resource_id,))
            conn.commit()
            return True

    @sqlite_retry()
    def toggle_favorite_research(self, resource_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE research_library SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END WHERE resource_id = ?", (resource_id,))
            conn.commit()
            return True

    # --- Discovery Schedules & Live Jobs ---
    def list_discovery_schedules(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM discovery_schedules ORDER BY id ASC")
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def add_discovery_schedule(self, task_name: str, query: str, category: str, frequency: str) -> int:
        now = time.time()
        interval = 21600 if frequency == "6h" else (43200 if frequency == "12h" else 86400)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO discovery_schedules (task_name, query, category, frequency, status, last_run, next_run, results_count, last_status)
            VALUES (?, ?, ?, ?, 'active', ?, ?, 0, 'Ready')
            """, (task_name, query, category, frequency, now, now + interval))
            conn.commit()
            return cursor.lastrowid

    @sqlite_retry()
    def update_discovery_schedule_status(self, schedule_id: int, status: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE discovery_schedules SET status = ? WHERE id = ?", (status, schedule_id))
            conn.commit()
            return True

    def list_discovery_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM live_discovery_jobs ORDER BY started_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def create_discovery_job(self, job_id: str, query: str, source: str) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO live_discovery_jobs 
            (job_id, query, source, status, results_processed, new_resources, duplicates_skipped, error_message, started_at)
            VALUES (?, ?, ?, 'SEARCHING', 0, 0, 0, NULL, ?)
            """, (job_id, query, source, time.time()))
            conn.commit()
            return job_id

    @sqlite_retry()
    def update_discovery_job(self, job_id: str, status: str, processed: int = 0, new_count: int = 0, duplicates: int = 0, error: str = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE live_discovery_jobs
            SET status = ?, results_processed = ?, new_resources = ?, duplicates_skipped = ?, error_message = ?, completed_at = ?
            WHERE job_id = ?
            """, (status, processed, new_count, duplicates, error, time.time() if status in ['COMPLETED', 'FAILED'] else None, job_id))
            conn.commit()


    # --- Communication Logs CRUD ---
    @sqlite_retry()
    def add_communication_log(
        self,
        log_id: str,
        channel: str,
        recipient: str,
        content: str,
        subject: str = "",
        status: str = "draft",
        response_data: str = None,
        error_message: str = None
    ) -> str:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO communication_logs (
                id, channel, recipient, subject, content, status, response_data, error_message, created_at, sent_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id, channel, recipient, subject, content, status,
                response_data, error_message, now, now if status == "sent" else None
            ))
            conn.commit()
            return log_id

    def list_communication_logs(self, channel: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM communication_logs"
            params = []
            if channel and channel.lower() != "all":
                query += " WHERE channel = ?"
                params.append(channel.lower())
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def update_communication_log(self, log_id: str, status: str, response_data: str = None, error_message: str = None) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE communication_logs
            SET status = ?, response_data = ?, error_message = ?, sent_at = ?
            WHERE id = ?
            """, (status, response_data, error_message, time.time() if status == "sent" else None, log_id))
            conn.commit()
            return True


    # --- Amazon Price Tracker CRUD ---
    @sqlite_retry()
    def add_amazon_product(self, prod: Dict[str, Any]) -> str:
        now = time.time()
        pid = prod.get("id") or f"amz_{int(now*1000)}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO amazon_products (
                id, url, asin, title, currency, target_price, monitoring_frequency,
                latest_price, previous_price, lowest_price, highest_price, status,
                data_source, last_checked_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, prod["url"], prod.get("asin", "B000000000"), prod.get("title", "Amazon Product"),
                prod.get("currency", "INR"), prod.get("target_price"), prod.get("monitoring_frequency", "daily"),
                prod.get("latest_price"), prod.get("previous_price"), prod.get("lowest_price", prod.get("latest_price")),
                prod.get("highest_price", prod.get("latest_price")), prod.get("status", "active"),
                prod.get("data_source", "verified_catalog"), now, prod.get("created_at", now)
            ))
            conn.commit()
            return pid

    def list_amazon_products(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            q = "SELECT * FROM amazon_products"
            params = []
            if status and status.lower() != "all":
                q += " WHERE status = ?"
                params.append(status.lower())
            q += " ORDER BY created_at DESC"
            cursor.execute(q, params)
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def record_amazon_price(self, product_id: str, price: float, currency: str = "INR", data_source: str = "verified_catalog") -> Dict[str, Any]:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM amazon_products WHERE id = ?", (product_id,))
            prod = cursor.fetchone()
            if not prod:
                return {"error": "Product not found"}
            
            p_dict = dict(prod)
            prev = p_dict.get("latest_price") or price
            diff = round(price - prev, 2)
            pct = round((diff / prev * 100), 2) if prev > 0 else 0.0
            lowest = min(p_dict.get("lowest_price") or price, price)
            highest = max(p_dict.get("highest_price") or price, price)

            # Insert history observation
            cursor.execute("""
            INSERT INTO amazon_price_history (product_id, price, currency, difference, pct_change, data_source, observation_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_id, price, currency, diff, pct, data_source, now))

            # Update parent product
            cursor.execute("""
            UPDATE amazon_products
            SET latest_price = ?, previous_price = ?, lowest_price = ?, highest_price = ?, last_checked_at = ?, data_source = ?
            WHERE id = ?
            """, (price, prev, lowest, highest, now, data_source, product_id))
            conn.commit()

            return {
                "product_id": product_id,
                "latest_price": price,
                "previous_price": prev,
                "difference": diff,
                "pct_change": pct,
                "lowest_price": lowest,
                "highest_price": highest,
                "is_price_drop": diff < 0,
                "target_reached": bool(p_dict.get("target_price") and price <= p_dict["target_price"])
            }

    def get_price_history(self, product_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return self.get_amazon_price_history(product_id, limit)

    def get_amazon_price_history(self, product_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM amazon_price_history WHERE product_id = ? ORDER BY observation_time DESC LIMIT ?", (product_id, limit))
            return [dict(r) for r in cursor.fetchall()]

    # --- Job Postings & Career CRUD ---
    @sqlite_retry()
    def add_job_posting(self, job: Dict[str, Any]) -> str:
        now = time.time()
        jid = job.get("id") or f"job_{int(now*1000)}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO job_postings (
                id, title, company, location, source_url, skills_required, salary_info,
                experience_level, application_status, follow_up_date, notes, discovered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                jid, job["title"], job["company"], job.get("location", "Mumbai, Maharashtra"),
                job.get("source_url", ""), job.get("skills_required", "SQL, Python"),
                job.get("salary_info", "₹12-18 LPA"), job.get("experience_level", "Mid-Senior"),
                job.get("application_status", "discovered"), job.get("follow_up_date", ""),
                job.get("notes", ""), now
            ))
            conn.commit()
            return jid

    def list_job_postings(self, search: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            q = "SELECT * FROM job_postings WHERE 1=1"
            params = []
            if search and search.strip():
                q += " AND (title LIKE ? OR company LIKE ? OR skills_required LIKE ?)"
                s = f"%{search.strip()}%"
                params.extend([s, s, s])
            if location and location.strip():
                q += " AND location LIKE ?"
                params.append(f"%{location.strip()}%")
            q += " ORDER BY discovered_at DESC"
            cursor.execute(q, params)
            return [dict(r) for r in cursor.fetchall()]

    # --- Learning Sessions CRUD ---
    @sqlite_retry()
    def save_learning_session(self, sess: Dict[str, Any]) -> str:
        now = time.time()
        sid = sess.get("id") or f"learn_{int(now*1000)}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO learning_sessions (
                id, subject, topic, difficulty, questions_json, answers_json, score, weak_areas, status, completed_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sid, sess["subject"], sess["topic"], sess.get("difficulty", "medium"),
                json.dumps(sess.get("questions", [])), json.dumps(sess.get("answers", [])),
                int(sess.get("score", 0)), sess.get("weak_areas", ""), sess.get("status", "completed"),
                now, now
            ))
            conn.commit()
            return sid

    def list_learning_sessions(self, subject: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            q = "SELECT * FROM learning_sessions"
            params = []
            if subject and subject.lower() != "all":
                q += " WHERE subject = ?"
                params.append(subject.lower())
            q += " ORDER BY created_at DESC"
            cursor.execute(q, params)
            results = []
            for r in cursor.fetchall():
                d = dict(r)
                d["questions"] = json.loads(d["questions_json"]) if d["questions_json"] else []
                d["answers"] = json.loads(d["answers_json"]) if d["answers_json"] else []
                results.append(d)
            return results

    # --- Recovery History CRUD ---
    @sqlite_retry()
    def record_recovery_run(self, session_id: str, interrupted: int, overdue: int, recovered: int, coalesced: int, failed: int, log_summary: str) -> int:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO recovery_history (session_id, discovered_interrupted, discovered_overdue, recovered_tasks, coalesced_reminders, failed_retries, summary_log, recovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, interrupted, overdue, recovered, coalesced, failed, log_summary, now))
            conn.commit()
            return cursor.lastrowid

    def list_recovery_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recovery_history ORDER BY recovered_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    # --- Scheduled Discoveries CRUD ---
    @sqlite_retry()
    def record_discovery_issue(self, issue: Dict[str, Any]) -> str:
        now = time.time()
        iid = issue.get("id") or f"disc_{int(now*1000)}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO scheduled_discoveries (
                id, cycle_id, category, severity, title, description, evidence,
                recommended_action, status, acknowledged_at, resolved_at, detected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                iid, issue.get("cycle_id", "manual"), issue["category"], issue["severity"],
                issue["title"], issue["description"], issue.get("evidence", ""),
                issue.get("recommended_action", ""), issue.get("status", "unresolved"),
                issue.get("acknowledged_at"), issue.get("resolved_at"), issue.get("detected_at", now)
            ))
            conn.commit()
            return iid

    def list_discovery_issues(self, status: Optional[str] = None, severity: Optional[str] = None, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            q = "SELECT * FROM scheduled_discoveries WHERE 1=1"
            params = []
            if status and status != "all":
                q += " AND status = ?"
                params.append(status)
            if severity and severity != "all":
                q += " AND severity = ?"
                params.append(severity.upper())
            if category and category != "all":
                q += " AND category = ?"
                params.append(category)
            q += " ORDER BY detected_at DESC LIMIT ?"
            params.append(limit)
            cursor.execute(q, params)
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def update_discovery_issue_status(self, issue_id: str, new_status: str) -> bool:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if new_status == "resolved":
                cursor.execute("UPDATE scheduled_discoveries SET status = 'resolved', resolved_at = ? WHERE id = ?", (now, issue_id))
            elif new_status == "acknowledged":
                cursor.execute("UPDATE scheduled_discoveries SET status = 'acknowledged', acknowledged_at = ? WHERE id = ?", (now, issue_id))
            else:
                cursor.execute("UPDATE scheduled_discoveries SET status = ? WHERE id = ?", (new_status, issue_id))
            conn.commit()
            return True

    @sqlite_retry()
    def record_discovery_cycle(self, cycle: Dict[str, Any]) -> str:
        now = time.time()
        cid = cycle.get("id") or f"cycle_{int(now*1000)}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO scheduled_discovery_cycles (
                id, overall_status, duration_sec, categories_checked, total_issues,
                critical_count, warning_count, info_count, resolved_since_last,
                summary_report, telegram_sent, telegram_error, executed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cid, cycle.get("overall_status", "HEALTHY"), cycle.get("duration_sec", 0.0),
                json.dumps(cycle.get("categories_checked", [])), cycle.get("total_issues", 0),
                cycle.get("critical_count", 0), cycle.get("warning_count", 0),
                cycle.get("info_count", 0), cycle.get("resolved_since_last", 0),
                cycle.get("summary_report", ""), 1 if cycle.get("telegram_sent") else 0,
                cycle.get("telegram_error"), cycle.get("executed_at", now)
            ))
            conn.commit()
            return cid

    def list_discovery_cycles(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scheduled_discovery_cycles ORDER BY executed_at DESC LIMIT ?", (limit,))
            res = []
            for r in cursor.fetchall():
                d = dict(r)
                d["categories_checked"] = json.loads(d["categories_checked"]) if d["categories_checked"] else []
                res.append(d)
            return res

    # --- Notification History CRUD ---
    @sqlite_retry()
    def record_notification(self, notif: Dict[str, Any]) -> str:
        now = time.time()
        nid = notif.get("id") or f"notif_{int(now*1000)}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO notification_history (
                id, notification_type, channel, recipient, title, content, status, retry_count, error_message, cycle_id, created_at, sent_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nid, notif.get("notification_type", "hourly_summary"), notif.get("channel", "telegram"),
                notif.get("recipient", ""), notif.get("title", "Notification"), notif.get("content", ""),
                notif.get("status", "sent"), notif.get("retry_count", 0), notif.get("error_message"),
                notif.get("cycle_id"), notif.get("created_at", now), notif.get("sent_at", now)
            ))
            conn.commit()
            return nid

    def list_notification_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notification_history ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def update_notification_status(self, notif_id: str, status: str, error_message: str = None) -> bool:
        now = time.time()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE notification_history
            SET status = ?, retry_count = retry_count + 1, error_message = ?, sent_at = CASE WHEN ? = 'sent' THEN ? ELSE sent_at END
            WHERE id = ?
            """, (status, error_message, status, now, notif_id))
            conn.commit()
            return True

    # --- Storage Measurement History CRUD ---
    @sqlite_retry()
    def record_storage_measurement(self, category: str, path: str, size_bytes: int, file_count: int):
        now = time.time()
        date_str = time.strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO storage_measurements (measurement_date, category, path, size_bytes, file_count, measured_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, category, path, size_bytes, file_count, now))
            conn.commit()

    def get_storage_trends(self, limit_days: int = 14) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT measurement_date, category, SUM(size_bytes) as total_size_bytes, SUM(file_count) as total_files
            FROM storage_measurements
            GROUP BY measurement_date, category
            ORDER BY measurement_date DESC
            LIMIT ?
            """, (limit_days * 12,))
            return [dict(r) for r in cursor.fetchall()]


    # --- Task Scheduler Operations ---
    @sqlite_retry()
    def create_automation_task(self, task_data: Dict[str, Any]) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            tid = task_data.get("id") or f"task_{int(time.time()*1000)}"
            now = time.time()
            cursor.execute("""
            INSERT OR REPLACE INTO scheduled_automation_tasks (
                id, name, description, task_type, script_content, file_path, db_connection,
                schedule_type, recurrence_expr, start_time, end_time, timezone, timeout_sec,
                retry_policy, working_dir, env_vars, notification_pref, is_enabled, is_paused,
                status, next_run_at, last_run_at, last_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tid,
                task_data.get("name", "Untitled Automation Task"),
                task_data.get("description", ""),
                task_data.get("task_type", "python"),
                task_data.get("script_content", ""),
                task_data.get("file_path", ""),
                task_data.get("db_connection", ""),
                task_data.get("schedule_type", "daily"),
                task_data.get("recurrence_expr", ""),
                task_data.get("start_time", ""),
                task_data.get("end_time", ""),
                task_data.get("timezone", "Asia/Kolkata"),
                task_data.get("timeout_sec", 300),
                json.dumps(task_data.get("retry_policy", {"max_retries": 2, "retry_interval_sec": 60})),
                task_data.get("working_dir", ""),
                json.dumps(task_data.get("env_vars", {})),
                json.dumps(task_data.get("notification_pref", {"email": True, "telegram": True})),
                1 if task_data.get("is_enabled", True) else 0,
                1 if task_data.get("is_paused", False) else 0,
                task_data.get("status", "Ready"),
                task_data.get("next_run_at", ""),
                task_data.get("last_run_at", ""),
                task_data.get("last_status", ""),
                task_data.get("created_at", now),
                now
            ))
            conn.commit()
            return tid

    def get_automation_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scheduled_automation_tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            d = dict(row)
            d["retry_policy"] = json.loads(d["retry_policy"]) if d.get("retry_policy") else {}
            d["env_vars"] = json.loads(d["env_vars"]) if d.get("env_vars") else {}
            d["notification_pref"] = json.loads(d["notification_pref"]) if d.get("notification_pref") else {}
            return d

    def list_automation_tasks(self, filter_status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if filter_status:
                cursor.execute("SELECT * FROM scheduled_automation_tasks WHERE status = ? ORDER BY created_at DESC", (filter_status,))
            else:
                cursor.execute("SELECT * FROM scheduled_automation_tasks ORDER BY created_at DESC")
            results = []
            for r in cursor.fetchall():
                d = dict(r)
                d["retry_policy"] = json.loads(d["retry_policy"]) if d.get("retry_policy") else {}
                d["env_vars"] = json.loads(d["env_vars"]) if d.get("env_vars") else {}
                d["notification_pref"] = json.loads(d["notification_pref"]) if d.get("notification_pref") else {}
                results.append(d)
            return results

    @sqlite_retry()
    def update_automation_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            for k, v in updates.items():
                if k in ["retry_policy", "env_vars", "notification_pref"]:
                    v = json.dumps(v)
                fields.append(f"{k} = ?")
                values.append(v)
            if not fields:
                return True
            fields.append("updated_at = ?")
            values.append(time.time())
            values.append(task_id)
            cursor.execute(f"UPDATE scheduled_automation_tasks SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
            return cursor.rowcount > 0

    @sqlite_retry()
    def delete_automation_task(self, task_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scheduled_automation_tasks WHERE id = ?", (task_id,))
            cursor.execute("DELETE FROM task_execution_runs WHERE task_id = ?", (task_id,))
            conn.commit()
            return True

    @sqlite_retry()
    def record_task_run(self, run_data: Dict[str, Any]) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            rid = run_data.get("run_id") or f"run_{int(time.time()*1000)}"
            cursor.execute("""
            INSERT OR REPLACE INTO task_execution_runs (
                run_id, task_id, task_name, trigger_type, start_time, end_time,
                duration_sec, status, exit_code, stdout, stderr, error_details, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rid,
                run_data.get("task_id", ""),
                run_data.get("task_name", ""),
                run_data.get("trigger_type", "Scheduled"),
                run_data.get("start_time", ""),
                run_data.get("end_time", ""),
                run_data.get("duration_sec", 0.0),
                run_data.get("status", "Running"),
                run_data.get("exit_code", 0),
                run_data.get("stdout", ""),
                run_data.get("stderr", ""),
                run_data.get("error_details", ""),
                time.time()
            ))
            conn.commit()
            return rid

    @sqlite_retry()
    def update_task_run(self, run_id: str, updates: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            for k, v in updates.items():
                fields.append(f"{k} = ?")
                values.append(v)
            if not fields:
                return True
            values.append(run_id)
            cursor.execute(f"UPDATE task_execution_runs SET {', '.join(fields)} WHERE run_id = ?", values)
            conn.commit()
            return cursor.rowcount > 0

    def list_task_runs(self, task_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if task_id:
                cursor.execute("SELECT * FROM task_execution_runs WHERE task_id = ? ORDER BY created_at DESC LIMIT ?", (task_id, limit))
            else:
                cursor.execute("SELECT * FROM task_execution_runs ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    def get_task_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM task_execution_runs WHERE run_id = ?", (run_id,))
            r = cursor.fetchone()
            return dict(r) if r else None

    # --- News Articles Operations ---
    @sqlite_retry()
    def save_news_article(self, article: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            aid = article.get("article_id") or f"news_{int(time.time()*1000)}_{abs(hash(article.get('url','')))%100000}"
            cursor.execute("""
            INSERT OR IGNORE INTO news_articles (
                article_id, publisher, title, url, summary_en, summary_mr,
                category, importance, published_at, retrieved_at, thumbnail_url, is_new, is_notified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aid,
                article.get("publisher", "ABP Majha"),
                article.get("title", ""),
                article.get("url", ""),
                article.get("summary_en", ""),
                article.get("summary_mr", ""),
                article.get("category", "Maharashtra"),
                article.get("importance", "Normal"),
                article.get("published_at", ""),
                time.time(),
                article.get("thumbnail_url", ""),
                1 if article.get("is_new", True) else 0,
                1 if article.get("is_notified", False) else 0
            ))
            conn.commit()
            return cursor.rowcount > 0

    def list_news_articles(self, category: Optional[str] = None, publisher: Optional[str] = None, search: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM news_articles WHERE 1=1"
            params = []
            if category and category.lower() != 'all':
                query += " AND LOWER(category) = LOWER(?)"
                params.append(category)
            if publisher and publisher.lower() != 'all':
                query += " AND LOWER(publisher) = LOWER(?)"
                params.append(publisher)
            if search:
                query += " AND (title LIKE ? OR summary_en LIKE ? OR summary_mr LIKE ?)"
                p = f"%{search}%"
                params.extend([p, p, p])
            query += " ORDER BY retrieved_at DESC LIMIT ?"
            params.append(limit)
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    def get_unnotified_news_articles(self, limit: int = 5) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM news_articles WHERE is_notified = 0 AND (importance = 'Breaking' OR importance = 'High') ORDER BY retrieved_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    @sqlite_retry()
    def mark_news_article_notified(self, article_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE news_articles SET is_notified = 1, is_new = 0 WHERE article_id = ?", (article_id,))
            conn.commit()
            return True

    # --- Entertainment & Modern Lifestyle Operations ---
    @sqlite_retry()
    def save_entertainment_item(self, item: Dict[str, Any]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            iid = item.get("item_id") or f"ent_{int(time.time()*1000)}_{abs(hash(item.get('title','')))%100000}"
            cursor.execute("""
            INSERT OR REPLACE INTO entertainment_items (
                item_id, category, title, creator, description, thumbnail_url,
                media_url, source, published_at, metadata_json, is_favorite, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                iid,
                item.get("category", "Bollywood"),
                item.get("title", ""),
                item.get("creator", ""),
                item.get("description", ""),
                item.get("thumbnail_url", ""),
                item.get("media_url", ""),
                item.get("source", ""),
                item.get("published_at", ""),
                json.dumps(item.get("metadata", {})),
                1 if item.get("is_favorite", False) else 0,
                time.time()
            ))
            conn.commit()
            return True

    def list_entertainment_items(self, category: Optional[str] = None, search: Optional[str] = None, favorites_only: bool = False, limit: int = 60) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM entertainment_items WHERE 1=1"
            params = []
            if category and category.lower() != 'all':
                query += " AND LOWER(category) = LOWER(?)"
                params.append(category)
            if favorites_only:
                query += " AND is_favorite = 1"
            if search:
                query += " AND (title LIKE ? OR creator LIKE ? OR description LIKE ?)"
                p = f"%{search}%"
                params.extend([p, p, p])
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            cursor.execute(query, params)
            res = []
            for r in cursor.fetchall():
                d = dict(r)
                d["metadata"] = json.loads(d["metadata_json"]) if d.get("metadata_json") else {}
                res.append(d)
            return res

    @sqlite_retry()
    def toggle_entertainment_favorite(self, item_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE entertainment_items SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END WHERE item_id = ?", (item_id,))
            conn.commit()
            return True

    # --- Books & Reading Operations ---
    @sqlite_retry()
    def save_uploaded_book(self, book: Dict[str, Any]) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            bid = book.get("book_id") or f"book_{int(time.time()*1000)}"
            cursor.execute("""
            INSERT OR REPLACE INTO uploaded_books (
                book_id, title, author, file_path, file_type, total_pages, total_chapters,
                chapters_json, reading_progress_pct, current_chapter_idx, bookmarks_json,
                notes_json, processed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bid,
                book.get("title", "Untitled Book"),
                book.get("author", "Unknown Author"),
                book.get("file_path", ""),
                book.get("file_type", "pdf"),
                book.get("total_pages", 1),
                book.get("total_chapters", 1),
                json.dumps(book.get("chapters", [])),
                book.get("reading_progress_pct", 0.0),
                book.get("current_chapter_idx", 0),
                json.dumps(book.get("bookmarks", [])),
                json.dumps(book.get("notes", [])),
                time.time()
            ))
            conn.commit()
            return bid

    def get_uploaded_book(self, book_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM uploaded_books WHERE book_id = ?", (book_id,))
            r = cursor.fetchone()
            if not r:
                return None
            d = dict(r)
            d["chapters"] = json.loads(d["chapters_json"]) if d.get("chapters_json") else []
            d["bookmarks"] = json.loads(d["bookmarks_json"]) if d.get("bookmarks_json") else []
            d["notes"] = json.loads(d["notes_json"]) if d.get("notes_json") else []
            return d

    def list_uploaded_books(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM uploaded_books ORDER BY processed_at DESC")
            res = []
            for r in cursor.fetchall():
                d = dict(r)
                d["chapters"] = json.loads(d["chapters_json"]) if d.get("chapters_json") else []
                d["bookmarks"] = json.loads(d["bookmarks_json"]) if d.get("bookmarks_json") else []
                d["notes"] = json.loads(d["notes_json"]) if d.get("notes_json") else []
                res.append(d)
            return res

    @sqlite_retry()
    def update_book_progress(self, book_id: str, progress_pct: float, chapter_idx: int, bookmarks: Optional[List[Any]] = None, notes: Optional[List[Any]] = None) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = ["reading_progress_pct = ?", "current_chapter_idx = ?"]
            values = [progress_pct, chapter_idx]
            if bookmarks is not None:
                updates.append("bookmarks_json = ?")
                values.append(json.dumps(bookmarks))
            if notes is not None:
                updates.append("notes_json = ?")
                values.append(json.dumps(notes))
            values.append(book_id)
            cursor.execute(f"UPDATE uploaded_books SET {', '.join(updates)} WHERE book_id = ?", values)
            conn.commit()
            return True

    @sqlite_retry()
    def save_book_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            count = 0
            now = time.time()
            for c in chunks:
                cid = c.get("chunk_id") or f"chk_{int(now*1000)}_{count}"
                cursor.execute("""
                INSERT OR REPLACE INTO book_chunks (
                    chunk_id, book_id, chapter_index, chapter_title, page_number, chunk_text, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    cid,
                    c.get("book_id", ""),
                    c.get("chapter_index", 0),
                    c.get("chapter_title", ""),
                    c.get("page_number", 1),
                    c.get("chunk_text", ""),
                    now
                ))
                count += 1
            conn.commit()
            return count

    def search_book_chunks(self, book_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            words = query.lower().split()
            # Simple keyword match
            conditions = []
            params = [book_id]
            for w in words[:4]:
                conditions.append("LOWER(chunk_text) LIKE ?")
                params.append(f"%{w}%")
            cond_str = " AND ".join(conditions) if conditions else "1=1"
            params.append(limit)
            cursor.execute(f"SELECT * FROM book_chunks WHERE book_id = ? AND ({cond_str}) LIMIT ?", params)
            rows = cursor.fetchall()
            if not rows:
                cursor.execute("SELECT * FROM book_chunks WHERE book_id = ? LIMIT ?", (book_id, limit))
                rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_book_chunks(self, book_id: str, chapter_index: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if chapter_index is not None:
                cursor.execute("SELECT * FROM book_chunks WHERE book_id = ? AND chapter_index = ? ORDER BY page_number ASC LIMIT ?", (book_id, chapter_index, limit))
            else:
                cursor.execute("SELECT * FROM book_chunks WHERE book_id = ? ORDER BY chapter_index ASC, page_number ASC LIMIT ?", (book_id, limit))
            return [dict(r) for r in cursor.fetchall()]


db = DatabaseManager()
Database = DatabaseManager

# --- Integrated Credentials Vault Helper (AES-256-GCM Authenticated Encryption) ---

def _resolve_vault_master_key() -> bytes:
    """
    Resolves the 256-bit AES-GCM master encryption key.
    Key priority:
    1. Environment variable STUDIO_VAULT_KEY (base64 32-byte or SHA-256 hashed).
    2. Secure key file ~/.nano_pro_studio/vault.key (stored outside repository with 0600 permissions).
    3. Deterministic NanoPro cluster 32-byte master key (ensures Local and Render Cloud decrypt seamlessly).
    """
    env_key = os.environ.get("STUDIO_VAULT_KEY")
    if env_key:
        try:
            raw_b64 = base64.b64decode(env_key.strip().encode("utf-8"))
            if len(raw_b64) == 32:
                return raw_b64
        except Exception:
            pass
        return hashlib.sha256(env_key.encode("utf-8")).digest()

    key_dir = Path.home() / ".nano_pro_studio"
    key_file = key_dir / "vault.key"
    try:
        if key_file.exists() and key_file.is_file():
            key_data = key_file.read_bytes()
            if len(key_data) == 32:
                return key_data
            return hashlib.sha256(key_data).digest()
        else:
            key_dir.mkdir(parents=True, exist_ok=True)
            # Universal cluster 32-byte key for seamless Local & Render Cloud interoperability
            cluster_key = base64.b64decode(b"lAtCLQL91eKiorkzjKgv8c9yL9Oe4i0W7ANjfD3wvMs=")
            key_file.write_bytes(cluster_key)
            try:
                os.chmod(key_file, 0o600)
            except Exception:
                pass
            return cluster_key
    except Exception:
        return base64.b64decode(b"lAtCLQL91eKiorkzjKgv8c9yL9Oe4i0W7ANjfD3wvMs=")

def _legacy_xor_decrypt(enc_text: str) -> str:
    """Decrypts legacy XOR/SHA-256 format for backward compatibility and migration."""
    try:
        legacy_key = os.environ.get("STUDIO_VAULT_KEY", "Mangesh_AI_Studio_Master_Secret_2026_SecureKey")
        raw_b64 = base64.b64decode(enc_text.encode("utf-8"))
        key_hash = hashlib.sha256(legacy_key.encode("utf-8")).digest()
        extended_key = (key_hash * ((len(raw_b64) // len(key_hash)) + 1))[:len(raw_b64)]
        dec = bytes(a ^ b for a, b in zip(raw_b64, extended_key))
        return dec.decode("utf-8", errors="replace")
    except Exception:
        return ""

def encrypt_value(raw_text: str) -> str:
    """
    Encrypts sensitive string using authenticated AES-256-GCM.
    Produces format: 'aesgcm:' + base64(12-byte nonce + ciphertext + 16-byte tag).
    """
    if not raw_text:
        return ""
    try:
        key = _resolve_vault_master_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # Standard 96-bit nonce for AES-GCM
        ct = aesgcm.encrypt(nonce, raw_text.encode("utf-8"), None)
        return "aesgcm:" + base64.b64encode(nonce + ct).decode("utf-8")
    except Exception as e:
        log_event(f"Vault encryption error: {e}", level="ERROR", component="CredentialsVault")
        return ""

def decrypt_value(enc_text: str) -> str:
    """
    Decrypts credential secret using AES-256-GCM with resilient multi-key self-healing.
    Supports seamless backward compatibility and cross-cloud migration (Local, Render, Docker).
    """
    if not enc_text:
        return ""
    try:
        if enc_text.startswith("aesgcm:"):
            raw_b64 = base64.b64decode(enc_text[7:].encode("utf-8"))
            if len(raw_b64) < 28:
                return ""
            nonce = raw_b64[:12]
            ct = raw_b64[12:]
            
            # Candidate keys to ensure 100% decryption across Local, Render, and Docker
            candidate_keys = [
                _resolve_vault_master_key(),
                base64.b64decode(b"lAtCLQL91eKiorkzjKgv8c9yL9Oe4i0W7ANjfD3wvMs="),
                hashlib.sha256(b"mangesh_host_NanoPro_Vault_2026").digest(),
                hashlib.sha256(b"Mangesh_AI_Studio_Master_Secret_2026_SecureKey").digest()
            ]
            
            for k in candidate_keys:
                try:
                    dec = AESGCM(k).decrypt(nonce, ct, None).decode("utf-8", errors="replace")
                    if dec:
                        return dec
                except Exception:
                    continue

            return _legacy_xor_decrypt(enc_text)
        else:
            return _legacy_xor_decrypt(enc_text)
    except Exception:
        legacy = _legacy_xor_decrypt(enc_text)
        if legacy:
            return legacy
        log_event("CredentialsVault notice: Secret requires re-saving (token not decryptable with active master key).", level="WARNING", component="CredentialsVault")
        return ""

def mask_credential(val: str) -> str:
    if not val:
        return ""
    if len(val) <= 4:
        return "••••••••"
    return val[:2] + "•" * (len(val) - 4) + val[-2:]

class CredentialsVault:
    def __init__(self, ttl: float = 300.0):
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self._cache_lock = threading.RLock()
        self._ttl = ttl
        self.migrate_legacy_credentials()

    def invalidate_cache(self, key: Optional[str] = None):
        """Invalidates in-memory credential cache entries on write or deletion."""
        with self._cache_lock:
            if key:
                self._cache.pop(key, None)
            else:
                self._cache.clear()

    def clear_cache(self):
        """Clears all cached credentials."""
        self.invalidate_cache()

    def migrate_legacy_credentials(self):
        """
        Automatically inspects stored credentials and migrates any legacy XOR-encrypted
        records to AES-256-GCM authenticated encryption.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, service_name, encrypted_secret FROM credentials")
                rows = cursor.fetchall()
                migrated = 0
                for r in rows:
                    enc = r["encrypted_secret"] or ""
                    if enc and not enc.startswith("aesgcm:"):
                        plain = _legacy_xor_decrypt(enc)
                        if plain:
                            new_enc = encrypt_value(plain)
                            cursor.execute("UPDATE credentials SET encrypted_secret = ? WHERE id = ?", (new_enc, r["id"]))
                            migrated += 1
                if migrated > 0:
                    conn.commit()
                    log_event(f"Migrated {migrated} legacy credentials to AES-256-GCM authenticated encryption", component="CredentialsVault")
        except Exception as e:
            log_event(f"Credential vault migration check: {e}", level="WARNING", component="CredentialsVault")

    @sqlite_retry()
    def store_credential(
        self,
        service_name: str,
        credential_type: str,
        username: str = "",
        secret_value: str = "",
        host: str = "",
        port: str = "",
        database_name: str = "",
        email: str = "",
        mobile_number: str = "",
        additional_info: Dict[str, Any] = None
    ) -> str:
        service_name = (service_name or "").strip()
        meta = additional_info or {}
        now = time.time()

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, encrypted_secret, username, host, port, database_name, email, mobile_number, additional_metadata FROM credentials WHERE service_name = ? LIMIT 1", (service_name,))
            existing = cursor.fetchone()

            if existing:
                cred_id = existing["id"]
                # Preserve existing secret if secret_value is not provided or empty
                if not secret_value or not secret_value.strip():
                    enc_secret = existing["encrypted_secret"]
                else:
                    enc_secret = encrypt_value(secret_value.strip())

                cursor.execute("""
                UPDATE credentials SET
                    credential_type = ?,
                    username = ?,
                    encrypted_secret = ?,
                    host = ?,
                    port = ?,
                    database_name = ?,
                    email = ?,
                    mobile_number = ?,
                    additional_metadata = ?,
                    updated_at = ?
                WHERE id = ?
                """, (
                    credential_type,
                    username or existing["username"],
                    enc_secret,
                    host or existing["host"],
                    port or existing["port"],
                    database_name or existing["database_name"],
                    email or existing["email"],
                    mobile_number or existing["mobile_number"],
                    json.dumps(meta),
                    now,
                    cred_id
                ))
                conn.commit()
                self.invalidate_cache()
                log_event(f"Updated existing credential [{cred_id}] for service '{service_name}' [AES-256-GCM]", component="CredentialsVault")
                return cred_id
            else:
                cred_id = f"cred_{credential_type.lower()}_{int(now*1000)}"
                enc_secret = encrypt_value(secret_value.strip()) if secret_value else ""
                cursor.execute("""
                INSERT INTO credentials (
                    id, service_name, credential_type, username, encrypted_secret,
                    host, port, database_name, email, mobile_number, additional_metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cred_id, service_name, credential_type, username, enc_secret,
                    host, port, database_name, email, mobile_number, json.dumps(meta), now, now
                ))
                conn.commit()
                self.invalidate_cache()
                log_event(f"Stored credential [{cred_id}] for service '{service_name}' ({credential_type}) [AES-256-GCM]", component="CredentialsVault")
                return cred_id

    def add_credential(self, *args, **kwargs) -> str:
        """Alias for store_credential to satisfy standard vault interface (F10)."""
        return self.store_credential(*args, **kwargs)

    def list_credentials(self, mask: bool = True) -> List[Dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM credentials ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            result = []
            for r in rows:
                d = dict(r)
                decrypted = decrypt_value(d.get("encrypted_secret", ""))
                d["secret_value"] = mask_credential(decrypted) if mask else decrypted
                d["additional_metadata"] = json.loads(d["additional_metadata"]) if d.get("additional_metadata") else {}
                del d["encrypted_secret"]
                result.append(d)
            return result

    def get_credential(self, service_name_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves credential from in-memory cache (< 0.1ms) if present and valid.
        Falls back to indexed SQLite lookup and populates cache on cold queries.
        """
        now = time.time()
        with self._cache_lock:
            cached = self._cache.get(service_name_or_id)
            if cached:
                cached_time, cached_val = cached
                if now - cached_time < self._ttl:
                    return dict(cached_val)
                else:
                    self._cache.pop(service_name_or_id, None)

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM credentials WHERE id = ? OR service_name = ? LIMIT 1", (service_name_or_id, service_name_or_id))
            row = cursor.fetchone()
            if not row:
                return None
            d = dict(row)
            d["secret_value"] = decrypt_value(d.get("encrypted_secret", ""))
            d["additional_metadata"] = json.loads(d["additional_metadata"]) if d.get("additional_metadata") else {}
            del d["encrypted_secret"]

            with self._cache_lock:
                val_copy = dict(d)
                self._cache[d["id"]] = (now, val_copy)
                self._cache[d["service_name"]] = (now, val_copy)

            return dict(d)

    @sqlite_retry()
    def delete_credential(self, cred_id: str) -> bool:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM credentials WHERE id = ? OR service_name = ?", (cred_id, cred_id))
            conn.commit()
        self.invalidate_cache()
        log_event(f"Deleted credential [{cred_id}]", component="CredentialsVault")
        return True

credentials_vault = CredentialsVault()
