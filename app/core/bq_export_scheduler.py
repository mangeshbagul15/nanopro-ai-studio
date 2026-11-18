"""Periodic BigQuery -> AWS export while the app is awake.

The external scheduler (EventBridge / cron-job.org) only wakes the host; this
loop is what keeps the bronze lake current without anyone pressing a button.
"""
from __future__ import annotations

import os
import threading
import time

from app.core.logger import log_event

_STARTED = threading.Event()
DEFAULT_INTERVAL_MIN = 30


def _enabled() -> bool:
    return (os.environ.get("NANOPRO_BQ_AUTO_EXPORT") or "1").strip().lower() not in ("0", "false", "no", "off")


def _interval_seconds() -> int:
    try:
        minutes = int(os.environ.get("NANOPRO_BQ_EXPORT_INTERVAL_MIN") or DEFAULT_INTERVAL_MIN)
    except ValueError:
        minutes = DEFAULT_INTERVAL_MIN
    return max(5, minutes) * 60


def _loop() -> None:
    time.sleep(90)  # let the boot sequence finish first
    while True:
        if _enabled():
            try:
                from app.core.bigquery_aws_pipeline import run_pipeline

                result = run_pipeline()
                log_event(
                    f"[BQExport] {result.get('status')}: {result.get('summary')}",
                    component="BQExportScheduler",
                )
            except Exception as exc:
                log_event(f"[BQExport] run failed: {exc}", level="WARNING", component="BQExportScheduler")
        time.sleep(_interval_seconds())


def start() -> None:
    if not _enabled() or _STARTED.is_set():
        return
    _STARTED.set()
    threading.Thread(target=_loop, daemon=True, name="bq-export-scheduler").start()
    log_event(f"[BQExport] scheduler armed, every {_interval_seconds() // 60} minutes.", component="BQExportScheduler")
