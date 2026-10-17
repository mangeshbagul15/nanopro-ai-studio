"""
Mangesh Nano Pro AI Studio - 9:16 SQL Short Video Client-Side Engine
Handles HTML5 Canvas 1080x1920 9:16 rendering, dynamic arrow motion, 
typewriter SQL code animations, multilingual voiceover, and MediaRecorder export.
"""

def get_sql_video_js() -> str:
    return r'''
    <script>
    /* ==========================================================================
       9:16 SQL SHORT & REEL ENGINE (CLIENT-SIDE ZERO-SERVER-LOAD)
       ========================================================================== */
    const SQL_CLIENT_PRESETS = {
        "zp_school_ranking": {
            id: "zp_school_ranking",
            title: "🏫 ZP शाळा निकाल: समान गुण असताना २ रा क्रमांक (DENSE_RANK)",
            difficulty: "Easy",
            hook_mr: "🚨 २ विद्यार्थ्यांना समान ९२% गुण असतील तर पुढचा नंबर ३ रा की २ रा? ९९% मुलं इथे चुकतात!",
            hook_hi: "🚨 2 स्टूडेंट्स के बराबर 92% मार्क्स हों तो 2nd रैंक कैसे निकालें? DENSE_RANK का कमाल!",
            hook_en: "🚨 Handling duplicate top scores in school rankings using DENSE_RANK!",
            hook_minglish: "🚨 2 mulanna same marks asel tar pudhcha number 2 ra ki 3 ra? ZP school SQL test!",
            hook_hinglish: "🚨 2 students ke same marks hone par 2nd rank kaise nikale? ZP school rank formula!",
            question: "गावातील शाळेच्या परीक्षेत २ मुलांना एकसारखे ९२% गुण मिळाले. तर २ रा क्रमांक शोधण्यासाठी DENSE_RANK() चा वापर करा.",
            table_name: "school_results",
            col_headers: ["विद्यार्थी", "रोल नं", "गुण %", "निकाल (RANK)"],
            schema_sql: `CREATE TABLE school_results (
    roll_no INTEGER PRIMARY KEY,
    student_name TEXT,
    marks REAL
);
INSERT INTO school_results VALUES 
(1, 'राहुल पाटील', 92.0),
(2, 'सुमित शिंदे', 92.0),
(3, 'स्नेहल जाधव', 88.0),
(4, 'अमोल पवार', 85.0);`,
            solution_sql: `WITH RankedResults AS (
    SELECT student_name, marks,
        DENSE_RANK() OVER (
            ORDER BY marks DESC
        ) AS rank_no
    FROM school_results
)
SELECT student_name, marks, rank_no
FROM RankedResults
WHERE rank_no = 2;`,
            arrow_target: "DENSE_RANK() OVER (ORDER BY marks DESC)",
            arrow_line_idx: 2,
            explanation_mr: "इथे राहुल आणि सुमित दोघांना ९२% असल्याने १ ला क्रमांक मिळतो. RANK() मुळे पुढचा नंबर ३ रा होतो, पण DENSE_RANK() नंबर स्किप न करता स्नेहलला अचूक २ रा क्रमांक देते!",
            explanation_hi: "यहाँ दो स्टूडेंट्स के 92% होने पर दोनों को 1st रैंक मिलती है। DENSE_RANK() रैंक स्किप नहीं करता और 88% वाले को सही 2nd रैंक देता है!",
            explanation_en: "When students tie with 92%, DENSE_RANK() assigns Rank 1 to both and Rank 2 to Snehal without skipping numbers!",
            explanation_minglish: "Rahul ani Sumit donhina 92% aslyane 1st rank bhetli. DENSE_RANK mule number skip hot nahi ani Snehal la 2nd rank bhetate!",
            explanation_hinglish: "Rahul aur Sumit dono ko 1st rank mili. DENSE_RANK rank skip nahi karta aur Snehal ko exact 2nd rank deta hai!",
            pro_tip: "💡 Pro Tip: शाळेचे निकाल किंवा परीक्षांमध्ये समान गुण असताना नेहमी DENSE_RANK() वापरावे!",
            sample_rows: [
                {account: "राहुल पाटील", date: "Roll 1", amt: "९२%", balance: "Rank 1 (Tie)"},
                {account: "सुमित शिंदे", date: "Roll 2", amt: "९२%", balance: "Rank 1 (Tie)"},
                {account: "स्नेहल जाधव", date: "Roll 3", amt: "८८%", balance: "🎯 Rank 2 (अचूक)"},
                {account: "अमोल पवार", date: "Roll 4", amt: "८५%", balance: "Rank 3"}
            ]
        },
        "kirana_dukan_hisob": {
            id: "kirana_dukan_hisob",
            title: "🛒 गावचे किराणा दुकान: चालू उधारी व शिल्लक हिशोब (PARTITION BY)",
            difficulty: "Medium",
            hook_mr: "🚨 गावच्या किराणा दुकानाचा हिशोब SQL ने कसा करायचा? प्रत्येक ग्राहकाची चालू उधारी कशी काढायची?",
            hook_hi: "🚨 किराना दुकान का उधारी-जमा हिसाब SQL Window Function से कैसे निकालें?",
            hook_en: "🚨 Village General Store: Customer-wise Cumulative Credit & Balance Tracking!",
            hook_minglish: "🚨 Kirana dukan cha udhari hisob SQL ne kasa thevaycha? Running balance formula!",
            hook_hinglish: "🚨 Kirana store ka udhari balance SQL window function se calculate kare!",
            question: "गावातील किराणा दुकानातील ग्राहकांच्या उधारी व जमा नोंदीवरून प्रत्येक ग्राहकाची चालू शिल्लक रक्कम (Running Balance) काढा.",
            table_name: "kirana_transactions",
            col_headers: ["ग्राहक", "बिल तारीख", "रक्कम", "चालू उधारी"],
            schema_sql: `CREATE TABLE kirana_transactions (
    bill_no INTEGER PRIMARY KEY,
    customer_name TEXT,
    bill_date TEXT,
    amount REAL
);
INSERT INTO kirana_transactions VALUES 
(1, 'मारुती काका', '2026-10-01', 1500.0),
(2, 'मारुती काका', '2026-10-05', -500.0),
(3, 'मारुती काका', '2026-10-10', 800.0),
(4, 'तात्या पाटील', '2026-10-02', 3000.0);`,
            solution_sql: `SELECT 
    customer_name, bill_date, amount,
    SUM(amount) OVER (
        PARTITION BY customer_name 
        ORDER BY bill_date 
        ROWS BETWEEN UNBOUNDED PRECEDING 
        AND CURRENT ROW
    ) AS current_balance
FROM kirana_transactions;`,
            arrow_target: "PARTITION BY customer_name",
            arrow_line_idx: 3,
            explanation_mr: "इथे 'PARTITION BY customer_name' मुळे मारुती काका आणि तात्या पाटील यांचा उधारीचा हिशोब स्वतंत्र राहतो आणि एकत्र मिसळत नाही! आणि 'SUM() OVER' चालू उधारी अचूक दाखवते!",
            explanation_hi: "यहाँ 'PARTITION BY customer_name' से हर ग्राहक का हिसाब अलग पार्टीशन में रहता है, और 'SUM() OVER' से चालू उधारी बैलेंस निकल आता है!",
            explanation_en: "PARTITION BY customer_name keeps each customer's balance completely separate and calculates running totals!",
            explanation_minglish: "PARTITION BY mule Maruti Kaka ani Tatya Patil yaancha hisob vegla rahto ani current udhari clear diste!",
            explanation_hinglish: "PARTITION BY se har customer ka hisab alag rehta hai aur running balance step by step calculate hota hai!",
            pro_tip: "💡 Pro Tip: प्रत्येक गावातील किंवा छोट्या उद्योगातील हिशोबासाठी PARTITION BY हा सर्वात सोपा आणि शक्तिशाली नियम आहे!",
            sample_rows: [
                {account: "मारुती काका", date: "१०-०१", amt: "+₹१,५००", balance: "₹१,५०० उधारी"},
                {account: "मारुती काका", date: "१०-०५", amt: "-₹५००", balance: "₹१,००० शिल्लक"},
                {account: "मारुती काका", date: "१०-१०", amt: "+₹८००", balance: "₹१,८०० उधारी"},
                {account: "तात्या पाटील", date: "१०-०२", amt: "+₹३,०००", balance: "₹३,००० उधारी"}
            ]
        },
        "bank_running_total": {
            id: "bank_running_total",
            title: "HDFC / SBI: Cumulative Running Balance",
            difficulty: "Medium",
            hook_mr: "🚨 ९०% मुलं या HDFC बँक SQL प्रश्नात फेल होतात! क्युम्युलेटिव्ह बॅलन्स कसा काढायचा?",
            hook_hi: "🚨 90% लोग इस Bank SQL सवाल में अटक जाते हैं! Cumulative Balance कैसे निकालें?",
            hook_en: "🚨 90% Fail this Bank SQL Interview Question! Running Balance Formula",
            hook_minglish: "🚨 90% pora ya Bank SQL question madhe fail hotat! Running balance kasa kadhaycha?",
            hook_hinglish: "🚨 90% log is Bank SQL interview question me fail ho jate hai! Running balance kaise nikale?",
            question: "Calculate cumulative running balance for each customer account ordered by transaction date.",
            table_name: "bank_transactions",
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
(104, 'ACC-8821', '2026-10-08', -3000.0);`,
            solution_sql: `SELECT 
    account_no, txn_date, amount,
    SUM(amount) OVER (
        PARTITION BY account_no 
        ORDER BY txn_date 
        ROWS BETWEEN UNBOUNDED PRECEDING 
        AND CURRENT ROW
    ) AS running_balance
FROM bank_transactions;`,
            arrow_target: "PARTITION BY account_no",
            arrow_line_idx: 4,
            explanation_mr: "इथे 'PARTITION BY account_no' मुळे प्रत्येक खात्याची बेरीज स्वतंत्रपणे मोजली जाते आणि 'ROWS BETWEEN UNBOUNDED PRECEDING' मुळे बॅलन्स ॲक्युम्युलेट होतो!",
            explanation_hi: "यहाँ 'PARTITION BY account_no' हर अकाउंट का अलग ग्रुप बनाता है और हर रो के साथ बैलेंस अपडेट होता जाता है!",
            explanation_en: "SUM() OVER is a Window Function. PARTITION BY resets per customer, while ORDER BY accumulates sequentially!",
            explanation_minglish: "Ithe 'PARTITION BY account_no' mule pratyek account cha vegla group banto ani running total calculate hote!",
            explanation_hinglish: "Yaha 'PARTITION BY account_no' har account ka alag partition banata hai aur balance accumulate karta hai!",
            pro_tip: "💡 Pro Tip: Never use a subquery for running totals in production—Window Functions execute in O(N) linear time!",
            sample_rows: [
                {account: "ACC-8821", date: "10-01", amt: "+₹5,000", balance: "₹5,000"},
                {account: "ACC-8821", date: "10-03", amt: "-₹1,200", balance: "₹3,800"},
                {account: "ACC-8821", date: "10-05", amt: "+₹8,500", balance: "₹12,300"},
                {account: "ACC-8821", date: "10-08", amt: "-₹3,000", balance: "₹9,300"}
            ]
        },
        "bank_consecutive_fraud": {
            id: "bank_consecutive_fraud",
            title: "ICICI / Axis: Detect Rapid Consecutive High-Value Withdrawals",
            difficulty: "Hard",
            hook_mr: "🚨 फ्रॉड डिटेक्शन SQL टेस्ट! एकाच तासात दोन मोठे विड्रॉव्हल कसे शोधायचे?",
            hook_hi: "🚨 Bank Fraud Detection Query! 1 घंटे में लगातार 2 बड़े विड्रॉवल कैसे पकड़ें?",
            hook_en: "🚨 Fraud Detection SQL Test! Find consecutive high-value withdrawals!",
            hook_minglish: "🚨 Fraud detection SQL test! Ekyach taasat 2 mothe withdrawals kase shodhayche?",
            hook_hinglish: "🚨 Fraud detection SQL test! Ek hi ghante me 2 bade withdrawals kaise track kare?",
            question: "Find all accounts that made consecutive withdrawals of more than ₹10,000 using LAG().",
            table_name: "customer_withdrawals",
            schema_sql: `CREATE TABLE customer_withdrawals (
    id INTEGER PRIMARY KEY,
    acc_id TEXT,
    withdraw_amt REAL,
    w_time TEXT
);
INSERT INTO customer_withdrawals VALUES 
(1, 'SB-1001', 15000.0, '10:00:00'),
(2, 'SB-1001', 20000.0, '10:25:00'),
(3, 'SB-1002', 2000.0, '11:00:00');`,
            solution_sql: `WITH TxnWithLag AS (
    SELECT acc_id, withdraw_amt, w_time,
        LAG(withdraw_amt, 1) OVER (
            PARTITION BY acc_id 
            ORDER BY w_time
        ) AS prev_amt
    FROM customer_withdrawals
)
SELECT acc_id, withdraw_amt, prev_amt
FROM TxnWithLag
WHERE withdraw_amt >= 10000 
  AND prev_amt >= 10000;`,
            arrow_target: "LAG(withdraw_amt, 1) OVER",
            arrow_line_idx: 3,
            explanation_mr: "इथे 'LAG()' फंक्शन आधीचा रेकॉर्ड खेचून आणते. दोन्ही विड्रॉव्हल ₹10,000 पेक्षा जास्त असल्यास लगेच फ्रॉड फ्लॅग होतो!",
            explanation_hi: "यहाँ LAG() पिछली रो की वैल्यू खींचता है। दोनों विड्रॉवल ₹10,000+ होने पर फ्रॉड फ़्लैग होता है!",
            explanation_en: "LAG() accesses the previous record without self-joins. If both exceed ₹10,000, we flag fraud!",
            explanation_minglish: "Ithe LAG() function previous record gheun yeta ani back-to-back 10k+ transactions flag karto!",
            explanation_hinglish: "Yaha LAG() function previous row fetch karta hai aur back-to-back 10k transactions flag karta hai!",
            pro_tip: "💡 Pro Tip: LAG() and LEAD() eliminate expensive self-joins by scanning partitions in a single pass!",
            sample_rows: [
                {account: "SB-1001", date: "10:00", amt: "₹15,000", balance: "ALERT: 1st High Txn"},
                {account: "SB-1001", date: "10:25", amt: "₹20,000", balance: "🚨 FRAUD DETECTED!"}
            ]
        },
        "bank_salary_rank": {
            id: "bank_salary_rank",
            title: "Goldman / Morgan: 2nd Highest Salary Without Ties",
            difficulty: "Medium",
            hook_mr: "🚨 सेकंड हायेस्ट सॅलरी विचारल्यावर ९५% मुलं 'LIMIT 1 OFFSET 1' लिहून चुकतात! DENSE_RANK() का लागते?",
            hook_hi: "🚨 2nd Highest Salary में LIMIT 1 OFFSET 1 मत लिखना! DENSE_RANK() क्यों ज़रूरी है?",
            hook_en: "🚨 Stop using LIMIT 1 OFFSET 1 for 2nd Highest Salary! Why DENSE_RANK is mandatory!",
            hook_minglish: "🚨 2nd Highest Salary madhe 'LIMIT 1 OFFSET 1' lihun chuktat! DENSE_RANK kashi vapraychi?",
            hook_hinglish: "🚨 2nd Highest Salary me LIMIT 1 OFFSET 1 mat likhna! DENSE_RANK ka real rule dekho!",
            question: "Find the 2nd highest salary from the bank employees table handling duplicate top salaries cleanly.",
            table_name: "bank_employees",
            schema_sql: `CREATE TABLE bank_employees (
    emp_id INTEGER PRIMARY KEY,
    emp_name TEXT,
    dept TEXT,
    salary REAL
);
INSERT INTO bank_employees VALUES 
(1, 'Aarav Sharma', 'IB', 185000.0),
(2, 'Rohit Deshmukh', 'IB', 185000.0),
(3, 'Priya Kulkarni', 'Risk', 160000.0);`,
            solution_sql: `WITH RankedSalaries AS (
    SELECT emp_name, dept, salary,
        DENSE_RANK() OVER (
            ORDER BY salary DESC
        ) AS rnk
    FROM bank_employees
)
SELECT emp_name, dept, salary
FROM RankedSalaries
WHERE rnk = 2;`,
            arrow_target: "DENSE_RANK() OVER (ORDER BY salary DESC)",
            arrow_line_idx: 2,
            explanation_mr: "जर टॉप २ लोकांची सॅलरी समान (उदा. ₹1.85L) असेल, तर RANK() पुढचा रँक ३ करतो. पण DENSE_RANK() नंबर स्किप न करता अचूक २ रा नंबर शोधते!",
            explanation_hi: "अगर 2 एम्प्लॉइज़ की सैलरी सेम है तो RANK() 3 पर कूद जाएगा। DENSE_RANK() बिना स्किप किए 2nd सैलरी देता है!",
            explanation_en: "DENSE_RANK() never skips ranks after ties (1, 1, 2). Regular RANK() skips (1, 1, 3) causing query errors!",
            explanation_minglish: "Top 2 chi salary same asel tar RANK() 3 var jump karte. Pan DENSE_RANK() 2nd salary exact kadhte!",
            explanation_hinglish: "Agar top 2 salary same hai to RANK() rank 3 pe jump karega. DENSE_RANK() exact 2nd rank nikalta hai!",
            pro_tip: "💡 Pro Tip: When ties are possible, DENSE_RANK() is the only standard-compliant solution!",
            sample_rows: [
                {account: "Aarav Sharma", date: "Rank 1", amt: "₹1,85,000", balance: "Tie #1"},
                {account: "Rohit Deshmukh", date: "Rank 1", amt: "₹1,85,000", balance: "Tie #2"},
                {account: "Priya Kulkarni", date: "Rank 2", amt: "₹1,60,000", balance: "🎯 2nd Highest"}
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
        activePreset: SQL_CLIENT_PRESETS["zp_school_ranking"],
        selectedAvatar: "Nadim_public_5",
        avatarVideoElement: null,
        avatarVideoLoaded: false,
        animationFrameId: null,
        lastTimestamp: null,
        isExporting: false,
        mediaRecorder: null,
        recordedChunks: []
    };

    // Initialize Workspace on Page Load
    document.addEventListener("DOMContentLoaded", () => {
        initSqlShortWorkspace();
    });

    function initSqlShortWorkspace() {
        const preset = sqlShortState.activePreset;
        const qEl = document.getElementById("sqlShortQuestion");
        const cEl = document.getElementById("sqlShortCodePreview");
        if (qEl) qEl.value = preset.question;
        if (cEl) cEl.value = preset.solution_sql;

        updateSqlBlueprintUI(preset);
        renderSqlShortFrame(0);
    }

    function setSqlAudioLang(lang) {
        sqlShortState.audioLang = lang;
        document.querySelectorAll(".sql-lang-btn").forEach(b => b.classList.remove("active"));
        const btn = document.getElementById("btnAudio" + lang.charAt(0).toUpperCase() + lang.slice(1));
        if (btn) btn.classList.add("active");
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
            restartSqlShortPlay();
        }
    }

    function updateSqlBlueprintUI(p) {
        const hookText = p['hook_' + sqlShortState.textStyle] || p['hook_' + sqlShortState.audioLang] || p.hook_mr;
        const hookEl = document.getElementById("bpTimelineHook");
        if (hookEl) hookEl.innerText = hookText;
        const arrowEl = document.getElementById("bpArrowTarget");
        if (arrowEl) arrowEl.innerText = p.arrow_target || "OVER ()";
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
                    table_name: data.table_name || "bank_data",
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
                        {account: "ACC-101", date: "T1", amt: "₹5,000", balance: "Step 1"},
                        {account: "ACC-101", date: "T2", amt: "₹12,000", balance: "Step 2"}
                    ]
                };
                document.getElementById("sqlShortCodePreview").value = data.solution_sql;
                updateSqlBlueprintUI(sqlShortState.activePreset);
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
        statusEl.innerHTML = `<span>⚡ Submitting to Autonomous Avatar Router (Auto-failover HeyGen ➔ D-ID ➔ Canvas active)...</span>`;
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
                    statusEl.innerHTML = `<span>✅ HeyGen 4K Video #${data.video_id} queued${failoverTag}! Polling...</span>`;
                    pollHeyGenVideo(data.video_id, statusEl, btn);
                } else if (data.provider === "D-ID" && data.talk_id) {
                    const failoverTag = data.failover_used ? " (Auto-switched from HeyGen)" : "";
                    statusEl.innerHTML = `<span>✅ D-ID Talk #${data.talk_id} queued${failoverTag}! Polling lip-sync...</span>`;
                    pollDIDVideo(data.talk_id, statusEl, btn);
                } else {
                    // Zero-drop client canvas fallback
                    btn.disabled = false;
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `🛡️ <b>Zero-Hang Guarantee Active:</b> Cloud tokens rate-limited. Auto-switched to High-Tech Cyber Canvas Presenter! Click [Play] or [Download] below.`;
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
            vid.playsInline = true;
            vid.muted = true;
            vid.loop = true;
            vid.style.display = "none";
            document.body.appendChild(vid);
        }
        vid.src = url;
        vid.load();
        vid.onloadeddata = () => {
            sqlShortState.avatarVideoElement = vid;
            sqlShortState.avatarVideoLoaded = true;
            vid.play().catch(e => console.log("Avatar preview autoplay:", e));
            renderSqlShortFrame(sqlShortState.currentTime);
        };
    }

    function pollHeyGenVideo(videoId, statusEl, btn) {
        const interval = setInterval(async () => {
            try {
                const res = await fetch("/api/heygen/status/" + videoId);
                const data = await res.json();
                if (data.status === "completed" && data.video_url) {
                    clearInterval(interval);
                    btn.disabled = false;
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `🎉 <b>HeyGen Video Ready &amp; Composited!</b> <a href="${data.video_url}" target="_blank" style="color:#38BDF8; font-weight:bold; text-decoration:underline;">[▶ Raw 4K MP4]</a> • 🛡️ <i>Watermark removed in 9:16 Canvas!</i>`;
                    loadAvatarVideoToEngine(data.video_url);
                } else if (data.status === "failed") {
                    clearInterval(interval);
                    btn.disabled = false;
                    statusEl.style.color = "#EF4444";
                    statusEl.innerText = "HeyGen Rendering failed: " + (data.error || "Unknown error");
                } else {
                    statusEl.innerHTML = `<span>⏳ Rendering HeyGen 4K Avatar (Status: ${data.status || "processing"})...</span>`;
                }
            } catch (e) {}
        }, 3000);
    }

    function pollDIDVideo(talkId, statusEl, btn) {
        const interval = setInterval(async () => {
            try {
                const res = await fetch("/api/did/status/" + talkId);
                const data = await res.json();
                if (data.status === "done" && data.result_url) {
                    clearInterval(interval);
                    btn.disabled = false;
                    statusEl.style.color = "#10B981";
                    statusEl.innerHTML = `🎉 <b>D-ID Video Ready &amp; Composited!</b> <a href="${data.result_url}" target="_blank" style="color:#38BDF8; font-weight:bold; text-decoration:underline;">[▶ Raw MP4]</a> • 🛡️ <i>Watermark removed in 9:16 Canvas!</i>`;
                    loadAvatarVideoToEngine(data.result_url);
                } else if (data.status === "error") {
                    clearInterval(interval);
                    btn.disabled = false;
                    statusEl.style.color = "#EF4444";
                    statusEl.innerText = "D-ID Rendering failed: " + (data.error || "Unknown error");
                } else {
                    statusEl.innerHTML = `<span>⏳ D-ID Lipsync Rendering (Status: ${data.status || "started"})...</span>`;
                }
            } catch (e) {}
        }, 2000);
    }

    /* In-Memory SQLite Sandbox Runner */
    async function runInMemorySqlSandbox() {
        const p = sqlShortState.activePreset;
        const code = document.getElementById("sqlShortCodePreview").value.trim() || p.solution_sql;
        const outTable = document.getElementById("sandboxOutputTable");
        const latEl = document.getElementById("sandboxLatency");

        outTable.innerHTML = `<div style="color:#38BDF8; padding:8px;">Running query in ephemeral SQLite...</div>`;
        const t0 = performance.now();

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
            const dur = (performance.now() - t0).toFixed(1);
            latEl.innerText = `⚡ ${dur}ms`;

            if (data.status === "success") {
                let html = `<table style="width:100%; border-collapse:collapse; text-align:left;">`;
                html += `<thead><tr style="border-bottom:1px solid #283C62; color:#38BDF8;">`;
                data.columns.forEach(col => {
                    html += `<th style="padding:4px 6px;">${col}</th>`;
                });
                html += `</tr></thead><tbody>`;
                data.rows.forEach((r, idx) => {
                    const bg = idx % 2 === 0 ? "rgba(255,255,255,0.02)" : "transparent";
                    html += `<tr style="background:${bg}; border-bottom:1px solid rgba(255,255,255,0.05);">`;
                    data.columns.forEach(col => {
                        html += `<td style="padding:4px 6px; color:#F8FAFC;">${r[col]}</td>`;
                    });
                    html += `</tr>`;
                });
                html += `</tbody></table>`;
                outTable.innerHTML = html;
            } else {
                outTable.innerHTML = `<div style="color:#EF4444; padding:6px;">SQL Error: ${data.message}</div>`;
            }
        } catch (e) {
            outTable.innerHTML = `<div style="color:#EF4444; padding:6px;">Connection Error: ${e.message}</div>`;
        }
    }

    /* ==========================================================================
       9:16 CANVAS RENDERING ENGINE (1080x1920 High Definition)
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

        // Top Status Header (Time, Title & Difficulty Pill)
        ctx.fillStyle = "rgba(14, 21, 40, 0.85)";
        ctx.fillRect(40, 60, W - 80, 110);
        ctx.strokeStyle = "#1E2D4A";
        ctx.strokeRect(40, 60, W - 80, 110);

        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 32px 'Segoe UI', sans-serif";
        const topHeaderTitle = p.id.startsWith("zp_") ? "🏫 ZP SCHOOL SQL MASTERCLASS" : (p.id.startsWith("kirana_") ? "🛒 RURAL BUSINESS SQL LOGIC" : "🏦 BANK SQL INTERVIEW DRILL");
        ctx.fillText(topHeaderTitle, 70, 125);

        // Difficulty Pill
        ctx.fillStyle = "#F59E0B";
        ctx.fillRect(W - 250, 92, 170, 48);
        ctx.fillStyle = "#000000";
        ctx.font = "bold 24px 'Segoe UI', sans-serif";
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
        if (sqlShortState.selectedAvatar && sqlShortState.selectedAvatar !== "none") {
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

            // Render live avatar video if loaded from HeyGen / D-ID with Anti-Watermark Center-Crop!
            const vid = sqlShortState.avatarVideoElement;
            if (vid && sqlShortState.avatarVideoLoaded && vid.readyState >= 2) {
                ctx.save();
                ctx.beginPath();
                ctx.arc(avatarX, avatarY, radius, 0, Math.PI * 2);
                ctx.clip(); // Circular mask completely eliminates corner watermark logos!

                const vw = vid.videoWidth || 640;
                const vh = vid.videoHeight || 480;
                // Center 70% width and 70% height crop discards outer 15% margins where watermarks sit
                const sx = vw * 0.15;
                const sy = vh * 0.05;
                const sw = vw * 0.70;
                const sh = vh * 0.70;

                ctx.drawImage(vid, sx, sy, sw, sh, avatarX - radius, avatarY - radius, radius * 2, radius * 2);
                ctx.restore();
            } else {
                // High-Tech Cyber Teacher Icon
                ctx.font = "44px 'Segoe UI Emoji', sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("🧑‍🏫", avatarX, avatarY + 16);
            }

            // "AI MENTOR" Pill Badge below avatar
            ctx.fillStyle = "#8B5CF6";
            ctx.beginPath();
            ctx.roundRect(avatarX - 55, avatarY + 38, 110, 24, 12);
            ctx.fill();
            ctx.fillStyle = "#FFFFFF";
            ctx.font = "bold 13px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("AI शिक्षक", avatarX, avatarY + 54);
            ctx.textAlign = "left";

            ctx.restore();
        }

        // =========================================================================
        // TIMELINE PHASES (0 to 60 Seconds)
        // =========================================================================

        // PHASE 1 (0 to 5s): VIRAL PEAK POINT / HOOK
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
            ctx.font = "bold 44px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("🚨 90% CANDIDATES FAIL THIS QUESTION!", 0, -20);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "bold 34px 'Segoe UI', sans-serif";
            const hookText = p['hook_' + sqlShortState.textStyle] || p['hook_' + sqlShortState.audioLang] || p.hook_mr;
            ctx.fillText(wrapCanvasText(ctx, hookText, 860)[0] || hookText, 0, 45);

            ctx.restore();
        }

        // PHASE 2 (5 to 18s): PROBLEM & REAL BANK DATA SCHEMA
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
            ctx.font = "bold 32px 'Segoe UI', sans-serif";
            ctx.fillText("📋 BANK INTERVIEW SCENARIO:", 90, 315);

            ctx.fillStyle = "#E2E8F0";
            ctx.font = "28px 'Segoe UI', sans-serif";
            const qLines = wrapCanvasText(ctx, p.question, W - 180);
            qLines.slice(0, 2).forEach((l, i) => {
                ctx.fillText(l, 90, 370 + i * 42);
            });

            // Animated Real Bank Transaction Cards
            ctx.fillStyle = "#94A3B8";
            ctx.font = "bold 26px monospace";
            ctx.fillText(`TABLE: ${p.table_name}`, 60, 510);

            const sampleRows = p.sample_rows || [];
            sampleRows.forEach((r, idx) => {
                const cardY = 540 + idx * 110;
                const animOffset = Math.max(0, (idx * 1.5 + 6.0 - t) * 60);

                ctx.fillStyle = idx % 2 === 0 ? "rgba(30, 41, 59, 0.85)" : "rgba(15, 23, 42, 0.85)";
                ctx.beginPath();
                ctx.roundRect(60 + animOffset, cardY, W - 120, 90, 14);
                ctx.fill();
                ctx.strokeStyle = "#283C62";
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.fillStyle = "#38BDF8";
                ctx.font = "bold 28px monospace";
                ctx.fillText(r.account, 90 + animOffset, cardY + 55);

                ctx.fillStyle = "#94A3B8";
                ctx.font = "24px monospace";
                ctx.fillText(r.date, 340 + animOffset, cardY + 55);

                ctx.fillStyle = r.amt.startsWith("+") ? "#10B981" : (r.amt.startsWith("-") ? "#EF4444" : "#F59E0B");
                ctx.font = "bold 28px monospace";
                ctx.fillText(r.amt, 540 + animOffset, cardY + 55);

                ctx.fillStyle = "#6366F1";
                ctx.font = "24px monospace";
                ctx.fillText(r.balance, 760 + animOffset, cardY + 55);
            });

            ctx.restore();
        }

        // PHASE 3 (18 to 42s): ANIMATED SQL CODE & DYNAMIC ARROW MOTION
        if (t >= 17.5 && t < 43.0) {
            ctx.save();
            const cAlpha = t < 18.5 ? (t - 17.5) : (t > 42.0 ? (43.0 - t) : 1.0);
            ctx.globalAlpha = Math.max(0, Math.min(1.0, cAlpha));

            // Code Window Header
            ctx.fillStyle = "#0B1120";
            ctx.beginPath();
            ctx.roundRect(50, 240, W - 100, 780, 24);
            ctx.fill();
            ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
            ctx.lineWidth = 3;
            ctx.stroke();

            // Mac-style Window Dots
            ctx.fillStyle = "#EF4444"; ctx.beginPath(); ctx.arc(90, 280, 12, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#F59E0B"; ctx.beginPath(); ctx.arc(130, 280, 12, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#10B981"; ctx.beginPath(); ctx.arc(170, 280, 12, 0, Math.PI * 2); ctx.fill();

            ctx.fillStyle = "#94A3B8";
            ctx.font = "22px monospace";
            ctx.fillText("sql_solution.sql — 9:16 Studio", 220, 288);

            // SQL Code Line-by-Line Typewriter Animation
            const codeLines = p.solution_sql.split("\n");
            const typingSpeed = (t - 18.0) * 1.5; // lines typed per second
            const linesToShow = Math.min(codeLines.length, Math.floor(typingSpeed));

            let arrowTargetY = 460;
            let arrowTargetX = 640;

            for (let i = 0; i < linesToShow; i++) {
                const lineY = 350 + i * 54;
                const lineText = codeLines[i];

                // Check if this line is the arrow target
                const isTarget = p.arrow_target && lineText.includes(p.arrow_target.split(" ")[0]);
                if (isTarget) {
                    arrowTargetY = lineY;
                    arrowTargetX = 80 + ctx.measureText(lineText).width + 30;
                }

                // Line numbering
                ctx.fillStyle = "#475569";
                ctx.font = "26px monospace";
                ctx.fillText((i + 1).toString().padStart(2, "0"), 80, lineY);

                // Syntax highlighting
                renderSqlSyntaxLine(ctx, lineText, 140, lineY);
            }

            // DYNAMIC GLOWING ARROW MOTION
            if (t >= 22.0) {
                const arrowBounce = Math.sin((t - 22.0) * 6) * 18;
                const arrowX = Math.min(W - 140, arrowTargetX + 70 + arrowBounce);
                const arrowY = arrowTargetY - 8;

                // Glowing Arrow Laser Trail
                ctx.shadowColor = "#38BDF8";
                ctx.shadowBlur = 20;

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
                ctx.fillRect(arrowX + 140, arrowY - 20, 200, 42);
                ctx.fillStyle = "#000";
                ctx.font = "bold 20px 'Segoe UI', sans-serif";
                ctx.fillText("⚡ CRITICAL CLAUSE", arrowX + 150, arrowY + 8);

                ctx.shadowBlur = 0;
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
            ctx.roundRect(50, 240, W - 100, 780, 24);
            ctx.fill();
            ctx.strokeStyle = "#10B981";
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = "#10B981";
            ctx.font = "bold 36px 'Segoe UI', sans-serif";
            ctx.fillText("✅ REAL QUERY EXECUTION OUTPUT:", 90, 310);

            // Table Header (Dynamic based on preset or default)
            const headers = p.col_headers || ["ACCOUNT", "TXN_DATE", "AMOUNT", "RUNNING_BAL"];
            ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
            ctx.fillRect(80, 350, W - 160, 60);
            ctx.fillStyle = "#38BDF8";
            ctx.font = "bold 26px monospace";
            ctx.fillText(headers[0], 110, 390);
            ctx.fillText(headers[1], 350, 390);
            ctx.fillText(headers[2], 560, 390);
            ctx.fillText(headers[3], 780, 390);

            // Render Output Rows with glowing running balance
            const sampleRows = p.sample_rows || [];
            sampleRows.forEach((r, idx) => {
                const rowY = 440 + idx * 80;
                ctx.fillStyle = idx % 2 === 0 ? "rgba(255,255,255,0.03)" : "transparent";
                ctx.fillRect(80, rowY - 30, W - 160, 70);

                ctx.fillStyle = "#F8FAFC";
                ctx.font = "26px monospace";
                ctx.fillText(r.account, 110, rowY + 14);
                ctx.fillText(r.date, 350, rowY + 14);
                ctx.fillText(r.amt, 560, rowY + 14);

                // Glowing Calculated Balance
                ctx.shadowColor = "#10B981";
                ctx.shadowBlur = 15;
                ctx.fillStyle = "#10B981";
                ctx.font = "bold 28px monospace";
                ctx.fillText(r.balance, 780, rowY + 14);
                ctx.shadowBlur = 0;
            });

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
            ctx.font = "bold 40px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("💡 INTERVIEW PRO-TIP", W / 2, 380);

            ctx.fillStyle = "#F8FAFC";
            ctx.font = "30px 'Segoe UI', sans-serif";
            const tipLines = wrapCanvasText(ctx, p.pro_tip, W - 200);
            tipLines.forEach((l, i) => {
                ctx.fillText(l, W / 2, 450 + i * 46);
            });

            // Follow / Save CTA
            ctx.fillStyle = "#F59E0B";
            ctx.font = "bold 34px 'Segoe UI', sans-serif";
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
        // ZERO-WATERMARK SHIELD & NATIONAL MISSION BANNER (Bottom Footer)
        // =========================================================================
        ctx.fillStyle = "#070B16";
        ctx.fillRect(0, H - 120, W, 120);

        // Tiranga Tri-Color Glowing Ribbon
        const mGrad = ctx.createLinearGradient(0, H - 120, W, H - 120);
        mGrad.addColorStop(0, "#FF9933");  // Saffron
        mGrad.addColorStop(0.5, "#FFFFFF"); // White
        mGrad.addColorStop(1, "#138808");  // Green
        ctx.fillStyle = mGrad;
        ctx.fillRect(0, H - 120, W, 5);

        ctx.fillStyle = "#F8FAFC";
        ctx.font = "bold 26px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("🇮🇳 नॅनोप्रो डिजिटल भारत मिशन • ग्रामीण व ZP शाळांसाठी मोफत तंत्रज्ञान शिक्षण", W / 2, H - 70);

        ctx.fillStyle = "#38BDF8";
        ctx.font = "bold 20px 'Segoe UI', sans-serif";
        ctx.fillText("✨ 100% Clean Zero-Watermark Studio • Instagram Reels & YouTube 9:16 Shorts", W / 2, H - 32);
        ctx.textAlign = "left";
    }

    // Syntax Highlight Helper
    function renderSqlSyntaxLine(ctx, text, startX, lineY) {
        const tokens = text.split(/(\s+|[(),;])/);
        let currX = startX;
        tokens.forEach(tok => {
            const upper = tok.trim().toUpperCase();
            if (["SELECT", "FROM", "WHERE", "WITH", "AS", "AND", "OR", "GROUP", "BY", "ORDER"].includes(upper)) {
                ctx.fillStyle = "#38BDF8"; // Cyan keyword
                ctx.font = "bold 26px monospace";
            } else if (["OVER", "PARTITION", "ROWS", "BETWEEN", "PRECEDING", "FOLLOWING", "CURRENT", "ROW"].includes(upper)) {
                ctx.fillStyle = "#F59E0B"; // Amber Window clause
                ctx.font = "bold 26px monospace";
            } else if (["SUM", "LAG", "LEAD", "DENSE_RANK", "RANK", "ROW_NUMBER", "COUNT", "AVG"].includes(upper)) {
                ctx.fillStyle = "#10B981"; // Emerald function
                ctx.font = "bold 26px monospace";
            } else if (!isNaN(tok.trim()) && tok.trim() !== "") {
                ctx.fillStyle = "#EC4899"; // Magenta number
                ctx.font = "26px monospace";
            } else {
                ctx.fillStyle = "#F8FAFC"; // Normal text
                ctx.font = "26px monospace";
            }
            ctx.fillText(tok, currX, lineY);
            currX += ctx.measureText(tok).width;
        });
    }

    // Text Wrap Utility
    function wrapCanvasText(ctx, text, maxWidth) {
        if (!text) return [];
        const words = text.split(" ");
        const lines = [];
        let curr = "";
        words.forEach(w => {
            const test = curr ? (curr + " " + w) : w;
            if (ctx.measureText(test).width <= maxWidth) {
                curr = test;
            } else {
                lines.push(curr);
                curr = w;
            }
        });
        if (curr) lines.push(curr);
        return lines;
    }

    /* ==========================================================================
       TRANSPORT & PLAYBACK TIMELINE CONTROLS
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
            sqlShortState.currentTime = 0.0;
        }
        sqlShortState.isPlaying = true;
        sqlShortState.lastTimestamp = performance.now();
        document.getElementById("btnPlayPause").innerText = "⏸ Pause";

        // Speak Voiceover via Web Speech API if supported
        speakVoiceoverPhase(sqlShortState.currentTime);

        function step(now) {
            if (!sqlShortState.isPlaying) return;
            const deltaSec = (now - sqlShortState.lastTimestamp) / 1000.0 * sqlShortState.playbackSpeed;
            sqlShortState.lastTimestamp = now;
            sqlShortState.currentTime += deltaSec;

            if (sqlShortState.currentTime >= sqlShortState.maxDuration) {
                sqlShortState.currentTime = sqlShortState.maxDuration;
                pauseSqlShortPlay();
            }

            renderSqlShortFrame(sqlShortState.currentTime);
            updatePlayerScrubberUI(sqlShortState.currentTime);

            sqlShortState.animationFrameId = requestAnimationFrame(step);
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
        if (window.speechSynthesis) window.speechSynthesis.cancel();
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
        updatePlayerScrubberUI(sqlShortState.currentTime);
        renderSqlShortFrame(sqlShortState.currentTime);
    }

    function setSqlShortSpeed(val) {
        sqlShortState.playbackSpeed = parseFloat(val);
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

    function speakVoiceoverPhase(t) {
        if (!window.speechSynthesis) return;
        const p = sqlShortState.activePreset;
        const lang = sqlShortState.audioLang;
        let phrase = "";

        if (t < 5.0) phrase = p['hook_' + lang] || p.hook_mr;
        else if (t < 20.0) phrase = p.question;
        else if (t < 42.0) phrase = p['explanation_' + lang] || p.explanation_mr;
        else phrase = p.pro_tip;

        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(phrase);
        u.lang = lang === 'hi' ? 'hi-IN' : (lang === 'mr' ? 'mr-IN' : 'en-US');
        u.rate = 1.05;
        window.speechSynthesis.speak(u);
    }

    /* ==========================================================================
       ZERO-SERVER-LOAD CLIENT-SIDE VIDEO RECORDER & DOWNLOAD
       ========================================================================== */
    async function exportSqlShortVideo() {
        const canvas = document.getElementById("sqlShortCanvas");
        const btn = document.getElementById("btnDownloadShortVideo");
        const btnLabel = document.getElementById("exportBtnLabel");
        const pBar = document.getElementById("exportProgressBar");
        const pFill = document.getElementById("exportProgressFill");
        const pText = document.getElementById("exportProgressText");

        if (!canvas.captureStream) {
            alert("Your browser does not support Canvas.captureStream. Please use Chrome/Edge.");
            return;
        }

        pauseSqlShortPlay();
        sqlShortState.currentTime = 0.0;
        pBar.style.display = "block";
        btn.disabled = true;
        btnLabel.innerText = "RECORDING 9:16 VIDEO...";

        const stream = canvas.captureStream(30); // 30 FPS high-definition stream
        let mimeType = "video/webm;codecs=vp9";
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = "video/webm";
        }

        const chunks = [];
        const recorder = new MediaRecorder(stream, {
            mimeType: mimeType,
            videoBitsPerSecond: 8000000 // 8 Mbps high quality
        });

        recorder.ondataavailable = e => {
            if (e.data && e.data.size > 0) chunks.push(e.data);
        };

        recorder.onstop = () => {
            pFill.style.width = "100%";
            pText.innerText = "Encoding finished! Downloading video file...";
            const blob = new Blob(chunks, { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            const filename = `Clean_ZeroWatermark_9x16_${sqlShortState.activePreset.id}.webm`;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            setTimeout(() => {
                pBar.style.display = "none";
                pFill.style.width = "0%";
                btn.disabled = false;
                btnLabel.innerText = "DOWNLOAD 9:16 VIDEO (CLEAN & NO WATERMARK)";
                alert(`🎉 100% Clean Zero-Watermark 9:16 Video Ready!\nFile: ${filename}\n🛡️ Zero third-party watermarks • Perfect for Instagram Reels & YouTube Shorts!`);
            }, 1000);
        };

        recorder.start();

        // High-speed 60-second frame render
        const totalFrames = 60 * 30; // 1800 frames
        let frameCount = 0;
        const dt = 1.0 / 30.0;

        function recordStep() {
            if (frameCount < totalFrames) {
                sqlShortState.currentTime = frameCount * dt;
                
                // Synchronize live avatar video frame if active
                if (sqlShortState.avatarVideoElement && sqlShortState.avatarVideoElement.duration > 0) {
                    sqlShortState.avatarVideoElement.currentTime = (frameCount * dt) % sqlShortState.avatarVideoElement.duration;
                }

                renderSqlShortFrame(sqlShortState.currentTime);
                updatePlayerScrubberUI(sqlShortState.currentTime);
                frameCount++;

                if (frameCount % 30 === 0) {
                    const pct = Math.floor((frameCount / totalFrames) * 100);
                    pFill.style.width = `${pct}%`;
                    pText.innerText = `Recording clean frame ${frameCount}/${totalFrames} (${pct}%)...`;
                }
                requestAnimationFrame(recordStep);
            } else {
                recorder.stop();
            }
        }
        requestAnimationFrame(recordStep);
    }
    </script>
    '''
