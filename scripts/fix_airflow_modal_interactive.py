"""Fix Airflow modal interactive styles, add Explorer launch button, and ensure 100% clickability."""
import re

# 1. Update app/ui/global_ai_lab_view.py
with open('app/ui/global_ai_lab_view.py', 'r', encoding='utf-8') as f:
    view_code = f.read()

# Add Airflow Launch banner inside Explorer header in global_ai_lab_view.py
old_explorer_head = '''    <!-- Panel 2: DATA MODELING EXPLORER (AWS, Snowflake, BigQuery, DuckDB) -->
    <aside class="ailab-explorer" id="ailabExplorer">
      <div class="ailab-explorer-head">
        <div style="display:flex;align-items:center;gap:6px;">
          <span style="font-size:14px;">🗄️</span>
          <span class="ailab-explorer-title">Explorer</span>
          <span class="ailab-explorer-badge" id="ailabExplorerCount">4 Databases</span>
        </div>
        <div class="ailab-explorer-tools">
          <button class="ailab-iconbtn" onclick="ailabLoadExplorer(true)" title="Rescan Lakehouses">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.5 9a9 9 0 0114.9-3.4L23 10M1 14l4.6 4.4A9 9 0 0020.5 15"/></svg>
          </button>
          <button class="ailab-iconbtn" onclick="ailabToggleExplorer()" title="Hide Explorer">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </button>
        </div>
      </div>
      <div class="ailab-explorer-search">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
        <input type="text" id="ailabExplorerFilter" placeholder="Search databases, schemas, tables..." oninput="ailabFilterExplorer(this.value)">
      </div>'''

new_explorer_head = '''    <!-- Panel 2: DATA MODELING EXPLORER (AWS, Snowflake, BigQuery, DuckDB) -->
    <aside class="ailab-explorer" id="ailabExplorer">
      <div class="ailab-explorer-head">
        <div style="display:flex;align-items:center;gap:6px;">
          <span style="font-size:14px;">🗄️</span>
          <span class="ailab-explorer-title">Explorer</span>
          <span class="ailab-explorer-badge" id="ailabExplorerCount">4 Databases</span>
        </div>
        <div class="ailab-explorer-tools">
          <button type="button" class="ailab-iconbtn" onclick="ailabOpenAirflowModal()" title="Open Airflow Orchestrator & SFTP Hub" style="width:auto;padding:0 8px;gap:4px;color:#34D399;border-color:rgba(16,185,129,0.4);background:rgba(16,185,129,0.15);font-weight:700;font-size:11px;cursor:pointer;">
            <span>⏱️ Airflow</span>
          </button>
          <button class="ailab-iconbtn" onclick="ailabLoadExplorer(true)" title="Rescan Lakehouses">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.5 9a9 9 0 0114.9-3.4L23 10M1 14l4.6 4.4A9 9 0 0020.5 15"/></svg>
          </button>
          <button class="ailab-iconbtn" onclick="ailabToggleExplorer()" title="Hide Explorer">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
          </button>
        </div>
      </div>
      <!-- Persistent Airflow & SFTP Action Card inside Explorer -->
      <div style="padding:8px 12px;background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(6,182,212,0.1));border-bottom:1px solid rgba(16,185,129,0.3);display:flex;align-items:center;justify-content:space-between;">
        <div style="display:flex;align-items:center;gap:7px;">
          <span style="font-size:16px;">⏱️</span>
          <div>
            <div style="font-size:11.5px;font-weight:800;color:#F8FAFC;">Airflow Orchestrator</div>
            <div style="font-size:10px;color:#34D399;">8 DAGs • EOD T-1 • SFTP Hub</div>
          </div>
        </div>
        <button type="button" class="ailab-btn-primary" onclick="ailabOpenAirflowModal()" style="padding:4px 10px;font-size:11px;background:#10B981;border-color:#10B981;color:#FFFFFF;font-weight:800;cursor:pointer;border-radius:6px;box-shadow:0 0 10px rgba(16,185,129,0.4);">
          Launch ➔
        </button>
      </div>
      <div class="ailab-explorer-search">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
        <input type="text" id="ailabExplorerFilter" placeholder="Search databases, schemas, tables..." oninput="ailabFilterExplorer(this.value)">
      </div>'''

if old_explorer_head in view_code:
    view_code = view_code.replace(old_explorer_head, new_explorer_head, 1)
    print("SUCCESS: Added Explorer Airflow launch card in global_ai_lab_view.py")

# Update Modal inline style to fixed 999999
old_modal_tag = '<div class="ailab-modal-backdrop" id="ailabAirflowModal" onclick="ailabCloseAirflowModal(event)">'
new_modal_tag = '<div class="ailab-modal-backdrop" id="ailabAirflowModal" style="position:fixed !important;top:0 !important;left:0 !important;right:0 !important;bottom:0 !important;width:100vw !important;height:100vh !important;z-index:999999 !important;background:rgba(3,7,18,0.88) !important;backdrop-filter:blur(12px) !important;display:none;align-items:center;justify-content:center;padding:16px;box-sizing:border-box;" onclick="ailabCloseAirflowModal(event)">'

if old_modal_tag in view_code:
    view_code = view_code.replace(old_modal_tag, new_modal_tag, 1)
    print("SUCCESS: Updated modal style to fixed 999999 in global_ai_lab_view.py")

# Update open/close JS methods in global_ai_lab_view.py
old_js_open = '''  window.ailabOpenAirflowModal = async function() {
    const modal = document.getElementById("ailabAirflowModal");
    if (!modal) return;
    modal.classList.add("is-open");
    await ailabLoadAirflowDags();
    await ailabLoadSftpReports();
  };

  window.ailabCloseAirflowModal = function(e) {
    if (e && e.target !== e.currentTarget && !e.target.classList.contains("ailab-modal-close")) return;
    const modal = document.getElementById("ailabAirflowModal");
    if (modal) modal.classList.remove("is-open");
  };'''

new_js_open = '''  window.ailabOpenAirflowModal = async function() {
    console.log("[Airflow] Opening Airflow Orchestrator & SFTP Modal...");
    const modal = document.getElementById("ailabAirflowModal");
    if (!modal) {
      console.error("[Airflow] Modal element #ailabAirflowModal not found!");
      alert("Airflow modal element not found!");
      return;
    }
    modal.style.display = "flex";
    modal.classList.add("is-open");
    try {
      await ailabLoadAirflowDags();
    } catch (err) {
      console.error("[Airflow] Error loading DAGs:", err);
    }
    try {
      await ailabLoadSftpReports();
    } catch (err) {
      console.error("[Airflow] Error loading SFTP reports:", err);
    }
  };

  window.ailabCloseAirflowModal = function(e) {
    if (e && e.target !== e.currentTarget && !e.target.classList.contains("ailab-modal-close")) return;
    const modal = document.getElementById("ailabAirflowModal");
    if (modal) {
      modal.style.display = "none";
      modal.classList.remove("is-open");
    }
  };'''

if old_js_open in view_code:
    view_code = view_code.replace(old_js_open, new_js_open, 1)
    print("SUCCESS: Updated JS open/close methods in global_ai_lab_view.py")

# Update Topbar button styling for high visibility and pointer
old_btn = '''<button type="button" class="ailab-browse-btn" onclick="ailabOpenAirflowModal()" title="Apache Airflow Orchestrator, Medallion DAGs & SFTP Hub" style="background:rgba(16,185,129,0.15);border-color:rgba(16,185,129,0.4);color:#34D399;font-weight:700;">
        <span>⏱️ Airflow &amp; SFTP</span>
      </button>'''

new_btn = '''<button type="button" class="ailab-browse-btn" id="ailabAirflowTopbarBtn" onclick="ailabOpenAirflowModal()" title="Apache Airflow Orchestrator, Medallion DAGs & SFTP Hub" style="background:rgba(16,185,129,0.22) !important;border:1.5px solid #10B981 !important;box-shadow:0 0 12px rgba(16,185,129,0.4) !important;color:#34D399 !important;font-weight:800 !important;cursor:pointer !important;z-index:999 !important;display:inline-flex !important;align-items:center !important;gap:5px !important;">
        <span class="ailab-pulse-dot" style="background:#10B981 !important;box-shadow:0 0 6px #10B981 !important;width:7px;height:7px;border-radius:50%;display:inline-block;"></span>
        <span>⏱️ Airflow &amp; SFTP</span>
      </button>'''

if old_btn in view_code:
    view_code = view_code.replace(old_btn, new_btn, 1)
    print("SUCCESS: Updated topbar button in global_ai_lab_view.py")

with open('app/ui/global_ai_lab_view.py', 'w', encoding='utf-8') as f:
    f.write(view_code)
print("SUCCESS: Written updated global_ai_lab_view.py")
