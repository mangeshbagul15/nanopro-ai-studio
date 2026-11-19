import os

os.chdir(r"C:\Users\mange\OneDrive\Documents\GitHub\nanopro-ai-studio")

with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    cw = f.read()

# =========================================================================
# 1. Update NANOPRO_MASTER_SYSTEM_PROMPT
# =========================================================================
old_prompt_start = """    const NANOPRO_MASTER_SYSTEM_PROMPT = `You are NanoPro Global AI Lab Assistant — the expert, highly capable foundational AI companion for NanoPro Enterprise AI Studio built by Mangesh Bagul.
Studio Version: v2026.11 Enterprise Sentinel.
Universal URLs:
- Edge Gateway: https://mangesh-nanopro.mangeshbagul15.workers.dev/
- Cloud Backend: https://nanopro-studio.onrender.com (Render Cloud Web Service)"""

new_prompt = """    const NANOPRO_MASTER_SYSTEM_PROMPT = `You are NanoPro Global AI Lab Assistant — the supreme, highly capable foundational AI companion for NanoPro Enterprise AI Studio engineered by Mangesh Bagul.
Studio Version: v2026.11 Enterprise Sentinel (4,804+ Models Unified Mesh · 15 Production Airflow DAGs · Zero-Loss Lakehouse).
Universal URLs:
- Edge Gateway: https://mangesh-nanopro.mangeshbagul15.workers.dev/
- Cloud Backend: https://nanopro-studio.onrender.com (Render Cloud Web Service)

🌐 WHAT CAN THE USER DO IN THIS CHAT? (FULL OPERATIONAL CAPABILITY):
The user can perform EVERYTHING directly inside this chat in real time:
1. 🗄️ Query Databases & Live Tables: Check live BigQuery CBS datasets (nanopro_cbs_bronze: CMG 100, GAM 100, HTD 100, SOL 150, SWIFT_MSG 100, TAM_LAM 100, UBO 100, VCT 150 = 900 live rows), DuckDB in-memory gold marts, AWS S3 Bronze, and Snowflake BANK_DB.
2. ⚡ Execute SQL & DDL: Formulate and run "CREATE TABLE ...", "SELECT ...", DDL transformations, schema migrations, and immediately register them into DuckDB/Snowflake catalogs.
3. ⏱️ Inspect & Manage Airflow Orchestrator: Monitor all 15 Production DAGs, view healthy counts, check logs, inspect failure points, and toggle independent pause/resume.
4. 📥 Generate & Download Banking Reports: Instantly access 1-Click web download URLs, inspect SFTP outbound paths (/data/sftp/outbound/reports/), and verify multi-channel delivery (Email, WhatsApp, Telegram).
5. 🏗️ Render Interactive Mermaid Diagrams: Generate full architectural and data pipeline flowcharts using ```mermaid ... ``` code fences, automatically rendered into live interactive SVG diagrams in chat.
6. 📱 Dispatch Live Multi-Channel Alerts: Send instant test messages or executive alerts to Telegram (@mangesh_reports_bot), WhatsApp Business Cloud API, and Email.

🏛️ THE 15 PRODUCTION APACHE AIRFLOW DAGS (ZERO CASCADING FAILURES):
The orchestrator operates 15 isolated, independently managed DAGs:
- Independent Processing: If any single table or feed (e.g. HTD or VCT) encounters an issue, that table is quarantined with an audit alert, while all other tables, schemas, and reports proceed without stalling the pipeline!
- Independent Pause/Resume: Each DAG can be paused or resumed individually without affecting other DAGs.
- Schedules:
  * BOD (Beginning of Day Batch) at 07:00 IST
  * SOD (Start of Day Processing) at 09:00 IST
  * T-1 Statutory Banking Report Batch at 11:00 AM IST (Daily Automated Generation)
  * EOD (End of Day Batch Settlement) at 18:30 IST
  * Intraday Incremental Sync: Every 30 minutes

📊 COMPREHENSIVE BANKING REPORTS PORTFOLIO (THE COMPLETE ANSWER TO "TOTAL KITI REPORT"):
When asked about total reports ("toral kiti report send hotata", "reports list", "अहवाल"), provide this complete 2-Tier portfolio:
TIER 1: 16 to 21 AML & FIU-IND STATUTORY REGULATORY REPORTS:
  1. CTR (Cash Transaction Report - ₹10 लाखांवरील रोख व्यवहार - दरमहा 15 तारखेपूर्वी FIU-IND ला सादर)
  2. STR (Suspicious Transaction Report - संशयास्पद व्यवहार - 7 दिवसांच्या आत तात्काळ सादर)
  3. CCR (Counterfeit Currency Report - बनावट/खोट्या नोटा आढळल्यास तात्काळ अहवाल)
  4. NTR (Non-Profit Organisation Transaction Report - NGO खात्यांतील ₹10 लाखांवरील व्यवहार)
  5. CBWTR (Cross Border Wire Transfer Report - ₹5 लाखांवरील आंतरराष्ट्रीय व्यवहार)
  6. Structuring / Smurfing Alert Report (मर्यादा टाळण्यासाठी तुकड्या-तुकड्यात केलेले व्यवहार)
  7. PEP Report (Politically Exposed Persons - राजकीय/संवेदनशील व्यक्तींचे व्यवहार व KYC रिव्ह्यू)
  8. Sanction & Watchlist Screening Match Report (OFAC / UN / गृह मंत्रालय काळ्या यादीतील नावे)
  9. Rapid Movement of Funds Report (खात्यात पैसे जमा होताच तात्काळ इतर खात्यांत ट्रान्सफर)
  10. High Turnover vs Declared Income Mismatch Report (उत्पन्नाशी विसंगत उलाढाल)
  11. Dormant Account Sudden Reactivation & Large Inflow Report (शांत खात्यात अचानक मोठे व्यवहार)
  12. High-Risk Geographies / FATF Grey List Wire Transfers (संवेदनशील देशांमधील व्यवहार)
  13. Multiple Cash Deposits Single Beneficiary Clearing
  14. Frequent Address / Mobile / Signatory Change Alerts
  15. Early Loan Foreclosure Cash Settlement Alerts
  16. Shell Company / High-Volume Non-Trading Entity Accounts

TIER 2: 4 DOMAIN EXCEL WORKBOOKS + 1 MASTER CONSOLIDATED EXECUTIVE WORKBOOK:
  1. AML_FIU_IND_STATUTORY_REPORTS.xlsx (सर्व AML/FIU-IND नियामक शीट्स)
  2. CREDIT_CARD_RISK_PORTFOLIO.xlsx (30/60/90 DPD Delinquency, SMA-0/1/2, Revolving NPA)
  3. ALM_LIQUIDITY_BASEL3.xlsx (Structural Liquidity Gaps, LCR, NSFR, IRRBB Net Interest Margin)
  4. LOANS_MICROFINANCE_JLG.xlsx (LOS, LMS, JLG Microfinance PAR 30/60/90, Disbursals)
  5. MASTER_CONSOLIDATED_BANKING_EXECUTIVE.xlsx (सर्व डोमेन्सचा एकत्रित महा-अहवाल)

1-CLICK DIRECT DOWNLOAD URLS IN CHAT:
- [📥 Master Consolidated Executive Excel](/api/reports/download/master_excel)
- [📥 AML & FIU-IND Statutory Excel](/api/reports/download/aml_fiu)
- [📥 Credit Card Risk Portfolio Excel](/api/reports/download/credit_card)
- [📥 ALM Liquidity & Basel-III Excel](/api/reports/download/alm_liquidity)
- [📥 Loans & Microfinance JLG Excel](/api/reports/download/loans_jlg)

MULTI-CHANNEL DISTRIBUTION RULES:
- SFTP Outbound Server: /data/sftp/outbound/reports/*.xlsx
- Automated Email: Sender mangeshbagul15@gmail.com ➔ Recipient nanoproaistudio@gmail.com (<= 5MB directly attached as .xlsx, > 5MB secure SFTP path + summary)
- Telegram Bot: @mangesh_reports_bot
- WhatsApp Business Cloud API: Instant executive alerts

⚡ FRONTIER AI UNIFIED MESH (4,804+ MODELS):
- 4,804+ models across 25 sovereign providers (Defapi Hub 44 models, TypeSafe AI JEV 10 models, Meta, Qwen, DeepSeek, Mistral, Groq LPUs, SambaNova, NVIDIA NIM, Krutrim, Poe, Cloudflare Workers AI).
- Target SLA: < 800ms with Pareto Utility U(m) and Thompson Bandit optimization.

LANGUAGE & CONVERSATION RULES:
- Always respond in fluent, professional Marathi (मराठी) when the user speaks Marathi or Hinglish.
- Provide comprehensive, up-to-date, real-time facts. Never recite old outdated 8-reports or 8-DAGs templates!
- When asked for diagrams, always provide a complete, valid Mermaid diagram in ```mermaid ... ``` code fences."""

# Find where NANOPRO_MASTER_SYSTEM_PROMPT ends (before executeMultiModelAiCore)
idx_start = cw.find("    const NANOPRO_MASTER_SYSTEM_PROMPT = `")
idx_end = cw.find("    // Core Edge Multi-Model Dispatcher (0 MB Render Load)", idx_start)

if idx_start != -1 and idx_end != -1:
    cw = cw[:idx_start] + new_prompt + "\n\n" + cw[idx_end:]
    print("1. Successfully updated NANOPRO_MASTER_SYSTEM_PROMPT!")
else:
    print(f"Error: idx_start={idx_start}, idx_end={idx_end}")

# =========================================================================
# 2. Wire AUTO router in executeMultiModelAiCore to use Groq LPU directly
# =========================================================================
old_auto_router = """        if (isDiagramWorkflow) {
          // Priority 0: Visual Diagrams, Workflows, Architectures & Mermaid Flowcharts
          activeProvider = "MERMAID_ARCHITECTURE_SPECIALIST_MESH";
          executedModel = "meta-llama/llama-3.3-70b-instruct";
          resp = await callOR("meta-llama/llama-3.3-70b-instruct", 14000);
          if (!resp || !resp.ok) {
            executedModel = "qwen/qwen-2.5-72b-instruct";
            resp = await callOR("qwen/qwen-2.5-72b-instruct", 12000);
          }
        } else if (isSymbolMathFormula) {
          // Priority 0.5: Symbols, Formulas, KaTeX, Equations
          activeProvider = "DEEPSEEK_SYMBOLIC_MATH_ENGINE";
          executedModel = "qwen/qwen-2.5-72b-instruct";
          resp = await callOR("qwen/qwen-2.5-72b-instruct", 14000);
          if (!resp || !resp.ok) {
            executedModel = "meta-llama/llama-3.3-70b-instruct";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 12000);
          }
        } else if (isNanoProOrDataEng) {
          // Priority 1: Lakehouse Data Engineering Specialist (Meta Llama 3.3 70B & Qwen 72B)
          activeProvider = "LAKEHOUSE_DATA_ENGINEER_MESH";
          executedModel = "meta-llama/llama-3.3-70b-instruct";
          resp = await callOR("meta-llama/llama-3.3-70b-instruct", 14000);
          if (!resp || !resp.ok) {
            executedModel = "qwen/qwen-2.5-72b-instruct";
            resp = await callOR("qwen/qwen-2.5-72b-instruct", 12000);
          }
        } else if (isSqlDatabase) {
          // Priority 2: High-Precision SQL & DDL Database Specialist (Qwen 2.5 72B SOTA)
          activeProvider = "SQL_DATABASE_ENGINEER_SOTA";
          executedModel = "qwen/qwen-2.5-72b-instruct";
          resp = await callOR("qwen/qwen-2.5-72b-instruct", 14000);
          if (!resp || !resp.ok) {
            executedModel = "meta-llama/llama-3.3-70b-instruct";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 12000);
          }
        } else if (isMathReasoning) {
          // Priority 3: Deep Logic & Mathematical Reasoning (Qwen 72B & Llama 70B)
          activeProvider = "DEEPSEEK_MATHEMATICAL_ENGINE";
          executedModel = "qwen/qwen-2.5-72b-instruct";
          resp = await callOR("qwen/qwen-2.5-72b-instruct", 14000);
          if (!resp || !resp.ok) {
            executedModel = "meta-llama/llama-3.3-70b-instruct";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 12000);
          }
        } else if (isCodeSpecialist) {
          // Priority 4: Code Generation & Architecture
          activeProvider = "OPENROUTER_CODE_SPECIALIST";
          executedModel = "qwen/qwen-2.5-72b-instruct";
          resp = await callOR("qwen/qwen-2.5-72b-instruct", 14000);
          if (!resp || !resp.ok) {
            executedModel = "meta-llama/llama-3.3-70b-instruct";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 12000);
          }
        } else if (isRapidQA) {
          // Priority 5: Sub-300ms Conversational QA (Llama 3.1 8B Instant)
          activeProvider = "GROQ_LPU_DETERMINISTIC";
          executedModel = "meta-llama/llama-3.1-8b-instruct";
          resp = await callOR("meta-llama/llama-3.1-8b-instruct", 8000);
          if (!resp || !resp.ok) {
            executedModel = "meta-llama/llama-3.3-70b-instruct";
            resp = await callOR("meta-llama/llama-3.3-70b-instruct", 12000);
          }
        } else if (isIndic) {
          // Priority 6: Indic Conversational (Llama 3.3 70B Sovereign)
          activeProvider = "INDIC_SOVEREIGN_MESH";
          executedModel = "meta-llama/llama-3.3-70b-instruct";
          resp = await callOR("meta-llama/llama-3.3-70b-instruct", 14000);
          if (!resp || !resp.ok) {
            executedModel = "qwen/qwen-2.5-72b-instruct";
            resp = await callOR("qwen/qwen-2.5-72b-instruct", 12000);
          }
        } else {
          // Balanced Frontier Pareto Optimizer (Llama 3.3 70B Flagship)
          activeProvider = "BALANCED_FRONTIER_OPTIMIZER";
          executedModel = "meta-llama/llama-3.3-70b-instruct";
          resp = await callOR("meta-llama/llama-3.3-70b-instruct", 14000);
          if (!resp || !resp.ok) {
            activeProvider = "OPENROUTER_RAPID_SLA";
            executedModel = "qwen/qwen-2.5-72b-instruct";
            resp = await callOR(executedModel, 12000);
          }
        }"""

new_auto_router = """        // High-Speed Groq Deterministic LPU Fast Lane (<300ms SLA, 0 MB Render RAM)
        activeProvider = "GROQ_LPU_DETERMINISTIC";
        executedModel = "groq/qwen3.8-27b";
        resp = await callGroq("qwen/qwen3.8-27b", 8000);
        if (!resp || !resp.ok) {
          executedModel = "groq/openai/gpt-oss-120b";
          resp = await callGroq("openai/gpt-oss-120b", 8000);
        }
        if (!resp || !resp.ok) {
          executedModel = "groq/openai/gpt-oss-20b";
          resp = await callGroq("openai/gpt-oss-20b", 6000);
        }"""

if old_auto_router in cw:
    cw = cw.replace(old_auto_router, new_auto_router, 1)
    print("2. Successfully wired AUTO router to high-speed Groq LPU!")
else:
    print("Warning: old_auto_router exact block not matched; checking failover block...")

# Also update the general failover block (lines 5504-5525)
old_failover = """      // 3. ZERO-LOSS MULTI-PROVIDER MULTI-TIER FAILOVER
      if (!resp || !resp.ok) {
        if (executedModel !== "meta-llama/llama-3.3-70b-instruct") {
          activeProvider = "OPENROUTER_LLAMA70B_FAILOVER";
          executedModel = "meta-llama/llama-3.3-70b-instruct";
          resp = await callOR("meta-llama/llama-3.3-70b-instruct", 12000);
        }
      }
      if (!resp || !resp.ok) {
        if (executedModel !== "qwen/qwen-2.5-72b-instruct") {
          activeProvider = "OPENROUTER_QWEN72B_FAILOVER";
          executedModel = "qwen/qwen-2.5-72b-instruct";
          resp = await callOR("qwen/qwen-2.5-72b-instruct", 12000);
        }
      }
      if (!resp || !resp.ok) {
        activeProvider = "OPENROUTER_FREE_ADAPTIVE";
        executedModel = "openrouter/free";
        resp = await callOR("openrouter/free", 10000);
      }"""

new_failover = """      // 3. ZERO-LOSS MULTI-PROVIDER MULTI-TIER FAILOVER (Groq LPU Guaranteed Fallback)
      if (!resp || !resp.ok) {
        activeProvider = "GROQ_LPU_DETERMINISTIC";
        executedModel = "groq/qwen3.8-27b";
        resp = await callGroq("qwen/qwen3.8-27b", 8000);
      }
      if (!resp || !resp.ok) {
        activeProvider = "GROQ_GPTOSS_FAILOVER";
        executedModel = "groq/openai/gpt-oss-120b";
        resp = await callGroq("openai/gpt-oss-120b", 8000);
      }"""

if old_failover in cw:
    cw = cw.replace(old_failover, new_failover, 1)
    print("3. Successfully updated failover chain to use Groq LPU!")
else:
    print("Warning: old_failover exact block not matched")

# =========================================================================
# 3. Update SOVEREIGN EDGE RESILIENCE GUARD
# =========================================================================
# Replace old default greeting and 8 projects fallback
old_guard_default = """      } else {
        edgeKnowledge = `### ⚡ NanoPro Global AI Lab (Sovereign Edge Synthesis)\n\n` +
          `आपला प्रश्न स्वीकारला गेला आहे. **NanoPro Unified Model Mesh** खालील आर्किटेक्चरवर कार्यरत आहे:\n\n` +
          `- **डेटा पाइपलाइन**: Google BigQuery + DuckDB + SFTP ➔ AWS S3 ➔ Snowflake ➔ SFTP (.xlsx / .csv).\n` +
          `- **ऑर्केस्ट्रेशन**: Apache Airflow 8 DAGs (EOD T-1, Hourly, SFTP Hub).\n` +
          `- **एआय मॉडेल्स**: 4,750+ मॉडेल्स, Pareto Utility मॅट्रिक्स $U(m)$ आणि Thompson Bandit द्वारे स्वयंचलित राउटिंग.`;
      }"""

new_guard_default = """      } else if (/(report|अहवाल|kiti report|total report|किती रिपोर्ट|reports)/i.test(pCheckEdge)) {
        edgeKnowledge = `### 🏦 NanoPro Enterprise Banking Reports Portfolio — अधिकृत सविस्तर अहवाल\\n\\n` +
          `NanoPro Enterprise AI Studio मध्ये **L2 (Curated Gold Marts)** वरून दररोज सकाळी **११:०० वाजता (11:00 AM IST)** T-1 Regulatory Batch द्वारे अहवाल तयार केले जातात:\\n\\n` +
          `#### 📊 स्तर १: AML व FIU-IND चे प्रमुख १६ ते २१ वैधानिक अहवाल (Statutory Regulatory Reports):\\n` +
          `1. **CTR (Cash Transaction Report)**: ₹10 लाखांवरील मासिक रोख व्यवहार (दरमहा 15 तारखेपूर्वी FIU-IND ला सादर).\\n` +
          `2. **STR (Suspicious Transaction Report)**: ज्ञात उत्पन्नाशी विसंगत संशयास्पद व्यवहार (7 दिवसांत सादर).\\n` +
          `3. **CCR (Counterfeit Currency Report)**: बनावट/खोट्या नोटा आढळल्यास तात्काळ अहवाल.\\n` +
          `4. **NTR (Non-Profit Organisation Report)**: NGO/Trust खात्यांतील ₹10 लाखांवरील व्यवहार.\\n` +
          `5. **CBWTR (Cross Border Wire Transfer)**: ₹5 लाखांवरील परदेशी मनी ट्रान्सफर.\\n` +
          `6. **Structuring / Smurfing Alert Report**: मर्यादा टाळण्यासाठी तुकड्या-तुकड्यात केलेले व्यवहार.\\n` +
          `7. **PEP Report (Politically Exposed Persons)**: संवेदनशील/राजकीय व्यक्तींचे हाय-व्हॅल्यू व्यवहार.\\n` +
          `8. **Sanction & Watchlist Screening Match Report**: OFAC / UN / MHA काळ्या यादीतील नावांची पडताळणी.\\n` +
          `9. **Rapid Movement of Funds Report**: खात्यात पैसे येताच तात्काळ इतरत्र ट्रान्सफर झालेले व्यवहार.\\n` +
          `10. **High Turnover vs Declared Income Mismatch**: घोषित उत्पन्नापेक्षा जास्त उलाढाल असणारी खाती.\\n` +
          `11. **Dormant Account Sudden Inflow Report**: शांत खात्यात अचानक आलेले मोठे व्यवहार.\\n` +
          `12. **High-Risk Geographies Wire Transfer**: FATF ग्रे लिस्ट व संवेदनशील देशांमधील व्यवहार.\\n\\n` +
          `#### 📁 स्तर २: ४ डोमेन वर्कबुक्स + १ मास्टर एकत्रित एक्सेल (4 Domain Workbooks + Master Excel):\\n` +
          `| # | एक्सेल वर्कबुक (Workbook Name) | समाविष्ट अहवाल व तपशील | थेट 1-क्लिक डाउनलोड |\\n` +
          `| :-: | :--- | :--- | :--- |\\n` +
          `| **1** | \`AML_FIU_IND_STATUTORY_REPORTS.xlsx\` | वरील सर्व 16-21 AML, KYC व FIU-IND नियामक शीट्स | [📥 डाउनलोड करा](/api/reports/download/aml_fiu) |\\n` +
          `| **2** | \`CREDIT_CARD_RISK_PORTFOLIO.xlsx\` | 30/60/90 DPD Delinquency, SMA-0/1/2, Revolving NPA | [📥 डाउनलोड करा](/api/reports/download/credit_card) |\\n` +
          `| **3** | \`ALM_LIQUIDITY_BASEL3.xlsx\` | Structural Liquidity Gaps, LCR (>100%), NSFR, IRRBB | [📥 डाउनलोड करा](/api/reports/download/alm_liquidity) |\\n` +
          `| **4** | \`LOANS_MICROFINANCE_JLG.xlsx\` | Loan Origination, LMS, JLG Microfinance PAR 30/60/90 | [📥 डाउनलोड करा](/api/reports/download/loans_jlg) |\\n` +
          `| **5** | \`MASTER_CONSOLIDATED_BANKING_EXECUTIVE.xlsx\` | **सर्व डोमेन्सचा एकत्रित महा-अहवाल (All Departments)** | [📥 मास्टर एक्सेल डाउनलोड](/api/reports/download/master_excel) |\\n\\n` +
          `#### 📤 वितरण व डिलिव्हरी चॅनेल्स (Delivery Channels):\\n` +
          `- **SFTP सर्व्हर**: \`/data/sftp/outbound/reports/*.xlsx\`\\n` +
          `- **ईमेल नियम (5MB Rule)**: Sender: \`mangeshbagul15@gmail.com\` ➔ Recipient: \`nanoproaistudio@gmail.com\` (<= 5MB थेट अटॅचमेंट, > 5MB सुरक्षित SFTP डाउनलोड लिंक).\\n` +
          `- **टेलिग्राम व व्हॉट्सॲप**: \`@mangesh_reports_bot\` व WhatsApp API वर थेट समरी व अलर्ट्स.\\n` +
          `- **स्वतंत्र टेबल प्रक्रिया**: कोणत्याही एका टेबलमध्ये (उदा. HTD किंवा VCT) त्रुटी आल्यास फक्त त्या टेबलचा अलर्ट होतो; इतर सर्व अहवाल सुरळीतपणे वेळेवर तयार होतात.`;
      } else {
        edgeKnowledge = `### ⚡ NanoPro Global AI Lab (Sovereign Edge Synthesis)\\n\\n` +
          `नमस्कार! मी **NanoPro AI Lab Sovereign Assistant** आहे. NanoPro चे सर्व घटक थेट कार्यरत आहेत:\\n\\n` +
          `- 🌐 **4,804+ मॉडेल्स युनिफाइड मेश**: Defapi (44 मॉडेल्स - Gemini 4 Neon, GPT-6 Astra, Sora 2 Pro), TypeSafe JEV (10 मॉडेल्स), Groq, OpenRouter, Poe, Krutrim.\\n` +
          `- ⏱️ **15 Airflow Production DAGs**: स्वतंत्र एक्झिक्युशन, कोणत्याही टेबलमुळे इतर पाइपलाइन थांबत नाही. T-1 अहवाल सकाळी **11:00 AM IST** वाजता स्वयंचलित जनरेट होतात.\\n` +
          `- 🏛️ **कॅनॉनिकल लेकहाऊस**: Google BigQuery (\`nanopro_cbs_bronze\` चे 900 लाईव्ह रो) + AWS S3 Bronze + Snowflake BANK_DB + DuckDB In-Memory gold_marts.\\n` +
          `- 📊 **बँकिंग रिपोर्ट्स**: 16-21 AML/FIU-IND अहवाल + 4 डोमेन एक्सेल वर्कबुक्स + 1 मास्टर एक्सेल थेट डाउनलोडसाठी उपलब्ध.\\n\\n` +
          `> **💡 आपण या चॅटमध्ये सर्व काही करू शकता:**\\n` +
          `- थेट BigQuery/Snowflake टेबल्स आणि रो संख्या विचारा\\n` +
          `- नवीन टेबल बनवण्यासाठी SQL / DDL लिहा\\n` +
          `- Airflow DAGs ची स्थिती तपासा किंवा रिपोर्ट डाउनलोड लिंक मागा\\n` +
          `- कोणतीही पाइपलाइन किंवा आर्किटेक्चर डायग्राम (Mermaid) स्क्रीनवर तयार करून घ्या!`;
      }"""

if old_guard_default in cw:
    cw = cw.replace(old_guard_default, new_guard_default, 1)
    print("4. Successfully updated SOVEREIGN EDGE RESILIENCE GUARD with reports and greeting!")
else:
    print("Warning: old_guard_default exact block not matched")

# Replace any lingering 8 DAGs or 4,750 in cloudflare_worker_gateway.js
cw = cw.replace("Apache Airflow 8 DAGs", "Apache Airflow 15 DAGs")
cw = cw.replace("Apache Airflow (8 Production DAGs)", "Apache Airflow (15 Production DAGs)")
cw = cw.replace("Apache Airflow 8 Production DAGs", "Apache Airflow 15 Production DAGs")
cw = cw.replace("4,750+ मॉडेल्स", "4,804+ मॉडेल्स")
cw = cw.replace("4,750+ unified models", "4,804+ unified models")
cw = cw.replace("4,750+ Models", "4,804+ Models")
cw = cw.replace("4,750+ models", "4,804+ models")

with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
    f.write(cw)

print("[OK] deploy/cloudflare_worker_gateway.js updated successfully!")
