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
        "pro_tip": "💡 Interviewer Pro-Tip: 'LIMIT 1 OFFSET 1' breaks when the top salary has duplicates (Priya & Kiran both 80,000). The Subquery or DENSE_RANK() approach is mandatory in FAANG interviews!"
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
                    f"You are an expert SQL teacher. Generate an 85-second step-by-step educational lesson plan for YouTube Shorts/Reels:\n"
                    f"Question: {topic_or_question}\n"
                    f"Target Language: {lang_key}\n\n"
                    f"Return ONLY valid raw JSON with:\n"
                    f'{{"title": "...", "hook": "Viral hook with emoji", "schema_sql": "SQLite CREATE & INSERT", '
                    f'"inner_query_sql": "Inner SQL", "solution_sql": "Full SQL Query", "arrow_target": "Clause", '
                    f'"explanation": "2-sentence explanation", "pro_tip": "Interviewer pro-tip", '
                    f'"scenes": ['
                    f'{{"id": 1, "start": 0.0, "end": 8.0, "speech": "Question Intro & Schema"}}, '
                    f'{{"id": 2, "start": 8.0, "end": 20.0, "speech": "Understand Question & Ties"}}, '
                    f'{{"id": 3, "start": 20.0, "end": 32.0, "speech": "Strategy Flowchart"}}, '
                    f'{{"id": 4, "start": 32.0, "end": 44.0, "speech": "Build Inner Query"}}, '
                    f'{{"id": 5, "start": 44.0, "end": 58.0, "speech": "Apply Filter & Evaluate Rows"}}, '
                    f'{{"id": 6, "start": 58.0, "end": 72.0, "speech": "Final Execution & Output"}}, '
                    f'{{"id": 7, "start": 72.0, "end": 85.0, "speech": "Interview Tip & @Code_With_Mangesh"}}'
                    f']}}\n'
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
                        "inner_query_sql": parsed.get("inner_query_sql", ""),
                        "arrow_target": parsed.get("arrow_target", "OVER ()"),
                        "explanation_mr": parsed.get("explanation", "ही क्वेरी अचूक निकाल देते."),
                        "explanation_hi": parsed.get("explanation", "यह क्वेरी सटीक रिजल्ट देती है."),
                        "explanation_en": parsed.get("explanation", "This query calculates the exact outcome."),
                        "explanation_minglish": parsed.get("explanation", "Hi query accurate result dete."),
                        "explanation_hinglish": parsed.get("explanation", "Ye query exact result deti hai."),
                        "pro_tip": parsed.get("pro_tip", "💡 Pro Tip: Optimize using appropriate indexes."),
                        "scenes": parsed.get("scenes", [])
                    }
            except Exception as e:
                log_event(f"AI Prompt generation fallback: {e}", level="DEBUG", component="SqlShortEngine")

        if not matched:
            matched = BANKING_SQL_PRESETS[0]

        hook = matched.get(f"hook_{lang_key}", matched.get("hook_mr", matched["hook_en"]))
        explanation = matched.get(f"explanation_{lang_key}", matched.get("explanation_mr", matched["explanation_en"]))

        # 85-Second Master Storyboard Timeline (7 Educational Scenes)
        timeline = [
            {"time": "0:00 - 0:08", "phase": "INTRO", "title": "1. Question Intro & Schema", "action": "Display question, highlight requirement, EMPLOYEES table, empty SQL editor", "text": hook},
            {"time": "0:08 - 0:20", "phase": "UNDERSTAND", "title": "2. Inspect Values & Tie Trap", "action": "Highlight duplicate 80k values, demonstrate why LIMIT 1 OFFSET 1 fails", "text": matched["question"]},
            {"time": "0:20 - 0:32", "phase": "LOGIC", "title": "3. 4-Step Strategy Flowchart", "action": "Max ➔ Exclude ➔ Remaining Pool ➔ Final Max logic algorithm", "text": "Step-by-step logic before writing code"},
            {"time": "0:32 - 0:44", "phase": "INNER_SQL", "title": "4. Build Inner Query", "action": "Typewriter builds SELECT MAX(SALARY), points arrow from table, outputs 80,000", "text": matched.get("inner_query_sql", "SELECT MAX(SALARY) FROM EMPLOYEES;")},
            {"time": "0:44 - 0:58", "phase": "FILTER", "title": "5. Row-by-Row Simulation", "action": "Apply WHERE SALARY < (MAX), evaluate each employee row, eliminate 80k ties", "text": "Row evaluation: Amit/Rahul/Neha KEEP, Priya/Kiran EXCLUDE"},
            {"time": "0:58 - 1:12", "phase": "RESULT", "title": "6. Outer MAX & Final Output", "action": "Execute complete query, outer MAX selects 70,000, glowing neon output card", "text": explanation},
            {"time": "1:12 - 1:25", "phase": "OUTRO", "title": "7. Interviewer Pro-Tip & Outro", "action": "Explain ANSI SQL standard, DENSE_RANK() for Nth salary, branding @Code_With_Mangesh", "text": matched["pro_tip"]}
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
            "inner_query_sql": matched.get("inner_query_sql", ""),
            "arrow_target": matched["arrow_target"],
            "explanation": explanation,
            "pro_tip": matched["pro_tip"],
            "timeline": timeline,
            "scenes": matched.get("scenes", []),
            "max_duration_seconds": 85,
            "aspect_ratio": "9:16",
            "branding": "@Code_With_Mangesh"
        }

    def synthesize_voiceover(self, text: str, language: str = "mr") -> Optional[str]:
        """Synthesizes voiceover using Neural TTS Engine (ElevenLabs -> Microsoft Neural Edge-TTS)."""
        from app.core.neural_tts import neural_tts
        res = neural_tts.synthesize(text=text, language=language)
        if res.get("status") == "success":
            return res.get("file_path")
        return None


# Global Singleton instance
sql_short_engine = SqlShortVideoEngine()
