
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
const CARDS = [
  {id:"pipelines", glyph:"⛓", name:"Pipelines", hint:"BOD · SOD · T1 · EOD", api:"/api/scheduler/tasks",
   metric:d => { const t = list(d); const on = t.filter(isTaskOn).length;
     return [on, "of " + t.length + " live"]; }},
  {id:"datamodel", glyph:"◈", name:"Data Modeling", hint:"AI schema & SQL", api:"/api/data_modeling/status",
   metric:() => ["AI", "ready"]},
  {id:"infra", glyph:"⬡", name:"Infra & Security", hint:"Cloud · auth · guards", api:"/api/runtime/profile",
   metric:d => [d.cloud_safe_mode ? "SAFE" : "OPEN", d.environment || "cloud"]},
  {id:"databases", glyph:"▤", name:"Databases", hint:"Neon · DuckDB · BigQuery", api:"/api/database/databases",
   metric:d => [list(d).length, "sources"]},
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

function renderPayload(d){
  const rows = [];
  const push = (k, v) => { if (v !== undefined && v !== null && typeof v !== "object") rows.push([k, v]); };
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
    Object.keys(d).slice(0, 16).forEach(k => {
      const v = d[k];
      if (Array.isArray(v)) {
        if (v.length && typeof v[0] === "object") renderItems(v, k);
        else if (v.every(x => x === null || typeof x !== "object"))
          rows.push([k, v.slice(0, 6).join(", ") + (v.length > 6 ? " +" + (v.length - 6) : "")]);
        else rows.push([k, v.length + " items"]);
      } else if (v && typeof v === "object") {
        const ks = Object.keys(v);
        if (ks.length <= 6) ks.forEach(kk => push(k + "." + kk, v[kk]));
        else rows.push([k, ks.length + " keys"]);
      } else push(k, v);
    });
  }
  if (!rows.length) return '<div class="mut">No data yet.</div>';
  return rows.map(([k, v]) => '<div class="row"><span>' + esc(unent(k)) + '</span><span>' + esc(unent(v)) + '</span></div>').join("");
}

function esc(v){
  return String(v).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));
}

async function openCard(card){
  $("#d-title").textContent = card.name;
  $("#d-body").innerHTML = '<div class="mut">Loading…</div>';
  $("#drawer").classList.add("open");
  const link = card.id === "render"
    ? '<a class="open-link" href="https://dashboard.render.com/" target="_blank" rel="noopener">Render dashboard ↗</a>'
    : '<a class="open-link" href="/legacy">Open full workspace →</a>';
  try {
    const d = await get(card.api);
    $("#d-body").innerHTML = renderPayload(d) + link;
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
    $("#d-title").textContent = d.intent || "answer";
    $("#d-body").innerHTML = '<div class="ans">' + esc(d.answer || "") + '</div>' +
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
