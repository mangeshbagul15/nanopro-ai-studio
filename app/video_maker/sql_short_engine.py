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
import re
import time
import json
import sqlite3
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.core.logger import log_event
from app.core.config import VIDEO_OUTPUT_DIR, BASE_DIR
from app.core.elevenlabs_voice import elevenlabs_voice
from app.core.upstash_cache import upstash_cache


TOP_MNC_SQL_PRESETS = [
    {
        "id": "sql_q1_second_highest_salary",
        "title": "Top MNC / FAANG: 2nd Highest Salary with Duplicate Check (Subquery Method)",
        "difficulty": "Core Interview Question",
        "category": "Subqueries & Aggregate Functions",
        "hook_mr": "🚨 Top IT कंपन्यांच्या SQL इंटरव्ह्यूमध्ये ९०% मुलं या प्रश्नात चूक करतात! एकापेक्षा जास्त लोकांचा पगार समान असताना २ रा सर्वाधिक पगार कसा शोधायचा?",
        "hook_hi": "🚨 Top IT कंपनियों के SQL इंटरव्यू में 90% लोग इस सवाल में गलती करते हैं! जब कई लोगों की सेम सैलरी हो तो 2nd हाईएस्ट सैलरी कैसे निकालें?",
        "hook_en": "🚨 90% of candidates make a mistake on this top SQL interview question: Finding the 2nd Highest Salary with Ties!",
        "hook_minglish": "🚨 Top MNC interview madhe 90% loka fasatat! Priya & Kiran doghanchi salary same 80k aslyavar 2nd highest salary kashi kadhaychi?",
        "hook_hinglish": "🚨 Top MNC interview me 90% log fas jate hai! Priya & Kiran dono ki salary same 80k hone par 2nd highest salary kaise nikale?",
        "question": "You have an EMPLOYEES table (EMP_ID, EMP_NAME, DEPARTMENT, SALARY) with records: Amit (60k), Rahul (50k), Priya (80k), Neha (70k), Kiran (80k). How would you find the second-highest salary?",
        "table_name": "EMPLOYEES",
        "schema_sql": """CREATE TABLE IF NOT EXISTS EMPLOYEES (
    EMP_ID INTEGER PRIMARY KEY,
    EMP_NAME TEXT,
    DEPARTMENT TEXT,
    SALARY REAL
);
INSERT OR REPLACE INTO EMPLOYEES VALUES 
(101, 'Amit', 'IT', 60000),
(102, 'Rahul', 'HR', 50000),
(103, 'Priya', 'IT', 80000),
(104, 'Neha', 'Finance', 70000),
(105, 'Kiran', 'IT', 80000);""",
        "solution_sql": """SELECT MAX(SALARY) AS SECOND_HIGHEST_SALARY
FROM EMPLOYEES
WHERE SALARY < (
    SELECT MAX(SALARY)
    FROM EMPLOYEES
);""",
        "arrow_target": "WHERE SALARY < (SELECT MAX(SALARY))",
        "explanation_mr": "इथे आतील सबक्वेरी आधी पूर्ण टेबलमधून कमाल पगार ८०,००० शोधून काढते. मग बाहेरील मुख्य क्वेरी ८०,००० पेक्षा कमी असलेल्या पगारांमधून (६० हजार, ५० हजार, ७० हजार) सर्वात मोठा पगार शोधते, जो येतो बरोबर ७०,०००! जर 'LIMIT 1 OFFSET 1' वापरले तर ८०,००० दोनदा आल्यामुळे उत्तर चुकेल, पण ही सबक्वेरी पद्धत १००% अचूक काम करते!",
        "explanation_hi": "यहाँ अंदर वाली सबक्वेरी पहले पूरे टेबल से मैक्सिमम सैलरी 80,000 निकालती है। फिर बाहर वाली मेन क्वेरी 80,000 से कम वाली सैलरीज में से सबसे बड़ी सैलरी चुनती है, जो आती है 70,000! अगर 'LIMIT 1 OFFSET 1' लगाते तो 80,000 दो बार होने से उत्तर गलत आता, लेकिन सबक्वेरी मेथड 100% सही उत्तर देता है!",
        "explanation_en": "The inner subquery first finds the maximum salary (80,000). The outer query then filters out all salaries equal to or greater than 80,000, and selects the MAX of the remaining salaries (60k, 50k, 70k), which is 70,000! 'LIMIT 1 OFFSET 1' fails on duplicate ties, whereas this subquery method is 100% reliable!",
        "explanation_minglish": "Inner query adhi MAX salary 80,000 kadhte. Mag outer query 80,000 peksha lahan aslelya salaries madhun MAX ghete, ji 70,000 ahe! Duplicates aslyamule LIMIT 1 OFFSET 1 fail hote, pan he subquery solution 100% correct ahe!",
        "explanation_hinglish": "Inner query pehle MAX salary 80,000 nikalegi. Fir outer query 80,000 se kam me se MAX legi, jo 70,000 hai! Duplicates me LIMIT 1 OFFSET 1 fail hota hai, but ye subquery solution 100% sahi hai!",
        "pro_tip": "💡 Interviewer Pro-Tip: 'LIMIT 1 OFFSET 1' breaks when the top salary has duplicates (Priya & Kiran both 80,000). The Subquery or DENSE_RANK() approach is mandatory in FAANG interviews!",
        "sample_rows": [
            {"account": "101 Amit", "date": "IT", "amt": "₹60,000", "balance": "60k (< 80k)"},
            {"account": "102 Rahul", "date": "HR", "amt": "₹50,000", "balance": "50k (< 80k)"},
            {"account": "103 Priya", "date": "IT", "amt": "₹80,000", "balance": "80k (Top Tie)"},
            {"account": "104 Neha", "date": "Finance", "amt": "₹70,000", "balance": "70k (🎯 2nd)"},
            {"account": "105 Kiran", "date": "IT", "amt": "₹80,000", "balance": "80k (Top Tie)"}
        ],
        "filter_evaluations": [
            {"name": "Amit", "salary": "60,000", "cond": "60000 < 80000", "res": "TRUE", "action": "KEEP", "status": "keep"},
            {"name": "Rahul", "salary": "50,000", "cond": "50000 < 80000", "res": "TRUE", "action": "KEEP", "status": "keep"},
            {"name": "Priya", "salary": "80,000", "cond": "80000 < 80000", "res": "FALSE", "action": "EXCLUDE", "status": "exclude"},
            {"name": "Neha", "salary": "70,000", "cond": "70000 < 80000", "res": "TRUE", "action": "KEEP", "status": "keep"},
            {"name": "Kiran", "salary": "80,000", "cond": "80000 < 80000", "res": "FALSE", "action": "EXCLUDE", "status": "exclude"}
        ],
        "output_value": "70000",
        "scenes": [
            {
                "id": 1, "start": 0.0, "end": 8.0,
                "speech_en": "Here's a popular SQL interview question. How do you find the second-highest salary from an Employees table? Let's understand the logic and build the query step by step.",
                "speech_mr": "एसक्यूएल इंटरव्ह्यूमधील सर्वात महत्त्वाचा प्रश्न: एम्प्लॉईज टेबलमधून दुसऱ्या क्रमांकाचा सर्वाधिक पगार कसा शोधायचा? चला लॉजिक समजून घेऊन स्टेप-बाय-स्टेप क्वेरी लिहूया!",
                "speech_hi": "एसक्यूएल इंटरव्यू का एक बेहद पॉपुलर सवाल: एम्प्लॉईज टेबल से सेकंड हाईएस्ट सैलरी कैसे निकालें? आइए लॉजिक समझकर स्टेप बाय स्टेप क्वेरी बनाते हैं!"
            },
            {
                "id": 2, "start": 8.0, "end": 20.0,
                "speech_en": "First, understand the requirement. We need the second-highest distinct salary, not the second employee. Notice that eighty thousand appears twice. We must count it only once.",
                "speech_mr": "पहिले प्रश्न नीट समजून घ्या. आपल्याला दुसरा डिस्टिंक्ट पगार हवा आहे, दुसरा कर्मचारी नाही. इथे ऐंशी हजार पगार दोनदा आला आहे. तो आपल्याला एकदाच मोजायचा आहे.",
                "speech_hi": "पहले सवाल को समझिए. हमें सेकंड हाईएस्ट डिस्टिंक्ट सैलरी चाहिए. ध्यान दीजिए कि अस्सी हजार दो बार आया है. हमें इसे केवल एक बार ही गिनना है."
            },
            {
                "id": 3, "start": 20.0, "end": 32.0,
                "speech_en": "Now, how should we solve it? First, find the maximum salary. Then exclude that salary. Finally, find the maximum from the remaining values. That's our second-highest salary.",
                "speech_mr": "आता हे कसे सोडवायचे? प्रथम सर्वात मोठा पगार शोधा. मग तो पगार वगळा. आणि उरलेल्या पगारांमधून सर्वात मोठा पगार निवडा. तोच आपला दुसरा सर्वाधिक पगार!",
                "speech_hi": "अब इसे कैसे सॉल्व करें? पहले मैक्सिमम सैलरी निकालिए. फिर उसे बाहर कीजिए. और बाकी बची वैल्यूज में से मैक्सिमम निकालिए. वही है हमारी सेकंड हाईएस्ट सैलरी!"
            },
            {
                "id": 4, "start": 32.0, "end": 44.0,
                "speech_en": "Let's write the inner query first. SELECT MAX salary FROM Employees. This returns eighty thousand, the highest salary in our table.",
                "speech_mr": "चला आधी आतील क्वेरी लिहूया: सिलेक्ट मॅक्स सॅलरी फ्रॉम एम्प्लॉईज. ही क्वेरी आपल्याला ऐंशी हजार, म्हणजेच सर्वात मोठा पगार देते.",
                "speech_hi": "आइए पहले इनर क्वेरी लिखते हैं: सिलेक्ट मैक्स सैलरी फ्रॉम एम्प्लॉईज. यह हमें अस्सी हजार यानी सबसे बड़ी सैलरी देती है."
            },
            {
                "id": 5, "start": 44.0, "end": 58.0,
                "speech_en": "Next, we exclude the highest salary using WHERE salary is less than the result of our inner query. This removes both eighty-thousand values, leaving seventy, sixty, and fifty thousand.",
                "speech_mr": "आता व्हेअर सॅलरी लहान सबक्वेरी ही अट लावून ऐंशी हजार वगळूया. यामुळे ऐंशी हजार असणाऱ्या दोन्ही नोंदी वगळल्या जाऊन सत्तर, साठ आणि पन्नास हजार उरतात.",
                "speech_hi": "अब व्हेअर सैलरी लेस दैन सबक्वेरी लगाकर अस्सी हजार को फिल्टर करते हैं. इससे दोनों अस्सी हजार वाले रिकॉर्ड्स हट जाते हैं और सत्तर, साठ और पचास हजार बचते हैं."
            },
            {
                "id": 6, "start": 58.0, "end": 72.0,
                "speech_en": "Now the outer MAX function checks the remaining salaries. The highest remaining value is seventy thousand. That's our answer! The key is using a subquery to exclude the original maximum.",
                "speech_mr": "आता बाहेरील मॅक्स फंक्शन उरलेल्या पगारांमधून सर्वात मोठा पगार शोधते. उरलेल्यांमध्ये सर्वात मोठी रक्कम आहे सत्तर हजार! सबक्वेरीमुळे हे उत्तर १०० टक्के अचूक येते!",
                "speech_hi": "अब आउटर मैक्स फंक्शन बचे हुए रिकॉर्ड्स को चेक करता है. सबसे बड़ी बची हुई वैल्यू है सत्तर हजार! यही हमारा सही जवाब है!"
            },
            {
                "id": 7, "start": 72.0, "end": 85.0,
                "speech_en": "Interview tip! Always clarify whether they want the second-highest distinct salary. If the highest salary appears multiple times, this query still returns the correct second-highest value. Follow Code with Mangesh for more SQL interview questions!",
                "speech_mr": "इंटरव्ह्यू टिप! जर सर्वाधिक पगार अनेक लोकांचा समान असेल तरीही ही सबक्वेरी अचूक काम करते. पुढील एसक्यूएल प्रश्नांसाठी फॉलो करा कोड विथ मंगेश!",
                "speech_hi": "इंटरव्यू टिप! अगर हाईएस्ट सैलरी डुप्लीकेट भी हो, तब भी यह सबक्वेरी मेथड हमेशा सही उत्तर देता है. ऐसे ही एसक्यूएल सवालों के लिए फॉलो कीजिए कोड विथ मंगेश!"
            }
        ]
    },
    {
        "id": "faang_dense_rank_ties",
        "title": "Amazon / Google: 2nd & Nth Highest Salary With Ties (DENSE_RANK vs RANK)",
        "difficulty": "Hard (FAANG Standard)",
        "category": "Window Functions & Deduplication",
        "hook_mr": "🚨 Google आणि Amazon इंटरव्ह्यूमध्ये ९५% मुलं या प्रश्नात फेल होतात! समान पगार असताना २ रा सर्वाधिक पगार कसा काढायचा?",
        "hook_hi": "🚨 Google और Amazon SQL इंटरव्यू का सबसे घातक सवाल! जब दो लोगों की सेम सैलरी हो तो 2nd हाईएस्ट सैलरी कैसे निकालें?",
        "hook_en": "🚨 95% of candidates fail this Google & Amazon SQL interview question: 2nd Highest Salary with Ties!",
        "hook_minglish": "🚨 Google & Amazon interview madhe 95% pora fail hotat! Duplicate salary aslyavar 2nd highest salary kashi kadhaychi?",
        "hook_hinglish": "🚨 Google & Amazon SQL interview me 95% log fail ho jate hai! Duplicate salary hone par 2nd highest salary kaise nikale?",
        "question": "Find the 2nd highest salary from the employees table. When multiple employees tie for the top salary, ensure the 2nd distinct highest salary is returned cleanly.",
        "table_name": "company_employees",
        "schema_sql": """CREATE TABLE IF NOT EXISTS company_employees (
    emp_id INTEGER PRIMARY KEY,
    emp_name TEXT,
    department TEXT,
    salary REAL
);
INSERT OR REPLACE INTO company_employees VALUES 
(1, 'Aarav Sharma', 'Investment Banking', 185000.0),
(2, 'Rohit Deshmukh', 'Investment Banking', 185000.0),
(3, 'Priya Kulkarni', 'Cloud Platforms', 160000.0),
(4, 'Sneha Patel', 'Security Ops', 140000.0),
(5, 'Amit Verma', 'Fintech Infrastructure', 120000.0);""",
        "solution_sql": """WITH RankedSalaries AS (
    SELECT 
        emp_name,
        department,
        salary,
        DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM company_employees
)
SELECT emp_name, department, salary
FROM RankedSalaries
WHERE rnk = 2;""",
        "arrow_target": "DENSE_RANK() OVER (ORDER BY salary DESC)",
        "explanation_mr": "इथे आरव आणि रोहित दोघांचा पगार समान ₹१,८५,००० असल्याने दोघांना १ ला रँक मिळतो. सामान्य RANK() वापरल्यास पुढचा नंबर ३ रा होतो, ज्यामुळे २ रा नंबर गायब होतो! पण DENSE_RANK() नंबर स्किप न करता प्रियाला अचूक २ रा नंबर देते!",
        "explanation_hi": "यहाँ आरव और रोहित दोनों की सैलरी ₹1,85,000 होने पर दोनों को 1st रैंक मिलती है। सामान्य RANK() 2nd रैंक स्किप करके 3rd कर देता है, लेकिन DENSE_RANK() बिना स्किप किए प्रिया को सटीक 2nd रैंक देता है!",
        "explanation_en": "When multiple employees tie for the highest salary, standard RANK() skips rank 2 and jumps to 3 (1, 1, 3). DENSE_RANK() never skips numbers (1, 1, 2), guaranteeing the exact 2nd highest salary!",
        "explanation_minglish": "Top 2 chi salary same asel tar RANK() rank 3 var jump karte. Pan DENSE_RANK() rank skip karat nahi ani accurate 2nd salary Priya la milte!",
        "explanation_hinglish": "Ties hone par normal RANK() 3 pe jump karega. But DENSE_RANK() rank skip nahi karta aur exact 2nd salary nikalta hai!",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: Never use 'LIMIT 1 OFFSET 1' when salaries can tie—DENSE_RANK() is the only standard-compliant solution!"
    },
    {
        "id": "goldman_running_balance",
        "title": "Goldman Sachs / HDFC: Cumulative Running Ledger Balance (SUM OVER PARTITION BY)",
        "difficulty": "Medium (Banking Standard)",
        "category": "Financial Ledgers & Window Aggregates",
        "hook_mr": "🚨 HDFC आणि Goldman Sachs बँकेच्या टेक्निकल राऊंडमधील नंबर १ प्रश्न: क्युम्युलेटिव्ह बॅलन्स कसा काढायचा?",
        "hook_hi": "🚨 Goldman Sachs और HDFC बैंक इंटरव्यू का पसंदीदा सवाल: Cumulative Running Balance कैसे कैलकुलेट करें?",
        "hook_en": "🚨 Goldman Sachs & HDFC favorite SQL test: Calculate running ledger balance per account!",
        "hook_minglish": "🚨 Goldman Sachs & HDFC interview cha No. 1 question: Cumulative balance kasa calculate karaycha?",
        "hook_hinglish": "🚨 Goldman Sachs & HDFC interview ka No. 1 question: Cumulative running balance kaise nikale?",
        "question": "Calculate the cumulative running balance for each customer account ordered by transaction date without using slow correlated subqueries.",
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
        "explanation_mr": "इथे 'PARTITION BY account_no' मुळे प्रत्येक बँक खात्याचा स्वतंत्र ग्रुप तयार होतो आणि 'SUM(amount) OVER' मुळे सुरुवातीपासून आजपर्यंतची चालू शिल्लक अचूक मोजली जाते!",
        "explanation_hi": "यहाँ 'PARTITION BY account_no' हर अकाउंट को अलग रखता है और 'SUM(amount) OVER' लगातार चालू बैलेंस को जोड़ता जाता है!",
        "explanation_en": "PARTITION BY account_no keeps each customer ledger strictly isolated while SUM() OVER accumulates sequentially in O(N) linear time!",
        "explanation_minglish": "PARTITION BY account_no mule pratyek account cha vegla ledger rahto ani running balance step-by-step calculate hoto!",
        "explanation_hinglish": "PARTITION BY se har account ka hisab alag rehta hai aur running balance step by step calculate hota hai!",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: Correlated subqueries run in O(N²) quadratic time and lock the database. Window functions process millions of rows in linear O(N) time!"
    },
    {
        "id": "uber_consecutive_active_days",
        "title": "Uber / Swiggy: Consecutive Active Days (Gaps & Islands Problem)",
        "difficulty": "Hard (Algorithm Design)",
        "category": "Gaps and Islands Analytics",
        "hook_mr": "🚨 Uber आणि Swiggy च्या सिस्टीम डिझाइन SQL मध्ये सलग ३ दिवस सक्रिय ड्रायव्हर्स कसे शोधायचे?",
        "hook_hi": "🚨 Uber और Swiggy डेटा एनालिस्ट इंटरव्यू: लगातार 3 दिन एक्टिव रहने वाले राइडर्स कैसे खोजें?",
        "hook_en": "🚨 Uber & Swiggy Data Analyst Interview: Solve the legendary Gaps and Islands problem!",
        "hook_minglish": "🚨 Uber ani Swiggy interview cha legendary Gaps & Islands problem kasa solve karaycha?",
        "hook_hinglish": "🚨 Uber aur Swiggy ka classic Gaps & Islands SQL problem: Consecutive 3 days active users!",
        "question": "Find all driver IDs who completed rides for at least 3 consecutive days using the Gaps and Islands date subtraction technique.",
        "table_name": "driver_trips",
        "schema_sql": """CREATE TABLE IF NOT EXISTS driver_trips (
    trip_id INTEGER PRIMARY KEY,
    driver_id TEXT,
    trip_date TEXT
);
INSERT OR REPLACE INTO driver_trips VALUES 
(1, 'DRV-101', '2026-10-01'),
(2, 'DRV-101', '2026-10-02'),
(3, 'DRV-101', '2026-10-03'),
(4, 'DRV-101', '2026-10-05'),
(5, 'DRV-202', '2026-10-01'),
(6, 'DRV-202', '2026-10-03');""",
        "solution_sql": """WITH GroupedTrips AS (
    SELECT 
        driver_id,
        trip_date,
        DATE(trip_date, '-' || ROW_NUMBER() OVER (
            PARTITION BY driver_id ORDER BY trip_date
        ) || ' days') AS island_group
    FROM driver_trips
)
SELECT 
    driver_id,
    MIN(trip_date) AS streak_start,
    MAX(trip_date) AS streak_end,
    COUNT(*) AS consecutive_days
FROM GroupedTrips
GROUP BY driver_id, island_group
HAVING COUNT(*) >= 3;""",
        "arrow_target": "ROW_NUMBER() OVER (PARTITION BY driver_id ORDER BY trip_date)",
        "explanation_mr": "जेव्हा तारखा सलग असतात, तेव्हा 'trip_date - ROW_NUMBER()' केल्यास एकच स्थिर तारीख (Island Group Key) मिळते! ग्रुप बाय आणि HAVING COUNT >= 3 लावल्यास सलग ३ दिवस काम केलेले ड्रायव्हर्स अचूक सापडतात!",
        "explanation_hi": "जब तारीखें लगातार होती हैं, तो trip_date में से ROW_NUMBER घटाने पर एक स्थिर ग्रुप मिलता है! HAVING COUNT >= 3 से लगातार स्ट्रीक वाले ड्राइवर्स मिल जाते हैं!",
        "explanation_en": "Subtracting ROW_NUMBER() from consecutive dates yields an identical anchor date (island key). Grouping by this key with HAVING COUNT >= 3 cleanly isolates streaks!",
        "explanation_minglish": "Trip_date madhun ROW_NUMBER minus kelyavar constant anchor date milte. HAVING COUNT >= 3 mule 3 consecutive days streak clear diste!",
        "explanation_hinglish": "Dates me se ROW_NUMBER minus karne par island key banti hai aur continuous active days filter ho jate hai!",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: The 'date minus row_number' trick is the most prized FAANG technique for solving streak and login retention queries!"
    },
    {
        "id": "netflix_top_n_per_category",
        "title": "Netflix / Spotify: Top 2 Most Streamed Titles Per Category (PARTITION BY DENSE_RANK)",
        "difficulty": "Medium (Media & Content Tech)",
        "category": "Category Grouping & Leaderboards",
        "hook_mr": "🚨 Netflix आणि Spotify च्या डेटा सायन्स मुलाखतीत प्रत्येक कॅटेगरीतील टॉप २ शो कसे शोधतात?",
        "hook_hi": "🚨 Netflix और Spotify SQL इंटरव्यू: हर कैटेगरी में से टॉप 2 सबसे ज्यादा देखे गए शोज कैसे निकालें?",
        "hook_en": "🚨 Netflix & Spotify Data Science Interview: Extract Top 2 most streamed titles per genre!",
        "hook_minglish": "🚨 Netflix & Spotify interview: pratyek genre madhun Top 2 most watched movies kase kadhayche?",
        "hook_hinglish": "🚨 Netflix & Spotify interview: har category se Top 2 highest stream titles kaise filter kare?",
        "question": "Find the top 2 most watched titles for each genre based on total watch hours using window partitioning.",
        "table_name": "content_streams",
        "schema_sql": """CREATE TABLE IF NOT EXISTS content_streams (
    content_id INTEGER PRIMARY KEY,
    title TEXT,
    genre TEXT,
    watch_hours INTEGER
);
INSERT OR REPLACE INTO content_streams VALUES 
(1, 'Stranger Things', 'Sci-Fi', 850000),
(2, 'Dark', 'Sci-Fi', 720000),
(3, 'Black Mirror', 'Sci-Fi', 610000),
(4, 'The Crown', 'Drama', 910000),
(5, 'Breaking Bad', 'Drama', 990000),
(6, 'Ozark', 'Drama', 540000);""",
        "solution_sql": """WITH RankedContent AS (
    SELECT 
        title,
        genre,
        watch_hours,
        DENSE_RANK() OVER (
            PARTITION BY genre 
            ORDER BY watch_hours DESC
        ) AS rank_in_genre
    FROM content_streams
)
SELECT title, genre, watch_hours, rank_in_genre
FROM RankedContent
WHERE rank_in_genre <= 2;""",
        "arrow_target": "PARTITION BY genre ORDER BY watch_hours DESC",
        "explanation_mr": "इथे 'PARTITION BY genre' मुळे प्रत्येक जॉनरचे (Sci-Fi, Drama) स्वतंत्र रँकिंग ब्लॉक तयार होते आणि 'WHERE rank_in_genre <= 2' मुळे प्रत्येक जॉनरचे टॉप २ शोज बाहेर येतात!",
        "explanation_hi": "यहाँ 'PARTITION BY genre' हर जॉनर का अलग पार्टीशन बनाता है और 'WHERE rank_in_genre <= 2' से हर कैटेगरी के टॉप 2 शोज फिल्टर हो जाते हैं!",
        "explanation_en": "PARTITION BY genre resets the ranking boundary for each genre independently, letting WHERE rank <= 2 extract top performers without grouping collapse!",
        "explanation_minglish": "PARTITION BY genre mule Sci-Fi ani Drama cha ranking vegla hoto ani top 2 titles extract hotat!",
        "explanation_hinglish": "PARTITION BY genre se category wise ranking reset hoti hai aur top 2 records easily mil jate hai!",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: Using PARTITION BY with DENSE_RANK() avoids expensive self-joins and scales to millions of catalogue items!"
    },
    {
        "id": "meta_reciprocal_friends",
        "title": "Meta / LinkedIn: Find Reciprocal Follows / Mutual Connections (Self-Join)",
        "difficulty": "Medium (Graph & Social Networks)",
        "category": "Self-Joins & Graph Relations",
        "hook_mr": "🚨 Meta (Facebook) आणि LinkedIn च्या SQL टेस्टमध्ये म्युचुअल फॉलोवर्स कसे शोधायचे?",
        "hook_hi": "🚨 Meta और LinkedIn इंटरव्यू: दो लोग जो एक-दूसरे को फॉलो करते हैं उन्हें SQL से कैसे निकालें?",
        "hook_en": "🚨 Meta & LinkedIn SQL Interview: Find all pairs of mutual / reciprocal connections!",
        "hook_minglish": "🚨 Meta & LinkedIn interview: mutual friends ani reciprocal follows kase find out karayche?",
        "hook_hinglish": "🚨 Meta & LinkedIn interview: mutual connections aur reciprocal follow pairs kaise nikale?",
        "question": "Find all distinct pairs of users who reciprocally follow each other (User A follows B AND User B follows A). Do not return duplicate reversed pairs (A, B) and (B, A).",
        "table_name": "user_follows",
        "schema_sql": """CREATE TABLE IF NOT EXISTS user_follows (
    user_id TEXT,
    following_id TEXT,
    follow_date TEXT,
    PRIMARY KEY (user_id, following_id)
);
INSERT OR REPLACE INTO user_follows VALUES 
('USR-1', 'USR-2', '2026-10-01'),
('USR-2', 'USR-1', '2026-10-02'),
('USR-1', 'USR-3', '2026-10-03'),
('USR-3', 'USR-4', '2026-10-04'),
('USR-4', 'USR-3', '2026-10-05');""",
        "solution_sql": """SELECT 
    f1.user_id AS user_a,
    f1.following_id AS user_b
FROM user_follows f1
JOIN user_follows f2 
  ON f1.user_id = f2.following_id 
 AND f1.following_id = f2.user_id
WHERE f1.user_id < f1.following_id;""",
        "arrow_target": "ON f1.user_id = f2.following_id AND f1.following_id = f2.user_id",
        "explanation_mr": "इथे आपण Self-Join वापरला आहे. पण '(USR-1, USR-2)' आणि '(USR-2, USR-1)' अशी डुप्लिकेट जोडी नको म्हणून 'WHERE f1.user_id < f1.following_id' लावून एकच अचूक जोडी ठेवली!",
        "explanation_hi": "यहाँ हमने Self-Join इस्तेमाल किया है। '(A, B)' और '(B, A)' जैसे डुप्लिकेट्स को रोकने के लिए 'WHERE user_id < following_id' की शर्त लगाई गई है!",
        "explanation_en": "Self-joining the table on reciprocal user IDs matches bidirectional friendships. Adding 'WHERE f1.user_id < f1.following_id' eliminates symmetric duplicate pairs!",
        "explanation_minglish": "Self-join kelyane reciprocal follows bhetle. Ani f1.user_id < f1.following_id mule reverse duplicates delete jhale!",
        "explanation_hinglish": "Self-join se mutual followers nikalte hai aur f1.user_id < f1.following_id se duplicate pairs filter ho jate hai!",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: Whenever comparing bidirectional graph edges, adding '<' on the keys prevents redundant mirrored output!"
    },
    {
        "id": "amazon_churn_zero_orders",
        "title": "Amazon / Flipkart: Customers Who Registered But Never Placed an Order (Anti-Join)",
        "difficulty": "Easy to Medium (E-Commerce Standard)",
        "category": "Anti-Joins & NULL Handling",
        "hook_mr": "🚨 Amazon SQL राउंड १: रजिस्ट्रेशन केले पण १ ही ऑर्डर न दिलेले ग्राहक कसे शोधायचे? 'NOT IN' का वापरू नये?",
        "hook_hi": "🚨 Amazon SQL Interview: वे कस्टमर्स जिन्होंने रजिस्टर किया पर कभी ऑर्डर नहीं दिया! NOT IN क्यों फेल होता है?",
        "hook_en": "🚨 Amazon & Flipkart SQL Test: Find registered customers with ZERO orders! Why NOT IN fails!",
        "hook_minglish": "🚨 Amazon SQL test: account banavla pan 0 orders keleli lok kashi shodhaychi? LEFT JOIN magic!",
        "hook_hinglish": "🚨 Amazon SQL test: sign up kiya par zero orders wale customers kaise filter kare?",
        "question": "Find all registered customers who have never placed an order. Demonstrate why LEFT JOIN with IS NULL is superior to NOT IN.",
        "table_name": "portal_customers",
        "schema_sql": """CREATE TABLE IF NOT EXISTS portal_customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT,
    signup_date TEXT
);
CREATE TABLE IF NOT EXISTS portal_orders (
    order_id INTEGER PRIMARY KEY,
    customer_id TEXT,
    order_date TEXT,
    total_amt REAL
);
INSERT OR REPLACE INTO portal_customers VALUES 
('CUST-1', 'Rajesh K', '2026-09-01'),
('CUST-2', 'Sunita M', '2026-09-05'),
('CUST-3', 'Vikram T', '2026-09-10');
INSERT OR REPLACE INTO portal_orders VALUES 
(501, 'CUST-1', '2026-09-12', 4500.0),
(502, 'CUST-3', '2026-09-15', 1200.0);""",
        "solution_sql": """SELECT 
    c.customer_id,
    c.customer_name,
    c.signup_date
FROM portal_customers c
LEFT JOIN portal_orders o 
  ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;""",
        "arrow_target": "WHERE o.order_id IS NULL",
        "explanation_mr": "इथे 'LEFT JOIN' मुळे सर्व ग्राहक येतात. ज्यांनी खरेदी केली नाही त्यांच्या ऑर्डर आयडी समोर 'NULL' येतो. 'WHERE o.order_id IS NULL' मुळे शून्य ऑर्डर असलेले ग्राहक अचूक वेगळे होतात!",
        "explanation_hi": "यहाँ 'LEFT JOIN' सभी कस्टमर्स को लाता है। जिन्होंने कोई ऑर्डर नहीं किया उनके सामने NULL होता है। 'WHERE order_id IS NULL' से वे तुरंत फिल्टर हो जाते हैं!",
        "explanation_en": "LEFT JOIN preserves all customers. For non-purchasers, order columns evaluate to NULL. 'WHERE o.order_id IS NULL' filters them safely without the 3-valued NULL trap of NOT IN!",
        "explanation_minglish": "LEFT JOIN mule sagli lok yetat ani purchase naslyane order_id NULL disto. WHERE o.order_id IS NULL zero order customers extract karte!",
        "explanation_hinglish": "LEFT JOIN se all customers load hote hai aur WHERE order_id IS NULL se non-buying customers accurately filter hote hai!",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: If a subquery contains even a single NULL, 'NOT IN' returns EMPTY SET! In production, always use LEFT JOIN with IS NULL or NOT EXISTS!"
    },
    {
        "id": "stripe_consecutive_fraud",
        "title": "Stripe / PayPal: Rapid Consecutive Suspicious Card Withdrawals (LAG / LEAD)",
        "difficulty": "Hard (Fintech Security)",
        "category": "Fraud Detection & Time-Series Analytics",
        "hook_mr": "🚨 Stripe आणि PayPal फ्रॉड डिटेक्शन SQL: ५ मिनिटांत एकाच कार्डवरून सलग मोठे विड्रॉव्हल कसे पकडायचे?",
        "hook_hi": "🚨 Stripe और PayPal फ्रॉड डिटेक्शन: 5 मिनट में लगातार 2 बड़े विड्रॉल कैसे डिटेक्ट करें?",
        "hook_en": "🚨 Stripe & PayPal Fraud Security: Detect rapid consecutive high-value withdrawals with LAG()!",
        "hook_minglish": "🚨 Stripe & PayPal fraud detection: 5 min madhe back-to-back mothe transactions kase track karayche?",
        "hook_hinglish": "🚨 Stripe & PayPal fraud detection: LAG function se rapid suspicious transactions kaise pakde?",
        "question": "Find all card accounts that made consecutive withdrawals of more than ₹10,000 back-to-back using the LAG() window function.",
        "table_name": "card_transactions",
        "schema_sql": """CREATE TABLE IF NOT EXISTS card_transactions (
    id INTEGER PRIMARY KEY,
    card_no TEXT,
    amount REAL,
    tx_time TEXT
);
INSERT OR REPLACE INTO card_transactions VALUES 
(1, 'CARD-1001', 15000.0, '10:00:00'),
(2, 'CARD-1001', 20000.0, '10:04:00'),
(3, 'CARD-1002', 2000.0, '11:00:00'),
(4, 'CARD-1002', 500.0, '11:15:00'),
(5, 'CARD-1003', 45000.0, '12:00:00'),
(6, 'CARD-1003', 50000.0, '12:03:00');""",
        "solution_sql": """WITH TxnWithLag AS (
    SELECT 
        card_no,
        amount,
        tx_time,
        LAG(amount, 1) OVER (
            PARTITION BY card_no 
            ORDER BY tx_time
        ) AS prev_amount
    FROM card_transactions
)
SELECT card_no, amount, prev_amount, tx_time
FROM TxnWithLag
WHERE amount >= 10000 AND prev_amount >= 10000;""",
        "arrow_target": "LAG(amount, 1) OVER (PARTITION BY card_no ORDER BY tx_time)",
        "explanation_mr": "इथे 'LAG()' फंक्शन आधीच्या विड्रॉव्हलची रक्कम लगेच पुढच्या ओळीत दाखवते. जर चालू रक्कम आणि आधीची रक्कम दोन्ही ₹१०,००० पेक्षा जास्त असतील तर फ्रॉड अलार्म लगेच ट्रिगर होतो!",
        "explanation_hi": "यहाँ 'LAG()' फंक्शन पिछली ट्रांजैक्शन की वैल्यू सामने लाता है। जब करंट और पिछला दोनों अमाउंट ₹10,000+ होते हैं तो फ्रॉड फ़्लैग हो जाता है!",
        "explanation_en": "LAG() accesses preceding rows without self-joins. Checking where both current amount and prev_amount exceed ₹10,000 detects velocity fraud in a single scan!",
        "explanation_minglish": "LAG() function adhicha transaction samor aante. Current ani previous amount 10k peksha jast asel tar fraud alert lagech disto!",
        "explanation_hinglish": "LAG() function pichhle record ko current row me fetch karta hai aur consecutive high value transactions flag ho jate hai!",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: LAG() and LEAD() avoid costly Cartesian self-joins and are the foundation of real-time fraud engines!"
    },
    {
        "id": "zomato_mom_growth",
        "title": "Swiggy / Zomato: Month-over-Month (MoM) Revenue Growth Percentage (LAG Window)",
        "difficulty": "Medium (Business Intelligence & Metrics)",
        "category": "Financial Metrics & KPI Reporting",
        "hook_mr": "🚨 Zomato आणि Swiggy बिझनेस रिपोर्टिंग: दर महिन्याची टक्केवारीतील वाढ (MoM Growth %) कशी काढायची?",
        "hook_hi": "🚨 Zomato और Swiggy डेटा एनालिटिक्स: Month-over-Month रेवेन्यू ग्रोथ % कैसे निकालें?",
        "hook_en": "🚨 Swiggy & Zomato Business Intelligence: Calculate Month-over-Month (MoM) Growth % with LAG()!",
        "hook_minglish": "🚨 Zomato & Swiggy BI interview: Month-over-Month growth percentage kashi calculate karaychi?",
        "hook_hinglish": "🚨 Zomato & Swiggy analytics: MoM revenue growth % ka standard SQL formula!",
        "question": "Calculate the Month-over-Month (MoM) revenue growth percentage across consecutive reporting months using the LAG() window function.",
        "table_name": "monthly_business_metrics",
        "schema_sql": """CREATE TABLE IF NOT EXISTS monthly_business_metrics (
    report_month TEXT PRIMARY KEY,
    total_revenue REAL
);
INSERT OR REPLACE INTO monthly_business_metrics VALUES 
('2026-07', 5000000.0),
('2026-08', 6200000.0),
('2026-09', 7500000.0),
('2026-10', 9000000.0);""",
        "solution_sql": """WITH MonthlyTotals AS (
    SELECT 
        report_month,
        total_revenue,
        LAG(total_revenue, 1) OVER (
            ORDER BY report_month
        ) AS prev_month_revenue
    FROM monthly_business_metrics
)
SELECT 
    report_month,
    total_revenue,
    prev_month_revenue,
    ROUND(
        ((total_revenue - prev_month_revenue) * 100.0) / prev_month_revenue, 
        2
    ) AS mom_growth_pct
FROM MonthlyTotals;""",
        "arrow_target": "LAG(total_revenue, 1) OVER (ORDER BY report_month)",
        "explanation_mr": "इथे 'LAG(total_revenue, 1)' मागील महिन्याचा महसूल बरोबर बाजूला आणतो, ज्यामुळे ((Current - Prev) * 100 / Prev) सूत्राने टक्केवारीतील नफा अचूक काढता येतो!",
        "explanation_hi": "यहाँ 'LAG(total_revenue, 1)' पिछले महीने का रेवेन्यू सामने लाता है, जिससे ((Current - Prev) * 100 / Prev) फ़ॉर्मूले से MoM Growth % निकल आता है!",
        "explanation_en": "LAG(total_revenue, 1) pulls previous month revenue onto the current row, allowing clean ((Current - Prev) * 100 / Prev) calculation without joining on date offsets!",
        "explanation_minglish": "LAG function pichlya mahinyacha revenue deto ani MoM growth percentage clean calculate hoto!",
        "explanation_hinglish": "LAG() se pichhle mahine ka revenue easily milta hai aur MoM percentage growth accurately compute hoti hai!",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: Rounding to 2 decimal places and handling NULL on the first month makes your SQL dashboard-ready for C-level executives!"
    }
]

BANKING_SQL_PRESETS = TOP_MNC_SQL_PRESETS

TOP_MNC_THEORY_PRESETS = [
    {
        "id": "theory_where_vs_having",
        "title": "FAANG / MNC SQL Theory: WHERE vs HAVING Clause",
        "content_type": "theory",
        "difficulty": "Core Interview Question",
        "category": "Query Execution Order & Grouping",
        "question": "What is the key difference between the WHERE and HAVING clauses in SQL, and when should each be used?",
        "concept_summary": "WHERE filters individual rows before grouping; HAVING filters aggregated groups after GROUP BY.",
        "hook_mr": "🚨 Top IT कंपन्यांच्या SQL इंटरव्ह्यूमध्ये ९५% मुलं या प्रश्नात अडकतात! WHERE आणि HAVING क्लॉजमध्ये नेमका फरक काय आहे?",
        "hook_hi": "🚨 Top IT कंपनियों के SQL इंटरव्यू में 95% लोग अटक जाते हैं! WHERE और HAVING क्लॉज में असली अंतर क्या है?",
        "hook_en": "🚨 95% of candidates stumble on this core SQL interview question: The exact difference between WHERE and HAVING!",
        "hook_minglish": "🚨 MNC interview madhe 95% loka fasatat! WHERE ani HAVING clause madhla exact difference kay ahe?",
        "hook_hinglish": "🚨 Top MNC interview me 95% log fas jate hai! WHERE aur HAVING clause ka exact difference kya hai?",
        "comparison_title": "WHERE vs HAVING COMPARISON MATRIX",
        "comparison_headers": ["FEATURE / ASPECT", "WHERE CLAUSE", "HAVING CLAUSE"],
        "comparison_rows": [
            {"feature": "Execution Stage", "col_a": "Pre-Filter (Before GROUP BY)", "col_b": "Post-Filter (After GROUP BY)"},
            {"feature": "Aggregate Functions", "col_a": "❌ CANNOT use (SUM, COUNT)", "col_b": "✅ CAN use (e.g. COUNT > 5)"},
            {"feature": "Target Scope", "col_a": "Individual table rows", "col_b": "Aggregated groups"},
            {"feature": "Index Optimization", "col_a": "Uses Table Indexes fast", "col_b": "Cannot use B-Tree indexes directly"}
        ],
        "syntax_a_title": "WHERE CLAUSE (ROW-LEVEL FILTER)",
        "syntax_a_code": "SELECT name, department, salary\nFROM employees\nWHERE salary > 50000;",
        "syntax_b_title": "HAVING CLAUSE (GROUP-LEVEL FILTER)",
        "syntax_b_code": "SELECT department, COUNT(*)\nFROM employees\nGROUP BY department\nHAVING COUNT(*) > 5;",
        "traps_title": "COMMON INTERVIEW TRAPS & MISTAKES",
        "traps": [
            "❌ Trap: Writing WHERE COUNT(*) > 2 fails with a syntax error (aggregates illegal in WHERE)!",
            "✅ Rule: Always filter non-aggregated rows with WHERE first to cut group memory by 90%!"
        ],
        "golden_rule": "Golden Rule: Filter individual rows with WHERE; filter aggregated groups with HAVING.",
        "pro_tip": "💡 Senior Interviewer Pro-Tip: In production, always push filters to WHERE before GROUP BY so the database hashes fewer rows in memory!",
        "scenes": [
            {
                "id": 1, "start": 0.0, "end": 8.0,
                "speech_en": "Here's one of the most frequently asked SQL theory interview questions. What is the real difference between WHERE and HAVING? Let's break it down simply.",
                "speech_mr": "एसक्यूएल थिअरी इंटरव्ह्यूमधील सर्वात लोकप्रिय प्रश्न: व्हेअर आणि हॅव्हिंग क्लॉजमध्ये नेमका काय फरक आहे? चला अगदी सोप्या भाषेत समजून घेऊया!",
                "speech_hi": "एसक्यूएल थ्योरी इंटरव्यू का सबसे पसंदीदा सवाल: WHERE और HAVING क्लॉज में असली अंतर क्या है? आइए इसे आसान भाषा में समझते हैं!"
            },
            {
                "id": 2, "start": 8.0, "end": 20.0,
                "speech_en": "Candidates often get confused because both clauses filter data. But the critical difference is WHEN and WHAT they filter. WHERE filters individual rows, while HAVING filters grouped results.",
                "speech_mr": "उमेदवार अनेकदा कन्फ्युज होतात कारण दोन्ही क्लॉज डेटा फिल्टर करतात. पण मुख्य फरक हा आहे की ते कधी आणि काय फिल्टर करतात. व्हेअर स्वतंत्र रो फिल्टर करते, तर हॅव्हिंग ग्रुप्सना फिल्टर करते.",
                "speech_hi": "कैंडिडेट्स अक्सर कन्फ्यूज हो जाते हैं क्योंकि दोनों डेटा फिल्टर करते हैं. लेकिन असली फर्क यह है कि WHERE टेबल की हर रो को फिल्टर करता है, जबकि HAVING ग्रुप्स को फिल्टर करता है."
            },
            {
                "id": 3, "start": 20.0, "end": 32.0,
                "speech_en": "Look at the database execution pipeline. First, WHERE filters out rows before grouping happens. Then GROUP BY groups the remaining rows. Finally, HAVING evaluates aggregate conditions on those groups.",
                "speech_mr": "डेटाबेस एक्झिक्युशन पाइपलाइन बघा. आधी व्हेअर क्लॉज ग्रुपिंग होण्यापूर्वीच नको असलेल्या ओळी वगळतो. मग ग्रुप बाय उरलेल्या ओळींचे ग्रुप करतो. आणि शेवटी हॅव्हिंग त्या ग्रुप्सवर अटी तपासतो.",
                "speech_hi": "डेटाबेस का एग्जीक्यूशन आर्डर देखिए. पहले WHERE ग्रुपिंग से पहले रो फिल्टर करता है. फिर GROUP BY ग्रुप बनाता है. और अंत में HAVING उन ग्रुप्स पर कंडीशन चेक करता है."
            },
            {
                "id": 4, "start": 32.0, "end": 44.0,
                "speech_en": "Here is the syntax difference. In WHERE, you write salary greater than fifty thousand. In HAVING, you must use aggregate functions like COUNT greater than five or SUM greater than one lakh.",
                "speech_mr": "सिंटॅक्समधील फरक बघा. व्हेअरमध्ये तुम्ही सॅलरी ५० हजारांपेक्षा मोठी अशी अट लिहिता. पण हॅव्हिंगमध्ये तुम्ही काऊंट ५ पेक्षा जास्त किंवा सम १ लाखांपेक्षा जास्त असे ॲग्रीगेट फंक्शन वापरता.",
                "speech_hi": "सिंटैक्स का अंतर देखिए. WHERE में आप सैलरी ५० हजार से ज्यादा लिखते हैं. लेकिन HAVING में आपको COUNT या SUM जैसे एग्रीगेट फंक्शन्स का इस्तेमाल करना होता है."
            },
            {
                "id": 5, "start": 44.0, "end": 58.0,
                "speech_en": "Remember this comparison matrix. WHERE executes before GROUP BY, cannot use aggregates, and uses indexes. HAVING executes after GROUP BY, allows aggregate functions, but cannot use table indexes.",
                "speech_mr": "हा कम्पॅरिझन मॅट्रिक्स लक्षात ठेवा. व्हेअर ग्रुप बायच्या आधी चालतो आणि ॲग्रीगेट्स वापरू शकत नाही. हॅव्हिंग ग्रुप बाय नंतर चालतो, ॲग्रीगेट्स वापरू शकतो पण इंडेक्स थेट वापरू शकत नाही.",
                "speech_hi": "यह कंपैरिजन मैट्रिक्स याद रखिए. WHERE ग्रुप बाय से पहले चलता है और एग्रीगेट्स इस्तेमाल नहीं कर सकता. HAVING ग्रुप बाय के बाद चलता है और एग्रीगेट फंक्शन्स को सपोर्ट करता है."
            },
            {
                "id": 6, "start": 58.0, "end": 72.0,
                "speech_en": "Avoid the fatal interview trap. Writing WHERE COUNT greater than two causes an immediate SQL syntax error! The golden rule is: filter rows with WHERE, and filter groups with HAVING.",
                "speech_mr": "इंटरव्ह्यूमधील सर्वात मोठी चूक टाळा: व्हेअर काऊंट दोनपेक्षा जास्त लिहिल्यास सिंटॅक्स एरर येतो! सुवर्ण नियम: स्वतंत्र ओळींसाठी व्हेअर, आणि ग्रुप्ससाठी नेहमी हॅव्हिंग!",
                "speech_hi": "इंटरव्यू की सबसे बड़ी गलती से बचिए: WHERE में COUNT लिखने पर एरर आ जाता है! गोल्डन नियम: रो के लिए WHERE, और ग्रुप्स के लिए हमेशा HAVING!"
            },
            {
                "id": 7, "start": 72.0, "end": 85.0,
                "speech_en": "Interviewer pro tip! Always filter as many rows as possible in WHERE before GROUP BY to save database memory. Follow Code with Mangesh for top SQL interview preparation!",
                "speech_mr": "इंटरव्ह्यूअर प्रो-टिप! मेमरी वाचवण्यासाठी ग्रुप बायच्या आधीच व्हेअरने जास्तीत जास्त डेटा फिल्टर करा. पुढील एसक्यूएल तयारीसाठी फॉलो करा कोड विथ मंगेश!",
                "speech_hi": "इंटरव्यूअर प्रो-टिप! डेटाबेस मेमोरी बचाने के लिए हमेशा GROUP BY से पहले WHERE में अधिक से अधिक रो फिल्टर करें. फॉलो कीजिए कोड विथ मंगेश!"
            }
        ]
    },
    {
        "id": "theory_acid_properties",
        "title": "DBMS & SQL Theory: ACID Properties in Databases",
        "content_type": "theory",
        "difficulty": "FAANG & Banking Core",
        "category": "Transactions & Concurrency Control",
        "question": "Explain ACID properties in database management systems with a real banking money transfer scenario.",
        "concept_summary": "Atomicity, Consistency, Isolation, and Durability guarantee valid database transactions even through crashes and errors.",
        "hook_mr": "🚨 बँकिंग आणि FAANG इंटरव्ह्यूमध्ये विचारला जाणारा प्रश्न: डेटाबेसमधील ACID प्रॉपर्टीज नक्की काय असतात?",
        "hook_hi": "🚨 बैंकिंग और FAANG इंटरव्यू का पसंदीदा सवाल: डेटाबेस में ACID प्रॉपर्टीज का क्या मतलब होता है?",
        "hook_en": "🚨 Top FAANG and Banking Interview Question: What do ACID properties actually mean in databases?",
        "hook_minglish": "🚨 Banking ani FAANG interview cha top question: Database madhle ACID properties kase explain karayche?",
        "hook_hinglish": "🚨 Banking aur FAANG interview ka core question: ACID properties ko real banking example se kaise samjhaye?",
        "comparison_title": "ACID PROPERTIES MATRIX (BANK TRANSFER)",
        "comparison_headers": ["ACID PROPERTY", "CORE MEANING", "BANKING SCENARIO"],
        "comparison_rows": [
            {"feature": "A - Atomicity", "col_a": "All or Nothing (No partial state)", "col_b": "Debit ₹10k and Credit ₹10k must both commit or rollback"},
            {"feature": "C - Consistency", "col_a": "Preserves integrity rules", "col_b": "Total bank money remains identical before and after"},
            {"feature": "I - Isolation", "col_a": "Concurrent txns don't interfere", "col_b": "Two simultaneous ATM withdrawals lock account row"},
            {"feature": "D - Durability", "col_a": "Committed data is permanent", "col_b": "Power failure immediately after commit preserves balance"}
        ],
        "syntax_a_title": "TRANSACTION COMMIT PATTERN",
        "syntax_a_code": "BEGIN TRANSACTION;\n  UPDATE accounts SET balance = balance - 5000 WHERE acc_no = 'A1';\n  UPDATE accounts SET balance = balance + 5000 WHERE acc_no = 'B2';\nCOMMIT;",
        "syntax_b_title": "ERROR ROLLBACK PATTERN",
        "syntax_b_code": "BEGIN TRANSACTION;\n  UPDATE accounts SET balance = balance - 5000 WHERE acc_no = 'A1';\n  -- IF NETWORK/SERVER FAILS:\n  ROLLBACK; -- Both balances safely restored!",
        "traps_title": "COMMON INTERVIEW TRAPS & CONCEPTS",
        "traps": [
            "❌ Trap: Confusing Consistency with Isolation! Consistency is business rules; Isolation is concurrency locking.",
            "✅ Rule: Wrap multi-table operations in explicit transactions to prevent catastrophic financial data corruption!"
        ],
        "golden_rule": "Golden Rule: Transactions must be Atomic, Consistent, Isolated, and Durable.",
        "pro_tip": "💡 Senior Architect Pro-Tip: Be ready to explain Isolation levels (Read Committed vs Repeatable Read vs Serializable)!",
        "scenes": [
            {
                "id": 1, "start": 0.0, "end": 8.0,
                "speech_en": "Here's a cornerstone question in software interviews: What are the ACID properties in database systems? Let's understand them with a banking transfer.",
                "speech_mr": "सॉफ्टवेअर मुलाखतींमधील अत्यंत महत्त्वाचा प्रश्न: डेटाबेस मॅनेजमेंटमधील ॲसिड म्हणजेच ACID प्रॉपर्टीज काय आहेत? चला एका बँक ट्रान्सफरने समजून घेऊ!",
                "speech_hi": "सॉफ्टवेयर इंटरव्यू का क्लासिक सवाल: डेटाबेस में ACID प्रॉपर्टीज क्या होती हैं? आइए इसे बैंक ट्रांसफर के उदाहरण से समझते हैं!"
            },
            {
                "id": 2, "start": 8.0, "end": 20.0,
                "speech_en": "ACID stands for Atomicity, Consistency, Isolation, and Durability. Together, they guarantee that your database never loses money or corrupts records during server crashes or concurrent users.",
                "speech_mr": "ॲसिड म्हणजे अटॉमिसिटी, कन्सिस्टन्सी, आयसोलेशन आणि ड्युरॅबिलिटी. जेव्हा सर्व्हर क्रॅश होतो किंवा एकाच वेळी अनेक युजर्स पैसे ट्रान्सफर करतात, तेव्हा डेटा सुरक्षित ठेवण्याची ही हमी देतात.",
                "speech_hi": "ACID का मतलब है एटॉमिकिटी, कंसिस्टेंसी, आइसोलेशन और ड्यूरेबिलिटी. ये चारों मिलकर यह सुनिश्चित करते हैं कि सर्वर क्रैश होने पर भी डेटा कभी खराब न हो."
            },
            {
                "id": 3, "start": 20.0, "end": 32.0,
                "speech_en": "First is Atomicity: all or nothing. If five thousand rupees are debited from Account A, and the server crashes before crediting Account B, the entire transaction automatically rolls back. Money is never lost.",
                "speech_mr": "पहिली आहे अटॉमिसिटी: एकतर पूर्ण काम किंवा काहीच नाही. खात्यातून ५ हजार कट झाले आणि सर्व्हर बंद पडला, तर ट्रान्झॅक्शन आपोआप रोलबॅक होते. पैसे सुरक्षित राहतात.",
                "speech_hi": "पहली है एटॉमिकिटी: सब कुछ या कुछ भी नहीं. अगर खाते से पैसे कट गए और दूसरे खाते में जाने से पहले सर्वर बंद हो गया, तो पूरा ट्रांजैक्शन अपने आप रोलबैक हो जाता है."
            },
            {
                "id": 4, "start": 32.0, "end": 44.0,
                "speech_en": "Next is Consistency: database rules and constraints are strictly maintained. Total money across the bank before and after the transfer remains identical. Balance cannot drop below minimum thresholds.",
                "speech_mr": "दुसरी आहे कन्सिस्टन्सी: डेटाबेसचे नियम तंतोतंत पाळले जातात. ट्रान्सफरच्या आधी आणि नंतर बँकेतील एकूण रक्कम सारखीच राहते. बॅलन्स कधीही चुकीचा होत नाही.",
                "speech_hi": "दूसरी है कंसिस्टेंसी: डेटाबेस के सभी रूल्स सुरक्षित रहते हैं. बैंक का कुल बैलेंस ट्रांसफर से पहले और बाद में एकदम एक समान रहता है."
            },
            {
                "id": 5, "start": 44.0, "end": 58.0,
                "speech_en": "Third is Isolation: concurrent transactions execute without interfering. If two family members withdraw from the same ATM card at the same second, row locking prevents double spending.",
                "speech_mr": "तिसरी आहे आयसोलेशन: एकाच वेळी होणारे दोन व्यवहार एकमेकांत अडथळा आणत नाहीत. दोन लोकांनी एकाच क्षणी पैसे काढण्याचा प्रयत्न केला तरी रो लॉकिंगमुळे अचूक हिशोब राहतो.",
                "speech_hi": "तीसरी है आइसोलेशन: एक ही समय में चलने वाले दो ट्रांजैक्शन आपस में टकराते नहीं हैं. रो लॉकिंग की वजह से डबल विड्रॉल की समस्या कभी नहीं होती."
            },
            {
                "id": 6, "start": 58.0, "end": 72.0,
                "speech_en": "Finally, Durability guarantees that once a transaction commits, the record is permanently saved to disk. Even if the data center loses power a millisecond later, the committed balance survives.",
                "speech_mr": "आणि शेवटी ड्युरॅबिलिटी: एकदा व्यवहार कमिट झाला की डेटा कायमस्वरूपी सेव्ह होतो. पॉवर गेली किंवा हार्डवेअर फेल झाले तरीही बॅलन्स सुरक्षित राहतो.",
                "speech_hi": "और अंत में ड्यूरेबिलिटी: एक बार कमिट होने के बाद डेटा स्थायी रूप से सुरक्षित हो जाता है. पावर कट होने पर भी आपका डेटा कभी डिलीट नहीं होता."
            },
            {
                "id": 7, "start": 72.0, "end": 85.0,
                "speech_en": "Interviewer pro tip! In senior rounds, explain isolation levels like Read Committed and Serializable. Follow Code with Mangesh for more top interview lessons!",
                "speech_mr": "इंटरव्ह्यूअर प्रो-टिप! सिनियर मुलाखतींमध्ये आयसोलेशन लेव्हल्स म्हणजेच रीड कमिटेड आणि सिरियलायझेबल नक्की समजावून सांगा. फॉलो करा कोड विथ मंगेश!",
                "speech_hi": "इंटरव्यूअर प्रो-टिप! सीनियर राउंड्स में रीड कमिटेड और सीरियलाइजेबल जैसे आइसोलेशन लेवल्स को एक्सप्लेन करें. फॉलो कीजिए कोड विथ मंगेश!"
            }
        ]
    },
    {
        "id": "theory_primary_vs_unique_key",
        "title": "SQL Schema Design: Primary Key vs Unique Key",
        "content_type": "theory",
        "difficulty": "Core Interview Question",
        "category": "Data Modeling & Constraints",
        "question": "What is the difference between a Primary Key and a Unique Key in SQL?",
        "concept_summary": "Primary Key uniquely identifies each row and never allows NULL; Unique Key enforces column uniqueness and allows NULL.",
        "hook_mr": "🚨 SQL डेटाबेस डिझाइन मुलाखतीचा मूलभूत प्रश्न: प्रायमरी की आणि युनिक की मध्ये नक्की काय फरक असतो?",
        "hook_hi": "🚨 SQL डेटाबेस डिजाइन इंटरव्यू का बेसिक सवाल: Primary Key और Unique Key में क्या फर्क होता है?",
        "hook_en": "🚨 Core SQL interview question: The fundamental difference between Primary Key and Unique Key!",
        "hook_minglish": "🚨 SQL interview madhe nehemi vicharnara question: Primary Key vs Unique Key madhla difference!",
        "hook_hinglish": "🚨 SQL interview ka standard question: Primary Key aur Unique Key me kya antar hai?",
        "comparison_title": "PRIMARY KEY vs UNIQUE KEY MATRIX",
        "comparison_headers": ["FEATURE / CRITERIA", "PRIMARY KEY", "UNIQUE KEY"],
        "comparison_rows": [
            {"feature": "NULL Value Allowance", "col_a": "❌ Strictly NOT NULL (0 NULLs allowed)", "col_b": "✅ Allows NULL (1 or more depending on engine)"},
            {"feature": "Count per Table", "col_a": "Only ONE Primary Key per table", "col_b": "Multiple Unique Keys allowed per table"},
            {"feature": "Default Index Created", "col_a": "Clustered Index (physical row ordering)", "col_b": "Non-Clustered Index (logical lookup pointer)"},
            {"feature": "Core Purpose", "col_a": "Entity row identity (e.g. user_id)", "col_b": "Business uniqueness (e.g. email, phone)"}
        ],
        "syntax_a_title": "PRIMARY KEY SYNTAX",
        "syntax_a_code": "CREATE TABLE employees (\n    emp_id INT PRIMARY KEY,\n    name VARCHAR(100) NOT NULL\n);",
        "syntax_b_title": "UNIQUE KEY SYNTAX",
        "syntax_b_code": "CREATE TABLE employees (\n    emp_id INT PRIMARY KEY,\n    email VARCHAR(255) UNIQUE\n);",
        "traps_title": "COMMON INTERVIEW TRAPS",
        "traps": [
            "❌ Trap: Thinking a table can have two primary keys! Use a composite primary key if multiple columns identify a row.",
            "✅ Rule: Use Primary Key for identity; use Unique Key on candidate keys like Email, Phone, Aadhaar, PAN!"
        ],
        "golden_rule": "Golden Rule: Primary Key identifies the row; Unique Key guarantees unique business attributes.",
        "pro_tip": "💡 Senior DBA Pro-Tip: In MySQL InnoDB, table data is physically sorted by Primary Key. Keep it small (e.g. BIGINT)!",
        "scenes": [
            {
                "id": 1, "start": 0.0, "end": 8.0,
                "speech_en": "Here's a fundamental SQL schema interview question: What is the real difference between a Primary Key and a Unique Key? Let's clarify it completely.",
                "speech_mr": "एसक्यूएल स्कीमा डिझाइनमधील मूलभूत प्रश्न: प्रायमरी की आणि युनिक की मध्ये नक्की काय फरक आहे? चला अगदी स्पष्ट समजून घेऊया!",
                "speech_hi": "एसक्यूएल स्कीमा डिजाइन का एक बुनियादी सवाल: Primary Key और Unique Key में क्या फर्क है? आइए इसे पूरी तरह साफ करते हैं!"
            },
            {
                "id": 2, "start": 8.0, "end": 20.0,
                "speech_en": "Both constraints enforce uniqueness, but there are four major differences that interviewers test: null handling, count per table, index type, and their intended purpose in system design.",
                "speech_mr": "दोन्ही कन्स्ट्रेंट्स डेटा युनिक ठेवतात, पण मुलाखतीत चार महत्त्वाचे फरक तपासले जातात: नल व्हॅल्यू, टेबलमधील संख्या, इंडेक्सचा प्रकार आणि त्यांचा खरा उद्देश.",
                "speech_hi": "दोनों ही डेटा को डुप्लीकेट होने से रोकते हैं, लेकिन चार बड़े अंतर होते हैं: NULL वैल्यू, टेबल में संख्या, इंडेक्स का टाइप और उनका असली मकसद."
            },
            {
                "id": 3, "start": 20.0, "end": 32.0,
                "speech_en": "Difference number one: NULL values! A Primary Key strictly forbids NULL values. Every single row must have an ID. In contrast, a Unique Key allows NULL values because an unknown value doesn't violate uniqueness.",
                "speech_mr": "पहिला फरक: नल व्हॅल्यू! प्रायमरी की मध्ये नल अजिबात चालत नाही. प्रत्येक ओळीला आयडी असणे अनिवार्य आहे. पण युनिक की मध्ये नल व्हॅल्यू चालू शकते.",
                "speech_hi": "पहिला अंतर: NULL वैल्यू! Primary Key में NULL कभी भी अलाउड नहीं होता. लेकिन Unique Key में आप NULL वैल्यू स्टोर कर सकते हैं."
            },
            {
                "id": 4, "start": 32.0, "end": 44.0,
                "speech_en": "Difference number two: Quantity per table. You can have only one Primary Key in a table. However, you can create multiple Unique Keys on columns like email, mobile number, and passport ID.",
                "speech_mr": "दुसरा फरक: एका टेबलमध्ये फक्त एकच प्रायमरी की असू शकते. पण युनिक की तुम्ही अनेक कॉलम्सवर लावू शकता, जसे की ईमेल, मोबाईल नंबर आणि पॅन कार्ड.",
                "speech_hi": "दूसरा अंतर: टेबल में एक ही Primary Key हो सकती है. जबकि Unique Key आप कई कॉलम्स जैसे ईमेल, मोबाइल और आधार पर बना सकते हैं."
            },
            {
                "id": 5, "start": 44.0, "end": 58.0,
                "speech_en": "Difference number three: Index creation! By default, a Primary Key creates a Clustered Index, sorting data physically on disk. A Unique Key creates a Non-Clustered Index, which acts as a fast lookup index.",
                "speech_mr": "तिसरा फरक: इंडेक्सचा प्रकार! प्रायमरी की आपोआप क्लस्टर्ड इंडेक्स बनवते, ज्यामुळे हार्ड डिस्कवर डेटा एका क्रमाने सेव्ह होतो. युनिक की नॉन-क्लस्टर्ड इंडेक्स तयार करते.",
                "speech_hi": "तीसरा अंतर: इंडेक्स! Primary Key अपने आप Clustered Index बनाती है जिससे डिस्क पर डेटा सॉर्ट होता है. Unique Key नॉन-क्लस्टर्ड इंडेक्स बनाती है."
            },
            {
                "id": 6, "start": 58.0, "end": 72.0,
                "speech_en": "Avoid the interview trap: never say a table can have two primary keys! If you need multiple columns to identify a row, that's called a Composite Primary Key. The golden rule: Primary Key identifies the row, Unique Key protects business data.",
                "speech_mr": "इंटरव्ह्यू ट्रॅप टाळा: कधीही म्हणू नका की टेबलला दोन प्रायमरी की असतात! एकापेक्षा जास्त कॉलम असल्यास त्याला कॉम्पोझिट प्रायमरी की म्हणतात. सुवर्ण नियम: रो ओळखण्यासाठी प्रायमरी की, युनिक डेटासाठी युनिक की!",
                "speech_hi": "इंटरव्यू ट्रैप से बचिए: कभी मत कहिए कि दो Primary Key हो सकती हैं! दो कॉलम मिलाने पर उसे Composite Key कहते हैं. गोल्डन नियम: रो की पहचान Primary Key है, डेटा की सुरक्षा Unique Key है."
            },
            {
                "id": 7, "start": 72.0, "end": 85.0,
                "speech_en": "Interviewer pro tip! In MySQL InnoDB, the Primary Key defines table clustering. Keep it integer and auto-incrementing for best performance! Follow Code with Mangesh!",
                "speech_mr": "इंटरव्ह्यूअर प्रो-टिप! मायएसक्यूएल मध्ये प्रायमरी की ने डेटा क्लस्टर होतो, म्हणून तो नेहमी इंटिजर ठेवावा. पुढील तयारीसाठी फॉलो करा कोड विथ मंगेश!",
                "speech_hi": "इंटरव्यूअर प्रो-टिप! MySQL InnoDB में Primary Key से डेटा क्लस्टर होता है, इसलिए इसे हमेशा ऑटो-इंक्रीमेंट इंटीजर रखें. फॉलो कीजिए कोड विथ मंगेश!"
            }
        ]
    }
]


class SqlShortVideoEngine:
    """
    Dedicated 9:16 Short Video Creation Engine.
    Produces viral 85-second Reels & Shorts with synchronized code, arrows, and multilingual voiceovers.
    Supports both SQL Coding / Query questions and SQL Theory / Concept questions.
    """

    def __init__(self):
        self.output_dir = VIDEO_OUTPUT_DIR / "sql_shorts"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_presets(self) -> List[Dict[str, Any]]:
        """Returns built-in high-yield banking & theory interview SQL scenarios."""
        return BANKING_SQL_PRESETS + TOP_MNC_THEORY_PRESETS

    def _detect_content_type(self, text: str) -> str:
        """Detects whether prompt is a SQL coding problem or a Theory/concept question."""
        lower = text.lower()
        theory_keywords = [
            "difference between", "diff between", "vs", "versus", "what is", "what are",
            "explain the difference", "theory", "acid", "normalization", "normal form",
            "primary key vs", "unique key", "truncate vs", "delete vs", "drop vs",
            "stored procedure vs", "view vs", "clustered", "non-clustered",
            "where vs having", "having vs where", "union vs union all",
            "inner join vs left join", "cross join vs", "null vs 0", "char vs varchar"
        ]
        query_keywords = [
            "select", "from", "table", "salary", "query", "find", "write", "calculate",
            "highest", "lowest", "dense_rank", "partition", "lead", "lag", "streak",
            "consecutive", "running balance", "cumulative", "employee", "employees",
            "order by", "group by", "create table", "insert into"
        ]

        # First check explicit theory keywords
        for kw in theory_keywords:
            if kw in lower:
                return "theory"

        # Check explicit query keywords
        for kw in query_keywords:
            if kw in lower:
                return "sql_query"

        # If has code fence or SQL keywords
        if "```sql" in lower or "```" in lower:
            return "sql_query"

        return "theory"

    def _ensure_seven_scenes(self, matched: Dict[str, Any], content_type: str, lang_key: str) -> List[Dict[str, Any]]:
        """Ensures all 7 scenes (0-85s) are populated for any Query or Theory scenario."""
        existing = matched.get("scenes") or []
        if len(existing) >= 7:
            return existing

        title = matched.get("title", "SQL Interview Question")
        question = matched.get("question", "")
        pro_tip = matched.get("pro_tip", "💡 Senior Interviewer Pro-Tip: Explain query logic step-by-step.")

        if content_type == "theory":
            concept = matched.get("concept_summary", "Understand the core structural differences between SQL operations.")
            golden = matched.get("golden_rule", "Filter individual records with WHERE, filter aggregated groups with HAVING.")
            return [
                {
                    "id": 1, "start": 0.0, "end": 8.0,
                    "speech_en": f"Here is a key SQL theory question: {title}. Let's break down the core concept step by step.",
                    "speech_mr": f"एसक्यूएल थिअरी इंटरव्ह्यूचा अत्यंत महत्त्वाचा प्रश्न: {title}! चला ही संकल्पना स्टेप बाय स्टेप समजून घेऊया.",
                    "speech_hi": f"एसक्यूएल थ्योरी इंटरव्यू का बहुत जरूरी सवाल: {title}! आइए इस कॉन्सेप्ट को आसान भाषा में स्टेप बाय स्टेप समझते हैं."
                },
                {
                    "id": 2, "start": 8.0, "end": 20.0,
                    "speech_en": f"Candidates often get confused on this topic. {concept}. Let's understand why this distinction is critical.",
                    "speech_mr": f"उमेदवार अनेकदा या विषयात गोंधळात पडतात. {concept}. ही संकल्पना स्पष्ट असणे का गरजेचे आहे ते पाहूया.",
                    "speech_hi": f"कैंडिडेट्स अक्सर इस टॉपिक पर अटक जाते हैं. {concept}. आइए समझते हैं कि यह अंतर इतना महत्वपूर्ण क्यों है."
                },
                {
                    "id": 3, "start": 20.0, "end": 32.0,
                    "speech_en": "Look at the internal database execution pipeline. The engine processes operations in a strict order of precedence.",
                    "speech_mr": "डेटाबेसची अंतर्गत एक्झिक्युशन पाइपलाइन समजून घ्या. एसक्यूएल इंजिन एका विशिष्ट क्रमाने सर्व ऑपरेशन्स प्रोसेस करते.",
                    "speech_hi": "डेटाबेस का इंटरनल एग्जीक्यूशन पाइपलाइन देखिए. इंजन हमेशा एक तय क्रम में ही सभी ऑपरेशन्स को प्रोसेस करता है."
                },
                {
                    "id": 4, "start": 32.0, "end": 44.0,
                    "speech_en": "Here is the code syntax side-by-side. Notice how each clause is structured and where it is placed in the query.",
                    "speech_mr": "इथे दोन्ही पद्धतींचा कोड सिंटॅक्स शेजारी-शेजारी बघा. क्लॉजची रचना आणि क्वेरीमधील जागा यातील फरक लगेच लक्षात येईल.",
                    "speech_hi": "यहाँ दोनों का कोड सिंटैक्स साथ-साथ देखिए. क्लॉज की बनावट और क्वेरी में उसकी पोजीशन का अंतर साफ नजर आता है."
                },
                {
                    "id": 5, "start": 44.0, "end": 58.0,
                    "speech_en": "Memorize this comprehensive comparison matrix: execution stage, aggregate function support, and index optimization.",
                    "speech_mr": "हा संपूर्ण तुलना मॅट्रिक्स लक्षात ठेवा: एक्झिक्युशन टप्पा, ॲग्रीगेट फंक्शन सपोर्ट, आणि इंडेक्स ऑप्टिमायझेशनमधील मुख्य फरक.",
                    "speech_hi": "यह पूरा कंपैरिजन मैट्रिक्स याद रखिए: एग्जीक्यूशन स्टेज, एग्रीगेट फंक्शन्स का इस्तेमाल, और इंडेक्स ऑप्टिमाइजेशन."
                },
                {
                    "id": 6, "start": 58.0, "end": 72.0,
                    "speech_en": f"Watch out for fatal interview traps! Always remember this universal golden rule: {golden}.",
                    "speech_mr": f"इंटरव्ह्यूमधील सर्वात घातक चुका टाळा! नेहमी लक्षात ठेवा हा सुवर्ण नियम: {golden}!",
                    "speech_hi": f"इंटरव्यू की सबसे कॉमन गलतियों से बचें! हमेशा याद रखें यह गोल्डन रूल: {golden}!"
                },
                {
                    "id": 7, "start": 72.0, "end": 85.0,
                    "speech_en": f"{pro_tip} Follow Code with Mangesh for more top MNC interview preparation videos!",
                    "speech_mr": f"{pro_tip} अशाच टॉप मल्टिनॅशनल कंपनी इंटरव्ह्यू तयारीसाठी फॉलो करा कोड विथ मंगेश!",
                    "speech_hi": f"{pro_tip} ऐसे ही टॉप कंपनी इंटरव्यू की पक्की तैयारी के लिए फॉलो कीजिए कोड विथ मंगेश!"
                }
            ]
        else:
            tbl = matched.get("table_name", "EMPLOYEES")
            return [
                {
                    "id": 1, "start": 0.0, "end": 8.0,
                    "speech_en": f"Here is a top SQL interview coding question: {title}. Let's understand the logic and build the query step by step.",
                    "speech_mr": f"एसक्यूएल इंटरव्ह्यूचा अत्यंत महत्त्वाचा कोडिंग प्रश्न: {title}! चला लॉजिक समजून घेऊन स्टेप बाय स्टेप क्वेरी लिहूया.",
                    "speech_hi": f"एसक्यूएल इंटरव्यू का बहुत ही पॉपुलर कोडिंग सवाल: {title}! आइए लॉजिक समझकर स्टेप बाय स्टेप क्वेरी बनाते हैं."
                },
                {
                    "id": 2, "start": 8.0, "end": 20.0,
                    "speech_en": f"First inspect the table schema and data in {tbl}. Pay close attention to duplicate values, edge cases, and ties.",
                    "speech_mr": f"प्रथम {tbl} टेबलचा डेटा आणि स्ट्रक्चर नीट तपासा. डुप्लिकेट व्हॅल्यूज आणि समान नोंदींवर विशेष लक्ष द्या.",
                    "speech_hi": f"पहले {tbl} टेबल का डेटा और स्कीमा ध्यान से देखिए. डुप्लिकेट वैल्यूज और टाई रिकॉर्ड्स पर खास ध्यान देना जरूरी है."
                },
                {
                    "id": 3, "start": 20.0, "end": 32.0,
                    "speech_en": "Now let's choose our strategy. We will break the problem down logically into atomic operations before writing the full query.",
                    "speech_mr": "आता योग्य रणनीती ठरवूया. संपूर्ण क्वेरी एकदम न लिहिता समस्येचे लहान-लहान लॉजिकल भागात विभाजन करूया.",
                    "speech_hi": "अब सही स्ट्रैटेजी चुनते हैं. पूरी क्वेरी एक साथ लिखने के बजाय सवाल को छोटे लॉजिकल स्टेप्स में बांटते हैं."
                },
                {
                    "id": 4, "start": 32.0, "end": 44.0,
                    "speech_en": "Let's construct the core subquery or partition clause. This isolates our primary filter condition cleanly.",
                    "speech_mr": "चला आधी मुख्य सबक्वेरी किंवा पार्टीशन क्लॉज तयार करूया. यामुळे आपली प्राथमिक फिल्टर अट अचूकपणे वेगळी होते.",
                    "speech_hi": "आइए पहले कोर सबक्वेरी या पार्टीशन क्लॉज लिखते हैं. इससे हमारी मेन फिल्टर कंडीशन बिल्कुल अलग हो जाती है."
                },
                {
                    "id": 5, "start": 44.0, "end": 58.0,
                    "speech_en": "Next we apply our outer condition and simulate the row-by-row filtering. Rows matching our criteria are kept, and the rest excluded.",
                    "speech_mr": "आता बाहेरील अट लावून प्रत्येक ओळीचे फिल्टरिंग तपासूया. अटी पूर्ण करणाऱ्या नोंदी राहतात आणि बाकीच्या वगळल्या जातात.",
                    "speech_hi": "अब बाहरी कंडीशन लगाकर हर रो का फिल्टरिंग चेक करते हैं. जो रिकॉर्ड्स मैच होते हैं वो बचते हैं बाकी सब बाहर हो जाते हैं."
                },
                {
                    "id": 6, "start": 58.0, "end": 72.0,
                    "speech_en": "Now the database executes the complete query and calculates the final output cleanly. Here is the verified result!",
                    "speech_mr": "आता डेटाबेस संपूर्ण क्वेरी एक्झिक्युट करतो आणि अचूक अंतिम उत्तर स्क्रीनवर दाखवतो. हे पहा अंतिम निकाल!",
                    "speech_hi": "अब डेटाबेस पूरी क्वेरी को रन करता है और सही आउटपुट स्क्रीन पर निकालता है. यह रहा फाइनल रिजल्ट!"
                },
                {
                    "id": 7, "start": 72.0, "end": 85.0,
                    "speech_en": f"{pro_tip} Follow Code with Mangesh for more top MNC interview preparation videos!",
                    "speech_mr": f"{pro_tip} अशाच टॉप मल्टिनॅशनल कंपनी इंटरव्ह्यू तयारीसाठी फॉलो करा कोड विथ मंगेश!",
                    "speech_hi": f"{pro_tip} ऐसे ही टॉप कंपनी इंटरव्यू की पक्की तैयारी के लिए फॉलो कीजिए कोड विथ मंगेश!"
                }
            ]


    def _parse_master_prompt_text(self, text: str, lang_key: str = "mr") -> Optional[Dict[str, Any]]:
        """
        Parses structured Markdown Master Prompt text if pasted directly by user.
        Extracts title, question, tables, code, and scenes.
        """
        if not ("## SCENE" in text or "SCENE 1" in text or "MASTER PROMPT" in text or "**Question:**" in text):
            return None

        title_m = re.search(r"(?:#+\s*Video Title:?\s*|\*\*Video Title:\*\*\s*)([^\n\r]+)", text, re.IGNORECASE)
        title = title_m.group(1).strip() if title_m else "SQL Interview Question"

        q_m = re.search(r"(?:\*\*Question:\*\*\s*|##+\s*Question\s*\n+)(.*?)(?=\n+\*\*Sample Data|\n+##|\n+\*\*Expected|\Z)", text, re.IGNORECASE | re.DOTALL)
        question = q_m.group(1).strip() if q_m else text.split("\n")[0]

        sql_m = re.search(r"```sql\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        solution_sql = sql_m.group(1).strip() if sql_m else ""

        output_m = re.search(r"(?:Expected Output:|\*\*Expected Output:\*\*|Output:)\s*(?:```(?:text)?\s*)?([^\n`]+)", text, re.IGNORECASE)
        output_val = "70000"
        if output_m:
            raw_out = output_m.group(1).strip()
            num_m = re.search(r"(\d+[\d,.]*)", raw_out)
            if num_m:
                output_val = num_m.group(1)
            else:
                output_val = raw_out

        # Extract scenes
        scenes = []
        scene_blocks = re.findall(r"##\s*SCENE\s*(\d+)[^\n]*\n+([\s\S]*?)(?=##\s*SCENE|\Z)", text, re.IGNORECASE)
        for s_num, s_body in scene_blocks:
            idx = int(s_num)
            voice_m = re.search(r"AI Teacher Voice[^\n]*\n+[\"“]([\s\S]*?)[\"”]", s_body, re.IGNORECASE)
            speech = voice_m.group(1).strip() if voice_m else ""
            
            # Duration mapping based on scene index (0-8, 8-20, 20-32, 32-44, 44-58, 58-72, 72-85)
            timing_map = {
                1: (0.0, 8.0),
                2: (8.0, 20.0),
                3: (20.0, 32.0),
                4: (32.0, 44.0),
                5: (44.0, 58.0),
                6: (58.0, 72.0),
                7: (72.0, 85.0)
            }
            start_t, end_t = timing_map.get(idx, ((idx - 1) * 12.0, idx * 12.0))
            scenes.append({
                "id": idx,
                "start": start_t,
                "end": end_t,
                "speech_en": speech,
                "speech_mr": speech,
                "speech_hi": speech
            })

        # If it matches Q1 second highest salary, fill in native Marathi and Hindi translations
        if "second-highest salary" in text.lower() or "second highest" in text.lower():
            preset_q1 = BANKING_SQL_PRESETS[0]
            if not solution_sql:
                solution_sql = preset_q1["solution_sql"]
            return {
                "id": "sql_q1_second_highest_salary",
                "content_type": "sql_query",
                "title": title or preset_q1["title"],
                "difficulty": "FAANG / MNC Standard",
                "question": question or preset_q1["question"],
                "table_name": "EMPLOYEES",
                "col_headers": ["EMP_ID", "EMP_NAME", "DEPARTMENT", "SALARY"],
                "sample_rows": [
                    {"account": "101 Amit", "date": "IT", "amt": "₹60,000", "balance": "60k (< 80k)"},
                    {"account": "102 Rahul", "date": "HR", "amt": "₹50,000", "balance": "50k (< 80k)"},
                    {"account": "103 Priya", "date": "IT", "amt": "₹80,000", "balance": "80k (Top Tie)"},
                    {"account": "104 Neha", "date": "Finance", "amt": "₹70,000", "balance": "70k (🎯 2nd)"},
                    {"account": "105 Kiran", "date": "IT", "amt": "₹80,000", "balance": "80k (Top Tie)"}
                ],
                "filter_evaluations": [
                    {"name": "Amit", "salary": "60,000", "cond": "60000 < 80000", "res": "TRUE", "action": "KEEP", "status": "keep"},
                    {"name": "Rahul", "salary": "50,000", "cond": "50000 < 80000", "res": "TRUE", "action": "KEEP", "status": "keep"},
                    {"name": "Priya", "salary": "80,000", "cond": "80000 < 80000", "res": "FALSE", "action": "EXCLUDE", "status": "exclude"},
                    {"name": "Neha", "salary": "70,000", "cond": "70000 < 80000", "res": "TRUE", "action": "KEEP", "status": "keep"},
                    {"name": "Kiran", "salary": "80,000", "cond": "80000 < 80000", "res": "FALSE", "action": "EXCLUDE", "status": "exclude"}
                ],
                "schema_sql": preset_q1["schema_sql"],
                "solution_sql": solution_sql or preset_q1["solution_sql"],
                "inner_query_sql": "SELECT MAX(SALARY) FROM EMPLOYEES;",
                "arrow_target": "WHERE SALARY < (SELECT MAX(SALARY))",
                "explanation_mr": preset_q1["explanation_mr"],
                "explanation_hi": preset_q1["explanation_hi"],
                "explanation_en": preset_q1["explanation_en"],
                "pro_tip": preset_q1["pro_tip"],
                "output_value": "70000",
                "scenes": [
                    {
                        "id": 1, "start": 0.0, "end": 8.0,
                        "speech_en": "Here's a popular SQL interview question. How do you find the second-highest salary from an Employees table? Let's understand the logic and build the query step by step.",
                        "speech_mr": "एसक्यूएल इंटरव्ह्यूमधील सर्वात महत्त्वाचा प्रश्न: एम्प्लॉईज टेबलमधून दुसऱ्या क्रमांकाचा सर्वाधिक पगार कसा शोधायचा? चला लॉजिक समजून घेऊन स्टेप-बाय-स्टेप क्वेरी लिहूया!",
                        "speech_hi": "एसक्यूएल इंटरव्यू का एक बेहद पॉपुलर सवाल: एम्प्लॉईज टेबल से सेकंड हाईएस्ट सैलरी कैसे निकालें? आइए लॉजिक समझकर स्टेप बाय स्टेप क्वेरी बनाते हैं!"
                    },
                    {
                        "id": 2, "start": 8.0, "end": 20.0,
                        "speech_en": "First, understand the requirement. We need the second-highest distinct salary, not the second employee. Notice that eighty thousand appears twice. We must count it only once.",
                        "speech_mr": "पहिले प्रश्न नीट समजून घ्या. आपल्याला दुसरा डिस्टिंक्ट पगार हवा आहे, दुसरा कर्मचारी नाही. इथे ऐंशी हजार पगार दोनदा आला आहे. तो आपल्याला एकदाच मोजायचा आहे.",
                        "speech_hi": "पहले सवाल को समझिए. हमें सेकंड हाईएस्ट डिस्टिंक्ट सैलरी चाहिए. ध्यान दीजिए कि अस्सी हजार दो बार आया है. हमें इसे केवल एक बार ही गिनना है."
                    },
                    {
                        "id": 3, "start": 20.0, "end": 32.0,
                        "speech_en": "Now, how should we solve it? First, find the maximum salary. Then exclude that salary. Finally, find the maximum from the remaining values. That's our second-highest salary.",
                        "speech_mr": "आता हे कसे सोडवायचे? प्रथम सर्वात मोठा पगार शोधा. मग तो पगार वगळा. आणि उरलेल्या पगारांमधून सर्वात मोठा पगार निवडा. तोच आपला दुसरा सर्वाधिक पगार!",
                        "speech_hi": "अब इसे कैसे सॉल्व करें? पहले मैक्सिमम सैलरी निकालिए. फिर उसे बाहर कीजिए. और बाकी बची वैल्यूज में से मैक्सिमम निकालिए. वही है हमारी सेकंड हाईएस्ट सैलरी!"
                    },
                    {
                        "id": 4, "start": 32.0, "end": 44.0,
                        "speech_en": "Let's write the inner query first. SELECT MAX salary FROM Employees. This returns eighty thousand, the highest salary in our table.",
                        "speech_mr": "चला आधी आतील क्वेरी लिहूया: सिलेक्ट मॅक्स सॅलरी फ्रॉम एम्प्लॉईज. ही क्वेरी आपल्याला ऐंशी हजार, म्हणजेच सर्वात मोठा पगार देते.",
                        "speech_hi": "आइए पहले इनर क्वेरी लिखते हैं: सिलेक्ट मैक्स सैलरी फ्रॉम एम्प्लॉईज. यह हमें अस्सी हजार यानी सबसे बड़ी सैलरी देती है."
                    },
                    {
                        "id": 5, "start": 44.0, "end": 58.0,
                        "speech_en": "Next, we exclude the highest salary using WHERE salary is less than the result of our inner query. This removes both eighty-thousand values, leaving seventy, sixty, and fifty thousand.",
                        "speech_mr": "आता व्हेअर सॅलरी लहान सबक्वेरी ही अट लावून ऐंशी हजार वगळूया. यामुळे ऐंशी हजार असणाऱ्या दोन्ही नोंदी वगळल्या जाऊन सत्तर, साठ आणि पन्नास हजार उरतात.",
                        "speech_hi": "अब व्हेअर सैलरी लेस दैन सबक्वेरी लगाकर अस्सी हजार को फिल्टर करते हैं. इससे दोनों अस्सी हजार वाले रिकॉर्ड्स हट जाते हैं और सत्तर, साठ और पचास हजार बचते हैं."
                    },
                    {
                        "id": 6, "start": 58.0, "end": 72.0,
                        "speech_en": "Now the outer MAX function checks the remaining salaries. The highest remaining value is seventy thousand. That's our answer! The key is using a subquery to exclude the original maximum.",
                        "speech_mr": "आता बाहेरील मॅक्स फंक्शन उरलेल्या पगारांमधून सर्वात मोठा पगार शोधते. उरलेल्यांमध्ये सर्वात मोठी रक्कम आहे सत्तर हजार! सबक्वेरीमुळे हे उत्तर १०० टक्के अचूक येते!",
                        "speech_hi": "अब आउटर मैक्स फंक्शन बचे हुए रिकॉर्ड्स को चेक करता है. सबसे बड़ी बची हुई वैल्यू है सत्तर हजार! यही हमारा सही जवाब है!"
                    },
                    {
                        "id": 7, "start": 72.0, "end": 85.0,
                        "speech_en": "Interview tip! Always clarify whether they want the second-highest distinct salary. If the highest salary appears multiple times, this query still returns the correct second-highest value. Follow Code with Mangesh for more SQL interview questions!",
                        "speech_mr": "इंटरव्ह्यू टिप! जर सर्वाधिक पगार अनेक लोकांचा समान असेल तरीही ही सबक्वेरी अचूक काम करते. पुढील एसक्यूएल प्रश्नांसाठी फॉलो करा कोड विथ मंगेश!",
                        "speech_hi": "इंटरव्यू टिप! अगर हाईएस्ट सैलरी डुप्लीकेट भी हो, तब भी यह सबक्वेरी मेथड हमेशा सही उत्तर देता है. ऐसे ही एसक्यूएल सवालों के लिए फॉलो कीजिए कोड विथ मंगेश!"
                    }
                ]
            }

        return {
            "id": "custom_master_prompt",
            "content_type": "sql_query" if solution_sql else "theory",
            "title": title,
            "difficulty": "Interview Standard",
            "question": question,
            "table_name": "interview_data",
            "col_headers": ["COL_1", "COL_2", "COL_3", "TARGET"],
            "sample_rows": [
                {"account": "101", "date": "Row 1", "amt": "Value A", "balance": "Status 1"},
                {"account": "102", "date": "Row 2", "amt": "Value B", "balance": "Status 2"}
            ],
            "schema_sql": "",
            "solution_sql": solution_sql or "-- Built step-by-step from prompt",
            "inner_query_sql": "",
            "arrow_target": "OVER ()",
            "explanation_mr": "प्रॉम्प्टनुसार क्वेरी लॉजिक तयार केले आहे.",
            "explanation_hi": "प्रॉम्प्ट के अनुसार क्वेरी लॉजिक तैयार किया गया है.",
            "explanation_en": "Query logic constructed as instructed in prompt.",
            "pro_tip": "💡 Interview Pro-Tip: Explain query execution plan step-by-step.",
            "output_value": output_val,
            "scenes": scenes if scenes else []
        }

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
            cursor.executescript(schema_sql)
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

    async def generate_short_prompt_async(
        self,
        topic_or_question: str,
        difficulty: str = "Medium",
        language: str = "mr"
    ) -> Dict[str, Any]:
        """
        Asynchronously generates an 85-second video creation blueprint:
        - Detects content type: SQL Query or Theory
        - Extracts / generates 7-scene educational storyboard
        - Synthesizes synchronized regional voice audio (Marathi / Hindi / English)
        """
        clean_lang = (language or "mr").lower()
        if clean_lang in ["minglish", "mr_en", "mr"]:
            lang_key = "mr"
        elif clean_lang in ["hinglish", "hi_en", "hi"]:
            lang_key = "hi"
        else:
            lang_key = "en"

        text_input = (topic_or_question or "").strip()
        matched = None

        # 1. Try parsing full Markdown Master Prompt first
        if "## SCENE" in text_input or "MASTER PROMPT" in text_input or "**Question:**" in text_input:
            parsed_master = self._parse_master_prompt_text(text_input, lang_key=lang_key)
            if parsed_master:
                matched = parsed_master

        # 2. Check if topic matches theory presets
        content_type = self._detect_content_type(text_input)
        if not matched and content_type == "theory":
            lower_q = text_input.lower()
            for tp in TOP_MNC_THEORY_PRESETS:
                if tp["id"] in lower_q or any(kw in lower_q for kw in tp["title"].lower().split() if len(kw) > 4):
                    matched = tp
                    break
            if not matched:
                if "where" in lower_q and "having" in lower_q:
                    matched = TOP_MNC_THEORY_PRESETS[0]
                elif "acid" in lower_q or "atomicity" in lower_q:
                    matched = TOP_MNC_THEORY_PRESETS[1]
                elif "primary" in lower_q and "unique" in lower_q:
                    matched = TOP_MNC_THEORY_PRESETS[2]

        # 3. Check if topic matches SQL query presets
        if not matched and content_type == "sql_query":
            lower_q = text_input.lower()
            for qp in BANKING_SQL_PRESETS:
                if qp["id"] in lower_q or any(kw in lower_q for kw in qp["title"].lower().split() if len(kw) > 4):
                    matched = qp
                    break

        # 4. If still not matched, synthesize via AI model adapter
        if not matched and len(text_input) > 10:
            try:
                from app.core.model_adapter import model_manager
                if content_type == "theory":
                    ai_prompt = (
                        f"You are a principal SQL teacher. Generate an 85-second step-by-step educational lesson for YouTube Shorts/Reels on this SQL Theory question:\n"
                        f"Question: {text_input}\n"
                        f"Target Language: {lang_key}\n\n"
                        f"Return strictly valid raw JSON:\n"
                        f'{{"content_type": "theory", "title": "...", "concept_summary": "1-2 sentence core definition", '
                        f'"comparison_title": "COMPARISON MATRIX", "comparison_headers": ["ASPECT", "CONCEPT A", "CONCEPT B"], '
                        f'"comparison_rows": ['
                        f'{{"feature": "Execution Stage", "col_a": "...", "col_b": "..."}}, '
                        f'{{"feature": "Usage Scope", "col_a": "...", "col_b": "..."}}'
                        f'], '
                        f'"syntax_a_title": "CONCEPT A SYNTAX", "syntax_a_code": "SELECT ...;", '
                        f'"syntax_b_title": "CONCEPT B SYNTAX", "syntax_b_code": "SELECT ...;", '
                        f'"traps": ["Trap 1", "Rule 1"], "golden_rule": "Golden takeaway rule", "pro_tip": "Interviewer pro-tip", '
                        f'"scenes": ['
                        f'{{"id": 1, "start": 0.0, "end": 8.0, "speech_en": "Intro", "speech_mr": "मराठी स्पष्टीकरण", "speech_hi": "हिन्दी स्पष्टीकरण"}}, '
                        f'{{"id": 2, "start": 8.0, "end": 20.0, "speech_en": "Why asked", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 3, "start": 20.0, "end": 32.0, "speech_en": "Core Architecture", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 4, "start": 32.0, "end": 44.0, "speech_en": "Syntax comparison", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 5, "start": 44.0, "end": 58.0, "speech_en": "Matrix breakdown", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 6, "start": 58.0, "end": 72.0, "speech_en": "Traps and golden rule", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 7, "start": 72.0, "end": 85.0, "speech_en": "Pro-tip and @Code_With_Mangesh", "speech_mr": "...", "speech_hi": "..."}}'
                        f']}}'
                    )
                else:
                    ai_prompt = (
                        f"You are an expert SQL teacher. Generate an 85-second step-by-step educational lesson plan for YouTube Shorts/Reels on this SQL coding question:\n"
                        f"Question: {text_input}\n"
                        f"Target Language: {lang_key}\n\n"
                        f"Return strictly valid raw JSON:\n"
                        f'{{"content_type": "sql_query", "title": "...", "table_name": "EMPLOYEES", '
                        f'"schema_sql": "CREATE TABLE ...; INSERT INTO ...;", "inner_query_sql": "SELECT ...;", '
                        f'"solution_sql": "SELECT ...;", "arrow_target": "...", "explanation": "2-sentence summary", "pro_tip": "...", '
                        f'"scenes": ['
                        f'{{"id": 1, "start": 0.0, "end": 8.0, "speech_en": "Question intro", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 2, "start": 8.0, "end": 20.0, "speech_en": "Inspect table & ties", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 3, "start": 20.0, "end": 32.0, "speech_en": "Algorithm logic", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 4, "start": 32.0, "end": 44.0, "speech_en": "Inner query build", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 5, "start": 44.0, "end": 58.0, "speech_en": "Row filter simulation", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 6, "start": 58.0, "end": 72.0, "speech_en": "Outer execution and output", "speech_mr": "...", "speech_hi": "..."}}, '
                        f'{{"id": 7, "start": 72.0, "end": 85.0, "speech_en": "Interviewer pro tip and @Code_With_Mangesh", "speech_mr": "...", "speech_hi": "..."}}'
                        f']}}'
                    )

                ai_resp, used_model, _ = model_manager.execute_with_fallback(
                    prompt=ai_prompt,
                    system_prompt="You output strictly raw valid JSON without markdown fences."
                )
                if "{" in ai_resp and "}" in ai_resp:
                    json_str = ai_resp[ai_resp.find("{"):ai_resp.rfind("}") + 1]
                    parsed = json.loads(json_str)
                    matched = parsed
                    matched["id"] = "custom_ai_scenario"
                    matched["question"] = text_input
                    matched["difficulty"] = difficulty
            except Exception as e:
                log_event(f"AI short prompt synthesis notice: {e}", level="DEBUG", component="SqlShortEngine")

        # Fallback to default presets if nothing matched
        if not matched:
            if content_type == "theory":
                matched = TOP_MNC_THEORY_PRESETS[0]
            else:
                matched = BANKING_SQL_PRESETS[0]

        matched_content_type = matched.get("content_type", content_type)
        scenes = self._ensure_seven_scenes(matched, matched_content_type, lang_key)
        matched["scenes"] = scenes

        # Gather voice narration script across scenes
        narration_parts = []
        for s in scenes:
            txt = s.get(f"speech_{lang_key}") or s.get("speech_en") or s.get("speech") or ""
            if txt:
                narration_parts.append(txt.strip())

        full_narration = "\n\n".join(narration_parts)
        if not full_narration:
            full_narration = matched.get(f"explanation_{lang_key}") or matched.get("explanation_mr") or matched.get("question", "")

        # Synthesize regional audio
        audio_url = f"/audio/preset_sql_q1_second_highest_salary_{lang_key}.mp3"
        try:
            from app.core.neural_tts import neural_tts
            preset_id = matched.get("id", "custom")
            tts_res = await neural_tts.synthesize_async(
                text=full_narration,
                language=lang_key,
                custom_filename=f"voice_{preset_id}_{lang_key}.mp3"
            )
            if tts_res.get("status") == "success" and tts_res.get("audio_url"):
                audio_url = tts_res.get("audio_url")
        except Exception as e:
            log_event(f"Audio synthesis notice in short engine: {e}", level="DEBUG", component="SqlShortEngine")

        hook = matched.get(f"hook_{lang_key}", matched.get("hook_mr", matched.get("hook_en", "")))
        explanation = matched.get(f"explanation_{lang_key}", matched.get("explanation_mr", matched.get("explanation_en", "")))

        res = {
            "status": "success",
            "content_type": matched_content_type,
            "id": matched.get("id", "custom"),
            "title": matched.get("title", "SQL Interview Preparation"),
            "difficulty": difficulty,
            "language": lang_key,
            "audio_url": audio_url,
            "hook": hook,
            "question": matched.get("question", text_input),
            "pro_tip": matched.get("pro_tip", "💡 Senior Interviewer Pro-Tip: Explain query logic step-by-step."),
            "scenes": scenes,
            "max_duration_seconds": 85,
            "aspect_ratio": "9:16",
            "branding": "@Code_With_Mangesh"
        }

        # Include SQL query specific fields
        if matched_content_type == "sql_query":
            sample_rows = matched.get("sample_rows")
            if not sample_rows:
                sample_rows = [
                    {"account": "101 Amit", "date": "IT", "amt": "₹60,000", "balance": "Active"},
                    {"account": "102 Rahul", "date": "HR", "amt": "₹50,000", "balance": "Active"},
                    {"account": "103 Priya", "date": "IT", "amt": "₹80,000", "balance": "Top Tie"},
                    {"account": "104 Neha", "date": "Finance", "amt": "₹70,000", "balance": "🎯 Target"},
                    {"account": "105 Kiran", "date": "IT", "amt": "₹80,000", "balance": "Top Tie"}
                ]
            filter_evals = matched.get("filter_evaluations")
            if not filter_evals:
                filter_evals = [
                    {"name": "Amit", "salary": "60,000", "cond": "60000 < MAX", "res": "TRUE", "action": "KEEP", "status": "keep"},
                    {"name": "Rahul", "salary": "50,000", "cond": "50000 < MAX", "res": "TRUE", "action": "KEEP", "status": "keep"},
                    {"name": "Priya", "salary": "80,000", "cond": "80000 < MAX", "res": "FALSE", "action": "EXCLUDE", "status": "exclude"},
                    {"name": "Neha", "salary": "70,000", "cond": "70000 < MAX", "res": "TRUE", "action": "KEEP", "status": "keep"},
                    {"name": "Kiran", "salary": "80,000", "cond": "80000 < MAX", "res": "FALSE", "action": "EXCLUDE", "status": "exclude"}
                ]

            res.update({
                "table_name": matched.get("table_name", "EMPLOYEES"),
                "col_headers": matched.get("col_headers", ["EMP_ID", "EMP_NAME", "DEPARTMENT", "SALARY"]),
                "sample_rows": sample_rows,
                "filter_evaluations": filter_evals,
                "output_value": matched.get("output_value", "70000"),
                "schema_sql": matched.get("schema_sql", ""),
                "solution_sql": matched.get("solution_sql", ""),
                "inner_query_sql": matched.get("inner_query_sql", ""),
                "arrow_target": matched.get("arrow_target", "OVER ()"),
                "explanation": explanation
            })
        else:
            # Include Theory specific fields
            comp_rows = matched.get("comparison_rows")
            if not comp_rows:
                comp_rows = [
                    {"feature": "Execution Stage", "col_a": "Pre-Filter Stage", "col_b": "Post-Filter Stage"},
                    {"feature": "Target Scope", "col_a": "Individual Records", "col_b": "Aggregated Groups"},
                    {"feature": "Aggregate Functions", "col_a": "❌ Not Supported", "col_b": "✅ Supported (SUM, COUNT)"},
                    {"feature": "Index Utilization", "col_a": "Uses Table B-Tree", "col_b": "In-Memory Hash"}
                ]
            res.update({
                "concept_summary": matched.get("concept_summary", ""),
                "comparison_title": matched.get("comparison_title", "COMPARISON MATRIX"),
                "comparison_headers": matched.get("comparison_headers", ["ASPECT", "CONCEPT A", "CONCEPT B"]),
                "comparison_rows": comp_rows,
                "syntax_a_title": matched.get("syntax_a_title", "SYNTAX A"),
                "syntax_a_code": matched.get("syntax_a_code", ""),
                "syntax_b_title": matched.get("syntax_b_title", "SYNTAX B"),
                "syntax_b_code": matched.get("syntax_b_code", ""),
                "traps_title": matched.get("traps_title", "COMMON INTERVIEW TRAPS"),
                "traps": matched.get("traps", []),
                "golden_rule": matched.get("golden_rule", "Golden Rule: Check execution order carefully."),
                "solution_sql": matched.get("syntax_a_code", "") + "\n\n" + matched.get("syntax_b_code", ""),
                "explanation": matched.get("concept_summary", "")
            })

        return res

    def generate_short_prompt(
        self,
        topic_or_question: str,
        difficulty: str = "Medium",
        language: str = "mr"
    ) -> Dict[str, Any]:
        """Synchronous wrapper for generate_short_prompt_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In running loop, return baseline structure synchronously
                pass
        except Exception:
            pass

        return asyncio.run(self.generate_short_prompt_async(topic_or_question, difficulty, language))

    def synthesize_voiceover(self, text: str, language: str = "mr") -> Optional[str]:
        """Synthesizes voiceover using Neural TTS Engine."""
        from app.core.neural_tts import neural_tts
        res = neural_tts.synthesize(text=text, language=language)
        if res.get("status") == "success":
            return res.get("file_path")
        return None


# Global Singleton instance
sql_short_engine = SqlShortVideoEngine()

