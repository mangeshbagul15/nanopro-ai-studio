import os

path = os.path.join("app", "ui", "global_ai_lab_view.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Engine Filter pills in HTML (around lines 3660-3667)
old_filter_html = """        <button type="button" class="ailab-pill is-active" id="dagFilterAll" onclick="ailabOrchFilterEngine('all')">&#9889; All (12)</button>
        <button type="button" class="ailab-pill" id="dagFilterBigquery" onclick="ailabOrchFilterEngine('bigquery')">&#9729;&#65039; Google BigQuery (1)</button>
        <button type="button" class="ailab-pill" id="dagFilterAws" onclick="ailabOrchFilterEngine('aws')">&#128312; AWS S3 / Glue (2)</button>
        <button type="button" class="ailab-pill" id="dagFilterSnowflake" onclick="ailabOrchFilterEngine('snowflake')">&#10052;&#65039; Snowflake L0-L2 (6)</button>
        <button type="button" class="ailab-pill" id="dagFilterDuckdb" onclick="ailabOrchFilterEngine('duckdb')">&#129414; DuckDB (1)</button>
        <button type="button" class="ailab-pill" id="dagFilterReports" onclick="ailabOrchFilterEngine('reports')">&#128202; Reports &amp; Alerts (2)</button>"""

new_filter_html = """        <button type="button" class="ailab-pill is-active" id="dagFilterAll" onclick="ailabOrchFilterEngine('all')">&#9889; All (15)</button>
        <button type="button" class="ailab-pill" id="dagFilterBigquery" onclick="ailabOrchFilterEngine('bigquery')">&#9729;&#65039; Google BigQuery (1)</button>
        <button type="button" class="ailab-pill" id="dagFilterAws" onclick="ailabOrchFilterEngine('aws')">&#128312; AWS S3 / Glue (2)</button>
        <button type="button" class="ailab-pill" id="dagFilterSnowflake" onclick="ailabOrchFilterEngine('snowflake')">&#10052;&#65039; Snowflake L0-L2 (6)</button>
        <button type="button" class="ailab-pill" id="dagFilterDuckdb" onclick="ailabOrchFilterEngine('duckdb')">&#129414; DuckDB (1)</button>
        <button type="button" class="ailab-pill" id="dagFilterReports" onclick="ailabOrchFilterEngine('reports')">&#128202; Reports &amp; Alerts (5)</button>"""

assert old_filter_html in content, "old_filter_html not found"
content = content.replace(old_filter_html, new_filter_html, 1)

# 2. Update orchDialog to prevent stacking multiple overlays
old_dialog = """  function orchDialog(message, defaultValue) {
    return new Promise(resolve => {
      const isPrompt = defaultValue !== undefined;
      const wrap = document.createElement("div");
      wrap.style.cssText = "position:fixed;inset:0;z-index:30050;background:rgba(2,6,23,0.72);display:flex;align-items:center;justify-content:center;padding:18px;";"""

new_dialog = """  function orchDialog(message, defaultValue) {
    const prev = document.getElementById("orchDialogWrap");
    if (prev) prev.remove();
    return new Promise(resolve => {
      const isPrompt = defaultValue !== undefined;
      const wrap = document.createElement("div");
      wrap.id = "orchDialogWrap";
      wrap.style.cssText = "position:fixed;inset:0;z-index:30050;background:rgba(2,6,23,0.72);display:flex;align-items:center;justify-content:center;padding:18px;";"""

assert old_dialog in content, "old_dialog not found"
content = content.replace(old_dialog, new_dialog, 1)

# 3. Add engine helpers and window.ailabOrchFilterEngine, and update ailabOrchRenderDags, ailabOrchRun, ailabOrchPause
old_render_dags_block = """  window.ailabOrchRenderDags = function(data) {
    const box = document.getElementById("airflowDagsList");
    if (!box) return;
    const dags = data.dags || [];
    const countTab = document.getElementById("orchDagCountTab");
    if (countTab) countTab.textContent = `${dags.length} DAG${dags.length === 1 ? "" : "s"}`;
    if (!dags.length) {
      box.innerHTML = `<div style="text-align:center;padding:20px;color:#94A3B8;">No DAGs reported.</div>`;
      return;
    }
    const cycles = (data.cycles || {}).cycles || [];
    const schedules = data.cycle_schedules || {};

    box.innerHTML = dags.map(dag => {
      const [stageBg, stageFg] = orchStageColor(dag.stage);
      const metrics = [];
      if (dag.tables != null && dag.tables !== "") metrics.push(`<span style="color:#94A3B8;">tables</span> <strong style="color:#F8FAFC;">${orchEsc(dag.tables)}</strong>`);
      if (dag.rows != null && dag.rows !== "") metrics.push(`<span style="color:#94A3B8;">rows</span> <strong style="color:#F8FAFC;">${orchNum(dag.rows)}</strong>`);
      if (dag.duplicates_removed != null) metrics.push(`<span style="color:#94A3B8;">dupes removed</span> <strong style="color:#F8FAFC;">${orchNum(dag.duplicates_removed)}</strong>`);
      if (dag.run_id) metrics.push(`<span style="color:#94A3B8;">run</span> <code style="color:#CBD5E1;">${orchEsc(dag.run_id)}</code>`);

      const cycleStrip = dag.id === "bq_to_s3" ? `
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;">
          ${cycles.map(c => `
            <span style="background:rgba(30,41,59,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:3px 8px;font-size:10.5px;color:#CBD5E1;">
              ${orchEsc(c.cycle)} ${orchEsc(c.scheduled_ist)} IST ${orchBadge(c.state)}
              <button type="button" onclick="ailabOrchEditCycle('${orchEsc(c.cycle)}', '${orchEsc(c.scheduled_ist)}')" style="background:none;border:none;color:#38BDF8;cursor:pointer;font-size:10.5px;padding:0 2px;">edit</button>
            </span>`).join("")}
        </div>` : "";

      return `
        <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:6px;">
            <div style="display:flex;align-items:center;gap:8px;min-width:0;">
              <span style="background:${stageBg};color:${stageFg};font-size:9.5px;font-weight:800;padding:2px 7px;border-radius:4px;">${orchEsc(dag.stage)}</span>
              <span style="font-weight:800;color:#F8FAFC;font-size:13px;">${orchEsc(dag.name)}</span>
              <code style="font-size:10px;color:#64748B;">${orchEsc(dag.id)}</code>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
              ${dag.in_flight ? `<span style="font-size:10px;color:#38BDF8;">running...</span>` : ""}
              ${orchBadge(dag.status)}
            </div>
          </div>
          <div style="font-size:11.5px;color:#94A3B8;line-height:1.5;margin-bottom:6px;">${orchEsc(dag.description)}</div>
          <div style="font-size:11px;color:#CBD5E1;line-height:1.6;margin-bottom:6px;">${orchEsc(dag.detail)}</div>
          ${dag.last_error ? `<div style="background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.35);border-radius:6px;padding:6px 9px;font-size:11px;color:#FCA5A5;margin-bottom:6px;word-break:break-word;"><strong>Last failure ${orchEsc(String(dag.last_error.at || "").replace("T", " "))}:</strong> ${orchEsc(dag.last_error.message || "")}</div>` : ""}
          ${(dag.errors && dag.errors.length) ? `<div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.3);border-radius:6px;padding:6px 9px;font-size:11px;color:#FCA5A5;margin-bottom:6px;">${dag.errors.map(e => `<div><strong>${orchEsc(e.file || "")}</strong>: ${orchEsc(e.error || "")}</div>`).join("")}</div>` : ""}
          <div style="display:flex;gap:14px;flex-wrap:wrap;font-size:11px;margin-bottom:6px;">${metrics.join("")}</div>
          <div style="font-size:10.5px;color:#64748B;margin-bottom:8px;">Schedule: ${orchEsc(dag.schedule)}${dag.finished_at ? ` &bull; finished ${orchEsc(dag.finished_at)}` : ""}</div>
          ${cycleStrip}
          <div style="display:flex;gap:6px;flex-wrap:wrap;border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;margin-top:8px;">
            <button type="button" class="ailab-code-btn" onclick="ailabOrchRun('${orchEsc(dag.id)}')" style="font-size:11px;color:#34D399;border-color:rgba(16,185,129,0.4);">&#9654; ${dag.id === "alerts" ? "Send summary" : "Run now"}</button>
            <button type="button" class="ailab-code-btn" onclick="ailabOrchPause('${orchEsc(dag.id)}')" style="font-size:11px;color:${dag.paused ? "#34D399" : "#FBBF24"};border-color:rgba(255,255,255,0.2);">${dag.paused ? "&#9654; Resume" : "&#10074;&#10074; Pause"}</button>
            ${dag.id === "alerts" ? "" : `<button type="button" class="ailab-code-btn" onclick="ailabOrchRollback('${orchEsc(dag.id)}')" style="font-size:11px;color:#F87171;border-color:rgba(248,113,113,0.4);">&#9198; Rollback</button>`}
          </div>
        </div>`;
    }).join("");
  };

  window.ailabOrchRun = async function(dagId) {
    ailabOrchToast(`Dispatching ${dagId}...`, "#38BDF8");
    try {
      const res = await ailabAuthFetch(ORCH_API + "/dag/run", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dag_id: dagId, mode: "incremental" })
      });
      const data = await res.json();
      if (!res.ok) { ailabOrchToast(data.detail || "Run failed", "#F87171"); return; }
      const footer = document.getElementById("airflowFooterLeft");
      if (footer) footer.textContent = data.message || "Dispatched";
      ailabOrchToast(data.message || `${dagId} dispatched`, data.status === "dispatched" ? "#34D399" : "#FBBF24");
      setTimeout(() => ailabOrchRefreshAll(true), 2000);
    } catch (err) { ailabOrchToast("Run error: " + err.message, "#F87171"); }
  };

  window.ailabOrchPause = async function(dagId) {
    try {
      const res = await ailabAuthFetch(ORCH_API + "/dag/pause", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dag_id: dagId })
      });
      const data = await res.json();
      if (!res.ok) { ailabOrchToast(data.detail || "Pause failed", "#F87171"); return; }
      ailabOrchToast(`${dagId}: ${data.state || "updated"}`, data.state === "PAUSED" ? "#FBBF24" : "#34D399");
      await ailabOrchRefreshAll(true);
    } catch (err) { ailabOrchToast("Pause error: " + err.message, "#F87171"); }
  };"""

new_render_dags_block = """  window.ailabOrchCurrentEngine = "all";

  function orchDagEngine(id) {
    if (id === "bq_to_s3") return "bigquery";
    if (id === "sftp_to_s3" || id === "glue_catalog") return "aws";
    if (id.startsWith("snowflake_") || id.startsWith("bank_l") || id === "bank_raw_history") return "snowflake";
    if (id === "duckdb_report") return "duckdb";
    return "reports";
  }

  function orchEngineBadge(eng) {
    const b = {
      bigquery: ["rgba(56,189,248,0.15)", "#38BDF8", "&#9729;&#65039; BigQuery"],
      aws: ["rgba(251,146,60,0.15)", "#FB923C", "&#128312; AWS S3/Glue"],
      snowflake: ["rgba(147,197,253,0.15)", "#93C5FD", "&#10052;&#65039; Snowflake"],
      duckdb: ["rgba(234,179,8,0.15)", "#EAB308", "&#129414; DuckDB"],
      reports: ["rgba(52,211,153,0.15)", "#34D399", "&#128202; Report Mart"],
    }[eng] || ["rgba(148,163,184,0.15)", "#94A3B8", eng];
    return `<span style="background:${b[0]};color:${b[1]};font-size:9.5px;font-weight:700;padding:2px 6px;border-radius:4px;border:1px solid ${b[0]};">${b[2]}</span>`;
  }

  window.ailabOrchFilterEngine = function(engine) {
    window.ailabOrchCurrentEngine = engine || "all";
    const pillMap = {
      all: "dagFilterAll",
      bigquery: "dagFilterBigquery",
      aws: "dagFilterAws",
      snowflake: "dagFilterSnowflake",
      duckdb: "dagFilterDuckdb",
      reports: "dagFilterReports",
    };
    Object.entries(pillMap).forEach(([k, id]) => {
      const el = document.getElementById(id);
      if (el) {
        if (k === window.ailabOrchCurrentEngine) el.classList.add("is-active");
        else el.classList.remove("is-active");
      }
    });
    if (window.ailabOrchState && window.ailabOrchState.overview) {
      ailabOrchRenderDags(window.ailabOrchState.overview);
    }
  };

  window.ailabOrchRenderDags = function(data) {
    const box = document.getElementById("airflowDagsList");
    if (!box) return;
    window.ailabOrchState = window.ailabOrchState || {};
    window.ailabOrchState.overview = data;
    const allDags = data.dags || [];
    const countTab = document.getElementById("orchDagCountTab");
    if (countTab) countTab.textContent = `${allDags.length} DAG${allDags.length === 1 ? "" : "s"}`;
    if (!allDags.length) {
      box.innerHTML = `<div style="text-align:center;padding:20px;color:#94A3B8;">No DAGs reported.</div>`;
      return;
    }
    const curEngine = window.ailabOrchCurrentEngine || "all";
    const dags = curEngine === "all" ? allDags : allDags.filter(d => orchDagEngine(d.id) === curEngine);
    if (!dags.length) {
      box.innerHTML = `<div style="text-align:center;padding:24px;color:#94A3B8;">No DAGs found for engine <strong>${orchEsc(curEngine)}</strong>. <button type="button" class="ailab-code-btn" onclick="ailabOrchFilterEngine('all')" style="margin-left:8px;color:#38BDF8;">Show all (${allDags.length})</button></div>`;
      return;
    }
    const cycles = (data.cycles || {}).cycles || [];

    box.innerHTML = dags.map(dag => {
      const [stageBg, stageFg] = orchStageColor(dag.stage);
      const engBadge = orchEngineBadge(orchDagEngine(dag.id));
      const metrics = [];
      if (dag.tables != null && dag.tables !== "") metrics.push(`<span style="color:#94A3B8;">tables</span> <strong style="color:#F8FAFC;">${orchEsc(dag.tables)}</strong>`);
      if (dag.rows != null && dag.rows !== "") metrics.push(`<span style="color:#94A3B8;">rows</span> <strong style="color:#F8FAFC;">${orchNum(dag.rows)}</strong>`);
      if (dag.duplicates_removed != null) metrics.push(`<span style="color:#94A3B8;">dupes removed</span> <strong style="color:#F8FAFC;">${orchNum(dag.duplicates_removed)}</strong>`);
      if (dag.run_id) metrics.push(`<span style="color:#94A3B8;">run</span> <code style="color:#CBD5E1;">${orchEsc(dag.run_id)}</code>`);

      const cycleStrip = dag.id === "bq_to_s3" ? `
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;">
          ${cycles.map(c => `
            <span style="background:rgba(30,41,59,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:3px 8px;font-size:10.5px;color:#CBD5E1;">
              ${orchEsc(c.cycle)} ${orchEsc(c.scheduled_ist)} IST ${orchBadge(c.state)}
              <button type="button" onclick="ailabOrchEditCycle('${orchEsc(c.cycle)}', '${orchEsc(c.scheduled_ist)}')" style="background:none;border:none;color:#38BDF8;cursor:pointer;font-size:10.5px;padding:0 2px;">edit</button>
            </span>`).join("")}
        </div>` : "";

      return `
        <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;transition:border-color 0.15s ease;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:6px;">
            <div style="display:flex;align-items:center;gap:8px;min-width:0;flex-wrap:wrap;">
              <span style="background:${stageBg};color:${stageFg};font-size:9.5px;font-weight:800;padding:2px 7px;border-radius:4px;">${orchEsc(dag.stage)}</span>
              ${engBadge}
              <span style="font-weight:800;color:#F8FAFC;font-size:13px;">${orchEsc(dag.name)}</span>
              <code style="font-size:10px;color:#64748B;">${orchEsc(dag.id)}</code>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
              ${dag.in_flight ? `<span style="font-size:10px;color:#38BDF8;font-weight:700;">&#8635; running...</span>` : ""}
              ${orchBadge(dag.status)}
            </div>
          </div>
          <div style="font-size:11.5px;color:#94A3B8;line-height:1.5;margin-bottom:6px;">${orchEsc(dag.description)}</div>
          <div style="font-size:11px;color:#CBD5E1;line-height:1.6;margin-bottom:6px;">${orchEsc(dag.detail)}</div>
          ${dag.last_error ? `<div style="background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.35);border-radius:6px;padding:6px 9px;font-size:11px;color:#FCA5A5;margin-bottom:6px;word-break:break-word;"><strong>Last failure ${orchEsc(String(dag.last_error.at || "").replace("T", " "))}:</strong> ${orchEsc(dag.last_error.message || "")}</div>` : ""}
          ${(dag.errors && dag.errors.length) ? `<div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.3);border-radius:6px;padding:6px 9px;font-size:11px;color:#FCA5A5;margin-bottom:6px;">${dag.errors.map(e => `<div><strong>${orchEsc(e.file || "")}</strong>: ${orchEsc(e.error || "")}</div>`).join("")}</div>` : ""}
          <div style="display:flex;gap:14px;flex-wrap:wrap;font-size:11px;margin-bottom:6px;">${metrics.join("")}</div>
          <div style="font-size:10.5px;color:#64748B;margin-bottom:8px;">Schedule: ${orchEsc(dag.schedule)}${dag.finished_at ? ` &bull; finished ${orchEsc(dag.finished_at)}` : ""}</div>
          ${cycleStrip}
          <div style="display:flex;gap:6px;flex-wrap:wrap;border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;margin-top:8px;">
            <button type="button" class="ailab-code-btn" onclick="ailabOrchRun('${orchEsc(dag.id)}', this)" style="font-size:11px;color:#34D399;border-color:rgba(16,185,129,0.4);">&#9654; ${dag.id === "alerts" ? "Send summary" : "Run now"}</button>
            <button type="button" class="ailab-code-btn" onclick="ailabOrchPause('${orchEsc(dag.id)}', this)" style="font-size:11px;color:${dag.paused ? "#34D399" : "#FBBF24"};border-color:rgba(255,255,255,0.2);">${dag.paused ? "&#9654; Resume" : "&#10074;&#10074; Pause"}</button>
            ${dag.id === "alerts" ? "" : `<button type="button" class="ailab-code-btn" onclick="ailabOrchRollback('${orchEsc(dag.id)}', this)" style="font-size:11px;color:#F87171;border-color:rgba(248,113,113,0.4);">&#9198; Rollback</button>`}
          </div>
        </div>`;
    }).join("");
  };

  window.ailabOrchRun = async function(dagId, btnEl) {
    if (btnEl) {
      if (btnEl.disabled) return;
      btnEl.disabled = true;
      btnEl.dataset.origText = btnEl.innerHTML;
      btnEl.innerHTML = `<span style="display:inline-block;width:9px;height:9px;border:2px solid #34D399;border-top-color:transparent;border-radius:50%;animation:spin 0.6s linear infinite;vertical-align:middle;margin-right:4px;"></span> Running...`;
    }
    ailabOrchToast(`Dispatching ${dagId}...`, "#38BDF8");
    try {
      const res = await ailabAuthFetch(ORCH_API + "/dag/run", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dag_id: dagId, mode: "incremental" })
      });
      const data = await res.json();
      if (!res.ok) { ailabOrchToast(data.detail || "Run failed", "#F87171"); return; }
      const footer = document.getElementById("airflowFooterLeft");
      if (footer) footer.textContent = data.message || "Dispatched";
      ailabOrchToast(data.message || `${dagId} dispatched`, data.status === "dispatched" ? "#34D399" : "#FBBF24");
      setTimeout(() => ailabOrchRefreshAll(true), 1200);
    } catch (err) {
      ailabOrchToast("Run error: " + err.message, "#F87171");
    } finally {
      if (btnEl) {
        btnEl.disabled = false;
        if (btnEl.dataset.origText) btnEl.innerHTML = btnEl.dataset.origText;
      }
    }
  };

  window.ailabOrchPause = async function(dagId, btnEl) {
    if (btnEl) {
      if (btnEl.disabled) return;
      btnEl.disabled = true;
      btnEl.dataset.origText = btnEl.innerHTML;
      btnEl.innerHTML = `<span style="display:inline-block;width:9px;height:9px;border:2px solid #FBBF24;border-top-color:transparent;border-radius:50%;animation:spin 0.6s linear infinite;vertical-align:middle;margin-right:4px;"></span> Updating...`;
    }
    try {
      const res = await ailabAuthFetch(ORCH_API + "/dag/pause", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dag_id: dagId })
      });
      const data = await res.json();
      if (!res.ok) { ailabOrchToast(data.detail || "Pause failed", "#F87171"); return; }
      ailabOrchToast(`${dagId}: ${data.state || "updated"}`, data.state === "PAUSED" ? "#FBBF24" : "#34D399");
      await ailabOrchRefreshAll(true);
    } catch (err) {
      ailabOrchToast("Pause error: " + err.message, "#F87171");
    } finally {
      if (btnEl) {
        btnEl.disabled = false;
        if (btnEl.dataset.origText) btnEl.innerHTML = btnEl.dataset.origText;
      }
    }
  };"""

assert old_render_dags_block in content, "old_render_dags_block not found"
content = content.replace(old_render_dags_block, new_render_dags_block, 1)

# 4. Enhance ailabOrchRenderOutbound to show Excel badges and download links for all separate packages
old_outbound = """  window.ailabOrchRenderOutbound = function(out) {
    const box = document.getElementById("airflowSftpOutbound");
    if (!box) return;
    const reports = out.reports || [];
    box.innerHTML = reports.length ? reports.map(item => `
      <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(52,211,153,0.22);border-radius:7px;padding:8px 10px;display:flex;align-items:center;justify-content:space-between;gap:10px;">
        <div style="min-width:0;">
          <div style="font-size:12px;font-weight:700;color:#F8FAFC;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${orchEsc(item.filename)}</div>
          <div style="font-size:10.5px;color:#94A3B8;">${orchEsc(item.sftp_path)} &bull; ${orchEsc((item.bytes / 1024).toFixed(1))} KB &bull; ${orchEsc(item.modified || "")}</div>
        </div>
        ${item.download_url ? `<a href="${orchEsc(item.download_url)}" target="_blank" rel="noopener" class="ailab-code-btn" style="font-size:10.5px;color:#38BDF8;text-decoration:none;">Download</a>` : ""}
      </div>`).join("") : `<div style="text-align:center;padding:12px;color:#94A3B8;">No reports published to sftp/outbound/reports yet.</div>`;
  };"""

new_outbound = """  window.ailabOrchRenderOutbound = function(out) {
    const box = document.getElementById("airflowSftpOutbound");
    if (!box) return;
    const reports = out.reports || [];
    box.innerHTML = reports.length ? reports.map(item => {
      const isXlsx = String(item.filename || "").endsWith(".xlsx");
      const icon = isXlsx ? "&#128215; Excel" : "&#128196; CSV";
      const badgeBg = isXlsx ? "rgba(16,185,129,0.18)" : "rgba(56,189,248,0.18)";
      const badgeFg = isXlsx ? "#34D399" : "#38BDF8";
      return `
        <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(52,211,153,0.25);border-radius:8px;padding:9px 12px;display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:6px;">
          <div style="min-width:0;">
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="background:${badgeBg};color:${badgeFg};font-size:9.5px;font-weight:800;padding:2px 6px;border-radius:4px;">${icon}</span>
              <div style="font-size:12px;font-weight:700;color:#F8FAFC;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${orchEsc(item.filename)}</div>
            </div>
            <div style="font-size:10.5px;color:#94A3B8;margin-top:3px;"><code>${orchEsc(item.sftp_path)}</code> &bull; ${orchEsc((item.bytes / 1024).toFixed(1))} KB ${item.modified ? `&bull; ${orchEsc(String(item.modified).slice(0, 19).replace('T', ' '))}` : ""}</div>
          </div>
          ${item.download_url ? `<a href="${orchEsc(item.download_url)}" target="_blank" rel="noopener" class="ailab-code-btn" style="font-size:11px;color:#38BDF8;text-decoration:none;font-weight:700;white-space:nowrap;">&#11015; Download</a>` : ""}
        </div>`;
    }).join("") : `<div style="text-align:center;padding:12px;color:#94A3B8;">No reports published to sftp/outbound/reports yet.</div>`;
  };"""

assert old_outbound in content, "old_outbound not found"
content = content.replace(old_outbound, new_outbound, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched global_ai_lab_view.py")
