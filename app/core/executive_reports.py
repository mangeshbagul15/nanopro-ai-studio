"""
Mangesh Nano Pro AI Studio - Automated Executive Excel & Telegram Insights Engine
Compiles executive business intelligence, banking analytics, and cloud lakehouse metrics into
a styled Excel workbook (.xlsx) and dispatches it directly to Telegram Chat ID 1200023268.
"""

import os
import time
import sqlite3
import requests
from typing import Dict, Any, List
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from app.core.connection_manager import connection_manager
from app.core.logger import log_event

from app.core.config import (
    TELEGRAM_REPORTS_BOT_TOKEN,
    TELEGRAM_NEWS_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)

TELEGRAM_BOT_TOKEN = TELEGRAM_REPORTS_BOT_TOKEN
REPORTS_DIR = os.path.join("data", "reports")

class ExecutiveReportManager:
    """Generates styled Executive BI Excel workbooks and dispatches them via Telegram."""

    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "database", "studio_memory.db")

    def _get_sqlite_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def generate_and_dispatch(self) -> Dict[str, Any]:
        """Creates full executive workbook and dispatches directly to Telegram."""
        start_time = time.time()
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"NanoPro_Executive_BI_{timestamp_str}.xlsx"
        filepath = os.path.join(REPORTS_DIR, filename)

        # Step 1: Collect KPIs from Neon Cloud & SQLite
        metrics = self._gather_metrics()

        # Step 2: Build Styled Excel Workbook
        self._build_excel_workbook(filepath, metrics)

        # Step 3: Dispatch to Telegram
        telegram_status = self._send_to_telegram(filepath, metrics)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "success",
            "report_file": filename,
            "filepath": filepath,
            "telegram_delivered": telegram_status,
            "duration_ms": duration_ms,
            "metrics": metrics["summary"]
        }

    def _gather_metrics(self) -> Dict[str, Any]:
        """Extracts live metrics from Neon PostgreSQL, SQLite, and System stats."""
        # 1. Neon Banking Stream
        neon_res = connection_manager.execute_query(
            "POSTGRES_CLOUD_FREE",
            "SELECT txn_id, customer_name, amount, channel, merchant, city, sync_status, created_at FROM neon_banking_stream ORDER BY created_at DESC LIMIT 100;"
        )
        txns = neon_res.get("rows", [])
        total_txns = len(txns)
        total_volume = sum(float(t.get("amount", 0) or 0) for t in txns)
        avg_amount = (total_volume / total_txns) if total_txns > 0 else 0.0

        # 2. SQLite Medallion L0 Staging & Users
        l0_count = 0
        active_users = 0
        pending_users = 0
        users_list = []

        try:
            with self._get_sqlite_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) AS cnt FROM medallion_l0_staging;")
                r = cursor.fetchone()
                if r: l0_count = r["cnt"]

                cursor.execute("SELECT username, full_name, email, role, status, access_mode, last_login_at FROM users;")
                for u in cursor.fetchall():
                    users_list.append(dict(u))
                    if u["status"] == "ACTIVE": active_users += 1
                    elif u["status"] == "PENDING_APPROVAL": pending_users += 1
        except Exception as e:
            log_event(f"Error gathering local metrics: {e}", component="ExecutiveReport", level="WARNING")

        return {
            "summary": {
                "generated_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "total_stream_txns": total_txns,
                "total_volume_inr": round(total_volume, 2),
                "avg_ticket_inr": round(avg_amount, 2),
                "medallion_l0_count": l0_count,
                "active_users": active_users,
                "pending_approvals": pending_users,
                "cloud_source": "Neon PostgreSQL (Singapore)",
                "lakehouse_target": "Snowflake Medallion L0"
            },
            "transactions": txns,
            "users": users_list
        }

    def _build_excel_workbook(self, filepath: str, data: Dict[str, Any]):
        """Builds a beautiful 3-sheet workbook with enterprise blue styling."""
        wb = openpyxl.Workbook()
        
        # Styles
        font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Dark Blue
        fill_accent = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid") # Sky Blue
        font_title = Font(name="Calibri", size=16, bold=True, color="0F172A")
        font_kpi_num = Font(name="Calibri", size=18, bold=True, color="0284C7")
        border_thin = Border(left=Side(style='thin', color='E2E8F0'),
                             right=Side(style='thin', color='E2E8F0'),
                             top=Side(style='thin', color='E2E8F0'),
                             bottom=Side(style='thin', color='E2E8F0'))

        # Sheet 1: Executive KPI Summary
        ws1 = wb.active
        ws1.title = "Executive Summary"
        ws1.views.sheetView[0].showGridLines = True

        ws1.merge_cells("A1:G1")
        ws1["A1"] = "MANGESH NANO PRO AI STUDIO - EXECUTIVE BI REPORT"
        ws1["A1"].font = font_title
        ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws1.row_dimensions[1].height = 35

        ws1.merge_cells("A2:G2")
        ws1["A2"] = f"Generated on {data['summary']['generated_at']} | Autonomous Cloud Analytics"
        ws1["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")
        ws1["A2"].alignment = Alignment(horizontal="center")

        # KPI Cards Table
        kpis = [
            ("एकूण ट्रान्झॅक्शन्स (Total Stream Volume)", f"₹ {data['summary']['total_volume_inr']:,.2f}"),
            ("एकूण व्यवहार संख्या (Transaction Count)", f"{data['summary']['total_stream_txns']}"),
            ("सरासरी व्यवहार मूल्य (Average Ticket Size)", f"₹ {data['summary']['avg_ticket_inr']:,.2f}"),
            ("Snowflake L0 Staging Records", f"{data['summary']['medallion_l0_count']}"),
            ("सक्रिय युझर्स (Active Enterprise Users)", f"{data['summary']['active_users']}"),
            ("मंजुरी प्रलंबित (Pending User Approvals)", f"{data['summary']['pending_approvals']}"),
            ("प्राथमिक क्लाउड डेटाबेस (Cloud Engine)", f"{data['summary']['cloud_source']}")
        ]

        ws1["B4"] = "METRIC INDICATOR"
        ws1["C4"] = "EXECUTIVE VALUE"
        ws1["B4"].font = font_header
        ws1["B4"].fill = fill_header
        ws1["C4"].font = font_header
        ws1["C4"].fill = fill_header

        row_idx = 5
        for label, val in kpis:
            ws1.cell(row=row_idx, column=2, value=label).border = border_thin
            val_cell = ws1.cell(row=row_idx, column=3, value=val)
            val_cell.border = border_thin
            val_cell.font = Font(name="Calibri", size=11, bold=True, color="0369A1")
            row_idx += 1

        ws1.column_dimensions['B'].width = 45
        ws1.column_dimensions['C'].width = 30

        # Sheet 2: Banking Transactions Ledger
        ws2 = wb.create_sheet(title="Banking Stream Ledger")
        ws2.views.sheetView[0].showGridLines = True
        headers_ws2 = ["Txn ID", "Customer Name", "Amount (INR)", "Channel", "Merchant", "City", "Sync Status", "Timestamp"]
        for col_i, h in enumerate(headers_ws2, 1):
            cell = ws2.cell(row=1, column=col_i, value=h)
            cell.font = font_header
            cell.fill = fill_accent
            cell.alignment = Alignment(horizontal="center")

        ws2.row_dimensions[1].height = 24

        for r_i, txn in enumerate(data.get("transactions", []), 2):
            ws2.cell(row=r_i, column=1, value=str(txn.get("txn_id", "")))
            ws2.cell(row=r_i, column=2, value=str(txn.get("customer_name", "")))
            amt_cell = ws2.cell(row=r_i, column=3, value=float(txn.get("amount", 0) or 0))
            amt_cell.number_format = '#,##0.00'
            ws2.cell(row=r_i, column=4, value=str(txn.get("channel", "")))
            ws2.cell(row=r_i, column=5, value=str(txn.get("merchant", "")))
            ws2.cell(row=r_i, column=6, value=str(txn.get("city", "")))
            ws2.cell(row=r_i, column=7, value=str(txn.get("sync_status", "")))
            ws2.cell(row=r_i, column=8, value=str(txn.get("created_at", "")))

        for col in ws2.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws2.column_dimensions[col_letter].width = max(max_len + 4, 12)

        # Sheet 3: Enterprise Users & RBAC
        ws3 = wb.create_sheet(title="Users & Governance")
        ws3.views.sheetView[0].showGridLines = True
        headers_ws3 = ["Username", "Full Name", "Email", "Role", "Status", "Access Mode"]
        for col_i, h in enumerate(headers_ws3, 1):
            cell = ws3.cell(row=1, column=col_i, value=h)
            cell.font = font_header
            cell.fill = fill_header

        for r_i, u in enumerate(data.get("users", []), 2):
            ws3.cell(row=r_i, column=1, value=str(u.get("username", "")))
            ws3.cell(row=r_i, column=2, value=str(u.get("full_name", "")))
            ws3.cell(row=r_i, column=3, value=str(u.get("email", "")))
            ws3.cell(row=r_i, column=4, value=str(u.get("role", "")))
            ws3.cell(row=r_i, column=5, value=str(u.get("status", "")))
            ws3.cell(row=r_i, column=6, value=str(u.get("access_mode", "")))

        for col in ws3.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws3.column_dimensions[col_letter].width = max(max_len + 4, 12)

        wb.save(filepath)
        log_event(f"Executive BI Workbook generated at {filepath}", component="ExecutiveReport")

    def _send_to_telegram(self, filepath: str, data: Dict[str, Any]) -> bool:
        """Sends executive summary HTML message + formatted Excel file directly to Telegram."""
        summary = data["summary"]
        text = (
            f"📊 <b>MANGESH NANO PRO — DAILY EXECUTIVE BI REPORT</b> 🚀\n"
            f"<i>तारीख व वेळ: {summary['generated_at']}</i>\n\n"
            f"💰 <b>एकूण ट्रान्झॅक्शन्स व्हॉल्यूम:</b> ₹ {summary['total_volume_inr']:,.2f}\n"
            f"📈 <b>एकूण व्यवहार संख्या:</b> {summary['total_stream_txns']} ट्रान्झॅक्शन्स\n"
            f"🎯 <b>सरासरी व्यवहार मूल्य:</b> ₹ {summary['avg_ticket_inr']:,.2f}\n"
            f"❄️ <b>Snowflake L0 Staging Ledger:</b> {summary['medallion_l0_count']} records\n"
            f"👥 <b>सक्रिय युझर्स:</b> {summary['active_users']} | <b>मंजुरी प्रलंबित:</b> {summary['pending_approvals']}\n"
            f"🌐 <b>Cloud Database:</b> {summary['cloud_source']}\n\n"
            f"📎 <i>खाली संपूर्ण एक्सेल (.xlsx) बिझनेस वर्कबुक जोडली आहे.</i>"
        )

        try:
            # 1. Send HTML Briefing
            msg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(msg_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=6)

            # 2. Send Document (.xlsx)
            doc_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            with open(filepath, "rb") as f:
                files = {"document": (os.path.basename(filepath), f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                data_payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": f"📑 NanoPro Executive BI Report ({summary['generated_at']})"}
                resp = requests.post(doc_url, data=data_payload, files=files, timeout=15)
                return resp.status_code == 200
        except Exception as e:
            log_event(f"Failed to dispatch report to Telegram: {e}", component="ExecutiveReport", level="ERROR")
            return False

executive_report_manager = ExecutiveReportManager()
