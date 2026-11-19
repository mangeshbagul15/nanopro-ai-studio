import os
import re

path = os.path.join("app", "core", "snowflake_lakehouse.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern for SUM(IFF(column_name, 1, 0)) where column_name is a simple identifier (or table.col)
# Replace with COUNT_IF(TO_VARCHAR(col) IN ('Y','YES','TRUE','1') OR TRY_TO_BOOLEAN(TO_VARCHAR(col)) = TRUE)

def repl(m):
    col = m.group(1).strip()
    # If col already has comparison like "RE_KYC_DUE_DATE IS NOT NULL...", keep IFF
    if any(k in col.upper() for k in ("IS NOT NULL", "IS NULL", "<=", ">=", "<", ">", "=", " IN ")):
        return m.group(0)
    return f"COUNT_IF(TO_VARCHAR({col}) IN ('Y','YES','TRUE','1') OR TRY_TO_BOOLEAN(TO_VARCHAR({col})) = TRUE)"

new_content = re.sub(r"SUM\(IFF\(([^,\)]+),\s*1,\s*0\)\)", repl, content)

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully patched snowflake_lakehouse.py")
