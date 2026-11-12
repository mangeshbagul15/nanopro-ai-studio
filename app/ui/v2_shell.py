"""NanoPro OS v2 shell: one screen, ten modules, live telemetry.

The legacy dashboard stays reachable at /legacy. This module intentionally
keeps the DOM, CSS and JS self-contained so the new front end has no build
step and no external dependencies.
"""


def get_v2_html(user_name: str = "") -> str:
    safe_name = (user_name or "Operator").replace("<", "").replace(">", "")[:32]
    return _SHELL.replace("__USER_NAME__", safe_name)


_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>NanoPro OS</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%230B1120'/%3E%3Cpath d='M16 46 L32 16 L48 46 L38 46 L32 30 L26 46 Z' fill='%2338BDF8'/%3E%3C/svg%3E" />
<style>
:root{
  --bg:#04060c; --panel:rgba(12,18,32,.72); --line:rgba(94,234,212,.16);
  --ink:#e6f1ff; --dim:#7c8ba3; --cyan:#22d3ee; --violet:#a78bfa; --lime:#a3e635;
  --amber:#fbbf24; --red:#fb7185;
}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:var(--bg);color:var(--ink);
  font:14px/1.45 "Inter","Segoe UI",system-ui,sans-serif}
body:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(60% 45% at 12% 0%,rgba(34,211,238,.14),transparent 60%),
    radial-gradient(55% 45% at 92% 8%,rgba(167,139,250,.14),transparent 62%),
    radial-gradient(70% 60% at 50% 110%,rgba(163,230,53,.07),transparent 60%);}
body:after{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.35;
  background:repeating-linear-gradient(0deg,rgba(255,255,255,.028) 0 1px,transparent 1px 4px);}
.wrap{position:relative;z-index:1;max-width:1180px;margin:0 auto;padding:18px 18px 40px}
header{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:.16em;font-size:13px}
.dot{width:10px;height:10px;border-radius:50%;background:var(--cyan);
  box-shadow:0 0 12px var(--cyan),0 0 30px rgba(34,211,238,.6);animation:pulse 2.4s infinite}
@keyframes pulse{50%{opacity:.45}}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-left:auto}
.chip{display:flex;gap:8px;align-items:center;padding:6px 11px;border-radius:999px;
  border:1px solid var(--line);background:rgba(10,16,28,.7);font-size:11.5px;color:var(--dim)}
.chip b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
.chip i{width:7px;height:7px;border-radius:50%;background:var(--dim);display:block}
.chip.ok i{background:var(--lime);box-shadow:0 0 10px var(--lime)}
.chip.warn i{background:var(--amber);box-shadow:0 0 10px var(--amber)}
.chip.bad i{background:var(--red);box-shadow:0 0 10px var(--red)}
h1{font-size:20px;font-weight:600;margin:22px 0 2px;letter-spacing:.01em}
h1 span{color:var(--dim);font-weight:400}
.ask{display:flex;gap:8px;margin-top:14px}
.ask input{flex:1;min-width:0;background:rgba(10,16,28,.7);border:1px solid var(--line);
  border-radius:12px;color:var(--ink);padding:11px 14px;font:inherit;outline:none}
.ask input:focus{border-color:var(--cyan);box-shadow:0 0 0 3px rgba(34,211,238,.12)}
.ask button{border:1px solid var(--line);background:rgba(34,211,238,.12);color:var(--ink);
  border-radius:12px;padding:0 16px;cursor:pointer;font:inherit}
.ask button:hover{border-color:var(--cyan)}
.tower-hdr{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin:22px 0 6px}
.tower-hdr h1{margin:0;font-size:20px;font-weight:600;letter-spacing:.01em}
.tower-hdr h1 span{color:var(--dim);font-weight:400}
.user-action-bar{display:flex;align-items:center;gap:8px}
.btn-user-action{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:8px;font-size:11.5px;font-weight:700;cursor:pointer;transition:all .15s ease;border:1px solid var(--line);background:rgba(15,23,42,.8);color:#94a3b8}
.btn-user-action:hover{color:#f8fafc;border-color:var(--cyan);background:rgba(34,211,238,.12);transform:translateY(-1px)}
.btn-switch{color:#38bdf8;border-color:rgba(56,189,248,.3)}
.btn-switch:hover{border-color:#38bdf8;background:rgba(56,189,248,.18)}
.btn-logout{color:#f87171;border-color:rgba(248,113,113,.3)}
.btn-logout:hover{color:#fca5a5;border-color:#ef4444;background:rgba(239,68,68,.18)}
.ans{font-size:13px;line-height:1.6;padding:2px 0 12px;color:#e2e8f0;word-break:break-word}
.ans table{width:100%;border-collapse:collapse;margin:12px 0;font-size:12px;background:rgba(15,23,42,.6);border-radius:8px;overflow:hidden}
.ans th,.ans td{padding:8px 12px;border:1px solid rgba(148,163,184,.15);text-align:left}
.ans th{background:rgba(30,41,59,.8);color:#38bdf8;font-weight:700}
.ans tr:nth-child(even){background:rgba(15,23,42,.35)}
.ans pre{background:#0b1120;border:1px solid #1e293b;border-radius:8px;padding:12px;overflow-x:auto;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;margin:12px 0;color:#38bdf8}
.ans code{background:rgba(56,189,248,.1);color:#38bdf8;padding:2px 6px;border-radius:4px;font-size:11.5px;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.ans pre code{background:transparent;padding:0;color:#e2e8f0}
.ans ul,.ans ol{padding-left:20px;margin:8px 0}
.ans li{margin:4px 0}
.ans h2,.ans h3,.ans h4{color:#f8fafc;margin:14px 0 6px}
.ans blockquote{border-left:3px solid #38bdf8;padding-left:12px;color:#94a3b8;margin:8px 0}
.ans strong{color:#f8fafc}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(196px,1fr));gap:12px;margin-top:16px}
.card{position:relative;text-align:left;padding:15px 15px 13px;border-radius:16px;cursor:pointer;
  border:1px solid var(--line);background:var(--panel);backdrop-filter:blur(10px);
  transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease;color:inherit;font:inherit}
.card:hover{transform:translateY(-2px);border-color:rgba(34,211,238,.45);
  box-shadow:0 10px 34px rgba(34,211,238,.10)}
.card:focus-visible{outline:2px solid var(--cyan);outline-offset:2px}
.card .gl{font-size:20px;line-height:1;filter:drop-shadow(0 0 10px rgba(34,211,238,.5))}
.card h2{font-size:13.5px;font-weight:600;margin:10px 0 3px;letter-spacing:.01em}
.card p{margin:0;color:var(--dim);font-size:11.5px}
.card .val{font-size:19px;font-weight:650;margin-top:10px;font-variant-numeric:tabular-nums}
.card .val small{font-size:11px;color:var(--dim);font-weight:500;margin-left:4px}
.card:nth-child(3n+2){border-color:rgba(167,139,250,.18)}
.card:nth-child(3n+2):hover{border-color:rgba(167,139,250,.5);box-shadow:0 10px 34px rgba(167,139,250,.10)}
footer{margin-top:26px;display:flex;gap:16px;flex-wrap:wrap;align-items:center;
  font-size:11.5px;color:var(--dim);border-top:1px solid rgba(255,255,255,.06);padding-top:14px}
footer a{color:var(--dim);text-decoration:none;border-bottom:1px dotted rgba(255,255,255,.2)}
footer a:hover{color:var(--ink)}
#station{position:fixed;inset:0;z-index:7;display:flex;flex-direction:column;overflow:hidden;
  background:rgba(4,6,12,.965);backdrop-filter:blur(18px);
  transform:translateY(100%);transition:transform .3s cubic-bezier(.22,.61,.36,1)}
#station.open{transform:none}
.sbar{display:flex;align-items:center;gap:14px;padding:14px 18px;
  border-bottom:1px solid rgba(34,211,238,.18)}
.xbtn{background:none;border:1px solid var(--line);color:var(--ink);border-radius:10px;
  padding:6px 12px;cursor:pointer;font:inherit}
.xbtn:hover{border-color:rgba(34,211,238,.5)}
.sbar .total{font-size:24px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1}
.meta{color:var(--dim);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase}
.sbody{flex:1;display:grid;grid-template-columns:250px 1fr;gap:14px;padding:14px 18px;overflow:hidden}
.glist{overflow:auto;border:1px solid var(--line);border-radius:14px;background:var(--panel);padding:6px}
.gitem{display:flex;align-items:center;gap:8px;width:100%;padding:7px 9px;border-radius:9px;
  background:none;border:0;color:inherit;font:inherit;cursor:pointer;text-align:left;font-size:12px}
.gitem:hover{background:rgba(34,211,238,.08)}
.gitem.on{background:rgba(34,211,238,.14)}
.gitem b{margin-left:auto;font-variant-numeric:tabular-nums;font-weight:600}
.gitem small{color:var(--dim);font-size:10px}
.smain{display:flex;flex-direction:column;gap:12px;min-width:0;min-height:0}
#orbits{width:100%;height:220px;flex:0 0 auto;border:1px solid var(--line);border-radius:14px;
  background:radial-gradient(60% 80% at 50% 50%,rgba(34,211,238,.07),transparent 72%)}
.search{display:flex;gap:8px}
.search input{flex:1;background:rgba(10,16,28,.7);border:1px solid var(--line);border-radius:10px;
  color:var(--ink);padding:9px 12px;font:inherit;outline:none;min-width:0}
.search input:focus{border-color:var(--cyan)}
.roster{overflow:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(184px,1fr));
  gap:8px;align-content:start;padding-bottom:16px}
.agent{padding:9px 11px;border:1px solid rgba(255,255,255,.07);border-radius:11px;
  background:rgba(10,16,28,.6);font-size:11.5px;min-width:0}
.agent .an{display:block;font-weight:600;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.agent .ag{color:var(--dim);font-size:10.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block}
.agent .st{float:right;font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim)}
.agent .st.run{color:var(--lime)}
.more{grid-column:1/-1;padding:9px;border:1px dashed var(--line);border-radius:10px;
  background:none;color:var(--dim);cursor:pointer;font:inherit}
.more:hover{color:var(--ink)}
@media(max-width:760px){
  .sbody{grid-template-columns:1fr;overflow:auto}
  .glist{max-height:150px}
  #orbits{height:165px}
}
#drawer{position:fixed;z-index:5;inset:auto 0 0 0;max-height:72vh;overflow:auto;
  transform:translateY(102%);transition:transform .24s cubic-bezier(.22,.61,.36,1);
  background:rgba(6,10,18,.96);border-top:1px solid rgba(34,211,238,.35);
  backdrop-filter:blur(18px);box-shadow:0 -18px 60px rgba(0,0,0,.6)}
#drawer.open{transform:none}
.dhead{display:flex;align-items:center;gap:12px;padding:14px 18px;position:sticky;top:0;
  background:rgba(6,10,18,.98);border-bottom:1px solid rgba(255,255,255,.06)}
.dhead h3{margin:0;font-size:14px;font-weight:600}
.dhead button{margin-left:auto;background:none;border:1px solid var(--line);color:var(--ink);
  border-radius:9px;padding:5px 12px;cursor:pointer;font:inherit}
.dbody{padding:12px 18px 26px}
.row{display:flex;gap:12px;align-items:baseline;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05)}
.row span:first-child{color:var(--dim);min-width:130px;font-size:12px;text-transform:capitalize}
.row span:last-child{margin-left:auto;text-align:right;font-variant-numeric:tabular-nums;font-size:12.5px}
.mut{color:var(--dim);font-size:12px}
.open-link{display:inline-block;margin-top:14px;color:var(--cyan);text-decoration:none;font-size:12.5px}
@media(max-width:520px){h1{font-size:17px}.chips{width:100%;margin-left:0}}

.task-card{background:rgba(15,23,42,.7);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:14px;margin-bottom:12px;transition:all .2s}
.task-card:hover{border-color:rgba(34,211,238,.35);background:rgba(15,23,42,.9)}
.task-card-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.task-name{font-size:13.5px;font-weight:700;color:var(--ink);letter-spacing:.02em}
.task-lineage{font-size:11.5px;color:var(--cyan);margin-bottom:8px;font-family:monospace}
.task-meta{display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:11.5px;color:var(--dim);background:rgba(0,0,0,.25);padding:8px 10px;border-radius:8px;margin-bottom:10px}
.task-actions{display:flex;gap:8px;flex-wrap:wrap}
.task-btn{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:var(--ink);padding:5px 12px;border-radius:6px;font-size:11px;cursor:pointer;font-family:inherit;transition:all .15s}
.task-btn:hover{background:rgba(34,211,238,.18);border-color:var(--cyan);color:#fff}
.task-btn.run{background:rgba(34,197,94,.15);border-color:rgba(34,197,94,.3);color:#4ade80}
.task-btn.run:hover{background:rgba(34,197,94,.3);border-color:#4ade80}
.task-btn.danger{background:rgba(239,68,68,.15);border-color:rgba(239,68,68,.3);color:#f87171}
.task-btn.danger:hover{background:rgba(239,68,68,.3);border-color:#f87171}
@media(max-width:600px){.task-meta{grid-template-columns:1fr}}

</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="brand"><span class="dot"></span>NANOPRO OS</div>
  <div class="chips" id="chips">
    <div class="chip" id="c-core"><i></i>CORE <b>—</b></div>
    <div class="chip" id="c-egress"><i></i>EGRESS <b>—</b></div>
    <div class="chip" id="c-ai"><i></i>AI <b>—</b></div>
    <div class="chip" id="c-tasks"><i></i>TASKS <b>—</b></div>
  </div>
</header>

<div class="tower-hdr">
  <h1>Control tower <span>· __USER_NAME__</span></h1>
  <div class="user-action-bar">
    <button type="button" class="btn-user-action btn-switch" onclick="switchUser()" title="Switch user / login with different credentials">
      <span>👤</span> Switch User
    </button>
    <button type="button" class="btn-user-action btn-logout" onclick="performLogout()" title="Sign out completely">
      <span>🚪</span> Sign out
    </button>
  </div>
</div>

<form class="ask" id="ask">
  <input id="ask-input" placeholder="Ask NanoPro — status, pipelines, agents…" autocomplete="off" aria-label="Ask NanoPro" />
  <button type="submit" aria-label="Send">→</button>
</form>

<div class="grid" id="grid"></div>

<footer>
  <span id="f-ver">v2026.11</span>
  <span id="f-host">—</span>
  <a href="/legacy" style="margin-left:auto">Legacy console →</a>
</footer>
</div>

<div id="station" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Agent Station">
  <div class="sbar">
    <button id="s-back" class="xbtn" type="button" aria-label="Back">←</button>
    <div>
      <div class="meta">Holographic Station</div>
      <div class="total" id="s-total">—</div>
    </div>
    <div style="margin-left:auto;text-align:right">
      <div class="meta">Active</div>
      <div class="total" id="s-active" style="font-size:18px">—</div>
    </div>
  </div>
  <div class="sbody">
    <div class="glist" id="s-groups"></div>
    <div class="smain">
      <canvas id="orbits" aria-hidden="true"></canvas>
      <div class="search">
        <input id="s-search" placeholder="Find agent" autocomplete="off" aria-label="Find agent" />
        <button class="xbtn" id="s-clear" type="button">Clear</button>
      </div>
      <div class="roster" id="s-roster"></div>
    </div>
  </div>
</div>

<div id="drawer" role="dialog" aria-modal="false" aria-label="Module detail">
  <div class="dhead"><h3 id="d-title">—</h3><button id="d-close">Close</button></div>
  <div class="dbody" id="d-body"></div>
</div>

<script>
// Google One Tap stores g_state with raw JSON, and Cloudflare drops the whole
// Cookie header on the Render subrequest when it sees those characters — every
// authenticated card then 401s. Clear it, and carry the session token
// explicitly so live data loads through the Worker regardless.
try { document.cookie = "g_state=; Max-Age=0; path=/; SameSite=Lax"; } catch (e) {}
(function () {
  function sessionToken() {
    let t = "";
    try { t = localStorage.getItem("nanopro_session_token") || ""; } catch (e) {}
    if (!/^np_sess_/.test(t)) {
      const m = document.cookie.match(/(?:^|;\s*)nanopro_session=([^;]+)/);
      if (m) { try { t = decodeURIComponent(m[1]); } catch (e) { t = m[1]; } }
    }
    return /^np_sess_/.test(t) ? t : "";
  }
  const nativeFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    try {
      const t = sessionToken();
      if (t && typeof input === "string") {
        init = init || {};
        init.headers = new Headers(init.headers || {});
        if (!init.headers.has("X-Session-Token")) init.headers.set("X-Session-Token", t);
      }
    } catch (e) {}
    return nativeFetch(input, init);
  };
})();
function performLogout() {
  try { localStorage.removeItem("nanopro_session_token"); } catch(e) {}
  try { sessionStorage.clear(); } catch(e) {}
  document.cookie = "nanopro_session=; Max-Age=0; path=/; SameSite=Lax";
  document.cookie = "nanopro_session=; Max-Age=0; path=/; domain=" + location.hostname + "; SameSite=Lax";
  try {
    fetch("/api/auth/logout", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({session_token: sessionToken()})
    }).catch(function(){});
  } catch(e) {}
  window.location.replace("/login?logout=1&t=" + Date.now());
}

function switchUser() {
  try { localStorage.removeItem("nanopro_session_token"); } catch(e) {}
  try { sessionStorage.clear(); } catch(e) {}
  document.cookie = "nanopro_session=; Max-Age=0; path=/; SameSite=Lax";
  window.location.replace("/login?switch=1&t=" + Date.now());
}

function renderMarkdown(md) {
  if (!md) return "";
  var NL = String.fromCharCode(10);
  var s = String(md).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  var lines = s.split(NL);
  var out = [];
  var inTable = false;
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (line.charAt(0) === "|" && line.charAt(line.length - 1) === "|") {
      if (line.indexOf("---") !== -1 || line.indexOf(":--") !== -1) continue;
      if (!inTable) { inTable = true; out.push("<table>"); }
      var cells = line.split("|").slice(1, -1);
      out.push("<tr>" + cells.map(function(c) { return "<td>" + c.trim() + "</td>"; }).join("") + "</tr>");
    } else {
      if (inTable) { inTable = false; out.push("</table>"); }
      if (line.indexOf("### ") === 0) out.push("<h3>" + line.substring(4) + "</h3>");
      else if (line.indexOf("## ") === 0) out.push("<h2>" + line.substring(3) + "</h2>");
      else if (line.indexOf("# ") === 0) out.push("<h1>" + line.substring(2) + "</h1>");
      else if (line.indexOf("- ") === 0 || line.indexOf("* ") === 0) out.push("<li>" + line.substring(2) + "</li>");
      else if (line === "") out.push("<br>");
      else out.push(line);
    }
  }
  if (inTable) out.push("</table>");
  var res = out.join("<br>").replace(/<br><table/g, "<table").replace(/<\/table><br>/g, "</table>");
  res = res.replace(/\*\*([^\*]+)\*\*/g, "<strong>$1</strong>");
  res = res.replace(/`([^`]+)`/g, "<code>$1</code>");
  return res;
}

const CARDS = [
  {id:"scheduler", glyph:"⏱", name:"Task Scheduler", hint:"Crons · Airflow DAGs · Triggers", api:"/api/scheduler/tasks",
   metric:d => { const t = list(d); const on = t.filter(isTaskOn).length;
     return [on, "of " + t.length + " crons"]; }},
  {id:"pipelines", glyph:"⛓", name:"Pipelines", hint:"L0 ➔ L1 ➔ L2 Medallion", api:"/api/operations/state",
   metric:d => ["ACTIVE", "Lakehouse"]},
  {id:"datamodel", glyph:"◈", name:"Data Modeling", hint:"AI schema & SQL", api:"/api/data_modeling/status",
   metric:() => ["AI", "ready"]},
  {id:"infra", glyph:"⬡", name:"Infra & Security", hint:"Cloud · auth · guards", api:"/api/runtime/profile",
   metric:d => [d.cloud_safe_mode ? "SAFE" : "OPEN", d.environment || "cloud"]},
  {id:"databases", glyph:"▤", name:"Databases", hint:"Neon · DuckDB · BigQuery", api:"/api/database/databases",
   metric:d => [list(d).length, "sources"]},
  {id:"mcp", glyph:"🔌", name:"MCP Server", hint:"BigQuery · Supabase · Tools", api:"/mcp/manifest",
   metric:d => [d.tools_count || (d.tools && d.tools.length) || 9, "tools"]},
  {id:"agents", glyph:"✦", name:"Agent Station", hint:"Enterprise agent fleet", api:"/api/agents/list",
   station:true, metric:d => [list(d).length, "agents"]},
  {id:"comms", glyph:"✉", name:"Communication", hint:"Email · Telegram · WhatsApp", api:"/api/communication/ledger",
   metric:d => [list(d).length, "recent"]},
  {id:"video", glyph:"▶", name:"Video Studio", hint:"Universal video maker", api:"/api/video/2026_matrix_catalog",
   metric:d => [countDeep(d), "presets"]},
  {id:"payments", glyph:"₹", name:"Payments", hint:"Gateway & plans", api:"/api/payments/plans",
   metric:d => [list(d).length, "plans"]},
  {id:"monitor", glyph:"◎", name:"Monitoring", hint:"Health · egress · jobs", api:"/api/operations/state",
   metric:d => ["LIVE", (d && (d.status || d.health_status)) || "ok"]},
  {id:"render", glyph:"☁", name:"Render Cloud", hint:"Bandwidth · builds · hours", api:"/api/v2/render",
   metric:d => { const m = /([\d.]+) GB of/.exec((d && d.bandwidth) || ""); return [m ? m[1] : "—", "GB of 5"]; }},
  {id:"news", glyph:"◫", name:"Signals", hint:"Market & news feed", api:"/api/news/articles",
   metric:d => [list(d).length, "articles"]},
];
const $ = s => document.querySelector(s);
const list = d => {
  if (Array.isArray(d)) return d;
  if (d && typeof d === "object") {
    for (const k of Object.keys(d)) if (Array.isArray(d[k])) return d[k];
  }
  return [];
};
const countDeep = d => Array.isArray(d) ? d.length : (d && typeof d === "object" ? Object.keys(d).length : 0);
const isTaskOn = x => {
  if (!x) return false;
  const v = x.is_enabled !== undefined && x.is_enabled !== null ? x.is_enabled : x.enabled;
  const paused = x.is_paused === 1 || x.is_paused === true || x.is_paused === "1";
  return !paused && (v === 1 || v === true || v === "1");
};

let apiActive = 0; const apiQueue = [];
function apiSlot(){
  return new Promise(resolve => {
    if (apiActive < 4) { apiActive++; resolve(); } else apiQueue.push(resolve);
  });
}
function apiFree(){
  apiActive--;
  const next = apiQueue.shift();
  if (next) { apiActive++; next(); }
}
async function get(p){
  await apiSlot();
  try {
    for (let attempt = 0; ; attempt++) {
      const r = await fetch(p, {credentials:"same-origin", headers:{"Accept":"application/json"}});
      if (r.ok) return r.json();
      if ((r.status !== 429 && r.status !== 503) || attempt >= 1) throw new Error(r.status);
      await new Promise(done => setTimeout(done, 1500));
    }
  } finally { apiFree(); }
}

const grid = $("#grid");
CARDS.forEach(c => {
  const b = document.createElement("button");
  b.className = "card"; b.type = "button";
  b.innerHTML = '<div class="gl">' + c.glyph + '</div><h2>' + c.name + '</h2><p>' + c.hint + '</p>' +
                '<div class="val" id="v-' + c.id + '">—</div>';
  b.addEventListener("click", () => (c.station ? openStation() : openCard(c, b)));
  grid.appendChild(b);
});

function setVal(id, value, unit){
  const el = document.getElementById("v-" + id);
  if(!el) return;
  el.innerHTML = (value == null ? "—" : String(value)) + (unit ? "<small>" + unit + "</small>" : "");
}

function chip(id, cls, text){
  const el = document.getElementById(id);
  if(!el) return;
  el.className = "chip " + (cls || "");
  el.innerHTML = "<i></i>" + text;
}

function unent(v){
  return String(v)
    .replace(/&#(\d+);/g, (m, n) => String.fromCharCode(+n))
    .replace(/&(amp|quot|lt|gt|nbsp);/g, (m, n) => ({amp:"&",quot:'"',lt:"<",gt:">",nbsp:" "}[n]));
}

const KEY_LABELS = {
  bt_verdict: "Verdict", bt_mode: "Throttle mode", http_responses: "HTTP responses",
  service_initiated: "Service-initiated", service_sources: "Top source",
  websocket_responses: "WebSocket responses", private_link: "Private link",
  soft_warn_at: "Soft warning at", heavy_pause_at: "Heavy pause at", suspend_at: "Suspension at",
  instance_uptime: "Instance uptime", instance_limit: "Instance limit",
  pipeline_minutes: "Pipeline minutes", custom_domains: "Custom domains",
  latest_deploy: "Latest deploy", api_source: "Data source", checked_at: "Checked at",
  avg_per_day: "Avg per day", used_gb: "Used", by_category: "By category",
  projected_month_gb: "Projected month", day: "Day", month: "Month"
};
const prettyKey = k => {
  if (KEY_LABELS[k]) return KEY_LABELS[k];
  const s = String(k).replace(/_/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
};

function naturalSchedule(type, expr){
  if (!type) return "On-demand";
  var t = String(type).toLowerCase();
  var e = String(expr || "").trim();
  if (t === "daily") {
    var parts = e.split(":");
    var h = parseInt(parts[0], 10) || 0;
    var m = parts[1] || "00";
    var ampm = h >= 12 ? "PM" : "AM";
    var h12 = h % 12 || 12;
    return "Every day at " + (h12 < 10 ? "0" + h12 : h12) + ":" + m + " " + ampm + " IST";
  }
  if (t === "minutes") return "Every " + e + " minutes";
  if (t === "hourly") return "Every " + e + " hours";
  if (t === "cron") return "Cron expression: " + e;
  return t + " " + e;
}

function getTaskTargetLineage(name, desc){
  var n = String(name || "").toUpperCase();
  if (n.indexOf("BOD") !== -1) return "🎯 Cloud OLTP (Neon / Render Postgres) ➔ AWS S3 Lake ➔ Snowflake L0-L1-L2 ➔ Cloud Marts (91 Tables)";
  if (n.indexOf("SOD") !== -1) return "🎯 FX Card Rates, Limits & Intraday Delta ➔ Snowflake Live";
  if (n.indexOf("DAILY_T1") !== -1) return "🎯 Delta Watermark Ingestion ➔ All 9 Banking Projects";
  if (n.indexOf("EOD") !== -1) return "🎯 Trial Balance Reconciliation ➔ Email / WhatsApp / Telegram Ledger";
  if (n.indexOf("SFTP_INBOUND") !== -1) return "🎯 Cloud SFTP /inbound/ (Pipe, CSV, XLSX) ➔ Parquet Lakehouse";
  if (n.indexOf("SFTP_20DAY") !== -1) return "🎯 Storage Sentinel ➔ Purge files & S3 objects older than 20 days";
  if (n.indexOf("STORAGE_RETENTION") !== -1) return "🎯 Disk Pressure Guard ➔ Checkpoint & Vacuum SQLite Database";
  if (n.indexOf("DUCKDB_S3") !== -1) return "🎯 DuckDB Gold Marts ➔ AWS S3 Cloud Mirror (ap-southeast-2)";
  if (n.indexOf("TELEGRAM_APK") !== -1) return "🎯 Telegram APK Dispatcher (@mangesh_apk_bot)";
  if (n.indexOf("WHATSAPP") !== -1) return "🎯 Meta WhatsApp Cloud API (+918433755448)";
  if (n.indexOf("INCREMENTAL") !== -1) return "🎯 15-Minute Incremental Watermark S3 ➔ Snowflake";
  return "🎯 " + (desc || "Autonomous Enterprise Pipeline");
}

function renderSchedulerConsole(d){
  var tasks = list(d);
  var activeCount = 0;
  var pausedCount = 0;
  for (var i = 0; i < tasks.length; i++) {
    if (tasks[i].is_paused) pausedCount++;
    else if (tasks[i].is_enabled) activeCount++;
  }
  
  var html = '<div class="scheduler-wrap">';
  html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px;">';
  html += '<div>';
  html += '<div style="font-size:15px;font-weight:700;color:var(--ink);">⏱ Enterprise Task Scheduler & DAG Orchestrator</div>';
  html += '<div style="font-size:11.5px;color:var(--dim);margin-top:2px;">Apache Airflow / EventBridge Spec · 24/7 Render Cloud Live</div>';
  html += '</div>';
  html += '<div style="display:flex;gap:8px;">';
  html += '<button type="button" class="task-btn run" onclick="toggleNewTaskForm()">+ New Task</button>';
  html += '<button type="button" class="task-btn" onclick="refreshSchedulerView()">🔄 Refresh</button>';
  html += '</div>';
  html += '</div>';

  html += '<div style="display:flex;gap:12px;margin-bottom:16px;background:rgba(0,0,0,.25);padding:10px 14px;border-radius:10px;font-size:12px;flex-wrap:wrap;">';
  html += '<div>🟢 <b>' + activeCount + '</b> Active Crons</div>';
  html += '<div>⏸ <b>' + pausedCount + '</b> Paused</div>';
  html += '<div>📦 <b>' + tasks.length + '</b> Total Tasks</div>';
  html += '<div style="margin-left:auto;color:var(--cyan);">☁ Render Cloud Primary Node</div>';
  html += '</div>';

  html += '<div id="new-task-form" style="display:none;background:rgba(15,23,42,.85);border:1px solid rgba(34,211,238,.3);border-radius:12px;padding:14px;margin-bottom:16px;">';
  html += '<div style="font-weight:600;font-size:13px;margin-bottom:10px;color:var(--cyan);">Create New Automation Task</div>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;">';
  html += '<input id="nt-name" placeholder="Task Name (e.g. DAILY_BANKING_ETL)" style="background:rgba(0,0,0,.4);border:1px solid var(--line);border-radius:6px;padding:8px;color:#fff;font-size:12px;" />';
  html += '<select id="nt-type" style="background:rgba(0,0,0,.4);border:1px solid var(--line);border-radius:6px;padding:8px;color:#fff;font-size:12px;">';
  html += '<option value="daily">Daily at specific time (e.g. 06:00)</option>';
  html += '<option value="minutes">Interval in minutes (e.g. 15)</option>';
  html += '<option value="hourly">Interval in hours (e.g. 4)</option>';
  html += '<option value="cron">Standard Cron (e.g. 30 1 * * *)</option>';
  html += '</select>';
  html += '</div>';
  html += '<div style="display:grid;grid-template-columns:1fr 2fr;gap:10px;margin-bottom:10px;">';
  html += '<input id="nt-expr" placeholder="Recurrence Value (e.g. 07:30 or 15)" style="background:rgba(0,0,0,.4);border:1px solid var(--line);border-radius:6px;padding:8px;color:#fff;font-size:12px;" />';
  html += '<input id="nt-desc" placeholder="Description & Target (e.g. Extract Oracle delta to S3 & notify Telegram)" style="background:rgba(0,0,0,.4);border:1px solid var(--line);border-radius:6px;padding:8px;color:#fff;font-size:12px;" />';
  html += '</div>';
  html += '<div style="display:flex;gap:8px;">';
  html += '<button type="button" class="task-btn run" onclick="submitCreateTask()">Save & Deploy Task</button>';
  html += '<button type="button" class="task-btn" onclick="toggleNewTaskForm()">Cancel</button>';
  html += '</div>';
  html += '</div>';

  if (!tasks.length) {
    html += '<div class="mut">No scheduled tasks found in database.</div>';
  } else {
    for (var j = 0; j < tasks.length; j++) {
      var t = tasks[j];
      var isPaused = Boolean(t.is_paused);
      var isOff = !t.is_enabled;
      var badge = '<span style="background:rgba(34,197,94,.18);color:#4ade80;padding:2px 8px;border-radius:6px;font-size:10px;font-weight:600;">ACTIVE ●</span>';
      if (isOff) badge = '<span style="background:rgba(239,68,68,.18);color:#f87171;padding:2px 8px;border-radius:6px;font-size:10px;font-weight:600;">DISABLED</span>';
      else if (isPaused) badge = '<span style="background:rgba(245,158,11,.18);color:#fbbf24;padding:2px 8px;border-radius:6px;font-size:10px;font-weight:600;">PAUSED ⏸</span>';

      html += '<div class="task-card" id="tc-' + t.id + '">';
      html += '<div class="task-card-hdr">';
      html += '<div class="task-name">' + esc(t.name) + '</div>';
      html += '<div>' + badge + '</div>';
      html += '</div>';

      html += '<div class="task-lineage">' + esc(getTaskTargetLineage(t.name, t.description)) + '</div>';

      html += '<div class="task-meta">';
      html += '<div>🗓 <b>Schedule:</b> ' + esc(naturalSchedule(t.schedule_type, t.recurrence_expr)) + '</div>';
      html += '<div>⏭ <b>Next Run:</b> ' + (t.next_run_at ? esc(t.next_run_at) + ' IST' : 'Scheduled') + '</div>';
      html += '<div>⏳ <b>Last Run:</b> ' + (t.last_run_at ? esc(t.last_run_at) : 'Completed in cycle') + '</div>';
      html += '<div>📊 <b>Status:</b> ' + esc(t.last_status || t.status || 'Ready') + '</div>';
      html += '</div>';

            html += '<div class="task-actions">';
      html += '<button type="button" class="task-btn run" data-tid="' + t.id + '" data-tname="' + esc(t.name) + '" onclick="triggerTaskNow(this.dataset.tid, this.dataset.tname)" title="Execute immediately">▶ Run Now</button>';
      if (isPaused) {
        html += '<button type="button" class="task-btn" data-tid="' + t.id + '" onclick="resumeTask(this.dataset.tid)" title="Resume scheduled executions">▶ Resume</button>';
      } else {
        html += '<button type="button" class="task-btn" data-tid="' + t.id + '" onclick="pauseTask(this.dataset.tid)" title="Temporarily halt schedule">⏸ Pause</button>';
      }
      html += '<button type="button" class="task-btn" data-tid="' + t.id + '" data-tname="' + esc(t.name) + '" data-ttype="' + esc(t.schedule_type) + '" data-texpr="' + esc(t.recurrence_expr) + '" onclick="editTaskTime(this.dataset.tid, this.dataset.tname, this.dataset.ttype, this.dataset.texpr)" title="Modify execution time">✏ Change Time</button>';
      html += '<button type="button" class="task-btn danger" data-tid="' + t.id + '" data-tname="' + esc(t.name) + '" onclick="deleteTask(this.dataset.tid, this.dataset.tname)" title="Delete automation task">🗑 Delete</button>';
      html += '</div>';
      html += '</div>';
    }
  }

  html += '</div>';
  return html;
}

function toggleNewTaskForm(){
  var f = document.getElementById("new-task-form");
  if (f) f.style.display = f.style.display === "none" ? "block" : "none";
}

async function triggerTaskNow(taskId, name){
  if (!confirm("Execute task '" + name + "' immediately on Render Cloud?")) return;
  try {
    var r = await fetch("/api/scheduler/tasks/" + taskId + "/run_now", { method: "POST" });
    var d = await r.json();
    alert("Task '" + name + "' dispatched successfully! Status: " + (d.status || "Executing"));
    refreshSchedulerView();
  } catch (e) {
    alert("Trigger failed: " + e.message);
  }
}

async function pauseTask(taskId){
  try {
    await fetch("/api/scheduler/tasks/" + taskId + "/pause", { method: "POST" });
    refreshSchedulerView();
  } catch (e) {
    alert("Pause failed: " + e.message);
  }
}

async function resumeTask(taskId){
  try {
    await fetch("/api/scheduler/tasks/" + taskId + "/resume", { method: "POST" });
    refreshSchedulerView();
  } catch (e) {
    alert("Resume failed: " + e.message);
  }
}

async function editTaskTime(taskId, name, type, currExpr){
  var newVal = prompt("Enter new recurrence schedule for '" + name + "' (" + type + ") (e.g. 06:30 for daily, or 15 for minutes):", currExpr);
  if (!newVal || newVal.trim() === currExpr) return;
  try {
    var r = await fetch("/api/scheduler/tasks/" + taskId, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recurrence_expr: newVal.trim() })
    });
    if (r.ok) {
      alert("Schedule updated to: " + newVal.trim());
      refreshSchedulerView();
    } else {
      alert("Failed to update schedule (HTTP " + r.status + ")");
    }
  } catch (e) {
    alert("Update error: " + e.message);
  }
}

async function deleteTask(taskId, name){
  if (!confirm("Are you sure you want to permanently delete task '" + name + "'?")) return;
  try {
    var r = await fetch("/api/scheduler/tasks/" + taskId, { method: "DELETE" });
    if (r.ok) {
      refreshSchedulerView();
    } else {
      alert("Failed to delete task (HTTP " + r.status + ")");
    }
  } catch (e) {
    alert("Delete error: " + e.message);
  }
}

async function submitCreateTask(){
  var name = (document.getElementById("nt-name").value || "").trim();
  var type = document.getElementById("nt-type").value;
  var expr = (document.getElementById("nt-expr").value || "").trim();
  var desc = (document.getElementById("nt-desc").value || "").trim();
  if (!name || !expr) {
    alert("Please enter a Task Name and Recurrence Value.");
    return;
  }
  try {
    var r = await fetch("/api/scheduler/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        task_type: "scheduled_job",
        schedule_type: type,
        recurrence_expr: expr,
        description: desc || ("Custom " + type + " automation task"),
        timezone: "Asia/Kolkata",
        is_enabled: true
      })
    });
    if (r.ok) {
      alert("New automation task '" + name + "' created and deployed!");
      refreshSchedulerView();
    } else {
      alert("Failed to create task (HTTP " + r.status + ")");
    }
  } catch (e) {
    alert("Creation error: " + e.message);
  }
}

async function refreshSchedulerView(){
  var scCard = CARDS.find(function(c){ return c.id === "scheduler"; });
  if (scCard) {
    var d = await get(scCard.api);
    document.getElementById("d-body").innerHTML = renderSchedulerConsole(d);
  }
}

function renderPayload(d){
  const rows = [];
  const push = (k, v) => { if (v !== undefined && v !== null && typeof v !== "object") rows.push([prettyKey(k), v]); };
  const renderItems = (items, prefix) => {
    items.slice(0, 10).forEach((it, i) => {
      if (it && typeof it === "object") {
        let label = it.name || it.task_name || it.title || it.subject || it.id || (prefix + " " + (i + 1));
        if (it.channel && it.recipient) label = it.channel + " · " + (it.subject || it.recipient);
        let state = it.status || it.state || (it.enabled !== undefined ? (it.enabled ? "enabled" : "off") : "");
        if (!state && it.total_display) state = it.total_display;
        if (state && it.formatted_time) state += " · " + it.formatted_time;
        rows.push([label, state]);
      } else push(prefix + " " + (i + 1), it);
    });
    if (items.length > 10) rows.push([prefix + " total", items.length]);
  };
  if (Array.isArray(d)) renderItems(d, "item");
  else if (d && typeof d === "object") {
    Object.keys(d).slice(0, 40).forEach(k => {
      const v = d[k];
      if (Array.isArray(v)) {
        if (v.length && typeof v[0] === "object") renderItems(v, k);
        else if (v.every(x => x === null || typeof x !== "object"))
          rows.push([prettyKey(k), v.slice(0, 6).join(", ") + (v.length > 6 ? " +" + (v.length - 6) : "")]);
        else rows.push([prettyKey(k), v.length + " items"]);
      } else if (v && typeof v === "object") {
        const ks = Object.keys(v);
        if (ks.length <= 6) ks.forEach(kk => push(k + "." + kk, v[kk]));
        else rows.push([prettyKey(k), ks.length + " keys"]);
      } else push(k, v);
    });
  }
  if (!rows.length) return '<div class="mut">No data yet.</div>';
  return rows.map(([k, v]) => '<div class="row"><span>' + esc(unent(k)) + '</span><span>' + esc(unent(v)) + '</span></div>').join("");
}

function esc(v){
  if (v == null) return "";
  var s = String(v);
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

async function openCard(card){
  $("#d-title").textContent = card.name;
  $("#d-body").innerHTML = '<div class="mut">Loading…</div>';
  $("#drawer").classList.add("open");
  const link = card.id === "render"
    ? '<a class="open-link" href="https://dashboard.render.com/" target="_blank" rel="noopener">Render dashboard ↗</a>'
    : (card.id === "mcp"
       ? '<a class="open-link" href="/mcp/manifest" target="_blank" rel="noopener">Inspect MCP manifest ↗</a>'
       : '<a class="open-link" href="/legacy">Open full workspace →</a>');
  try {
    const d = await get(card.api);
    if (card.id === "scheduler") {
      $("#d-body").innerHTML = renderSchedulerConsole(d);
    } else {
      $("#d-body").innerHTML = renderPayload(d) + link;
    }
  } catch (e) {
    $("#d-body").innerHTML = '<div class="mut">Not available on this lane (' + e.message + ').</div>' + link;
  }
}

$("#d-close").addEventListener("click", () => $("#drawer").classList.remove("open"));

$("#ask-input").addEventListener("keydown", e => {
  if (e.key === "Enter") { e.preventDefault(); $("#ask").requestSubmit(); }
});

$("#ask").addEventListener("submit", async e => {
  e.preventDefault();
  const q = $("#ask-input").value.trim();
  if (!q) return;
  $("#d-title").textContent = "NanoPro";
  $("#d-body").innerHTML = '<div class="mut">Thinking…</div>';
  $("#drawer").classList.add("open");
  try {
    let r, d = {};
    for (let attempt = 0; ; attempt++) {
      r = await fetch("/api/v2/chat", {
        method: "POST", credentials: "same-origin",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: q})
      });
      d = await r.json().catch(() => ({}));
      if (r.ok || r.status !== 503 || attempt >= 1) break;
      await new Promise(done => setTimeout(done, 2000));
    }
    if (!r.ok) throw new Error((d && d.detail) || ("HTTP " + r.status));
    $("#d-title").textContent = d.intent || "NanoPro AI Copilot";
    $("#d-body").innerHTML = '<div class="ans">' + renderMarkdown(d.answer || "") + '</div>' +
      '<div class="row"><span>intent</span><span>' + esc(d.intent || "—") + '</span></div>' +
      '<div class="row"><span>model</span><span>' + esc(d.model || "rules") + '</span></div>' +
      '<div class="row"><span>latency</span><span>' + (Number(d.latency_ms) || 0) + ' ms</span></div>' +
      '<a class="open-link" href="/legacy">Open full workspace →</a>';
    $("#ask-input").value = "";
  } catch (err) {
    $("#d-body").innerHTML = '<div class="mut">' + esc(err.message || String(err)) + '</div>';
  }
});

const station = {agents:[], groups:{}, loaded:false, filter:"", q:"", shown:72, raf:0};

async function openStation(){
  $("#station").classList.add("open");
  $("#station").setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  if (!station.loaded) {
    $("#s-total").textContent = "…";
    try {
      const d = await get("/api/agents/list");
      station.agents = list(d);
      station.groups = (d && d.group_summaries) || {};
    } catch (e) { /* surface as offline */ }
    station.loaded = true;
  }
  renderStation();
  startOrbits();
}

function closeStation(){
  $("#station").classList.remove("open");
  $("#station").setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  cancelAnimationFrame(station.raf);
}

function renderStation(){
  const all = station.agents;
  const active = all.filter(x => /Running|Assigned|Retrying/.test(x.state || "")).length;
  $("#s-total").textContent = all.length ? all.length + " agents" : "offline";
  $("#s-active").textContent = active;
  const box = $("#s-groups");
  box.innerHTML = "";
  let entries = Object.entries(station.groups || {}).filter(([, v]) => v && v.count > 0);
  if (!entries.length) {
    const counts = {};
    all.forEach(x => { const g = x.group || "?"; counts[g] = (counts[g] || 0) + 1; });
    entries = Object.keys(counts).sort().map(k => [k, {name: k, count: counts[k], active: 0}]);
  }
  const allBtn = document.createElement("button");
  allBtn.className = "gitem" + (station.filter ? "" : " on");
  allBtn.type = "button";
  allBtn.innerHTML = "<span>All groups</span><b>" + all.length + "</b>";
  allBtn.onclick = () => { station.filter = ""; renderStation(); };
  box.appendChild(allBtn);
  entries.forEach(([k, v]) => {
    const b = document.createElement("button");
    b.className = "gitem" + (station.filter === k ? " on" : "");
    b.type = "button";
    b.innerHTML = "<span>" + esc(k) + " · " + esc(v.name || "") + "</span><b>" + (v.count || 0) + "</b>" +
                  (v.active ? "<small>" + v.active + " ✓</small>" : "");
    b.onclick = () => { station.filter = station.filter === k ? "" : k; renderStation(); };
    box.appendChild(b);
  });
  renderRoster();
}

function renderRoster(){
  const box = $("#s-roster");
  const q = station.q.trim().toLowerCase();
  const rows = station.agents.filter(x => {
    if (station.filter && x.group !== station.filter) return false;
    if (!q) return true;
    const hay = ((x.name || "") + " " + (x.role || "") + " " + (x.group_name || "") + " " + (x.agent_id || "")).toLowerCase();
    return hay.indexOf(q) !== -1;
  });
  const shown = rows.slice(0, station.shown);
  box.innerHTML = shown.map(x => {
    const running = /Running|Assigned|Retrying/.test(x.state || "");
    return '<div class="agent"><span class="st' + (running ? " run" : "") + '">' + esc(x.state || "Idle") + '</span>' +
      '<span class="an">' + esc(x.name || x.agent_id || "agent") + '</span>' +
      '<span class="ag">' + esc((x.group || "") + " · " + (x.role || x.group_name || "")) + '</span></div>';
  }).join("");
  if (!shown.length) box.innerHTML = '<div class="mut">No agents match.</div>';
  if (rows.length > shown.length) {
    const more = document.createElement("button");
    more.className = "more";
    more.type = "button";
    more.textContent = "Show " + Math.min(120, rows.length - shown.length) + " more";
    more.onclick = () => { station.shown += 120; renderRoster(); };
    box.appendChild(more);
  }
}

function startOrbits(){
  const cv = $("#orbits");
  if (!cv || !cv.getContext) return;
  cancelAnimationFrame(station.raf);
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ctx = cv.getContext("2d");
  const groups = [...new Set(station.agents.map(x => x.group || "?"))].sort();
  const per = {}, seen = {};
  const dots = station.agents.map(x => {
    const gi = Math.max(0, groups.indexOf(x.group || "?"));
    per[gi] = (per[gi] || 0) + 1;
    seen[gi] = (seen[gi] || 0) + 1;
    return {gi, k: seen[gi], total: 0, hue: (gi * 23 + 188) % 360};
  });
  dots.forEach(d => { d.total = per[d.gi]; });

  function frame(t){
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = cv.clientWidth, h = cv.clientHeight;
    if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
      cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const cx = w / 2, cy = h / 2;
    const maxR = Math.min(w, h) / 2 - 10;
    const base = 26, step = groups.length > 1 ? (maxR - base) / (groups.length - 1) : 0;
    ctx.lineWidth = 1;
    ctx.strokeStyle = "rgba(34,211,238,.10)";
    groups.forEach((_, gi) => {
      ctx.beginPath();
      ctx.arc(cx, cy, base + gi * step, 0, Math.PI * 2);
      ctx.stroke();
    });
    dots.forEach(d => {
      const r = base + d.gi * step;
      const a = (d.k / Math.max(1, d.total)) * Math.PI * 2 + t * (0.00012 + d.gi * 0.00001);
      ctx.beginPath();
      ctx.arc(cx + Math.cos(a) * r, cy + Math.sin(a) * r, 1.7, 0, Math.PI * 2);
      ctx.fillStyle = "hsla(" + d.hue + ",92%,66%,.9)";
      ctx.fill();
    });
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "650 22px Inter,system-ui,sans-serif";
    ctx.fillStyle = "rgba(230,241,255,.92)";
    ctx.fillText(String(station.agents.length), cx, cy - 4);
    ctx.font = "500 9px Inter,system-ui,sans-serif";
    ctx.fillStyle = "rgba(124,139,163,.9)";
    ctx.fillText("AGENTS", cx, cy + 14);
    if (!reduce) station.raf = requestAnimationFrame(frame);
  }
  station.raf = requestAnimationFrame(frame);
}

$("#s-back").addEventListener("click", closeStation);
$("#s-search").addEventListener("input", e => { station.q = e.target.value; station.shown = 72; renderRoster(); });
$("#s-clear").addEventListener("click", () => { station.q = ""; $("#s-search").value = ""; renderRoster(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeStation(); });

async function boot(){
  const [health, profile, egress, tasks] = await Promise.allSettled([
    get("/api/health"), get("/api/runtime/profile"), get("/api/runtime/egress/audit"), get("/api/scheduler/tasks"),
  ]);

  if (health.status === "fulfilled") {
    const h = health.value;
    const b = h.backend || {};
    const used = h.memory ? h.memory.used_percentage : null;
    if (used != null) chip("c-core", "ok", "CORE <b>" + used + "% RAM</b>");
    else {
      const up = h.status === "success" || h.health_status === "HEALTHY" || b.reachable === true;
      chip("c-core", up ? "ok" : "bad", "CORE <b>" + (up ? "up" : "down") +
        (up && b.latency_ms ? " " + b.latency_ms + "ms" : "") + "</b>");
    }
    const host = h.server_tier || (h.server === "cloudflare-edge" ? "cloudflare-edge" : "cloud");
    const os = (h.os_platform || "").split("-").slice(0, 2).join(" ");
    $("#f-host").textContent = host + (os ? " · " + os : (b.http_status ? " · backend " + b.http_status : ""));
  } else chip("c-core", "bad", "CORE <b>down</b>");

  if (egress.status === "fulfilled") {
    const e = egress.value;
    const cls = e.verdict === "ok" ? "ok" : (e.verdict === "watch" ? "warn" : "bad");
    chip("c-egress", cls, "EGRESS <b>" + Number(e.used_gb || 0).toFixed(2) + "/" + (e.limit_gb || 5) + " GB</b>");
  } else chip("c-egress", "warn", "EGRESS <b>—</b>");

  if (profile.status === "fulfilled") {
    const c = profile.value.concurrency || {};
    chip("c-ai", "ok", "AI <b>" + (c.ai_active ?? 0) + "/" + (c.ai_limit ?? 0) + "</b>");
    setVal("infra", profile.value.cloud_safe_mode ? "SAFE" : "OPEN", profile.value.environment || "");
  } else chip("c-ai", "warn", "AI <b>—</b>");

  if (tasks.status === "fulfilled") {
    const t = list(tasks.value);
    const on = t.filter(isTaskOn).length;
    chip("c-tasks", on ? "ok" : "warn", "TASKS <b>" + on + " on</b>");
    setVal("pipelines", on, "of " + t.length + " live");
  } else chip("c-tasks", "warn", "TASKS <b>—</b>");

  await Promise.allSettled(CARDS.slice(1).map(async c => {
    try {
      const d = await get(c.api);
      const [v, u] = c.metric(d);
      setVal(c.id, v, u);
    } catch (e) {
      setVal(c.id, "n/a", "");
    }
  }));
}
boot();
</script>
</body>
</html>
"""
