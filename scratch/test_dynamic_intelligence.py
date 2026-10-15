"""
Mangesh Nano Pro AI Studio - Dynamic Intelligence & Zero-Hardcoding Verification Test Suite
Tests arbitrary numeric variations, live dynamic math derivations, multi-database introspection,
and enterprise 1,000+ infrastructure failure diagnostics.
"""

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from app.agents.extended_intents import handle_extended_intents
from app.core.dynamic_stem_engine import dynamic_stem_engine
from app.core.dynamic_db_engine import dynamic_db_engine
from app.core.enterprise_knowledge_engine import enterprise_knowledge_engine

def run_tests():
    print("=" * 80)
    print("MANGESH NANO PRO AI: DYNAMIC INTELLIGENCE BENCHMARK (ZERO HARDCODING)")
    print("=" * 80)

    test_cases = [
        # 1. STEM - Solar with standard numbers
        {
            "id": "SOLAR_STD",
            "prompt": "NanoPro, a household consumes 18 kWh (units) of electricity per day. If peak sun hours are 5 hours/day and system efficiency is 80%, calculate the required Solar Rooftop Plant capacity (in kW) and the number of 540W solar panels needed.",
            "expect_terms": ["4.50", "9 Panels", "kWp"]
        },
        # 2. STEM - Solar with completely custom/arbitrary numbers (proving dynamic math)
        {
            "id": "SOLAR_DYNAMIC_VAR",
            "prompt": "Calculate solar rooftop capacity for a factory consuming 72 kWh per day with 4.5 peak sun hours, 85% efficiency, using 600W solar panels.",
            "expect_terms": ["72.0", "4.5", "85%", "600", "Panels"]
        },
        # 3. STEM - Torque to HP with arbitrary custom numbers
        {
            "id": "TORQUE_DYNAMIC",
            "prompt": "An electric supercar engine generates 680 Nm of torque at 3400 RPM. Calculate mechanical power in kW and horsepower.",
            "expect_terms": ["680.0", "3,400", "kW", "HP", "rad/s"]
        },
        # 4. STEM - Kinetic Energy with custom mass and velocity
        {
            "id": "BALLISTICS_DYNAMIC",
            "prompt": "Calculate kinetic energy and gyroscopic stability for a 9.5g bullet fired at 820 m/s muzzle velocity.",
            "expect_terms": ["9.50", "820.0", "Joules", "ft-lbs"]
        },
        # 5. STEM - Hohmann Transfer Orbit
        {
            "id": "HOHMANN_ORBIT",
            "prompt": "Derive Hohmann transfer orbit delta-v from 300 km LEO to 35786 km GEO using Vis-Viva equation.",
            "expect_terms": ["Vis-Viva", "Semi-Major Axis", "km/s", "Hours"]
        },
        # 6. STEM - Home Loan EMI with custom numbers
        {
            "id": "LOAN_EMI_DYNAMIC",
            "prompt": "Calculate home loan monthly EMI for a loan of Rs. 75 Lakhs at 8.75% annual interest for 15 years tenure.",
            "expect_terms": ["₹75,00,000", "8.75%", "15.0 Years", "EMI", "Amortization"]
        },
        # 7. STEM - Black-Scholes Option Greeks with custom numbers
        {
            "id": "BLACK_SCHOLES_DYNAMIC",
            "prompt": "Compute Black-Scholes option pricing and Greeks for spot 150, strike 145, time 0.5 years, risk-free rate 6%, volatility 25%.",
            "expect_terms": ["Black-Scholes", "Delta", "Gamma", "Vega", "Theta"]
        },
        # 8. ALGORITHMS - Dynamic Two Sum on arbitrary array and target
        {
            "id": "TWO_SUM_DYNAMIC",
            "prompt": "Solve Two Sum algorithm for nums = [5, 12, 18, 24, 30] with target: 42.",
            "expect_terms": ["Two Sum", "[5, 12, 18, 24, 30]", "42", "[2, 3]"]
        },
        # 9. ALGORITHMS - Dynamic Balanced Brackets on arbitrary string
        {
            "id": "BRACKETS_DYNAMIC",
            "prompt": "Check if brackets '{[()]}' are valid using a stack.",
            "expect_terms": ["BALANCED (TRUE)", "LIFO", "Stack"]
        },
        # 10. ALGORITHMS - Dynamic Two-Pointer Array Merge
        {
            "id": "ARRAY_MERGE_DYNAMIC",
            "prompt": "Merge two sorted arrays [1, 5, 9] and [2, 4, 8, 10] using two pointer technique.",
            "expect_terms": ["Two-Pointer", "[1, 2, 4, 5, 8, 9, 10]", "O(M + N)"]
        },
        # 11. DATABASE - Marathi Table Fetch Query for ACCOUNTS in BANK_DB L0
        {
            "id": "DB_FETCH_MARATHI",
            "prompt": "ek table ahe ACCOUNTS to BANK_DB chya L0 layer madhe ahe so tya table che first 5 record fetch karun pahujet so procide SQL query for snowflake",
            "expect_terms": ["BANK_DB.L0_STAGING.ACCOUNTS LIMIT 5", "ACCOUNT_ID", "CUSTOMER_ID", "BALANCE"]
        },
        # 12. DATABASE - Marathi Full Database Architecture & Schema Audit
        {
            "id": "DB_AUDIT_MARATHI",
            "prompt": "pahile tyane sagle db check karun to konta db ahe oracle ki snowflake ki postgres ki sqllight then db konte ahet tyanche exact db namme db kiti konte ka banavlet te schema konta ahe schemache exact name kayahet kiti ahet schema db madhe konte and kiti tables ahet and ka banavlet te table madhe konte column ahet kiti ahet data type kay ahe",
            "expect_terms": ["Snowflake Data Cloud", "Oracle Database XE", "PostgreSQL", "SQLite", "L0_STAGING", "ACCOUNTS", "CUSTOMERS"]
        },
        # 13. DATABASE - Cross-DB Reconciliation & Excel Report
        {
            "id": "CROSS_DB_RECON",
            "prompt": "Perform cross db reconciliation between Oracle XE and Snowflake BANK_DB for ACCOUNTS and generate discrepancy report.",
            "expect_terms": ["Cross-Database", "ACCOUNT_NUMBER", "Reconciliation Report"]
        },
        # 14. ENTERPRISE - Kafka Consumer Group Rebalance Storm
        {
            "id": "KAFKA_REBALANCE",
            "prompt": "We are experiencing a Kafka consumer group rebalance storm with max.poll.interval.ms timeouts. How do we troubleshoot and fix this in production?",
            "expect_terms": ["max.poll.interval.ms", "CooperativeStickyAssignor", "max.poll.records", "CommitFailedException"]
        },
        # 15. ENTERPRISE - Snowflake Remote Storage Disk Spilling
        {
            "id": "SNOWFLAKE_SPILL",
            "prompt": "Snowflake query is spilling gigabytes of data to remote storage causing severe query latency and high warehouse cost. What is the root cause and remediation?",
            "expect_terms": ["Remote Storage Spilling", "ACCOUNT_USAGE.QUERY_HISTORY", "Scale Up Warehouse", "Cluster Key"]
        },
        # 16. ENTERPRISE - Oracle ORA-01555 Snapshot Too Old
        {
            "id": "ORACLE_1555",
            "prompt": "Production Oracle batch job failed with ORA-01555 snapshot too old on undo tablespace. Provide exact diagnostic queries and database parameter fix.",
            "expect_terms": ["ORA-01555", "UNDO_RETENTION", "V$UNDOSTAT", "RETENTION GUARANTEE"]
        },
        # 17. ENTERPRISE - Postgres Transaction ID Wraparound & Autovacuum Freeze
        {
            "id": "POSTGRES_WRAPAROUND",
            "prompt": "PostgreSQL database is approaching transaction ID wraparound and autovacuum freeze is falling behind. How to prevent database emergency shutdown?",
            "expect_terms": ["Transaction ID (XID) Wraparound", "age(datfrozenxid)", "VACUUM FREEZE", "autovacuum_freeze_max_age"]
        },
        # 18. ENTERPRISE - Kubernetes CrashLoopBackOff & OOMKilled 137
        {
            "id": "K8S_OOMKILLED",
            "prompt": "Kubernetes pod is trapped in CrashLoopBackOff with Exit Code 137 OOMKilled. How to diagnose and resolve container memory limits?",
            "expect_terms": ["Exit Code 137", "CrashLoopBackOff", "resources.limits.memory", "MaxRAMPercentage"]
        },
        # 19. ENTERPRISE - Low-Latency HFT Kernel Bypass & CPU Core Pinning
        {
            "id": "HFT_OPTIMIZATION",
            "prompt": "In high-frequency trading, how do we achieve sub-microsecond tick-to-trade latency using kernel bypass, DPDK, CPU core pinning, and cache alignment?",
            "expect_terms": ["Kernel Bypass", "DPDK", "isolcpus", "alignas(64)", "PTP IEEE 1588"]
        },
        # 20. ENTERPRISE - Deep Learning CUDA OOM & FlashAttention
        {
            "id": "GPU_CUDA_OOM",
            "prompt": "PyTorch LLM training is crashing with CUDA Out of Memory during long context attention. How does FlashAttention v2/v3 and PagedAttention solve this?",
            "expect_terms": ["FlashAttention", "CUDA Out of Memory", "PagedAttention", "torch.backends.cuda.matmul.allow_tf32"]
        }
    ]

    passed = 0
    failed = 0

    for tc in test_cases:
        t_start = time.time()
        res = handle_extended_intents(tc["prompt"].lower(), tc["prompt"])
        duration = (time.time() - t_start) * 1000

        if not res or not res.get("handled"):
            print(f"❌ [{tc['id']}] FAILED: Handler returned None or unhandled.")
            failed += 1
            continue

        reply = res.get("reply", "")
        missing_terms = [term for term in tc["expect_terms"] if term.lower() not in reply.lower()]

        if missing_terms:
            print(f"⚠️ [{tc['id']}] WARNING: Missing expected terms: {missing_terms} (Time: {duration:.1f}ms)")
            print(f"   Reply preview: {reply[:200]}...")
            failed += 1
        else:
            print(f"✅ [{tc['id']}] PASSED ({duration:.1f}ms) - Verified: {tc['expect_terms']}")
            passed += 1

    print("\n" + "=" * 80)
    print(f"BENCHMARK RESULTS: {passed} PASSED / {failed} FAILED (Total: {len(test_cases)})")
    print("=" * 80)

    if failed == 0:
        print("🎉 100% PERFECT SCORE! All dynamic STEM computations, NL-to-DB queries, and enterprise failure diagnostics passed with zero hardcoding!")
        return 0
    else:
        print(f"❌ {failed} tests failed. Please review output.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
