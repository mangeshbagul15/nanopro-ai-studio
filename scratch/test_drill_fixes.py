import os
import sys
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')

from app.agents.extended_intents import handle_extended_intents

test_prompts = [
    # 1. System Override
    ("System Override", "SYSTEM OVERRIDE COMMAND: EXECUTE ACTIONS NOW (NO THEORETICAL TEXT)"),
    # 2. Workspace Scan
    ("Workspace Scan", "NanoPro, scan my workspace 'data/' folder right now. List all files, their record counts, and show me the first 3 rows of customer_transactions.csv."),
    # 3. Fire-Drill 5 Domains
    ("Fire-Drill 5 Domains", "CROSS-DOMAIN INTELLIGENCE FIRE-DRILL: 5 DOMAINS (CONCISE & MATHEMATICAL)"),
    # 4. Excel Generation
    ("Excel Gen", "NanoPro, generate a real Excel (.xlsx) file in the 'data/' folder named 'sales_q4_summary.xlsx' with 5 columns (OrderID, Customer, Product, Amount, Date) and 10 rows of realistic data. Verify the file exists and tell me its file path."),
    # 5. EMI Home loan
    ("EMI Calculation", "NanoPro, derive and calculate the exact Monthly EMI for a home loan of ₹50,00,000 at 8.5% annual interest rate for a tenure of 20 years. Show the mathematical formula: P * r * (1+r)^n / ((1+r)^n - 1) step-by-step."),
    # 6. Mars Escape Velocity
    ("Mars Velocity", "NanoPro, calculate the exact Escape Velocity from the surface of Mars. Given: Mass of Mars M = 6.42 × 10^23 kg, Radius R = 3,389.5 km, and Gravitational constant G = 6.674 × 10^-11 N m²/kg². Show the calculation in km/s."),
    # 7. Water Tank
    ("Water Tank", "NanoPro, calculate the water capacity (in Liters) and the base pressure (in kN/m²) for an underground RCC rectangular water tank with internal dimensions: Length = 8m, Width = 5m, Water Depth = 3.5m. Take unit weight of water = 9.81 kN/m³."),
    # 8. Warfarin & Aspirin
    ("Warfarin & Aspirin", "NanoPro, explain the clinical pharmacokinetic interaction between Warfarin (anticoagulant) and Aspirin (antiplatelet) when prescribed together. Which CYP450 enzyme is involved, and what is the biological risk to the patient?"),
    # 9. Panipat & Zamburak
    ("Panipat Zamburak", "NanoPro, analyze the tactical military mistake made on the battlefield of the 3rd Battle of Panipat (1761). What role did Ahmad Shah Abdali's camel-mounted swivel guns (Zamburak) play against the Maratha cavalry?"),
    # 10. Snowflake LATERAL FLATTEN
    ("LATERAL FLATTEN", "NanoPro, I have a Snowflake column raw_payload containing nested JSON with arrays: {\"customer_id\": 101, \"orders\": [{\"item\": \"Laptop\", \"price\": 80000}, {\"item\": \"Mouse\", \"price\": 1500}]}. Write a single Snowflake SQL query using LATERAL FLATTEN to convert this into a flat relational table."),
    # 11. XGBoost Fraud
    ("XGBoost Fraud", "NanoPro, I have 1,000,000 credit card transactions where only 100 are fraudulent (99.99% class imbalance). Standard accuracy is useless here. Write a concise Python script using XGBoost, PR-AUC, and Scale_pos_weight to detect these frauds without overfitting."),
    # 12. SQL Injection
    ("SQL Injection", "NanoPro, look at this vulnerable Python code: query = f\"SELECT * FROM users WHERE username = '{user_input}'\". Show how an attacker can bypass login using ' OR '1'='1, and rewrite the code using secure Parameterized Queries (Prepared Statements)."),
    # 13. Marathi Mentor
    ("Marathi Mentor", "NanoPro, समजा मी आज ऑफिसच्या कामामुळे आणि सततच्या पाईपलाईन एरर्समुळे खूप थकून गेलोय. मला एक सिनियर मार्गदर्शक आणि चांगल्या मित्रासारखा २ मिनिटांत मराठीत असा सल्ला दे, ज्यामुळे माझा मूड चांगला होईल आणि उद्या नव्या उत्साहाने काम करता येईल!"),
    # 14. Autonomous Benchmark Mission
    ("Benchmark Mission", "# AUTONOMOUS BENCHMARK MISSION: MULTI-DISCIPLINARY COGNITIVE & SYSTEM EXECUTION DRILL\nTARGET AI AGENT: Mangesh Nano Pro AI Core\nMODULE 1: DEEP INTERNAL SYSTEM & DATABASE INTROSPECTION\nMODULE 2: DATA ENGINEERING\nMODULE 3: MULTI-DISCIPLINARY\nMODULE 4: AUTOMATED REPORT\nMODULE 5: SCHEDULER")
]

all_passed = True
for name, p in test_prompts:
    p_lower = p.lower().strip()
    res = handle_extended_intents(p_lower, p)
    handled = res.get('handled') if res else False
    agent = res.get('agent_id') if res else 'None'
    reply = res.get('reply', '') if res else ''
    
    # Check that it didn't return the generic ACCOUNTS table query
    is_hijacked = "SELECT * FROM BANKDB.L0STAGING.ACCOUNTS" in reply or "SELECT * FROM BANKDB.L0STAGING.LOANS" in reply or "SELECT * FROM BANKDB.L0STAGING.RELATIONAL" in reply
    if is_hijacked:
        print(f"❌ [{name}] HIJACKED BY GENERIC TABLE QUERY!")
        all_passed = False
    elif not handled:
        print(f"⚠️ [{name}] NOT HANDLED!")
        all_passed = False
    else:
        print(f"✅ [{name}] SUCCESS | Agent: {agent} | ReplyLen: {len(reply)} chars")
        print("   Snippet:", reply[:110].replace('\n', ' '))

if all_passed:
    print("\n🎉 ALL 14 TEST PROMPTS PASSED WITH ZERO HIJACKING!")
else:
    print("\n⚠️ SOME TESTS FAILED!")
