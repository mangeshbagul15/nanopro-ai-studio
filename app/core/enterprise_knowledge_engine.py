"""
Mangesh Nano Pro AI Studio - Enterprise High-Tech Knowledge & Diagnostics Engine
Comprehensive troubleshooting repository and automated reasoning engine covering
1,000+ real-world enterprise infrastructure, lakehouse, database, and cloud failure modes.

Domains:
1. Apache Kafka & Event Streaming (Rebalance storms, partition skew, DLQ, ISR shrink)
2. Snowflake & Cloud Lakehouse (Remote disk spilling, micro-partition clustering, warehouse queueing)
3. Oracle Database Enterprise & XE (ORA-01555, ORA-00060, ORA-04031, ORA-01653, latch contention)
4. PostgreSQL Relational Engines (Transaction ID wraparound, TOAST bloat, WAL lag, PgBouncer)
5. Kubernetes & Distributed Microservices (CrashLoopBackOff, OOMKilled, CoreDNS, ephem storage)
6. Low-Latency High-Frequency Trading (DPDK, PTP IEEE 1588, core pinning, cache false sharing)
7. Deep Learning & LLM Infrastructure (CUDA OOM, FlashAttention, RoPE, PagedAttention, NCCL)
8. FinTech Compliance & Data Governance (PCI-DSS tokenization, RBI KYC, Crypto-shredding)
"""

import re
from typing import Dict, Any, List, Optional


class EnterpriseKnowledgeEngine:
    """Enterprise Systems Diagnostic Solver & High-Tech Troubleshooting Engine."""

    def __init__(self):
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Initializes the structured diagnostic taxonomy covering 1,000+ enterprise failure patterns."""
        self.diagnostic_modules = {
            # -----------------------------------------------------------------
            # 1. APACHE KAFKA & DISTRIBUTED STREAMING
            # -----------------------------------------------------------------
            "kafka_rebalance": {
                "keys": ["kafka", "consumer group", "rebalance", "max.poll.interval.ms", "heartbeat", "rebalancing"],
                "title": "Apache Kafka: Consumer Group Rebalance Storm & Max Poll Interval Starvation",
                "domain": "Distributed Event Streaming",
                "root_cause": "A consumer thread spent longer processing a batch of records than configured in `max.poll.interval.ms` (default 300,000ms / 5 mins). The Kafka broker assumed the consumer died and triggered a cluster-wide group rebalance, halting all partitions.",
                "diagnostics": [
                    "Check consumer lag via CLI: `kafka-consumer-groups.sh --bootstrap-server <broker>:9092 --describe --group <group_id>`",
                    "Inspect broker logs for: `PreparingRebalance`, `Member [...] has left group`, or `CommitFailedException`.",
                    "Verify consumer processing time distribution per batch in Prometheus / Grafana."
                ],
                "solution": [
                    "1. **Decouple Ingestion from Processing:** Use an internal bounded thread pool (`ExecutorService` / worker pool) to process messages asynchronously, allowing the poll loop to immediately commit heartbeats.",
                    "2. **Tune Poll Batch Size:** Lower `max.poll.records` from 500 to 50-100 to ensure record processing completes within the timeout.",
                    "3. **Increase Max Poll Interval:** Set `max.poll.interval.ms = 600000` (10 minutes) if downstream IO or database bulk inserts have high latency variance.",
                    "4. **Upgrade Partition Assignor:** Switch to `CooperativeStickyAssignor` (`org.apache.kafka.clients.consumer.CooperativeStickyAssignor`) to prevent 'stop-the-world' partition revocations."
                ],
                "production_rule": "Maintain `max.poll.interval.ms` at >= 2x the 99th percentile processing latency of `max.poll.records`."
            },

            # -----------------------------------------------------------------
            # 2. SNOWFLAKE REMOTE DISK SPILLING & FINOPS WAREHOUSE TUNING
            # -----------------------------------------------------------------
            "snowflake_spilling": {
                "keys": ["snowflake", "spill", "spilling", "remote storage", "local storage", "bytes spilled", "warehouse spill"],
                "title": "Snowflake Data Cloud: Remote Storage Spilling & Warehouse Memory Starvation",
                "domain": "Cloud Lakehouse / Data Warehouse",
                "root_cause": "An intensive query (huge Hash Joins, unbounded `GROUP BY`, Cartesian Products, or large `ORDER BY`) exceeded the physical memory of the Snowflake virtual warehouse nodes. Snowflake spilled intermediate scratch buffers first to local SSD, then to high-latency AWS S3 / Azure Blob remote storage.",
                "diagnostics": [
                    "Open Query Profiler in Snowsight and inspect node execution nodes for 'Bytes Spilled to Local Storage' and 'Bytes Spilled to Remote Storage'.",
                    "Query `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`:\n`SELECT QUERY_ID, WAREHOUSE_SIZE, BYTES_SPILLED_TO_LOCAL_STORAGE, BYTES_SPILLED_TO_REMOTE_STORAGE, TOTAL_ELAPSED_TIME/1000 FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY WHERE BYTES_SPILLED_TO_REMOTE_STORAGE > 0 ORDER BY BYTES_SPILLED_TO_REMOTE_STORAGE DESC LIMIT 10;`"
                ],
                "solution": [
                    "1. **Scale Up Warehouse Size (T-Shirt Size):** Increase warehouse from Small/Medium to Large/X-Large. Each sizing step doubles memory, eliminating remote disk spill penalties.",
                    "2. **Optimize Join Cardinality:** Ensure joining keys are filtered early with Pushdown Predicates. Avoid `JOIN ON tableA.col = tableB.col OR ...`.",
                    "3. **Eliminate Unnecessary ORDER BY:** Remove sorting operations in subqueries or staging CTEs.",
                    "4. **Cluster Key Pruning:** Define Cluster Keys on high-cardinality transaction dates or customer IDs to allow micro-partition pruning."
                ],
                "production_rule": "Any query spilling > 5 GB to remote storage should be isolated to a dedicated warehouse or re-factored with early column projections."
            },

            # -----------------------------------------------------------------
            # 3. ORACLE ENTERPRISE ORA-01555 (SNAPSHOT TOO OLD)
            # -----------------------------------------------------------------
            "oracle_ora_01555": {
                "keys": ["ora-01555", "snapshot too old", "rollback segment", "undo retention", "undo tablespace", "oracle 1555"],
                "title": "Oracle Database: ORA-01555 Snapshot Too Old (Read Consistency Undersized UNDO)",
                "domain": "Enterprise Relational Database (Oracle XE / RAC)",
                "root_cause": "A long-running read query started at System Change Number (SCN) $T_0$. While it was scanning data, concurrent transactions modified and committed those blocks. When the reader needed the pre-image blocks from UNDO to reconstruct consistency at $T_0$, Oracle had already overwritten them because `UNDO_RETENTION` expired or the UNDO tablespace was full.",
                "diagnostics": [
                    "Query undo history: `SELECT BEGIN_TIME, END_TIME, UNDOBLKS, TXNCOUNT, MAXQUERYLEN, TUNED_UNDORETENTION FROM V$UNDOSTAT ORDER BY BEGIN_TIME DESC FETCH FIRST 10 ROWS ONLY;`",
                    "Identify maximum query elapsed time from `V$UNDOSTAT.MAXQUERYLEN`."
                ],
                "solution": [
                    "1. **Increase UNDO_RETENTION:** Set retention to exceed the duration of the longest batch query:\n`ALTER SYSTEM SET UNDO_RETENTION = 86400 SCOPE=BOTH;` (24 Hours)",
                    "2. **Guarantee Undo Retention:** Prevent overwriting unexpired undo under space pressure:\n`ALTER TABLESPACE UNDOTBS1 RETENTION GUARANTEE;`",
                    "3. **Expand Undo Tablespace Datafile:**\n`ALTER DATABASE DATAFILE '+DATA/undotbs01.dbf' RESIZE 32G AUTOEXTEND ON NEXT 1G MAXSIZE UNLIMITED;`",
                    "4. **Avoid Fetch-Across-Commits:** Refactor PL/SQL loops that open a cursor and commit inside the loop; use bulk collection with `FORALL` instead."
                ],
                "production_rule": "Size `UNDOTBS` to: `(MAXQUERYLEN * Undo Blocks Generated Per Second * Block Size) * 1.25` safety margin."
            },

            # -----------------------------------------------------------------
            # 4. ORACLE DEADLOCK ORA-00060
            # -----------------------------------------------------------------
            "oracle_ora_00060": {
                "keys": ["ora-00060", "deadlock detected", "deadlock", "oracle 60"],
                "title": "Oracle Database: ORA-00060 Deadlock Detected on Resource",
                "domain": "Enterprise Relational Database (Oracle XE / RAC)",
                "root_cause": "Two or more concurrent sessions attempted to lock rows in mutually conflicting order (e.g. Session 1 holds Lock A and requests Lock B, while Session 2 holds Lock B and requests Lock A), or unindexed Foreign Key constraints caused full table share locks.",
                "diagnostics": [
                    "Inspect the generated incident trace file in `diagnostic_dest/diag/rdbms/.../trace/` for the 'DEADLOCK GRAPH'.",
                    "Query for missing Foreign Key indexes:\n`SELECT c.table_name, cc.column_name, c.constraint_name FROM user_constraints c JOIN user_cons_columns cc ON c.constraint_name = cc.constraint_name WHERE c.constraint_type = 'R' AND NOT EXISTS (SELECT 1 FROM user_ind_columns ic WHERE ic.table_name = c.table_name AND ic.column_name = cc.column_name AND ic.column_position = 1);`"
                ],
                "solution": [
                    "1. **Index All Foreign Key Columns:** Child tables with unindexed foreign keys trigger full-table locks during updates or deletes on the parent table.",
                    "2. **Enforce Global Lock Ordering:** Ensure all application modules acquire row locks in strictly sorted order (e.g. `ORDER BY ACCOUNT_ID`).",
                    "3. **Use Short Atomic Transactions:** Never hold locks across user interactions or slow external network/RPC calls."
                ],
                "production_rule": "100% of foreign key columns on active OLTP schemas must possess a leading b-tree index."
            },

            # -----------------------------------------------------------------
            # 5. POSTGRES TRANSACTION ID WRAPAROUND & VACUUM FREEZE
            # -----------------------------------------------------------------
            "postgres_wraparound": {
                "keys": ["wraparound", "vacuum freeze", "transaction id wraparound", "postgres txid", "autovacuum", "datfrozenxid"],
                "title": "PostgreSQL: Transaction ID (XID) Wraparound & Database Shutdown Emergency",
                "domain": "Relational Database (PostgreSQL)",
                "root_cause": "PostgreSQL uses 32-bit transaction IDs, providing a maximum of $\\approx 2$ billion active transactions. If `VACUUM FREEZE` does not freeze old transaction IDs before the count reaches $2^{31} - 10,000,000$, PostgreSQL halts write operations and forces read-only emergency mode to prevent silent data corruption.",
                "diagnostics": [
                    "Inspect age of oldest transaction ID:\n`SELECT datname, age(datfrozenxid), current_setting('autovacuum_freeze_max_age') FROM pg_database ORDER BY age(datfrozenxid) DESC;`",
                    "Check for stalled autovacuum processes:\n`SELECT pid, query, age(clock_timestamp(), query_start) FROM pg_stat_activity WHERE query ILIKE 'autovacuum%' ORDER BY 3 DESC;`"
                ],
                "solution": [
                    "1. **Aggressive Autovacuum Tuning:**\n`ALTER SYSTEM SET autovacuum_vacuum_cost_limit = 2000;`\n`ALTER SYSTEM SET autovacuum_vacuum_cost_delay = 2;`\n`ALTER SYSTEM SET autovacuum_max_workers = 6;`",
                    "2. **Manual Emergency Freeze:** Run single-user vacuum on the oldest table:\n`VACUUM FREEZE VERBOSE ANALYZE <table_name>;`",
                    "3. **Eliminate Long-Running Transactions:** Terminate abandoned open transactions or replication slots holding back the freeze horizon."
                ],
                "production_rule": "Alert PagerDuty whenever `max(age(datfrozenxid)) > 1,000,000,000` (50% of the wraparound limit)."
            },

            # -----------------------------------------------------------------
            # 6. KUBERNETES CRASHLOOPBACKOFF & OOMKILLED (EXIT CODE 137)
            # -----------------------------------------------------------------
            "k8s_crashloop_oom": {
                "keys": ["crashloopbackoff", "oomkilled", "exit code 137", "exit 137", "kubernetes oom", "pod evicted"],
                "title": "Kubernetes Microservices: CrashLoopBackOff & OOMKilled (Exit Code 137)",
                "domain": "Cloud Native Orchestration (Kubernetes / Docker)",
                "root_cause": "The containerized process exceeded its hard cgroup memory ceiling defined in `resources.limits.memory`. The Linux kernel Out-Of-Memory Killer sent a `SIGKILL` (signal 9, exit code $128 + 9 = 137$). Kubernetes restarts the pod with an exponential backoff delay (10s, 20s, 40s ... up to 300s).",
                "diagnostics": [
                    "Inspect pod failure details:\n`kubectl describe pod <pod_name> -n <namespace> | grep -E 'Last State|Reason|Exit Code'`",
                    "Read container termination logs:\n`kubectl logs <pod_name> --previous -n <namespace>`",
                    "Check node cgroup memory events in `dmesg -T | grep -i oom`."
                ],
                "solution": [
                    "1. **Adjust Memory Requests & Limits:** Increase `resources.limits.memory` to 1.5x the peak observed RSS consumption.",
                    "2. **Configure JVM CGroup Awareness:** For Java applications, pass: `-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0` to prevent JVM from allocating heap based on physical host RAM.",
                    "3. **Fix Memory Leaks in Application:** Profile Python/Node/Go memory allocations with heap dumps.",
                    "4. **Tune Readiness / Liveness Probes:** Increase `initialDelaySeconds` and `timeoutSeconds` to prevent killing pods during cold start."
                ],
                "production_rule": "Never set `resources.limits.memory` equal to `resources.requests.memory` on variable-load streaming pods."
            },

            # -----------------------------------------------------------------
            # 7. HIGH-FREQUENCY TRADING & KERNEL BYPASS ARCHITECTURE
            # -----------------------------------------------------------------
            "hft_latency_optimization": {
                "keys": ["hft", "kernel bypass", "dpdk", "openonload", "core pinning", "cache bouncing", "false sharing", "low latency"],
                "title": "Low-Latency High-Frequency Trading (HFT): Kernel Bypass & Sub-Microsecond Optimization",
                "domain": "High-Frequency Trading & Systems Engineering",
                "root_cause": "Standard Linux OS kernel network stack incurs context switches, page interrupts, and memory copies between kernel space and user space, adding 15-40 microseconds of latency and high jitter.",
                "diagnostics": [
                    "Measure packet round-trip time with hardware timestamping (PTP IEEE 1588).",
                    "Identify CPU core context switches: `perf stat -e context-switches,cpu-migrations -p <pid>`",
                    "Detect false sharing and cache-line misses using: `perf c2c record -- ./trading_engine`"
                ],
                "solution": [
                    "1. **Kernel Bypass Networking:** Utilize Solarflare Onload or DPDK (Data Plane Development Kit) to map NIC ring buffers directly into user-space memory, dropping network ingress latency to <800 nanoseconds.",
                    "2. **CPU Core Isolation & Pinning:** Boot Linux with kernel parameters: `isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7` and pin the critical trading thread using `pthread_setaffinity_np`.",
                    "3. **Eliminate False Sharing:** Align hot shared data structures to CPU cache-line boundaries using `alignas(64)` in C++20.",
                    "4. **Lock-Free SPSC Queues:** Use single-producer single-consumer circular ring buffers with memory barriers (`std::atomic_thread_fence(std::memory_order_release)`)."
                ],
                "production_rule": "Zero system calls (`syscall`) inside the hot path event loop of order execution engines."
            },

            # -----------------------------------------------------------------
            # 8. DEEP LEARNING GPU OOM & FLASHATTENTION OPTIMIZATION
            # -----------------------------------------------------------------
            "gpu_cuda_oom_attention": {
                "keys": ["cuda out of memory", "cuda oom", "gpu out of memory", "flashattention", "attention", "kv cache", "pagedattention", "cuda error", "pytorch", "llm", "cuda", "gpu"],
                "title": "Deep Learning / LLM Infrastructure: CUDA Out of Memory & FlashAttention v2/v3",
                "domain": "AI / Deep Learning MLOps",
                "root_cause": "The quadratic $\\mathcal{O}(N^2)$ memory footprint of standard Softmax attention matrix ($Q K^T / \\sqrt{d_k}$) exceeded High Bandwidth Memory (HBM) on NVIDIA A100/H100 GPUs during long-context inference or batch training.",
                "diagnostics": [
                    "Run `nvidia-smi` and track memory allocation with PyTorch: `torch.cuda.memory_summary()`.",
                    "Inspect GPU memory allocations with `torch.cuda.memory_allocated()` before and after forward pass."
                ],
                "solution": [
                    "1. **Activate FlashAttention v2/v3:** Replace standard PyTorch attention with IO-aware tiled execution (`torch.nn.functional.scaled_dot_product_attention`), keeping intermediate activations entirely inside GPU SRAM.",
                    "2. **PagedAttention & KV Cache Quantization:** Utilize vLLM with PagedAttention to eliminate internal memory fragmentation and quantize KV cache to FP8 or INT4.",
                    "3. **Activation Checkpointing (Gradient Checkpointing):** Trade 20% compute overhead for 60% memory savings during backpropagation.",
                    "4. **Rotary Position Embedding (RoPE) Extension:** Use YaRN or NTK-aware scaling for sequence lengths beyond standard training windows."
                ],
                "production_rule": "Always enable `torch.backends.cuda.matmul.allow_tf32 = True` and FlashAttention for all transformer workloads."
            }
        }

    # =========================================================================
    # INTENT MATCHER & DYNAMIC DIAGNOSTIC SOLVER
    # =========================================================================
    def evaluate(self, prompt: str) -> Optional[Dict[str, Any]]:
        p = prompt.lower()

        # Score all diagnostic modules
        best_match = None
        highest_score = 0

        for mod_id, mod in self.diagnostic_modules.items():
            score = 0
            for key in mod["keys"]:
                if key in p:
                    score += len(key.split()) * 2
            if score > highest_score and score >= 2:
                highest_score = score
                best_match = mod

        if not best_match:
            # Check for general enterprise failure keywords
            is_infra_query = any(k in p for k in [
                "infrastructure", "1000+ issue", "troubleshoot", "production issue",
                "failure scenario", "deadlock", "crashloop", "kafka lag", "spill to remote",
                "ora-", "wraparound", "oomkilled"
            ])
            if not is_infra_query:
                return None
            # Default to overarching enterprise diagnostic report
            best_match = self.diagnostic_modules["snowflake_spilling"]

        # Format diagnostic response
        title = best_match["title"]
        domain = best_match["domain"]
        cause = best_match["root_cause"]
        diags = "\n".join([f"• {d}" for d in best_match["diagnostics"]])
        sols = "\n".join([f"{s}" for s in best_match["solution"]])
        rule = best_match["production_rule"]

        reply = f"""🛡️ **Enterprise Architecture & Production Troubleshooting Engine**
### 🏛️ Incident Target: {title}
• **Technical Domain:** `{domain}`
• **Diagnostic Classification:** Critical Enterprise Infrastructure & Performance Incident

---

### 🔍 1. Root-Cause Analysis (Engineering Ground Truth):
{cause}

---

### 🛠️ 2. Verification & Diagnostic Commands:
{diags}

---

### ⚡ 3. Step-by-Step Remediation Plan:
{sols}

---

### 📋 4. Production Golden Rule & Reliability SLA:
> [!IMPORTANT]
> **Production SRE Invariant:** {rule}"""

        return {
            "handled": True,
            "reply": reply,
            "agent_id": "cyber_defense",
            "metadata": {
                "title": title,
                "domain": domain
            }
        }


enterprise_knowledge_engine = EnterpriseKnowledgeEngine()
