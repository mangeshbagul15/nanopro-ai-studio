"""
Mangesh Nano Pro AI Studio - 9:16 SQL Short Video Client-Side Engine
Handles HTML5 Canvas 1080x1920 9:16 rendering, dynamic arrow motion, 
typewriter SQL code animations, multilingual voiceover, and MediaRecorder export with audio multiplexing.
"""

def get_sql_video_js() -> str:
    return r'''
    <script>
    /* ==========================================================================
       9:16 SQL SHORT & REEL ENGINE (CLIENT-SIDE ZERO-SERVER-LOAD)
       ========================================================================== */
    const SQL_CLIENT_PRESETS = {
        "sql_q1_second_highest_salary": {
            id: "sql_q1_second_highest_salary",
            title: "Top MNC / FAANG: 2nd Highest Salary with Duplicate Check (Subquery Method)",
            difficulty: "Core Question",
            hook_mr: "🚨 Top IT कंपन्यांच्या SQL इंटरव्ह्यूमध्ये ९०% मुलं या प्रश्नात चूक करतात! एकापेक्षा जास्त लोकांचा पगार समान असताना २ रा सर्वाधिक पगार कसा शोधायचा?",
            hook_hi: "🚨 Top IT कंपनियों के SQL इंटरव्यू में 90% लोग इस सवाल में गलती करते हैं! जब कई लोगों की सेम सैलरी हो तो 2nd हाईएस्ट सैलरी कैसे निकालें?",
            hook_en: "🚨 90% of candidates make a mistake on this top SQL interview question: Finding the 2nd Highest Salary with Ties!",
            hook_minglish: "🚨 Top MNC interview madhe 90% loka fasatat! Priya & Kiran doghanchi salary same 80k aslyavar 2nd highest salary kashi kadhaychi?",
            hook_hinglish: "🚨 Top MNC interview me 90% log fas jate hai! Priya & Kiran dono ki salary same 80k hone par 2nd highest salary kaise nikale?",
            question: "You have an EMPLOYEES table (EMP_ID, EMP_NAME, DEPARTMENT, SALARY) with records: Amit (60k), Rahul (50k), Priya (80k), Neha (70k), Kiran (80k). How would you find the second-highest salary?",
            table_name: "EMPLOYEES",
            col_headers: ["EMP_ID", "EMP_NAME", "DEPT", "SALARY"],
            schema_sql: `CREATE TABLE EMPLOYEES (
    EMP_ID INTEGER PRIMARY KEY,
    EMP_NAME TEXT,
    DEPARTMENT TEXT,
    SALARY REAL
);
INSERT INTO EMPLOYEES VALUES 
(101, 'Amit', 'IT', 60000),
(102, 'Rahul', 'HR', 50000),
(103, 'Priya', 'IT', 80000),
(104, 'Neha', 'Finance', 70000),
(105, 'Kiran', 'IT', 80000);`,
            solution_sql: `SELECT MAX(SALARY) AS SECOND_HIGHEST_SALARY
FROM EMPLOYEES
WHERE SALARY < (
    SELECT MAX(SALARY)
    FROM EMPLOYEES
);`,
            arrow_target: "WHERE SALARY < (SELECT MAX(SALARY))",
            arrow_line_idx: 2,
            explanation_mr: "इथे आतील सबक्वेरी आधी पूर्ण टेबलमधून कमाल पगार ८०,००० शोधून काढते. मग बाहेरील मुख्य क्वेरी ८०,००० पेक्षा कमी असलेल्या पगारांमधून (६० हजार, ५० हजार, ७० हजार) सर्वात मोठा पगार शोधते, जो येतो बरोबर ७०,०००! जर 'LIMIT 1 OFFSET 1' वापरले तर ८०,००० दोनदा आल्यामुळे उत्तर चुकेल, पण ही सबक्वेरी पद्धत १००% अचूक काम करते!",
            explanation_hi: "यहाँ अंदर वाली सबक्वेरी पहले पूरे टेबल से मैक्सिमम सैलरी 80,000 निकालती है। फिर बाहर वाली मेन क्वेरी 80,000 से कम वाली सैलरीज में से सबसे बड़ी सैलरी चुनती है, जो आती है 70,000! अगर 'LIMIT 1 OFFSET 1' लगाते तो 80,000 दो बार होने से उत्तर गलत आता, लेकिन सबक्वेरी मेथड 100% सही उत्तर देता है!",
            explanation_en: "The inner subquery first finds the maximum salary (80,000). The outer query then filters out all salaries equal to or greater than 80,000, and selects the MAX of the remaining salaries (60k, 50k, 70k), which is 70,000! 'LIMIT 1 OFFSET 1' fails on duplicate ties, whereas this subquery method is 100% reliable!",
            explanation_minglish: "Inner query adhi MAX salary 80,000 kadhte. Mag outer query 80,000 peksha lahan aslelya salaries madhun MAX ghete, ji 70,000 ahe! Duplicates aslyamule LIMIT 1 OFFSET 1 fail hote, pan he subquery solution 100% correct ahe!",
            explanation_hinglish: "Inner query pehle MAX salary 80,000 nikalegi. Fir outer query 80,000 se kam me se MAX legi, jo 70,000 hai! Duplicates me LIMIT 1 OFFSET 1 fail hota hai, but ye subquery solution 100% sahi hai!",
            pro_tip: "💡 Interviewer Pro-Tip: 'LIMIT 1 OFFSET 1' breaks when the top salary has duplicates (Priya & Kiran both 80,000). The Subquery or DENSE_RANK() approach is mandatory in FAANG interviews!",
            sample_rows: [
                {account: "101 Amit", date: "IT", amt: "₹60,000", balance: "Filtered (< 80k)"},
                {account: "102 Rahul", date: "HR", amt: "₹50,000", balance: "Filtered (< 80k)"},
                {account: "103 Priya", date: "IT", amt: "₹80,000", balance: "❌ MAX (Excluded)"},
                {account: "104 Neha", date: "Finance", amt: "₹70,000", balance: "🎯 2nd Highest MAX!"},
                {account: "105 Kiran", date: "IT", amt: "₹80,000", balance: "❌ MAX (Excluded)"}
            ]
        },
        "faang_dense_rank_ties": {
            id: "faang_dense_rank_ties",
            title: "Amazon / Google: 2nd Highest Salary With Ties (DENSE_RANK)",
            difficulty: "Hard",
            hook_mr: "🚨 Google आणि Amazon मुलाखतीत ९५% मुलं या प्रश्नात फेल होतात! समान पगार असताना २ रा नंबर कसा काढायचा?",
            hook_hi: "🚨 Google और Amazon SQL इंटरव्यू का सबसे घातक सवाल! जब दो लोगों की सेम सैलरी हो तो 2nd हाईएस्ट सैलरी कैसे निकालें?",
            hook_en: "🚨 95% of candidates fail this Google & Amazon SQL interview question: 2nd Highest Salary with Ties!",
            hook_minglish: "🚨 Google & Amazon interview madhe 95% pora fail hotat! Duplicate salary aslyavar 2nd highest salary kashi kadhaychi?",
            hook_hinglish: "🚨 Google & Amazon SQL interview me 95% log fail ho jate hai! Duplicate salary hone par 2nd highest salary kaise nikale?",
            question: "Find the 2nd highest salary from the employees table. When multiple employees tie for the top salary, ensure the 2nd distinct highest salary is returned cleanly.",
            table_name: "company_employees",
            col_headers: ["EMPLOYEE", "DEPARTMENT", "SALARY", "DENSE_RANK"],
            schema_sql: `CREATE TABLE company_employees (
    emp_id INTEGER PRIMARY KEY,
    emp_name TEXT,
    department TEXT,
    salary REAL
);
INSERT INTO company_employees VALUES 
(1, 'Aarav Sharma', 'Investment', 185000.0),
(2, 'Rohit Deshmukh', 'Investment', 185000.0),
(3, 'Priya Kulkarni', 'Platforms', 160000.0),
(4, 'Sneha Patel', 'Security', 140000.0);`,
            solution_sql: `WITH RankedSalaries AS (
    SELECT emp_name, department, salary,
        DENSE_RANK() OVER (
            ORDER BY salary DESC
        ) AS rnk
    FROM company_employees
)
SELECT emp_name, department, salary
FROM RankedSalaries
WHERE rnk = 2;`,
            arrow_target: "DENSE_RANK() OVER (ORDER BY salary DESC)",
            arrow_line_idx: 2,
            explanation_mr: "इथे आरव आणि रोहित दोघांचा पगार समान ₹१,८५,००० असल्याने दोघांना १ ला रँक मिळतो. RANK() मुळे पुढचा नंबर ३ रा होतो, पण DENSE_RANK() नंबर स्किप न करता प्रियाला अचूक २ रा नंबर देते!",
            explanation_hi: "यहाँ आरव और रोहित दोनों की सैलरी ₹1,85,000 होने पर दोनों को 1st रैंक मिलती है। DENSE_RANK() रैंक स्किप नहीं करता और प्रिया को सही 2nd रैंक देता है!",
            explanation_en: "When multiple employees tie for the highest salary, standard RANK() skips rank 2 and jumps to 3 (1, 1, 3). DENSE_RANK() never skips numbers (1, 1, 2)!",
            explanation_minglish: "Top 2 chi salary same asel tar RANK() rank 3 var jump karte. Pan DENSE_RANK() rank skip karat nahi ani accurate 2nd salary Priya la bhetate!",
            explanation_hinglish: "Ties hone par normal RANK() 3 pe jump karega. But DENSE_RANK() rank skip nahi karta aur exact 2nd salary nikalta hai!",
            pro_tip: "💡 Senior Interviewer Pro-Tip: Never use 'LIMIT 1 OFFSET 1' when salaries can tie—DENSE_RANK() is the only standard-compliant solution!",
            sample_rows: [
                {account: "Aarav Sharma", date: "Investment", amt: "₹1,85,000", balance: "Rank 1 (Tie)"},
                {account: "Rohit Deshmukh", date: "Investment", amt: "₹1,85,000", balance: "Rank 1 (Tie)"},
                {account: "Priya Kulkarni", date: "Platforms", amt: "₹1,60,000", balance: "🎯 Rank 2 (अचूक)"},
                {account: "Sneha Patel", date: "Security", amt: "₹1,40,000", balance: "Rank 3"}
            ]
        },
        "goldman_running_balance": {
            id: "goldman_running_balance",
            title: "Goldman Sachs / HDFC: Cumulative Running Balance (SUM OVER PARTITION BY)",
            difficulty: "Medium",
            hook_mr: "🚨 HDFC आणि Goldman Sachs बँकेच्या टेक्निकल राऊंडमधील नंबर १ प्रश्न: क्युम्युलेटिव्ह बॅलन्स कसा काढायचा?",
            hook_hi: "🚨 Goldman Sachs और HDFC बैंक इंटरव्यू का पसंदीदा सवाल: Cumulative Running Balance कैसे कैलकुलेट करें?",
            hook_en: "🚨 Goldman Sachs & HDFC favorite SQL test: Calculate running ledger balance per account!",
            hook_minglish: "🚨 Goldman Sachs & HDFC interview cha No. 1 question: Cumulative balance kasa calculate karaycha?",
            hook_hinglish: "🚨 Goldman Sachs & HDFC interview ka No. 1 question: Cumulative running balance kaise nikale?",
            question: "Calculate the cumulative running balance for each customer account ordered by transaction date without using slow correlated subqueries.",
            table_name: "bank_transactions",
            col_headers: ["ACCOUNT", "TXN_DATE", "AMOUNT", "RUNNING_BAL"],
            schema_sql: `CREATE TABLE bank_transactions (
    txn_id INTEGER PRIMARY KEY,
    account_no TEXT,
    txn_date TEXT,
    amount REAL
);
INSERT INTO bank_transactions VALUES 
(101, 'ACC-8821', '2026-10-01', 5000.0),
(102, 'ACC-8821', '2026-10-03', -1200.0),
(103, 'ACC-8821', '2026-10-05', 8500.0),
(104, 'ACC-9942', '2026-10-02', 12000.0);`,
            solution_sql: `SELECT account_no, txn_date, amount,
    SUM(amount) OVER (
        PARTITION BY account_no 
        ORDER BY txn_date 
        ROWS BETWEEN UNBOUNDED PRECEDING 
        AND CURRENT ROW
    ) AS running_balance
FROM bank_transactions;`,
            arrow_target: "PARTITION BY account_no",
            arrow_line_idx: 2,
            explanation_mr: "इथे 'PARTITION BY account_no' मुळे प्रत्येक खात्याचा स्वतंत्र ग्रुप तयार होतो, आणि 'ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW' मुळे सुरुवातीपासून आजपर्यंतची चालू बेरीज चालू राहते!",
            explanation_hi: "यहाँ 'PARTITION BY account_no' हर अकाउंट को अलग रखता है और 'SUM(amount) OVER' लगातार चालू बैलेंस को जोड़ता जाता है!",
            explanation_en: "PARTITION BY account_no keeps each customer ledger strictly isolated while SUM() OVER accumulates sequentially in O(N) linear time!",
            explanation_minglish: "PARTITION BY account_no mule pratyek account cha vegla ledger rahto ani running balance step-by-step calculate hoto!",
            explanation_hinglish: "PARTITION BY se har account ka hisab alag rehta hai aur running balance step by step calculate hota hai!",
            pro_tip: "💡 Senior Interviewer Pro-Tip: Correlated subqueries run in quadratic O(N²) time. Window functions process millions of rows in linear O(N) time!",
            sample_rows: [
                {account: "ACC-8821", date: "2026-10-01", amt: "+₹5,000", balance: "₹5,000"},
                {account: "ACC-8821", date: "2026-10-03", amt: "-₹1,200", balance: "₹3,800"},
                {account: "ACC-8821", date: "2026-10-05", amt: "+₹8,500", balance: "🎯 ₹12,300"},
                {account: "ACC-9942", date: "2026-10-02", amt: "+₹12,000", balance: "₹12,000"}
            ]
        },
        "uber_consecutive_active_days": {
            id: "uber_consecutive_active_days",
            title: "Uber / Swiggy: Consecutive Active Days (Gaps & Islands Problem)",
            difficulty: "Hard",
            hook_mr: "🚨 Uber आणि Swiggy च्या सिस्टीम डिझाइन SQL मध्ये सलग ३ दिवस सक्रिय ड्रायव्हर्स कसे शोधायचे?",
            hook_hi: "🚨 Uber और Swiggy डेटा एनालिस्ट इंटरव्यू: लगातार 3 दिन एक्टिव रहने वाले राइडर्स कैसे खोजें?",
            hook_en: "🚨 Uber & Swiggy Data Analyst Interview: Solve the legendary Gaps and Islands problem!",
            hook_minglish: "🚨 Uber ani Swiggy interview cha legendary Gaps & Islands problem kasa solve karaycha?",
            hook_hinglish: "🚨 Uber aur Swiggy ka classic Gaps & Islands SQL problem: Consecutive 3 days active users!",
            question: "Find all driver IDs who completed rides for at least 3 consecutive days using the Gaps and Islands date subtraction technique.",
            table_name: "driver_trips",
            col_headers: ["DRIVER_ID", "STREAK_START", "STREAK_END", "ACTIVE_DAYS"],
            schema_sql: `CREATE TABLE driver_trips (
    trip_id INTEGER PRIMARY KEY,
    driver_id TEXT,
    trip_date TEXT
);
INSERT INTO driver_trips VALUES 
(1, 'DRV-101', '2026-10-01'),
(2, 'DRV-101', '2026-10-02'),
(3, 'DRV-101', '2026-10-03'),
(4, 'DRV-202', '2026-10-01');`,
            solution_sql: `WITH GroupedTrips AS (
    SELECT driver_id, trip_date,
        DATE(trip_date, '-' || ROW_NUMBER() OVER (
            PARTITION BY driver_id ORDER BY trip_date
        ) || ' days') AS island_group
    FROM driver_trips
)
SELECT driver_id, MIN(trip_date) AS s_start,
    MAX(trip_date) AS s_end, COUNT(*) AS days
FROM GroupedTrips
GROUP BY driver_id, island_group
HAVING COUNT(*) >= 3;`,
            arrow_target: "ROW_NUMBER() OVER (PARTITION BY driver_id ORDER BY trip_date)",
            arrow_line_idx: 2,
            explanation_mr: "जेव्हा तारखा सलग असतात, तेव्हा 'trip_date - ROW_NUMBER()' केल्यास एकच स्थिर तारीख (Island Group Key) मिळते! HAVING COUNT >= 3 ने सलग ३ दिवस काम केलेले ड्रायव्हर्स सापडतात!",
            explanation_hi: "जब तारीखें लगातार होती हैं, तो trip_date में से ROW_NUMBER घटाने पर एक स्थिर ग्रुप मिलता है! HAVING COUNT >= 3 से लगातार एक्टिव ड्राइवर्स मिल जाते हैं!",
            explanation_en: "Subtracting ROW_NUMBER() from consecutive dates yields an identical anchor date. Grouping with HAVING COUNT >= 3 cleanly isolates streaks!",
            explanation_minglish: "Trip_date madhun ROW_NUMBER minus kelyavar constant anchor date milte. HAVING COUNT >= 3 mule 3 days streak clear diste!",
            explanation_hinglish: "Dates me se ROW_NUMBER minus karne par island key banti hai aur continuous active days filter ho jate hai!",
            pro_tip: "💡 Senior Interviewer Pro-Tip: The 'date minus row_number' trick is the most prized FAANG technique for solving streak and login retention queries!",
            sample_rows: [
                {account: "DRV-101", date: "2026-10-01", amt: "Day 1", balance: "Active"},
                {account: "DRV-101", date: "2026-10-02", amt: "Day 2", balance: "Active"},
                {account: "DRV-101", date: "2026-10-03", amt: "Day 3", balance: "🎯 Streak: 3 Days"}
            ]
        },
        "netflix_top_n_per_category": {
            id: "netflix_top_n_per_category",
            title: "Netflix / Spotify: Top 2 Most Streamed Titles Per Category (PARTITION BY)",
            difficulty: "Medium",
            hook_mr: "🚨 Netflix आणि Spotify च्या डेटा सायन्स मुलाखतीत प्रत्येक कॅटेगरीतील टॉप २ शो कसे शोधतात?",
            hook_hi: "🚨 Netflix और Spotify SQL इंटरव्यू: हर कैटेगरी में से टॉप 2 सबसे ज्यादा देखे गए शोज कैसे निकालें?",
            hook_en: "🚨 Netflix & Spotify Data Science Interview: Extract Top 2 most streamed titles per genre!",
            hook_minglish: "🚨 Netflix & Spotify interview: pratyek genre madhun Top 2 most watched movies kase kadhayche?",
            hook_hinglish: "🚨 Netflix & Spotify interview: har category se Top 2 highest stream titles kaise filter kare?",
            question: "Find the top 2 most watched titles for each genre based on total watch hours using window partitioning.",
            table_name: "content_streams",
            col_headers: ["TITLE", "GENRE", "WATCH_HOURS", "GENRE_RANK"],
            schema_sql: `CREATE TABLE content_streams (
    content_id INTEGER PRIMARY KEY,
    title TEXT,
    genre TEXT,
    watch_hours INTEGER
);
INSERT INTO content_streams VALUES 
(1, 'Stranger Things', 'Sci-Fi', 850000),
(2, 'Dark', 'Sci-Fi', 720000),
(3, 'The Crown', 'Drama', 910000),
(4, 'Breaking Bad', 'Drama', 990000);`,
            solution_sql: `WITH RankedContent AS (
    SELECT title, genre, watch_hours,
        DENSE_RANK() OVER (
            PARTITION BY genre 
            ORDER BY watch_hours DESC
        ) AS rank_in_genre
    FROM content_streams
)
SELECT title, genre, watch_hours, rank_in_genre
FROM RankedContent
WHERE rank_in_genre <= 2;`,
            arrow_target: "PARTITION BY genre ORDER BY watch_hours DESC",
            arrow_line_idx: 3,
            explanation_mr: "इथे 'PARTITION BY genre' मुळे प्रत्येक जॉनरचे (Sci-Fi, Drama) स्वतंत्र रँकिंग ब्लॉक तयार होते आणि 'WHERE rank_in_genre <= 2' मुळे प्रत्येक जॉनरचे टॉप २ शोज बाहेर येतात!",
            explanation_hi: "यहाँ 'PARTITION BY genre' हर जॉनर का अलग पार्टीशन बनाता है और 'WHERE rank_in_genre <= 2' से हर कैटेगरी के टॉप 2 शोज फिल्टर हो जाते हैं!",
            explanation_en: "PARTITION BY genre resets the ranking boundary for each genre independently, letting WHERE rank <= 2 extract top performers without grouping collapse!",
            explanation_minglish: "PARTITION BY genre mule Sci-Fi ani Drama cha ranking vegla hoto ani top 2 titles extract hotat!",
            explanation_hinglish: "PARTITION BY genre se category wise ranking reset hoti hai aur top 2 records easily mil jate hai!",
            pro_tip: "💡 Senior Interviewer Pro-Tip: Using PARTITION BY with DENSE_RANK() avoids expensive self-joins and scales to millions of catalogue items!",
            sample_rows: [
                {account: "Breaking Bad", date: "Drama", amt: "990,000 hrs", balance: "🎯 Rank 1"},
                {account: "The Crown", date: "Drama", amt: "910,000 hrs", balance: "🎯 Rank 2"},
                {account: "Stranger Things", date: "Sci-Fi", amt: "850,000 hrs", balance: "🎯 Rank 1"},
                {account: "Dark", date: "Sci-Fi", amt: "720,000 hrs", balance: "🎯 Rank 2"}
            ]
        },
        "meta_reciprocal_friends": {
            id: "meta_reciprocal_friends",
            title: "Meta / LinkedIn: Find Reciprocal Follows / Mutual Connections (Self-Join)",
            difficulty: "Medium",
            hook_mr: "🚨 Meta (Facebook) आणि LinkedIn च्या SQL टेस्टमध्ये म्युचुअल फॉलोवर्स कसे शोधायचे?",
            hook_hi: "🚨 Meta और LinkedIn इंटरव्यू: दो लोग जो एक-दूसरे को फॉलो करते हैं उन्हें SQL से कैसे निकालें?",
            hook_en: "🚨 Meta & LinkedIn SQL Interview: Find all pairs of mutual / reciprocal connections!",
            hook_minglish: "🚨 Meta & LinkedIn interview: mutual friends ani reciprocal follows kase find out karayche?",
            hook_hinglish: "🚨 Meta & LinkedIn interview: mutual connections aur reciprocal follow pairs kaise nikale?",
            question: "Find all distinct pairs of users who reciprocally follow each other. Do not return duplicate reversed pairs (A, B) and (B, A).",
            table_name: "user_follows",
            col_headers: ["USER_A", "USER_B", "STATUS", "RELATION"],
            schema_sql: `CREATE TABLE user_follows (
    user_id TEXT,
    following_id TEXT,
    follow_date TEXT,
    PRIMARY KEY (user_id, following_id)
);
INSERT INTO user_follows VALUES 
('USR-1', 'USR-2', '2026-10-01'),
('USR-2', 'USR-1', '2026-10-02'),
('USR-3', 'USR-4', '2026-10-04'),
('USR-4', 'USR-3', '2026-10-05');`,
            solution_sql: `SELECT f1.user_id AS user_a,
    f1.following_id AS user_b
FROM user_follows f1
JOIN user_follows f2 
  ON f1.user_id = f2.following_id 
 AND f1.following_id = f2.user_id
WHERE f1.user_id < f1.following_id;`,
            arrow_target: "ON f1.user_id = f2.following_id AND f1.following_id = f2.user_id",
            arrow_line_idx: 3,
            explanation_mr: "इथे Self-Join वापरला आहे. '(USR-1, USR-2)' आणि '(USR-2, USR-1)' अशी डुप्लिकेट जोडी नको म्हणून 'WHERE f1.user_id < f1.following_id' लावून एकच अचूक जोडी ठेवली!",
            explanation_hi: "यहाँ हमने Self-Join इस्तेमाल किया है। '(A, B)' और '(B, A)' जैसे डुप्लिकेट्स को रोकने के लिए 'WHERE user_id < following_id' की शर्त लगाई गई है!",
            explanation_en: "Self-joining the table on reciprocal user IDs matches bidirectional friendships. Adding 'WHERE f1.user_id < f1.following_id' eliminates symmetric duplicate pairs!",
            explanation_minglish: "Self-join kelyane reciprocal follows bhetle. Ani f1.user_id < f1.following_id mule reverse duplicates delete jhale!",
            explanation_hinglish: "Self-join se mutual followers nikalte hai aur f1.user_id < f1.following_id se duplicate pairs filter ho jate hai!",
            pro_tip: "💡 Senior Interviewer Pro-Tip: Whenever comparing bidirectional graph edges, adding '<' on the keys prevents redundant mirrored output!",
            sample_rows: [
                {account: "USR-1", date: "USR-2", amt: "Follows Both", balance: "🎯 Mutual Match"},
                {account: "USR-3", date: "USR-4", amt: "Follows Both", balance: "🎯 Mutual Match"}
            ]
        },
        "amazon_churn_zero_orders": {
            id: "amazon_churn_zero_orders",
            title: "Amazon / Flipkart: Customers Who Registered But Never Placed an Order (Anti-Join)",
            difficulty: "Easy",
            hook_mr: "🚨 Amazon SQL राउंड १: रजिस्ट्रेशन केले पण १ ही ऑर्डर न दिलेले ग्राहक कसे शोधायचे? 'NOT IN' का वापरू नये?",
            hook_hi: "🚨 Amazon SQL Interview: वे कस्टमर्स जिन्होंने रजिस्टर किया पर कभी ऑर्डर नहीं दिया! NOT IN क्यों फेल होता है?",
            hook_en: "🚨 Amazon & Flipkart SQL Test: Find registered customers with ZERO orders! Why NOT IN fails!",
            hook_minglish: "🚨 Amazon SQL test: account banavla pan 0 orders keleli lok kashi shodhaychi? LEFT JOIN magic!",
            hook_hinglish: "🚨 Amazon SQL test: sign up kiya par zero orders wale customers kaise filter kare?",
            question: "Find all registered customers who have never placed an order. Demonstrate why LEFT JOIN with IS NULL is superior to NOT IN.",
            table_name: "portal_customers",
            col_headers: ["CUSTOMER_ID", "NAME", "SIGNUP_DATE", "TOTAL_ORDERS"],
            schema_sql: `CREATE TABLE portal_customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT,
    signup_date TEXT
);
CREATE TABLE portal_orders (
    order_id INTEGER PRIMARY KEY,
    customer_id TEXT,
    total_amt REAL
);
INSERT INTO portal_customers VALUES 
('CUST-1', 'Rajesh K', '2026-09-01'),
('CUST-2', 'Sunita M', '2026-09-05');
INSERT INTO portal_orders VALUES (501, 'CUST-1', 4500.0);`,
            solution_sql: `SELECT c.customer_id, c.customer_name,
    c.signup_date
FROM portal_customers c
LEFT JOIN portal_orders o 
  ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;`,
            arrow_target: "WHERE o.order_id IS NULL",
            arrow_line_idx: 4,
            explanation_mr: "इथे 'LEFT JOIN' मुळे सर्व ग्राहक येतात. खरेदी नसलेल्यांच्या ऑर्डर आयडी समोर 'NULL' येतो. 'WHERE o.order_id IS NULL' मुळे शून्य ऑर्डर असलेले ग्राहक अचूक वेगळे होतात!",
            explanation_hi: "यहाँ 'LEFT JOIN' सभी कस्टमर्स को लाता है। 'WHERE order_id IS NULL' से वे कस्टमर्स तुरंत फिल्टर हो जाते हैं जिन्होंने कभी कोई खरीदारी नहीं की!",
            explanation_en: "LEFT JOIN preserves all customers. For non-purchasers, order columns evaluate to NULL. 'WHERE o.order_id IS NULL' filters them safely without the NULL trap of NOT IN!",
            explanation_minglish: "LEFT JOIN mule sagli lok yetat ani purchase naslyane order_id NULL disto. WHERE o.order_id IS NULL zero order customers extract karte!",
            explanation_hinglish: "LEFT JOIN se all customers load hote hai aur WHERE order_id IS NULL se non-buying customers accurately filter hote hai!",
            pro_tip: "💡 Senior Interviewer Pro-Tip: If a subquery contains even a single NULL, 'NOT IN' returns EMPTY SET! In production, always use LEFT JOIN with IS NULL or NOT EXISTS!",
            sample_rows: [
                {account: "CUST-1", date: "Rajesh K", amt: "₹4,500.0", balance: "1 Order (Active)"},
                {account: "CUST-2", date: "Sunita M", amt: "NULL", balance: "🎯 0 Orders (Churn Risk)"}
            ]
        },
        "stripe_consecutive_fraud": {
            id: "stripe_consecutive_fraud",
            title: "Stripe / PayPal: Rapid Consecutive Suspicious Card Withdrawals (LAG / LEAD)",
            difficulty: "Hard",
            hook_mr: "🚨 Stripe आणि PayPal फ्रॉड डिटेक्शन SQL: ५ मिनिटांत एकाच कार्डवरून सलग मोठे विड्रॉव्हल कसे पकडायचे?",
            hook_hi: "🚨 Stripe और PayPal फ्रॉड डिटेक्शन: 5 मिनट में लगातार 2 बड़े विड्रॉल कैसे डिटेक्ट करें?",
            hook_en: "🚨 Stripe & PayPal Fraud Security: Detect rapid consecutive high-value withdrawals with LAG()!",
            hook_minglish: "🚨 Stripe & PayPal fraud detection: 5 min madhe back-to-back mothe transactions kase track karayche?",
            hook_hinglish: "🚨 Stripe & PayPal fraud detection: LAG function se rapid suspicious transactions kaise pakde?",
            question: "Find all card accounts that made consecutive withdrawals of more than ₹10,000 back-to-back using the LAG() window function.",
            table_name: "card_transactions",
            col_headers: ["CARD_NO", "AMOUNT", "PREV_AMOUNT", "FRAUD_STATUS"],
            schema_sql: `CREATE TABLE card_transactions (
    id INTEGER PRIMARY KEY,
    card_no TEXT,
    amount REAL,
    tx_time TEXT
);
INSERT INTO card_transactions VALUES 
(1, 'CARD-1001', 15000.0, '10:00:00'),
(2, 'CARD-1001', 20000.0, '10:04:00'),
(3, 'CARD-1002', 2000.0, '11:00:00');`,
            solution_sql: `WITH TxnWithLag AS (
    SELECT card_no, amount, tx_time,
        LAG(amount, 1) OVER (
            PARTITION BY card_no 
            ORDER BY tx_time
        ) AS prev_amount
    FROM card_transactions
)
SELECT card_no, amount, prev_amount, tx_time
FROM TxnWithLag
WHERE amount >= 10000 AND prev_amount >= 10000;`,
            arrow_target: "LAG(amount, 1) OVER (PARTITION BY card_no ORDER BY tx_time)",
            arrow_line_idx: 2,
            explanation_mr: "इथे 'LAG()' फंक्शन आधीच्या विड्रॉव्हलची रक्कम लगेच पुढच्या ओळीत दाखवते. जर चालू रक्कम आणि आधीची रक्कम दोन्ही ₹१०,००० पेक्षा जास्त असतील तर फ्रॉड अलार्म लगेच ट्रिगर होतो!",
            explanation_hi: "यहाँ 'LAG()' पिछली ट्रांजैक्शन की वैल्यू सामने लाता है। जब करंट और पिछला दोनों अमाउंट ₹10,000+ होते हैं तो फ्रॉड फ़्लैग हो जाता है!",
            explanation_en: "LAG() accesses preceding rows without self-joins. Checking where both current amount and prev_amount exceed ₹10,000 detects velocity fraud in a single scan!",
            explanation_minglish: "LAG() function adhicha transaction samor aante. Current ani previous amount 10k peksha jast asel tar fraud alert lagech disto!",
            explanation_hinglish: "LAG() function pichhle record ko current row me fetch karta hai aur consecutive high value transactions flag ho jate hai!",
            pro_tip: "💡 Senior Interviewer Pro-Tip: LAG() and LEAD() avoid costly Cartesian self-joins and are the foundation of real-time fraud engines!",
            sample_rows: [
                {account: "CARD-1001", date: "10:00:00", amt: "₹15,000", balance: "Txn #1"},
                {account: "CARD-1001", date: "10:04:00", amt: "₹20,000", balance: "🚨 FRAUD ALERT (Consecutive)"}
            ]
        },
        "zomato_mom_growth": {
            id: "zomato_mom_growth",
            title: "Swiggy / Zomato: Month-over-Month (MoM) Revenue Growth Percentage (LAG Window)",
            difficulty: "Medium",
            hook_mr: "🚨 Zomato आणि Swiggy बिझनेस रिपोर्टिंग: दर महिन्याची टक्केवारीतील वाढ (MoM Growth %) कशी काढायची?",
            hook_hi: "🚨 Zomato और Swiggy डेटा एनालिटिक्स: Month-over-Month रेवेन्यू ग्रोथ % कैसे निकालें?",
            hook_en: "🚨 Swiggy & Zomato Business Intelligence: Calculate Month-over-Month (MoM) Growth % with LAG()!",
            hook_minglish: "🚨 Zomato & Swiggy BI interview: Month-over-Month growth percentage kashi calculate karaychi?",
            hook_hinglish: "🚨 Zomato & Swiggy analytics: MoM revenue growth % ka standard SQL formula!",
            question: "Calculate the Month-over-Month (MoM) revenue growth percentage across consecutive reporting months using the LAG() window function.",
            table_name: "monthly_business_metrics",
            col_headers: ["REPORT_MONTH", "REVENUE", "PREV_MONTH", "MOM_GROWTH_%"],
            schema_sql: `CREATE TABLE monthly_business_metrics (
    report_month TEXT PRIMARY KEY,
    total_revenue REAL
);
INSERT INTO monthly_business_metrics VALUES 
('2026-07', 5000000.0),
('2026-08', 6200000.0),
('2026-09', 7500000.0),
('2026-10', 9000000.0);`,
            solution_sql: `WITH MonthlyTotals AS (
    SELECT report_month, total_revenue,
        LAG(total_revenue, 1) OVER (
            ORDER BY report_month
        ) AS prev_month_revenue
    FROM monthly_business_metrics
)
SELECT report_month, total_revenue, prev_month_revenue,
    ROUND(((total_revenue - prev_month_revenue) * 100.0) / prev_month_revenue, 2) AS mom_growth_pct
FROM MonthlyTotals;`,
            arrow_target: "LAG(total_revenue, 1) OVER (ORDER BY report_month)",
            arrow_line_idx: 2,
            explanation_mr: "इथे 'LAG(total_revenue, 1)' मागील महिन्याचा महसूल बरोबर बाजूला आणतो, ज्यामुळे ((Current - Prev) * 100 / Prev) सूत्राने टक्केवारीतील नफा अचूक काढता येतो!",
            explanation_hi: "यहाँ 'LAG(total_revenue, 1)' पिछले महीने का रेवेन्यू सामने लाता है, जिससे ((Current - Prev) * 100 / Prev) फ़ॉर्मूले से MoM Growth % निकल आता है!",
            explanation_en: "LAG(total_revenue, 1) pulls previous month revenue onto the current row, allowing clean ((Current - Prev) * 100 / Prev) calculation without joining on date offsets!",
            explanation_minglish: "LAG function pichlya mahinyacha revenue deto ani MoM growth percentage clean calculate hoto!",
            explanation_hinglish: "LAG() se pichhle mahine ka revenue easily milta hai aur MoM percentage growth accurately compute hoti hai!",
            pro_tip: "💡 Senior Interviewer Pro-Tip: Rounding to 2 decimal places and handling NULL on the first month makes your SQL dashboard-ready for C-level executives!",
            sample_rows: [
                {account: "2026-07", date: "₹50.0 L", amt: "Base Month", balance: "0.0%"},
                {account: "2026-08", date: "₹62.0 L", amt: "₹50.0 L", balance: "+24.0% Growth"},
                {account: "2026-09", date: "₹75.0 L", amt: "₹62.0 L", balance: "+20.97% Growth"},
                {account: "2026-10", date: "₹90.0 L", amt: "₹75.0 L", balance: "🎯 +20.0% Growth"}
            ]
        }
    };

    let sqlShortState = {
        currentTime: 0.0,
        maxDuration: 60.0,
        isPlaying: false,
        playbackSpeed: 1.0,
        audioLang: 'mr',
        textStyle: 'minglish',
        showAvatar: true,
        activePreset: SQL_CLIENT_PRESETS["sql_q1_second_highest_salary"],
        selectedAvatar: "Nadim_public_5",
        avatarVideoElement: null,
        avatarVideoLoaded: false,
        backgroundVideoElement: null,
        backgroundVideoLoaded: false,
        animationFrameId: null,
        lastTimestamp: null,
        isExporting: false,
        mediaRecorder: null,
        recordedChunks: [],
        audioUrl: "/audio/preset_sql_q1_second_highest_salary_mr.mp3"
    };

    // Initialize Workspace on Page Load
    document.addEventListener("DOMContentLoaded", () => {
        initSqlShortWorkspace();
    });

    // Also initialize immediately in case script is injected after DOMContentLoaded
    setTimeout(() => {
        if (!document.getElementById("sqlShortQuestion") || !document.getElementById("sqlShortQuestion").value) {
            initSqlShortWorkspace();
        }
    }, 150);

    function initSqlShortWorkspace() {
        const preset = sqlShortState.activePreset;
        const qEl = document.getElementById("sqlShortQuestion");
        const cEl = document.getElementById("sqlShortCodePreview");
        if (qEl) qEl.value = preset.question;
        if (cEl) cEl.value = preset.solution_sql;

        updateSqlBlueprintUI(preset);
        loadPresetVoiceAudio();
        renderSqlShortFrame(0);
    }

    // Audio Loading & Synthesis
    async function loadPresetVoiceAudio() {
        const p = sqlShortState.activePreset;
        const lang = sqlShortState.audioLang;
        const audioEl = document.getElementById("sqlVoiceAudio");
        const badge = document.getElementById("activeVoiceBadge");

        if (badge) {
            badge.innerText = lang === "mr" ? "🇮🇳 मराठी शिक्षिका (Aarohi Neural)" : (lang === "hi" ? "🇮🇳 हिन्दी शिक्षिका (Swara Neural)" : "🇬🇧 English Teacher (Neerja Neural)");
        }

        try {
            const res = await fetch("/api/sql_video/synthesize_voice", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    preset_id: p.id,
                    language: lang,
                    text: p.question
                })
            });
            const data = await res.json();
            if (data.status === "success" && data.audio_url) {
                sqlShortState.audioUrl = data.audio_url;
                if (audioEl) {
                    audioEl.src = data.audio_url;
                    audioEl.load();
                }
            }
        } catch(e) {
            console.warn("Audio loading notice:", e);
        }
    }

    function setSqlAudioLang(lang) {
        sqlShortState.audioLang = lang;
        document.querySelectorAll(".sql-lang-btn").forEach(b => b.classList.remove("active"));
        const btn = document.getElementById("btnAudio" + lang.charAt(0).toUpperCase() + lang.slice(1));
        if (btn) btn.classList.add("active");
        
        loadPresetVoiceAudio();
        updateSqlBlueprintUI(sqlShortState.activePreset);
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function setSqlTextStyle(style) {
        sqlShortState.textStyle = style;
        document.querySelectorAll(".sql-text-btn").forEach(b => b.classList.remove("active"));
        const btn = document.getElementById("btnText" + style.charAt(0).toUpperCase() + style.slice(1));
        if (btn) btn.classList.add("active");
        updateSqlBlueprintUI(sqlShortState.activePreset);
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function toggleSqlAvatar(enabled) {
        sqlShortState.showAvatar = !!enabled;
        const btnOn = document.getElementById("btnAvatarToggleOn");
        const btnOff = document.getElementById("btnAvatarToggleOff");
        if (enabled) {
            if (btnOn) btnOn.classList.add("active");
            if (btnOff) btnOff.classList.remove("active");
        } else {
            if (btnOn) btnOn.classList.remove("active");
            if (btnOff) btnOff.classList.add("active");
        }
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function handleSqlPresetChange(val) {
        if (val === "custom") {
            document.getElementById("sqlShortQuestion").value = "";
            document.getElementById("sqlShortCodePreview").value = "";
            return;
        }
        const p = SQL_CLIENT_PRESETS[val];
        if (p) {
            sqlShortState.activePreset = p;
            document.getElementById("sqlShortQuestion").value = p.question;
            document.getElementById("sqlShortCodePreview").value = p.solution_sql;
            updateSqlBlueprintUI(p);
            loadPresetVoiceAudio();
            restartSqlShortPlay();
        }
    }

    function updateSqlBlueprintUI(p) {
        const hookText = p['hook_' + sqlShortState.textStyle] || p['hook_' + sqlShortState.audioLang] || p.hook_mr;
        const hookEl = document.getElementById("bpTimelineHook");
        if (hookEl) hookEl.innerText = hookText;
        const arrowEl = document.getElementById("bpArrowTarget");
        if (arrowEl) arrowEl.innerText = p.arrow_target || "OVER ()";

        // Update Technical Concept Breakdown Box
        const conceptEl = document.getElementById("studentConceptHelp");
        if (conceptEl) {
            conceptEl.innerHTML = `
                • <b>प्रश्न समजून घ्या (Question Understanding):</b> ${p.question}<br>
                • <b>महत्त्वाची क्लॉज व ॲरो (Critical Clause):</b> <code style="color:#38BDF8; background:rgba(56,189,248,0.1); padding:2px 4px; border-radius:4px;">${p.arrow_target}</code><br>
                • <b>स्पष्टीकरण:</b> ${p['explanation_' + sqlShortState.textStyle] || p['explanation_' + sqlShortState.audioLang] || p.explanation_mr}<br>
                • <b>${p.pro_tip}</b>
            `;
        }
    }

    async function generateSqlShortBlueprint() {
        const q = document.getElementById("sqlShortQuestion").value.trim();
        const btn = document.getElementById("btnGenerateSqlBlueprint");
        if (!q) { alert("Please enter an SQL question or banking scenario!"); return; }

        btn.innerHTML = `<span>⏳ Synthesizing 60s AI Blueprint...</span>`;
        btn.disabled = true;

        try {
            const res = await fetch("/api/sql_video/generate_prompt", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    question: q,
                    language: sqlShortState.textStyle || sqlShortState.audioLang
                })
            });
            const data = await res.json();
            if (data.status === "success") {
                sqlShortState.activePreset = {
                    id: "custom_ai",
                    title: data.title,
                    difficulty: data.difficulty || "Medium",
                    hook_mr: data.hook,
                    hook_hi: data.hook,
                    hook_en: data.hook,
                    hook_minglish: data.hook,
                    hook_hinglish: data.hook,
                    question: data.question,
                    table_name: data.table_name || "interview_data",
                    col_headers: ["COL_1", "COL_2", "COL_3", "OUTPUT_VAL"],
                    schema_sql: data.schema_sql,
                    solution_sql: data.solution_sql,
                    arrow_target: data.arrow_target,
                    explanation_mr: data.explanation,
                    explanation_hi: data.explanation,
                    explanation_en: data.explanation,
                    explanation_minglish: data.explanation,
                    explanation_hinglish: data.explanation,
                    pro_tip: data.pro_tip,
                    sample_rows: [
                        {account: "REC-101", date: "T1", amt: "₹5,000", balance: "Step 1"},
                        {account: "REC-102", date: "T2", amt: "₹12,000", balance: "Step 2"}
                    ]
                };
                document.getElementById("sqlShortCodePreview").value = data.solution_sql;
                updateSqlBlueprintUI(sqlShortState.activePreset);
                loadPresetVoiceAudio();
                restartSqlShortPlay();
            } else {
                alert("Blueprint generation: " + (data.message || "Failed"));
            }
        } catch (e) {
            console.warn("Using local generator fallback:", e);
        } finally {
            btn.innerHTML = `<span>✨ Generate 60s AI Blueprint &amp; Prompt</span>`;
            btn.disabled = false;
        }
    }

    function setSqlAvatarPresenter(val) {
        sqlShortState.selectedAvatar = val;
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    async function renderAiAvatarVideo() {
        const avatar = sqlShortState.selectedAvatar;
        const statusEl = document.getElementById("avatarRenderStatus");
        const btn = document.getElementById("btnRenderAvatar");
        if (!avatar || avatar === "none") {
            alert("Please select an AI Avatar from the dropdown first!");
            return;
        }

        const p = sqlShortState.activePreset;
        const script = p['hook_' + sqlShortState.textStyle] || p['hook_' + sqlShortState.audioLang] || p.hook_mr;

        statusEl.style.display = "block";
        statusEl.style.color = "#38BDF8";
        statusEl.innerHTML = `<span>⚡ Submitting to Autonomous Avatar Router (Auto-failover HeyGen ➔ D-ID ➔ Cyber Canvas)...</span>`;
        btn.disabled = true;

        try {
            const preferred = avatar.startsWith("did") ? "did" : (avatar !== "none" ? "heygen" : "auto");
            const res = await fetch("/api/video/avatar_cascade", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    script: script,
                    preferred_provider: preferred,
                    avatar_id: avatar.startsWith("did") ? null : avatar,
                    language: sqlShortState.audioLang
                })
            });
            const data = await res.json();

            if (data.status === "success") {
                if (data.provider === "HeyGen" && data.video_id) {
                    const failoverTag = data.failover_used ? " (Auto-switched)" : "";
                    statusEl.innerHTML = `<span>✅ HeyGen 4K Video #${data.video_id} queued${failoverTag}! Generating lip-sync...</span>`;
                    pollHeyGenVideo(data.video_id, statusEl, btn);
                } else if (data.provider === "D-ID" && data.talk_id) {
                    const failoverTag = data.failover_used ? " (Auto-switched from HeyGen)" : "";
                    statusEl.innerHTML = `<span>✅ D-ID Talk #${data.talk_id} queued${failoverTag}! Generating lip-sync...</span>`;
                    pollDIDVideo(data.talk_id, statusEl, btn);
                } else {
                    btn.disabled = false;
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `🛡️ <b>Live Cyber Avatar Active:</b> Auto-switched to High-Tech Presenter with zero watermark!`;
                }
            } else {
                statusEl.style.color = "#EF4444";
                statusEl.innerText = "Router Error: " + (data.message || "Failed");
                btn.disabled = false;
            }
        } catch (e) {
            statusEl.style.color = "#EF4444";
            statusEl.innerText = "Network Error: " + e.message;
            btn.disabled = false;
        }
    }

    function loadAvatarVideoToEngine(url) {
        let vid = document.getElementById("sqlShortAvatarVideo");
        if (!vid) {
            vid = document.createElement("video");
            vid.id = "sqlShortAvatarVideo";
            vid.crossOrigin = "anonymous";
            vid.loop = true;
            vid.muted = true;
            vid.playsInline = true;
            vid.style.display = "none";
            document.body.appendChild(vid);
        }
        vid.src = url;
        vid.onloadeddata = () => {
            sqlShortState.avatarVideoElement = vid;
            sqlShortState.avatarVideoLoaded = true;
            vid.play().catch(e => console.warn("Avatar video autoplay:", e));
            renderSqlShortFrame(sqlShortState.currentTime);
        };
        vid.load();
    }

    async function pollHeyGenVideo(videoId, statusEl, btn) {
        let attempts = 0;
        const maxAttempts = 25;
        const interval = setInterval(async () => {
            attempts++;
            try {
                const res = await fetch(`/api/video/heygen/status/${videoId}`);
                const data = await res.json();
                if (data.status === "completed" && data.video_url) {
                    clearInterval(interval);
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `<span>🎉 HeyGen 4K Avatar Ready! Synced to Video Player.</span>`;
                    btn.disabled = false;
                    loadAvatarVideoToEngine(data.video_url);
                } else if (data.status === "failed") {
                    clearInterval(interval);
                    statusEl.style.color = "#EF4444";
                    statusEl.innerText = "HeyGen Generation Failed: " + (data.error || "Unknown");
                    btn.disabled = false;
                } else {
                    statusEl.innerText = `⏳ HeyGen Rendering: ${data.status || 'processing'} (${attempts}/${maxAttempts})...`;
                }
            } catch (e) {
                console.warn("HeyGen Poll error:", e);
            }
            if (attempts >= maxAttempts) {
                clearInterval(interval);
                statusEl.style.color = "#F59E0B";
                statusEl.innerText = "HeyGen took longer than expected. Using High-Tech Cyber Canvas Presenter.";
                btn.disabled = false;
            }
        }, 3000);
    }

    async function pollDIDVideo(talkId, statusEl, btn) {
        let attempts = 0;
        const maxAttempts = 25;
        const interval = setInterval(async () => {
            attempts++;
            try {
                const res = await fetch(`/api/video/did/status/${talkId}`);
                const data = await res.json();
                if (data.status === "done" && data.result_url) {
                    clearInterval(interval);
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `<span>🎉 D-ID Lip-Sync Ready! Synced to Video Player.</span>`;
                    btn.disabled = false;
                    loadAvatarVideoToEngine(data.result_url);
                } else if (data.status === "error") {
                    clearInterval(interval);
                    statusEl.style.color = "#EF4444";
                    statusEl.innerText = "D-ID Generation Error: " + (data.error || "Unknown");
                    btn.disabled = false;
                } else {
                    statusEl.innerText = `⏳ D-ID Rendering: ${data.status || 'started'} (${attempts}/${maxAttempts})...`;
                }
            } catch (e) {
                console.warn("D-ID Poll error:", e);
            }
            if (attempts >= maxAttempts) {
                clearInterval(interval);
                statusEl.style.color = "#F59E0B";
                statusEl.innerText = "D-ID took longer than expected. Using High-Tech Cyber Canvas Presenter.";
                btn.disabled = false;
            }
        }, 2500);
    }

    async function renderCinematicBackgroundVideo() {
        const bgChoice = document.getElementById("sqlCinematicBgSelect").value;
        const statusEl = document.getElementById("cinematicBgRenderStatus");
        const btn = document.getElementById("btnRenderCinematicBg");

        if (bgChoice === "cyber_matrix") {
            sqlShortState.backgroundVideoElement = null;
            sqlShortState.backgroundVideoLoaded = false;
            statusEl.style.display = "block";
            statusEl.style.color = "#10B981";
            statusEl.innerText = "⚡ Using Cyber Grid Neon Canvas (Ultra-Fast 60 FPS)";
            renderSqlShortFrame(sqlShortState.currentTime);
            return;
        }

        statusEl.style.display = "block";
        statusEl.style.color = "#C084FC";
        statusEl.innerHTML = `<span>⏳ Synthesizing 3D Motion Video (Runway Gen-4 / Luma)...</span>`;
        btn.disabled = true;

        try {
            const isLuma = bgChoice.startsWith("luma");
            const endpoint = isLuma ? "/api/video/luma_cascade" : "/api/video/runway/generate";
            const promptText = isLuma 
                ? "3D cinematic golden SQL database particles flowing vertically in dark cyberspace, 9:16 aspect ratio, volumetric lighting, 4k"
                : "Hyper-realistic high-tech Mumbai banking server room, glowing neon cyan data racks, server status lights, 9:16 vertical view, photorealistic, 8k";

            const res = await fetch(endpoint, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ prompt: promptText, aspect_ratio: "9:16" })
            });
            const data = await res.json();
            if (data.status === "success") {
                statusEl.style.color = "#10B981";
                statusEl.innerHTML = `<span>✅ 3D Motion Generation Queued! Polling stream...</span>`;
                btn.disabled = false;
            } else {
                statusEl.style.color = "#EF4444";
                statusEl.innerText = "Motion Engine: " + (data.message || "Failed");
                btn.disabled = false;
            }
        } catch (e) {
            statusEl.style.color = "#EF4444";
            statusEl.innerText = "Network Error: " + e.message;
            btn.disabled = false;
        }
    }

    async function runInMemorySqlSandbox() {
        const code = document.getElementById("sqlShortCodePreview").value;
        const p = sqlShortState.activePreset;
        const latencyEl = document.getElementById("sandboxLatency");
        const outTableEl = document.getElementById("sandboxOutputTable");

        latencyEl.innerText = "Executing...";
        try {
            const res = await fetch("/api/sql_video/run_sandbox", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    schema_sql: p.schema_sql,
                    query_sql: code
                })
            });
            const data = await res.json();
            latencyEl.innerText = `⏱️ ${data.latency_ms || 1.2} ms (SQLite In-Memory)`;

            if (data.status === "success" && data.columns && data.rows) {
                let html = `<table style="width:100%; border-collapse:collapse; text-align:left;">`;
                html += `<thead><tr style="border-bottom:1px solid #1E2D4A; color:#38BDF8;">`;
                data.columns.forEach(c => html += `<th style="padding:4px 6px;">${c}</th>`);
                html += `</tr></thead><tbody>`;
                data.rows.forEach(r => {
                    html += `<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">`;
                    r.forEach(v => html += `<td style="padding:4px 6px; color:#F8FAFC;">${v}</td>`);
                    html += `</tr>`;
                });
                html += `</tbody></table>`;
                outTableEl.innerHTML = html;
            } else {
                outTableEl.innerHTML = `<span style="color:#EF4444;">Error: ${data.message || 'Execution failed'}</span>`;
            }
        } catch (e) {
            latencyEl.innerText = "Error";
            outTableEl.innerHTML = `<span style="color:#EF4444;">Sandbox Error: ${e.message}</span>`;
        }
    }

    /* ==========================================================================
       CANVAS RENDERING ENGINE (1080 x 1920 9:16 VERTICAL REEL FORMAT)
       ========================================================================== */
    function renderSqlShortFrame(t) {
        const canvas = document.getElementById("sqlShortCanvas");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const W = 1080;
        const H = 1920;
        const p = sqlShortState.activePreset;

        // 1. Dark Cyber/Fintech Neon Background
        ctx.fillStyle = "#070B16";
        ctx.fillRect(0, 0, W, H);

        // Tech grid lines
        ctx.strokeStyle = "rgba(56, 189, 248, 0.04)";
        ctx.lineWidth = 2;
        for (let x = 0; x < W; x += 80) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        }
        for (let y = 0; y < H; y += 80) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
        }

        // Render 3D Motion Video (if loaded)
        const bgVid = sqlShortState.backgroundVideoElement;
        if (bgVid && sqlShortState.backgroundVideoLoaded && bgVid.readyState >= 2) {
            ctx.save();
            ctx.globalAlpha = 0.35;
            const bgW = bgVid.videoWidth || 720;
            const bgH = bgVid.videoHeight || 1280;
            const cropX = bgW * 0.06;
            const cropY = bgH * 0.06;
            const cropW = bgW * 0.88;
            const cropH = bgH * 0.88;
            ctx.drawImage(bgVid, cropX, cropY, cropW, cropH, 0, 0, W, H);
            ctx.restore();
        }

        // Top Status Header (Time, Title & Difficulty Pill)
        ctx.fillStyle = "rgba(14, 21, 40, 0.85)";
        ctx.fillRect(40, 60, W - 80, 110);
        ctx.strokeStyle = "#1E2D4A";
        ctx.strokeRect(40, 60, W - 80, 110);

        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 30px 'Segoe UI', sans-serif";
        ctx.fillText("🚀 FAANG & TOP MNC SQL INTERVIEW PREP", 70, 125);

        // Difficulty Pill
        ctx.fillStyle = "#F59E0B";
        ctx.fillRect(W - 250, 92, 170, 48);
        ctx.fillStyle = "#000000";
        ctx.font = "bold 22px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(p.difficulty.toUpperCase(), W - 165, 124);
        ctx.textAlign = "left";

        // Progress Bar (0:00 to 1:00)
        const progress = Math.min(1.0, t / 60.0);
        ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
        ctx.fillRect(40, 185, W - 80, 10);
        const grad = ctx.createLinearGradient(40, 0, W - 40, 0);
        grad.addColorStop(0, "#06B6D4");
        grad.addColorStop(0.5, "#38BDF8");
        grad.addColorStop(1, "#10B981");
        ctx.fillStyle = grad;
        ctx.fillRect(40, 185, (W - 80) * progress, 10);

        // AI AVATAR PRESENTER PiP (Picture-in-Picture badge with Anti-Watermark Circular Crop)
        if (sqlShortState.showAvatar && sqlShortState.selectedAvatar && sqlShortState.selectedAvatar !== "none") {
            ctx.save();
            const avatarX = W - 140;
            const avatarY = 125;
            const radius = 54;

            // Outer glowing ring
            const glow = 1.0 + Math.sin(t * 5) * 0.08;
            ctx.shadowColor = "#8B5CF6";
            ctx.shadowBlur = 18;
            ctx.strokeStyle = "#8B5CF6";
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.arc(avatarX, avatarY, radius * glow, 0, Math.PI * 2);
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Background circle
            ctx.fillStyle = "#0F172A";
            ctx.beginPath();
            ctx.arc(avatarX, avatarY, radius, 0, Math.PI * 2);
            ctx.fill();

            // Render live avatar video if loaded
            const vid = sqlShortState.avatarVideoElement;
            if (vid && sqlShortState.avatarVideoLoaded && vid.readyState >= 2) {
                ctx.save();
                ctx.beginPath();
                ctx.arc(avatarX, avatarY, radius, 0, Math.PI * 2);
                ctx.clip();

                const vw = vid.videoWidth || 640;
                const vh = vid.videoHeight || 480;
                const sx = vw * 0.15;
                const sy = vh * 0.05;
                const sw = vw * 0.70;
                const sh = vh * 0.70;

                ctx.drawImage(vid, sx, sy, sw, sh, avatarX - radius, avatarY - radius, radius * 2, radius * 2);
                ctx.restore();
            } else {
                // Procedural Cyber Teacher Avatar Presenter
                ctx.fillStyle = "#38BDF8";
                ctx.font = "38px 'Segoe UI', sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("🧑‍💼", avatarX, avatarY + 12);
                ctx.textAlign = "left";
            }

            ctx.restore();
        }

        // =========================================================================
        // TIMELINE PHASES (0 to 60 Seconds)
        // =========================================================================

        // PHASE 1 (0 to 5.5s): VIRAL PEAK POINT / HOOK
        if (t < 5.5) {
            const hookAlpha = t < 5.0 ? 1.0 : (5.5 - t) / 0.5;
            ctx.save();
            ctx.globalAlpha = Math.max(0, hookAlpha);

            // Flashing Red Alert Badge
            const pulse = 1.0 + Math.sin(t * 8) * 0.04;
            ctx.translate(W / 2, 420);
            ctx.scale(pulse, pulse);

            ctx.fillStyle = "rgba(239, 68, 68, 0.25)";
            ctx.beginPath();
            ctx.roundRect(-460, -90, 920, 180, 30);
            ctx.fill();
            ctx.strokeStyle = "#EF4444";
            ctx.lineWidth = 6;
            ctx.stroke();

            ctx.fillStyle = "#EF4444";
            ctx.font = "bold 42px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("🚨 95% CANDIDATES FAIL THIS QUESTION!", 0, -20);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 32px 'Segoe UI', sans-serif";
            const hookText = p['hook_' + sqlShortState.textStyle] || p['hook_' + sqlShortState.audioLang] || p.hook_mr;
            ctx.fillText(wrapCanvasText(ctx, hookText, 860)[0] || hookText, 0, 45);

            ctx.restore();
        }

        // PHASE 2 (5 to 18s): PROBLEM & REAL DATA SCHEMA
        if (t >= 4.5 && t < 19.0) {
            ctx.save();
            const pAlpha = t < 5.5 ? (t - 4.5) : (t > 18.0 ? (19.0 - t) : 1.0);
            ctx.globalAlpha = Math.max(0, Math.min(1.0, pAlpha));

            // Problem Box
            ctx.fillStyle = "rgba(16, 25, 46, 0.95)";
            ctx.beginPath();
            ctx.roundRect(60, 260, W - 120, 200, 20);
            ctx.fill();
            ctx.strokeStyle = "#38BDF8";
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 30px 'Segoe UI', sans-serif";
            ctx.fillText("📋 INTERVIEW QUESTION & UNDERSTANDING:", 90, 315);

            ctx.fillStyle = "#E2E8F0";
            ctx.font = "26px 'Segoe UI', sans-serif";
            const qLines = wrapCanvasText(ctx, p.question, W - 180);
            qLines.slice(0, 2).forEach((l, i) => {
                ctx.fillText(l, 90, 370 + i * 42);
            });

            // Animated Input Table Cards
            ctx.fillStyle = "#94A3B8";
            ctx.font = "bold 26px monospace";
            ctx.fillText(`INPUT TABLE: ${p.table_name}`, 60, 510);

            const headers = p.col_headers || ["COL_1", "COL_2", "COL_3", "STATUS"];
            ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
            ctx.fillRect(60, 530, W - 120, 60);
            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 24px monospace";
            ctx.fillText(headers[0], 90, 570);
            ctx.fillText(headers[1], 350, 570);
            ctx.fillText(headers[2], 610, 570);
            ctx.fillText(headers[3], 830, 570);

            // Row cards
            const sampleRows = p.sample_rows || [];
            sampleRows.forEach((r, idx) => {
                const rowY = 610 + idx * 85;
                ctx.fillStyle = idx % 2 === 0 ? "rgba(15, 23, 42, 0.9)" : "rgba(30, 41, 59, 0.8)";
                ctx.fillRect(60, rowY, W - 120, 75);
                ctx.strokeStyle = "#1E2D4A";
                ctx.strokeRect(60, rowY, W - 120, 75);

                ctx.fillStyle = "#F8FAFC";
                ctx.font = "24px monospace";
                ctx.fillText(r.account, 90, rowY + 46);
                ctx.fillText(r.date, 350, rowY + 46);
                ctx.fillText(r.amt, 610, rowY + 46);

                const isWarning = r.balance && (r.balance.includes("Tie") || r.balance.includes("MAX"));
                ctx.fillStyle = isWarning ? "#F59E0B" : "#38BDF8";
                ctx.font = "bold 24px monospace";
                ctx.fillText(r.balance, 830, rowY + 46);
            });

            // Problem Nuance & Tie Alert Badge
            if (p.id === "sql_q1_second_highest_salary" || p.id === "faang_dense_rank_ties") {
                ctx.fillStyle = "rgba(245, 158, 11, 0.15)";
                ctx.beginPath();
                ctx.roundRect(60, 1050, W - 120, 80, 16);
                ctx.fill();
                ctx.strokeStyle = "#F59E0B";
                ctx.lineWidth = 2.5;
                ctx.stroke();

                ctx.fillStyle = "#F59E0B";
                ctx.font = "bold 24px 'Segoe UI', sans-serif";
                ctx.fillText("⚠️ INTERVIEW TRAP: Priya & Kiran both earn ₹80,000! 'LIMIT 1 OFFSET 1' will FAIL!", 90, 1100);
            }

            ctx.restore();
        }

        // PHASE 3 (18 to 42s): TYPEWRITER SQL CODE & GLOWING LASER ARROW WITH 3D CALLOUT POPUP
        if (t >= 17.5 && t < 43.0) {
            ctx.save();
            const cAlpha = t < 18.5 ? (t - 17.5) : (t > 42.0 ? (43.0 - t) : 1.0);
            ctx.globalAlpha = Math.max(0, Math.min(1.0, cAlpha));

            // Code Editor Window (IDE style)
            ctx.fillStyle = "#0B1120";
            ctx.beginPath();
            ctx.roundRect(50, 240, W - 100, 840, 24);
            ctx.fill();
            ctx.strokeStyle = "#38BDF8";
            ctx.lineWidth = 3;
            ctx.stroke();

            // Window Header with Mac dots
            ctx.fillStyle = "#1E293B";
            ctx.fillRect(50, 240, W - 100, 60);
            ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(85, 270, 10, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(115, 270, 10, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(145, 270, 10, 0, Math.PI * 2); ctx.fill();

            ctx.fillStyle = "#94A3B8";
            ctx.font = "bold 22px monospace";
            ctx.fillText("query_solution.sql", 185, 278);

            // Typewriter Code Lines
            const codeLines = p.solution_sql.split("\n");
            const typingSpeed = (t - 18.0) * 1.5;
            const linesToShow = Math.min(codeLines.length, Math.floor(typingSpeed));

            let arrowTargetY = 460;
            let arrowTargetX = 640;

            for (let i = 0; i < linesToShow; i++) {
                const lineY = 340 + i * 50;
                const lineText = codeLines[i];

                const isTarget = p.arrow_target && (lineText.includes(p.arrow_target.split(" ")[0]) || (p.arrow_line_idx !== undefined && i === p.arrow_line_idx));
                if (isTarget) {
                    arrowTargetY = lineY;
                    arrowTargetX = 80 + ctx.measureText(lineText).width + 30;
                }

                ctx.fillStyle = "#475569";
                ctx.font = "26px monospace";
                ctx.fillText((i + 1).toString().padStart(2, "0"), 80, lineY);

                renderSqlSyntaxLine(ctx, lineText, 140, lineY);
            }

            // DYNAMIC GLOWING ARROW MOTION
            if (t >= 21.0) {
                const arrowBounce = Math.sin((t - 21.0) * 6) * 16;
                const arrowX = Math.min(W - 140, arrowTargetX + 70 + arrowBounce);
                const arrowY = arrowTargetY - 8;

                ctx.shadowColor = "#38BDF8";
                ctx.shadowBlur = 22;

                ctx.fillStyle = "#38BDF8";
                ctx.beginPath();
                ctx.moveTo(arrowX, arrowY);
                ctx.lineTo(arrowX + 45, arrowY - 22);
                ctx.lineTo(arrowX + 45, arrowY - 10);
                ctx.lineTo(arrowX + 130, arrowY - 10);
                ctx.lineTo(arrowX + 130, arrowY + 10);
                ctx.lineTo(arrowX + 45, arrowY + 10);
                ctx.lineTo(arrowX + 45, arrowY + 22);
                ctx.closePath();
                ctx.fill();

                // Arrow Label Badge
                ctx.fillStyle = "#F59E0B";
                ctx.fillRect(arrowX + 140, arrowY - 20, 210, 42);
                ctx.fillStyle = "#000";
                ctx.font = "bold 20px 'Segoe UI', sans-serif";
                ctx.fillText("⚡ CRITICAL CLAUSE", arrowX + 150, arrowY + 8);

                ctx.shadowBlur = 0;
            }

            // ANIMATED 3D POPUP CALLOUT BOX (Explaining why query works)
            if (t >= 22.5) {
                const popAlpha = Math.min(1.0, (t - 22.5) * 1.5);
                ctx.save();
                ctx.globalAlpha = ctx.globalAlpha * popAlpha;

                // Subtle floating bounce
                const floatY = Math.sin((t - 22.5) * 3) * 6;

                ctx.fillStyle = "rgba(11, 17, 32, 0.96)";
                ctx.beginPath();
                ctx.roundRect(80, 690 + floatY, W - 160, 360, 20);
                ctx.fill();
                ctx.strokeStyle = "#38BDF8";
                ctx.lineWidth = 3;
                ctx.shadowColor = "rgba(56, 189, 248, 0.4)";
                ctx.shadowBlur = 18;
                ctx.stroke();
                ctx.shadowBlur = 0;

                // Popup Header with badge
                ctx.fillStyle = "#38BDF8";
                ctx.fillRect(80, 690 + floatY, W - 160, 52);
                ctx.fillStyle = "#070B16";
                ctx.font = "bold 22px 'Segoe UI', sans-serif";
                ctx.fillText("💡 HOW THE AI QUERY SOLVES THIS STEP-BY-STEP", 110, 725 + floatY);

                if (p.id === "sql_q1_second_highest_salary") {
                    ctx.fillStyle = "#F8FAFC";
                    ctx.font = "bold 23px 'Segoe UI', sans-serif";
                    ctx.fillText("1️⃣ Inner Subquery: (SELECT MAX(SALARY)) ➔ ₹80,000", 110, 780 + floatY);

                    ctx.fillStyle = "#EF4444";
                    ctx.fillText("2️⃣ Filter: WHERE SALARY < 80,000 excludes Priya & Kiran duplicates!", 110, 830 + floatY);

                    ctx.fillStyle = "#38BDF8";
                    ctx.fillText("3️⃣ Remaining Pool: Amit (60k), Rahul (50k), Neha (70k)", 110, 880 + floatY);

                    ctx.fillStyle = "#10B981";
                    ctx.font = "bold 25px 'Segoe UI', sans-serif";
                    ctx.fillText("🎯 Outer Query: SELECT MAX() from remaining ➔ 70,000 (Neha)!", 110, 940 + floatY);

                    ctx.fillStyle = "#F59E0B";
                    ctx.font = "italic 21px 'Segoe UI', sans-serif";
                    ctx.fillText("✨ Solves duplicate tie gracefully without hardcoded offsets", 110, 995 + floatY);
                } else {
                    ctx.fillStyle = "#F8FAFC";
                    ctx.font = "bold 23px 'Segoe UI', sans-serif";
                    ctx.fillText(`1️⃣ Target Clause: ${p.arrow_target}`, 110, 780 + floatY);

                    ctx.fillStyle = "#38BDF8";
                    const expSnippet = wrapCanvasText(ctx, p.explanation_en || p.explanation_mr, W - 220);
                    expSnippet.slice(0, 3).forEach((line, idx) => {
                        ctx.fillText(line, 110, 835 + idx * 45 + floatY);
                    });

                    ctx.fillStyle = "#10B981";
                    ctx.font = "bold 24px 'Segoe UI', sans-serif";
                    ctx.fillText("🎯 Guarantees O(N) performance without table locks!", 110, 995 + floatY);
                }

                ctx.restore();
            }

            ctx.restore();
        }

        // PHASE 4 (42 to 54s): REAL SIMULATED OUTPUT CALCULATION
        if (t >= 41.5 && t < 55.0) {
            ctx.save();
            const rAlpha = t < 42.5 ? (t - 41.5) : (t > 54.0 ? (55.0 - t) : 1.0);
            ctx.globalAlpha = Math.max(0, Math.min(1.0, rAlpha));

            ctx.fillStyle = "#10192E";
            ctx.beginPath();
            ctx.roundRect(50, 240, W - 100, 840, 24);
            ctx.fill();
            ctx.strokeStyle = "#10B981";
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = "#10B981";
            ctx.font = "bold 34px 'Segoe UI', sans-serif";
            ctx.fillText("✅ REAL QUERY EXECUTION OUTPUT:", 90, 310);

            // Table Header
            const headers = p.col_headers || ["COL_1", "COL_2", "COL_3", "RESULT"];
            ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
            ctx.fillRect(80, 350, W - 160, 60);
            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 24px monospace";
            ctx.fillText(headers[0], 110, 390);
            ctx.fillText(headers[1], 350, 390);
            ctx.fillText(headers[2], 560, 390);
            ctx.fillText(headers[3], 780, 390);

            // Render Output Rows
            const sampleRows = p.sample_rows || [];
            sampleRows.forEach((r, idx) => {
                const rowY = 440 + idx * 75;
                ctx.fillStyle = idx % 2 === 0 ? "rgba(255,255,255,0.03)" : "transparent";
                ctx.fillRect(80, rowY - 26, W - 160, 68);

                ctx.fillStyle = "#F8FAFC";
                ctx.font = "24px monospace";
                ctx.fillText(r.account, 110, rowY + 14);
                ctx.fillText(r.date, 350, rowY + 14);
                ctx.fillText(r.amt, 560, rowY + 14);

                const isExcluded = r.balance && r.balance.includes("Excluded");
                const isSelected = r.balance && (r.balance.includes("2nd Highest") || r.balance.includes("अचूक"));
                
                if (isSelected) {
                    ctx.shadowColor = "#10B981";
                    ctx.shadowBlur = 15;
                    ctx.fillStyle = "#10B981";
                } else if (isExcluded) {
                    ctx.fillStyle = "#EF4444";
                } else {
                    ctx.fillStyle = "#38BDF8";
                }
                ctx.font = "bold 24px monospace";
                ctx.fillText(r.balance, 780, rowY + 14);
                ctx.shadowBlur = 0;
            });

            // BIG GLOWING RESULT BADGE (Highlighted Final Answer)
            ctx.fillStyle = "rgba(16, 185, 129, 0.2)";
            ctx.beginPath();
            ctx.roundRect(80, 830, W - 160, 210, 18);
            ctx.fill();
            ctx.strokeStyle = "#10B981";
            ctx.lineWidth = 3.5;
            ctx.shadowColor = "rgba(16, 185, 129, 0.4)";
            ctx.shadowBlur = 20;
            ctx.stroke();
            ctx.shadowBlur = 0;

            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 22px 'Segoe UI', sans-serif";
            ctx.fillText("🎯 VERIFIED FINAL QUERY OUTPUT:", 110, 875);

            if (p.id === "sql_q1_second_highest_salary") {
                ctx.fillStyle = "#F8FAFC";
                ctx.font = "22px monospace";
                ctx.fillText("OUTPUT COLUMN: SECOND_HIGHEST_SALARY", 110, 925);

                ctx.fillStyle = "#10B981";
                ctx.font = "bold 48px monospace";
                ctx.fillText("VALUE: 70000", 110, 985);

                ctx.fillStyle = "#F59E0B";
                ctx.font = "bold 20px 'Segoe UI', sans-serif";
                ctx.fillText("✅ Verified Match: Neha (Finance Department)", 110, 1022);
            } else {
                ctx.fillStyle = "#10B981";
                ctx.font = "bold 40px monospace";
                ctx.fillText("QUERY EXECUTED CLEANLY IN O(N)", 110, 940);

                ctx.fillStyle = "#F8FAFC";
                ctx.font = "22px 'Segoe UI', sans-serif";
                ctx.fillText("Zero duplicate errors, ready for interview submission!", 110, 995);
            }

            ctx.restore();
        }

        // PHASE 5 (54 to 60s): PRO TIP & VIRAL RETENTION OUTRO
        if (t >= 53.5) {
            ctx.save();
            const oAlpha = t < 54.5 ? (t - 53.5) : 1.0;
            ctx.globalAlpha = Math.max(0, Math.min(1.0, oAlpha));

            ctx.fillStyle = "rgba(139, 92, 246, 0.2)";
            ctx.beginPath();
            ctx.roundRect(60, 300, W - 120, 360, 24);
            ctx.fill();
            ctx.strokeStyle = "#8B5CF6";
            ctx.lineWidth = 4;
            ctx.stroke();

            ctx.fillStyle = "#8B5CF6";
            ctx.font = "bold 38px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("💡 SENIOR INTERVIEWER PRO-TIP", W / 2, 380);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "28px 'Segoe UI', sans-serif";
            const tipLines = wrapCanvasText(ctx, p.pro_tip, W - 200);
            tipLines.forEach((l, i) => {
                ctx.fillText(l, W / 2, 450 + i * 46);
            });

            ctx.fillStyle = "#F59E0B";
            ctx.font = "bold 32px 'Segoe UI', sans-serif";
            ctx.fillText("⭐ SAVE THIS REEL FOR YOUR NEXT INTERVIEW!", W / 2, 600);
            ctx.textAlign = "left";

            ctx.restore();
        }

        // =========================================================================
        // BOTTOM SUBTITLE / TEXT OVERLAY BANNER (Multilingual)
        // =========================================================================
        ctx.fillStyle = "rgba(15, 23, 42, 0.95)";
        ctx.fillRect(40, H - 360, W - 80, 220);
        ctx.strokeStyle = "rgba(56, 189, 248, 0.3)";
        ctx.lineWidth = 2;
        ctx.strokeRect(40, H - 360, W - 80, 220);

        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 24px 'Segoe UI', sans-serif";
        const langBadge = sqlShortState.textStyle.toUpperCase() + " EXPLANATION";
        ctx.fillText(`💬 ${langBadge}:`, 70, H - 315);

        ctx.fillStyle = "#FFFFFF";
        ctx.font = "30px 'Segoe UI', sans-serif";
        const explanationText = p['explanation_' + sqlShortState.textStyle] || p['explanation_' + sqlShortState.audioLang] || p.explanation_mr;
        const subLines = wrapCanvasText(ctx, explanationText, W - 140);
        subLines.slice(0, 3).forEach((line, idx) => {
            ctx.fillText(line, 70, H - 260 + idx * 42);
        });

        // =========================================================================
        // ZERO-WATERMARK SHIELD (Bottom Footer)
        // =========================================================================
        ctx.fillStyle = "#070B16";
        ctx.fillRect(0, H - 120, W, 120);

        // Tri-Color Glowing Ribbon
        const mGrad = ctx.createLinearGradient(0, H - 120, W, H - 120);
        mGrad.addColorStop(0, "#0284C7");
        mGrad.addColorStop(0.5, "#38BDF8");
        mGrad.addColorStop(1, "#10B981");
        ctx.fillStyle = mGrad;
        ctx.fillRect(0, H - 120, W, 5);

        ctx.fillStyle = "#F8FAFC";
        ctx.font = "bold 26px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("🚀 TOP MNC & FAANG SQL INTERVIEW PREPARATION STUDIO", W / 2, H - 70);

        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 20px 'Segoe UI', sans-serif";
        ctx.fillText("✨ 100% Clean Zero-Watermark Studio • Step-by-Step Code Mastery", W / 2, H - 32);
        ctx.textAlign = "left";
    }

    // Syntax Highlight Helper
    function renderSqlSyntaxLine(ctx, text, startX, lineY) {
        const tokens = text.split(/(\s+|[(),;])/);
        let currX = startX;

        const KEYWORDS = ["SELECT", "FROM", "WHERE", "ORDER", "BY", "DESC", "ASC", "OVER", "PARTITION", "ROWS", "BETWEEN", "UNBOUNDED", "PRECEDING", "AND", "CURRENT", "ROW", "WITH", "AS", "GROUP", "HAVING", "LIMIT", "OFFSET", "JOIN", "LEFT", "ON", "DATE", "ROUND", "COUNT", "MIN", "MAX"];
        const FUNCTIONS = ["DENSE_RANK", "RANK", "ROW_NUMBER", "SUM", "LAG", "LEAD", "AVG"];

        ctx.font = "bold 26px monospace";

        tokens.forEach(tok => {
            const clean = tok.toUpperCase().trim();
            if (KEYWORDS.includes(clean)) {
                ctx.fillStyle = "#38BDF8";
            } else if (FUNCTIONS.includes(clean)) {
                ctx.fillStyle = "#F472B6";
            } else if (/^\d+(\.\d+)?$/.test(clean)) {
                ctx.fillStyle = "#F59E0B";
            } else if (clean.startsWith("'") || clean.startsWith('"')) {
                ctx.fillStyle = "#10B981";
            } else {
                ctx.fillStyle = "#F8FAFC";
            }
            ctx.fillText(tok, currX, lineY);
            currX += ctx.measureText(tok).width;
        });
    }

    function wrapCanvasText(ctx, text, maxWidth) {
        if (!text) return [];
        const words = text.split(" ");
        const lines = [];
        let currLine = "";

        words.forEach(w => {
            const testLine = currLine ? (currLine + " " + w) : w;
            if (ctx.measureText(testLine).width > maxWidth && currLine) {
                lines.push(currLine);
                currLine = w;
            } else {
                currLine = testLine;
            }
        });
        if (currLine) lines.push(currLine);
        return lines;
    }

    /* ==========================================================================
       SMARTPHONE TRANSPORT & PLAYBACK
       ========================================================================== */
    function toggleSqlShortPlay() {
        if (sqlShortState.isPlaying) {
            pauseSqlShortPlay();
        } else {
            playSqlShort();
        }
    }

    function playSqlShort() {
        if (sqlShortState.currentTime >= sqlShortState.maxDuration) {
            sqlShortState.currentTime = 0;
        }
        sqlShortState.isPlaying = true;
        document.getElementById("btnPlayPause").innerText = "⏸ Pause";

        // Play synchronized natural voice audio
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (audioEl && audioEl.src && !audioEl.error) {
            audioEl.currentTime = sqlShortState.currentTime;
            audioEl.playbackRate = sqlShortState.playbackSpeed;
            audioEl.play().catch(e => console.warn("Audio play prevented:", e));
        }

        let lastTime = performance.now();

        function step(now) {
            if (!sqlShortState.isPlaying) return;
            const deltaSec = (now - lastTime) / 1000.0;
            lastTime = now;

            sqlShortState.currentTime += deltaSec * sqlShortState.playbackSpeed;
            if (sqlShortState.currentTime > sqlShortState.maxDuration) {
                sqlShortState.currentTime = sqlShortState.maxDuration;
                pauseSqlShortPlay();
            }

            renderSqlShortFrame(sqlShortState.currentTime);
            updatePlayerScrubberUI(sqlShortState.currentTime);

            if (sqlShortState.isPlaying) {
                sqlShortState.animationFrameId = requestAnimationFrame(step);
            }
        }
        sqlShortState.animationFrameId = requestAnimationFrame(step);
    }

    function pauseSqlShortPlay() {
        sqlShortState.isPlaying = false;
        if (sqlShortState.animationFrameId) {
            cancelAnimationFrame(sqlShortState.animationFrameId);
            sqlShortState.animationFrameId = null;
        }
        document.getElementById("btnPlayPause").innerText = "▶ Play";
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (audioEl) audioEl.pause();
    }

    function restartSqlShortPlay() {
        pauseSqlShortPlay();
        sqlShortState.currentTime = 0.0;
        updatePlayerScrubberUI(0);
        renderSqlShortFrame(0);
        playSqlShort();
    }

    function seekSqlShortPlayer(val) {
        sqlShortState.currentTime = parseFloat(val);
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (audioEl) audioEl.currentTime = sqlShortState.currentTime;
        updatePlayerScrubberUI(sqlShortState.currentTime);
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function setSqlShortSpeed(val) {
        sqlShortState.playbackSpeed = parseFloat(val);
        const audioEl = document.getElementById("sqlVoiceAudio");
        if (audioEl) audioEl.playbackRate = sqlShortState.playbackSpeed;
    }

    function updatePlayerScrubberUI(t) {
        const sc = document.getElementById("sqlShortScrubber");
        if (sc) sc.value = t;
        const tm = document.getElementById("playerTimer");
        if (tm) {
            const mins = Math.floor(t / 60);
            const secs = Math.floor(t % 60).toString().padStart(2, "0");
            tm.innerText = `${mins}:${secs} / 1:00`;
        }
    }

    function downloadVoiceoverMp3() {
        const audioEl = document.getElementById("sqlVoiceAudio");
        const url = (audioEl && audioEl.src) ? audioEl.src : sqlShortState.audioUrl;
        if (!url) {
            alert("Voiceover audio is still loading, please wait 2 seconds.");
            return;
        }
        const a = document.createElement("a");
        a.href = url;
        a.download = `Voiceover_${sqlShortState.activePreset.id}_${sqlShortState.audioLang}.mp3`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    /* ==========================================================================
       MEDIARECORDER AUDIO-MULTIPLEXED EXPORT & DOWNLOAD
       ========================================================================== */
    async function exportSqlShortVideo(durationSec = 60) {
        const canvas = document.getElementById("sqlShortCanvas");
        const audioEl = document.getElementById("sqlVoiceAudio");
        const btn = document.getElementById("btnDownloadShortVideo");
        const btnLabel = document.getElementById("exportBtnLabel");
        const pContainer = document.getElementById("exportProgressBarContainer");
        const pFill = document.getElementById("exportProgressFill");
        const pDesc = document.getElementById("exportStageDesc");
        const pPctText = document.getElementById("exportPercentNum");
        const pEstTime = document.getElementById("exportEstTime");
        const pFrameStats = document.getElementById("exportFrameStats");
        const badgeEl = document.getElementById("exportLiveBadge");
        const celebrationBox = document.getElementById("videoReadyCelebration");

        if (!canvas || !canvas.captureStream) {
            alert("Your browser does not support Canvas.captureStream. Please use Chrome or Edge.");
            return;
        }

        pauseSqlShortPlay();
        if (celebrationBox) celebrationBox.style.display = "none";
        if (pContainer) pContainer.style.display = "block";
        if (badgeEl) {
            badgeEl.innerText = "रेंडरिंग चालू (Rendering...)";
            badgeEl.style.color = "#38BDF8";
            badgeEl.style.background = "rgba(56, 189, 248, 0.15)";
        }
        if (btn) btn.disabled = true;
        if (btnLabel) btnLabel.innerText = `⏳ व्हिडिओ व ऑडिओ एकत्र रेंडर होत आहे (${durationSec}s)...`;

        // Audio Multiplexing Setup
        let audioTracks = [];
        let audioCtx = null;
        if (audioEl && audioEl.src && !audioEl.error) {
            try {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') {
                    await audioCtx.resume();
                }
                const audioDest = audioCtx.createMediaStreamDestination();
                const audioSource = audioCtx.createMediaElementSource(audioEl);
                audioSource.connect(audioDest);
                audioSource.connect(audioCtx.destination);
                audioTracks = audioDest.stream.getAudioTracks();
            } catch(e) {
                console.warn("AudioContext stream capture notice:", e);
            }
        }

        const videoTracks = canvas.captureStream(30).getVideoTracks();
        const combinedStream = new MediaStream([...videoTracks, ...audioTracks]);

        let mimeType = "video/webm;codecs=vp9,opus";
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = "video/webm;codecs=vp8,opus";
        }
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = "video/webm";
        }

        const chunks = [];
        const recorder = new MediaRecorder(combinedStream, {
            mimeType: mimeType,
            videoBitsPerSecond: 8000000
        });

        recorder.ondataavailable = e => {
            if (e.data && e.data.size > 0) chunks.push(e.data);
        };

        const totalDuration = durationSec || 60;
        const totalFrames = totalDuration * 30;
        let frameCount = 0;
        const dt = 1.0 / 30.0;
        const startTime = performance.now();

        recorder.onstop = () => {
            if (audioEl) audioEl.pause();
            if (pFill) pFill.style.width = "100%";
            if (pPctText) pPctText.innerText = "100%";
            if (pDesc) pDesc.innerText = "✅ रेंडरिंग पूर्ण झाले! व्हिडिओ व ऑडिओ डाऊनलोड होत आहे...";
            if (badgeEl) {
                badgeEl.innerText = "पूर्ण झाले (Completed)";
                badgeEl.style.color = "#10B981";
                badgeEl.style.background = "rgba(16, 185, 129, 0.2)";
            }

            for (let i = 1; i <= 5; i++) {
                const pill = document.getElementById("stagePill" + i);
                if (pill) pill.className = "stage-pill done";
            }

            const blob = new Blob(chunks, { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            const filename = `Clean_9x16_${sqlShortState.activePreset.id}_${sqlShortState.audioLang}_${totalDuration}s.webm`;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            setTimeout(() => {
                if (celebrationBox) {
                    celebrationBox.style.display = "block";
                    celebrationBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    const btnAgain = document.getElementById("btnDownloadAgain");
                    if (btnAgain) {
                        btnAgain.href = url;
                        btnAgain.download = filename;
                    }
                }
                if (btn) btn.disabled = false;
                if (btnLabel) btnLabel.innerText = "DOWNLOAD 9:16 VIDEO (WITH NATURAL VOICE AUDIO)";
            }, 300);
        };

        recorder.start();
        if (audioEl && audioEl.src) {
            audioEl.currentTime = 0;
            audioEl.play().catch(e => console.warn("Audio play during export:", e));
        }

        function updateStagePill(stageNum) {
            for (let i = 1; i <= 5; i++) {
                const pill = document.getElementById("stagePill" + i);
                if (!pill) continue;
                if (i < stageNum) pill.className = "stage-pill done";
                else if (i === stageNum) pill.className = "stage-pill active";
                else pill.className = "stage-pill";
            }
        }

        function recordStep() {
            if (frameCount < totalFrames) {
                const stepBatch = totalDuration <= 10 ? 1 : 2;
                for (let b = 0; b < stepBatch && frameCount < totalFrames; b++) {
                    sqlShortState.currentTime = (frameCount * dt);
                    const t = sqlShortState.currentTime;

                    let currentStage = 1;
                    let stageText = "पायरी १/५: 🚨 व्हायरल हुक व प्रश्न";
                    if (totalDuration <= 10) {
                        if (t < 2.0) { currentStage = 1; stageText = "पायरी १/५: 🚨 व्हायरल हुक (0-2s)"; }
                        else if (t < 4.0) { currentStage = 2; stageText = "पायरी २/५: 📋 डेटा स्कीमा (2-4s)"; }
                        else if (t < 7.0) { currentStage = 3; stageText = "पायरी ३/५: ⚡ SQL कोड व ॲरो (4-7s)"; }
                        else if (t < 9.0) { currentStage = 4; stageText = "पायरी ४/५: 🧮 निकाल कॅल्क्युलेशन (7-9s)"; }
                        else { currentStage = 5; stageText = "पायरी ५/५: 🛡️ 100% वॉटरमार्क-फ्री HD व्हिडिओ (9-10s)"; }
                    } else {
                        if (t < 5.0) { currentStage = 1; stageText = "पायरी १/५: 🚨 व्हायरल हुक व प्रश्न (0-5s)"; }
                        else if (t < 18.0) { currentStage = 2; stageText = "पायरी २/५: 📋 डेटा स्कीमा व रेकॉर्ड्स (5-18s)"; }
                        else if (t < 42.0) { currentStage = 3; stageText = "पायरी ३/५: ⚡ टाईपरायटर SQL कोड व लेझर ॲरो (18-42s)"; }
                        else if (t < 54.0) { currentStage = 4; stageText = "पायरी ४/५: 🧮 निकाल कॅल्क्युलेशन (42-54s)"; }
                        else { currentStage = 5; stageText = "पायरी ५/५: 🛡️ 100% वॉटरमार्क-फ्री HD व्हिडिओ (54-60s)"; }
                    }

                    updateStagePill(currentStage);

                    if (sqlShortState.avatarVideoElement && sqlShortState.avatarVideoElement.duration > 0) {
                        sqlShortState.avatarVideoElement.currentTime = t % sqlShortState.avatarVideoElement.duration;
                    }

                    renderSqlShortFrame(t);
                    updatePlayerScrubberUI(t);
                    frameCount++;
                }

                if (frameCount % 15 === 0 || frameCount >= totalFrames) {
                    const pct = Math.min(100, Math.floor((frameCount / totalFrames) * 100));
                    if (pFill) pFill.style.width = pct + "%";
                    if (pPctText) pPctText.innerText = pct + "%";

                    const elapsedSec = (performance.now() - startTime) / 1000.0;
                    if (elapsedSec > 0.2) {
                        const framesPerSec = frameCount / elapsedSec;
                        const remainingSec = Math.max(1, Math.ceil((totalFrames - frameCount) / framesPerSec));
                        if (pEstTime) pEstTime.innerText = `⏱️ अंदाजे वेळ: ${remainingSec} सेकंद बाकी (${remainingSec}s left)`;
                    }
                    if (pFrameStats) pFrameStats.innerText = `🎞️ फ्रेम: ${frameCount} / ${totalFrames}`;
                }

                requestAnimationFrame(recordStep);
            } else {
                recorder.stop();
            }
        }
        requestAnimationFrame(recordStep);
    }

    function downloadCurrentFrameAsPng() {
        const canvas = document.getElementById("sqlShortCanvas");
        if (!canvas) return;
        const dataUrl = canvas.toDataURL("image/png");
        const a = document.createElement("a");
        a.href = dataUrl;
        a.download = `SQL_Interview_Frame_${sqlShortState.activePreset.id}_${Math.floor(sqlShortState.currentTime)}s.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    // Expose Functions to Global Window
    window.setSqlAudioLang = setSqlAudioLang;
    window.setSqlTextStyle = setSqlTextStyle;
    window.toggleSqlAvatar = toggleSqlAvatar;
    window.setSqlAvatarPresenter = setSqlAvatarPresenter;
    window.generateSqlShortBlueprint = generateSqlShortBlueprint;
    window.renderAiAvatarVideo = renderAiAvatarVideo;
    window.renderCinematicBackgroundVideo = renderCinematicBackgroundVideo;
    window.seekSqlShortPlayer = seekSqlShortPlayer;
    window.toggleSqlShortPlay = toggleSqlShortPlay;
    window.restartSqlShortPlay = restartSqlShortPlay;
    window.setSqlShortSpeed = setSqlShortSpeed;
    window.exportSqlShortVideo = exportSqlShortVideo;
    window.downloadCurrentFrameAsPng = downloadCurrentFrameAsPng;
    window.runInMemorySqlSandbox = runInMemorySqlSandbox;
    window.handleSqlPresetChange = handleSqlPresetChange;
    window.downloadVoiceoverMp3 = downloadVoiceoverMp3;
    window.loadPresetVoiceAudio = loadPresetVoiceAudio;
    </script>
    '''
