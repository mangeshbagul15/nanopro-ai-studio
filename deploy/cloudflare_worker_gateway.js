/**
 * Mangesh Nano Pro AI Studio - Central Master Cloudflare Gateway Worker
 * =====================================================================
 */
const CONFIG = {
  UPSTREAMS: {
    // Live Local Laptop Master Tunnel (Active & Connected)
    LOCAL_LAPTOP: "https://forgot-delivery-thats-view.trycloudflare.com",
    
    // Cloud Tiers (100% Free / Zero Card)
    CLOUD_NORTHFLANK: "https://nanopro-studio.northflank.app",
    CLOUD_ZEABUR: "https://nanopro-studio.zeabur.app",
    CLOUD_RENDER: "https://mangesh-nanopro-studio.onrender.com",
    CLOUD_RENDER_MIRROR: "https://mangesh-nanopro-mirror.onrender.com",
    CLOUD_BACK4APP: "https://nanopro-studio.b4a.run",
    CLOUD_ALWAYSDATA: "https://nanopro.alwaysdata.net",
    CLOUD_SERV00: "https://nanopro.serv00.net"
  },
  TIMEOUT_MS: 4000
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    const localTunnel = env?.LOCAL_TUNNEL_URL || CONFIG.UPSTREAMS.LOCAL_LAPTOP;
    const northflankUrl = env?.NORTHFLANK_URL || CONFIG.UPSTREAMS.CLOUD_NORTHFLANK;
    const zeaburUrl = env?.ZEABUR_URL || CONFIG.UPSTREAMS.CLOUD_ZEABUR;
    const renderUrl = env?.RENDER_URL || CONFIG.UPSTREAMS.CLOUD_RENDER;
    const renderMirrorUrl = env?.RENDER_MIRROR_URL || CONFIG.UPSTREAMS.CLOUD_RENDER_MIRROR;
    const back4appUrl = env?.BACK4APP_URL || CONFIG.UPSTREAMS.CLOUD_BACK4APP;
    const alwaysdataUrl = env?.ALWAYSDATA_URL || CONFIG.UPSTREAMS.CLOUD_ALWAYSDATA;
    const serv00Url = env?.SERV00_URL || CONFIG.UPSTREAMS.CLOUD_SERV00;

    let candidateUpstreams = [];
    if (path.startsWith("/api/video") || path.startsWith("/api/apk") || path.startsWith("/api/ollama")) {
      candidateUpstreams = [localTunnel, northflankUrl, zeaburUrl, renderUrl, renderMirrorUrl, back4appUrl];
    } else if (path.startsWith("/api/cron") || path.startsWith("/api/monitoring") || path.startsWith("/api/telegram")) {
      candidateUpstreams = [localTunnel, northflankUrl, zeaburUrl, renderUrl, renderMirrorUrl, back4appUrl, alwaysdataUrl, serv00Url];
    } else {
      candidateUpstreams = [localTunnel, northflankUrl, zeaburUrl, renderUrl, renderMirrorUrl, back4appUrl];
    }

    let lastError = null;
    let attemptedNodes = [];

    for (const upstreamBase of candidateUpstreams) {
      if (!upstreamBase) continue;
      const targetUrl = new URL(path + url.search, upstreamBase);
      attemptedNodes.push(upstreamBase);

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT_MS);

        // Fix: Replace incoming Host header with the target upstream host to prevent Error 1016 / 530
        const newHeaders = new Headers(request.headers);
        newHeaders.delete("host");
        newHeaders.set("Host", targetUrl.host);
        newHeaders.set("X-Forwarded-Host", url.host);
        newHeaders.set("X-NanoPro-Gateway", "Cloudflare-Workers-Master");

        const response = await fetch(targetUrl.toString(), {
          method: request.method,
          headers: newHeaders,
          body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
          redirect: "follow",
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.status >= 502 && response.status <= 504) {
          lastError = `HTTP ${response.status} from ${upstreamBase}`;
          continue;
        }

        const finalHeaders = new Headers(response.headers);
        finalHeaders.set("X-NanoPro-Routed-Node", upstreamBase);
        finalHeaders.set("X-NanoPro-Failover-Attempts", attemptedNodes.length.toString());
        finalHeaders.set("Access-Control-Allow-Origin", "*");

        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: finalHeaders
        });
      } catch (err) {
        lastError = err.message || err.toString();
      }
    }

    return new Response(JSON.stringify({
      error: "ALL_CLUSTER_NODES_STANDBY",
      message: "NanoPro Gateway attempted all live cluster nodes. Data remains secure.",
      attempted_nodes: attemptedNodes,
      last_error: lastError,
      timestamp: new Date().toISOString()
    }, null, 2), {
      status: 503,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
};
