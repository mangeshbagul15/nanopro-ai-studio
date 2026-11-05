"""
NanoPro Data Modeling by AI - Snowflake-style conversational workspace UI.
"""


def get_data_modeling_html() -> str:
    return r'''
<div class="workspace-view" id="view-data_modeling_ai">
<style>
#view-data_modeling_ai .dm-app { position:relative; display:flex; flex-direction:column; height:calc(100vh - 128px); min-height:600px; background:#0B1120; border:1px solid #1E293B; border-radius:16px; overflow:hidden; box-shadow:0 18px 48px rgba(2,6,23,.45); }
#view-data_modeling_ai .dm-topbar { display:flex; align-items:center; justify-content:space-between; gap:14px; padding:12px 16px; background:linear-gradient(135deg, rgba(15,23,42,.98), rgba(30,27,75,.55)); border-bottom:1px solid #1E293B; flex-wrap:wrap; }
#view-data_modeling_ai .dm-brand { display:flex; align-items:center; gap:12px; min-width:0; }
#view-data_modeling_ai .dm-logo { width:38px; height:38px; display:flex; align-items:center; justify-content:center; border-radius:11px; font-size:20px; background:linear-gradient(135deg,#38BDF8,#6366F1); color:#FFF; box-shadow:0 6px 16px rgba(56,189,248,.35); }
#view-data_modeling_ai .dm-brand h2 { margin:0; font-size:15px; letter-spacing:.7px; color:#F8FAFC; font-weight:900; }
#view-data_modeling_ai .dm-brand p { margin:2px 0 0; font-size:11px; color:#94A3B8; }
#view-data_modeling_ai .dm-top-actions { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
#view-data_modeling_ai .dm-ai-badge { font-size:10.5px; font-weight:800; letter-spacing:.4px; padding:5px 10px; border-radius:999px; border:1px solid #334155; background:#0B1120; color:#94A3B8; white-space:nowrap; }
#view-data_modeling_ai .dm-ai-badge.live { color:#6EE7B7; border-color:#065F46; background:rgba(6,95,70,.22); }
#view-data_modeling_ai .dm-ai-badge.catalog { color:#FCD34D; border-color:#92400E; background:rgba(146,64,14,.18); }
#view-data_modeling_ai .dm-btn { padding:8px 13px; border-radius:9px; border:1px solid #334155; background:#1E293B; color:#E2E8F0; font-size:12px; font-weight:800; cursor:pointer; transition:background .15s, border-color .15s, transform .12s; white-space:nowrap; }
#view-data_modeling_ai .dm-btn:hover { background:#273549; border-color:#475569; transform:translateY(-1px); }
#view-data_modeling_ai .dm-btn.primary { background:linear-gradient(135deg,#0EA5E9,#2563EB); border:0; color:#FFF; box-shadow:0 6px 16px rgba(37,99,235,.3); }
#view-data_modeling_ai .dm-btn.ghost { background:transparent; }
#view-data_modeling_ai .dm-body { flex:1; display:flex; min-height:0; position:relative; }
#view-data_modeling_ai .dm-rail { width:300px; flex:0 0 auto; display:flex; flex-direction:column; min-height:0; background:#0F172A; border-right:1px solid #1E293B; transition:width .18s ease; }
#view-data_modeling_ai .dm-rail-head { display:flex; align-items:center; justify-content:flex-end; padding:8px 10px 0; }
#view-data_modeling_ai .dm-collapse { width:30px; height:30px; border-radius:8px; border:1px solid #334155; background:#0B1120; color:#94A3B8; font-size:14px; font-weight:900; cursor:pointer; line-height:1; }
#view-data_modeling_ai .dm-collapse:hover { color:#38BDF8; border-color:#0EA5E9; }
#view-data_modeling_ai .dm-rail-mini { display:none; flex-direction:column; gap:8px; padding:10px 8px; }
#view-data_modeling_ai .dm-mini-btn { display:flex; flex-direction:column; align-items:center; gap:3px; padding:9px 4px; border-radius:10px; border:1px solid transparent; background:transparent; color:#94A3B8; font-size:9px; font-weight:800; cursor:pointer; }
#view-data_modeling_ai .dm-mini-btn span:first-child { font-size:17px; }
#view-data_modeling_ai .dm-mini-btn:hover, #view-data_modeling_ai .dm-mini-btn.active { color:#38BDF8; background:rgba(14,165,233,.1); border-color:#0EA5E9; }
#view-data_modeling_ai .dm-rail-panels { display:flex; flex-direction:column; min-height:0; flex:1; }
#view-data_modeling_ai .dm-tabs { display:flex; gap:4px; padding:4px 10px 0; }
#view-data_modeling_ai .dm-tab { flex:1; padding:9px 6px; border:0; border-bottom:2px solid transparent; background:transparent; color:#94A3B8; font-size:11.5px; font-weight:800; letter-spacing:.3px; cursor:pointer; }
#view-data_modeling_ai .dm-tab.active { color:#38BDF8; border-bottom-color:#38BDF8; }
#view-data_modeling_ai .dm-panel { flex:1; min-height:0; display:flex; flex-direction:column; padding:10px; gap:8px; }
#view-data_modeling_ai .dm-panel[hidden] { display:none; }
#view-data_modeling_ai .dm-new-ws { width:100%; padding:10px; border-radius:9px; border:1px dashed #334155; background:rgba(14,165,233,.06); color:#38BDF8; font-size:12px; font-weight:800; cursor:pointer; }
#view-data_modeling_ai .dm-new-ws:hover { background:rgba(14,165,233,.14); border-color:#0EA5E9; }
#view-data_modeling_ai .dm-ws-list, #view-data_modeling_ai .dm-tree { flex:1; min-height:0; overflow:auto; display:flex; flex-direction:column; gap:6px; padding-right:2px; }
#view-data_modeling_ai .dm-ws { border:1px solid #1E293B; background:#0B1120; border-radius:10px; padding:9px 10px; cursor:pointer; transition:border-color .14s, background .14s; }
#view-data_modeling_ai .dm-ws:hover { border-color:#334155; background:#111C31; }
#view-data_modeling_ai .dm-ws.active { border-color:#0EA5E9; background:rgba(14,165,233,.1); box-shadow:inset 2px 0 0 #38BDF8; }
#view-data_modeling_ai .dm-ws-top { display:flex; align-items:center; gap:6px; }
#view-data_modeling_ai .dm-ws-name { flex:1; min-width:0; font-size:12.5px; font-weight:800; color:#E2E8F0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-ws-meta { margin-top:4px; font-size:10px; color:#64748B; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-icon-btn { border:0; background:transparent; color:#64748B; font-size:12px; cursor:pointer; padding:2px 4px; border-radius:5px; }
#view-data_modeling_ai .dm-icon-btn:hover { color:#38BDF8; background:rgba(14,165,233,.12); }
#view-data_modeling_ai .dm-rename { width:100%; background:#111C31; border:1px solid #0EA5E9; border-radius:6px; color:#F8FAFC; font-size:12px; font-weight:700; padding:4px 6px; outline:none; }
#view-data_modeling_ai .dm-filter { width:100%; background:#0B1120; border:1px solid #334155; border-radius:8px; color:#F8FAFC; font-size:11.5px; padding:8px 10px; outline:none; box-sizing:border-box; }
#view-data_modeling_ai .dm-filter:focus { border-color:#0EA5E9; box-shadow:0 0 0 3px rgba(14,165,233,.12); }
#view-data_modeling_ai .dm-db-head { display:flex; align-items:center; justify-content:space-between; font-size:10px; font-weight:800; letter-spacing:.5px; text-transform:uppercase; color:#64748B; padding:2px 2px 0; }
#view-data_modeling_ai .dm-mini-action { border:0; background:transparent; color:#64748B; font-size:14px; cursor:pointer; border-radius:5px; padding:0 4px; }
#view-data_modeling_ai .dm-mini-action:hover { color:#38BDF8; }
#view-data_modeling_ai .dm-db { border:1px solid #1E293B; border-radius:9px; background:#0B1120; overflow:hidden; }
#view-data_modeling_ai .dm-db-row, #view-data_modeling_ai .dm-schema-row, #view-data_modeling_ai .dm-table { width:100%; border:0; background:transparent; color:#CBD5E1; text-align:left; cursor:pointer; display:flex; align-items:center; gap:7px; }
#view-data_modeling_ai .dm-db-row { padding:9px 9px; }
#view-data_modeling_ai .dm-db-row:hover { background:rgba(14,165,233,.07); }
#view-data_modeling_ai .dm-caret { width:10px; flex:0 0 auto; color:#64748B; font-size:9px; transition:transform .14s; }
#view-data_modeling_ai .dm-db.open > .dm-db-row .dm-caret { transform:rotate(90deg); }
#view-data_modeling_ai .dm-db-ico { flex:0 0 auto; font-size:12px; width:20px; height:20px; display:flex; align-items:center; justify-content:center; border-radius:5px; background:rgba(56,189,248,.12); color:#38BDF8; font-weight:900; }
#view-data_modeling_ai .dm-db.ws .dm-db-ico { background:rgba(16,185,129,.14); color:#34D399; }
#view-data_modeling_ai .dm-db-name { flex:1; min-width:0; font-size:11.5px; font-weight:800; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-db-meta { flex:0 0 auto; font-size:9px; color:#64748B; font-weight:700; }
#view-data_modeling_ai .dm-schemas { border-top:1px solid #1E293B; }
#view-data_modeling_ai .dm-schema-row { padding:7px 9px 7px 22px; font-size:10.5px; font-weight:800; color:#94A3B8; }
#view-data_modeling_ai .dm-schema-row:hover { background:rgba(56,189,248,.05); color:#38BDF8; }
#view-data_modeling_ai .dm-tables { padding:1px 0 5px; }
#view-data_modeling_ai .dm-table { padding:6px 9px 6px 42px; font-size:10.5px; color:#94A3B8; }
#view-data_modeling_ai .dm-table:hover { background:rgba(99,102,241,.12); color:#E2E8F0; }
#view-data_modeling_ai .dm-t-ico { font-size:9px; color:#6366F1; }
#view-data_modeling_ai .dm-view-tag { margin-left:auto; font-size:8px; font-weight:900; color:#A78BFA; border:1px solid #6D28D9; border-radius:4px; padding:1px 4px; }
#view-data_modeling_ai .dm-main { flex:1; min-width:0; display:flex; flex-direction:column; background:radial-gradient(1200px 500px at 80% -10%, rgba(56,189,248,.07), transparent 60%), #0B1120; }
#view-data_modeling_ai .dm-chat-head { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:11px 16px; border-bottom:1px solid #1E293B; background:rgba(15,23,42,.6); }
#view-data_modeling_ai .dm-ws-title { font-size:13.5px; font-weight:900; color:#F8FAFC; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-ws-sub { margin-top:2px; font-size:10px; color:#64748B; }
#view-data_modeling_ai .dm-messages { flex:1; min-height:0; overflow:auto; padding:18px 18px 8px; display:flex; flex-direction:column; gap:14px; }
#view-data_modeling_ai .dm-msg { display:flex; gap:9px; align-items:flex-start; }
#view-data_modeling_ai .dm-msg.user { flex-direction:row-reverse; }
#view-data_modeling_ai .dm-avatar { flex:0 0 auto; width:30px; height:30px; border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:10.5px; font-weight:900; background:#1E293B; color:#94A3B8; border:1px solid #334155; }
#view-data_modeling_ai .dm-msg.ai .dm-avatar { background:linear-gradient(135deg,#0EA5E9,#6366F1); color:#FFF; border:0; }
#view-data_modeling_ai .dm-msg.user .dm-avatar { font-size:8.5px; letter-spacing:0; }
#view-data_modeling_ai .dm-bubble { max-width:min(760px, 86%); background:#0F172A; border:1px solid #1E293B; border-radius:12px; padding:11px 13px; }
#view-data_modeling_ai .dm-msg.user .dm-bubble { background:rgba(37,99,235,.18); border-color:rgba(37,99,235,.45); }
#view-data_modeling_ai .dm-text { font-size:12.5px; line-height:1.62; color:#E2E8F0; white-space:pre-wrap; word-break:break-word; }
#view-data_modeling_ai .dm-msg.user .dm-text { color:#DBEAFE; }
#view-data_modeling_ai .dm-sql { margin-top:9px; border:1px solid #1E293B; border-radius:8px; background:#020617; }
#view-data_modeling_ai .dm-sql summary { cursor:pointer; padding:6px 9px; font-size:10px; font-weight:800; letter-spacing:.4px; color:#38BDF8; text-transform:uppercase; }
#view-data_modeling_ai .dm-sql pre { margin:0; padding:9px 11px; font-size:11px; line-height:1.5; color:#93C5FD; overflow:auto; white-space:pre; font-family:Consolas,Monaco,monospace; border-top:1px solid #1E293B; }
#view-data_modeling_ai .dm-msg-foot { display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:8px; }
#view-data_modeling_ai .dm-mini-tag { font-size:9px; font-weight:800; letter-spacing:.3px; color:#94A3B8; background:#111C31; border:1px solid #334155; border-radius:999px; padding:2px 7px; }
#view-data_modeling_ai .dm-mini-tag.ok { color:#6EE7B7; border-color:#065F46; }
#view-data_modeling_ai .dm-mini-tag.err { color:#FCA5A5; border-color:#7F1D1D; }
#view-data_modeling_ai .dm-link-btn { border:1px solid #334155; background:#0B1120; color:#38BDF8; font-size:10px; font-weight:800; padding:4px 8px; border-radius:6px; cursor:pointer; }
#view-data_modeling_ai .dm-link-btn:hover { border-color:#0EA5E9; background:rgba(14,165,233,.1); }
#view-data_modeling_ai .dm-typing { display:inline-flex; gap:4px; align-items:center; padding:4px 0; }
#view-data_modeling_ai .dm-typing i { width:6px; height:6px; border-radius:50%; background:#38BDF8; animation:dmdot 1s infinite ease-in-out; }
#view-data_modeling_ai .dm-typing i:nth-child(2) { animation-delay:.15s; }
#view-data_modeling_ai .dm-typing i:nth-child(3) { animation-delay:.3s; }
@keyframes dmdot { 0%,80%,100% { opacity:.25; transform:translateY(0); } 40% { opacity:1; transform:translateY(-3px); } }
#view-data_modeling_ai .dm-empty { margin:auto; max-width:620px; text-align:center; padding:10px 8px; }
#view-data_modeling_ai .dm-empty-ico { width:58px; height:58px; margin:0 auto 12px; border-radius:16px; display:flex; align-items:center; justify-content:center; font-size:26px; background:linear-gradient(135deg,rgba(56,189,248,.18),rgba(99,102,241,.18)); border:1px solid #334155; }
#view-data_modeling_ai .dm-empty h3 { margin:0 0 5px; font-size:16px; color:#F8FAFC; }
#view-data_modeling_ai .dm-empty p { margin:0 0 14px; font-size:12px; color:#94A3B8; line-height:1.6; }
#view-data_modeling_ai .dm-suggest { display:flex; flex-wrap:wrap; gap:7px; justify-content:center; }
#view-data_modeling_ai .dm-suggest button { border:1px solid #334155; background:#0F172A; color:#CBD5E1; font-size:11px; padding:7px 10px; border-radius:999px; cursor:pointer; }
#view-data_modeling_ai .dm-suggest button:hover { border-color:#0EA5E9; color:#38BDF8; background:rgba(14,165,233,.08); }
#view-data_modeling_ai .dm-result { border-top:1px solid #1E293B; background:#0F172A; max-height:42%; display:flex; flex-direction:column; }
#view-data_modeling_ai .dm-result[hidden] { display:none; }
#view-data_modeling_ai .dm-result-head { display:flex; align-items:center; gap:10px; padding:8px 14px; border-bottom:1px solid #1E293B; }
#view-data_modeling_ai .dm-result-title { font-size:11.5px; font-weight:900; color:#F8FAFC; }
#view-data_modeling_ai .dm-result-meta { font-size:9.5px; color:#64748B; font-weight:700; }
#view-data_modeling_ai .dm-result-actions { margin-left:auto; display:flex; gap:6px; }
#view-data_modeling_ai .dm-result-body { overflow:auto; padding:0; min-height:0; }
#view-data_modeling_ai .dm-table-wrap { overflow:auto; max-width:100%; }
#view-data_modeling_ai table.dm-data-table { border-collapse:collapse; width:100%; font-size:11px; }
#view-data_modeling_ai table.dm-data-table th { position:sticky; top:0; background:#111C31; color:#93C5FD; text-align:left; font-weight:800; padding:7px 10px; border-bottom:1px solid #334155; white-space:nowrap; z-index:1; }
#view-data_modeling_ai table.dm-data-table td { padding:6px 10px; border-bottom:1px solid #16233b; color:#CBD5E1; white-space:nowrap; max-width:340px; overflow:hidden; text-overflow:ellipsis; }
#view-data_modeling_ai table.dm-data-table tr:hover td { background:rgba(56,189,248,.05); }
#view-data_modeling_ai .dm-composer { border-top:1px solid #1E293B; padding:10px 14px 4px; background:#0B1120; }
#view-data_modeling_ai .dm-compose-row { display:flex; align-items:flex-end; gap:9px; background:#0F172A; border:1px solid #334155; border-radius:13px; padding:8px 9px 8px 12px; transition:border-color .15s, box-shadow .15s; }
#view-data_modeling_ai .dm-compose-row:focus-within { border-color:#0EA5E9; box-shadow:0 0 0 3px rgba(14,165,233,.12); }
#view-data_modeling_ai .dm-compose-row textarea { flex:1; min-height:24px; max-height:160px; resize:none; background:transparent; border:0; outline:0; color:#F8FAFC; font-size:13px; line-height:1.5; font-family:inherit; padding:3px 0; }
#view-data_modeling_ai .dm-compose-row textarea::placeholder { color:#64748B; }
#view-data_modeling_ai .dm-send { flex:0 0 auto; width:36px; height:36px; border-radius:10px; border:0; background:linear-gradient(135deg,#0EA5E9,#2563EB); color:#FFF; font-size:16px; font-weight:900; cursor:pointer; display:flex; align-items:center; justify-content:center; }
#view-data_modeling_ai .dm-send:disabled { opacity:.5; cursor:not-allowed; }
#view-data_modeling_ai .dm-hint { text-align:center; font-size:9.5px; color:#475569; padding:4px 0 6px; }
#view-data_modeling_ai .dm-muted { color:#64748B; font-size:11.5px; padding:10px; }
#view-data_modeling_ai .dm-drawer-backdrop, #view-data_modeling_ai .dm-modal { position:absolute; inset:0; z-index:40; background:rgba(2,6,23,.72); display:none; }
#view-data_modeling_ai .dm-drawer-backdrop.open, #view-data_modeling_ai .dm-modal.open { display:flex; }
#view-data_modeling_ai .dm-drawer { margin-left:auto; width:min(480px,100%); height:100%; background:#0F172A; border-left:1px solid #334155; display:flex; flex-direction:column; animation:dmSlide .18s ease; }
@keyframes dmSlide { from { transform:translateX(24px); opacity:.4; } to { transform:translateX(0); opacity:1; } }
#view-data_modeling_ai .dm-drawer-head, #view-data_modeling_ai .dm-modal-head { display:flex; align-items:flex-start; justify-content:space-between; gap:10px; padding:14px 16px; border-bottom:1px solid #1E293B; }
#view-data_modeling_ai .dm-drawer-title, #view-data_modeling_ai .dm-modal-title { font-size:14px; font-weight:900; color:#F8FAFC; }
#view-data_modeling_ai .dm-drawer-sub { margin-top:3px; font-size:10px; color:#64748B; }
#view-data_modeling_ai .dm-drawer-body { flex:1; overflow:auto; padding:14px 16px; }
#view-data_modeling_ai .dm-stat-row { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:12px; }
#view-data_modeling_ai .dm-stat { font-size:10px; font-weight:800; color:#CBD5E1; background:#0B1120; border:1px solid #334155; border-radius:999px; padding:4px 9px; }
#view-data_modeling_ai .dm-section-title { font-size:10px; font-weight:900; letter-spacing:.6px; text-transform:uppercase; color:#64748B; margin:14px 0 6px; }
#view-data_modeling_ai .dm-drawer pre { margin:0; background:#020617; border:1px solid #1E293B; border-radius:8px; padding:9px 11px; font-size:10.5px; line-height:1.5; color:#93C5FD; overflow:auto; white-space:pre-wrap; }
#view-data_modeling_ai .dm-drawer-foot { padding:10px 16px; border-top:1px solid #1E293B; display:flex; gap:8px; }
#view-data_modeling_ai .dm-modal { align-items:center; justify-content:center; }
#view-data_modeling_ai .dm-modal-card { width:min(460px,92%); background:#0F172A; border:1px solid #334155; border-radius:14px; box-shadow:0 24px 60px rgba(2,6,23,.7); }
#view-data_modeling_ai .dm-modal-body { padding:16px; display:flex; flex-direction:column; gap:11px; }
#view-data_modeling_ai .dm-field label { display:block; font-size:10px; font-weight:900; letter-spacing:.5px; text-transform:uppercase; color:#94A3B8; margin-bottom:5px; }
#view-data_modeling_ai .dm-field input, #view-data_modeling_ai .dm-field select { width:100%; box-sizing:border-box; background:#0B1120; border:1px solid #334155; border-radius:8px; color:#F8FAFC; font-size:12.5px; padding:9px 10px; outline:none; }
#view-data_modeling_ai .dm-field input:focus, #view-data_modeling_ai .dm-field select:focus { border-color:#0EA5E9; }
#view-data_modeling_ai .dm-field input[type=file] { padding:7px; font-size:11px; color:#94A3B8; }
#view-data_modeling_ai .dm-field-note { font-size:10px; color:#64748B; line-height:1.5; }
#view-data_modeling_ai .dm-modal-foot { display:flex; justify-content:flex-end; gap:8px; padding:0 16px 16px; }
#view-data_modeling_ai .dm-toast { position:absolute; right:18px; bottom:78px; z-index:60; max-width:380px; padding:10px 13px; border-radius:10px; font-size:11.5px; font-weight:700; line-height:1.5; background:#0F172A; border:1px solid #334155; color:#E2E8F0; box-shadow:0 14px 34px rgba(2,6,23,.6); opacity:0; transform:translateY(8px); pointer-events:none; transition:opacity .18s, transform .18s; }
#view-data_modeling_ai .dm-toast.show { opacity:1; transform:translateY(0); }
#view-data_modeling_ai .dm-toast.ok { border-color:#065F46; color:#6EE7B7; }
#view-data_modeling_ai .dm-toast.err { border-color:#7F1D1D; color:#FCA5A5; }
#view-data_modeling_ai .dm-app.dm-collapsed .dm-rail { width:64px; }
#view-data_modeling_ai .dm-app.dm-collapsed .dm-rail-panels { display:none; }
#view-data_modeling_ai .dm-app.dm-collapsed .dm-rail-mini { display:flex; }
#view-data_modeling_ai .dm-app.dm-collapsed .dm-rail-head { justify-content:center; padding:8px 0 0; }
#view-data_modeling_ai .dm-app.dm-collapsed .dm-collapse { transform:rotate(180deg); }
@media (max-width: 900px) {
  #view-data_modeling_ai .dm-app { height:calc(100vh - 104px); min-height:520px; }
  #view-data_modeling_ai .dm-rail { position:absolute; left:0; top:0; bottom:0; z-index:25; width:270px; box-shadow:14px 0 40px rgba(2,6,23,.6); }
  #view-data_modeling_ai .dm-app.dm-collapsed .dm-rail { width:56px; box-shadow:none; }
  #view-data_modeling_ai .dm-messages { padding:12px; }
  #view-data_modeling_ai .dm-bubble { max-width:92%; }
  #view-data_modeling_ai .dm-brand p { display:none; }
}
</style>

<div class="dm-app" id="dmShell">
  <div class="dm-topbar">
    <div class="dm-brand">
      <div class="dm-logo">&#10052;</div>
      <div>
        <h2>DATA MODELING BY AI</h2>
        <p>Talk to every NanoPro database - no SQL, just results</p>
      </div>
    </div>
    <div class="dm-top-actions">
      <span class="dm-ai-badge" id="dmAiBadge">Checking AI...</span>
      <button class="dm-btn ghost" id="dmSfBtn" onclick="dmSetupSnowflake()" title="Create BANK_DB, schemas, sample table and pipeline metadata in Snowflake">&#10052; Snowflake setup</button>
      <button class="dm-btn ghost" onclick="dmNewSchema()" title="Create a new schema in the active workspace">&#43; Schema</button>
      <button class="dm-btn primary" onclick="dmUploadOpen()">&#8679; Upload CSV / Excel</button>
    </div>
  </div>

  <div class="dm-body">
    <aside class="dm-rail" id="dmRail">
      <div class="dm-rail-head">
        <button class="dm-collapse" id="dmCollapseBtn" onclick="dmToggleRail()" title="Minimize panel">&#171;</button>
      </div>
      <div class="dm-rail-mini">
        <button class="dm-mini-btn" data-section="workspaces" onclick="dmSetSection('workspaces')" title="Workspaces"><span>&#128193;</span><span>Workspaces</span></button>
        <button class="dm-mini-btn" data-section="databases" onclick="dmSetSection('databases')" title="Databases"><span>&#128451;</span><span>Databases</span></button>
      </div>
      <div class="dm-rail-panels">
        <div class="dm-tabs">
          <button class="dm-tab active" data-section="workspaces" onclick="dmSetSection('workspaces')">Workspaces</button>
          <button class="dm-tab" data-section="databases" onclick="dmSetSection('databases')">Databases</button>
        </div>
        <section class="dm-panel" data-panel="workspaces">
          <button class="dm-new-ws" onclick="dmCreateWorkspace()">&#43; New workspace</button>
          <div class="dm-ws-list" id="dmWorkspaceList"></div>
        </section>
        <section class="dm-panel" data-panel="databases" hidden>
          <input class="dm-filter" id="dmCatalogFilter" placeholder="Search databases or tables..." oninput="dmRenderTree()">
          <div class="dm-db-head">
            <span>All NanoPro databases</span>
            <button class="dm-mini-action" onclick="dmLoadCatalog(true)" title="Refresh catalog">&#8635;</button>
          </div>
          <div class="dm-tree" id="dmDatabaseTree"></div>
        </section>
      </div>
    </aside>

    <main class="dm-main">
      <div class="dm-chat-head">
        <div style="min-width:0;">
          <div class="dm-ws-title" id="dmActiveName">No workspace yet</div>
          <div class="dm-ws-sub" id="dmActiveId">Create a workspace to start talking to your data</div>
        </div>
        <button class="dm-link-btn" onclick="dmOpenCatalog('workspaces')">&#128193; Workspaces</button>
      </div>

      <div class="dm-messages" id="dmMessages">
        <div class="dm-empty" id="dmEmptyState">
          <div class="dm-empty-ico">&#10052;</div>
          <h3>Your data, in plain language</h3>
          <p>Ask for tables, joins, filters, reports or uploads. The AI writes and runs the SQL for you and shows the data below.</p>
          <div class="dm-suggest">
            <button data-prompt="List all databases and tables available in NanoPro with row counts." onclick="dmUsePrompt(this)">What data do I have?</button>
            <button data-prompt="Create a table called sales_orders with id, customer_name, city, amount and order_date, then insert 3 sample rows." onclick="dmUsePrompt(this)">Create a table with sample data</button>
            <button data-prompt="Use Snowflake: create a table BANK_DB.SALES.CUSTOMERS with customer data and show the contents." onclick="dmUsePrompt(this)">Create a Snowflake table</button>
            <button data-prompt="Join my workspace tables and show the top customers by total amount." onclick="dmUsePrompt(this)">Build a join and rank results</button>
            <button onclick="dmUploadOpen()">Upload CSV / Excel</button>
          </div>
        </div>
      </div>

      <div class="dm-result" id="dmResultPanel" hidden>
        <div class="dm-result-head">
          <span class="dm-result-title" id="dmResultTitle">Result</span>
          <span class="dm-result-meta" id="dmResultMeta"></span>
          <div class="dm-result-actions">
            <a class="dm-link-btn" id="dmResultDownload" href="#" hidden>&#8681; Download CSV</a>
            <button class="dm-link-btn" onclick="dmCloseResult()">Close</button>
          </div>
        </div>
        <div class="dm-result-body" id="dmResultBody"></div>
      </div>

      <div class="dm-composer">
        <div class="dm-compose-row">
          <textarea id="dmInput" rows="1" placeholder="Ask anything: create a table, join data, filter rows, build a report..."></textarea>
          <button class="dm-send" id="dmSend" onclick="dmSendMessage()" title="Send">&#8593;</button>
        </div>
        <div class="dm-hint">Enter to send &middot; Shift+Enter for a new line &middot; AI writes the SQL, you just decide</div>
      </div>
    </main>
  </div>

  <div class="dm-drawer-backdrop" id="dmTableBackdrop" onclick="dmCloseTable(event)">
    <div class="dm-drawer" onclick="event.stopPropagation()">
      <div class="dm-drawer-head">
        <div style="min-width:0;">
          <div class="dm-drawer-title" id="dmTableTitle">Table</div>
          <div class="dm-drawer-sub" id="dmTableSub"></div>
        </div>
        <button class="dm-icon-btn" onclick="dmCloseTable()" title="Close">&#10005;</button>
      </div>
      <div class="dm-drawer-body" id="dmTableBody"><div class="dm-muted">Loading table metadata...</div></div>
      <div class="dm-drawer-foot">
        <button class="dm-btn primary" onclick="dmAskAboutTable()">Ask AI about this table</button>
        <button class="dm-btn ghost" onclick="dmCloseTable()">Close</button>
      </div>
    </div>
  </div>

  <div class="dm-modal" id="dmUploadModal">
    <div class="dm-modal-card">
      <div class="dm-modal-head">
        <div>
          <div class="dm-modal-title">Upload CSV / Excel into a table</div>
          <div class="dm-drawer-sub">Stored inside the active workspace - safe and reversible</div>
        </div>
        <button class="dm-icon-btn" onclick="dmUploadClose()" title="Close">&#10005;</button>
      </div>
      <div class="dm-modal-body">
        <div class="dm-field">
          <label>File (CSV, XLSX, XLSM - max 25 MB, 50,000 rows)</label>
          <input type="file" id="dmUpFile" accept=".csv,.xlsx,.xlsm,text/csv">
        </div>
        <div class="dm-field">
          <label>Table name (leave blank to use the file name)</label>
          <input type="text" id="dmUpTable" placeholder="e.g. sales_orders">
        </div>
        <div class="dm-field">
          <label>Schema</label>
          <select id="dmUpSchema"><option value="main">main</option></select>
        </div>
        <div class="dm-field">
          <label>Mode</label>
          <select id="dmUpMode">
            <option value="create">Create a new table</option>
            <option value="append">Append to an existing table</option>
          </select>
          <div class="dm-field-note">Column types are detected automatically. Appending adds missing columns when needed.</div>
        </div>
      </div>
      <div class="dm-modal-foot">
        <button class="dm-btn ghost" onclick="dmUploadClose()">Cancel</button>
        <button class="dm-btn primary" id="dmUpSubmit" onclick="dmSubmitUpload()">Import data</button>
      </div>
    </div>
  </div>

  <div class="dm-modal" id="dmSchemaModal">
    <div class="dm-modal-card">
      <div class="dm-modal-head">
        <div>
          <div class="dm-modal-title">New schema</div>
          <div class="dm-drawer-sub">Schemas live inside the active workspace as separate database files</div>
        </div>
        <button class="dm-icon-btn" onclick="dmCloseSchema()" title="Close">&#10005;</button>
      </div>
      <div class="dm-modal-body">
        <div class="dm-field">
          <label>Schema name</label>
          <input type="text" id="dmSchemaName" placeholder="e.g. marketing">
        </div>
      </div>
      <div class="dm-modal-foot">
        <button class="dm-btn ghost" onclick="dmCloseSchema()">Cancel</button>
        <button class="dm-btn primary" onclick="dmSubmitSchema()">Create schema</button>
      </div>
    </div>
  </div>

  <div class="dm-modal" id="dmSfModal">
    <div class="dm-modal-card">
      <div class="dm-modal-head">
        <div>
          <div class="dm-modal-title">Connect Snowflake</div>
          <div class="dm-drawer-sub">Account XMUTKDJ-KP74023 &middot; MANGESHBAGUL15@GMAIL.COM &middot; ACCOUNTADMIN</div>
        </div>
        <button class="dm-icon-btn" onclick="dmCloseSfModal()" title="Close">&#10005;</button>
      </div>
      <div class="dm-modal-body">
        <div class="dm-field">
          <label>Snowflake password</label>
          <input type="password" id="dmSfPassword" placeholder="Password for MANGESHBAGUL15@GMAIL.COM" autocomplete="new-password">
          <div class="dm-field-note">Stored only in NanoPro's encrypted Credential Vault. Used to create BANK_DB, the SALES and L0_STAGING schemas, empty SALES_ORDERS and PIPELINE tables plus the revenue view. No sample rows are inserted.</div>
        </div>
      </div>
      <div class="dm-modal-foot">
        <button class="dm-btn ghost" onclick="dmCloseSfModal()">Cancel</button>
        <button class="dm-btn primary" id="dmSfSave" onclick="dmSubmitSfPassword()">Save &amp; set up</button>
      </div>
    </div>
  </div>

  <div class="dm-toast" id="dmToast"></div>
</div>
</div>
'''


def get_data_modeling_js() -> str:
    return r'''
<script>
(function () {
    if (window.__dmModuleLoaded) return;
    window.__dmModuleLoaded = true;

    var DM = {
        inited: false,
        bound: false,
        sending: false,
        workspaceId: localStorage.getItem('dm_active_ws') || '',
        railOpen: localStorage.getItem('dm_rail') !== 'closed',
        section: localStorage.getItem('dm_section') || 'workspaces',
        workspaces: [],
        catalog: [],
        openDbs: {},
        openSchemas: {},
        tableCtx: null,
        toastTimer: null
    };
    window.dmState = DM;

    function $(id) { return document.getElementById(id); }

    function dmEsc(value) {
        return String(value === null || value === undefined ? '' : value)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function dmAttr(value) { return dmEsc(value); }

    function dmToast(message, kind) {
        var el = $('dmToast');
        if (!el) return;
        el.textContent = message;
        el.className = 'dm-toast show' + (kind ? ' ' + kind : '');
        clearTimeout(DM.toastTimer);
        DM.toastTimer = setTimeout(function () { el.className = 'dm-toast'; }, 4200);
    }

    async function dmApi(path, options) {
        options = options || {};
        var headers = Object.assign({}, options.headers || {});
        if (options.body && typeof options.body === 'string') headers['Content-Type'] = 'application/json';
        var res = await fetch('/api/data_modeling' + path, Object.assign({}, options, {
            headers: headers,
            credentials: 'same-origin'
        }));
        if (res.status === 401) {
            window.location.href = '/login';
            throw new Error('Session expired. Please log in again.');
        }
        var data = null;
        try { data = await res.json(); } catch (err) { data = null; }
        if (!res.ok || (data && data.status === 'error')) {
            var detail = data && (data.message || data.detail);
            if (detail && typeof detail === 'object') detail = JSON.stringify(detail);
            throw new Error(detail || ('Request failed (' + res.status + ')'));
        }
        return data || {};
    }

    function dmFmtTime(stamp) {
        if (!stamp) return '';
        var d = new Date(stamp);
        if (isNaN(d.getTime())) return '';
        return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }

    function dmFmtBytes(bytes) {
        var n = Number(bytes || 0);
        if (!n) return '0 B';
        if (n >= 1073741824) return (n / 1073741824).toFixed(1) + ' GB';
        if (n >= 1048576) return (n / 1048576).toFixed(1) + ' MB';
        if (n >= 1024) return (n / 1024).toFixed(1) + ' KB';
        return n + ' B';
    }

    function dmTableHtml(columns, rows) {
        columns = columns || [];
        rows = rows || [];
        if (!columns.length) return '<div class="dm-muted">Statement completed - no rows returned.</div>';
        var head = columns.map(function (c) { return '<th>' + dmEsc(c) + '</th>'; }).join('');
        var body = rows.length ? rows.map(function (row) {
            return '<tr>' + columns.map(function (c) {
                var v = row[c];
                if (v === null || v === undefined) v = '';
                else if (typeof v === 'object') v = JSON.stringify(v);
                return '<td title="' + dmAttr(v) + '">' + dmEsc(v) + '</td>';
            }).join('') + '</tr>';
        }).join('') : '<tr><td colspan="' + columns.length + '" class="dm-muted">No rows.</td></tr>';
        return '<div class="dm-table-wrap"><table class="dm-data-table"><thead><tr>' + head + '</tr></thead><tbody>' + body + '</tbody></table></div>';
    }

    // ---------------------------------------------------------------- rail

    function dmApplyRail() {
        var shell = $('dmShell');
        if (!shell) return;
        shell.classList.toggle('dm-collapsed', !DM.railOpen);
        var btn = $('dmCollapseBtn');
        if (btn) btn.title = DM.railOpen ? 'Minimize panel' : 'Expand panel';
        document.querySelectorAll('#view-data_modeling_ai .dm-mini-btn').forEach(function (el) {
            el.classList.toggle('active', DM.railOpen && el.getAttribute('data-section') === DM.section);
        });
    }

    window.dmToggleRail = function () {
        DM.railOpen = !DM.railOpen;
        localStorage.setItem('dm_rail', DM.railOpen ? 'open' : 'closed');
        dmApplyRail();
    };

    window.dmSetSection = function (section) {
        DM.section = section === 'databases' ? 'databases' : 'workspaces';
        localStorage.setItem('dm_section', DM.section);
        DM.railOpen = true;
        localStorage.setItem('dm_rail', 'open');
        document.querySelectorAll('#view-data_modeling_ai .dm-tab').forEach(function (el) {
            el.classList.toggle('active', el.getAttribute('data-section') === DM.section);
        });
        document.querySelectorAll('#view-data_modeling_ai .dm-panel').forEach(function (el) {
            el.hidden = el.getAttribute('data-panel') !== DM.section;
        });
        dmApplyRail();
    };

    window.dmOpenCatalog = function (section) {
        window.dmSetSection(section || 'databases');
    };

    // ------------------------------------------------------------ workspaces

    function dmUpdateHeader() {
        var ws = null;
        for (var i = 0; i < DM.workspaces.length; i++) {
            if (DM.workspaces[i].id === DM.workspaceId) { ws = DM.workspaces[i]; break; }
        }
        var nameEl = $('dmActiveName');
        var idEl = $('dmActiveId');
        if (!nameEl || !idEl) return;
        if (ws) {
            nameEl.textContent = ws.name || 'Untitled workspace';
            idEl.textContent = ws.id + ' \u00b7 ' + (ws.table_count || 0) + ' table(s) \u00b7 ' + (ws.created_by || 'you');
        } else {
            nameEl.textContent = 'No workspace yet';
            idEl.textContent = 'Create a workspace to start talking to your data';
        }
    }

    function dmRenderWorkspaces() {
        var list = $('dmWorkspaceList');
        if (!list) return;
        if (!DM.workspaces.length) {
            list.innerHTML = '<div class="dm-muted">No workspaces yet.<br>Create one to get a private, writable database.</div>';
            return;
        }
        list.innerHTML = DM.workspaces.map(function (ws) {
            var active = ws.id === DM.workspaceId ? ' active' : '';
            var tables = ws.table_count || 0;
            return '<div class="dm-ws' + active + '" data-ws="' + dmAttr(ws.id) + '" onclick="dmSelectWorkspace(this.getAttribute(\'data-ws\'))">' +
                '<div class="dm-ws-top"><span class="dm-ws-name">' + dmEsc(ws.name || 'Untitled workspace') + '</span>' +
                '<button class="dm-icon-btn" title="Rename" onclick="event.stopPropagation(); dmRenameWorkspace(this.closest(\'.dm-ws\').getAttribute(\'data-ws\'))">&#9998;</button></div>' +
                '<div class="dm-ws-meta">' + dmEsc(ws.id) + ' \u00b7 ' + tables + ' table(s) \u00b7 ' + dmEsc(dmFmtTime(ws.updated_at)) + '</div>' +
                '</div>';
        }).join('');
    }

    window.dmLoadWorkspaces = async function () {
        try {
            var data = await dmApi('/workspaces');
            DM.workspaces = data.workspaces || [];
        } catch (err) {
            dmToast(err.message, 'err');
            DM.workspaces = [];
        }
        if (DM.workspaceId) {
            var exists = DM.workspaces.some(function (ws) { return ws.id === DM.workspaceId; });
            if (!exists) DM.workspaceId = '';
        }
        if (!DM.workspaceId && DM.workspaces.length) DM.workspaceId = DM.workspaces[0].id;
        dmRenderWorkspaces();
        dmUpdateHeader();
        return DM.workspaces;
    };

    window.dmCreateWorkspace = async function (silent) {
        try {
            var data = await dmApi('/workspaces', { method: 'POST', body: JSON.stringify({ name: '' }) });
            var ws = data.workspace;
            DM.workspaceId = ws.id;
            localStorage.setItem('dm_active_ws', ws.id);
            await dmLoadWorkspaces();
            await dmLoadCatalog(true);
            dmRenderMessages([]);
            dmUpdateHeader();
            if (!silent) dmToast('Workspace ' + ws.id + ' created', 'ok');
            var input = $('dmInput');
            if (input) input.focus();
            return ws.id;
        } catch (err) {
            dmToast(err.message, 'err');
            return '';
        }
    };

    window.dmSelectWorkspace = async function (workspaceId) {
        if (!workspaceId) return;
        DM.workspaceId = workspaceId;
        localStorage.setItem('dm_active_ws', workspaceId);
        dmRenderWorkspaces();
        dmUpdateHeader();
        dmCloseResult();
        await dmLoadMessages();
        if (window.innerWidth <= 900) {
            DM.railOpen = false;
            dmApplyRail();
        }
    };

    window.dmRenameWorkspace = function (workspaceId) {
        var row = document.querySelector('#view-data_modeling_ai .dm-ws[data-ws="' + workspaceId + '"]');
        if (!row) return;
        var nameEl = row.querySelector('.dm-ws-name');
        if (!nameEl) return;
        var current = nameEl.textContent;
        var input = document.createElement('input');
        input.className = 'dm-rename';
        input.value = current;
        nameEl.replaceWith(input);
        input.focus();
        input.select();
        var done = false;
        var commit = async function () {
            if (done) return;
            done = true;
            var value = input.value.trim();
            if (!value || value === current) {
                dmRenderWorkspaces();
                return;
            }
            try {
                await dmApi('/workspaces/' + encodeURIComponent(workspaceId), { method: 'PATCH', body: JSON.stringify({ name: value }) });
                dmToast('Workspace renamed', 'ok');
            } catch (err) {
                dmToast(err.message, 'err');
            }
            await dmLoadWorkspaces();
        };
        input.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter') { ev.preventDefault(); input.blur(); }
            else if (ev.key === 'Escape') { input.value = current; input.blur(); }
        });
        input.addEventListener('blur', commit, { once: true });
    };

    // --------------------------------------------------------------- catalog

    function dmFilterMatches(entry, schema, table, q) {
        if (!q) return true;
        var dbName = String(entry.name || '').toLowerCase();
        var dbId = String(entry.id || '').toLowerCase();
        var sName = String(schema || '').toLowerCase();
        var tName = String(table || '').toLowerCase();
        return dbName.indexOf(q) >= 0 || dbId.indexOf(q) >= 0 || sName.indexOf(q) >= 0 || tName.indexOf(q) >= 0;
    }

    function dmDbMeta(entry, tableTotal) {
        var status = String(entry.status || '');
        if (status === 'live') return tableTotal + ' tbl';
        if (status === 'not_configured') return 'not configured';
        if (status === 'driver_missing') return 'driver missing';
        if (status === 'unreachable') return 'unreachable';
        if (entry.error) return 'unavailable';
        return tableTotal + ' tbl';
    }

    window.dmRenderTree = function () {
        var tree = $('dmDatabaseTree');
        if (!tree) return;
        var filterEl = $('dmCatalogFilter');
        var q = filterEl ? filterEl.value.trim().toLowerCase() : '';
        if (!DM.catalog.length) {
            tree.innerHTML = '<div class="dm-muted">No databases detected yet.</div>';
            return;
        }
        var html = '';
        DM.catalog.forEach(function (entry) {
            var schemas = entry.schemas || [];
            var tableTotal = 0;
            var bodyHtml = '';
            var dbMatch = !q || dmFilterMatches(entry, '', '', q);
            schemas.forEach(function (schema) {
                var schemaMatch = !q || dbMatch || String(schema.name || '').toLowerCase().indexOf(q) >= 0;
                var tables = (schema.tables || []).filter(function (t) {
                    return schemaMatch || String(t.name || '').toLowerCase().indexOf(q) >= 0;
                });
                tableTotal += tables.length;
                if (q && !tables.length && !schemaMatch) return;
                var schemaKey = entry.id + '::' + schema.name;
                var open = !!q || !!DM.openSchemas[schemaKey];
                var rows = tables.length ? tables.map(function (t) {
                    return '<button class="dm-table" data-db="' + dmAttr(entry.id) + '" data-schema="' + dmAttr(schema.name) + '" data-table="' + dmAttr(t.name) + '">' +
                        '<span class="dm-t-ico">&#9638;</span>' + dmEsc(t.name) +
                        (t.type === 'view' ? '<span class="dm-view-tag">VIEW</span>' : '') +
                        '</button>';
                }).join('') : '<div class="dm-muted">No tables yet.</div>';
                bodyHtml += '<div class="dm-schema">' +
                    '<button class="dm-schema-row" data-schema-key="' + dmAttr(schemaKey) + '"><span class="dm-caret" style="' + (open ? 'transform:rotate(90deg);' : '') + '">&#9656;</span>' + dmEsc(schema.name) + '</button>' +
                    '<div class="dm-tables"' + (open ? '' : ' hidden') + '>' + rows + '</div></div>';
            });
            if (q && !tableTotal && !dbMatch) return;
            if (entry.detail) bodyHtml = '<div class="dm-muted">' + dmEsc(entry.detail) + '</div>' + bodyHtml;
            if (entry.error) bodyHtml = '<div class="dm-muted">' + dmEsc(entry.error) + '</div>' + bodyHtml;
            var openDb = !!q || !!DM.openDbs[entry.id];
            var engineTag = String(entry.engine || '').toUpperCase().slice(0, 5);
            var cls = entry.kind === 'workspace' ? ' ws' : '';
            html += '<div class="dm-db' + (openDb ? ' open' : '') + cls + '">' +
                '<button class="dm-db-row" data-db-toggle="' + dmAttr(entry.id) + '">' +
                '<span class="dm-caret">&#9656;</span>' +
                '<span class="dm-db-ico">' + dmEsc(engineTag) + '</span>' +
                '<span class="dm-db-name" title="' + dmAttr(entry.name) + '">' + dmEsc(entry.name) + '</span>' +
                '<span class="dm-db-meta">' + dmEsc(dmDbMeta(entry, tableTotal)) + '</span>' +
                '</button>' +
                '<div class="dm-schemas"' + (openDb ? '' : ' hidden') + '>' +
                (bodyHtml || '<div class="dm-muted">No tables yet.</div>') +
                '</div></div>';
        });
        tree.innerHTML = html || '<div class="dm-muted">Nothing matches that search.</div>';
    };

    window.dmLoadCatalog = async function (refresh) {
        try {
            var data = await dmApi('/catalog' + (refresh ? '?refresh=true' : ''));
            DM.catalog = data.databases || [];
        } catch (err) {
            dmToast(err.message, 'err');
            DM.catalog = [];
        }
        dmRenderTree();
        return DM.catalog;
    };

    window.dmLoadSfStatus = async function () {
        try {
            var data = await dmApi('/snowflake/status');
            var sf = data.snowflake || {};
            var btn = $('dmSfBtn');
            if (!btn) return;
            if (sf.configured) {
                btn.title = 'Snowflake ' + (sf.account || '') + ' \u00b7 ' + (sf.user || '') + ' - click to create or refresh the warehouse tables';
            } else if (!sf.password_set) {
                btn.title = 'Snowflake password is not set. Add it to the Credential Vault or SNOWFLAKE_PASSWORD, then click here.';
            } else {
                btn.title = 'Snowflake driver is missing on the server (requirements.txt).';
            }
        } catch (err) { /* status is best-effort */ }
    };

    window.dmSetupSnowflake = async function () {
        var btn = $('dmSfBtn');
        if (!btn || btn.disabled) return;
        var original = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '&#10052; Setting up...';
        dmToast('Creating the warehouse, schemas and empty tables...', '');
        try {
            var data = await dmApi('/snowflake/setup', { method: 'POST' });
            DM.openDbs['connection:NANO_PRO_SNOWFLAKE'] = true;
            DM.openSchemas['connection:NANO_PRO_SNOWFLAKE::' + data.database + '.' + data.sales_schema] = true;
            await dmLoadCatalog(true);
            window.dmSetSection('databases');
            var counts = data.row_counts || {};
            var tables = data.tables || [];
            var summary = 'Database ' + data.database + ' \u00b7 schemas ' + (data.schemas || []).join(', ') +
                '. ' + tables.length + ' object(s) ready, all empty (no sample rows): ' +
                tables.map(function (t) {
                    var n = counts[t];
                    return t + (n === undefined ? '' : ' (' + n + ' row' + (n === 1 ? '' : 's') + ')');
                }).join(', ') + '. Account ' + (data.account || '') + '.';
            window.dmShowResultPanel('Snowflake structure ready', summary, null);
            dmToast('Snowflake tables created - 0 sample rows', 'ok');
            window.dmLoadSfStatus();
        } catch (err) {
            window.dmShowResultPanel('Snowflake setup needs attention', err.message, null);
            dmToast(err.message, 'err');
            if (/password|credential|vault/i.test(err.message || '')) window.dmOpenSfPassword();
        } finally {
            btn.disabled = false;
            btn.innerHTML = original;
        }
    };

    window.dmOpenSfPassword = function () {
        var modal = $('dmSfModal');
        if (!modal) return;
        $('dmSfPassword').value = '';
        modal.classList.add('open');
        setTimeout(function () { var el = $('dmSfPassword'); if (el) el.focus(); }, 40);
    };

    window.dmCloseSfModal = function () {
        var modal = $('dmSfModal');
        if (modal) modal.classList.remove('open');
    };

    window.dmSubmitSfPassword = async function () {
        var input = $('dmSfPassword');
        var password = (input && input.value ? input.value : '').trim();
        if (!password) { dmToast('Enter the Snowflake password.', 'err'); return; }
        var btn = $('dmSfSave');
        btn.disabled = true;
        btn.textContent = 'Saving...';
        try {
            await dmApi('/snowflake/credentials', { method: 'POST', body: JSON.stringify({ password: password }) });
            if (input) input.value = '';
            window.dmCloseSfModal();
            dmToast('Snowflake password saved', 'ok');
            await window.dmSetupSnowflake();
        } catch (err) {
            dmToast(err.message, 'err');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Save & set up';
        }
    };

    function dmTreeClick(ev) {
        var tableBtn = ev.target.closest('[data-table]');
        if (tableBtn) {
            window.dmShowTable(tableBtn.getAttribute('data-db'), tableBtn.getAttribute('data-schema'), tableBtn.getAttribute('data-table'));
            return;
        }
        var schemaBtn = ev.target.closest('[data-schema-key]');
        if (schemaBtn) {
            var key = schemaBtn.getAttribute('data-schema-key');
            DM.openSchemas[key] = !DM.openSchemas[key];
            window.dmRenderTree();
            return;
        }
        var dbBtn = ev.target.closest('[data-db-toggle]');
        if (dbBtn) {
            var id = dbBtn.getAttribute('data-db-toggle');
            DM.openDbs[id] = !DM.openDbs[id];
            window.dmRenderTree();
        }
    }

    // ---------------------------------------------------------- table details

    window.dmShowTable = async function (dbId, schema, table) {
        DM.tableCtx = { dbId: dbId, schema: schema, table: table };
        var backdrop = $('dmTableBackdrop');
        var body = $('dmTableBody');
        $('dmTableTitle').textContent = table;
        $('dmTableSub').textContent = schema + ' \u00b7 ' + dbId;
        body.innerHTML = '<div class="dm-muted">Loading table metadata...</div>';
        backdrop.classList.add('open');
        try {
            var data = await dmApi('/table?db_id=' + encodeURIComponent(dbId) + '&schema=' + encodeURIComponent(schema) + '&table=' + encodeURIComponent(table));
            dmRenderTableDetails(data.table || {});
        } catch (err) {
            body.innerHTML = '<div class="dm-muted">' + dmEsc(err.message) + '</div>';
        }
    };

    function dmRenderTableDetails(details) {
        var body = $('dmTableBody');
        var columns = details.columns || [];
        var sample = details.sample || [];
        var sampleCols = columns.map(function (c) { return c.name; });
        var entity = details.table || 'table';
        $('dmTableTitle').textContent = entity;
        $('dmTableSub').textContent = (details.database || '') + ' \u00b7 ' + (details.schema || 'main');

        var html = '<div class="dm-stat-row">' +
            '<span class="dm-stat">' + (details.row_count === null || details.row_count === undefined ? 'Rows: n/a' : 'Rows: ' + details.row_count) + '</span>' +
            '<span class="dm-stat">Columns: ' + columns.length + '</span>' +
            (details.foreign_keys && details.foreign_keys.length ? '<span class="dm-stat">FK: ' + details.foreign_keys.length + '</span>' : '') +
            (details.indexes && details.indexes.length ? '<span class="dm-stat">Indexes: ' + details.indexes.length + '</span>' : '') +
            '</div>';
        if (details.error) html += '<div class="dm-muted">' + dmEsc(details.error) + '</div>';

        html += '<div class="dm-section-title">Columns</div>';
        if (columns.length) {
            html += '<div class="dm-table-wrap"><table class="dm-data-table"><thead><tr><th>#</th><th>Column</th><th>Data type</th><th>Null</th><th>Key</th><th>Default</th></tr></thead><tbody>';
            columns.forEach(function (c, idx) {
                html += '<tr><td>' + (idx + 1) + '</td><td>' + dmEsc(c.name) + '</td><td>' + dmEsc(c.data_type || 'TEXT') + '</td>' +
                    '<td>' + (c.not_null ? 'NOT NULL' : 'NULL') + '</td>' +
                    '<td>' + (c.is_pk ? 'PRIMARY KEY' : '') + '</td>' +
                    '<td>' + dmEsc(c.default === null || c.default === undefined ? '' : c.default) + '</td></tr>';
            });
            html += '</tbody></table></div>';
        } else {
            html += '<div class="dm-muted">No column metadata available.</div>';
        }

        if (sample.length) {
            html += '<div class="dm-section-title">Sample data (first 5 rows)</div>' + dmTableHtml(sampleCols, sample);
        }
        if (details.ddl) {
            html += '<div class="dm-section-title">Definition</div><pre>' + dmEsc(details.ddl) + '</pre>';
        }
        if (details.foreign_keys && details.foreign_keys.length) {
            html += '<div class="dm-section-title">Foreign keys</div><pre>' + dmEsc(JSON.stringify(details.foreign_keys, null, 2)) + '</pre>';
        }
        if (details.indexes && details.indexes.length) {
            html += '<div class="dm-section-title">Indexes</div><pre>' + dmEsc(JSON.stringify(details.indexes, null, 2)) + '</pre>';
        }
        body.innerHTML = html;
    }

    window.dmCloseTable = function (ev) {
        if (ev && ev.target && ev.target.id !== 'dmTableBackdrop') return;
        var backdrop = $('dmTableBackdrop');
        if (backdrop) backdrop.classList.remove('open');
    };

    window.dmAskAboutTable = function () {
        var ctx = DM.tableCtx;
        if (!ctx) return;
        var prompt = 'Explain the table "' + ctx.table + '" in schema "' + ctx.schema + '" of "' + ctx.dbId + '": what it stores, its key columns and how it can be joined with other tables.';
        window.dmCloseTable();
        var input = $('dmInput');
        if (input) {
            input.value = prompt;
            input.focus();
            dmAutoGrow(input);
        }
    };

    // ---------------------------------------------------------------- upload

    window.dmUploadOpen = async function () {
        if (!DM.workspaceId) {
            await dmCreateWorkspace(true);
            if (!DM.workspaceId) { dmToast('Create a workspace first.', 'err'); return; }
        }
        var modal = $('dmUploadModal');
        var select = $('dmUpSchema');
        var ws = null;
        DM.workspaces.forEach(function (w) { if (w.id === DM.workspaceId) ws = w; });
        var schemas = (ws && ws.schemas) || [{ name: 'main' }];
        select.innerHTML = schemas.map(function (s) {
            return '<option value="' + dmAttr(s.name) + '">' + dmEsc(s.name) + '</option>';
        }).join('');
        $('dmUpTable').value = '';
        $('dmUpFile').value = '';
        modal.classList.add('open');
    };

    window.dmUploadClose = function () {
        var modal = $('dmUploadModal');
        if (modal) modal.classList.remove('open');
    };

    window.dmSubmitUpload = async function () {
        var fileEl = $('dmUpFile');
        var file = fileEl && fileEl.files ? fileEl.files[0] : null;
        if (!file) { dmToast('Choose a CSV or Excel file first.', 'err'); return; }
        var btn = $('dmUpSubmit');
        btn.disabled = true;
        btn.textContent = 'Importing...';
        var form = new FormData();
        form.append('file', file);
        form.append('workspace_id', DM.workspaceId);
        form.append('table_name', $('dmUpTable').value.trim());
        form.append('mode', $('dmUpMode').value);
        form.append('schema', $('dmUpSchema').value);
        try {
            var data = await dmApi('/upload', { method: 'POST', body: form });
            window.dmUploadClose();
            dmToast('Imported ' + data.rows_inserted + ' rows into ' + data.schema + '.' + data.table, 'ok');
            await dmLoadWorkspaces();
            await dmLoadCatalog(true);
            dmShowResultPanel('Import complete',
                'Table ' + data.schema + '.' + data.table + ' now holds ' + data.total_rows + ' row(s). ' +
                data.rows_inserted + ' row(s) were added from ' + file.name + '.',
                { columns: (data.columns || []).map(function (c) { return c.name; }), rows: [], row_count: 0 });
            var input = $('dmInput');
            if (input && !input.value) {
                input.value = 'Show me the first 10 rows of ' + data.table + ' and summarise what this data contains.';
                dmAutoGrow(input);
            }
        } catch (err) {
            dmToast(err.message, 'err');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Import data';
        }
    };

    // ---------------------------------------------------------------- schema

    window.dmNewSchema = async function () {
        if (!DM.workspaceId) {
            await dmCreateWorkspace(true);
            if (!DM.workspaceId) return;
        }
        var modal = $('dmSchemaModal');
        $('dmSchemaName').value = '';
        modal.classList.add('open');
        setTimeout(function () { var el = $('dmSchemaName'); if (el) el.focus(); }, 40);
    };

    window.dmCloseSchema = function () {
        var modal = $('dmSchemaModal');
        if (modal) modal.classList.remove('open');
    };

    window.dmSubmitSchema = async function () {
        var name = ($('dmSchemaName').value || '').trim();
        if (!name) { dmToast('Enter a schema name.', 'err'); return; }
        try {
            await dmApi('/workspaces/' + encodeURIComponent(DM.workspaceId) + '/schemas', {
                method: 'POST', body: JSON.stringify({ name: name })
            });
            window.dmCloseSchema();
            dmToast('Schema ' + name + ' created', 'ok');
            await dmLoadWorkspaces();
            await dmLoadCatalog(true);
        } catch (err) {
            dmToast(err.message, 'err');
        }
    };

    // ---------------------------------------------------------------- chat

    function dmEmptyHtml() {
        return '<div class="dm-empty" id="dmEmptyState">' +
            '<div class="dm-empty-ico">&#10052;</div>' +
            '<h3>Your data, in plain language</h3>' +
            '<p>Ask for tables, joins, filters, reports or uploads. The AI writes and runs the SQL for you and shows the data below.</p>' +
            '<div class="dm-suggest">' +
            '<button data-prompt="List all databases and tables available in NanoPro with row counts." onclick="dmUsePrompt(this)">What data do I have?</button>' +
            '<button data-prompt="Create a table called sales_orders with id, customer_name, city, amount and order_date, then insert 3 sample rows." onclick="dmUsePrompt(this)">Create a table with sample data</button>' +
            '<button data-prompt="Use Snowflake: create a table BANK_DB.SALES.CUSTOMERS with customer data and show the contents." onclick="dmUsePrompt(this)">Create a Snowflake table</button>' +
            '<button data-prompt="Join my workspace tables and show the top customers by total amount." onclick="dmUsePrompt(this)">Build a join and rank results</button>' +
            '<button onclick="dmUploadOpen()">Upload CSV / Excel</button>' +
            '</div></div>';
    }

    function dmMsgHtml(msg) {
        var role = msg.role === 'user' ? 'user' : 'ai';
        var meta = msg.meta || {};
        var html = '<div class="dm-msg ' + role + '">' +
            '<div class="dm-avatar">' + (role === 'user' ? 'YOU' : 'AI') + '</div>' +
            '<div class="dm-bubble"><div class="dm-text">' + dmEsc(msg.content || '') + '</div>';
        var sql = msg.sql || meta.sql || '';
        if (sql) {
            html += '<details class="dm-sql"><summary>SQL used by the AI</summary><pre>' + dmEsc(sql) + '</pre></details>';
        }
        if (meta.error) {
            html += '<div class="dm-mini-tag err" style="display:inline-block;margin-top:8px;">' + dmEsc(meta.error) + '</div>';
        }
        if (role === 'ai') {
            html += '<div class="dm-msg-foot">';
            if (meta.model) html += '<span class="dm-mini-tag">' + dmEsc(meta.model) + '</span>';
            if (meta.fast_path) html += '<span class="dm-mini-tag ok">instant NLU</span>';
            if (meta.latency_ms) {
                var ms = Number(meta.latency_ms);
                var speed = ms >= 1000 ? (ms / 1000).toFixed(1) + 's' : Math.round(ms) + 'ms';
                html += '<span class="dm-mini-tag">' + speed + '</span>';
            }
            if (meta.row_count) html += '<span class="dm-mini-tag ok">' + meta.row_count + ' row(s)</span>';
            else if (meta.rows_affected) html += '<span class="dm-mini-tag ok">' + meta.rows_affected + ' affected</span>';
            if (meta.schedule_created) html += '<span class="dm-mini-tag ok">scheduled</span>';
            if (meta.run_id) html += '<button class="dm-link-btn" data-run="' + dmAttr(meta.run_id) + '">Show data</button>';
            if (sql) html += '<button class="dm-link-btn" data-copy="' + dmAttr(sql) + '">Copy SQL</button>';
            html += '</div>';
        }
        html += '</div></div>';
        return html;
    }

    window.dmRenderMessages = function (messages) {
        var box = $('dmMessages');
        if (!box) return;
        if (!messages || !messages.length) {
            box.innerHTML = dmEmptyHtml();
            return;
        }
        box.innerHTML = messages.map(dmMsgHtml).join('');
        box.scrollTop = box.scrollHeight;
    };

    window.dmLoadMessages = async function () {
        if (!DM.workspaceId) {
            window.dmRenderMessages([]);
            return;
        }
        try {
            var data = await dmApi('/workspaces/' + encodeURIComponent(DM.workspaceId) + '/messages');
            window.dmRenderMessages(data.messages || []);
        } catch (err) {
            dmToast(err.message, 'err');
        }
    };

    window.dmUsePrompt = function (btn) {
        var prompt = btn.getAttribute('data-prompt') || '';
        var input = $('dmInput');
        if (!input) return;
        input.value = prompt;
        input.focus();
        dmAutoGrow(input);
    };

    function dmAutoGrow(el) {
        if (!el) return;
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 160) + 'px';
    }

    function dmAppendTyping() {
        var box = $('dmMessages');
        if (!box) return;
        var empty = $('dmEmptyState');
        if (empty) empty.remove();
        var el = document.createElement('div');
        el.className = 'dm-msg ai';
        el.id = 'dmTypingRow';
        el.innerHTML = '<div class="dm-avatar">AI</div><div class="dm-bubble"><div class="dm-typing"><i></i><i></i><i></i></div></div>';
        box.appendChild(el);
        box.scrollTop = box.scrollHeight;
    }

    function dmRemoveTyping() {
        var el = $('dmTypingRow');
        if (el) el.remove();
    }

    function dmAppendLocalUser(text) {
        var box = $('dmMessages');
        if (!box) return;
        var empty = $('dmEmptyState');
        if (empty) empty.remove();
        var el = document.createElement('div');
        el.className = 'dm-msg user';
        el.innerHTML = '<div class="dm-avatar">YOU</div><div class="dm-bubble"><div class="dm-text">' + dmEsc(text) + '</div></div>';
        box.appendChild(el);
        box.scrollTop = box.scrollHeight;
    }

    window.dmSendMessage = async function () {
        if (DM.sending) return;
        var input = $('dmInput');
        if (!input) return;
        var text = (input.value || '').trim();
        if (!text) { input.focus(); return; }
        if (!DM.workspaceId) {
            var id = await dmCreateWorkspace(true);
            if (!id) return;
        }
        var sendBtn = $('dmSend');
        DM.sending = true;
        if (sendBtn) sendBtn.disabled = true;
        input.value = '';
        dmAutoGrow(input);
        dmAppendLocalUser(text);
        dmAppendTyping();
        try {
            var data = await dmApi('/chat', {
                method: 'POST',
                body: JSON.stringify({ workspace_id: DM.workspaceId, message: text })
            });
            dmRemoveTyping();
            if (data.workspace_created) {
                dmToast('New workspace "' + (data.workspace_created.name || '') + '" created', 'ok');
                await dmLoadWorkspaces();
            }
            if (data.schema_created) {
                dmToast('Schema ' + data.schema_created.schema + ' created', 'ok');
            }
            await dmLoadWorkspaces();
            await dmLoadCatalog();
            dmUpdateHeader();
            await dmLoadMessages();
            if (data.result) {
                dmRenderResult(data.result);
            } else if (data.error) {
                dmToast(data.error, 'err');
            }
        } catch (err) {
            dmRemoveTyping();
            dmToast(err.message, 'err');
            var box = $('dmMessages');
            if (box && !box.querySelector('.dm-msg.ai')) dmRenderMessages([]);
        } finally {
            DM.sending = false;
            if (sendBtn) sendBtn.disabled = false;
        }
    };

    // --------------------------------------------------------------- results

    window.dmShowResultPanel = function (title, note, result) {
        var panel = $('dmResultPanel');
        if (!panel) return;
        $('dmResultTitle').textContent = title || 'Result';
        var metaParts = [];
        if (result && result.row_count !== undefined) metaParts.push(result.row_count + ' row(s)');
        if (result && result.truncated) metaParts.push('preview capped');
        if (result && result.execution_time_ms) metaParts.push(result.execution_time_ms + ' ms');
        if (result) metaParts.push(result.run_id ? 'saved result' : 'not saved');
        $('dmResultMeta').textContent = metaParts.join(' \u00b7 ');
        var body = $('dmResultBody');
        var html = '';
        if (note) html += '<div class="dm-muted">' + dmEsc(note) + '</div>';
        if (result) html += dmTableHtml(result.columns || [], result.rows || []);
        body.innerHTML = html;
        var dl = $('dmResultDownload');
        if (result && result.run_id) {
            dl.href = '/api/data_modeling/runs/' + encodeURIComponent(result.run_id) + '/download';
            dl.hidden = false;
        } else {
            dl.hidden = true;
            dl.removeAttribute('href');
        }
        panel.hidden = false;
    };

    window.dmRenderResult = function (result) {
        var cols = (result.columns || []).length;
        window.dmShowResultPanel('Result', 'The AI ran this query in your workspace. ' + cols + ' column(s) returned.', result);
    };

    window.dmCloseResult = function () {
        var panel = $('dmResultPanel');
        if (panel) panel.hidden = true;
    };

    async function dmReplayRun(runId) {
        try {
            var data = await dmApi('/runs/' + encodeURIComponent(runId));
            var run = data.run || {};
            window.dmShowResultPanel('Saved result', 'Replayed from chat history.', {
                columns: run.columns || [],
                rows: run.rows || [],
                row_count: run.row_count || 0,
                run_id: run.run_id
            });
        } catch (err) {
            dmToast(err.message, 'err');
        }
    }

    async function dmCopyText(text) {
        try {
            await navigator.clipboard.writeText(text);
            dmToast('SQL copied', 'ok');
        } catch (err) {
            var ta = document.createElement('textarea');
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            try { document.execCommand('copy'); dmToast('SQL copied', 'ok'); }
            catch (e) { dmToast('Copy failed', 'err'); }
            ta.remove();
        }
    }

    function dmMessagesClick(ev) {
        var runBtn = ev.target.closest('[data-run]');
        if (runBtn) { dmReplayRun(runBtn.getAttribute('data-run')); return; }
        var copyBtn = ev.target.closest('[data-copy]');
        if (copyBtn) { dmCopyText(copyBtn.getAttribute('data-copy')); }
    }

    // ------------------------------------------------------------------ boot

    async function dmLoadStatus() {
        try {
            var data = await dmApi('/status');
            var badge = $('dmAiBadge');
            if (!badge) return;
            if (data.ai_ready) {
                badge.textContent = 'AI ready \u00b7 ' + (data.model || 'model');
                badge.className = 'dm-ai-badge live';
            } else {
                badge.textContent = 'Catalog mode \u00b7 AI key missing';
                badge.className = 'dm-ai-badge catalog';
            }
        } catch (err) {
            var badge = $('dmAiBadge');
            if (badge) { badge.textContent = 'Offline'; badge.className = 'dm-ai-badge'; }
        }
    }

    function dmBind() {
        if (DM.bound) return;
        DM.bound = true;
        var tree = $('dmDatabaseTree');
        if (tree) tree.addEventListener('click', dmTreeClick);
        var messages = $('dmMessages');
        if (messages) messages.addEventListener('click', dmMessagesClick);
        var input = $('dmInput');
        if (input) {
            input.addEventListener('input', function () { dmAutoGrow(input); });
            input.addEventListener('keydown', function (ev) {
                if (ev.key === 'Enter' && !ev.shiftKey && !ev.isComposing) {
                    ev.preventDefault();
                    window.dmSendMessage();
                }
            });
        }
        var uploadModal = $('dmUploadModal');
        if (uploadModal) {
            uploadModal.addEventListener('click', function (ev) {
                if (ev.target === uploadModal) window.dmUploadClose();
            });
        }
        var schemaModal = $('dmSchemaModal');
        if (schemaModal) {
            schemaModal.addEventListener('click', function (ev) {
                if (ev.target === schemaModal) window.dmCloseSchema();
            });
            var schemaInput = $('dmSchemaName');
            if (schemaInput) schemaInput.addEventListener('keydown', function (ev) {
                if (ev.key === 'Enter') { ev.preventDefault(); window.dmSubmitSchema(); }
            });
        }
        var sfModal = $('dmSfModal');
        if (sfModal) {
            sfModal.addEventListener('click', function (ev) {
                if (ev.target === sfModal) window.dmCloseSfModal();
            });
            var sfInput = $('dmSfPassword');
            if (sfInput) sfInput.addEventListener('keydown', function (ev) {
                if (ev.key === 'Enter') { ev.preventDefault(); window.dmSubmitSfPassword(); }
            });
        }
        document.addEventListener('keydown', function (ev) {
            if (ev.key !== 'Escape') return;
            window.dmUploadClose();
            window.dmCloseSchema();
            window.dmCloseSfModal();
        });
    }

    window.initDataModeling = async function () {
        if (!$('dmShell')) return;
        DM.inited = true;
        dmBind();
        window.dmSetSection(DM.section);
        dmApplyRail();
        await dmLoadStatus();
        await dmLoadSfStatus();
        await dmLoadWorkspaces();
        await dmLoadCatalog();
        dmUpdateHeader();
        if (DM.workspaceId) {
            await dmLoadMessages();
        } else {
            window.dmRenderMessages([]);
        }
    };

    window.dmRenderTree = window.dmRenderTree || function () {};
})();
</script>
'''
