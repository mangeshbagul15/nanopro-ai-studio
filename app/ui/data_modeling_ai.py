"""
NanoPro Data Modeling by AI - three panel conversational studio.

Panel 1: Chats & Projects (pinned chats, chat list, project folders)
Panel 2: Explorer (project tables plus every real database: schemas, tables, columns)
Panel 3: Copilot chat with the data dock underneath.
"""


def get_data_modeling_html() -> str:
    return r'''
<div class="workspace-view" id="view-data_modeling_ai">
<style>
#view-data_modeling_ai {
  flex: 1 1 0% !important;
  width: 100% !important;
  height: 100% !important;
  max-height: 100% !important;
  min-height: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
  display: none;
}
#view-data_modeling_ai.active {
  display: flex !important;
  flex-direction: column !important;
}
body:has(#view-data_modeling_ai.active) #main-content-viewport,
#main-content-viewport:has(#view-data_modeling_ai.active) {
  padding: 0 !important;
  overflow: hidden !important;
}
#view-data_modeling_ai .dm-app {
  --dm-bg:#0B1119; --dm-panel:#0F1724; --dm-panel-2:#121C2B; --dm-line:#1E2A3C; --dm-line-2:#26364C;
  --dm-text:#E6EDF7; --dm-muted:#92A4BE; --dm-dim:#6B7C97;
  --dm-accent:#4C8DFF; --dm-accent-soft:rgba(76,141,255,.15);
  --dm-green:#3FB950; --dm-red:#F85149; --dm-amber:#E3B341;
  position:relative; display:flex; flex-direction:column;
  flex: 1 1 0% !important; width:100% !important; height:100% !important; max-height:100% !important; min-height:0 !important;
  background:var(--dm-bg); border:none !important; border-radius:0 !important; overflow:hidden !important;
  box-shadow:none !important; margin:0 !important;
  font-family:"Inter","Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  font-size:13px; line-height:1.5; color:var(--dm-text);
  -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;
}
#view-data_modeling_ai .dm-app button,
#view-data_modeling_ai .dm-app input,
#view-data_modeling_ai .dm-app textarea,
#view-data_modeling_ai .dm-app select { font-family:inherit; font-size:inherit; color:inherit; }
#view-data_modeling_ai .dm-app *, #view-data_modeling_ai .dm-app *::before, #view-data_modeling_ai .dm-app *::after { box-sizing:border-box; }
#view-data_modeling_ai .dm-svg { width:15px; height:15px; flex:0 0 auto; stroke:currentColor; fill:none; stroke-width:1.7; stroke-linecap:round; stroke-linejoin:round; }

/* ---------------------------------------------------------------- topbar */
#view-data_modeling_ai .dm-topbar { display:flex; align-items:center; gap:10px; padding:9px 12px; background:linear-gradient(180deg,#101A28,#0D1520); border-bottom:1px solid var(--dm-line); flex-wrap:nowrap; }
#view-data_modeling_ai .dm-top-left { display:flex; align-items:center; gap:4px; }
#view-data_modeling_ai .dm-brand { display:flex; align-items:center; gap:10px; min-width:0; flex:1; }
#view-data_modeling_ai .dm-logo { width:32px; height:32px; flex:0 0 auto; display:flex; align-items:center; justify-content:center; border-radius:9px; background:linear-gradient(135deg,#2F81F7,#1F6FEB); color:#FFF; box-shadow:0 4px 14px rgba(47,129,247,.35); }
#view-data_modeling_ai .dm-logo svg { width:18px; height:18px; stroke:#FFF; }
#view-data_modeling_ai .dm-brand-text { min-width:0; }
#view-data_modeling_ai .dm-brand-text h2 { margin:0; font-size:12.5px; font-weight:700; letter-spacing:.09em; color:#F2F6FC; white-space:nowrap; }
#view-data_modeling_ai .dm-brand-text p { margin:1px 0 0; font-size:11px; color:var(--dm-dim); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
#view-data_modeling_ai .dm-top-actions { display:flex; align-items:center; gap:6px; flex:0 0 auto; }
#view-data_modeling_ai .dm-ai-badge { font-size:10.5px; font-weight:600; letter-spacing:.02em; padding:4px 9px; border-radius:999px; border:1px solid var(--dm-line-2); background:#0B1320; color:var(--dm-muted); white-space:nowrap; }
#view-data_modeling_ai .dm-ai-badge.live { color:#7EE787; border-color:rgba(63,185,80,.45); background:rgba(63,185,80,.1); }
#view-data_modeling_ai .dm-ai-badge.catalog { color:#E3B341; border-color:rgba(227,179,65,.45); background:rgba(227,179,65,.1); }

/* --------------------------------------------------------------- buttons */
#view-data_modeling_ai .dm-btn { display:inline-flex; align-items:center; gap:6px; padding:6px 11px; border-radius:7px; border:1px solid var(--dm-line-2); background:#16202F; color:#D6E2F2; font-size:12px; font-weight:600; cursor:pointer; white-space:nowrap; transition:background .14s, border-color .14s, color .14s; }
#view-data_modeling_ai .dm-btn:hover { background:#1C293B; border-color:#33455F; color:#FFF; }
#view-data_modeling_ai .dm-btn.primary { background:linear-gradient(135deg,#2F81F7,#1F6FEB); border-color:#2F81F7; color:#FFF; }
#view-data_modeling_ai .dm-btn.primary:hover { background:linear-gradient(135deg,#4C8DFF,#2F81F7); }
#view-data_modeling_ai .dm-btn[disabled] { opacity:.55; cursor:not-allowed; }
#view-data_modeling_ai .dm-btn svg { width:14px; height:14px; }
#view-data_modeling_ai .dm-iconbtn { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; padding:0; border-radius:7px; border:1px solid transparent; background:transparent; color:var(--dm-muted); cursor:pointer; transition:background .14s, color .14s, border-color .14s; }
#view-data_modeling_ai .dm-iconbtn:hover { background:#1A2636; color:#F2F6FC; border-color:var(--dm-line); }
#view-data_modeling_ai .dm-iconbtn.is-on { background:var(--dm-accent-soft); color:#8FB8FF; border-color:rgba(76,141,255,.35); }
#view-data_modeling_ai .dm-iconbtn svg { width:15px; height:15px; }
#view-data_modeling_ai .dm-linkbtn { display:inline-flex; align-items:center; gap:5px; padding:4px 9px; border-radius:6px; border:1px solid var(--dm-line-2); background:#121C2B; color:#9DC0FF; font-size:11.5px; font-weight:600; cursor:pointer; text-decoration:none; white-space:nowrap; }
#view-data_modeling_ai .dm-linkbtn:hover { border-color:var(--dm-accent); background:rgba(76,141,255,.12); color:#CFE0FF; }
#view-data_modeling_ai .dm-linkbtn[hidden] { display:none; }
#view-data_modeling_ai .dm-linkbtn svg { width:13px; height:13px; }
#view-data_modeling_ai .dm-export { display:inline-flex; align-items:center; }
#view-data_modeling_ai .dm-export[hidden] { display:none; }
#view-data_modeling_ai .dm-export-select { height:27px; padding:0 5px; border:1px solid var(--dm-line-2); border-right:none; border-radius:6px 0 0 6px; background:#121C2B; color:#9DC0FF; font-size:11.5px; font-weight:600; cursor:pointer; outline:none; }
#view-data_modeling_ai .dm-export-select:hover, #view-data_modeling_ai .dm-export-select:focus { border-color:var(--dm-accent); background:rgba(76,141,255,.12); }
#view-data_modeling_ai .dm-export .dm-linkbtn { border-radius:0 6px 6px 0; }

/* ------------------------------------------------------------------ body */
#view-data_modeling_ai .dm-body { flex:1; display:flex; min-height:0; position:relative; }

/* ---------------------------------------------------- panel 1: chats */
#view-data_modeling_ai .dm-chats { position:relative; width:272px; flex:0 0 auto; display:flex; flex-direction:column; min-height:0; background:var(--dm-panel); border-right:1px solid var(--dm-line); }
#view-data_modeling_ai .dm-explorer { position:relative; width:292px; flex:0 0 auto; display:flex; flex-direction:column; min-height:0; background:#0D1520; border-right:1px solid var(--dm-line); }
#view-data_modeling_ai .dm-app.hide-chats .dm-chats,
#view-data_modeling_ai .dm-app.hide-explorer .dm-explorer { display:none; }
#view-data_modeling_ai .dm-panel-head { display:flex; align-items:center; gap:6px; height:44px; padding:0 8px 0 12px; border-bottom:1px solid var(--dm-line); flex:0 0 auto; }
#view-data_modeling_ai .dm-panel-title { flex:1; min-width:0; font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#A9BBD4; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
#view-data_modeling_ai .dm-panel-tools { display:flex; align-items:center; gap:2px; }
#view-data_modeling_ai .dm-panel-scroll { flex:1; min-height:0; overflow:auto; overscroll-behavior:contain; padding:8px 6px 12px; scrollbar-width:thin; scrollbar-color:#2A3A50 transparent; }
#view-data_modeling_ai .dm-panel-scroll::-webkit-scrollbar, #view-data_modeling_ai .dm-tree::-webkit-scrollbar, #view-data_modeling_ai .dm-messages::-webkit-scrollbar, #view-data_modeling_ai .dm-data-body::-webkit-scrollbar, #view-data_modeling_ai .dm-table-wrap::-webkit-scrollbar, #view-data_modeling_ai .dm-sql pre::-webkit-scrollbar { width:10px; height:10px; }
#view-data_modeling_ai .dm-panel-scroll::-webkit-scrollbar-thumb, #view-data_modeling_ai .dm-tree::-webkit-scrollbar-thumb, #view-data_modeling_ai .dm-messages::-webkit-scrollbar-thumb, #view-data_modeling_ai .dm-data-body::-webkit-scrollbar-thumb, #view-data_modeling_ai .dm-table-wrap::-webkit-scrollbar-thumb, #view-data_modeling_ai .dm-sql pre::-webkit-scrollbar-thumb { background:#3B5472; border-radius:8px; border:2px solid transparent; background-clip:content-box; }
#view-data_modeling_ai .dm-panel-scroll::-webkit-scrollbar-thumb:hover, #view-data_modeling_ai .dm-tree::-webkit-scrollbar-thumb:hover, #view-data_modeling_ai .dm-messages::-webkit-scrollbar-thumb:hover, #view-data_modeling_ai .dm-data-body::-webkit-scrollbar-thumb:hover, #view-data_modeling_ai .dm-table-wrap::-webkit-scrollbar-thumb:hover, #view-data_modeling_ai .dm-sql pre::-webkit-scrollbar-thumb:hover { background:#4F6E92; background-clip:content-box; }
#view-data_modeling_ai .dm-panel-scroll::-webkit-scrollbar-track, #view-data_modeling_ai .dm-tree::-webkit-scrollbar-track, #view-data_modeling_ai .dm-messages::-webkit-scrollbar-track, #view-data_modeling_ai .dm-data-body::-webkit-scrollbar-track { background:transparent; }
#view-data_modeling_ai .dm-sec { margin-bottom:8px; }
#view-data_modeling_ai .dm-sec-head { display:flex; align-items:center; gap:6px; padding:6px 8px 5px; font-size:10.5px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--dm-dim); }
#view-data_modeling_ai .dm-sec-head > span:first-child { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-sec-count { font-size:10px; font-weight:600; color:var(--dm-dim); letter-spacing:0; }
#view-data_modeling_ai .dm-sec-add { width:20px; height:20px; padding:0; border:0; background:transparent; color:var(--dm-dim); border-radius:5px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; }
#view-data_modeling_ai .dm-sec-add:hover { color:#9DC0FF; background:rgba(76,141,255,.12); }
#view-data_modeling_ai .dm-sec-add svg { width:13px; height:13px; }
#view-data_modeling_ai .dm-note { padding:5px 9px 7px; font-size:11.5px; line-height:1.55; color:var(--dm-dim); }

#view-data_modeling_ai .dm-row { display:flex; align-items:center; gap:7px; width:100%; min-height:30px; padding:4px 8px; margin:1px 0; border:0; border-radius:7px; background:transparent; color:#CBD8E9; font-size:12.5px; font-weight:500; text-align:left; cursor:pointer; transition:background .12s, color .12s; }
#view-data_modeling_ai .dm-row:hover { background:#16202F; color:#F2F6FC; }
#view-data_modeling_ai .dm-row.is-active { background:var(--dm-accent-soft); color:#FFFFFF; box-shadow:inset 2px 0 0 var(--dm-accent); }
#view-data_modeling_ai .dm-row-ico { display:inline-flex; align-items:center; justify-content:center; width:16px; color:var(--dm-muted); }
#view-data_modeling_ai .dm-row.is-active .dm-row-ico { color:#8FB8FF; }
#view-data_modeling_ai .dm-row-ico svg { width:14px; height:14px; }
#view-data_modeling_ai .dm-row-label { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-row-meta { flex:0 0 auto; font-size:10.5px; font-weight:600; color:var(--dm-dim); }
#view-data_modeling_ai .dm-row-acts { display:none; align-items:center; gap:1px; flex:0 0 auto; }
#view-data_modeling_ai .dm-row:hover .dm-row-acts, #view-data_modeling_ai .dm-row.is-active .dm-row-acts { display:flex; }
#view-data_modeling_ai .dm-rowact { width:21px; height:21px; padding:0; border:0; border-radius:5px; background:transparent; color:var(--dm-muted); cursor:pointer; display:inline-flex; align-items:center; justify-content:center; }
#view-data_modeling_ai .dm-rowact:hover { background:#223349; color:#FFF; }
#view-data_modeling_ai .dm-rowact svg { width:13px; height:13px; }
#view-data_modeling_ai .dm-caret { display:inline-flex; align-items:center; justify-content:center; width:13px; height:13px; flex:0 0 auto; color:var(--dm-dim); transition:transform .15s; }
#view-data_modeling_ai .dm-caret.is-open { transform:rotate(90deg); }
#view-data_modeling_ai .dm-caret svg { width:11px; height:11px; stroke-width:2.2; }
#view-data_modeling_ai .dm-proj-kids { margin:1px 0 4px 14px; padding-left:8px; border-left:1px solid var(--dm-line); }
#view-data_modeling_ai .dm-newchat-row { color:var(--dm-muted); font-size:12px; }
#view-data_modeling_ai .dm-newchat-row:hover { color:#9DC0FF; }
#view-data_modeling_ai .dm-panel-foot { flex:0 0 auto; padding:10px 10px 12px; border-top:1px solid var(--dm-line); }
#view-data_modeling_ai .dm-newchat-btn { display:flex; align-items:center; justify-content:center; gap:7px; width:100%; padding:7px 10px; border-radius:7px; border:1px dashed var(--dm-line-2); background:rgba(76,141,255,.05); color:#9DC0FF; font-size:12px; font-weight:600; cursor:pointer; }
#view-data_modeling_ai .dm-newchat-btn:hover { border-color:var(--dm-accent); background:rgba(76,141,255,.12); color:#CFE0FF; }
#view-data_modeling_ai .dm-newchat-btn svg { width:14px; height:14px; }

/* ------------------------------------------------------- panel 2: tree */
#view-data_modeling_ai .dm-search { padding:8px 8px 6px; flex:0 0 auto; position:relative; }
#view-data_modeling_ai .dm-search input { width:100%; height:30px; padding:0 28px 0 9px; border-radius:7px; border:1px solid var(--dm-line-2); background:#0A1220; color:var(--dm-text); font-size:12px; outline:none; }
#view-data_modeling_ai .dm-search input::placeholder { color:#5E6F89; }
#view-data_modeling_ai .dm-search input:focus { border-color:var(--dm-accent); box-shadow:0 0 0 3px rgba(76,141,255,.12); }
#view-data_modeling_ai .dm-search-clear { position:absolute; right:14px; top:50%; transform:translateY(-50%); width:19px; height:19px; padding:0; border:0; border-radius:5px; background:transparent; color:var(--dm-dim); cursor:pointer; display:none; align-items:center; justify-content:center; }
#view-data_modeling_ai .dm-search-clear.show { display:inline-flex; }
#view-data_modeling_ai .dm-search-clear:hover { color:#F2F6FC; background:#223349; }
#view-data_modeling_ai .dm-search-clear svg { width:12px; height:12px; }
#view-data_modeling_ai .dm-tree { flex:1; min-height:0; overflow:auto; overscroll-behavior:contain; padding:2px 6px 10px; scrollbar-width:thin; scrollbar-color:#2A3A50 transparent; }
#view-data_modeling_ai .dm-group { margin-bottom:6px; }
#view-data_modeling_ai .dm-group-head { display:flex; align-items:center; gap:6px; position:sticky; top:0; z-index:3; padding:5px 6px; border-radius:6px; background:#0D1520; color:#A9BBD4; font-size:10.5px; font-weight:700; letter-spacing:.07em; text-transform:uppercase; cursor:pointer; }
#view-data_modeling_ai .dm-group-head:hover { background:#131E2D; }
#view-data_modeling_ai .dm-group-head .dm-tlabel { text-transform:uppercase; letter-spacing:.07em; font-size:10.5px; font-weight:700; color:#A9BBD4; }
#view-data_modeling_ai .dm-trow { display:flex; align-items:center; gap:6px; width:100%; min-height:27px; padding:3px 6px; border:0; border-radius:6px; background:transparent; color:#C6D4E6; font-size:12px; text-align:left; cursor:pointer; transition:background .12s, color .12s; }
#view-data_modeling_ai .dm-trow:hover { background:#16202F; color:#F2F6FC; }
#view-data_modeling_ai .dm-trow.is-active { background:var(--dm-accent-soft); color:#FFF; }
#view-data_modeling_ai .dm-trow.is-db { font-weight:600; color:#DCE7F5; }
#view-data_modeling_ai .dm-trow.is-schema { font-size:11.5px; font-weight:600; color:#AFC1D8; }
#view-data_modeling_ai .dm-trow.is-table { font-size:12px; color:#BCCDE2; }
#view-data_modeling_ai .dm-trow.is-col { font-size:11px; color:#8FA2BC; min-height:23px; cursor:default; }
#view-data_modeling_ai .dm-trow.is-col:hover { background:transparent; color:#8FA2BC; }
#view-data_modeling_ai .dm-tcaret { display:inline-flex; align-items:center; justify-content:center; width:13px; height:13px; flex:0 0 auto; padding:0; border:0; background:transparent; color:var(--dm-dim); cursor:pointer; transition:transform .15s; }
#view-data_modeling_ai .dm-tcaret.is-open { transform:rotate(90deg); }
#view-data_modeling_ai .dm-tcaret.is-empty { visibility:hidden; }
#view-data_modeling_ai .dm-tcaret svg { width:11px; height:11px; stroke-width:2.2; }
#view-data_modeling_ai .dm-tico { display:inline-flex; align-items:center; justify-content:center; width:15px; flex:0 0 auto; color:#7E93AF; }
#view-data_modeling_ai .dm-tico svg { width:13px; height:13px; }
#view-data_modeling_ai .dm-tico.is-db { color:#8FB8FF; }
#view-data_modeling_ai .dm-tico.is-ws { color:#7EE787; }
#view-data_modeling_ai .dm-tlabel { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-tbadge { flex:0 0 auto; font-size:9.5px; font-weight:700; letter-spacing:.02em; color:#7E93AF; background:#121C2B; border:1px solid var(--dm-line); border-radius:999px; padding:1px 6px; }
#view-data_modeling_ai .dm-tbadge.live { color:#7EE787; border-color:rgba(63,185,80,.4); }
#view-data_modeling_ai .dm-tbadge.pk { color:#E3B341; border-color:rgba(227,179,65,.4); }
#view-data_modeling_ai .dm-ttype { flex:0 0 auto; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:9.5px; color:#6B7C97; }
#view-data_modeling_ai .dm-tacts { display:flex; align-items:center; gap:1px; }
#view-data_modeling_ai .dm-tact { width:19px; height:19px; padding:0; border:0; border-radius:4px; background:transparent; color:var(--dm-dim); cursor:pointer; display:none; align-items:center; justify-content:center; }
#view-data_modeling_ai .dm-trow:hover .dm-tact { display:inline-flex; }
#view-data_modeling_ai .dm-tact:hover { background:#223349; color:#9DC0FF; }
#view-data_modeling_ai .dm-tact svg { width:12px; height:12px; }
#view-data_modeling_ai .dm-tree-note { padding:4px 9px 7px; font-size:11px; line-height:1.55; color:var(--dm-dim); }

/* ------------------------------------------------------------------ main */
#view-data_modeling_ai .dm-main { flex:1; min-width:0; display:flex; flex-direction:column; background:radial-gradient(900px 380px at 82% -12%, rgba(76,141,255,.08), transparent 62%), var(--dm-bg); }
#view-data_modeling_ai .dm-chat-head { flex:0 0 auto; display:flex; align-items:center; gap:10px; padding:9px 14px; border-bottom:1px solid var(--dm-line); background:rgba(15,23,36,.72); }
#view-data_modeling_ai .dm-chat-head-main { flex:1; min-width:0; }
#view-data_modeling_ai .dm-chat-title { font-size:13.5px; font-weight:600; color:#F2F6FC; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-chat-sub { margin-top:1px; font-size:11px; color:var(--dm-dim); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-chat-actions { display:flex; align-items:center; gap:2px; flex:0 0 auto; }
#view-data_modeling_ai .dm-messages { flex:1 1 auto; min-height:170px; overflow-x:auto; overflow-y:auto; overscroll-behavior:contain; padding:16px 16px 10px; display:flex; flex-direction:column; gap:13px; scrollbar-width:thin; scrollbar-color:#3B5472 transparent; scrollbar-gutter:stable; }
#view-data_modeling_ai .dm-msg { display:flex; gap:9px; align-items:flex-start; min-width:0; max-width:100%; }
#view-data_modeling_ai .dm-msg.user { flex-direction:row-reverse; }
#view-data_modeling_ai .dm-avatar { flex:0 0 auto; width:28px; height:28px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; letter-spacing:.03em; background:#1B2739; color:#AFC1D8; border:1px solid var(--dm-line-2); }
#view-data_modeling_ai .dm-msg.ai .dm-avatar { background:linear-gradient(135deg,#2F81F7,#1F6FEB); color:#FFF; border-color:transparent; }
#view-data_modeling_ai .dm-bubble { max-width:min(780px,88%); min-width:0; background:var(--dm-panel); border:1px solid var(--dm-line); border-radius:11px; padding:10px 12px; }
#view-data_modeling_ai .dm-msg.user .dm-bubble { background:rgba(47,129,247,.14); border-color:rgba(76,141,255,.35); }
#view-data_modeling_ai .dm-text { font-size:13px; line-height:1.62; color:#DFE9F6; white-space:pre-wrap; word-break:break-word; }
#view-data_modeling_ai .dm-msg.user .dm-text { color:#EAF2FF; }
#view-data_modeling_ai .dm-sql { margin-top:8px; border:1px solid var(--dm-line); border-radius:7px; background:#070D16; overflow:hidden; }
#view-data_modeling_ai .dm-sql summary { cursor:pointer; padding:5px 9px; font-size:10.5px; font-weight:700; letter-spacing:.03em; color:#8FB8FF; text-transform:uppercase; }
#view-data_modeling_ai .dm-sql pre { margin:0; padding:8px 10px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:11.5px; line-height:1.55; color:#A8CBFF; overflow-x:auto; white-space:pre; border-top:1px solid var(--dm-line); }
#view-data_modeling_ai .dm-msg-foot { display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-top:8px; }
#view-data_modeling_ai .dm-tag { font-size:10px; font-weight:600; color:#9DB1CB; background:#121C2B; border:1px solid var(--dm-line); border-radius:999px; padding:2px 7px; }
#view-data_modeling_ai .dm-tag.ok { color:#7EE787; border-color:rgba(63,185,80,.4); }
#view-data_modeling_ai .dm-tag.err { color:#FF9B93; border-color:rgba(248,81,73,.4); }
#view-data_modeling_ai .dm-typing { display:inline-flex; gap:4px; align-items:center; padding:5px 2px; }
#view-data_modeling_ai .dm-typing i { width:6px; height:6px; border-radius:50%; background:#4C8DFF; animation:dmdot 1s infinite ease-in-out; }
#view-data_modeling_ai .dm-typing i:nth-child(2) { animation-delay:.15s; }
#view-data_modeling_ai .dm-typing i:nth-child(3) { animation-delay:.3s; }
@keyframes dmdot { 0%,80%,100% { opacity:.25; transform:translateY(0); } 40% { opacity:1; transform:translateY(-3px); } }
#view-data_modeling_ai .dm-empty { margin:auto; max-width:600px; text-align:center; padding:18px 10px 26px; }
#view-data_modeling_ai .dm-empty-ico { width:52px; height:52px; margin:0 auto 12px; border-radius:14px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,rgba(76,141,255,.18),rgba(63,185,80,.12)); border:1px solid var(--dm-line-2); color:#9DC0FF; }
#view-data_modeling_ai .dm-empty-ico svg { width:24px; height:24px; }
#view-data_modeling_ai .dm-empty h3 { margin:0 0 6px; font-size:16px; font-weight:600; color:#F2F6FC; }
#view-data_modeling_ai .dm-empty p { margin:0 0 14px; font-size:12.5px; line-height:1.6; color:var(--dm-muted); }
#view-data_modeling_ai .dm-suggest { display:flex; flex-wrap:wrap; gap:6px; justify-content:center; }
#view-data_modeling_ai .dm-suggest button { border:1px solid var(--dm-line-2); background:#121C2B; color:#C6D4E6; font-size:12px; padding:6px 11px; border-radius:999px; cursor:pointer; transition:border-color .14s, color .14s, background .14s; }
#view-data_modeling_ai .dm-suggest button:hover { border-color:var(--dm-accent); color:#CFE0FF; background:rgba(76,141,255,.1); }

/* ------------------------------------------------------------- data dock */
#view-data_modeling_ai .dm-data { position:relative; flex:0 1 auto; height:250px; min-height:120px; display:flex; flex-direction:column; border-top:1px solid var(--dm-line); background:var(--dm-panel); }
#view-data_modeling_ai .dm-app.data-collapsed .dm-data { height:38px !important; min-height:38px !important; }
#view-data_modeling_ai .dm-app.data-collapsed .dm-data-body,
#view-data_modeling_ai .dm-app.data-collapsed .dm-grip-h { display:none; }
#view-data_modeling_ai .dm-data-head { flex:0 0 auto; display:flex; align-items:center; gap:8px; padding:6px 10px; border-bottom:1px solid var(--dm-line); min-height:37px; }
#view-data_modeling_ai .dm-data-title { font-size:12.5px; font-weight:600; color:#F2F6FC; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:280px; }
#view-data_modeling_ai .dm-data-meta { flex:1; min-width:0; font-size:11px; color:var(--dm-dim); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
#view-data_modeling_ai .dm-data-actions { display:flex; align-items:center; gap:5px; flex:0 0 auto; }
#view-data_modeling_ai .dm-data-toggle svg { transition:transform .15s; }
#view-data_modeling_ai .dm-app.data-collapsed .dm-data-toggle svg { transform:rotate(180deg); }
#view-data_modeling_ai .dm-data-body { flex:1; min-height:0; overflow:auto; overscroll-behavior:contain; padding:10px 12px 14px; scrollbar-width:thin; scrollbar-color:#3B5472 transparent; scrollbar-gutter:stable both-edges; }
#view-data_modeling_ai .dm-data-empty { display:flex; align-items:center; justify-content:center; height:100%; min-height:110px; padding:16px 20px; text-align:center; font-size:12px; line-height:1.6; color:var(--dm-dim); }
#view-data_modeling_ai .dm-stat-row { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
#view-data_modeling_ai .dm-stat { font-size:10.5px; font-weight:600; color:#C6D4E6; background:#121C2B; border:1px solid var(--dm-line); border-radius:999px; padding:3px 9px; }
#view-data_modeling_ai .dm-sec-title { font-size:10px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--dm-dim); margin:12px 0 6px; }
#view-data_modeling_ai .dm-note-line { font-size:11.5px; color:var(--dm-muted); margin-bottom:8px; line-height:1.55; }
#view-data_modeling_ai .dm-data-body pre { margin:0; background:#070D16; border:1px solid var(--dm-line); border-radius:7px; padding:8px 10px; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:11px; line-height:1.55; color:#A8CBFF; overflow:auto; white-space:pre-wrap; }
#view-data_modeling_ai .dm-table-wrap { overflow:auto; border:1px solid var(--dm-line); border-radius:8px; max-width:100%; scrollbar-width:thin; scrollbar-color:#3B5472 transparent; scrollbar-gutter:stable; }
#view-data_modeling_ai table.dm-dtable { border-collapse:collapse; width:max-content; min-width:100%; font-size:11.5px; }
#view-data_modeling_ai table.dm-dtable th { position:sticky; top:0; z-index:1; background:#16202F; color:#9DC0FF; text-align:left; font-weight:600; padding:6px 10px; border-bottom:1px solid var(--dm-line-2); white-space:nowrap; }
#view-data_modeling_ai table.dm-dtable td { padding:5px 10px; border-bottom:1px solid #16202F; color:#D6E2F2; white-space:nowrap; }
#view-data_modeling_ai table.dm-dtable tr:last-child td { border-bottom:0; }
#view-data_modeling_ai table.dm-dtable tbody tr:hover td { background:rgba(76,141,255,.06); }
#view-data_modeling_ai .dm-muted { color:var(--dm-dim); font-size:12px; padding:8px 2px; }

/* ---------------------------------------------------------------- composer */
#view-data_modeling_ai .dm-composer { flex:0 0 auto; padding:10px 16px 8px; border-top:1px solid var(--dm-line); background:#0B1119; }
#view-data_modeling_ai .dm-compose-row { display:flex; align-items:flex-end; gap:8px; background:#101A28; border:1px solid var(--dm-line-2); border-radius:11px; padding:7px 8px 7px 11px; transition:border-color .14s, box-shadow .14s; }
#view-data_modeling_ai .dm-compose-row:focus-within { border-color:var(--dm-accent); box-shadow:0 0 0 3px rgba(76,141,255,.12); }
#view-data_modeling_ai .dm-compose-row textarea { flex:1; min-height:24px; max-height:150px; resize:none; background:transparent; border:0; outline:0; color:#F2F6FC; font-size:13px; line-height:1.55; padding:3px 0; }
#view-data_modeling_ai .dm-compose-row textarea::placeholder { color:#5E6F89; }
#view-data_modeling_ai .dm-send { flex:0 0 auto; width:32px; height:32px; border-radius:8px; border:0; background:linear-gradient(135deg,#2F81F7,#1F6FEB); color:#FFF; cursor:pointer; display:flex; align-items:center; justify-content:center; }
#view-data_modeling_ai .dm-send:hover { background:linear-gradient(135deg,#4C8DFF,#2F81F7); }
#view-data_modeling_ai .dm-send:disabled { opacity:.5; cursor:not-allowed; }
#view-data_modeling_ai .dm-send svg { width:16px; height:16px; }
#view-data_modeling_ai .dm-attach-btn { flex:0 0 auto; width:32px; height:32px; border-radius:8px; border:1px solid transparent; background:transparent; color:#8FA8C8; cursor:pointer; display:flex; align-items:center; justify-content:center; }
#view-data_modeling_ai .dm-attach-btn:hover { background:#16233A; color:#C7DBF7; }
#view-data_modeling_ai .dm-attach-btn.busy { opacity:.55; cursor:progress; }
#view-data_modeling_ai .dm-attach-btn svg { width:17px; height:17px; }
#view-data_modeling_ai .dm-attach-strip { display:flex; flex-wrap:wrap; gap:6px; padding:0 2px 7px; }
#view-data_modeling_ai .dm-attach-strip:empty { display:none; }
#view-data_modeling_ai .dm-ctx { display:flex; align-items:center; gap:7px; margin:0 2px 7px; padding:5px 8px; background:#0C1A2C; border:1px solid #234463; border-left:3px solid var(--dm-accent); border-radius:8px; font-size:11.5px; color:#CFE0F5; }
#view-data_modeling_ai .dm-ctx[hidden] { display:none; }
#view-data_modeling_ai .dm-ctx-label { flex:0 0 auto; font-size:9.5px; font-weight:800; letter-spacing:.07em; text-transform:uppercase; color:#7FB0FF; }
#view-data_modeling_ai .dm-ctx-path { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-family:ui-monospace,Consolas,monospace; }
#view-data_modeling_ai .dm-ctx-path b { color:#FFF; font-weight:600; }
#view-data_modeling_ai .dm-ctx-level { flex:0 0 auto; font-size:9.5px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:#8FA8C8; background:#16233A; border-radius:4px; padding:1px 5px; }
#view-data_modeling_ai .dm-ctx-x { flex:0 0 auto; border:0; background:transparent; color:#8FA8C8; cursor:pointer; font-size:14px; line-height:1; padding:1px 4px; border-radius:4px; }
#view-data_modeling_ai .dm-ctx-x:hover { background:#22314A; color:#FFF; }
#view-data_modeling_ai .dm-attach-chip { display:inline-flex; align-items:center; gap:7px; max-width:280px; background:#101A28; border:1px solid var(--dm-line-2); border-radius:8px; padding:4px 6px 4px 5px; font-size:11px; color:#CFE0F5; }
#view-data_modeling_ai .dm-attach-thumb { width:26px; height:26px; border-radius:5px; object-fit:cover; background:#0B1119; flex:0 0 auto; }
#view-data_modeling_ai .dm-attach-kind { flex:0 0 auto; width:26px; height:26px; border-radius:5px; display:flex; align-items:center; justify-content:center; background:#16233A; color:#7FB0FF; font-size:9px; font-weight:800; letter-spacing:.04em; }
#view-data_modeling_ai .dm-attach-name { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-attach-meta { color:#6F86A6; font-size:10px; white-space:nowrap; }
#view-data_modeling_ai .dm-attach-x { flex:0 0 auto; border:0; background:transparent; color:#8FA8C8; cursor:pointer; font-size:13px; line-height:1; padding:2px 3px; border-radius:4px; }
#view-data_modeling_ai .dm-attach-x:hover { background:#22314A; color:#FFF; }
#view-data_modeling_ai .dm-attach-spin { width:11px; height:11px; border:2px solid #2F81F7; border-top-color:transparent; border-radius:50%; animation:dmspin .7s linear infinite; }
@keyframes dmspin { to { transform:rotate(360deg); } }
#view-data_modeling_ai .dm-msg-atts { display:flex; flex-wrap:wrap; gap:5px; margin-top:7px; }
#view-data_modeling_ai .dm-msg-att { display:inline-flex; align-items:center; gap:5px; background:#0B1524; border:1px solid var(--dm-line-2); border-radius:6px; padding:2px 7px; font-size:10.5px; color:#A8CBFF; max-width:240px; }
#view-data_modeling_ai .dm-msg-att span { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#view-data_modeling_ai .dm-hint { text-align:center; font-size:10px; color:#5E6F89; padding:4px 0 6px; }

/* ------------------------------------------------------------------ grips */
#view-data_modeling_ai .dm-grip-v { position:absolute; top:0; right:-3px; bottom:0; width:6px; cursor:col-resize; z-index:14; }
#view-data_modeling_ai .dm-grip-v:hover, #view-data_modeling_ai .dm-grip-v.dragging { background:linear-gradient(180deg,transparent,rgba(76,141,255,.55),transparent); }
#view-data_modeling_ai .dm-grip-h { position:absolute; top:-3px; left:0; right:0; height:6px; cursor:row-resize; z-index:14; }
#view-data_modeling_ai .dm-grip-h:hover, #view-data_modeling_ai .dm-grip-h.dragging { background:linear-gradient(90deg,transparent,rgba(76,141,255,.55),transparent); }

/* --------------------------------------------------------------- modals */
#view-data_modeling_ai .dm-modal { position:absolute; inset:0; z-index:70; background:rgba(3,7,14,.72); display:none; align-items:center; justify-content:center; padding:16px; }
#view-data_modeling_ai .dm-modal.open { display:flex; }
#view-data_modeling_ai .dm-modal-card { width:min(468px,100%); background:var(--dm-panel); border:1px solid var(--dm-line-2); border-radius:12px; box-shadow:0 24px 60px rgba(0,0,0,.55); overflow:hidden; }
#view-data_modeling_ai .dm-modal-head { display:flex; align-items:flex-start; justify-content:space-between; gap:10px; padding:13px 14px; border-bottom:1px solid var(--dm-line); }
#view-data_modeling_ai .dm-modal-title { font-size:14px; font-weight:600; color:#F2F6FC; }
#view-data_modeling_ai .dm-modal-sub { margin-top:2px; font-size:11.5px; color:var(--dm-dim); line-height:1.5; }
#view-data_modeling_ai .dm-modal-body { padding:14px; display:flex; flex-direction:column; gap:10px; }
#view-data_modeling_ai .dm-field label { display:block; font-size:10.5px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--dm-muted); margin-bottom:5px; }
#view-data_modeling_ai .dm-field input, #view-data_modeling_ai .dm-field select { width:100%; height:34px; padding:0 10px; background:#0A1220; border:1px solid var(--dm-line-2); border-radius:7px; color:#F2F6FC; font-size:12.5px; outline:none; }
#view-data_modeling_ai .dm-field input:focus, #view-data_modeling_ai .dm-field select:focus { border-color:var(--dm-accent); box-shadow:0 0 0 3px rgba(76,141,255,.12); }
#view-data_modeling_ai .dm-field input[type=file] { height:auto; padding:7px 8px; font-size:11.5px; color:var(--dm-muted); }
#view-data_modeling_ai .dm-field-note { font-size:11px; color:var(--dm-dim); line-height:1.55; }
#view-data_modeling_ai .dm-modal-foot { display:flex; justify-content:flex-end; gap:8px; padding:0 14px 14px; }

/* ------------------------------------------------------------------ menu */
#view-data_modeling_ai .dm-menu { position:fixed; z-index:95; min-width:212px; padding:5px; background:#121C2B; border:1px solid var(--dm-line-2); border-radius:9px; box-shadow:0 18px 44px rgba(0,0,0,.55); }
#view-data_modeling_ai .dm-menu[hidden] { display:none; }
#view-data_modeling_ai .dm-menu-item { display:flex; align-items:center; gap:8px; width:100%; padding:6px 8px; border:0; border-radius:6px; background:transparent; color:#D6E2F2; font-size:12.5px; text-align:left; cursor:pointer; white-space:nowrap; }
#view-data_modeling_ai .dm-menu-item:hover { background:#1C293B; color:#FFF; }
#view-data_modeling_ai .dm-menu-item.danger { color:#FF9B93; }
#view-data_modeling_ai .dm-menu-item.danger:hover { background:rgba(248,81,73,.14); color:#FFC1BC; }
#view-data_modeling_ai .dm-menu-item:disabled { opacity:.45; cursor:not-allowed; }
#view-data_modeling_ai .dm-menu-item svg { width:14px; height:14px; }
#view-data_modeling_ai .dm-menu-sep { height:1px; margin:4px 6px; background:var(--dm-line); }

/* ----------------------------------------------------------------- toast */
#view-data_modeling_ai .dm-toast { position:absolute; right:16px; bottom:74px; z-index:90; max-width:380px; padding:9px 12px; border-radius:9px; font-size:12px; font-weight:500; line-height:1.5; background:#121C2B; border:1px solid var(--dm-line-2); color:#E6EDF7; box-shadow:0 14px 34px rgba(0,0,0,.5); opacity:0; transform:translateY(8px); pointer-events:none; transition:opacity .18s, transform .18s; }
#view-data_modeling_ai .dm-toast.show { opacity:1; transform:translateY(0); }
#view-data_modeling_ai .dm-toast.ok { border-color:rgba(63,185,80,.5); color:#9BE9A8; }
#view-data_modeling_ai .dm-toast.err { border-color:rgba(248,81,73,.5); color:#FFB3AD; }

/* ---------------------------------------------------------------- mobile */
@media (max-width:1180px) {
  #view-data_modeling_ai { height:100vh !important; }
  #view-data_modeling_ai .dm-app { height:100% !important; min-height:0 !important; border-radius:0 !important; }
  #view-data_modeling_ai .dm-chats, #view-data_modeling_ai .dm-explorer { position:absolute; top:0; bottom:0; z-index:40; box-shadow:16px 0 44px rgba(0,0,0,.55); }
  #view-data_modeling_ai .dm-chats { left:0; }
  #view-data_modeling_ai .dm-explorer { left:0; }
  #view-data_modeling_ai .dm-brand-text p { display:none; }
  #view-data_modeling_ai .dm-ai-badge { display:none; }
  #view-data_modeling_ai .dm-btn span { display:none; }
  #view-data_modeling_ai .dm-btn { padding:6px 8px; }
  #view-data_modeling_ai .dm-messages { padding:12px 10px 8px; }
  #view-data_modeling_ai .dm-bubble { max-width:94%; }
  #view-data_modeling_ai .dm-data { height:210px; }
  #view-data_modeling_ai .dm-messages { min-height:130px; }
  #view-data_modeling_ai .dm-data-title { max-width:150px; }
  #view-data_modeling_ai .dm-topbar { padding:8px; }
}
@media (max-height:620px) {
  #view-data_modeling_ai .dm-messages { min-height:120px; }
  #view-data_modeling_ai .dm-data { min-height:180px; }
}
</style>

<div class="dm-app" id="dmShell">

  <div class="dm-topbar">
    <div class="dm-top-left">
      <button class="dm-iconbtn" id="dmChatsToggle" onclick="dmToggleChats()" title="Show or hide Chats &amp; Projects">
        <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8z"/></svg>
      </button>
      <button class="dm-iconbtn" id="dmExplorerToggle" onclick="dmToggleExplorer()" title="Show or hide Explorer">
        <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/></svg>
      </button>
    </div>
    <div class="dm-brand">
      <div class="dm-logo">
        <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2v20"/><path d="M4.9 6.5l14.2 11"/><path d="M19.1 6.5L4.9 17.5"/><path d="M9 3.6l3 3 3-3"/><path d="M9 20.4l3-3 3 3"/></svg>
      </div>
      <div class="dm-brand-text">
        <h2>DATA MODELING BY AI</h2>
        <p>Talk to every NanoPro database &mdash; no SQL, just results</p>
      </div>
    </div>
    <div class="dm-top-actions">
      <span class="dm-ai-badge live" id="dmAiBadge">AI ready &middot; gemini-3.5-flash-lite</span>
      <button class="dm-btn" onclick="dmUploadOpen()" title="Upload CSV or Excel into the active chat">
        <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/></svg>
        <span>Upload</span>
      </button>
      <button class="dm-btn" id="dmSfBtn" onclick="dmSetupSnowflake()" title="Create the Snowflake warehouse structure">
        <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2v20"/><path d="M4.9 6.5l14.2 11"/><path d="M19.1 6.5L4.9 17.5"/></svg>
        <span>Snowflake</span>
      </button>
    </div>
  </div>

  <div class="dm-body">

    <aside class="dm-chats" id="dmChatsPanel">
      <div class="dm-panel-head">
        <span class="dm-panel-title">Chats &amp; Projects</span>
        <div class="dm-panel-tools">
          <button class="dm-iconbtn" onclick="dmNewChat('')" title="New chat">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
          </button>
          <button class="dm-iconbtn" onclick="dmNewProject()" title="New project">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/><path d="M12 11v6"/><path d="M9 14h6"/></svg>
          </button>
          <button class="dm-iconbtn" onclick="dmToggleChats()" title="Hide panel">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
          </button>
        </div>
      </div>

      <div class="dm-panel-scroll" id="dmChatsScroll">
        <div class="dm-sec" id="dmPinnedSec" hidden>
          <div class="dm-sec-head"><span>Pinned</span></div>
          <div id="dmPinnedList"></div>
        </div>
        <div class="dm-sec">
          <div class="dm-sec-head">
            <span>Chats &amp; Tasks</span>
            <span class="dm-sec-count" id="dmChatCount">0</span>
          </div>
          <div id="dmChatList"></div>
        </div>
        <div class="dm-sec">
          <div class="dm-sec-head">
            <span>Projects</span>
            <button class="dm-sec-add" onclick="dmNewProject()" title="New project">
              <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
            </button>
          </div>
          <div id="dmProjectList"></div>
        </div>
      </div>

      <div class="dm-panel-foot">
        <button class="dm-newchat-btn" onclick="dmNewChat('')">
          <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
          New chat
        </button>
      </div>
      <div class="dm-grip-v" id="dmChatsGrip" title="Drag to resize"></div>
    </aside>

    <aside class="dm-explorer" id="dmExplorer">
      <div class="dm-panel-head">
        <span class="dm-panel-title">Explorer</span>
        <div class="dm-panel-tools">
          <button class="dm-iconbtn" onclick="dmLoadCatalog(true)" title="Rescan every database">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.5 9a9 9 0 0 1 14.9-3.4L23 10"/><path d="M1 14l4.6 4.4A9 9 0 0 0 20.5 15"/></svg>
          </button>
          <button class="dm-iconbtn" onclick="dmToggleExplorer()" title="Hide panel">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
          </button>
        </div>
      </div>
      <div class="dm-search">
        <input id="dmCatalogFilter" type="text" placeholder="Search databases, schemas, tables, columns" autocomplete="off" spellcheck="false">
        <button class="dm-search-clear" id="dmClearFilter" onclick="dmClearFilter()" title="Clear search">
          <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="dm-tree" id="dmDatabaseTree">
        <div class="dm-tree-note">Scanning your databases in the background&hellip;</div>
      </div>
      <div class="dm-panel-foot" style="display:flex;gap:6px;">
        <button class="dm-btn" style="flex:1;justify-content:center;" onclick="dmUploadOpen()">Upload</button>
        <button class="dm-btn" style="flex:1;justify-content:center;" onclick="dmNewSchema()">Schema</button>
      </div>
      <div class="dm-grip-v" id="dmExplorerGrip" title="Drag to resize"></div>
    </aside>

    <main class="dm-main">
      <div class="dm-chat-head">
        <div class="dm-chat-head-main">
          <div class="dm-chat-title" id="dmActiveName">No chat selected</div>
          <div class="dm-chat-sub" id="dmActiveId">Create a chat to start talking to your data</div>
        </div>
        <div class="dm-chat-actions">
          <button class="dm-iconbtn" id="dmPinBtn" onclick="dmTogglePinActive()" title="Pin this chat">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 17v5"/><path d="M5 17h14v-1.8a2 2 0 0 0-1.1-1.8l-1.8-.9A2 2 0 0 1 15 10.8V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.8a2 2 0 0 1-1.1 1.8l-1.8.9A2 2 0 0 0 5 15.2z"/></svg>
          </button>
          <button class="dm-iconbtn" onclick="dmRenameActive()" title="Rename this chat">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>
          </button>
        </div>
      </div>

      <div class="dm-messages" id="dmMessages"></div>

      <div class="dm-composer">
        <div class="dm-attach-strip" id="dmAttachStrip"></div>
        <div class="dm-ctx" id="dmCtxBar" hidden>
          <span class="dm-ctx-label">Using</span>
          <span class="dm-ctx-level" id="dmCtxLevel">DB</span>
          <span class="dm-ctx-path" id="dmCtxPath"></span>
          <button type="button" class="dm-ctx-x" onclick="dmClearSelection()" title="Clear the selected database, schema or table">&times;</button>
        </div>
        <div class="dm-compose-row">
          <button class="dm-attach-btn" id="dmAttachBtn" type="button" onclick="dmPickAttachment()" title="Attach a CSV, Excel, JSON file or an image">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M21.4 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
          </button>
          <textarea id="dmInput" rows="1" placeholder="Ask anything or attach a file &mdash; &quot;create a new table from this Excel&quot; / &quot;append this data to this table&quot;&hellip;"></textarea>
          <button class="dm-send" id="dmSend" onclick="dmSendMessage()" title="Send (Enter)">
            <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5"/><path d="M5 12l7-7 7 7"/></svg>
          </button>
        </div>
        <input type="file" id="dmAttachInput" multiple hidden accept=".csv,.tsv,.xlsx,.xlsm,.json,.png,.jpg,.jpeg,.webp,.gif,.bmp" onchange="dmAttachmentChosen(this)">
        <div class="dm-hint">Enter to send &middot; Shift+Enter for a new line &middot; attach CSV / Excel / JSON or an image; say &quot;new table&quot; or &quot;append to this table&quot;</div>
      </div>

      <section class="dm-data" id="dmDataPanel">
        <div class="dm-data-head">
          <span class="dm-data-title" id="dmDataTitle">Data</span>
          <span class="dm-data-meta" id="dmDataMeta">Table previews and query results appear here</span>
          <div class="dm-data-actions">
            <button class="dm-linkbtn" id="dmAskTableBtn" onclick="dmAskAboutTable()" hidden>
              <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/></svg>
              Ask AI
            </button>
            <span class="dm-export" id="dmExportWrap" hidden>
              <select class="dm-export-select" id="dmExportFormat" onchange="dmApplyExportFormat()" title="Download format">
                <option value="csv">CSV</option>
                <option value="xlsx">Excel (.xlsx)</option>
                <option value="pipe">Text (pipe |)</option>
                <option value="tab">Text (tab)</option>
              </select>
              <a class="dm-linkbtn" id="dmResultDownload" href="#" title="Download this data">
                <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></svg>
                Download
              </a>
            </span>
            <button class="dm-linkbtn" onclick="dmClearData()" title="Clear the data dock">Clear</button>
            <button class="dm-iconbtn dm-data-toggle" id="dmDataToggle" onclick="dmToggleData()" title="Collapse or expand data">
              <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>
            </button>
          </div>
        </div>
        <div class="dm-data-body" id="dmDataBody">
          <div class="dm-data-empty">Select a table in the Explorer or ask a question &mdash; tables and query results open here, below the chat box.</div>
        </div>
        <div class="dm-grip-h" id="dmDataGrip" title="Drag to resize"></div>
      </section>
    </main>
  </div>

  <div class="dm-modal" id="dmNameModal">
    <div class="dm-modal-card">
      <div class="dm-modal-head">
        <div>
          <div class="dm-modal-title" id="dmNameTitle">Name</div>
          <div class="dm-modal-sub" id="dmNameNote"></div>
        </div>
        <button class="dm-iconbtn" onclick="dmNameClose()" title="Close">
          <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="dm-modal-body">
        <div class="dm-field">
          <label id="dmNameLabel" for="dmNameInput">Name</label>
          <input id="dmNameInput" type="text" maxlength="64" autocomplete="off">
        </div>
      </div>
      <div class="dm-modal-foot">
        <button class="dm-btn" onclick="dmNameClose()">Cancel</button>
        <button class="dm-btn primary" onclick="dmNameSubmit()">Save</button>
      </div>
    </div>
  </div>

  <div class="dm-modal" id="dmUploadModal">
    <div class="dm-modal-card">
      <div class="dm-modal-head">
        <div>
          <div class="dm-modal-title">Upload CSV / Excel into a table</div>
          <div class="dm-modal-sub">Stored inside the active chat &mdash; safe and reversible</div>
        </div>
        <button class="dm-iconbtn" onclick="dmUploadClose()" title="Close">
          <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="dm-modal-body">
        <div class="dm-field">
          <label for="dmUpFile">File (CSV, XLSX, XLSM &mdash; max 25 MB, 50,000 rows)</label>
          <input type="file" id="dmUpFile" accept=".csv,.xlsx,.xlsm,text/csv">
        </div>
        <div class="dm-field">
          <label for="dmUpTable">Table name (leave blank to use the file name)</label>
          <input type="text" id="dmUpTable" placeholder="e.g. sales_orders" autocomplete="off">
        </div>
        <div class="dm-field">
          <label for="dmUpSchema">Schema</label>
          <select id="dmUpSchema"><option value="main">main</option></select>
        </div>
        <div class="dm-field">
          <label for="dmUpMode">Mode</label>
          <select id="dmUpMode">
            <option value="create">Create a new table</option>
            <option value="append">Append to an existing table</option>
          </select>
          <div class="dm-field-note">Column types are detected automatically. Appending adds missing columns when needed.</div>
        </div>
      </div>
      <div class="dm-modal-foot">
        <button class="dm-btn" onclick="dmUploadClose()">Cancel</button>
        <button class="dm-btn primary" id="dmUpSubmit" onclick="dmSubmitUpload()">Import data</button>
      </div>
    </div>
  </div>

  <div class="dm-modal" id="dmSchemaModal">
    <div class="dm-modal-card">
      <div class="dm-modal-head">
        <div>
          <div class="dm-modal-title">New schema</div>
          <div class="dm-modal-sub">Schemas live inside the active chat as separate database files</div>
        </div>
        <button class="dm-iconbtn" onclick="dmCloseSchema()" title="Close">
          <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="dm-modal-body">
        <div class="dm-field">
          <label for="dmSchemaName">Schema name</label>
          <input type="text" id="dmSchemaName" placeholder="e.g. marketing" autocomplete="off">
        </div>
      </div>
      <div class="dm-modal-foot">
        <button class="dm-btn" onclick="dmCloseSchema()">Cancel</button>
        <button class="dm-btn primary" onclick="dmSubmitSchema()">Create schema</button>
      </div>
    </div>
  </div>

  <div class="dm-modal" id="dmSfModal">
    <div class="dm-modal-card">
      <div class="dm-modal-head">
        <div>
          <div class="dm-modal-title">Connect Snowflake</div>
          <div class="dm-modal-sub">Account XMUTKDJ-KP74023 &middot; MANGESHBAGUL15@GMAIL.COM &middot; ACCOUNTADMIN</div>
        </div>
        <button class="dm-iconbtn" onclick="dmCloseSfModal()" title="Close">
          <svg class="dm-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="dm-modal-body">
        <div class="dm-field">
          <label for="dmSfPassword">Snowflake password</label>
          <input type="password" id="dmSfPassword" placeholder="Password for MANGESHBAGUL15@GMAIL.COM" autocomplete="new-password">
          <div class="dm-field-note">Stored only in NanoPro's encrypted Credential Vault. Used to create BANK_DB, the SALES and L0_STAGING schemas, empty SALES_ORDERS and PIPELINE tables plus the revenue view. No sample rows are inserted.</div>
        </div>
      </div>
      <div class="dm-modal-foot">
        <button class="dm-btn" onclick="dmCloseSfModal()">Cancel</button>
        <button class="dm-btn primary" id="dmSfSave" onclick="dmSubmitSfPassword()">Save &amp; set up</button>
      </div>
    </div>
  </div>

  <div class="dm-menu" id="dmMenu" hidden></div>
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

    function dmGetSessionToken() {
        if (typeof currentSessionToken !== 'undefined' && currentSessionToken) return currentSessionToken;
        try {
            var m = document.cookie.match(/(?:^|;\s*)nanopro_session=([^;]+)/);
            if (m && m[1]) return decodeURIComponent(m[1]);
        } catch (e) {}
        try {
            var t = localStorage.getItem('nanopro_session_token');
            if (t) return t;
        } catch (e) {}
        return '';
    }

    function dmCurrentUsername() {
        var u = window.currentUser || (typeof currentUser !== 'undefined' ? currentUser : null);
        var uname = (u && u.username) ? u.username : '';
        if (!uname) {
            try { uname = localStorage.getItem('nanopro_active_account') || ''; } catch (e) {}
        }
        var low = (uname || '').toLowerCase().trim();
        if (!low || ['nanopro', 'mangesh', 'mangeshbagul15', 'admin', 'user_admin_001'].indexOf(low) !== -1 ||
            low.indexOf('mangeshbagul15') !== -1 || low.indexOf('8433755448') !== -1) {
            return 'nanopro';
        }
        return low;
    }

    function dmUserKey(baseKey) {
        var user = dmCurrentUsername();
        return baseKey + '_' + user;
    }

    var DM = {
        inited: false,
        bound: false,
        sending: false,
        workspaceId: (function () {
            try {
                var u = '_' + dmCurrentUsername();
                return localStorage.getItem('dm_active_ws' + u) || localStorage.getItem('dm_active_ws_nanopro') || localStorage.getItem('dm_active_ws') || '';
            } catch (e) { return ''; }
        })(),
        projectId: (function () {
            try {
                var u = '_' + dmCurrentUsername();
                return localStorage.getItem('dm_active_prj' + u) || localStorage.getItem('dm_active_prj_nanopro') || localStorage.getItem('dm_active_prj') || '';
            } catch (e) { return ''; }
        })(),
        chatsOpen: localStorage.getItem('dm_chats_hidden') !== '1',
        explorerOpen: localStorage.getItem('dm_explorer_hidden') !== '1',
        dataOpen: false,
        dataHeight: parseInt(localStorage.getItem('dm_data_h') || '0', 10) || 250,
        workspaces: [],
        projects: [],
        catalog: [],
        scanning: false,
        pollTries: 0,
        pollTimer: null,
        treeOpen: (function () {
            try { return JSON.parse(localStorage.getItem('dm_tree_open') || '{}') || {}; }
            catch (err) { return {}; }
        })(),
        projectsOpen: (function () {
            try { return JSON.parse(localStorage.getItem('dm_projects_open') || '{}') || {}; }
            catch (err) { return {}; }
        })(),
        columns: {},
        colLoading: {},
        lastMessages: [],
        attachments: [],
        tableCtx: null,
        selection: null,
        exportTarget: null,
        nameCb: null,
        menuItems: null,
        toastTimer: null
    };
    window.dmState = DM;

    var ICONS = {
        plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
        chat: '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8z"/>',
        folder: '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
        pin: '<path d="M12 17v5"/><path d="M5 17h14v-1.8a2 2 0 0 0-1.1-1.8l-1.8-.9A2 2 0 0 1 15 10.8V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.8a2 2 0 0 1-1.1 1.8l-1.8.9A2 2 0 0 0 5 15.2z"/>',
        more: '<circle cx="5" cy="12" r="1.6" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.6" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1.6" fill="currentColor" stroke="none"/>',
        pencil: '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/>',
        trash: '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/>',
        database: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
        snowflake: '<path d="M12 2v20"/><path d="M4.9 6.5l14.2 11"/><path d="M19.1 6.5L4.9 17.5"/><path d="M9 3.6l3 3 3-3"/><path d="M9 20.4l3-3 3 3"/>',
        table: '<path d="M3 5h18v14H3z"/><path d="M3 10h18"/><path d="M9 10v9"/><path d="M15 10v9"/>',
        grid: '<path d="M4 4h16v16H4z"/><path d="M9.3 4v16"/><path d="M14.7 4v16"/>',
        key: '<path d="M21 2l-2 2"/><path d="M15.5 7.5L19 4l3 3-3.5 3.5"/><path d="M10.5 11.5a5 5 0 1 0 3 3"/><path d="M10.5 11.5l6-6"/>',
        chevron: '<path d="M9 18l6-6-6-6"/>',
        close: '<path d="M18 6L6 18"/><path d="M6 6l12 12"/>',
        sparkle: '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/>'
    };

    function $(id) { return document.getElementById(id); }

    function dmIcon(name, cls) {
        return '<svg class="dm-svg' + (cls ? ' ' + cls : '') + '" viewBox="0 0 24 24" aria-hidden="true">' + (ICONS[name] || ICONS.chat) + '</svg>';
    }

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
        var token = dmGetSessionToken();
        if (token && !headers['Authorization']) {
            headers['Authorization'] = 'Bearer ' + token;
        }
        var timeoutMs = options.timeoutMs || 45000;
        var fetchOptions = Object.assign({}, options, {
            headers: headers,
            credentials: 'same-origin'
        });
        delete fetchOptions.timeoutMs;
        var timer = null;
        if (!fetchOptions.signal && window.AbortController) {
            var controller = new AbortController();
            fetchOptions.signal = controller.signal;
            timer = setTimeout(function () { controller.abort(); }, timeoutMs);
        }
        var res;
        try {
            res = await fetch('/api/data_modeling' + path, fetchOptions);
        } catch (err) {
            if (err && err.name === 'AbortError') {
                var timeoutErr = new Error('The data backend is still working. I will keep checking for the reply.');
                timeoutErr.timeout = true;
                throw timeoutErr;
            }
            throw err;
        } finally {
            if (timer) clearTimeout(timer);
        }
        if (res.status === 401) {
            throw new Error('Session expired. Please log in again.');
        }
        var data = null;
        try { data = await res.json(); } catch (err) { data = null; }
        if (!res.ok || (data && data.status === 'error')) {
            var detail = data && (data.message || data.detail);
            if (detail && typeof detail === 'object') detail = JSON.stringify(detail);
            var apiErr = new Error(detail || ('Request failed (' + res.status + ')'));
            apiErr.status = res.status;
            throw apiErr;
        }
        return data || {};
    }

    function dmSaveJson(key, value) {
        try { localStorage.setItem(key, JSON.stringify(value)); } catch (err) { /* private mode */ }
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
        return '<div class="dm-table-wrap"><table class="dm-dtable"><thead><tr>' + head + '</tr></thead><tbody>' + body + '</tbody></table></div>';
    }

    // ------------------------------------------------------------- layout

    function dmFit() {
        var app = $('dmShell');
        if (!app) return;
        var view = $('view-data_modeling_ai');
        var vp = $('main-content-viewport');
        if (vp) {
            vp.style.padding = '0';
            vp.style.overflow = 'hidden';
        }
        if (view) {
            view.style.height = '100%';
            view.style.maxHeight = '100%';
            view.style.minHeight = '0';
            view.style.padding = '0';
            view.style.margin = '0';
            view.style.overflow = 'hidden';
        }
        app.style.height = '100%';
        app.style.maxHeight = '100%';
        app.style.minHeight = '0';
    }

    window.dmToggleChats = function () {
        DM.chatsOpen = !DM.chatsOpen;
        if (DM.chatsOpen && window.innerWidth <= 1180) DM.explorerOpen = false;
        if (window.innerWidth > 1180) localStorage.setItem('dm_chats_hidden', DM.chatsOpen ? '0' : '1');
        dmApplyPanels();
    };

    window.dmToggleExplorer = function () {
        DM.explorerOpen = !DM.explorerOpen;
        if (DM.explorerOpen && window.innerWidth <= 1180) DM.chatsOpen = false;
        if (window.innerWidth > 1180) localStorage.setItem('dm_explorer_hidden', DM.explorerOpen ? '0' : '1');
        dmApplyPanels();
    };

    function dmApplyPanels() {
        var shell = $('dmShell');
        if (!shell) return;
        shell.classList.toggle('hide-chats', !DM.chatsOpen);
        shell.classList.toggle('hide-explorer', !DM.explorerOpen);
        var c = $('dmChatsToggle');
        var e = $('dmExplorerToggle');
        if (c) c.classList.toggle('is-on', DM.chatsOpen);
        if (e) e.classList.toggle('is-on', DM.explorerOpen);
    }

    window.dmToggleData = function () {
        DM.dataOpen = !DM.dataOpen;
        localStorage.setItem('dm_data_open', DM.dataOpen ? '1' : '0');
        dmApplyData();
    };

    function dmApplyData() {
        var shell = $('dmShell');
        var panel = $('dmDataPanel');
        if (!shell || !panel) return;
        shell.classList.toggle('data-collapsed', !DM.dataOpen);
        panel.style.height = DM.dataHeight + 'px';
        var btn = $('dmDataToggle');
        if (btn) btn.title = DM.dataOpen ? 'Collapse data' : 'Expand data';
    }

    function dmInitGripV(handleId, panelId, storageKey, min, max) {
        var handle = $(handleId);
        var panel = $(panelId);
        if (!handle || !panel) return;
        var saved = parseInt(localStorage.getItem(storageKey) || '0', 10);
        if (saved >= min && saved <= max) panel.style.width = saved + 'px';
        handle.addEventListener('pointerdown', function (ev) {
            ev.preventDefault();
            var startX = ev.clientX;
            var startW = panel.getBoundingClientRect().width;
            handle.classList.add('dragging');
            document.body.style.cursor = 'col-resize';
            function move(e) {
                var w = Math.max(min, Math.min(max, startW + (e.clientX - startX)));
                panel.style.width = Math.round(w) + 'px';
                dmFit();
            }
            function up() {
                handle.classList.remove('dragging');
                document.body.style.cursor = '';
                document.removeEventListener('pointermove', move);
                document.removeEventListener('pointerup', up);
                localStorage.setItem(storageKey, String(Math.round(panel.getBoundingClientRect().width)));
            }
            document.addEventListener('pointermove', move);
            document.addEventListener('pointerup', up);
        });
    }

    function dmInitGripH() {
        var handle = $('dmDataGrip');
        var panel = $('dmDataPanel');
        if (!handle || !panel) return;
        handle.addEventListener('pointerdown', function (ev) {
            ev.preventDefault();
            var startY = ev.clientY;
            var startH = panel.getBoundingClientRect().height;
            handle.classList.add('dragging');
            document.body.style.cursor = 'row-resize';
            function move(e) {
                var h = Math.max(120, Math.min(window.innerHeight * 0.65, startH - (e.clientY - startY)));
                DM.dataHeight = Math.round(h);
                panel.style.height = DM.dataHeight + 'px';
            }
            function up() {
                handle.classList.remove('dragging');
                document.body.style.cursor = '';
                document.removeEventListener('pointermove', move);
                document.removeEventListener('pointerup', up);
                localStorage.setItem('dm_data_h', String(DM.dataHeight));
            }
            document.addEventListener('pointermove', move);
            document.addEventListener('pointerup', up);
        });
    }

    // ---------------------------------------------------- chats & projects

    function dmFindWorkspace(id) {
        for (var i = 0; i < DM.workspaces.length; i++) {
            if (DM.workspaces[i].id === id) return DM.workspaces[i];
        }
        return null;
    }

    function dmFindProject(id) {
        for (var i = 0; i < DM.projects.length; i++) {
            if (DM.projects[i].id === id) return DM.projects[i];
        }
        return null;
    }

    function dmActiveWorkspace() { return dmFindWorkspace(DM.workspaceId); }

    function dmChatRow(ws) {
        var active = ws.id === DM.workspaceId;
        return '<div class="dm-row' + (active ? ' is-active' : '') + '" data-chat="' + dmAttr(ws.id) + '" role="button" tabindex="0" title="' + dmAttr(ws.name || 'Untitled chat') + '">' +
            '<span class="dm-row-ico">' + dmIcon('chat') + '</span>' +
            '<span class="dm-row-label">' + dmEsc(ws.name || 'Untitled chat') + '</span>' +
            ((ws.message_count && ws.project_id) ? '' : '<span class="dm-row-meta">' + (ws.message_count ? ws.message_count : '') + '</span>') +
            '<span class="dm-row-acts">' +
                '<button class="dm-rowact" data-cact="pin" data-id="' + dmAttr(ws.id) + '" title="' + (ws.pinned ? 'Unpin' : 'Pin') + '">' + dmIcon('pin') + '</button>' +
                '<button class="dm-rowact" data-cact="menu" data-id="' + dmAttr(ws.id) + '" title="More actions">' + dmIcon('more') + '</button>' +
            '</span></div>';
    }

    function dmProjectRow(project) {
        var open = !!DM.projectsOpen[project.id];
        var chats = DM.workspaces.filter(function (ws) { return ws.project_id === project.id && !ws.pinned; });
        var html = '<div class="dm-row' + (open ? ' is-open' : '') + '" data-proj="' + dmAttr(project.id) + '" role="button" tabindex="0" title="' + dmAttr(project.name) + '">' +
            '<span class="dm-caret' + (open ? ' is-open' : '') + '">' + dmIcon('chevron') + '</span>' +
            '<span class="dm-row-ico">' + dmIcon('folder') + '</span>' +
            '<span class="dm-row-label">' + dmEsc(project.name || 'Project') + '</span>' +
            '<span class="dm-row-meta">' + (chats.length ? chats.length : '') + '</span>' +
            '<span class="dm-row-acts">' +
                '<button class="dm-rowact" data-pact="new" data-id="' + dmAttr(project.id) + '" title="New chat in this project">' + dmIcon('plus') + '</button>' +
                '<button class="dm-rowact" data-pact="menu" data-id="' + dmAttr(project.id) + '" title="More actions">' + dmIcon('more') + '</button>' +
            '</span></div>';
        if (open) {
            html += '<div class="dm-proj-kids">';
            html += chats.length ? chats.map(dmChatRow).join('') : '<div class="dm-note">No chats yet.</div>';
            html += '<div class="dm-row dm-newchat-row" data-pact="new" data-id="' + dmAttr(project.id) + '" role="button" tabindex="0">' +
                '<span class="dm-row-ico">' + dmIcon('plus') + '</span>' +
                '<span class="dm-row-label">New chat in ' + dmEsc(project.name || 'this project') + '</span></div>';
            html += '</div>';
        }
        return html;
    }

    function dmRenderChats() {
        var projectIds = DM.projects.map(function (p) { return p.id; });
        var pinned = DM.workspaces.filter(function (ws) { return ws.pinned; });
        var loose = DM.workspaces.filter(function (ws) {
            return !ws.pinned && (!ws.project_id || projectIds.indexOf(ws.project_id) < 0);
        });
        var pinnedSec = $('dmPinnedSec');
        if (pinnedSec) pinnedSec.hidden = !pinned.length;
        var pinnedList = $('dmPinnedList');
        if (pinnedList) pinnedList.innerHTML = pinned.map(dmChatRow).join('');
        var list = $('dmChatList');
        if (list) {
            list.innerHTML = loose.length ? loose.map(dmChatRow).join('')
                : '<div class="dm-note">No chats here yet. Press + to start one.</div>';
        }
        var count = $('dmChatCount');
        if (count) count.textContent = String(loose.length);
        var projects = $('dmProjectList');
        if (projects) {
            projects.innerHTML = DM.projects.length ? DM.projects.map(dmProjectRow).join('')
                : '<div class="dm-note">No projects yet. Group related chats into a project.</div>';
        }
    }

    function dmProjectName(projectId) {
        var project = dmFindProject(projectId);
        return project ? project.name : '';
    }

    function dmUpdateHeader() {
        var ws = dmActiveWorkspace();
        var nameEl = $('dmActiveName');
        var subEl = $('dmActiveId');
        var pinBtn = $('dmPinBtn');
        if (!nameEl || !subEl) return;
        if (ws) {
            nameEl.textContent = ws.name || 'Untitled chat';
            var bits = [ws.id];
            if (ws.project_id) bits.push(dmProjectName(ws.project_id));
            if (ws.message_count) bits.push(ws.message_count + ' message(s)');
            subEl.textContent = bits.join(' \u00b7 ');
            if (pinBtn) {
                pinBtn.classList.toggle('is-on', !!ws.pinned);
                pinBtn.title = ws.pinned ? 'Unpin this chat' : 'Pin this chat';
            }
        } else {
            nameEl.textContent = 'No chat selected';
            subEl.textContent = 'Create a chat to start talking to your data';
            if (pinBtn) pinBtn.classList.remove('is-on');
        }
    }

    function dmPickActiveChat() {
        var userKey = dmUserKey('dm_active_ws');
        var savedWs = localStorage.getItem(userKey) || localStorage.getItem('dm_active_ws_nanopro') || localStorage.getItem('dm_active_ws') || '';
        if (savedWs && dmFindWorkspace(savedWs)) {
            DM.workspaceId = savedWs;
            return savedWs;
        }
        if (DM.workspaceId && dmFindWorkspace(DM.workspaceId)) return DM.workspaceId;
        DM.workspaceId = DM.workspaces.length ? DM.workspaces[0].id : '';
        if (DM.workspaceId) {
            localStorage.setItem(userKey, DM.workspaceId);
            localStorage.setItem('dm_active_ws', DM.workspaceId);
        }
        return DM.workspaceId;
    }

    window.dmLoadChats = async function () {
        try {
            var data = await dmApi('/workspaces?light=true');
            DM.workspaces = data.workspaces || [];
        } catch (err) {
            dmToast(err.message, 'err');
        }
        dmPickActiveChat();
        dmRenderChats();
        dmUpdateHeader();
        return DM.workspaces;
    };

    window.dmLoadProjects = async function () {
        try {
            var data = await dmApi('/projects');
            DM.projects = data.projects || [];
        } catch (err) {
            dmToast(err.message, 'err');
        }
        dmRenderChats();
        return DM.projects;
    };

    window.dmSelectChat = async function (workspaceId) {
        if (!workspaceId) return;
        if (workspaceId !== DM.workspaceId) {
            DM.selection = null;
            if (typeof dmRenderSelection === 'function') dmRenderSelection();
        }
        DM.workspaceId = workspaceId;
        var userKey = dmUserKey('dm_active_ws');
        localStorage.setItem(userKey, workspaceId);
        localStorage.setItem('dm_active_ws', workspaceId);
        var ws = dmFindWorkspace(workspaceId);
        if (ws && ws.project_id) {
            DM.projectId = ws.project_id;
            localStorage.setItem(dmUserKey('dm_active_prj'), DM.projectId);
            localStorage.setItem('dm_active_prj', DM.projectId);
        }
        // Save active workspace to backend DuckDB in background
        dmApi('/workspaces/' + encodeURIComponent(workspaceId) + '/active', { method: 'POST' }).catch(function () {});
        dmRenderChats();
        dmUpdateHeader();
        dmEmptyData();
        if (window.innerWidth <= 1180) { DM.chatsOpen = false; dmApplyPanels(); }
        await dmLoadMessages();
        dmRestoreDraft();
        dmRenderTree();
    };

    async function dmEnsureSchemas() {
        var ws = dmActiveWorkspace();
        if (!ws || (ws.schemas && ws.schemas.length)) return ws;
        try {
            var data = await dmApi('/workspaces?light=false');
            (data.workspaces || []).forEach(function (item) {
                if (item.id === DM.workspaceId && item.schemas) ws.schemas = item.schemas;
            });
        } catch (err) { /* the main schema is always available */ }
        return ws;
    }

    window.dmNewChat = async function (projectId) {
        if (!DM.inited) {
            window.initDataModeling();
        }
        var target = projectId || '';
        try {
            var data = await dmApi('/workspaces', {
                method: 'POST',
                body: JSON.stringify({ name: '', project_id: target })
            });
            var ws = data.workspace || {};
            if (!ws.id) throw new Error('The chat could not be created.');
            DM.workspaceId = ws.id;
            DM.selection = null;
            if (typeof dmRenderSelection === 'function') dmRenderSelection();
            if (!DM.workspaces) DM.workspaces = [];
            if (!DM.workspaces.some(function (w) { return w.id === ws.id; })) {
                DM.workspaces.unshift(ws);
            }
            var userKey = dmUserKey('dm_active_ws');
            localStorage.setItem(userKey, ws.id);
            localStorage.setItem('dm_active_ws', ws.id);
            if (target) {
                DM.projectId = target;
                localStorage.setItem(dmUserKey('dm_active_prj'), target);
                localStorage.setItem('dm_active_prj', target);
                DM.projectsOpen[target] = true;
                dmSaveJson('dm_projects_open', DM.projectsOpen);
            }
            dmCloseDataPanel();
            dmEmptyData();
            dmRenderMessages([]);
            dmRenderChats();
            dmUpdateHeader();
            await Promise.all([dmLoadChats(), dmLoadProjects()]);
            dmApi('/workspaces/' + encodeURIComponent(ws.id) + '/active', { method: 'POST' }).catch(function () {});
            dmRenderTree();
            dmToast('New chat ready', 'ok');
            if (window.innerWidth <= 1180) { DM.chatsOpen = false; dmApplyPanels(); }
            var input = $('dmInput');
            if (input) {
                input.focus();
                input.value = '';
            }
            return ws.id;
        } catch (err) {
            dmToast(err.message, 'err');
            return '';
        }
    };

    window.dmToggleProject = function (projectId) {
        if (!projectId) return;
        var open = !DM.projectsOpen[projectId];
        DM.projectsOpen[projectId] = open;
        dmSaveJson('dm_projects_open', DM.projectsOpen);
        if (open) {
            DM.projectId = projectId;
            localStorage.setItem('dm_active_prj', projectId);
        }
        dmRenderChats();
        dmRenderTree();
    };

    window.dmTogglePin = async function (workspaceId) {
        var ws = dmFindWorkspace(workspaceId);
        if (!ws) return;
        try {
            await dmApi('/workspaces/' + encodeURIComponent(workspaceId) + '/pin', {
                method: 'POST',
                body: JSON.stringify({ pinned: !ws.pinned })
            });
            await dmLoadChats();
            dmRenderTree();
            dmToast(ws.pinned ? 'Chat unpinned' : 'Chat pinned', 'ok');
        } catch (err) {
            dmToast(err.message, 'err');
        }
    };

    window.dmTogglePinActive = function () {
        if (DM.workspaceId) window.dmTogglePin(DM.workspaceId);
    };

    window.dmDeleteChat = async function (workspaceId) {
        var ws = dmFindWorkspace(workspaceId);
        var label = ws ? (ws.name || 'this chat') : 'this chat';
        if (!window.confirm('Delete "' + label + '"?\n\nIts messages, tables and saved results are removed. This cannot be undone.')) return;
        try {
            await dmApi('/workspaces/' + encodeURIComponent(workspaceId), { method: 'DELETE' });
            if (DM.workspaceId === workspaceId) {
                DM.workspaceId = '';
                localStorage.removeItem('dm_active_ws');
            }
            await Promise.all([dmLoadChats(), dmLoadProjects()]);
            DM.workspaceId = dmPickActiveChat();
            dmRenderChats();
            dmUpdateHeader();
            dmEmptyData();
            await dmLoadMessages();
            dmRenderTree();
            dmToast('Chat deleted', 'ok');
        } catch (err) {
            dmToast(err.message, 'err');
        }
    };

    window.dmNewProject = function () {
        window.dmPromptName({
            title: 'New project',
            label: 'Project name',
            value: '',
            note: 'Chats started inside a project stay grouped with it.'
        }, async function (name) {
            try {
                var data = await dmApi('/projects', { method: 'POST', body: JSON.stringify({ name: name }) });
                var project = data.project || {};
                if (project.id) {
                    DM.projectsOpen[project.id] = true;
                    dmSaveJson('dm_projects_open', DM.projectsOpen);
                }
                await dmLoadProjects();
                if (project.id) await window.dmNewChat(project.id);
                dmToast('Project "' + (project.name || name) + '" created', 'ok');
            } catch (err) {
                dmToast(err.message, 'err');
            }
        });
    };

    window.dmRenameChat = function (workspaceId) {
        var ws = dmFindWorkspace(workspaceId);
        if (!ws) return;
        window.dmPromptName({
            title: 'Rename chat',
            label: 'Chat name',
            value: ws.name || '',
            note: 'Only you see this name.'
        }, async function (name) {
            try {
                await dmApi('/workspaces/' + encodeURIComponent(workspaceId), {
                    method: 'PATCH',
                    body: JSON.stringify({ name: name })
                });
                await dmLoadChats();
                dmRenderTree();
                dmToast('Chat renamed', 'ok');
            } catch (err) {
                dmToast(err.message, 'err');
            }
        });
    };

    window.dmRenameActive = function () {
        if (DM.workspaceId) window.dmRenameChat(DM.workspaceId);
        else dmToast('Open a chat first.', 'err');
    };

    window.dmRenameProject = function (projectId) {
        var project = dmFindProject(projectId);
        if (!project) return;
        window.dmPromptName({
            title: 'Rename project',
            label: 'Project name',
            value: project.name || '',
            note: ''
        }, async function (name) {
            try {
                await dmApi('/projects/' + encodeURIComponent(projectId), {
                    method: 'PATCH',
                    body: JSON.stringify({ name: name })
                });
                await Promise.all([dmLoadProjects(), dmLoadChats()]);
                dmRenderTree();
                dmToast('Project renamed', 'ok');
            } catch (err) {
                dmToast(err.message, 'err');
            }
        });
    };

    window.dmDeleteProject = async function (projectId, withChats) {
        var project = dmFindProject(projectId);
        var label = project ? project.name : 'this project';
        var message = withChats
            ? 'Delete "' + label + '" and every chat inside it? This cannot be undone.'
            : 'Delete the project "' + label + '"? Its chats stay in Chats & Tasks.';
        if (!window.confirm(message)) return;
        try {
            await dmApi('/projects/' + encodeURIComponent(projectId) + '?delete_chats=' + (withChats ? 'true' : 'false'), { method: 'DELETE' });
            delete DM.projectsOpen[projectId];
            dmSaveJson('dm_projects_open', DM.projectsOpen);
            if (DM.projectId === projectId) {
                DM.projectId = '';
                localStorage.removeItem('dm_active_prj');
            }
            if (withChats && !dmFindWorkspace(DM.workspaceId)) {
                DM.workspaceId = '';
                localStorage.removeItem('dm_active_ws');
            }
            await Promise.all([dmLoadProjects(), dmLoadChats()]);
            dmPickActiveChat();
            dmRenderChats();
            dmUpdateHeader();
            await dmLoadMessages();
            dmRenderTree();
            dmToast('Project deleted', 'ok');
        } catch (err) {
            dmToast(err.message, 'err');
        }
    };

    async function dmMoveChat(workspaceId, projectId) {
        try {
            await dmApi('/workspaces/' + encodeURIComponent(workspaceId) + '/project', {
                method: 'POST',
                body: JSON.stringify({ project_id: projectId || '' })
            });
            if (projectId) {
                DM.projectsOpen[projectId] = true;
                dmSaveJson('dm_projects_open', DM.projectsOpen);
            }
            await Promise.all([dmLoadChats(), dmLoadProjects()]);
            dmRenderTree();
            dmToast(projectId ? 'Moved to project' : 'Removed from project', 'ok');
        } catch (err) {
            dmToast(err.message, 'err');
        }
    }

    // ------------------------------------------------------------- the menu

    function dmHideMenu() {
        var menu = $('dmMenu');
        if (menu) menu.hidden = true;
        DM.menuItems = null;
    }

    function dmShowMenu(x, y, items) {
        var menu = $('dmMenu');
        if (!menu) return;
        DM.menuItems = items;
        menu.innerHTML = items.map(function (item, index) {
            if (item.sep) return '<div class="dm-menu-sep"></div>';
            return '<button class="dm-menu-item' + (item.danger ? ' danger' : '') + '" data-mi="' + index + '"' + (item.disabled ? ' disabled' : '') + '>' +
                (item.icon ? dmIcon(item.icon) : '') + '<span>' + dmEsc(item.label) + '</span></button>';
        }).join('');
        menu.hidden = false;
        var width = 220;
        var height = 16 + items.length * 31;
        var left = Math.max(8, Math.min(x, window.innerWidth - width - 10));
        var top = Math.max(8, Math.min(y, window.innerHeight - height - 10));
        menu.style.left = left + 'px';
        menu.style.top = top + 'px';
    }

    window.dmChatMenu = function (workspaceId, x, y) {
        var ws = dmFindWorkspace(workspaceId);
        if (!ws) return;
        var items = [
            { label: ws.pinned ? 'Unpin chat' : 'Pin chat', icon: 'pin', run: function () { window.dmTogglePin(workspaceId); } },
            { label: 'Rename chat', icon: 'pencil', run: function () { window.dmRenameChat(workspaceId); } }
        ];
        if (DM.projects.length) {
            items.push({ sep: true });
            DM.projects.slice(0, 8).forEach(function (project) {
                if (project.id === ws.project_id) return;
                items.push({
                    label: 'Move to ' + project.name,
                    icon: 'folder',
                    run: function () { dmMoveChat(workspaceId, project.id); }
                });
            });
            if (ws.project_id) {
                items.push({ label: 'Remove from project', icon: 'folder', run: function () { dmMoveChat(workspaceId, ''); } });
            }
        }
        items.push({ sep: true });
        items.push({ label: 'Delete this chat', icon: 'trash', danger: true, run: function () { window.dmDeleteChat(workspaceId); } });
        dmShowMenu(x, y, items);
    };

    window.dmProjectMenu = function (projectId, x, y) {
        var project = dmFindProject(projectId);
        if (!project) return;
        dmShowMenu(x, y, [
            { label: 'New chat in project', icon: 'plus', run: function () { window.dmNewChat(projectId); } },
            { label: 'Rename project', icon: 'pencil', run: function () { window.dmRenameProject(projectId); } },
            { sep: true },
            { label: 'Delete project (keep chats)', icon: 'folder', run: function () { window.dmDeleteProject(projectId, false); } },
            { label: 'Delete project and chats', icon: 'trash', danger: true, run: function () { window.dmDeleteProject(projectId, true); } }
        ]);
    };

    // --------------------------------------------------------- name dialog

    window.dmPromptName = function (options, callback) {
        options = options || {};
        DM.nameCb = callback || null;
        var modal = $('dmNameModal');
        if (!modal) return;
        $('dmNameTitle').textContent = options.title || 'Name';
        $('dmNameLabel').textContent = options.label || 'Name';
        $('dmNameNote').textContent = options.note || '';
        $('dmNameInput').value = options.value || '';
        modal.classList.add('open');
        setTimeout(function () {
            var input = $('dmNameInput');
            if (!input) return;
            input.focus();
            input.select();
        }, 40);
    };

    window.dmNameClose = function () {
        var modal = $('dmNameModal');
        if (modal) modal.classList.remove('open');
        DM.nameCb = null;
    };

    window.dmNameSubmit = function () {
        var input = $('dmNameInput');
        var value = input ? input.value.trim() : '';
        if (!value) { dmToast('Enter a name first.', 'err'); return; }
        var callback = DM.nameCb;
        window.dmNameClose();
        if (callback) callback(value);
    };

    // ------------------------------------------------------------- explorer

    function dmColumnKey(dbId, schema, table) { return dbId + '::' + schema + '::' + table; }

    function dmColsCached(dbId, schema, table) {
        return DM.columns[dmColumnKey(dbId, schema, table)] || null;
    }

    function dmTableMatches(dbId, schema, table, q) {
        if (String(table.name || '').toLowerCase().indexOf(q) >= 0) return true;
        var cols = dmColsCached(dbId, schema, table.name);
        if (!cols) return false;
        return cols.some(function (c) { return String(c.name || '').toLowerCase().indexOf(q) >= 0; });
    }

    function dmFilterEntry(entry, q) {
        var text = (String(entry.name || '') + ' ' + String(entry.id || '') + ' ' + String(entry.engine || '')).toLowerCase();
        var entryMatch = !q || text.indexOf(q) >= 0;
        var schemas = [];
        (entry.schemas || []).forEach(function (schema) {
            var schemaMatch = entryMatch || String(schema.name || '').toLowerCase().indexOf(q) >= 0;
            var tables = (schema.tables || []).filter(function (table) {
                if (!q) return true;
                return schemaMatch || dmTableMatches(entry.id, schema.name, table, q);
            });
            if (!q || schemaMatch || tables.length) schemas.push({ schema: schema, tables: tables });
        });
        if (q && !entryMatch && !schemas.length) return null;
        var total = 0;
        schemas.forEach(function (item) { total += item.tables.length; });
        return { entry: entry, schemas: schemas, total: total };
    }

    function dmTreeRow(depth, opts) {
        var html = '<div class="dm-trow' + (opts.cls ? ' ' + opts.cls : '') + (opts.active ? ' is-active' : '') + '" style="padding-left:' + (4 + depth * 13) + 'px"';
        if (opts.attrs) html += ' ' + opts.attrs;
        html += ' role="button" tabindex="0">';
        if (opts.key) {
            html += '<button type="button" class="dm-tcaret' + (opts.open ? ' is-open' : '') + '" data-act="toggle" data-key="' + dmAttr(opts.key) + '" title="Expand or collapse">' + dmIcon('chevron') + '</button>';
        } else {
            html += '<span class="dm-tcaret is-empty">' + dmIcon('chevron') + '</span>';
        }
        html += '<span class="dm-tico' + (opts.iconCls ? ' ' + opts.iconCls : '') + '">' + dmIcon(opts.icon || 'table') + '</span>';
        html += '<span class="dm-tlabel">' + dmEsc(opts.label || '') + '</span>';
        if (opts.type) html += '<span class="dm-ttype">' + dmEsc(opts.type) + '</span>';
        if (opts.badge) html += '<span class="dm-tbadge' + (opts.badgeCls ? ' ' + opts.badgeCls : '') + '">' + dmEsc(opts.badge) + '</span>';
        if (opts.actions) html += '<span class="dm-tacts">' + opts.actions + '</span>';
        html += '</div>';
        return html;
    }

    function dmTableNode(entry, schema, table, depth, q) {
        var key = 'tb:' + entry.id + '::' + schema.name + '::' + table.name;
        var open = q ? true : !!DM.treeOpen[key];
        var cols = dmColsCached(entry.id, schema.name, table.name);
        var badge = table.type === 'view' ? 'VIEW' : (table.row_count ? table.row_count + 'r' : '');
        var sel = DM.selection;
        var picked = !!(sel && sel.dbId === entry.id && sel.schema === schema.name && sel.table === table.name);
        var html = dmTreeRow(depth, {
            cls: 'is-table',
            key: key,
            open: open,
            active: picked,
            icon: table.type === 'view' ? 'grid' : 'table',
            label: table.name,
            badge: badge,
            attrs: 'data-act="table" data-db="' + dmAttr(entry.id) + '" data-schema="' + dmAttr(schema.name) + '" data-table="' + dmAttr(table.name) + '" title="' + dmAttr(schema.name + '.' + table.name) + '"'
        });
        if (!open) return html;
        if (DM.colLoading[key]) return html + '<div class="dm-tree-note" style="padding-left:' + (18 + depth * 13) + 'px">Loading columns...</div>';
        if (!cols) return html + '<div class="dm-tree-note" style="padding-left:' + (18 + depth * 13) + 'px">Open the table to load its columns.</div>';
        if (!cols.length) return html + '<div class="dm-tree-note" style="padding-left:' + (18 + depth * 13) + 'px">No columns found.</div>';
        cols.forEach(function (column) {
            html += dmTreeRow(depth + 1, {
                cls: 'is-col',
                icon: column.is_pk ? 'key' : 'grid',
                label: column.name,
                type: column.data_type || 'TEXT',
                badge: column.is_pk ? 'PK' : '',
                badgeCls: 'pk'
            });
        });
        return html;
    }

    function dmSchemaNode(entry, item, depth, q) {
        var key = 'sc:' + entry.id + '::' + item.schema.name;
        var open = q ? true : !!DM.treeOpen[key];
        var sel = DM.selection;
        var picked = !!(sel && sel.dbId === entry.id && sel.schema === item.schema.name && !sel.table);
        var html = dmTreeRow(depth, {
            cls: 'is-schema',
            key: key,
            open: open,
            active: picked,
            icon: 'folder',
            label: item.schema.name,
            badge: item.tables.length ? item.tables.length + ' tbl' : '',
            attrs: 'data-act="schema" data-db="' + dmAttr(entry.id) + '" data-schema="' + dmAttr(item.schema.name) + '" title="' + dmAttr(entry.id + '.' + item.schema.name) + '"'
        });
        if (!open) return html;
        if (!item.tables.length) return html + '<div class="dm-tree-note" style="padding-left:' + (18 + depth * 13) + 'px">No tables yet.</div>';
        item.tables.forEach(function (table) { html += dmTableNode(entry, item.schema, table, depth + 1, q); });
        return html;
    }

    function dmEngineIcon(entry) {
        var engine = String(entry.engine || '').toLowerCase();
        if (entry.kind === 'workspace') return { icon: 'database', cls: 'is-ws' };
        if (engine.indexOf('snow') >= 0) return { icon: 'snowflake', cls: 'is-db' };
        return { icon: 'database', cls: 'is-db' };
    }

    function dmStatusBadge(entry, total) {
        var status = String(entry.status || '');
        if (status === 'live' || status === 'online') return { text: total + ' tbl', cls: 'live' };
        if (status === 'not_configured') return { text: 'auth', cls: '' };
        if (status === 'driver_missing') return { text: 'driver', cls: '' };
        if (status === 'unreachable') return { text: 'offline', cls: '' };
        if (entry.error) return { text: 'error', cls: '' };
        return { text: total + ' tbl', cls: '' };
    }

    function dmDbNode(filtered, depth, q) {
        var entry = filtered.entry;
        var key = 'db:' + entry.id;
        var open = q ? true : !!DM.treeOpen[key];
        var ico = dmEngineIcon(entry);
        var badge = dmStatusBadge(entry, filtered.total);
        var sel = DM.selection;
        var active = !!(entry.workspace_id && entry.workspace_id === DM.workspaceId) ||
            !!(sel && sel.dbId === entry.id && !sel.schema && !sel.table);
        var html = dmTreeRow(depth, {
            cls: 'is-db',
            key: key,
            open: open,
            active: active,
            icon: ico.icon,
            iconCls: ico.cls,
            label: entry.name || entry.id,
            badge: badge.text,
            badgeCls: badge.cls,
            attrs: 'data-act="db" data-db="' + dmAttr(entry.id) + '" title="' + dmAttr(entry.id) + '"'
        });
        if (!open) return html;
        if (!filtered.schemas.length) {
            return html + '<div class="dm-tree-note" style="padding-left:' + (18 + depth * 13) + 'px">' + dmEsc(entry.detail || entry.error || 'No schemas or tables yet.') + '</div>';
        }
        filtered.schemas.forEach(function (item) { html += dmSchemaNode(entry, item, depth + 1, q); });
        return html;
    }

    function dmGroupHtml(groupKey, title, icon, entries, q, emptyNote) {
        var open = q ? true : DM.treeOpen['root:' + groupKey] !== false;
        var head = '<div class="dm-group-head" data-act="toggle" data-key="root:' + groupKey + '" role="button" tabindex="0">' +
            '<span class="dm-tcaret' + (open ? ' is-open' : '') + '">' + dmIcon('chevron') + '</span>' +
            '<span class="dm-tico' + (groupKey === 'databases' ? ' is-db' : ' is-ws') + '">' + dmIcon(icon) + '</span>' +
            '<span class="dm-tlabel">' + dmEsc(title) + '</span>' +
            '<span class="dm-tbadge">' + entries.length + '</span>' +
            '</div>';
        if (!open) return head;
        if (!entries.length) return head + '<div class="dm-tree-note">' + dmEsc(emptyNote) + '</div>';
        var body = '';
        entries.forEach(function (item) { body += dmDbNode(item, 1, q); });
        return head + body;
    }

    function dmScopeWorkspaceIds() {
        var ids = [];
        var ws = dmActiveWorkspace();
        if (ws) {
            ids.push(ws.id);
            if (ws.project_id) {
                DM.workspaces.forEach(function (other) {
                    if (other.project_id === ws.project_id && ids.indexOf(other.id) < 0) ids.push(other.id);
                });
            }
        } else if (DM.projectId) {
            DM.workspaces.forEach(function (other) {
                if (other.project_id === DM.projectId) ids.push(other.id);
            });
        }
        return ids;
    }

    window.dmRenderTree = function () {
        var tree = $('dmDatabaseTree');
        if (!tree) return;
        var filterEl = $('dmCatalogFilter');
        var q = filterEl ? filterEl.value.trim().toLowerCase() : '';
        var clearBtn = $('dmClearFilter');
        if (clearBtn) clearBtn.classList.toggle('show', !!q);

        var all = DM.catalog || [];
        if (!all.length) {
            tree.innerHTML = '<div class="dm-tree-note">' +
                (DM.scanning ? 'Scanning your databases in the background...' : 'No databases detected yet. Click rescan to look again.') +
                '</div>';
            return;
        }
        var scopeIds = dmScopeWorkspaceIds();
        var scoped = [];
        var databases = [];
        all.forEach(function (entry) {
            var filtered = dmFilterEntry(entry, q);
            if (!filtered) return;
            if (entry.kind === 'workspace') {
                if (scopeIds.indexOf(entry.workspace_id) >= 0) scoped.push(filtered);
            } else {
                databases.push(filtered);
            }
        });

        var ws = dmActiveWorkspace();
        var scopeName = ws ? (ws.name || 'this chat') : (dmProjectName(DM.projectId) || 'this chat');
        var label = 'Tables in ' + scopeName;
        var html = dmGroupHtml('project', label, 'folder', scoped, q, 'No tables yet. Upload a file or ask the AI to create one.');
        html += dmGroupHtml('databases', 'Databases', 'database', databases, q, 'No external databases detected yet.');
        tree.innerHTML = html || '<div class="dm-tree-note">Nothing matches that search.</div>';
    };

    window.dmClearFilter = function () {
        var el = $('dmCatalogFilter');
        if (el) { el.value = ''; el.focus(); }
        window.dmRenderTree();
    };

    function dmToggleNode(key) {
        if (!key) return;
        var open = key.indexOf('root:') === 0 ? DM.treeOpen[key] !== false : !!DM.treeOpen[key];
        DM.treeOpen[key] = !open;
        dmSaveJson('dm_tree_open', DM.treeOpen);
        if (DM.treeOpen[key] && key.indexOf('tb:') === 0) {
            var parts = key.split('::');
            dmLoadColumns(parts[0].slice(3), parts[1], parts[2]);
        }
        window.dmRenderTree();
    }

    async function dmLoadColumns(dbId, schema, table) {
        if (!dbId || !schema || !table) return;
        var key = 'tb:' + dbId + '::' + schema + '::' + table;
        if (dmColsCached(dbId, schema, table) || DM.colLoading[key]) return;
        DM.colLoading[key] = true;
        window.dmRenderTree();
        try {
            var data = await dmApi('/table?db_id=' + encodeURIComponent(dbId) + '&schema=' + encodeURIComponent(schema) + '&table=' + encodeURIComponent(table));
            DM.columns[dmColumnKey(dbId, schema, table)] = ((data.table || {}).columns) || [];
        } catch (err) {
            DM.columns[dmColumnKey(dbId, schema, table)] = [];
            dmToast(err.message, 'err');
        }
        delete DM.colLoading[key];
        window.dmRenderTree();
    }

    function dmCacheCatalog(list) {
        try {
            var text = JSON.stringify(list || []);
            if (text.length < 450000) localStorage.setItem('dm_catalog_cache', text);
        } catch (err) { /* quota */ }
    }

    function dmCachedCatalog() {
        try {
            var list = JSON.parse(localStorage.getItem('dm_catalog_cache') || '[]');
            return Array.isArray(list) ? list : [];
        } catch (err) { return []; }
    }

    function dmPollCatalog() {
        clearTimeout(DM.pollTimer);
        DM.pollTimer = setTimeout(async function () {
            if (!DM.scanning || DM.pollTries > 16) { DM.scanning = false; return; }
            DM.pollTries++;
            try {
                var data = await dmApi('/catalog?fast=1');
                if (data.databases && data.databases.length) {
                    DM.catalog = data.databases;
                    dmCacheCatalog(DM.catalog);
                    window.dmRenderTree();
                }
                DM.scanning = !!data.scanning;
                if (DM.scanning) dmPollCatalog();
            } catch (err) {
                DM.scanning = false;
            }
        }, 1400);
    }

    window.dmLoadCatalog = async function (refresh) {
        try {
            var data = await dmApi('/catalog' + (refresh ? '?refresh=true' : '?fast=1'));
            if (data.databases && data.databases.length) {
                DM.catalog = data.databases;
                dmCacheCatalog(DM.catalog);
            }
            DM.scanning = !!data.scanning;
            window.dmRenderTree();
            if (DM.scanning) { DM.pollTries = 0; dmPollCatalog(); }
        } catch (err) {
            dmToast(err.message, 'err');
            window.dmRenderTree();
        }
    };

    var dmSingleClickTimer = null;

    function dmTreeClick(ev) {
        var el = ev.target.closest('[data-act]');
        if (!el) return;
        var act = el.getAttribute('data-act');
        if (act === 'toggle') {
            ev.stopPropagation();
            dmToggleNode(el.getAttribute('data-key'));
            return;
        }
        var dbId = el.getAttribute('data-db');
        var schema = el.getAttribute('data-schema');
        var table = el.getAttribute('data-table');
        clearTimeout(dmSingleClickTimer);
        dmSingleClickTimer = setTimeout(function () {
            if (act === 'db') dmToggleNode('db:' + dbId);
            else if (act === 'schema') dmToggleNode('sc:' + dbId + '::' + schema);
            else if (act === 'table') window.dmShowTable(dbId, schema, table);
        }, 200);
    }

    function dmDbLabel(dbId) {
        var id = String(dbId || '');
        if (!id) return 'active workspace';
        if (id.indexOf('workspace:') === 0) {
            var wsId = id.slice('workspace:'.length);
            for (var i = 0; i < DM.workspaces.length; i++) {
                if (DM.workspaces[i].id === wsId) return DM.workspaces[i].name || wsId;
            }
            return wsId;
        }
        for (var j = 0; j < DM.catalog.length; j++) {
            if (DM.catalog[j].id === id) return DM.catalog[j].name || id;
        }
        return id;
    }

    window.dmSelectionPath = function () {
        var sel = DM.selection;
        if (!sel || !sel.dbId) return '';
        var parts = [dmDbLabel(sel.dbId)];
        if (sel.schema) parts.push(sel.schema);
        if (sel.table) parts.push(sel.table);
        return parts.join(' \u203a ');
    };

    window.dmRenderSelection = function () {
        var bar = $('dmCtxBar');
        var pathEl = $('dmCtxPath');
        var levelEl = $('dmCtxLevel');
        if (!bar || !pathEl) return;
        var sel = DM.selection;
        if (!sel || !sel.dbId) { bar.hidden = true; return; }
        var level = sel.table ? 'Table' : (sel.schema ? 'Schema' : 'Database');
        if (levelEl) levelEl.textContent = level;
        var label = dmDbLabel(sel.dbId);
        var html = '<b>' + dmEsc(label) + '</b>';
        if (sel.schema) html += ' \u203a ' + dmEsc(sel.schema);
        if (sel.table) html += ' \u203a <b>' + dmEsc(sel.table) + '</b>';
        pathEl.innerHTML = html;
        pathEl.title = (sel.dbId || '') + (sel.schema ? '.' + sel.schema : '') + (sel.table ? '.' + sel.table : '');
        bar.hidden = false;
    };

    window.dmSetSelection = function (dbId, schema, table) {
        if (!dbId) return;
        schema = schema || '';
        table = table || '';
        DM.selection = { dbId: dbId, schema: schema, table: table };
        if (table) DM.tableCtx = { dbId: dbId, schema: schema || 'main', table: table };
        window.dmRenderSelection();
        var level = table ? 'Table' : (schema ? 'Schema' : 'Database');
        dmToast(level + ' selected: ' + window.dmSelectionPath(), 'ok');
    };

    window.dmClearSelection = function () {
        DM.selection = null;
        window.dmRenderSelection();
        dmToast('Selection cleared', 'ok');
    };

    function dmInsertComposerPath(dbId, schema, table) {
        var input = $('dmInput');
        if (!input || !dbId || !table) return;
        var dbLabel = String(dbId).indexOf('workspace:') === 0 ? String(dbId).slice(10) : String(dbId);
        var text = dbLabel + '.' + (schema || 'main') + '.' + table;
        var start = input.selectionStart == null ? input.value.length : input.selectionStart;
        var end = input.selectionEnd == null ? start : input.selectionEnd;
        if (start > end) { var tmp = start; start = end; end = tmp; }
        var before = input.value.slice(0, start);
        var after = input.value.slice(end);
        if (before && !/[\s"'(]$/.test(before)) text = ' ' + text;
        if (after && !/^[\s"'),.]/.test(after)) text = text + ' ';
        input.value = before + text + after;
        var pos = before.length + text.length;
        input.focus();
        input.setSelectionRange(pos, pos);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function dmTreeDblClick(ev) {
        clearTimeout(dmSingleClickTimer);
        var el = ev.target.closest('[data-act]');
        if (!el) return;
        var act = el.getAttribute('data-act');
        if (act === 'toggle') return;
        ev.preventDefault();
        ev.stopPropagation();
        var dbId = el.getAttribute('data-db');
        if (act === 'db') { window.dmSetSelection(dbId, '', ''); return; }
        if (act === 'schema') { window.dmSetSelection(dbId, el.getAttribute('data-schema'), ''); return; }
        if (act === 'table') {
            var schema = el.getAttribute('data-schema');
            var table = el.getAttribute('data-table');
            window.dmSetSelection(dbId, schema, table);
            dmInsertComposerPath(dbId, schema, table);
            window.dmShowTable(dbId, schema, table);
        }
    }

    // ----------------------------------------------------------- data dock

    function dmOpenData() {
        if (!DM.dataOpen) {
            DM.dataOpen = true;
            localStorage.setItem('dm_data_open', '1');
            dmApplyData();
        }
    }

    function dmCloseDataPanel() {
        DM.tableCtx = null;
        var ask = $('dmAskTableBtn');
        if (ask) ask.hidden = true;
    }

    function dmExportUrl() {
        var target = DM.exportTarget;
        if (!target) return '';
        var select = $('dmExportFormat');
        var fmt = select ? select.value : 'csv';
        if (target.kind === 'run') {
            return '/api/data_modeling/runs/' + encodeURIComponent(target.runId) + '/download?format=' + encodeURIComponent(fmt);
        }
        return '/api/data_modeling/table/download?db_id=' + encodeURIComponent(target.dbId) +
            '&schema=' + encodeURIComponent(target.schema || 'main') +
            '&table=' + encodeURIComponent(target.table) +
            '&format=' + encodeURIComponent(fmt);
    }

    window.dmApplyExportFormat = function () {
        var wrap = $('dmExportWrap');
        var link = $('dmResultDownload');
        if (!wrap || !link) return;
        var url = dmExportUrl();
        if (!url) {
            wrap.hidden = true;
            link.removeAttribute('href');
            return;
        }
        link.href = url;
        wrap.hidden = false;
    };

    function dmSetExportTarget(target) {
        DM.exportTarget = target || null;
        window.dmApplyExportFormat();
    }

    window.dmEmptyData = function () {
        dmCloseDataPanel();
        var title = $('dmDataTitle');
        var meta = $('dmDataMeta');
        var body = $('dmDataBody');
        if (title) title.textContent = 'Data';
        if (meta) meta.textContent = 'Table previews and query results appear here';
        if (body) body.innerHTML = '<div class="dm-data-empty">Select a table in the Explorer or ask a question &mdash; tables and query results open here, below the chat.</div>';
        dmSetExportTarget(null);
    };

    window.dmClearData = function () {
        window.dmEmptyData();
        dmToast('Data panel cleared', 'ok');
    };

    window.dmShowTable = async function (dbId, schema, table) {
        dmOpenData();
        dmCloseDataPanel();
        if (window.innerWidth <= 1180 && DM.explorerOpen) {
            DM.explorerOpen = false;
            dmApplyPanels();
        }
        DM.tableCtx = { dbId: dbId, schema: schema, table: table };
        dmSetExportTarget({ kind: 'table', dbId: dbId, schema: schema, table: table });
        var ask = $('dmAskTableBtn');
        if (ask) ask.hidden = false;
        var title = $('dmDataTitle');
        var meta = $('dmDataMeta');
        var body = $('dmDataBody');
        if (title) title.textContent = table;
        if (meta) meta.textContent = dmDbLabel(dbId) + ' \u203a ' + schema + ' \u203a ' + table;
        if (body) body.innerHTML = '<div class="dm-muted">Loading table metadata...</div>';
        try {
            var data = await dmApi('/table?db_id=' + encodeURIComponent(dbId) + '&schema=' + encodeURIComponent(schema) + '&table=' + encodeURIComponent(table));
            var details = data.table || {};
            DM.columns[dmColumnKey(dbId, schema, table)] = details.columns || [];
            window.dmRenderTableDetails(details);
            if (DM.treeOpen['tb:' + dbId + '::' + schema + '::' + table]) window.dmRenderTree();
        } catch (err) {
            if (body) body.innerHTML = '<div class="dm-muted">' + dmEsc(err.message) + '</div>';
        }
    };

    window.dmRenderTableDetails = function (details) {
        var body = $('dmDataBody');
        if (!body) return;
        var columns = details.columns || [];
        var sample = details.sample || [];
        var sampleCols = columns.map(function (column) { return column.name; });
        var title = $('dmDataTitle');
        var meta = $('dmDataMeta');
        if (title) title.textContent = details.table || 'Table';
        if (meta) meta.textContent = dmDbLabel(details.database || '') + ' \u203a ' + (details.schema || 'main') + ' \u203a ' + (details.table || '');

        var html = '<div class="dm-stat-row">' +
            '<span class="dm-stat">' + (details.row_count === null || details.row_count === undefined ? 'Rows: n/a' : 'Rows: ' + details.row_count) + '</span>' +
            '<span class="dm-stat">Columns: ' + columns.length + '</span>' +
            (details.foreign_keys && details.foreign_keys.length ? '<span class="dm-stat">FK: ' + details.foreign_keys.length + '</span>' : '') +
            (details.indexes && details.indexes.length ? '<span class="dm-stat">Indexes: ' + details.indexes.length + '</span>' : '') +
            '</div>';
        if (details.error) html += '<div class="dm-note-line">' + dmEsc(details.error) + '</div>';

        html += '<div class="dm-sec-title">Columns</div>';
        if (columns.length) {
            html += '<div class="dm-table-wrap"><table class="dm-dtable"><thead><tr><th>#</th><th>Column</th><th>Data type</th><th>Null</th><th>Key</th><th>Default</th></tr></thead><tbody>';
            columns.forEach(function (column, index) {
                html += '<tr><td>' + (index + 1) + '</td><td>' + dmEsc(column.name) + '</td><td>' + dmEsc(column.data_type || 'TEXT') + '</td>' +
                    '<td>' + (column.not_null ? 'NOT NULL' : 'NULL') + '</td>' +
                    '<td>' + (column.is_pk ? 'PRIMARY KEY' : '') + '</td>' +
                    '<td>' + dmEsc(column.default === null || column.default === undefined ? '' : column.default) + '</td></tr>';
            });
            html += '</tbody></table></div>';
        } else {
            html += '<div class="dm-muted">No column metadata available.</div>';
        }

        if (sample.length) {
            html += '<div class="dm-sec-title">Sample data (first 5 rows)</div>' + dmTableHtml(sampleCols, sample);
        }
        if (details.ddl) {
            html += '<div class="dm-sec-title">Definition</div><pre>' + dmEsc(details.ddl) + '</pre>';
        }
        if (details.foreign_keys && details.foreign_keys.length) {
            html += '<div class="dm-sec-title">Foreign keys</div><pre>' + dmEsc(JSON.stringify(details.foreign_keys, null, 2)) + '</pre>';
        }
        if (details.indexes && details.indexes.length) {
            html += '<div class="dm-sec-title">Indexes</div><pre>' + dmEsc(JSON.stringify(details.indexes, null, 2)) + '</pre>';
        }
        body.innerHTML = html;
    };

    window.dmAskAboutTable = function () {
        var ctx = DM.tableCtx;
        if (!ctx) return;
        var prompt = 'Explain the table "' + ctx.table + '" in schema "' + ctx.schema + '" of "' + ctx.dbId + '": what it stores, its key columns and how it can be joined with other tables.';
        var input = $('dmInput');
        if (input) {
            input.value = prompt;
            input.focus();
            dmAutoGrow(input);
        }
    };

    window.dmShowResultPanel = function (title, note, result) {
        dmOpenData();
        dmCloseDataPanel();
        var titleEl = $('dmDataTitle');
        var metaEl = $('dmDataMeta');
        var body = $('dmDataBody');
        if (titleEl) titleEl.textContent = title || 'Result';
        var meta = [];
        if (result && result.row_count !== undefined) meta.push(result.row_count + ' row(s)');
        if (result && result.truncated) meta.push('preview capped');
        if (result && result.execution_time_ms) meta.push(result.execution_time_ms + ' ms');
        if (metaEl) metaEl.textContent = meta.join(' \u00b7 ');
        var html = '';
        if (note) html += '<div class="dm-note-line">' + dmEsc(note) + '</div>';
        if (result) html += dmTableHtml(result.columns || [], result.rows || []);
        if (body) body.innerHTML = html || '<div class="dm-muted">No data.</div>';
        if (result && result.run_id) {
            dmSetExportTarget({ kind: 'run', runId: result.run_id });
        } else if (result && result.table_target) {
            dmSetExportTarget(result.table_target);
        } else {
            dmSetExportTarget(null);
        }
    };

    window.dmRenderResult = function (result) {
        window.dmShowResultPanel('Query result', 'The AI ran this query in your chat workspace.', result);
    };

    // ------------------------------------------------------------- messages

    function dmEmptyHtml() {
        return '<div class="dm-empty" id="dmEmptyState">' +
            '<div class="dm-empty-ico">' + dmIcon('sparkle') + '</div>' +
            '<h3>Your data, in plain language</h3>' +
            '<p>Ask for tables, joins, filters, reports or uploads. The AI writes and runs the SQL for you and the data opens in the dock below.</p>' +
            '<div class="dm-suggest">' +
            '<button data-prompt="List all databases and tables available in NanoPro with row counts." onclick="dmUsePrompt(this)">What data do I have?</button>' +
            '<button data-prompt="Create a table called sales_orders with id, customer_name, city, amount and order_date, then insert 3 sample rows." onclick="dmUsePrompt(this)">Create a table with sample data</button>' +
            '<button data-prompt="Use Snowflake: create a table BANK_DB.SALES.CUSTOMERS with customer data and show the contents." onclick="dmUsePrompt(this)">Create a Snowflake table</button>' +
            '<button data-prompt="Join my workspace tables and show the top customers by total amount." onclick="dmUsePrompt(this)">Build a join and rank results</button>' +
            '<button onclick="dmUploadOpen()">Upload CSV / Excel</button>' +
            '</div></div>';
    }

    function dmMsgHtml(message) {
        var role = message.role === 'user' ? 'user' : 'ai';
        var meta = message.meta || {};
        var sql = message.sql_text || message.sql || meta.sql || '';
        var html = '<div class="dm-msg ' + role + '">' +
            '<div class="dm-avatar">' + (role === 'user' ? 'YOU' : 'AI') + '</div>' +
            '<div class="dm-bubble"><div class="dm-text">' + dmEsc(message.content || '') + '</div>';
        if (role === 'user') {
            html += dmAttachmentTagsHtml(meta.attachments);
        }
        if (sql) {
            html += '<details class="dm-sql"><summary>SQL used by the AI</summary><pre>' + dmEsc(sql) + '</pre></details>';
        }
        if (meta.error) {
            html += '<div class="dm-tag err" style="display:inline-block;margin-top:8px;">' + dmEsc(meta.error) + '</div>';
        }
        if (role === 'ai') {
            html += '<div class="dm-msg-foot">';
            if (meta.model) html += '<span class="dm-tag">' + dmEsc(meta.model) + '</span>';
            if (meta.fast_path) html += '<span class="dm-tag ok">instant NLU</span>';
            if (meta.latency_ms) {
                var ms = Number(meta.latency_ms);
                var speed = ms >= 1000 ? (ms / 1000).toFixed(1) + 's' : Math.round(ms) + 'ms';
                html += '<span class="dm-tag">' + speed + '</span>';
            }
            if (meta.row_count) html += '<span class="dm-tag ok">' + meta.row_count + ' row(s)</span>';
            else if (meta.rows_affected) html += '<span class="dm-tag ok">' + meta.rows_affected + ' affected</span>';
            if (meta.run_id) html += '<button class="dm-linkbtn" data-run="' + dmAttr(meta.run_id) + '">Show data</button>';
            if (sql) html += '<button class="dm-linkbtn" data-copy="' + dmAttr(sql) + '">Copy SQL</button>';
            html += '</div>';
        }
        html += '</div></div>';
        return html;
    }

    window.dmRenderMessages = function (messages) {
        var box = $('dmMessages');
        DM.lastMessages = messages || [];
        if (!box) return;
        if (!messages || !messages.length) {
            box.innerHTML = dmEmptyHtml();
            return;
        }
        box.innerHTML = messages.map(dmMsgHtml).join('');
        box.scrollTop = box.scrollHeight;
    };

    window.dmLoadMessages = async function (silent) {
        if (!DM.workspaceId) {
            window.dmRenderMessages([]);
            return [];
        }
        try {
            var data = await dmApi('/workspaces/' + encodeURIComponent(DM.workspaceId) + '/messages');
            var messages = data.messages || [];
            window.dmRenderMessages(messages);
            return messages;
        } catch (err) {
            if (!silent) dmToast(err.message, 'err');
            return null;
        }
    };

    async function dmRecoverLateReply(baselineAi, workspaceId) {
        // The gateway can give up before Render's LLM call finishes. The backend
        // still persists the assistant message, so poll until it shows up.
        var deadline = Date.now() + 110000;
        while (Date.now() < deadline) {
            await new Promise(function (resolve) { setTimeout(resolve, 4000); });
            if (DM.workspaceId !== workspaceId) return false;
            try {
                var data = await dmApi('/workspaces/' + encodeURIComponent(workspaceId) + '/messages', { timeoutMs: 20000 });
                var messages = data.messages || [];
                var aiCount = messages.filter(function (m) { return m.role !== 'user'; }).length;
                if (aiCount > baselineAi) {
                    window.dmRenderMessages(messages);
                    dmToast('Reply received.', 'ok');
                    return true;
                }
            } catch (err) { /* backend still busy - keep polling */ }
        }
        return false;
    }

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
        el.style.height = Math.min(el.scrollHeight, 150) + 'px';
    }

    function dmRestoreDraft() {
        var input = $('dmInput');
        if (!input) return;
        try {
            var draftKey = dmUserKey('dm_draft_' + (DM.workspaceId || 'global'));
            var draft = localStorage.getItem(draftKey) || '';
            input.value = draft;
            dmAutoGrow(input);
        } catch (e) {}
    }

    function dmSaveDraft() {
        var input = $('dmInput');
        if (!input) return;
        try {
            var draftKey = dmUserKey('dm_draft_' + (DM.workspaceId || 'global'));
            if (input.value && input.value.trim()) {
                localStorage.setItem(draftKey, input.value);
            } else {
                localStorage.removeItem(draftKey);
            }
        } catch (e) {}
    }

    function dmClearDraft() {
        var input = $('dmInput');
        if (input) input.value = '';
        try {
            var draftKey = dmUserKey('dm_draft_' + (DM.workspaceId || 'global'));
            localStorage.removeItem(draftKey);
        } catch (e) {}
    }

    // ------------------------------------------------------------ attachments

    function dmHumanSize(bytes) {
        var n = Number(bytes || 0);
        if (n >= 1048576) return (n / 1048576).toFixed(1) + ' MB';
        if (n >= 1024) return Math.round(n / 1024) + ' KB';
        return n + ' B';
    }

    function dmAttachmentMetaLine(att) {
        if (att.error) return att.error;
        if (att.loading) return 'uploading…';
        if (att.kind === 'image') {
            return (att.width && att.height) ? att.width + '×' + att.height + ' · image' : 'image';
        }
        var bits = [];
        if (att.row_count !== undefined && att.row_count !== null) bits.push(att.row_count + ' rows');
        if (att.columns && att.columns.length) bits.push(att.columns.length + ' cols');
        if (!bits.length) bits.push(dmHumanSize(att.size_bytes));
        return bits.join(' · ');
    }

    function dmAttachmentChipHtml(att, removable) {
        var thumb = att.localUrl
            ? '<img class="dm-attach-thumb" src="' + dmAttr(att.localUrl) + '" alt="">'
            : '<span class="dm-attach-kind">' + (att.loading ? '<span class="dm-attach-spin"></span>' : (att.kind === 'image' ? 'IMG' : 'TBL')) + '</span>';
        var id = att.attachment_id || att.local_id || '';
        return '<div class="dm-attach-chip">' + thumb +
            '<div style="min-width:0;">' +
            '<div class="dm-attach-name" title="' + dmAttr(att.filename || '') + '">' + dmEsc(att.filename || 'Attachment') + '</div>' +
            '<div class="dm-attach-meta" title="' + dmAttr(dmAttachmentMetaLine(att)) + '">' + dmEsc(dmAttachmentMetaLine(att)) + '</div>' +
            '</div>' +
            (removable ? '<button class="dm-attach-x" type="button" title="Remove attachment" onclick="dmRemoveAttachment(\'' + dmAttr(id) + '\')">✕</button>' : '') +
            '</div>';
    }

    function dmRenderAttachStrip() {
        var strip = $('dmAttachStrip');
        if (!strip) return;
        strip.innerHTML = (DM.attachments || []).map(function (att) {
            return dmAttachmentChipHtml(att, true);
        }).join('');
    }

    window.dmPickAttachment = function () {
        if (DM.sending) return;
        var input = $('dmAttachInput');
        if (input) input.click();
    };

    window.dmAttachmentChosen = async function (input) {
        var files = Array.prototype.slice.call((input && input.files) || []);
        if (input) input.value = '';
        if (!files.length) return;
        if (!DM.workspaceId) {
            var created = await window.dmNewChat(DM.projectId || '');
            if (!created) { dmToast('Create a chat first.', 'err'); return; }
        }
        if (!DM.attachments) DM.attachments = [];
        var room = 5 - DM.attachments.length;
        if (room <= 0) { dmToast('At most 5 attachments per message.', 'err'); return; }
        if (files.length > room) {
            files = files.slice(0, room);
            dmToast('Only 5 attachments are sent at a time.', 'err');
        }
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            if (file.size > 25 * 1024 * 1024) {
                dmToast(file.name + ' is larger than 25 MB.', 'err');
                continue;
            }
            var entry = {
                local_id: 'loc_' + Date.now() + '_' + i,
                filename: file.name,
                size_bytes: file.size,
                kind: /^image\//i.test(file.type || '') ? 'image' : 'table',
                loading: true,
                error: ''
            };
            if (entry.kind === 'image' && window.URL && URL.createObjectURL) {
                entry.localUrl = URL.createObjectURL(file);
            }
            DM.attachments.push(entry);
            dmRenderAttachStrip();
            var btn = $('dmAttachBtn');
            if (btn) btn.classList.add('busy');
            var form = new FormData();
            form.append('file', file);
            form.append('workspace_id', DM.workspaceId);
            try {
                var data = await dmApi('/attachments', { method: 'POST', body: form });
                var info = data.attachment || {};
                entry.attachment_id = info.attachment_id;
                entry.kind = info.kind || entry.kind;
                entry.row_count = info.row_count;
                entry.columns = info.columns || [];
                entry.width = info.width;
                entry.height = info.height;
                entry.error = info.error || '';
                entry.loading = false;
            } catch (err) {
                entry.loading = false;
                entry.error = err.message;
                dmToast(err.message, 'err');
            }
            if (btn && !(DM.attachments || []).some(function (att) { return att.loading; })) {
                btn.classList.remove('busy');
            }
            dmRenderAttachStrip();
        }
    };

    window.dmRemoveAttachment = function (id) {
        var index = -1;
        (DM.attachments || []).forEach(function (att, i) {
            if ((att.attachment_id || att.local_id) === id) index = i;
        });
        if (index < 0) return;
        var removed = DM.attachments.splice(index, 1)[0];
        if (removed && removed.localUrl && window.URL && URL.revokeObjectURL) {
            URL.revokeObjectURL(removed.localUrl);
        }
        dmRenderAttachStrip();
    };

    function dmAttachmentTagsHtml(attachments) {
        if (!attachments || !attachments.length) return '';
        return '<div class="dm-msg-atts">' + attachments.map(function (att) {
            return '<span class="dm-msg-att" title="' + dmAttr(att.filename || '') + '">' +
                '<strong style="color:#7FB0FF;">' + (att.kind === 'image' ? 'IMG' : 'TBL') + '</strong>' +
                '<span>' + dmEsc(att.filename || 'attachment') + '</span></span>';
        }).join('') + '</div>';
    }

    function dmAppendTyping() {
        var box = $('dmMessages');
        if (!box) return;
        var empty = $('dmEmptyState');
        if (empty) empty.remove();
        var row = document.createElement('div');
        row.className = 'dm-msg ai';
        row.id = 'dmTypingRow';
        row.innerHTML = '<div class="dm-avatar">AI</div><div class="dm-bubble"><div class="dm-typing"><i></i><i></i><i></i></div></div>';
        box.appendChild(row);
        box.scrollTop = box.scrollHeight;
    }

    function dmRemoveTyping() {
        var row = $('dmTypingRow');
        if (row) row.remove();
    }

    function dmAppendLocalUser(text, attachments) {
        var box = $('dmMessages');
        if (!box) return;
        var empty = $('dmEmptyState');
        if (empty) empty.remove();
        var row = document.createElement('div');
        row.className = 'dm-msg user';
        row.innerHTML = '<div class="dm-avatar">YOU</div><div class="dm-bubble"><div class="dm-text">' +
            dmEsc(text) + '</div>' + dmAttachmentTagsHtml(attachments) + '</div>';
        box.appendChild(row);
        box.scrollTop = box.scrollHeight;
    }

    window.dmSendMessage = async function () {
        if (DM.sending) return;
        var input = $('dmInput');
        if (!input) return;
        var text = (input.value || '').trim();
        var pending = DM.attachments || [];
        if (pending.some(function (att) { return att.loading; })) {
            dmToast('Wait for the attachment to finish uploading.', 'err');
            return;
        }
        var ready = pending.filter(function (att) { return !!att.attachment_id; });
        if (!text && !ready.length) { input.focus(); return; }
        if (!DM.workspaceId) {
            var created = await window.dmNewChat(DM.projectId || '');
            if (!created) return;
        }
        var sendBtn = $('dmSend');
        DM.sending = true;
        if (sendBtn) sendBtn.disabled = true;
        input.value = '';
        dmClearDraft();
        dmAutoGrow(input);
        dmAppendLocalUser(text || ('Attached: ' + ready.map(function (att) { return att.filename; }).join(', ')), ready);
        dmAppendTyping();
        var workspaceId = DM.workspaceId;
        var baselineAi = (DM.lastMessages || []).filter(function (m) { return m.role !== 'user'; }).length;
        if (!DM.lastMessages || !DM.lastMessages.length) {
            try {
                var seeded = await dmApi('/workspaces/' + encodeURIComponent(workspaceId) + '/messages', { timeoutMs: 20000 });
                baselineAi = (seeded.messages || []).filter(function (m) { return m.role !== 'user'; }).length;
            } catch (err) { /* baseline is only used for late-reply recovery */ }
        }
        var payload = {
            workspace_id: workspaceId,
            message: text,
            attachments: ready.map(function (att) { return { attachment_id: att.attachment_id }; })
        };
        if (DM.selection && DM.selection.dbId) {
            payload.context = {
                db_id: DM.selection.dbId || '',
                schema: DM.selection.schema || '',
                table: DM.selection.table || ''
            };
        } else if (DM.tableCtx && DM.tableCtx.table) {
            payload.context = { db_id: DM.tableCtx.dbId || '', schema: DM.tableCtx.schema || '', table: DM.tableCtx.table };
        }
        try {
            var data = await dmApi('/chat', {
                method: 'POST',
                body: JSON.stringify(payload),
                timeoutMs: 120000
            });
            dmRemoveTyping();
            if (data.schema_created) dmToast('Schema ' + data.schema_created.schema + ' created', 'ok');
            if (data.imports && data.imports.length) {
                var first = data.imports[0];
                dmToast('Imported ' + first.rows_inserted + ' row(s) into ' + first.schema + '.' + first.table, 'ok');
                if (data.imports.length === 1) {
                    DM.tableCtx = { dbId: 'workspace:' + DM.workspaceId, schema: first.schema, table: first.table };
                }
            }
            pending.forEach(function (att) {
                if (att.localUrl && window.URL && URL.revokeObjectURL) URL.revokeObjectURL(att.localUrl);
            });
            DM.attachments = [];
            dmRenderAttachStrip();
            await dmLoadChats();
            window.dmLoadCatalog(false);
            dmUpdateHeader();
            await dmLoadMessages(true);
            if (data.message && data.message.content) {
                var shown = DM.lastMessages || [];
                var hasReply = shown.some(function (m) { return m.role !== 'user' && m.content === data.message.content; });
                if (!hasReply) {
                    dmRemoveTyping();
                    window.dmRenderMessages(shown.concat([data.message]));
                }
            }
            if (data.result) {
                window.dmRenderResult(data.result);
            } else if (data.error) {
                dmToast(data.error, 'err');
            }
            dmRenderTree();
        } catch (err) {
            dmRemoveTyping();
            if (err.status === 404 && /workspace not found/i.test(err.message || '')) {
                DM.workspaceId = '';
                DM.lastMessages = [];
                DM.tableCtx = null;
                try {
                    localStorage.removeItem(dmUserKey('dm_active_ws'));
                    localStorage.removeItem('dm_active_ws_nanopro');
                    localStorage.removeItem('dm_active_ws');
                } catch (ignore) { /* private mode */ }
                dmToast('This chat no longer exists on the server because the backend restarted. Please start a new chat.', 'err');
                await dmLoadChats();
                window.dmRenderMessages([]);
                dmUpdateHeader();
                dmRenderTree();
                return;
            }
            if (err.timeout || err.status === 502 || err.status === 503 || err.status === 504 || err.status === 524) {
                dmToast('Gateway is slow - checking the backend for your reply…', 'ok');
                var recovered = await dmRecoverLateReply(baselineAi, workspaceId);
                if (recovered) {
                    await dmLoadChats();
                    dmUpdateHeader();
                    dmRenderTree();
                    return;
                }
            }
            dmToast(err.message, 'err');
            var box = $('dmMessages');
            if (box && !box.querySelector('.dm-msg.ai')) {
                var persisted = await dmLoadMessages(true);
                if (!persisted || !persisted.length) window.dmRenderMessages([]);
            }
        } finally {
            DM.sending = false;
            if (sendBtn) sendBtn.disabled = false;
        }
    };

    async function dmReplayRun(runId) {
        try {
            var data = await dmApi('/runs/' + encodeURIComponent(runId));
            var run = data.run || {};
            window.dmShowResultPanel('Saved result', 'Replayed from this chat history.', {
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
            var area = document.createElement('textarea');
            area.value = text;
            document.body.appendChild(area);
            area.select();
            try { document.execCommand('copy'); dmToast('SQL copied', 'ok'); }
            catch (e) { dmToast('Copy failed', 'err'); }
            area.remove();
        }
    }

    function dmMessagesClick(ev) {
        var runBtn = ev.target.closest('[data-run]');
        if (runBtn) { dmReplayRun(runBtn.getAttribute('data-run')); return; }
        var copyBtn = ev.target.closest('[data-copy]');
        if (copyBtn) dmCopyText(copyBtn.getAttribute('data-copy'));
    }

    // --------------------------------------------------------------- upload

    window.dmUploadOpen = async function () {
        if (!DM.workspaceId) {
            var created = await window.dmNewChat(DM.projectId || '');
            if (!created) { dmToast('Create a chat first.', 'err'); return; }
        }
        var modal = $('dmUploadModal');
        var select = $('dmUpSchema');
        var ws = await dmEnsureSchemas();
        var schemas = (ws && ws.schemas && ws.schemas.length) ? ws.schemas : [{ name: 'main', tables: [] }];
        if (select) {
            select.innerHTML = schemas.map(function (schema) {
                return '<option value="' + dmAttr(schema.name) + '">' + dmEsc(schema.name) + '</option>';
            }).join('');
        }
        if ($('dmUpTable')) $('dmUpTable').value = '';
        if ($('dmUpFile')) $('dmUpFile').value = '';
        if (modal) modal.classList.add('open');
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
        if (btn) { btn.disabled = true; btn.textContent = 'Importing...'; }
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
            await dmLoadChats();
            window.dmLoadCatalog(false);
            dmRenderTree();
            window.dmShowResultPanel('Import complete',
                'Table ' + data.schema + '.' + data.table + ' now holds ' + data.total_rows + ' row(s). ' +
                data.rows_inserted + ' row(s) were added from ' + file.name + '.',
                { columns: (data.columns || []).map(function (c) { return c.name; }), rows: [], row_count: 0,
                  table_target: { kind: 'table', dbId: 'workspace:' + DM.workspaceId, schema: data.schema, table: data.table } });
            var input = $('dmInput');
            if (input && !input.value) {
                input.value = 'Show me the first 10 rows of ' + data.table + ' and summarise what this data contains.';
                dmAutoGrow(input);
            }
        } catch (err) {
            dmToast(err.message, 'err');
        } finally {
            if (btn) { btn.disabled = false; btn.textContent = 'Import data'; }
        }
    };

    // --------------------------------------------------------------- schema

    window.dmNewSchema = async function () {
        if (!DM.workspaceId) {
            var created = await window.dmNewChat(DM.projectId || '');
            if (!created) return;
        }
        var modal = $('dmSchemaModal');
        if ($('dmSchemaName')) $('dmSchemaName').value = '';
        if (modal) modal.classList.add('open');
        setTimeout(function () { var el = $('dmSchemaName'); if (el) el.focus(); }, 40);
    };

    window.dmCloseSchema = function () {
        var modal = $('dmSchemaModal');
        if (modal) modal.classList.remove('open');
    };

    window.dmSubmitSchema = async function () {
        var input = $('dmSchemaName');
        var name = input ? input.value.trim() : '';
        if (!name) { dmToast('Enter a schema name.', 'err'); return; }
        try {
            var data = await dmApi('/workspaces/' + encodeURIComponent(DM.workspaceId) + '/schemas', {
                method: 'POST',
                body: JSON.stringify({ name: name })
            });
            window.dmCloseSchema();
            dmToast('Schema ' + name + ' created', 'ok');
            await dmLoadChats();
            var ws = dmActiveWorkspace();
            if (ws && data.workspace && data.workspace.schemas) ws.schemas = data.workspace.schemas;
            window.dmLoadCatalog(false);
            dmRenderTree();
        } catch (err) {
            dmToast(err.message, 'err');
        }
    };

    // ------------------------------------------------------------ snowflake

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
        } catch (err) { /* best effort */ }
    };

    window.dmSetupSnowflake = async function () {
        var btn = $('dmSfBtn');
        if (!btn || btn.disabled) return;
        btn.disabled = true;
        dmToast('Creating the warehouse, schemas and empty tables...', '');
        try {
            var data = await dmApi('/snowflake/setup', { method: 'POST' });
            DM.treeOpen['db:connection:NANO_PRO_SNOWFLAKE'] = true;
            DM.treeOpen['sc:connection:NANO_PRO_SNOWFLAKE::' + data.database + '.' + data.sales_schema] = true;
            dmSaveJson('dm_tree_open', DM.treeOpen);
            await window.dmLoadCatalog(true);
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
        }
    };

    window.dmOpenSfPassword = function () {
        var modal = $('dmSfModal');
        if (!modal) return;
        if ($('dmSfPassword')) $('dmSfPassword').value = '';
        modal.classList.add('open');
        setTimeout(function () { var el = $('dmSfPassword'); if (el) el.focus(); }, 40);
    };

    window.dmCloseSfModal = function () {
        var modal = $('dmSfModal');
        if (modal) modal.classList.remove('open');
    };

    window.dmSubmitSfPassword = async function () {
        var input = $('dmSfPassword');
        var password = input ? input.value.trim() : '';
        if (!password) { dmToast('Enter the Snowflake password.', 'err'); return; }
        var btn = $('dmSfSave');
        if (btn) { btn.disabled = true; btn.textContent = 'Saving...'; }
        try {
            await dmApi('/snowflake/credentials', { method: 'POST', body: JSON.stringify({ password: password }) });
            if (input) input.value = '';
            window.dmCloseSfModal();
            dmToast('Snowflake password saved', 'ok');
            await window.dmSetupSnowflake();
        } catch (err) {
            dmToast(err.message, 'err');
        } finally {
            if (btn) { btn.disabled = false; btn.textContent = 'Save & set up'; }
        }
    };

    // ----------------------------------------------------------------- boot

    async function dmLoadStatus() {
        var badge = $('dmAiBadge');
        try {
            var data = await dmApi('/status');
            if (!badge) return;
            if (data && (data.ai_ready || data.status === 'success')) {
                badge.textContent = 'AI ready \u00b7 ' + (data.model || 'gemini-3.5-flash-lite');
                badge.className = 'dm-ai-badge live';
            } else if (data && data.status === 'STANDBY_ACTIVE') {
                badge.textContent = 'Cloud Sentinel Active';
                badge.className = 'dm-ai-badge live';
            } else {
                badge.textContent = 'Catalog mode \u00b7 AI key missing';
                badge.className = 'dm-ai-badge catalog';
            }
        } catch (err) {
            if (badge) { badge.textContent = 'Catalog mode'; badge.className = 'dm-ai-badge catalog'; }
        }
    }

    function dmBind() {
        if (DM.bound) return;
        DM.bound = true;

        var chatsScroll = $('dmChatsScroll');
        if (chatsScroll) {
            chatsScroll.addEventListener('click', function (ev) {
                var chatAct = ev.target.closest('[data-cact]');
                if (chatAct) {
                    ev.stopPropagation();
                    var chatId = chatAct.getAttribute('data-id');
                    if (chatAct.getAttribute('data-cact') === 'pin') window.dmTogglePin(chatId);
                    else {
                        var rect = chatAct.getBoundingClientRect();
                        window.dmChatMenu(chatId, rect.right - 10, rect.bottom + 4);
                    }
                    return;
                }
                var projAct = ev.target.closest('[data-pact]');
                if (projAct) {
                    ev.stopPropagation();
                    var projectId = projAct.getAttribute('data-id');
                    if (projAct.getAttribute('data-pact') === 'new') window.dmNewChat(projectId);
                    else {
                        var prect = projAct.getBoundingClientRect();
                        window.dmProjectMenu(projectId, prect.right - 10, prect.bottom + 4);
                    }
                    return;
                }
                var projRow = ev.target.closest('[data-proj]');
                if (projRow) { window.dmToggleProject(projRow.getAttribute('data-proj')); return; }
                var chatRow = ev.target.closest('[data-chat]');
                if (chatRow) window.dmSelectChat(chatRow.getAttribute('data-chat'));
            });
            chatsScroll.addEventListener('contextmenu', function (ev) {
                var chatRow = ev.target.closest('[data-chat]');
                if (chatRow) {
                    ev.preventDefault();
                    window.dmChatMenu(chatRow.getAttribute('data-chat'), ev.clientX, ev.clientY);
                    return;
                }
                var projRow = ev.target.closest('[data-proj]');
                if (projRow) {
                    ev.preventDefault();
                    window.dmProjectMenu(projRow.getAttribute('data-proj'), ev.clientX, ev.clientY);
                }
            });
            chatsScroll.addEventListener('keydown', function (ev) {
                if (ev.key !== 'Enter' && ev.key !== ' ') return;
                var row = ev.target.closest('[data-chat],[data-proj]');
                if (!row || ev.target.tagName === 'BUTTON') return;
                ev.preventDefault();
                row.click();
            });
        }

        var tree = $('dmDatabaseTree');
        if (tree) {
            tree.addEventListener('click', dmTreeClick);
            tree.addEventListener('dblclick', dmTreeDblClick);
            tree.addEventListener('keydown', function (ev) {
                if (ev.key !== 'Enter' && ev.key !== ' ') return;
                var el = ev.target.closest('[data-act]');
                if (!el || el.tagName === 'BUTTON') return;
                ev.preventDefault();
                el.click();
            });
        }

        var filter = $('dmCatalogFilter');
        if (filter) {
            filter.addEventListener('input', function () { window.dmRenderTree(); });
            filter.addEventListener('keydown', function (ev) {
                if (ev.key === 'Escape') { filter.value = ''; window.dmRenderTree(); }
            });
        }

        var messages = $('dmMessages');
        if (messages) messages.addEventListener('click', dmMessagesClick);

        var input = $('dmInput');
        if (input) {
            input.addEventListener('input', function () {
                dmAutoGrow(input);
                dmSaveDraft();
            });
            input.addEventListener('keydown', function (ev) {
                if (ev.key === 'Enter' && !ev.shiftKey && !ev.isComposing) {
                    ev.preventDefault();
                    window.dmSendMessage();
                }
            });
        }

        var menu = $('dmMenu');
        if (menu) {
            menu.addEventListener('click', function (ev) {
                var btn = ev.target.closest('[data-mi]');
                if (!btn) return;
                var item = (DM.menuItems || [])[Number(btn.getAttribute('data-mi'))];
                dmHideMenu();
                if (item && item.run) item.run();
            });
        }
        document.addEventListener('click', function (ev) {
            if (!ev.target.closest('#dmMenu')) dmHideMenu();
        });
        document.addEventListener('scroll', dmHideMenu, true);

        var nameInput = $('dmNameInput');
        if (nameInput) nameInput.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter') { ev.preventDefault(); window.dmNameSubmit(); }
        });
        var schemaInput = $('dmSchemaName');
        if (schemaInput) schemaInput.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter') { ev.preventDefault(); window.dmSubmitSchema(); }
        });
        var sfInput = $('dmSfPassword');
        if (sfInput) sfInput.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter') { ev.preventDefault(); window.dmSubmitSfPassword(); }
        });

        ['dmNameModal', 'dmUploadModal', 'dmSchemaModal', 'dmSfModal'].forEach(function (id) {
            var modal = $(id);
            if (!modal) return;
            modal.addEventListener('click', function (ev) {
                if (ev.target !== modal) return;
                if (id === 'dmNameModal') window.dmNameClose();
                if (id === 'dmUploadModal') window.dmUploadClose();
                if (id === 'dmSchemaModal') window.dmCloseSchema();
                if (id === 'dmSfModal') window.dmCloseSfModal();
            });
        });

        document.addEventListener('keydown', function (ev) {
            if (ev.key !== 'Escape') return;
            window.dmNameClose();
            window.dmUploadClose();
            window.dmCloseSchema();
            window.dmCloseSfModal();
            dmHideMenu();
        });

        dmInitGripV('dmChatsGrip', 'dmChatsPanel', 'dm_chats_w', 220, 400);
        dmInitGripV('dmExplorerGrip', 'dmExplorer', 'dm_explorer_w', 220, 420);
        dmInitGripH();

        var resizeTimer = null;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(dmFit, 120);
        });
    }

    window.initDataModeling = function () {
        if (!$('dmShell')) return;
        if (DM.inited) {
            dmFit();
            dmApplyPanels();
            dmApplyData();
            Promise.all([
                window.dmLoadProjects(),
                window.dmLoadChats(),
                dmApi('/active_state').catch(function () { return {}; })
            ]).then(function (results) {
                var activeState = (results && results[2]) ? results[2] : {};
                if (activeState && activeState.active_workspace_id && dmFindWorkspace(activeState.active_workspace_id)) {
                    DM.workspaceId = activeState.active_workspace_id;
                } else {
                    dmPickActiveChat();
                }
                dmRenderChats();
                dmUpdateHeader();
                window.dmRenderTree();
                return window.dmLoadMessages().then(dmRestoreDraft);
            }).catch(function () {});
            return;
        }
        DM.inited = true;
        if (window.innerWidth <= 1180) {
            DM.chatsOpen = false;
            DM.explorerOpen = false;
        }
        dmBind();
        dmApplyPanels();
        dmApplyData();
        dmFit();

        DM.catalog = dmCachedCatalog();
        window.dmRenderTree();
        dmRenderChats();
        window.dmRenderMessages([]);
        dmUpdateHeader();
        window.dmEmptyData();

        dmLoadStatus();
        window.dmLoadSfStatus();
        dmLoadCatalog(false);

        Promise.all([
            window.dmLoadProjects(),
            window.dmLoadChats(),
            dmApi('/active_state').catch(function () { return {}; })
        ]).then(async function (results) {
            var activeState = (results && results[2]) ? results[2] : {};
            if (activeState && activeState.active_workspace_id && dmFindWorkspace(activeState.active_workspace_id)) {
                DM.workspaceId = activeState.active_workspace_id;
            } else {
                dmPickActiveChat();
            }
            if (!DM.workspaceId && (!DM.workspaces || DM.workspaces.length === 0)) {
                await window.dmNewChat('');
            } else {
                dmRenderChats();
                dmUpdateHeader();
                window.dmRenderTree();
                await window.dmLoadMessages();
                dmRestoreDraft();
            }
        }).catch(function (err) {
            console.warn('initDataModeling startup err:', err);
        });
    };

    // Auto-boot whenever the view is active or becomes visible
    function dmCheckAndBoot() {
        var view = $('view-data_modeling_ai');
        if (view && (view.classList.contains('active') || view.style.display === 'flex' || (window.getComputedStyle && window.getComputedStyle(view).display !== 'none'))) {
            if (!DM.inited) window.initDataModeling();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', dmCheckAndBoot);
    } else {
        setTimeout(dmCheckAndBoot, 50);
    }

    try {
        var _viewEl = $('view-data_modeling_ai');
        if (_viewEl && window.MutationObserver) {
            var _mo = new MutationObserver(function (mutations) {
                for (var i = 0; i < mutations.length; i++) {
                    if (mutations[i].attributeName === 'class' && _viewEl.classList.contains('active')) {
                        if (!DM.inited) window.initDataModeling();
                        break;
                    }
                }
            });
            _mo.observe(_viewEl, { attributes: true, attributeFilter: ['class'] });
        }
    } catch (_) {}

    var _shell = $('dmShell');
    if (_shell) {
        _shell.addEventListener('click', function () {
            if (!DM.inited) window.initDataModeling();
        }, { passive: true });
    }
})();
</script>
'''
