"""CI entrypoint: seed the bank source model from a GitHub Actions runner.

The free Render instance only has 512 MB and dies while the BigQuery SDK
imports, so the seed runs here instead. Credentials come from the environment;
nothing is printed except status and counts.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

REQUIRED = (
    "GCP_SERVICE_ACCOUNT_JSON",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_S3_BUCKET",
)


def _verify() -> dict:
    """Row counts per seeded table straight from BigQuery."""
    from app.core import bank_core_model as model
    from app.core.live_catalog import _bigquery_client

    client, _ = _bigquery_client()
    project = client.project
    counts: dict = {}
    for schema in (model.BASE_SCHEMA, model.CORE_SCHEMA, model.REF_SCHEMA, model.CDC_SCHEMA):
        query = (
            "SELECT table_name, row_count FROM `{0}.{1}.__TABLES__` "
            "ORDER BY table_name".format(project, schema)
        )
        try:
            rows = list(client.query(query).result())
        except Exception as exc:  # noqa: BLE001
            counts[schema] = {"error": str(exc)[:200]}
            continue
        counts[schema] = {row["table_name"]: int(row["row_count"]) for row in rows}
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100)
    parser.add_argument("--no-sftp", action="store_true")
    parser.add_argument("--no-chain", action="store_true")
    parser.add_argument("--no-verify", action="store_true")
    args = parser.parse_args()

    missing = [name for name in REQUIRED if not (os.environ.get(name) or "").strip()]
    if missing:
        print("MISSING_SECRETS=" + ",".join(missing))
        return 2

    if args.no_chain:
        os.environ["NANOPRO_BQ_AUTO_EXPORT"] = "0"

    from app.core import bank_core_seed

    result = bank_core_seed.seed(args.rows, not args.no_sftp)
    summary = {
        key: result.get(key)
        for key in ("status", "batch_id", "tables", "rows", "errors", "steps", "sftp", "export", "raw")
    }
    print("SEED_RESULT=" + json.dumps(summary, default=str)[:4000])

    if not args.no_verify:
        print("COUNT_RESULT=" + json.dumps(_verify(), default=str)[:6000])

    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
