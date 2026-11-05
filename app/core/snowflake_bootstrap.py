"""
One-click Snowflake structure setup for NanoPro Data Modeling by AI.

Creates the warehouse, database, medallion/pipeline schemas, an empty
SALES_ORDERS table, an empty PIPELINE_RUNS table and the region revenue view.
No rows are inserted: every number reported here is read back from the live
account, so the workspace never shows demo data.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.core import snowflake_client
from app.core.logger import log_event

DATABASE = "BANK_DB"
SALES_SCHEMA = "SALES"
PIPELINE_SCHEMA = "L0_STAGING"
SCHEMAS = [PIPELINE_SCHEMA, "L1_HARMONIZED", "L2_CURATED", SALES_SCHEMA]


def ensure_structure(connection_name: str = snowflake_client.CONNECTION_NAME) -> Dict[str, Any]:
    """Creates the warehouse/database/schemas/tables/view. Safe to run repeatedly."""
    steps: List[Dict[str, str]] = []
    conn = snowflake_client.open_connection(database=None, schema=None, warehouse=None)
    cur = conn.cursor()

    def run(label: str, sql: str) -> None:
        cur.execute(sql)
        steps.append({"step": label, "status": "ok"})

    try:
        run(
            "Create warehouse COMPUTE_WH",
            "CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH WITH WAREHOUSE_SIZE = 'XSMALL' "
            "AUTO_SUSPEND = 60 AUTO_RESUME = TRUE",
        )
        run("Use warehouse", "USE WAREHOUSE COMPUTE_WH")
        run(f"Create database {DATABASE}", f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
        run("Use database", f"USE DATABASE {DATABASE}")
        for schema in SCHEMAS:
            run(f"Create schema {schema}", f"CREATE SCHEMA IF NOT EXISTS {DATABASE}.{schema}")
        run("Use schema", f"USE SCHEMA {DATABASE}.{SALES_SCHEMA}")
        run(
            "Create table SALES_ORDERS",
            f"""CREATE TABLE IF NOT EXISTS {DATABASE}.{SALES_SCHEMA}.SALES_ORDERS (
                ORDER_ID NUMBER AUTOINCREMENT,
                CUSTOMER_NAME VARCHAR(120),
                CITY VARCHAR(80),
                REGION VARCHAR(40),
                AMOUNT NUMBER(12,2),
                ORDER_DATE DATE
            )""",
        )
        run(
            "Create view V_REGION_REVENUE",
            f"""CREATE OR REPLACE VIEW {DATABASE}.{SALES_SCHEMA}.V_REGION_REVENUE AS
                SELECT REGION, COUNT(*) AS ORDERS, SUM(AMOUNT) AS REVENUE
                FROM {DATABASE}.{SALES_SCHEMA}.SALES_ORDERS
                GROUP BY REGION""",
        )
        run(
            "Create pipeline table PIPELINE_RUNS",
            f"""CREATE TABLE IF NOT EXISTS {DATABASE}.{PIPELINE_SCHEMA}.PIPELINE_RUNS (
                RUN_ID NUMBER AUTOINCREMENT,
                PIPELINE_NAME VARCHAR(120),
                STATUS VARCHAR(30),
                ROWS_LOADED NUMBER,
                STARTED_AT TIMESTAMP_NTZ
            )""",
        )
        run(
            "Create pipeline table PIPELINE_SCHEDULE",
            f"""CREATE TABLE IF NOT EXISTS {DATABASE}.{PIPELINE_SCHEMA}.PIPELINE_SCHEDULE (
                PIPELINE_NAME VARCHAR(120),
                SOURCE_OBJECT VARCHAR(400),
                TARGET_SCHEMA VARCHAR(120),
                CRON_EXPRESSION VARCHAR(60),
                IS_ACTIVE BOOLEAN,
                UPDATED_AT TIMESTAMP_NTZ
            )""",
        )

        cur.execute(f"SELECT COUNT(*) FROM {DATABASE}.{SALES_SCHEMA}.SALES_ORDERS")
        orders = int(cur.fetchone()[0] or 0)
        cur.execute(f"SELECT COUNT(*) FROM {DATABASE}.{PIPELINE_SCHEMA}.PIPELINE_RUNS")
        runs = int(cur.fetchone()[0] or 0)
        cur.execute(f"SELECT COUNT(*) FROM {DATABASE}.{PIPELINE_SCHEMA}.PIPELINE_SCHEDULE")
        schedules = int(cur.fetchone()[0] or 0)
        cur.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE()")
        session = cur.fetchone()
        conn.commit()
    finally:
        try:
            cur.close()
        finally:
            conn.close()

    snowflake_client.clear_catalog_cache()
    log_event(
        f"Snowflake structure ready on {DATABASE}: SALES_ORDERS={orders}, "
        f"PIPELINE_RUNS={runs}, PIPELINE_SCHEDULE={schedules}",
        component="SnowflakeBootstrap",
    )
    return {
        "status": "success",
        "account": session[0] if session else "",
        "user": session[1] if session else "",
        "role": session[2] if session else "",
        "database": DATABASE,
        "sales_schema": SALES_SCHEMA,
        "pipeline_schema": PIPELINE_SCHEMA,
        "schemas": SCHEMAS,
        "table": f"{DATABASE}.{SALES_SCHEMA}.SALES_ORDERS",
        "tables": [
            f"{DATABASE}.{SALES_SCHEMA}.SALES_ORDERS",
            f"{DATABASE}.{SALES_SCHEMA}.V_REGION_REVENUE",
            f"{DATABASE}.{PIPELINE_SCHEMA}.PIPELINE_RUNS",
            f"{DATABASE}.{PIPELINE_SCHEMA}.PIPELINE_SCHEDULE",
        ],
        "row_counts": {
            f"{DATABASE}.{SALES_SCHEMA}.SALES_ORDERS": orders,
            f"{DATABASE}.{PIPELINE_SCHEMA}.PIPELINE_RUNS": runs,
            f"{DATABASE}.{PIPELINE_SCHEMA}.PIPELINE_SCHEDULE": schedules,
        },
        "total_orders": orders,
        "steps": steps,
        "preview_columns": [],
        "preview_rows": [],
    }
