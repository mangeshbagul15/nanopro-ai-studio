"""
Mangesh Nano Pro AI Studio - Production Scenario-Based Interview Preparation Knowledge Bank
Senior Data Engineer & Snowflake Specialist (4 Years Experience)

Contains 45 in-depth, production scenario questions across 9 technical domains:
1. Python for Data Engineering (AST, Pandas, PySpark, Multi-threading, Memory optimization)
2. Advanced SQL (Window Functions, CTEs, Analytical queries, Query profiling)
3. Data Engineering Architecture & Lakehouse Design
4. Data Governance & Metadata Management
5. Robust ETL / ELT Pipelines & CDC (Change Data Capture)
6. Snowflake Architecture (Micro-partitioning, Clustering, Time Travel, Zero-Copy Clone, Snowpipe, Streams & Tasks)
7. AWS Data Services (S3 Landing, Glue, Athena, EMR, DMS, Redshift)
8. CI/CD & Orchestration (Airflow DAGs, Docker, Git, CI/CD pipelines)
9. Generative AI & LLMOps in Data Engineering

Each scenario includes:
- Source & Provenance Badge
- Production Enterprise Scenario Description
- Conversational Marathi-English ("Minlish") Summary: "या प्रश्नाचा नेमका अर्थ काय आहे?"
- Production Solution & Code/SQL Architecture
- Interviewer Strategy Tip
- Follow-up Cross-Question & Deep-Dive Answer
"""

from typing import List, Dict, Any

SCENARIO_DOMAINS = [
    "Python for Data Engineering",
    "Advanced SQL",
    "Lakehouse Architecture",
    "Data Governance & Metadata",
    "ETL / ELT & CDC",
    "Snowflake Architecture",
    "AWS Data Services",
    "CI/CD & Orchestration",
    "Generative AI & LLMOps"
]

PRODUCTION_SCENARIO_QUESTIONS: List[Dict[str, Any]] = [
    # =========================================================================
    # DOMAIN 1: PYTHON FOR DATA ENGINEERING
    # =========================================================================
    {
        "id": "py_01",
        "domain": "Python for Data Engineering",
        "category": "Python for Data Engineering",
        "source_badge": "HackerRank Hard | Goldman Sachs Banking Pipeline 2026",
        "scenario": (
            "You are designing a dynamic data ingestion framework in Python where analytical teams submit SQL expressions "
            "and PySpark transformation logic via configuration files. To prevent SQL injections, unsafe OS calls (e.g., eval(), os.system()), "
            "and unbounded cartesian joins, how do you use Python's Abstract Syntax Tree (ast module) to statically parse, inspect, "
            "and validate user-submitted code before cluster execution?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "कंपनीमध्ये ॲनालिस्ट लोक configuration फाईलमध्ये स्वतःचे SQL किंवा Python/PySpark कोड लिहून देतात. "
            "पण जर कोणी चुकीने किंवा मुद्दाम 'os.system(\"rm -rf\")' किंवा 'eval()' सारखा घातक कोड टाकला, किंवा भयंकर मोठा cartesian join लिहिला, "
            "तर क्लस्टर क्रॅश होऊ शकतो किंवा डेटा लीक होऊ शकतो. त्यामुळे कोड रन करायच्या आधीच Python च्या 'ast' (Abstract Syntax Tree) मॉड्युलने "
            "त्या कोडचे झाड (syntax tree) बनवून, धोकादायक फंक्शन्स ब्लॉक कशी करायची आणि कोड सेफ आहे का हे कसे तपासायचे, हे सांगायचे आहे."
        ),
        "in_depth_answer": (
            "Architectural Solution using Python AST:\n\n"
            "1. AST Visitor Implementation:\n"
            "We construct a custom `ast.NodeVisitor` that traverses the syntax tree before submission. It maintains an allowlist "
            "of permissible node types (e.g., `ast.BinOp`, `ast.Compare`, `ast.Call` on approved PySpark DataFrame methods) and raises "
            "a `SecurityValidationError` if blacklisted calls like `eval`, `exec`, `os`, `subprocess`, or `sys` are encountered.\n\n"
            "```python\n"
            "import ast\n\n"
            "class SafePipelineValidator(ast.NodeVisitor):\n"
            "    BANNED_FUNCS = {'eval', 'exec', '__import__', 'compile', 'open'}\n"
            "    BANNED_MODULES = {'os', 'sys', 'subprocess', 'shutil', 'socket'}\n\n"
            "    def visit_Import(self, node):\n"
            "        for alias in node.names:\n"
            "            if alias.name.split('.')[0] in self.BANNED_MODULES:\n"
            "                raise ValueError(f'Security Violation: Disallowed module import {alias.name}')\n"
            "        self.generic_visit(node)\n\n"
            "    def visit_Call(self, node):\n"
            "        if isinstance(node.func, ast.Name) and node.func.id in self.BANNED_FUNCS:\n"
            "            raise ValueError(f'Security Violation: Forbidden function invocation {node.func.id}')\n"
            "        self.generic_visit(node)\n\n"
            "# Production Pipeline Gate\n"
            "def validate_user_script(script_code: str):\n"
            "    tree = ast.parse(script_code)\n"
            "    validator = SafePipelineValidator()\n"
            "    validator.visit(tree)\n"
            "    return True\n"
            "```\n\n"
            "2. Spark Execution Sandbox:\n"
            "Once AST validation passes, the transformation runs inside a restricted namespace dictionary containing only approved Spark DataFrame handles."
        ),
        "interviewer_tip": "Highlight that AST validation performs static analysis at zero cluster cost, stopping malicious or invalid tasks in CI/CD before spinning up EMR or Databricks compute.",
        "follow_up_question": "How do you detect if a user submitted a nested PySpark crossJoin() without an ON condition inside the AST?",
        "follow_up_answer": (
            "In the AST visitor, override `visit_Call(self, node)`. Check if `node.func` is an `ast.Attribute` with `attr == 'crossJoin'`. "
            "Inspect `node.args` or `node.keywords`. If the arguments don't specify strict join predicates or if the cross-joined dataset cardinality "
            "exceeds 10,000 records, reject the job and enforce explicit broadcast or key-based partitioned joins."
        )
    },
    {
        "id": "py_02",
        "domain": "Python for Data Engineering",
        "category": "Python for Data Engineering",
        "source_badge": "LeetCode Hard | Morgan Stanley Trading Mart 2026",
        "scenario": (
            "A PySpark daily reconciliation job processing 250M core banking records fails intermittently with `ExecutorLostFailure` "
            "and `java.lang.OutOfMemoryError: Java heap space`. Upon profiling Spark UI, you find that 99% of tasks finish in 4 seconds, "
            "but one single task runs for 45 minutes on partition 142 due to severe key skew on `ACCOUNT_ID = 9999999` (Internal Suspense Account). "
            "How do you resolve this data skew in PySpark without dropping records?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "२५ कोटी बँक रेकॉर्ड्स रिकन्साईल करताना Spark जॉब क्रॅश होतोय. Spark UI मध्ये दिसते की बाकी सर्व टास्क्स ४ सेकंदात संपतात, "
            "पण एकाच टास्कला ४५ मिनिटे लागतात कारण 'ACCOUNT_ID = 9999999' (बँकेचे सस्पेन्स अकाउंट) वर लाखो ट्रॅन्झॅक्शन्स आहेत. "
            "त्यामुळे एकाच एक्झिक्युटरवर पूर्ण भार येऊन OOM (Out Of Memory) एरर येतो. डेटा न गाळता हा Key Skew (डेटा तिरपेपणा) कसा सोडवायचा?"
        ),
        "in_depth_answer": (
            "Production Solution: Salting the Skewed Key in PySpark:\n\n"
            "1. Root Cause Identification:\n"
            "When Spark performs a shuffle-hash join or groupBy, records with the same hash key land on the same partition. "
            "The suspense account key causes partition 142 to hold 40GB while other partitions hold only 50MB.\n\n"
            "2. Salted Join Architecture:\n"
            "We append a random salt integer `[0 to N-1]` (e.g., N=10) to the skewed key on the left large dataset, and replicate (explode) "
            "the corresponding dimension records on the right dataset by an array `[0..N-1]`:\n\n"
            "```python\n"
            "from pyspark.sql import functions as F\n\n"
            "SALT_FACTOR = 16\n\n"
            "# 1. Add random salt to large transactional table\n"
            "df_txns_salted = df_transactions.withColumn(\n"
            "    'salted_key', \n"
            "    F.when(F.col('account_id') == '9999999', \n"
            "           F.concat(F.col('account_id'), F.lit('_'), (F.rand() * SALT_FACTOR).cast('int')))\n"
            "     .otherwise(F.concat(F.col('account_id'), F.lit('_0')))\n"
            ")\n\n"
            "# 2. Explode lookup dimension table for matching salt ranges\n"
            "df_accounts_exploded = df_accounts.withColumn(\n"
            "    'salt_array', \n"
            "    F.when(F.col('account_id') == '9999999', F.array([F.lit(i) for i in range(SALT_FACTOR)]))\n"
            "     .otherwise(F.array([F.lit(0)]))\n"
            ").withColumn('salt_val', F.explode('salt_array')) \\\n"
            " .withColumn('salted_key', F.concat(F.col('account_id'), F.lit('_'), F.col('salt_val')))\n\n"
            "# 3. Execute distributed hash join without executor memory spike\n"
            "df_reconciled = df_txns_salted.join(df_accounts_exploded, on='salted_key', how='inner') \\\n"
            "    .drop('salted_key', 'salt_array', 'salt_val')\n"
            "```\n\n"
            "3. Adaptive Query Execution (AQE):\n"
            "Enable Spark 3.x AQE skew join optimization:\n"
            "`spark.sql.adaptive.skewJoin.enabled = true` and `spark.sql.adaptive.skewJoin.skewedPartitionFactor = 5`."
        ),
        "interviewer_tip": "Mention that while AQE handles basic skew automatically, custom salting is required when the skew ratio exceeds 1:1000 in massive banking datasets.",
        "follow_up_question": "What happens to shuffle partition memory if you set SALT_FACTOR too high, say 1000?",
        "follow_up_answer": (
            "Setting SALT_FACTOR excessively high blows up the dimension table via `explode()`, creating millions of unnecessary rows "
            "and severe metadata overhead. Benchmarking showing optimal salt factors between 8 and 32 yields maximum distribution without Cartesian memory bloat."
        )
    },
    {
        "id": "py_03",
        "domain": "Python for Data Engineering",
        "category": "Python for Data Engineering",
        "source_badge": "HackerRank Hard | Barclays Risk Lakehouse 2026",
        "scenario": (
            "A daily risk reporting microservice in Python crashes with `MemoryError` when loading a 35GB compressed CSV file into Pandas "
            "on an 8GB RAM worker pod. You are tasked with refactoring the pipeline to stream and aggregate this data in under 2 minutes "
            "with a strict 1GB peak memory ceiling. How do you implement this using Polars LazyFrames and Apache Arrow zero-copy memory?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "८GB रॅम असणाऱ्या कंटेनरमध्ये ३५GB ची मोठी CSV फाईल Pandas मध्ये `pd.read_csv()` केल्यावर `MemoryError` येतो. "
            "Pandas संपूर्ण फाईल एकाच वेळी रॅममध्ये लोड करतो. आपल्याला हा पाईपलाईन Polars LazyFrame आणि Apache Arrow वापरून "
            "फक्त १GB रॅमच्या मर्यादेत आणि २ मिनिटांच्या आत रन करायचा आहे. हे streaming बॅचेसने कसे साध्य करायचे?"
        ),
        "in_depth_answer": (
            "Production Solution with Polars LazyFrame & Streaming Mode:\n\n"
            "1. Why Pandas Fails:\n"
            "Pandas creates Python object wrappers with an overhead of 3x to 5x of the raw file size. A 35GB CSV easily demands 120GB+ RAM in Pandas.\n\n"
            "2. Polars Zero-Copy Arrow Architecture:\n"
            "Polars uses Rust and Arrow columnar format with query optimization and streaming query execution. `scan_csv()` builds a lazy plan "
            "with projection and predicate pushdown, reading only necessary columns and streaming chunks without holding the full table in memory:\n\n"
            "```python\n"
            "import polars as pl\n\n"
            "def process_risk_exposure(file_path: str, output_parquet: str):\n"
            "    # Build optimized query execution graph\n"
            "    lazy_plan = (\n"
            "        pl.scan_csv(file_path, low_memory=True, rechunk=False)\n"
            "        .filter(pl.col('STATUS') == 'SETTLED')\n"
            "        .select([\n"
            "            pl.col('BRANCH_CODE'),\n"
            "            pl.col('PORTFOLIO_ID'),\n"
            "            pl.col('EXPOSURE_INR').cast(pl.Float64),\n"
            "            pl.col('COLLATERAL_VALUE').cast(pl.Float64)\n"
            "        ])\n"
            "        .group_by(['BRANCH_CODE', 'PORTFOLIO_ID'])\n"
            "        .agg([\n"
            "            pl.sum('EXPOSURE_INR').alias('TOTAL_EXPOSURE'),\n"
            "            pl.sum('COLLATERAL_VALUE').alias('TOTAL_COLLATERAL'),\n"
            "            pl.count().alias('TRADE_COUNT')\n"
            "        ])\n"
            "        .with_columns((\n"
            "            (pl.col('TOTAL_EXPOSURE') - pl.col('TOTAL_COLLATERAL'))\n"
            "            .alias('NET_RISK_CAPITAL')\n"
            "        ))\n"
            "    )\n\n"
            "    # Execute in streaming mode (spills to disk if RAM > 800MB)\n"
            "    lazy_plan.sink_parquet(\n"
            "        output_parquet, \n"
            "        compression='snappy',\n"
            "        row_group_size=100000\n"
            "    )\n\n"
            "process_risk_exposure('s3://lake/daily_exposure_35gb.csv', 's3://lake/risk_summary.parquet')\n"
            "```\n\n"
            "3. Memory Footprint:\n"
            "Peak RSS remains stable at ~420MB regardless of whether the file is 35GB or 350GB."
        ),
        "interviewer_tip": "Emphasize `sink_parquet()` over `collect(streaming=True)`. `sink_parquet()` streams output directly to storage, never materializing the final DataFrame in Python memory.",
        "follow_up_question": "What if the CSV has malformed rows with varying column counts?",
        "follow_up_answer": (
            "Pass `ignore_errors=True` and configure `truncate_ragged_lines=True` in `scan_csv()`. "
            "For enterprise audits, we stream malformed lines into a Dead Letter Queue (DLQ) file using Python's `csv` module chunk reader before the Polars stage."
        )
    },
    {
        "id": "py_04",
        "domain": "Python for Data Engineering",
        "category": "Python for Data Engineering",
        "source_badge": "Top Hackathon Winner | Citi Banking Ingestion 2026",
        "scenario": (
            "You need to fetch daily currency exchange rates and sanctions audit files from 60 external banking REST APIs, parse their JSON responses, "
            "encrypt sensitive payloads using AES-GCM, and compress them into Snappy-Parquet format for S3 landing. "
            "How do you design a hybrid concurrency model combining Python's `asyncio`/`aiohttp` for non-blocking I/O with `ProcessPoolExecutor` "
            "for CPU-bound encryption and Parquet serialization?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "६० वेगवेगळ्या बँकांच्या REST API मधून डेटा आणायचा आहे, JSON पार्स करायचा आहे, AES एनक्रिप्शन करायचे आहे आणि Snappy-Parquet मध्ये कॉम्प्रेस करून S3 वर टाकायचे आहे. "
            "नेटवर्क कॉल (Network I/O) हे स्लो असतात, तर एनक्रिप्शन आणि कॉम्प्रेशन हे CPU खातात. "
            "Python च्या GIL (Global Interpreter Lock) मुळे मल्टी-थ्रेडिंगमध्ये CPU काम अडकते. "
            "म्हणून `asyncio` (Network साठी) आणि `ProcessPoolExecutor` (CPU कामासाठी) एकत्र कसे चालवायचे?"
        ),
        "in_depth_answer": (
            "Hybrid Concurrency Architecture:\n\n"
            "1. Architectural Separation:\n"
            "- I/O Bound: Use `asyncio` with `aiohttp` to dispatch 60 HTTP GET requests concurrently with connection pooling.\n"
            "- CPU Bound: Offload AES-256-GCM encryption and Parquet compression to a `concurrent.futures.ProcessPoolExecutor` pool "
            "to bypass the Global Interpreter Lock (GIL) and utilize all physical CPU cores.\n\n"
            "```python\n"
            "import asyncio\n"
            "import aiohttp\n"
            "import pyarrow as pa\n"
            "import pyarrow.parquet as pq\n"
            "from concurrent.futures import ProcessPoolExecutor\n\n"
            "# CPU Worker: runs in separate OS process (bypassing GIL)\n"
            "def cpu_encrypt_and_serialize(raw_records: list, target_path: str):\n"
            "    table = pa.Table.from_pylist(raw_records)\n"
            "    # Simulated AES crypto & Snappy Parquet write\n"
            "    pq.write_table(table, target_path, compression='snappy')\n"
            "    return {'path': target_path, 'rows': len(raw_records)}\n\n"
            "# Async I/O Orchestrator\n"
            "async def fetch_endpoint(session: aiohttp.ClientSession, url: str) -> list:\n"
            "    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:\n"
            "        return await resp.json()\n\n"
            "async def run_hybrid_ingestion(endpoints: list):\n"
            "    loop = asyncio.get_running_loop()\n"
            "    with ProcessPoolExecutor(max_workers=4) as process_pool:\n"
            "        connector = aiohttp.TCPConnector(limit=60)\n"
            "        async with aiohttp.ClientSession(connector=connector) as session:\n"
            "            tasks = [fetch_endpoint(session, u['url']) for u in endpoints]\n"
            "            results = await asyncio.gather(*tasks, return_exceptions=True)\n\n"
            "        # Dispatch CPU serialization tasks to process pool\n"
            "        cpu_futures = []\n"
            "        for idx, data in enumerate(results):\n"
            "            if isinstance(data, list):\n"
            "                target = f'/tmp/batch_{idx}.parquet'\n"
            "                fut = loop.run_in_executor(process_pool, cpu_encrypt_and_serialize, data, target)\n"
            "                cpu_futures.append(fut)\n\n"
            "        completed = await asyncio.gather(*cpu_futures)\n"
            "        return completed\n"
            "```\n\n"
            "2. Performance Impact:\n"
            "Total ingestion runtime drops from 180 seconds (sequential) to 4.2 seconds."
        ),
        "interviewer_tip": "Explicitly explain why you didn't use `threading.Thread` for the compression phase: Python's GIL serializes CPU bytecode execution, reducing multi-threaded CPU tasks to single-core speed.",
        "follow_up_question": "What happens if one of the 60 banking endpoints returns HTTP 429 Too Many Requests?",
        "follow_up_answer": (
            "We wrap `fetch_endpoint` with exponential backoff using `tenacity` or custom jitter: "
            "`sleep = min(60, (2 ** attempt) + random.uniform(0, 1))`. We also inspect the `Retry-After` HTTP header to pause only that specific client coroutine."
        )
    },
    {
        "id": "py_05",
        "domain": "Python for Data Engineering",
        "category": "Python for Data Engineering",
        "source_badge": "MNC Tier-1 | Snowflake Partner Labs 2026",
        "scenario": (
            "You are auditing 50 million legacy CBS transaction log records stored in binary format on a local NVMe drive. "
            "Your service is deployed in an AWS Fargate container with a strict 512MB RAM hard limit. "
            "How do you process, validate checksums, and stream records to Snowflake without triggering Linux OOM killer (cgroups SIGKILL)?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "५ कोटी जुने बँक ट्रॅन्झॅक्शन रेकॉर्ड्स एका मोठ्या फाईलमध्ये आहेत आणि तुमच्या AWS Fargate कंटेनरला फक्त ५१२MB रॅम आहे. "
            "जर तुम्ही फाईल पूर्ण वाचायला गेलात, तर Linux OS त्वरित कंटेनरला 'SIGKILL' मारून बंद करतो (OOM Killer). "
            "मेमरी ५१२MB च्या आत ठेवून Python Generators आणि `mmap` (Memory Mapping) द्वारे डेटा कसा स्ट्रीम करायचा?"
        ),
        "in_depth_answer": (
            "Production Solution with Memory Mapping (`mmap`) & Chunked Generators:\n\n"
            "1. Memory Mapping Advantage:\n"
            "`mmap` maps the file directly into the process's virtual address space. The OS kernel's page cache pages in only the 4KB pages "
            "being read, automatically discarding unmodified pages when memory pressure occurs. It avoids copying buffer data from kernel space to user space.\n\n"
            "```python\n"
            "import mmap\n"
            "import struct\n"
            "from typing import Generator, Dict, Any\n\n"
            "RECORD_STRUCT = struct.Struct('!I16sQd')  # 36 bytes: txn_id, account_hash, epoch_ms, amount\n\n"
            "def stream_binary_transactions(file_path: str) -> Generator[Dict[str, Any], None, None]:\n"
            "    record_size = RECORD_STRUCT.size\n"
            "    with open(file_path, 'rb') as f:\n"
            "        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:\n"
            "            total_bytes = mm.size()\n"
            "            cursor = 0\n"
            "            while cursor + record_size <= total_bytes:\n"
            "                raw_bytes = mm[cursor : cursor + record_size]\n"
            "                txn_id, acct_hash, epoch_ms, amount = RECORD_STRUCT.unpack(raw_bytes)\n"
            "                cursor += record_size\n"
            "                yield {\n"
            "                    'txn_id': txn_id,\n"
            "                    'account_hash': acct_hash.decode('ascii').strip('\\x00'),\n"
            "                    'epoch_ms': epoch_ms,\n"
            "                    'amount': amount\n"
            "                }\n\n"
            "# Micro-batch buffer for Snowflake Streaming Ingest\n"
            "def batch_stream_to_snowflake(generator, batch_size=50000):\n"
            "    buffer = []\n"
            "    for record in generator:\n"
            "        buffer.append(record)\n"
            "        if len(buffer) >= batch_size:\n"
            "            yield buffer\n"
            "            buffer = []  # Explicit dereference for garbage collector\n"
            "    if buffer:\n"
            "        yield buffer\n"
            "```\n\n"
            "2. Memory Profile:\n"
            "Peak container memory stays under 85MB for all 50 million records."
        ),
        "interviewer_tip": "Mention `struct.Struct` pre-compilation. Pre-compiling the binary unpacker yields a 4x speedup over calling `struct.unpack('!I16sQd', ...)` in an iterative loop.",
        "follow_up_question": "Why did you use `mmap` instead of a plain `f.read(record_size)` loop?",
        "follow_up_answer": (
            "`f.read()` makes 50 million individual system calls (`read` syscalls), incurring heavy context switching overhead between user mode and kernel mode. "
            "`mmap` allows direct pointer arithmetic in memory space, reducing execution time from 14 minutes to 38 seconds."
        )
    },

    # =========================================================================
    # DOMAIN 2: ADVANCED SQL
    # =========================================================================
    {
        "id": "sql_01",
        "domain": "Advanced SQL",
        "category": "Advanced SQL",
        "source_badge": "LeetCode Database Hard | JPMorgan Asset Mart 2026",
        "scenario": (
            "A banking compliance regulator requires you to detect all customers who had continuous negative ledger balances "
            "for 7 or more consecutive calendar days across a 100-million row daily balance snapshot table (`CUSTOMER_DAILY_BALANCE`). "
            "How do you formulate a high-performance query using the Gaps-and-Islands window function technique?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकिंग ऑडिटसाठी अशा ग्राहकांना शोधायचे आहे ज्यांचे बँक बॅलन्स सलग ७ किंवा त्यापेक्षा जास्त दिवस मायनस (negative) होते. "
            "टेबलमध्ये १० कोटी रेकॉर्ड्स आहेत. जर ग्राहक २ दिवस मायनस राहिला, ३ ऱ्या दिवशी पॉझिटिव्ह झाला, आणि पुन्हा ५ दिवस मायनस झाला तर ते चालणार नाही; सलग ७ दिवस हवे आहेत. "
            "SQL मधील 'Gaps and Islands' अल्गोरिदम (`ROW_NUMBER()` मधील फरक) वापरून हे कसे शोधायचे?"
        ),
        "in_depth_answer": (
            "Production Solution using Gaps-and-Islands Method:\n\n"
            "1. Algorithmic Principle:\n"
            "Subtracting a continuous sequence `ROW_NUMBER()` from the calendar date `SNAPSHOT_DATE` produces a constant group key "
            "(`ISLAND_ID`) as long as the dates are unbroken consecutive days. If a gap occurs, the arithmetic difference shifts.\n\n"
            "```sql\n"
            "WITH negative_balances AS (\n"
            "    -- Step 1: Filter to only negative balance records\n"
            "    SELECT \n"
            "        CUSTOMER_ID,\n"
            "        SNAPSHOT_DATE,\n"
            "        CLOSING_BALANCE,\n"
            "        ROW_NUMBER() OVER(\n"
            "            PARTITION BY CUSTOMER_ID \n"
            "            ORDER BY SNAPSHOT_DATE\n"
            "        ) AS SEQ_NUM\n"
            "    FROM CUSTOMER_DAILY_BALANCE\n"
            "    WHERE CLOSING_BALANCE < 0\n"
            "),\n"
            "islands AS (\n"
            "    -- Step 2: Calculate Island Identifier (Date - Sequence)\n"
            "    SELECT \n"
            "        CUSTOMER_ID,\n"
            "        SNAPSHOT_DATE,\n"
            "        CLOSING_BALANCE,\n"
            "        DATEADD('day', -SEQ_NUM, SNAPSHOT_DATE) AS ISLAND_GROUP_KEY\n"
            "    FROM negative_balances\n"
            "),\n"
            "streak_aggregates AS (\n"
            "    -- Step 3: Aggregate streaks and filter for >= 7 consecutive days\n"
            "    SELECT \n"
            "        CUSTOMER_ID,\n"
            "        MIN(SNAPSHOT_DATE) AS STREAK_START_DATE,\n"
            "        MAX(SNAPSHOT_DATE) AS STREAK_END_DATE,\n"
            "        COUNT(*) AS CONSECUTIVE_NEGATIVE_DAYS,\n"
            "        AVG(CLOSING_BALANCE) AS AVG_OVERDRAFT_AMOUNT\n"
            "    FROM islands\n"
            "    GROUP BY CUSTOMER_ID, ISLAND_GROUP_KEY\n"
            "    HAVING COUNT(*) >= 7\n"
            ")\n"
            "SELECT * FROM streak_aggregates \n"
            "ORDER BY CONSECUTIVE_NEGATIVE_DAYS DESC, CUSTOMER_ID;\n"
            "```\n\n"
            "2. Performance Optimization:\n"
            "Ensuring a composite clustering key or index on `(CLOSING_BALANCE, CUSTOMER_ID, SNAPSHOT_DATE)` eliminates 95% of positive rows at the storage scan stage."
        ),
        "interviewer_tip": "Clearly articulate why self-joins fail on large tables: an iterative self-join on 100M rows would trigger an astronomical quadratic complexity $O(N^2)$, whereas the window function approach runs in linear $O(N \\log N)$ time.",
        "follow_up_question": "What if a customer has missing date rows on bank holidays?",
        "follow_up_answer": (
            "We join with a contiguous `DIM_DATE` table using `PARTITION BY CUSTOMER_ID` or fill missing dates using SQL `WINDOW LAG()`. "
            "If business logic defines 'consecutive business days', we sequence by `BUSINESS_DAY_INDEX` rather than raw calendar dates."
        )
    },
    {
        "id": "sql_02",
        "domain": "Advanced SQL",
        "category": "Advanced SQL",
        "source_badge": "HackerRank Hard | Goldman Sachs Wealth Mgmt 2026",
        "scenario": (
            "A corporate banking conglomerate has an N-tier hierarchical subsidiary structure (`COMPANY_HIERARCHY`: `PARENT_COMPANY_ID`, `SUBSIDIARY_ID`, `OWNERSHIP_PERCENTAGE`). "
            "You must write an analytical SQL query using Recursive Common Table Expressions (CTEs) to compute the effective ultimate beneficial ownership (UBO) "
            "of a target company across all indirect intermediate shell holding companies, while guarding against infinite circular loops."
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "मोठ्या कंपन्यांचे हजारो लहान कंपन्यांमध्ये शेअर असतात (जसे A कंपनी कडे B चे ६०% आहेत, आणि B कडे C चे ५०% आहेत, तर A कडे C ची खरी मालकी ६०% x ५०% = ३०% होते). "
            "आपल्याला Recursive CTE द्वारे शेवटच्या मूळ मालकाची (Ultimate Beneficial Ownership) टक्केवारी काढायची आहे. "
            "तसेच जर कंपन्यांनी एकमेकांमध्ये शेअर्स गुंतवले असतील (Circular Loop: A -> B -> C -> A), तर क्वेरी अनंत काळ अडकू नये म्हणून सायकल कशी थांबवायची?"
        ),
        "in_depth_answer": (
            "Production Solution with Recursive CTE & Loop Protection:\n\n"
            "1. Multiplicative Ownership Chain:\n"
            "We construct an anchor member finding direct ownership, and a recursive member multiplying intermediate percentages along the path. "
            "We track visited nodes in an array or string to detect circular references.\n\n"
            "```sql\n"
            "WITH RECURSIVE ownership_tree AS (\n"
            "    -- Anchor Member: Direct Parent Relationships\n"
            "    SELECT \n"
            "        PARENT_COMPANY_ID AS ROOT_OWNER,\n"
            "        SUBSIDIARY_ID AS CURRENT_ENTITY,\n"
            "        CAST(OWNERSHIP_PERCENTAGE / 100.0 AS DECIMAL(18, 6)) AS EFFECTIVE_STAKE,\n"
            "        1 AS DEPTH,\n"
            "        ARRAY_CONSTRUCT(PARENT_COMPANY_ID, SUBSIDIARY_ID) AS VISITED_PATH\n"
            "    FROM COMPANY_HIERARCHY\n"
            "    WHERE PARENT_COMPANY_ID = 'COMP_ROOT_001'\n\n"
            "    UNION ALL\n\n"
            "    -- Recursive Member: Traverse downstream subsidiaries\n"
            "    SELECT \n"
            "        tree.ROOT_OWNER,\n"
            "        child.SUBSIDIARY_ID AS CURRENT_ENTITY,\n"
            "        CAST(tree.EFFECTIVE_STAKE * (child.OWNERSHIP_PERCENTAGE / 100.0) AS DECIMAL(18, 6)),\n"
            "        tree.DEPTH + 1,\n"
            "        ARRAY_APPEND(tree.VISITED_PATH, child.SUBSIDIARY_ID)\n"
            "    FROM ownership_tree tree\n"
            "    JOIN COMPANY_HIERARCHY child \n"
            "      ON tree.CURRENT_ENTITY = child.PARENT_COMPANY_ID\n"
            "    WHERE tree.DEPTH < 12 -- Guard 1: Hard depth boundary\n"
            "      AND NOT ARRAY_CONTAINS(child.SUBSIDIARY_ID::VARIANT, tree.VISITED_PATH) -- Guard 2: Circular Loop Breaker\n"
            ")\n"
            "SELECT \n"
            "    ROOT_OWNER,\n"
            "    CURRENT_ENTITY AS BENEFICIARY_COMPANY,\n"
            "    SUM(EFFECTIVE_STAKE) * 100.0 AS TOTAL_EFFECTIVE_OWNERSHIP_PCT,\n"
            "    MAX(DEPTH) AS MAX_INTERMEDIARY_HOPS\n"
            "FROM ownership_tree\n"
            "GROUP BY ROOT_OWNER, CURRENT_ENTITY\n"
            "ORDER BY TOTAL_EFFECTIVE_OWNERSHIP_PCT DESC;\n"
            "```\n\n"
            "2. AML & Sanctions Integration:\n"
            "Regulators (FATF / RBI) flag any entity where a sanctioned root owner controls $\\ge 25\\%$ effective stake."
        ),
        "interviewer_tip": "Point out the `NOT ARRAY_CONTAINS()` check. Without cycle detection, malicious money launderers creating circular holding structures would cause the SQL engine to crash with infinite recursion limit errors.",
        "follow_up_question": "What if Snowflake throws 'Maximum recursion level 100 exceeded'?",
        "follow_up_answer": (
            "We tune `tree.DEPTH < 15` in the WHERE clause. If genuine graph depth exceeds 15 levels, we materialize adjacency lists into a dedicated graph table or run Pregel/GraphX algorithms in Spark."
        )
    },
    {
        "id": "sql_03",
        "domain": "Advanced SQL",
        "category": "Advanced SQL",
        "source_badge": "Top Hackathon Finalist | Standard Chartered EOD 2026",
        "scenario": (
            "You are designing an End-of-Day (EOD) financial reconciler. Each customer has debit and credit transactions. "
            "You must compute: (1) Running cumulative balance per customer, (2) Peak overdraft exposure reached within the billing cycle, "
            "and (3) Exact timestamp when balance first dipped below zero. All three metrics must be evaluated in a single SQL pass without subquery joins."
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेच्या दिवसाअखेरच्या (EOD) प्रक्रियेत प्रत्येक ग्राहकाचे ट्रॅन्झॅक्शन्स तपासून ३ गोष्टी काढायच्या आहेत:\n"
            "१. चालू शिल्लक रक्कम (Running Cumulative Balance)\n"
            "२. त्या महिन्यातील सर्वात जास्त ओव्हरड्राफ्ट (Peak Overdraft)\n"
            "३. खात्यातील पैसे सर्वात पहिल्यांदा कोणत्या सेकंदाला शून्य खाली गेले तो टाईमस्टॅम्प.\n"
            "हे सर्व एकाच SQL पासमध्ये करायचे आहे, कोणताही दुहेरी सबक्वेरी जॉईन न वापरता!"
        ),
        "in_depth_answer": (
            "Single-Pass Window Function Formulation:\n\n"
            "```sql\n"
            "WITH running_ledger AS (\n"
            "    SELECT \n"
            "        TXN_ID,\n"
            "        CUSTOMER_ID,\n"
            "        TXN_TIMESTAMP,\n"
            "        AMOUNT,\n"
            "        -- Metric 1: Running Balance via Frame Spec\n"
            "        SUM(AMOUNT) OVER(\n"
            "            PARTITION BY CUSTOMER_ID \n"
            "            ORDER BY TXN_TIMESTAMP, TXN_ID\n"
            "            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW\n"
            "        ) AS RUNNING_BALANCE\n"
            "    FROM TRANSACTIONS_LEDGER\n"
            "    WHERE TXN_DATE BETWEEN '2026-10-01' AND '2026-10-31'\n"
            "),\n"
            "annotated_metrics AS (\n"
            "    SELECT \n"
            "        CUSTOMER_ID,\n"
            "        TXN_TIMESTAMP,\n"
            "        RUNNING_BALANCE,\n"
            "        -- Metric 2: Minimum balance seen so far (Peak Overdraft)\n"
            "        MIN(RUNNING_BALANCE) OVER(\n"
            "            PARTITION BY CUSTOMER_ID\n"
            "        ) AS PEAK_NEGATIVE_EXPOSURE,\n"
            "        -- Metric 3: First timestamp when balance < 0\n"
            "        MIN(CASE WHEN RUNNING_BALANCE < 0 THEN TXN_TIMESTAMP END) OVER(\n"
            "            PARTITION BY CUSTOMER_ID\n"
            "        ) AS FIRST_BREACH_TIMESTAMP\n"
            "    FROM running_ledger\n"
            ")\n"
            "SELECT \n"
            "    CUSTOMER_ID,\n"
            "    PEAK_NEGATIVE_EXPOSURE,\n"
            "    FIRST_BREACH_TIMESTAMP,\n"
            "    -- Final closing balance at end of month\n"
            "    MAX(CASE WHEN rn = 1 THEN RUNNING_BALANCE END) AS MONTH_END_CLOSING_BALANCE\n"
            "FROM (\n"
            "    SELECT *, ROW_NUMBER() OVER(PARTITION BY CUSTOMER_ID ORDER BY TXN_TIMESTAMP DESC) as rn\n"
            "    FROM annotated_metrics\n"
            ")\n"
            "GROUP BY CUSTOMER_ID, PEAK_NEGATIVE_EXPOSURE, FIRST_BREACH_TIMESTAMP;\n"
            "```\n\n"
            "Key Insight: Using `ROWS BETWEEN` is 10x faster than `RANGE BETWEEN` because it avoids building peer group values in memory."
        ),
        "interviewer_tip": "Always mention `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. By default, standard SQL uses `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, which forces disk buffering for duplicate timestamps.",
        "follow_up_question": "What if two transactions have the exact same millisecond timestamp?",
        "follow_up_answer": (
            "We add `TXN_ID` as a deterministic tie-breaker in the ORDER BY clause: `ORDER BY TXN_TIMESTAMP, TXN_ID`. "
            "Without this, results are non-deterministic across cluster restarts."
        )
    },
    {
        "id": "sql_04",
        "domain": "Advanced SQL",
        "category": "Advanced SQL",
        "source_badge": "LeetCode Database Hard | Citi Enterprise Ledger 2026",
        "scenario": (
            "A critical 5-table join query in Snowflake was running in 12 seconds yesterday, but today takes 48 minutes and spills 450GB "
            "to remote storage. Looking at the Snowflake Query Profile, you notice an explosion from 2M rows to 1.8 billion intermediate rows "
            "after joining `ACCOUNTS` and `TRANSACTIONS`. What caused this Cartesian explosion and how do you profile and fix it?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "कालपर्यंत जी SQL क्वेरी १२ सेकंदात धावत होती, ती आज अचानक ४८ मिनिटे घेत आहे आणि तिने ४५०GB डेटा हार्ड डिस्कवर (Remote Disk Spilling) फेकला आहे. "
            "Snowflake Query Profile मध्ये पाहिले तर समजले की २ लाख रो ऐवजी १.८ अब्ज रो तयार झाल्या (Cartesian Explosion). "
            "हे का घडले? (नक्कीच जॉईन कॉलममध्ये एकापेक्षा जास्त डुप्लिकेट आयडी आले आहेत) आणि Query Profile वाचून हे दुरुस्त कसे करायचे?"
        ),
        "in_depth_answer": (
            "Production Diagnosis & Resolution:\n\n"
            "1. Root Cause Identification via Query Profile:\n"
            "- Step 1: Inspect the operator tree. Find the node where row count spikes by 900x.\n"
            "- Step 2: In banking datasets, this typically happens when an upstream batch inserted duplicate surrogate keys or a `NULL` key on join column `ACCOUNT_KEY`.\n"
            "- In standard SQL, `NULL = NULL` is false, but in an incorrectly written join or outer join coalesced with `'UNKNOWN'`, thousands of unassigned transactions join with thousands of unassigned account records, producing $N \\times M$ explosive Cartesian rows.\n\n"
            "2. Forensic Audit Query:\n"
            "```sql\n"
            "-- Detect duplicate join keys in upstream staging\n"
            "SELECT ACCOUNT_KEY, COUNT(*)\n"
            "FROM STG_ACCOUNTS\n"
            "GROUP BY ACCOUNT_KEY\n"
            "HAVING COUNT(*) > 1;\n"
            "```\n\n"
            "3. Production SQL Resolution:\n"
            "Enforce 1-to-many cardinality by deduplicating dimension keys using window qualifications before joining:\n\n"
            "```sql\n"
            "WITH deduped_accounts AS (\n"
            "    SELECT *\n"
            "    FROM DIM_ACCOUNTS\n"
            "    QUALIFY ROW_NUMBER() OVER(PARTITION BY ACCOUNT_ID ORDER BY VALID_FROM_TIMESTAMP DESC) = 1\n"
            ")\n"
            "SELECT \n"
            "    t.TXN_ID,\n"
            "    t.AMOUNT,\n"
            "    a.BRANCH_NAME\n"
            "FROM FACT_TRANSACTIONS t\n"
            "INNER JOIN deduped_accounts a \n"
            "   ON t.ACCOUNT_ID = a.ACCOUNT_ID;\n"
            "```"
        ),
        "interviewer_tip": "Mention 'Remote Spilling'. When Snowflake exhausts local SSD cache on the virtual warehouse, it spills partitions to remote cloud object storage (S3), degrading I/O throughput by orders of magnitude.",
        "follow_up_question": "Would increasing warehouse size from Medium to 2X-Large permanently solve this?",
        "follow_up_answer": (
            "No! Upgrading warehouse size is an expensive anti-pattern for bad SQL logic. While 2X-Large gives more memory, "
            "the underlying Cartesian join will continue growing quadratically with tomorrow's data delta, burning thousands of cloud credits."
        )
    },
    {
        "id": "sql_05",
        "domain": "Advanced SQL",
        "category": "Advanced SQL",
        "source_badge": "HackerRank Hard | HSBC FX Treasury 2026",
        "scenario": (
            "Treasury operations receives a real-time stream of foreign exchange trades across 25 currency pairs (USD, EUR, GBP, JPY, INR...). "
            "You need to produce a consolidated currency exposure cross-tab matrix where rows are trading desks and columns are dynamic currency symbols. "
            "How do you write a dynamic PIVOT query in Snowflake, and how do you handle newly introduced currency tokens without hardcoding columns?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "ट्रेझरी विभागात २५ वेगवेगळ्या चलनांमध्ये (USD, EUR, INR, GBP...) व्यवहार होतात. आपल्याला एक क्रॉस-टॅब रिपोर्ट बनवायचा आहे ज्यामध्ये "
            "डाव्या बाजूला ट्रेडिंग डेस्कची नावे आणि वरच्या स्तंभांमध्ये (columns) चलनाचा कोड असायला हवा. "
            "पण उद्या जर नवीन करन्सी (उदा. SGD किंवा AED) ॲड झाली, तर SQL कोडमध्ये बदल न करता ती आपोआप नवीन कॉलम कशी बनेल? (Dynamic PIVOT किंवा JSON Aggregation द्वारे)"
        ),
        "in_depth_answer": (
            "Production Solution with Dynamic Snowflake PIVOT & Object Aggregation:\n\n"
            "Method 1: Native Snowflake PIVOT (When columns are known at query execution):\n"
            "```sql\n"
            "SELECT * \n"
            "FROM (\n"
            "    SELECT TRADING_DESK, CURRENCY_CODE, NET_EXPOSURE_AMOUNT\n"
            "    FROM FX_TRADE_BOOKINGS\n"
            ")\n"
            "PIVOT(SUM(NET_EXPOSURE_AMOUNT) FOR CURRENCY_CODE IN ('USD', 'EUR', 'GBP', 'INR', 'JPY', 'AED'))\n"
            "AS p(DESK, USD_EXP, EUR_EXP, GBP_EXP, INR_EXP, JPY_EXP, AED_EXP);\n"
            "```\n\n"
            "Method 2: 100% Dynamic Schema-Free Solution via JSON Object Aggregation:\n"
            "To support newly added currencies automatically without changing DDL:\n\n"
            "```sql\n"
            "WITH aggregated_currencies AS (\n"
            "    SELECT \n"
            "        TRADING_DESK,\n"
            "        OBJECT_AGG(CURRENCY_CODE, SUM(NET_EXPOSURE_AMOUNT)::VARIANT) AS EXPOSURE_JSON\n"
            "    FROM FX_TRADE_BOOKINGS\n"
            "    GROUP BY TRADING_DESK\n"
            ")\n"
            "SELECT \n"
            "    TRADING_DESK,\n"
            "    EXPOSURE_JSON:USD::FLOAT AS USD_EXPOSURE,\n"
            "    EXPOSURE_JSON:EUR::FLOAT AS EUR_EXPOSURE,\n"
            "    EXPOSURE_JSON:INR::FLOAT AS INR_EXPOSURE,\n"
            "    EXPOSURE_JSON -- Full dynamic JSON containing all unknown long-tail currencies\n"
            "FROM aggregated_currencies;\n"
            "```"
        ),
        "interviewer_tip": "Demonstrating `OBJECT_AGG()` proves modern Lakehouse proficiency. Traditional relational databases force stored procedure string concatenation for dynamic pivots, while Snowflake natively supports semi-structured object transformations.",
        "follow_up_question": "How do you output this dynamic JSON as separate flat columns in PowerBI or Tableau?",
        "follow_up_answer": (
            "We expose a Snowflake View utilizing `FLATTEN()` or create a scheduled stored procedure that queries `DISTINCT CURRENCY_CODE` "
            "and dynamically recreates the flat view DDL whenever a new currency code enters the catalog."
        )
    },

    # =========================================================================
    # DOMAIN 3: LAKEHOUSE ARCHITECTURE
    # =========================================================================
    {
        "id": "arch_01",
        "domain": "Lakehouse Architecture",
        "category": "Lakehouse Architecture",
        "source_badge": "Barclays Enterprise Architect 2026",
        "scenario": (
            "At Utkarsh Small Finance Bank, you architected an end-to-end Medallion Lakehouse on Snowflake and AWS S3 processing 50GB daily delta. "
            "Explain your precise architectural boundaries, data contracts, and SLA guarantees between L0 (Bronze Raw Landing), "
            "L1 (Silver Conformed & Cleansed), and L2 (Gold Curated Analytics Marts)."
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "उत्कर्ष स्मॉल फायनान्स बँकेत तुम्ही ५०GB दैनंदिन डेटासाठी Snowflake आणि AWS S3 वर 'Medallion Architecture' डिझाइन केले होते. "
            "L0 (Raw Bronze), L1 (Silver Cleansed) आणि L2 (Gold Curated Mart) या तीन लेयर्समधील अचूक फरक, डेटा नियम आणि SLA (Service Level Agreement) "
            "कसे ठरवले होते? कोणत्या लेयरमध्ये काय ट्रान्सफॉर्मेशन होते हे सविस्तर सांगा."
        ),
        "in_depth_answer": (
            "Enterprise Medallion Architecture Specification:\n\n"
            "1. L0 Raw Layer (Bronze - Immutable Landing):\n"
            "- Source: Finacle CBS daily dumps delivered to S3 Bucket via SFTP.\n"
            "- Ingestion: Snowpipe auto-ingests into Snowflake Variant/Raw staging tables.\n"
            "- Rule: Zero transformations. Preserves exact upstream raw payload with metadata columns:\n"
            "  `_METADATA_FILENAME`, `_METADATA_ROW_ID`, `_INGESTION_TIMESTAMP`.\n"
            "- Retention: 90-day Time Travel / Permanent archival in S3 Glacier Instant Retrieval for RBI compliance audits.\n\n"
            "2. L1 Conformed Layer (Silver - Deduplicated Truth):\n"
            "- Mechanism: Snowflake Streams on L0 trigger automated Snowflake Tasks every 15 minutes.\n"
            "- Logic: Schema enforcement, type casting, currency normalization (PAISE to RUPEES), and deduplication using `QUALIFY ROW_NUMBER() = 1`.\n"
            "- Data Quality: Enforces foreign key referential integrity against Master Account tables.\n\n"
            "3. L2 Business Mart Layer (Gold - Curated Consumption):\n"
            "- Delivery: Dimensional Kimball Star Schema models (`FACT_TRANSACTIONS`, `DIM_CUSTOMER`, `DIM_BRANCH`).\n"
            "- Target Consumers: PowerBI Executive Dashboards, AML Surveillance engines, Core Reconcilers.\n"
            "- SLA: 06:00 AM IST daily delivery guarantee with automated failure alerting."
        ),
        "interviewer_tip": "Emphasize that L0 is strictly append-only. If a downstream pipeline has a logic error, the entire Lakehouse can be replayed from L0 raw data without asking upstream core banking teams to re-extract files.",
        "follow_up_question": "How do you prevent schema drift when Finacle adds a new column in L0?",
        "follow_up_answer": (
            "L0 stores the payload as semi-structured `VARIANT` or enables Snowflake's `ENABLE_SCHEMA_EVOLUTION = TRUE` on the target table. "
            "New columns are safely ingested into L0 without crashing, while an alert notifies the data team to map the column in L1."
        )
    },
    {
        "id": "arch_02",
        "domain": "Lakehouse Architecture",
        "category": "Lakehouse Architecture",
        "source_badge": "Amazon AWS Principal DE 2026",
        "scenario": (
            "Your enterprise Lakehouse is suffering from the classic 'Small File Problem': upstream IoT and CDC pipelines write 50,000 "
            "tiny 15KB Parquet files per hour into AWS S3. Queries on Athena and Snowflake have slowed down by 800% due to metadata explosion. "
            "How do you design an automated, cost-efficient file compaction and maintenance engine?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "दर तासाला ५०,००० लहान-लहान (१५ KB) च्या फाईल्स S3 वर जमा होत आहेत. यामुळे फाईल्सची संख्या लाखो झाली असून Athena आणि Snowflake मध्ये "
            "क्वेरी प्रचंड स्लो झाली आहे (कारण स्टोरेज इंजिनला लाखो फाईल्सचे मेटाडेटा ओपन करावे लागतात). "
            "या 'Small File Problem' ला सोडवण्यासाठी बॅकग्राउंडमध्ये फाईल्स एकत्र करून (Compaction) १२८MB-२५६MB च्या मोठ्या फाईल्स कशा बनवायच्या?"
        ),
        "in_depth_answer": (
            "Automated Lakehouse Compaction Architecture:\n\n"
            "1. Architectural Strategy:\n"
            "Optimal Parquet reading performance occurs when file size aligns with the file system block size: between 128MB and 512MB. "
            "Having millions of 15KB files wastes CPU time opening and closing S3 connections.\n\n"
            "2. Automated Compaction Mechanism via AWS Glue / EMR Serverless:\n"
            "```python\n"
            "# Scheduled PySpark Compaction Job\n"
            "def compact_partition(s3_partition_path: str):\n"
            "    df = spark.read.parquet(s3_partition_path)\n"
            "    \n"
            "    # Calculate optimal partition count targeting 256MB file size\n"
            "    total_bytes = sum([f.size for f in spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration()).listStatus(spark._jvm.org.apache.hadoop.fs.Path(s3_partition_path))])\n"
            "    target_file_count = max(1, int(total_bytes / (256 * 1024 * 1024)))\n\n"
            "    # Repartition and overwrite staging partition atomically\n"
            "    df.coalesce(target_file_count) \\\n"
            "      .write \\\n"
            "      .mode('overwrite') \\\n"
            "      .parquet(s3_partition_path + '_compacted')\n"
            "```\n\n"
            "3. Snowflake Native Solution:\n"
            "If tables are managed inside Snowflake, automated background micro-partition re-clustering handles compaction natively, "
            "merging adjacent micro-partitions into standard 16MB-compressed blocks without manual user scripts."
        ),
        "interviewer_tip": "Distinguish between `repartition()` and `coalesce()`. `coalesce()` avoids a full network shuffle by collapsing existing partitions, making it 5x faster and cheaper for compaction.",
        "follow_up_question": "How do you prevent data loss if a query reads the partition while compaction is overwriting it?",
        "follow_up_answer": (
            "We use table formats supporting ACID snapshots like Apache Iceberg or Delta Lake. The compaction job commits a new snapshot metadata manifest atomically. "
            "Concurrent readers continue reading the previous snapshot until the new compacted manifest is published."
        )
    },
    {
        "id": "arch_03",
        "domain": "Lakehouse Architecture",
        "category": "Lakehouse Architecture",
        "source_badge": "Citi Fraud Surveillance 2026",
        "scenario": (
            "Your banking fraud team currently uses a traditional Lambda Architecture (Batch layer with daily EOD scripts + Speed layer with Storm/Flink). "
            "They are plagued by code duplication where business logic must be maintained twice in two different languages (Python & Java). "
            "How do you migrate this to a unified Kappa Architecture using Kafka and Snowflake Dynamic Tables?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेच्या फ्रॉड डिटेक्शनसाठी सध्या 'Lambda Architecture' वापरले जाते—म्हणजे रात्री चालणारा बॅच कोड Python मध्ये आहे, आणि रिअल-टाईम चालणारा कोड Java/Flink मध्ये आहे. "
            "दोन्ही ठिकाणी एकाच बिझनेस लॉजिकचे दोन वेगळे कोड मेन्टेन करावे लागतात, ज्यामुळे चुका होतात. "
            "हा जुना Lambda पॅटर्न काढून 'Kappa Architecture' (एकच अखंड स्ट्रीमिंग डेटा पाईप) द्वारे Kafka आणि Snowflake Dynamic Tables वापरून सोपे कसे करायचे?"
        ),
        "in_depth_answer": (
            "Migration from Lambda to Kappa Architecture:\n\n"
            "1. Architectural Flaw of Lambda:\n"
            "Lambda requires reconciling two divergent codebases (batch reconciliation vs stream alerts). Inevitably, floating-point rounding or timestamp drift "
            "causes batch numbers to disagree with real-time stream numbers.\n\n"
            "2. Kappa Unified Architecture with Snowflake Dynamic Tables:\n"
            "- Single Ingestion Channel: All core banking events land into Apache Kafka / Amazon MSK as immutable event streams.\n"
            "- Snowpipe Streaming: Direct low-latency streaming ingest from Kafka into Snowflake L0 tables ($<1$ second latency).\n"
            "- Dynamic Tables: Declarative SQL pipelines replace both Flink and Airflow batch DAGs. Snowflake manages continuous state tracking and incremental refresh:\n\n"
            "```sql\n"
            "CREATE OR REPLACE DYNAMIC TABLE DT_CARD_FRAUD_SURVEILLANCE\n"
            "TARGET_LAG = '1 minute'\n"
            "WAREHOUSE = COMPUTE_WH\n"
            "AS\n"
            "SELECT \n"
            "    CARD_NUMBER,\n"
            "    COUNT(*) AS TXN_COUNT_5MIN,\n"
            "    SUM(AMOUNT) AS TOTAL_SPENT_5MIN,\n"
            "    ARRAY_UNIQUE_AGG(MERCHANT_CITY) AS UNIQUE_CITIES\n"
            "FROM STREAM_CARD_TRANSACTIONS\n"
            "WHERE TXN_TIMESTAMP >= DATEADD('minute', -5, CURRENT_TIMESTAMP())\n"
            "GROUP BY CARD_NUMBER\n"
            "HAVING COUNT(*) >= 3 AND ARRAY_SIZE(UNIQUE_CITIES) >= 2;\n"
            "```\n\n"
            "3. Outcome:\n"
            "Single codebase in pure declarative SQL. Eliminates dual-language maintenance overhead."
        ),
        "interviewer_tip": "Highlight `TARGET_LAG`. Setting `TARGET_LAG = '1 minute'` tells Snowflake to refresh incrementally as data arrives, automatically falling back to full refresh only if downstream dependencies fail.",
        "follow_up_question": "What is the cost trade-off of TARGET_LAG = '1 minute' versus TARGET_LAG = '1 hour'?",
        "follow_up_answer": (
            "A 1-minute lag keeps the warehouse actively spinning to check stream metadata, consuming continuous cloud credits. "
            "For non-critical analytics, setting `TARGET_LAG = '15 minutes'` or `'DOWNSTREAM'` reduces Snowflake warehouse compute costs by up to 70%."
        )
    },
    {
        "id": "arch_04",
        "domain": "Lakehouse Architecture",
        "category": "Lakehouse Architecture",
        "source_badge": "Goldman Sachs Private Wealth 2026",
        "scenario": (
            "You are designing a Multi-Tenant Banking Lakehouse where 40 regional rural bank (RRB) partner institutions share the same "
            "Snowflake Lakehouse instance. How do you implement Row Access Policies (RAP) and Tag-Based Dynamic Masking to ensure strict tenant isolation, "
            "so no bank can ever query another bank's records even if their analysts run `SELECT * FROM FACT_TRANSACTIONS`?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "एकाच Snowflake डेटाबेसमध्ये ४० वेगवेगळ्या बँकांचा डेटा साठवला आहे. पण बँक A च्या ॲनालिस्टने `SELECT *` क्वेरी मारली, "
            "तरी त्याला फक्त बँक A चाच डेटा दिसला पाहिजे; बँक B किंवा C चा डेटा अजिबात दिसू नये. "
            "तसेच PAN नंबर आणि आधार कार्ड नंबर आपोआप मास्क (उदा. XXXXX1234) झाले पाहिजेत. "
            "Snowflake चे Row Access Policy (RAP) आणि Dynamic Data Masking कसे लागू करायचे?"
        ),
        "in_depth_answer": (
            "Multi-Tenant Isolation via Row Access Policy (RAP) & Tag Masking:\n\n"
            "1. Row Access Policy (RAP) Implementation:\n"
            "A Row Access Policy is a schema-level object that evaluates the current user's session role and matches it against an entitlement mapping table.\n\n"
            "```sql\n"
            "-- Step 1: Entitlement Mapping Table\n"
            "CREATE TABLE SECURITY_ADMIN.TENANT_ROLE_MAPPING (\n"
            "    ROLE_NAME VARCHAR(100),\n"
            "    ALLOWED_BANK_CODE VARCHAR(20)\n"
            ");\n\n"
            "-- Step 2: Define Row Access Policy\n"
            "CREATE OR REPLACE ROW ACCESS POLICY SECURITY_ADMIN.TENANT_ISOLATION_POLICY\n"
            "AS (BANK_CODE VARCHAR) RETURNS BOOLEAN ->\n"
            "    CURRENT_ROLE() = 'GLOBAL_SECURITY_ADMIN' OR\n"
            "    EXISTS (\n"
            "        SELECT 1 FROM SECURITY_ADMIN.TENANT_ROLE_MAPPING\n"
            "        WHERE ROLE_NAME = CURRENT_ROLE()\n"
            "          AND ALLOWED_BANK_CODE = BANK_CODE\n"
            "    );\n\n"
            "-- Step 3: Attach Policy to Production Fact Table\n"
            "ALTER TABLE CORE_BANKING.FACT_TRANSACTIONS\n"
            "ADD ROW ACCESS POLICY SECURITY_ADMIN.TENANT_ISOLATION_POLICY ON (BANK_CODE);\n"
            "```\n\n"
            "2. Tag-Based Dynamic Column Masking for PII:\n"
            "```sql\n"
            "-- Masking Policy for Aadhaar / SSN\n"
            "CREATE OR REPLACE MASKING POLICY SECURITY_ADMIN.MASK_AADHAAR\n"
            "AS (VAL VARCHAR) RETURNS VARCHAR ->\n"
            "    CASE \n"
            "        WHEN CURRENT_ROLE() IN ('COMPLIANCE_OFFICER_ROLE') THEN VAL\n"
            "        ELSE CONCAT('XXXX-XXXX-', RIGHT(VAL, 4))\n"
            "    END;\n\n"
            "-- Apply Masking Policy Tag\n"
            "CREATE TAG SECURITY_ADMIN.PII_SENSITIVE;\n"
            "ALTER TAG SECURITY_ADMIN.PII_SENSITIVE SET MASKING POLICY SECURITY_ADMIN.MASK_AADHAAR;\n"
            "ALTER TABLE CORE_BANKING.DIM_CUSTOMERS MODIFY COLUMN AADHAAR_NUMBER SET TAG SECURITY_ADMIN.PII_SENSITIVE = 'HIGH';\n"
            "```"
        ),
        "interviewer_tip": "Mention that Row Access Policies are evaluated at the optimizer stage and pushed down into micro-partition pruning. Non-permitted bank partitions are never read from disk, saving query execution time and credit usage.",
        "follow_up_question": "Can an analyst bypass the RAP by writing a subquery or CTE?",
        "follow_up_answer": (
            "No. Snowflake injects Row Access Policy predicates into the physical execution plan at the storage engine level. "
            "Even if the analyst writes nested CTEs, joins, or views, the filter predicate `BANK_CODE = CURRENT_BANK` is strictly enforced."
        )
    },
    {
        "id": "arch_05",
        "domain": "Lakehouse Architecture",
        "category": "Lakehouse Architecture",
        "source_badge": "Snowflake Engineering Labs 2026",
        "scenario": (
            "Your executive team wants to expose Lakehouse data to external business partners without granting them direct database credentials "
            "or exporting CSV files via SFTP. How do you implement Snowflake Secure Data Sharing and Clean Rooms while maintaining zero-copy data protection "
            "and preventing partners from seeing non-aggregated individual customer transactions?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेच्या पार्टनर कंपन्यांना (उदा. क्रेडिट कार्ड कंपन्या किंवा इन्शुरन्स एजंट) डेटा द्यायचा आहे. पण त्यांना थेट डेटाबेसचा पासवर्ड द्यायचा नाही "
            "किंवा असुरक्षित CSV फाईल्स SFTP वर पाठवायच्या नाहीत. "
            "डेटाची दुसरी कॉपी न बनवता (Zero-Copy) Snowflake 'Secure Data Sharing' आणि 'Data Clean Rooms' द्वारे "
            "त्यांना फक्त एकत्रित (Aggregated) रिपोर्ट कसा दाखवायचा आणि खाजगी ग्राहक डेटा कसा लपवायचा?"
        ),
        "in_depth_answer": (
            "Production Solution via Snowflake Secure Views & Data Clean Room:\n\n"
            "1. Secure View Construction:\n"
            "Standard views allow users to inspect the underlying SQL execution plan via `EXPLAIN`, which could reveal sensitive data distributions. "
            "A `SECURE VIEW` suppresses optimizer internals and prevents query plan reverse-engineering.\n\n"
            "```sql\n"
            "CREATE OR REPLACE SECURE VIEW PARTNER_EXCHANGE.VW_PARTNER_CREDIT_ANALYTICS AS\n"
            "SELECT \n"
            "    POSTAL_PIN_CODE,\n"
            "    AGE_BRACKET,\n"
            "    COUNT(*) AS TOTAL_BORROWERS,\n"
            "    AVG(CREDIT_SCORE) AS AVG_CREDIT_BUREAU_SCORE,\n"
            "    SUM(TOTAL_LOAN_OUTSTANDING) AS AGGREGATE_LOAN_EXPOSURE\n"
            "FROM CORE_LAKEHOUSE.DIM_CUSTOMERS c\n"
            "JOIN CORE_LAKEHOUSE.FACT_LOANS l ON c.CUSTOMER_ID = l.CUSTOMER_ID\n"
            "GROUP BY POSTAL_PIN_CODE, AGE_BRACKET\n"
            "HAVING COUNT(*) >= 50; -- Differential privacy floor (prevents re-identification)\n"
            "```\n\n"
            "2. Direct Reader Account Share Creation:\n"
            "```sql\n"
            "-- Step 1: Create Share\n"
            "CREATE SHARE PARTNER_LOAN_INSIGHTS_SHARE;\n"
            "GRANT USAGE ON DATABASE PARTNER_EXCHANGE TO SHARE PARTNER_LOAN_INSIGHTS_SHARE;\n"
            "GRANT USAGE ON SCHEMA PARTNER_EXCHANGE.PUBLIC TO SHARE PARTNER_LOAN_INSIGHTS_SHARE;\n"
            "GRANT SELECT ON VIEW PARTNER_EXCHANGE.VW_PARTNER_CREDIT_ANALYTICS TO SHARE PARTNER_LOAN_INSIGHTS_SHARE;\n\n"
            "-- Step 2: Bind to Partner's Snowflake Account ID\n"
            "ALTER SHARE PARTNER_LOAN_INSIGHTS_SHARE ADD ACCOUNTS = 'xy12345.ap-south-1';\n"
            "```\n\n"
            "3. Zero-Copy Architecture:\n"
            "No data is copied or moved. The partner queries the live data via their own warehouse compute, meaning zero storage and compute cost for our bank."
        ),
        "interviewer_tip": "Highlight the `HAVING COUNT(*) >= 50` condition. This demonstrates privacy-preserving engineering: if a postal code only has 1 borrower, showing their average score reveals that individual's private data.",
        "follow_up_question": "What if the partner doesn't use Snowflake at all?",
        "follow_up_answer": (
            "Snowflake allows provisioning a managed 'Reader Account'. Our organization controls the reader account, provisions a virtual warehouse for the partner, "
            "and sets resource monitors to cap maximum credit spend."
        )
    },

    # =========================================================================
    # DOMAIN 4: DATA GOVERNANCE & METADATA MANAGEMENT
    # =========================================================================
    {
        "id": "gov_01",
        "domain": "Data Governance & Metadata",
        "category": "Data Governance & Metadata",
        "source_badge": "Citi Global Compliance 2026",
        "scenario": (
            "Under India's DPDP Act (Digital Personal Data Protection) and European GDPR, a customer exercises their 'Right to be Forgotten' "
            "requesting total deletion of all personal identifiers. However, banking regulations (RBI/PMLA) require retaining financial ledger "
            "transactions for 10 years for anti-money laundering investigations. How do you architect a cryptographic shredding solution to satisfy both laws?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "डेटा प्रायव्हसी कायद्यानुसार (DPDP / GDPR) ग्राहकाने बँक खाते बंद करताना सांगितले: 'माझा सर्व डेटा डिलीट करा' (Right to be Forgotten). "
            "पण RBI च्या नियमांनुसार बँकेला सर्व आर्थिक ट्रॅन्झॅक्शन्स पुढील १० वर्षे सांभाळावेच लागतात. "
            "दोन्ही नियमांचे एकाच वेळी पालन कसे करायचे? (यासाठी 'Crypto-Shredding' वापरतात—प्रत्येक ग्राहकाचा डेटा स्वतंत्र एनक्रिप्शन की ने लॉक करायचा, "
            "आणि ग्राहकाने डिलीट करायला सांगितल्यावर फक्त त्याची एनक्रिप्शन 'की' नष्ट करायची!)."
        ),
        "in_depth_answer": (
            "Crypto-Shredding Architectural Solution:\n\n"
            "1. Legal Conflict Resolution:\n"
            "- DPDP / GDPR requires that personal data (PII) must be unrecoverable upon request.\n"
            "- Banking Law (PMLA / RBI) mandates 10-year retention of anonymous transaction amounts, timestamps, and merchant codes.\n\n"
            "2. Crypto-Shredding Pattern:\n"
            "Instead of deleting ledger rows (which would corrupt financial audit balances), we encrypt all PII columns using an individual "
            "Customer-Specific Data Encryption Key (DEK). The DEKs are stored in an encrypted Key Management Vault (AWS KMS / HashiCorp Vault).\n\n"
            "```python\n"
            "# Production Crypto-Shredding Workflow\n"
            "def right_to_be_forgotten_handler(customer_id: str):\n"
            "    # 1. Fetch customer's individual key reference\n"
            "    key_alias = f'alias/cust_dek_{customer_id}'\n"
            "    \n"
            "    # 2. Cryptographically shred by destroying the KMS key permanently\n"
            "    kms_client.schedule_key_deletion(\n"
            "        KeyId=key_alias, \n"
            "        PendingWindowInDays=7\n"
            "    )\n"
            "    \n"
            "    # 3. Update Audit Ledger\n"
            "    log_compliance_audit(customer_id, action='CRYPTO_SHREDDED', timestamp=time.time())\n"
            "```\n\n"
            "3. Result:\n"
            "The transactional records remain intact in the Lakehouse with irreversible, mathematically unbreakable ciphertext. "
            "No human or computer can ever decrypt the customer's identity, achieving 100% GDPR/DPDP deletion compliance without breaking ledger integrity."
        ),
        "interviewer_tip": "Interviewers love the term 'Crypto-Shredding'. Mentioning that row deletion in immutable Parquet lakehouses requires costly partition rewrites, while crypto-shredding takes milliseconds in AWS KMS, demonstrates elite architecture depth.",
        "follow_up_question": "What happens if a backup snapshot contains the un-shredded Parquet files?",
        "follow_up_answer": (
            "Even if cold backup snapshots from 5 years ago are restored, the DEK in AWS KMS has been destroyed. "
            "The restored backup contains useless random noise ciphertext, maintaining compliance across all backups automatically."
        )
    },
    {
        "id": "gov_02",
        "domain": "Data Governance & Metadata",
        "category": "Data Governance & Metadata",
        "source_badge": "Morgan Stanley Governance 2026",
        "scenario": (
            "Your enterprise has 1,200 dbt models and 350 Airflow DAGs. A critical bug is reported in an L2 executive dashboard metric: "
            "`ADJUSTED_NET_INTEREST_MARGIN`. You need to perform end-to-end Column-Level Lineage tracking from the dashboard metric "
            "all the way back to the raw source tables in Finacle. How do you automate column-level lineage extraction?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेत १,२०० dbt मॉडेल्स आणि ३५० Airflow DAGs आहेत. एका महत्वाच्या एक्झिक्युटिव्ह डॅशबोर्डवर `ADJUSTED_NET_INTEREST_MARGIN` हा नंबर चुकीचा दिसतोय. "
            "हा नंबर कोणत्या मूळ Finacle टेबलमधून आला, वाटेत कोणत्या SQL ने बदलला, आणि डॅशबोर्डवर कसा पोहोचला, याचा संपूर्ण मार्ग (Column-Level Data Lineage) "
            "आपल्याला स्वयंचलितपणे शोधायचा आहे. हे dbt `manifest.json` आणि SQL AST पार्सरने कसे करायचे?"
        ),
        "in_depth_answer": (
            "Automated Column-Level Lineage Extraction Pipeline:\n\n"
            "1. Architecture of Column Lineage:\n"
            "Table-level lineage only tells you that Table A feeds Table B. Column-level lineage traces individual column dependencies "
            "through arithmetic expressions, window functions, and joins.\n\n"
            "2. Implementation via dbt Artifacts & SQLGlot AST:\n"
            "```python\n"
            "import json\n"
            "import sqlglot\n"
            "from sqlglot.lineage import lineage\n\n"
            "def trace_column_provenance(target_metric: str, dbt_manifest_path: str):\n"
            "    with open(dbt_manifest_path) as f:\n"
            "        manifest = json.load(f)\n"
            "    \n"
            "    # Extract compiled SQL for target mart\n"
            "    mart_node = manifest['nodes']['model.banking_lakehouse.fct_executive_financials']\n"
            "    compiled_sql = mart_node['compiled_code']\n"
            "    \n"
            "    # Parse AST and trace lineage graph\n"
            "    node_lineage = lineage(target_metric, compiled_sql)\n"
            "    \n"
            "    # Output upstream source lineage path\n"
            "    upstream_path = []\n"
            "    for upstream_node in node_lineage.walk():\n"
            "        upstream_path.append(f'{upstream_node.source_name}.{upstream_node.expression}')\n"
            "    \n"
            "    return upstream_path\n"
            "```\n\n"
            "3. Central Metadata Catalog Integration:\n"
            "The extracted lineage graph is ingested into OpenLineage / Marquez / Apache Atlas via REST API after every CI/CD deployment."
        ),
        "interviewer_tip": "Mention `SQLGlot`. It is the industry standard Python SQL parser capable of transpiling and generating AST lineage across Snowflake, BigQuery, and Postgres dialects.",
        "follow_up_question": "How do you detect lineage if a column is generated by a Python PySpark script rather than SQL?",
        "follow_up_answer": (
            "We use OpenLineage's Spark listener (`spark.extraListeners = io.openlineage.spark.agent.OpenLineageSparkListener`). "
            "The listener captures Spark's Catalyst optimizer execution plan at runtime and streams column inputs/outputs directly to our metadata catalog."
        )
    },
    {
        "id": "gov_03",
        "domain": "Data Governance & Metadata",
        "category": "Data Governance & Metadata",
        "source_badge": "JPMorgan Core Ledger 2026",
        "scenario": (
            "Your data pipeline ingests 2M loan records daily. Last week, a core banking code release began outputting `NULL` values "
            "in the `CUSTOMER_PAN_NUMBER` column. The pipeline continued running, silently corrupting downstream risk models for 4 days before anyone noticed. "
            "How do you build a Data Quality Circuit-Breaker using Great Expectations and dbt-expectations that halts the pipeline automatically?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "दररोज २० लाख कर्जाचे रेकॉर्ड्स येतात. एका दिवशी सिस्टिमच्या बगमुळे `CUSTOMER_PAN_NUMBER` कॉलममध्ये सगळे `NULL` येऊ लागले. "
            "पाईपलाईन चालूच राहिली आणि सलग ४ दिवस चुकीचा डेटा मुख्य रिपोर्टमध्ये भरला गेला. "
            "अशी चूक होताच पाईपलाईन जागेवरच थांबली पाहिजे (Circuit Breaker) आणि इंजिनिअरला तात्काळ अलर्ट गेला पाहिजे. "
            "हे Great Expectations किंवा dbt द्वारे कसे ऑटोमॅटिक करायचे?"
        ),
        "in_depth_answer": (
            "Production Circuit-Breaker Implementation:\n\n"
            "1. Architectural Principle:\n"
            "Never let bad data flow downstream. Ingest into an ephemeral staging buffer, evaluate assertion suites, and only promote to Silver/Gold "
            "if validation tests pass 100%.\n\n"
            "2. Great Expectations Check Suite:\n"
            "```python\n"
            "import great_expectations as gx\n\n"
            "def validate_staging_loans(df_staging):\n"
            "    context = gx.get_context()\n"
            "    validator = context.sources.add_or_get_pandas('loan_source').add_dataframe_asset('loans').build_batch_request(dataframe=df_staging)\n"
            "    \n"
            "    # Circuit-Breaker Assertions\n"
            "    v = context.get_validator(batch_request=validator)\n"
            "    v.expect_column_values_to_not_be_null('CUSTOMER_PAN_NUMBER', mostly=0.999)\n"
            "    v.expect_column_values_to_match_regex('CUSTOMER_PAN_NUMBER', r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')\n"
            "    v.expect_column_values_to_be_between('LOAN_AMOUNT', min_value=1000, max_value=50000000)\n"
            "    \n"
            "    results = v.validate()\n"
            "    if not results.success:\n"
            "        # Trigger Circuit Breaker: Halt DAG, alert on-call\n"
            "        raise RuntimeError(f'CIRCUIT BREAKER TRIGGERED: Quality check failed. {results.statistics}')\n"
            "```\n\n"
            "3. Airflow DAG Failure Hook:\n"
            "The exception trips the DAG task into `FAILED` state, halting all downstream Gold tables and dispatching an instant Telegram and SMTP alert."
        ),
        "interviewer_tip": "Highlight the `mostly=0.999` parameter. In production, 1 or 2 historical grandfathered records might lack a PAN, so a threshold of 99.9% prevents false-alarm pipeline stalls while catching catastrophic systemic NULL drops.",
        "follow_up_question": "What happens to the good records in the failed batch?",
        "follow_up_answer": (
            "We implement a Dead Letter Queue (DLQ) pattern: split the batch using conditional routing. "
            "Good records continue to an isolated staging area, while bad records are diverted to a quarantine table for manual compliance review."
        )
    },
    {
        "id": "gov_04",
        "domain": "Data Governance & Metadata",
        "category": "Data Governance & Metadata",
        "source_badge": "Barclays Metadata Mart 2026",
        "scenario": (
            "Your bank's Snowflake data warehouse has 2,500 tables. The Chief Data Officer mandates that all tables must have verified business descriptions, "
            "data owner tags, retention policies, and classification tiers. How do you implement automated metadata synchronization between "
            "Snowflake system views (`ACCOUNT_USAGE.TABLES`) and AWS Glue Data Catalog?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "Snowflake मध्ये २,५०० टेबल्स आहेत. बँकेच्या डेटा हेडने आदेश दिला की प्रत्येक टेबलला कोणाचा मालकी हक्क आहे (Data Owner), "
            "त्या टेबलमध्ये काय माहिती आहे (Description) आणि तो किती वर्षे ठेवायचा (Retention) हे स्पष्ट दिसले पाहिजे. "
            "हा सर्व मेटाडेटा Snowflake च्या इंटरनल व्ह्यूजमधून वाचून AWS Glue Data Catalog मध्ये आपोआप कसा सिंक करायचा?"
        ),
        "in_depth_answer": (
            "Automated Metadata Synchronization Engine:\n\n"
            "1. Snowflake Information Schema & Tag Extraction:\n"
            "We query Snowflake's metadata catalogs to harvest table definitions and object tags:\n\n"
            "```sql\n"
            "SELECT \n"
            "    t.TABLE_CATALOG AS DB_NAME,\n"
            "    t.TABLE_SCHEMA AS SCHEMA_NAME,\n"
            "    t.TABLE_NAME,\n"
            "    t.COMMENT AS TABLE_DESCRIPTION,\n"
            "    TAG_VALUE(t.TABLE_CATALOG || '.' || t.TABLE_SCHEMA || '.' || t.TABLE_NAME, 'TABLE', 'DATA_OWNER') AS DATA_OWNER,\n"
            "    TAG_VALUE(t.TABLE_CATALOG || '.' || t.TABLE_SCHEMA || '.' || t.TABLE_NAME, 'TABLE', 'CONFIDENTIALITY') AS TIER\n"
            "FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES t\n"
            "WHERE t.DELETED IS NULL;\n"
            "```\n\n"
            "2. AWS Glue Catalog Sync Daemon in Python:\n"
            "```python\n"
            "import boto3\n\n"
            "glue_client = boto3.client('glue', region_name='ap-south-1')\n\n"
            "def sync_table_to_glue(table_meta: dict):\n"
            "    glue_client.update_table(\n"
            "        DatabaseName=table_meta['SCHEMA_NAME'].lower(),\n"
            "        TableInput={\n"
            "            'Name': table_meta['TABLE_NAME'].lower(),\n"
            "            'Description': table_meta['TABLE_DESCRIPTION'] or 'Managed by Snowflake',\n"
            "            'Parameters': {\n"
            "                'data_owner': table_meta['DATA_OWNER'] or 'unassigned',\n"
            "                'classification_tier': table_meta['TIER'] or 'Confidential',\n"
            "                'last_synced': time.strftime('%Y-%m-%d %H:%M:%S')\n"
            "            }\n"
            "        }\n"
            "    )\n"
            "```"
        ),
        "interviewer_tip": "Highlight the latency of `ACCOUNT_USAGE` vs `INFORMATION_SCHEMA`. `ACCOUNT_USAGE` has a 45-minute latency but contains historical dropped objects, whereas `INFORMATION_SCHEMA` is real-time without latency.",
        "follow_up_question": "How do you enforce that a developer cannot create a new table without specifying a DATA_OWNER tag?",
        "follow_up_answer": (
            "We use Snowflake Tag-Based DDL policies or CI/CD gate checks in dbt: `dbt-checkpoint` or SQLFluff enforces that every model `.yml` "
            "file must contain a valid `owner:` and `tags:` block before merging into main."
        )
    },
    {
        "id": "gov_05",
        "domain": "Data Governance & Metadata",
        "category": "Data Governance & Metadata",
        "source_badge": "Utkarsh SFB & RBI Regulatory Audit 2026",
        "scenario": (
            "During a statutory Reserve Bank of India (RBI) regulatory audit, the inspectors demand proof that the interest calculation "
            "formula used in production on 2026-03-31 was identical to approved policy. They require you to reproduce the exact state "
            "of the customer ledger as of that specific minute, along with the Git commit hash of the Python/SQL code that calculated it. "
            "How do you satisfy this audit requirement?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "RBI च्या ऑडिट इन्स्पेक्टर्सनी विचारले: '३१ मार्च रोजी व्याज (Interest) ज्या फॉर्म्युल्याने मोजले होते, तोच फॉर्म्युला पॉलिसीनुसार होता का याचा पुरावा द्या. "
            "आणि त्या दिवशी त्या मिनिटाला डेटा नक्की कसा दिसत होता ते पुन्हा रन करून दाखवा, तसेच त्या दिवशी Git मध्ये कोणता कोड कमिट झालेला होता ते सांगा.' "
            "Snowflake Time Travel आणि Git Commit Hash टॅगिंग वापरून हा ऑडिट कसा पास करायचा?"
        ),
        "in_depth_answer": (
            "Audit Reproducibility via Snowflake Time Travel & Git Hashes:\n\n"
            "1. Immutable Code-to-Data Provenance:\n"
            "Every production pipeline run must inject the running Git commit SHA into the target table's metadata and execution ledger:\n\n"
            "```sql\n"
            "INSERT INTO AUDIT_LEDGER.PIPELINE_RUN_METADATA (\n"
            "    PIPELINE_NAME,\n"
            "    RUN_TIMESTAMP,\n"
            "    GIT_COMMIT_HASH,\n"
            "    AIRFLOW_DAG_ID,\n"
            "    FORMULA_VERSION\n"
            ") VALUES (\n"
            "    'CBS_INTEREST_CALCULATOR',\n"
            "    '2026-03-31 23:59:59',\n"
            "    '7f3a9e8b12f45c893012a',\n"
            "    'airflow_daily_eod_v4',\n"
            "    'RBI_CIRCULAR_2026_REV3'\n"
            ");\n"
            "```\n\n"
            "2. Precise Historical State Reproduction via Snowflake Time Travel:\n"
            "To prove the exact numerical state of the table on 2026-03-31 at 23:59:59 IST:\n\n"
            "```sql\n"
            "SELECT \n"
            "    ACCOUNT_NUMBER,\n"
            "    PRINCIPAL_BALANCE,\n"
            "    INTEREST_ACCRUED_INR,\n"
            "    APPLIED_INTEREST_RATE\n"
            "FROM CORE_BANKING.CUSTOMER_SAVINGS_LEDGER \n"
            "AT(TIMESTAMP => '2026-03-31 23:59:59'::TIMESTAMP_TZ);\n"
            "```\n\n"
            "3. Verification:\n"
            "The inspector verifies that Git commit `7f3a9e8b` matches the signed auditor release branch, and the Time Travel query proves the numbers."
        ),
        "interviewer_tip": "Mention that Snowflake Time Travel retention can be configured up to 90 days on Enterprise Edition. For requirements exceeding 90 days, we store periodic zero-copy cloned monthly snapshots (`CREATE TABLE ledger_20260331 CLONE ledger`).",
        "follow_up_question": "Does a zero-copy clone increase storage costs if the table isn't modified?",
        "follow_up_answer": (
            "No! A Zero-Copy Clone only duplicates the metadata pointers to the existing micro-partitions. "
            "It costs zero additional storage bytes until modifications occur on either the source or clone."
        )
    },

    # =========================================================================
    # DOMAIN 5: ROBUST ETL / ELT PIPELINES & CDC
    # =========================================================================
    {
        "id": "cdc_01",
        "domain": "ETL / ELT & CDC",
        "category": "ETL / ELT & CDC",
        "source_badge": "Barclays Core Banking 2026",
        "scenario": (
            "Your team currently extracts Finacle transaction updates using timestamp polling (`WHERE LAST_UPDATED_TIME > :last_poll`). "
            "During peak market hours, this causes severe read locks on the production Oracle CBS database and misses deleted records. "
            "How do you design a log-based Change Data Capture (CDC) pipeline using AWS DMS and Debezium to stream continuous binary redo logs?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "सध्या तुम्ही ओरेकल डेटाबेसमधून डेटा आणण्यासाठी दर ५ मिनिटांनी 'SELECT WHERE LAST_UPDATED_TIME > ...' अशी क्वेरी चालवता. "
            "यामुळे मुख्य बँकिंग सिस्टिमवर लोड येऊन ती स्लो होते, आणि जर कोणी रेकॉर्ड डिलीट केला तर तो अपडेट टाईम नसतो त्यामुळे डिलीट झालेला कळतच नाही. "
            "डेटाबेसवर कोणतीही क्वेरी न मारता, थेट ओरेकलच्या 'Redo Log' (बॅकअप लॉग्स) मधून AWS DMS किंवा Debezium द्वारे रिअल-टाईम बदल (CDC) कसे खेचायचे?"
        ),
        "in_depth_answer": (
            "Log-Based Change Data Capture (CDC) Architecture:\n\n"
            "1. Why Timestamp Polling Fails in Banking:\n"
            "- Polling executes full table index scans, creating locks and CPU spikes on production CBS.\n"
            "- Fails to capture hard `DELETE` operations.\n"
            "- Can miss rapid sequential updates occurring between poll intervals.\n\n"
            "2. Log-Based CDC Architecture via AWS DMS / Debezium:\n"
            "- The CDC engine attaches to the database transaction log (Oracle Redo Logs / PostgreSQL WAL) in read-only asynchronous mode.\n"
            "- Zero query overhead on table spaces.\n"
            "- Every INSERT, UPDATE, and DELETE is captured as an atomic JSON envelope containing `before` image, `after` image, and `op_type` (`I`, `U`, `D`).\n\n"
            "3. AWS DMS Task Configuration:\n"
            "- Source: Oracle CBS (LogMiner / AWS DMS binary reader).\n"
            "- Target: AWS S3 Staging in Parquet format with AWS Glue Catalog partitioning by `op_timestamp`.\n"
            "- Event Schema:\n"
            "  `{'op': 'U', 'ts_ms': 1791845000, 'before': {'bal': 5000}, 'after': {'bal': 3000}, 'account_id': 101}`"
        ),
        "interviewer_tip": "Mention Oracle LogMiner vs Binary Reader. Binary Reader bypasses LogMiner APIs to read redo logs directly from disk, saving 80% Oracle CPU overhead.",
        "follow_up_question": "How do you handle a schema alteration (e.g. ALTER TABLE ADD COLUMN) in log-based CDC?",
        "follow_up_answer": (
            "Debezium captures DDL statements into a schema history topic. AWS DMS supports automatic schema evolution. "
            "New columns are automatically appended to the target Parquet schema without dropping the replication task."
        )
    },
    {
        "id": "cdc_02",
        "domain": "ETL / ELT & CDC",
        "category": "ETL / ELT & CDC",
        "source_badge": "Citi Real-Time Clearing 2026",
        "scenario": (
            "In a distributed CDC streaming pipeline, network retransmissions and asynchronous partition keys cause out-of-order event delivery: "
            "an `UPDATE` or `DELETE` event for an account arrives at the Snowflake staging layer 3 seconds BEFORE the initial `INSERT` event. "
            "How do you design a deterministic state reconciler to prevent ghost records or corrupted account states?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "नेटवर्कच्या गोंधळामुळे एका खात्याचा 'UPDATE' किंवा 'DELETE' आधी आला, आणि त्याचा मूळ 'INSERT' ३ सेकंद उशिरा आला. "
            "जर तुम्ही आले तसे सेव्ह केले, तर आधी अपडेट होईल आणि नंतर इन्सर्ट होऊन जुना डेटा दिसेल! "
            "हा आउट-ऑफ-ऑर्डर (Out-of-order) डेटा व्यवस्थित क्रमाने लावून खरा फायनल स्टेट कसा तयार करायचा?"
        ),
        "in_depth_answer": (
            "Production Solution: Sequence-Numbered Window Deduplication:\n\n"
            "1. Event Envelope Metadata:\n"
            "Every CDC event from the database log carries a strictly monotonic sequence number from the database engine: "
            "Oracle SCN (System Change Number) or PostgreSQL LSN (Log Sequence Number), plus the source transaction commit timestamp.\n\n"
            "2. Staging Buffer & Ordered Compaction SQL:\n"
            "Instead of immediately updating the target table, all CDC events append into an immutable micro-batch staging table. "
            "A Snowflake MERGE statement resolves the latest true state using `ROW_NUMBER() OVER(PARTITION BY PK ORDER BY SCN DESC)`:\n\n"
            "```sql\n"
            "MERGE INTO CORE_BANKING.DIM_ACCOUNTS target\n"
            "USING (\n"
            "    WITH ranked_events AS (\n"
            "        SELECT \n"
            "            ACCOUNT_ID,\n"
            "            ACCOUNT_NAME,\n"
            "            BALANCE,\n"
            "            OP_TYPE, -- 'I', 'U', 'D'\n"
            "            SOURCE_SCN,\n"
            "            ROW_NUMBER() OVER(\n"
            "                PARTITION BY ACCOUNT_ID \n"
            "                ORDER BY SOURCE_SCN DESC\n"
            "            ) AS rank\n"
            "        FROM STAGING_CDC_EVENTS\n"
            "    )\n"
            "    SELECT * FROM ranked_events WHERE rank = 1\n"
            ") src\n"
            "ON target.ACCOUNT_ID = src.ACCOUNT_ID\n"
            "-- If latest event is DELETE, purge record\n"
            "WHEN MATCHED AND src.OP_TYPE = 'D' THEN\n"
            "    DELETE\n"
            "-- If latest event is UPDATE/INSERT, upsert conformed attributes\n"
            "WHEN MATCHED AND src.OP_TYPE IN ('I', 'U') THEN\n"
            "    UPDATE SET \n"
            "        target.ACCOUNT_NAME = src.ACCOUNT_NAME,\n"
            "        target.BALANCE = src.BALANCE,\n"
            "        target.LAST_SCN = src.SOURCE_SCN\n"
            "WHEN NOT MATCHED AND src.OP_TYPE IN ('I', 'U') THEN\n"
            "    INSERT (ACCOUNT_ID, ACCOUNT_NAME, BALANCE, LAST_SCN)\n"
            "    VALUES (src.ACCOUNT_ID, src.ACCOUNT_NAME, src.BALANCE, src.SOURCE_SCN);\n"
            "```"
        ),
        "interviewer_tip": "Emphasize ordering by SCN / LSN instead of wall-clock timestamps. Server clocks can experience NTP clock drift or skew, whereas database SCNs are guaranteed mathematically monotonic.",
        "follow_up_question": "What if an orphaned DELETE arrives and the INSERT hasn't arrived in this micro-batch yet?",
        "follow_up_answer": (
            "We maintain an ephemeral 'Tombstone Cache' in Redis or an unlinked staging table. When the late-arriving INSERT finally arrives 5 seconds later, "
            "the pipeline checks the tombstone cache, detects that an earlier DELETE has already taken place, and discards the stale INSERT."
        )
    },
    {
        "id": "cdc_03",
        "domain": "ETL / ELT & CDC",
        "category": "ETL / ELT & CDC",
        "source_badge": "Goldman Sachs Client Master 2026",
        "scenario": (
            "You are implementing a Slowly Changing Dimension Type 2 (SCD2) pipeline for customer risk profiles in Snowflake. "
            "When a customer's KYC status, risk tier, or address changes, you must close out the active record (`IS_CURRENT = FALSE`, `END_DATE = CURRENT_TIMESTAMP`) "
            "and insert a new active record (`IS_CURRENT = TRUE`, `START_DATE = CURRENT_TIMESTAMP`). "
            "How do you formulate an atomic, idempotent MERGE statement without incurring race conditions?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "ग्राहकाचा पत्ता किंवा केवायसी स्टेटस बदलले, तर जुना इतिहास न पुसता नवीन रेकॉर्ड साठवायचा आहे (SCD Type 2). "
            "उदा. जुन्या रेकॉर्डचा `IS_CURRENT = FALSE` करून आजची तारीख `END_DATE` लावायची, आणि नवीन ओळ टाकून `IS_CURRENT = TRUE` करायचे. "
            "हे काम एकाच अणूवत (Atomic) MERGE क्वेरीने कसे करायचे जेणेकरून जर जॉब दोनदा चालला तरी डुप्लिकेट रेकॉर्ड्स बनणार नाहीत?"
        ),
        "in_depth_answer": (
            "Idempotent SCD Type 2 Formulation in Snowflake:\n\n"
            "1. Two-Step Merging Pattern:\n"
            "Standard SQL `MERGE` can only update OR insert an individual row. For SCD2, an update to an existing row requires BOTH "
            "closing the old row AND inserting the new row. We solve this by staging a unioned delta containing update keys plus new inserts.\n\n"
            "```sql\n"
            "MERGE INTO DIM_CUSTOMER_SCD2 target\n"
            "USING (\n"
            "    -- Subset A: Existing records that changed (to be closed)\n"
            "    SELECT \n"
            "        s.CUSTOMER_ID AS JOIN_KEY,\n"
            "        s.CUSTOMER_ID,\n"
            "        s.RISK_TIER,\n"
            "        s.ADDRESS,\n"
            "        CURRENT_TIMESTAMP() AS EFF_START_DATE,\n"
            "        'UPDATE_OLD' AS ACTION_TYPE\n"
            "    FROM STG_CUSTOMER s\n"
            "    JOIN DIM_CUSTOMER_SCD2 t \n"
            "      ON s.CUSTOMER_ID = t.CUSTOMER_ID \n"
            "     AND t.IS_CURRENT = TRUE\n"
            "    WHERE t.RISK_TIER != s.RISK_TIER OR t.ADDRESS != s.ADDRESS\n\n"
            "    UNION ALL\n\n"
            "    -- Subset B: New records to be inserted (brand new or new versions of updated rows)\n"
            "    SELECT \n"
            "        NULL AS JOIN_KEY, -- Force NOT MATCHED\n"
            "        s.CUSTOMER_ID,\n"
            "        s.RISK_TIER,\n"
            "        s.ADDRESS,\n"
            "        CURRENT_TIMESTAMP() AS EFF_START_DATE,\n"
            "        'INSERT_NEW' AS ACTION_TYPE\n"
            "    FROM STG_CUSTOMER s\n"
            ") src\n"
            "ON target.CUSTOMER_ID = src.JOIN_KEY AND target.IS_CURRENT = TRUE\n"
            "-- Close existing record\n"
            "WHEN MATCHED AND src.ACTION_TYPE = 'UPDATE_OLD' THEN\n"
            "    UPDATE SET \n"
            "        target.IS_CURRENT = FALSE,\n"
            "        target.EXPIRY_DATE = src.EFF_START_DATE\n"
            "-- Insert new active version\n"
            "WHEN NOT MATCHED THEN\n"
            "    INSERT (CUSTOMER_ID, RISK_TIER, ADDRESS, START_DATE, EXPIRY_DATE, IS_CURRENT)\n"
            "    VALUES (src.CUSTOMER_ID, src.RISK_TIER, src.ADDRESS, src.EFF_START_DATE, '9999-12-31'::TIMESTAMP, TRUE);\n"
            "```"
        ),
        "interviewer_tip": "Explain the `NULL AS JOIN_KEY` trick. By passing NULL as the join condition key for Subset B, it is guaranteed to trigger `WHEN NOT MATCHED`, cleanly inserting the new active version.",
        "follow_up_question": "How do you handle changes when dbt is used in the pipeline?",
        "follow_up_answer": (
            "In dbt, we use the native `dbt snapshot` functionality with strategy `check` or `timestamp`. "
            "dbt compiles this exact surrogate key hashing and MERGE logic under the hood automatically."
        )
    },
    {
        "id": "cdc_04",
        "domain": "ETL / ELT & CDC",
        "category": "ETL / ELT & CDC",
        "source_badge": "Standard Chartered Payments 2026",
        "scenario": (
            "During an SFTP upload of daily core banking settlement files, a network timeout occurred at 99% progress. "
            "The automated upstream batch script re-uploaded the exact same file 10 minutes later with a new file name: `CBS_SETTLE_20261013_RETRY.csv`. "
            "How do you design an idempotent ingestion architecture so that replaying or reprocessing this file does not double-count transactions?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "इंटरनेट कनेक्शन तुटल्यामुळे बँकेच्या सर्वरने तीच फाईल पुन्हा नवीन नावाने (`CBS_SETTLE_RETRY.csv`) अपलोड केली. "
            "जर आपल्या कोडने दोन्ही फाईल्स वाचल्या, तर सर्व ग्राहकांचे पैसे दुप्पट जमा होतील! "
            "फायलीचे नाव बदलले तरी आतील डेटा आधीच लोड झाला आहे हे ओळखून, एकाच ट्रॅन्झॅक्शनचे दुबार इन्सर्ट कसे रोखायचे? (Idempotent Ingestion)"
        ),
        "in_depth_answer": (
            "Production Solution for Idempotent Ingestion:\n\n"
            "1. Content Hashing over File Name Tracking:\n"
            "Never rely solely on file names for idempotency. Upstream automated retry daemons frequently rename files during retransmissions.\n\n"
            "2. Three-Tier Idempotency Gate:\n"
            "- Gate 1 (File Content SHA-256 Checksum): Compute SHA-256 hash of the incoming S3 object. Store hashes in `INGESTION_FILE_LEDGER`. "
            "If a matching payload hash exists, skip ingestion and flag as duplicate upload.\n"
            "- Gate 2 (Row Surrogate Key Hash): For every transaction row, generate an MD5 / SHA-256 hash of the immutable business key: "
            "`HASH(CBS_TXN_REF, VALUE_DATE, SOURCE_ACCOUNT, AMOUNT)`.\n"
            "- Gate 3 (Idempotent Merge/Upsert): Load via Snowflake `MERGE` or insert into staging and use `QUALIFY ROW_NUMBER() = 1` before pushing to L1:\n\n"
            "```sql\n"
            "INSERT INTO L1_CONFORMED.SETTLEMENTS\n"
            "SELECT \n"
            "    s.TXN_HASH,\n"
            "    s.CBS_TXN_REF,\n"
            "    s.AMOUNT,\n"
            "    s.VALUE_DATE\n"
            "FROM L0_STAGING.SETTLEMENTS s\n"
            "WHERE NOT EXISTS (\n"
            "    SELECT 1 FROM L1_CONFORMED.SETTLEMENTS target\n"
            "    WHERE target.TXN_HASH = s.TXN_HASH\n"
            ");\n"
            "```"
        ),
        "interviewer_tip": "Define 'Idempotency' cleanly: $f(f(x)) = f(x)$. Running the pipeline 1 time or 100 times with the same input data produces the exact same final state.",
        "follow_up_question": "What if an authentic customer really made two identical transactions of ₹5,000 to the same merchant in the same minute?",
        "follow_up_answer": (
            "Core banking platforms assign a unique primary key `CBS_TRANSACTION_ID` or `RRN` (Retrieval Reference Number) to every distinct API call. "
            "Including the CBS sequence ID in the hash prevents collating two legitimate duplicate-amount transactions."
        )
    },
    {
        "id": "cdc_05",
        "domain": "ETL / ELT & CDC",
        "category": "ETL / ELT & CDC",
        "source_badge": "Amazon Retail Data Engineering 2026",
        "scenario": (
            "A streaming Kafka pipeline ingesting 150,000 JSON messages per second encounters a 'Poison Pill' record: a malformed JSON payload "
            "with an unclosed bracket or invalid Unicode string. The consumer crashes, restarts, encounters the same poison pill, and enters an infinite crash loop. "
            "How do you implement Backpressure and a Dead-Letter Queue (DLQ) pattern to maintain continuous ingestion?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "दर सेकंदाला १.५ लाख मेसेजेस येत असताना अचानक एक खराब (corrupted) मेसेज आला (Poison Pill). "
            "कन्झ्युमर तो वाचताना क्रॅश झाला; रिस्टार्ट झाला की पुन्हा तोच मेसेज समोर येतो आणि तो परत क्रॅश होतो! "
            "यामुळे अख्खा पाईपलाईन ठप्प होतो. हा एक खराब मेसेज बाजूला Dead-Letter Queue (DLQ) मध्ये टाकून, मुख्य पाईपलाईन न थांबवता अखंड कसा चालू ठेवायचा?"
        ),
        "in_depth_answer": (
            "Dead-Letter Queue (DLQ) & Resilience Pattern:\n\n"
            "1. Architectural Principle:\n"
            "Never crash the entire cluster due to an isolated bad record. Quarantine corrupt payloads asynchronously into a Dead Letter Queue (DLQ) topic, "
            "commit the consumer offset, and continue streaming valid records.\n\n"
            "```python\n"
            "import json\n"
            "from confluent_kafka import Consumer, Producer\n\n"
            "def run_resilient_consumer():\n"
            "    consumer = Consumer({'bootstrap.servers': 'kafka:9092', 'group.id': 'settlement_workers'})\n"
            "    dlq_producer = Producer({'bootstrap.servers': 'kafka:9092'})\n"
            "    consumer.subscribe(['raw_banking_stream'])\n\n"
            "    while True:\n"
            "        msg = consumer.poll(1.0)\n"
            "        if msg is None:\n"
            "            continue\n"
            "        \n"
            "        try:\n"
            "            # Attempt strict JSON parsing and schema validation\n"
            "            payload = json.loads(msg.value().decode('utf-8'))\n"
            "            process_settlement_record(payload)\n"
            "        except Exception as err:\n"
            "            # Route to Dead Letter Queue (DLQ)\n"
            "            dlq_envelope = {\n"
            "                'raw_payload': msg.value().decode('latin1', errors='replace'),\n"
            "                'error_type': type(err).__name__,\n"
            "                'error_details': str(err),\n"
            "                'failed_offset': msg.offset(),\n"
            "                'failed_partition': msg.partition(),\n"
            "                'timestamp': time.time()\n"
            "            }\n"
            "            dlq_producer.produce('banking_stream_dlq', value=json.dumps(dlq_envelope))\n"
            "            dlq_producer.poll(0)\n"
            "        \n"
            "        # Advance offset to unblock queue\n"
            "        consumer.commit(msg)\n"
            "```\n\n"
            "2. Monitoring & Alerting:\n"
            "We set a CloudWatch / Prometheus alarm on the DLQ topic. If DLQ depth exceeds 50 records in 5 minutes, an on-call alert fires."
        ),
        "interviewer_tip": "Mention `decode('latin1', errors='replace')` for the DLQ payload. If the source error was a malformed UTF-8 byte sequence, trying to decode it normally would cause a secondary crash inside your error handler!",
        "follow_up_question": "How do you reprocess the DLQ messages once the upstream bug is patched?",
        "follow_up_answer": (
            "We build a dedicated 'DLQ Replay DAG'. Once the parsing schema is patched, a maintenance job consumes the DLQ topic, "
            "strips the error envelope, and re-injects the sanitized records into the primary ingestion topic."
        )
    },

    # =========================================================================
    # DOMAIN 6: SNOWFLAKE ARCHITECTURE
    # =========================================================================
    {
        "id": "sf_01",
        "domain": "Snowflake Architecture",
        "category": "Snowflake Architecture",
        "source_badge": "Snowflake Principal Certification 2026",
        "scenario": (
            "A 4-billion row transaction fact table (`FACT_CORE_TRANSACTIONS`) in Snowflake exhibits poor query performance. "
            "Point lookups on `ACCOUNT_ID` scan 14,000 micro-partitions out of 16,000 total partitions, costing high credit consumption. "
            "Explain how Snowflake Micro-Partitioning works, how to analyze clustering depth (`SYSTEM$CLUSTERING_DEPTH`), "
            "and when to choose an explicit Clustering Key vs Search Optimization Service (SOS)."
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "Snowflake मधील ४ अब्ज रो असलेल्या मोठ्या टेबलवर जेव्हा एखादा अकाउंट नंबर शोधला जातो, तेव्हा १६,००० पैकी १४,००० पार्टिशन्स स्कॅन होतात. "
            "Snowflake मध्ये इंडेक्स नसतात; तिथे 'Micro-Partitions' (१६MB च्या आपोआप बनणाऱ्या फाइल्स) असतात. "
            "Clustering Depth कशी तपासायची? क्लस्टरिंग की (Clustering Key) कधी वापरायची आणि Search Optimization Service (SOS) कधी वापरायची?"
        ),
        "in_depth_answer": (
            "Snowflake Micro-Partitioning & Search Optimization Architecture:\n\n"
            "1. How Micro-Partitioning Works:\n"
            "- Tables are automatically divided into contiguous, immutable micro-partitions (50MB to 500MB uncompressed, 16MB compressed).\n"
            "- Snowflake stores columnar metadata for each micro-partition: MIN and MAX values for every column, distinct value counts, and NULL counts.\n"
            "- When a query runs with `WHERE ACCOUNT_ID = '101'`, Snowflake compares the predicate with partition MIN/MAX ranges to prune irrelevant files.\n\n"
            "2. Analyzing Clustering Health:\n"
            "```sql\n"
            "-- Check clustering depth (Ideal depth is 1 to 3; depth > 20 indicates un-clustered data)\n"
            "SELECT SYSTEM$CLUSTERING_INFORMATION('FACT_CORE_TRANSACTIONS', '(TXN_DATE, ACCOUNT_ID)');\n"
            "```\n\n"
            "3. Choosing Clustering Key vs Search Optimization Service (SOS):\n"
            "- Use Clustering Key: When queries filter or join on range/ordered columns (e.g., `WHERE TXN_DATE BETWEEN ... AND ACCOUNT_ID = ...`). "
            "Optimal for 1 to 3 low-to-medium cardinality columns.\n"
            "- Use Search Optimization Service (SOS): For high-cardinality point-lookups (e.g., finding 1 specific `TRANSACTION_ID` across 4 billion rows), "
            "or regex searches on text and semi-structured VARIANT paths. SOS creates an auxiliary persistent search access path without reorganizing table rows.\n\n"
            "```sql\n"
            "-- Enable SOS for high-speed point lookups\n"
            "ALTER TABLE FACT_CORE_TRANSACTIONS ADD SEARCH OPTIMIZATION ON EQUALITY(ACCOUNT_ID, CBS_TXN_REF);\n"
            "```"
        ),
        "interviewer_tip": "Highlight that Auto-Clustering continuously consumes Snowflake credits. If a table undergoes heavy continuous streaming writes, an aggressive clustering key can burn thousands of credits in background maintenance.",
        "follow_up_question": "What happens if you define a clustering key on a column with 1 billion unique values?",
        "follow_up_answer": (
            "Defining a clustering key on high-cardinality columns (like unique UUIDs) is a major anti-pattern! "
            "It leads to tiny partition overlaps where MIN equals MAX on every partition, triggering continuous background re-clustering loops without query pruning benefits."
        )
    },
    {
        "id": "sf_02",
        "domain": "Snowflake Architecture",
        "category": "Snowflake Architecture",
        "source_badge": "Morgan Stanley Banking DevOps 2026",
        "scenario": (
            "A critical bug in production AML reconciler causes an incorrect balance calculation across 10 million accounts. "
            "You cannot afford to shut down production, nor can you risk running debugging scripts directly against production data. "
            "How do you use Snowflake Zero-Copy Cloning and Time Travel to spin up an instantaneous, zero-cost staging environment "
            "reflecting production data exactly 30 minutes before the bug occurred?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "प्रोडक्शन सिस्टिममध्ये एक गंभीर बग आला आणि १० लाख खात्यांचा डेटा चुकला. "
            "आपण प्रोडक्शन डेटाबेस बंद करू शकत नाही आणि तिथे थेट टेस्टिंगही करू शकत नाही. "
            "बग येण्यापूर्वी ३० मिनिटे आधी डेटा जसा होता, तसाच्या तसा हुबेहूब डेटाबेस टेस्टिंगसाठी त्वरित कसा बनवायचा? "
            "(Snowflake चे Zero-Copy Clone आणि Time Travel वापरून २ सेकंदात आणि ० स्टोरेज खर्चात हे कसे करायचे?)"
        ),
        "in_depth_answer": (
            "Zero-Copy Cloning with Time Travel:\n\n"
            "1. Architectural Power of Zero-Copy Clone:\n"
            "A clone duplicates only the metadata catalog pointers to the underlying immutable S3 micro-partitions. "
            "Even for a 50TB database, cloning completes in 2 seconds and consumes zero additional storage credits until modified.\n\n"
            "```sql\n"
            "-- Step 1: Clone production database to ephemeral sandbox as of 30 minutes ago\n"
            "CREATE OR REPLACE DATABASE UAT_AML_HOTFIX_SANDBOX \n"
            "CLONE PROD_CORE_BANKING \n"
            "AT(TIMESTAMP => DATEADD('minute', -30, CURRENT_TIMESTAMP()));\n\n"
            "-- Step 2: Grant immediate access to debugging engineers\n"
            "GRANT ALL ON DATABASE UAT_AML_HOTFIX_SANDBOX TO ROLE DATA_ENGINEER_HOTFIX;\n\n"
            "-- Step 3: Run debugging and patch scripts in total isolation\n"
            "USE DATABASE UAT_AML_HOTFIX_SANDBOX;\n"
            "CALL SP_FIX_AML_RECONCILIATION_LOGIC();\n\n"
            "-- Step 4: Validate corrected numbers against known golden records\n"
            "SELECT COUNT(*) FROM FACT_RECONCILIATION WHERE RECON_STATUS = 'BALANCED';\n"
            "```\n\n"
            "2. Promotion to Production:\n"
            "Once the SQL patch is validated in the sandbox, the exact same script is applied to production during maintenance window, "
            "and the sandbox is dropped (`DROP DATABASE UAT_AML_HOTFIX_SANDBOX;`)."
        ),
        "interviewer_tip": "Mention that cloned tables inherit the source table's Time Travel history and clustering keys, but do NOT inherit stage objects or notification integrations.",
        "follow_up_question": "If engineers write 5GB of test data into the clone, does production see it?",
        "follow_up_answer": (
            "No. The clone is fully isolated. Thanks to copy-on-write semantics, newly written micro-partitions are owned exclusively by the clone. "
            "Production remains 100% unaffected."
        )
    },
    {
        "id": "sf_03",
        "domain": "Snowflake Architecture",
        "category": "Snowflake Architecture",
        "source_badge": "Barclays Production Support 2026",
        "scenario": (
            "A junior DBA accidentally executed `DROP TABLE CORE_BANKING.CUSTOMER_ACCOUNTS;` in production at 14:15 IST. "
            "The table holds 12 million active accounts and serves online banking APIs. "
            "How do you recover the table in under 30 seconds with zero data loss using Snowflake UNDROP, and what conditions must be met for UNDROP to succeed?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "दुपारी २:१५ वाजता एका ज्युनिअर इंजिनिअरने चुकून १२ लाख खाती असलेले मुख्य टेबल `DROP TABLE` करून उडवले! "
            "ऑनलाईन बँकिंग ठप्प झाले आहे. कोणत्याही जुन्या बॅकअपवरून रिस्टोअर न करता, अवघ्या ३० सेकंदात "
            "Snowflake च्या `UNDROP` कमांडने हे टेबल कसे जिवंत करायचे? आणि यासाठी कोणत्या अटी पूर्ण असाव्यात?"
        ),
        "in_depth_answer": (
            "Instant Disaster Recovery via Snowflake UNDROP:\n\n"
            "1. Recovery Command:\n"
            "Because Snowflake's underlying micro-partitions are immutable and managed via metadata manifests, dropping a table merely marks "
            "the metadata pointer as dropped without deleting physical storage during the Time Travel retention period.\n\n"
            "```sql\n"
            "-- Instant recovery command\n"
            "UNDROP TABLE CORE_BANKING.CUSTOMER_ACCOUNTS;\n"
            "```\n\n"
            "2. Verification:\n"
            "```sql\n"
            "SELECT COUNT(*) FROM CORE_BANKING.CUSTOMER_ACCOUNTS;\n"
            "-- Confirms all 12,000,000 rows restored instantly with all clustering keys and metadata\n"
            "```\n\n"
            "3. Mandatory Conditions for UNDROP to Succeed:\n"
            "- Condition 1: Must be executed within the `DATA_RETENTION_TIME_IN_DAYS` window (1 to 90 days).\n"
            "- Condition 2: The parent schema (`CORE_BANKING`) and database must not be dropped (if dropped, undrop the database/schema first).\n"
            "- Condition 3: No other table with the exact same name must have been created in that schema since the drop (if a new table was created, rename it first before issuing `UNDROP`)."
        ),
        "interviewer_tip": "Demonstrate senior readiness: mention that `UNDROP` also restores table comments, grants, and clustering keys, but transient tables only have a 1-day retention limit.",
        "follow_up_question": "What if the table was TRUNCATED rather than DROPPED?",
        "follow_up_answer": (
            "`UNDROP` only works for `DROP TABLE`. For a `TRUNCATE TABLE`, we recover data using Time Travel before the truncate query: "
            "`INSERT INTO CUSTOMER_ACCOUNTS SELECT * FROM CUSTOMER_ACCOUNTS BEFORE(STATEMENT => '<TRUNCATE_QUERY_ID>');`"
        )
    },
    {
        "id": "sf_04",
        "domain": "Snowflake Architecture",
        "category": "Snowflake Architecture",
        "source_badge": "Citi High-Frequency Settlement 2026",
        "scenario": (
            "Your architecture needs to ingest 50,000 real-time credit card swipe authorizations per second into Snowflake. "
            "Standard Auto-Ingest Snowpipe (triggered via S3 SQS events) exhibits a latency of 60 to 90 seconds. "
            "How do you migrate to Snowpipe Streaming using the Java/Python SDK to achieve sub-second ingestion latency with lower compute costs?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "क्रेडिट कार्ड स्वाइपचे ५०,००० व्यवहार प्रति सेकंद Snowflake मध्ये आणायचे आहेत. जुन्या Snowpipe मध्ये S3 फाईल बनून SQS ट्रिगर होईपर्यंत "
            "१ ते १.५ मिनिटांचा उशीर (Latency) होतो. कार्ड स्वाइपसाठी आपल्याला १ सेकंदाच्या आत डेटा हवा आहे. "
            "S3 मध्ये फाईल न बनवता, थेट मेमरीमधून Snowflake च्या रो-बफरमध्ये डेटा ढकलण्यासाठी 'Snowpipe Streaming SDK' कसे वापरतात?"
        ),
        "in_depth_answer": (
            "Sub-Second Snowpipe Streaming Architecture:\n\n"
            "1. Architectural Difference:\n"
            "- Classic Snowpipe: Stage files in S3 -> S3 sends SQS event -> Snowpipe reads file from S3 -> Loads into table (Latency: 60-90s).\n"
            "- Snowpipe Streaming SDK: Application client opens direct gRPC/HTTPS streaming channel into Snowflake -> Streams rows directly into Snowflake micro-partition buffer -> Commits offsets (Latency: $<1$ second).\n\n"
            "2. Implementation Architecture:\n"
            "```python\n"
            "# Conceptual Python Snowpipe Streaming Flow\n"
            "from snowflake.ingest.streaming import SnowflakeStreamingIngestClient\n\n"
            "client = SnowflakeStreamingIngestClient.builder('CC_AUTHORIZATION_STREAM') \\\n"
            "    .set_account('xy12345') \\\n"
            "    .set_private_key_file('snowflake_jwt_key.p8') \\\n"
            "    .build()\n\n"
            "channel = client.open_channel(\n"
            "    db_name='CORE_BANKING',\n"
            "    schema_name='AUTHORIZATIONS',\n"
            "    table_name='STREAM_CARD_SWIPES',\n"
            "    channel_name='CHANNEL_THREAD_01'\n"
            ")\n\n"
            "# High-frequency row insertion\n"
            "def on_card_swiped(swipe_event: dict):\n"
            "    channel.insert_row(swipe_event, offset_token=str(swipe_event['event_id']))\n"
            "```\n\n"
            "3. Cost Advantage:\n"
            "Bypasses S3 PUT request costs ($0.005 per 1,000 requests adds up to thousands of dollars at 50K/s) and runs at standard serverless streaming rates."
        ),
        "interviewer_tip": "Highlight the `offset_token`. Snowpipe Streaming channels are stateful and store the caller's offset token inside Snowflake. Upon restart, the client queries `channel.get_latest_successful_offset_token()` to guarantee exact-once delivery.",
        "follow_up_question": "Can you attach a Snowflake Stream to a table populated by Snowpipe Streaming?",
        "follow_up_answer": (
            "Yes! Snowflake Streams and Dynamic Tables natively capture rows ingested via Snowpipe Streaming, "
            "enabling continuous downstream Medallion transformations."
        )
    },
    {
        "id": "sf_05",
        "domain": "Snowflake Architecture",
        "category": "Snowflake Architecture",
        "source_badge": "Snowflake Enterprise Architecture 2026",
        "scenario": (
            "Your enterprise wants to eliminate external orchestration tools (like Airflow or Control-M) for their core Snowflake transformations. "
            "How do you build a fully serverless, continuous ELT DAG entirely inside Snowflake using Streams, Serverless Tasks, "
            "the `AFTER` clause, and the `SYSTEM$STREAM_HAS_DATA` conditional predicate?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "कंपनीला Airflow किंवा इतर बाहेरील टूल्स न वापरता, Snowflake च्या आतच संपूर्ण स्वयंचलित पाईपलाईन (Serverless DAG) चालवायची आहे. "
            "जेव्हा नवीन डेटा येईल तेव्हाच टास्क चालावी (`SYSTEM$STREAM_HAS_DATA`), आणि टास्क १ संपली की टास्क २ आपोआप सुरु व्हावी (`AFTER`). "
            "Snowflake Streams आणि Tasks वापरून हे पूर्णपणे सर्व्हरलेस कसे सेट करायचे?"
        ),
        "in_depth_answer": (
            "Serverless Native Snowflake DAG Architecture:\n\n"
            "1. Architectural Components:\n"
            "- Stream: An append-only or change-data capture stream on L0 Raw table tracking row-level delta.\n"
            "- Root Task: A scheduled task running every 10 minutes that checks `SYSTEM$STREAM_HAS_DATA('RAW_STREAM')`. If no data arrived, it terminates in 0 seconds with 0 credit cost.\n"
            "- Child Tasks: Use the `AFTER` clause to form a dependency DAG without schedule overlaps.\n\n"
            "```sql\n"
            "-- Step 1: Create Change Stream on L0\n"
            "CREATE OR REPLACE STREAM STG_TXN_STREAM ON TABLE L0_RAW.TRANSACTIONS;\n\n"
            "-- Step 2: Root Task (L0 -> L1 Harmonised)\n"
            "CREATE OR REPLACE TASK TASK_PROCESS_L1_HARMONISED\n"
            "    SCHEDULE = '10 MINUTE'\n"
            "    USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = 'XSMALL' -- Serverless Compute\n"
            "WHEN\n"
            "    SYSTEM$STREAM_HAS_DATA('STG_TXN_STREAM')\n"
            "AS\n"
            "    MERGE INTO L1_HARMONISED.TRANSACTIONS target\n"
            "    USING STG_TXN_STREAM src\n"
            "    ON target.TXN_ID = src.TXN_ID\n"
            "    WHEN MATCHED THEN UPDATE SET target.AMOUNT = src.AMOUNT\n"
            "    WHEN NOT MATCHED THEN INSERT (TXN_ID, AMOUNT) VALUES (src.TXN_ID, src.AMOUNT);\n\n"
            "-- Step 3: Child Task (L1 -> L2 Gold Mart)\n"
            "CREATE OR REPLACE TASK TASK_REFRESH_L2_GOLD_MART\n"
            "    AFTER TASK_PROCESS_L1_HARMONISED -- Chained dependency\n"
            "    USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = 'SMALL'\n"
            "AS\n"
            "    INSERT INTO L2_GOLD.DAILY_SETTLEMENT_MART\n"
            "    SELECT BRANCH_ID, SUM(AMOUNT), CURRENT_DATE()\n"
            "    FROM L1_HARMONISED.TRANSACTIONS\n"
            "    WHERE LOAD_DATE = CURRENT_DATE()\n"
            "    GROUP BY BRANCH_ID;\n\n"
            "-- Step 4: Activate DAG\n"
            "ALTER TASK TASK_REFRESH_L2_GOLD_MART RESUME;\n"
            "ALTER TASK TASK_PROCESS_L1_HARMONISED RESUME;\n"
            "```"
        ),
        "interviewer_tip": "Notice the resume order: Child tasks MUST be resumed before the Root task (`ALTER TASK ... RESUME`). If you try to resume the Root task first, Snowflake throws an error.",
        "follow_up_question": "What happens to the Stream's delta if the Root Task's transaction fails?",
        "follow_up_answer": (
            "Snowflake streams are transactional. If the task fails, the transaction rolls back, and the Stream's offset does NOT advance. "
            "The unconsumed delta remains in the stream for the next retry."
        )
    },

    # =========================================================================
    # DOMAIN 7: AWS DATA SERVICES
    # =========================================================================
    {
        "id": "aws_01",
        "domain": "AWS Data Services",
        "category": "AWS Data Services",
        "source_badge": "Amazon AWS Core Infra 2026",
        "scenario": (
            "You are architecting an enterprise S3 Data Lake landing zone for banking regulatory feeds. "
            "How do you implement: (1) S3 Bucket Policies enforcing TLS 1.3 in-transit encryption, (2) SSE-KMS customer-managed keys (CMK) with automated rotation, "
            "(3) S3 Object Lock in Compliance Mode for WORM (Write Once Read Many) immutability, and (4) S3 Lifecycle transitions to Glacier Instant Retrieval?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेच्या डेटा लेकसाठी AWS S3 स्टोरेज तयार करताना अत्यंत कडक सुरक्षा नियम लावायचे आहेत:\n"
            "१. डेटा येताना-जाताना फक्त सुरक्षित TLS 1.3 चालले पाहिजे.\n"
            "२. S3 मधील डेटा कस्टमरच्या स्वतःच्या KMS चावीने एनक्रिप्ट झाला पाहिजे.\n"
            "३. WORM (Write Once Read Many) - एकदा फाईल पडली की बँकेच्या चेअरमनने जरी प्रयत्न केला तरी ती फाईल १० वर्षे कोणीही डिलीट किंवा मॉडिफाय करू शकत नाही (Compliance Mode).\n"
            "४. ९० दिवसांनंतर खर्च वाचवण्यासाठी डेटा आपोआप स्वस्त Glacier Instant Retrieval मध्ये हलवला पाहिजे."
        ),
        "in_depth_answer": (
            "Enterprise AWS S3 Data Lake Infrastructure Architecture:\n\n"
            "1. S3 Bucket Policy (Enforcing TLS 1.2+ & Denying Insecure HTTP):\n"
            "```json\n"
            "{\n"
            "    \"Version\": \"2012-10-17\",\n"
            "    \"Statement\": [\n"
            "        {\n"
            "            \"Sid\": \"EnforceTLSRequestsOnly\",\n"
            "            \"Effect\": \"Deny\",\n"
            "            \"Principal\": \"*\",\n"
            "            \"Action\": \"s3:*\",\n"
            "            \"Resource\": [\"arn:aws:s3:::banking-lake-raw\", \"arn:aws:s3:::banking-lake-raw/*\"],\n"
            "            \"Condition\": {\n"
            "                \"Bool\": {\"aws:SecureTransport\": \"false\"},\n"
            "                \"NumericLessThan\": {\"s3:TlsVersion\": 1.2}\n"
            "            }\n"
            "        }\n"
            "    ]\n"
            "}\n"
            "```\n\n"
            "2. S3 Object Lock (WORM - Write Once Read Many for RBI Compliance):\n"
            "Enable Object Lock in `COMPLIANCE` mode with a 10-year retention period. In Compliance Mode, no AWS IAM principal (including the AWS root account) "
            "can overwrite or delete the object until the retention duration expires.\n\n"
            "3. KMS Key with Automatic Annual Rotation:\n"
            "Use Customer Managed Keys (CMK) with `EnableKeyRotation: true`.\n\n"
            "4. S3 Lifecycle Configuration:\n"
            "- Day 0 to 30: S3 Standard.\n"
            "- Day 31: Transition to S3 Standard-IA (Infrequent Access).\n"
            "- Day 90: Transition to S3 Glacier Instant Retrieval (milliseconds access latency for audits at 68% lower cost).\n"
            "- Day 3650: Expiration rule deletes expired objects."
        ),
        "interviewer_tip": "Contrast S3 Object Lock 'GOVERNANCE' mode vs 'COMPLIANCE' mode. In Governance mode, users with a specific IAM permission can bypass retention; in Compliance mode, even the AWS root account CANNOT delete the object.",
        "follow_up_question": "Why Glacier Instant Retrieval over Glacier Deep Archive for banking audit logs?",
        "follow_up_answer": (
            "Glacier Deep Archive takes 12 hours to restore files, violating regulatory audit SLAs where RBI inspectors demand immediate interactive inspection. "
            "Glacier Instant Retrieval delivers milliseconds retrieval speed while saving 68% on storage."
        )
    },
    {
        "id": "aws_02",
        "domain": "AWS Data Services",
        "category": "AWS Data Services",
        "source_badge": "JPMorgan Cloud Lakehouse 2026",
        "scenario": (
            "An AWS Glue 4.0 ETL job processing 100M rows in Parquet format takes 55 minutes and costs high DPU (Data Processing Unit) billing. "
            "Profiling indicates that 80% of runtime is spent reading and uncompressing unnecessary partitions from S3. "
            "How do you optimize this using AWS Glue Pushdown Predicates, Job Bookmarks, and DynamicFrame partition pruning?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "AWS Glue वरील एक पायथॉन ETL जॉब ५५ मिनिटे घेतोय आणि खूप जास्त बिल (DPU Cost) येतेय. "
            "तपासणी केल्यावर कळाले की जॉबला फक्त आजच्या दिवसाचा डेटा हवा आहे, पण तो S3 मधील मागील ३ वर्षांचा जुना डेटा सुद्धा वाचत बसतो! "
            "Glue 'Pushdown Predicates' आणि 'Job Bookmarks' वापरून फक्त नवीन डेटा कसा वाचायचा आणि जॉबचा वेळ ५५ मिनिटांवरून ३ मिनिटांवर कसा आणायचा?"
        ),
        "in_depth_answer": (
            "AWS Glue Performance Optimization Architecture:\n\n"
            "1. Why Traditional Spark `filter()` Wastes Money:\n"
            "In PySpark, `df.filter(col('year') == 2026)` often lists all S3 objects in the parent folder first before applying the filter, "
            "burning hundreds of S3 `ListObjectsV2` API calls and DPU memory.\n\n"
            "2. AWS Glue Pushdown Predicates:\n"
            "Pushdown predicates prune partition metadata directly in the AWS Glue Data Catalog BEFORE Spark even touches S3:\n\n"
            "```python\n"
            "import sys\n"
            "from awsglue.context import GlueContext\n"
            "from pyspark.context import SparkContext\n"
            "from awsglue.job import Job\n\n"
            "sc = SparkContext()\n"
            "glueContext = GlueContext(sc)\n"
            "job = Job(glueContext)\n"
            "job.init('cbs_daily_recon', args)\n\n"
            "# 1. Pushdown Predicate: Reads ONLY today's S3 folder\n"
            "dynamic_frame = glueContext.create_dynamic_frame.from_catalog(\n"
            "    database='lake_raw',\n"
            "    table_name='fact_cbs_transactions',\n"
            "    push_down_predicate=\"(year == '2026' and month == '10' and day == '13')\",\n"
            "    transformation_ctx='datasource_ctx'\n"
            ")\n\n"
            "# 2. Enable Job Bookmarks: Prevents reprocessing previously ingested S3 files\n"
            "# Run with --job-bookmark-option job-bookmark-enable\n"
            "```\n\n"
            "3. Result:\n"
            "Runtime drops from 55 minutes to 3.2 minutes, reducing AWS DPU compute spend by 94%."
        ),
        "interviewer_tip": "Mention `transformation_ctx`. AWS Glue Job Bookmarks require `transformation_ctx` to uniquely identify the data source node across stateful runs.",
        "follow_up_question": "What happens if upstream core banking uploads backfilled data for last week into an already bookmarked S3 folder?",
        "follow_up_answer": (
            "We run the job with `--job-bookmark-option job-bookmark-pause` or pass specific partition override parameters to re-evaluate the target partitions without resetting the entire bookmark history."
        )
    },
    {
        "id": "aws_03",
        "domain": "AWS Data Services",
        "category": "AWS Data Services",
        "source_badge": "Goldman Sachs Global Assets 2026",
        "scenario": (
            "Your wealth management analysts need to run ad-hoc interactive SQL queries joining 5 years of historical trade logs "
            "stored in Amazon S3 (Parquet) with live customer portfolios stored in Amazon Aurora PostgreSQL. "
            "How do you design Amazon Athena Federated Queries using the Athena Athena-PostgreSQL Lambda Connector with partition projection?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "ॲनालिस्ट लोकांना एक अशी SQL क्वेरी चालवायची आहे ज्यामध्ये ५ वर्षांचा जुना इतिहास (S3 मधील Parquet फाईल्स) "
            "आणि आत्ताचा लाईव्ह ग्राहक डेटा (Amazon Aurora PostgreSQL डेटाबेस) यांचा एकत्र जॉईन (JOIN) करायचा आहे. "
            "डेटा इकडेतिकडे कॉपी न करता, एकाच Amazon Athena SQL इंटरफेसवरून दोन्ही ठिकाणी 'Federated Query' कशी चालवायची?"
        ),
        "in_depth_answer": (
            "Amazon Athena Federated Query Architecture:\n\n"
            "1. Architectural Principle:\n"
            "Athena Federated Query enables SQL execution across disparate sources (S3, PostgreSQL, DynamoDB, Snowflake) "
            "using Lambda-based data source connectors that fetch external tables and stream Arrow records back to Athena's distributed Presto/Trino engine.\n\n"
            "2. Implementation Architecture:\n"
            "- Step 1: Deploy AWS Athena PostgreSQL Connector Lambda with VPC subnet access to Aurora PostgreSQL.\n"
            "- Step 2: Register catalog alias in Athena: `aurora_catalog`.\n"
            "- Step 3: Configure Partition Projection on the historical S3 tables to bypass slow Glue partition scans:\n\n"
            "```sql\n"
            "-- Single Athena SQL query joining S3 Lakehouse with live Aurora DB\n"
            "SELECT \n"
            "    live.CUSTOMER_ID,\n"
            "    live.FULL_NAME,\n"
            "    live.CURRENT_PORTFOLIO_VALUE,\n"
            "    hist.TOTAL_TRADES_5YR,\n"
            "    hist.LIFETIME_COMMISSION_PAID\n"
            "FROM \"aurora_catalog\".\"public\".\"dim_customers\" live\n"
            "INNER JOIN (\n"
            "    SELECT \n"
            "        CUSTOMER_ID,\n"
            "        COUNT(*) AS TOTAL_TRADES_5YR,\n"
            "        SUM(COMMISSION_FEE) AS LIFETIME_COMMISSION_PAID\n"
            "    FROM \"awsdatacatalog\".\"lakehouse_gold\".\"fact_historical_trades\"\n"
            "    WHERE trade_date >= '2021-01-01'\n"
            "    GROUP BY CUSTOMER_ID\n"
            ") hist \n"
            "ON live.CUSTOMER_ID = hist.CUSTOMER_ID;\n"
            "```"
        ),
        "interviewer_tip": "Mention 'Spill S3 Bucket' for Athena Federated Queries. When the external Aurora table returns large row sets, the Lambda connector spills intermediate Arrow buffers to S3 to prevent Lambda 10GB ephemeral storage limits from failing.",
        "follow_up_question": "Does Athena push down the WHERE clause to the Aurora PostgreSQL database?",
        "follow_up_answer": (
            "Yes! The Athena Lambda connector supports predicate pushdown: the `WHERE` filters on Aurora columns are translated into native PostgreSQL SQL "
            "and executed directly on Aurora, returning only matching rows across the wire."
        )
    },
    {
        "id": "aws_04",
        "domain": "AWS Data Services",
        "category": "AWS Data Services",
        "source_badge": "Citi Risk Analytics 2026",
        "scenario": (
            "Your data platform currently runs a 10-node Amazon EMR cluster (c5.4xlarge EC2 instances) 24/7 to process periodic PySpark batch jobs. "
            "The cluster sits idle 75% of the day, resulting in ₹4,50,000 monthly cloud waste. "
            "How do you migrate this workload to Amazon EMR Serverless, configuring application auto-scaling, ephemeral storage, and IAM job roles?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "तुमच्या कंपनीचा १० सर्व्हरचा EMR क्लस्टर २४ तास चालू असतो, पण काम फक्त दिवसातून ३-४ वेळाच असते (७५% वेळ सर्व्हर फुकट चालू राहून महिन्याला ४.५ लाख रुपये वाया जातात). "
            "हे कायमस्वरूपी सर्व्हर बंद करून 'EMR Serverless' वर कसे स्थलांतर करायचे? "
            "(जेव्हा काम येईल तेव्हाच सर्व्हर आपोआप सुरू होईल, काम संपले की बंद होईल, आणि जितके मिनिटे वापरले तितकेच पैसे लागतील)."
        ),
        "in_depth_answer": (
            "Migration to Amazon EMR Serverless Architecture:\n\n"
            "1. Architectural Benefits:\n"
            "- Zero EC2 cluster management, zero idle cost.\n"
            "- Pay strictly for vCPU, memory, and storage consumed by Spark drivers and executors down to the second.\n"
            "- Auto-scales from 0 to hundreds of vCPUs and scales back to 0 within 60 seconds of job completion.\n\n"
            "2. EMR Serverless Application Configuration:\n"
            "```bash\n"
            "# 1. Create EMR Serverless Application\n"
            "aws emr-serverless create-application \\\n"
            "    --type SPARK \\\n"
            "    --name BankingRiskBatchApp \\\n"
            "    --release-label emr-7.1.0 \\\n"
            "    --maximum-capacity '{ \"cpu\": \"100 vCPU\", \"memory\": \"400 GB\", \"disk\": \"2000 GB\" }' \\\n"
            "    --auto-stop-configuration '{ \"enabled\": true, \"idleTimeoutMinutes\": 5 }'\n"
            "```\n\n"
            "3. Submitting Job Run via Python Boto3:\n"
            "```python\n"
            "emr_client = boto3.client('emr-serverless')\n"
            "response = emr_client.start_job_run(\n"
            "    applicationId='app-1234567890',\n"
            "    executionRoleArn='arn:aws:iam::1234567890:role/EMRServerlessExecutionRole',\n"
            "    jobDriver={\n"
            "        'sparkSubmit': {\n"
            "            'entryPoint': 's3://banking-code/risk_calculation.py',\n"
            "            'entryPointArguments': ['--date', '2026-10-13'],\n"
            "            'sparkSubmitParameters': '--conf spark.executor.cores=4 --conf spark.executor.memory=16g --conf spark.dynamicAllocation.enabled=true'\n"
            "        }\n"
            "    }\n"
            ")\n"
            "```\n\n"
            "4. Cost Outcome: Monthly spend drops from ₹4,50,000 to ₹65,000 (an 85% cloud cost reduction)."
        ),
        "interviewer_tip": "Mention pre-initialized capacity. EMR Serverless supports pre-initialized worker pools if a business user requires jobs to start instantly in 2 seconds without waiting for container spin-up.",
        "follow_up_question": "How do you handle local disk spill in EMR Serverless if Spark shuffles exceed memory?",
        "follow_up_answer": (
            "We configure custom disk storage up to 200GB per worker in job parameters: "
            "`spark.emr-serverless.executor.disk=100G`. EMR Serverless mounts high-speed NVMe-backed ephemeral disk for shuffle spills."
        )
    },
    {
        "id": "aws_05",
        "domain": "AWS Data Services",
        "category": "AWS Data Services",
        "source_badge": "Standard Chartered Cloud Migration 2026",
        "scenario": (
            "You are streaming CDC transactions from an on-premise Finacle database to AWS S3 using AWS Database Migration Service (DMS). "
            "You notice that the DMS task intermittently fails with `Table Error: Out of Memory` when upstream core banking runs high-volume EOD batch updates. "
            "How do you tune AWS DMS task settings, CDC buffer limits, and commit rates to prevent task crashes?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेच्या मुख्य सर्व्हरवरून AWS DMS द्वारे S3 वर डेटा येत असताना, रात्री जेव्हा बँकेचा मोठा EOD बॅच चालतो, तेव्हा AWS DMS क्रॅश होतो "
            "आणि 'Out of Memory' एरर येतो. DMS टास्क सेटींग्ज, मेमरी बफर साईझ आणि कमिट रेट्स (Commit Rates) कसे ट्यून करायचे जेणेकरून लाखो ट्रॅन्झॅक्शन्स आले तरी DMS क्रॅश होणार नाही?"
        ),
        "in_depth_answer": (
            "AWS DMS Production Memory Tuning Architecture:\n\n"
            "1. Root Cause Analysis:\n"
            "During EOD batch processing, thousands of transactions commit in single multi-megabyte transactions. "
            "By default, DMS buffers uncommitted transactions in replication instance RAM. When memory threshold is breached, the replication task crashes.\n\n"
            "2. Production DMS Task Settings Tuning (`tasksettings.json`):\n"
            "```json\n"
            "{\n"
            "  \"TargetMetadata\": {\n"
            "    \"TargetSchema\": \"\",\n"
            "    \"SupportLobs\": true,\n"
            "    \"FullLobMode\": false,\n"
            "    \"LobChunkSize\": 64,\n"
            "    \"LimitedSizeLobMode\": true,\n"
            "    \"LobMaxSize\": 32\n"
            "  },\n"
            "  \"ChangeDataCaptureSettings\": {\n"
            "    \"MemoryLimitTotal\": 4096,\n"
            "    \"MemoryKeepTime\": 60,\n"
            "    \"StatementCacheSize\": 50,\n"
            "    \"BatchApplyEnabled\": true,\n"
            "    \"BatchApplyTimeoutMin\": 1,\n"
            "    \"BatchApplyTimeoutMax\": 30,\n"
            "    \"BatchSplitSize\": 5000\n"
            "  }\n"
            "}\n"
            "```\n\n"
            "3. Crucial Parameters:\n"
            "- `LimitedSizeLobMode = true`: Prevents unbounded LOB (Large Object) buffers from consuming RAM.\n"
            "- `MemoryLimitTotal = 4096`: Caps DMS memory before spilling overflow transactions to local replication disk.\n"
            "- `BatchApplyEnabled = true`: Bundles raw SQL statements into bulk batch arrays instead of single row-by-row transactions."
        ),
        "interviewer_tip": "Always call out `LimitedSizeLobMode`. Unrestricted Full LOB Mode is the #1 cause of AWS DMS out-of-memory crashes in enterprise financial pipelines.",
        "follow_up_question": "What if an individual LOB column genuinely exceeds 32KB?",
        "follow_up_answer": (
            "We use Inline LOB mode or configure S3 staging for large files, storing only the S3 URL pointer in the primary table."
        )
    },

    # =========================================================================
    # DOMAIN 8: CI/CD & ORCHESTRATION
    # =========================================================================
    {
        "id": "cicd_01",
        "domain": "CI/CD & Orchestration",
        "category": "CI/CD & Orchestration",
        "source_badge": "Barclays Enterprise Airflow 2026",
        "scenario": (
            "Your data engineering repository contains 250 distinct banking table ingestion models. Creating 250 separate Python DAG files "
            "caused the Apache Airflow Scheduler heartbeat to hang due to parse-time overhead. "
            "How do you design a Dynamic DAG generation pattern using YAML/JSON configuration files and single-file factory generation, "
            "while avoiding Airflow scheduler loop degradation?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेत २५० टेबल्ससाठी २५० वेगवेगळ्या Python फाईल्स बनवल्या, त्यामुळे Airflow चा शेड्युलर पूर्णपणे स्लो झाला आणि हँग झाला "
            "(कारण Airflow शेड्युलर दर ३० सेकंदांनी सर्व २५० फाईल्स पुन्हा वाचत बसतो). "
            "२५० स्वतंत्र फाईल्स न बनवता, एकाच YAML कॉन्फिगरेशन फाईलवरून आपोआप सर्व २५० DAGs डायनॅमिकली कसे तयार करायचे (Dynamic DAG Generation)?"
        ),
        "in_depth_answer": (
            "Dynamic DAG Factory Pattern for Airflow:\n\n"
            "1. Why Naive Dynamic DAGs Crash Airflow:\n"
            "If your DAG file makes external network calls (e.g., querying database tables or calling an API) during top-level code execution, "
            "the Airflow scheduler executes those network calls every 30 seconds during DAG parsing, freezing scheduler worker threads.\n\n"
            "2. Production Single-File Dynamic DAG Factory:\n"
            "Read configuration from local static JSON/YAML files (or environment variables) without external network I/O:\n\n"
            "```python\n"
            "import os\n"
            "import yaml\n"
            "from airflow import DAG\n"
            "from airflow.operators.python import PythonOperator\n"
            "from datetime import datetime\n\n"
            "CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'configs')\n\n"
            "def create_dag(dag_id: str, schedule: str, table_name: str):\n"
            "    default_args = {\n"
            "        'owner': 'data_eng',\n"
            "        'start_date': datetime(2026, 1, 1),\n"
            "        'retries': 2\n"
            "    }\n"
            "    \n"
            "    dag = DAG(dag_id=dag_id, schedule_interval=schedule, default_args=default_args, catchup=False)\n"
            "    \n"
            "    with dag:\n"
            "        PythonOperator(\n"
            "            task_id=f'ingest_{table_name}',\n"
            "            python_callable=run_table_ingest,\n"
            "            op_kwargs={'table': table_name}\n"
            "        )\n"
            "    return dag\n\n"
            "# Iterate through local YAML configurations\n"
            "for config_file in os.listdir(CONFIG_DIR):\n"
            "    if config_file.endswith('.yaml'):\n"
            "        with open(os.path.join(CONFIG_DIR, config_file)) as f:\n"
            "            cfg = yaml.safe_load(f)\n"
            "            dag_id = f\"ingest_cbs_{cfg['table_name']}\"\n"
            "            globals()[dag_id] = create_dag(dag_id, cfg['cron_schedule'], cfg['table_name'])\n"
            "```\n\n"
            "3. Airflow Rule:\n"
            "Injecting into `globals()` allows Airflow to register all 250 DAGs in $<0.4$ seconds parse time."
        ),
        "interviewer_tip": "Mention `catchup=False`. Without `catchup=False`, creating 250 dynamic DAGs with an older `start_date` triggers an accidental historical backfill storm of thousands of DAG runs, overwhelming workers.",
        "follow_up_question": "Why shouldn't you query a database inside the top-level loop of a DAG file?",
        "follow_up_answer": (
            "Because Airflow's DagFileProcessor loops through every DAG file every `min_file_process_interval` (default 30s). "
            "A database call inside the loop opens 250 database connections every 30 seconds, leading to connection pool exhaustion and scheduler freeze."
        )
    },
    {
        "id": "cicd_02",
        "domain": "CI/CD & Orchestration",
        "category": "CI/CD & Orchestration",
        "source_badge": "Morgan Stanley Production DAGs 2026",
        "scenario": (
            "In your Apache Airflow production environment, 40 batch DAGs each run an `S3KeySensor` waiting for files from upstream teams. "
            "Suddenly, all Airflow workers become unresponsive, and other critical DAGs fail to start because no worker slots are available. "
            "Explain Airflow Sensor Deadlocks and how configuring `mode='reschedule'` and `exponential_backoff` resolves this issue."
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "Airflow मध्ये ४० DAGs वर 'S3KeySensor' लावलेला आहे (जो S3 मध्ये फाईल आली आहे का ते तपासतो). "
            "फाईल उशिरा आल्यामुळे सर्व ४० सेन्सर्स वर्कर स्लॉट पकडून (occupy करून) बसून राहिले, ज्यामुळे इतर महत्त्वाचे DAGs सुरूच होऊ शकले नाहीत (Sensor Deadlock). "
            "`mode='poke'` काढून `mode='reschedule'` का करायचा? यामुळे वर्कर स्लॉट कसा मोकळा होतो?"
        ),
        "in_depth_answer": (
            "Airflow Sensor Deadlock Architecture & Resolution:\n\n"
            "1. The Poke Mode Deadlock Problem:\n"
            "By default, Airflow sensors operate in `mode='poke'`. In poke mode, the sensor process holds its worker execution slot continuously, "
            "sleeping for 60 seconds and checking again. If you have 32 worker slots and 32 sensors waiting for a delayed file, ALL worker slots "
            "are locked by idle sleeping sensors. No other pipeline can run, causing a complete system deadlock.\n\n"
            "2. Production Solution with `mode='reschedule'`:\n"
            "In `mode='reschedule'`, the sensor checks the file once. If the file is not present, the sensor task releases its worker slot, "
            "terminates its OS process, and re-enters the Airflow task queue in `UP_FOR_RESCHEDULE` state. Another waiting task can immediately use the free worker slot!\n\n"
            "```python\n"
            "from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor\n\n"
            "wait_for_cbs_feed = S3KeySensor(\n"
            "    task_id='wait_for_cbs_s3_file',\n"
            "    bucket_name='banking-lake-landing',\n"
            "    bucket_key='feeds/cbs/{{ ds }}/transactions.csv',\n"
            "    mode='reschedule',  # Releases worker slot between checks\n"
            "    poke_interval=300,   # Checks every 5 minutes\n"
            "    timeout=14400,       # 4 hours hard timeout\n"
            "    exponential_backoff=True,\n"
            "    soft_fail=False\n"
            ")\n"
            "```"
        ),
        "interviewer_tip": "Mention `soft_fail=True` vs `soft_fail=False`. With `soft_fail=True`, if the file never arrives within 4 hours, the task completes as `SKIPPED` rather than `FAILED`, which is ideal for optional weekend feeds.",
        "follow_up_question": "What is an Airflow Deferrable Operator?",
        "follow_up_answer": (
            "Deferrable Operators take this even further using Python `asyncio` triggers. A single lightweight `Triggerer` daemon monitors hundreds of sensors "
            "asynchronously, consuming zero worker slots and zero task state transitions until the external event fires."
        )
    },
    {
        "id": "cicd_03",
        "domain": "CI/CD & Orchestration",
        "category": "CI/CD & Orchestration",
        "source_badge": "Goldman Sachs Data Platform 2026",
        "scenario": (
            "Your data engineering pipelines run dbt-core transformations and PySpark tasks. Different teams require different library versions "
            "(e.g., Team A requires `pandas==1.5.3`, while Team B requires `pandas==2.2.0`). Upgrading the host Airflow worker causes package conflicts. "
            "How do you containerize pipeline execution using Airflow's `KubernetesPodOperator` to guarantee total dependency isolation and ephemeral security?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "एका टीमला Python मधील जुने लायब्ररी व्हर्जन लागते, तर दुसऱ्या टीमला नवीन लागते. मुख्य सर्व्हरवर लायब्ररी अपडेट केली की दुसऱ्यांचा कोड क्रॅश होतो (Dependency Hell). "
            "Airflow चा `KubernetesPodOperator` वापरून प्रत्येक टास्क एका स्वतंत्र Docker कंटेनरमध्ये कशी चालवायची? "
            "(टास्क सुरू झाली की नवीन कंटेनर तयार होईल, काम झाले की कंटेनर नष्ट होईल—कोणताही वाद नाही!)."
        ),
        "in_depth_answer": (
            "Containerized Execution via KubernetesPodOperator:\n\n"
            "1. Architectural Principle:\n"
            "Decouple the Airflow orchestration layer from task execution runtime dependencies. Airflow workers only dispatch task requests; "
            "all transformation logic, binaries, and specific Python packages execute inside dedicated Docker images on a Kubernetes (EKS) cluster.\n\n"
            "```python\n"
            "from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator\n"
            "from kubernetes.client import models as k8s\n\n"
            "run_dbt_transformation = KubernetesPodOperator(\n"
            "    task_id='dbt_aml_mart_transform',\n"
            "    name='dbt-aml-pod',\n"
            "    namespace='data-pipelines',\n"
            "    image='1234567890.dkr.ecr.ap-south-1.amazonaws.com/banking/dbt-aml:v2.4',\n"
            "    cmds=['dbt'],\n"
            "    arguments=['run', '--models', 'tag:aml_gold', '--target', 'prod'],\n"
            "    secrets=[\n"
            "        # Injected from Kubernetes Secret Vault at runtime (never embedded in code)\n"
            "        k8s.V1SecretKeySelector(name='snowflake-credentials', key='SNOWFLAKE_PASSWORD')\n"
            "    ],\n"
            "    container_resources=k8s.V1ResourceRequirements(\n"
            "        requests={'memory': '2Gi', 'cpu': '1000m'},\n"
            "        limits={'memory': '4Gi', 'cpu': '2000m'}\n"
            "    ),\n"
            "    is_delete_operator_pod=True,  # Pod destroyed on completion (ephemeral)\n"
            "    get_logs=True\n"
            ")\n"
            "```"
        ),
        "interviewer_tip": "Mention `is_delete_operator_pod=True`. In production, if you forget this flag, thousands of finished pods remain in the Kubernetes cluster in `Completed` state, exhausting the Kubernetes API server's etcd memory.",
        "follow_up_question": "How do you inspect logs if the pod is deleted on completion?",
        "follow_up_answer": (
            "`get_logs=True` streams the pod's stdout/stderr in real-time directly to the Airflow task log UI. "
            "Additionally, Kubernetes cluster log forwarders (FluentBit) stream all container logs to Amazon CloudWatch."
        )
    },
    {
        "id": "cicd_04",
        "domain": "CI/CD & Orchestration",
        "category": "CI/CD & Orchestration",
        "source_badge": "Amazon DE Platform 2026",
        "scenario": (
            "You are designing a professional GitHub Actions CI/CD pipeline for your team's Data Engineering repository. "
            "Before any pull request can be merged into the `main` branch, the pipeline must automatically: (1) Run SQLFluff linter on all SQL files, "
            "(2) Run pytest unit tests against an ephemeral DuckDB in-memory database, (3) Compile dbt models against a staging catalog, "
            "and (4) Block the merge if any test fails. How do you structure this GitHub Actions workflow?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "डेटा इंजिनिअरिंग टीमच्या कोडसाठी एक स्वयंचलित GitHub Actions CI/CD पाईपलाईन तयार करायची आहे. "
            "कोणीही नवीन कोड सबमिट केला की कोड आपोआप तपासला गेला पाहिजे:\n"
            "१. SQLFluff ने सर्व SQL ची स्टाईल आणि सिंटेक्स तपासणे.\n"
            "२. PyTest ने इन-मेमरी DuckDB वर युनिट टेस्ट रन करणे.\n"
            "३. dbt compile व्यवस्थित होतेय का तपासणे.\n"
            "जर एकही टेस्ट फेल झाली, तर कोड मुख्य सिस्टिममध्ये जाण्यापासून रोखणे (Block PR Merge). हे कसे लिहायचे?"
        ),
        "in_depth_answer": (
            "Production GitHub Actions CI/CD Pipeline:\n\n"
            "```yaml\n"
            "name: Data Engineering CI/CD Gate\n\n"
            "on:\n"
            "  pull_request:\n"
            "    branches: [ main ]\n\n"
            "jobs:\n"
            "  quality_gate:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Checkout Source Code\n"
            "        uses: actions/checkout@v4\n\n"
            "      - name: Set up Python 3.11\n"
            "        uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.11'\n"
            "          cache: 'pip'\n\n"
            "      - name: Install Linting & Test Dependencies\n"
            "        run: |\n"
            "          pip install sqlfluff==3.0.0 pytest==8.1.0 duckdb==0.10.0 dbt-snowflake==1.8.0\n\n"
            "      - name: Step 1: SQLFluff Linting Check (Snowflake Dialect)\n"
            "        run: sqlfluff lint models/ --dialect snowflake --strict\n\n"
            "      - name: Step 2: PyTest Unit Tests with In-Memory DuckDB\n"
            "        run: pytest tests/unit/ -v --maxfail=1\n\n"
            "      - name: Step 3: dbt Syntax & Model Compilation\n"
            "        env:\n"
            "          SNOWFLAKE_ACCOUNT: ${{ secrets.SF_ACCOUNT }}\n"
            "          SNOWFLAKE_USER: ${{ secrets.SF_CI_USER }}\n"
            "          SNOWFLAKE_PASSWORD: ${{ secrets.SF_CI_PASSWORD }}\n"
            "        run: dbt compile --target ci\n"
            "```\n\n"
            "Rule: Branch protection rules in GitHub prevent PR merging unless `quality_gate` reports status `SUCCESS`."
        ),
        "interviewer_tip": "Highlight using DuckDB for CI testing. Spinning up a full Snowflake warehouse for every PR costs money and takes minutes, while DuckDB runs mock SQL tests in 1.2 seconds directly in GitHub runners for $0.",
        "follow_up_question": "How do you ensure SQLFluff doesn't fail on proprietary Snowflake macros?",
        "follow_up_answer": (
            "We configure `.sqlfluff` configuration file setting `dialect = snowflake` and configure `templater = dbt` "
            "so SQLFluff compiles dbt Jinja macros before linting."
        )
    },
    {
        "id": "cicd_05",
        "domain": "CI/CD & Orchestration",
        "category": "CI/CD & Orchestration",
        "source_badge": "Utkarsh Small Finance Bank EOD 2026",
        "scenario": (
            "At Utkarsh Small Finance Bank, you designed Start-of-Day (SOD) and End-of-Day (EOD) orchestration workflows. "
            "The EOD pipeline consists of 3 distinct DAGs: (1) `DAG_CBS_SFTP_EXTRACT`, (2) `DAG_SNOWFLAKE_RECON`, and (3) `DAG_AML_SURVEILLANCE_MART`. "
            "`DAG_AML` must only execute if `DAG_RECON` finishes with 100% reconciliation match. "
            "How do you implement Cross-DAG dependencies using Airflow's `ExternalTaskSensor` and `TriggerDagRunOperator`?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "उत्कर्ष स्मॉल फायनान्स बँकेत दिवसाअखेरचे (EOD) ३ स्वतंत्र DAGs आहेत:\n"
            "१. फाईल्स डाऊनलोड करणारा DAG\n"
            "२. डेटा रिकन्साईल करणारा DAG\n"
            "३. AML मनी लाँड्रिंग चेक करणारा DAG.\n"
            "नियम असा आहे की जोपर्यंत रिकन्सिलिएशन १००% जुळत नाही, तोपर्यंत AML DAG सुरू होता कामा नये. "
            "Airflow मधील एका DAG मधून दुसऱ्या DAG ला ट्रिगर कसे करायचे किंवा दुसऱ्या DAG ची वाट कशी पाहायची (`ExternalTaskSensor` आणि `TriggerDagRunOperator`)?"
        ),
        "in_depth_answer": (
            "Cross-DAG Orchestration Pattern:\n\n"
            "Method 1: TriggerDagRunOperator with Conditional Logic:\n"
            "Inside `DAG_SNOWFLAKE_RECON`, a Python branching task checks if the reconciliation match rate is 100%. "
            "If matched, it executes `TriggerDagRunOperator` to trigger the downstream AML DAG:\n\n"
            "```python\n"
            "from airflow.operators.trigger_dagrun import TriggerDagRunOperator\n"
            "from airflow.operators.python import BranchPythonOperator\n\n"
            "def verify_recon_quality(ti):\n"
            "    match_rate = ti.xcom_pull(task_ids='calculate_recon_match', key='recon_match_rate')\n"
            "    if match_rate == 100.0:\n"
            "        return 'trigger_aml_dag'\n"
            "    return 'alert_compliance_officer'\n\n"
            "trigger_aml = TriggerDagRunOperator(\n"
            "    task_id='trigger_aml_dag',\n"
            "    trigger_dag_id='DAG_AML_SURVEILLANCE_MART',\n"
            "    conf={'triggered_by': 'EOD_RECON', 'batch_date': '{{ ds }}'},\n"
            "    wait_for_completion=False\n"
            ")\n"
            "```\n\n"
            "Method 2: ExternalTaskSensor (Downstream DAG pulls state from Upstream DAG):\n"
            "```python\n"
            "from airflow.sensors.external_task import ExternalTaskSensor\n\n"
            "wait_for_recon = ExternalTaskSensor(\n"
            "    task_id='wait_for_eod_recon_completion',\n"
            "    external_dag_id='DAG_SNOWFLAKE_RECON',\n"
            "    external_task_id='final_recon_signoff',\n"
            "    mode='reschedule',\n"
            "    timeout=7200\n"
            ")\n"
            "```"
        ),
        "interviewer_tip": "Highlight execution date alignment. When using `ExternalTaskSensor`, both DAGs must either share the exact same `execution_date` schedule, or you must supply an `execution_date_fn` parameter to translate schedules.",
        "follow_up_question": "What if DAG_RECON runs daily at 23:00, but DAG_AML runs at 01:00 the next day?",
        "follow_up_answer": (
            "We supply an `execution_delta=timedelta(hours=2)` parameter or use custom `execution_date_fn` in the `ExternalTaskSensor` "
            "to bridge the 2-hour schedule offset."
        )
    },

    # =========================================================================
    # DOMAIN 9: GENERATIVE AI & LLMOPS IN DATA ENGINEERING
    # =========================================================================
    {
        "id": "genai_01",
        "domain": "Generative AI & LLMOps",
        "category": "Generative AI & LLMOps",
        "source_badge": "Citi AI Innovation Lab 2026",
        "scenario": (
            "You are building a production Text-to-SQL copilot for non-technical banking relationship managers who query "
            "a 400-table core banking data warehouse in plain English. Generic LLMs often hallucinate invalid column names "
            "or attempt destructive `DROP/DELETE` statements. How do you design an enterprise Text-to-SQL architecture using "
            "Retrieval-Augmented Generation (RAG) on database schemas, AST SQL validation, and Read-Only role enforcement?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेच्या मॅनेजर्सना SQL येत नाही. ते साध्या इंग्रजीत प्रश्न विचारतात: 'गेल्या महिन्यात सर्वात जास्त FD कोणी काढली?'. "
            "आपल्याला असा AI बनवायचा आहे जो हा प्रश्न वाचून अचूक SQL क्वेरी लिहून देईल. "
            "पण AI चुकीचे कॉलम नावे मनाने बनवू नये (Hallucination) किंवा चुकून `DROP TABLE` लिहू नये, यासाठी "
            "RAG (स्कीमा शोधणे), SQL Parser (क्वेरी तपासणे) आणि Read-Only परमिशन अशी तिहेरी सुरक्षा कशी लावायची?"
        ),
        "in_depth_answer": (
            "Production Text-to-SQL Enterprise Architecture:\n\n"
            "1. Layer 1: Schema Vectorization & RAG Context Retrieval:\n"
            "- Rather than dumping all 400 tables into the LLM prompt (which blows up the token context and causes hallucinations), "
            "we index table DDLs, column comments, and business glossary terms in a Vector DB (Snowflake Cortex Search / Chroma).\n"
            "- The user's query ('Find top FD accounts in Mumbai') retrieves ONLY the top 3 relevant table schemas (`DIM_CUSTOMER`, `FACT_DEPOSITS`, `DIM_BRANCH`).\n\n"
            "2. Layer 2: Few-Shot Constrained Prompting:\n"
            "The system prompt includes the retrieved DDLs and 3 verified golden SQL query examples matching the target database dialect (Snowflake SQL).\n\n"
            "3. Layer 3: AST Parsing & Security Gate:\n"
            "```python\n"
            "import sqlglot\n"
            "from sqlglot.expressions import Drop, Delete, Update, Insert\n\n"
            "def validate_generated_sql(sql_str: str):\n"
            "    parsed = sqlglot.parse_one(sql_str, read='snowflake')\n"
            "    # Reject any non-SELECT statement\n"
            "    for bad_op in (Drop, Delete, Update, Insert):\n"
            "        if parsed.find(bad_op):\n"
            "            raise PermissionError('Security Violation: Generated SQL contains non-read operations.')\n"
            "    return parsed.sql(dialect='snowflake')\n"
            "```\n\n"
            "4. Layer 4: Execution Sandbox:\n"
            "Query runs strictly under an unprivileged `READONLY_ANALYST` role with a 15-second statement timeout."
        ),
        "interviewer_tip": "Mention `sqlglot.parse_one`. A regex search for the word 'DELETE' is flawed (a column might be named `IS_DELETED`), whereas AST parsing understands semantic grammar without false positives.",
        "follow_up_question": "How do you handle queries where the user says 'Show me sales in Bombay' but the database column uses 'MUMBAI'?",
        "follow_up_answer": (
            "We maintain a vector-indexed categorical value map: during retrieval, 'Bombay' maps to canonical categorical value 'MUMBAI', "
            "which is explicitly injected as a few-shot hint in the LLM prompt."
        )
    },
    {
        "id": "genai_02",
        "domain": "Generative AI & LLMOps",
        "category": "Generative AI & LLMOps",
        "source_badge": "Snowflake AI Research 2026",
        "scenario": (
            "When production data pipelines fail at 02:00 AM IST, on-call data engineers spend 45 minutes sifting through 10,000 lines "
            "of Airflow stack traces, Spark driver logs, and Snowflake error codes. How do you build an Autonomous AI Pipeline Incident Remediation Agent "
            "using local LLMs (Qwen2.5-Coder / DeepSeek) that parses raw log streams, identifies the root cause, and synthesizes an approved remediation script?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "रात्री २ वाजता जेव्हा Airflow किंवा Spark चा जॉब क्रॅश होतो, तेव्हा १०,००० ओळींचे लॉग्स वाचून नक्की काय चुकले हे शोधायला इंजिनिअरचा १ तास जातो. "
            "आपल्याला एक 'Autonomous AI Agent' बनवायचा आहे जो क्रॅश झाल्या क्षणी लॉग्स वाचेल, मूळ कारण (Root Cause) शोधेल, "
            "आणि समस्येचे १-ओळीचे निवारण (Fix Script) तयार करून Telegram आणि ई-मेलवर ऑन-कॉल इंजिनिअरला पाठवेल."
        ),
        "in_depth_answer": (
            "Autonomous Incident Remediation Agent Architecture:\n\n"
            "1. Architectural Pipeline:\n"
            "- Step 1 (Log Sanitization & Regex Extractor): Strip repetitive heartbeat log lines, mask passwords/tokens, and extract error frames containing `Traceback`, `SQLException`, `OutOfMemoryError`.\n"
            "- Step 2 (Local LLM Inference): Pipe sanitized log snippet into a local high-performance code model (`qwen2.5-coder:7b`) via Ollama/vLLM.\n"
            "- Step 3 (Structured Remediation Output): Instruct the model to return JSON matching a strict Pydantic schema: `root_cause`, `affected_table`, `remediation_sql`, `requires_manual_approval`.\n\n"
            "```python\n"
            "# Production Agent Core\n"
            "def diagnose_pipeline_crash(raw_log: str) -> dict:\n"
            "    sanitized_snippet = extract_error_context(raw_log, max_lines=80)\n"
            "    prompt = f\"\"\"\n"
            "    You are a Principal Data Engineer. Analyze this pipeline failure log:\n"
            "    {sanitized_snippet}\n"
            "    Return JSON:\n"
            "    {{\n"
            "      \"error_summary\": \"one line diagnosis\",\n"
            "      \"root_cause_type\": \"DATA_SKEW | SCHEMA_DRIFT | NETWORK | LOCK_TIMEOUT\",\n"
            "      \"remediation_script\": \"exact SQL or bash command to fix\"\n"
            "    }}\n"
            "    \"\"\"\n"
            "    response = ollama_client.chat(model='qwen2.5-coder:7b', messages=[{'role': 'user', 'content': prompt}])\n"
            "    return json.loads(response['message']['content'])\n"
            "```\n\n"
            "2. Telegram Dispatch:\n"
            "The synthesized diagnosis and remediation script are dispatched immediately to Telegram (`@mangesh_technews_bot`)."
        ),
        "interviewer_tip": "Emphasize security and local execution: cloud APIs like ChatGPT must not receive proprietary enterprise banking logs containing internal server IP addresses or table names. Running local Ollama / vLLM preserves 100% data residency.",
        "follow_up_question": "Should the AI automatically execute the remediation script without human intervention?",
        "follow_up_answer": (
            "For non-destructive idempotent actions (e.g., retrying a failed task or resuming a suspended task), yes. "
            "For any DDL alterations, table drops, or rollback queries, we strictly require human approval via a Telegram interactive callback button."
        )
    },
    {
        "id": "genai_03",
        "domain": "Generative AI & LLMOps",
        "category": "Generative AI & LLMOps",
        "source_badge": "JPMorgan AI Research 2026",
        "scenario": (
            "Your vendor testing team needs 500,000 realistic banking transaction records to benchmark a new credit card authorization system. "
            "Due to privacy regulations, you cannot share production data. Generating random numbers fails because vendor tests need realistic "
            "statistical correlations (e.g., higher spending on weekends, fraud rings clustered in specific PIN codes). "
            "How do you design a Synthetic Financial Data Generation pipeline using Generative AI with Differential Privacy?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "सॉफ्टवेअर टेस्ट करण्यासाठी व्हेंडर कंपनीला ५ लाख बँक ट्रॅन्झॅक्शन्स हवे आहेत. पण गोपनीयतेमुळे तुम्ही खरा ग्राहक डेटा देऊ शकत नाही. "
            "आणि जर अंदाजे खोटा डेटा बनवला, तर त्यात खरी बँकिंगची पॅटर्न्स (जसे शनिवार-रविवार जास्त खर्च होणे, किंवा विशिष्ट पिनकोडवर जास्त व्यवहार) दिसत नाहीत. "
            "खऱ्या डेटाची सांख्यिकी (Statistical Patterns) राखून, पण कोणत्याही ग्राहकाचा खरा नंबर न दाखवता, AI द्वारे ५ लाख हुबेहूब कृत्रिम (Synthetic) रेकॉर्ड्स कसे बनवायचे?"
        ),
        "in_depth_answer": (
            "Synthetic Financial Data Generation Architecture:\n\n"
            "1. Architectural Method: Tabular Variational Autoencoders (TVAE) / CTGAN:\n"
            "We train a conditional generative model (CTGAN) on historical transactional distributions with Differential Privacy ($\epsilon$-differential privacy).\n"
            "- It learns mathematical probability distributions: marginal distributions of amounts, conditional correlations between merchant categories and time-of-day, and geographic clustering.\n"
            "- Differential Privacy adds calibrated Laplacian or Gaussian noise to gradients during training, guaranteeing mathematically that no individual row from the training set can be reconstructed.\n\n"
            "2. Synthetic Generation Pipeline in Python:\n"
            "```python\n"
            "from sdv.single_table import CTGANSynthesizer\n"
            "from sdv.metadata import SingleTableMetadata\n\n"
            "def generate_synthetic_banking_data(sample_df, num_rows=500000):\n"
            "    metadata = SingleTableMetadata()\n"
            "    metadata.detect_from_dataframe(data=sample_df)\n"
            "    metadata.update_column(column_name='CARD_NUMBER', sdtype='credit_card_number')\n"
            "    \n"
            "    synthesizer = CTGANSynthesizer(metadata, epochs=30, verbose=True)\n"
            "    synthesizer.fit(sample_df)\n"
            "    \n"
            "    # Generate realistic synthetic data\n"
            "    synthetic_data = synthesizer.sample(num_rows=num_rows)\n"
            "    return synthetic_data\n"
            "```\n\n"
            "3. Validation:\n"
            "We compute KS-Complement and Chi-Squared statistical similarity metrics, ensuring $>96\%$ statistical fidelity without leaking real customer identities."
        ),
        "interviewer_tip": "Mention $\epsilon$ (Epsilon) in Differential Privacy. A lower $\epsilon$ value guarantees stronger mathematical privacy protection at the cost of slightly lower statistical fidelity.",
        "follow_up_question": "How do you prove to regulatory auditors that no real customer PII was leaked in the synthetic output?",
        "follow_up_answer": (
            "We run a Nearest Neighbor Distance Ratio (NNDR) test. We verify that the distance between every synthetic record and its closest real record "
            "is strictly above zero, proving zero exact matches and zero identity leakage."
        )
    },
    {
        "id": "genai_04",
        "domain": "Generative AI & LLMOps",
        "category": "Generative AI & LLMOps",
        "source_badge": "Morgan Stanley Tech Mart 2026",
        "scenario": (
            "Your enterprise uses LLMs to automatically ingest and tag 10,000 data catalog tables with business descriptions and data classifications. "
            "Occasionally, the LLM hallucinates incorrect compliance tags (e.g., tagging public holidays as 'CONFIDENTIAL_PII' or tagging credit cards as 'PUBLIC'). "
            "How do you implement LLMOps Evaluation frameworks (Ragas / TruLens / LlamaGuard) and deterministic guardrails in the metadata pipeline?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "१०,००० डेटाबेस टेबल्सना बिझनेस टॅग्ज लावण्यासाठी तुम्ही AI वापरत आहात. पण कधीकधी AI चुका करतो—क्रेडिट कार्डच्या नंबरला 'पब्लिक' टॅग लावून टाकतो "
            "किंवा कॅलेंडरच्या सुट्ट्यांना 'अति-गोपनीय' म्हणून चिन्हांकित करतो! "
            "AI ने जनरेट केलेले टॅग्ज आणि माहिती मुख्य डेटाबेसमध्ये जाण्याआधी, LLMOps गार्डरेल्स (Guardrails) द्वारे "
            "त्यांची खात्री (Validation) कशी करायची?"
        ),
        "in_depth_answer": (
            "LLMOps Metadata Evaluation & Guardrails Architecture:\n\n"
            "1. Two-Tier Validation Pattern:\n"
            "Never write unvalidated LLM output directly into production catalogs. Run an automated deterministic guardrail evaluation suite "
            "prior to metadata persistence.\n\n"
            "```python\n"
            "from pydantic import BaseModel, Field, validator\n"
            "from typing import List, Literal\n\n"
            "# 1. Pydantic Strict Schema Enforcement\n"
            "class CatalogEnrichment(BaseModel):\n"
            "    table_name: str\n"
            "    business_summary: str = Field(min_length=20, max_length=500)\n"
            "    classification_tier: Literal['PUBLIC', 'INTERNAL', 'CONFIDENTIAL_PII', 'RESTRICTED']\n"
            "    detected_pii_columns: List[str]\n\n"
            "    @validator('classification_tier')\n"
            "    def validate_pii_consistency(cls, v, values):\n"
            "        pii_cols = values.get('detected_pii_columns', [])\n"
            "        # Deterministic Guardrail: If PAN or CARD in columns, CANNOT be PUBLIC\n"
            "        if any('pan' in col.lower() or 'card' in col.lower() for col in pii_cols):\n"
            "            if v in ['PUBLIC', 'INTERNAL']:\n"
            "                raise ValueError('Guardrail Violation: Card/PAN columns detected but classified as PUBLIC!')\n"
            "        return v\n"
            "```\n\n"
            "2. LLM-as-a-Judge Evaluation via TruLens:\n"
            "Sample 5% of enriched descriptions daily and score for: (1) Groundedness, (2) Answer Relevance, and (3) Context Adherence."
        ),
        "interviewer_tip": "Pair LLMs with deterministic Pydantic schemas and regex checks. LLMs excel at drafting human explanations, but deterministic rules must enforce final compliance validation.",
        "follow_up_question": "What if an LLM response fails validation 3 times in a row?",
        "follow_up_answer": (
            "The pipeline assigns a fallback tag `NEEDS_HUMAN_TRIAGE`, alerts the data governance steward on Slack/Teams, and continues processing the remaining tables."
        )
    },
    {
        "id": "genai_05",
        "domain": "Generative AI & LLMOps",
        "category": "Generative AI & LLMOps",
        "source_badge": "Standard Chartered Wealth AI 2026",
        "scenario": (
            "Your bank processes 100,000 scanned PDF commercial loan agreements. Wealth advisors need to perform hybrid search "
            "(dense vector embedding search for semantic meaning + BM25 keyword search for exact interest rates and contract numbers) "
            "to answer compliance questions. How do you build an end-to-end multimodal ingestion and hybrid vector pipeline in Snowflake Cortex Search?"
        ),
        "marathi_summary": (
            "या प्रश्नाचा नेमका अर्थ काय आहे?:\n"
            "बँकेकडे १ लाख स्कॅन केलेल्या कर्जाच्या PDF फाईल्स आहेत. मॅनेजर्सना त्यातील मजकूर शोधायचा आहे. "
            "फक्त अर्थ शोधून चालणार नाही (उदा. 'लोन डिफॉल्ट नियम'), तर अचूक नंबर सुद्धा सापडला पाहिजे (उदा. '८.७५% व्याज' किंवा करार क्रमांक 'LN-90812'). "
            "यासाठी 'Hybrid Search' (Dense Vector Embeddings + BM25 Keywords) वापरून Snowflake Cortex द्वारे हाय-स्पीड सर्च इंजिन कसे उभे करायचे?"
        ),
        "in_depth_answer": (
            "Multimodal Hybrid Search Ingestion Architecture via Snowflake Cortex:\n\n"
            "1. Architectural Strategy:\n"
            "- Dense Vector Embeddings capture conceptual intent ('What happens if borrower defaults?').\n"
            "- Sparse BM25 / Keyword Search captures exact alphanumerics ('Loan Agreement #LN-2026-X89' or '8.75%').\n"
            "- Snowflake Cortex Search natively integrates both using reciprocal rank fusion (RRF).\n\n"
            "2. Ingestion & Embedding Pipeline:\n"
            "```sql\n"
            "-- Step 1: Chunked Document Staging\n"
            "CREATE OR REPLACE TABLE LOAN_DOC_CHUNKS (\n"
            "    DOC_ID VARCHAR,\n"
            "    CHUNK_ID VARCHAR,\n"
            "    CHUNK_TEXT VARCHAR,\n"
            "    CONTRACT_NUMBER VARCHAR,\n"
            "    INTEREST_RATE FLOAT\n"
            ");\n\n"
            "-- Step 2: Create Snowflake Cortex Search Service\n"
            "CREATE OR REPLACE CORTEX SEARCH SERVICE CSS_LOAN_CONTRACTS\n"
            "ON CHUNK_TEXT\n"
            "ATTRIBUTES CONTRACT_NUMBER, INTEREST_RATE\n"
            "WAREHOUSE = COMPUTE_WH\n"
            "TARGET_LAG = '1 hour'\n"
            "AS (\n"
            "    SELECT DOC_ID, CHUNK_ID, CHUNK_TEXT, CONTRACT_NUMBER, INTEREST_RATE\n"
            "    FROM LOAN_DOC_CHUNKS\n"
            ");\n"
            "```\n\n"
            "3. Querying via Python REST API:\n"
            "```python\n"
            "def query_cortex_search(user_query: str, target_contract: str):\n"
            "    response = cortex_client.search(\n"
            "        service_name='CSS_LOAN_CONTRACTS',\n"
            "        query=user_query,\n"
            "        columns=['DOC_ID', 'CHUNK_TEXT', 'INTEREST_RATE'],\n"
            "        filter={'@eq': {'CONTRACT_NUMBER': target_contract}},\n"
            "        limit=5\n"
            "    )\n"
            "    return response['results']\n"
            "```"
        ),
        "interviewer_tip": "Highlight Reciprocal Rank Fusion (RRF). RRF mathematically normalizes rank scores from dense vector cosine similarity and sparse BM25 keyword matching without needing manual weight tuning.",
        "follow_up_question": "What chunking strategy do you use for legal banking contracts?",
        "follow_up_answer": (
            "We use Recursive Character Splitting with section-aware boundaries (splitting by clauses: 'Section 1.1', 'Clause 4.2') "
            "with a chunk size of 1000 tokens and 200 token overlap to prevent splitting contractual definitions across chunk boundaries."
        )
    }
]

def get_all_scenario_questions(category: str = None) -> List[Dict[str, Any]]:
    """Returns scenario questions optionally filtered by domain category."""
    if not category or category.lower() in ["all", "all domains", "all scenarios"]:
        return PRODUCTION_SCENARIO_QUESTIONS
    cat_lower = category.lower().strip()
    return [
        q for q in PRODUCTION_SCENARIO_QUESTIONS
        if cat_lower in q.get("domain", "").lower() or cat_lower in q.get("category", "").lower()
    ]
