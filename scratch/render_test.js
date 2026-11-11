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


const samples = {
  news: {status:"success", total:22, articles:[
    {title:"&#039;जानवर को इंसान बनाना&#039;, दारोगा ने व्यापारी को पीटा"},
    {title:"आणखी एक बातमी"}]},
  ledger: {status:"success", ledger:[
    {channel:"whatsapp", recipient:"+91843…", subject:"WhatsApp Notification", status:"queued", formatted_time:"10:26"},
    {channel:"email", recipient:"m@x.com", subject:"Daily report", status:"sent", formatted_time:"09:10"}]},
  plans: {status:"success", currency:"INR", plans:[
    {name:"Ai Awaaz Starter", total_display:"₹299.00", monthly_minutes:100},
    {name:"Growth", total_display:"₹999.00"}]},
  tasks: {status:"success", tasks: Array.from({length:11}, (_,i) => ({task_name:"T"+(i+1), status:"Ready"}))}
};
for (const k of Object.keys(samples)) {
  const html = renderPayload(samples[k]);
  const text = html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  console.log(k, "=>", text.slice(0, 220));
}
if (renderPayload(samples.news).includes("&#039;")) { console.log("FAIL: entity leaked"); process.exit(1); }
console.log("RENDER_OK");
