import os

path = os.path.join("app", "ui", "global_ai_lab_view.py")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

bad_ending = """</script>
</div>
'''

  window.ailabOrchInitAgentsHUD = function() {
    const box = document.getElementById("aiAgentsLiveTelemetry");
    if (!box || box._timer) return;
    const actions = [
      "[Central AI Manager] Auto-assigned Agent #14 (o3-mini) to compute AML CTR cash deposits >= ₹10L.",
      "[Snowflake Squad #52] Processed incremental batch: 0 full re-inserts, Fact append verified.",
      "[BigQuery Agent #19] Verified partition manifest for nanopro_cbs_bronze. 900 records synchronized.",
      "[DuckDB Agent #07] Parity checksum validated against Snowflake L0 staging: 0 mismatch.",
      "[Reports Agent #88] Verified RBI Form A & Form VIII CRR/SLR liquidity buffer ratios.",
      "[Reports Agent #34] Verified 21 FIU-IND report tables and refreshed NANOPRO_AML_FIU_IND_21_Reports.xlsx.",
      "[Self-Healing Sentinel #09] Scanned table quarantine index: 100% healthy, no stranded locks.",
      "[Multi-Channel Agent #04] Verified SMTP relay (<15MB payload) and Telegram channel broadcast link."
    ];
    let idx = 0;
    box._timer = setInterval(() => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString("en-GB", { timeZone: "Asia/Kolkata" }) + " IST";
      const div = document.createElement("div");
      div.innerHTML = `<span style="color:#64748B;">[${timeStr}]</span> ${actions[idx % actions.length]}`;
      box.insertBefore(div, box.firstChild);
      if (box.children.length > 30) box.removeChild(box.lastChild);
      idx += 1;
    }, 4000);
  };"""

correct_ending = """  window.ailabOrchInitAgentsHUD = function() {
    const box = document.getElementById("aiAgentsLiveTelemetry");
    if (!box || box._timer) return;
    const actions = [
      "[Central AI Manager] Auto-assigned Agent #14 (o3-mini) to compute AML CTR cash deposits >= ₹10L.",
      "[Snowflake Squad #52] Processed incremental batch: 0 full re-inserts, Fact append verified.",
      "[BigQuery Agent #19] Verified partition manifest for nanopro_cbs_bronze. 900 records synchronized.",
      "[DuckDB Agent #07] Parity checksum validated against Snowflake L0 staging: 0 mismatch.",
      "[Reports Agent #88] Verified RBI Form A & Form VIII CRR/SLR liquidity buffer ratios.",
      "[Reports Agent #34] Verified 21 FIU-IND report tables and refreshed NANOPRO_AML_FIU_IND_21_Reports.xlsx.",
      "[Self-Healing Sentinel #09] Scanned table quarantine index: 100% healthy, no stranded locks.",
      "[Multi-Channel Agent #04] Verified SMTP relay (<15MB payload) and Telegram channel broadcast link."
    ];
    let idx = 0;
    box._timer = setInterval(() => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString("en-GB", { timeZone: "Asia/Kolkata" }) + " IST";
      const div = document.createElement("div");
      div.innerHTML = `<span style="color:#64748B;">[${timeStr}]</span> ${actions[idx % actions.length]}`;
      box.insertBefore(div, box.firstChild);
      if (box.children.length > 30) box.removeChild(box.lastChild);
      idx += 1;
    }, 4000);
  };
</script>
</div>
'''"""

assert bad_ending in text, "bad_ending not found"
text = text.replace(bad_ending, correct_ending, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed script position inside HTML template!")
