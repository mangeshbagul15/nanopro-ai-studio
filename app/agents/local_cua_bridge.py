# -*- coding: utf-8 -*-
"""
local_cua_bridge.py:
=============================================================================
NanoPro Local Computer Use Agent (CUA) / Autonomous Browser Bridge
=============================================================================
Runs EXCLUSIVELY on the user's LOCAL LAPTOP using local CPU, GPU, RAM & SSD.
Guarantees ZERO MB memory / CPU load on Render cloud servers.
Connects directly to Playwright Chromium and provides a lightweight MCP HTTP
API for the NanoPro Global AI Lab right-side split-screen viewport.

Usage:
    python app/agents/local_cua_bridge.py [--port 8765] [--headed]
"""

import os
import sys
import json
import base64
import asyncio
from aiohttp import web

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("[Error] Playwright is not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

PORT = 8765
BROWSER_INSTANCE = None
PLAYWRIGHT_OBJ = None
PAGE_INSTANCE = None
HEADED = "--headed" in sys.argv

# CORS Middleware
@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response(status=200)
    else:
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            response = ex
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    return response

async def init_browser(app):
    global PLAYWRIGHT_OBJ, BROWSER_INSTANCE, PAGE_INSTANCE
    print(f"[CUA Bridge] Initializing local Playwright Chromium (Headed={HEADED})...")
    PLAYWRIGHT_OBJ = await async_playwright().start()
    BROWSER_INSTANCE = await PLAYWRIGHT_OBJ.chromium.launch(
        headless=not HEADED,
        args=["--disable-web-security", "--no-sandbox"]
    )
    context = await BROWSER_INSTANCE.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 NanoPro-CUA/2026"
    )
    PAGE_INSTANCE = await context.new_page()
    try:
        await PAGE_INSTANCE.goto("https://en.wikipedia.org", timeout=15000, wait_until="domcontentloaded")
    except Exception:
        pass
    print(f"[CUA Bridge] Local Browser ready! Listening on http://127.0.0.1:{PORT}")

async def cleanup_browser(app):
    global BROWSER_INSTANCE, PLAYWRIGHT_OBJ
    print("[CUA Bridge] Shutting down browser...")
    if BROWSER_INSTANCE:
        await BROWSER_INSTANCE.close()
    if PLAYWRIGHT_OBJ:
        await PLAYWRIGHT_OBJ.stop()

# Handlers
async def handle_status(request):
    return web.json_response({
        "status": "online",
        "engine": "Playwright Chromium (Local Laptop Hardware)",
        "hardware": "Local Laptop GPU/CPU/RAM",
        "render_load": "0 MB (Render Bypassed)",
        "current_url": PAGE_INSTANCE.url if PAGE_INSTANCE else "about:blank"
    })

async def handle_screenshot(request):
    if not PAGE_INSTANCE:
        return web.json_response({"error": "Browser not initialized"}, status=500)
    shot_bytes = await PAGE_INSTANCE.screenshot(type="jpeg", quality=75)
    b64 = base64.b64encode(shot_bytes).decode("utf-8")
    return web.json_response({
        "status": "success",
        "url": PAGE_INSTANCE.url,
        "title": await PAGE_INSTANCE.title(),
        "screenshot": f"data:image/jpeg;base64,{b64}",
        "timestamp": asyncio.get_event_loop().time()
    })

async def handle_navigate(request):
    data = await request.json()
    url = data.get("url", "https://en.wikipedia.org")
    if not url.startswith("http"):
        url = "https://" + url
    print(f"[CUA Bridge] Navigating to: {url}")
    await PAGE_INSTANCE.goto(url, timeout=30000, wait_until="domcontentloaded")
    shot_bytes = await PAGE_INSTANCE.screenshot(type="jpeg", quality=75)
    b64 = base64.b64encode(shot_bytes).decode("utf-8")
    return web.json_response({
        "status": "success",
        "url": PAGE_INSTANCE.url,
        "title": await PAGE_INSTANCE.title(),
        "screenshot": f"data:image/jpeg;base64,{b64}"
    })

async def handle_click(request):
    data = await request.json()
    selector = data.get("selector")
    x = data.get("x")
    y = data.get("y")
    print(f"[CUA Bridge] Click: selector={selector}, x={x}, y={y}")
    if selector:
        await PAGE_INSTANCE.click(selector, timeout=5000)
    elif x is not None and y is not None:
        await PAGE_INSTANCE.mouse.click(float(x), float(y))
    await asyncio.sleep(0.3)
    shot_bytes = await PAGE_INSTANCE.screenshot(type="jpeg", quality=75)
    b64 = base64.b64encode(shot_bytes).decode("utf-8")
    return web.json_response({
        "status": "success",
        "url": PAGE_INSTANCE.url,
        "screenshot": f"data:image/jpeg;base64,{b64}"
    })

async def handle_type(request):
    data = await request.json()
    selector = data.get("selector")
    text = data.get("text", "")
    print(f"[CUA Bridge] Type into {selector}: '{text}'")
    if selector:
        await PAGE_INSTANCE.fill(selector, text)
    else:
        await PAGE_INSTANCE.keyboard.type(text)
    await asyncio.sleep(0.3)
    shot_bytes = await PAGE_INSTANCE.screenshot(type="jpeg", quality=75)
    b64 = base64.b64encode(shot_bytes).decode("utf-8")
    return web.json_response({
        "status": "success",
        "url": PAGE_INSTANCE.url,
        "screenshot": f"data:image/jpeg;base64,{b64}"
    })

async def handle_scroll(request):
    data = await request.json()
    direction = data.get("direction", "down")
    pixels = data.get("pixels", 300)
    dy = pixels if direction == "down" else -pixels
    await PAGE_INSTANCE.evaluate(f"window.scrollBy({{ top: {dy}, behavior: 'smooth' }})")
    await asyncio.sleep(0.3)
    shot_bytes = await PAGE_INSTANCE.screenshot(type="jpeg", quality=75)
    b64 = base64.b64encode(shot_bytes).decode("utf-8")
    return web.json_response({
        "status": "success",
        "url": PAGE_INSTANCE.url,
        "screenshot": f"data:image/jpeg;base64,{b64}"
    })

def create_app():
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get("/status", handle_status)
    app.router.add_get("/screenshot", handle_screenshot)
    app.router.add_post("/navigate", handle_navigate)
    app.router.add_post("/click", handle_click)
    app.router.add_post("/type", handle_type)
    app.router.add_post("/scroll", handle_scroll)
    app.on_startup.append(init_browser)
    app.on_cleanup.append(cleanup_browser)
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="127.0.0.1", port=PORT)
