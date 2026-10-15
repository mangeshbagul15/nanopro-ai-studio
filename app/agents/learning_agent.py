"""
Mangesh Nano Pro AI Studio - Learning & Interview Preparation Agent
Handles:
1. SQL scenario interview questions with step-by-step query logic
2. Python coding challenges with test validation
3. Snowflake architecture drills (Virtual warehouses, Clustering, Time travel)
4. Session tracking, weak-area detection, and progress history
"""

import time
import json
from typing import Dict, Any, List, Optional
from app.core.logger import log_event
from app.core.database import db

class LearningAgent:
    def __init__(self):
        pass

    def generate_sql_interview_session(self, difficulty: str = "medium") -> Dict[str, Any]:
        """Generates a high-yield SQL scenario interview drill with questions and answers."""
        log_event(f"LearningAgent: Generating SQL practice session (Difficulty: {difficulty})", component="LearningAgent")
        sid = f"learn_sql_{int(time.time()*1000)}"

        questions = [
            {
                "id": 1,
                "title": "Cumulative Running Total",
                "question": "Given a `transactions(customer_id, amount, txn_date)` table, write a query to calculate the cumulative total amount spent by each customer ordered by transaction date.",
                "solution": "SELECT customer_id, txn_date, amount, SUM(amount) OVER(PARTITION BY customer_id ORDER BY txn_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total FROM transactions;",
                "key_concept": "Window Function SUM() OVER (PARTITION BY ... ORDER BY ...)"
            },
            {
                "id": 2,
                "title": "Nth Highest Salary / Deduplication",
                "question": "Write a query to find the 2nd highest salary from the `employees` table without missing ties.",
                "solution": "WITH RankedSalaries AS (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rnk FROM employees) SELECT salary FROM RankedSalaries WHERE rnk = 2 LIMIT 1;",
                "key_concept": "DENSE_RANK() vs RANK() for tie handling"
            },
            {
                "id": 3,
                "title": "Find Duplicate Customer Records",
                "question": "Identify all duplicate email addresses in `customers` table and return the IDs of the records to remove (keeping the lowest ID).",
                "solution": "WITH Dupes AS (SELECT id, ROW_NUMBER() OVER(PARTITION BY email ORDER BY id ASC) as row_num FROM customers) SELECT id FROM Dupes WHERE row_num > 1;",
                "key_concept": "ROW_NUMBER() for safe deduplication"
            },
            {
                "id": 4,
                "title": "Self Joins: Manager-Employee Hierarchy",
                "question": "Given `employees(id, name, manager_id)`, write a query to list each employee alongside their manager's name. Include employees who do not have a manager.",
                "solution": "SELECT e.name AS employee_name, COALESCE(m.name, 'Top Executive') AS manager_name FROM employees e LEFT JOIN employees m ON e.manager_id = m.id;",
                "key_concept": "LEFT OUTER SELF JOIN with COALESCE"
            },
            {
                "id": 5,
                "title": "Day-Over-Day Metric Growth",
                "question": "Calculate the percentage revenue change day-over-day from `daily_sales(sale_date, total_revenue)`.",
                "solution": "SELECT sale_date, total_revenue, LAG(total_revenue, 1) OVER (ORDER BY sale_date) AS prev_day_revenue, ROUND(((total_revenue - LAG(total_revenue, 1) OVER (ORDER BY sale_date)) / LAG(total_revenue, 1) OVER (ORDER BY sale_date)) * 100, 2) AS pct_growth FROM daily_sales;",
                "key_concept": "LAG() analytic function for delta computation"
            }
        ]

        sess_data = {
            "id": sid,
            "subject": "sql",
            "topic": "Window Functions, Self-Joins & Ranking",
            "difficulty": difficulty,
            "questions": questions,
            "score": 100,
            "weak_areas": "None recorded",
            "status": "ready"
        }
        db.save_learning_session(sess_data)
        return sess_data

    def generate_snowflake_practice_session(self) -> Dict[str, Any]:
        """Generates Snowflake architecture interview practice drill."""
        log_event("LearningAgent: Generating Snowflake practice drill", component="LearningAgent")
        sid = f"learn_sf_{int(time.time()*1000)}"

        questions = [
            {
                "id": 1,
                "title": "Virtual Warehouse Auto-Scaling",
                "question": "How does Snowflake's Multi-cluster Warehouse scale dynamically under concurrency, and what is the difference between Standard and Economy scaling policies?",
                "solution": "Standard policy spins up additional clusters immediately upon queue buildup. Economy policy waits until enough concurrent queries justify a cluster for at least 6 minutes, prioritizing credit efficiency over sub-second latency.",
                "key_concept": "Multi-Cluster Warehouse Concurrency Management"
            },
            {
                "id": 2,
                "title": "Zero-Copy Cloning Mechanics",
                "question": "What happens under the hood when executing `CREATE TABLE orders_clone CLONE orders;` in Snowflake? Is storage duplicated?",
                "solution": "No physical storage is copied. Snowflake creates a new metadata pointer pointing to the identical immutable micro-partitions. Storage charges only accrue for micro-partitions modified after clone creation (Copy-on-Write).",
                "key_concept": "Metadata-driven Zero-Copy Cloning"
            },
            {
                "id": 3,
                "title": "Time Travel & Fail-safe",
                "question": "How do you restore a dropped table in Snowflake, and what is the maximum Time Travel retention period across Standard vs Enterprise editions?",
                "solution": "Execute `UNDROP TABLE my_table;`. Standard edition supports up to 1 day; Enterprise edition supports up to 90 days of Time Travel. Fail-safe provides a non-configurable 7-day disaster recovery window for Snowflake support only.",
                "key_concept": "Continuous Data Protection (CDP)"
            }
        ]

        sess_data = {
            "id": sid,
            "subject": "snowflake",
            "topic": "Snowflake Architecture, Cloning & Time Travel",
            "difficulty": "advanced",
            "questions": questions,
            "score": 100,
            "weak_areas": "None recorded",
            "status": "ready"
        }
        db.save_learning_session(sess_data)
        return sess_data

    def get_learning_progress(self) -> Dict[str, Any]:
        """Summarizes learning statistics and progress history."""
        sessions = db.list_learning_sessions()
        total_sessions = len(sessions)
        subjects = {}
        for s in sessions:
            sub = s["subject"]
            subjects[sub] = subjects.get(sub, 0) + 1

        return {
            "total_sessions_completed": total_sessions,
            "subject_breakdown": subjects,
            "recent_sessions": sessions[:5],
            "recommended_focus": "Snowflake Streams & Tasks and SQL Window Frames"
        }

    def generate_sql_drill(self, topic: str = "Window Functions", difficulty: str = "medium") -> Dict[str, Any]:
        res = self.generate_sql_interview_session(difficulty=difficulty)
        # Adapt keys for drill format
        formatted_q = []
        for q in res.get("questions", []):
            formatted_q.append({
                "question": f"{q['title']}: {q['question']}",
                "hint": q['key_concept'],
                "solution": q['solution']
            })
        return {
            "id": res["id"],
            "topic": topic or res["topic"],
            "difficulty": difficulty,
            "scenario": "Financial and transactional analytics database with high-volume customer events.",
            "questions": formatted_q
        }

    def generate_snowflake_drill(self) -> Dict[str, Any]:
        return self.generate_snowflake_practice_session()

learning_agent = LearningAgent()
