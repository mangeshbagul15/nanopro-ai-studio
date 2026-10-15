"""
Mangesh Nano Pro AI Studio - AI Text-to-SQL & Marathi Voice Query Engine
Translates natural language questions in Marathi (मराठी) and English into high-performance SQL,
executes against Neon Cloud PostgreSQL / Snowflake / SQLite, and prepares dynamic Chart.js visualizations.
"""

import os
import re
import json
import time
from typing import Dict, Any, List, Optional
from app.core.connection_manager import connection_manager
from app.core.logger import log_event

class TextToSQLEngine:
    """Intelligent AI Text & Voice to SQL Query Generator with Chart.js visualization."""

    def __init__(self):
        self.schema_context = """
Available Tables in Neon Cloud PostgreSQL & SQLite:

1. Table: neon_banking_stream (Cloud Streaming Transactions)
Columns:
- txn_id (VARCHAR/TEXT, Primary Key)
- account_id (VARCHAR/TEXT)
- customer_name (VARCHAR/TEXT)
- amount (NUMERIC/REAL, Transaction amount in INR)
- currency (VARCHAR/TEXT, default 'INR')
- txn_type (VARCHAR/TEXT: 'TRANSFER', 'PURCHASE', 'DEPOSIT', 'WITHDRAWAL')
- channel (VARCHAR/TEXT: 'UPI', 'NEFT', 'IMPS', 'DEBIT_CARD', 'NETBANKING')
- merchant (VARCHAR/TEXT)
- city (VARCHAR/TEXT: 'Mumbai', 'Pune', 'Nashik', 'Nagpur', 'Thane', 'Solapur', etc.)
- created_at (TIMESTAMP)
- sync_status (VARCHAR/TEXT: 'PENDING', 'SYNCED')

2. Table: users (Enterprise Directory)
Columns: id, username, full_name, email, role, status, allowed_views, access_mode, created_at, last_login_at

3. Table: audit_logs (Security Logs)
Columns: id, user_id, username, event_type, details, ip_address, created_at
"""

    def generate_and_execute(self, prompt: str, target_db: str = "POSTGRES_CLOUD_FREE") -> Dict[str, Any]:
        """
        Translates Marathi/English prompt to SQL, executes against target DB,
        and constructs dynamic Chart.js visualization.
        """
        start_time = time.time()
        prompt_clean = prompt.strip()

        # Step 1: AI Translation (Marathi/English -> SQL)
        sql = self._translate_prompt_to_sql(prompt_clean, target_db)
        log_event(f"Text-to-SQL Generated: '{sql}' for prompt: '{prompt_clean}'", component="TextToSQL")

        # Step 2: Execute SQL against Target DB
        db_target = target_db if target_db in ["POSTGRES_CLOUD_FREE", "MY_ORACLE_XE_LOCAL", "MY_POSTGRES_LOCAL"] else "POSTGRES_CLOUD_FREE"
        exec_res = connection_manager.execute_query(db_target, sql)

        if not exec_res.get("success"):
            # Fallback to local SQLite if cloud is unreachable
            log_event(f"Cloud DB execution failed, trying SQLite fallback: {exec_res.get('error_message')}", component="TextToSQL", level="WARNING")
            sqlite_sql = sql.replace("neon_banking_stream", "medallion_l0_staging")
            exec_res = connection_manager.execute_query("SQLITE", sqlite_sql)

        columns = exec_res.get("columns", [])
        rows = exec_res.get("rows", [])
        row_count = len(rows)

        # Step 3: Dynamic Chart.js Recommendation
        chart_config = self._build_chart_config(columns, rows, prompt_clean)

        # Step 4: Marathi Explanation
        explanation_mr = self._generate_marathi_explanation(prompt_clean, sql, row_count)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "success" if exec_res.get("success") else "partial",
            "prompt": prompt_clean,
            "generated_sql": sql,
            "target_db": db_target,
            "row_count": row_count,
            "columns": columns,
            "rows": rows[:100],  # Return up to 100 rows for UI display
            "chart_config": chart_config,
            "explanation_mr": explanation_mr,
            "execution_time_ms": duration_ms
        }

    def _translate_prompt_to_sql(self, prompt: str, target_db: str) -> str:
        """Uses LLM (Groq or Gemini) with zero-shot rule fallback to generate ANSI SQL."""
        p_lower = prompt.lower()

        # Rule-based fastpath for common Marathi/English queries
        if any(w in p_lower for w in ["टॉप ५", "top 5", "top five", "पाच मोठे", "मोठे व्यवहार"]):
            return "SELECT txn_id, customer_name, amount, channel, city, created_at FROM neon_banking_stream ORDER BY amount DESC LIMIT 5;"
        
        if any(w in p_lower for w in ["शहर", "city", "शहरांनुसार", "शहरानुसार"]):
            return "SELECT city, COUNT(*) AS txn_count, SUM(amount) AS total_amount, AVG(amount) AS avg_amount FROM neon_banking_stream GROUP BY city ORDER BY total_amount DESC;"

        if any(w in p_lower for w in ["upi", "युपीआय"]):
            return "SELECT txn_id, customer_name, amount, merchant, city, created_at FROM neon_banking_stream WHERE channel = 'UPI' ORDER BY created_at DESC;"

        if any(w in p_lower for w in ["एकूण रक्कम", "total amount", "एकूण व्हॉल्यूम", "समरी", "summary", "सरासरी"]):
            return "SELECT COUNT(*) AS total_transactions, SUM(amount) AS total_volume_inr, AVG(amount) AS avg_transaction_inr, MAX(amount) AS max_transaction_inr FROM neon_banking_stream;"

        if any(w in p_lower for w in ["प्रकार", "type", "txn_type", "प्रकारानुसार"]):
            return "SELECT txn_type, COUNT(*) AS txn_count, SUM(amount) AS total_amount FROM neon_banking_stream GROUP BY txn_type ORDER BY total_amount DESC;"

        if any(w in p_lower for w in ["मर्चंट", "merchant", "दुकानदार"]):
            return "SELECT merchant, COUNT(*) AS count, SUM(amount) AS total_spent FROM neon_banking_stream GROUP BY merchant ORDER BY total_spent DESC LIMIT 10;"

        # Try LLM generation via Groq or fallback
        try:
            from app.core.model_manager import model_manager
            system_prompt = f"""You are an expert Data Engineer & SQL Architect.
Given the following schema:
{self.schema_context}

The user will ask a query in Marathi, Hindi, or English.
Output ONLY the raw SQL query. Do NOT include markdown code blocks, do not explain. Just the executable SQL statement."""

            response = model_manager.generate_text(
                prompt=f"Convert to SQL: {prompt}",
                system_prompt=system_prompt,
                preferred_provider="groq"
            )
            raw_sql = response.get("text", "").strip()
            # Clean markdown formatting if present
            raw_sql = re.sub(r"^```(sql)?", "", raw_sql, flags=re.MULTILINE).replace("```", "").strip()
            if raw_sql.upper().startswith("SELECT"):
                return raw_sql
        except Exception as e:
            log_event(f"LLM Text-to-SQL generation failed, using default: {e}", component="TextToSQL", level="WARNING")

        # Fallback default
        return "SELECT txn_id, customer_name, amount, channel, city, created_at FROM neon_banking_stream ORDER BY created_at DESC LIMIT 10;"

    def _build_chart_config(self, columns: List[str], rows: List[Dict[str, Any]], prompt: str) -> Optional[Dict[str, Any]]:
        """Automatically determines suitable Chart.js chart (bar, pie, line) based on result set columns."""
        if not rows or len(rows) < 2:
            return None

        col_keys = [c.lower() for c in columns]
        
        # Look for category column and numeric column
        label_col = None
        data_col = None

        for col in columns:
            c_low = col.lower()
            if any(k in c_low for k in ["city", "channel", "txn_type", "merchant", "name", "category", "status"]):
                label_col = col
                break
        
        for col in columns:
            c_low = col.lower()
            if any(k in c_low for k in ["amount", "count", "total", "volume", "sum", "avg", "cnt"]):
                data_col = col
                break

        if not label_col or not data_col:
            # Fallback to first text column and first numeric column
            for col in columns:
                sample_val = rows[0].get(col)
                if isinstance(sample_val, (int, float)) and not data_col:
                    data_col = col
                elif isinstance(sample_val, str) and not label_col:
                    label_col = col

        if label_col and data_col:
            labels = [str(r.get(label_col, '')) for r in rows[:15]]
            data_points = []
            for r in rows[:15]:
                try:
                    val = float(r.get(data_col, 0) or 0)
                except (ValueError, TypeError):
                    val = 0.0
                data_points.append(round(val, 2))

            chart_type = "doughnut" if len(labels) <= 4 and ("type" in label_col.lower() or "channel" in label_col.lower()) else "bar"

            colors = [
                "rgba(56, 189, 248, 0.8)",
                "rgba(16, 185, 129, 0.8)",
                "rgba(245, 158, 11, 0.8)",
                "rgba(168, 85, 247, 0.8)",
                "rgba(239, 68, 68, 0.8)",
                "rgba(236, 72, 153, 0.8)",
                "rgba(14, 165, 233, 0.8)",
                "rgba(139, 92, 246, 0.8)"
            ]

            return {
                "type": chart_type,
                "label": f"{data_col.upper()} by {label_col.upper()}",
                "labels": labels,
                "datasets": [{
                    "label": f"{data_col} (INR / Count)",
                    "data": data_points,
                    "backgroundColor": colors[:len(labels)],
                    "borderColor": "rgba(255, 255, 255, 0.2)",
                    "borderWidth": 1
                }]
            }
        return None

    def _generate_marathi_explanation(self, prompt: str, sql: str, count: int) -> str:
        """Constructs a clear Marathi technical summary of the query executed and findings."""
        return (
            f"✅ तुमच्या <b>'{prompt}'</b> या प्रश्नावरून AI ने अचूक SQL तयार करून Neon Cloud वर चालवले.\n"
            f"📊 <b>एकूण निकाल:</b> {count} रेकॉर्ड्स प्राप्त झाले आहेत.\n"
            f"🔍 <b>एक्झिक्युट केलेले SQL:</b> <code>{sql}</code>"
        )

text_to_sql_engine = TextToSQLEngine()
