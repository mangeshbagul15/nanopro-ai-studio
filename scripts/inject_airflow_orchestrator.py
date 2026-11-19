"""Inject Airflow Orchestrator and SFTP Modal into global_ai_lab_view.py."""
import re

path = 'app/ui/global_ai_lab_view.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add topbar button for Airflow & SFTP
btn_target = '<button type="button" class="ailab-browse-btn" onclick="ailabOpenModelCatalogModal()"'
btn_replacement = '''<button type="button" class="ailab-browse-btn" onclick="ailabOpenAirflowModal()" title="Apache Airflow Orchestrator, Medallion DAGs & SFTP Hub" style="background:rgba(16,185,129,0.15);border-color:rgba(16,185,129,0.4);color:#34D399;font-weight:700;">
        <span>⏱️ Airflow &amp; SFTP</span>
      </button>
      <button type="button" class="ailab-browse-btn" onclick="ailabOpenModelCatalogModal()"'''

if btn_target in content and 'ailabOpenAirflowModal()' not in content:
    content = content.replace(btn_target, btn_replacement, 1)
    print("SUCCESS: Added topbar button")

# 2. Add Modal HTML before closing </div><!-- End #view-global_ai_lab -->
modal_html = '''
<!-- AIRFLOW ORCHESTRATOR & SFTP HUB MODAL -->
<div class="ailab-modal-backdrop" id="ailabAirflowModal" onclick="ailabCloseAirflowModal(event)">
  <div class="ailab-modal" style="max-width:920px;max-height:88vh;" onclick="event.stopPropagation()">
    <div class="ailab-modal-head">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-size:22px;">⏱️</span>
        <div>
          <div style="font-size:15px;font-weight:700;color:#F8FAFC;">NanoPro Airflow Orchestrator &amp; SFTP Storage Hub</div>
          <div style="font-size:12px;color:#94A3B8;">8 Core Banking Projects • Medallion Pipelines • T-1 Daily EOD • Direct Self-Healing</div>
        </div>
      </div>
      <button type="button" class="ailab-modal-close" onclick="ailabCloseAirflowModal()">&times;</button>
    </div>

    <!-- Navigation Pills / Tabs -->
    <div class="ailab-modal-pills" style="padding:10px 16px;border-bottom:1px solid rgba(255,255,255,0.06);display:flex;gap:8px;">
      <button type="button" class="ailab-pill is-active" id="tabAirflowDags" onclick="ailabSwitchAirflowTab('dags')">🚀 Banking DAGs</button>
      <button type="button" class="ailab-pill" id="tabAirflowSftp" onclick="ailabSwitchAirflowTab('sftp')">📁 SFTP Reports &amp; WinSCP</button>
      <button type="button" class="ailab-pill" id="tabAirflowArchitecture" onclick="ailabSwitchAirflowTab('arch')">🛡️ L1 Quality Gate &amp; Email Rule</button>
    </div>

    <!-- TAB 1: 8 BANKING DAGS -->
    <div id="airflowTabDags" style="padding:14px;overflow-y:auto;max-height:calc(88vh - 180px);">
      <!-- Top Status Banner -->
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;">
        <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;">
          <div style="font-size:11px;color:#94A3B8;">AIRFLOW SCHEDULER</div>
          <div style="font-size:13px;font-weight:700;color:#34D399;margin-top:2px;">● ACTIVE (live DAGs)</div>
        </div>
        <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;">
          <div style="font-size:11px;color:#94A3B8;">REPORTING BASIS</div>
          <div style="font-size:13px;font-weight:700;color:#38BDF8;margin-top:2px;">📅 T-1 (Yesterday Close)</div>
        </div>
        <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;">
          <div style="font-size:11px;color:#94A3B8;">L1 QUALITY GATE</div>
          <div style="font-size:13px;font-weight:700;color:#A78BFA;margin-top:2px;">🛡️ 0 Nulls • 0 Dupes</div>
        </div>
        <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px;">
          <div style="font-size:11px;color:#94A3B8;">EMAIL ROUTING</div>
          <div style="font-size:12px;font-weight:600;color:#FBBF24;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">📧 5MB Attached/Link</div>
        </div>
      </div>

      <!-- DAGs List Container -->
      <div id="airflowDagsList" style="display:flex;flex-direction:column;gap:12px;"></div>
    </div>

    <!-- TAB 2: SFTP REPORTS & WINSCP -->
    <div id="airflowTabSftp" style="display:none;padding:14px;overflow-y:auto;max-height:calc(88vh - 180px);">
      <!-- WinSCP / FileZilla Credential Card -->
      <div style="background:linear-gradient(135deg,rgba(30,41,59,0.8),rgba(15,23,42,0.9));border:1px solid rgba(56,189,248,0.3);border-radius:10px;padding:14px;margin-bottom:14px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:18px;">🔐</span>
            <span style="font-size:14px;font-weight:700;color:#F8FAFC;">WinSCP / FileZilla SFTP Access Credentials</span>
          </div>
          <span style="background:rgba(16,185,129,0.2);color:#34D399;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">STATUS: ACTIVE</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;font-size:12px;color:#CBD5E1;">
          <div><strong style="color:#94A3B8;">Host:</strong> <code>nanopro-studio.onrender.com</code></div>
          <div><strong style="color:#94A3B8;">Port:</strong> <code>22</code></div>
          <div><strong style="color:#94A3B8;">Username:</strong> <code>mangeshbagul15</code></div>
          <div><strong style="color:#94A3B8;">Inbound Drop Path:</strong> <code>/data/sftp/inbound/</code></div>
          <div><strong style="color:#94A3B8;">Outbound Reports:</strong> <code>/data/sftp/outbound/reports/</code></div>
          <div><strong style="color:#94A3B8;">Supported:</strong> <code>.csv, .xlsx, | delimited</code></div>
        </div>
      </div>

      <!-- Reports List -->
      <div style="font-size:13px;font-weight:700;color:#F8FAFC;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;">
        <span>📊 Outbound Business Excel Reports (T-1 Daily Close)</span>
        <span style="font-size:11px;color:#94A3B8;">1-Click Web Download Available</span>
      </div>
      <div id="airflowSftpReportsList" style="display:flex;flex-direction:column;gap:8px;"></div>
    </div>

    <!-- TAB 3: QUALITY GATE & EMAIL RULE -->
    <div id="airflowTabArch" style="display:none;padding:14px;overflow-y:auto;max-height:calc(88vh - 180px);">
      <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:16px;">
        <h4 style="margin:0 0 10px 0;font-size:14px;color:#38BDF8;">🛡️ L1 Quality Gate Architecture (No L1 = No Report)</h4>
        <p style="font-size:12.5px;color:#CBD5E1;line-height:1.6;margin:0 0 14px 0;">
          कच्चा डेटा (L0_STAGING) थेट रिपोर्टमध्ये कधीही जात नाही. जोपर्यंत L1_HARMONIZED लेयरमध्ये डुप्लिकेट्स, Null व्हॅल्यूज, आणि Negative Balance चे कडक नियम पूर्णपणे पास (100% Validated) होत नाहीत, तोपर्यंत पुढील L2 आणि EOD Excel रिपोर्ट ब्लॉक केला जातो. एरर आल्यास त्वरित अलर्ट ट्रिगर होतो आणि युझर डॅशबोर्डवरूनच <strong>Rollback</strong> करून स्वच्छ डेटा पुन्हा लोड करू शकतो.
        </p>

        <h4 style="margin:0 0 10px 0;font-size:14px;color:#FBBF24;">📧 5MB ईमेल पॉलिसी आणि SFTP पाथ नियम</h4>
        <ul style="font-size:12.5px;color:#CBD5E1;line-height:1.6;margin:0;padding-left:18px;">
          <li><strong>ईमेल प्रेषक (Sender):</strong> <code>mangeshbagul15@gmail.com</code></li>
          <li><strong>ईमेल प्राप्तकर्ता (Recipient):</strong> <code>nanoproaistudio@gmail.com</code></li>
          <li><strong>जर फाईल ≤ 5MB असेल:</strong> Excel (.xlsx) फाईल थेट ईमेलला अटॅच होते, ईमेल बॉडीमध्ये की समरी आणि SFTP चा पाथ दिलेला असतो.</li>
          <li><strong>जर फाईल &gt; 5MB असेल:</strong> ईमेल बाऊन्स टाळण्यासाठी कोणतीही फाईल अटॅच होत नाही; केवळ ईमेल बॉडी समरी आणि SFTP डाऊनलोड लिंक पाठवली जाते.</li>
        </ul>
      </div>
    </div>

    <div class="ailab-modal-footer">
      <div style="font-size:11.5px;color:#94A3B8;">
        Central Command Pane • Snowflake BANK_DB • AWS S3 • Airflow • SFTP
      </div>
      <button type="button" class="ailab-btn-primary" onclick="ailabCloseAirflowModal()">Close</button>
    </div>
  </div>
</div>
'''

if 'id="ailabAirflowModal"' not in content:
    model_modal_pattern = r'(<div class="ailab-modal-backdrop" id="ailabModelModal"[^>]*>[\s\S]*?</div>\s*</div>)'
    match = re.search(model_modal_pattern, content)
    if match:
        content = content[:match.end()] + "\n" + modal_html + content[match.end():]
        print("SUCCESS: Injected Airflow Modal HTML")

# 3. Add Javascript controller methods for Airflow & SFTP
js_block = '''
  // =========================================================================
  // AIRFLOW ORCHESTRATOR & SFTP HUB CONTROLLER
  // =========================================================================
  window.ailabOpenAirflowModal = async function() {
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
  };

  window.ailabSwitchAirflowTab = function(tab) {
    document.getElementById("tabAirflowDags")?.classList.toggle("is-active", tab === "dags");
    document.getElementById("tabAirflowSftp")?.classList.toggle("is-active", tab === "sftp");
    document.getElementById("tabAirflowArchitecture")?.classList.toggle("is-active", tab === "arch");

    const tDags = document.getElementById("airflowTabDags");
    const tSftp = document.getElementById("airflowTabSftp");
    const tArch = document.getElementById("airflowTabArch");
    if (tDags) tDags.style.display = tab === "dags" ? "block" : "none";
    if (tSftp) tSftp.style.display = tab === "sftp" ? "block" : "none";
    if (tArch) tArch.style.display = tab === "arch" ? "block" : "none";
  };

  window.ailabLoadAirflowDags = async function() {
    const list = document.getElementById("airflowDagsList");
    if (!list) return;
    list.innerHTML = `<div style="text-align:center;padding:20px;color:#94A3B8;">Loading Airflow DAGs...</div>`;

    try {
      const res = await fetch("/api/banking/dag/list");
      const data = await res.json();
      const dags = data.dags || [];
      if (!dags.length) {
        list.innerHTML = `<div style="text-align:center;padding:20px;color:#94A3B8;">No active DAGs found.</div>`;
        return;
      }

      list.innerHTML = dags.map(d => `
        <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="font-size:16px;">⚡</span>
              <div>
                <span style="font-weight:700;color:#F8FAFC;font-size:13.5px;">${d.dag_id}</span>
                <span style="font-size:11px;color:#38BDF8;margin-left:6px;">(${d.project_name})</span>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="background:rgba(16,185,129,0.2);color:#34D399;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">● ${d.status}</span>
              <span style="font-size:11px;color:#94A3B8;">${d.schedule}</span>
            </div>
          </div>

          <div style="font-size:12px;color:#94A3B8;margin-bottom:10px;line-height:1.4;">
            ${d.description}
          </div>

          <!-- Medallion Task Pipeline -->
          <div style="display:flex;align-items:center;gap:6px;font-size:11px;margin-bottom:12px;flex-wrap:wrap;">
            <span style="background:rgba(217,119,6,0.2);color:#F59E0B;padding:2px 8px;border-radius:4px;">L0: ${d.l0_table}</span>
            <span style="color:#64748B;">➔</span>
            <span style="background:rgba(6,182,212,0.2);color:#22D3EE;padding:2px 8px;border-radius:4px;">L1: ${d.l1_table}</span>
            <span style="color:#64748B;">➔</span>
            <span style="background:rgba(16,185,129,0.2);color:#34D399;padding:2px 8px;border-radius:4px;">L2: ${d.l2_table}</span>
            <span style="color:#64748B;">➔</span>
            <span style="background:rgba(168,85,247,0.2);color:#C084FC;padding:2px 8px;border-radius:4px;">Excel: ${d.report_size_mb} MB (${d.email_rule_applied})</span>
          </div>

          <!-- Controls -->
          <div style="display:flex;align-items:center;justify-content:space-between;border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;">
            <div style="display:flex;align-items:center;gap:6px;">
              <button type="button" class="ailab-code-btn" onclick="ailabTriggerDagRun('${d.project_id}', 'INCREMENTAL_LOAD')" style="color:#34D399;border-color:rgba(16,185,129,0.4);font-size:11px;">
                ▶ Run Incremental (T-1)
              </button>
              <button type="button" class="ailab-code-btn" onclick="ailabTriggerDagRun('${d.project_id}', 'FULL_LOAD')" style="color:#38BDF8;border-color:rgba(56,189,248,0.4);font-size:11px;">
                🔄 Full Load
              </button>
              <button type="button" class="ailab-code-btn" onclick="ailabRollbackDagLayer('${d.project_id}', 'L1_HARMONIZED')" style="color:#F87171;border-color:rgba(248,113,113,0.4);font-size:11px;" title="Rollback dirty/broken data directly from UI without opening code!">
                ⏪ Rollback L1
              </button>
            </div>
            <a href="/api/sftp/reports/download?filename=${encodeURIComponent(d.report_filename)}" target="_blank" class="ailab-code-btn" style="color:#FBBF24;border-color:rgba(251,191,36,0.4);text-decoration:none;font-size:11px;">
              📥 Download EOD Excel
            </a>
          </div>
        </div>
      `).join("");
    } catch (err) {
      list.innerHTML = `<div style="text-align:center;padding:20px;color:#F87171;">Failed to load DAGs: ${err.message}</div>`;
    }
  };

  window.ailabTriggerDagRun = async function(projectId, loadType) {
    try {
      const res = await fetch("/api/banking/dag/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId, load_type: loadType, mode: "APPEND" })
      });
      const data = await res.json();
      if (data.status === "success") {
        alert(`✅ DAG Triggered Successfully!\\nProject: ${data.result.project_name}\\nLoad: ${data.result.load_type}\\nT-1 Basis: ${data.result.t1_basis}\\nQuality Gate: ${data.result.quality_gate}\\nSFTP: ${data.result.sftp_path}\\nEmail: ${data.result.email_dispatched.rule}`);
        await ailabLoadAirflowDags();
      } else {
        alert(`❌ Failed: ${data.detail || "Error"}`);
      }
    } catch (err) {
      alert(`Error triggering DAG: ${err.message}`);
    }
  };

  window.ailabRollbackDagLayer = async function(projectId, layer) {
    if (!confirm(`Are you sure you want to rollback ${projectId.toUpperCase()} to ${layer}?\\nThis will purge broken data and restore previous stable watermark.`)) return;
    try {
      const res = await fetch("/api/banking/dag/rollback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId, target_layer: layer })
      });
      const data = await res.json();
      if (data.status === "success") {
        alert(`✅ Rollback Complete!\\n${data.result.message}`);
        await ailabLoadAirflowDags();
      } else {
        alert(`❌ Rollback Failed: ${data.detail || "Error"}`);
      }
    } catch (err) {
      alert(`Error rolling back: ${err.message}`);
    }
  };

  window.ailabLoadSftpReports = async function() {
    const list = document.getElementById("airflowSftpReportsList");
    if (!list) return;

    try {
      const res = await fetch("/api/sftp/reports/list");
      const data = await res.json();
      const reports = data.reports || [];
      if (!reports.length) {
        list.innerHTML = `<div style="text-align:center;padding:15px;color:#94A3B8;">No reports generated yet.</div>`;
        return;
      }

      list.innerHTML = reports.map(r => `
        <div style="background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:10px 14px;display:flex;align-items:center;justify-content:space-between;">
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:18px;">📊</span>
            <div>
              <div style="font-weight:700;color:#F8FAFC;font-size:13px;">${r.filename}</div>
              <div style="font-size:11px;color:#94A3B8;">SFTP Path: <code>${r.sftp_path}</code></div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="background:${r.size_mb <= 5.0 ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)"};color:${r.size_mb <= 5.0 ? "#34D399" : "#FBBF24"};font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">
              ${r.size_formatted} • ${r.email_rule}
            </span>
            <a href="/api/sftp/reports/download?filename=${encodeURIComponent(r.filename)}" target="_blank" class="ailab-code-btn" style="color:#38BDF8;border-color:rgba(56,189,248,0.4);text-decoration:none;font-size:11px;padding:4px 10px;">
              📥 1-Click Download
            </a>
          </div>
        </div>
      `).join("");
    } catch (err) {
      list.innerHTML = `<div style="text-align:center;padding:15px;color:#F87171;">Failed to load SFTP reports: ${err.message}</div>`;
    }
  };
'''

if 'window.ailabOpenAirflowModal' not in content:
    # Inject before </script>
    content = content.replace('</script>', js_block + '\n</script>', 1)
    print("SUCCESS: Injected Airflow JS controller methods")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: Updated global_ai_lab_view.py")
