import os

path = os.path.join("deploy", "cloudflare_worker_gateway.js")
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

old_loop = """  dags.forEach(d => {
    d.finished_at = new Date().toISOString();
  });"""

new_loop = """  globalThis._EDGE_PAUSED_DAGS = globalThis._EDGE_PAUSED_DAGS || new Set();
  dags.forEach(d => {
    d.finished_at = new Date().toISOString();
    if (globalThis._EDGE_PAUSED_DAGS.has(d.id)) {
      d.paused = true;
      d.status = "PAUSED";
    }
  });"""

assert old_loop in text, "old_loop not found"
text = text.replace(old_loop, new_loop, 1)

old_pause = """      if (path.endsWith("/dag/pause")) {
        let reqBody = {};
        try { reqBody = await request.json(); } catch (_) {}
        const dagId = reqBody.dag_id || "bq_to_s3";
        return new Response(JSON.stringify({
          status: "success",
          dag_id: dagId,
          state: "PAUSED"
        }), { status: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
      }"""

new_pause = """      if (path.endsWith("/dag/pause")) {
        let reqBody = {};
        try { reqBody = await request.json(); } catch (_) {}
        const dagId = reqBody.dag_id || "bq_to_s3";
        globalThis._EDGE_PAUSED_DAGS = globalThis._EDGE_PAUSED_DAGS || new Set();
        let nextState = "PAUSED";
        if (globalThis._EDGE_PAUSED_DAGS.has(dagId)) {
          globalThis._EDGE_PAUSED_DAGS.delete(dagId);
          nextState = "RESUMED";
        } else {
          globalThis._EDGE_PAUSED_DAGS.add(dagId);
          nextState = "PAUSED";
        }
        return new Response(JSON.stringify({
          status: "success",
          dag_id: dagId,
          state: nextState
        }), { status: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
      }"""

assert old_pause in text, "old_pause not found"
text = text.replace(old_pause, new_pause, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated edge pause logic successfully!")
