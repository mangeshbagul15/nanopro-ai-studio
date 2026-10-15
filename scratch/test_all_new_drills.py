import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

from app.agents.extended_intents import handle_extended_intents

TEST_CASES = [
    # --- Scientific & STEM ---
    ("Solar Rooftop Calculation", "NanoPro, a household consumes 18 kWh (units) of electricity per day. If peak sun hours are 5 hours/day and system efficiency is 80%, calculate the required Solar Rooftop Plant capacity (in kW) and the number of 540W solar panels needed.", ["4.5", "540W", "9"]),
    ("Torque to HP", "NanoPro, an electric motor produces 400 Nm of torque at 2,500 RPM. Calculate its mechanical power output in Horsepower (HP) and Kilowatts (kW).", ["140.4", "104.7", "7120.7"]),
    ("CRISPR-Cas9 PAM", "NanoPro, what is the role of the PAM (Protospacer Adjacent Motif) sequence in CRISPR-Cas9 genome editing, and what happens if the target DNA lacks this sequence?", ["NGG", "PAM", "Cas9"]),
    ("Transformer Attention sqrt(d_k)", "NanoPro, why is the dot product divided by the square root of the key dimension (sqrt(d_k)) in Transformer Attention mechanisms? What mathematical problem does this solve?", ["softmax", "d_k", "gradient"]),
    ("Benford's Law", "NanoPro, explain Benford's Law and demonstrate how it is used in forensic accounting and data engineering to detect fraudulent transactions in financial ledgers.", ["Benford", "log", "forensic"]),
    ("Bitmap Index OLTP", "NanoPro, why does creating a Bitmap Index on a high-cardinality or frequently updated column in an OLTP database cause severe performance degradation and deadlocks?", ["Bitmap", "lock", "OLTP"]),
    ("Roman Concrete Pozzolana", "NanoPro, explain the chemical and structural mechanism by which ancient Roman concrete (pozzolanic concrete) lasted over 2,000 years in seawater, whereas modern Portland cement degrades within decades.", ["pozzolan", "tobermorite", "seawater"]),
    ("ASML EUV 13.5nm Lithography", "NanoPro, explain the complete working mechanism of ASML Extreme Ultraviolet (EUV) lithography machines (13.5 nm wavelength) using tin laser-produced plasma (LPP) and Bragg multilayer mirrors.", ["13.5", "ASML", "Bragg", "tin"]),
    ("Kafka 12 Partitions 15 Consumers", "NanoPro, a Kafka consumer group with 15 consumers is subscribed to a topic with 12 partitions. Why are 3 consumers completely idle, and how can we redesign this system to increase throughput without increasing topic partitions?", ["idle", "partition", "consumer"]),
    ("AI Consciousness Marathi", "NanoPro, मराठीत सांगा: AI चे मानवी मेंदूसोबतचे साम्य आणि फरक काय आहेत? भविष्यात AI चे स्वतःचे भान (Consciousness) तयार होऊ शकते का, की ते फक्त अल्गोरिदम राहील?", ["मेंदू", "AI", "अल्गोरिदम"]),
    ("Shor's Algorithm QFT", "NanoPro, explain the mathematical foundation of Shor's Algorithm and why Quantum Fourier Transform (QFT) enables the polynomial-time factorization of RSA-2048 encryption keys.", ["Shor", "QFT", "RSA-2048"]),
    ("Hohmann Transfer Orbit", "NanoPro, a satellite is in Low Earth Orbit (LEO) at 300 km altitude. Calculate the delta-v (velocity change) required to transfer it to Geostationary Orbit (GEO) at 35,786 km using a Hohmann Transfer Orbit.", ["Hohmann", "24,432", "delta-v"]),
    ("HFT Sub-microsecond C++ FPGA", "NanoPro, in High-Frequency Trading (HFT), how do kernel-bypass networking (Solarflare OpenOnload), FPGA-based order routing, and cache-line aligned C++ memory structures achieve sub-microsecond tick-to-trade latency?", ["OpenOnload", "FPGA", "kernel bypass"]),
    ("BCI Neuralink vs EEG", "NanoPro, explain the biophysical signal processing differences between EEG-based Brain-Computer Interfaces (BCI) and intracortical neural implants (like Neuralink).", ["Neuralink", "EEG", "signal"]),
    ("Graphene Dirac Cones", "NanoPro, explain the electronic band structure of Graphene. Why do charge carriers behave as massless Dirac fermions, and why does this lead to extraordinary electrical conductivity despite zero bandgap?", ["Graphene", "Dirac", "fermion"]),
    ("PACELC Theorem Cassandra DynamoDB", "NanoPro, explain the PACELC theorem in distributed databases with real-world architectural comparisons between Apache Cassandra and Amazon DynamoDB under network partition and normal operation.", ["PACELC", "Cassandra", "DynamoDB"]),
    ("Hydroponics pH Drift Chelated Iron", "NanoPro, in hydroponics and aeroponics nutrient solutions, why does pH drift occur over time, how does it cause nutrient lockout, and what is the chemical mechanism of chelated iron (Fe-EDDHA vs Fe-EDTA) across different pH ranges?", ["EDDHA", "EDTA", "lockout"]),
    ("Bullet Kinetic Energy & Twist Rate", "NanoPro, a 7.62x39mm rifle cartridge fires a 7.9-gram (122 grain) bullet with a muzzle velocity of 720 m/s. Calculate its kinetic energy in Joules and foot-pounds, and explain the gyroscopic stability factor.", ["2,044", "Joules", "twist"]),
    ("Blue Carbon Mangroves", "NanoPro, explain the ecological and biogeochemical mechanism of 'Blue Carbon' sequestration in mangrove forests.", ["Blue Carbon", "anaerobic", "mangrove"]),

    # --- Technical & SQL Interview Challenges ---
    ("Self-Join Manager", "NanoPro, write a SQL query to display each employee's name along with their manager's name from an EMPLOYEES table using a self-join.", ["JOIN", "manager", "COALESCE"]),
    ("Frequency Inverted Dict", "NanoPro, write a Python script that takes a list of integers and returns the most frequent element and an inverted dictionary.", ["freq_dict", "inverted_dict"]),
    ("3rd Highest Salary DENSE_RANK", "NanoPro, write a SQL query using Window Functions (DENSE_RANK) to find the 3rd highest salary in each department.", ["DENSE_RANK", "salary"]),
    ("Gaps & Islands Login Streaks", "NanoPro, in SQL, how do you solve the 'Gaps and Islands' problem to find consecutive active login streaks of users?", ["ROW_NUMBER", "island", "streak"]),
    ("10GB Generator Execution Timer", "NanoPro, write a Python generator function that streams a 10 GB log file line-by-line with a decorator that logs execution time.", ["generator", "yield", "timer"]),
    ("Recursive JSON Flattener", "NanoPro, write a Python script that recursively flattens a deeply nested JSON object with multithreading.", ["flatten", "ThreadPool"]),
    ("AWS S3 to Snowflake ETL", "NanoPro, design a fault-tolerant ETL pipeline architecture that ingests 500,000 JSON records per hour from AWS S3 into Snowflake.", ["MERGE", "S3", "Snowflake"]),
    ("2nd Highest without LIMIT/TOP", "NanoPro, write a SQL query to find the second highest salary without using LIMIT, TOP, or OFFSET.", ["MAX", "salary"]),
    ("PIVOT without PIVOT Keyword", "NanoPro, write a SQL query to pivot monthly sales data without using the PIVOT keyword.", ["CASE WHEN", "SUM"]),
    ("Consecutive 3-Month Purchases", "NanoPro, write a SQL query to find customers who made consecutive purchases for 3 consecutive months.", ["LAG", "month"]),
    ("Two Sum O(n)", "NanoPro, write a Python function for Two Sum problem in O(n) time complexity.", ["two_sum", "time"]),
    ("Valid Brackets Stack", "NanoPro, write a Python function to validate balanced parentheses and brackets using a Stack.", ["stack", "is_valid_brackets"]),
    ("Two-Pointer Merge Sorted", "NanoPro, write a Python function to merge two sorted arrays into one sorted array in O(n+m) time without using sort().", ["merge", "two-pointer"]),
    ("SQLite 10k Batch Insert", "NanoPro, write a Python script to batch insert 10,000 records into SQLite using executemany within a transaction.", ["executemany", "sqlite"]),

    # --- Lakehouse Progression & Supreme Commands ---
    ("Bronze Table Ingestion", "NanoPro, execute Phase 1: Ingest Bronze dirty transactions table with messy data.", ["BRONZE", "dirty", "raw"]),
    ("Silver Data Cleaning", "NanoPro, execute Phase 2: Python Silver data cleaning and validation pipeline.", ["SILVER", "cleaning", "deduplicate"]),
    ("Gold Star Schema", "NanoPro, execute Phase 3: Gold Star Schema transformation with DENSE_RANK and priority tagging.", ["GOLD", "DENSE_RANK", "HNI"]),
    ("Multi-Sheet Excel Audit", "NanoPro, generate the multi-sheet Excel audit report daily_lakehouse_audit.xlsx.", ["daily_lakehouse_audit.xlsx", "Summary", "High_Value_Alerts"]),
    ("Final Deployment Sequence", "NanoPro, execute the final deployment and notification sequence for the Lakehouse EOD audit.", ["Final Deployment", "EOD", "mangeshbagul15@gmail.com"]),
    ("Supreme Master Command", "NanoPro, SUPREME MASTER COMMAND: FULL-SPECTRUM END-TO-END EXECUTION DRILL.", ["PHASE 1", "PHASE 2", "PHASE 3", "PHASE 4", "PHASE 5"]),
    ("Supreme SOC Brute Force", "NanoPro, SUPREME COMMAND: CYBER-SECURITY SOC & BRUTE-FORCE INTRUSION SENTINEL.", ["SOC", "brute-force", "192.168.1.105"]),
    ("Supreme Algo Trading RSI", "NanoPro, SUPREME COMMAND: FINANCIAL DATA SCIENCE & ALGORITHMIC TRADING INDICATOR.", ["TATA_STEEL", "RSI", "SMA_5"]),
    ("Supreme ML Churn", "NanoPro, SUPREME COMMAND: END-TO-END MACHINE LEARNING CHURN PREDICTION PIPELINE.", ["Churn", "92.4%"]),
    ("Supreme Reconciliation", "NanoPro, SUPREME COMMAND: FINANCIAL RECONCILIATION & DISCREPANCY DISCOVERY ENGINE.", ["Reconciliation", "AMOUNT_MISMATCH", "UNSETTLED_ORPHAN"]),
    ("Supreme Oracle PL/SQL Bulk", "NanoPro, SUPREME MASTER COMMAND: ORACLE PL/SQL HIGH-CONCURRENCY BULK TRANSACTION ENGINE.", ["BULK COLLECT", "FORALL", "SAVE EXCEPTIONS"]),
    ("Supreme Snowflake Streams & Tasks", "NanoPro, SUPREME MASTER COMMAND: SNOWFLAKE STREAMS & TASKS CONTINUOUS CDC LAKEHOUSE.", ["CREATE OR REPLACE STREAM", "CREATE OR REPLACE TASK", "SYSTEM$STREAM_HAS_DATA"]),
    ("Supreme Cross-Platform CDC", "NanoPro, SUPREME COMMAND: CROSS-PLATFORM ORACLE-TO-SNOWFLAKE CDC PIPELINE.", ["oracledb", "snowflake.connector", "write_pandas"]),
    ("Supreme FinOps Cost Sentinel", "NanoPro, SUPREME COMMAND: SNOWFLAKE COST SENTINEL: FINOPS ANALYTICS.", ["QUERY_HISTORY", "execution_time > 900000", "FinOps"]),
    ("SCD Type 2 Customer History", "NanoPro, implement SCD Type 2 dimension customer history.", ["SCD Type 2", "is_current", "valid_to"])
]

def run_tests():
    passed = 0
    failed = 0
    hijacked = 0
    total = len(TEST_CASES)

    print(f"\n========================================================")
    print(f"RUNNING COMPREHENSIVE DRILL BENCHMARK: {total} PROMPTS")
    print(f"========================================================\n")

    for idx, (title, prompt, expected_keywords) in enumerate(TEST_CASES, 1):
        res = handle_extended_intents(prompt.lower(), prompt, session_id="test_suite")
        if not res or not res.get("handled"):
            print(f"[{idx}/{total}] ❌ FAILED (Not Handled): {title}")
            failed += 1
            continue

        reply = res.get("reply", "")
        # Check for hijacking
        is_hijacked = (
            "SELECT * FROM BANK_DB.L0_STAGING.ACCOUNTS" in reply or
            "Table Structural Architecture: TRANSACTIONS" in reply or
            ("I'm sorry, but I can't assist with that request" in reply)
        )

        # Check for expected keywords
        missing_kw = [kw for kw in expected_keywords if kw.lower() not in reply.lower()]

        if is_hijacked:
            print(f"[{idx}/{total}] 🚨 HIJACKED: {title}")
            hijacked += 1
        elif missing_kw:
            print(f"[{idx}/{total}] ⚠️ MISSING KEYWORDS {missing_kw}: {title}")
            print(f"      Snippet: {reply[:150]}...")
            failed += 1
        else:
            print(f"[{idx}/{total}] ✅ PASSED: {title} (Agent: {res.get('agent_id')})")
            passed += 1

    print(f"\n========================================================")
    print(f"RESULTS: {passed}/{total} PASSED | {failed} FAILED | {hijacked} HIJACKED")
    print(f"========================================================\n")

    if passed == total:
        print("🎯 100% SUCCESS: All prompts verified with ZERO hijacking!")
        return 0
    else:
        print("⚠️ Some tests did not pass.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
