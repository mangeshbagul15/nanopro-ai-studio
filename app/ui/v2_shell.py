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

<h1>Control tower <span>· __USER_NAME__</span></h1>

<div class="grid" id="grid"></div>

<footer>
  <span id="f-ver">v2026.11</span>
  <span id="f-host">—</span>
  <a href="/legacy">Legacy console</a>
  <a href="/logout" style="margin-left:auto">Sign out</a>
</footer>
</div>

<div id="drawer" role="dialog" aria-modal="false" aria-label="Module detail">
  <div class="dhead"><h3 id="d-title">—</h3><button id="d-close">Close</button></div>
  <div class="dbody" id="d-body"></div>
</div>

<script>
const CARDS = [
  {id:"pipelines", glyph:"⛓", name:"Pipelines", hint:"BOD · SOD · T1 · EOD", api:"/api/scheduler/tasks",
   metric:d => { const t = list(d); const on = t.filter(x => x.enabled === 1 || x.enabled === true || x.enabled === "1").length;
     return [on, "of " + t.length + " live"]; }},
  {id:"datamodel", glyph:"◈", name:"Data Modeling", hint:"AI schema & SQL", api:"/api/data_modeling/status",
   metric:() => ["AI", "ready"]},
  {id:"infra", glyph:"⬡", name:"Infra & Security", hint:"Cloud · auth · guards", api:"/api/runtime/profile",
   metric:d => [d.cloud_safe_mode ? "SAFE" : "OPEN", d.environment || "cloud"]},
  {id:"databases", glyph:"▤", name:"Databases", hint:"Neon · DuckDB · BigQuery", api:"/api/database/databases",
   metric:d => [list(d).length, "sources"]},
  {id:"agents", glyph:"✦", name:"Agent Station", hint:"305 enterprise agents", api:"/api/agents/list",
   metric:d => [list(d).length, "agents"]},
  {id:"comms", glyph:"✉", name:"Communication", hint:"Email · Telegram · WhatsApp", api:"/api/emails/delivery-history",
   metric:d => [list(d).length, "recent"]},
  {id:"video", glyph:"▶", name:"Video Studio", hint:"Universal video maker", api:"/api/video/2026_matrix_catalog",
   metric:d => [countDeep(d), "presets"]},
  {id:"payments", glyph:"₹", name:"Payments", hint:"Gateway & plans", api:"/api/payments/plans",
   metric:d => [list(d).length, "plans"]},
  {id:"monitor", glyph:"◎", name:"Monitoring", hint:"Health · egress · jobs", api:"/api/operations/state",
   metric:d => ["LIVE", (d && (d.status || d.health_status)) || "ok"]},
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

async function get(p){
  const r = await fetch(p, {credentials:"same-origin", headers:{"Accept":"application/json"}});
  if(!r.ok) throw new Error(r.status);
  return r.json();
}

const grid = $("#grid");
CARDS.forEach(c => {
  const b = document.createElement("button");
  b.className = "card"; b.type = "button";
  b.innerHTML = '<div class="gl">' + c.glyph + '</div><h2>' + c.name + '</h2><p>' + c.hint + '</p>' +
                '<div class="val" id="v-' + c.id + '">—</div>';
  b.addEventListener("click", () => openCard(c, b));
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

function renderPayload(d){
  const rows = [];
  const push = (k, v) => { if (v !== undefined && v !== null && typeof v !== "object") rows.push([k, v]); };
  const items = Array.isArray(d) ? d : (d && typeof d === "object" ? list(d) : []);
  items.slice(0, 10).forEach((it, i) => {
    if (it && typeof it === "object") {
      const label = it.name || it.task_name || it.title || it.id || ("item " + (i + 1));
      const state = it.status || it.state || (it.enabled !== undefined ? (it.enabled ? "enabled" : "off") : "");
      rows.push([label, state]);
    } else push("item " + (i + 1), it);
  });
  if (items.length > 10) rows.push(["more", (items.length - 10) + " hidden"]);
  if (d && typeof d === "object" && !Array.isArray(d)) {
    Object.keys(d).slice(0, 12).forEach(k => {
      const v = d[k];
      if (Array.isArray(v)) { if (v !== items) rows.push([k, v.length + " items"]); }
      else if (v && typeof v === "object") rows.push([k, Object.keys(v).length + " keys"]);
      else push(k, v);
    });
  }
  if (!rows.length) return '<div class="mut">No data yet.</div>';
  return rows.map(([k, v]) => '<div class="row"><span>' + esc(k) + '</span><span>' + esc(v) + '</span></div>').join("");
}

function esc(v){
  return String(v).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c]));
}

async function openCard(card){
  $("#d-title").textContent = card.name;
  $("#d-body").innerHTML = '<div class="mut">Loading…</div>';
  $("#drawer").classList.add("open");
  try {
    const d = await get(card.api);
    $("#d-body").innerHTML = renderPayload(d) + '<a class="open-link" href="/legacy">Open full workspace →</a>';
  } catch (e) {
    $("#d-body").innerHTML = '<div class="mut">Not available on this lane (' + e.message + ').</div>' +
      '<a class="open-link" href="/legacy">Open full workspace →</a>';
  }
}

$("#d-close").addEventListener("click", () => $("#drawer").classList.remove("open"));

async function boot(){
  const [health, profile, egress, tasks] = await Promise.allSettled([
    get("/api/health"), get("/api/runtime/profile"), get("/api/runtime/egress/audit"), get("/api/scheduler/tasks"),
  ]);

  if (health.status === "fulfilled") {
    const h = health.value;
    const used = h.memory ? h.memory.used_percentage : null;
    chip("c-core", "ok", "CORE <b>" + (used != null ? used + "% RAM" : (h.health_status || "ok")) + "</b>");
    $("#f-host").textContent = (h.server_tier || "cloud") + " · " + (h.os_platform || "").split("-").slice(0, 2).join(" ");
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
    const on = t.filter(x => x.enabled === 1 || x.enabled === true || x.enabled === "1").length;
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
