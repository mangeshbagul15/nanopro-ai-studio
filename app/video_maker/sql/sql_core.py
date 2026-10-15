"""
@Code_With_Mangesh - AI Video Generator Studio (v12)
=====================================================
Stages shown live in the dashboard:
  1. learning -> load past examples from learning_store.json
  2. models   -> try models one by one (priority order, no parallel race)
  3. build    -> plan the logical SQL build-up and build the animation page
  4. video    -> Playwright + Chrome record the animation
  5. done

FEATURES
  * Animated SQL typing, built clause by clause (FROM -> JOIN -> ON -> WHERE ->
    GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT -> Final Query).
  * Every table used in FROM / JOIN gets its own sample table. Join steps mark
    matching and non-matching rows using shared column names.
  * The result table is labelled as simulated (no real database execution).
  * Horizontal, website-style dashboard (three side-by-side cards).
  * Centralised theme selector (12 themes, recent-history avoidance,
    topic-aware preferences) used by animations and thumbnails.
  * The animation tab opens immediately and waits for the page to be ready.
  * Learning memory is cached, the HTML template is built once, and the main
    model is warmed up at startup.

SQL FORMAT RULE:
  Every query is re-formatted with a clause-aware formatter.

AUDIO:
  The animation is completely silent - no sound of any kind.

THUMBNAIL BACKGROUND RULE:
  Click 1, 3, 5 ... -> mixed / gradient background (fresh theme each time)
  Click 2, 4, 6 ... -> ONE single flat colour (fresh colour each time)
"""

import asyncio
import os
import json
import random
import re
import uuid
import threading
import time
import subprocess
import platform
import traceback
from collections import deque
from pathlib import Path

from playwright.async_api import async_playwright
import ollama
try:
    from fastapi import FastAPI, Form
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    import uvicorn
    app = FastAPI()
except ImportError:
    class _DummyFastAPI:
        def get(self, *args, **kwargs):
            return lambda fn: fn
        def post(self, *args, **kwargs):
            return lambda fn: fn
    FastAPI = None
    def Form(default=""): return default
    HTMLResponse = JSONResponse = FileResponse = None
    uvicorn = None
    app = _DummyFastAPI()

# ============================================================
# MODELS - tried ONE BY ONE (no parallel race, so nothing hangs)
#   1) qwen2.5-coder:7b   -> best SQL accuracy + strict JSON (4.7 GB)
#   2) qwen2.5-coder:3b   -> very fast, coder-tuned (1.9 GB)
#   3) gemma3:4b          -> fast, good instruction following (3.3 GB)
#   4) phi4-mini:latest   -> fastest JSON (2.5 GB)
#   5) llama3.2:3b        -> light fallback (2.0 GB)
# ============================================================
MODELS_TO_TRY = [
    "qwen2.5-coder:7b",
    "qwen2.5-coder:3b",
    "gemma3:4b",
    "phi4-mini:latest",
    "llama3.2:3b",
]

# Smaller/faster models first - metadata and thumbnail copy do not need the big model
METADATA_MODELS = [
    "qwen2.5-coder:3b",
    "phi4-mini:latest",
    "gemma3:4b",
    "llama3.2:3b",
    "qwen2.5-coder:7b",
]

live_logs = []
LAST_RUN = {}                      # keeps the last generated question/query/logic

# ============================================================
# LIVE JOB TRACKING (live monitoring in the dashboard)
# ============================================================
JOBS = {}
JOBS_LOCK = threading.Lock()
PIPELINE_LOCK = threading.Lock()          # only one video is built at a time
THUMB_LOCK = threading.Lock()             # only one thumbnail render at a time
_thread_ctx = threading.local()           # each thread keeps its own job_id


def log_message(msg: str):
    print(msg)
    live_logs.append(msg)

    job_id = getattr(_thread_ctx, "job_id", None)
    if job_id:
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if job is not None:
                job["logs"].append(f"{time.strftime('%H:%M:%S')}  {msg}")
                job["updated"] = time.time()


def set_job_stage(job_id: str, stage: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if job is not None:
            job["stage"] = stage
            job["updated"] = time.time()


# ============================================================
# SETTINGS
# ============================================================
MAX_ATTEMPTS_PER_MODEL = 1         # INNER loop = 1 attempt per model
RECORD_WIDTH = 1080
RECORD_HEIGHT = 1920
END_CARD_STOP_MS = 1500            # stop recording right after the end card appears

MIN_SAMPLE_ROWS = 5                # every sample table shows at least this many rows
MAX_BUBBLE_CHARS = 58              # short comment lines -> always inside the bubble
MAX_PROCESS_CHARS = 62             # short concept lines
MAX_CHIP_CHARS = 30                # step labels from the allowed list

# thumbnail canvas (9:16) and the safe area reserved for platform UI
THUMB_WIDTH = 1080
THUMB_HEIGHT = 1920
THUMB_SAFE_LEFT = 70
THUMB_SAFE_RIGHT = 200             # extra protection: Shorts / Reels icons live here
THUMB_SAFE_TOP = 150
THUMB_SAFE_BOTTOM = 230

LEARNING_STORE_PATH = Path(r"C:\Mangesh\AI video\learning\learning_store.json")
THUMBNAIL_PATH = Path(r"C:\Mangesh\AI video\Output_Filee\youtube_short_thumbnail.png")
OUTPUT_DIR = r"C:\Mangesh\AI video\Output_File"
HTML_SAVE_DIR = r"C:\Mangesh\AI video\Input_File"
MAX_LEARNING_EXAMPLES = 25
MAX_FEWSHOT_EXAMPLES = 3
THEME_HISTORY_SIZE = 4             # how many recent themes are remembered per scope

OLLAMA_KEEP_ALIVE = "30m"          # keeps the model in RAM -> next run is faster
OLLAMA_OPTIONS = {
    "temperature": 0.25,
    "num_ctx": 8192,               # a small ctx truncated the prompt -> missing keys
    "num_predict": 2000,
    "top_p": 0.9,
    "repeat_penalty": 1.05,
}

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "question_banner": {"type": "string"},
        "table_name": {"type": "string"},
        "logic_explanation": {"type": "string"},
        "process_summary": {"type": "array", "items": {"type": "string"}},
        "sample_data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "cols": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["id", "cols"],
            },
        },
        "table_headers": {"type": "array", "items": {"type": "string"}},
        "tables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "headers": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                },
            },
        },
        "chips": {"type": "array", "items": {"type": "string"}},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "query": {"type": "string"},
                    "explanation": {"type": "string"},
                    "bubble": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["query", "explanation", "bubble"],
            },
        },
        "cleaned_output": {
            "type": "array",
            "items": {"type": "array", "items": {"type": "string"}},
        },
    },
    "required": ["question_banner", "table_name", "process_summary", "sample_data",
                 "table_headers", "chips", "steps", "cleaned_output"],
}

THUMBNAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "badge": {"type": "string"},
        "headline": {"type": "string"},
        "highlight": {"type": "string"},
        "subheadline": {"type": "string"},
        "sql_snippet": {"type": "string"},
        "bullets": {"type": "array", "items": {"type": "string"}},
        "footer": {"type": "string"},
        "theme": {"type": "string"},
    },
    "required": ["badge", "headline", "highlight", "subheadline", "sql_snippet",
                 "bullets", "footer", "theme"],
}

MIN_SQL_KEYWORDS = ("SELECT", "WITH", "DELETE", "INSERT", "UPDATE", "CREATE")

KEY_ALIASES = {
    "question_banner": ["question_banner", "question", "questionbanner", "banner", "title"],
    "table_name": ["table_name", "tablename", "table"],
    "logic_explanation": ["logic_explanation", "logicexplanation", "logic", "explanation", "approach"],
    "process_summary": ["process_summary", "processsummary", "process", "execution_process",
                        "how_it_runs", "process_steps", "summary"],
    "sample_data": ["sample_data", "sampledata", "sample_table", "table_data", "data",
                    "rows", "sample_rows", "sample_data_rows", "records"],
    "table_headers": ["table_headers", "tableheaders", "headers", "columns", "table_columns"],
    "tables": ["tables", "table_list", "sample_tables", "all_tables"],
    "chips": ["chips", "step_chips", "step_titles", "steps_chips", "titles"],
    "steps": ["steps", "queries", "step_list", "sql_steps"],
    "cleaned_output": ["cleaned_output", "cleanedoutput", "expected_output", "final_output",
                       "output", "result", "results"],
}

CLAUSE_KEYWORDS = ("GROUP BY", "ORDER BY", "UNION ALL", "QUALIFY", "WINDOW",
                   "HAVING", "LIMIT", "OFFSET", "FROM", "WHERE", "UNION")

# Only these labels may be used for the animated step chips
ALLOWED_LABELS = [
    "Understand Requirement",
    "Identify Tables",
    "Identify Columns",
    "Select Data",
    "Filter Data",
    "Join Data",
    "Match Records",
    "Calculate Values",
    "Aggregate Data",
    "Group Data",
    "Apply Aggregate Filter",
    "Build CTE",
    "Build Subquery",
    "Add Outer Query",
    "Apply Window Function",
    "Rank Results",
    "Handle Duplicates",
    "Remove Duplicates",
    "Transform Data",
    "Apply Conditional Logic",
    "Combine Results",
    "Compare Results",
    "Add Date Logic",
    "Sort Results",
    "Limit Results",
    "Modify Existing Query",
    "Validate Logic",
    "Review Result",
    "Optimize Query",
    "Final Query",
]

# ------------------------------------------------------------------
# SQL formatting vocabulary (longest phrases are always tried first)
# ------------------------------------------------------------------
SQL_INDENT = "    "

SQL_JOIN_KEYWORDS = (
    "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "FULL OUTER JOIN",
    "NATURAL JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
    "FULL JOIN", "CROSS JOIN", "JOIN",
)

SQL_FORMAT_PHRASES = tuple(sorted(
    SQL_JOIN_KEYWORDS + (
        "UNION ALL", "UNION", "EXCEPT", "INTERSECT", "MINUS",
        "GROUP BY", "ORDER BY", "QUALIFY", "WINDOW", "HAVING",
        "LIMIT", "OFFSET", "WHERE", "ON", "FROM", "SELECT", "WITH", "VALUES",
    ), key=len, reverse=True))

# clause keywords that matter when the query is sliced into build steps
SQL_STEP_PHRASES = tuple(sorted(
    ("SELECT", "FROM") + SQL_JOIN_KEYWORDS +
    ("ON", "WHERE", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"), key=len, reverse=True))

JOIN_WORDS = SQL_JOIN_KEYWORDS

CLAUSE_LABELS = {
    "Build CTE": "Build CTE",
    "FROM": "Identify Tables",
    "JOIN": "Join Data",
    "ON": "Match Records",
    "WHERE": "Filter Data",
    "GROUP BY": "Group Data",
    "HAVING": "Apply Aggregate Filter",
    "SELECT": "Select Data",
    "ORDER BY": "Sort Results",
    "LIMIT": "Limit Results",
}

CLAUSE_BUBBLES = {
    "Understand Requirement": ["What: The problem", "Why: Know the goal", "Result: Plan ready"],
    "Build CTE": ["What: WITH block", "Why: Reusable result", "Result: Named table"],
    "Identify Tables": ["What: FROM clause", "Why: Pick the table", "Result: Source ready"],
    "Join Data": ["What: JOIN clause", "Why: Add second table", "Result: Tables combined"],
    "Match Records": ["What: ON condition", "Why: Match the keys", "Result: Rows aligned"],
    "Filter Data": ["What: WHERE clause", "Why: Drop rows early", "Result: Fewer rows"],
    "Group Data": ["What: GROUP BY", "Why: Make the groups", "Result: One row per group"],
    "Apply Aggregate Filter": ["What: HAVING", "Why: Filter the groups", "Result: Kept groups"],
    "Apply Window Function": ["What: Window OVER()", "Why: Per group maths", "Result: Extra column"],
    "Rank Results": ["What: Window ranking", "Why: Number the rows", "Result: Ranked rows"],
    "Select Data": ["What: SELECT list", "Why: Choose the columns", "Result: Final shape"],
    "Remove Duplicates": ["What: DISTINCT", "Why: Drop repeats", "Result: Unique rows"],
    "Sort Results": ["What: ORDER BY", "Why: Sort the output", "Result: Ordered rows"],
    "Limit Results": ["What: LIMIT", "Why: Cap the rows", "Result: Top rows only"],
    "Final Query": ["What: Complete query", "Why: All clauses joined", "Result: Ready to run"],
}


# ============================================================
# SMALL HELPERS
# ============================================================
def _as_str_list(value, pad_to: int = 0):
    if value is None:
        items = []
    elif isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple)):
        items = ["" if v is None else str(v) for v in value]
    else:
        items = [str(value)]
    while len(items) < pad_to:
        items.append("")
    return items


def clamp_text(text, limit: int) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    cut = clean[:limit]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip(" ,.;:-") + "..."


def _esc(text) -> str:
    return (str(text or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def _base_name(name) -> str:
    """'BANK_DB.L0.CUSTOMERS' -> 'CUSTOMERS' (upper case, quotes removed)."""
    return str(name or "").split(".")[-1].strip().strip('"').upper()


def split_query_logic(text: str):
    """Return (user_sql, user_logic) from the Query/Logic box."""
    text = (text or "").strip()
    if not text:
        return "", ""
    up = text.upper()
    looks_sql = (
        ("SELECT" in up and "FROM" in up)
        or up.replace("\n", " ").strip().startswith(
            ("WITH ", "INSERT", "UPDATE", "DELETE", "CREATE", "MERGE", "SELECT"))
    )
    if looks_sql:
        return text, ""
    return "", text


# ============================================================
# SAMPLE TABLE HELPERS (always at least MIN_SAMPLE_ROWS rows)
# ============================================================
def _bump_value(value, step: int) -> str:
    """Increase the trailing number of a value (E001 -> E002) to make a new row."""
    text = str(value or "")
    match = re.search(r"(\d+)(\D*)$", text)
    if match:
        num = match.group(1)
        width = len(num)
        new_num = str(int(num) + max(1, int(step))).zfill(width)
        return text[:match.start(1)] + new_num + match.group(2)
    return (text + f"_{step}") if text else f"row_{step}"


def pad_sample_data(sample_data: list, minimum: int = MIN_SAMPLE_ROWS) -> list:
    """Guarantee at least 'minimum' sample rows (used to add the extra rows)."""
    rows = [dict(r) for r in (sample_data or [])]
    if not rows:
        return rows

    originals = [dict(r) for r in rows]
    guard = 0
    while len(rows) < minimum and guard < 12:
        guard += 1
        src = originals[guard % len(originals)]
        cols = list(src.get("cols") or [])
        if cols:
            cols[0] = _bump_value(cols[0], guard)
        rows.append({"id": f"row{len(rows) + 1}", "cols": cols})

    for idx, row in enumerate(rows):
        row["id"] = f"row{idx + 1}"
    return rows


# ============================================================
# DYNAMIC STEP LABELS (only from ALLOWED_LABELS)
# ============================================================
def normalize_label(text: str) -> str:
    """Return the matching allowed label, or '' when it is not in the list."""
    low = " ".join(str(text or "").split()).strip().lower()
    if not low:
        return ""
    for label in ALLOWED_LABELS:
        if label.lower() == low:
            return label
    for label in ALLOWED_LABELS:
        if label.lower() in low:
            return label
    return ""


def _added_text(step: dict) -> str:
    return (str(step.get("typed") or "")
            + str(step.get("prepend") or "")
            + str(step.get("appendafter") or ""))


def label_for_step(step: dict, index: int, total: int, final_sql: str) -> str:
    """Pick the single most accurate label for what this step actually does."""
    mode = str(step.get("mode") or "")
    up = _added_text(step).upper()

    if index == 0:
        first = str(step.get("query") or step.get("typed") or "").strip()
        fup = first.upper()
        if fup.lstrip().startswith("WITH"):
            return "Build CTE"
        inner = extract_innermost_subquery(final_sql) if final_sql else ""
        if inner and " ".join(inner.split()).upper() == " ".join(first.split()).upper():
            return "Build Subquery"
        if "(" in fup and "SELECT" in fup.split("(", 1)[1]:
            return "Build Subquery"
        if " JOIN " in fup:
            return "Join Data"
        if " WHERE " in fup:
            return "Filter Data"
        if any(f in fup for f in ("SUM(", "COUNT(", "AVG(", "MIN(", "MAX(")):
            return "Aggregate Data"
        return "Select Data"

    if mode == "wrap":
        return "Add Outer Query"

    if "JOIN" in up:
        return "Join Data"
    if "GROUP BY" in up:
        return "Group Data"
    if "HAVING" in up:
        return "Apply Aggregate Filter"
    if "WHERE" in up:
        return "Filter Data"
    if "ORDER BY" in up:
        return "Sort Results"
    if "LIMIT" in up:
        return "Limit Results"
    if "UNION" in up:
        return "Combine Results"
    if "DISTINCT" in up:
        return "Remove Duplicates"
    if "ROW_NUMBER" in up or "DENSE_RANK" in up or "RANK(" in up:
        return "Rank Results"
    if "PARTITION BY" in up or " OVER " in up:
        return "Apply Window Function"
    if "CASE" in up and "WHEN" in up:
        return "Apply Conditional Logic"
    if up.strip().startswith("WITH") or " WITH " in up[:16]:
        return "Build CTE"
    if "SELECT" in up and "FROM" in up:
        return "Add Outer Query"
    if any(f in up for f in ("SUM(", "COUNT(", "AVG(", "MIN(", "MAX(")):
        return "Aggregate Data"

    if index == total - 1:
        return "Final Query"
    return "Transform Data"


# ============================================================
# SQL FORMATTER
#   A clause-aware, quote-aware, paren-aware formatter that produces the same
#   clean shape for every query. Subqueries and WITH CTE blocks are formatted
#   recursively and indented.
# ============================================================
def _strip_sql_comments(sql: str) -> str:
    """Remove -- line comments and /* block comments */ without touching quotes."""
    out = []
    i = 0
    n = len(sql)
    in_quote = None
    while i < n:
        ch = sql[i]
        if in_quote:
            out.append(ch)
            if ch == in_quote:
                in_quote = None
            i += 1
            continue
        if ch in ("'", '"', "`"):
            in_quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "-" and i + 1 < n and sql[i + 1] == "-":
            while i < n and sql[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and sql[i + 1] == "*":
            i += 2
            while i + 1 < n and not (sql[i] == "*" and sql[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _collapse_ws(sql: str) -> str:
    """Collapse whitespace outside string literals to a single space."""
    out = []
    in_quote = None
    prev_space = False
    for ch in sql:
        if in_quote:
            out.append(ch)
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ("'", '"', "`"):
            in_quote = ch
            out.append(ch)
            prev_space = False
            continue
        if ch.isspace():
            if out and not prev_space:
                out.append(" ")
                prev_space = True
            continue
        out.append(ch)
        prev_space = False
    return "".join(out).strip()


def _scan_keywords(sql: str, phrases) -> list:
    """[(phrase, index)] for every top-level phrase (quotes and parens aware)."""
    up = str(sql or "").upper()
    n = len(up)
    marks = []
    depth = 0
    in_quote = None
    i = 0

    while i < n:
        ch = up[i]

        if in_quote:
            if ch == in_quote:
                in_quote = None
            i += 1
            continue

        if ch in ("'", '"', "`"):
            in_quote = ch
            i += 1
            continue

        if ch == "(":
            depth += 1
            i += 1
            continue

        if ch == ")":
            depth = max(0, depth - 1)
            i += 1
            continue

        if depth == 0:
            hit = None
            for phr in phrases:
                if up.startswith(phr, i):
                    before_ok = (i == 0) or not (up[i - 1].isalnum() or up[i - 1] == "_")
                    end = i + len(phr)
                    after_ok = (end >= n) or not (up[end].isalnum() or up[end] == "_")
                    if before_ok and after_ok:
                        hit = phr
                        break
            if hit:
                marks.append((hit, i))
                i += len(hit)
                continue

        i += 1

    return marks


def _find_keyword(sql: str, phrase: str) -> int:
    marks = _scan_keywords(sql, (phrase,))
    return marks[0][1] if marks else -1


def _split_top_level_commas(text: str) -> list:
    """Split on commas that are not inside quotes or parentheses."""
    parts = []
    depth = 0
    in_quote = None
    start = 0
    for i, ch in enumerate(str(text or "")):
        if in_quote:
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ("'", '"', "`"):
            in_quote = ch
            continue
        if ch == "(":
            depth += 1
            continue
        if ch == ")":
            depth = max(0, depth - 1)
            continue
        if ch == "," and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    cleaned = [p.strip() for p in parts if p.strip()]
    return cleaned or [str(text or "").strip()]


def _split_conditions(text: str) -> list:
    """[(connector, condition)] - connector is '' for the first condition."""
    marks = _scan_keywords(text, ("AND", "OR"))
    result = []
    prev_conn = ""
    start = 0
    for kw, pos in marks:
        chunk = text[start:pos].strip()
        if chunk:
            result.append((prev_conn, chunk))
        prev_conn = kw
        start = pos + len(kw)
    tail = text[start:].strip()
    if tail:
        result.append((prev_conn, tail))
    return result or [("", str(text or "").strip())]


def _is_subquery_start(text: str, j: int) -> bool:
    n = len(text)
    while j < n and text[j] == " ":
        j += 1
    for kw in ("SELECT", "WITH"):
        if text[j:j + len(kw)].upper() == kw:
            k = j + len(kw)
            if k >= n or not (text[k].isalnum() or text[k] == "_"):
                return True
    return False


def _match_paren(text: str, open_idx: int) -> int:
    depth = 0
    in_quote = None
    for i in range(open_idx, len(text)):
        ch = text[i]
        if in_quote:
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ("'", '"', "`"):
            in_quote = ch
            continue
        if ch == "(":
            depth += 1
            continue
        if ch == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _emit_expression(prefix: str, text: str, indent: int) -> list:
    """One line (or several when a subquery appears) with the prefix in front."""
    lines = []
    buf = prefix
    i = 0
    n = len(text or "")

    while i < n:
        ch = text[i]
        if ch == "(" and _is_subquery_start(text, i + 1):
            end = _match_paren(text, i)
            if end > i:
                inner = text[i + 1:end]
                lines.append((buf + "(").rstrip())
                lines.extend(_format_clauses(inner, indent + len(SQL_INDENT)))
                buf = (" " * indent) + ")"
                i = end + 1
                continue
        buf += ch
        i += 1

    lines.append(buf.rstrip())
    return lines


def _format_conditions(content: str, indent: int, first_prefix: str) -> list:
    """WHERE / ON / HAVING: first condition inline, AND / OR on their own lines."""
    pad = " " * indent
    lines = []
    for idx, (conn, cond) in enumerate(_split_conditions(content)):
        prefix = (pad + first_prefix) if idx == 0 else (pad + conn + " ")
        lines.extend(_emit_expression(prefix, cond, indent))
    return lines


def _format_cte_block(content: str, indent: int) -> list:
    """WITH a AS (...), b AS (...) -> each CTE on its own block, body indented."""
    pad = " " * indent
    parts = _split_top_level_commas(content)
    lines = []

    for idx, part in enumerate(parts):
        part = part.strip()
        as_pos = _find_keyword(part, "AS")
        if as_pos < 0:
            lines.append((pad + ("WITH " if idx == 0 else "") + part).rstrip())
            continue

        head = part[:as_pos].strip()
        tail = part[as_pos + 2:].strip()
        lead = "WITH " if idx == 0 else ""

        if tail.startswith("(") and tail.endswith(")"):
            inner = tail[1:-1]
            lines.append((pad + lead + head + " AS (").rstrip())
            lines.extend(_format_clauses(inner, indent + len(SQL_INDENT)))
            lines.append(pad + (")," if idx < len(parts) - 1 else ")"))
        else:
            lines.append((pad + lead + head + " AS " + tail).rstrip())

    return lines


def _clause_segments(body: str) -> list:
    """[(clause_keyword, clause_text)] in the order they appear."""
    marks = _scan_keywords(body, SQL_FORMAT_PHRASES)
    if not marks:
        return [("", str(body or "").strip())]

    segs = []
    if marks[0][1] > 0:
        head_text = body[:marks[0][1]].strip()
        if head_text:
            segs.append(("", head_text))

    for idx, (kw, pos) in enumerate(marks):
        end = marks[idx + 1][1] if idx + 1 < len(marks) else len(body)
        segs.append((kw, body[pos + len(kw):end].strip()))

    return segs


def _format_clauses(body: str, indent: int = 0) -> list:
    """Format a full query (or subquery) body at the given indentation."""
    body = str(body or "").strip()
    if not body:
        return []

    pad = " " * indent
    lines = []

    for kw, content in _clause_segments(body):
        # ---------------- WITH ... CTE block ----------------
        if kw == "WITH":
            lines.extend(_format_cte_block(content, indent))
            continue

        # ---------------- SELECT list: one column per line ----------------
        if kw == "SELECT":
            head = "SELECT"
            up = content.upper()
            if up.startswith("DISTINCT "):
                head, content = "SELECT DISTINCT", content[len("DISTINCT "):].strip()
            elif up.startswith("ALL "):
                head, content = "SELECT ALL", content[len("ALL "):].strip()

            items = _split_top_level_commas(content)
            if len(items) == 1 and items[0].strip() == "*":
                lines.append(pad + head + " *")
                continue

            lines.append(pad + head)
            for j, item in enumerate(items):
                comma = "," if j < len(items) - 1 else ""
                item_lines = _emit_expression(pad + SQL_INDENT, item, indent + len(SQL_INDENT))
                item_lines[-1] += comma
                lines.extend(item_lines)
            continue

        # ---------------- FROM: own line, extra tables indented ----------------
        if kw == "FROM":
            items = _split_top_level_commas(content)
            for j, item in enumerate(items):
                comma = "," if j < len(items) - 1 else ""
                if j == 0:
                    item_lines = _emit_expression(pad + "FROM ", item, indent)
                else:
                    item_lines = _emit_expression(pad + SQL_INDENT, item,
                                                  indent + len(SQL_INDENT))
                item_lines[-1] += comma
                lines.extend(item_lines)
            continue

        # ---------------- JOIN: own line, one join per line ----------------
        if kw in SQL_JOIN_KEYWORDS:
            if content:
                lines.extend(_emit_expression(pad + kw + " ", content, indent))
            else:
                lines.append(pad + kw)
            continue

        # ---------------- ON: indented under its JOIN ----------------
        if kw == "ON":
            lines.extend(_format_conditions(content, indent + len(SQL_INDENT), "ON "))
            continue

        # ---------------- WHERE / HAVING: AND / OR on their own lines ----------------
        if kw in ("WHERE", "HAVING"):
            lines.extend(_format_conditions(content, indent, kw + " "))
            continue

        # ---------------- GROUP BY / ORDER BY: one item per line ----------------
        if kw in ("GROUP BY", "ORDER BY"):
            items = _split_top_level_commas(content)
            if len(items) <= 1:
                lines.append((pad + kw + " " + (items[0] if items else "")).rstrip())
            else:
                lines.append(pad + kw)
                for j, item in enumerate(items):
                    comma = "," if j < len(items) - 1 else ""
                    lines.append(pad + SQL_INDENT + item + comma)
            continue

        # ---------------- LIMIT / OFFSET / UNION / QUALIFY / VALUES / other ----------------
        lines.append((pad + kw + (" " + content if content else "")).rstrip())

    return lines or [pad + body]


def format_sql(sql: str) -> str:
    """Aligned, properly indented multi-line SQL for ANY query.

    Idempotent, so it can be applied while the query is being typed and again at the end.
    """
    text = _collapse_ws(_strip_sql_comments(str(sql or "")))
    if not text:
        return ""

    semi = ""
    if text.endswith(";"):
        text = text[:-1].strip()
        semi = ";"

    lines = _format_clauses(text, 0)
    out = "\n".join(lines).rstrip()

    if semi:
        out = out + ";"
    return out


# ============================================================
# SQL EXTRACTION HELPERS
# ============================================================
def extract_primary_table(sql: str) -> str:
    """First table name used after FROM / JOIN (top level only)."""
    up = str(sql or "").upper()
    n = len(up)
    depth = 0
    in_quote = None
    i = 0

    while i < n:
        ch = up[i]

        if in_quote:
            if ch == in_quote:
                in_quote = None
            i += 1
            continue

        if ch in ("'", '"', '`'):
            in_quote = ch
            i += 1
            continue

        if ch == '(':
            depth += 1
            i += 1
            continue

        if ch == ')':
            depth = max(0, depth - 1)
            i += 1
            continue

        if depth == 0:
            for kw in ("FROM", "JOIN"):
                if up.startswith(kw, i) and i > 0 and up[i - 1] in ' \n':
                    end = i + len(kw)
                    if end < n and (up[end].isalnum() or up[end] == '_'):
                        break
                    j = end
                    while j < n and up[j].isspace():
                        j += 1
                    k = j
                    while k < n and (up[k].isalnum() or up[k] in '_.$'):
                        k += 1
                    name = up[j:k].strip()
                    if name and name not in ("SELECT", "WITH"):
                        return name
        i += 1
    return ""


def extract_all_tables(sql: str) -> list:
    """Every real table named after FROM / JOIN (CTE names are excluded)."""
    text = _strip_sql_comments(str(sql or ""))
    cte_names = {m.upper() for m in re.findall(r"(?i)([A-Za-z_][\w$]*)\s+AS\s*\(", text)}
    names = []
    for m in re.finditer(r"(?i)\b(?:FROM|JOIN)\s+([A-Za-z_][\w$.]*)", text):
        name = m.group(1).strip()
        if name.upper() in ("SELECT", "WITH") or _base_name(name) in cte_names:
            continue
        if name not in names:
            names.append(name)
    return names


def extract_innermost_subquery(sql: str) -> str:
    """Text of the deepest parenthesised SELECT (the inner query)."""
    up = str(sql or "").upper()
    n = len(up)
    stack = []
    best = None
    in_quote = None
    i = 0

    while i < n:
        ch = up[i]

        if in_quote:
            if ch == in_quote:
                in_quote = None
            i += 1
            continue

        if ch in ("'", '"', '`'):
            in_quote = ch
            i += 1
            continue

        if ch == '(':
            k = i + 1
            while k < n and up[k].isspace():
                k += 1
            if up.startswith("SELECT", k) or up.startswith("WITH", k):
                stack.append(i)
            i += 1
            continue

        if ch == ')':
            if stack:
                start = stack.pop()
                if best is None:
                    best = (start, i)
            i += 1
            continue

        i += 1

    if best is None:
        return ""
    s, e = best
    return sql[s + 1:e].strip()


def find_cte_block_end(sql: str) -> int:
    """Index where 'WITH ... AS (...)' definitions end and the main query starts."""
    up = str(sql or "").upper()
    if not up.lstrip().startswith("WITH"):
        return -1

    n = len(sql)
    depth = 0
    in_quote = None
    i = 0

    while i < n:
        ch = up[i]

        if in_quote:
            if ch == in_quote:
                in_quote = None
            i += 1
            continue

        if ch in ("'", '"', '`'):
            in_quote = ch
            i += 1
            continue

        if ch == '(':
            depth += 1
            i += 1
            continue

        if ch == ')':
            depth = max(0, depth - 1)
            i += 1
            continue

        if depth == 0 and up.startswith("SELECT", i) and i > 0 and up[i - 1] in ' )\n':
            end = i
            while end > 0 and sql[end - 1] in ' \n':
                end -= 1
            return end

        i += 1

    return -1


def split_text_chunks(text: str, parts: int) -> list:
    """Split text into 'parts' pieces at whitespace boundaries."""
    text = str(text or "")
    parts = max(1, int(parts or 1))
    if parts <= 1 or not text.strip():
        return [text]

    target = max(1, len(text) // parts)
    chunks = []
    start = 0
    while start < len(text) and len(chunks) < parts - 1:
        end = min(len(text) - 1, start + target - 1)
        cut = text.find(" ", end)
        if cut == -1:
            cut = len(text)
        chunks.append(text[start:cut])
        start = cut
    chunks.append(text[start:])
    return chunks


def _split_candidates(sql: str) -> list:
    """Top-level clause boundaries plus top-level subquery '(' positions."""
    up = sql.upper()
    n = len(sql)
    cands = []
    depth = 0
    in_quote = None
    i = 0

    while i < n:
        ch = sql[i]

        if in_quote:
            if ch == in_quote:
                in_quote = None
            i += 1
            continue

        if ch in ("'", '"', '`'):
            in_quote = ch
            i += 1
            continue

        if ch == '(':
            if depth == 0:
                k = i + 1
                while k < n and sql[k] == ' ':
                    k += 1
                if up.startswith("SELECT", k) or up.startswith("WITH", k):
                    j = i
                    while j > 0 and sql[j - 1].isspace():
                        j -= 1
                    if j > 0:
                        cands.append(j)
            depth += 1
            i += 1
            continue

        if ch == ')':
            depth = max(0, depth - 1)
            i += 1
            continue

        if depth == 0:
            hit = None
            for kw in CLAUSE_KEYWORDS:
                if up.startswith(kw, i) and i > 0 and (sql[i - 1] == ' ' or sql[i - 1] == '\n'):
                    end = i + len(kw)
                    if end >= n or not (sql[end].isalnum() or sql[end] == '_'):
                        hit = kw
                        break
            if hit:
                j = i
                while j > 0 and sql[j - 1].isspace():
                    j -= 1
                if j > 0:
                    cands.append(j)
                i += len(hit)
                continue

        i += 1

    return sorted(set(c for c in cands if 0 < c < n))


def split_sql_progressively(sql: str, parts: int) -> list:
    """Split aligned SQL into fragments that build the full query left to right."""
    sql = (sql or "").strip()
    parts = max(1, min(int(parts or 1), 6))
    if parts <= 1 or not sql:
        return [sql]

    cands = _split_candidates(sql)
    if len(cands) < parts - 1:
        for idx, ch in enumerate(sql):
            if ch == "\n" and 0 < idx < len(sql):
                cands.append(idx)
        cands = sorted(set(cands))

    if len(cands) < parts - 1:
        parts = max(1, min(parts, len(cands) + 1))

    if parts <= 1:
        return [sql]

    total = len(cands)
    chosen = []
    for k in range(1, parts):
        idx = int(round(k * total / parts)) - 1
        idx = max(0, min(total - 1, idx))
        chosen.append(cands[idx])
    chosen = sorted(set(chosen))

    frags = []
    prev = 0
    for c in chosen:
        frags.append(sql[prev:c])
        prev = c
    frags.append(sql[prev:])
    return [f for f in frags if f.strip()] or [sql]


# ============================================================
# LOGICAL QUERY-BUILD PARSER (FROM -> JOIN -> ON -> WHERE -> ... -> SELECT)
# ============================================================
def top_level_clauses(sql: str) -> list:
    """Return [(keyword, index)] for every build-relevant top level keyword."""
    return _scan_keywords(sql, SQL_STEP_PHRASES)


def slice_sql_pieces(sql: str) -> dict:
    """Cut the final SQL into contiguous clause texts, keeping the original text."""
    pieces = {"cte": "", "select": "", "from": "", "joins": [], "where": "",
              "group_by": "", "having": "", "order_by": "", "limit": "",
              "union": "", "has_union": False}

    marks = top_level_clauses(sql)
    if not marks:
        return pieces

    select_idx = -1
    for kw, idx in marks:
        if kw == "SELECT":
            select_idx = idx
            break
    if select_idx < 0:
        return pieces
    if select_idx > 0:
        pieces["cte"] = sql[:select_idx]

    for pos, (kw, idx) in enumerate(marks):
        if idx < select_idx:
            continue
        nxt = marks[pos + 1][1] if pos + 1 < len(marks) else len(sql)

        if kw == "SELECT":
            pieces["select"] = sql[idx:nxt]
        elif kw == "FROM":
            pieces["from"] = sql[idx:nxt]
        elif kw in JOIN_WORDS:
            end = nxt
            if pos + 1 < len(marks) and marks[pos + 1][0] == "ON":
                end = marks[pos + 1][1]
            pieces["joins"].append({"join": sql[idx:end], "on": ""})
        elif kw == "ON":
            if pieces["joins"]:
                pieces["joins"][-1]["on"] = sql[idx:nxt]
            else:
                pieces["from"] += sql[idx:nxt]
        elif kw == "WHERE":
            pieces["where"] = sql[idx:nxt]
        elif kw == "GROUP BY":
            pieces["group_by"] = sql[idx:nxt]
        elif kw == "HAVING":
            pieces["having"] = sql[idx:nxt]
        elif kw == "ORDER BY":
            pieces["order_by"] = sql[idx:nxt]
        elif kw == "LIMIT":
            pieces["limit"] = sql[idx:nxt]

    if "UNION" in sql.upper():
        pieces["has_union"] = True

    return pieces


def _select_label(select_text: str) -> str:
    """Label the SELECT step from what the projection really contains."""
    up = select_text.upper()
    if "OVER" in up or "PARTITION BY" in up:
        if "ROW_NUMBER" in up or "RANK(" in up or "DENSE_RANK" in up or "NTILE" in up:
            return "Rank Results"
        return "Apply Window Function"
    if "DISTINCT" in up:
        return "Remove Duplicates"
    if any(f in up for f in ("SUM(", "COUNT(", "AVG(", "MIN(", "MAX(")):
        return "Aggregate Data"
    return "Select Data"


def rows_for_step(kind: str, all_rows: list, result_rows: list,
                  sample_cols: list) -> list:
    """Which sample rows stay bright while this logical step is applied."""
    if kind in ("understand", "cte", "from", "join", "on"):
        return list(all_rows)
    if kind == "group":
        kept = []
        seen = set()
        for idx in result_rows:
            key = str(sample_cols[idx][0]) if idx < len(sample_cols) and sample_cols[idx] else str(idx)
            if key not in seen:
                seen.add(key)
                kept.append(idx)
        return kept or list(result_rows)
    return list(result_rows)


def build_logical_items(final_sql: str, data: dict) -> list:
    """Build the query the way it is logically written, step by step."""
    if not final_sql:
        return []

    head = final_sql.lstrip().upper()
    if not (head.startswith("SELECT") or head.startswith("WITH")):
        return []

    pieces = slice_sql_pieces(final_sql)
    if pieces.get("has_union") or not pieces["select"] or not pieces["from"]:
        return []

    question = str(data.get("question_banner") or "")
    sample = data.get("sample_data") or []
    cleaned = data.get("cleaned_output") or []
    sample_cols = [list(r.get("cols") or []) for r in sample]

    all_rows = list(range(len(sample)))
    keep_count = max(1, len(cleaned)) if cleaned else max(1, len(sample))
    result_rows = list(range(min(keep_count, len(sample)))) if sample else []

    items = []

    # 1) understand the requirement (no code is written yet)
    items.append({
        "sql": "",
        "label": "Understand Requirement",
        "kind": "understand",
        "bubble": CLAUSE_BUBBLES["Understand Requirement"],
        "explanation": clamp_text(question, 90),
        "rows": all_rows,
        "dim": False,
    })

    # 2) the CTE block is computed first
    if pieces["cte"].strip():
        items.append({
            "sql": pieces["cte"].rstrip(),
            "label": "Build CTE",
            "kind": "cte",
            "bubble": CLAUSE_BUBBLES["Build CTE"],
            "explanation": "The WITH block is prepared first",
            "rows": all_rows,
            "dim": False,
        })

    base = items[-1]["sql"] if items and items[-1]["kind"] == "cte" else ""
    body = []

    def push(label, kind, text, rows, dim):
        body.append(text)
        items.append({
            "sql": base + "".join(body),
            "label": label,
            "kind": kind,
            "bubble": CLAUSE_BUBBLES.get(label, ["What: Next clause",
                                                 "Why: Build the logic",
                                                 "Result: Query grows"]),
            "explanation": "",
            "rows": rows,
            "dim": dim,
        })

    # 3) FROM
    push("Identify Tables", "from", pieces["from"], all_rows, False)

    # 4) JOIN and its ON condition (each join is its own step)
    for pair in pieces["joins"]:
        push("Join Data", "join", pair["join"], all_rows, False)
        if pair["on"].strip():
            push("Match Records", "on", pair["on"], all_rows, False)

    # 5) the row filters and grouping
    filtered = False
    if pieces["where"].strip():
        push("Filter Data", "where", pieces["where"], result_rows, True)
        filtered = True
    if pieces["group_by"].strip():
        push("Group Data", "group",
             pieces["group_by"], rows_for_step("group", all_rows, result_rows, sample_cols), True)
        filtered = True
    if pieces["having"].strip():
        push("Apply Aggregate Filter", "having", pieces["having"], result_rows, True)
        filtered = True
    if not filtered and sample:
        result_rows = all_rows

    # 6) the SELECT list is inserted above everything that was built
    select_label = _select_label(pieces["select"])
    select_item = {
        "sql": base + pieces["select"] + "".join(body),
        "label": select_label,
        "kind": "select",
        "bubble": CLAUSE_BUBBLES.get(select_label,
                                     ["What: SELECT list", "Why: Choose the columns",
                                      "Result: Final shape"]),
        "explanation": "",
        "rows": result_rows,
        "dim": bool(pieces["where"].strip() or pieces["group_by"].strip()
                    or pieces["having"].strip()),
    }
    items.append(select_item)

    # 7) sorting and limiting come after the projection
    if pieces["order_by"].strip():
        push("Sort Results", "order", pieces["order_by"], result_rows, select_item["dim"])
    if pieces["limit"].strip():
        push("Limit Results", "limit", pieces["limit"], result_rows, select_item["dim"])

    # 8) the finished query
    items.append({
        "sql": final_sql,
        "label": "Final Query",
        "kind": "final",
        "bubble": CLAUSE_BUBBLES["Final Query"],
        "explanation": "Complete query in the correct SQL format",
        "rows": result_rows,
        "dim": select_item["dim"],
        "active_all": True,
    })

    for item in items:
        item["sql"] = str(item["sql"] or "")
    return items


def _common_prefix_len(a: str, b: str) -> int:
    limit = min(len(a), len(b))
    i = 0
    while i < limit and a[i] == b[i]:
        i += 1
    return i


def _common_suffix_len(a: str, b: str) -> int:
    limit = min(len(a), len(b))
    i = 0
    while i < limit and a[len(a) - 1 - i] == b[len(b) - 1 - i]:
        i += 1
    return i


def build_plan_from_items(items: list) -> list:
    """Turn cumulative query states into animation steps (start / append / insert / wrap)."""
    plan = []
    prev = ""

    for i, item in enumerate(items):
        target = str(item.get("sql") or "")
        entry = {
            "type": "query",
            "query": target,
            "typed": "",
            "prepend": "",
            "appendafter": "",
            "at": 0,
            "mode": "append",
            "label": item.get("label") or "Transform Data",
            "bubble": _as_str_list(item.get("bubble"), pad_to=3)[:3],
            "explanation": str(item.get("explanation") or ""),
            "rows": item.get("rows"),
            "dim": bool(item.get("dim")),
            "active_all": bool(item.get("active_all")),
        }

        if i == 0:
            entry["mode"] = "start"
            entry["typed"] = target
            start_off, end_off = 0, len(target)
        elif prev and prev in target and target.find(prev) > 0:
            pos = target.find(prev)
            entry["mode"] = "wrap"
            entry["prepend"] = target[:pos]
            entry["appendafter"] = target[pos + len(prev):]
            entry["at"] = pos
            start_off, end_off = 0, len(target)
        elif target.startswith(prev):
            entry["mode"] = "append"
            entry["typed"] = target[len(prev):]
            entry["at"] = len(prev)
            start_off, end_off = len(prev), len(target)
        else:
            pre = _common_prefix_len(prev, target)
            suffix = _common_suffix_len(prev[pre:], target[pre:])
            insert_end = len(target) - suffix if suffix else len(target)
            entry["mode"] = "insert"
            entry["typed"] = target[pre:insert_end]
            entry["at"] = pre
            start_off, end_off = pre, insert_end

        if entry["active_all"]:
            entry["active_from"] = 0
            entry["active_to"] = target.count("\n") + 1
        elif entry["mode"] == "wrap":
            entry["active_from"] = 0
            entry["active_to"] = target.count("\n")
        else:
            entry["active_from"] = target[:start_off].count("\n") if target else 0
            entry["active_to"] = target[:end_off].count("\n") if target else 0

        plan.append(entry)
        prev = target

    return plan


# ============================================================
# FALLBACK PLANNERS (used only when the SQL cannot be split logically)
# ============================================================
def build_nested_states(final_sql: str, count: int) -> list:
    """Inner query first, then the outer query built around it (inner code kept)."""
    inner = extract_innermost_subquery(final_sql)
    if not inner:
        return []

    pos = final_sql.find(inner)
    if pos <= 0:
        return []

    pre = final_sql[:pos]
    post = final_sql[pos + len(inner):]

    count = max(2, min(int(count or 3), 5))
    states = [inner, pre + inner]

    if count > 2 and post.strip():
        chunks = split_text_chunks(post, count - 2)
        for k in range(1, count - 1):
            states.append(pre + inner + "".join(chunks[:k]))

    if states[-1] != final_sql:
        states.append(final_sql)

    unique = []
    for s in states:
        if not unique or unique[-1] != s:
            unique.append(s)
    return unique


def build_cte_states(final_sql: str, count: int) -> list:
    """CTE first, then the outer query, then the remaining conditions (all appended)."""
    end = find_cte_block_end(final_sql)
    if end <= 0:
        return []

    base = final_sql[:end].rstrip()
    rest = final_sql[end:]
    if not base.strip() or not rest.strip():
        return []

    count = max(2, min(int(count or 3), 5))
    parts_wanted = count - 1
    if parts_wanted <= 1:
        return [base, base + rest]

    cands = _split_candidates(rest)
    if len(cands) < parts_wanted - 1:
        for idx, ch in enumerate(rest):
            if ch == "\n" and 0 < idx < len(rest):
                cands.append(idx)
        cands = sorted(set(cands))

    if len(cands) >= parts_wanted - 1 and parts_wanted > 1:
        total = len(cands)
        cuts = []
        for k in range(1, parts_wanted):
            idx = int(round(k * total / parts_wanted)) - 1
            idx = max(0, min(total - 1, idx))
            cuts.append(cands[idx])
        cuts = sorted(set(cuts))
    else:
        cuts = sorted(set(cands))

    states = [base]
    for c in cuts:
        states.append(base + rest[:c])
    states.append(base + rest)

    unique = []
    for s in states:
        if not unique or unique[-1] != s:
            unique.append(s)
    return unique


def build_plan_states(final_sql: str, count: int) -> list:
    """Fallback execution-order build: inner query -> CTE -> outer query -> conditions."""
    states = build_nested_states(final_sql, count)
    if not states:
        states = build_cte_states(final_sql, count)
    if not states:
        n = max(2, min(int(count or 3), 5))
        frags = split_sql_progressively(final_sql, n)
        cumulative = ""
        states = []
        for f in frags:
            cumulative += f
            states.append(cumulative)
    return states


# ============================================================
# THEME SYSTEM (one centralised place for every background)
#   - 12 professional themes, each defines the animation AND thumbnail colours
#   - ThemeSelector remembers the recent picks per scope and avoids repeats
#   - topic_theme_preferences() suggests themes that suit the SQL topic
# ============================================================
THEME_SPECS = [
    {"key": "ai_neon", "name": "AI Neon Purple",
     "bg": "linear-gradient(160deg,#170D2E 0%,#0B1020 100%)",
     "panel": "#21143D", "border": "#8B2EFF",
     "accent": "#8B2EFF", "accent2": "#F000D0", "solid": "#170D2E"},
]

# ONE colour system for the whole application (do not add other colours)
PALETTE = {
    "bg_purple": "#170D2E", "bg_navy": "#0B1020", "panel": "#21143D",
    "purple": "#8B2EFF", "magenta": "#F000D0", "pink": "#FF6B9D",
    "yellow": "#FFD900", "blue": "#1677FF", "orange": "#FF8A00",
    "white": "#FFFFFF", "lavender": "#D5CEE8",
}
GRADIENT = "linear-gradient(90deg,#8B2EFF 0%,#F000D0 55%,#FF6B9D 100%)"


def build_theme(spec: dict) -> dict:
    """The single colour system: used by the thumbnail (and the theme CSS of the page)."""
    return {
        "key": spec["key"],
        "name": spec["name"],
        "bg": spec["bg"],
        "glow1": "transparent",
        "glow2": "transparent",
        "glow3": "transparent",
        "panel": spec["panel"],
        "border": spec["border"],
        "accent": spec["accent"],
        "accent2": spec["accent2"],
        "accent_soft": spec["panel"],
        "accent_border": spec["border"],
        "text": PALETTE["white"],
        "muted": PALETTE["lavender"],
        "editor": PALETTE["bg_navy"],
        "grid": "transparent",
        "hl": GRADIENT,
        "bar": PALETTE["purple"],
        "tick": PALETTE["magenta"],
        "pill": PALETTE["yellow"],
        "pill_text": PALETTE["bg_purple"],
        "strip": GRADIENT,
        "bars": PALETTE["purple"],
        "kw": PALETTE["pink"],
        "fn": PALETTE["orange"],
        "num": PALETTE["lavender"],
        "solid": spec["solid"],
    }


THEME_BY_KEY = {spec["key"]: build_theme(spec) for spec in THEME_SPECS}
ALL_THEME_KEYS = [spec["key"] for spec in THEME_SPECS]

# old AI theme names -> new theme keys (so older prompts still map correctly)
THEME_KEY_ALIASES = {
    "neon_violet": "violet",
    "emerald_data": "emerald",
    "sunset_amber": "sunset",
    "crimson_ink": "burgundy",
    "graphite_lime": "charcoal",
    "graphite": "charcoal",
    "navy": "midnight",
    "navy_grid": "midnight",
}


class ThemeSelector:
    """Central picker: never repeats a recent theme while alternatives exist."""

    def __init__(self, memory: int = THEME_HISTORY_SIZE):
        self._memory = memory
        self._lock = threading.Lock()
        self._recent = {}

    def choose(self, scope: str, keys: list, preferred: list = ()) -> str:
        with self._lock:
            recent = self._recent.setdefault(scope, deque(maxlen=self._memory))
            pool = [k for k in keys if k not in recent]
            if not pool:
                last = recent[-1] if recent else None
                pool = [k for k in keys if k != last] or list(keys)
            chosen = next((k for k in preferred if k in pool), None)
            if chosen is None:
                chosen = random.choice(pool)
            recent.append(chosen)
            return chosen


THEME_SELECTOR = ThemeSelector()


def topic_theme_preferences(question: str, sql: str, ai_key: str = "") -> list:
    """Themes that suit the SQL topic, best first. The AI's own choice comes first."""
    text = f"{question} {sql}".upper()
    prefs = []

    def add(*keys):
        for k in keys:
            if k in THEME_BY_KEY and k not in prefs:
                prefs.append(k)

    if ai_key:
        add(THEME_KEY_ALIASES.get(ai_key, ai_key))
    if any(k in text for k in ("ROW_NUMBER", "DENSE_RANK", "RANK(", "NTILE", "OVER (", "OVER(")):
        add("violet", "indigo", "minimal_mono")
    if any(k in text for k in ("GROUP BY", "SUM(", "COUNT(", "AVG(", "HAVING", "MAX(", "MIN(")):
        add("emerald", "dark_teal", "arctic_steel")
    if "JOIN" in text:
        add("midnight", "electric_cyan")
    if any(k in text for k in ("DATE", "YEAR", "MONTH", "DAY", "TRUNC", "BETWEEN")):
        add("amber", "sunset")
    if any(k in text for k in ("DELETE", "UPDATE", "INSERT", "MERGE", "CREATE")):
        add("charcoal", "minimal_mono", "burgundy")
    add("midnight", "electric_cyan", "indigo", "dark_teal", "burgundy", "sunset",
        "arctic_steel", "emerald", "amber", "violet", "charcoal", "minimal_mono")
    return prefs


# ============================================================
# DYNAMIC BACKGROUND COLOURS - a new colour for every video and every thumbnail
# (only the background changes; the studio window keeps its own colours)
# ============================================================
BG_HUE_HISTORY = deque(maxlen=3)
BG_COLOUR_LOCK = threading.Lock()


def _hex_relative_luminance(hex_color):
    r, g, b = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]

    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def _contrast_ratio(a, b):
    la, lb = sorted([_hex_relative_luminance(a), _hex_relative_luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _hls_to_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def next_background_color():
    """A dark, eye-friendly background that is different from the last few ones.
    Text in white always keeps at least 7:1 contrast."""
    with BG_COLOUR_LOCK:
        for _ in range(3000):
            hue = random.random()
            too_close = any(min(abs(hue - h), 1 - abs(hue - h)) < 0.08 for h in BG_HUE_HISTORY)
            if too_close:
                continue
            light = random.uniform(0.12, 0.20)
            sat = random.uniform(0.30, 0.50)
            solid = _hls_to_hex(hue, light, sat)
            if _contrast_ratio(solid, "#FFFFFF") < 7.0:
                continue
            darker = _hls_to_hex(hue, max(0.06, light - 0.05), sat)
            BG_HUE_HISTORY.append(hue)
            return {"solid": solid,
                    "gradient": f"linear-gradient(160deg,{solid} 0%,{darker} 100%)",
                    "hue": round(hue * 360)}
        BG_HUE_HISTORY.append(0.62)
        return {"solid": "#1B1F3B", "gradient": "linear-gradient(160deg,#1B1F3B 0%,#101426 100%)", "hue": 223}


def choose_reel_theme(question: str, sql: str) -> dict:
    """Theme of one video: the palette for accents, a new background colour every time."""
    theme = dict(build_theme(THEME_SPECS[0]))
    colour = next_background_color()
    theme["bg"] = colour["gradient"]
    theme["solid"] = colour["solid"]
    theme["name"] = f"Background hue {colour['hue']}"
    return theme


def theme_css(theme: dict) -> str:
    """CSS custom properties for the animation page."""
    lines = [
        ":root {",
        f"  --bg: {theme['bg']};",
        f"  --glow-1: {theme['glow1']};",
        f"  --glow-2: {theme['glow2']};",
        f"  --panel-bg: {theme['panel']};",
        f"  --border-color: {theme['border']};",
        f"  --blue-accent: {theme['accent']};",
        f"  --green-accent: {theme['accent2']};",
        "  --yellow-accent: #facc15;",
        "  --red-accent: #f87171;",
        f"  --text-main: {theme['text']};",
        f"  --text-muted: {theme['muted']};",
        f"  --editor-bg: {theme['editor']};",
        f"  --grid-line: {theme['grid']};",
        "}",
    ]
    return "\n".join(lines)


# ============================================================
# LEARNING / TRAINING MEMORY (cached by file modification time)
# ============================================================
_LEARN_CACHE = {"mtime": None, "examples": []}
_LEARN_LOCK = threading.Lock()


def load_learning_store() -> list:
    try:
        if not LEARNING_STORE_PATH.exists():
            return []
        mtime = LEARNING_STORE_PATH.stat().st_mtime
        with _LEARN_LOCK:
            if _LEARN_CACHE["mtime"] == mtime:
                return list(_LEARN_CACHE["examples"])
            with open(LEARNING_STORE_PATH, "r", encoding="utf-8") as f:
                store = json.load(f)
            examples = store.get("examples", []) if isinstance(store, dict) else store
            if not isinstance(examples, list):
                examples = []
            _LEARN_CACHE["mtime"] = mtime
            _LEARN_CACHE["examples"] = examples
            return list(examples)
    except Exception as e:
        log_message(f"WARNING: learning memory read skipped: {str(e)[:60]}")
    return []


def save_learning_example(question: str, data: dict, model_name: str):
    try:
        LEARNING_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        examples = load_learning_store()

        q_key = question.strip().lower()
        examples = [ex for ex in examples
                    if str(ex.get("question", "")).strip().lower() != q_key]

        examples.append({
            "question": question,
            "question_banner": data.get("question_banner", question),
            "table_name": data.get("table_name", "TABLE"),
            "logic_explanation": data.get("logic_explanation", ""),
            "process_summary": data.get("process_summary", []),
            "table_headers": data.get("table_headers", []),
            "sample_data": data.get("sample_data", []),
            "chips": data.get("chips", []),
            "steps": [
                {
                    "query": s.get("query", ""),
                    "explanation": s.get("explanation", ""),
                    "bubble": s.get("bubble", []),
                }
                for s in data.get("steps", [])
            ],
            "cleaned_output": data.get("cleaned_output", []),
            "learned_from_model": model_name,
            "learned_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        examples = examples[-MAX_LEARNING_EXAMPLES:]

        with open(LEARNING_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump({"examples": examples}, f, ensure_ascii=False, indent=2)
        with _LEARN_LOCK:
            _LEARN_CACHE["mtime"] = None

        log_message(f"LEARNED + SAVED. Memory now holds {len(examples)} example(s)")
    except Exception as e:
        log_message(f"WARNING: could not save to learning memory: {str(e)[:60]}")


def build_few_shot_block(examples: list) -> str:
    if not examples:
        return ""

    blocks = []
    for ex in examples[-MAX_FEWSHOT_EXAMPLES:]:
        summary = {
            "question_banner": ex.get("question_banner", ex.get("question", "")),
            "table_name": ex.get("table_name", "TABLE"),
            "logic_explanation": ex.get("logic_explanation", ""),
            "process_summary": ex.get("process_summary", []),
            "table_headers": ex.get("table_headers", []),
            "sample_data": ex.get("sample_data", []),
            "chips": ex.get("chips", []),
            "steps": [
                {
                    "query": s.get("query", ""),
                    "explanation": s.get("explanation", ""),
                    "bubble": s.get("bubble", []),
                }
                for s in ex.get("steps", [])
            ],
            "cleaned_output": ex.get("cleaned_output", []),
        }
        blocks.append(json.dumps(summary, ensure_ascii=False, indent=2))

    return (
        "LEARNED EXAMPLES (your own previous CORRECT answers - copy this style, depth and exact JSON shape):\n"
        + "\n".join(blocks)
        + "\n\nUse the above ONLY as a style/logic reference. "
          "The CURRENT question below must be answered with fresh, correct SQL of the same quality."
    )


def build_error_feedback_block(model_name: str, attempt: int, error_text: str) -> str:
    return f"""SELF-CORRECTION REQUIRED - YOUR PREVIOUS ATTEMPT FAILED
Model: {model_name}
Failed attempt number: {attempt}
Exact error: {error_text}

Fix that exact error and return the corrected COMPLETE JSON only."""


# ============================================================
# RESPONSE REPAIR LAYER
# ============================================================
def _normalize_tables(raw) -> list:
    out = []
    if not isinstance(raw, list):
        return out
    for t in raw:
        if not isinstance(t, dict):
            continue
        name = str(t.get("name") or t.get("table_name") or "").strip()
        if not name:
            continue
        headers = _as_str_list(t.get("headers") or t.get("table_headers") or t.get("columns"))
        rows = []
        raw_rows = t.get("rows") or t.get("sample_data") or []
        if isinstance(raw_rows, list):
            for r in raw_rows:
                if isinstance(r, dict) and isinstance(r.get("cols"), (list, tuple)):
                    vals = _as_str_list(r.get("cols"))
                elif isinstance(r, dict) and headers:
                    vals = [str(r.get(h, "")) for h in headers]
                elif isinstance(r, dict):
                    vals = [str(v) for v in r.values()]
                else:
                    vals = _as_str_list(r)
                rows.append(vals)
        width = max([len(headers)] + [len(r) for r in rows] + [1])
        headers = headers + [f"COL_{i + 1}" for i in range(len(headers), width)]
        rows = [_as_str_list(r, pad_to=width)[:width] for r in rows]
        out.append({"name": name, "headers": headers, "rows": rows})
    return out


def normalize_parsed(raw_parsed, question: str = "") -> dict:
    parsed = raw_parsed

    if isinstance(parsed, dict) and len(parsed) == 1:
        only_key = list(parsed.keys())[0]
        if str(only_key).strip().lower() in ("response", "result", "data", "output", "json", "answer"):
            if isinstance(parsed[only_key], dict):
                parsed = parsed[only_key]

    if not isinstance(parsed, dict):
        raise ValueError("Response is not a JSON object")

    flat = {str(k).strip().lower().replace(" ", "_"): v for k, v in parsed.items()}
    found = {}
    for canonical, aliases in KEY_ALIASES.items():
        for alias in aliases:
            if alias in flat:
                found[canonical] = flat[alias]
                break

    raw_out = found.get("cleaned_output")
    if not isinstance(raw_out, list):
        raw_out = []
    cleaned_output = [_as_str_list(row) for row in raw_out
                      if isinstance(row, (list, tuple, str, dict))]

    raw_rows = found.get("sample_data")
    if not isinstance(raw_rows, list):
        raw_rows = []

    headers = _as_str_list(found.get("table_headers"))
    sample_cols = []
    for row in raw_rows:
        if isinstance(row, dict) and isinstance(row.get("cols"), (list, tuple)):
            sample_cols.append(_as_str_list(row.get("cols")))
        elif isinstance(row, dict):
            if headers:
                sample_cols.append([
                    str(row.get(h, row.get(h.lower(), row.get(h.upper(), "")))) for h in headers
                ])
            else:
                sample_cols.append(_as_str_list(list(row.values())))
        else:
            sample_cols.append(_as_str_list(row))

    widths = [len(r) for r in sample_cols] + [len(r) for r in cleaned_output] + [len(headers), 1]
    width = max(widths)
    if not headers or len(headers) < width:
        headers = headers + [f"COL_{i + 1}" for i in range(len(headers), width)]

    if not sample_cols:
        if cleaned_output:
            sample_cols = [list(r) for r in cleaned_output]
            log_message("REPAIR: sample_data was missing -> rebuilt from cleaned_output")
        else:
            sample_cols = [["-"] * width]
            log_message("REPAIR: sample_data was missing -> placeholder row used")

    sample_data = [
        {"id": f"row{i + 1}", "cols": _as_str_list(cols, pad_to=width)[:width]}
        for i, cols in enumerate(sample_cols)
    ]

    before = len(sample_data)
    sample_data = pad_sample_data(sample_data, MIN_SAMPLE_ROWS)
    if len(sample_data) > before:
        log_message(f"SAMPLE TABLE: padded {before} -> {len(sample_data)} rows")

    raw_steps = found.get("steps")
    if not isinstance(raw_steps, list):
        raw_steps = []
    steps = []
    for s in raw_steps:
        if isinstance(s, str):
            steps.append({"type": "query", "query": s.strip(),
                          "explanation": "", "bubble": ["", "", ""]})
            continue
        if not isinstance(s, dict):
            continue
        query = str(s.get("query") or s.get("sql") or s.get("code") or "").strip()
        explanation = clamp_text(s.get("explanation") or s.get("description") or "", 120)
        bubble = [clamp_text(b, MAX_BUBBLE_CHARS)
                  for b in _as_str_list(s.get("bubble") or s.get("bullets") or s.get("notes"),
                                        pad_to=3)[:3]]
        steps.append({"type": "query", "query": query,
                      "explanation": explanation, "bubble": bubble})

    raw_chips = _as_str_list(found.get("chips"))
    chips = []
    for c in raw_chips:
        label = normalize_label(c)
        if label:
            chips.append(label)
        elif c.strip():
            log_message(f"CHIP: '{clamp_text(c, 30)}' is not in the allowed label list - ignored")
    if len(chips) < len(steps):
        chips = chips + ["" for _ in range(len(chips), len(steps))]

    process = [clamp_text(p, MAX_PROCESS_CHARS)
               for p in _as_str_list(found.get("process_summary")) if p.strip()]

    return {
        "question_banner": str(found.get("question_banner") or question or "SQL Query"),
        "table_name": str(found.get("table_name") or "TABLE"),
        "logic_explanation": str(found.get("logic_explanation") or ""),
        "process_summary": process,
        "sample_data": sample_data,
        "table_headers": headers,
        "tables": _normalize_tables(found.get("tables")),
        "chips": chips,
        "steps": steps,
        "cleaned_output": cleaned_output,
    }


def derive_process_summary(data: dict) -> list:
    """2-3 short concept lines shown in the bottom comment bubble during the video."""
    process = [clamp_text(p, MAX_PROCESS_CHARS)
               for p in (data.get("process_summary") or [])
               if str(p).strip() and str(p).strip() != "..."]

    if not process:
        process = [clamp_text(s.get("explanation") or "", MAX_PROCESS_CHARS)
                   for s in data.get("steps", []) if str(s.get("explanation") or "").strip()]

    if not process:
        process = [
            "The FROM clause picks the table",
            "WHERE, GROUP BY and HAVING shape the rows",
            "SELECT chooses the final columns",
        ]

    return [p for p in process if p][:3]


def validate_json_response(raw_text: str, question: str = "") -> dict:
    text = raw_text.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start:end + 1]

    try:
        parsed = json.loads(text)
    except Exception as e:
        raise Exception(f"JSON error: {str(e)}")

    try:
        data = normalize_parsed(parsed, question)
    except Exception as e:
        raise Exception(f"JSON error: {str(e)}")

    if not data["steps"]:
        raise Exception("JSON error: Missing keys: ['steps']")

    usable = [s for s in data["steps"]
              if any(k in (s["query"] or "").upper() for k in MIN_SQL_KEYWORDS)]
    if not usable:
        raise Exception("JSON error: no step contains a full SQL query")

    data["steps"] = usable
    return data


# ============================================================
# RESULT COLUMN NAMES (used for the simulated result table)
# ============================================================
def output_column_names(sql: str, fallback_headers: list) -> list:
    """Names of the columns the query returns (aliases where given)."""
    pieces = slice_sql_pieces(sql or "")
    sel = pieces.get("select", "")
    body = re.sub(r"(?is)^\s*SELECT\s+(DISTINCT\s+|ALL\s+)?", "", sel).strip()
    items = _split_top_level_commas(body) if body else []
    names = []
    for item in items:
        if item.strip() == "*":
            names.extend(fallback_headers or ["*"])
            continue
        m = re.search(r"(?i)\bAS\s+([A-Za-z_][\w$]*|\"[^\"]+\")\s*$", item)
        if m:
            name = m.group(1).strip('"')
        else:
            m2 = re.search(r"([A-Za-z_][\w$]*)\s*$", item.strip())
            name = m2.group(1) if m2 else f"EXPR_{len(names) + 1}"
        names.append(name)
    return names


# ============================================================
# OLLAMA CALL
# ============================================================
def call_ollama_model(model_name: str, prompt: str):
    base = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "options": OLLAMA_OPTIONS,
        "keep_alive": OLLAMA_KEEP_ALIVE,
    }

    try:
        return ollama.chat(format=JSON_SCHEMA, **base), "schema-forced"
    except Exception as e:
        log_message(f"NOTE {model_name}: schema mode unsupported ({str(e)[:40]}) - JSON mode")

    try:
        return ollama.chat(format="json", **base), "json-mode"
    except Exception as e:
        log_message(f"NOTE {model_name}: JSON mode unsupported ({str(e)[:40]}) - plain mode")

    return ollama.chat(**base), "plain"


def build_prompt(question: str, few_shot_block: str = "", error_feedback: str = "",
                 user_sql: str = "", user_logic: str = "") -> str:
    label_list = ", ".join(f'"{lab}"' for lab in ALLOWED_LABELS)

    prompt = f"""You are an expert SQL instructor who teaches students with clean, aligned SQL.

LANGUAGE RULE (STRICT): every single word you output must be in English.
No Hindi, no Hinglish, no transliteration, anywhere.

FORMAT RULE (STRICT): every SQL query must be properly formatted multi-line SQL:
- SELECT on its own line, every column on its own indented line
- FROM on its own line, INNER JOIN / LEFT JOIN on their own lines
- the ON condition indented under its JOIN
- WHERE / GROUP BY / HAVING / ORDER BY / LIMIT each start on their own line
- AND / OR conditions on their own lines
- end with a semicolon

USER QUESTION: "{question}"

STEP 1: LOGICAL APPROACH (algorithm, aggregation, filtering, ordering)

STEP 2: TABLES AND SAMPLE DATA - MUST MATCH THE QUERY
- "tables" = EVERY table used in FROM or JOIN, each with "name", "headers" (real RAW column names)
  and 5 or 6 realistic "rows" using exactly those columns
- the first item of "tables" must be the main table of the FROM clause
- "table_name" and "table_headers" and "sample_data" describe that first table
- never invent unrelated columns; keep shared key columns (for example CUSTOMER_ID) with matching values across tables
- every table used in FROM or JOIN needs at least 4 columns and 5 rows, also when three or more tables are joined; keep the tables small and the column names short
- the sample data must demonstrate the problem: include rows that satisfy the condition AND rows that do not, keep key values matching across tables, and use realistic business values (names, amounts, dates)
- include both matching and non-matching key values across the tables, so the JOIN shows matched and unmatched rows

STEP 3: SQL SOLUTION
- each step must contain a COMPLETE, WORKING, PROPERLY FORMATTED query

STEP 4: EXPLAIN IN PARTS
- "steps" = 2 to 5 parts
- steps[i].explanation = one short sentence naming the SQL concept
- steps[i].bubble = exactly 3 short lines, each under {MAX_BUBBLE_CHARS} characters:
      "What: ...", "Why: ...", "Result: ..."

STEP 4b: STEP LABELS ("chips") - CHOOSE ONLY FROM THIS LIST
{label_list}

Rules for "chips":
- exactly one label per step, in the same order as "steps"
- use ONLY the labels above, word for word, and never invent a new label
- use the MINIMUM number of labels that genuinely describe this query

STEP 5: CONCEPT COMMENTS (shown in the bottom comment bubble during the video)
- "process_summary" = 2 or 3 very short sentences, each under {MAX_PROCESS_CHARS} characters
- these sentences must explain the CONCEPT of the query execution, in plain English
"""

    if user_sql:
        prompt += f"""
USER PROVIDED SQL - THIS IS AUTHORITATIVE (the animation must show exactly this):
{user_sql}

Rules:
- steps[i].query must contain this SQL (formatted), never a different query
- table_name, table_headers, tables, sample_data, chips, process_summary and cleaned_output
  must all describe THIS query and its real tables
"""

    if user_logic:
        prompt += f"""
USER PROVIDED LOGIC / GUIDANCE - YOU MUST FOLLOW THIS EXACTLY:
{user_logic}
"""

    prompt += r"""
NOW generate for the given question.

Return ONLY this JSON (no markdown, no explanation):
{
    "question_banner": "Repeat the exact question",
    "table_name": "EMPLOYEE",
    "logic_explanation": "Short step-by-step logic",
    "process_summary": [
        "The FROM clause picks the table",
        "WHERE keeps the matching rows",
        "SELECT shapes the final output"
    ],
    "tables": [
        {"name": "EMPLOYEE", "headers": ["EMP_ID", "NAME", "SALARY"],
         "rows": [["E001", "Raj Kumar", "95000"], ["E002", "Priya Sharma", "85000"],
                  ["E003", "Amit Singh", "75000"], ["E004", "Neha Patel", "85000"],
                  ["E005", "Vikram Rao", "68000"], ["E006", "Sneha Joshi", "72000"]]}
    ],
    "sample_data": [
        {"id": "row1", "cols": ["E001", "Raj Kumar", "95000"]},
        {"id": "row2", "cols": ["E002", "Priya Sharma", "85000"]},
        {"id": "row3", "cols": ["E003", "Amit Singh", "75000"]},
        {"id": "row4", "cols": ["E004", "Neha Patel", "85000"]},
        {"id": "row5", "cols": ["E005", "Vikram Rao", "68000"]},
        {"id": "row6", "cols": ["E006", "Sneha Joshi", "72000"]}
    ],
    "table_headers": ["EMP_ID", "NAME", "SALARY"],
    "chips": ["Identify Tables", "Filter Data", "Select Data", "Final Query"],
    "steps": [
        {
            "type": "query",
            "query": "SELECT\n    EMP_ID,\n    NAME,\n    SALARY\nFROM EMPLOYEE\nWHERE SALARY > 70000;",
            "explanation": "Pick the table, filter the rows, then choose the columns",
            "bubble": ["What: Simple SELECT", "Why: Filter first", "Result: Filtered rows"]
        }
    ],
    "cleaned_output": [
        ["E001", "Raj Kumar", "95000"]
    ]
}

CRITICAL RULES:
1. THINK about the logic first
2. EVERY WORD MUST BE IN ENGLISH
3. Every query must be PROPERLY FORMATTED multi-line SQL ending with ";"
4. "chips" must use ONLY the allowed labels above and only the clauses the query really has
5. sample_data must have 5 or 6 rows, table_name and table_headers MUST match the query
6. process_summary must have 2 or 3 short concept sentences
7. cleaned_output must match what the final query really returns
8. ALL KEYS ARE COMPULSORY: question_banner, table_name, logic_explanation, process_summary,
   sample_data, table_headers, tables, chips, steps, cleaned_output"""

    if few_shot_block:
        prompt += "\n\n" + few_shot_block

    if error_feedback:
        prompt += "\n\n" + error_feedback

    return prompt


# ============================================================
# YOUTUBE METADATA (Title / Description / Hashtags) - AI generated
#   Text only: these actions never change any background.
# ============================================================
def build_metadata_prompt(question: str, query_logic: str, kind: str) -> str:
    context = f'SQL QUESTION: "{question}"' if question else "SQL QUESTION: (not given)"
    if query_logic:
        context += f"\n\nSQL QUERY / LOGIC:\n{query_logic}"

    if kind == "title":
        task = ("Write ONE YouTube title for this SQL tutorial video.\n"
                "- maximum 70 characters\n"
                "- mention the real SQL concept and the table or column from the query\n"
                "- clear, specific and interesting for beginners\n"
                "- no quotes, no markdown, no hashtags\n"
                "Return ONLY the title text.")
    elif kind == "description":
        task = ("Write a YouTube description for this SQL tutorial video.\n"
                "- 4 to 6 short lines\n"
                "- line 1: what the viewer will learn in this video\n"
                "- then explain the logic in simple words, using the real table/column names\n"
                "- one closing line inviting viewers to subscribe for daily SQL content\n"
                "- plain English, no markdown, no hashtags\n"
                "Return ONLY the description text.")
    else:
        task = ("Generate 15 to 20 relevant YouTube hashtags for this SQL tutorial video.\n"
                "- mix broad tags (SQL, DataEngineering, SQLInterview) with specific tags\n"
                "  taken from the actual topic, table names and SQL concepts in the query\n"
                "- every hashtag starts with # and uses CamelCase with no spaces\n"
                "- one line, hashtags separated by spaces\n"
                "Return ONLY the hashtags.")

    return ("You are a YouTube content strategist for a SQL and Data Engineering channel.\n"
            "LANGUAGE RULE: reply in English only.\n\n"
            f"{context}\n\n{task}")


def clean_metadata_text(text: str, kind: str) -> str:
    t = str(text or "").strip()
    if not t:
        return ""

    lines = [ln for ln in t.splitlines() if not ln.strip().startswith("```")]
    t = "\n".join(lines).strip()
    t = t.replace("**", "").replace("__", "")

    if kind.startswith("title"):
        first = t.splitlines()[0].strip() if t.splitlines() else ""
        if first.lower().startswith("title:"):
            first = first.split(":", 1)[1].strip()
        return first.strip('"').strip("'").strip()[:110]

    if kind.startswith("hashtag"):
        tags = re.findall(r"#\w+", t)
        if not tags:
            words = re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", t)
            tags = ["#" + w for w in words]
        seen, out = set(), []
        for tag in tags:
            key = tag.lower()
            if key not in seen:
                seen.add(key)
                out.append(tag)
        return " ".join(out[:20])

    kept = [ln.strip() for ln in t.splitlines() if ln.strip()]
    return "\n".join(kept[:10])


# ============================================================
# TITLE LINE  (Topic | Audience | Skill | Format)  and  TAGS
# Built from the actual question and query. Words change every time and
# recent titles are never repeated.
# ============================================================
TITLE_FORMAT_OPTIONS = ["Short Word Question", "One Minute Question", "Quick Coding Question", "Interview Tip"]
RECENT_TITLES = deque(maxlen=12)
AUDIENCE_VARIANTS = {
    "Beginner Friendly": ["Beginner Friendly", "Learn SQL Basics", "Student Friendly"],
    "Interview Preparation": ["Interview Preparation", "Job Interview Practice", "Technical Interview"],
    "Data Analyst Level": ["Data Analyst Level", "Analytics Practice", "Advanced SQL"],
}
SKILL_VARIANTS = {
    "Unmatched Rows": ["Unmatched Rows", "Missing Matches", "Anti Join Pattern"],
    "NULL Filter": ["NULL Filter", "Missing Values", "IS NULL Check"],
    "Left Join": ["Left Join", "Keep All Rows", "Outer Join"],
    "Inner Join": ["Inner Join", "Matching Rows", "Joining Tables"],
    "Aggregate Filter": ["Aggregate Filter", "Group Filter", "HAVING Clause"],
    "Group By": ["Group By", "Summarising Data", "Grouped Totals"],
    "Window Functions": ["Window Functions", "Ranking Rows", "Running Totals"],
    "Subqueries": ["Subqueries", "Nested Queries", "Inner Query"],
    "CTE": ["CTE", "Temporary Result", "WITH Clause"],
    "Filtering": ["Filtering", "WHERE Clause", "Row Conditions"],
    "Sorting": ["Sorting", "ORDER BY", "Ranking Output"],
    "Distinct Values": ["Distinct Values", "Removing Duplicates", "Unique Rows"],
    "Basic Select": ["Basic Select", "Choosing Columns", "Reading Data"],
}
TITLE_LOCK = threading.Lock()
TAG_STOPWORDS = {"the", "a", "an", "of", "to", "in", "for", "and", "or", "who", "which", "that", "with",
                 "find", "all", "get", "show", "list", "is", "are", "have", "has", "never", "ever", "from",
                 "their", "each", "every", "by", "on", "at", "be", "do", "does", "made", "make"}


def _query_skill(query):
    """The main SQL / Python concept of the query, in plain words."""
    up = (query or "").upper()
    if re.search(r"\bLEFT\s+(OUTER\s+)?JOIN\b", up) and re.search(r"\bIS\s+NULL\b", up):
        return "Unmatched Rows"
    if re.search(r"\bIS\s+NULL\b", up):
        return "NULL Filter"
    if re.search(r"\bLEFT\s+(OUTER\s+)?JOIN\b", up):
        return "Left Join"
    if re.search(r"\bJOIN\b", up):
        return "Inner Join"
    if "HAVING" in up:
        return "Aggregate Filter"
    if "GROUP BY" in up:
        return "Group By"
    if re.search(r"\bOVER\s*\(", up):
        return "Window Functions"
    if up.lstrip().startswith("WITH"):
        return "CTE"
    if re.search(r"\(\s*SELECT\b", up):
        return "Subqueries"
    if "DISTINCT" in up:
        return "Distinct Values"
    if "ORDER BY" in up:
        return "Sorting"
    if "WHERE" in up:
        return "Filtering"
    return "Basic Select"


def _query_topic(query, question):
    text = f"{query or ''} {question or ''}"
    if re.search(r"(?i)\bdef\b|\bimport\b|\bprint\(|\bpython\b", text):
        return "Python Coding"
    return "SQL Query"


def _query_audience(query):
    up = (query or "").upper()
    score = sum(1 for k in ("JOIN", "GROUP BY", "HAVING", "OVER", "WITH", "(SELECT") if k in up)
    if score == 0:
        return "Beginner Friendly"
    if score == 1:
        return "Interview Preparation"
    return "Data Analyst Level"


def _unique_title(parts):
    """Return a title that was not used recently; rotate the format word if needed."""
    topic, audience, skill, fmt = parts
    candidates = [fmt] + [f for f in TITLE_FORMAT_OPTIONS if f != fmt]
    for f in candidates:
        line = " | ".join([topic, audience, skill, f])
        if line not in RECENT_TITLES:
            RECENT_TITLES.append(line)
            return line
    line = " | ".join([topic, audience, skill, fmt])
    RECENT_TITLES.append(line)
    return line


def _ask_model(prompt, num_predict=300):
    """Ask the metadata models in priority order; returns the first text that comes back."""
    for model_name in METADATA_MODELS:
        try:
            options = dict(OLLAMA_OPTIONS)
            options["temperature"] = 0.8
            options["num_predict"] = num_predict
            resp = ollama.chat(model=model_name,
                               messages=[{"role": "user", "content": prompt}],
                               options=options, keep_alive=OLLAMA_KEEP_ALIVE)
            text = str(resp["message"]["content"] or "").strip()
            if text:
                return text
        except Exception as e:
            log_message(f"METADATA: {model_name} failed - {str(e)[:60]}")
    return ""


def generate_title_line(question, query_logic):
    """Topic | Audience | Skill | Format, based on the question and query."""
    question = str(question or "").strip()
    query_logic = str(query_logic or "").strip()
    prompt = (
        "You write YouTube title parts for a SQL / Python education video.\n"
        f'QUESTION: "{question}"\nQUERY / LOGIC:\n{query_logic}\n\n'
        "Return ONLY a JSON object with four keys: topic, audience, skill, format.\n"
        "- topic: 2 to 3 words naming the area (for example SQL Query or Python Coding)\n"
        "- audience: 2 to 3 words naming the learner level or purpose\n"
        "- skill: 2 to 3 words naming the exact SQL or Python concept used in THIS query\n"
        "- format: 2 to 4 words naming the question type (for example Short Word Question)\n"
        "Use English only. Do not use # or quotes inside values."
    )
    parts = None
    raw = _ask_model(prompt, 160)
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        try:
            obj = json.loads(m.group(0))
            values = [str(obj.get(k, "")).strip() for k in ("topic", "audience", "skill", "format")]
            if all(values) and all(len(v.split()) <= 4 for v in values):
                parts = values
        except Exception:
            parts = None
    if parts is None:
        idx = len(RECENT_TITLES)
        level = _query_audience(query_logic)
        audience = AUDIENCE_VARIANTS[level][idx % len(AUDIENCE_VARIANTS[level])]
        skill = _query_skill(query_logic)
        skills = SKILL_VARIANTS.get(skill, [skill])
        parts = [_query_topic(query_logic, question), audience, skills[idx % len(skills)],
                 TITLE_FORMAT_OPTIONS[(len(question) + idx) % len(TITLE_FORMAT_OPTIONS)]]
    with TITLE_LOCK:
        return _unique_title(parts)


def generate_tags(question, query_logic):
    """Plain YouTube tag names, comma separated, no # symbol."""
    question = str(question or "").strip()
    query_logic = str(query_logic or "").strip()
    prompt = (
        "Write YouTube tag names for a SQL / Python education video.\n"
        f'QUESTION: "{question}"\nQUERY / LOGIC:\n{query_logic}\n\n'
        "Return 12 to 18 tags as ONE line of plain phrases separated by commas.\n"
        "Lowercase. No # symbol. Each tag 2 to 5 words, taken from the real concept, the question and the query.\n"
        "Example: left join, sql interview questions, find unmatched rows, data analyst sql, sql null filter"
    )
    raw = _ask_model(prompt, 220)
    tags = []
    for piece in re.split(r"[,\n]", raw or ""):
        tag = re.sub(r"[#\"'*\-\d\.\)]+", " ", piece).strip().lower()
        tag = " ".join(tag.split())
        if 1 < len(tag.split()) <= 6 and tag not in tags:
            tags.append(tag)
    if len(tags) < 6:
        skill = _query_skill(query_logic).lower()
        words = [w for w in re.findall(r"[a-zA-Z]+", question.lower()) if w not in TAG_STOPWORDS]
        base = [f"sql {skill}", f"{skill} sql", "sql interview questions", "data analyst sql",
                f"sql {skill} example", "sql query tutorial", "learn sql fast", "sql practice question"]
        if words:
            base.append(" ".join(words[:4]))
        for tag in base:
            if tag not in tags:
                tags.append(tag)
    return ", ".join(tags[:18])


def generate_metadata(question: str, query_logic: str, kind: str) -> str:
    kind = (kind or "title").strip().lower()
    if kind == "title":
        return generate_title_line(question, query_logic)
    if kind in ("tags", "tag", "hashtags", "hashtag"):
        return generate_tags(question, query_logic)
    if kind in ("hashtag", "hashtags", "tags", "tag"):
        kind = "hashtags"
    elif kind in ("desc", "description"):
        kind = "description"
    else:
        kind = "title"

    prompt = build_metadata_prompt(question, query_logic, kind)
    options = dict(OLLAMA_OPTIONS)
    options["temperature"] = 0.5
    if kind == "title":
        options["num_predict"] = 120
    elif kind == "description":
        options["num_predict"] = 700
    else:
        options["num_predict"] = 180

    for model_name in METADATA_MODELS:
        try:
            log_message(f"METADATA: generating {kind} with {model_name}...")
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                options=options,
                keep_alive=OLLAMA_KEEP_ALIVE,
            )
            text = clean_metadata_text(response["message"]["content"], kind)
            if text:
                log_message(f"METADATA: {kind} ready via {model_name} ({len(text)} chars)")
                return text
        except Exception as e:
            log_message(f"METADATA: {model_name} failed - {str(e)[:60]}")

    return ""


# ============================================================
# THUMBNAIL (AI copy + premium Playwright render, 1080x1920 PNG)
# ============================================================
THUMB_SQL_KEYWORDS = (
    "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "OFFSET",
    "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "JOIN", "ON", "AS", "WITH",
    "UNION ALL", "UNION", "AND", "OR", "NOT", "IN", "IS", "NULL", "DISTINCT", "CASE",
    "WHEN", "THEN", "ELSE", "END", "OVER", "PARTITION BY", "INSERT", "INTO", "VALUES",
    "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "BY", "BETWEEN", "LIKE", "DESC", "ASC",
)
THUMB_SQL_FUNCS = (
    "SUM", "COUNT", "AVG", "MIN", "MAX", "ROW_NUMBER", "RANK", "DENSE_RANK",
    "COALESCE", "CAST", "ROUND", "NTILE", "LAG", "LEAD",
)


def highlight_sql_code(sql_text: str) -> str:
    """Escape the SQL and colour keywords / functions / numbers for the thumbnail."""
    out = _esc(sql_text)
    kw_pattern = "|".join(re.escape(k) for k in sorted(THUMB_SQL_KEYWORDS, key=len, reverse=True))
    fn_pattern = "|".join(re.escape(k) for k in sorted(THUMB_SQL_FUNCS, key=len, reverse=True))
    out = re.sub(rf"\b({kw_pattern})\b", r'<span class="k">\1</span>', out, flags=re.IGNORECASE)
    out = re.sub(rf"\b({fn_pattern})\b", r'<span class="f">\1</span>', out, flags=re.IGNORECASE)
    out = re.sub(r"\b(\d+)\b", r'<span class="n">\1</span>', out)
    return out


def headline_with_highlight(headline: str, highlight: str) -> str:
    """Colour the AI chosen keyword inside the headline."""
    text = str(headline or "").strip()
    key = str(highlight or "").strip()
    if key and key.lower() in text.lower():
        idx = text.lower().find(key.lower())
        return (f'{_esc(text[:idx])}<span class="hl">{_esc(text[idx:idx + len(key)])}</span>'
                f'{_esc(text[idx + len(key):])}')
    return _esc(text)


def build_thumbnail_prompt(question: str, query_logic: str) -> str:
    context = f'SQL QUESTION: "{question}"' if question else "SQL QUESTION: (not given)"
    if query_logic:
        context += f"\n\nSQL QUERY / LOGIC:\n{query_logic}"

    theme_list = " | ".join(ALL_THEME_KEYS)

    return ("You are a top YouTube Shorts and Instagram Reels thumbnail designer for a SQL and "
            "Data Engineering channel watched by 18-30 year olds.\n"
            "LANGUAGE RULE: English only.\n"
            "The thumbnail is VERTICAL 9:16 (1080x1920) and must be understood in ONE glance "
            "on a phone screen.\n\n"
            f"{context}\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            '  "badge": "2 to 3 word category, e.g. SQL INTERVIEW",\n'
            '  "headline": "punchy hook, max 40 characters, no full stop",\n'
            '  "highlight": "1 to 3 words copied EXACTLY from the headline that deserve colour",\n'
            '  "subheadline": "max 64 characters, one line that explains the topic",\n'
            '  "sql_snippet": "2 to 4 real lines of the query - only the key idea",\n'
            '  "bullets": ["point 1 (max 32 chars)", "point 2", "point 3"],\n'
            '  "footer": "short call to action, max 32 characters",\n'
            f'  "theme": "pick the background that fits the topic: {theme_list}"\n'
            "}")


def normalize_thumb_content(raw: dict, question: str, query_logic: str) -> dict:
    raw = raw if isinstance(raw, dict) else {}

    def pick(key, limit, fallback=""):
        value = raw.get(key)
        if isinstance(value, (list, tuple)):
            value = value[0] if value else ""
        return clamp_text(value, limit) if str(value or "").strip() else fallback

    snippet_lines = [ln.rstrip() for ln in str(raw.get("sql_snippet") or "").splitlines() if ln.strip()]
    if not snippet_lines and query_logic:
        base = format_sql(query_logic) if "SELECT" in query_logic.upper() else ""
        snippet_lines = [ln for ln in base.splitlines() if ln.strip()][:4]
    if not snippet_lines:
        snippet_lines = ["SELECT ...", "FROM your_table", "WHERE condition;"]
    snippet = "\n".join(snippet_lines[:4])

    bullets = [clamp_text(b, 32) for b in _as_str_list(raw.get("bullets")) if str(b).strip()][:3]
    if not bullets:
        bullets = ["FROM picks the table", "WHERE filters rows", "SELECT shapes output"]

    headline = pick("headline", 40, clamp_text(question, 40) or "SQL Query Explained")
    highlight = pick("highlight", 22, "")
    if highlight and highlight.lower() not in headline.lower():
        highlight = ""

    return {
        "badge": pick("badge", 24, "SQL SHORTS"),
        "headline": headline,
        "highlight": highlight,
        "subheadline": pick("subheadline", 64, "Learn the exact logic step by step"),
        "sql_snippet": snippet,
        "bullets": bullets,
        "footer": pick("footer", 32, "Full tutorial on the channel"),
        "theme": pick("theme", 24, ""),
    }


def generate_thumbnail_content(question: str, query_logic: str) -> dict:
    prompt = build_thumbnail_prompt(question, query_logic)
    options = dict(OLLAMA_OPTIONS)
    options["temperature"] = 0.6
    options["num_predict"] = 560

    for model_name in METADATA_MODELS:
        try:
            log_message(f"THUMBNAIL: writing thumbnail copy with {model_name}...")
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                format=THUMBNAIL_SCHEMA,
                options=options,
                keep_alive=OLLAMA_KEEP_ALIVE,
            )
            raw = json.loads(response["message"]["content"])
            content = normalize_thumb_content(raw, question, query_logic)
            log_message(f"THUMBNAIL: copy ready via {model_name}")
            return content
        except Exception as e:
            log_message(f"THUMBNAIL: {model_name} failed - {str(e)[:60]}")

    log_message("THUMBNAIL: using derived copy (models did not return JSON)")
    return normalize_thumb_content({}, question, query_logic)


def _headline_size(text: str) -> int:
    """Smaller font for longer headlines so every word stays fully visible."""
    n = len(str(text or ""))
    if n <= 18:
        return 104
    if n <= 26:
        return 92
    if n <= 34:
        return 80
    return 70


def build_thumbnail_html(content: dict, theme: dict, background_mode: str = "gradient") -> str:
    """Gradient mode -> mixed multi-colour background.
       Solid mode    -> ONE flat colour, no gradient, no grid, no glow, no bars."""
    th = theme
    badge = _esc(content.get("badge"))
    headline_text = content.get("headline") or ""
    headline_html = headline_with_highlight(headline_text, content.get("highlight"))
    subheadline = _esc(content.get("subheadline"))
    footer = _esc(content.get("footer"))
    sql_html = highlight_sql_code(content.get("sql_snippet") or "")
    h_size = _headline_size(headline_text)
    sub_size = 35 if len(str(content.get("subheadline") or "")) <= 44 else 30

    bullets = [str(b) for b in (content.get("bullets") or []) if str(b).strip()][:3]
    bullets_html = "".join(
        f'<div class="point"><span class="tick">&#10003;</span><span>{_esc(b)}</span></div>'
        for b in bullets
    )

    bar_heights = sorted(random.sample(range(70, 215, 5), 7))
    bars_html = "".join(f'<span style="height:{h}px"></span>' for h in bar_heights)

    bg_css = th["bg"]

    if background_mode == "solid":
        decor_html = ""
    else:
        decor_html = (
            '<div class="grid"></div>\n'
            '    <div class="glow g1"></div>\n'
            '    <div class="glow g2"></div>\n'
            '    <div class="glow g3"></div>\n'
            f'    <div class="bars">{bars_html}</div>\n'
            '    <div class="strip"></div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ width: {THUMB_WIDTH}px; height: {THUMB_HEIGHT}px; overflow: hidden; }}
    body {{
        font-family: 'Inter', 'Poppins', 'Segoe UI Variable Display', 'Segoe UI',
                     system-ui, -apple-system, Arial, sans-serif;
        color: {th['text']}; background: {bg_css};
    }}
    .bg {{ position: absolute; inset: 0; background: {bg_css}; }}
    .grid {{
        position: absolute; inset: 0; opacity: .16;
        background-image:
            linear-gradient({th['grid']} 1px, transparent 1px),
            linear-gradient(90deg, {th['grid']} 1px, transparent 1px);
        background-size: 92px 92px;
    }}
    .glow {{ position: absolute; border-radius: 50%; filter: blur(96px); }}
    .g1 {{ width: 640px; height: 640px; left: -170px; top: -140px; background: {th['glow1']}; }}
    .g2 {{ width: 560px; height: 560px; right: -190px; bottom: 300px; background: {th['glow2']}; }}
    .g3 {{ width: 420px; height: 420px; left: 220px; bottom: -140px; background: {th['glow3']}; }}
    .bars {{
        position: absolute; left: {THUMB_SAFE_LEFT}px; bottom: 235px;
        display: flex; align-items: flex-end; gap: 16px; opacity: .38;
    }}
    .bars span {{
        display: block; width: 42px; border-radius: 10px 10px 4px 4px;
        background: {th['bars']};
    }}
    .strip {{
        position: absolute; top: 0; left: 0; right: 0; height: 14px;
        background: {th['strip']};
    }}
    .safe {{
        position: absolute; z-index: 5;
        left: {THUMB_SAFE_LEFT}px;
        right: {THUMB_SAFE_RIGHT}px;
        top: {THUMB_SAFE_TOP}px;
        bottom: {THUMB_SAFE_BOTTOM}px;
        display: flex; flex-direction: column; justify-content: space-between; gap: 22px;
    }}
    .top {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; }}
    .badge {{
        font-size: 26px; font-weight: 800; letter-spacing: 3px; text-transform: uppercase;
        color: {th['pill_text']}; background: {th['pill']}; border: 3px solid {th['pill']};
        padding: 12px 26px; border-radius: 60px;
        white-space: nowrap;
    }}
    .handle {{ font-size: 24px; font-weight: 700; color: {th['muted']}; white-space: nowrap; }}
    .hero h1 {{
        font-size: {h_size}px; line-height: 1.05; font-weight: 900;
        letter-spacing: -1.8px; color: {th['text']}; word-break: break-word;
    }}
    .hl {{
        background: {th['hl']};
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .sub {{
        margin-top: 18px; font-size: {sub_size}px; line-height: 1.3;
        font-weight: 600; color: {th['muted']}; word-break: break-word;
    }}
    .sqlcard {{
        position: relative; background: {th['editor']};
        border: 3px solid {th['border']}; border-left: 14px solid {th['bar']};
        border-radius: 22px; padding: 26px 28px 28px 30px;
        box-shadow: 0 26px 60px rgba(0,0,0,.55);
    }}
    .dots {{ display: flex; gap: 10px; margin-bottom: 18px; }}
    .dots i {{ display: block; width: 16px; height: 16px; border-radius: 50%; }}
    .dots i:nth-child(1) {{ background: #8B2EFF; }}
    .dots i:nth-child(2) {{ background: #F000D0; }}
    .dots i:nth-child(3) {{ background: #FF6B9D; }}
    .sqltag {{
        position: absolute; right: 26px; top: 22px; font-size: 22px;
        font-weight: 900; letter-spacing: 3px; color: {th['bar']};
    }}
    .sql {{
        font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
        font-size: 27px; line-height: 1.5; color: #FFFFFF; white-space: pre-wrap;
    }}
    .sql .k {{ color: {th['kw']}; font-weight: 700; }}
    .sql .f {{ color: {th['fn']}; }}
    .sql .n {{ color: {th['num']}; }}
    .points {{ display: flex; flex-direction: column; gap: 14px; }}
    .point {{
        display: flex; align-items: center; gap: 14px;
        font-size: 31px; font-weight: 700; color: #FFFFFF;
        background: {th['panel']}; border: 3px solid {th['border']};
        border-radius: 16px; padding: 15px 20px;
    }}
    .tick {{ color: {th['tick']}; font-size: 30px; }}
    .cta {{ display: flex; flex-direction: column; gap: 16px; }}
    .pill {{
        align-self: flex-start; font-size: 33px; font-weight: 900; color: {th['pill_text']};
        background: {th['pill']}; padding: 18px 34px; border-radius: 60px;
        box-shadow: 0 18px 42px rgba(0,0,0,.45);
    }}
    .handle2 {{ font-size: 25px; font-weight: 700; color: {th['muted']}; }}
</style>
</head>
<body>
    <div class="bg"></div>
    {decor_html}

    <div class="safe">
        <div class="top">
            <div class="badge">{badge}</div>
            <div class="handle">@Code_With_Mangesh</div>
        </div>

        <div class="hero">
            <h1>{headline_html}</h1>
            <div class="sub">{subheadline}</div>
        </div>

        <div class="sqlcard">
            <div class="dots"><i></i><i></i><i></i></div>
            <div class="sqltag">SQL</div>
            <div class="sql">{sql_html}</div>
        </div>

        <div class="points">{bullets_html}</div>

        <div class="cta">
            <div class="pill">{footer}</div>
            <div class="handle2">YouTube / Instagram: @Code_With_Mangesh</div>
        </div>
    </div>
</body>
</html>"""


async def render_thumbnail_png(html_text: str, out_path: Path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(
            viewport={"width": THUMB_WIDTH, "height": THUMB_HEIGHT},
            device_scale_factor=1,
        )
        await page.set_content(html_text, wait_until="load")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(out_path), type="png")
        await browser.close()


THUMB_BG_STATE = {"click": 0}      # 1st click gradient, 2nd click solid, ...


def make_solid_theme(theme: dict) -> dict:
    """Same design as the gradient theme, but the background is ONE flat colour."""
    solid_theme = dict(theme)
    solid_theme["bg"] = theme["solid"]
    return solid_theme


def create_thumbnail(question: str, query_logic: str) -> dict:
    """Generate the AI copy and render a 9:16 PNG.

    Background alternates on every click:
        click 1, 3, 5 ... -> mixed / gradient multi-colour background
        click 2, 4, 6 ... -> ONE single flat colour (no gradient, no texture)
    Each click gets a theme that differs from the recent ones (ThemeSelector).
    """
    content = generate_thumbnail_content(question, query_logic)
    prefs = topic_theme_preferences(question, query_logic, str(content.get("theme") or ""))

    next_click = THUMB_BG_STATE["click"] + 1
    background_mode = "solid"

    if background_mode == "gradient":
        key = THEME_SELECTOR.choose("thumb_gradient", ALL_THEME_KEYS, prefs)
        bg_theme = THEME_BY_KEY[key]
        log_message(f"THUMBNAIL: click #{next_click} -> MIXED GRADIENT background ({bg_theme['name']})")
    else:
        key = THEME_SELECTOR.choose("thumb_solid", ALL_THEME_KEYS, prefs)
        bg_theme = make_solid_theme(THEME_BY_KEY[key])
        _bgc = next_background_color()
        bg_theme["bg"] = _bgc["solid"]
        bg_theme["solid"] = _bgc["solid"]
        log_message(f"THUMBNAIL: click #{next_click} -> SINGLE SOLID COLOUR "
                    f"{bg_theme['solid']} ({bg_theme['name']})")

    content["background_mode"] = background_mode
    content["theme_used"] = bg_theme["name"]

    html_text = build_thumbnail_html(content, bg_theme, background_mode)

    with THUMB_LOCK:
        THUMBNAIL_PATH.parent.mkdir(parents=True, exist_ok=True)
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        log_message(f"THUMBNAIL: rendering {THUMB_WIDTH}x{THUMB_HEIGHT} PNG...")
        asyncio.run(render_thumbnail_png(html_text, THUMBNAIL_PATH))

    # only a successful render advances the alternation
    THUMB_BG_STATE["click"] = next_click

    log_message(f"THUMBNAIL: PNG saved -> {THUMBNAIL_PATH}")
    return content


# ============================================================
# TABLES FOR THE ANIMATION (every table used in FROM / JOIN)
# ============================================================
# ============================================================
# TABLE REFERENCES: every table in FROM / JOIN (alias, join type, ON text)
# ============================================================
TABLE_REF_RE = re.compile(
    r"(?i)\b(FROM|(?:(?:LEFT|RIGHT|FULL)(?:\s+OUTER)?\s+|INNER\s+|CROSS\s+|NATURAL\s+)?JOIN)\s+"
    r"([A-Za-z_][\w$.]*)")
REF_STOP_WORDS = {"LEFT", "RIGHT", "FULL", "INNER", "CROSS", "NATURAL", "OUTER", "JOIN", "ON",
                  "WHERE", "GROUP", "ORDER", "HAVING", "LIMIT", "UNION", "WITH", "SELECT", "AS",
                  "AND", "OR", "WINDOW", "QUALIFY", "SET", "VALUES"}
QUAL_RE = re.compile(r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\b")
ON_END = (r"(?=\s+(?:(?:LEFT|RIGHT|FULL|INNER|CROSS|NATURAL)\b\s*(?:OUTER\s+)?)?JOIN\b"
          r"|\s+WHERE\b|\s+GROUP\s+BY\b|\s+ORDER\s+BY\b|\s+HAVING\b|\s+LIMIT\b|\s+UNION\b|;|\)|$)")


def _strip_kw(text, keyword):
    """Remove a leading keyword phrase (WHERE, GROUP BY ...) from a clause text."""
    pattern = r"(?is)^\s*" + r"\s+".join(re.escape(w) for w in keyword.split()) + r"\b\s*"
    return re.sub(pattern, "", str(text or "").strip(), count=1).strip().rstrip(";").strip()


def parse_table_refs(sql):
    """Every real table named after FROM / JOIN, in query order."""
    text = _strip_sql_comments(str(sql or ""))
    cte_names = {m.upper() for m in re.findall(r"(?i)([A-Za-z_]\w*)\s+AS\s*\(", text)}
    refs = []
    for m in TABLE_REF_RE.finditer(text):
        phrase = " ".join(m.group(1).upper().split())
        name = m.group(2)
        base = _base_name(name)
        if base in cte_names:
            continue
        rest = text[m.end():]
        am = re.match(r"\s+(?:AS\s+)?([A-Za-z_]\w*)", rest, re.I)
        alias = None
        if am and am.group(1).upper() not in REF_STOP_WORDS:
            alias = am.group(1)
        after = rest[am.end():] if alias else rest
        role = "from" if phrase == "FROM" else "join"
        if role == "from":
            join_type = "FROM"
        else:
            words = phrase.replace("JOIN", "").split()
            join_type = words[0] if words else "INNER"
        on_text = ""
        if role == "join":
            om = re.match(r"\s+ON\s+(.*?)" + ON_END, after, re.S | re.I)
            if om:
                on_text = " ".join(om.group(1).split())
        alias = alias or base
        refs.append({"name": name, "base": base, "alias": alias, "alias_key": alias.upper(),
                     "role": role, "join_type": join_type, "on": on_text})
    return refs


def alias_map_of(refs):
    """alias (upper case) -> base table name (upper case)."""
    return {r["alias_key"]: r["base"].upper() for r in refs}


def qualified_cols(text, amap):
    """'c.CUSTOMER_ID' -> 'CUSTOMERS|CUSTOMER_ID' (using the alias map)."""
    out = []
    for a, c in QUAL_RE.findall(str(text or "")):
        b = amap.get(a.upper())
        if b:
            key = f"{b}|{c.upper()}"
            if key not in out:
                out.append(key)
    return out


def join_pairs(refs, amap):
    """[(baseL, colL, baseR, colR)] from every ON condition."""
    out = []
    for r in refs:
        for a1, c1, a2, c2 in re.findall(r"(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)", r.get("on") or ""):
            b1, b2 = amap.get(a1.upper()), amap.get(a2.upper())
            if b1 and b2:
                out.append((b1, c1.upper(), b2, c2.upper()))
    return out


def _col_index(table, col):
    names = [h.upper() for h in table["headers"]]
    return names.index(col) if col in names else -1


def synthesize_table(base, cols, pairs, by_key):
    """Sample rows for a referenced table the model did not provide.
    Join-key values are copied from the partner table for SOME rows only,
    so the JOIN shows both matching and non-matching records."""
    headers = list(cols) or [f"{base}_ID"]
    source = {}
    for b1, c1, b2, c2 in pairs:
        for me, mc, other, oc in ((b1, c1, b2, c2), (b2, c2, b1, c1)):
            if me == base and other in by_key and mc in headers:
                idx = _col_index(by_key[other], oc)
                if idx >= 0:
                    source[mc] = [row[idx] for row in by_key[other]["rows"]]
    rows = []
    for i in range(6):
        row = []
        for h in headers:
            vals = source.get(h)
            if vals and i % 2 == 0 and i // 2 < len(vals):
                row.append(str(vals[i // 2]))
            elif any(w in h for w in ("AMOUNT", "BAL", "PRICE", "QTY", "SALARY", "TOTAL")):
                row.append(str(100 * (i + 3)))
            elif h.endswith("_ID") or h == "ID":
                row.append(str(900 + i) if vals else str(1000 + i + 1))
            else:
                row.append(f"{h.replace('_', ' ').title()} {i + 1}")
        rows.append(row)
    return {"name": base, "key": base.upper(), "headers": headers, "rows": rows}


def ensure_all_tables(data, sql):
    """Make sure every table in FROM / JOIN has sample data and every referenced
    column exists. Returns (synthetic_table_keys, patched_column_keys)."""
    refs = parse_table_refs(sql)
    amap = alias_map_of(refs)
    tables = data["tables"]
    by_key = {t["key"]: t for t in tables}
    used = {}
    for key in qualified_cols(sql, amap):
        b, c = key.split("|", 1)
        used.setdefault(b, [])
        if c not in used[b]:
            used[b].append(c)
    pairs = join_pairs(refs, amap)
    synthetic, patched = [], []
    for r in refs:
        b = r["base"].upper()
        if b not in by_key:
            t = synthesize_table(b, used.get(b, []), pairs, by_key)
            tables.append(t)
            by_key[b] = t
            synthetic.append(b)
            log_message(f"TABLES: {b} was not in the model output - sample rows generated")
    for t in tables:
        have = [h.upper() for h in t["headers"]]
        for c in used.get(t["key"], []):
            if c not in have:
                t["headers"].append(c)
                for i, row in enumerate(t["rows"]):
                    row.append(_extra_value(c, i))
                patched.append(f"{t['key']}.{c}")
                log_message(f"COLUMNS: added missing column {t['key']}.{c} to the sample data")
    return synthetic, patched

# ============================================================
# SQLITE SIMULATION - runs the query on the sample data (not a real database)
# ============================================================
def _sql_val(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s.upper() == "NULL":
        return None
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    return s


def _display(v):
    return "NULL" if v is None else str(v)


def _ident(name):
    return '"' + str(name).replace('"', '""') + '"'


def simulate_sql(sql, tables, refs):
    """Run the query on the sample tables with SQLite.
    Returns the final rows, the intermediate FROM/JOIN rows (before WHERE), and
    which intermediate rows survive the WHERE filter."""
    sim = {"ok": False, "error": "", "aliases": [], "final_headers": [], "final_rows": [],
           "inter_headers": [], "inter_rows": [], "inter_rids": [], "inter_pass": [],
           "final_primary_rids": [], "agg": False}
    if not refs:
        sim["error"] = "No FROM table was found in this query."
        return sim
    clean = _strip_sql_comments(str(sql or "")).strip().rstrip(";").strip()
    sim["agg"] = bool(re.search(r"(?i)\bGROUP\s+BY\b|\bHAVING\b|\b(SUM|COUNT|AVG|MIN|MAX)\s*\(|"
                                r"\bDISTINCT\b|\bUNION\b|\bWITH\b", clean))
    aliases = []
    for r in refs:
        tidx = next((i for i, t in enumerate(tables) if t["key"] == r["base"].upper()), -1)
        aliases.append({"alias": r["alias"], "key": r["alias_key"], "base": r["base"].upper(),
                        "role": r["role"], "join_type": r["join_type"], "tidx": tidx, "on": r["on"]})
    sim["aliases"] = aliases
    if any(a["tidx"] < 0 for a in aliases):
        sim["error"] = "A referenced table has no sample data."
        return sim

    sim_sql = re.sub(r"(?i)(\b(?:FROM|JOIN)\s+)([A-Za-z_][\w$.]*)",
                     lambda m: m.group(1) + _base_name(m.group(2)), clean)
    con = sqlite3.connect(":memory:")
    try:
        bases = {}
        for a in aliases:
            bases[a["base"]] = tables[a["tidx"]]
        for base, t in bases.items():
            hs = list(t["headers"])
            cols_sql = ", ".join(_ident(h) for h in hs + ["__rid"])
            con.execute(f"CREATE TABLE {_ident(base)} ({cols_sql})")
            marks = ",".join("?" * (len(hs) + 1))
            for i, row in enumerate(t["rows"]):
                vals = [_sql_val(v) for v in list(row)[:len(hs)]]
                vals += [None] * (len(hs) - len(vals))
                con.execute(f"INSERT INTO {_ident(base)} VALUES ({marks})", vals + [i + 1])

        cur = con.execute(sim_sql)
        sim["final_headers"] = [d[0] for d in cur.description]
        sim["final_rows"] = [[_display(v) for v in r] for r in cur.fetchall()]

        from_hits = _scan_keywords(sim_sql, ("FROM",))
        tail = sim_sql[from_hits[0][1]:]
        cut = _scan_keywords(tail, ("WHERE", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"))
        join_part = tail[:cut[0][1]] if cut else tail

        select_cols, names, rid_offsets, pos = [], [], [], 0
        for a in aliases:
            hs = list(tables[a["tidx"]]["headers"]) + ["__rid"]
            for h in hs:
                select_cols.append(f"{a['alias']}.{_ident(h)} AS {_ident(a['alias'] + '.' + h)}")
                names.append(f"{a['alias']}.{h}")
            rid_offsets.append(pos + len(hs) - 1)
            pos += len(hs)
        raw = con.execute("SELECT " + ", ".join(select_cols) + " " + join_part).fetchall()
        inter_rids = [[row[o] for o in rid_offsets] for row in raw]
        keep = [i for i, n in enumerate(names) if not n.endswith(".__rid")]
        sim["inter_headers"] = [names[i] for i in keep]
        sim["inter_rows"] = [[_display(row[i]) for i in keep] for row in raw]
        sim["inter_rids"] = inter_rids

        if not sim["agg"]:
            rid_sel = ", ".join(f"{a['alias']}.__rid" for a in aliases)
            pass_set = {tuple(r) for r in con.execute(f"SELECT {rid_sel} " + tail).fetchall()}
            sim["inter_pass"] = [tuple(rids) in pass_set for rids in inter_rids]
            sim["final_primary_rids"] = sorted({r[0] for r in pass_set if r[0] is not None})
        else:
            sim["inter_pass"] = [True] * len(raw)
        sim["ok"] = True
    except Exception as e:
        sim["error"] = str(e)[:220]
    finally:
        con.close()
    return sim


# ============================================================
# STEP HIGHLIGHTS (which tables / columns each SQL step touches)
# ============================================================
def annotate_steps(plan, refs):
    amap = alias_map_of(refs)
    for s in plan:
        label = s.get("label") or ""
        text = _added_text(s) or s.get("query", "")
        if label == "Final Query":
            s["hl_tables"], s["hl_cols"], s["is_match"] = [], [], False
            continue
        cols = qualified_cols(text, amap)
        if label in ("Identify Tables", "Join Data"):
            tabs = [r["base"].upper() for r in refs
                    if re.search(rf"(?i)\b{re.escape(r['base'])}\b", text)]
        else:
            tabs = sorted({c.split("|")[0] for c in cols})
        s["hl_tables"] = tabs
        s["hl_cols"] = cols
        s["is_match"] = label in ("Join Data", "Match Records")


# ============================================================
# STUDENT EXPLANATIONS - built from the actual SQL, one sentence per stage
# ============================================================
def clause_learn(label, text, refs):
    """A simple, accurate sentence explaining the clause written in this stage."""
    t = str(text or "").strip()
    flat = " ".join(t.replace(";", " ").split())
    if label == "Understand Requirement":
        return "Read the question first and decide which tables and columns are needed."
    if label == "Build CTE":
        return "WITH names a temporary result (a CTE) that the main query can read."
    if label == "Final Query":
        return "The whole query runs in this order: FROM, JOIN, ON, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT."
    if re.match(r"(?i)^SELECT\b", flat):
        body = re.sub(r"(?is)^\s*SELECT\s+(DISTINCT\s+)?", "", t).rstrip(";").strip()
        cut = _scan_keywords(body, ("FROM",))
        if cut:
            body = body[:cut[0][1]]
        cols = ", ".join(_split_top_level_commas(body)) if body.strip() else "the columns"
        return f"SELECT chooses the columns shown in the answer: {clamp_text(cols, 140)}."
    if label == "Identify Tables" or re.match(r"(?i)^FROM\b", flat):
        names = [r["base"] for r in refs if r["role"] == "from"]
        base = names[0] if names else "the table"
        return f"FROM names the starting table: {base}. Every row of {base} is checked first."
    if label == "Join Data" or re.search(r"(?i)\bJOIN\b", flat):
        m = re.search(r"(?i)((?:LEFT|RIGHT|FULL|INNER|CROSS)(?:\s+OUTER)?\s+)?JOIN\s+([A-Za-z_][\w$.]*)", flat)
        kind = (m.group(1) or "INNER").split()[0].upper() if m else "INNER"
        base = _base_name(m.group(2)) if m else "another table"
        if kind == "LEFT":
            return (f"LEFT JOIN brings in rows from {base}. Every row of the first table is kept, "
                    f"even when {base} has no match.")
        if kind == "INNER":
            return f"INNER JOIN brings in rows from {base}. Only rows with a match in both tables are kept."
        return f"{kind} JOIN brings in rows from {base} and combines them using the ON rule."
    if label == "Match Records" or re.match(r"(?i)^ON\b", flat):
        cond = _strip_kw(t, "ON")
        return (f"ON decides which rows belong together: {clamp_text(cond, 120)}. "
                "A row is linked only when these values are equal.")
    if label == "Filter Data" or re.match(r"(?i)^WHERE\b", flat):
        cond = _strip_kw(t, "WHERE")
        if re.search(r"(?i)\bIS\s+NULL\b", cond):
            return (f"WHERE {clamp_text(cond, 120)} keeps rows where the value is missing (NULL). "
                    "After a LEFT JOIN, a missing value means no matching row was found.")
        return f"WHERE {clamp_text(cond, 120)} keeps only the rows that pass this test. All other rows are removed."
    if label == "Group Data" or re.match(r"(?i)^GROUP BY\b", flat):
        return (f"GROUP BY puts rows with the same {clamp_text(_strip_kw(t, 'GROUP BY'), 100)} into one group. "
                "Each group becomes one row in the result.")
    if label == "Apply Aggregate Filter" or re.match(r"(?i)^HAVING\b", flat):
        return f"HAVING keeps only the groups that pass: {clamp_text(_strip_kw(t, 'HAVING'), 120)}."
    if re.match(r"(?i)^ORDER BY\b", flat):
        return f"ORDER BY sorts the result rows by {clamp_text(_strip_kw(t, 'ORDER BY'), 100)}."
    if re.match(r"(?i)^LIMIT\b", flat):
        return f"LIMIT shows only the first {clamp_text(_strip_kw(t, 'LIMIT'), 20)} row(s)."
    return f"This part adds: {clamp_text(flat, 120)}."


def intro_learn_lines(refs):
    """Short introduction shown while the sample tables are on screen."""
    lines = []
    if not refs:
        return lines
    lines.append("The question needs data from: " + ", ".join(r["base"] for r in refs) + ".")
    for r in refs:
        if r["role"] == "join":
            lines.append(f"{r['base']} is linked to the first table by: "
                         f"{clamp_text(r['on'] or 'the join condition', 110)}.")
    return lines


def result_learn_lines(refs, sql, sim, data):
    """Why the final rows appear, in plain words."""
    if not sim.get("ok"):
        return ["The simulation could not run this query, so the expected output from the model is shown."]
    pieces = slice_sql_pieces(sql or "")
    where = _strip_kw(pieces["where"], "WHERE") if pieces["where"].strip() else ""
    total = len(sim.get("inter_rows", []))
    kept = sum(1 for x in sim.get("inter_pass", []) if x)
    lines = []
    if where:
        lines.append(f"After FROM and JOIN there are {total} row(s). WHERE {clamp_text(where, 100)} keeps {kept} of them.")
    else:
        lines.append(f"After FROM and JOIN there are {total} row(s). No WHERE filter is used, so all of them are kept.")
    if re.search(r"(?i)\bIS\s+NULL\b", where):
        lines.append("IS NULL keeps only the rows where the joined table had no match. Those are the answer rows.")
    if sim.get("final_rows"):
        lines.append("The final output shows only the selected columns: " + ", ".join(sim.get("final_headers", [])) + ".")
    else:
        lines.append("No row passes the condition for this sample data, so the output is empty.")
    return lines



# ============================================================
# VALIDATION - sample data, join keys and output must agree with the SQL
# ============================================================
def validate_learning_data(refs, sql, data, sim):
    """Returns a list of warnings (empty when everything is consistent)."""
    warnings = []
    amap = alias_map_of(refs)
    tables = {t["key"]: t for t in data.get("tables", [])}
    for r in refs[1:]:
        for bl, cl, br, cr in join_pairs([r], amap):
            lt, rt = tables.get(bl), tables.get(br)
            if not lt or not rt:
                warnings.append(f"a table used by the JOIN has no sample data: {bl} or {br}")
                continue
            li, ri = _col_index(lt, cl), _col_index(rt, cr)
            if li < 0 or ri < 0:
                warnings.append(f"a join column is missing: {bl}.{cl} or {br}.{cr}")
                continue
            lvals = {row[li] for row in lt["rows"]}
            rvals = {row[ri] for row in rt["rows"]}
            if not (lvals & rvals):
                warnings.append(f"no key values match between {bl}.{cl} and {br}.{cr}; "
                                "the JOIN links no rows, so the sample data does not show the idea")
    if sim.get("ok"):
        if not sim.get("final_rows"):
            warnings.append("the final output is empty for this sample data; the sample rows should "
                            "show at least one row that satisfies the question")
    else:
        warnings.append("the SQL simulation did not run: " + (sim.get("error") or "unknown error"))
    return warnings


# ============================================================
# TABLE SHAPE - every table has at least 4 columns and 5 rows (readable on a phone)
# ============================================================
MIN_TABLE_COLS = 4
MIN_TABLE_ROWS = 5
EXTRA_COLUMNS_BY_NAME = [
    ("CUSTOMER", ["CITY", "EMAIL"]),
    ("TRANSACTION", ["TXN_DATE", "STATUS"]),
    ("ACCOUNT", ["ACCOUNT_TYPE", "BRANCH"]),
    ("ORDER", ["ORDER_DATE", "STATUS"]),
    ("PRODUCT", ["CATEGORY", "PRICE"]),
    ("EMPLOYEE", ["DEPARTMENT", "SALARY"]),
]


def _extra_value(column, i):
    c = column.upper()
    if c == "CITY":
        return ["Pune", "Mumbai", "Nagpur", "Delhi", "Pune"][i % 5]
    if c == "EMAIL":
        return f"user{i + 1}@example.com"
    if c in ("TXN_DATE", "ORDER_DATE"):
        return f"2024-03-{(i % 28) + 1:02d}"
    if c == "STATUS":
        return ["Completed", "Pending", "Completed", "Failed", "Completed"][i % 5]
    if c == "ACCOUNT_TYPE":
        return ["Savings", "Current", "Savings", "Savings", "Current"][i % 5]
    if c == "BRANCH":
        return ["Pune Main", "Mumbai West", "Nagpur East", "Delhi Central", "Pune Main"][i % 5]
    if c == "CATEGORY":
        return ["Electronics", "Grocery", "Clothing", "Electronics", "Books"][i % 5]
    if c == "PRICE":
        return str(250 + 75 * i)
    if c == "DEPARTMENT":
        return ["Sales", "Finance", "IT", "Sales", "HR"][i % 5]
    if c == "SALARY":
        return str(45000 + 2500 * i)
    return f"Value {i + 1}"


def _extra_columns_for(key):
    for part, cols in EXTRA_COLUMNS_BY_NAME:
        if part in key:
            return cols
    return ["STATUS", "CREATED_DATE"]


def enforce_table_shape(data, sql):
    """Adds columns and rows when a table is too small. Added rows get NEW join-key values
    that match no row of the other tables, so the join results (and the answer) do not change."""
    refs = parse_table_refs(sql)
    amap = alias_map_of(refs)
    key_cols = {}
    for bl, cl, br, cr in join_pairs(refs, amap):
        key_cols.setdefault(bl, set()).add(cl)
        key_cols.setdefault(br, set()).add(cr)
    notes = []
    serial = 0
    for t in data.get("tables", []):
        existing = [h.upper() for h in t["headers"]]
        extras = [c for c in _extra_columns_for(t["key"]) if c not in existing]
        n = 0
        while len(t["headers"]) < MIN_TABLE_COLS:
            name = extras[n] if n < len(extras) else f"DETAIL_{n + 1}"
            n += 1
            if name in [h.upper() for h in t["headers"]]:
                continue
            t["headers"].append(name)
            for i, row in enumerate(t["rows"]):
                row.append(_extra_value(name, i))
            notes.append(f"{t['key']}: added column {name}")
        if not t["rows"]:
            t["rows"] = [[str(i + 1) if ci == 0 else _extra_value(h, i)
                          for ci, h in enumerate(t["headers"])] for i in range(MIN_TABLE_ROWS)]
            notes.append(f"{t['key']}: sample rows created")
        src_rows = [list(r) for r in t["rows"]]
        src_count = len(src_rows)
        keys = key_cols.get(t["key"], set())
        added = 0
        k = 0
        while len(t["rows"]) < MIN_TABLE_ROWS:
            row = list(src_rows[k % src_count])
            for ci, h in enumerate(t["headers"]):
                if ci == 0 or h.upper() in keys:
                    serial += 1
                    old = str(row[ci])
                    row[ci] = str(9000 + serial) if re.fullmatch(r"-?\d+", old) else f"NEW-{serial}"
            t["rows"].append(row)
            k += 1
            added += 1
        if added:
            notes.append(f"{t['key']}: sample rows raised to {MIN_TABLE_ROWS} (new key values, no new matches)")
    return notes


def _tables_for_animation(data, final_sql):
    """Every table the model returned, with the main FROM table first.
    Rows are used exactly as given so the SQL simulation matches what is shown."""
    tables = []
    for t in (data.get("tables") or []):
        tables.append({"name": t["name"], "key": _base_name(t["name"]),
                       "headers": list(t["headers"]), "rows": [list(r) for r in t["rows"]]})
    if not tables and data.get("sample_data"):
        rows = [list(r.get("cols") or []) for r in data["sample_data"]]
        headers = list(data.get("table_headers") or [])
        width = max([len(headers)] + [len(r) for r in rows] + [1])
        headers = headers + [f"COL_{i + 1}" for i in range(len(headers), width)]
        rows = [_as_str_list(r, pad_to=width)[:width] for r in rows]
        name = data.get("table_name") or "TABLE"
        tables.append({"name": name, "key": _base_name(name), "headers": headers, "rows": rows})
    primary = extract_primary_table(final_sql or "")
    if primary:
        for idx, t in enumerate(tables):
            if t["key"] == _base_name(primary):
                tables.insert(0, tables.pop(idx))
                break
    return tables


def finalize_for_animation(data, user_sql=""):
    """Format the SQL, collect every referenced table, build the typing steps (Step 5)
    and run the query on the sample data (Step 6)."""
    steps = data.get("steps") or []
    for s in steps:
        s["query"] = format_sql(s.get("query") or "")

    final_sql = format_sql(user_sql) if user_sql else ""
    if not final_sql:
        for s in reversed(steps):
            if s.get("query", "").strip():
                final_sql = s["query"]
                break

    # 1) every table in FROM / JOIN gets sample data
    data["tables"] = _tables_for_animation(data, final_sql)
    synthetic, patched = ensure_all_tables(data, final_sql)
    for _n in enforce_table_shape(data, final_sql):
        log_message("TABLE SHAPE: " + _n)
    tables = data["tables"]
    for t in tables:
        t["synthetic"] = t["key"] in synthetic
    if tables:
        data["table_name"] = tables[0]["name"]
        data["table_headers"] = tables[0]["headers"]
        data["sample_data"] = [{"id": f"row{i + 1}", "cols": r} for i, r in enumerate(tables[0]["rows"])]
    else:
        data["sample_data"] = pad_sample_data(data.get("sample_data") or [], MIN_SAMPLE_ROWS)

    # 2) result column names (used only if the simulation is unavailable)
    result_names = output_column_names(final_sql, data.get("table_headers") or [])
    cleaned = [list(r) for r in (data.get("cleaned_output") or [])]
    width = max([len(result_names)] + [len(r) for r in cleaned] + [1])
    result_names = result_names + [f"COL_{i + 1}" for i in range(len(result_names), width)]
    data["result_headers"] = result_names
    data["cleaned_output"] = [_as_str_list(r, pad_to=width)[:width] for r in cleaned]

    # 3) the logical SQL build, step by step (Step 5 typing animation)
    items = build_logical_items(final_sql, data) if final_sql else []
    if items:
        model_bubbles = [_as_str_list(s.get("bubble"), pad_to=3)[:3] for s in steps]
        model_expl = [str(s.get("explanation") or "") for s in steps]
        if model_bubbles:
            items[0]["bubble"] = model_bubbles[0] or items[0]["bubble"]
            if len(model_bubbles[-1]) and any(model_bubbles[-1]):
                items[-1]["bubble"] = model_bubbles[-1]
        if len(model_expl) == len(items):
            for i, text in enumerate(model_expl):
                if text:
                    items[i]["explanation"] = clamp_text(text, 110)
        plan = build_plan_from_items(items)
    else:
        log_message("PLANNER: clause split not possible - using the progressive build")
        states = build_plan_states(final_sql, len(steps) if steps else 3) if final_sql else [""]
        labels = []
        for i, st in enumerate(states):
            prev = states[i - 1] if i else ""
            if i == 0:
                pseudo = {"mode": "start", "typed": st, "query": st}
            elif prev and prev in st and st.find(prev) > 0:
                pseudo = {"mode": "wrap", "typed": "", "query": st}
            else:
                pseudo = {"mode": "append", "typed": st[len(prev):], "query": st}
            labels.append(label_for_step(pseudo, i, len(states), final_sql))
        plan = build_plan_from_items([
            {
                "sql": st,
                "label": labels[i],
                "bubble": (_as_str_list(steps[i].get("bubble"), pad_to=3)[:3]
                           if i < len(steps) and any(_as_str_list(steps[i].get("bubble")))
                           else CLAUSE_BUBBLES.get(labels[i], ["What: Next clause",
                                                               "Why: Build the logic",
                                                               "Result: Query grows"])),
                "explanation": (str(steps[i].get("explanation") or "") if i < len(steps) else ""),
                "rows": None,
                "dim": False,
            }
            for i, st in enumerate(states)
        ])

    labels = [str(p.get("label") or "Transform Data") for p in plan]
    data["chips"] = labels
    data["steps"] = plan

    # 4) which tables and columns each typed line touches, and the SQLite run (Step 6)
    refs = parse_table_refs(final_sql)
    annotate_steps(plan, refs)
    for _s in plan:
        _s["learn"] = clause_learn(_s.get("label") or "", _added_text(_s) or _s.get("query", ""), refs)
    sim = simulate_sql(final_sql, data["tables"], refs)
    data["sim"] = sim
    data["result_learn"] = result_learn_lines(refs, final_sql, sim, data)
    for _w in validate_learning_data(refs, final_sql, data, sim):
        log_message("CHECK: " + _w)
    data["intro_learn"] = intro_learn_lines(refs)
    if sim.get("ok"):
        data["result_headers"] = sim["final_headers"]
        data["cleaned_output"] = sim["final_rows"]
        shown = " | ".join(" , ".join(r) for r in sim["final_rows"][:5])
        data["result_explain"] = f"Result rows: {shown}" if shown else "No row satisfies the conditions."
    else:
        data["result_explain"] = ""
        log_message(f"SIMULATION: {sim.get('error') or 'not available'}")
    data["synthetic_tables"] = synthetic
    data["patched_cols"] = patched
    data["reel_theme"] = choose_reel_theme(str(data.get("question_banner") or ""), final_sql)

    LAST_RUN["question"] = str(data.get("question_banner") or "")
    LAST_RUN["final_query"] = final_sql
    LAST_RUN["logic_explanation"] = str(data.get("logic_explanation") or "")
    LAST_RUN["process_summary"] = data.get("process_summary") or []

    log_message(f"TABLES: {', '.join(t['name'] for t in tables) or 'none'}")
    log_message(f"SIMULATION: {'ok' if sim.get('ok') else 'unavailable'} | final rows={len(sim.get('final_rows', []))}")
    log_message(f"STEP LABELS: {' -> '.join(labels)}")
    return data



# ============================================================
# GENERATION (sequential models, priority order - never hangs)
# ============================================================
def fallback_from_user_sql(question: str, user_sql: str) -> dict:
    log_message("FALLBACK: all models failed - building the animation from your SQL only")
    return {
        "question_banner": question or "SQL Query",
        "table_name": extract_primary_table(user_sql) or "TABLE",
        "logic_explanation": "Your SQL is explained part by part",
        "process_summary": [
            "The FROM clause picks the table",
            "WHERE and GROUP BY shape the rows",
            "SELECT chooses the final columns",
        ],
        "sample_data": [
            {"id": "row1", "cols": ["ACC_001", "50000"]},
            {"id": "row2", "cols": ["ACC_001", "25000"]},
            {"id": "row3", "cols": ["ACC_002", "10000"]},
            {"id": "row4", "cols": ["ACC_002", "32000"]},
            {"id": "row5", "cols": ["ACC_003", "18000"]},
            {"id": "row6", "cols": ["ACC_003", "27000"]},
        ],
        "table_headers": ["ACCOUNT_ID", "AMOUNT"],
        "chips": ["Identify Tables", "Filter Data", "Select Data", "Final Query"],
        "steps": [
            {"type": "query", "query": user_sql,
             "explanation": "Build the query clause by clause",
             "bubble": ["What: Logical build", "Why: FROM first", "Result: Query ready"]},
        ],
        "cleaned_output": [["ACC_001", "75000"], ["ACC_002", "42000"]],
        "tables": [],
    }


def fallback_builtin(question: str) -> dict:
    log_message("WARNING: all models failed - using the built-in fallback video")
    query = ("SELECT\n    EMP_ID,\n    NAME,\n    SALARY\nFROM EMPLOYEE\nWHERE SALARY > 70000\n"
             "ORDER BY SALARY DESC;")
    return {
        "question_banner": question or "SQL Query",
        "table_name": "EMPLOYEE",
        "logic_explanation": "Pick the table, filter the rows, then choose the columns",
        "process_summary": [
            "FROM decides which table is read",
            "WHERE keeps only matching rows",
            "SELECT shapes the final output",
        ],
        "sample_data": [
            {"id": "row1", "cols": ["E001", "Raj Kumar", "95000"]},
            {"id": "row2", "cols": ["E002", "Priya Sharma", "85000"]},
            {"id": "row3", "cols": ["E003", "Amit Singh", "75000"]},
            {"id": "row4", "cols": ["E004", "Neha Patel", "85000"]},
            {"id": "row5", "cols": ["E005", "Vikram Rao", "68000"]},
            {"id": "row6", "cols": ["E006", "Sneha Joshi", "72000"]},
        ],
        "table_headers": ["EMP_ID", "NAME", "SALARY"],
        "chips": ["Identify Tables", "Filter Data", "Select Data", "Sort Results", "Final Query"],
        "steps": [
            {"type": "query", "query": query,
             "explanation": "Read the table, filter the rows, project the columns, sort",
             "bubble": ["What: Simple SELECT", "Why: Filter first", "Result: Sorted rows"]},
        ],
        "cleaned_output": [
            ["E001", "Raj Kumar", "95000"],
            ["E002", "Priya Sharma", "85000"],
        ],
        "tables": [],
    }


def generate_animation_data(question: str, query_logic: str = "") -> dict:
    user_sql, user_logic = split_query_logic(query_logic)
    if user_sql:
        log_message(f"SQL found in the Query box ({len(user_sql)} chars) - it is authoritative")
    elif user_logic:
        log_message(f"Logic found in the Query box ({len(user_logic)} chars) - follow it exactly")

    log_message("LEARNING STEP: loading memory...")
    learned = load_learning_store()
    usable = [ex for ex in learned if ex.get("steps")]
    if usable:
        log_message(f"Learning memory: {len(usable)} example(s), injecting "
                    f"{min(MAX_FEWSHOT_EXAMPLES, len(usable))}")
    else:
        log_message("Learning memory is empty - generating fresh")

    few_shot_block = build_few_shot_block(usable)
    last_error = "unknown"

    # ============ OUTER LOOP : MODEL (one at a time, priority order) ============
    for model_index, model_name in enumerate(MODELS_TO_TRY, start=1):
        error_feedback = ""

        # ============ INNER LOOP : ATTEMPTS ============
        for attempt in range(1, MAX_ATTEMPTS_PER_MODEL + 1):
            try:
                log_message(f"MODEL {model_index}/{len(MODELS_TO_TRY)}: {model_name} "
                            f"(attempt {attempt}/{MAX_ATTEMPTS_PER_MODEL})...")
                prompt = build_prompt(question, few_shot_block, error_feedback,
                                      user_sql, user_logic)
                response, mode = call_ollama_model(model_name, prompt)

                raw_text = response["message"]["content"].strip()
                log_message(f"Response received ({mode})")

                parsed_data = validate_json_response(raw_text, question)
                log_message(f"SUCCESS: {model_name} | steps={len(parsed_data['steps'])} "
                            f"| rows={len(parsed_data['sample_data'])} "
                            f"| tables={len(parsed_data['tables'])}")

                save_learning_example(question, parsed_data, model_name)
                parsed_data["process_summary"] = derive_process_summary(parsed_data)
                return finalize_for_animation(parsed_data, user_sql)

            except Exception as e:
                last_error = str(e)
                error_feedback = build_error_feedback_block(model_name, attempt, last_error)
                log_message(f"FAILED: {model_name} - {last_error[:70]}")

        log_message(f"Switching to the next model after {model_name} failed")

    log_message(f"All models failed (last error: {last_error[:70]})")
    data = fallback_from_user_sql(question, user_sql) if user_sql else fallback_builtin(question)
    data["process_summary"] = derive_process_summary(data)
    return finalize_for_animation(data, user_sql)


# ============================================================
# LEARNING ANIMATION PAGE - 9:16 Shorts / Reels, one colour system (see PALETTE)
# Order: watermark (top-left) -> question -> sample tables -> stage buttons
#        -> SQL query (typed) -> comments -> explanation -> final output
# Colours: #170D2E #0B1020 (backgrounds), #21143D (panels), #8B2EFF (neon purple),
#          #F000D0 (magenta), #FF6B9D (pink), #FFD900 (yellow badges and highlights),
#          #1677FF (electric blue, status), #FF8A00 (orange, status), #FFFFFF, #D5CEE8
# ============================================================
LEARN_TEMPLATE_HEAD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SQL Learning Animation</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 100vw; height: 100vh; background: #0B1020; display: flex; justify-content: center; align-items: center; overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; }
#stage { width: 1080px; height: 1920px; position: relative; overflow: hidden; background: var(--bg); color: #FFFFFF; transform-origin: center center; }

/* gradient for important headings, keywords and active elements only */
.gtext { background: linear-gradient(90deg, #8B2EFF 0%, #F000D0 55%, #FF6B9D 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }
.badge { display: inline-block; background: #FFD900; color: #170D2E; font-weight: 800; border-radius: 30px; padding: 3px 14px; font-size: 18px; letter-spacing: .5px; }

/* watermark: top-left corner, always visible */
#wm { position: absolute; z-index: 20; top: 52px; left: 60px; font-size: 26px; font-weight: 700; color: #FFFFFF; text-shadow: 0 0 10px rgba(139,46,255,.55); white-space: nowrap; }

/* content column: starts below the watermark, ends above the bottom platform band */
#content { position: absolute; z-index: 5; top: 118px; left: 56px; right: 56px; bottom: 236px; display: flex; flex-direction: column; }

#question { margin-top: 22px; background: #21143D; border: 1px solid #8B2EFF; border-radius: 14px; padding: 14px 20px; font-size: 31px; font-weight: 700; line-height: 1.32; color: #FFFFFF; box-shadow: 0 0 18px rgba(139,46,255,.25), 0 8px 20px rgba(0,0,0,.35); }

/* sample tables: every table used in the query, side by side */
#tables { margin-top: 18px; display: flex; gap: 14px; align-items: flex-start; }
.tpanel { flex: 1 1 0; min-width: 0; background: #21143D; border: 1px solid rgba(139,46,255,.55); border-radius: 12px; padding: 8px 12px; }
.tpanel.tactive { border-color: #F000D0; box-shadow: 0 0 12px rgba(240,0,208,.28); }
.tname { font-size: 23px; font-weight: 700; margin-bottom: 6px; }
table { width: 100%; border-collapse: collapse; font-size: 21px; color: #FFFFFF; }
th, td { padding: 5px 8px; text-align: left; border-bottom: 1px solid rgba(139,46,255,.35); white-space: nowrap; }
th { color: #D5CEE8; font-weight: 700; }
th.chl { background: #8B2EFF; color: #FFFFFF; }
td.note-cell { color: #1677FF; font-weight: 700; font-size: 18px; }
tr.jmatch td { background: rgba(22,119,255,.24); }
tr.jnomatch td { color: rgba(213,206,232,.6); }
tr.dimrow td { color: rgba(213,206,232,.45); }
tr.kept td { background: rgba(139,46,255,.34); color: #FFFFFF; }
tr.removed td { background: rgba(255,138,0,.16); color: rgba(213,206,232,.8); text-decoration: line-through; }

/* stage buttons: the current stage is highlighted automatically */
#chips { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 10px; }
.chip { font-size: 21px; font-weight: 600; padding: 8px 16px; border-radius: 40px; border: 1px solid rgba(139,46,255,.6); background: #21143D; color: #D5CEE8; cursor: pointer; transition: all .3s; }
.chip.done { border-color: #F000D0; color: #FFFFFF; }
.chip.active { background: linear-gradient(90deg, #8B2EFF 0%, #F000D0 55%, #FF6B9D 100%); border-color: transparent; color: #FFFFFF; box-shadow: 0 0 14px rgba(240,0,208,.35); }

/* SQL query: fixed code font, typed line by line, caret stays at the next character */
#editor { margin-top: 16px; background: #0B1020; border: 1px solid rgba(139,46,255,.6); border-radius: 14px; }
.ehead { padding: 6px 16px; font-size: 18px; font-weight: 700; letter-spacing: .5px; border-bottom: 1px solid rgba(139,46,255,.35); }
#escroll { max-height: 360px; overflow: hidden; padding: 10px 16px; font-family: 'Consolas', 'Courier New', monospace; font-size: 26px; line-height: 1.5; color: #FFFFFF; white-space: pre-wrap; tab-size: 4; }
.cl { border-left: 4px solid transparent; padding-left: 10px; margin-left: -14px; min-height: 1.5em; }
.cl.active { background: #21143D; border-left-color: #8B2EFF; }
.kw { font-weight: 700; background: linear-gradient(90deg, #8B2EFF 0%, #F000D0 55%, #FF6B9D 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }
.str { color: #D5CEE8; }
.num { color: #FF8A00; }
.cursor { display: inline-block; width: 3px; height: 1.05em; margin-left: 1px; background: #F000D0; vertical-align: text-bottom; animation: blink 1s step-end infinite; }

/* comments: directly below the query */
#comments { margin-top: 12px; background: #21143D; color: #FFFFFF; border: 1px solid rgba(139,46,255,.6); border-left: 6px solid #8B2EFF; border-radius: 12px; padding: 10px 18px; font-size: 23px; font-weight: 600; min-height: 118px; }
.cline { min-height: 1.3em; margin: 3px 0; opacity: 0; transition: opacity .3s; }
.cline.show { opacity: 1; }

/* explanation: student-friendly, synchronized with the active stage */
#explain { margin-top: 12px; background: #21143D; border: 1px solid rgba(139,46,255,.6); border-radius: 12px; padding: 10px 18px; font-size: 23px; line-height: 1.45; color: #FFFFFF; min-height: 150px; }
#explain .eh { font-size: 18px; font-weight: 700; letter-spacing: .5px; margin-bottom: 4px; background: linear-gradient(90deg, #8B2EFF 0%, #F000D0 55%, #FF6B9D 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }
#explain .eline { margin: 4px 0; opacity: 0; transition: opacity .35s; }
#explain .eline.show { opacity: 1; }

/* final output: shown after the query has been typed (replaces the editor) */
#result { margin-top: 12px; display: none; flex-direction: column; min-height: 0; }
.rlabel { margin-top: 8px; font-size: 19px; font-weight: 700; letter-spacing: .5px; }
.rbox { margin-top: 6px; background: #21143D; border: 1px solid rgba(139,46,255,.6); border-radius: 12px; padding: 6px 10px; overflow: auto; }
#inter { max-height: 250px; }
#inter table { font-size: 18px; table-layout: fixed; width: 100%; }
#inter th, #inter td { white-space: normal; overflow-wrap: anywhere; padding: 4px 6px; vertical-align: top; }
#final { max-height: 300px; }
.final table { font-size: 22px; table-layout: fixed; width: 100%; }
.final th, .final td { white-space: normal; word-break: break-word; overflow-wrap: anywhere; padding: 6px; vertical-align: top; }
.final th { color: #FFD900; }
.empty-row td { color: #D5CEE8; font-style: italic; }

#end-card { position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; background: var(--bg); z-index: 2000; display: flex; flex-direction: column; justify-content: center; align-items: center; opacity: 0; pointer-events: none; transition: opacity 1.8s ease-in-out; }
#end-card h1 { font-size: 70px; margin-bottom: 30px; text-align: center; }
#end-card p { font-size: 46px; margin: 20px 0; text-align: center; color: #FFFFFF; }
@keyframes blink { 50% { opacity: 0; } }
/* tables: 1-2 side by side, 3 or more wrap into a grid; every column and value stays inside its box */
#tables { flex-wrap: wrap; gap: 10px; }
#tables .tpanel { flex: 1 1 calc(50% - 10px); min-width: 0; overflow: hidden; padding: 6px 8px; }
#tables table { table-layout: fixed; width: 100%; }
#tables th, #tables td { white-space: normal; overflow-wrap: anywhere; word-break: break-word; padding: 4px 5px; }
#tables.tables-few table { font-size: 19px; }
#tables.tables-s table { font-size: 16px; }
#tables.tables-s .tname { font-size: 18px; }
#tables.tables-xs table { font-size: 14px; }
#tables.tables-xs .tname { font-size: 16px; }
#tables.tables-xs .tpanel { flex: 1 1 calc(33.3% - 10px); }
</style>
</head>
<body>
<div id="stage">
  <div id="wm">@Code_With_Mangesh</div>
  <div id="content">
    <div id="question"></div>
    <div id="tables"></div>
    <div id="chips"></div>
    <div id="editor">
      <div class="ehead"><span class="gtext">SQL QUERY</span></div>
      <div id="escroll"><span id="code"></span></div>
    </div>
    <div id="comments"></div>
    <div id="explain"></div>
    <div id="result">
      <div class="rlabel gtext">ROWS AFTER FROM AND JOIN (purple = kept by WHERE)</div>
      <div class="rbox" id="inter"></div>
      <div class="rlabel"><span class="badge">FINAL OUTPUT</span></div>
      <div class="rbox final" id="final"></div>
    </div>
  </div>
  <div id="end-card">
    <h1 class="gtext">Got it? 🤔</h1>
    <p>Comment your answer!</p>
    <p>Share &amp; Like</p>
    <br><br><p style="color: #FFD900; font-weight: bold; font-size: 56px;">@Code_With_Mangesh</p>
    <p>Daily SQL &amp; Data Engineering 🚀</p>
  </div>
</div>
"""

LEARN_TEMPLATE_JS = r"""
<script>
const P = __PAYLOAD__;
const SIM = P.sim || {ok: false};
const $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const TYPING_SPEED = 50;
const VIS = {};
let currentCode = '', activeFrom = 0, activeTo = 0;

function resetVis() {
  VIS.tables = new Set(); VIS.cols = new Set(); VIS.rowKeep = null; VIS.rowMark = {}; VIS.note = {};
}
resetVis();

function resizeStage() {
  const s = Math.min(window.innerWidth / 1080, window.innerHeight / 1920);
  $('stage').style.transform = 'scale(' + s + ')';
}

async function wait(ms) {
  let left = ms;
  while (left > 0) {
    const s = Math.min(60, left);
    await sleep(s);
    left -= s;
  }
}

function idxOfKey(k) { return P.tables.findIndex(t => t.key === String(k).toUpperCase()); }

// ---------- sample tables: every table used in the query ----------
function renderTables() {
  const host = $('tables');
  const nTables = P.tables.length;
  host.className = nTables >= 5 ? 'tables-xs' : (nTables >= 3 ? 'tables-s' : 'tables-few');
  host.innerHTML = '';
  P.tables.forEach((t, ti) => {
    const panel = document.createElement('div');
    panel.className = 'tpanel' + (VIS.tables.has(ti) ? ' tactive' : '');
    const title = document.createElement('div');
    title.className = 'tname';
    title.textContent = t.name + (t.synthetic ? ' *' : '');
    panel.appendChild(title);
    const tbl = document.createElement('table');
    const hr = document.createElement('tr');
    const hasNotes = !!(VIS.note[ti] && Object.keys(VIS.note[ti]).length);
    t.headers.forEach(h => {
      const th = document.createElement('th');
      th.textContent = h;
      if (VIS.cols.has(t.key + '|' + h.toUpperCase())) th.classList.add('chl');
      hr.appendChild(th);
    });
    if (hasNotes) { const th = document.createElement('th'); th.textContent = 'Match'; hr.appendChild(th); }
    tbl.appendChild(hr);
    t.rows.forEach((r, ri) => {
      const tr = document.createElement('tr');
      const cls = [];
      if (VIS.rowKeep && VIS.rowKeep[ti] && !VIS.rowKeep[ti].has(ri)) cls.push('dimrow');
      const mk = VIS.rowMark[ti] && VIS.rowMark[ti][ri];
      if (mk) cls.push(mk);
      tr.className = cls.join(' ');
      r.forEach(v => { const td = document.createElement('td'); td.textContent = v; tr.appendChild(td); });
      if (hasNotes) {
        const td = document.createElement('td');
        td.className = 'note-cell';
        td.textContent = (VIS.note[ti] && VIS.note[ti][ri]) || '';
        tr.appendChild(td);
      }
      tbl.appendChild(tr);
    });
    panel.appendChild(tbl);
    host.appendChild(panel);
  });
}

function buildResultTable(headers, rows, emptyText) {
  const tbl = document.createElement('table');
  const hr = document.createElement('tr');
  headers.forEach(h => { const th = document.createElement('th'); th.textContent = h; hr.appendChild(th); });
  tbl.appendChild(hr);
  if (!rows.length && emptyText) {
    const tr = document.createElement('tr');
    tr.className = 'empty-row';
    const td = document.createElement('td');
    td.colSpan = Math.max(headers.length, 1);
    td.textContent = emptyText;
    tr.appendChild(td);
    tbl.appendChild(tr);
  }
  rows.forEach(r => {
    const tr = document.createElement('tr');
    r.forEach(v => { const td = document.createElement('td'); td.textContent = v; tr.appendChild(td); });
    tbl.appendChild(tr);
  });
  return tbl;
}

// ---------- matches taken from the simulated FROM + JOIN rows ----------
function computeMatches() {
  if (!SIM.ok || !SIM.aliases || SIM.aliases.length < 2) return null;
  const L = SIM.aliases[0], R = SIM.aliases[1];
  if (L.tidx < 0 || R.tidx < 0) return null;
  const leftMatches = {};
  SIM.inter_rids.forEach(r => {
    const l = r[0], rr = r[1];
    if (l === null || l === undefined) return;
    if (!leftMatches[l]) leftMatches[l] = [];
    if (rr !== null && rr !== undefined && !leftMatches[l].includes(rr)) leftMatches[l].push(rr);
  });
  return {leftIdx: L.tidx, rightIdx: R.tidx, leftMatches: leftMatches};
}

// ---------- stage buttons: the current stage is highlighted automatically ----------
function buildChips() {
  const host = $('chips');
  host.innerHTML = '';
  P.steps.forEach((s, i) => {
    const d = document.createElement('div');
    d.className = 'chip';
    d.id = 'chip' + i;
    d.textContent = s.label;
    d.onclick = () => { setComments(s.bubble); setExplain(s.learn ? [s.learn] : []); };
    host.appendChild(d);
  });
}

function markChips(current) {
  P.steps.forEach((s, i) => {
    const d = $('chip' + i);
    if (!d) return;
    d.classList.remove('active', 'done');
    if (i < current) d.classList.add('done');
    else if (i === current) d.classList.add('active');
  });
}

// ---------- comments below the query ----------
function setComments(lines) {
  const box = $('comments');
  box.innerHTML = '';
  (lines || []).forEach(t => {
    if (!t) return;
    const d = document.createElement('div');
    d.className = 'cline show';
    d.textContent = t;
    box.appendChild(d);
  });
}

async function revealComments(lines) {
  const box = $('comments');
  box.innerHTML = '';
  (lines || []).filter(t => t).forEach(t => {
    const d = document.createElement('div');
    d.className = 'cline';
    d.textContent = t;
    box.appendChild(d);
  });
  for (const d of Array.from(box.children)) {
    await wait(380);
    d.classList.add('show');
  }
  await wait(600);
}

// ---------- explanation: a student-friendly sentence for every stage ----------
function setExplain(lines) {
  const box = $('explain');
  box.innerHTML = '';
  const head = document.createElement('div');
  head.className = 'eh';
  head.textContent = 'WHAT THIS PART DOES';
  box.appendChild(head);
  (lines || []).filter(t => t).forEach(t => {
    const d = document.createElement('div');
    d.className = 'eline show';
    d.textContent = t;
    box.appendChild(d);
  });
}

async function revealExplain(lines) {
  const box = $('explain');
  box.innerHTML = '';
  const head = document.createElement('div');
  head.className = 'eh';
  head.textContent = 'WHY THESE ROWS?';
  box.appendChild(head);
  const items = (lines || []).filter(t => t).map(t => {
    const d = document.createElement('div');
    d.className = 'eline';
    d.textContent = t;
    box.appendChild(d);
    return d;
  });
  for (const d of items) {
    await wait(420);
    d.classList.add('show');
  }
  await wait(500);
}

// ---------- SQL highlighting (escape first, then colour keywords, strings and numbers) ----------
const KW = ['SELECT','FROM','WHERE','DELETE','INSERT','UPDATE','CREATE','DROP','ALTER','JOIN',
            'INNER','LEFT','RIGHT','OUTER','FULL','CROSS','GROUP BY','ORDER BY','HAVING','LIMIT',
            'OFFSET','DISTINCT','AND','OR','NOT','IN','BETWEEN','LIKE','IS','NULL','CASE','WHEN',
            'THEN','ELSE','END','AS','WITH','PARTITION BY','OVER','ROW_NUMBER','RANK','DENSE_RANK',
            'MAX','MIN','SUM','COUNT','AVG','ON','UNION','ALL','ASC','DESC'];
KW.sort((a, b) => b.length - a.length);
const KW_RE = new RegExp('\\b(' + KW.map(k => k.replace(/ /g, '\\s+')).join('|') + ')\\b', 'gi');

function hl(line) {
  let s = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  s = s.replace(/'([^']*)'/g, '<span class="str">\'$1\'</span>');
  s = s.replace(KW_RE, '<span class="kw">$1</span>');
  s = s.replace(/\b(\d+)\b/g, '<span class="num">$1</span>');
  return s;
}

// The font size never changes. The caret is written inside the line being typed.
function renderCode() {
  const lines = currentCode.split('\n');
  const caret = lines.length - 1;
  let html = '';
  for (let i = 0; i < lines.length; i++) {
    const active = (i >= activeFrom && i <= activeTo);
    const body = hl(lines[i]);
    const inner = (i === caret) ? body + '<span class="cursor"></span>' : (body.length ? body : '&nbsp;');
    html += '<div class="cl' + (active ? ' active' : '') + '">' + inner + '</div>';
  }
  $('code').innerHTML = html;
  $('escroll').scrollTop = $('escroll').scrollHeight;
}

async function typeText(text) {
  for (let k = 0; k < text.length; k++) {
    currentCode += text.charAt(k);
    renderCode();
    await wait(TYPING_SPEED);
  }
}
async function typeInsert(at, text) {
  const left = currentCode.slice(0, at), right = currentCode.slice(at);
  for (let k = 1; k <= text.length; k++) {
    currentCode = left + text.slice(0, k) + right;
    renderCode();
    await wait(TYPING_SPEED);
  }
}
async function typeWrap(pre, post) {
  const kept = currentCode;
  for (let k = 1; k <= pre.length; k++) {
    currentCode = pre.slice(0, k) + kept;
    renderCode();
    await wait(TYPING_SPEED);
  }
  const base = pre + kept;
  for (let k = 1; k <= post.length; k++) {
    currentCode = base + post.slice(0, k);
    renderCode();
    await wait(TYPING_SPEED);
  }
}
async function typeStep(s) {
  if (s.mode === 'wrap') return typeWrap(s.prepend || '', s.appendafter || '');
  if (s.mode === 'insert') return typeInsert(s.at || 0, s.typed || '');
  const text = s.typed || (s.mode === 'start' ? (s.query || '') : '');
  if (text) await typeText(text);
}

// ---------- scene A: sample data for every table in the query ----------
async function sceneTables() {
  resetVis();
  renderTables();
  setExplain(P.intro_learn || []);
  await wait(5000);
}

// ---------- scene B: SQL typed line by line, stage buttons and explanation follow the progress ----------
async function sceneTyping() {
  resetVis();
  currentCode = '';
  activeFrom = 0;
  activeTo = 0;
  $('editor').style.display = 'block';
  $('escroll').style.maxHeight = P.tables.length >= 3 ? '300px' : '360px';
  renderCode();
  $('escroll').onclick = e => {
    const el = e.target.closest('.cl');
    if (!el) return;
    const li = Array.from(el.parentNode.children).indexOf(el);
    const cands = P.steps.filter(s => li >= s.active_from && li <= s.active_to);
    if (!cands.length) return;
    cands.sort((a, b) => (a.active_to - a.active_from) - (b.active_to - b.active_from));
    setComments(cands[0].bubble);
    setExplain(cands[0].learn ? [cands[0].learn] : []);
  };
  const m = computeMatches();
  for (let i = 0; i < P.steps.length; i++) {
    const s = P.steps[i];
    markChips(i);
    setExplain(s.learn ? [s.learn] : []);
    activeFrom = s.active_from || 0;
    activeTo = (s.active_to === undefined) ? activeFrom : s.active_to;
    renderCode();
    VIS.tables = new Set((s.hl_tables || []).map(k => idxOfKey(k)).filter(x => x >= 0));
    VIS.cols = new Set(s.hl_cols || []);
    VIS.rowKeep = (s.dim && s.rows) ? {0: new Set(s.rows)} : null;
    VIS.rowMark = {};
    VIS.note = {};
    if (s.is_match && m) {
      VIS.note[m.leftIdx] = {};
      VIS.rowMark[m.leftIdx] = {};
      VIS.rowMark[m.rightIdx] = {};
      Object.keys(m.leftMatches).forEach(l => {
        const idx = Number(l) - 1;
        const ms = m.leftMatches[l];
        VIS.note[m.leftIdx][idx] = ms.length ? ('✔ ' + ms.length + ' match') : '✖ no match';
        VIS.rowMark[m.leftIdx][idx] = ms.length ? 'jmatch' : 'jnomatch';
        ms.forEach(rid => { VIS.rowMark[m.rightIdx][rid - 1] = 'jmatch'; });
      });
    }
    renderTables();
    await revealComments(s.bubble);
    if (s.typed || s.prepend || s.appendafter) await typeStep(s);
    await wait(600);
  }
  activeFrom = 0;
  activeTo = 9999;
  renderCode();
  await wait(800);
}

// ---------- scene C: rows after JOIN, WHERE filter, final output (always shown) ----------
async function sceneResult() {
  resetVis();
  markChips(P.steps.length);
  $('editor').style.display = 'none';
  $('result').style.display = 'flex';

  // final output: from the SQLite run, or the model's expected output if the run was not possible
  const fH = P.final_headers || [];
  const fR = P.final_rows || [];
  $('final').innerHTML = '';
  $('final').appendChild(buildResultTable(fH, fR, 'No row satisfies the condition for this sample data.'));

  if (SIM.ok) {
    if (!SIM.agg && SIM.final_primary_rids && P.tables.length) {
      VIS.rowMark[0] = {};
      P.tables[0].rows.forEach((r, ri) => {
        VIS.rowMark[0][ri] = SIM.final_primary_rids.includes(ri + 1) ? 'kept' : 'removed';
      });
    }
    renderTables();
    const tbl = buildResultTable(SIM.inter_headers, SIM.inter_rows, '');
    $('inter').innerHTML = '';
    $('inter').appendChild(tbl);
    const trs = Array.from(tbl.querySelectorAll('tr')).slice(1);
    for (let i = 0; i < trs.length; i++) {
      await wait(300);
      trs[i].classList.add(SIM.inter_pass[i] ? 'kept' : 'removed');
    }
  } else {
    $('inter').innerHTML = '';
    const note = document.createElement('div');
    note.style.fontSize = '20px';
    note.textContent = 'The simulation could not run this query. The expected output from the model is shown below.';
    $('inter').appendChild(note);
  }
  await revealExplain(P.result_learn || []);
  await wait(3000);
}

async function runAll() {
  $('end-card').style.opacity = '0';
  try {
    await sceneTables();
    await sceneTyping();
    await sceneResult();
    await wait(3500);
    $('content').style.transition = 'opacity .6s';
    $('content').style.opacity = '0';
    await wait(700);
    $('content').style.visibility = 'hidden';
    $('end-card').style.opacity = '1';
  } catch (e) {
    console.error(e);
  }
}

resizeStage();
window.addEventListener('resize', resizeStage);
$('question').textContent = P.question;
buildChips();
window.onload = runAll;
</script>
</body>
</html>
"""

LEARN_TEMPLATE = LEARN_TEMPLATE_HEAD + LEARN_TEMPLATE_JS

LOADING_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Preparing animation...</title>
<style>
body { margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
       background: linear-gradient(135deg, #0b1121 0%, #1e293b 100%); color: #e2e8f0;
       font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; }
.box { padding: 30px; }
.spin { width: 54px; height: 54px; margin: 0 auto 18px auto; border-radius: 50%;
        border: 5px solid #334155; border-top-color: #38bdf8; animation: s 0.9s linear infinite; }
@keyframes s { to { transform: rotate(360deg); } }
.stage { color: #94a3b8; font-size: 14px; margin-top: 10px; }
</style>
</head>
<body>
<div class="box">
  <div class="spin"></div>
  <div>Preparing your animation...</div>
  <div class="stage" id="s"></div>
</div>
<script>
const JOB = "__JOB_ID__";
async function poll() {
    try {
        const r = await fetch('/status/' + JOB, { cache: 'no-store' });
        const d = await r.json();
        document.getElementById('s').textContent = d.stage ? ('Stage: ' + d.stage) : '';
        if (d.html_ready) { location.reload(); return; }
        if (d.status === 'error') {
            document.querySelector('.box').textContent = 'Generation failed. Check the dashboard logs.';
            return;
        }
    } catch (e) { /* keep polling */ }
    setTimeout(poll, 400);
}
poll();
</script>
</body>
</html>
"""


def build_payload(data):
    """Everything the Step 5 / Step 6 page needs, as one JSON object."""
    steps = data.get("steps") or []
    sim = data.get("sim") or {"ok": False, "error": "No SQL to simulate"}
    tables = []
    for t in data.get("tables") or []:
        tables.append({
            "name": t["name"],
            "key": t.get("key") or _base_name(t["name"]),
            "synthetic": bool(t.get("synthetic")),
            "headers": t["headers"],
            "rows": t["rows"],
        })
    return {
        "question": str(data.get("question_banner") or "SQL Query"),
        "tables": tables,
        "synthetic": data.get("synthetic_tables") or [],
        "steps": steps,
        "sim": sim,
        "result_explain": data.get("result_explain") or "",
        "result_learn": data.get("result_learn") or [],
        "intro_learn": data.get("intro_learn") or [],
        "final_headers": (sim.get("final_headers") if sim.get("ok") else (data.get("result_headers") or [])),
        "final_rows": (sim.get("final_rows") if sim.get("ok") else (data.get("cleaned_output") or [])),
    }


def safe_json(obj):
    """JSON that is safe to place inside a <script> block."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def create_html_file(data, output_path):
    """Build the Step 5 / Step 6 page, save it, and return its HTML."""
    log_message("Building HTML...")
    try:
        theme = data.get("reel_theme") or choose_reel_theme(str(data.get("question_banner") or ""), "")
        log_message(f"BACKGROUND: {theme['name']}")
        html_content = (LEARN_TEMPLATE
                        .replace("__THEME_CSS__", theme_css(theme))
                        .replace("__PAYLOAD__", safe_json(build_payload(data))))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        log_message("HTML created")
        return html_content
    except Exception as e:
        log_message(f"HTML error: {str(e)}")
        raise



async def record_video(html_file_path: Path, output_dir: str) -> str:
    """Record the silent reel animation (no audio of any kind)."""
    log_message("Launching Chrome...")
    video_path = ""

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(channel="chrome", headless=False, slow_mo=50)
            context = await browser.new_context(
                record_video_dir=output_dir,
                record_video_size={"width": RECORD_WIDTH, "height": RECORD_HEIGHT},
                viewport={"width": RECORD_WIDTH, "height": RECORD_HEIGHT},
                device_scale_factor=2
            )
            page = await context.new_page()
            video = page.video
            log_message("Loading animation...")
            await page.goto(html_file_path.as_uri())

            try:
                await page.wait_for_function(
                    "document.getElementById('end-card') && document.getElementById('end-card').style.opacity === '1'",
                    timeout=240000
                )
                log_message("Animation complete - stopping the recording now")
                await page.wait_for_timeout(END_CARD_STOP_MS)
            except Exception:
                log_message("WARNING: animation timeout - stopping the recording")

            await context.close()
            await browser.close()

            try:
                if video:
                    video_path = await video.path()
            except Exception:
                video_path = ""

            log_message("Recording stopped, video saved")
    except Exception as e:
        log_message(f"Video error: {str(e)}")
        raise

    return video_path


# ============================================================
# PIPELINE RUNNER (background thread + live logs)
# ============================================================
def run_pipeline(job_id: str, question: str, query_logic: str):
    _thread_ctx.job_id = job_id

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(HTML_SAVE_DIR, exist_ok=True)

    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if job is not None:
            job["status"] = "running"

    try:
        if not PIPELINE_LOCK.acquire(blocking=False):
            log_message("A previous job is running - waiting for it to finish...")
            set_job_stage(job_id, "queued")
            PIPELINE_LOCK.acquire()

        try:
            set_job_stage(job_id, "learning")
            log_message(f"Question: {question[:70]}")
            log_message("Model is thinking about the logic...")

            animation_data = generate_animation_data(question, query_logic)

            set_job_stage(job_id, "build")
            log_message("Logic understood - building the reel...")
            html_file_path = Path(HTML_SAVE_DIR) / "dynamic_animation.html"
            html_content = create_html_file(animation_data, html_file_path)

            # the animation tab can open now: it shows the page as soon as it is ready
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                if job is not None:
                    job["html"] = html_content
                    job["html_ready"] = True
                    job["updated"] = time.time()

            set_job_stage(job_id, "video")
            if platform.system() == "Windows":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            video_path = asyncio.run(record_video(html_file_path, OUTPUT_DIR))
            if video_path:
                log_message(f"FINAL VIDEO (silent) -> {video_path}")

            log_message("VIDEO COMPLETE - code stopped")
            set_job_stage(job_id, "done")
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                if job is not None:
                    job["status"] = "done"
                    job["finished"] = time.time()
        finally:
            PIPELINE_LOCK.release()

    except Exception as e:
        log_message(f"ERROR: {str(e)[:150]}")
        try:
            log_message("TRACEBACK: " + traceback.format_exc().splitlines()[-1][:150])
        except Exception:
            pass
        set_job_stage(job_id, "error")
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if job is not None:
                job["status"] = "error"
                job["finished"] = time.time()


# ============================================================
# DASHBOARD (horizontal, website-style layout)
# ============================================================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@Code_With_Mangesh - AI Video Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
            background: linear-gradient(135deg, #0b1121 0%, #1e293b 100%);
            color: #f8fafc; min-height: 100vh; padding: 18px;
        }
        .wrap { max-width: 1600px; margin: 0 auto; }
        .topbar {
            display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
            background: rgba(30, 41, 59, 0.85); border: 2px solid #334155;
            border-radius: 14px; padding: 14px 22px; margin-bottom: 16px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.45);
        }
        .brand h1 { font-size: 22px; color: #38bdf8; }
        .brand p { font-size: 12.5px; color: #94a3b8; margin-top: 4px; }
        .stages { display: flex; gap: 8px; flex-wrap: wrap; margin-left: auto; }
        .stage {
            font-size: 12px; font-weight: 600; padding: 7px 12px; border-radius: 8px;
            border: 2px solid #334155; color: #64748b; background: #0f172a; transition: all 0.3s;
            white-space: nowrap;
        }
        .stage.active { border-color: #38bdf8; color: #38bdf8; background: rgba(56,189,248,0.12);
            box-shadow: 0 0 12px rgba(56,189,248,0.35); }
        .stage.done { border-color: #4ade80; color: #4ade80; background: rgba(74,222,128,0.10); }
        .stage.error { border-color: #f87171; color: #f87171; background: rgba(248,113,113,0.12); }

        .grid {
            display: grid;
            grid-template-columns: minmax(320px, 1.05fr) minmax(320px, 1fr) minmax(340px, 1.2fr);
            gap: 16px; align-items: start;
        }
        .card {
            background: rgba(30, 41, 59, 0.82); border: 2px solid #334155; border-radius: 14px;
            padding: 18px; box-shadow: 0 16px 40px rgba(0,0,0,0.5);
        }
        .card h2 {
            font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase;
            color: #cbd5e1; margin-bottom: 12px; font-weight: 700;
        }
        label { font-size: 13.5px; font-weight: 600; color: #cbd5e1; display: block; margin: 10px 0 6px 0; }
        label small { color: #64748b; font-weight: 400; }
        textarea {
            width: 100%; padding: 10px; font-size: 13.5px; background: #0f172a; color: #e2e8f0;
            border: 2px solid #334155; border-radius: 8px; resize: vertical;
            font-family: 'Consolas', 'Segoe UI', sans-serif; line-height: 1.45;
            transition: border-color 0.3s;
        }
        #question { height: 84px; }
        #queryLogic { height: 230px; font-family: 'Consolas', monospace; }
        textarea:focus { outline: none; border-color: #38bdf8; box-shadow: 0 0 10px rgba(56,189,248,0.3); }
        .row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
        button {
            background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
            color: #0f172a; font-size: 15px; font-weight: bold; padding: 12px 22px;
            border: none; border-radius: 9px; cursor: pointer; width: 100%;
            margin-top: 12px; transition: all 0.3s; box-shadow: 0 6px 16px rgba(56,189,248,0.3);
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(56,189,248,0.5); }
        button:disabled { background: #64748b; cursor: not-allowed; transform: none; box-shadow: none; }
        button.mini {
            background: #1e293b; color: #38bdf8; border: 2px solid #38bdf8;
            width: auto; flex: 1 1 auto; margin-top: 0; font-size: 13px;
            padding: 10px 8px; box-shadow: none;
        }
        button.mini:hover { background: rgba(56,189,248,0.12); transform: translateY(-1px); box-shadow: none; }
        button.mini:disabled { background: #334155; color: #64748b; border-color: #334155; }
        .note { font-size: 11.5px; color: #64748b; margin-top: 8px; }
        .link-btn {
            display: none; text-align: center; margin-top: 10px; font-size: 13px; font-weight: 700;
            padding: 9px 12px; border-radius: 8px; border: 2px solid #38bdf8; color: #38bdf8;
            background: #1e293b; text-decoration: none;
        }
        .link-btn:hover { background: rgba(56,189,248,0.12); }
        #metaBox { display: none; margin-top: 14px; }
        .meta-head { display: flex; align-items: center; gap: 10px; margin-bottom: 7px; flex-wrap: wrap; }
        .meta-title { font-size: 13.5px; font-weight: 600; color: #cbd5e1; }
        .meta-copy { flex: 0 0 auto; margin-left: auto; font-size: 12px; padding: 5px 14px; width: auto; margin-top: 0; }
        .meta-out {
            background: #0f172a; border: 2px solid #334155; border-radius: 9px; padding: 12px;
            font-size: 13px; color: #e2e8f0; line-height: 1.6; white-space: pre-wrap;
            max-height: 240px; overflow-y: auto;
        }
        #thumbBox { display: none; margin-top: 14px; }
        .thumb-wrap {
            display: flex; align-items: center; justify-content: center;
            background: #0f172a; border: 2px solid #334155; border-radius: 9px; padding: 12px; min-height: 120px;
        }
        #thumbImg { display: none; max-height: 420px; border-radius: 8px; border: 1px solid #334155; }
        .thumb-status { font-size: 12.5px; color: #94a3b8; text-align: center; }
        .mini-link {
            margin-left: auto; font-size: 12px; font-weight: 700; padding: 6px 14px;
            border-radius: 8px; border: 2px solid #4ade80; color: #4ade80;
            background: #1e293b; text-decoration: none;
        }
        .mini-link:hover { background: rgba(74,222,128,0.12); }
        .log-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
        .pill { font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 18px;
            border: 2px solid #334155; color: #94a3b8; background: #0f172a; }
        .pill.running { border-color: #38bdf8; color: #38bdf8; }
        .pill.done { border-color: #4ade80; color: #4ade80; }
        .pill.error { border-color: #f87171; color: #f87171; }
        .timer { margin-left: auto; font-family: 'Consolas', monospace; font-size: 12px; color: #64748b; }
        .logs-box {
            background: #0f172a; border: 2px solid #334155; border-radius: 9px; padding: 12px;
            height: 540px; overflow-y: auto; font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px; color: #4ade80; line-height: 1.6; white-space: pre-wrap;
        }
        @media (max-width: 1000px) {
            .grid { grid-template-columns: 1fr; }
            .logs-box { height: 300px; }
            .stages { margin-left: 0; }
        }
    </style>
</head>
<body>
<div class="wrap">
    <div class="topbar">
        <div class="brand">
            <h1>AI Video Generator Studio</h1>
            <p>@Code_With_Mangesh - Smart SQL Learning</p>
        </div>
        <div class="stages" id="stages">
            <div class="stage" data-stage="learning">1. Learning memory</div>
            <div class="stage" data-stage="models">2. Models</div>
            <div class="stage" data-stage="build">3. Building</div>
            <div class="stage" data-stage="video">4. Recording</div>
            <div class="stage" data-stage="done">5. Done</div>
        </div>
    </div>

    <div class="grid">
        <!-- ============ COLUMN 1: INPUT ============ -->
        <div class="card">
            <h2>1 - Input</h2>
            <form id="videoForm">
                <label for="question">Question <small>(problem statement of the video)</small></label>
                <textarea id="question" placeholder="Example: Find the employee with the second highest salary"></textarea>

                <label for="queryLogic">Query or Logic <small>(optional - paste your SQL or write the logic)</small></label>
                <textarea id="queryLogic" placeholder="SELECT ACCOUNT_ID, SUM(AMOUNT) AS TOTAL_AMOUNT&#10;FROM TRANSACTIONS&#10;GROUP BY ACCOUNT_ID;&#10;&#10;Or write: group by account, use SUM and COUNT, year 2024 only"></textarea>

                <button type="submit" id="playBtn">Generate Video</button>
                <a id="animLink" class="link-btn" href="#" target="_blank">Open animation tab</a>
                <p class="note">The animation tab opens immediately and shows the SQL build, tables and simulated result.</p>
            </form>
        </div>

        <!-- ============ COLUMN 2: TOOLS ============ -->
        <div class="card">
            <h2>2 - YouTube Tools</h2>
            <div class="row">
                <button type="button" class="mini" id="btnTitle">Generate Title</button>
                <button type="button" class="mini" id="btnDesc">Generate Description</button>
                <button type="button" class="mini" id="btnTags">Generate Hashtags</button>
            </div>

            <div id="metaBox">
                <div class="meta-head">
                    <span class="meta-title" id="metaTitle">AI YouTube Metadata</span>
                    <button type="button" class="mini meta-copy" id="btnCopy">Copy</button>
                </div>
                <div class="meta-out" id="metaOut"></div>
            </div>

            <div class="row">
                <button type="button" class="mini" id="btnThumb">Create Thumbnail (9:16 PNG)</button>
            </div>
            <p class="note">Thumbnail background alternates: click 1 = mixed gradient, click 2 = one solid colour, and so on. Each click uses a fresh theme.</p>

            <div id="thumbBox">
                <div class="meta-head">
                    <span class="meta-title">AI Thumbnail - 1080x1920 PNG</span>
                    <a id="thumbDl" class="mini-link" href="/download/thumbnail" download="youtube_short_thumbnail.png">Download PNG</a>
                </div>
                <div class="thumb-wrap">
                    <div class="thumb-status" id="thumbStatus">Rendering 1080 x 1920 PNG...</div>
                    <img id="thumbImg" alt="generated thumbnail" />
                </div>
            </div>
        </div>

        <!-- ============ COLUMN 3: LIVE MONITORING ============ -->
        <div class="card">
            <h2>3 - Live Monitoring</h2>
            <div class="log-head">
                <span class="pill" id="statusPill">Idle</span>
                <span class="timer" id="timer"></span>
            </div>
            <div class="logs-box" id="logs">Ready. Fill in the Question box, the Query/Logic box, or both.</div>
        </div>
    </div>
</div>

<script>
    const form = document.getElementById('videoForm');
    const qBox = document.getElementById('question');
    const logicBox = document.getElementById('queryLogic');
    const logsDiv = document.getElementById('logs');
    const btn = document.getElementById('playBtn');
    const pill = document.getElementById('statusPill');
    const timerEl = document.getElementById('timer');
    const stageEls = document.querySelectorAll('.stage');
    const animLink = document.getElementById('animLink');

    const metaBox = document.getElementById('metaBox');
    const metaOut = document.getElementById('metaOut');
    const metaTitle = document.getElementById('metaTitle');
    const btnCopy = document.getElementById('btnCopy');
    const metaBtns = [document.getElementById('btnTitle'),
                      document.getElementById('btnDesc'),
                      document.getElementById('btnTags')];

    const btnThumb = document.getElementById('btnThumb');
    const thumbBox = document.getElementById('thumbBox');
    const thumbImg = document.getElementById('thumbImg');
    const thumbStatus = document.getElementById('thumbStatus');
    const thumbDl = document.getElementById('thumbDl');

    const STAGE_ORDER = ['learning', 'models', 'build', 'video', 'done'];
    let tickHandle = null;

    function setPill(text, cls) {
        pill.innerText = text;
        pill.className = 'pill' + (cls ? ' ' + cls : '');
    }

    function paintStages(stage, status) {
        const idx = STAGE_ORDER.indexOf(stage);
        stageEls.forEach(el => {
            const s = el.getAttribute('data-stage');
            el.classList.remove('active', 'done', 'error');
            const sIdx = STAGE_ORDER.indexOf(s);
            if (status === 'error' && sIdx === Math.max(idx, 0)) { el.classList.add('error'); return; }
            if (idx === -1) return;
            if (sIdx < idx || status === 'done') el.classList.add('done');
            else if (sIdx === idx && status !== 'done') el.classList.add('active');
        });
    }

    function startTimer(t0) {
        if (tickHandle) clearInterval(tickHandle);
        tickHandle = setInterval(() => {
            timerEl.innerText = 'Elapsed ' + ((Date.now() - t0) / 1000).toFixed(1) + 's';
        }, 200);
    }

    function stopTimer() { if (tickHandle) clearInterval(tickHandle); tickHandle = null; }

    async function pollJob(jobId, t0) {
        let printed = 0;
        while (true) {
            let data;
            try {
                const r = await fetch('/status/' + jobId, { cache: 'no-store' });
                data = await r.json();
            } catch (e) {
                setPill('Connection lost', 'error');
                stopTimer();
                return;
            }

            if (data.logs && data.logs.length > printed) {
                const fresh = data.logs.slice(printed);
                printed = data.logs.length;
                for (const line of fresh) {
                    logsDiv.appendChild(document.createTextNode(line + '\\n'));
                }
                logsDiv.scrollTop = logsDiv.scrollHeight;
            }

            paintStages(data.stage, data.status);
            timerEl.innerText = 'Elapsed ' + ((Date.now() - t0) / 1000).toFixed(1) + 's';

            if (data.status === 'done') { setPill('Video ready', 'done'); stopTimer(); return; }
            if (data.status === 'error') { setPill('Failed', 'error'); stopTimer(); return; }
            if (data.status === 'running' || data.status === 'queued') {
                setPill(data.stage ? ('Working: ' + data.stage) : 'Working', 'running');
            }
            await new Promise(r => setTimeout(r, 600));
        }
    }

    form.onsubmit = async (e) => {
        e.preventDefault();

        const q = qBox.value.trim();
        const logic = logicBox.value.trim();

        if (!q && !logic) {
            logsDiv.textContent = 'Please fill in the Question box or the Query/Logic box.\\n';
            return;
        }

        // open the animation tab right away (blank now, filled once the job id is known)
        const win = window.open('about:blank', '_blank');

        btn.disabled = true;
        btn.innerText = 'AI is thinking...';
        logsDiv.textContent = '';
        setPill('Starting...', 'running');
        animLink.style.display = 'none';

        const t0 = Date.now();
        paintStages('learning', 'running');
        startTimer(t0);

        try {
            const r = await fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({ question: q, query_logic: logic }).toString()
            });
            const res = await r.json();

            if (!res.job_id) {
                logsDiv.textContent += 'Error: ' + (res.error || 'the job did not start') + '\\n';
                setPill('Failed', 'error');
                stopTimer();
                if (win) win.close();
            } else {
                const url = '/animation/' + res.job_id;
                if (win) win.location.href = url;
                animLink.href = url;
                animLink.style.display = 'block';
                await pollJob(res.job_id, t0);
            }
        } catch (err) {
            logsDiv.textContent += 'Error: ' + err.message + '\\n';
            setPill('Failed', 'error');
            stopTimer();
            if (win) win.close();
        }

        btn.disabled = false;
        btn.innerText = 'Generate Video';
    };

    // ---------- AI YouTube metadata buttons (text only, no background change) ----------
    function setMetaBusy(busy) { metaBtns.forEach(b => b.disabled = busy); }

    async function runMeta(kind) {
        const q = qBox.value.trim();
        const logic = logicBox.value.trim();

        const labels = { title: 'Title', description: 'Description', hashtags: 'Hashtags' };
        metaBox.style.display = 'block';
        metaTitle.innerText = 'AI ' + labels[kind];
        metaOut.textContent = 'Generating ' + labels[kind].toLowerCase() + ' from the question, query and logic...';
        setMetaBusy(true);

        try {
            const r = await fetch('/metadata', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({ question: q, query_logic: logic, kind: kind }).toString()
            });
            const res = await r.json();
            metaOut.textContent = res.text ? res.text
                : ('Error: ' + (res.error || 'the model could not generate this'));
        } catch (err) {
            metaOut.textContent = 'Error: ' + err.message;
        }

        setMetaBusy(false);
    }

    document.getElementById('btnTitle').onclick = () => runMeta('title');
    document.getElementById('btnDesc').onclick = () => runMeta('description');
    document.getElementById('btnTags').onclick = () => runMeta('hashtags');

    btnCopy.onclick = async () => {
        try {
            await navigator.clipboard.writeText(metaOut.innerText);
            btnCopy.innerText = 'Copied';
        } catch (e) {
            btnCopy.innerText = 'Select all';
        }
        setTimeout(() => { btnCopy.innerText = 'Copy'; }, 1200);
    };

    // ---------- Create Thumbnail (background alternates: gradient, solid, ...) ----------
    btnThumb.onclick = async () => {
        const q = qBox.value.trim();
        const logic = logicBox.value.trim();

        thumbBox.style.display = 'block';
        thumbImg.style.display = 'none';
        thumbImg.removeAttribute('src');
        thumbStatus.style.display = 'block';
        thumbStatus.textContent = 'Rendering 1080 x 1920 PNG (background changes each click)...';
        btnThumb.disabled = true;
        btnThumb.innerText = 'Creating thumbnail...';

        try {
            const r = await fetch('/thumbnail', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({ question: q, query_logic: logic }).toString()
            });
            const res = await r.json();

            if (res.ok) {
                thumbImg.onload = () => {
                    thumbStatus.style.display = 'none';
                    thumbImg.style.display = 'block';
                };
                thumbImg.src = res.url;
                thumbDl.href = res.url;
                thumbDl.setAttribute('download', res.filename || 'youtube_short_thumbnail.png');

                const mode = (res.content && res.content.background_mode) || '';
                if (mode) {
                    const used = (res.content && res.content.theme_used) || '';
                    metaBox.style.display = 'block';
                    metaTitle.innerText = 'Thumbnail background';
                    metaOut.textContent = (mode === 'solid')
                        ? 'Single solid colour background (no gradient): ' + used
                        : 'Mixed gradient background: ' + used;
                }
            } else {
                thumbStatus.textContent = 'Error: ' + (res.error || 'thumbnail failed');
            }
        } catch (err) {
            thumbStatus.textContent = 'Error: ' + err.message;
        }

        btnThumb.disabled = false;
        btnThumb.innerText = 'Create Thumbnail (9:16 PNG)';
    };
</script>
</body>
</html>
"""


# ============================================================
# ROUTES
# ============================================================
def _clean_inputs(question: str, query_logic: str):
    question = (question or "").strip()
    query_logic = (query_logic or "").strip()
    low = question.lower()
    for pref in ("question:", "question -", "question-", "sql question:", "q:"):
        if low.startswith(pref):
            question = question[len(pref):].strip()
            break
    return question, query_logic


def _fill_from_last_run(question: str, query_logic: str, tag: str):
    if not query_logic and LAST_RUN.get("final_query"):
        query_logic = LAST_RUN["final_query"]
        log_message(f"{tag}: using the last generated query from this session")
    if not query_logic and LAST_RUN.get("logic_explanation"):
        query_logic = LAST_RUN["logic_explanation"]
    if not question and LAST_RUN.get("question"):
        question = LAST_RUN["question"]
    return question, query_logic


DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@Code_With_Mangesh - AI Video Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; background: linear-gradient(160deg, #170D2E 0%, #0B1020 100%); color: #FFFFFF; min-height: 100vh; padding: 18px; }
        .wrap { max-width: 1600px; margin: 0 auto; }
        .topbar { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; background: #21143D; border: 1px solid rgba(139,46,255,.6); border-radius: 14px; padding: 14px 22px; margin-bottom: 16px; box-shadow: 0 0 20px rgba(139,46,255,.18); }
        .brand h1 { font-size: 24px; font-weight: 800; background: linear-gradient(90deg, #8B2EFF 0%, #F000D0 55%, #FF6B9D 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent; }
        .brand p { font-size: 13px; color: #D5CEE8; margin-top: 4px; }
        .stages { display: flex; gap: 8px; flex-wrap: wrap; margin-left: auto; }
        .stage { font-size: 13px; font-weight: 600; padding: 7px 12px; border-radius: 8px; border: 1px solid rgba(139,46,255,.5); color: #D5CEE8; background: #0B1020; white-space: nowrap; transition: all .3s; }
        .stage.active { border-color: #F000D0; color: #FFFFFF; box-shadow: 0 0 10px rgba(240,0,208,.25); }
        .stage.done { border-color: #8B2EFF; color: #D5CEE8; }
        .stage.error { border-color: #FF8A00; color: #FF8A00; }
        .grid { display: grid; grid-template-columns: minmax(320px, 1.05fr) minmax(320px, 1fr) minmax(340px, 1.2fr); gap: 16px; align-items: start; }
        .card { background: #21143D; border: 1px solid rgba(139,46,255,.6); border-radius: 14px; padding: 18px; box-shadow: 0 0 20px rgba(139,46,255,.14); min-width: 0; }
        .card h2 { font-size: 14px; letter-spacing: 1px; text-transform: uppercase; color: #D5CEE8; margin-bottom: 12px; font-weight: 700; }
        label { font-size: 14px; font-weight: 600; color: #D5CEE8; display: block; margin: 12px 0 6px 0; }
        label small { color: #D5CEE8; font-weight: 400; opacity: .8; }
        textarea { width: 100%; padding: 10px; font-size: 14px; background: #0B1020; color: #FFFFFF; border: 1px solid rgba(139,46,255,.6); border-radius: 8px; resize: vertical; font-family: 'Consolas', 'Segoe UI', sans-serif; line-height: 1.45; }
        #question { height: 96px; }
        #queryLogic { height: 230px; font-family: 'Consolas', monospace; }
        textarea:focus { outline: none; border-color: #F000D0; box-shadow: 0 0 10px rgba(240,0,208,.25); }
        .row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
        button { font-size: 15px; font-weight: 700; padding: 12px 22px; border: none; border-radius: 9px; cursor: pointer; width: 100%; margin-top: 14px; transition: all .3s; color: #FFFFFF; background: #21143D; border: 1px solid #1677FF; }
        button:hover { box-shadow: 0 0 12px rgba(22,119,255,.3); }
        button:disabled { opacity: .45; cursor: not-allowed; }
        /* main call to action: highlight yellow */
        button.cta { background: #FFD900; color: #170D2E; border: none; }
        button.cta:hover { box-shadow: 0 0 14px rgba(255,217,0,.35); }
        button.mini { width: auto; flex: 1 1 auto; margin-top: 0; font-size: 14px; padding: 11px 8px; }
        .note { font-size: 12.5px; color: #D5CEE8; margin-top: 8px; opacity: .85; }
        #metaBox { display: none; margin-top: 14px; }
        .meta-head { display: flex; align-items: center; gap: 10px; margin-bottom: 7px; flex-wrap: wrap; }
        .meta-title { font-size: 14px; font-weight: 700; color: #D5CEE8; }
        .meta-copy { flex: 0 0 auto; margin-left: auto; font-size: 13px; padding: 5px 14px; width: auto; margin-top: 0; }
        .meta-out { background: #0B1020; border: 1px solid rgba(139,46,255,.6); border-radius: 9px; padding: 12px; font-size: 14px; color: #FFFFFF; line-height: 1.6; white-space: pre-wrap; max-height: 260px; overflow-y: auto; word-break: break-word; }
        #thumbBox { display: none; margin-top: 14px; }
        .thumb-wrap { display: flex; align-items: center; justify-content: center; background: #0B1020; border: 1px solid rgba(139,46,255,.6); border-radius: 9px; padding: 12px; min-height: 120px; }
        #thumbImg { display: none; max-height: 420px; border-radius: 8px; border: 1px solid rgba(139,46,255,.6); }
        .thumb-status { font-size: 13px; color: #D5CEE8; text-align: center; }
        .mini-link { margin-left: auto; font-size: 13px; font-weight: 700; padding: 6px 14px; border-radius: 8px; border: 1px solid #FFD900; color: #FFD900; background: #21143D; text-decoration: none; }
        .log-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
        .logs-label { font-size: 14px; font-weight: 700; color: #D5CEE8; }
        .pill { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 18px; border: 1px solid rgba(139,46,255,.6); color: #D5CEE8; background: #0B1020; }
        .pill.running { border-color: #1677FF; color: #FFFFFF; }
        .pill.done { border-color: #FFD900; color: #FFD900; }
        .pill.error { border-color: #FF8A00; color: #FF8A00; }
        .timer { margin-left: auto; font-family: 'Consolas', monospace; font-size: 12.5px; color: #D5CEE8; }
        .logs-box { background: #0B1020; border: 1px solid rgba(139,46,255,.6); border-radius: 9px; padding: 12px; height: 520px; overflow-y: auto; font-family: 'Consolas', 'Courier New', monospace; font-size: 12.5px; color: #D5CEE8; line-height: 1.6; white-space: pre-wrap; }
        @media (max-width: 1000px) {
            .grid { grid-template-columns: 1fr; }
            .logs-box { height: 300px; }
            .stages { margin-left: 0; }
        }
    </style>
</head>
<body>
<div class="wrap">
    <div class="topbar">
        <div class="brand">
            <h1>AI Video Generator Studio</h1>
            <p>@Code_With_Mangesh - Smart SQL Learning</p>
        </div>
        <div class="stages" id="stages">
            <div class="stage" data-stage="learning">Learning memory</div>
            <div class="stage" data-stage="models">Models</div>
            <div class="stage" data-stage="build">Building HTML</div>
            <div class="stage" data-stage="video">Recording</div>
            <div class="stage" data-stage="done">Done</div>
        </div>
    </div>

    <div class="grid">
        <!-- ============ LEFT: INPUT ============ -->
        <div class="card">
            <h2>Input</h2>
            <form id="videoForm">
                <label for="question">Question <small>(problem statement of the video)</small></label>
                <textarea id="question" placeholder="Example: Find customers who have never made a transaction."></textarea>

                <label for="queryLogic">Query or Logic <small>(optional - paste your SQL or write the logic)</small></label>
                <textarea id="queryLogic" placeholder="SELECT c.CUSTOMER_ID, c.CUSTOMER_NAME FROM CUSTOMERS c LEFT JOIN TRANSACTIONS t ON c.CUSTOMER_ID = t.CUSTOMER_ID WHERE t.CUSTOMER_ID IS NULL;"></textarea>

                <button type="submit" id="playBtn" class="cta">Create Video</button>
                <p class="note">Silent animation - the query is built logically: FROM, JOIN, ON, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT. Each new video gets a new background colour.</p>
            </form>
        </div>

        <!-- ============ MIDDLE: YOUTUBE TOOLS ============ -->
        <div class="card">
            <h2>YouTube Tools</h2>
            <div class="row">
                <button type="button" class="mini" id="btnTitle">Generate Title</button>
                <button type="button" class="mini" id="btnDesc">Generate Description</button>
                <button type="button" class="mini" id="btnTags">Generate Tags</button>
            </div>

            <div id="metaBox">
                <div class="meta-head">
                    <span class="meta-title" id="metaTitle">YouTube Metadata</span>
                    <button type="button" class="mini meta-copy" id="btnCopy">Copy</button>
                </div>
                <div class="meta-out" id="metaOut"></div>
            </div>

            <div class="row">
                <button type="button" class="mini" id="btnThumb">Create Thumbnail (9:16 PNG)</button>
            </div>

            <div id="thumbBox">
                <div class="meta-head">
                    <span class="meta-title">Thumbnail - 1080x1920 PNG</span>
                    <a id="thumbDl" class="mini-link" href="/download/thumbnail" download="youtube_short_thumbnail.png">Download PNG</a>
                </div>
                <div class="thumb-wrap">
                    <div class="thumb-status" id="thumbStatus">Rendering 1080 x 1920 PNG...</div>
                    <img id="thumbImg" alt="generated thumbnail" />
                </div>
            </div>
        </div>

        <!-- ============ RIGHT: LIVE MONITORING ============ -->
        <div class="card">
            <h2>Live Monitoring</h2>
            <div class="log-head">
                <span class="pill" id="statusPill">Idle</span>
                <span class="timer" id="timer"></span>
            </div>
            <div class="logs-box" id="logs">Ready. Fill in the Question box, the Query/Logic box, or both.</div>
        </div>
    </div>
</div>

<script>
    const form = document.getElementById('videoForm');
    const qBox = document.getElementById('question');
    const logicBox = document.getElementById('queryLogic');
    const logsDiv = document.getElementById('logs');
    const btn = document.getElementById('playBtn');
    const pill = document.getElementById('statusPill');
    const timerEl = document.getElementById('timer');
    const stageEls = document.querySelectorAll('.stage');

    const metaBox = document.getElementById('metaBox');
    const metaOut = document.getElementById('metaOut');
    const metaTitle = document.getElementById('metaTitle');
    const btnCopy = document.getElementById('btnCopy');
    const metaBtns = [document.getElementById('btnTitle'), document.getElementById('btnDesc'), document.getElementById('btnTags')];

    const btnThumb = document.getElementById('btnThumb');
    const thumbBox = document.getElementById('thumbBox');
    const thumbImg = document.getElementById('thumbImg');
    const thumbStatus = document.getElementById('thumbStatus');
    const thumbDl = document.getElementById('thumbDl');

    const STAGE_ORDER = ['learning', 'models', 'build', 'video', 'done'];
    let tickHandle = null;

    function setPill(text, cls) {
        pill.innerText = text;
        pill.className = 'pill' + (cls ? ' ' + cls : '');
    }

    function paintStages(stage, status) {
        const idx = STAGE_ORDER.indexOf(stage);
        stageEls.forEach(el => {
            const s = el.getAttribute('data-stage');
            el.classList.remove('active', 'done', 'error');
            const sIdx = STAGE_ORDER.indexOf(s);
            if (status === 'error' && sIdx === Math.max(idx, 0)) { el.classList.add('error'); return; }
            if (idx === -1) return;
            if (sIdx < idx || status === 'done') el.classList.add('done');
            else if (sIdx === idx && status !== 'done') el.classList.add('active');
        });
    }

    function startTimer(t0) {
        if (tickHandle) clearInterval(tickHandle);
        tickHandle = setInterval(() => { timerEl.innerText = 'Elapsed ' + ((Date.now() - t0) / 1000).toFixed(1) + 's'; }, 200);
    }
    function stopTimer() { if (tickHandle) clearInterval(tickHandle); tickHandle = null; }

    async function pollJob(jobId, t0) {
        let printed = 0;
        while (true) {
            let data;
            try {
                const r = await fetch('/status/' + jobId, { cache: 'no-store' });
                data = await r.json();
            } catch (e) {
                setPill('Connection lost', 'error');
                stopTimer();
                return;
            }
            if (data.logs && data.logs.length > printed) {
                const fresh = data.logs.slice(printed);
                printed = data.logs.length;
                for (const line of fresh) logsDiv.appendChild(document.createTextNode(line + '\n'));
                logsDiv.scrollTop = logsDiv.scrollHeight;
            }
            paintStages(data.stage, data.status);
            timerEl.innerText = 'Elapsed ' + ((Date.now() - t0) / 1000).toFixed(1) + 's';
            if (data.status === 'done') { setPill('Video ready', 'done'); stopTimer(); return; }
            if (data.status === 'error') { setPill('Failed', 'error'); stopTimer(); return; }
            if (data.status === 'running' || data.status === 'queued') {
                setPill(data.stage ? ('Working: ' + data.stage) : 'Working', 'running');
            }
            await new Promise(r => setTimeout(r, 600));
        }
    }

    form.onsubmit = async (e) => {
        e.preventDefault();
        const q = qBox.value.trim();
        const logic = logicBox.value.trim();
        if (!q && !logic) {
            logsDiv.textContent = 'Please fill in the Question box or the Query/Logic box.\n';
            return;
        }
        btn.disabled = true;
        btn.innerText = 'Creating video...';
        logsDiv.textContent = '';
        setPill('Starting...', 'running');
        const t0 = Date.now();
        paintStages('learning', 'running');
        startTimer(t0);
        try {
            const r = await fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({ question: q, query_logic: logic }).toString()
            });
            const res = await r.json();
            if (!res.job_id) {
                logsDiv.textContent += 'Error: ' + (res.error || 'the job did not start') + '\n';
                setPill('Failed', 'error');
                stopTimer();
            } else {
                await pollJob(res.job_id, t0);
            }
        } catch (err) {
            logsDiv.textContent += 'Error: ' + err.message + '\n';
            setPill('Failed', 'error');
            stopTimer();
        }
        btn.disabled = false;
        btn.innerText = 'Create Video';
    };

    // ---------- Title (Topic | Audience | Skill | Format), Description, Tags ----------
    function setMetaBusy(busy) { metaBtns.forEach(b => b.disabled = busy); }

    async function runMeta(kind) {
        const q = qBox.value.trim();
        const logic = logicBox.value.trim();
        const labels = { title: 'Title', description: 'Description', tags: 'Tags' };
        metaBox.style.display = 'block';
        metaTitle.innerText = labels[kind];
        metaOut.textContent = 'Generating ' + labels[kind].toLowerCase() + ' from the question and query...';
        setMetaBusy(true);
        try {
            const r = await fetch('/metadata', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({ question: q, query_logic: logic, kind: kind }).toString()
            });
            const res = await r.json();
            metaOut.textContent = res.text ? res.text : ('Error: ' + (res.error || 'the model could not generate this'));
        } catch (err) {
            metaOut.textContent = 'Error: ' + err.message;
        }
        setMetaBusy(false);
    }

    document.getElementById('btnTitle').onclick = () => runMeta('title');
    document.getElementById('btnDesc').onclick = () => runMeta('description');
    document.getElementById('btnTags').onclick = () => runMeta('tags');

    btnCopy.onclick = async () => {
        try { await navigator.clipboard.writeText(metaOut.innerText); btnCopy.innerText = 'Copied'; }
        catch (e) { btnCopy.innerText = 'Select all'; }
        setTimeout(() => { btnCopy.innerText = 'Copy'; }, 1200);
    };

    // ---------- Thumbnail (each thumbnail gets a new background colour) ----------
    btnThumb.onclick = async () => {
        const q = qBox.value.trim();
        const logic = logicBox.value.trim();
        thumbBox.style.display = 'block';
        thumbImg.style.display = 'none';
        thumbImg.removeAttribute('src');
        thumbStatus.style.display = 'block';
        thumbStatus.textContent = 'Rendering 1080 x 1920 PNG...';
        btnThumb.disabled = true;
        btnThumb.innerText = 'Creating thumbnail...';
        try {
            const r = await fetch('/thumbnail', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: new URLSearchParams({ question: q, query_logic: logic }).toString()
            });
            const res = await r.json();
            if (res.ok) {
                thumbImg.onload = () => { thumbStatus.style.display = 'none'; thumbImg.style.display = 'block'; };
                thumbImg.src = res.url;
                thumbDl.href = res.url;
                thumbDl.setAttribute('download', res.filename || 'youtube_short_thumbnail.png');
            } else {
                thumbStatus.textContent = 'Error: ' + (res.error || 'thumbnail failed');
            }
        } catch (err) {
            thumbStatus.textContent = 'Error: ' + err.message;
        }
        btnThumb.disabled = false;
        btnThumb.innerText = 'Create Thumbnail (9:16 PNG)';
    };
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return DASHBOARD_HTML


@app.post("/generate")
async def generate(question: str = Form(""), query_logic: str = Form("")):
    global live_logs
    live_logs = []

    question, query_logic = _clean_inputs(question, query_logic)

    if not question and not query_logic:
        return JSONResponse({"error": "Please fill in the Question box or the Query/Logic box"},
                            status_code=400)

    if not question:
        question = "Explain and animate this SQL query step by step"

    cutoff = time.time() - 3600
    with JOBS_LOCK:
        for jid in [k for k, v in JOBS.items() if v.get("started", 0) < cutoff]:
            JOBS.pop(jid, None)

        job_id = uuid.uuid4().hex[:12]
        JOBS[job_id] = {
            "logs": [],
            "status": "queued",
            "stage": "learning",
            "started": time.time(),
            "finished": None,
            "question": question[:200],
            "html": None,
            "html_ready": False,
        }

    threading.Thread(target=run_pipeline, args=(job_id, question, query_logic),
                     daemon=True).start()

    return JSONResponse({"job_id": job_id})


@app.get("/animation/{job_id}", response_class=HTMLResponse)
async def animation_page(job_id: str):
    """Shows the animation as soon as it is built; before that, a small loading page."""
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if job is None:
            return HTMLResponse("<h3 style='font-family:sans-serif'>Unknown or expired job.</h3>",
                                status_code=404)
        html_content = job.get("html")
    if html_content:
        return HTMLResponse(html_content)
    return HTMLResponse(LOADING_TEMPLATE.replace("__JOB_ID__", job_id))


@app.post("/metadata")
async def metadata(question: str = Form(""), query_logic: str = Form(""), kind: str = Form("title")):
    """Generate a YouTube title, description or hashtags with the AI model (text only)."""
    question, query_logic = _clean_inputs(question, query_logic)
    question, query_logic = _fill_from_last_run(question, query_logic, "METADATA")

    if not question and not query_logic:
        return JSONResponse({"error": "Please fill in the Question box or the Query/Logic box"},
                            status_code=400)

    text = await asyncio.to_thread(generate_metadata, question, query_logic, kind)
    if not text:
        return JSONResponse({"error": "the models could not generate this - please try again"})

    return JSONResponse({"kind": kind, "text": text})


@app.post("/thumbnail")
async def thumbnail(question: str = Form(""), query_logic: str = Form("")):
    """Create a fresh 1080x1920 (9:16) thumbnail PNG.

    Background alternates on every call (gradient, solid, ...) and each call gets a
    theme that differs from the recent ones.
    """
    question, query_logic = _clean_inputs(question, query_logic)
    question, query_logic = _fill_from_last_run(question, query_logic, "THUMBNAIL")

    if not question and not query_logic:
        return JSONResponse({"error": "Please fill in the Question box or the Query/Logic box"},
                            status_code=400)

    try:
        content = await asyncio.to_thread(create_thumbnail, question, query_logic)
    except Exception as e:
        log_message(f"THUMBNAIL ERROR: {str(e)[:120]}")
        return JSONResponse({"error": f"thumbnail render failed: {str(e)[:80]}"})

    return JSONResponse({
        "ok": True,
        "url": f"/download/thumbnail?ts={int(time.time())}",
        "filename": "youtube_short_thumbnail.png",
        "size": f"{THUMB_WIDTH}x{THUMB_HEIGHT}",
        "content": content,
    })


@app.get("/download/thumbnail")
async def download_thumbnail():
    """Serve the PNG unchanged, so the download keeps full 1080x1920 quality."""
    if not THUMBNAIL_PATH.exists():
        return JSONResponse({"error": "no thumbnail created yet"}, status_code=404)
    return FileResponse(str(THUMBNAIL_PATH),
                        media_type="image/png",
                        filename="youtube_short_thumbnail.png")


@app.get("/status/{job_id}")
async def job_status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if job is None:
            return JSONResponse({"error": "unknown job", "logs": [], "status": "error"}, status_code=404)

        elapsed = (job.get("finished") or time.time()) - job["started"]
        return JSONResponse({
            "job_id": job_id,
            "status": job["status"],
            "stage": job["stage"],
            "logs": list(job["logs"]),
            "count": len(job["logs"]),
            "elapsed": round(elapsed, 1),
            "html_ready": bool(job.get("html_ready")),
        })


# ============================================================
# STARTUP HELPERS
# ============================================================
def warm_up_models():
    """Load the main model into memory in the background so the first job starts faster."""
    try:
        log_message(f"WARM-UP: loading {MODELS_TO_TRY[0]} into memory...")
        ollama.generate(model=MODELS_TO_TRY[0], prompt="", keep_alive=OLLAMA_KEEP_ALIVE)
        log_message("WARM-UP: model ready")
    except Exception as e:
        log_message(f"WARM-UP skipped: {str(e)[:60]}")


def open_browser_correctly(url: str):
    try:
        time.sleep(2)
        if platform.system() == 'Windows':
            os.startfile(url)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', url])
        else:
            subprocess.Popen(['xdg-open', url])
        print(f"Opened {url}")
    except Exception:
        print(f"Open this URL manually: {url}")


if __name__ == "__main__":
    url = "http://127.0.0.1:8000"
    print(f"\nAI Video Generator Studio (v12)\nOpen: {url}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(HTML_SAVE_DIR, exist_ok=True)

    threading.Thread(target=warm_up_models, daemon=True).start()
    threading.Thread(target=open_browser_correctly, args=(url,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")
