"""
Mangesh Nano Pro AI Studio - 9:16 SQL Short Video Creation Engine
Specialized for Mobile, Instagram Reels & YouTube Shorts (Max 60 Seconds).
Features:
- Banking & enterprise-level SQL interview scenarios.
- Viral peak-point hook in the first 3 seconds for audience retention.
- Step-by-step animated SQL code typing with glowing syntax highlighting.
- Moving arrow indicators highlighting key SQL keywords (PARTITION BY, DENSE_RANK, etc.).
- Multilingual voiceover (Marathi, Hindi, English) powered by ElevenLabs Voice AI.
- Multilingual subtitle overlays (English, Minglish, Hinglish).
- Zero-server-load client-side Canvas/MediaRecorder MP4 rendering & download.
- Live in-memory SQLite sandbox for verifying queries against real bank tables.
"""

import os
import time
import json
import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.core.logger import log_event
from app.core.config import VIDEO_OUTPUT_DIR, BASE_DIR
from app.core.elevenlabs_voice import elevenlabs_voice
from app.core.upstash_cache import upstash_cache


BANKING_SQL_PRESETS = [
    {
        "id": "bank_running_total",
        "title": "HDFC / SBI: Cumulative Running Balance",
        "difficulty": "Medium",
        "hook_mr": "🚨 ९०% मुलं या HDFC बँक SQL प्रश्नात फेल होतात! क्युम्युलेटिव्ह बॅलन्स कसा काढायचा?",
        "hook_hi": "🚨 90% लोग इस Bank SQL इंटरव्यू सवाल में अटक जाते हैं! Cumulative Balance कैसे निकालें?",
        "hook_en": "🚨 90% of candidates FAIL this Bank SQL Interview question! How to calculate Running Balance?",
        "hook_minglish": "🚨 90% pora ya Bank SQL question madhe fail hotat! Cumulative balance kasa kadhaycha?",
        "hook_hinglish": "🚨 90% log is Bank SQL interview question me fail ho jate hai! Running balance kaise nikale?",
        "question": "Calculate the cumulative running balance for each customer account ordered by transaction date.",
        "table_name": "bank_transactions",
        "schema_sql": """CREATE TABLE IF NOT EXISTS bank_transactions (
    txn_id INTEGER PRIMARY KEY,
    account_no TEXT,
    txn_date TEXT,
    amount REAL,
    txn_type TEXT
);
INSERT OR REPLACE INTO bank_transactions VALUES 
(101, 'ACC-8821', '2026-10-01', 5000.0, 'CREDIT'),
(102, 'ACC-8821', '2026-10-03', -1200.0, 'DEBIT'),
(103, 'ACC-8821', '2026-10-05', 8500.0, 'CREDIT'),
(104, 'ACC-8821', '2026-10-08', -3000.0, 'DEBIT'),
(105, 'ACC-9942', '2026-10-02', 12000.0, 'CREDIT'),
(106, 'ACC-9942', '2026-10-06', -4500.0, 'DEBIT');""",
        "solution_sql": """SELECT 
    account_no,
    txn_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY account_no 
        ORDER BY txn_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_balance
FROM bank_transactions;""",
        "arrow_target": "PARTITION BY account_no",
        "explanation_mr": "इथे 'SUM(amount) OVER' ही Window Function आहे. 'PARTITION BY account_no' मुळे प्रत्येक खात्याचा स्वतंत्र ग्रुप तयार होतो, आणि 'ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW' मुळे सुरुवातीपासून आजपर्यंतची बेरीज चालू राहते!",
        "explanation_hi": "यहाँ 'SUM() OVER' Window Function है। 'PARTITION BY account_no' हर अकाउंट का अलग ग्रुप बनाता है, और हर रो के साथ बैलेंस अपडेट होता जाता है!",
        "explanation_en": "SUM() OVER is a Window Function. 'PARTITION BY account_no' resets the tally per customer account, while 'ORDER BY txn_date' accumulates sequentially!",
        "explanation_minglish": "Ithe 'SUM(amount) OVER' hi Window Function ahe. 'PARTITION BY account_no' mule pratyek account cha vegla group hoto, ani running balance step-by-step calculate hoto!",
        "explanation_hinglish": "Yaha 'SUM() OVER' Window Function hai. 'PARTITION BY account_no' se har account ka alag group banta hai, aur har transaction ke sath balance update hota hai!",
        "pro_tip": "💡 Pro Tip: Never use a subquery for running totals in production databases—Window Functions execute in O(N) linear time!"
    },
    {
        "id": "bank_consecutive_fraud",
        "title": "ICICI / Axis: Detect Rapid Consecutive High-Value Withdrawals",
        "difficulty": "Hard",
        "hook_mr": "🚨 फ्रॉड डिटेक्शन SQL टेस्ट! एकाच तासात दोन मोठे विड्रॉव्हल कसे शोधायचे?",
        "hook_hi": "🚨 Bank Fraud Detection SQL Query! 1 घंटे में लगातार बड़े ट्रांजैक्शन्स कैसे पकड़ें?",
        "hook_en": "🚨 Fraud Detection SQL Test! Find consecutive high-value transactions within 1 hour!",
        "hook_minglish": "🚨 Fraud detection SQL test! Ekyach taasat don mothe withdrawals kase shodhayche?",
        "hook_hinglish": "🚨 Fraud detection SQL test! Ek hi ghante me do bade withdrawals kaise track kare?",
        "question": "Find all accounts that made consecutive withdrawals of more than ₹10,000 back-to-back using the LAG() function.",
        "table_name": "customer_withdrawals",
        "schema_sql": """CREATE TABLE IF NOT EXISTS customer_withdrawals (
    id INTEGER PRIMARY KEY,
    acc_id TEXT,
    withdraw_amt REAL,
    w_time TEXT
);
INSERT OR REPLACE INTO customer_withdrawals VALUES 
(1, 'SB-1001', 15000.0, '10:00:00'),
(2, 'SB-1001', 20000.0, '10:25:00'),
(3, 'SB-1002', 2000.0, '11:00:00'),
(4, 'SB-1002', 500.0, '11:15:00'),
(5, 'SB-1003', 45000.0, '12:00:00'),
(6, 'SB-1003', 50000.0, '12:10:00');""",
        "solution_sql": """WITH TxnWithLag AS (
    SELECT 
        acc_id,
        withdraw_amt,
        w_time,
        LAG(withdraw_amt, 1) OVER (
            PARTITION BY acc_id 
            ORDER BY w_time
        ) AS prev_amt
    FROM customer_withdrawals
)
SELECT acc_id, withdraw_amt, prev_amt, w_time
FROM TxnWithLag
WHERE withdraw_amt >= 10000 AND prev_amt >= 10000;""",
        "arrow_target": "LAG(withdraw_amt, 1)",
        "explanation_mr": "इथे 'LAG()' फंक्शन आधीचा रेकॉर्ड खेचून आणते. जर सध्याचा विड्रॉव्हल आणि आधीचा विड्रॉव्हल दोन्ही ₹10,000 पेक्षा जास्त असतील, तर हा फ्रॉड अलार्म लगेच ट्रिगर होतो!",
        "explanation_hi": "यहाँ 'LAG()' फंक्शन पिछली रो की वैल्यू खींचता है। जब करंट और पिछला अमाउंट दोनों ₹10,000+ होते हैं, तो फ्रॉड फ़्लैग होता है!",
        "explanation_en": "LAG() accesses data from the previous row without a self-join. If both current and previous withdrawals exceed ₹10,000, we flag potential fraud!",
        "explanation_minglish": "Ithe 'LAG()' function adhicha record khedun aante. Current ani previous donhi amount 10k peksha jast asel tar fraud alert trigger hoto!",
        "explanation_hinglish": "Yaha 'LAG()' function pichhla record fetch karta hai. Current aur previous dono amount 10k se zyada hone par fraud alert trigger hota hai!",
        "pro_tip": "💡 Pro Tip: LAG() and LEAD() eliminate expensive self-joins by scanning the partition in a single pass!"
    },
    {
        "id": "bank_salary_rank",
        "title": "Morgan Stanley / Goldman: 2nd Highest Bonus / Salary Without Ties",
        "difficulty": "Medium",
        "hook_mr": "🚨 सेकंड हायेस्ट सॅलरी विचारल्यावर ९५% मुलं 'LIMIT 1 OFFSET 1' लिहून चुकतात! खरा नियम काय?",
        "hook_hi": "🚨 2nd Highest Salary में LIMIT 1 OFFSET 1 मत लिखना! DENSE_RANK() क्यों ज़रूरी है?",
        "hook_en": "🚨 Stop using LIMIT 1 OFFSET 1 for 2nd Highest Salary! Why DENSE_RANK is mandatory!",
        "hook_minglish": "🚨 2nd Highest Salary madhe pora 'LIMIT 1 OFFSET 1' lihun chuktat! DENSE_RANK kashi vapraychi?",
        "hook_hinglish": "🚨 2nd Highest Salary me LIMIT 1 OFFSET 1 mat likhna! DENSE_RANK ka real use dekho!",
        "question": "Find the 2nd highest salary from the bank employees table, handling duplicate top salaries cleanly.",
        "table_name": "bank_employees",
        "schema_sql": """CREATE TABLE IF NOT EXISTS bank_employees (
    emp_id INTEGER PRIMARY KEY,
    emp_name TEXT,
    dept TEXT,
    salary REAL
);
INSERT OR REPLACE INTO bank_employees VALUES 
(1, 'Aarav Sharma', 'Investment Banking', 185000.0),
(2, 'Rohit Deshmukh', 'Investment Banking', 185000.0),
(3, 'Priya Kulkarni', 'Risk Management', 160000.0),
(4, 'Sneha Patel', 'Wealth Management', 140000.0),
(5, 'Amit Verma', 'Retail Banking', 120000.0);""",
        "solution_sql": """WITH RankedSalaries AS (
    SELECT 
        emp_name,
        dept,
        salary,
        DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM bank_employees
)
SELECT emp_name, dept, salary
FROM RankedSalaries
WHERE rnk = 2;""",
        "arrow_target": "DENSE_RANK() OVER (ORDER BY salary DESC)",
        "explanation_mr": "जर टॉप २ लोकांची सॅलरी समान (उदा. ₹1,85,000) असेल, तर 'RANK()' मुळे पुढचा रँक थेट ३ होतो, आणि 'OFFSET 1' चुकीचा निकाल देतो. पण 'DENSE_RANK()' नंबरिंग स्किप न करता अचूक २ रा नंबर शोधते!",
        "explanation_hi": "अगर 2 एम्प्लॉइज़ की सैलरी सेम ₹1,85,000 है, तो RANK() नंबर स्किप कर देगा। DENSE_RANK() बिना स्किप किए सही 2nd रैंक देता है!",
        "explanation_en": "DENSE_RANK() never skips ranks after ties (1, 1, 2). Regular RANK() skips (1, 1, 3), causing OFFSET queries to fail in production!",
        "explanation_minglish": "Top 2 chi salary same asel tar RANK() rank 3 var jump karte. Pan DENSE_RANK() rank skip karat nahi ani accurate 2nd salary bhetate!",
        "explanation_hinglish": "Agar top 2 salary same hai to RANK() rank 3 pe jump karega. But DENSE_RANK() rank skip nahi karta aur exact 2nd salary nikalta hai!",
        "pro_tip": "💡 Pro Tip: When ties are possible, DENSE_RANK() is the only standard-compliant solution!"
    }
]


class SqlShortVideoEngine:
    """
    Dedicated 9:16 Short Video Creation Engine.
    Produces viral 60-second Reels & Shorts with synchronized code, arrows, and voiceovers.
    """

    def __init__(self):
        self.output_dir = VIDEO_OUTPUT_DIR / "sql_shorts"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_presets(self) -> List[Dict[str, Any]]:
        """Returns built-in high-yield banking interview SQL scenarios."""
        return BANKING_SQL_PRESETS

    def execute_sandbox_sql(self, schema_sql: str, query_sql: str) -> Dict[str, Any]:
        """
        Executes real SQL in an ephemeral in-memory SQLite sandbox.
        Zero disk bloat, zero server load.
        """
        t0 = time.time()
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            # 1. Execute schema creation & sample data
            cursor.executescript(schema_sql)
            # 2. Execute target query
            cursor.execute(query_sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            data = [dict(r) for r in rows]
            dur_ms = round((time.time() - t0) * 1000, 2)
            return {
                "status": "success",
                "columns": columns,
                "rows": data,
                "row_count": len(data),
                "duration_ms": dur_ms
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "duration_ms": round((time.time() - t0) * 1000, 2)
            }
        finally:
            conn.close()

    def generate_short_prompt(
        self,
        topic_or_question: str,
        difficulty: str = "Medium",
        language: str = "mr"  # mr, hi, en
    ) -> Dict[str, Any]:
        """
        Generates a complete 60-second video creation blueprint:
        - 3-second Viral Hook
        - Real Banking Scenario & Table Schema
        - SQL Code with clause highlight timeline
        - Dynamic Arrow Target Marker
        - Multilingual Voiceover Script
        """
        # Resolve language mappings
        clean_lang = language.lower()
        if clean_lang in ["minglish", "mr_en"]:
            lang_key = "minglish"
        elif clean_lang in ["hinglish", "hi_en"]:
            lang_key = "hinglish"
        elif clean_lang in ["hi", "hindi"]:
            lang_key = "hi"
        elif clean_lang in ["en", "english"]:
            lang_key = "en"
        else:
            lang_key = "mr"

        # Check if topic matches existing presets
        clean_q = topic_or_question.lower()
        matched = None
        for p in BANKING_SQL_PRESETS:
            if p["id"] in clean_q or any(w in clean_q for w in p["title"].lower().split() if len(w) > 3):
                matched = p
                break

        # If not in presets and custom question provided, attempt AI blueprint synthesis
        if not matched and len(topic_or_question.strip()) > 15:
            try:
                from app.core.model_adapter import model_manager
                ai_prompt = (
                    f"You are an expert SQL video instructor. Generate a 60-second viral Short/Reel lesson plan for this SQL interview question:\n"
                    f"Question: {topic_or_question}\n"
                    f"Target Language: {lang_key}\n\n"
                    f"Return ONLY a valid JSON object with these exact keys:\n"
                    f'{{"title": "...", "hook": "Viral 3s hook with emoji", "schema_sql": "SQLite CREATE & INSERT", '
                    f'"solution_sql": "SQL Query", "arrow_target": "Exact clause to point arrow at", '
                    f'"explanation": "Clear 2-sentence explanation", "pro_tip": "Interview pro-tip"}}\n'
                )
                ai_resp, used_model, _ = model_manager.execute_with_fallback(
                    prompt=ai_prompt,
                    system_prompt="You output strictly raw valid JSON without markdown fences."
                )
                if "{" in ai_resp and "}" in ai_resp:
                    json_str = ai_resp[ai_resp.find("{"):ai_resp.rfind("}") + 1]
                    parsed = json.loads(json_str)
                    matched = {
                        "id": "custom_ai_scenario",
                        "title": parsed.get("title", "Advanced SQL Interview Challenge"),
                        "difficulty": difficulty,
                        "hook_mr": parsed.get("hook", "🚨 या SQL प्रश्नात बहुतांश मुलं चुकतात!"),
                        "hook_hi": parsed.get("hook", "🚨 इस SQL इंटरव्यू सवाल में 90% फेल होते हैं!"),
                        "hook_en": parsed.get("hook", "🚨 90% of candidates fail this SQL Interview question!"),
                        "hook_minglish": parsed.get("hook", "🚨 Ya SQL question madhe 90% loka fail hotat!"),
                        "hook_hinglish": parsed.get("hook", "🚨 Is SQL interview question me 90% log fail hote hai!"),
                        "question": topic_or_question,
                        "table_name": "custom_data",
                        "schema_sql": parsed.get("schema_sql", BANKING_SQL_PRESETS[0]["schema_sql"]),
                        "solution_sql": parsed.get("solution_sql", BANKING_SQL_PRESETS[0]["solution_sql"]),
                        "arrow_target": parsed.get("arrow_target", "OVER ()"),
                        "explanation_mr": parsed.get("explanation", "ही क्वेरी अचूक निकाल देते."),
                        "explanation_hi": parsed.get("explanation", "यह क्वेरी सटीक रिजल्ट देती है."),
                        "explanation_en": parsed.get("explanation", "This query calculates the exact outcome."),
                        "explanation_minglish": parsed.get("explanation", "Hi query accurate result dete."),
                        "explanation_hinglish": parsed.get("explanation", "Ye query exact result deti hai."),
                        "pro_tip": parsed.get("pro_tip", "💡 Pro Tip: Optimize using appropriate indexes.")
                    }
            except Exception as e:
                log_event(f"AI Prompt generation fallback: {e}", level="DEBUG", component="SqlShortEngine")

        if not matched:
            matched = BANKING_SQL_PRESETS[0]

        hook = matched.get(f"hook_{lang_key}", matched.get("hook_mr", matched["hook_en"]))
        explanation = matched.get(f"explanation_{lang_key}", matched.get("explanation_mr", matched["explanation_en"]))

        # Timeline duration allocation (Total: 60s)
        timeline = [
            {"time": "0:00 - 0:05", "phase": "HOOK", "title": "Viral Question Hook", "action": "Zoom on red badge + sound effect", "text": hook},
            {"time": "0:05 - 0:18", "phase": "PROBLEM", "title": "Real Bank Data Schema", "action": "Display glowing customer transaction cards", "text": matched["question"]},
            {"time": "0:18 - 0:42", "phase": "SQL_LOGIC", "title": "Clause-by-Clause SQL Build", "action": "Typewriter code animation + Arrow pointing to key logic", "text": matched["solution_sql"], "arrow_target": matched["arrow_target"]},
            {"time": "0:42 - 0:54", "phase": "RESULT", "title": "Simulated Output Table", "action": "Highlight matching fraudulent / calculated rows in Neon Cyan", "text": explanation},
            {"time": "0:54 - 1:00", "phase": "OUTRO", "title": "Pro Takeaway & Follow", "action": "Like & Subscribe CTA + Interview Pro Tip", "text": matched["pro_tip"]}
        ]

        return {
            "status": "success",
            "title": matched["title"],
            "difficulty": difficulty,
            "language": lang_key,
            "hook": hook,
            "question": matched["question"],
            "table_name": matched["table_name"],
            "schema_sql": matched["schema_sql"],
            "solution_sql": matched["solution_sql"],
            "arrow_target": matched["arrow_target"],
            "explanation": explanation,
            "pro_tip": matched["pro_tip"],
            "timeline": timeline,
            "max_duration_seconds": 60,
            "aspect_ratio": "9:16"
        }

    def synthesize_voiceover(self, text: str, language: str = "mr") -> Optional[str]:
        """Synthesizes voiceover using ElevenLabs Voice AI (API #9)."""
        if not elevenlabs_voice.is_available():
            return None
        try:
            audio_filename = f"sql_short_voice_{int(time.time())}_{language}.mp3"
            audio_path = str(self.output_dir / audio_filename)
            res = elevenlabs_voice.generate_speech(
                text=text,
                output_path=audio_path,
                voice_id="EXAVITQu4vr4xnSDxMaL"  # Sarah - Multilingual v2
            )
            return res.get("file_path")
        except Exception as e:
            log_event(f"Voiceover generation failed: {e}", level="WARNING", component="SqlShortEngine")
            return None


# Global Singleton instance
sql_short_engine = SqlShortVideoEngine()
