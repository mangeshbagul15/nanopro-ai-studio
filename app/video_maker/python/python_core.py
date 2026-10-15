"""
@Code_With_Mangesh - AI Python Video Generator Studio
======================================================
Two input modes:
  1. Question-Code mode -> the Python code you paste is animated exactly as written
  2. Question + Logic   -> the AI writes the code, then it is animated the same way

SAMPLE DATA (taken from the code itself):
  The main literal data in the code decides the sample shape:
    list / tuple / set of scalars  -> chips   [ 101, 102, 101 ]
    list of dicts or tuples        -> table
    dict of scalars                -> KEY | VALUE table
    dict of lists / dicts          -> table
  File or database code (no literal) -> the column names used in the code are shown.


PROGRAM OUTPUT:
  The pasted code is run in a sandbox subprocess (5 second limit). The real printed
  output is shown. If the code needs a file or database, output is not shown.

PASTE REPAIR:
  Accidentally duplicated or unfinished statements are removed before animation.

TYPING MODEL (append-only):
  The program is split into top-level statements in FILE ORDER.
  Consecutive statements with the same label form one step.
  Every step only APPENDS new text to the editor. Nothing already typed is
  ever retyped. The final step only highlights the complete program.

AUDIO:
  The animation is completely silent.

THUMBNAIL BACKGROUND RULE:
  1st click -> mixed gradient, 2nd click -> one flat colour, and so on.
"""

import asyncio
import ast
import os
import sys
import json
import random
import re
import subprocess
import tempfile
import textwrap
import uuid
import threading
import time
import platform
import traceback
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
# MODELS - tried ONE BY ONE (no parallel race)
# ============================================================
MODELS_TO_TRY = [
    "qwen2.5-coder:7b",
    "qwen2.5-coder:3b",
    "gemma3:4b",
    "phi4-mini:latest",
    "llama3.2:3b",
]

METADATA_MODELS = [
    "qwen2.5-coder:3b",
    "phi4-mini:latest",
    "gemma3:4b",
    "llama3.2:3b",
    "qwen2.5-coder:7b",
]

live_logs = []
LAST_RUN = {}

# ============================================================
# LIVE JOB TRACKING
# ============================================================
JOBS = {}
JOBS_LOCK = threading.Lock()
PIPELINE_LOCK = threading.Lock()
THUMB_LOCK = threading.Lock()
_thread_ctx = threading.local()


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
MAX_ATTEMPTS_PER_MODEL = 1
RECORD_WIDTH = 1080
RECORD_HEIGHT = 1920
END_CARD_STOP_MS = 1500

MIN_SAMPLE_ROWS = 5
MAX_SHOWN_SAMPLE_ROWS = 8
MAX_BUBBLE_CHARS = 58
MAX_PROCESS_CHARS = 62
PROGRAM_RUN_TIMEOUT_S = 5
MAX_OUTPUT_LINES = 10

THUMB_WIDTH = 1080
THUMB_HEIGHT = 1920
THUMB_SAFE_LEFT = 70
THUMB_SAFE_RIGHT = 200
THUMB_SAFE_TOP = 150
THUMB_SAFE_BOTTOM = 230

LEARNING_STORE_PATH = Path(r"C:\Mangesh\AI video\learning\learning_store_python.json")
THUMBNAIL_PATH = Path(r"C:\Mangesh\AI video\Output_Files\youtube_short_thumbnail.png")
MAX_LEARNING_EXAMPLES = 25
MAX_FEWSHOT_EXAMPLES = 3

OLLAMA_KEEP_ALIVE = "30m"
OLLAMA_OPTIONS = {
    "temperature": 0.25,
    "num_ctx": 8192,
    "num_predict": 1500,
    "top_p": 0.9,
    "repeat_penalty": 1.05,
}

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "question_banner": {"type": "string"},
        "dataset_name": {"type": "string"},
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
        "chips": {"type": "array", "items": {"type": "string"}},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "code": {"type": "string"},
                    "explanation": {"type": "string"},
                    "bubble": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["code", "explanation", "bubble"],
            },
        },
        "cleaned_output": {
            "type": "array",
            "items": {"type": "array", "items": {"type": "string"}},
        },
    },
    "required": ["question_banner", "dataset_name", "process_summary", "sample_data",
                 "table_headers", "chips", "steps", "cleaned_output"],
}

THUMBNAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "badge": {"type": "string"},
        "headline": {"type": "string"},
        "highlight": {"type": "string"},
        "subheadline": {"type": "string"},
        "code_snippet": {"type": "string"},
        "bullets": {"type": "array", "items": {"type": "string"}},
        "footer": {"type": "string"},
        "theme": {"type": "string"},
    },
    "required": ["badge", "headline", "highlight", "subheadline", "code_snippet",
                 "bullets", "footer", "theme"],
}

KEY_ALIASES = {
    "question_banner": ["question_banner", "question", "questionbanner", "banner", "title"],
    "dataset_name": ["dataset_name", "table_name", "dataset", "variable", "input_name"],
    "logic_explanation": ["logic_explanation", "logicexplanation", "logic", "explanation", "approach"],
    "process_summary": ["process_summary", "processsummary", "process", "how_it_runs",
                        "process_steps", "summary"],
    "sample_data": ["sample_data", "sampledata", "sample_input", "sample_table", "table_data",
                    "data", "rows", "sample_rows", "input_data", "records"],
    "table_headers": ["table_headers", "tableheaders", "headers", "columns", "fields"],
    "chips": ["chips", "step_chips", "step_titles", "titles"],
    "steps": ["steps", "code_steps", "python_steps", "step_list"],
    "cleaned_output": ["cleaned_output", "cleanedoutput", "expected_output", "printed_output",
                       "final_output", "output", "result", "results"],
}

FORBIDDEN_PY_CALLS = ("input(", "eval(", "exec(", "os.system", "subprocess", "socket",
                      "requests.", "urllib", "__import__(")
FORBIDDEN_PY_MODULES = ("os", "subprocess", "socket", "requests", "urllib", "sys")

ALLOWED_LABELS = [
    "Understand Requirement", "Import Libraries", "Define Constants", "Define Function",
    "Define Class", "Create Data", "Read Input", "Validate Input", "Transform Data",
    "Filter Records", "Loop Over Items", "Apply Condition", "Handle Error",
    "Aggregate Values", "Build Dictionary", "Build List", "Sort Results",
    "Use Helper Function", "Return Result", "Print Output", "Add Main Guard",
    "Modify Existing Code", "Validate Logic", "Review Result", "Optimize Code", "Final Code",
    "Connect Database", "Write Output File", "Send Notification", "Commit Transaction",
]

CODE_BUBBLES = {
    "Understand Requirement": ["What: The problem", "Why: Know the goal", "Result: Plan ready"],
    "Import Libraries": ["What: import statement", "Why: Bring tools in", "Result: Modules ready"],
    "Define Constants": ["What: Module constants", "Why: Fixed values once", "Result: Names ready"],
    "Define Function": ["What: def block", "Why: Reuse logic", "Result: Callable function"],
    "Define Class": ["What: class block", "Why: Group data and methods", "Result: Class ready"],
    "Create Data": ["What: Input data", "Why: Something to process", "Result: Data ready"],
    "Read Input": ["What: File or input read", "Why: Get the records", "Result: Records loaded"],
    "Validate Input": ["What: Input check", "Why: Reject bad values", "Result: Clean input"],
    "Transform Data": ["What: Data change", "Why: Shape the values", "Result: New values"],
    "Filter Records": ["What: Filter step", "Why: Keep matching items", "Result: Fewer items"],
    "Loop Over Items": ["What: for loop", "Why: Visit each item", "Result: Items processed"],
    "Apply Condition": ["What: if statement", "Why: Choose a path", "Result: Branch decided"],
    "Handle Error": ["What: try / except", "Why: Stay safe on errors", "Result: Error handled"],
    "Aggregate Values": ["What: Aggregate call", "Why: Combine the values", "Result: One value"],
    "Build Dictionary": ["What: Dict built", "Why: Map key to value", "Result: Lookup ready"],
    "Build List": ["What: List built", "Why: Collect results", "Result: List ready"],
    "Sort Results": ["What: sorted() call", "Why: Put items in order", "Result: Ordered items"],
    "Use Helper Function": ["What: Function call", "Why: Reuse the helper", "Result: Value returned"],
    "Return Result": ["What: return", "Why: Send value back", "Result: Value ready"],
    "Print Output": ["What: print()", "Why: Show the answer", "Result: Visible output"],
    "Add Main Guard": ["What: __main__ guard", "Why: Run only as script", "Result: Entry point set"],
    "Modify Existing Code": ["What: Change code", "Why: Fix the logic", "Result: Code updated"],
    "Validate Logic": ["What: Logic check", "Why: Catch mistakes", "Result: Logic verified"],
    "Review Result": ["What: Output check", "Why: Confirm the answer", "Result: Answer confirmed"],
    "Optimize Code": ["What: Faster version", "Why: Less work", "Result: Better code"],
    "Final Code": ["What: Complete program", "Why: All parts joined", "Result: Ready to run"],
    "Connect Database": ["What: DB connection", "Why: Reach the table", "Result: Connected"],
    "Write Output File": ["What: File written", "Why: Keep an audit copy", "Result: File saved"],
    "Send Notification": ["What: Email sent", "Why: Tell the team", "Result: Notified"],
    "Commit Transaction": ["What: commit()", "Why: Save all changes", "Result: Data stored"],
}

DIM_LABELS = {"Apply Condition", "Filter Records", "Aggregate Values", "Sort Results",
              "Return Result", "Print Output"}

READ_NAMES = {"open", "DictReader", "reader", "read_csv", "read_excel", "load", "loads",
              "readlines", "read_text"}
WRITE_NAMES = {"to_excel", "to_csv", "write", "writelines", "dump", "write_text"}
DB_NAMES = {"connect", "cursor", "execute", "executemany", "rollback"}
MAIL_NAMES = {"SMTP", "sendmail", "send_message", "starttls", "login", "EmailMessage"}
AGG_NAMES = {"sum", "len", "max", "min", "count", "Counter", "groupby", "mean", "average"}
BLOCK_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.If, ast.For,
               ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try)


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


def python_has_valid_syntax(code: str) -> bool:
    try:
        ast.parse(str(code or ""))
        return True
    except SyntaxError:
        return False


# ============================================================
# PASTE REPAIR (removes accidentally duplicated, unfinished statements)
# ============================================================
def _open_bracket_depth(lines: list) -> int:
    """Number of brackets still open at the end of these lines (strings and comments ignored)."""
    depth = 0
    quote = None
    for line in lines:
        i = 0
        while i < len(line):
            ch = line[i]
            if quote:
                if ch == "\\":
                    i += 2
                    continue
                if ch == quote:
                    quote = None
            elif ch in ("'", '"'):
                quote = ch
            elif ch == "#":
                break
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth = max(0, depth - 1)
            i += 1
    return depth


def repair_pasted_code(text: str):
    """Return (repaired_text, removed_line_count).

    A top-level line (no indentation) is a new statement. If an earlier statement is
    still open (unclosed bracket) and the same top-level line appears again, the
    earlier broken copy is removed and the new copy is kept."""
    lines = str(text or "").replace("\r\n", "\n").split("\n")
    out = []
    removed = 0
    for line in lines:
        starts_statement = bool(line.strip()) and not line[:1].isspace()
        if starts_statement and _open_bracket_depth(out) > 0:
            key = line.rstrip()
            earlier = None
            for idx, prev in enumerate(out):
                if prev.rstrip() == key and not prev[:1].isspace():
                    earlier = idx
                    break
            if earlier is not None:
                removed += len(out) - earlier
                out = out[:earlier]
        out.append(line)
    cleaned = "\n".join(out).strip("\n")
    return cleaned, removed


def split_query_logic(text: str):
    """Return (user_code, user_logic) from the Code/Logic box.
    Pasted code is repaired first, so accidental duplicate lines do not reach the animation."""
    text = (text or "").strip()
    if not text:
        return "", ""

    repaired, removed = repair_pasted_code(text)
    if removed:
        log_message(f"PASTE REPAIR: removed {removed} duplicated / unfinished line(s) from the pasted code")

    if python_has_valid_syntax(repaired):
        return repaired, ""
    if re.search(r"^\s*(def|class|import|from)\s", repaired, re.MULTILINE):
        return repaired, ""
    return "", text


# ============================================================
# SAMPLE DATA - taken from the code's own literal data
# ============================================================
def _type_name(values) -> str:
    names = {type(v).__name__ for v in values}
    return names.pop() if len(names) == 1 else "mixed"


def _ordered_union(key_lists) -> list:
    out = []
    for keys in key_lists:
        for k in keys:
            if k not in out:
                out.append(k)
    return out


def _usage_counts(tree) -> dict:
    counts = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            counts[node.id] = counts.get(node.id, 0) + 1
    return counts


def find_sample_source(code: str):
    """Return (name, value) of the most-used top-level literal collection, or None.
    Example: ids = [101, 102, 101] used in Counter(ids) is chosen."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    usage = _usage_counts(tree)
    best = None
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            continue
        try:
            value = ast.literal_eval(node.value)
        except Exception:
            continue
        if not isinstance(value, (list, tuple, set, frozenset, dict)) or len(value) == 0:
            continue
        name = node.targets[0].id
        score = usage.get(name, 0)
        if best is None or score > best[0]:
            best = (score, name, value)
    return (best[1], best[2]) if best else None


def build_sample_view(name: str, value) -> dict:
    """Shape the sample exactly like the literal in the code.
    kind 'list'  -> chips inside [ ]
    kind 'table' -> table with headers"""
    if isinstance(value, dict):
        items = list(value.items())
        if items and all(isinstance(v, dict) for _, v in items):
            keys = _ordered_union([v.keys() for _, v in items])
            headers = ["KEY"] + [str(k) for k in keys]
            rows = [[str(k)] + [str(v.get(kk, "")) for kk in keys] for k, v in items]
            label = f"dict of {len(items)} records"
        elif items and all(isinstance(v, (list, tuple)) for _, v in items) \
                and len({len(v) for _, v in items}) == 1:
            count = len(items[0][1])
            headers = [str(k) for k, _ in items]
            rows = [[str(v[i]) for _, v in items] for i in range(count)]
            label = f"dict of {len(items)} columns"
        else:
            headers = ["KEY", "VALUE"]
            rows = [[repr(k), repr(v)] for k, v in items]
            label = f"dict of {len(items)} keys"
        kind = "table"
    else:
        seq = list(value)
        if isinstance(value, (set, frozenset)):
            try:
                seq = sorted(seq)
            except TypeError:
                pass
        container = {list: "list", tuple: "tuple", set: "set", frozenset: "set"}.get(type(value), "list")

        if all(isinstance(v, dict) for v in seq):
            keys = _ordered_union([v.keys() for v in seq])
            headers = [str(k) for k in keys]
            rows = [[str(v.get(k, "")) for k in keys] for v in seq]
            kind = "table"
            label = f"{container} of {len(seq)} dict records"
        elif all(isinstance(v, (list, tuple)) for v in seq) \
                and len({len(v) for v in seq}) == 1 and len(seq[0]) > 1:
            headers = [f"COL_{i + 1}" for i in range(len(seq[0]))]
            rows = [[str(x) for x in v] for v in seq]
            kind = "table"
            label = f"{container} of {len(seq)} rows"
        else:
            headers = []
            rows = [[repr(v)] for v in seq]
            kind = "list"
            label = f"{container} of {len(seq)} {_type_name(seq)} items"

    total = len(rows)
    note = ""
    if total > MAX_SHOWN_SAMPLE_ROWS:
        note = f"+{total - MAX_SHOWN_SAMPLE_ROWS} more not shown"
        rows = rows[:MAX_SHOWN_SAMPLE_ROWS]

    return {
        "kind": kind,
        "name": name,
        "title": f"{name}  =  {label}",
        "headers": headers,
        "rows": rows,
        "note": note,
        "source": "code literal",
    }


def find_source_headers(code: str):
    """For file / database code with no literal data: the column names used in the code
    (for example row["EMP_ID"]) and the file name. Returns (headers, file_name)."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [], ""

    found = []
    file_name = ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            sl = node.slice
            if isinstance(sl, ast.Constant) and isinstance(sl.value, str) \
                    and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ ]*", sl.value):
                found.append((node.lineno, node.col_offset, sl.value))
        if isinstance(node, ast.Call) and not file_name:
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else "")
            if name in READ_NAMES and node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                file_name = node.args[0].value

    headers = []
    for _, _, value in sorted(found):
        if value not in headers:
            headers.append(value)
    return headers, file_name


def resolve_sample_view(final_code: str, data: dict) -> dict:
    """Priority: literal data in the code > column names used by file/DB code > AI sample."""
    if final_code and python_has_valid_syntax(final_code):
        src = find_sample_source(final_code)
        if src:
            view = build_sample_view(*src)
            log_message(f"SAMPLE: {view['title']} (taken from the code)")
            return view

        headers, file_name = find_source_headers(final_code)
        if headers:
            title = f"{file_name or 'source'}  =  input columns"
            log_message(f"SAMPLE: input columns {', '.join(headers)} (rows come from the source at run time)")
            return {
                "kind": "table",
                "name": file_name or "source",
                "title": title,
                "headers": headers,
                "rows": [["..."] * len(headers)],
                "note": "Real rows come from the source file or table when the code runs",
                "source": "code columns",
            }

    model_rows = [list(r.get("cols") or []) for r in (data.get("sample_data") or [])]
    headers = _as_str_list(data.get("table_headers"))
    dataset = str(data.get("dataset_name") or "data")
    if model_rows:
        if len(headers) <= 1:
            return {"kind": "list", "name": dataset, "title": f"{dataset}  =  sample",
                    "headers": [], "rows": [[r[0] if r else ""] for r in model_rows],
                    "note": "", "source": "AI sample"}
        return {"kind": "table", "name": dataset, "title": f"{dataset}  =  sample",
                "headers": headers, "rows": model_rows, "note": "", "source": "AI sample"}

    return {"kind": "list", "name": dataset, "title": f"{dataset}  =  no sample",
            "headers": [], "rows": [["-"]], "note": "", "source": "none"}


def _matching_rows(rows: list, output_lines: list):
    """Rows whose value is printed in the program output. None when unknown."""
    tokens = set(re.findall(r"[A-Za-z0-9_.\-]+", " ".join(output_lines or [])))
    if not tokens:
        return None
    hit = []
    for i, cols in enumerate(rows):
        for c in cols:
            if c.strip("'\"") in tokens or c in tokens:
                hit.append(i)
                break
    return hit or None


# ============================================================
# PROGRAM OUTPUT (real run in a sandbox subprocess)
# ============================================================
def run_program_output(code: str) -> list:
    """Run the code and capture printed lines. Returns [] if the code needs files,
    a database or network, fails, or runs too long."""
    if not code.strip() or validate_python_code(code):
        return []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "sample_run.py"
            script.write_text(code, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(script)],
                cwd=tmp,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=PROGRAM_RUN_TIMEOUT_S,
                env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            )
    except subprocess.TimeoutExpired:
        log_message("OUTPUT: program took too long - output not shown")
        return []
    except Exception as e:
        log_message(f"OUTPUT: could not run the sample ({str(e)[:60]})")
        return []

    if proc.returncode != 0:
        log_message("OUTPUT: code needs a file or database - output not shown in the reel")
        return []

    lines = [ln.rstrip() for ln in proc.stdout.splitlines() if ln.strip()]
    log_message(f"OUTPUT: {len(lines)} line(s) captured from a real run")
    return lines[:MAX_OUTPUT_LINES]


def normalize_label(text: str) -> str:
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


# ============================================================
# PYTHON FORMATTER (4-space indentation, keeps the real structure)
# ============================================================
PY_INDENT = "    "
_CONTINUATION_RE = re.compile(r"^(else|elif|except|finally)\b")


def _normalise_tabs_and_trailing(code: str) -> str:
    lines = str(code or "").replace("\t", PY_INDENT).replace("\r\n", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip("\n")


def format_python(code: str) -> str:
    """Clean, aligned Python with 4-space indentation. Idempotent."""
    text = _normalise_tabs_and_trailing(code)
    if not text:
        return ""

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return textwrap.dedent(text).strip("\n")

    lines = text.split("\n")

    starts = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue
        idxs = [node.lineno - 1]
        idxs += [d.lineno - 1 for d in getattr(node, "decorator_list", [])]
        for idx in idxs:
            if idx < len(lines) and lines[idx][:node.col_offset].strip() == "":
                starts[idx] = node.col_offset

    levels = sorted(set(starts.values()))

    def depth_of(width: int) -> int:
        depth = 0
        for i, level in enumerate(levels):
            if level <= width:
                depth = i
        return depth

    out = []
    anchor_old = 0
    anchor_new = 0
    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            out.append("")
            continue
        width = len(raw) - len(raw.lstrip(" "))

        if idx in starts:
            anchor_old = width
            anchor_new = depth_of(width) * len(PY_INDENT)
            out.append(" " * anchor_new + stripped)
        elif stripped.startswith("#") or _CONTINUATION_RE.match(stripped):
            out.append(" " * (depth_of(width) * len(PY_INDENT)) + stripped)
        else:
            new_width = anchor_new + max(0, width - anchor_old)
            out.append(" " * new_width + stripped)

    result = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip("\n")

    try:
        ast.parse(result)
    except SyntaxError:
        return textwrap.dedent(text).strip("\n")
    return result


# ============================================================
# STATEMENT SEGMENTS (file order, one entry per top-level statement)
# ============================================================
def _call_names(node) -> set:
    names = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
                if isinstance(func.value, ast.Name):
                    names.add(func.value.id)
        if isinstance(sub, ast.Name):
            names.add(sub.id)
    return names


def _is_literal(value) -> bool:
    try:
        ast.literal_eval(value)
        return True
    except Exception:
        return False


def _is_main_guard(node) -> bool:
    test = node.test
    return (isinstance(test, ast.Compare) and isinstance(test.left, ast.Name)
            and test.left.id == "__name__")


def _is_print(node) -> bool:
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name) and node.value.func.id == "print")


def _label_for_node(node) -> str:
    """One label per top-level statement, chosen from what the statement does."""
    calls = _call_names(node)

    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return "Import Libraries"
    if isinstance(node, ast.ClassDef):
        return "Define Class"
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return "Define Function"
    if isinstance(node, ast.Assign) and node.targets and all(
            isinstance(t, ast.Name) and t.id.isupper() for t in node.targets):
        return "Define Constants"
    if isinstance(node, ast.If) and _is_main_guard(node):
        return "Add Main Guard"
    if isinstance(node, ast.Try):
        return "Handle Error"
    if isinstance(node, ast.Return):
        return "Return Result"
    if _is_print(node):
        return "Print Output"
    if calls & MAIL_NAMES:
        return "Send Notification"
    if calls & WRITE_NAMES:
        return "Write Output File"
    if "commit" in calls:
        return "Commit Transaction"
    if calls & DB_NAMES or "connect" in calls:
        return "Connect Database"
    if calls & READ_NAMES:
        return "Read Input"
    if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
        return "Loop Over Items"
    if isinstance(node, ast.If):
        return "Apply Condition"
    if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
        value = node.value
        if _is_literal(value):
            return "Create Data"
        if isinstance(value, ast.ListComp):
            return "Filter Records" if any(g.ifs for g in value.generators) else "Build List"
        if isinstance(value, (ast.Dict, ast.DictComp)):
            return "Build Dictionary"
    if "sort" in calls or "sorted" in calls:
        return "Sort Results"
    if calls & AGG_NAMES:
        return "Aggregate Values"
    if "append" in calls:
        return "Build List"
    return "Transform Data"


def _statement_segments(final_code: str) -> list:
    """Each top-level statement, in file order, as one complete text block.
    Comment lines directly above a statement stay with it."""
    tree = ast.parse(final_code)
    lines = final_code.split("\n")
    segs = []
    prev_end = 0
    for node in tree.body:
        end = node.end_lineno
        chunk = lines[prev_end:end]
        prev_end = end
        while chunk and not chunk[0].strip():
            chunk = chunk[1:]
        text = "\n".join(chunk).rstrip()
        segs.append({
            "text": text,
            "block": isinstance(node, BLOCK_NODES),
            "label": _label_for_node(node),
        })

    tail = "\n".join(lines[prev_end:]).strip("\n")
    if tail.strip():
        if segs:
            segs[-1]["text"] = segs[-1]["text"] + "\n" + tail.rstrip()
        else:
            segs.append({"text": tail.rstrip(), "block": False, "label": "Transform Data"})
    return segs


def _group_statements(segs: list) -> list:
    """Consecutive statements with the same label become one step."""
    groups = []
    for seg in segs:
        if groups and groups[-1][0] == seg["label"]:
            groups[-1][1].append(seg)
        else:
            groups.append((seg["label"], [seg]))
    return groups


def _result_rows(data: dict):
    """(all_rows, result_rows). Result rows are the sample rows whose value shows in the output."""
    sample = data.get("sample_data") or []
    all_rows = list(range(len(sample)))
    cols = [list(s.get("cols") or []) for s in sample]
    hit = _matching_rows(cols, data.get("output_lines") or [])
    result_rows = hit if hit else all_rows
    return all_rows, result_rows


def build_typing_steps(final_code: str, data: dict):
    """Return (steps, full_code). Every step only APPENDS text to the editor."""
    question = str(data.get("question_banner") or "")
    all_rows, result_rows = _result_rows(data)

    steps = [{
        "label": "Understand Requirement",
        "typed": "",
        "active_from": 0,
        "active_to": 0,
        "bubble": CODE_BUBBLES["Understand Requirement"],
        "explanation": clamp_text(question, 90),
        "rows": all_rows,
        "dim": False,
    }]

    code = ""
    last_block = False
    for label, group in _group_statements(_statement_segments(final_code)):
        typed = ""
        active_from = None
        for seg in group:
            sep = ""
            if code:
                sep = "\n\n" if (seg["block"] or last_block) else "\n"
            if active_from is None:
                active_from = (code + sep).count("\n")
            chunk = sep + seg["text"]
            typed += chunk
            code += chunk
            last_block = seg["block"]

        dim = label in DIM_LABELS
        steps.append({
            "label": label,
            "typed": typed,
            "active_from": active_from,
            "active_to": code.count("\n"),
            "bubble": CODE_BUBBLES.get(label, CODE_BUBBLES["Transform Data"]),
            "explanation": "",
            "rows": result_rows if dim else all_rows,
            "dim": dim,
        })

    steps.append({
        "label": "Final Code",
        "typed": "",
        "active_from": 0,
        "active_to": 99999,
        "bubble": CODE_BUBBLES["Final Code"],
        "explanation": "Complete program in the correct Python format",
        "rows": result_rows,
        "dim": any(s["dim"] for s in steps[1:]),
    })
    return steps, code


def build_single_step(final_code: str, data: dict):
    """Fallback for code that cannot be split: the whole program is typed once."""
    question = str(data.get("question_banner") or "")
    all_rows, result_rows = _result_rows(data)
    steps = [
        {
            "label": "Understand Requirement",
            "typed": "",
            "active_from": 0,
            "active_to": 0,
            "bubble": CODE_BUBBLES["Understand Requirement"],
            "explanation": clamp_text(question, 90),
            "rows": all_rows,
            "dim": False,
        },
        {
            "label": "Final Code",
            "typed": final_code,
            "active_from": 0,
            "active_to": 99999,
            "bubble": CODE_BUBBLES["Final Code"],
            "explanation": "Complete program in the correct Python format",
            "rows": result_rows,
            "dim": False,
        },
    ]
    return steps, final_code


# ============================================================
# REEL BACKGROUND THEMES
# ============================================================
def _mk_reel_theme(name, bg, glow1, glow2, panel, border, accent, accent2,
                   text="#f8fafc", muted="#94a3b8", editor="rgba(9,13,24,.94)",
                   grid="rgba(148,163,184,.07)"):
    return {
        "name": name, "bg": bg, "glow1": glow1, "glow2": glow2,
        "panel": panel, "border": border, "accent": accent, "accent2": accent2,
        "text": text, "muted": muted, "editor": editor, "grid": grid,
    }


REEL_THEMES = {
    "midnight": _mk_reel_theme(
        "Midnight Blue",
        "radial-gradient(circle at 12% 6%, #16305c 0%, rgba(11,17,33,0) 55%),"
        " radial-gradient(circle at 88% 96%, #1f2a55 0%, rgba(11,17,33,0) 58%),"
        " linear-gradient(160deg, #0b1121 0%, #080d18 62%, #05070d 100%)",
        "rgba(56,189,248,.20)", "rgba(167,139,250,.18)",
        "rgba(30,41,59,.90)", "#334155", "#38bdf8", "#4ade80"),
    "violet": _mk_reel_theme(
        "Deep Violet",
        "radial-gradient(circle at 14% 8%, #331a5e 0%, rgba(12,8,24,0) 56%),"
        " radial-gradient(circle at 88% 94%, #3d1547 0%, rgba(12,8,24,0) 58%),"
        " linear-gradient(160deg, #120b24 0%, #0c0718 62%, #06040d 100%)",
        "rgba(167,139,250,.22)", "rgba(244,114,182,.16)",
        "rgba(38,30,60,.90)", "#41355f", "#c4b5fd", "#f472b6"),
    "emerald": _mk_reel_theme(
        "Emerald Analytics",
        "radial-gradient(circle at 12% 6%, #0e4437 0%, rgba(5,18,16,0) 56%),"
        " radial-gradient(circle at 90% 94%, #10384a 0%, rgba(5,18,16,0) 58%),"
        " linear-gradient(160deg, #071b18 0%, #05120f 62%, #020806 100%)",
        "rgba(74,222,128,.20)", "rgba(45,212,191,.16)",
        "rgba(22,44,40,.90)", "#2c4a44", "#4ade80", "#2dd4bf"),
    "navy": _mk_reel_theme(
        "Navy Grid",
        "radial-gradient(circle at 10% 4%, #123054 0%, rgba(7,14,26,0) 56%),"
        " radial-gradient(circle at 92% 96%, #0d2740 0%, rgba(7,14,26,0) 58%),"
        " linear-gradient(160deg, #081626 0%, #060f1b 62%, #03070d 100%)",
        "rgba(56,189,248,.18)", "rgba(96,165,250,.16)",
        "rgba(17,34,54,.92)", "#2a4360", "#60a5fa", "#38bdf8",
        grid="rgba(148,197,253,.09)"),
    "amber": _mk_reel_theme(
        "Amber Ink",
        "radial-gradient(circle at 12% 6%, #4a2a0e 0%, rgba(18,10,5,0) 56%),"
        " radial-gradient(circle at 90% 94%, #3d1a2c 0%, rgba(18,10,5,0) 58%),"
        " linear-gradient(160deg, #1b1008 0%, #130b06 62%, #0a0503 100%)",
        "rgba(251,191,36,.20)", "rgba(244,114,182,.14)",
        "rgba(44,32,20,.92)", "#5a4527", "#fbbf24", "#f97316"),
    "graphite": _mk_reel_theme(
        "Graphite",
        "radial-gradient(circle at 12% 6%, #2b323b 0%, rgba(12,14,17,0) 56%),"
        " radial-gradient(circle at 90% 94%, #1f2a1a 0%, rgba(12,14,17,0) 58%),"
        " linear-gradient(160deg, #15181c 0%, #101215 62%, #08090b 100%)",
        "rgba(163,230,53,.16)", "rgba(148,163,184,.16)",
        "rgba(30,34,39,.92)", "#3a4149", "#a3e635", "#22d3ee"),
    "crimson": _mk_reel_theme(
        "Crimson Ink",
        "radial-gradient(circle at 12% 5%, #5a1024 0%, rgba(16,5,9,0) 54%),"
        " radial-gradient(circle at 92% 96%, #3b1050 0%, rgba(16,5,9,0) 56%),"
        " linear-gradient(158deg, #1c070e 0%, #120408 62%, #080204 100%)",
        "rgba(248,113,113,.20)", "rgba(217,70,239,.14)",
        "rgba(48,20,28,.92)", "#5a2a36", "#fb7185", "#f87171"),
}

LAST_REEL_THEME = {"key": ""}


def choose_reel_theme(question: str, code: str) -> dict:
    text = f"{question} {code}".lower()

    if any(k in text for k in ("try", "except", "error", "exception", "validation", "raise")):
        want = "crimson"
    elif any(k in text for k in ("class", "object", "inherit", "decorator", "recursion",
                                 "__init__", "self.")):
        want = "violet"
    elif any(k in text for k in ("pandas", "groupby", "sum(", "count(", "average", "mean(",
                                 "len(", "analysis", "dataframe", "counter", "oracle", "execute(",
                                 "duplicate", "snowflake")):
        want = "emerald"
    elif any(k in text for k in ("file", "json", "api", "request", "csv", "loop", "for ",
                                 "excel", "read_excel", "smtp", "email")):
        want = "navy"
    elif any(k in text for k in ("date", "time", "datetime", "timedelta", "month", "year")):
        want = "amber"
    elif any(k in text for k in ("delete", "update", "pop(", "remove", "modify")):
        want = "graphite"
    else:
        want = "midnight"

    keys = list(REEL_THEMES.keys())
    if want == LAST_REEL_THEME["key"]:
        want = keys[(keys.index(want) + 1) % len(keys)]
    LAST_REEL_THEME["key"] = want
    return REEL_THEMES[want]


# ============================================================
# LEARNING / TRAINING MEMORY
# ============================================================
def load_learning_store() -> list:
    try:
        if LEARNING_STORE_PATH.exists():
            with open(LEARNING_STORE_PATH, "r", encoding="utf-8") as f:
                store = json.load(f)
            examples = store.get("examples", []) if isinstance(store, dict) else store
            if isinstance(examples, list):
                return examples
    except Exception as e:
        log_message(f"WARNING: learning memory read skipped: {str(e)[:60]}")
    return []


def _summary_of_example(ex: dict) -> dict:
    return {
        "question_banner": ex.get("question_banner", ex.get("question", "")),
        "dataset_name": ex.get("dataset_name", "data"),
        "logic_explanation": ex.get("logic_explanation", ""),
        "process_summary": ex.get("process_summary", []),
        "table_headers": ex.get("table_headers", []),
        "sample_data": ex.get("sample_data", []),
        "steps": [
            {
                "code": s.get("code", ""),
                "explanation": s.get("explanation", ""),
                "bubble": s.get("bubble", []),
            }
            for s in ex.get("steps", [])
        ],
        "cleaned_output": ex.get("cleaned_output", []),
    }


def save_learning_example(question: str, data: dict, model_name: str):
    try:
        LEARNING_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        examples = load_learning_store()

        q_key = question.strip().lower()
        examples = [ex for ex in examples
                    if str(ex.get("question", "")).strip().lower() != q_key]

        record = _summary_of_example(data)
        record["question"] = question
        record["learned_from_model"] = model_name
        record["learned_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        examples.append(record)
        examples = examples[-MAX_LEARNING_EXAMPLES:]

        with open(LEARNING_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump({"examples": examples}, f, ensure_ascii=False, indent=2)

        log_message(f"LEARNED + SAVED. Memory now holds {len(examples)} example(s)")
    except Exception as e:
        log_message(f"WARNING: could not save to learning memory: {str(e)[:60]}")


def build_few_shot_block(examples: list) -> str:
    if not examples:
        return ""

    blocks = [json.dumps(_summary_of_example(ex), ensure_ascii=False, indent=2)
              for ex in examples[-MAX_FEWSHOT_EXAMPLES:]]

    return (
        "LEARNED EXAMPLES (your own previous CORRECT answers - copy this style, depth and exact JSON shape):\n"
        + "\n".join(blocks)
        + "\n\nUse the above ONLY as a style reference. "
          "The CURRENT question below must be answered with fresh, correct Python of the same quality."
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
        headers = headers + [f"VALUE_{i + 1}" for i in range(len(headers), width)]

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
        log_message(f"SAMPLE INPUT: padded {before} -> {len(sample_data)} rows")

    raw_steps = found.get("steps")
    if not isinstance(raw_steps, list):
        raw_steps = []
    steps = []
    for s in raw_steps:
        if isinstance(s, str):
            steps.append({"code": s.strip(), "explanation": "", "bubble": ["", "", ""]})
            continue
        if not isinstance(s, dict):
            continue
        code = str(s.get("code") or s.get("query") or s.get("source") or "").strip()
        explanation = clamp_text(s.get("explanation") or s.get("description") or "", 120)
        bubble = [clamp_text(b, MAX_BUBBLE_CHARS)
                  for b in _as_str_list(s.get("bubble") or s.get("bullets") or s.get("notes"),
                                        pad_to=3)[:3]]
        steps.append({"code": code, "explanation": explanation, "bubble": bubble})

    raw_chips = _as_str_list(found.get("chips"))
    chips = []
    for c in raw_chips:
        label = normalize_label(c)
        if label:
            chips.append(label)
        elif c.strip():
            log_message(f"CHIP: '{clamp_text(c, 30)}' is not in the allowed label list - ignored")

    process = [clamp_text(p, MAX_PROCESS_CHARS)
               for p in _as_str_list(found.get("process_summary")) if p.strip()]

    return {
        "question_banner": str(found.get("question_banner") or question or "Python Program"),
        "dataset_name": str(found.get("dataset_name") or "data"),
        "logic_explanation": str(found.get("logic_explanation") or ""),
        "process_summary": process,
        "sample_data": sample_data,
        "table_headers": headers,
        "chips": chips,
        "steps": steps,
        "cleaned_output": cleaned_output,
    }


def pad_sample_data(sample_data: list, minimum: int = MIN_SAMPLE_ROWS) -> list:
    """Only for AI-written samples (never for literal data taken from the code)."""
    rows = [dict(r) for r in (sample_data or [])]
    if not rows:
        return rows

    def bump(value, step):
        text = str(value or "")
        match = re.search(r"(\d+)(\D*)$", text)
        if match:
            num = match.group(1)
            new_num = str(int(num) + max(1, int(step))).zfill(len(num))
            return text[:match.start(1)] + new_num + match.group(2)
        return (text + f"_{step}") if text else f"row_{step}"

    originals = [dict(r) for r in rows]
    guard = 0
    while len(rows) < minimum and guard < 12:
        guard += 1
        src = originals[guard % len(originals)]
        cols = list(src.get("cols") or [])
        if cols:
            cols[0] = bump(cols[0], guard)
        rows.append({"id": f"row{len(rows) + 1}", "cols": cols})

    for idx, row in enumerate(rows):
        row["id"] = f"row{idx + 1}"
    return rows


def derive_process_summary(data: dict) -> list:
    process = [clamp_text(p, MAX_PROCESS_CHARS)
               for p in (data.get("process_summary") or []) if str(p).strip() and str(p).strip() != "..."]

    if not process:
        process = [clamp_text(s.get("explanation") or "", MAX_PROCESS_CHARS)
                   for s in data.get("steps", []) if str(s.get("explanation") or "").strip()]

    if not process:
        process = [
            "Imports bring in the tools",
            "The loop visits each item",
            "print() shows the final answer",
        ]

    return [p for p in process if p][:3]


def validate_python_code(code: str, strict: bool = False) -> str:
    """Return '' when acceptable, otherwise the error message.
    strict=True also runs compile(), used for the final program."""
    if not code.strip():
        return "empty code"
    try:
        tree = ast.parse(code)
        if strict:
            compile(code, "<string>", "exec")
    except SyntaxError as e:
        return f"SyntaxError at line {e.lineno}: {e.msg}"

    for bad in FORBIDDEN_PY_CALLS:
        if bad in code:
            return f"forbidden call used: {bad}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_PY_MODULES:
                    return f"forbidden module import: {alias.name}"
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in FORBIDDEN_PY_MODULES:
                return f"forbidden module import: {node.module}"
    return ""


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

    steps = data["steps"]
    if not steps:
        raise Exception("JSON error: Missing keys: ['steps']")

    last_err = validate_python_code(steps[-1]["code"], strict=True)
    if last_err:
        raise Exception(f"PYTHON error: {last_err}")

    kept = [s for s in steps[:-1] if not validate_python_code(s["code"])]
    data["steps"] = kept + [steps[-1]]
    return data


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
                 user_logic: str = "") -> str:
    label_list = ", ".join(f'"{lab}"' for lab in ALLOWED_LABELS)

    prompt = f"""You are an expert Python instructor who teaches students with clean, well-aligned code.

LANGUAGE RULE (STRICT): every single word you output must be in English.
No Hindi, no Hinglish, no transliteration, anywhere.

FORMAT RULE (STRICT): every Python step must be properly formatted:
- 4-space indentation
- one statement per line
- multi-line lists and dicts with one item per line and a trailing comma
- comments only where they teach something

CODE RULES (STRICT):
- valid, runnable Python 3
- standard library only (pandas, oracledb, smtplib only if the question clearly needs them, and then say so in logic_explanation)
- no input(), no eval/exec, no os.system/subprocess/socket
- file reading, Excel, Oracle and email steps are allowed when the question asks for them
- no randomness; the sample data is fixed and deterministic
- the LAST step must be the complete program; earlier steps must be valid code at that point of the build
- every step is built from WHOLE statements: never leave a list, dict or call half open

USER QUESTION: "{question}"

STEP 1: UNDERSTAND THE PROBLEM
STEP 2: LOGICAL APPROACH (read, validate, transform, load, write output, notify, error handling)
STEP 3: SAMPLE INPUT - MUST MATCH THE CODE
- the sample must be the SAME literal data the code assigns to its main variable
- a list of numbers or strings -> one value per row, table_headers = ["VALUE"]
- a list of dicts or tuples -> one record per row, table_headers = the real field names
- a dict -> one key/value per row
- "dataset_name" = the real main variable name used in the code
- "sample_data" must have 5 or 6 rows when the code has that many values
- never invent a different dataset from the code

STEP 4: PYTHON SOLUTION
- steps = the program built part by part, the last step is the complete program

STEP 5: EXPLAIN IN PARTS
- "steps" = 2 to 5 parts
- steps[i].explanation = one short sentence naming the Python concept
- steps[i].bubble = exactly 3 short lines, each under {MAX_BUBBLE_CHARS} characters:
      "What: ...", "Why: ...", "Result: ..."

STEP 5b: STEP LABELS ("chips") - CHOOSE ONLY FROM THIS LIST
{label_list}

Rules for "chips":
- use ONLY the labels above, word for word
- one label per step, in the same order as "steps"

STEP 6: CONCEPT COMMENTS (shown in the bottom comment bubble during the video)
- "process_summary" = 2 or 3 very short sentences, each under {MAX_PROCESS_CHARS} characters
- these sentences must explain the CONCEPT of the program in plain English
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
    "dataset_name": "ids",
    "logic_explanation": "Short step-by-step logic",
    "process_summary": [
        "The list holds the IDs to check",
        "Counter counts each ID",
        "IDs seen twice are kept"
    ],
    "sample_data": [
        {"id": "row1", "cols": ["101"]},
        {"id": "row2", "cols": ["102"]},
        {"id": "row3", "cols": ["101"]},
        {"id": "row4", "cols": ["103"]},
        {"id": "row5", "cols": ["102"]}
    ],
    "table_headers": ["VALUE"],
    "chips": ["Create Data", "Filter Records", "Print Output", "Final Code"],
    "steps": [
        {
            "type": "code",
            "code": "from collections import Counter\n\nids = [101, 102, 101, 103, 102]\n\nduplicates = [\n    k for k, v in Counter(ids).items()\n    if v > 1\n]\n\nprint(duplicates)",
            "explanation": "Counter counts each ID, and IDs seen more than once are kept",
            "bubble": ["What: Count the IDs", "Why: Find repeats", "Result: Duplicate IDs"]
        }
    ],
    "cleaned_output": [
        ["[101, 102]"]
    ]
}

CRITICAL RULES:
1. THINK about the logic first
2. EVERY WORD MUST BE IN ENGLISH
3. Every step must be PROPERLY FORMATTED runnable Python made of whole statements
4. sample_data must match the literal data in the code, dataset_name and table_headers MUST match the code
5. process_summary must have 2 or 3 short concept sentences
6. cleaned_output must match what the final program really prints
7. ALL KEYS ARE COMPULSORY: question_banner, dataset_name, logic_explanation, process_summary,
   sample_data, table_headers, chips, steps, cleaned_output"""

    if few_shot_block:
        prompt += "\n\n" + few_shot_block

    if error_feedback:
        prompt += "\n\n" + error_feedback

    return prompt


# ============================================================
# QUESTION-CODE MODE (the pasted code is the animation source)
# ============================================================
def build_question_code_data(question: str, user_code: str) -> dict:
    """Skeleton data for the pasted code. Sample and output are read from the code itself."""
    return {
        "question_banner": question or "Python Program",
        "dataset_name": "data",
        "logic_explanation": "The code below is shown exactly as written",
        "process_summary": [],
        "sample_data": [],
        "table_headers": [],
        "chips": [],
        "steps": [{
            "code": format_python(user_code),
            "explanation": "Full program, built part by part",
            "bubble": ["What: Your code", "Why: Step by step", "Result: Program ready"],
        }],
        "cleaned_output": [],
    }


# ============================================================
# YOUTUBE METADATA (Title / Description / Hashtags)
# ============================================================
def build_metadata_prompt(question: str, query_logic: str, kind: str) -> str:
    context = f'PYTHON QUESTION: "{question}"' if question else "PYTHON QUESTION: (not given)"
    if query_logic:
        context += f"\n\nPYTHON CODE / LOGIC:\n{query_logic}"

    if kind == "title":
        task = ("Write ONE YouTube title for this Python tutorial video.\n"
                "- maximum 70 characters\n"
                "- mention the real Python concept and the function or variable from the code\n"
                "- clear, specific and interesting for beginners\n"
                "- no quotes, no markdown, no hashtags\n"
                "Return ONLY the title text.")
    elif kind == "description":
        task = ("Write a YouTube description for this Python tutorial video.\n"
                "- 4 to 6 short lines\n"
                "- line 1: what the viewer will learn in this video\n"
                "- then explain the logic in simple words, using the real function and variable names\n"
                "- one closing line inviting viewers to subscribe for daily Python content\n"
                "- plain English, no markdown, no hashtags\n"
                "Return ONLY the description text.")
    else:
        task = ("Generate 15 to 20 relevant YouTube hashtags for this Python tutorial video.\n"
                "- must include #Python, #PythonProgramming, #CodeWithMangesh\n"
                "- add topic tags such as #PythonInterview, #PythonTips, #LearnPython, #CodingForBeginners\n"
                "- add tags taken from the real topic and function names in the code\n"
                "- every hashtag starts with # and uses CamelCase with no spaces\n"
                "- one line, hashtags separated by spaces\n"
                "Return ONLY the hashtags.")

    return ("You are a YouTube content strategist for a Python programming channel.\n"
            "Write for Python learners. LANGUAGE RULE: reply in English only.\n\n"
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
        required = ["#Python", "#PythonProgramming", "#CodeWithMangesh"]
        seen, out = set(), []
        for tag in required + tags:
            key = tag.lower()
            if key not in seen:
                seen.add(key)
                out.append(tag)
        return " ".join(out[:20])

    kept = [ln.strip() for ln in t.splitlines() if ln.strip()]
    return "\n".join(kept[:10])


def generate_metadata(question: str, query_logic: str, kind: str) -> str:
    kind = (kind or "title").strip().lower()
    if kind in ("hashtag", "hashtags", "tags", "tag"):
        kind = "hashtags"
    elif kind in ("desc", "description"):
        kind = "description"
    else:
        kind = "title"

    prompt = build_metadata_prompt(question, query_logic, kind)
    options = dict(OLLAMA_OPTIONS)
    options["temperature"] = 0.5
    options["num_predict"] = {"title": 120, "description": 700}.get(kind, 180)

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
# THUMBNAIL THEMES - GRADIENT MODE
# ============================================================
def _mk_theme(name, bg, glow, accent, accent_soft, accent_border, hl, bar, tick,
              pill, pill_text, strip, bars, grid, kw, fn, num,
              text="#ffffff", muted="#a9b8cd"):
    return {
        "name": name, "bg": bg,
        "glow1": glow[0], "glow2": glow[1], "glow3": glow[2],
        "accent": accent, "accent_soft": accent_soft, "accent_border": accent_border,
        "hl": hl, "bar": bar, "tick": tick,
        "pill": pill, "pill_text": pill_text, "strip": strip, "bars": bars,
        "grid": grid, "kw": kw, "fn": fn, "num": num,
        "text": text, "muted": muted,
    }


THUMB_THEMES = {
    "midnight": _mk_theme(
        "Midnight Cyan",
        "radial-gradient(circle at 10% 4%, #17325f 0%, rgba(11,17,33,0) 52%),"
        " radial-gradient(circle at 92% 98%, #2b1a58 0%, rgba(11,17,33,0) 55%),"
        " linear-gradient(158deg, #0c1424 0%, #070c17 62%, #05080f 100%)",
        ("rgba(56,189,248,.42)", "rgba(167,139,250,.38)", "rgba(74,222,128,.20)"),
        "#38bdf8", "rgba(56,189,248,.12)", "rgba(56,189,248,.55)",
        "linear-gradient(90deg,#38bdf8 0%,#a78bfa 100%)", "#4ade80", "#4ade80",
        "linear-gradient(90deg,#38bdf8 0%,#a78bfa 100%)", "#04121f",
        "linear-gradient(90deg,#38bdf8 0%,#a78bfa 55%,#4ade80 100%)",
        "linear-gradient(180deg,#38bdf8 0%,rgba(56,189,248,.04) 100%)",
        "rgba(148,163,184,.20)", "#38bdf8", "#fbbf24", "#f472b6",
    ),
    "neon_violet": _mk_theme(
        "Neon Violet",
        "radial-gradient(circle at 14% 6%, #3b1d6e 0%, rgba(10,7,22,0) 54%),"
        " radial-gradient(circle at 90% 94%, #6d1f5c 0%, rgba(10,7,22,0) 56%),"
        " linear-gradient(160deg, #140b2b 0%, #0a0718 60%, #05030d 100%)",
        ("rgba(167,139,250,.46)", "rgba(244,114,182,.38)", "rgba(56,189,248,.22)"),
        "#c4b5fd", "rgba(196,181,253,.12)", "rgba(196,181,253,.55)",
        "linear-gradient(90deg,#a78bfa 0%,#f472b6 100%)", "#f472b6", "#f472b6",
        "linear-gradient(90deg,#a78bfa 0%,#f472b6 100%)", "#180a22",
        "linear-gradient(90deg,#a78bfa 0%,#f472b6 55%,#38bdf8 100%)",
        "linear-gradient(180deg,#a78bfa 0%,rgba(167,139,250,.04) 100%)",
        "rgba(196,181,253,.18)", "#c4b5fd", "#fbbf24", "#f472b6",
    ),
    "emerald_data": _mk_theme(
        "Emerald Data",
        "radial-gradient(circle at 12% 4%, #0d4a3c 0%, rgba(5,20,17,0) 54%),"
        " radial-gradient(circle at 90% 96%, #123f52 0%, rgba(5,20,17,0) 56%),"
        " linear-gradient(158deg, #071b18 0%, #04120f 62%, #020806 100%)",
        ("rgba(74,222,128,.40)", "rgba(45,212,191,.34)", "rgba(56,189,248,.20)"),
        "#4ade80", "rgba(74,222,128,.12)", "rgba(74,222,128,.55)",
        "linear-gradient(90deg,#4ade80 0%,#2dd4bf 100%)", "#2dd4bf", "#2dd4bf",
        "linear-gradient(90deg,#4ade80 0%,#2dd4bf 100%)", "#04211a",
        "linear-gradient(90deg,#4ade80 0%,#2dd4bf 55%,#38bdf8 100%)",
        "linear-gradient(180deg,#4ade80 0%,rgba(74,222,128,.04) 100%)",
        "rgba(134,239,172,.18)", "#4ade80", "#fbbf24", "#f472b6",
    ),
    "sunset_amber": _mk_theme(
        "Sunset Amber",
        "radial-gradient(circle at 12% 6%, #6a2f10 0%, rgba(24,10,4,0) 54%),"
        " radial-gradient(circle at 92% 96%, #6d1f3f 0%, rgba(24,10,4,0) 56%),"
        " linear-gradient(158deg, #24100a 0%, #170806 62%, #0b0403 100%)",
        ("rgba(251,146,60,.44)", "rgba(244,114,182,.34)", "rgba(250,204,21,.22)"),
        "#fbbf24", "rgba(251,191,36,.12)", "rgba(251,191,36,.55)",
        "linear-gradient(90deg,#fbbf24 0%,#f97316 100%)", "#f97316", "#fbbf24",
        "linear-gradient(90deg,#fbbf24 0%,#f97316 100%)", "#2a1204",
        "linear-gradient(90deg,#fbbf24 0%,#f97316 55%,#f472b6 100%)",
        "linear-gradient(180deg,#fbbf24 0%,rgba(251,191,36,.04) 100%)",
        "rgba(253,186,116,.18)", "#fbbf24", "#f97316", "#f472b6",
    ),
    "crimson_ink": _mk_theme(
        "Crimson Ink",
        "radial-gradient(circle at 12% 5%, #5a1024 0%, rgba(16,5,9,0) 54%),"
        " radial-gradient(circle at 92% 96%, #3b1050 0%, rgba(16,5,9,0) 56%),"
        " linear-gradient(158deg, #1c070e 0%, #120408 62%, #080204 100%)",
        ("rgba(248,113,113,.44)", "rgba(217,70,239,.32)", "rgba(251,191,36,.18)"),
        "#fb7185", "rgba(251,113,133,.12)", "rgba(251,113,133,.55)",
        "linear-gradient(90deg,#fb7185 0%,#d946ef 100%)", "#f87171", "#f87171",
        "linear-gradient(90deg,#fb7185 0%,#d946ef 100%)", "#2a0713",
        "linear-gradient(90deg,#fb7185 0%,#d946ef 55%,#fbbf24 100%)",
        "linear-gradient(180deg,#fb7185 0%,rgba(251,113,133,.04) 100%)",
        "rgba(252,165,165,.18)", "#fb7185", "#fbbf24", "#d946ef",
    ),
    "arctic_steel": _mk_theme(
        "Arctic Steel",
        "radial-gradient(circle at 12% 4%, #1e3a5f 0%, rgba(10,16,24,0) 54%),"
        " radial-gradient(circle at 92% 96%, #14324a 0%, rgba(10,16,24,0) 56%),"
        " linear-gradient(158deg, #0d1622 0%, #0a1119 62%, #05080d 100%)",
        ("rgba(125,211,252,.40)", "rgba(148,163,184,.34)", "rgba(226,232,240,.18)"),
        "#7dd3fc", "rgba(125,211,252,.12)", "rgba(125,211,252,.55)",
        "linear-gradient(90deg,#7dd3fc 0%,#e2e8f0 100%)", "#38bdf8", "#7dd3fc",
        "linear-gradient(90deg,#7dd3fc 0%,#e2e8f0 100%)", "#0a1520",
        "linear-gradient(90deg,#7dd3fc 0%,#e2e8f0 55%,#38bdf8 100%)",
        "linear-gradient(180deg,#7dd3fc 0%,rgba(125,211,252,.04) 100%)",
        "rgba(203,213,225,.18)", "#7dd3fc", "#fbbf24", "#f472b6",
    ),
    "graphite_lime": _mk_theme(
        "Graphite Lime",
        "radial-gradient(circle at 12% 5%, #2c3540 0%, rgba(10,11,13,0) 54%),"
        " radial-gradient(circle at 92% 96%, #23330f 0%, rgba(10,11,13,0) 56%),"
        " linear-gradient(158deg, #16191d 0%, #101215 62%, #08090b 100%)",
        ("rgba(163,230,53,.40)", "rgba(148,163,184,.32)", "rgba(56,189,248,.18)"),
        "#a3e635", "rgba(163,230,53,.12)", "rgba(163,230,53,.55)",
        "linear-gradient(90deg,#a3e635 0%,#22d3ee 100%)", "#a3e635", "#a3e635",
        "linear-gradient(90deg,#a3e635 0%,#22d3ee 100%)", "#131a05",
        "linear-gradient(90deg,#a3e635 0%,#22d3ee 55%,#38bdf8 100%)",
        "linear-gradient(180deg,#a3e635 0%,rgba(163,230,53,.04) 100%)",
        "rgba(203,213,225,.16)", "#a3e635", "#fbbf24", "#22d3ee",
    ),
}

LAST_THUMB_THEME = {"key": ""}


def choose_theme(ai_key: str) -> dict:
    key = str(ai_key or "").strip().lower().replace(" ", "_").replace("-", "_")
    keys = list(THUMB_THEMES.keys())
    if key not in THUMB_THEMES:
        key = random.choice(keys)
    if key == LAST_THUMB_THEME["key"]:
        key = keys[(keys.index(key) + 1) % len(keys)]
    LAST_THUMB_THEME["key"] = key
    return THUMB_THEMES[key]


# ============================================================
# THUMBNAIL - SOLID MODE
# ============================================================
THUMB_SOLID_COLORS = [
    {"name": "Solid Navy",      "hex": "#0E1E3C", "accent": "#38bdf8"},
    {"name": "Solid Deep Blue", "hex": "#0B2A4A", "accent": "#7dd3fc"},
    {"name": "Solid Purple",    "hex": "#241046", "accent": "#c4b5fd"},
    {"name": "Solid Plum",      "hex": "#2E1038", "accent": "#f472b6"},
    {"name": "Solid Teal",      "hex": "#06302E", "accent": "#2dd4bf"},
    {"name": "Solid Forest",    "hex": "#0C2B1C", "accent": "#4ade80"},
    {"name": "Solid Charcoal",  "hex": "#14161A", "accent": "#a3e635"},
    {"name": "Solid Rust",      "hex": "#33190B", "accent": "#fbbf24"},
    {"name": "Solid Black",     "hex": "#0A0A0C", "accent": "#38bdf8"},
]

LAST_SOLID = {"name": ""}


def pick_solid_color(question: str, code: str) -> dict:
    text = f"{question} {code}".lower()

    if any(k in text for k in ("try", "except", "error", "exception")):
        want = "Solid Plum"
    elif any(k in text for k in ("class", "def ", "decorator", "recursion")):
        want = "Solid Purple"
    elif any(k in text for k in ("sum(", "groupby", "count", "average", "pandas", "len(", "counter",
                                 "duplicate")):
        want = "Solid Teal"
    elif any(k in text for k in ("date", "time", "datetime", "timedelta")):
        want = "Solid Rust"
    elif any(k in text for k in ("file", "json", "api", "request", "loop", "for ", "csv", "excel",
                                 "oracle", "email", "snowflake")):
        want = "Solid Navy"
    else:
        want = "Solid Deep Blue"

    by_name = {c["name"]: c for c in THUMB_SOLID_COLORS}
    chosen = by_name.get(want) or random.choice(THUMB_SOLID_COLORS)
    if chosen["name"] == LAST_SOLID["name"]:
        idx = THUMB_SOLID_COLORS.index(chosen)
        chosen = THUMB_SOLID_COLORS[(idx + 1) % len(THUMB_SOLID_COLORS)]
    LAST_SOLID["name"] = chosen["name"]
    return chosen


def make_solid_theme(theme: dict, solid: dict) -> dict:
    solid_theme = dict(theme)
    solid_theme["bg"] = solid["hex"]
    solid_theme["accent"] = solid["accent"]
    solid_theme["name"] = solid["name"]
    return solid_theme


# ============================================================
# THUMBNAIL (AI copy + Playwright render, 1080x1920 PNG)
# ============================================================
THUMB_PY_KEYWORDS = {
    "def", "class", "return", "if", "elif", "else", "for", "while", "in", "not", "and", "or",
    "is", "import", "from", "as", "try", "except", "finally", "with", "lambda", "pass",
    "break", "continue", "yield", "global", "None", "True", "False", "self",
}
THUMB_PY_BUILTINS = {
    "print", "len", "range", "sum", "max", "min", "sorted", "enumerate", "zip", "open",
    "str", "int", "float", "list", "dict", "set", "tuple", "input", "type", "isinstance",
    "Counter",
}


def highlight_python_code(code_text: str) -> str:
    out_lines = []
    for raw in str(code_text or "").split("\n"):
        parts = []
        i, n = 0, len(raw)
        while i < n:
            ch = raw[i]
            if ch == "#":
                parts.append(f'<span class="c">{_esc(raw[i:])}</span>')
                break
            if ch in ("'", '"'):
                j = i + 1
                while j < n and raw[j] != ch:
                    j += 2 if raw[j] == "\\" else 1
                end = min(j + 1, n)
                parts.append(f'<span class="s">{_esc(raw[i:end])}</span>')
                i = end
                continue
            if ch.isdigit():
                j = i
                while j < n and (raw[j].isdigit() or raw[j] == "."):
                    j += 1
                parts.append(f'<span class="n">{_esc(raw[i:j])}</span>')
                i = j
                continue
            if ch.isalpha() or ch == "_":
                j = i
                while j < n and (raw[j].isalnum() or raw[j] == "_"):
                    j += 1
                word = raw[i:j]
                if word in THUMB_PY_KEYWORDS:
                    parts.append(f'<span class="k">{word}</span>')
                elif word in THUMB_PY_BUILTINS:
                    parts.append(f'<span class="f">{word}</span>')
                else:
                    parts.append(_esc(word))
                i = j
                continue
            parts.append(_esc(ch))
            i += 1
        out_lines.append("".join(parts))
    return "\n".join(out_lines)


def headline_with_highlight(headline: str, highlight: str) -> str:
    text = str(headline or "").strip()
    key = str(highlight or "").strip()
    if key and key.lower() in text.lower():
        idx = text.lower().find(key.lower())
        return (f'{_esc(text[:idx])}<span class="hl">{_esc(text[idx:idx + len(key)])}</span>'
                f'{_esc(text[idx + len(key):])}')
    return _esc(text)


def build_thumbnail_prompt(question: str, query_logic: str) -> str:
    context = f'PYTHON QUESTION: "{question}"' if question else "PYTHON QUESTION: (not given)"
    if query_logic:
        context += f"\n\nPYTHON CODE / LOGIC:\n{query_logic}"

    theme_list = " | ".join(THUMB_THEMES.keys())

    return ("You are a top YouTube Shorts and Instagram Reels thumbnail designer for a Python "
            "programming channel watched by beginners and job seekers.\n"
            "LANGUAGE RULE: English only.\n"
            "The thumbnail is VERTICAL 9:16 (1080x1920) and must be understood in ONE glance "
            "on a phone screen. Use the real function or variable names from the code.\n\n"
            f"{context}\n\n"
            "Return ONLY this JSON:\n"
            "{\n"
            '  "badge": "one of: PYTHON BASICS, PYTHON INTERVIEW, PYTHON FOR DATA, PYTHON TRICKS",\n'
            '  "headline": "punchy hook, max 40 characters, no full stop",\n'
            '  "highlight": "1 to 3 words copied EXACTLY from the headline that deserve colour",\n'
            '  "subheadline": "max 64 characters, one line that explains the topic",\n'
            '  "code_snippet": "2 to 4 real lines of the Python code - only the key idea",\n'
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

    snippet_lines = [ln.rstrip() for ln in str(raw.get("code_snippet") or "").splitlines() if ln.strip()]
    if not snippet_lines and query_logic and python_has_valid_syntax(query_logic):
        snippet_lines = [ln for ln in format_python(query_logic).splitlines() if ln.strip()][:4]
    if not snippet_lines:
        snippet_lines = ["def solve(nums):", "    return sorted(nums)[-2]"]
    snippet = "\n".join(snippet_lines[:4])

    bullets = [clamp_text(b, 32) for b in _as_str_list(raw.get("bullets")) if str(b).strip()][:3]
    if not bullets:
        bullets = ["def defines the function", "for visits each item", "return sends value back"]

    headline = pick("headline", 40, clamp_text(question, 40) or "Python Explained")
    highlight = pick("highlight", 22, "")
    if highlight and highlight.lower() not in headline.lower():
        highlight = ""

    badge = pick("badge", 24, "PYTHON BASICS").upper()
    if badge not in ("PYTHON BASICS", "PYTHON INTERVIEW", "PYTHON FOR DATA", "PYTHON TRICKS"):
        badge = "PYTHON BASICS"

    return {
        "badge": badge,
        "headline": headline,
        "highlight": highlight,
        "subheadline": pick("subheadline", 64, "Learn the exact logic step by step"),
        "code_snippet": snippet,
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


def build_thumbnail_html(content: dict, theme: dict, background_mode: str = "gradient") -> str:
    th = theme
    badge = _esc(content.get("badge"))
    headline_html = headline_with_highlight(content.get("headline"), content.get("highlight"))
    subheadline = _esc(content.get("subheadline"))
    footer = _esc(content.get("footer"))
    code_html = highlight_python_code(content.get("code_snippet") or "")

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
        color: {th['accent']}; border: 3px solid {th['accent_border']};
        background: {th['accent_soft']}; padding: 12px 26px; border-radius: 60px;
        white-space: nowrap;
    }}
    .handle {{ font-size: 24px; font-weight: 700; color: {th['muted']}; white-space: nowrap; }}
    .hero h1 {{
        font-size: 92px; line-height: 1.05; font-weight: 900;
        letter-spacing: -1.8px; color: {th['text']}; word-break: break-word;
    }}
    .hl {{
        background: {th['hl']};
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .sub {{
        margin-top: 18px; font-size: 35px; line-height: 1.3;
        font-weight: 600; color: {th['muted']}; word-break: break-word;
    }}
    .codecard {{
        position: relative; background: rgba(10,16,28,.94);
        border: 3px solid rgba(120,140,170,.35); border-left: 14px solid {th['bar']};
        border-radius: 22px; padding: 26px 28px 28px 30px;
        box-shadow: 0 26px 60px rgba(0,0,0,.55);
    }}
    .dots {{ display: flex; gap: 10px; margin-bottom: 18px; }}
    .dots i {{ display: block; width: 16px; height: 16px; border-radius: 50%; }}
    .dots i:nth-child(1) {{ background: #f87171; }}
    .dots i:nth-child(2) {{ background: #fbbf24; }}
    .dots i:nth-child(3) {{ background: #4ade80; }}
    .codetag {{
        position: absolute; right: 26px; top: 22px; font-size: 22px;
        font-weight: 900; letter-spacing: 3px; color: {th['bar']};
    }}
    .code {{
        font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
        font-size: 27px; line-height: 1.5; color: #e9eef7; white-space: pre-wrap;
    }}
    .code .k {{ color: {th['kw']}; font-weight: 700; }}
    .code .f {{ color: {th['fn']}; }}
    .code .n {{ color: {th['num']}; }}
    .code .s {{ color: #86efac; }}
    .code .c {{ color: #64748b; font-style: italic; }}
    .points {{ display: flex; flex-direction: column; gap: 14px; }}
    .point {{
        display: flex; align-items: center; gap: 14px;
        font-size: 31px; font-weight: 700; color: #eef3fa;
        background: rgba(148,163,184,.08); border: 2px solid rgba(148,163,184,.16);
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

        <div class="codecard">
            <div class="dots"><i></i><i></i><i></i></div>
            <div class="codetag">PY</div>
            <div class="code">{code_html}</div>
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


THUMB_BG_STATE = {"click": 0}


def create_thumbnail(question: str, query_logic: str) -> dict:
    """Click 1, 3, 5 ... -> gradient. Click 2, 4, 6 ... -> one flat colour.
    The counter advances only after a successful render."""
    content = generate_thumbnail_content(question, query_logic)
    theme = choose_theme(content.get("theme"))

    next_click = THUMB_BG_STATE["click"] + 1
    background_mode = "gradient" if (next_click % 2 == 1) else "solid"

    if background_mode == "solid":
        solid = pick_solid_color(question, query_logic)
        bg_theme = make_solid_theme(theme, solid)
        log_message(f"THUMBNAIL: click #{next_click} -> SINGLE SOLID COLOUR "
                    f"{solid['hex']} ({solid['name']})")
    else:
        bg_theme = theme
        log_message(f"THUMBNAIL: click #{next_click} -> MIXED GRADIENT background "
                    f"({theme['name']})")

    content["background_mode"] = background_mode
    content["theme_used"] = bg_theme["name"]

    html_text = build_thumbnail_html(content, bg_theme, background_mode)

    with THUMB_LOCK:
        THUMBNAIL_PATH.parent.mkdir(parents=True, exist_ok=True)
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        log_message(f"THUMBNAIL: rendering {THUMB_WIDTH}x{THUMB_HEIGHT} PNG...")
        asyncio.run(render_thumbnail_png(html_text, THUMBNAIL_PATH))

    THUMB_BG_STATE["click"] = next_click
    log_message(f"THUMBNAIL: PNG saved -> {THUMBNAIL_PATH}")
    return content


# ============================================================
# FINALISE THE ANIMATION
# ============================================================
def finalize_for_animation(data: dict, user_code: str = "") -> dict:
    steps_in = data.get("steps") or []
    for s in steps_in:
        s["code"] = format_python(s.get("code") or "")

    final_code = format_python(user_code) if user_code else ""
    if not final_code:
        for s in reversed(steps_in):
            if s.get("code", "").strip():
                final_code = s["code"]
                break

    question = str(data.get("question_banner") or "")
    code_ok = bool(final_code) and python_has_valid_syntax(final_code)

    # PROGRAM OUTPUT: real run first; AI mode falls back to the model's own output
    output_lines = run_program_output(final_code) if code_ok else []
    if not output_lines and not user_code and data.get("cleaned_output"):
        output_lines = [", ".join(r) if len(r) > 1 else (r[0] if r else "")
                        for r in data["cleaned_output"]][:MAX_OUTPUT_LINES]

    # SAMPLE DATA: taken from the code, shaped like the code's own literal
    view = resolve_sample_view(final_code if code_ok else "", data)
    data["sample_view"] = view
    data["sample_data"] = [{"id": f"row{i + 1}", "cols": list(r)} for i, r in enumerate(view["rows"])]
    data["output_lines"] = output_lines

    if code_ok:
        steps, full_code = build_typing_steps(final_code, data)
    else:
        log_message("PLANNER: code is not valid Python - typing it as one block")
        steps, full_code = build_single_step(final_code, data)

    # AI mode only: use the model's own bubbles for the first and last step
    if steps_in and not user_code:
        first_bubble = _as_str_list(steps_in[0].get("bubble"), pad_to=3)[:3]
        if any(first_bubble):
            steps[0]["bubble"] = first_bubble
        last_bubble = _as_str_list(steps_in[-1].get("bubble"), pad_to=3)[:3]
        if any(last_bubble):
            steps[-1]["bubble"] = last_bubble
        last_expl = str(steps_in[-1].get("explanation") or "")
        if last_expl:
            steps[-1]["explanation"] = clamp_text(last_expl, 110)

    data["steps"] = steps
    data["chips"] = [s["label"] for s in steps]

    LAST_RUN["question"] = question
    LAST_RUN["final_code"] = full_code
    LAST_RUN["logic_explanation"] = str(data.get("logic_explanation") or "")
    LAST_RUN["process_summary"] = data.get("process_summary") or []

    data["reel_theme"] = choose_reel_theme(question, full_code)

    log_message(f"SAMPLE: {view['title']} | {len(view['rows'])} row(s) shown")
    log_message(f"STEPS: {len(steps)}")
    log_message(f"STEP LABELS: {' -> '.join(data['chips'])}")
    log_message("NOTE: append-only typing - nothing already typed is typed again")
    for i, s in enumerate(steps):
        preview = (s.get("typed") or "").replace("\n", "\\n")[:50]
        log_message(f"   step{i + 1} {s['label']}: {preview}")

    return data


# ============================================================
# GENERATION (sequential models, priority order)
# ============================================================
def fallback_builtin(question: str) -> dict:
    log_message("WARNING: all models failed - using the built-in fallback video")
    code = (
        "def second_largest(nums):\n"
        "    unique = sorted(set(nums))\n"
        "    return unique[-2]\n"
        "\n"
        "\n"
        "numbers = [10, 20, 20, 35, 5, 35]\n"
        "print(second_largest(numbers))"
    )
    return {
        "question_banner": question or "Python Program",
        "dataset_name": "numbers",
        "logic_explanation": "Remove duplicates, sort, then pick the second value from the end",
        "process_summary": [
            "set() removes repeated values",
            "sorted() puts the values in order",
            "The second value from the end is the answer",
        ],
        "sample_data": [],
        "table_headers": ["VALUE"],
        "chips": [],
        "steps": [
            {"code": code,
             "explanation": "Define the helper, create the data, then print the result",
             "bubble": ["What: Helper function", "Why: Reuse the logic", "Result: Second value"]},
        ],
        "cleaned_output": [["20"]],
    }


def generate_animation_data(question: str, query_logic: str = "") -> dict:
    user_code, user_logic = split_query_logic(query_logic)

    # QUESTION-CODE MODE: the pasted (and repaired) code is the animation source
    if user_code:
        log_message(f"QUESTION-CODE MODE: {len(user_code)} chars of Python code - used as-is")
        data = build_question_code_data(question, user_code)
        data["process_summary"] = derive_process_summary(data)
        return finalize_for_animation(data, user_code)

    if user_logic:
        log_message(f"Logic found in the Code box ({len(user_logic)} chars) - follow it exactly")

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

    for model_index, model_name in enumerate(MODELS_TO_TRY, start=1):
        error_feedback = ""

        for attempt in range(1, MAX_ATTEMPTS_PER_MODEL + 1):
            try:
                log_message(f"MODEL {model_index}/{len(MODELS_TO_TRY)}: {model_name} "
                            f"(attempt {attempt}/{MAX_ATTEMPTS_PER_MODEL})...")
                prompt = build_prompt(question, few_shot_block, error_feedback, user_logic)
                response, mode = call_ollama_model(model_name, prompt)

                raw_text = response["message"]["content"].strip()
                log_message(f"Response received ({mode})")

                parsed_data = validate_json_response(raw_text, question)
                log_message(f"SUCCESS: {model_name} | steps={len(parsed_data['steps'])} "
                            f"| rows={len(parsed_data['sample_data'])}")

                save_learning_example(question, parsed_data, model_name)
                parsed_data["process_summary"] = derive_process_summary(parsed_data)
                return finalize_for_animation(parsed_data, "")

            except Exception as e:
                last_error = str(e)
                error_feedback = build_error_feedback_block(model_name, attempt, last_error)
                log_message(f"FAILED: {model_name} - {last_error[:70]}")

        log_message(f"Switching to the next model after {model_name} failed")

    log_message(f"All models failed (last error: {last_error[:70]})")
    data = fallback_builtin(question)
    data["process_summary"] = derive_process_summary(data)
    return finalize_for_animation(data, "")


# ============================================================
# HTML BUILD
# ============================================================
def _sample_html(view: dict) -> str:
    """Sample panel body: chips for a plain list, a table for records / dicts / columns."""
    if view.get("kind") == "list":
        chips = "".join(
            f'<span class="sitem" id="row{i + 1}">{_esc(r[0] if r else "")}</span>'
            for i, r in enumerate(view.get("rows", []))
        )
        return f'<div class="seq"><span class="br">[</span>{chips}<span class="br">]</span></div>'

    head = "".join(f"<th>{_esc(h)}</th>" for h in view.get("headers", []))
    body = "".join(
        f'<tr id="row{i + 1}">' + "".join(f"<td>{_esc(c)}</td>" for c in r) + "</tr>"
        for i, r in enumerate(view.get("rows", []))
    )
    return f"<table><tr>{head}</tr>{body}</table>"


def create_html_file(data: dict, output_path: Path):
    log_message("Building HTML...")

    try:
        view = data.get("sample_view") or {"kind": "list", "title": "sample", "rows": [], "headers": [], "note": ""}
        sample_body_html = _sample_html(view)
        sample_title = _esc(view.get("title", "sample"))
        note_text = view.get("note", "")
        note_html = f'<div class="sample-note">{_esc(note_text)}</div>' if note_text else ""

        steps = data.get('steps', [])
        chips_html = ""
        for idx, step in enumerate(steps):
            chips_html += f'<div class="chip" id="chip{idx + 1}">{_esc(step["label"])}</div>'

        # only what the browser needs (no full code per step, keeps the HTML small)
        steps_js = json.dumps([
            {
                "typed": s.get("typed") or "",
                "active_from": s.get("active_from", 0),
                "active_to": s.get("active_to", 0),
                "rows": s.get("rows"),
                "dim": bool(s.get("dim")),
                "bubble": _as_str_list(s.get("bubble"), pad_to=3)[:3],
            }
            for s in steps
        ])

        out_lines = data.get("output_lines") or []
        if out_lines:
            output_html = "\n".join(_esc(line) for line in out_lines)
        else:
            output_html = "Output needs real files or a database, so it is not shown here."

        concept_lines = data.get('process_summary') or derive_process_summary(data)
        concept_json = json.dumps([str(c) for c in concept_lines[:3]])

        question_banner = _esc(data.get('question_banner', 'Python Program'))

        theme = data.get("reel_theme") or choose_reel_theme(question_banner, "")
        log_message(f"BACKGROUND: {theme['name']}")

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Animation Reel</title>
    <style>
        :root {{
            --bg: {theme['bg']};
            --glow-1: {theme['glow1']};
            --glow-2: {theme['glow2']};
            --panel-bg: {theme['panel']};
            --border-color: {theme['border']};
            --blue-accent: {theme['accent']};
            --green-accent: {theme['accent2']};
            --yellow-accent: #facc15;
            --red-accent: #f87171;
            --text-main: {theme['text']};
            --text-muted: {theme['muted']};
            --editor-bg: {theme['editor']};
            --grid-line: {theme['grid']};
        }}
        body {{ margin: 0; padding: 0; width: 100vw; height: 100vh; background-color: #000; display: flex; justify-content: center; align-items: center; overflow: hidden; font-family: 'Segoe UI', Roboto, sans-serif; }}
        #stage {{ width: 1080px; height: 1920px; background-color: #05070d; color: var(--text-main); position: relative; transform-origin: center center; overflow: hidden; }}
        .bg-layer {{ position: absolute; inset: 0; z-index: 0; background: var(--bg); }}
        .bg-glow {{ position: absolute; z-index: 0; border-radius: 50%; filter: blur(120px); }}
        .bg-glow-a {{ width: 720px; height: 720px; left: -200px; top: -180px; background: var(--glow-1); }}
        .bg-glow-b {{ width: 640px; height: 640px; right: -220px; bottom: 140px; background: var(--glow-2); }}
        .bg-grid {{ position: absolute; inset: 0; z-index: 0; opacity: .55;
            background-image: linear-gradient(var(--grid-line) 1px, transparent 1px),
                              linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
            background-size: 96px 96px; }}
        .bg-scrim {{ position: absolute; inset: 0; z-index: 1; background: rgba(3,6,12,.32); pointer-events: none; }}
        .watermark {{ position: absolute; top: 70px; left: 60px; font-size: 26px; font-weight: 600; color: rgba(255, 255, 255, 0.24); z-index: 10; }}
        .safe-zone-content {{ position: absolute; z-index: 5; top: 130px; bottom: 250px; left: 60px; right: 150px; display: flex; flex-direction: column; gap: 18px; }}
        .question-banner {{ background-color: var(--panel-bg); border-left: 10px solid var(--blue-accent); border-top: 2px solid var(--border-color); border-right: 2px solid var(--border-color); border-bottom: 2px solid var(--border-color); padding: 18px 24px; border-radius: 14px; font-size: 26px; line-height: 1.4; flex-shrink: 0; box-shadow: 0 8px 20px rgba(0,0,0,0.4); }}
        .question-banner span.icon {{ color: var(--blue-accent); font-weight: bold; }}
        .data-panel {{ background-color: var(--panel-bg); border: 2px solid var(--border-color); border-radius: 14px; padding: 14px 18px; flex-shrink: 0; }}
        .panel-title {{ font-size: 19px; color: var(--text-muted); letter-spacing: 2px; margin-bottom: 10px; font-weight: 600; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 19px; }}
        th, td {{ padding: 6px 10px; text-align: left; border-bottom: 2px solid var(--border-color); }}
        th {{ color: var(--blue-accent); font-weight: 600; }}
        tr.row-dim td {{ opacity: .28; }}
        tr.row-keep td {{ opacity: 1; }}
        @keyframes highlightPulse {{ 0% {{ background-color: transparent; }} 50% {{ background-color: rgba(248, 113, 113, 0.4); }} 100% {{ background-color: rgba(248, 113, 113, 0.15); }} }}
        .highlight-row td {{ animation: highlightPulse 0.5s ease-out forwards; color: var(--red-accent); font-weight: bold; }}
        .seq {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-family: Consolas, 'Courier New', monospace; font-size: 24px; }}
        .br {{ color: var(--text-muted); font-size: 34px; font-weight: 700; }}
        .sitem {{ border: 2px solid var(--border-color); border-radius: 10px; padding: 6px 14px; color: #e8eef8; background: rgba(15, 23, 42, 0.6); transition: opacity 0.3s; }}
        .sitem.row-dim {{ opacity: .28; }}
        .sitem.row-keep {{ opacity: 1; }}
        .sitem.highlight-row {{ animation: highlightPulse 0.5s ease-out forwards; color: var(--red-accent); font-weight: bold; }}
        .sample-note {{ font-size: 17px; color: var(--text-muted); margin-top: 8px; }}
        .chips-container {{ display: flex; gap: 10px; flex-shrink: 0; flex-wrap: wrap; }}
        .chip {{ border: 2px solid var(--border-color); padding: 7px 18px; border-radius: 40px; font-size: 21px; color: var(--text-muted); font-weight: 600; transition: all 0.3s; }}
        @keyframes pop {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); box-shadow: 0 0 15px rgba(56, 189, 248, 0.5); }} 100% {{ transform: scale(1); }} }}
        .chip.active {{ border-color: var(--blue-accent); color: var(--blue-accent); background: rgba(56, 189, 248, 0.12); animation: pop 0.4s ease-out; }}
        .editor-container {{ background-color: var(--editor-bg); border: 3px solid var(--border-color); border-radius: 14px; display: flex; flex-direction: column; flex-grow: 1; min-height: 0; max-height: 510px; }}
        .editor-header {{ padding: 8px 16px; font-size: 17px; color: var(--text-muted); border-bottom: 2px solid var(--border-color); letter-spacing: 2px; font-weight: 600; }}
        /* ONE fixed font size for the whole animation - never reduced. Long code scrolls. */
        .editor-scroll-area {{ padding: 12px 16px; overflow-y: auto; flex-grow: 1; font-family: 'Consolas', 'Courier New', monospace; font-size: 24px; line-height: 1.55; color: #e8eef8; text-align: left; white-space: pre-wrap; word-wrap: break-word; tab-size: 4; }}
        .cl {{ border-left: 5px solid transparent; padding-left: 10px; margin-left: -15px; border-radius: 6px; transition: background 0.25s, border-color 0.25s; min-height: 1.55em; }}
        .cl.active {{ background: rgba(56, 189, 248, 0.13); border-left-color: var(--blue-accent); }}
        .cursor {{ display: inline-block; width: 3px; height: 1.05em; margin-left: 1px; background-color: var(--blue-accent); vertical-align: text-bottom; border-radius: 1px; animation: blink 1s step-end infinite; }}
        .tk-kw {{ color: #7dd3fc; font-weight: bold; }}
        .tk-bi {{ color: #facc15; }}
        .tk-str {{ color: #86efac; }}
        .tk-num {{ color: #f87171; }}
        .tk-com {{ color: #64748b; font-style: italic; }}
        .tk-dec {{ color: #c4b5fd; }}
        .bottom-section {{ position: relative; height: 230px; flex-shrink: 0; margin-top: 26px; }}
        .speech-bubble {{ position: absolute; width: 100%; height: 100%; background-color: #ffffff; color: #0f172a; padding: 20px 26px; border-radius: 20px 20px 20px 0px; box-shadow: 0 15px 30px rgba(0,0,0,0.4); font-size: 23px; line-height: 1.45; font-weight: 600; opacity: 0; transform: translateY(20px); transition: opacity 0.4s, transform 0.4s; border: 5px solid var(--blue-accent); box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; overflow: hidden; }}
        .speech-bubble.visible {{ opacity: 1; transform: translateY(0); }}
        .speech-line {{ margin: 5px 0; opacity: 0; transition: opacity 0.3s; font-size: 20px; }}
        .speech-line.show {{ opacity: 1; }}
        .output-panel {{ position: absolute; width: 100%; height: 100%; background-color: var(--panel-bg); border: 3px solid var(--green-accent); border-radius: 16px; padding: 20px; box-sizing: border-box; display: none; animation: slideUp 0.8s ease-out forwards; overflow-y: auto; }}
        .out-text {{ margin: 0; font-family: Consolas, 'Courier New', monospace; font-size: 24px; line-height: 1.5; color: #e8eef8; white-space: pre-wrap; }}
        .channel-bar {{ position: absolute; left: 60px; right: 60px; bottom: 72px; z-index: 12;
            display: flex; justify-content: center; align-items: center; gap: 18px;
            font-size: 25px; font-weight: 700; color: var(--text-muted); }}
        .ch-item {{ display: inline-flex; align-items: center; gap: 10px; white-space: nowrap; }}
        .ch-yt {{ color: var(--red-accent); }}
        .ch-ig {{ color: var(--yellow-accent); }}
        .ch-sep {{ color: var(--border-color); }}
        #end-card {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; background-color: rgba(8, 12, 22, 0.985); z-index: 2000; display: flex; flex-direction: column; justify-content: center; align-items: center; opacity: 0; pointer-events: none; transition: opacity 1.8s ease-in-out; box-sizing: border-box; }}
        #end-card h1 {{ font-size: 70px; margin-bottom: 30px; text-align: center; color: var(--blue-accent); }}
        #end-card p {{ font-size: 46px; margin: 20px 0; text-align: center; }}
        @keyframes blink {{ 50% {{ opacity: 0; }} }}
        @keyframes slideUp {{ 0% {{ opacity: 0; transform: translateY(40px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
    </style>
</head>
<body>
    <div id="stage">
        <div class="bg-layer"></div>
        <div class="bg-glow bg-glow-a"></div>
        <div class="bg-glow bg-glow-b"></div>
        <div class="bg-grid"></div>
        <div class="bg-scrim"></div>

        <div class="watermark">@Code_With_Mangesh</div>
        <div class="safe-zone-content">
            <div class="question-banner"><span class="icon">Question:</span> {question_banner}</div>
            <div class="data-panel">
                <div class="panel-title">{sample_title}</div>
                {sample_body_html}
                {note_html}
            </div>
            <div class="chips-container">{chips_html}</div>
            <div class="editor-container">
                <div class="editor-header">PYTHON CODE</div>
                <div class="editor-scroll-area" id="editor-scroll"><span id="code-content"></span></div>
            </div>
            <div class="bottom-section">
                <div class="speech-bubble" id="speech-bubble">
                    <div class="speech-line" id="bubble-line1"></div>
                    <div class="speech-line" id="bubble-line2"></div>
                    <div class="speech-line" id="bubble-line3"></div>
                </div>
                <div class="output-panel" id="expected-output">
                    <div class="panel-title">PROGRAM OUTPUT</div>
                    <pre class="out-text">{output_html}</pre>
                </div>
            </div>
        </div>

        <div class="channel-bar">
            <span class="ch-item"><span class="ch-yt">&#9654;</span> YouTube: @Code_With_Mangesh</span>
            <span class="ch-sep">&#8226;</span>
            <span class="ch-item"><span class="ch-ig">&#9678;</span> Instagram: @code_with_mangesh</span>
        </div>

        <div id="end-card">
            <h1>Got it? 🤔</h1>
            <p>Comment your answer!</p>
            <p>Share & Like</p>
            <br><br><p style="color: var(--blue-accent); font-weight: bold; font-size: 56px;">@Code_With_Mangesh</p>
            <p>Daily Python & Data Science 🚀</p>
        </div>
    </div>
    <script>
        const steps = {steps_js};
        const conceptLines = {concept_json};

        function resizeStage() {{
            const stage = document.getElementById('stage');
            const scaleX = window.innerWidth / 1080;
            const scaleY = window.innerHeight / 1920;
            const scale = Math.min(scaleX, scaleY);
            stage.style.transform = `scale(${{scale}})`;
        }}
        window.addEventListener('resize', resizeStage); resizeStage();

        let currentCode = "";
        let activeFrom = 0;
        let activeTo = 0;
        const codeContent = document.getElementById('code-content');
        const editorScroll = document.getElementById('editor-scroll');
        const bubble = document.getElementById('speech-bubble');

        const PY_KEYWORDS = new Set(['def','class','return','if','elif','else','for','while','in','not','and','or','is','import','from','as','try','except','finally','with','lambda','pass','break','continue','yield','global','None','True','False','self']);
        const PY_BUILTINS = new Set(['print','len','range','sum','max','min','sorted','enumerate','zip','open','str','int','float','list','dict','set','tuple','input','type','isinstance','Counter']);

        function escapeHtml(s) {{
            return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        }}

        function highlightLine(line) {{
            const trimmed = line.trimStart();
            if (trimmed.startsWith('@')) {{
                return '<span class="tk-dec">' + escapeHtml(line) + '</span>';
            }}

            let out = '';
            let i = 0;
            const n = line.length;
            while (i < n) {{
                const ch = line[i];

                if (ch === '#') {{
                    out += '<span class="tk-com">' + escapeHtml(line.slice(i)) + '</span>';
                    break;
                }}

                if (ch === '"' || ch === "'") {{
                    const quote = ch;
                    let j = i + 1;
                    while (j < n && line[j] !== quote) {{
                        if (line[j] === '\\\\') j++;
                        j++;
                    }}
                    const end = Math.min(j + 1, n);
                    out += '<span class="tk-str">' + escapeHtml(line.slice(i, end)) + '</span>';
                    i = end;
                    continue;
                }}

                if (/[0-9]/.test(ch) && (i === 0 || !/[A-Za-z_]/.test(line[i - 1]))) {{
                    let j = i;
                    while (j < n && /[0-9.]/.test(line[j])) j++;
                    out += '<span class="tk-num">' + escapeHtml(line.slice(i, j)) + '</span>';
                    i = j;
                    continue;
                }}

                if (/[A-Za-z_]/.test(ch)) {{
                    let j = i;
                    while (j < n && /[A-Za-z0-9_]/.test(line[j])) j++;
                    const word = line.slice(i, j);
                    if (PY_KEYWORDS.has(word)) {{
                        out += '<span class="tk-kw">' + word + '</span>';
                    }} else if (PY_BUILTINS.has(word)) {{
                        out += '<span class="tk-bi">' + word + '</span>';
                    }} else {{
                        out += escapeHtml(word);
                    }}
                    i = j;
                    continue;
                }}

                out += escapeHtml(ch);
                i++;
            }}
            return out;
        }}

        const CARET_HTML = '<span class="cursor"></span>';

        function renderCode() {{
            const lines = currentCode.split('\\n');
            const caretLine = lines.length - 1;
            let html = '';

            for (let i = 0; i < lines.length; i++) {{
                const isActive = (i >= activeFrom && i <= activeTo);
                const isCaretLine = (i === caretLine);
                const body = highlightLine(lines[i]);

                let inner;
                if (isCaretLine) {{
                    inner = body + CARET_HTML;
                }} else if (body.length) {{
                    inner = body;
                }} else {{
                    inner = '&nbsp;';
                }}

                html += '<div class="cl' + (isActive ? ' active' : '') + '">' + inner + '</div>';
            }}

            codeContent.innerHTML = html;
            editorScroll.scrollTop = editorScroll.scrollHeight;
        }}

        const TYPING_SPEED = 50;

        // append-only typing: each character is added at the end, nothing is retyped
        async function typeStep(text) {{
            for (let k = 0; k < text.length; k++) {{
                currentCode += text.charAt(k);
                renderCode();
                await new Promise(r => setTimeout(r, TYPING_SPEED));
            }}
        }}

        // sample items: table rows or list chips, both carry id="rowN"
        function applyRows(keep, dim) {{
            const all = document.querySelectorAll('[id^="row"]');
            all.forEach((el, idx) => {{
                const kept = (!Array.isArray(keep)) ? true : keep.indexOf(idx) !== -1;
                el.classList.remove('highlight-row');
                el.classList.toggle('row-dim', !!dim && !kept);
                el.classList.toggle('row-keep', kept);
            }});
            if (!all.length) return;
            let firstKept = 0;
            if (Array.isArray(keep) && keep.length) firstKept = keep[0];
            if (all[firstKept]) all[firstKept].classList.add('highlight-row');
        }}

        async function showBubble(lines) {{
            bubble.classList.add('visible');
            for (let i = 1; i <= 3; i++) {{
                document.getElementById('bubble-line' + i).className = 'speech-line';
                document.getElementById('bubble-line' + i).innerText = lines[i - 1] || "";
            }}
            for (let i = 1; i <= 3; i++) {{
                await new Promise(r => setTimeout(r, 420));
                document.getElementById('bubble-line' + i).classList.add('show');
            }}
            await new Promise(r => setTimeout(r, 1100));
        }}

        function hideBubble() {{ bubble.classList.remove('visible'); }}

        async function runAnimation() {{
            await new Promise(r => setTimeout(r, 800));

            for (let i = 0; i < steps.length; i++) {{
                const step = steps[i];

                const chipEl = document.getElementById('chip' + (i + 1));
                if (chipEl) chipEl.classList.add('active');

                activeFrom = step.active_from;
                activeTo = step.active_to;
                renderCode();

                applyRows(step.rows, step.dim);

                await showBubble(step.bubble);

                if (step.typed) {{
                    await typeStep(step.typed);
                }}

                hideBubble();
                await new Promise(r => setTimeout(r, 1100));
            }}

            activeFrom = 0;
            activeTo = 99999;
            renderCode();

            if (conceptLines && conceptLines.length > 0) {{
                await showBubble(conceptLines);
                hideBubble();
                await new Promise(r => setTimeout(r, 500));
            }}

            document.querySelectorAll('[id^="row"]').forEach(r => r.classList.remove('row-dim'));
            await new Promise(r => setTimeout(r, 700));
            document.getElementById('expected-output').style.display = 'block';
            editorScroll.scrollTop = editorScroll.scrollHeight;
            await new Promise(r => setTimeout(r, 3000));
            document.getElementById('end-card').style.opacity = '1';
        }}

        window.onload = runAnimation;
    </script>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        log_message("HTML created")

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
                    timeout=180000
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

    output_dir = r"C:\Mangesh\AI video\Output_File"
    html_save_dir = r"C:\Mangesh\AI video\Input_File"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(html_save_dir, exist_ok=True)

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
            html_file_path = Path(html_save_dir) / "dynamic_animation.html"
            create_html_file(animation_data, html_file_path)

            set_job_stage(job_id, "video")
            if platform.system() == "Windows":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            video_path = asyncio.run(record_video(html_file_path, output_dir))
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


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>@Code_With_Mangesh - AI Python Video Studio</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                background: linear-gradient(135deg, #0b1121 0%, #1e293b 100%);
                color: #f8fafc;
                padding: 18px;
                min-height: 100vh;
            }
            .container {
                width: 100%;
                max-width: 720px;
                margin: auto;
                background: rgba(30, 41, 59, 0.8);
                backdrop-filter: blur(10px);
                padding: 22px;
                border-radius: 14px;
                box-shadow: 0 16px 44px rgba(0,0,0,0.6);
                border: 2px solid #334155;
            }
            h1 { color: #38bdf8; text-align: center; margin-bottom: 6px; font-size: 23px; }
            .subtitle { text-align: center; color: #94a3b8; margin-bottom: 18px; font-size: 13px; }
            .mode-note { font-size: 12px; color: #94a3b8; background: #0f172a; border: 1px dashed #334155;
                border-radius: 8px; padding: 8px 10px; margin-bottom: 4px; line-height: 1.5; }
            .mode-note b { color: #38bdf8; }
            label {
                font-size: 14px; font-weight: 600; color: #cbd5e1;
                display: block; margin: 12px 0 6px 0;
            }
            label small { color: #64748b; font-weight: 400; }
            textarea {
                width: 100%; padding: 10px; font-size: 13.5px; background: #0f172a;
                color: #e2e8f0; border: 2px solid #334155; border-radius: 8px;
                resize: vertical; font-family: 'Consolas', 'Segoe UI', sans-serif;
                transition: border-color 0.3s; line-height: 1.45;
            }
            #question { height: 60px; }
            #queryLogic { height: 150px; font-family: 'Consolas', monospace; }
            textarea:focus { outline: none; border-color: #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); }
            button {
                background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
                color: #0f172a; font-size: 16px; font-weight: bold; padding: 13px 26px;
                border: none; border-radius: 9px; cursor: pointer; width: 100%;
                margin-top: 16px; transition: all 0.3s;
                box-shadow: 0 6px 16px rgba(56, 189, 248, 0.3);
            }
            button:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(56, 189, 248, 0.5); }
            button:disabled { background: #64748b; cursor: not-allowed; transform: none; box-shadow: none; }
            button.mini {
                background: #1e293b; color: #38bdf8; border: 2px solid #38bdf8;
                width: auto; flex: 1 1 auto; margin-top: 0; font-size: 13px;
                padding: 11px 8px; box-shadow: none;
            }
            button.mini:hover { background: rgba(56,189,248,0.12); transform: translateY(-1px); box-shadow: none; }
            button.mini:disabled { background: #334155; color: #64748b; border-color: #334155; }
            .meta-row { display: flex; gap: 8px; margin-top: 12px; }
            #metaBox { display: none; margin-top: 14px; }
            .meta-head { display: flex; align-items: center; gap: 10px; margin-bottom: 7px; flex-wrap: wrap; }
            .meta-title { font-size: 14px; font-weight: 600; color: #cbd5e1; }
            .meta-copy { flex: 0 0 auto; margin-left: auto; font-size: 12px; padding: 5px 14px; }
            .meta-out {
                background: #0f172a; border: 2px solid #334155; border-radius: 9px; padding: 12px;
                font-size: 13px; color: #e2e8f0; line-height: 1.6; white-space: pre-wrap;
                max-height: 230px; overflow-y: auto;
            }
            .mini-link {
                margin-left: auto; font-size: 12px; font-weight: 700; padding: 6px 14px;
                border-radius: 8px; border: 2px solid #4ade80; color: #4ade80;
                background: #1e293b; text-decoration: none;
            }
            .mini-link:hover { background: rgba(74,222,128,0.12); }
            #thumbBox { display: none; margin-top: 14px; }
            .thumb-wrap {
                display: flex; align-items: center; justify-content: center;
                background: #0f172a; border: 2px solid #334155; border-radius: 9px; padding: 12px;
            }
            #thumbImg { display: none; max-height: 360px; border-radius: 8px; border: 1px solid #334155; }
            .thumb-status { font-size: 12.5px; color: #94a3b8; text-align: center; }
            .note { font-size: 11.5px; color: #64748b; margin-top: 8px; text-align: center; }
            .stages { display: flex; gap: 6px; flex-wrap: wrap; margin: 18px 0 10px 0; }
            .stage {
                flex: 1 1 auto; text-align: center; font-size: 11.5px; font-weight: 600;
                padding: 7px 8px; border-radius: 7px; border: 2px solid #334155;
                color: #64748b; background: #0f172a; transition: all 0.3s;
            }
            .stage.active { border-color: #38bdf8; color: #38bdf8; background: rgba(56,189,248,0.12);
                box-shadow: 0 0 12px rgba(56,189,248,0.35); }
            .stage.done { border-color: #4ade80; color: #4ade80; background: rgba(74,222,128,0.10); }
            .stage.error { border-color: #f87171; color: #f87171; background: rgba(248,113,113,0.12); }
            .log-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
            .logs-label { font-size: 14px; font-weight: 600; color: #cbd5e1; }
            .pill { font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 18px;
                border: 2px solid #334155; color: #94a3b8; background: #0f172a; }
            .pill.running { border-color: #38bdf8; color: #38bdf8; }
            .pill.done { border-color: #4ade80; color: #4ade80; }
            .pill.error { border-color: #f87171; color: #f87171; }
            .timer { margin-left: auto; font-family: 'Consolas', monospace; font-size: 12px; color: #64748b; }
            .logs-box {
                background: #0f172a; border: 2px solid #334155; border-radius: 9px; padding: 12px;
                height: 210px; overflow-y: auto; font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px; color: #4ade80; line-height: 1.6; white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Python Video Generator Studio</h1>
            <p class="subtitle">@Code_With_Mangesh - Smart Python Learning</p>

            <form id="videoForm">
                <label for="question">Question <small>(title shown on the video)</small></label>
                <textarea id="question" placeholder="Example: Find duplicate transaction IDs before loading data into Snowflake"></textarea>

                <label for="queryLogic">Code or Logic <small>(paste Python code OR write the logic)</small></label>
                <div class="mode-note">
                    <b>Question-Code mode:</b> paste your full Python code and the animation shows that code exactly as written. The sample data is taken from the code (a list shows as [ ] chips, records show as a table). The PROGRAM OUTPUT is the real printed result. Accidentally duplicated lines are repaired automatically.<br>
                    <b>Question + Logic mode:</b> write only the logic in plain English and the AI builds the code.
                </div>
                <textarea id="queryLogic" placeholder="from collections import Counter&#10;&#10;ids = [101, 102, 101, 103, 102]&#10;...&#10;&#10;OR  write the logic: find IDs that occur more than once"></textarea>

                <button type="submit" id="playBtn">Generate Video</button>
                <p class="note">Silent animation - the code is typed once, statement by statement, in the same order as your file.</p>
            </form>

            <div class="meta-row">
                <button type="button" class="mini" id="btnTitle">Generate Title</button>
                <button type="button" class="mini" id="btnDesc">Generate Description</button>
                <button type="button" class="mini" id="btnTags">Generate Hashtags</button>
            </div>

            <div class="meta-row">
                <button type="button" class="mini" id="btnThumb">Create Thumbnail (9:16 PNG)</button>
            </div>
            <p class="note">Thumbnail background alternates: 1st click = mixed gradient, 2nd click = one solid colour, and so on.</p>

            <div id="metaBox">
                <div class="meta-head">
                    <span class="meta-title" id="metaTitle">AI YouTube Metadata</span>
                    <button type="button" class="mini meta-copy" id="btnCopy">Copy</button>
                </div>
                <div class="meta-out" id="metaOut"></div>
            </div>

            <div id="thumbBox">
                <div class="meta-head">
                    <span class="meta-title">AI Thumbnail - 1080x1920 PNG (safe area for Shorts / Reels)</span>
                    <a id="thumbDl" class="mini-link" href="/download/thumbnail" download="youtube_short_thumbnail.png">Download PNG</a>
                </div>
                <div class="thumb-wrap">
                    <div class="thumb-status" id="thumbStatus">Rendering 1080 x 1920 PNG...</div>
                    <img id="thumbImg" alt="generated thumbnail" />
                </div>
            </div>

            <div class="stages" id="stages">
                <div class="stage" data-stage="learning">1. Learning memory</div>
                <div class="stage" data-stage="models">2. Models</div>
                <div class="stage" data-stage="build">3. Building HTML</div>
                <div class="stage" data-stage="video">4. Recording</div>
                <div class="stage" data-stage="done">5. Done</div>
            </div>

            <div class="log-head">
                <span class="logs-label">Live Monitoring</span>
                <span class="pill" id="statusPill">Idle</span>
                <span class="timer" id="timer"></span>
            </div>
            <div class="logs-box" id="logs">Ready. Fill in the Question box, the Code/Logic box, or both.</div>
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
                    const el = (Date.now() - t0) / 1000;
                    timerEl.innerText = 'Elapsed ' + el.toFixed(1) + 's';

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
                    logsDiv.textContent = 'Please fill in the Question box or the Code/Logic box.\\n';
                    return;
                }

                btn.disabled = true;
                btn.innerText = 'AI is thinking...';
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
                        logsDiv.textContent += 'Error: ' + (res.error || 'the job did not start') + '\\n';
                        setPill('Failed', 'error');
                        stopTimer();
                    } else {
                        await pollJob(res.job_id, t0);
                    }
                } catch (err) {
                    logsDiv.textContent += 'Error: ' + err.message + '\\n';
                    setPill('Failed', 'error');
                    stopTimer();
                }

                btn.disabled = false;
                btn.innerText = 'Generate Video';
            };

            function setMetaBusy(busy) {
                metaBtns.forEach(b => b.disabled = busy);
            }

            async function runMeta(kind) {
                const q = qBox.value.trim();
                const logic = logicBox.value.trim();

                const labels = { title: 'Title', description: 'Description', hashtags: 'Hashtags' };
                metaBox.style.display = 'block';
                metaTitle.innerText = 'AI ' + labels[kind];
                metaOut.textContent = 'Generating ' + labels[kind].toLowerCase()
                    + ' from the question, code and logic...';
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

            btnThumb.onclick = async () => {
                const q = qBox.value.trim();
                const logic = logicBox.value.trim();

                thumbBox.style.display = 'block';
                thumbImg.style.display = 'none';
                thumbImg.removeAttribute('src');
                thumbStatus.style.display = 'block';
                thumbStatus.textContent = 'Rendering 1080 x 1920 PNG (background alternates each click)...';
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
                            metaBox.style.display = 'block';
                            metaTitle.innerText = 'Thumbnail background';
                            metaOut.textContent = (mode === 'solid')
                                ? 'Single solid colour background (no gradient).'
                                : 'Mixed gradient multi-colour background.';
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


def _clean_form_text(question: str, query_logic: str):
    question = (question or "").strip()
    query_logic = (query_logic or "").strip()

    low = question.lower()
    for pref in ("question:", "question -", "question-", "python question:", "q:"):
        if low.startswith(pref):
            question = question[len(pref):].strip()
            break

    if not query_logic and LAST_RUN.get("final_code"):
        query_logic = LAST_RUN["final_code"]
    if not query_logic and LAST_RUN.get("logic_explanation"):
        query_logic = LAST_RUN["logic_explanation"]
    if not question and LAST_RUN.get("question"):
        question = LAST_RUN["question"]
    return question, query_logic


@app.post("/generate")
async def generate(question: str = Form(""), query_logic: str = Form("")):
    global live_logs
    live_logs = []

    question = (question or "").strip()
    query_logic = (query_logic or "").strip()

    low = question.lower()
    for pref in ("question:", "question -", "question-", "python question:", "q:"):
        if low.startswith(pref):
            question = question[len(pref):].strip()
            break

    if not question and not query_logic:
        return JSONResponse({"error": "Please fill in the Question box or the Code/Logic box"},
                            status_code=400)

    if not question:
        question = "Explain and animate this Python code step by step"

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
        }

    threading.Thread(target=run_pipeline, args=(job_id, question, query_logic),
                     daemon=True).start()

    return JSONResponse({"job_id": job_id})


@app.post("/metadata")
async def metadata(question: str = Form(""), query_logic: str = Form(""), kind: str = Form("title")):
    question, query_logic = _clean_form_text(question, query_logic)

    if not question and not query_logic:
        return JSONResponse({"error": "Please fill in the Question box or the Code/Logic box"},
                            status_code=400)

    text = await asyncio.to_thread(generate_metadata, question, query_logic, kind)
    if not text:
        return JSONResponse({"error": "the models could not generate this - please try again"})

    return JSONResponse({"kind": kind, "text": text})


@app.post("/thumbnail")
async def thumbnail(question: str = Form(""), query_logic: str = Form("")):
    """Create a fresh 1080x1920 (9:16) thumbnail PNG.
    Background alternates on every call: 1st = gradient, 2nd = solid colour, ..."""
    question, query_logic = _clean_form_text(question, query_logic)

    if not question and not query_logic:
        return JSONResponse({"error": "Please fill in the Question box or the Code/Logic box"},
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
        })


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
    print(f"\nAI Python Video Generator Studio\nOpen: {url}\n")

    threading.Thread(target=open_browser_correctly, args=(url,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")