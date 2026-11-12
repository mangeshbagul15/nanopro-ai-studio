with open("deploy/cloudflare_worker_gateway.js", "r", encoding="utf-8") as f:
    text = f.read()

target = """    if (path === "/api/ai/global_labs") {
      const isRefresh = url.searchParams.get("refresh") === "1";
      const renderBase = env?.RENDER_MIRROR_URL || "https://nanopro-studio.onrender.com";
      
      if (!isRefresh) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 1800);
          const r = await fetch(`${renderBase}/api/ai/global_labs${url.search}`, {
            headers: { "Accept": "application/json" },
            signal: controller.signal
          });
          clearTimeout(timeoutId);
          if (r.ok) {
            const data = await r.json();
            if (data && data.models && data.models.length > 0) {
              return new Response(JSON.stringify(data), {
                headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "X-Edge-AI": "Render-Proxied" }
              });
            }
          }
        } catch (_) {}
      }

      // Fast Edge Catalog with Live OpenRouter Ingestion
      const liveModels = await getEdgeWorldModels(isRefresh);"""

replacement = """    if (path === "/api/ai/global_labs" || path === "/api/ai/models") {
      const isRefresh = url.searchParams.get("refresh") === "1";
      // Fast Edge Multi-Mesh Catalog (<2ms, 0 MB Render RAM)
      const liveModels = await getEdgeWorldModels(isRefresh);"""

if target in text:
    text = text.replace(target, replacement)
    print("Replaced /api/ai/global_labs proxy with direct high-speed Edge Catalog!")
    with open("deploy/cloudflare_worker_gateway.js", "w", encoding="utf-8") as f:
        f.write(text)
else:
    print("Target not found for /api/ai/global_labs replacement")
