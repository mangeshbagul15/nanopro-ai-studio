import os

os.chdir(r"C:\Users\mange\OneDrive\Documents\GitHub\nanopro-ai-studio")

with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    cw = f.read()

target = """      } else {
        edgeKnowledge = `### ⚡ NanoPro Global AI Lab (Sovereign Edge Synthesis)\\n\\n` +
          `आपला प्रश्न स्वीकारला गेला आहे. **NanoPro Unified Model Mesh** खालील आर्किटेक्चरवर कार्यरत आहे:\\n\\n` +
          `- **डेटा पाइपलाइन**: Google BigQuery + DuckDB + SFTP ➔ AWS S3 ➔ Snowflake ➔ SFTP (.xlsx / .csv).\\n` +
          `- **ऑर्केस्ट्रेशन**: Apache Airflow 15 DAGs (EOD T-1, Hourly, SFTP Hub).\\n` +
          `- **एआय मॉडेल्स**: 4,804+ मॉडेल्स, Pareto Utility मॅट्रिक्स $U(m)$ आणि Thompson Bandit द्वारे स्वयंचलित राउटिंग.`;
      }"""

replacement = """      } else if (/(report|अहवाल|kiti report|total report|किती रिपोर्ट|reports)/i.test(pCheckEdge)) {
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

# Normalize CRLF
norm_cw = cw.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")
norm_replacement = replacement.replace("\r\n", "\n")

if norm_target in norm_cw:
    norm_cw = norm_cw.replace(norm_target, norm_replacement, 1)
    with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
        f.write(norm_cw)
    print("Successfully replaced edge fallback in deploy/cloudflare_worker_gateway.js!")
else:
    print("Error: norm_target not found in norm_cw")
