"""Regression checks for the Data Modeling chat. Run: python scripts/dm_eval.py

Creates a throwaway workspace, exercises direct SQL, charts, cache, profiling and
the read-only lock, then deletes the workspace.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core import data_modeling_ai as dm

CSV = (
    b"Merchant,Category,Amount\n"
    b"Amazon,Shopping,1250\n"
    b"Swiggy,Food,480\n"
    b"Uber,Transport,220\n"
    b"Flipkart,Shopping,3100\n"
)

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f" :: {detail}"))


def last_assistant_meta(workspace_id, user):
    messages = dm.get_messages(workspace_id, 5, user=user) or []
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("meta") or {}
    return {}


def main():
    user = "eval"
    workspace = dm.create_workspace("DM eval workspace", user=user)
    wid = workspace["id"]
    try:
        dm.import_table(wid, "eval.csv", CSV, table_name="EVAL_TXN", mode="create", schema="main")

        result = dm.chat(
            wid,
            "SELECT Category, SUM(Amount) AS total FROM EVAL_TXN GROUP BY Category"
            " ORDER BY total DESC bar chart",
            user=user,
        )
        check("direct SQL runs with a trailing chart hint", not result.get("error"), str(result.get("error")))
        check("chart payload is built", bool(last_assistant_meta(wid, user).get("chart")))
        check("rows are returned", int((result.get("result") or {}).get("row_count") or 0) >= 2)

        dm.chat(wid, "SELECT COUNT(*) AS n FROM EVAL_TXN", user=user)
        repeat = dm.chat(wid, "SELECT COUNT(*) AS n FROM EVAL_TXN", user=user)
        check("repeat read hits the SQL cache", bool((repeat.get("result") or {}).get("cached")))

        profile = dm.chat(wid, "profile EVAL_TXN", user=user)
        reply = profile.get("reply") or ""
        check(
            "profile reports rows and amount range",
            "Data profile: EVAL_TXN" in reply and "min 220" in reply and "max 3100" in reply,
            reply[:220],
        )
        check("profile runs without a model call", profile.get("model") == "fast-nlu")

        dm.chat(wid, "remember: Amount is in INR, never paise", user=user)
        shown = dm.chat(wid, "what do you remember", user=user)
        check("workspace notes persist", "Amount is in INR" in (shown.get("reply") or ""), shown.get("reply"))
        prompt = dm._system_prompt(dm.get_workspace(wid, user=user) or {})
        check("workspace notes reach the model prompt", "Amount is in INR" in prompt)
        dm.chat(wid, "forget notes", user=user)
        cleared = dm.chat(wid, "what do you remember", user=user)
        check("workspace notes clear", "No notes saved" in (cleared.get("reply") or ""), cleared.get("reply"))

        dm.chat(wid, "lock workspace", user=user)
        blocked = dm.chat(wid, "CREATE TABLE LOCK_PROBE (id INTEGER)", user=user)
        check(
            "write is blocked while locked",
            "read-only" in str(blocked.get("error") or ""),
            str(blocked.get("error")),
        )

        try:
            dm.import_table(wid, "probe.csv", b"a,b\n1,2\n", table_name="LOCK_IMPORT")
            import_blocked = False
        except ValueError as exc:
            import_blocked = "read-only" in str(exc)
        check("file import is blocked while locked", import_blocked)

        dm.chat(wid, "unlock workspace", user=user)
        allowed = dm.chat(wid, "CREATE TABLE LOCK_PROBE (id INTEGER)", user=user)
        check("write is allowed after unlock", not allowed.get("error"), str(allowed.get("error")))
    finally:
        try:
            dm.delete_workspace(wid, user=user)
        except Exception as exc:
            print(f"cleanup failed: {exc}")

    failed = [name for name, ok in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
