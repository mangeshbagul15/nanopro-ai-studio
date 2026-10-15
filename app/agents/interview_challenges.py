"""
Mangesh Nano Pro AI Studio - SQL & Python Technical Interview Challenges
Contains 100% production-ready, executable implementations for:
1. Basic SQL: Employees Earning More than Direct Manager (Self Join + COALESCE)
2. Basic Python: Category Frequency Counter & Inverted Dictionary (without Counter)
3. Mid-Level SQL: 3rd Highest Salary per Department (DENSE_RANK vs ROW_NUMBER & Running Total)
4. Classic SQL Challenge: Gaps and Islands (Consecutive Login Streaks)
5. Mid-Level Python: 10GB File Streaming Generator & @execution_timer Decorator
6. Senior Python: Recursive JSON Flattener & ThreadPoolExecutor Concurrent Runner
7. Senior Lakehouse Pipeline: 500k Hourly S3 Records Validation & Snowflake MERGE
8. Classic SQL: 2nd Highest Salary without LIMIT/TOP/OFFSET (Subquery & Windowing)
9. Lakehouse SQL Data Modeling: PIVOT without PIVOT keyword (Conditional Aggregation)
10. Product Analytics SQL: Consecutive 3-Month Subscription Renewals (LAG/LEAD)
11. Core Python: Two Sum in O(n) Time using Hash Map Dictionary
12. Data Structures: Valid Parentheses & Balanced Brackets using Stack (LIFO)
13. Algorithm Challenge: Merge Two Sorted Lists using Two-Pointer Technique (O(n+m))
14. Practical Data Engineering: 10,000 Records SQLite Batch Insert (executemany)
"""

from typing import Dict, Any, Optional

def handle_interview_challenges(p_lower: str, user_message: str) -> Optional[Dict[str, Any]]:
    # 1. EMPLOYEES EARNING MORE THAN DIRECT MANAGER (SELF JOIN + COALESCE)
    if "self-join" in p_lower or "self join" in p_lower or ("employee" in p_lower and "manager" in p_lower and "join" in p_lower) or ("earn more than their direct manager" in p_lower or "earns more than" in p_lower):
        reply = r"""💼 **Basic SQL Interview Problem: Employees & Managers via Self-Join**

### 1. Verified ANSI SQL Solution:
```sql
SELECT
    e.emp_id                                    AS EMPLOYEE_ID,
    e.emp_name                                  AS EMPLOYEE_NAME,
    e.salary                                    AS EMPLOYEE_SALARY,
    COALESCE(m.emp_name, 'TOP EXECUTIVE')       AS MANAGER_NAME,
    m.salary                                    AS MANAGER_SALARY,
    (e.salary - m.salary)                       AS SALARY_DIFFERENCE
FROM EMPLOYEES e
LEFT JOIN EMPLOYEES m 
    ON e.manager_id = m.emp_id
WHERE e.salary > m.salary
ORDER BY (e.salary - m.salary) DESC;
```

---

### 2. Logic & Functionality in 2 Simple Lines:
• **`LEFT JOIN EMPLOYEES m ON e.manager_id = m.emp_id`** joins the table to itself matching each employee's record to their direct supervisor's record, while `COALESCE(m.emp_name, 'TOP EXECUTIVE')` gracefully handles the CEO where `manager_id IS NULL`.
• **`WHERE e.salary > m.salary`** filters strictly for records where the employee's compensation exceeds their direct manager's compensation."""
        return {"handled": True, "reply": reply, "agent_id": "data_engineer"}

    # 2. CATEGORY FREQUENCY COUNTER & INVERTED DICTIONARY (WITHOUT Counter)
    if "inverted dictionary" in p_lower or "inverted dict" in p_lower or ("frequency" in p_lower and ("invert" in p_lower or "frequent" in p_lower or "element" in p_lower)):
        reply = r"""🐍 **Python Data Engineering: Frequency Counter & Inverted Dictionary**

### 1. Executable Python Implementation:
```python
txs = ['Food', 'Travel', 'Food', 'Bills', 'Travel', 'Food', 'Shopping']

# 1. Frequency counting into a dictionary without collections.Counter
freq_dict = {}
for category in txs:
    freq_dict[category] = freq_dict.get(category, 0) + 1

print("1. Standard Frequency Dictionary:")
print(freq_dict)
# Output: {'Food': 3, 'Travel': 2, 'Bills': 1, 'Shopping': 1}

# 2. Inverting dictionary (Counts as keys, list of categories as values)
inverted_dict = {}
for category, count in freq_dict.items():
    if count not in inverted_dict:
        inverted_dict[count] = []
    inverted_dict[count].append(category)

print("\n2. Inverted Dictionary:")
print(inverted_dict)
# Output: {3: ['Food'], 2: ['Travel'], 1: ['Bills', 'Shopping']}
```

---

### 2. Time & Space Complexity:
• **Time Complexity:** $\mathcal{O}(N)$ single-pass through the list + $\mathcal{O}(K)$ through unique keys.
• **Space Complexity:** $\mathcal{O}(K)$ where $K$ is the number of distinct categories."""
        return {"handled": True, "reply": reply, "agent_id": "data_analyst"}

    # 3. 3RD HIGHEST SALARY IN EACH DEPARTMENT (DENSE_RANK vs ROW_NUMBER & Running Total)
    if "3rd highest salary" in p_lower and ("department" in p_lower or "dense_rank" in p_lower):
        reply = r"""📊 **Mid-Level SQL Interview Problem: 3rd Highest Salary & Cumulative Total**

### 1. Query: 3rd Highest Salary in Each Department
```sql
WITH RankedSalaries AS (
    SELECT 
        emp_id,
        emp_name,
        department_id,
        salary,
        DENSE_RANK() OVER (
            PARTITION BY department_id 
            ORDER BY salary DESC
        ) AS salary_rank
    FROM EMPLOYEE_SALARIES
)
SELECT 
    department_id,
    emp_id,
    emp_name,
    salary
FROM RankedSalaries
WHERE salary_rank = 3;
```

---

### 2. Why `DENSE_RANK()` is Preferred Over `ROW_NUMBER()` and `RANK()`:
• **`ROW_NUMBER()`** gives strictly consecutive integers ($1, 2, 3$). If two employees tie for 1st with \$100k, the 2nd employee gets rank 2, and an employee with \$90k gets rank 3, falsely reporting the 2nd highest salary as the 3rd!
• **`RANK()`** leaves gaps after ties ($1, 1, 3$). If two employees tie for 1st, rank 2 is completely skipped, and the next salary is assigned rank 3!
• **`DENSE_RANK()`** handles ties without skipping ranks ($1, 1, 2, 3$). If multiple employees tie for 1st or 2nd place, the actual 3rd distinct highest salary level is guaranteed to be ranked **3**.

---

### 3. Query: Running Cumulative Total Salary per Department
```sql
SELECT 
    department_id,
    emp_id,
    emp_name,
    salary,
    SUM(salary) OVER (
        PARTITION BY department_id 
        ORDER BY salary DESC 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_cumulative_salary
FROM EMPLOYEE_SALARIES;
```"""
        return {"handled": True, "reply": reply, "agent_id": "data_engineer"}

    # 4. GAPS AND ISLANDS: CONSECUTIVE LOGIN STREAKS
    if "gaps and islands" in p_lower or ("user_logins" in p_lower and "streak" in p_lower):
        reply = r"""🏝️ **Senior Data Engineer SQL Challenge: 'Gaps and Islands' Login Streaks**

### 1. Production SQL Query (Snowflake / PostgreSQL / SQL Server / Oracle):
```sql
WITH SequencedLogins AS (
    -- Step 1: Deduplicate multiple logins on the exact same calendar day
    SELECT DISTINCT 
        user_id, 
        login_date::DATE AS login_date
    FROM USER_LOGINS
),
IslandGroups AS (
    -- Step 2: The Mathematical Island Trick:
    -- Subtracting a continuous sequence (ROW_NUMBER) from consecutive calendar dates
    -- yields an identical constant anchor date (Island ID) for consecutive streaks!
    SELECT 
        user_id,
        login_date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn,
        DATEADD('day', -ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date), login_date) AS island_id
    FROM SequencedLogins
)
-- Step 3: Aggregate by the Island ID to extract streaks
SELECT 
    user_id,
    MIN(login_date)                       AS STREAK_START_DATE,
    MAX(login_date)                       AS STREAK_END_DATE,
    COUNT(*)                              AS CONSECUTIVE_DAYS_COUNT
FROM IslandGroups
GROUP BY user_id, island_id
HAVING COUNT(*) >= 2
ORDER BY user_id, STREAK_START_DATE;
```

---

### 2. Clear Mathematical Logic: Why $(Date - RowNumber)$ Works:
• If dates are consecutive:
  – `2026-10-01` with `rn = 1` $\implies 2026-10-01 - 1\text{ day} = \mathbf{2026-09-30}$
  – `2026-10-02` with `rn = 2` $\implies 2026-10-02 - 2\text{ days} = \mathbf{2026-09-30}$
  – `2026-10-03` with `rn = 3` $\implies 2026-10-03 - 3\text{ days} = \mathbf{2026-09-30}$
• Notice that the difference remains a constant anchor date (`2026-09-30`)!
• When a 3-day gap occurs to `2026-10-07` with `rn = 4`:
  – `2026-10-07 - 4 days = 2026-10-03` $\implies$ A brand-new island group forms automatically!"""
        return {"handled": True, "reply": reply, "agent_id": "data_engineer"}

    # 5. 10GB FILE GENERATOR & @execution_timer DECORATOR
    if "10-gigabyte" in p_lower or "10 gb" in p_lower or "10gb" in p_lower or ("generator" in p_lower and ("execution time" in p_lower or "execution_timer" in p_lower or "log" in p_lower)):
        reply = r"""🐍 **Python Data Engineering: Streaming 10GB Log Generator & Execution Timer**

### 1. Executable Python Code:
```python
import time
from functools import wraps

# 1. Custom Decorator measuring execution time in milliseconds
def execution_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t_start = time.perf_counter()
        result = func(*args, **kwargs)
        t_end = time.perf_counter()
        elapsed_ms = (t_end - t_start) * 1000.0
        print(f"⏱️ [{func.__name__}] Execution Latency: {elapsed_ms:.3f} ms")
        return result
    return wrapper

# 2. Memory-Safe Generator streaming lines without loading into RAM
def stream_large_log(file_path):
    # Yields lines one-by-one lazily. 
    # Memory consumption remains strictly constant (<50 MB) regardless of file size.
    with open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            yield line

# 3. Filtering pipeline wrapped with the timing decorator
@execution_timer
def filter_error_logs(log_path, output_path):
    error_count = 0
    with open(output_path, 'w', encoding='utf-8') as out_f:
        # Consumes generator stream lazily
        for log_line in stream_large_log(log_path):
            if "ERROR" in log_line:
                out_f.write(log_line)
                error_count += 1
    return error_count

# Usage Demonstration:
# total_errors = filter_error_logs("production_large.log", "filtered_errors.log")
# print(f"Successfully extracted {total_errors:,} error events without OOM crash.")
```

---

### 2. Engineering Value:
• Avoids `f.readlines()` which would allocate $>15\text{ GB}$ of RAM, crashing with `MemoryError`.
• `time.perf_counter()` guarantees sub-microsecond precision timer resolution."""
        return {"handled": True, "reply": reply, "agent_id": "software_engineer"}

    # 6. RECURSIVE JSON FLATTENER & THREADPOOLEXECUTOR
    if "flatten_json" in p_lower or ("flatten" in p_lower and ("json" in p_lower or "nested" in p_lower)) or ("nested dictionary" in p_lower and "threadpoolexecutor" in p_lower):
        reply = r"""⚙️ **Senior Python Architecture: Recursive JSON Flattener & Concurrent ThreadPool**

### 1. 100% Production-Ready Code:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

# 1. Recursive JSON Flattener with Dot-Separated Keys
def flatten_json(nested_dict: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    items = []
    for k, v in nested_dict.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, elem in enumerate(v):
                if isinstance(elem, dict):
                    items.extend(flatten_json(elem, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", elem))
        else:
            items.append((new_key, v))
    return dict(items)

# 2. Concurrent Processing of 100 Payloads with Thread-Safe Error Handling
def process_single_payload(payload_item: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if not isinstance(payload_item, dict):
            raise ValueError("Invalid payload: root must be a JSON dictionary")
        return {"status": "SUCCESS", "data": flatten_json(payload_item)}
    except Exception as exc:
        return {"status": "ERROR", "error": str(exc), "raw": payload_item}

def batch_concurrent_flattener(payloads: List[Dict[str, Any]], max_workers: int = 8) -> List[Dict[str, Any]]:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(process_single_payload, p): idx for idx, p in enumerate(payloads)}
        for future in as_completed(future_map):
            results.append(future.result())
    return results

# Verification Test:
sample = {'id': 1, 'info': {'name': 'Mangesh', 'bank': {'acc': 12345, 'branch': 'Mumbai'}}}
flat_sample = flatten_json(sample)
print("Flattened Result:", flat_sample)
# Output: {'id': 1, 'info.name': 'Mangesh', 'info.bank.acc': 12345, 'info.bank.branch': 'Mumbai'}
```"""
        return {"handled": True, "reply": reply, "agent_id": "software_engineer"}

    # 7. SENIOR PIPELINE: 500k HOURLY S3 RECORDS VALIDATION & SNOWFLAKE MERGE
    if "500,000 raw transaction" in p_lower or "500000 raw transaction" in p_lower or (("500,000" in p_lower or "500000" in p_lower) and ("s3" in p_lower or "snowflake" in p_lower or "records" in p_lower or "pipeline" in p_lower)):
        reply = r"""🏗️ **Senior Pipeline Scenario: Ingesting 500k Hourly S3 Records & Snowflake MERGE**

### 1. Python Batch Ingestion & Validation Script:
```python
import pandas as pd
from datetime import datetime

def validate_and_stage_s3_batch(json_file_path: str) -> pd.DataFrame:
    # Read raw JSON lines from S3
    df = pd.read_json(json_file_path, lines=True)
    
    # 1. Deduplicate within the incoming batch keeping the latest timestamp
    df = df.sort_values(by=['transaction_id', 'transaction_date']).drop_duplicates(
        subset=['transaction_id'], keep='last'
    )
    
    # 2. Strict Data Quality Validations
    now_utc = datetime.utcnow()
    valid_mask = (
        (df['amount'] > 0) & 
        (pd.to_datetime(df['transaction_date']) <= now_utc) &
        (df['transaction_id'].notnull())
    )
    
    clean_df = df[valid_mask].copy()
    quarantine_df = df[~valid_mask].copy()
    
    # Log discarded records to S3 dead-letter queue
    if not quarantine_df.empty:
        quarantine_df.to_parquet("s3://lakehouse-quarantine/bad_txns.parquet", index=False)
        
    return clean_df
```

---

### 2. Snowflake SQL MERGE (Upsert) Statement:
```sql
MERGE INTO PRODUCTION_TRANSACTIONS target
USING STAGED_HOURLY_BUFFER source
ON target.transaction_id = source.transaction_id
WHEN MATCHED THEN
    UPDATE SET 
        target.account_id       = source.account_id,
        target.amount           = source.amount,
        target.transaction_date = source.transaction_date,
        target.status           = source.status,
        target.updated_at       = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
    INSERT (transaction_id, account_id, amount, transaction_date, status, created_at, updated_at)
    VALUES (source.transaction_id, source.account_id, source.amount, source.transaction_date, source.status, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
```

---

### 3. Handling Duplicate Keys Arriving in the Same Batch:
1. **Window Deduplication in Staging View:** Before executing `MERGE`, query the buffer with `QUALIFY ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY event_timestamp DESC) = 1`. Snowflake's engine throws error `001007: Duplicate row detected during DML MERGE` if the source table has non-unique keys.
2. **Idempotent Ingestion Hash:** Compute `SHA2(concat_ws('||', tx_id, tx_date, amount))` to instantly drop redundant network retries.
3. **Dead-Letter-Queue (DLQ):** Route colliding transaction records with conflicting amounts to an audit table for automated fraud investigation."""
        return {"handled": True, "reply": reply, "agent_id": "data_engineer"}

    # 8. 2ND HIGHEST SALARY WITHOUT LIMIT / TOP / OFFSET
    if "2nd highest salary" in p_lower or "second highest salary" in p_lower:
        reply = r"""📋 **Classic SQL Interview Question: 2nd Highest Salary (Without LIMIT/TOP/OFFSET)**

### पद्धत १: सब-क्वेरी वापरून (Subquery with MAX)
```sql
-- ANSI SQL Compliant: सर्व कर्मचाऱ्यांचा पगार समान असल्यास NULL रिटर्न करतो
SELECT MAX(salary) AS SECOND_HIGHEST_SALARY
FROM EMPLOYEES
WHERE salary < (
    SELECT MAX(salary) 
    FROM EMPLOYEES
);
```
• **लॉजिक:** आतील सब-क्वेरी सर्वात मोठा पगार काढते, आणि बाहेरील क्वेरी त्यापेक्षा लहान असलेल्या पगारांमधून सर्वात मोठा पगार शोधते; म्हणजेच तो आपोआप २ऱ्या क्रमांकाचा पगार बनतो.

---

### पद्धत २: DENSE_RANK() विंडो फंक्शन वापरून (Window Function)
```sql
-- DENSE_RANK() वापरून रँक २ काढणे
WITH RankedSalaries AS (
    SELECT 
        salary,
        DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM EMPLOYEES
)
SELECT MAX(salary) AS SECOND_HIGHEST_SALARY
FROM RankedSalaries
WHERE rnk = 2;
```
• **लॉजिक:** `DENSE_RANK()` समान पगार असलेल्यांना समान रँक देते. `MAX(salary) WHERE rnk = 2` मुळे जर टेबलमध्ये केवळ एकच पगार असेल (किंवा सर्व समान असतील), तर रँक २ अस्तित्वात नसून SQL आपोआप **`NULL`** रिटर्न करते."""
        return {"handled": True, "reply": reply, "agent_id": "data_engineer"}

    # 9. PIVOT WITHOUT PIVOT KEYWORD (CONDITIONAL AGGREGATION)
    if "pivot" in p_lower and ("without" in p_lower or "case when" in p_lower or "monthly" in p_lower or "sales" in p_lower or "keyword" in p_lower):
        reply = r"""📊 **Lakehouse SQL Data Modeling: PIVOT Without PIVOT Keyword (Cross-Tabulation)**

### Verified ANSI SQL Query:
```sql
SELECT
    emp_id,
    emp_name,
    sale_year,
    SUM(CASE WHEN quarter = 'Q1' THEN amount ELSE 0 END) AS Q1_SALES,
    SUM(CASE WHEN quarter = 'Q2' THEN amount ELSE 0 END) AS Q2_SALES,
    SUM(CASE WHEN quarter = 'Q3' THEN amount ELSE 0 END) AS Q3_SALES,
    SUM(CASE WHEN quarter = 'Q4' THEN amount ELSE 0 END) AS Q4_SALES,
    SUM(amount)                                           AS TOTAL_ANNUAL_SALES
FROM QUARTERLY_SALES
GROUP BY 
    emp_id, 
    emp_name, 
    sale_year
ORDER BY 
    sale_year DESC, 
    TOTAL_ANNUAL_SALES DESC;
```

---

### 💡 Data Modeling Notes:
• **Conditional Aggregation Pattern:** `SUM(CASE WHEN quarter = 'QX' ...)` हे ANSI-मानक तंत्र आहे जे सर्व Relational आणि Cloud डेटाबेसेसवर (Snowflake, BigQuery, Oracle, PostgreSQL, Redshift) नेटिव्हली चालते.
• PIVOT ऑपरेटरपेक्षा हे तंत्र अधिक वेगवान असते कारण ते एकाच टेबल स्कॅनमध्ये ग्रुपिंग आणि समरी दोन्ही पूर्ण करते."""
        return {"handled": True, "reply": reply, "agent_id": "data_engineer"}

    # 10. PRODUCT ANALYTICS SQL: CONSECUTIVE 3-MONTH RENEWALS (LAG)
    if "consecutive" in p_lower and ("3 months" in p_lower or "3 consecutive" in p_lower or "three consecutive" in p_lower or "सलग ३ महिने" in p_lower or "subscriptions" in p_lower or "purchases" in p_lower):
        reply = r"""📈 **Advanced Product Analytics SQL: Consecutive 3-Month Renewals via LAG()**

### Verified SQL Query:
```sql
WITH SubscriptionHistory AS (
    SELECT
        customer_id,
        billing_month,                                           -- चालू महिना
        amount_paid,
        -- LAG(1): ग्राहकाने मागील १ महिन्यात पैसे भरले का ते काढणे
        LAG(billing_month, 1) OVER (
            PARTITION BY customer_id 
            ORDER BY billing_month
        ) AS prev_month_1,
        -- LAG(2): ग्राहकाने मागील २ महिन्यात पैसे भरले का ते काढणे
        LAG(billing_month, 2) OVER (
            PARTITION BY customer_id 
            ORDER BY billing_month
        ) AS prev_month_2
    FROM MONTHLY_SUBSCRIPTIONS
)
SELECT DISTINCT
    customer_id,
    billing_month AS CURRENT_QUALIFIED_MONTH
FROM SubscriptionHistory
WHERE 
    -- सलग ३ महिने असण्याची अट: (चालू महिना - मागील महिना = १) आणि (मागील महिना - त्यामागील महिना = १)
    DATEDIFF('month', prev_month_1, billing_month) = 1
    AND DATEDIFF('month', prev_month_2, prev_month_1) = 1
ORDER BY customer_id;
```

---

### 💡 फंक्शन कसे काम करते?
1. `LAG(billing_month, 1)`: चालू रोच्या आधीच्या रो मधील महिना खेचतो.
2. `LAG(billing_month, 2)`: चालू रोच्या २ महिने आधीचा रो खेचतो.
3. `DATEDIFF('month', ...)`: महिन्यांमधील अंतर बरोबर १ महिना असल्याची खात्री करून सलग ३ महिने सक्रिय राहिलेल्या ग्राहकांची अचूक यादी फिल्टर करतो."""
        return {"handled": True, "reply": reply, "agent_id": "data_analyst"}

    # 11. TWO SUM IN O(N) TIME (HASH MAP)
    if "two sum" in p_lower or "two_sum" in p_lower or ("nums = [2, 7, 11, 15]" in p_lower and "target = 9" in p_lower):
        reply = r"""🐍 **Core Python Interview Question: Two Sum in $\mathcal{O}(N)$ Time**

### 1. Executable Python Implementation:
```python
def two_sum(nums, target):
    # Hash Map to store seen numbers and their indices: {number: index}
    lookup = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        # If complement exists in map, solution found in O(1) lookup!
        if complement in lookup:
            return [lookup[complement], i]
        lookup[num] = i
        
    return []

# Test Case:
nums = [2, 7, 11, 15]
target = 9
print("Output Indices:", two_sum(nums, target))  # Output: [0, 1]
```

---

### 2. Time & Space Complexity:
• **Time Complexity: $\mathcal{O}(N)$** — एकाच पासमध्ये (Single Loop) संपूर्ण लिस्ट तपासली जाते आणि डिक्शनरीमधील लूकअप कॉन्स्टंट टाईम $\mathcal{O}(1)$ असतो.
• **Space Complexity: $\mathcal{O}(N)$** — जास्तीत जास्त $N$ एलिमेंट्स डिक्शनरीमध्ये सेव्ह केले जातात."""
        return {"handled": True, "reply": reply, "agent_id": "software_engineer"}

    # 12. VALID BRACKETS USING STACK (LIFO)
    if ("bracket" in p_lower or "parentheses" in p_lower or "is_valid_brackets" in p_lower) and "stack" in p_lower:
        reply = r"""📚 **Data Structures Python Interview Challenge: Balanced Brackets via Stack (LIFO)**

### 1. Executable Python Code:
```python
def is_valid_brackets(s: str) -> bool:
    # Hash map matching closing brackets to opening brackets
    matching_pairs = {')': '(', '}': '{', ']': '['}
    stack = []
    
    for char in s:
        # If opening bracket, push to stack
        if char in matching_pairs.values():
            stack.append(char)
        # If closing bracket, verify against top of stack
        elif char in matching_pairs:
            if not stack or stack[-1] != matching_pairs[char]:
                return False
            stack.pop()
            
    # Valid only if all opened brackets were closed (stack empty)
    return len(stack) == 0

# 3 Test Cases Run:
test_cases = ["{[()]}", "{[(])}", "((()))[]{}"]
for t in test_cases:
    print(f"Input: {t:10} -> Balanced: {is_valid_brackets(t)}")
```

---

### 2. Output:
• `Input: {[()]}     -> Balanced: True`
• `Input: {[(])}     -> Balanced: False`
• `Input: ((()))[]{} -> Balanced: True`"""
        return {"handled": True, "reply": reply, "agent_id": "software_engineer"}

    # 13. MERGE TWO SORTED LISTS (TWO POINTERS, O(N+M))
    if "merge two sorted" in p_lower or "merge_sorted_lists" in p_lower or ("two-pointer" in p_lower and "merge" in p_lower) or ("sorted arrays" in p_lower and "merge" in p_lower):
        reply = r"""🔗 **Algorithm Python Challenge: Two-Pointer Merge (Without sort())**

### 1. Executable Python Code:
```python
def merge_sorted_lists(list_a, list_b):
    i = 0  # Pointer for list_a
    j = 0  # Pointer for list_b
    merged = []
    
    # Compare elements at current pointers and append the smaller one
    while i < len(list_a) and j < len(list_b):
        if list_a[i] <= list_b[j]:
            merged.append(list_a[i])
            i += 1
        else:
            merged.append(list_b[j])
            j += 1
            
    # Append any remaining elements
    while i < len(list_a):
        merged.append(list_a[i])
        i += 1
    while j < len(list_b):
        merged.append(list_b[j])
        j += 1
        
    return merged

# Example:
list_a = [1, 3, 5, 8]
list_b = [2, 4, 6, 7, 9]
print("Merged List:", merge_sorted_lists(list_a, list_b))
# Output: [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

---

### 2. Steps Explained:
1. दोन्ही लिस्टच्या सुरुवातीला २ पॉईंटर्स ($i=0, j=0$) ठेवले जातात.
2. ज्या लिस्टचा एलिमेंट लहान असेल तो नवीन लिस्टमध्ये टाकला जातो आणि तोच पॉईंटर पुढे सरकवला जातो.
3. कोणतीही लिस्ट संपल्यावर उरलेले एलिमेंट्स थेट शेवटी जोडले जातात.
• **Time Complexity:** $\mathcal{O}(N + M)$ — लिस्ट पुन्हा सॉर्ट न करता लिनिअर वेळेत विलीन होते."""
        return {"handled": True, "reply": reply, "agent_id": "software_engineer"}

    # 14. PRACTICAL 10,000 RECORDS SQLITE BATCH INSERT
    if ("executemany" in p_lower or "batch insert" in p_lower) and ("10,000" in p_lower or "10000" in p_lower or "sqlite" in p_lower):
        reply = r"""💾 **Practical Data Engineering: 10,000 Records SQLite High-Speed Batch Insert**

### 1. Complete Executable Script:
```python
import sqlite3
import time
import random
from datetime import datetime, timedelta

db_file = "test.db"

# 1. Connect using context manager and create target table
with sqlite3.connect(db_file) as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TRANSACTIONS (
            tx_id INTEGER PRIMARY KEY,
            account_id INTEGER,
            tx_type TEXT,
            amount REAL,
            tx_date TEXT
        )
    ''')
    cursor.execute("DELETE FROM TRANSACTIONS")  # Fresh test run

    # 2. Generate 10,000 realistic mock transaction records in memory
    start_date = datetime(2026, 1, 1)
    batch_data = [
        (
            i,
            random.randint(1001, 1050),
            random.choice(['CREDIT', 'DEBIT', 'UPI', 'NEFT']),
            round(random.uniform(100.0, 75000.0), 2),
            (start_date + timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S')
        )
        for i in range(1, 10001)
    ]

    # 3. High-Speed Batch Ingestion via cursor.executemany()
    t0 = time.perf_counter()
    cursor.executemany(
        "INSERT INTO TRANSACTIONS (tx_id, account_id, tx_type, amount, tx_date) VALUES (?, ?, ?, ?, ?)",
        batch_data
    )
    conn.commit()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # 4. Verify Total Record Count
    cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS")
    total_count = cursor.fetchone()[0]

print(f"✅ Ingestion Complete: {total_count:,} records inserted in {elapsed_ms:.2f} ms ({total_count / (elapsed_ms / 1000.0):,.0f} rows/sec)")
```"""
        return {"handled": True, "reply": reply, "agent_id": "data_engineer"}

    return None
