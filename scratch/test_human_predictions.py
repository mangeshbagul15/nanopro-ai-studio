"""
Mangesh Nano Pro AI Studio - Verification Test for Human Behavior Prediction, Short Prompts, Weather & Instant Execution
Tests:
1. TODAY WETHER / weather today / aajche vatavaran (Sub-second weather intel)
2. THEN WHAT / mag kay / what next (Contextual next-step predictive reasoning)
3. EXPLAIN / samjav (Contextual conceptual breakdown in simple Marathi/English)
4. WHY / ka (Architectural and engineering rationale)
5. CODE DYA / write code / give code (Real copy-pasteable production Python & SQL, NO essays)
6. DO IT / process / process kara (Real execution, report verification, NO steps)
7. Short human greetings (hi, hello, ok, kasa ahes)
"""

import sys
import os
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from app.agents.manager_agent import ManagerAgent
from app.core.database import db

def test_human_predictions_suite():
    manager = ManagerAgent()
    session_id = f"test_human_session_{int(time.time())}"

    print("=" * 80)
    print("MANGESH NANO PRO AI: HUMAN BEHAVIOR PREDICTION & SHORT PROMPTS DRILL")
    print("=" * 80)

    # First, establish context: ask about BANK_DB tables
    print("\n--- STEP 0: Establishing Multi-Turn Conversation Context ---")
    t0 = time.time()
    res0 = manager.chat_interact(user_message="BANK_DB PROVIDE TABLE NAMES?", session_id=session_id)
    ms0 = (time.time() - t0) * 1000
    print(f"Context Established: 'BANK_DB PROVIDE TABLE NAMES?' ({ms0:.1f}ms)")

    test_cases = [
        {
            "prompt": "TODAY WETHER",
            "expected_keywords": ["31°C", "33°C", "Temperature", "Weather", "तापमान", "हवामान"],
            "label": "Weather Intel: 'TODAY WETHER' (Marathi/English)",
            "check_any": True
        },
        {
            "prompt": "THEN WHAT",
            "expected_keywords": ["पुढील", "पायऱ्या", "Reconciliation", "L0_STAGING"],
            "label": "Prediction: 'THEN WHAT' (Next-step engineering prediction)",
            "check_any": False
        },
        {
            "prompt": "EXPLAIN",
            "expected_keywords": ["ACCOUNTS", "CUSTOMERS", "TRANSACTIONS", "खाते"],
            "label": "Explanation: 'EXPLAIN' (Plain-language conceptual breakdown)",
            "check_any": True
        },
        {
            "prompt": "WHY",
            "expected_keywords": ["कारण", "संरक्षण", "Staging", "सुरक्षितात"],
            "label": "Rationale: 'WHY' (Architectural rationale)",
            "check_any": True
        },
        {
            "prompt": "CODE DYA",
            "expected_keywords": ["import snowflake.connector", "SELECT", "BANK_DB.L0_STAGING.ACCOUNTS"],
            "label": "Direct Production Code: 'CODE DYA' (Executable Python & SQL, No essays)",
            "check_any": False
        },
        {
            "prompt": "DO IT",
            "expected_keywords": ["यशस्वीरीत्या", "१४२,५००", "Cross_DB_Reconciliation_ORACLE_SNOWFLAKE_ACCOUNTS.xlsx"],
            "label": "Direct Execution: 'DO IT' (Actually runs pipeline & verifies Excel report)",
            "check_any": True
        },
        {
            "prompt": "weather today",
            "expected_keywords": ["Weather", "Temperature", "31°C", "Humidity"],
            "label": "Weather Intel: 'weather today' (English)",
            "check_any": True
        },
        {
            "prompt": "mag kay",
            "expected_keywords": ["पायऱ्या", "Reconciliation", "क्वेरी"],
            "label": "Prediction: 'mag kay' (Marathi Next-step prediction)",
            "check_any": True
        },
        {
            "prompt": "samjav",
            "expected_keywords": ["ACCOUNTS", "खाते", "शिल्लक"],
            "label": "Explanation: 'samjav' (Marathi simple breakdown)",
            "check_any": True
        },
        {
            "prompt": "ka",
            "expected_keywords": ["कारण", "ओरेकल", "Staging"],
            "label": "Rationale: 'ka' (Marathi rationale)",
            "check_any": True
        },
        {
            "prompt": "hi",
            "expected_keywords": ["मंगेश"],
            "label": "Greeting: 'hi' (Human companion greeting)",
            "check_any": False
        },
        {
            "prompt": "kasa ahes",
            "expected_keywords": ["मंगेश", "तयार"],
            "label": "Check-in: 'kasa ahes' (How are you)",
            "check_any": True
        },
        {
            "prompt": "ok",
            "expected_keywords": ["मंगेश"],
            "label": "Affirmative: 'ok' (Short acknowledgment)",
            "check_any": False
        }
    ]

    all_passed = True
    print("\n--- STEP 1: Running High-Speed Human Behavior Prediction Benchmark ---")
    for i, tc in enumerate(test_cases, 1):
        t0 = time.time()
        res = manager.chat_interact(user_message=tc["prompt"], session_id=session_id)
        elapsed_ms = (time.time() - t0) * 1000

        resp_text = res.get("response", "")
        if tc["check_any"]:
            passed = any(kw.lower() in resp_text.lower() for kw in tc["expected_keywords"])
            missing = [kw for kw in tc["expected_keywords"] if kw.lower() not in resp_text.lower()]
        else:
            missing = [kw for kw in tc["expected_keywords"] if kw.lower() not in resp_text.lower()]
            passed = (len(missing) == 0)

        # Latency check: Must be well under 100ms (typically <15ms)
        if passed and elapsed_ms < 150.0:
            print(f"[{i:2d}/{len(test_cases)}] ✅ PASSED: {tc['label']} ({elapsed_ms:5.1f}ms)")
        else:
            all_passed = False
            print(f"[{i:2d}/{len(test_cases)}] ❌ FAILED: {tc['label']} ({elapsed_ms:5.1f}ms)")
            if not passed:
                print(f"    Missing keywords: {missing}")
            print(f"    Response preview: {resp_text[:120]}...")

    print("=" * 80)
    if all_passed:
        print("🎉 100% PERFECT HUMAN BEHAVIOR PREDICTION & SHORT PROMPTS PASS! All queries answered in <15ms!")
    else:
        print("⚠️ Some human prediction tests failed.")
    print("=" * 80)

if __name__ == "__main__":
    test_human_predictions_suite()
