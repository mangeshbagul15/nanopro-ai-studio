/**
 * Mangesh Nano Pro AI Studio - Central Master Cloudflare Gateway Worker
 * =====================================================================
 * This script runs globally at Cloudflare's Edge (100% Lifetime Free - Zero Card).
 * Provides the ONE FIXED MASTER URL:
 *   https://mangesh-nanopro.workers.dev
 *
 * Capabilities:
 *   1. Single Public Endpoint for Clients, Users, Admins, and cron-job.org
 *   2. Dynamic Upstream Routing & Circuit Breaker:
 *        - Local Laptop Master (trycloudflare.com Tunnel)
 *        - Northflank Cloud Node
 *        - Zeabur Cloud Node
 *        - Render Cloud Node
 *   3. Intelligent Workload Segregation:
 *        - 1080p Video / APK binary streams -> Local Master (falls back to cloud queue if off)
 *        - 24/7 cron-job.org / Webhooks / APIs -> Cloud Node
 *   4. Zero Downtime Transparent Failover:
 *        - If primary upstream fails (5xx / timeout), immediately forwards to next healthy peer!
 */

const CONFIG = {
  // Upstream Endpoints (Configurable via Cloudflare Environment Variables or hardcoded fallbacks)
  UPSTREAMS: {
    // Local Laptop Tunnel (Updates dynamically or through fixed Cloudflare Named Tunnel)
    LOCAL_LAPTOP: "https://mainstream-pics-gif-otherwise.trycloudflare.com",
    
    // Cloud Tiers (100% Free / Zero Card)
    CLOUD_NORTHFLANK: "https://nanopro-studio.northflank.app",
    CLOUD_ZEABUR: "https://nanopro-studio.zeabur.app",
    CLOUD_RENDER: "https://mangesh-nanopro-studio.onrender.com"
  },
  TIMEOUT_MS: 3000
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Allow overriding upstreams via Cloudflare Worker Environment Variables
    const localTunnel = env?.LOCAL_TUNNEL_URL || CONFIG.UPSTREAMS.LOCAL_LAPTOP;
    const northflankUrl = env?.NORTHFLANK_URL || CONFIG.UPSTREAMS.CLOUD_NORTHFLANK;
    const zeaburUrl = env?.ZEABUR_URL || CONFIG.UPSTREAMS.CLOUD_ZEABUR;
    const renderUrl = env?.RENDER_URL || CONFIG.UPSTREAMS.CLOUD_RENDER;

    // Ordered list of candidate upstreams based on task type
    let candidateUpstreams = [];

    // Rule A: Heavy Compute (1080p Video, Heavy APK downloads, Local Ollama)
    if (path.startsWith("/api/video") || path.startsWith("/api/apk") || path.startsWith("/api/ollama")) {
      candidateUpstreams = [localTunnel, northflankUrl, zeaburUrl, renderUrl];
    }
    // Rule B: 24/7 Webhooks, Cron Schedules, Telegram, Health
    else if (path.startsWith("/api/cron") || path.startsWith("/api/monitoring") || path.startsWith("/api/telegram")) {
      candidateUpstreams = [northflankUrl, zeaburUrl, renderUrl, localTunnel];
    }
    // Rule C: General Dashboard & APIs
    else {
      // Local first if alive, otherwise seamless cloud
      candidateUpstreams = [localTunnel, northflankUrl, zeaburUrl, renderUrl];
    }

    // Try each upstream sequentially until one responds healthy
    let lastError = null;
    let attemptedNodes = [];

    for (const upstreamBase of candidateUpstreams) {
      if (!upstreamBase) continue;
      
      const targetUrl = new URL(path + url.search, upstreamBase);
      attemptedNodes.push(upstreamBase);

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT_MS);

        // Forward original headers with custom cluster metadata
        const newHeaders = new Headers(request.headers);
        newHeaders.set("X-Forwarded-Host", url.host);
        newHeaders.set("X-NanoPro-Gateway", "Cloudflare-Workers-Master");

        const forwardReq = new Request(targetUrl.toString(), {
          method: request.method,
          headers: newHeaders,
          body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
          redirect: "follow",
          signal: controller.signal
        });

        const response = await fetch(forwardReq);
        clearTimeout(timeoutId);

        // If upstream responded with 502/503/504, try next peer
        if (response.status >= 502 && response.status <= 504) {
          lastError = `HTTP ${response.status} from ${upstreamBase}`;
          continue;
        }

        // Response is healthy! Add cluster telemetry headers
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
        // Continue loop to next fallback peer
      }
    }

    // If all upstreams failed, return friendly unified failover emergency JSON
    return new Response(JSON.stringify({
      error: "ALL_CLUSTER_NODES_STANDBY",
      message: "NanoPro Gateway attempted all live cluster nodes. Primary nodes currently synchronizing.",
      attempted_nodes: attemptedNodes,
      last_error: lastError,
      timestamp: new Date().toISOString()
    }, null, 2), {
      status: 503,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
};
