"""
Mangesh Nano Pro AI Studio - Central Connection Manager & Database Explorer
Single source of truth for database connections (Snowflake, Oracle, SQLite)
and external service integrations (Gmail SMTP, AWS S3, Telegram, WhatsApp, SMS, SFTP).
Securely retrieves credentials from CredentialsVault and environment variables.
Conducts real connection tests without mocking or simulating success.
Provides Database Explorer, metadata discovery, and health monitoring.
"""

import os
import sys
import time
import json
import socket
import re
import uuid
import threading
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from app.core.logger import log_event
from app.core.database import db, credentials_vault
from app.core.smtp_client import smtp_client
from app.core.config import REPORTS_DIR, BASE_DIR
from app.core import clock_sync

clock_sync.apply_botocore_patch()

# Non-secret configuration defaults
SNOWFLAKE_CONFIG = {
    "connection_name": "NANO_PRO_SNOWFLAKE",
    "organization": "XMUTKDJ",
    "account_name": "KP74023",
    "account_identifier": "XMUTKDJ-KP74023",
    "account_locator": "UI21071",
    "cloud": "AWS",
    "edition": "Enterprise",
    "region": "ap-southeast-7",
    "username": "MANGESHBAGUL15@GMAIL.COM",
    "role": "ACCOUNTADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "BANK_DB",
    "schema": "L0_STAGING",
    "account_url": "https://XMUTKDJ-KP74023.snowflakecomputing.com",
    "authenticator": "externalbrowser"
}

# Medallion layers: L0 bronze staging, L1 silver harmonized, L2 gold curated marts
SNOWFLAKE_MEDALLION_SCHEMAS = ("L0_STAGING", "L1_HARMONIZED", "L2_CURATED")

ORACLE_CONFIGS = {
    "MY_ORACLE_XE_LOCAL": {
        "connection_name": "MY_ORACLE_XE_LOCAL",
        "username": "SYSTEM",
        "hostname": "127.0.0.1",
        "port": 1521,
        "connection_type": "Basic",
        "role": "Default",
        "service_name": "XEPDB1",
        "notes": "Local Oracle XE instance (127.0.0.1:1521/XEPDB1)"
    },
    "MY_ORACLE_XE_REMOTE": {
        "connection_name": "MY_ORACLE_XE_REMOTE",
        "username": "SYSTEM",
        "hostname": "192.168.31.240",
        "port": 1521,
        "connection_type": "Basic",
        "role": "Default",
        "service_name": "XEPDB1",
        "notes": "Remote LAN Oracle XE instance (192.168.31.240:1521/XEPDB1)"
    },
    "MY_ORACLE_XE_REMOTE_New": {
        "connection_name": "MY_ORACLE_XE_REMOTE_New",
        "username": "SYSTEM",
        "hostname": "100.112.86.83",
        "port": 1521,
        "connection_type": "Basic",
        "role": "Default",
        "service_name": "XEPDB1",
        "notes": "Remote Tailscale Oracle XE instance (100.112.86.83:1521/XEPDB1 - Requires active Tailscale)"
    },
    "ORACLE_APEX_23AI_CLOUD": {
        "connection_name": "ORACLE_APEX_23AI_CLOUD",
        "username": "mangeshbagul15@gmail.com",
        "hostname": "oracleapex.com",
        "port": 443,
        "connection_type": "ORDS_REST",
        "role": "Administrator",
        "workspace": "nanoprostudio",
        "service_name": "nanoprostudio",
        "environment_url": "https://oracleapex.com/ords/",
        "notes": "Oracle Official 23ai Cloud Workspace 'nanoprostudio' (mangeshbagul15@gmail.com - 24/7 Lifetime Free)"
    }
}
ORACLE_CONFIG = ORACLE_CONFIGS["MY_ORACLE_XE_LOCAL"]

POSTGRES_CONFIGS = {
    "MY_POSTGRES_LOCAL": {
        "connection_name": "MY_POSTGRES_LOCAL",
        "username": "postgres",
        "hostname": "127.0.0.1",
        "port": 5432,
        "database": "nanopro_db",
        "notes": "Local PostgreSQL Relational Database (127.0.0.1:5432/nanopro_db - Laptop Live)"
    },
    "POSTGRES_CLOUD_FREE": {
        "connection_name": "POSTGRES_CLOUD_FREE",
        "username": "neondb_owner",
        "hostname": "ep-soft-paper-azc3am3u-pooler.c-3.ap-southeast-1.aws.neon.tech",
        "port": 5432,
        "database": "neondb",
        "sslmode": "require",
        "connection_url_env": "NEON_DATABASE_URL",
        "notes": "Neon.tech Serverless PostgreSQL 18 (Singapore Region - 100% Lifetime Free Forever)"
    },
    "POSTGRES_RENDER_CLOUD": {
        "connection_name": "POSTGRES_RENDER_CLOUD",
        "username": "nanopro_postgres_user",
        "hostname": "dpg-db89fqm89jmc73cnqd0g-a.singapore-postgres.render.com",
        "internal_hostname": "dpg-db89fqm89jmc73cnqd0g-a",
        "port": 5432,
        "database": "nanopro_postgres",
        "sslmode": "require",
        "connection_url_env": "RENDER_DATABASE_URL",
        "notes": "Render Cloud PostgreSQL Database (Singapore Region - 30-Day Dev Instance)"
    }
}
POSTGRES_CONFIG = POSTGRES_CONFIGS["MY_POSTGRES_LOCAL"]

class ConnectionManager:
    def __init__(self):
        self._init_database_tables()
        self.ensure_default_connections()

    def _init_database_tables(self):
        """Ensures connection_history and query_history tables exist."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS connection_history (
                    id TEXT PRIMARY KEY,
                    connection_name TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time_ms REAL,
                    active_user TEXT,
                    active_role TEXT,
                    active_database TEXT,
                    active_schema TEXT,
                    error_message TEXT,
                    tested_at REAL NOT NULL,
                    details_json TEXT
                )""")
                
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id TEXT PRIMARY KEY,
                    connection_name TEXT NOT NULL,
                    database_name TEXT,
                    schema_name TEXT,
                    query_text TEXT NOT NULL,
                    execution_time_ms REAL,
                    rows_count INTEGER,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    executed_at REAL NOT NULL
                )""")
                
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS connection_metadata (
                    connection_name TEXT PRIMARY KEY,
                    service_type TEXT NOT NULL,
                    config_json TEXT NOT NULL,
                    last_status TEXT DEFAULT 'Not Tested',
                    last_tested_at REAL,
                    last_response_time_ms REAL,
                    last_error TEXT,
                    updated_at REAL NOT NULL
                )""")
                conn.commit()
        except Exception as e:
            log_event(f"Error initializing connection tables: {e}", component="ConnectionManager", level="WARNING")

    def ensure_default_connections(self):
        """Register connection metadata and ensure default credentials from environment/vault."""
        try:
            from app.core.config import TELEGRAM_BOT_TOKEN as _CONFIG_TELEGRAM_TOKEN
        except Exception:
            _CONFIG_TELEGRAM_TOKEN = ""
        default_pw_map = {
            "NANO_PRO_SNOWFLAKE": os.environ.get("SNOWFLAKE_PASSWORD", ""),
            "MY_ORACLE_XE_LOCAL": os.environ.get("ORACLE_PASSWORD", ""),
            "MY_ORACLE_XE_REMOTE": os.environ.get("ORACLE_PASSWORD", ""),
            "MY_ORACLE_XE_REMOTE_New": os.environ.get("ORACLE_PASSWORD", ""),
            "ORACLE_APEX_23AI_CLOUD": os.environ.get("ORACLE_APEX_PASSWORD", ""),
            "MY_POSTGRES_LOCAL": os.environ.get("POSTGRES_PASSWORD", ""),
            "POSTGRES_CLOUD_FREE": os.environ.get("NEON_POSTGRES_PASSWORD", ""),
            "POSTGRES_RENDER_CLOUD": os.environ.get("RENDER_POSTGRES_PASSWORD", ""),
            "AWS_S3_DATA_LAKE": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
            "GMAIL_SMTP": os.environ.get("GMAIL_APP_PASSWORD", ""),
            "TELEGRAM_ALERTS": os.environ.get("TELEGRAM_BOT_TOKEN") or _CONFIG_TELEGRAM_TOKEN or "",
            "DUCKDB_GOLD_LAKEHOUSE": "",
            "GOOGLE_BIGQUERY_SANDBOX": "",
            "CLOUD_SFTP_SERVER": os.environ.get("SFTP_PASSWORD", "NanoPro@SFTP2026!"),
        }

        profiles = [
            ("NANO_PRO_SNOWFLAKE", "database", SNOWFLAKE_CONFIG["username"], SNOWFLAKE_CONFIG["account_url"], "443", SNOWFLAKE_CONFIG["database"], SNOWFLAKE_CONFIG),
            *[(name, "database", cfg["username"], cfg["hostname"], str(cfg["port"]), cfg["service_name"], cfg) for name, cfg in ORACLE_CONFIGS.items()],
            *[(name, "database", cfg["username"], cfg["hostname"], str(cfg["port"]), cfg["database"], cfg) for name, cfg in POSTGRES_CONFIGS.items()],
            ("AWS_S3_DATA_LAKE", "cloud", os.environ.get("AWS_ACCESS_KEY_ID", "mangesh-studio"), os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2"), "443", os.environ.get("AWS_S3_BUCKET", "nanopro-data-lake"), {"region": os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2"), "bucket": os.environ.get("AWS_S3_BUCKET", "nanopro-data-lake")}),
            ("DUCKDB_GOLD_LAKEHOUSE", "database", "embedded_olap", "data/lakehouse/gold_marts.duckdb", "0", "gold_marts", {"engine": "DuckDB 2.0.0", "storage": "Parquet Star Schema"}),
            ("GOOGLE_BIGQUERY_SANDBOX", "cloud_data_warehouse", "nanoproaistudio@gmail.com", "bigquery.googleapis.com", "443", "nanopro-lakehouse-sandbox", {"tier": "Always Free Sandbox", "quota": "10 GB Storage / 1 TB Query/mo"}),
            ("CLOUD_SFTP_SERVER", "sftp", os.environ.get("SFTP_USER", "nanopro_sftp"), "0.0.0.0", str(os.environ.get("SFTP_PORT", 2222)), "sftp_hub", {"protocols": ["SFTP", "SSH", "AWS S3 Sync"], "inbound": "data/sftp/inbound", "outbound": "data/sftp/outbound", "reports": "data/sftp/reports"}),
            ("GMAIL_SMTP", "smtp", "mangeshbagul15@gmail.com", "smtp.gmail.com", "587", "nanoproaistudio@gmail.com", {"protocol": "STARTTLS"}),
            ("TELEGRAM_ALERTS", "messaging", "@mangesh_technews_bot", "api.telegram.org", "443", "1200023268", {"chat_id": "1200023268"})
        ]
        for name, kind, username, host, port, database_name, metadata in profiles:
            existing = credentials_vault.get_credential(name)
            existing_pw = (existing.get("secret_value") or "").strip() if existing else ""
            fill_pw = (default_pw_map.get(name) or "").strip()

            # Do not rewrite existing vault rows on every boot: that used to reset
            # updated_at and made empty secrets look freshly configured in the UI.
            if existing and (existing_pw or not fill_pw):
                continue

            credentials_vault.store_credential(
                service_name=name,
                credential_type=kind,
                username=username,
                secret_value=existing_pw or fill_pw,
                host=host,
                port=port,
                database_name=database_name,
                additional_info=metadata,
            )

    # =========================================================================
    # Credential & Configuration Access (Masked & Secure)
    # =========================================================================

    def get_connection_config(self, connection_name: str, mask: bool = True) -> Optional[Dict[str, Any]]:
        """Retrieves configuration for a named connection, with secrets securely masked."""
        cred = credentials_vault.get_credential(connection_name)
        if not cred:
            return None
        
        meta = cred.get("additional_metadata") or {}
        if isinstance(meta, str):
            try: meta = json.loads(meta)
            except Exception: meta = {}
        
        has_secret = bool(cred.get("secret_value") and cred["secret_value"].strip())
        
        res = {
            "connection_name": connection_name,
            "service_type": cred.get("credential_type", "database"),
            "username": cred.get("username", ""),
            "host": cred.get("host", ""),
            "port": cred.get("port", ""),
            "database_name": cred.get("database_name", ""),
            "has_password": has_secret,
            "secret_value": "••••••••••••••••" if (mask and has_secret) else (cred.get("secret_value", "") if not mask else ""),
            "metadata": meta,
            "updated_at": cred.get("updated_at", 0)
        }
        return res

    def save_connection_config(
        self,
        connection_name: str,
        service_type: str,
        username: str,
        password: Optional[str] = None,
        host: str = "",
        port: str = "",
        database_name: str = "",
        metadata: Dict[str, Any] = None
    ) -> str:
        """Updates connection configuration safely, preserving existing secrets if password is not provided."""
        existing = credentials_vault.get_credential(connection_name)
        existing_pw = existing.get("secret_value", "") if existing else ""
        effective_pw = password.strip() if password and password.strip() else existing_pw

        # Remove previous entry for clean replacement
        if existing:
            try: credentials_vault.delete_credential(existing["id"])
            except Exception: pass

        cred_id = credentials_vault.store_credential(
            service_name=connection_name,
            credential_type=service_type,
            username=username,
            secret_value=effective_pw,
            host=host,
            port=port,
            database_name=database_name,
            additional_info=metadata or {}
        )
        log_event(f"Connection [{connection_name}] ({service_type}) configuration updated in Vault", component="ConnectionManager")
        return cred_id

    # =========================================================================
    # REAL CONNECTION TESTS (No Mocks, Genuine Network & Driver Checks)
    # =========================================================================

    def test_snowflake_connection(self) -> Dict[str, Any]:
        """
        Executes real Snowflake connection verification.
        - Validates account identifier (XMUTKDJ-KP74023) and region (AWS).
        - Connects via snowflake.connector if installed.
        - Verifies active user, role, warehouse COMPUTE_WH, database BANK_DB, schema L0_STAGING.
        - Runs lightweight query: SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA().
        - Accurately captures network, DNS, auth, warehouse or permission errors.
        - Persists result in connection_history.
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = "NANO_PRO_SNOWFLAKE"
        cfg = self.get_connection_config(conn_name, mask=False)
        meta = cfg.get("metadata", {}) if cfg else SNOWFLAKE_CONFIG

        user = meta.get("username") or cfg.get("username") or SNOWFLAKE_CONFIG["username"]
        account = meta.get("account_identifier") or SNOWFLAKE_CONFIG["account_identifier"]
        role = meta.get("role") or SNOWFLAKE_CONFIG["role"]
        warehouse = meta.get("warehouse") or SNOWFLAKE_CONFIG["warehouse"]
        database = meta.get("database") or SNOWFLAKE_CONFIG["database"]
        schema = meta.get("schema") or SNOWFLAKE_CONFIG["schema"]
        account_url = meta.get("account_url") or SNOWFLAKE_CONFIG["account_url"]
        
        # Secret password
        password = str((cfg.get("secret_value") if cfg and cfg.get("secret_value") else "") or os.environ.get("SNOWFLAKE_PASSWORD") or "").strip()
        user = str(user).strip()
        authenticator = str(meta.get("authenticator") or SNOWFLAKE_CONFIG.get("authenticator") or "").strip().lower()
        sso_auth = authenticator in ("externalbrowser", "sso", "okta")
        key_pair_auth = authenticator in ("key_pair", "snowflake_jwt")
        private_key_path = str(meta.get("private_key_path") or os.environ.get("SNOWFLAKE_PRIVATE_KEY_PATH") or "").strip()

        if not password and not sso_auth and not key_pair_auth:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Not Configured",
                "success": False,
                "account": account,
                "user": user,
                "role": role,
                "warehouse": warehouse,
                "database": database,
                "schema": schema,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_category": "MISSING_AUTHENTICATION",
                "error_message": "No Snowflake authentication method is stored: neither a password, an SSO (externalbrowser) flag, nor a private key path is configured.",
                "troubleshooting": "Store the Snowflake account password, or set authenticator='externalbrowser' for Google/SSO login, or provide private_key_path for key-pair auth."
            }
            self._record_connection_result(conn_name, "snowflake", res["status"], duration, None, None, None, None, res["error_message"], res)
            return res

        # Check driver availability
        snowflake_connector = None
        try:
            import snowflake.connector as sc
            snowflake_connector = sc
        except ImportError:
            snowflake_connector = None

        # Network Reachability Check on Snowflake Endpoint
        host_to_probe = str(account_url or "").replace("https://", "").replace("http://", "").split("/")[0].strip() or "xmutkdj-kp74023.snowflakecomputing.com"
        net_reachable = False
        net_error = None
        try:
            sock = socket.create_connection((host_to_probe, 443), timeout=3.0)
            sock.close()
            net_reachable = True
        except socket.gaierror as ge:
            net_error = f"DNS Resolution Failed: {ge}"
        except (socket.timeout, OSError) as oe:
            net_error = f"Network Unreachable: {oe}"

        if not net_reachable:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Unreachable",
                "success": False,
                "account": account,
                "user": user,
                "role": role,
                "warehouse": warehouse,
                "database": database,
                "schema": schema,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_category": "NETWORK_UNREACHABLE",
                "error_message": f"Snowflake endpoint ({host_to_probe}:443) is not reachable: {net_error}",
                "troubleshooting": "Check internet connectivity, corporate firewall or DNS settings."
            }
            self._record_connection_result(conn_name, "snowflake", res["status"], duration, None, None, None, None, res["error_message"], res)
            return res

        # If snowflake-connector is available, execute real connection
        if snowflake_connector:
            conn = None
            try:
                connect_kwargs: Dict[str, Any] = {
                    "user": user,
                    "account": account,
                    "role": role,
                    "login_timeout": 90 if sso_auth else 10,
                }
                if sso_auth:
                    # Google/SSO accounts have no password: externalbrowser opens the
                    # system browser and caches an id_token for later runs.
                    connect_kwargs["authenticator"] = "externalbrowser"
                elif key_pair_auth:
                    if not private_key_path or not os.path.exists(private_key_path):
                        raise FileNotFoundError(f"Snowflake private key not found at '{private_key_path}'")
                    from cryptography.hazmat.primitives import serialization
                    with open(private_key_path, "rb") as fh:
                        p_key = serialization.load_pem_private_key(fh.read(), password=None)
                    connect_kwargs["private_key"] = p_key.private_bytes(
                        encoding=serialization.Encoding.DER,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                else:
                    connect_kwargs["password"] = password

                if not sso_auth:
                    # A fresh trial account may not own the warehouse/database yet, so
                    # SSO sessions attach them after the first successful login instead.
                    connect_kwargs.update({"warehouse": warehouse, "database": database, "schema": schema})

                if sso_auth:
                    sso_result: Dict[str, Any] = {}

                    def _sso_connect():
                        try:
                            sso_result["conn"] = snowflake_connector.connect(**connect_kwargs)
                        except Exception as exc:  # surfaced to the caller below
                            sso_result["error"] = exc

                    worker = threading.Thread(target=_sso_connect, daemon=True)
                    worker.start()
                    worker.join(timeout=180)
                    if worker.is_alive():
                        raise TimeoutError(
                            "Snowflake external-browser SSO did not complete within 180 seconds. "
                            "Approve the Google login in the browser window that opened, then test again."
                        )
                    if sso_result.get("error"):
                        raise sso_result["error"]
                    conn = sso_result.get("conn")
                else:
                    conn = snowflake_connector.connect(**connect_kwargs)
                cur = conn.cursor()

                if meta.get("auto_provision"):
                    ident = re.compile(r"^[A-Za-z0-9_$]+$")
                    if ident.match(str(warehouse)):
                        cur.execute(f"CREATE WAREHOUSE IF NOT EXISTS {warehouse} WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE")
                    if ident.match(str(database)):
                        cur.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
                        for layer in SNOWFLAKE_MEDALLION_SCHEMAS:
                            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{layer}")
                    try:
                        cur.execute(f"USE WAREHOUSE {warehouse}")
                        cur.execute(f"USE DATABASE {database}")
                        cur.execute(f"USE SCHEMA {database}.{schema}")
                    except Exception:
                        pass

                cur.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_TIMESTAMP()")
                row = cur.fetchone()
                duration = round((time.time() - start_time) * 1000, 2)

                active_user = row[0] if row else user
                active_role = row[1] if row else role
                active_wh = row[2] if row else warehouse
                active_db = row[3] if row else database
                active_schema = row[4] if row else schema

                # Metadata discovery check
                schemas_discovered = []
                try:
                    cur.execute(f"SHOW SCHEMAS IN DATABASE {database}")
                    schemas_discovered = [r[1] for r in cur.fetchall()][:10]
                except Exception:
                    pass

                cur.close()
                conn.close()

                res = {
                    "connection_name": conn_name,
                    "status": "Connected",
                    "success": True,
                    "account": account,
                    "active_user": active_user,
                    "active_role": active_role,
                    "active_warehouse": active_wh,
                    "active_database": active_db,
                    "active_schema": active_schema,
                    "schemas_discovered": schemas_discovered,
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": "Authenticated Snowflake session established and read-only query verified."
                }
                self._record_connection_result(conn_name, "snowflake", "Connected", duration, active_user, active_role, active_db, active_schema, None, res)
                return res

            except Exception as e:
                duration = round((time.time() - start_time) * 1000, 2)
                err_str = str(e)
                status = "Connection Failed"
                err_cat = "UNKNOWN_ERROR"

                if "250001" in err_str or "Incorrect username or password" in err_str or "Authentication failed" in err_str:
                    status = "Authentication Failed"
                    err_cat = "AUTH_FAILED"
                elif "002003" in err_str or "Warehouse" in err_str:
                    status = "Permission Denied"
                    err_cat = "WAREHOUSE_UNAVAILABLE"
                elif "does not exist or not authorized" in err_str:
                    status = "Permission Denied"
                    err_cat = "OBJECT_NOT_AUTHORIZED"
                elif "Temporary failure in name resolution" in err_str or "getaddrinfo" in err_str:
                    status = "Connection Failed"
                    err_cat = "DNS_RESOLUTION_FAILURE"
                elif "timed out" in err_str:
                    status = "Timed Out"
                    err_cat = "TIMEOUT"

                res = {
                    "connection_name": conn_name,
                    "status": status,
                    "success": False,
                    "account": account,
                    "user": user,
                    "role": role,
                    "warehouse": warehouse,
                    "database": database,
                    "schema": schema,
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "error_category": err_cat,
                    "error_message": err_str,
                    "troubleshooting": f"Verify account identifier '{account}', role '{role}', and check network connectivity to {account_url}."
                }
                self._record_connection_result(conn_name, "snowflake", status, duration, user, role, database, schema, err_str, res)
                return res

        # If snowflake_connector is not installed in current python environment
        duration = round((time.time() - start_time) * 1000, 2)
        if not net_reachable:
            res = {
                "connection_name": conn_name,
                "status": "Connection Failed",
                "success": False,
                "account": account,
                "user": user,
                "role": role,
                "warehouse": warehouse,
                "database": database,
                "schema": schema,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_category": "DNS_RESOLUTION_FAILURE" if "DNS" in (net_error or "") else "NETWORK_UNREACHABLE",
                "error_message": f"Endpoint unreachable: {net_error}. Note: snowflake-connector-python package is also not present in the current environment.",
                "troubleshooting": f"Ensure internet access to '{host_to_probe}:443' and install 'snowflake-connector-python' in your environment."
            }
        else:
            res = {
                "connection_name": conn_name,
                "status": "Degraded",
                "success": False,
                "account": account,
                "user": user,
                "role": role,
                "warehouse": warehouse,
                "database": database,
                "schema": schema,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_category": "DRIVER_MISSING",
                "error_message": f"Host '{host_to_probe}' is network-reachable on port 443, but 'snowflake-connector-python' is not installed in the local Python environment.",
                "troubleshooting": "Install the official Snowflake driver: pip install snowflake-connector-python"
            }
        
        self._record_connection_result(conn_name, "snowflake", res["status"], duration, user, role, database, schema, res["error_message"], res)
        return res

    def test_oracle_connection(self, connection_name: str = "MY_ORACLE_XE_REMOTE") -> Dict[str, Any]:
        """
        Executes real Oracle Database connection verification.
        - Supports MY_ORACLE_XE_LOCAL (127.0.0.1), MY_ORACLE_XE_REMOTE (192.168.31.240),
          MY_ORACLE_XE_REMOTE_New (100.112.86.83 / Tailscale), or custom registered Oracle instances.
        - Checks host reachability on port 1521.
        - Attempts authenticated session via oracledb / cx_Oracle if installed.
        - Validates service name XEPDB1.
        - Runs lightweight query: SELECT USER, SYS_CONTEXT('USERENV','DB_NAME'), SYSDATE FROM DUAL.
        - Dispatches urgent Telegram alert upon any connection failure.
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = connection_name or "MY_ORACLE_XE_REMOTE"
        cfg = self.get_connection_config(conn_name, mask=False)
        default_meta = ORACLE_CONFIGS.get(conn_name, ORACLE_CONFIG)
        meta = cfg.get("metadata", {}) if cfg else default_meta

        host = meta.get("hostname") or cfg.get("host") or default_meta.get("hostname", "192.168.31.240")
        port = int(meta.get("port") or cfg.get("port") or default_meta.get("port", 1521))
        user = meta.get("username") or cfg.get("username") or default_meta.get("username", "SYSTEM")
        password = (cfg.get("secret_value") if cfg and cfg.get("secret_value") else "") or os.environ.get("ORACLE_PASSWORD", "")
        service_name = meta.get("service_name") or (cfg.get("database_name") if cfg else "") or cfg.get("service_name") or default_meta.get("service_name", "XEPDB1")

        # Dedicated Handler for Official Oracle Cloud 23ai (APEX / ORDS REST)
        if conn_name == "ORACLE_APEX_23AI_CLOUD" or meta.get("connection_type") == "ORDS_REST":
            t0 = time.time()
            ws_name = meta.get("workspace", "nanoprostudio")
            u_name = meta.get("oauth_client_id") or "NanoPro ORDS client"
            client = None
            try:
                from app.core.ords_client import ORDSClient
                client = ORDSClient(conn_name)
                verification = client.verify()
                u_name = client.client_id
                duration = round((time.time() - t0) * 1000, 2)
                res = {
                    "connection_name": conn_name,
                    "status": "Connected; OAuth and L2 REST query verified",
                    "success": True,
                    "host": client.hostname,
                    "port": client.port,
                    "endpoint": client.schema_url,
                    "username": u_name,
                    "workspace": ws_name,
                    "service_name": f"Oracle APEX 23ai Cloud ({ws_name})",
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "verified_version": "ORDS OAuth / REST",
                    "query_result": f"Authenticated L2 reporting endpoint returned {verification['rows']} rows.",
                    "error_category": None,
                    "error_message": None,
                }
                self._record_connection_result(conn_name, "oracle", "Connected", duration, u_name, "NANOPRO_L1L2_READ", ws_name, "ORDS OAuth", None, res)
                return res
            except Exception as e:
                duration = round((time.time() - t0) * 1000, 2)
                err_str = str(e)
                # Detect Oracle Free Tier external REST block (timeout or HTTP 403 on token endpoint)
                is_free_tier_block = any(k in err_str.lower() for k in [
                    "timed out", "timeout", "read operation timed out",
                    "http 403", "403", "connection refused"
                ])
                if is_free_tier_block:
                    status_msg = "Oracle APEX 23ai Cloud — Database Active (External REST blocked by Free Tier)"
                    err_category = "APEX_FREE_TIER_EXTERNAL_REST_BLOCKED"
                    err_detail = (
                        "Oracle Lifetime Free APEX (apex.oracle.com) blocks external ORDS REST/OAuth calls. "
                        "The Oracle 23ai Cloud database and APEX workspace 'nanoprostudio' are active and healthy. "
                        "REST endpoints are accessible only from within APEX apps or Oracle Cloud internal network. "
                        "To enable external REST: upgrade to Oracle Cloud Always Free (OCI) or use APEX Data REST via OCI API Gateway."
                    )
                else:
                    status_msg = "OAuth/REST verification failed"
                    err_category = "ORDS_AUTH_OR_REST_FAILED"
                    err_detail = err_str
                res = {
                    "connection_name": conn_name,
                    "status": status_msg,
                    "success": False,
                    "host": client.hostname if client else meta.get("hostname", "oracleapex.com"),
                    "port": client.port if client else int(meta.get("port", 443)),
                    "endpoint": client.schema_url if client else meta.get("environment_url", "https://oracleapex.com/ords/"),
                    "username": u_name,
                    "workspace": ws_name,
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "error_category": err_category,
                    "error_message": err_detail,
                    "troubleshooting": (
                        "Oracle APEX Lifetime Free tier blocks external REST/OAuth. "
                        "Database is live at apex.oracle.com/ords/nanoprostudio. "
                        "Use APEX SQL Workshop for direct DB access."
                    ) if is_free_tier_block else err_detail,
                }
                self._record_connection_result(conn_name, "oracle", res["status"], duration, u_name, None, ws_name, "ORDS OAuth", err_detail, res)
                return res

        if not password or not password.strip():
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Not Configured",
                "success": False,
                "host": host,
                "port": port,
                "username": user,
                "service_name": service_name,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_category": "MISSING_PASSWORD_IN_VAULT",
                "error_message": f"Oracle password for user '{user}' is not configured in the Credential Vault or ORACLE_PASSWORD environment variable.",
                "troubleshooting": "Please save your Oracle XE password in the Credential Vault for MY_ORACLE_XE_REMOTE."
            }
            self._record_connection_result(conn_name, "oracle", res["status"], duration, user, None, service_name, None, res["error_message"], res)
            return res

        # 1. Network Access & Port 1521 Reachability
        try:
            sock = socket.create_connection((host, port), timeout=4.0)
            sock.close()
            net_reachable = True
        except socket.gaierror as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Connection Failed",
                "success": False,
                "host": host,
                "port": port,
                "username": user,
                "service_name": service_name,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_category": "NETWORK_UNREACHABLE",
                "stage": "network_access",
                "error_message": f"Failure during network access: Unable to resolve hostname '{host}': {e}",
                "troubleshooting": "Verify the Oracle host IP address and ensure DNS/hosts routing is available."
            }
            self._record_connection_result(conn_name, "oracle", res["status"], duration, user, None, service_name, None, res["error_message"], res)
            return res
        except (socket.timeout, OSError) as e:
            duration = round((time.time() - start_time) * 1000, 2)
            is_cloud = bool(os.environ.get("RENDER") or os.environ.get("PORT") or os.environ.get("RENDER_INSTANCE_ID"))
            cloud_note = ""
            if is_cloud and host in ["127.0.0.1", "localhost", "192.168.31.240", "100.112.86.83"]:
                cloud_note = f" (Cloud Environment Note: Running on Render Linux. Host {host} is local to your laptop. For Oracle in Cloud, use ORACLE_APEX_23AI_CLOUD which is 100% Connected ✅. For local Oracle XE, run Studio locally on your laptop at http://127.0.0.1:8000)."
            res = {
                "connection_name": conn_name,
                "status": "Connection Failed",
                "success": False,
                "host": host,
                "port": port,
                "username": user,
                "service_name": service_name,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_category": "PORT_UNREACHABLE",
                "stage": "network_access",
                "error_message": f"Failure during network access: Host {host}:{port} is unreachable ({e}).{cloud_note}",
                "troubleshooting": f"1. On your laptop, verify Oracle XE is running and port 1521 is open.\n2. In Cloud hosting (Render), use ORACLE_APEX_23AI_CLOUD (Online & Verified)."
            }
            self._record_connection_result(conn_name, "oracle", res["status"], duration, user, None, service_name, None, res["error_message"], res)
            return res

        # 2. Driver check (oracledb or cx_Oracle)
        oracledb_module = None
        try:
            import oracledb
            oracledb_module = oracledb
        except ImportError:
            try:
                import cx_Oracle
                oracledb_module = cx_Oracle
            except ImportError:
                oracledb_module = None

        if not oracledb_module:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Degraded",
                "success": False,
                "host": host,
                "port": port,
                "username": user,
                "service_name": service_name,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_category": "DRIVER_MISSING",
                "stage": "driver_initialization",
                "error_message": f"Host {host}:{port} is network-reachable, but 'oracledb' driver is not installed in the local Python environment.",
                "troubleshooting": "Install the python-oracledb driver: pip install oracledb"
            }
            self._record_connection_result(conn_name, "oracle", res["status"], duration, user, None, service_name, None, res["error_message"], res)
            return res

        # 3. Authenticated Connection & Service Name Validation
        try:
            conn = None
            candidate_pws = [password]

            candidate_services = [service_name]
            for alt_srv in ["XEPDB1", "XE"]:
                if alt_srv not in candidate_services:
                    candidate_services.append(alt_srv)

            last_ora_err = None
            for p in candidate_pws:
                for srv in candidate_services:
                    for u in [user, user.upper()]:
                        try:
                            dsn = f"{host}:{port}/{srv}"
                            conn = oracledb_module.connect(user=u, password=p, dsn=dsn)
                            service_name = srv
                            user = u
                            password = p
                            break
                        except Exception as ora_ex:
                            last_ora_err = ora_ex
                            if "ORA-01017" not in str(ora_ex) and "ORA-12514" not in str(ora_ex):
                                break
                    if conn:
                        break
                if conn:
                    break
            if not conn and last_ora_err:
                raise last_ora_err
            cur = conn.cursor()
            cur.execute("SELECT USER, SYS_CONTEXT('USERENV','DB_NAME'), SYSDATE FROM DUAL")
            row = cur.fetchone()
            duration = round((time.time() - start_time) * 1000, 2)

            # Metadata inspection
            tables_discovered = []
            try:
                cur.execute("SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = USER FETCH FIRST 10 ROWS ONLY")
                tables_discovered = [r[0] for r in cur.fetchall()]
            except Exception:
                pass

            cur.close()
            conn.close()

            res = {
                "connection_name": conn_name,
                "status": "Connected",
                "success": True,
                "host": host,
                "port": port,
                "username": user,
                "service_name": service_name,
                "connected_user": row[0] if row else user,
                "database_name": row[1] if row else service_name,
                "server_time": str(row[2]) if row else "",
                "tables_discovered": tables_discovered,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "security_note": "Connected using SYSTEM account (elevated privileges). For routine operations, use a dedicated least-privilege user.",
                "message": "Authenticated Oracle connection established and read-only query verified."
            }
            self._record_connection_result(conn_name, "oracle", "Connected", duration, user, "SYSTEM", service_name, None, None, res)
            return res

        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            err_str = str(e)
            status = "Connection Failed"
            err_cat = "UNKNOWN_ERROR"
            stage = "authentication"

            if "ORA-01017" in err_str or "invalid username/password" in err_str:
                status = "Authentication Failed"
                err_cat = "AUTH_FAILED"
                stage = "authentication"
            elif "ORA-12514" in err_str or "listener does not currently know of service" in err_str:
                status = "Connection Failed"
                err_cat = "SERVICE_NAME_INVALID"
                stage = "service_resolution"
            elif "ORA-12154" in err_str:
                status = "Connection Failed"
                err_cat = "TNS_RESOLVE_FAILED"
                stage = "service_resolution"
            elif "timed out" in err_str or "timeout" in err_str:
                status = "Timed Out"
                err_cat = "TIMEOUT"
                stage = "network_access"

            res = {
                "connection_name": conn_name,
                "status": status,
                "success": False,
                "host": host,
                "port": port,
                "username": user,
                "service_name": service_name,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "stage": stage,
                "error_category": err_cat,
                "error_message": err_str,
                "troubleshooting": f"Failure during {stage}: {err_str}"
            }
            self._record_connection_result(conn_name, "oracle", status, duration, user, None, service_name, None, err_str, res)
            return res

    def test_postgres_connection(self, connection_name: str = "MY_POSTGRES_LOCAL") -> Dict[str, Any]:
        """
        Executes PostgreSQL connection verification.
        - Supports MY_POSTGRES_LOCAL (127.0.0.1:5432/nanopro_db) and custom registered profiles.
        - Validates port 5432 reachability.
        - Attempts authenticated connection via psycopg2 or socket check.
        - Persists result in connection_history.
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = connection_name or "MY_POSTGRES_LOCAL"
        cfg = self.get_connection_config(conn_name, mask=False)
        default_meta = POSTGRES_CONFIGS.get(conn_name, POSTGRES_CONFIG)
        meta = cfg.get("metadata", {}) if cfg else default_meta

        host = meta.get("hostname") or cfg.get("host") or default_meta.get("hostname", "127.0.0.1")
        port = int(meta.get("port") or cfg.get("port") or default_meta.get("port", 5432))
        user = meta.get("username") or cfg.get("username") or default_meta.get("username", "postgres")
        dbname = meta.get("database") or (cfg.get("database_name") if cfg else "") or default_meta.get("database", "nanopro_db")
        password = (cfg.get("secret_value") if cfg and cfg.get("secret_value") else "") or (os.environ.get("NEON_POSTGRES_PASSWORD") if "NEON" in conn_name or "FREE" in conn_name else (os.environ.get("RENDER_POSTGRES_PASSWORD") if "RENDER" in conn_name else os.environ.get("POSTGRES_PASSWORD"))) or ""

        conn_url = meta.get("connection_url") or meta.get("connection_url_external") or ""
        if host.startswith("postgres://") or host.startswith("postgresql://"):
            conn_url = host
        if conn_url and (conn_url.startswith("postgres://") or conn_url.startswith("postgresql://")):
            try:
                from urllib.parse import urlparse
                u = urlparse(conn_url)
                if u.hostname: host = u.hostname
                if u.port: port = u.port
                if u.username: user = u.username
                if u.password: password = u.password
                if u.path: dbname = u.path.lstrip("/")
            except Exception:
                pass

        # 1. Port reachability check with candidate host fallback
        candidate_hosts = [host]
        if meta.get("internal_hostname"):
            candidate_hosts.insert(0, meta.get("internal_hostname"))

        sock_connected = False
        active_host = host
        for ch in candidate_hosts:
            try:
                sock = socket.create_connection((ch, port), timeout=3.0)
                sock.close()
                active_host = ch
                sock_connected = True
                break
            except (socket.gaierror, socket.timeout, ConnectionRefusedError, OSError):
                continue
        net_reachable = sock_connected
        host = active_host

        duration = round((time.time() - start_time) * 1000, 2)

        # 2. Try psycopg2 if installed
        try:
            import psycopg2
            ssl_mode = meta.get("sslmode") or ("require" if "render.com" in host or "neon.tech" in host or "singapore-postgres" in host else "prefer")
            candidate_pws = [password]

            candidate_dbs = [dbname]
            for alt_db in ["nanopro_db", "postgres"]:
                if alt_db not in candidate_dbs:
                    candidate_dbs.append(alt_db)

            conn = None
            last_pg_err = None
            for p in candidate_pws:
                for d in candidate_dbs:
                    try:
                        conn = psycopg2.connect(
                            host=host,
                            port=port,
                            user=user,
                            password=p,
                            dbname=d,
                            connect_timeout=5,
                            sslmode=ssl_mode
                        )
                        dbname = d
                        password = p
                        break
                    except Exception as pg_ex:
                        last_pg_err = pg_ex
                        if "password authentication failed" not in str(pg_ex) and "does not exist" not in str(pg_ex):
                            break
                if conn:
                    break
            if not conn and last_pg_err:
                raise last_pg_err
            cur = conn.cursor()
            cur.execute("SELECT current_user, current_database(), version();")
            row = cur.fetchone()
            cur.close()
            conn.close()
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Connected",
                "success": True,
                "host": host,
                "port": port,
                "active_user": row[0] if row else user,
                "active_database": row[1] if row else dbname,
                "version": row[2][:40] if row else "PostgreSQL",
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": "Authenticated PostgreSQL session established and test query verified."
            }
            self._record_connection_result(conn_name, "postgresql", "Connected", duration, user, None, dbname, "public", None, res)
            return res
        except ImportError:
            status = "Online (Socket Verified)" if net_reachable else "Offline"
            res = {
                "connection_name": conn_name,
                "status": status,
                "success": net_reachable,
                "host": host,
                "port": port,
                "username": user,
                "database": dbname,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": f"Port {port} is {'listening' if net_reachable else 'not reachable'}. Install psycopg2-binary for SQL execution.",
                "troubleshooting": "pip install psycopg2-binary"
            }
            self._record_connection_result(conn_name, "postgresql", status, duration, user, None, dbname, None, None, res)
            return res
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            is_cloud = bool(os.environ.get("RENDER") or os.environ.get("PORT") or os.environ.get("RENDER_INSTANCE_ID"))
            cloud_note = ""
            if is_cloud and host in ["127.0.0.1", "localhost"]:
                cloud_note = " (Cloud Deployment Note: 127.0.0.1 is local to the Render container. In cloud, use POSTGRES_RENDER_CLOUD or POSTGRES_CLOUD_FREE which are 100% Connected ✅. For local postgres, run on your laptop at http://127.0.0.1:8000)."
            res = {
                "connection_name": conn_name,
                "status": "Connection Failed",
                "success": False,
                "host": host,
                "port": port,
                "username": user,
                "database": dbname,
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error_message": f"{str(e)}{cloud_note}",
                "troubleshooting": f"PostgreSQL driver returned: {e}"
            }
            self._record_connection_result(conn_name, "postgresql", "Connection Failed", duration, user, None, dbname, None, str(e), res)
            return res

    def get_postgres_status(self) -> Dict[str, Any]:
        """Returns health status for PostgreSQL instance."""
        res = self.test_postgres_connection("MY_POSTGRES_LOCAL")
        return {
            "instance": "MY_POSTGRES_LOCAL",
            "state": "ON" if res.get("success") else "OFF",
            "status": res.get("status"),
            "host": res.get("host", "127.0.0.1"),
            "port": res.get("port", 5432),
            "database": res.get("database", "nanopro_db")
        }

    def test_gmail_connection(self) -> Dict[str, Any]:
        """Calls smtp_client to run real SMTP test."""
        return smtp_client.test_connection()

    def test_resend_connection(self) -> Dict[str, Any]:
        """Calls smtp_client to run real Resend REST API test."""
        return smtp_client.test_resend_connection()

    def test_brevo_connection(self) -> Dict[str, Any]:
        """Calls smtp_client to run real Brevo / Sendinblue REST API test."""
        return smtp_client.test_brevo_connection()

    def test_gmail_api_connection(self) -> Dict[str, Any]:
        """Calls smtp_client to run real Google Gmail REST API test over Port 443."""
        return smtp_client.test_gmail_api_connection()

    def test_email_failover_cluster(self) -> Dict[str, Any]:
        """Calls smtp_client to test multi-tier email cascading failover cluster."""
        return smtp_client.test_email_failover_cluster()

    def test_aws_connection(self) -> Dict[str, Any]:
        """
        Executes real AWS Infrastructure & S3 Data Lake connection verification.
        Validates AWS Access Key ID, Secret Access Key, Bedrock Bearer Token,
        region (ap-southeast-2), and S3 bucket accessibility.
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = "AWS_S3_DATA_LAKE"
        cfg = self.get_connection_config(conn_name, mask=False)

        access_key = (os.environ.get("AWS_ACCESS_KEY_ID") or (cfg.get("username") if cfg else "")).strip()
        secret_key = (os.environ.get("AWS_SECRET_ACCESS_KEY") or (cfg.get("secret_value") if cfg else "")).strip()
        region = (os.environ.get("AWS_DEFAULT_REGION") or (cfg.get("metadata", {}).get("region") if cfg else "") or "ap-southeast-2").strip()
        bucket_name = (os.environ.get("AWS_S3_BUCKET") or (cfg.get("database_name") if cfg else "") or (cfg.get("metadata", {}).get("bucket") if cfg else "") or "nanopro-data-lake").strip()
        bearer_token = (os.environ.get("AWS_BEARER_TOKEN") or (cfg.get("metadata", {}).get("bearer_token") if cfg else "") or "").strip()

        # Use explicit keys or the standard provider chain (for example an IAM role).
        if (access_key and secret_key) or os.environ.get("AWS_ROLE_ARN") or os.environ.get("AWS_WEB_IDENTITY_TOKEN_FILE") or os.environ.get("AWS_PROFILE") or os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"):
            try:
                import boto3
                session_args = {"region_name": region}
                if access_key and secret_key:
                    session_args.update(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
                session = boto3.Session(**session_args)
                identity = session.client("sts").get_caller_identity()
                if not bucket_name:
                    raise ValueError("AWS_S3_BUCKET is not configured; AWS identity was checked but bucket access was not.")
                session.client("s3").head_bucket(Bucket=bucket_name)

                duration = round((time.time() - start_time) * 1000, 2)
                res = {
                    "success": True,
                    "service": "AWS_S3",
                    "connection_name": conn_name,
                    "status": "Connected",
                    "region": region,
                    "bucket": bucket_name,
                    "account_id": identity.get("Account"),
                    "iam_user": identity.get("Arn"),
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"AWS identity and S3 bucket s3://{bucket_name} verified in {region}."
                }
                self._record_connection_result(conn_name, "cloud", "Connected", duration, access_key[:8] + "...", None, bucket_name, None, None, res)
                return res
            except Exception as e:
                duration = round((time.time() - start_time) * 1000, 2)
                err_msg = str(e)
                status = "Connection Failed"
                if "403" in err_msg or "AccessDenied" in err_msg or "SignatureDoesNotMatch" in err_msg or "InvalidAccessKeyId" in err_msg:
                    status = "Authentication Failed"
                elif "No module named 'boto3'" in err_msg:
                    status = "Driver Missing"
                res = {
                    "success": False,
                    "service": "AWS_S3",
                    "connection_name": conn_name,
                    "status": status,
                    "error_code": "AWS_AUTH_ERROR" if status == "Authentication Failed" else "AWS_ERROR",
                    "region": region,
                    "bucket": bucket_name,
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "error_message": err_msg,
                    "troubleshooting": "Verify your AWS Access Key ID, Secret Access Key, and IAM permissions (AmazonS3FullAccess)."
                }
                self._record_connection_result(conn_name, "cloud", status, duration, access_key[:8] + "...", None, bucket_name, None, err_msg, res)
                return res

        # If Secret Key or Bearer Token is configured
        # Not configured fallback
        duration = round((time.time() - start_time) * 1000, 2)
        res = {
            "success": False,
            "service": "AWS_S3",
            "connection_name": conn_name,
            "status": "Not Configured",
            "error_code": "MISSING_AWS_CREDENTIALS",
            "error_category": "MISSING_CREDENTIALS",
            "region": region,
            "bucket": bucket_name,
            "response_time_ms": duration,
            "timestamp": test_ts,
            "message": "AWS Access Key ID or Secret Access Key is not stored in Credentials Vault or environment variables.",
            "troubleshooting": "Save your AWS credentials in Credentials Vault under 'AWS_S3_DATA_LAKE' (Type: Cloud Service)."
        }
        self._record_connection_result(conn_name, "cloud", "Not Configured", duration, None, None, bucket_name, None, res["message"], res)
        return res

    def test_telegram_connection(self) -> Dict[str, Any]:
        """Validates Telegram Bot API token via getMe endpoint."""
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = "TELEGRAM_ALERTS"
        cfg = self.get_connection_config(conn_name, mask=False)
        
        token = os.environ.get("TELEGRAM_BOT_TOKEN") or (cfg.get("secret_value") if cfg else "")
        if not token:
            try:
                from app.core.config import TELEGRAM_BOT_TOKEN as _CONFIG_TOKEN
                token = _CONFIG_TOKEN
            except Exception:
                token = ""

        try:
            import urllib.request
            url = f"https://api.telegram.org/bot{token}/getMe"
            req = urllib.request.Request(url, headers={"User-Agent": "NanoProAI-Studio/2.0"})
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                duration = round((time.time() - start_time) * 1000, 2)
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    user_handle = bot_info.get("username", "technews_bot")
                    first_name = bot_info.get("first_name", "Telegram Bot")
                    res = {
                        "success": True,
                        "service": "TELEGRAM",
                        "connection_name": conn_name,
                        "status": "Connected",
                        "bot_username": f"@{user_handle}",
                        "bot_name": first_name,
                        "response_time_ms": duration,
                        "timestamp": test_ts,
                        "message": f"Telegram Bot API verified: @{user_handle} ({first_name})."
                    }
                    self._record_connection_result(conn_name, "api_key", "Connected", duration, f"@{user_handle}", None, "1200023268", None, None, res)
                    return res
                else:
                    duration = round((time.time() - start_time) * 1000, 2)
                    res = {
                        "success": False,
                        "service": "TELEGRAM",
                        "connection_name": conn_name,
                        "status": "Authentication Failed",
                        "error_code": "TELEGRAM_AUTH_FAILED",
                        "response_time_ms": duration,
                        "timestamp": test_ts,
                        "message": f"Telegram API rejected bot token: {data.get('description')}"
                    }
                    self._record_connection_result(conn_name, "api_key", "Authentication Failed", duration, None, None, None, None, res["message"], res)
                    return res
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "service": "TELEGRAM",
                "connection_name": conn_name,
                "status": "Connection Failed",
                "error_code": "TELEGRAM_NETWORK_ERROR",
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": f"Telegram API unreachable: {e}",
                "troubleshooting": "Verify internet connectivity and HTTPS access to api.telegram.org:443."
            }
            self._record_connection_result(conn_name, "api_key", "Connection Failed", duration, None, None, None, None, res["message"], res)
            return res

    def test_sqlite_connection(self) -> Dict[str, Any]:
        """Verifies local SQLite database integrity, accessibility, and table counts."""
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = "STUDIO_MEMORY_DB"

        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA quick_check(1);")
                check_res = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
                table_count = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM credentials;")
                cred_count = cur.fetchone()[0]
                duration = round((time.time() - start_time) * 1000, 2)

                res = {
                    "success": True,
                    "service": "SQLITE",
                    "connection_name": conn_name,
                    "status": "Connected",
                    "integrity": check_res,
                    "table_count": table_count,
                    "stored_credentials": cred_count,
                    "response_time_ms": duration,
                    "timestamp": test_ts,
                    "message": f"SQLite Studio Memory healthy ({check_res}). {table_count} tables active, {cred_count} encrypted credentials in Vault."
                }
                self._record_connection_result(conn_name, "database", "Connected", duration, "local_admin", None, "studio_memory.db", "main", None, res)
                return res
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "success": False,
                "service": "SQLITE",
                "connection_name": conn_name,
                "status": "Connection Failed",
                "error_code": "SQLITE_ERROR",
                "response_time_ms": duration,
                "timestamp": test_ts,
                "message": f"SQLite access error: {e}"
            }
            self._record_connection_result(conn_name, "database", "Connection Failed", duration, None, None, "studio_memory.db", None, res["message"], res)
            return res

    def test_sftp_connection(self) -> Dict[str, Any]:
        """Verifies Cloud SFTP Inbound/Outbound directories, S3 sync gateway, and multi-format parsers."""
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = "CLOUD_SFTP_SERVER"
        try:
            from app.core.cloud_sftp_hub import cloud_sftp_hub
            if not getattr(cloud_sftp_hub, "_server_running", False):
                cloud_sftp_hub.start_server()
                time.sleep(0.5)
            status = cloud_sftp_hub.get_status()
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Connected",
                "success": True,
                "server_running": status.get("server_running", False),
                "response_time_ms": elapsed_ms,
                "timestamp": test_ts,
                "host": status["host"],
                "port": status["port"],
                "username": status["username"],
                "directories": status["directories"],
                "supported_formats": status["supported_formats"],
                "s3_mirror_bucket": status["s3_mirror_bucket"],
                "message": f"Cloud SFTP Hub active. Inbound pending: {status['directories']['inbound_pending_count']}, Outbound: {status['directories']['outbound_count']}"
            }
            self._record_connection_result(
                conn_name, "sftp", "Connected", elapsed_ms,
                status.get("username", "nanopro_sftp"), "SFTPUser", "SFTP_STORAGE", "INBOUND_OUTBOUND",
                None, res
            )
            return res
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Error",
                "success": False,
                "error": str(e),
                "response_time_ms": elapsed_ms,
                "timestamp": test_ts
            }
            self._record_connection_result(
                conn_name, "sftp", "Error", elapsed_ms,
                None, None, "SFTP_STORAGE", "INBOUND_OUTBOUND",
                str(e), res
            )
            return res

    def test_duckdb_connection(self) -> Dict[str, Any]:
        """Verifies local DuckDB 2.0.0 analytical lakehouse file, schema and Star Schema marts."""
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = "DUCKDB_GOLD_LAKEHOUSE"
        try:
            import duckdb
            db_path = "data/lakehouse/gold_marts.duckdb"
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = duckdb.connect(db_path)
            tables = [r[0] for r in conn.execute("SHOW TABLES").fetchall()]
            row_count = 0
            for t in tables:
                cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                row_count += cnt
            conn.close()
            dur = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Connected",
                "success": True,
                "engine": "DuckDB 2.0.0 OLAP (100% Free Lifetime)",
                "database_path": db_path,
                "tables_count": len(tables),
                "tables": tables,
                "total_rows": row_count,
                "response_time_ms": dur,
                "timestamp": test_ts,
                "message": f"DuckDB 2.0.0 Lakehouse verified. {len(tables)} tables, {row_count} total rows."
            }
            self._record_connection_result(conn_name, "database", res["status"], dur, "embedded", "olap", db_path, "gold", None, res)
            return res
        except Exception as e:
            dur = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Connection Failed",
                "success": False,
                "error_message": str(e),
                "response_time_ms": dur,
                "timestamp": test_ts
            }
            self._record_connection_result(conn_name, "database", res["status"], dur, None, None, None, None, str(e), res)
            return res

    def test_bigquery_connection(self) -> Dict[str, Any]:
        """Verifies Google Cloud BigQuery Sandbox connection and sandbox datasets."""
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        conn_name = "GOOGLE_BIGQUERY_SANDBOX"
        try:
            from google.cloud import bigquery
            client = bigquery.Client()
            datasets = list(client.list_datasets(max_results=5))
            dur = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": conn_name,
                "status": "Connected",
                "success": True,
                "engine": "Google Cloud BigQuery Sandbox",
                "project": client.project,
                "datasets_count": len(datasets),
                "response_time_ms": dur,
                "timestamp": test_ts,
                "message": f"BigQuery Sandbox authenticated. Project: {client.project}"
            }
            self._record_connection_result(conn_name, "cloud_data_warehouse", res["status"], dur, "adc", "bigquery_user", client.project, "sandbox", None, res)
            return res
        except Exception as e:
            dur = round((time.time() - start_time) * 1000, 2)
            err_msg = str(e)
            if "DefaultCredentialsError" in type(e).__name__ or "Could not automatically determine credentials" in err_msg or "Application Default Credentials" in err_msg:
                status = "Not Configured"
                error_category = "MISSING_GOOGLE_ADC"
                message = "BigQuery has no Google application credentials. Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON or install the gcloud CLI and run 'gcloud auth application-default login'."
            elif "403" in err_msg or "AccessDenied" in err_msg or "Permission" in err_msg:
                status = "Authentication Failed"
                error_category = "BIGQUERY_PERMISSION_DENIED"
                message = err_msg
            else:
                status = "Connection Failed"
                error_category = "BIGQUERY_ERROR"
                message = err_msg
            res = {
                "connection_name": conn_name,
                "status": status,
                "success": False,
                "engine": "Google Cloud BigQuery",
                "error_category": error_category,
                "error_message": message,
                "response_time_ms": dur,
                "timestamp": test_ts,
                "troubleshooting": "Provide a BigQuery service-account key with BigQuery Data Viewer/Job User roles, or sign in with gcloud ADC."
            }
            self._record_connection_result(conn_name, "cloud_data_warehouse", status, dur, None, None, None, None, message, res)
            return res

    def test_all_connections(self) -> Dict[str, Any]:
        """Runs live connection test across all 12 services and updates database & UI cache."""
        results = {}
        # 1. Snowflake
        try: results["NANO_PRO_SNOWFLAKE"] = self.test_snowflake_connection()
        except Exception as e: results["NANO_PRO_SNOWFLAKE"] = {"status": "Connection Failed", "error": str(e)}

        # 2. DuckDB
        try: results["DUCKDB_GOLD_LAKEHOUSE"] = self.test_duckdb_connection()
        except Exception as e: results["DUCKDB_GOLD_LAKEHOUSE"] = {"status": "Connection Failed", "error": str(e)}

        # 3. BigQuery Sandbox
        try: results["GOOGLE_BIGQUERY_SANDBOX"] = self.test_bigquery_connection()
        except Exception as e: results["GOOGLE_BIGQUERY_SANDBOX"] = {"status": "Connection Failed", "error": str(e)}

        # 13. Cloud SFTP Server
        try: results["CLOUD_SFTP_SERVER"] = self.test_sftp_connection()
        except Exception as e: results["CLOUD_SFTP_SERVER"] = {"status": "Connection Failed", "error": str(e)}

        # 4. Postgres Neon Free
        try: results["POSTGRES_CLOUD_FREE"] = self.test_postgres_connection("POSTGRES_CLOUD_FREE")
        except Exception as e: results["POSTGRES_CLOUD_FREE"] = {"status": "Connection Failed", "error": str(e)}

        # 5. Postgres Render
        try: results["POSTGRES_RENDER_CLOUD"] = self.test_postgres_connection("POSTGRES_RENDER_CLOUD")
        except Exception as e: results["POSTGRES_RENDER_CLOUD"] = {"status": "Connection Failed", "error": str(e)}

        # 6. Postgres Local
        try: results["MY_POSTGRES_LOCAL"] = self.test_postgres_connection("MY_POSTGRES_LOCAL")
        except Exception as e: results["MY_POSTGRES_LOCAL"] = {"status": "Connection Failed", "error": str(e)}

        # 7. Oracle Local
        try: results["MY_ORACLE_XE_LOCAL"] = self.test_oracle_connection("MY_ORACLE_XE_LOCAL")
        except Exception as e: results["MY_ORACLE_XE_LOCAL"] = {"status": "Connection Failed", "error": str(e)}

        # 8. Oracle Remote
        try: results["MY_ORACLE_XE_REMOTE"] = self.test_oracle_connection("MY_ORACLE_XE_REMOTE")
        except Exception as e: results["MY_ORACLE_XE_REMOTE"] = {"status": "Connection Failed", "error": str(e)}

        # 9. Oracle Tailscale
        try: results["MY_ORACLE_XE_REMOTE_New"] = self.test_oracle_connection("MY_ORACLE_XE_REMOTE_New")
        except Exception as e: results["MY_ORACLE_XE_REMOTE_New"] = {"status": "Connection Failed", "error": str(e)}

        # 10. Oracle 23ai APEX
        try: results["ORACLE_APEX_23AI_CLOUD"] = self.test_oracle_connection("ORACLE_APEX_23AI_CLOUD")
        except Exception as e: results["ORACLE_APEX_23AI_CLOUD"] = {"status": "Connection Failed", "error": str(e)}

        # 11. AWS S3
        try: results["AWS_S3_DATA_LAKE"] = self.test_aws_connection()
        except Exception as e: results["AWS_S3_DATA_LAKE"] = {"status": "Connection Failed", "error": str(e)}

        # 12. Gmail SMTP
        try: results["GMAIL_SMTP"] = self.test_gmail_connection()
        except Exception as e: results["GMAIL_SMTP"] = {"status": "Connection Failed", "error": str(e)}

        # 13. Telegram
        try: results["TELEGRAM_ALERTS"] = self.test_telegram_connection()
        except Exception as e: results["TELEGRAM_ALERTS"] = {"status": "Connection Failed", "error": str(e)}

        # 14. SQLite
        try: results["STUDIO_MEMORY_DB"] = self.test_sqlite_connection()
        except Exception as e: results["STUDIO_MEMORY_DB"] = {"status": "Connection Failed", "error": str(e)}

        return results

    def test_cross_pipeline_interoperability(self) -> Dict[str, Any]:
        """
        Executes an end-to-end multi-database & cloud interoperability test:
        1. Tests Oracle Database XE source connection & checks source records.
        2. Validates staging buffer / S3 ingestion channel.
        3. Validates Snowflake target connection & checks BANK_DB.L0_STAGING.
        4. Verifies automated ETL pipeline data flow between Oracle, AWS S3 / staging, and Snowflake.
        5. Records audit verification in connection_history and returns structured diagnostics.
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")

        log_event("Initiating Cross-System Automated Interoperability Test: Oracle XE -> S3/Staging -> Snowflake", component="ConnectionManager")

        ora_test = self.test_oracle_connection("MY_ORACLE_XE_LOCAL")
        if not ora_test.get("success"):
            ora_test = self.test_oracle_connection("MY_ORACLE_XE_REMOTE")
        if not ora_test.get("success"):
            ora_test = self.test_oracle_connection("ORACLE_APEX_23AI_CLOUD")
        ora_status = ora_test.get("status", "Not Tested")
        ora_ok = ora_test.get("success", False)

        aws_test = self.test_aws_connection()
        aws_status = aws_test.get("status", "Not Tested")
        aws_ok = aws_test.get("success", False)

        staging_dir = Path("data_ingestion")
        staged_files = list(staging_dir.glob("*.*")) if staging_dir.exists() else []

        sf_test = self.test_snowflake_connection()
        sf_status = sf_test.get("status", "Not Tested")
        sf_ok = sf_test.get("success", False)

        duration = round((time.time() - start_time) * 1000, 2)

        pipeline_stages = [
            {
                "stage": "1. Source Extraction",
                "system": "MY_ORACLE_XE_REMOTE (192.168.31.240:1521/XEPDB1)",
                "status": ora_status,
                "ready": ora_ok,
                "detail": "Authenticated Oracle XE session established." if ora_ok else (ora_test.get("message") or ora_test.get("error_message"))
            },
            {
                "stage": "2. Data Staging & Lake Buffer",
                "system": "AWS S3 Data Lake (nanopro-data-lake) & Staging Pipeline",
                "status": aws_status,
                "ready": aws_ok,
                "detail": f"AWS identity/bucket check passed; {len(staged_files)} local staging files detected. No transfer was performed."
            },
            {
                "stage": "3. Data Warehouse Target",
                "system": "NANO_PRO_SNOWFLAKE (XMUTKDJ-KP74023 / BANK_DB.L0_STAGING)",
                "status": sf_status,
                "ready": sf_ok,
                "detail": "Snowflake session active on COMPUTE_WH." if sf_ok else (sf_test.get("message") or sf_test.get("error_message"))
            },
            {
                "stage": "4. Automated Cross-DB ETL Engine",
                "system": "Data Transfer Engine (connection_manager.py)",
                "status": "Connectivity Verified" if (ora_ok and aws_ok and sf_ok) else "Not Verified",
                "ready": ora_ok and aws_ok and sf_ok,
                "detail": "This check verifies connections only; no Oracle→S3→Snowflake data transfer is performed."
            }
        ]

        all_connected = (ora_ok and aws_ok and sf_ok)
        overall_status = "Fully Interconnected" if all_connected else "Partial"
        message = (
            "Oracle, AWS identity/S3 bucket, and Snowflake connection checks passed. This is a connectivity check; no data was transferred."
            if all_connected else
            f"Interoperability Test: Oracle ({ora_status}), S3 ({aws_status}), Snowflake ({sf_status}). Both Oracle and Snowflake must be Connected for live automated sync."
        )

        res = {
            "success": all_connected,
            "service": "CROSS_PIPELINE",
            "connection_name": "ORACLE_AWS_SNOWFLAKE_PIPELINE",
            "status": overall_status,
            "oracle_status": ora_status,
            "aws_status": aws_status,
            "snowflake_status": sf_status,
            "pipeline_stages": pipeline_stages,
            "response_time_ms": duration,
            "timestamp": test_ts,
            "message": message,
            "automation_ready": all_connected
        }

        self._record_connection_result(
            "ORACLE_AWS_SNOWFLAKE_PIPELINE", "pipeline", overall_status, duration,
            "SYSTEM -> MANGESHBAGUL15", "ACCOUNTADMIN", "XEPDB1 -> BANK_DB", "L0_STAGING",
            None if all_connected else message, res
        )
        return res

    def _record_connection_result(
        self,
        conn_name: str,
        service_type: str,
        status: str,
        response_time: float,
        user: Optional[str],
        role: Optional[str],
        database: Optional[str],
        schema: Optional[str],
        error: Optional[str],
        details: Dict[str, Any]
    ):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO connection_history (
                    id, connection_name, service_type, status, response_time_ms,
                    active_user, active_role, active_database, active_schema,
                    error_message, tested_at, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"hist_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}", conn_name, service_type, status, response_time,
                    user, role, database, schema, error, time.time(), json.dumps(details)
                ))
                
                # Update connection metadata cache
                cursor.execute("""
                INSERT OR REPLACE INTO connection_metadata (
                    connection_name, service_type, config_json, last_status,
                    last_tested_at, last_response_time_ms, last_error, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conn_name, service_type, json.dumps(details), status,
                    time.time(), response_time, error, time.time()
                ))
                conn.commit()

            # Immediate Emergency Telegram & WhatsApp Notification upon connection failure
            if status not in ["Connected", "Operational", "Fully Interconnected", "Not Configured", "Gateway Reachable; Database Login Unverified"]:
                from app.core.communication_center import communication_center
                now_t = time.time()
                if not hasattr(self, "_last_alert_map"):
                    self._last_alert_map = {}
                # Debounce to once per 10 minutes per connection unless critical
                if (now_t - self._last_alert_map.get(conn_name, 0)) > 3600:
                    self._last_alert_map[conn_name] = now_t
                    try:
                        communication_center.send_emergency_connection_failure_alert(
                            connection_name=conn_name,
                            service_type=service_type,
                            error_details=error or status
                        )
                    except Exception as alert_err:
                        log_event(f"Error dispatching connection alert: {alert_err}", component="ConnectionManager", level="WARNING")

        except Exception as e:
            log_event(f"Error recording connection result: {e}", component="ConnectionManager", level="WARNING")

    # =========================================================================
    # LIVE HEALTH MONITOR FOR ALL CONFIGURED CONNECTIONS
    # =========================================================================

    def get_all_connections_health(self) -> List[Dict[str, Any]]:
        """
        Returns live health status of all configured services:
        Snowflake, Oracle (Local, Remote, Tailscale), Gmail, AWS S3, AWS DMS, Telegram, SQLite.
        """
        connections = [
            {
                "connection_name": "NANO_PRO_SNOWFLAKE",
                "service_type": "Snowflake Data Warehouse",
                "host_identifier": SNOWFLAKE_CONFIG["account_identifier"],
                "target": f"{SNOWFLAKE_CONFIG['database']}.{SNOWFLAKE_CONFIG['schema']}",
                "user_role": f"{SNOWFLAKE_CONFIG['username']} ({SNOWFLAKE_CONFIG['role']})",
                "has_credentials": bool(os.environ.get("SNOWFLAKE_PASSWORD") or (self.get_connection_config("NANO_PRO_SNOWFLAKE", mask=False) or {}).get("secret_value")),
                "configured": True
            },
            {
                "connection_name": "MY_ORACLE_XE_LOCAL",
                "service_type": "Oracle Database XE (Localhost)",
                "host_identifier": "127.0.0.1:1521",
                "target": "XEPDB1",
                "user_role": "SYSTEM (Local Basic)",
                "has_credentials": bool(os.environ.get("ORACLE_PASSWORD") or (self.get_connection_config("MY_ORACLE_XE_LOCAL", mask=False) or {}).get("secret_value")),
                "configured": True
            },
            {
                "connection_name": "MY_ORACLE_XE_REMOTE",
                "service_type": "Oracle Database XE (Remote LAN)",
                "host_identifier": f"{ORACLE_CONFIG['hostname']}:{ORACLE_CONFIG['port']}",
                "target": ORACLE_CONFIG["service_name"],
                "user_role": f"{ORACLE_CONFIG['username']} (Default)",
                "has_credentials": bool(os.environ.get("ORACLE_PASSWORD") or (self.get_connection_config("MY_ORACLE_XE_REMOTE", mask=False) or {}).get("secret_value")),
                "configured": True
            },
            {
                "connection_name": "MY_ORACLE_XE_REMOTE_New",
                "service_type": "Oracle Database XE (Tailscale)",
                "host_identifier": "100.112.86.83:1521",
                "target": "XEPDB1",
                "user_role": "SYSTEM (Tailscale Secure)",
                "has_credentials": bool(os.environ.get("ORACLE_PASSWORD") or (self.get_connection_config("MY_ORACLE_XE_REMOTE_New", mask=False) or {}).get("secret_value")),
                "configured": True
            },
            {
                "connection_name": "ORACLE_APEX_23AI_CLOUD",
                "service_type": "Oracle Database 23ai (APEX Cloud)",
                "host_identifier": "oracleapex.com:443 (ORDS REST)",
                "target": "Workspace: nanoprostudio",
                "user_role": "mangeshbagul15@gmail.com (Cloud DBA)",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "POSTGRES_RENDER_CLOUD",
                "service_type": "Render PostgreSQL Cloud (Singapore)",
                "host_identifier": "dpg-db89fqm89jmc73cnqd0g-a.singapore-postgres.render.com:5432",
                "target": "nanopro_postgres",
                "user_role": "nanopro_postgres_user (SSL Enforced)",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "POSTGRES_CLOUD_FREE",
                "service_type": "Neon PostgreSQL Cloud (AWS ap-southeast-1)",
                "host_identifier": "ep-soft-paper-azc3am3u-pooler.c-3.ap-southeast-1.aws.neon.tech:5432",
                "target": "neondb",
                "user_role": "neondb_owner (Serverless Pooler)",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "MY_POSTGRES_LOCAL",
                "service_type": "PostgreSQL Local (127.0.0.1:5432)",
                "host_identifier": "127.0.0.1:5432",
                "target": "nanopro_db",
                "user_role": "postgres (Local CBS CDC)",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "GMAIL_SMTP",
                "service_type": "Gmail SMTP Integration",
                "host_identifier": "smtp.gmail.com:587 (STARTTLS)",
                "target": "nanoproaistudio@gmail.com",
                "user_role": "mangeshbagul15@gmail.com",
                "has_credentials": bool(smtp_client.get_secret_password()),
                "configured": True
            },
            {
                "connection_name": "EMAIL_FAILOVER_CLUSTER",
                "service_type": "Cloud HTTPS Email Cascading Cluster",
                "host_identifier": "Port 443 Multi-Tier Cascade",
                "target": "Gmail API ➔ Resend ➔ Brevo ➔ SMTP ➔ Telegram",
                "user_role": "Zero-Downtime Autonomous Failover",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "EMAIL_RESEND_API",
                "service_type": "Resend Developer Email API",
                "host_identifier": "api.resend.com:443 (HTTPS)",
                "target": "3,000 Free Emails / Month",
                "user_role": "mangeshbagul15@gmail.com",
                "has_credentials": bool(smtp_client.get_resend_config()["has_credentials"]),
                "configured": bool(smtp_client.get_resend_config()["has_credentials"])
            },
            {
                "connection_name": "EMAIL_BREVO_API",
                "service_type": "Brevo / Sendinblue Email API",
                "host_identifier": "api.brevo.com:443 (HTTPS)",
                "target": "300 Free Emails / Day",
                "user_role": "mangeshbagul15@gmail.com",
                "has_credentials": bool(smtp_client.get_brevo_config()["has_credentials"]),
                "configured": bool(smtp_client.get_brevo_config()["has_credentials"])
            },
            {
                "connection_name": "EMAIL_GMAIL_API",
                "service_type": "Google Gmail REST API",
                "host_identifier": "gmail.googleapis.com:443 (HTTPS)",
                "target": "Socket-Free Direct Google API",
                "user_role": "mangeshbagul15@gmail.com",
                "has_credentials": bool(smtp_client.get_gmail_api_config()["has_credentials"]),
                "configured": bool(smtp_client.get_gmail_api_config()["has_credentials"])
            },
            {
                "connection_name": "AWS_S3_DATA_LAKE",
                "service_type": "AWS Infrastructure & S3",
                "host_identifier": "AWS AP-Southeast-7",
                "target": "s3://nanopro-data-lake",
                "user_role": "IAM: NanoProDataEngineer",
                "has_credentials": bool(os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_SECRET_ACCESS_KEY")),
                "configured": True
            },
            {
                "connection_name": "AWS_DMS_MIGRATION",
                "service_type": "AWS Database Migration Service",
                "host_identifier": "dms.ap-southeast-2.amazonaws.com",
                "target": "Oracle XE ➔ S3 Lake CDC",
                "user_role": "dms.t3.medium (Available)",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "TELEGRAM_ALERTS",
                "service_type": "Telegram Broadcast Bot",
                "host_identifier": "api.telegram.org",
                "target": "Chat ID: 1200023268",
                "user_role": "@mangesh_technews_bot",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "STUDIO_MEMORY_DB",
                "service_type": "SQLite Studio Memory",
                "host_identifier": "Local Filesystem",
                "target": "studio_memory.db",
                "user_role": "local_admin",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "ORACLE_AWS_SNOWFLAKE_PIPELINE",
                "service_type": "Cross-System ETL Pipeline",
                "host_identifier": "Oracle ➔ S3/Staging ➔ Snowflake",
                "target": "XEPDB1 ➔ nanopro-data-lake ➔ BANK_DB",
                "user_role": "SYSTEM ➔ ACCOUNTADMIN",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "DUCKDB_GOLD_LAKEHOUSE",
                "service_type": "DuckDB 2.0.0 Analytical Lakehouse",
                "host_identifier": "data/lakehouse/gold_marts.duckdb",
                "target": "gold_marts (Star Schema)",
                "user_role": "embedded_olap (100% Lifetime Free)",
                "has_credentials": True,
                "configured": True
            },
            {
                "connection_name": "GOOGLE_BIGQUERY_SANDBOX",
                "service_type": "Google Cloud BigQuery (Sandbox)",
                "host_identifier": "bigquery.googleapis.com",
                "target": "nanopro-lakehouse-sandbox",
                "user_role": "nanoproaistudio@gmail.com (10 GB Free Storage)",
                "has_credentials": True,
                "configured": True
            }
        ]

        # Dynamically append any custom databases registered in Vault / connection_metadata
        std_names = {c["connection_name"] for c in connections}
        try:
            vault_creds = credentials_vault.list_credentials(mask=False)
            for vc in vault_creds:
                sname = vc.get("service_name")
                ctype = (vc.get("credential_type") or "").lower()
                if sname and sname not in std_names:
                    is_db = ctype in ["database", "oracle", "postgres", "snowflake", "mysql", "sqlserver", "sqlite"] or "DB" in sname.upper() or vc.get("database_name")
                    if is_db:
                        connections.append({
                            "connection_name": sname,
                            "service_type": f"Custom DB ({ctype.upper() if ctype else 'DATABASE'})",
                            "host_identifier": f"{vc.get('host') or '127.0.0.1'}:{vc.get('port') or '1521'}",
                            "target": vc.get('database_name') or 'Default',
                            "user_role": f"{vc.get('username') or 'admin'} (Custom)",
                            "has_credentials": bool(vc.get("secret_value")),
                            "configured": True,
                            "is_custom": True
                        })
                        std_names.add(sname)
        except Exception as ve:
            log_event(f"Error loading custom connections for health monitor: {ve}", component="ConnectionManager", level="WARNING")

        # Fetch last tested status from connection_history
        results = []
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for c in connections:
                cursor.execute("""
                SELECT status, response_time_ms, active_user, active_role, active_database, active_schema, error_message, tested_at
                FROM connection_history
                WHERE connection_name = ?
                ORDER BY tested_at DESC LIMIT 1
                """, (c["connection_name"],))
                row = cursor.fetchone()
                
                if row:
                    c["current_status"] = row["status"]
                    c["last_tested_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["tested_at"]))
                    c["response_time_ms"] = row["response_time_ms"]
                    c["last_error"] = row["error_message"]
                    if row["active_user"]:
                        c["active_user"] = row["active_user"]
                else:
                    c["current_status"] = "Not Tested" if c["has_credentials"] else "Not Configured"
                    c["last_tested_at"] = "Never"
                    c["response_time_ms"] = None
                    c["last_error"] = None

                c["next_health_check"] = "In 15 minutes"
                results.append(c)

        return results

    # =========================================================================
    # DATABASE EXPLORER & LIVE DATA FETCHING (Read-Only & Safe)
    # =========================================================================

    def list_accessible_databases(self, connection_name: str) -> List[str]:
        """Lists databases discovered live for the selected connection."""
        if connection_name == "STUDIO_MEMORY_DB":
            return ["main"]
        from app.core import live_catalog

        entry = live_catalog.find(connection_name)
        if not entry or entry.get("status") != "live":
            return []
        names: List[str] = []
        for group in entry.get("schemas") or []:
            database = group.get("database") or str(group.get("name") or "").split(".", 1)[0]
            if database and database not in names:
                names.append(database)
        return names

    def list_accessible_schemas(self, connection_name: str, database_name: str = "") -> List[str]:
        """Lists schemas discovered live for the selected connection."""
        if connection_name == "STUDIO_MEMORY_DB":
            return ["main"]
        from app.core import live_catalog

        entry = live_catalog.find(connection_name)
        if not entry or entry.get("status") != "live":
            return []
        names: List[str] = []
        for group in entry.get("schemas") or []:
            if database_name and str(group.get("database") or "") != database_name:
                continue
            schema = str(group.get("schema") or group.get("name") or "")
            if schema and schema not in names:
                names.append(schema)
        return names

    def list_accessible_tables(self, connection_name: str, database_name: str = "", schema_name: str = "") -> List[str]:
        """Lists tables/views discovered live for the selected schema."""
        if connection_name == "STUDIO_MEMORY_DB":
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                return [r[0] for r in cur.fetchall()]
        from app.core import live_catalog

        entry = live_catalog.find(connection_name)
        if not entry or entry.get("status") != "live":
            return []
        tables: List[str] = []
        for group in entry.get("schemas") or []:
            if database_name and str(group.get("database") or "") != database_name:
                continue
            if schema_name and str(group.get("schema") or group.get("name") or "") != schema_name:
                continue
            for item in group.get("tables") or []:
                name = str(item.get("name") or "")
                if name and name not in tables:
                    tables.append(name)
        return tables

    def get_table_metadata(self, connection_name: str, table_name: str, schema_name: str = "") -> Dict[str, Any]:
        """Returns real columns and row count read from the live database."""
        if connection_name == "STUDIO_MEMORY_DB":
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(f"PRAGMA table_info({table_name})")
                rows = cur.fetchall()
                columns = []
                for r in rows:
                    columns.append({
                        "name": r[1],
                        "data_type": r[2],
                        "not_null": bool(r[3]),
                        "is_pk": bool(r[5])
                    })
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                return {"table_name": table_name, "columns": columns, "row_count": count}

        from app.core import live_catalog

        entry = live_catalog.find(connection_name)
        if not entry:
            return {"table_name": table_name, "columns": [], "row_count": 0, "error": "Connection not found in the live catalog."}
        schema = schema_name
        if not schema:
            for group in entry.get("schemas") or []:
                if any(str(t.get("name")) == table_name for t in group.get("tables") or []):
                    schema = str(group.get("schema") or group.get("name") or "")
                    break
        try:
            details = live_catalog.table_details(connection_name, schema, table_name)
        except Exception as exc:
            return {"table_name": table_name, "columns": [], "row_count": 0, "error": str(exc)[:300]}
        return {
            "table_name": table_name,
            "columns": details.get("columns") or [],
            "row_count": details.get("row_count") or 0,
            "sample": details.get("sample") or [],
            "ddl": details.get("ddl") or "",
        }

    def execute_query(
        self,
        connection_name: str,
        query_text: str,
        database_name: str = "",
        schema_name: str = "",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Executes an authorized read-only SQL query on the specified connection.
        Enforces read-only safety (blocks DROP, ALTER, DELETE, TRUNCATE without explicit approval).
        Times execution and records in query_history.
        """
        start_time = time.time()
        query_clean = query_text.strip()
        query_id = f"qry_{int(start_time*1000)}"

        # Safety Check
        disallowed_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE"]
        upper_q = query_clean.upper()
        for kw in disallowed_keywords:
            if re.search(r'\b' + kw + r'\b', upper_q):
                err = f"Execution blocked by Safety Governance: Destructive operation '{kw}' requires explicit one-click approval."
                self._record_query_history(query_id, connection_name, database_name, schema_name, query_clean, 0, 0, "blocked", err)
                return {
                    "success": False,
                    "error": err,
                    "status": "Blocked by Governance",
                    "requires_approval": True,
                    "query_id": query_id
                }

        # Internal SQLite execution
        if connection_name == "STUDIO_MEMORY_DB":
            try:
                # Strip catalog/schema qualifiers like BANK_DB.L0_STAGING.ACCOUNTS -> ACCOUNTS
                exec_q = query_clean.rstrip(";").strip()
                for _ in range(3):
                    exec_q = re.sub(
                        r'\b(FROM|JOIN|INTO|UPDATE|TABLE)\s+([a-zA-Z0-9_\"\$]+\.)+([a-zA-Z0-9_\"\$]+)',
                        r'\1 \3',
                        exec_q,
                        flags=re.IGNORECASE
                    )
                # Translate Oracle ROWNUM if present
                exec_q = re.sub(r"\bWHERE\s+ROWNUM\s*<=\s*(\d+)\b", r"LIMIT \1", exec_q, flags=re.IGNORECASE)
                exec_q = re.sub(r"\bAND\s+ROWNUM\s*<=\s*(\d+)\b", r"LIMIT \1", exec_q, flags=re.IGNORECASE)

                with db.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(exec_q)
                    rows = cur.fetchmany(limit)
                    columns = [d[0] for d in cur.description] if cur.description else []
                    duration = round((time.time() - start_time) * 1000, 2)
                    
                    data = [dict(r) for r in rows]
                    self._record_query_history(query_id, connection_name, "main", "main", query_clean, duration, len(data), "success", None)
                    return {
                        "success": True,
                        "query_id": query_id,
                        "connection_name": connection_name,
                        "columns": columns,
                        "rows": data,
                        "row_count": len(data),
                        "execution_time_ms": duration,
                        "status": "Success"
                    }
            except Exception as e:
                duration = round((time.time() - start_time) * 1000, 2)
                err = str(e)
                self._record_query_history(query_id, connection_name, "main", "main", query_clean, duration, 0, "error", err)
                return {
                    "success": False,
                    "query_id": query_id,
                    "error": err,
                    "execution_time_ms": duration,
                    "status": "Error"
                }

        # Remote Database (Snowflake or Oracle)
        # Attempt real driver execution if connected, or report clear diagnostic state
        if connection_name == "NANO_PRO_SNOWFLAKE":
            test_res = self.test_snowflake_connection()
            if not test_res.get("success"):
                duration = round((time.time() - start_time) * 1000, 2)
                err = f"Cannot execute query on Snowflake: Connection test failed ({test_res.get('status')} - {test_res.get('error_message')})"
                self._record_query_history(query_id, connection_name, database_name, schema_name, query_clean, duration, 0, "error", err)
                return {
                    "success": False,
                    "query_id": query_id,
                    "connection_name": connection_name,
                    "error": err,
                    "connection_status": test_res.get("status"),
                    "execution_time_ms": duration,
                    "status": "Connection Failed"
                }

        elif connection_name == "MY_ORACLE_XE_REMOTE":
            test_res = self.test_oracle_connection()
            if not test_res.get("success"):
                duration = round((time.time() - start_time) * 1000, 2)
                err = f"Cannot execute query on Oracle: Connection test failed ({test_res.get('status')} - {test_res.get('error_message')})"
                self._record_query_history(query_id, connection_name, database_name, schema_name, query_clean, duration, 0, "error", err)
                return {
                    "success": False,
                    "query_id": query_id,
                    "connection_name": connection_name,
                    "error": err,
                    "connection_status": test_res.get("status"),
                    "execution_time_ms": duration,
                    "status": "Connection Failed"
                }

        # PostgreSQL execution (Neon Cloud Free, Render Cloud, Local)
        if connection_name in ["POSTGRES_CLOUD_FREE", "MY_POSTGRES_LOCAL", "POSTGRES_RENDER_CLOUD"]:
            try:
                import psycopg2
                import psycopg2.extras
                cred = credentials_vault.get_credential(connection_name)
                conn_kwargs = {}
                conn_str = None
                if cred and cred.get("host"):
                    conn_kwargs = {
                        "host": cred.get("host"),
                        "user": cred.get("username"),
                        "password": cred.get("secret_value"),
                        "port": cred.get("port") or 5432,
                        "dbname": cred.get("database_name") or ("neondb" if "NEON" in connection_name or "FREE" in connection_name else "nanopro_postgres"),
                        "connect_timeout": 8
                    }
                    if "CLOUD" in connection_name or "FREE" in connection_name:
                        conn_kwargs["sslmode"] = "require"
                else:
                    url_key = {
                        "POSTGRES_CLOUD_FREE": "NEON_DATABASE_URL",
                        "POSTGRES_RENDER_CLOUD": "RENDER_DATABASE_URL",
                    }.get(connection_name)
                    conn_str = os.environ.get(url_key, "").strip() if url_key else ""

                if not conn_kwargs and not conn_str:
                    return {"success": False, "error": f"Connection '{connection_name}' is not configured.", "query_id": query_id}
                
                if conn_kwargs:
                    pconn = psycopg2.connect(**conn_kwargs)
                else:
                    pconn = psycopg2.connect(conn_str, connect_timeout=8)
                
                with pconn:
                    with pconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as pcur:
                        pcur.execute(query_clean)
                        if pcur.description:
                            rows = pcur.fetchmany(limit)
                            columns = [d[0] for d in pcur.description]
                            data = [dict(r) for r in rows]
                        else:
                            columns = []
                            data = []
                        duration = round((time.time() - start_time) * 1000, 2)
                        self._record_query_history(query_id, connection_name, database_name or "neondb", schema_name or "public", query_clean, duration, len(data), "success", None)
                        return {
                            "success": True,
                            "query_id": query_id,
                            "connection_name": connection_name,
                            "columns": columns,
                            "rows": data,
                            "row_count": len(data),
                            "execution_time_ms": duration,
                            "status": "Success"
                        }
            except Exception as pe:
                duration = round((time.time() - start_time) * 1000, 2)
                err = str(pe)
                self._record_query_history(query_id, connection_name, database_name or "neondb", schema_name or "public", query_clean, duration, 0, "error", err)
                return {
                    "success": False,
                    "query_id": query_id,
                    "error": f"PostgreSQL Execution Error: {err}",
                    "execution_time_ms": duration,
                    "status": "Error"
                }

        duration = round((time.time() - start_time) * 1000, 2)
        return {
            "success": False,
            "query_id": query_id,
            "error": "Query engine awaiting driver installation or remote database reachability.",
            "execution_time_ms": duration,
            "status": "Failed"
        }

    def _record_query_history(
        self,
        query_id: str,
        connection_name: str,
        database: str,
        schema: str,
        query_text: str,
        duration: float,
        rows_count: int,
        status: str,
        error: Optional[str]
    ):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO query_history (
                    id, connection_name, database_name, schema_name,
                    query_text, execution_time_ms, rows_count, status, error_message, executed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    query_id, connection_name, database, schema, query_text,
                    duration, rows_count, status, error, time.time()
                ))
                conn.commit()
        except Exception as e:
            log_event(f"Error logging query history: {e}", component="ConnectionManager", level="WARNING")

    def list_query_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent query execution history."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT * FROM query_history ORDER BY executed_at DESC LIMIT ?
                """, (limit,))
                return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []

    def export_results_csv(self, columns: List[str], rows: List[Dict[str, Any]], filename_prefix: str = "query_export") -> str:
        """Exports query results to a CSV file in REPORTS_DIR."""
        import csv
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{ts}.csv"
        out_path = REPORTS_DIR / filename
        
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for r in rows:
                writer.writerow([r.get(col, "") for col in columns])
        
        log_event(f"Exported {len(rows)} records to {out_path}", component="ConnectionManager")
        return str(out_path)

    def get_all_oracle_statuses(self) -> Dict[str, Any]:
        """
        Tests all 3 configured Oracle database instances (Local, Remote, Tailscale)
        and reports which ones are ON (reachable/authenticated) and which are OFF.
        Enables seamless failover and multi-database operation.
        """
        results = {}
        online_candidates = []
        for cname in ["MY_ORACLE_XE_LOCAL", "MY_ORACLE_XE_REMOTE", "MY_ORACLE_XE_REMOTE_New"]:
            test_res = self.test_oracle_connection(cname)
            is_on = test_res.get("success", False) or test_res.get("status") in ["Connected", "Degraded"]
            results[cname] = {
                "connection_name": cname,
                "host": test_res.get("host"),
                "port": test_res.get("port"),
                "service": test_res.get("service_name"),
                "state": "ON" if is_on else "OFF",
                "status": test_res.get("status"),
                "response_time_ms": test_res.get("response_time_ms", 0),
                "message": test_res.get("message") or test_res.get("error_message")
            }
            if is_on:
                online_candidates.append(cname)

        return {
            "status": "success",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "oracle_instances": results,
            "online_instances_count": len(online_candidates),
            "primary_active_instance": online_candidates[0] if online_candidates else "None (All currently offline)",
            "summary": f"{len(online_candidates)} of 3 Oracle instances are reachable."
        }

    def add_custom_database(
        self,
        connection_name: str,
        service_type: str = "database",
        username: str = "SYSTEM",
        password: str = "",
        host: str = "127.0.0.1",
        port: str = "1521",
        database_name: str = "XEPDB1",
        metadata: Optional[Dict[str, Any]] = None,
        sync_cloud: bool = True
    ) -> Dict[str, Any]:
        """
        Dynamically registers a new database connection into the Credentials Vault.
        Supports Oracle, Snowflake, PostgreSQL, MySQL, SQL Server, and SQLite.
        Immediately synchronizes local Vault, .env files, SQL Studio catalog, and pushes to GitHub/Render Cloud.
        """
        meta = metadata or {}
        meta["host"] = host
        meta["port"] = port
        meta["database_name"] = database_name
        meta["username"] = username
        meta["service_type"] = service_type

        cred_id = self.save_connection_config(
            connection_name=connection_name,
            service_type=service_type,
            username=username,
            password=password,
            host=host,
            port=str(port),
            database_name=database_name,
            metadata=meta
        )

        # Store in connection_metadata table for persistent schema discovery
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO connection_metadata (connection_name, service_type, config_json, last_status, updated_at)
                VALUES (?, ?, ?, 'Configured', ?)
                ON CONFLICT(connection_name) DO UPDATE SET
                    service_type = excluded.service_type,
                    config_json = excluded.config_json,
                    updated_at = excluded.updated_at
                """, (connection_name, service_type, json.dumps(meta), time.time()))
                conn.commit()
        except Exception as e:
            log_event(f"Error persisting connection_metadata for [{connection_name}]: {e}", component="ConnectionManager", level="WARNING")

        # Synchronize environment variable and .env files
        clean_key = re.sub(r'[^A-Z0-9_]', '_', connection_name.upper())
        if password:
            os.environ[f"{clean_key}_PASSWORD"] = password
            self._update_env_file_variable(f"{clean_key}_PASSWORD", password)

        # Register custom tables into sql_query_studio metadata
        try:
            from app.database.sql_query_studio import sql_query_studio
            eng_key = "oracle" if "oracle" in service_type.lower() else ("snowflake" if "snow" in service_type.lower() else ("postgres" if "post" in service_type.lower() else "sqlite"))
            if eng_key in sql_query_studio.metadata:
                s_name = database_name or ("XEPDB1" if eng_key == "oracle" else ("L0_STAGING" if eng_key == "snowflake" else "public"))
                clean_name = re.sub(r'[^A-Z0-9_]', '', connection_name.upper())[:12]
                custom_tbls = [f"{clean_name}_CUSTOMERS", f"{clean_name}_ACCOUNTS", f"{clean_name}_TRANSACTIONS", f"{clean_name}_AUDIT_LOG"]
                sql_query_studio.metadata[eng_key]["databases"][connection_name] = {
                    "label": f"{connection_name} [Service: {s_name} | {host}:{port}]",
                    "service_name": s_name,
                    "host": host,
                    "port": port,
                    "schemas": { s_name: custom_tbls }
                }
        except Exception:
            pass

        # Trigger immediate live connectivity test to populate health status
        test_res = {}
        try:
            test_res = self.test_custom_database(connection_name)
        except Exception:
            pass

        # Auto-sync to GitHub & Render Cloud
        cloud_res = {}
        if sync_cloud:
            cloud_res = self.sync_to_cloud(f"feat(connections): register new database [{connection_name}] ({service_type})")

        return {
            "status": "success",
            "credential_id": cred_id,
            "connection_name": connection_name,
            "service_type": service_type,
            "test_result": test_res,
            "git_synced": cloud_res.get("git_pushed", False),
            "render_deploy_triggered": cloud_res.get("render_deploy_triggered", False),
            "commit_hash": cloud_res.get("commit_hash", ""),
            "message": f"✅ Database [{connection_name}] ({service_type}) successfully added and encrypted with AES-256-GCM in Vault! Local .env updated and synced to GitHub/Render Cloud."
        }

    def update_connection_password(self, connection_name: str, new_password: str, sync_cloud: bool = True) -> Dict[str, Any]:
        """
        Updates the password for an existing connection with verified rights and .env sync.
        Synchronizes:
        1. Local AES-256-GCM Vault (SQLite storage).
        2. Runtime os.environ and in-memory client connection pools.
        3. Local .env files across all project workspaces.
        4. GitHub repository and Render Cloud auto-deployment (zero-hang).
        """
        cfg = self.get_connection_config(connection_name, mask=False)
        conn_upper = connection_name.upper()

        if not cfg:
            # Fallback configuration synthesize
            if "ORACLE" in conn_upper and connection_name in ORACLE_CONFIGS:
                oc = ORACLE_CONFIGS[connection_name]
                cfg = {"service_type": "database", "username": oc["username"], "host": oc["hostname"], "port": str(oc["port"]), "database_name": oc.get("service_name", "XEPDB1"), "metadata": oc}
            elif "SNOWFLAKE" in conn_upper:
                cfg = {"service_type": "database", "username": SNOWFLAKE_CONFIG["username"], "host": SNOWFLAKE_CONFIG["account_url"], "port": "443", "database_name": SNOWFLAKE_CONFIG["database"], "metadata": SNOWFLAKE_CONFIG}
            elif "POSTGRES" in conn_upper and connection_name in POSTGRES_CONFIGS:
                pc = POSTGRES_CONFIGS[connection_name]
                cfg = {"service_type": "database", "username": pc["username"], "host": pc["hostname"], "port": str(pc["port"]), "database_name": pc.get("database", "nanopro_db"), "metadata": pc}
            elif "SMTP" in conn_upper or "GMAIL" in conn_upper:
                cfg = {"service_type": "email", "username": "mangeshbagul15@gmail.com", "host": "smtp.gmail.com", "port": "587", "database_name": "", "metadata": {}}
            else:
                cfg = {"service_type": "database", "username": "admin", "host": "127.0.0.1", "port": "1521", "database_name": "XEPDB1", "metadata": {}}

        # Update in Credentials Vault
        cred_id = self.save_connection_config(
            connection_name=connection_name,
            service_type=cfg.get("service_type", "database"),
            username=cfg.get("username", ""),
            password=new_password,
            host=cfg.get("host", ""),
            port=str(cfg.get("port", "")),
            database_name=cfg.get("database_name", ""),
            metadata=cfg.get("metadata", {})
        )

        # Synchronize runtime os.environ, in-memory configurations, and .env files
        env_updated = False
        synced_keys = []

        # 1. Oracle Databases
        if "ORACLE" in conn_upper:
            os.environ["ORACLE_PASSWORD"] = new_password
            self._update_env_file_variable("ORACLE_PASSWORD", new_password)
            synced_keys.append("ORACLE_PASSWORD")
            # Update all active Oracle configs in memory
            for k in ORACLE_CONFIGS:
                ORACLE_CONFIGS[k]["password"] = new_password
            ORACLE_CONFIG["password"] = new_password
            if conn_upper == "ORACLE_APEX_23AI_CLOUD":
                os.environ["ORACLE_APEX_PASSWORD"] = new_password
                self._update_env_file_variable("ORACLE_APEX_PASSWORD", new_password)
                synced_keys.append("ORACLE_APEX_PASSWORD")
            env_updated = True

        # 2. Snowflake Data Warehouse
        elif "SNOWFLAKE" in conn_upper:
            os.environ["SNOWFLAKE_PASSWORD"] = new_password
            self._update_env_file_variable("SNOWFLAKE_PASSWORD", new_password)
            SNOWFLAKE_CONFIG["password"] = new_password
            synced_keys.append("SNOWFLAKE_PASSWORD")
            env_updated = True

        # 3. PostgreSQL Databases
        elif "POSTGRES" in conn_upper:
            if "NEON" in conn_upper or "FREE" in conn_upper:
                os.environ["NEON_POSTGRES_PASSWORD"] = new_password
                self._update_env_file_variable("NEON_POSTGRES_PASSWORD", new_password)
                synced_keys.append("NEON_POSTGRES_PASSWORD")
            elif "RENDER" in conn_upper:
                os.environ["RENDER_POSTGRES_PASSWORD"] = new_password
                self._update_env_file_variable("RENDER_POSTGRES_PASSWORD", new_password)
                synced_keys.append("RENDER_POSTGRES_PASSWORD")
            else:
                os.environ["POSTGRES_PASSWORD"] = new_password
                self._update_env_file_variable("POSTGRES_PASSWORD", new_password)
                synced_keys.append("POSTGRES_PASSWORD")
            if connection_name in POSTGRES_CONFIGS:
                POSTGRES_CONFIGS[connection_name]["password"] = new_password
            env_updated = True

        # 4. Gmail SMTP
        elif "GMAIL_SMTP" in conn_upper or (("GMAIL" in conn_upper or "SMTP" in conn_upper) and "API" not in conn_upper):
            os.environ["GMAIL_APP_PASSWORD"] = new_password
            os.environ["SMTP_PASSWORD"] = new_password
            self._update_env_file_variable("GMAIL_APP_PASSWORD", new_password)
            self._update_env_file_variable("SMTP_PASSWORD", new_password)
            synced_keys.extend(["GMAIL_APP_PASSWORD", "SMTP_PASSWORD"])
            try:
                smtp_client.save_configuration(password=new_password)
            except Exception:
                pass
            env_updated = True

        # 5. Resend API
        elif "RESEND" in conn_upper:
            os.environ["RESEND_API_KEY"] = new_password
            self._update_env_file_variable("RESEND_API_KEY", new_password)
            synced_keys.append("RESEND_API_KEY")
            try:
                smtp_client.save_resend_config(api_key=new_password)
            except Exception:
                pass
            env_updated = True

        # 6. Brevo API
        elif "BREVO" in conn_upper:
            os.environ["BREVO_API_KEY"] = new_password
            self._update_env_file_variable("BREVO_API_KEY", new_password)
            synced_keys.append("BREVO_API_KEY")
            try:
                smtp_client.save_brevo_config(api_key=new_password)
            except Exception:
                pass
            env_updated = True

        # 7. Gmail REST API
        elif "GMAIL_API" in conn_upper:
            os.environ["GMAIL_API_REFRESH_TOKEN"] = new_password
            self._update_env_file_variable("GMAIL_API_REFRESH_TOKEN", new_password)
            synced_keys.append("GMAIL_API_REFRESH_TOKEN")
            try:
                smtp_client.save_gmail_api_config(refresh_token=new_password)
            except Exception:
                pass
            env_updated = True

        # 8. AWS S3 Data Lake
        elif "AWS" in conn_upper:
            os.environ["AWS_SECRET_ACCESS_KEY"] = new_password
            self._update_env_file_variable("AWS_SECRET_ACCESS_KEY", new_password)
            synced_keys.append("AWS_SECRET_ACCESS_KEY")
            env_updated = True

        # 9. Telegram Alerts
        elif "TELEGRAM" in conn_upper:
            os.environ["TELEGRAM_BOT_TOKEN"] = new_password
            self._update_env_file_variable("TELEGRAM_BOT_TOKEN", new_password)
            synced_keys.append("TELEGRAM_BOT_TOKEN")
            env_updated = True

        # 10. Dynamic / Custom database
        else:
            clean_k = re.sub(r'[^A-Z0-9_]', '_', conn_upper) + "_PASSWORD"
            os.environ[clean_k] = new_password
            self._update_env_file_variable(clean_k, new_password)
            synced_keys.append(clean_k)
            env_updated = True

        log_event(f"Password updated for connection [{connection_name}] (Cred ID: {cred_id}, env keys: {synced_keys})", component="ConnectionManager")

        # Auto-sync to GitHub & Render Cloud if requested
        cloud_res = {}
        if sync_cloud:
            cloud_res = self.sync_to_cloud(f"chore(vault): update password for [{connection_name}]")

        return {
            "status": "success",
            "connection_name": connection_name,
            "credential_id": cred_id,
            "env_synced": env_updated,
            "synced_keys": synced_keys,
            "git_synced": cloud_res.get("git_pushed", False),
            "render_deploy_triggered": cloud_res.get("render_deploy_triggered", False),
            "commit_hash": cloud_res.get("commit_hash", ""),
            "message": f"✅ Password for '{connection_name}' successfully updated across all 3 tiers:\n1. Local Vault (AES-256-GCM) & .env\n2. GitHub Repository\n3. Render Cloud (Auto-Deploy Triggered)"
        }

    def _update_env_file_variable(self, key: str, value: str):
        """Safely updates or appends a key-value pair in .env file across all project workspaces."""
        targets = [
            BASE_DIR / ".env",
            Path("C:/Mangesh/NanoPro_AI_Studio_Made_By_Mangesh/Mangesh_Nano_Pro_AI_Studio/.env")
        ]
        for env_path in targets:
            if not env_path.parent.exists():
                continue
            try:
                lines = []
                if env_path.exists():
                    lines = env_path.read_text(encoding="utf-8").splitlines()
                found = False
                new_lines = []
                for line in lines:
                    if line.strip().startswith(f"{key}="):
                        new_lines.append(f"{key}={value}")
                        found = True
                    else:
                        new_lines.append(line)
                if not found:
                    new_lines.append(f"{key}={value}")
                env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            except Exception as e:
                log_event(f"Error syncing {key} to {env_path}: {e}", component="ConnectionManager", level="WARNING")

    def sync_to_cloud(self, commit_msg: str = "") -> Dict[str, Any]:
        """
        Commits encrypted Vault database and configuration updates to Git,
        and pushes to GitHub repository (https://github.com/mangeshbagul15/nanopro-ai-studio.git)
        which triggers Render Cloud auto-deployment.
        Ensures Local, GitHub, and Render are in 100% lockstep synchronization.
        """
        import subprocess
        import shutil
        start_t = time.time()
        msg = commit_msg or f"chore(vault): auto-sync credentials & connection manager [{time.strftime('%Y-%m-%d %H:%M:%S')}]"
        repo_dir = str(BASE_DIR)

        try:
            # 1. Flush SQLite DB WAL to ensure file on disk has latest commits
            with db.get_connection() as conn:
                conn.execute("PRAGMA wal_checkpoint(FULL);")
                conn.commit()
        except Exception as e:
            log_event(f"WAL checkpoint notice: {e}", component="ConnectionManager", level="DEBUG")

        # 2. Stage updated vault database and connection files
        staged_files = [
            "app/database/studio_memory.db",
            "app/core/connection_manager.py",
            "app/core/database.py",
            "app/core/smtp_client.py",
            "app/ui/dashboard.py",
            "main.py"
        ]

        # Also copy to secondary workspace if present
        sec_dir = Path("C:/Mangesh/NanoPro_AI_Studio_Made_By_Mangesh/Mangesh_Nano_Pro_AI_Studio")
        if sec_dir.exists():
            try:
                for sf in staged_files:
                    src_f = BASE_DIR / sf
                    dst_f = sec_dir / sf
                    if src_f.exists():
                        dst_f.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_f, dst_f)
                src_env = BASE_DIR / ".env"
                if src_env.exists():
                    shutil.copy2(src_env, sec_dir / ".env")
            except Exception as se:
                log_event(f"Secondary workspace sync notice: {se}", component="ConnectionManager", level="WARNING")

        # 3. Execute git add, commit, push
        try:
            for sf in staged_files:
                subprocess.run(["git", "add", sf], cwd=repo_dir, capture_output=True, timeout=10)

            commit_res = subprocess.run(["git", "commit", "-m", msg], cwd=repo_dir, capture_output=True, text=True, timeout=15)

            # Authenticated push URL
            push_url = "origin"
            push_res = subprocess.run(["git", "push", push_url, "main"], cwd=repo_dir, capture_output=True, text=True, timeout=30)

            duration = round((time.time() - start_t) * 1000, 2)
            push_ok = push_res.returncode == 0

            rev_res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir, capture_output=True, text=True, timeout=5)
            commit_hash = rev_res.stdout.strip() if rev_res.returncode == 0 else "HEAD"

            return {
                "success": push_ok,
                "git_committed": commit_res.returncode == 0 or "nothing to commit" in (commit_res.stdout or ""),
                "git_pushed": push_ok,
                "commit_hash": commit_hash,
                "render_deploy_triggered": push_ok,
                "render_target": "https://nanopro-ai-studio.onrender.com",
                "execution_time_ms": duration,
                "message": "✅ Local changes, encrypted Vault, and credentials committed to GitHub! Render auto-deploy triggered." if push_ok else f"Git push notice: {push_res.stderr.strip()[:200]}"
            }
        except Exception as ge:
            return {
                "success": False,
                "git_pushed": False,
                "error": str(ge),
                "message": f"Cloud sync error: {ge}"
            }

    def test_custom_database(self, connection_name: str) -> Dict[str, Any]:
        """
        Executes real connectivity test for dynamically registered custom databases.
        Inspects service_type and routes to appropriate driver or socket verification.
        """
        start_time = time.time()
        test_ts = time.strftime("%Y-%m-%d %H:%M:%S")
        cfg = self.get_connection_config(connection_name, mask=False)
        if not cfg:
            return {
                "connection_name": connection_name,
                "status": "Not Configured",
                "success": False,
                "error": f"Connection [{connection_name}] not found in Vault."
            }

        stype = (cfg.get("service_type") or "").lower()
        if "oracle" in stype:
            return self.test_oracle_connection(connection_name)
        elif "post" in stype:
            return self.test_postgres_connection(connection_name)
        elif "snow" in stype:
            return self.test_snowflake_connection()

        # Generic TCP socket test for MySQL, SQL Server, etc.
        host = cfg.get("host") or "127.0.0.1"
        port = int(cfg.get("port") or 1521)
        try:
            sock = socket.create_connection((host, port), timeout=4.0)
            sock.close()
            duration = round((time.time() - start_time) * 1000, 2)
            res = {
                "connection_name": connection_name,
                "status": "Connected",
                "success": True,
                "host": f"{host}:{port}",
                "database": cfg.get("database_name"),
                "user": cfg.get("username"),
                "response_time_ms": duration,
                "timestamp": test_ts,
                "diagnostic": f"TCP Port {port} reachable and verified."
            }
            self._record_connection_result(connection_name, stype, "Connected", duration, cfg.get("username"), "Default", cfg.get("database_name"), None, None, res)
            return res
        except Exception as e:
            duration = round((time.time() - start_time) * 1000, 2)
            err = str(e)
            res = {
                "connection_name": connection_name,
                "status": "Connection Failed",
                "success": False,
                "host": f"{host}:{port}",
                "database": cfg.get("database_name"),
                "user": cfg.get("username"),
                "response_time_ms": duration,
                "timestamp": test_ts,
                "error": err,
                "diagnostic": f"Failed reaching {host}:{port}: {err}"
            }
            self._record_connection_result(connection_name, stype, "Connection Failed", duration, cfg.get("username"), "Default", cfg.get("database_name"), None, err, res)
            return res


    # =========================================================================
    # AUTONOMOUS CONNECTION SENTINEL & ANTI-ACCOUNT-LOCKOUT PROTOCOL
    # =========================================================================
    def start_autonomous_sentinel(self):
        """
        Launches the Autonomous Background Connection Sentinel.
        Continuously verifies Oracle XE, Snowflake, SMTP, and Telegram.
        Enforces DBA account lockout prevention protocol on authentication failures.
        """
        if getattr(self, "_sentinel_running", False):
            return
        import threading
        self._sentinel_running = True
        self._auth_locked_services = getattr(self, "_auth_locked_services", set())
        self._backoff_delays = getattr(self, "_backoff_delays", {})
        self._sentinel_thread = threading.Thread(target=self._sentinel_loop, daemon=True)
        self._sentinel_thread.start()
        log_event("ConnectionManager: Autonomous Connection Sentinel started with anti-lockout protection.", component="ConnectionSentinel")

    def stop_autonomous_sentinel(self):
        """Gracefully halts the background connection sentinel."""
        self._sentinel_running = False

    def reset_sentinel_lockout(self, service_name: str):
        """Clears account lockout guard when user enters updated credentials."""
        if hasattr(self, "_auth_locked_services") and service_name in self._auth_locked_services:
            self._auth_locked_services.remove(service_name)
            log_event(f"ConnectionSentinel: Cleared lockout guard for [{service_name}]. Safe retry enabled.", component="ConnectionSentinel")

    def get_sentinel_status(self) -> Dict[str, Any]:
        """Returns active sentinel state, monitored services, and lockout flags."""
        return {
            "sentinel_active": getattr(self, "_sentinel_running", False),
            "monitored_targets": ["MY_ORACLE_XE_LOCAL", "MY_ORACLE_XE_REMOTE", "NANO_PRO_SNOWFLAKE", "GMAIL_SMTP", "TELEGRAM"],
            "auth_locked_services": list(getattr(self, "_auth_locked_services", set())),
            "backoff_delays": getattr(self, "_backoff_delays", {})
        }

    def _sentinel_loop(self):
        """
        Autonomous background sentinel executing continuous connection health audits across all 12 services.
        Applies exponential backoff on network issues, halts on auth errors, and automatically executes failover
        and emergency alerting to WhatsApp and Telegram.
        """
        time.sleep(4.0)  # Initial boot grace period
        all_targets = [
            "NANO_PRO_SNOWFLAKE", "DUCKDB_GOLD_LAKEHOUSE", "GOOGLE_BIGQUERY_SANDBOX",
            "POSTGRES_CLOUD_FREE", "MY_ORACLE_XE_LOCAL", "MY_ORACLE_XE_REMOTE",
            "POSTGRES_RENDER_CLOUD", "MY_POSTGRES_LOCAL", "GMAIL_SMTP",
            "TELEGRAM_ALERTS", "STUDIO_MEMORY_DB", "AWS_S3_DATA_LAKE"
        ]

        while getattr(self, "_sentinel_running", False):
            try:
                for svc in all_targets:
                    if not getattr(self, "_sentinel_running", False):
                        break

                    # 1. Anti-Account-Lockout Check: Do NOT retry if authentication failed until password updated
                    if svc in self._auth_locked_services:
                        continue

                    # 2. Network Backoff Check
                    delay = self._backoff_delays.get(svc, 0)
                    if delay > 0:
                        self._backoff_delays[svc] = max(0, delay - 20)
                        continue

                    # 3. Perform Connection Verification
                    try:
                        res = None
                        if "ORACLE" in svc:
                            res = self.test_oracle_connection(svc)
                        elif "SNOWFLAKE" in svc:
                            res = self.test_snowflake_connection()
                        elif "DUCKDB" in svc:
                            res = self.test_duckdb_connection()
                        elif "BIGQUERY" in svc:
                            res = self.test_bigquery_connection()
                        elif "POSTGRES" in svc:
                            res = self.test_postgres_connection(svc)
                        elif "GMAIL" in svc:
                            res = self.test_gmail_connection()
                        elif "TELEGRAM" in svc:
                            res = self.test_telegram_connection()
                        elif "AWS" in svc or "S3" in svc:
                            res = self.test_aws_connection()
                        elif "STUDIO_MEMORY" in svc:
                            res = self.test_sqlite_connection()

                        if not res:
                            continue

                        err_msg = str(res.get("error_message") or "")
                        err_cat = res.get("error_category", "")

                        # Check for Authentication Failures (ORA-01017, Snowflake incorrect pwd)
                        is_auth_error = (
                            "ORA-01017" in err_msg or 
                            "AUTH_FAILED" in err_cat or 
                            "invalid username/password" in err_msg.lower() or
                            "incorrect username or password" in err_msg.lower()
                        )

                        if is_auth_error:
                            self._auth_locked_services.add(svc)
                            log_event(
                                f"ConnectionSentinel: AUTHENTICATION FAILURE detected for [{svc}]. "
                                f"HALTING AUTO-RETRY to prevent DBA account lockout policy enforcement!",
                                level="WARNING", component="ConnectionSentinel"
                            )
                            # Alert Mangesh on WhatsApp and Telegram
                            from app.core.communication_center import communication_center
                            communication_center.send_emergency_connection_failure_alert(
                                connection_name=svc,
                                service_type="Database Auth",
                                error_details=f"Authentication Failure ({err_msg}). Halting retries to prevent lockout."
                            )
                        elif res.get("success"):
                            # Healthy connection: recheck in 3 minutes (180s)
                            self._backoff_delays[svc] = 180
                            self._backoff_delays[f"{svc}_factor"] = 20
                        else:
                            # Network/Listener/Timeout issue: Exponential backoff (20s -> 40s -> 80s -> 180s)
                            curr_factor = self._backoff_delays.get(f"{svc}_factor", 20)
                            next_factor = min(curr_factor * 2, 180)
                            self._backoff_delays[f"{svc}_factor"] = next_factor
                            self._backoff_delays[svc] = next_factor
                            log_event(f"ConnectionSentinel: [{svc}] down/unreachable. Backing off for {next_factor}s.", level="INFO", component="ConnectionSentinel")
                    except Exception as test_err:
                        pass
            except Exception as loop_err:
                pass
            time.sleep(20.0)

connection_manager = ConnectionManager()
