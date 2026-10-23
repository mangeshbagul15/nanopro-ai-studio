"""
NanoPro AI Studio - ETL Live Data Streamer
==========================================
Continuously generates live random banking data for all 9 ETL projects
and loads into Neon PostgreSQL L0 tables every N seconds.

Projects: Credit Card, AML, ALM, ADF CIMS, CBS, UPI, UCIC, Bureau Mart, Data Lake
Target: Neon PostgreSQL L0 tables (live streaming)
Interval: 30 seconds (configurable)
"""

from __future__ import annotations
import os
import threading
import time
import datetime
from typing import Optional

from app.core.logger import log_event
from app.core.config import TELEGRAM_CHAT_ID

IST_OFFSET = 5.5

def _ist_now() -> str:
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=IST_OFFSET)
    return now.strftime("%Y-%m-%d %H:%M:%S")

def _today() -> str:
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=IST_OFFSET)
    return now.strftime("%Y-%m-%d")


class ETLLiveStreamer:
    """
    Background thread that streams live random data into Neon L0 tables.
    Interval: 30 seconds — inserts 5-10 new records per project per cycle.
    Auto-starts on boot. Runs forever until stopped.
    """

    DEFAULT_INTERVAL = 30   # seconds between batches
    ROWS_PER_BATCH   = 8    # records per project per cycle

    def __init__(self):
        self._stop     = threading.Event()
        self._thread:  Optional[threading.Thread] = None
        self._interval = self.DEFAULT_INTERVAL
        self._stats    = {}   # project_key -> {total_inserted, last_insert}
        self._lock     = threading.Lock()

    def start(self, interval: int = DEFAULT_INTERVAL):
        if self._thread and self._thread.is_alive():
            log_event("ETL Live Streamer already running", component="ETLLiveStream")
            return
        self._interval = interval
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="ETLLiveStreamer"
        )
        self._thread.start()
        log_event(f"ETL Live Streamer started (interval={interval}s, {self.ROWS_PER_BATCH} rows/project/cycle)", component="ETLLiveStream")

    def stop(self):
        self._stop.set()
        log_event("ETL Live Streamer stopped", component="ETLLiveStream")

    def get_stats(self) -> dict:
        with self._lock:
            return dict(self._stats)

    def _loop(self):
        """Main streaming loop — runs every N seconds."""
        # Wait for server to fully boot before first insert
        self._stop.wait(15)

        while not self._stop.is_set():
            try:
                self._stream_one_cycle()
            except Exception as e:
                log_event(f"ETL Live Streamer cycle error: {e}", level="WARNING", component="ETLLiveStream")
            self._stop.wait(self._interval)

    def _stream_one_cycle(self):
        """Insert ROWS_PER_BATCH records into each project's Neon L0 table."""
        neon_url = os.environ.get("NEON_DATABASE_URL", "")
        if not neon_url:
            return

        try:
            import psycopg2
        except ImportError:
            return

        from app.core.etl_automation_pipeline import PROJECTS, generate_sample_data

        conn = None
        try:
            conn = psycopg2.connect(neon_url, connect_timeout=10)
            conn.autocommit = True
            cur  = conn.cursor()

            for key, p in PROJECTS.items():
                try:
                    records = generate_sample_data(key, self.ROWS_PER_BATCH)
                    if not records:
                        continue

                    table = p["neon_l0"]
                    cols  = list(records[0].keys())

                    # Ensure table exists
                    col_defs = ", ".join([f'"{c}" TEXT' for c in cols])
                    cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')

                    # Add metadata columns if missing
                    for mc in ["date_of_generation", "report_date", "execution_date", "stream_ts"]:
                        try:
                            cur.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "{mc}" TEXT')
                        except Exception:
                            pass

                    # Insert records
                    col_str = ", ".join([f'"{c}"' for c in cols])
                    phs     = ", ".join(["%s"] * len(cols))
                    for r in records:
                        cur.execute(
                            f'INSERT INTO "{table}" ({col_str}) VALUES ({phs})',
                            [str(r.get(c, "")) for c in cols]
                        )

                    with self._lock:
                        if key not in self._stats:
                            self._stats[key] = {"total_inserted": 0, "last_insert": None, "table": table}
                        self._stats[key]["total_inserted"] += len(records)
                        self._stats[key]["last_insert"]     = _ist_now()

                except Exception as e:
                    log_event(f"[LiveStream] {key} insert error: {e}", level="WARNING", component="ETLLiveStream")

            cur.close()
        except Exception as e:
            log_event(f"[LiveStream] Neon connection error: {e}", level="WARNING", component="ETLLiveStream")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass


# Module-level singleton
etl_live_streamer = ETLLiveStreamer()
