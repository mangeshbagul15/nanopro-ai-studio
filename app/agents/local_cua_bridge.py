# -*- coding: utf-8 -*-
"""
NanoPro CUA Bridge — real remote-controlled Chromium on the local laptop.

The Global AI Lab panel drives this daemon over HTTP. Every action the agent
takes happens in a visible Chromium window on this machine, so the user and the
agent observe the same screen. Nothing heavy runs on Render.

Start it with:
    start_cua_bridge.bat
    python app/agents/local_cua_bridge.py --headed

Endpoints (all CORS-enabled, loopback only):
    GET  /status      bridge + page state
    GET  /frame       latest JPEG screenshot of the controlled page
    POST /navigate    {"url": "https://..."}
    POST /snapshot    page text + numbered interactive elements
    POST /act         {"action": "click|type|press|scroll|goto|back|select|wait|hover|select_text|copy|paste|download|upload|drag", ...}
    POST /reset       fresh blank tab
    GET  /            human readable help page
"""

import argparse
import asyncio
import base64
import ipaddress
import os
import socket
import sys
import time
import urllib.parse

from aiohttp import web

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("[CUA Bridge] Playwright missing. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


VIEWPORT = {"width": 1280, "height": 800}
MAX_ELEMENTS = 160
MAX_TEXT = 7000
DEFAULT_URL = "about:blank"
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "NanoProCUA")

SNAPSHOT_JS = r"""
() => {
  const looksVisible = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width < 3 || r.height < 3) return false;
    if (r.bottom < -40 || r.top > window.innerHeight * 1.5) return false;
    const s = getComputedStyle(el);
    return s.visibility !== 'hidden' && s.display !== 'none' && s.opacity !== '0';
  };
  const selector = 'a[href],button,input,textarea,select,summary,[role="button"],[role="link"],[role="tab"],[role="menuitem"],[role="slider"],[aria-valuenow],[draggable="true"],[contenteditable="true"],[onclick]';
  const nodes = Array.from(document.querySelectorAll(selector));
  const registry = [];
  const elements = [];
  for (const el of nodes) {
    if (!looksVisible(el)) continue;
    const tag = el.tagName.toLowerCase();
    const isField = tag === 'input' || tag === 'textarea' || tag === 'select';
    const label = (el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('placeholder') || el.getAttribute('title') || el.getAttribute('name') || el.getAttribute('alt') || '')
      .replace(/\s+/g, ' ').trim().slice(0, 90);
    if (!label && !isField) continue;
    const r = el.getBoundingClientRect();
    elements.push({
      i: elements.length,
      tag: tag,
      type: (el.getAttribute('type') || '').toLowerCase(),
      label: label,
      href: tag === 'a' ? String(el.getAttribute('href') || '').slice(0, 120) : '',
      x: Math.round(r.left),
      y: Math.round(r.top),
      w: Math.round(r.width),
      h: Math.round(r.height)
    });
    registry.push(el);
    if (elements.length >= __MAX_ELEMENTS__) break;
  }
  window.__NANOPRO_CUA_ELS = registry;
  const bodyText = (document.body ? document.body.innerText : '') || '';
  const text = bodyText.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim().slice(0, __MAX_TEXT__);
  return {
    url: location.href,
    title: document.title,
    text: text,
    elements: elements,
    scroll: {
      y: Math.round(window.scrollY),
      height: Math.round(document.documentElement.scrollHeight),
      viewport: window.innerHeight
    }
  };
}
"""


def _is_public_url(url: str):
    """Refuse non-web schemes and private/loopback targets so the daemon cannot be
    turned into a probe for the laptop's own network."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False, "invalid url"
    if parsed.scheme not in ("http", "https"):
        return False, "only http and https are allowed"
    host = parsed.hostname or ""
    if not host:
        return False, "missing host"
    if host.lower() in ("localhost", "localhost.localdomain"):
        return False, "localhost is blocked"
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False, f"cannot resolve {host}"
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            return False, f"private address blocked ({ip})"
    return True, "ok"


def _normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


class BrowserBridge:
    def __init__(self, headless: bool, profile_dir: str):
        self.headless = headless
        self.profile_dir = profile_dir
        self.lock = asyncio.Lock()
        self.playwright = None
        self.context = None
        self.page = None
        self.last_frame = b""
        self.last_frame_at = 0.0
        self.started_at = time.time()
        self.downloads = []
        self._download_tasks = set()

    async def start(self):
        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile_dir,
            headless=self.headless,
            viewport=VIEWPORT,
            accept_downloads=True,
            permissions=["clipboard-read", "clipboard-write"],
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1280,880",
            ],
        )
        self.context.on("page", self._track_page)
        pages = self.context.pages
        self.page = pages[0] if pages else await self.context.new_page()
        self._watch_downloads(self.page)
        print(f"[CUA Bridge] Chromium ready (headless={self.headless}, profile={self.profile_dir})")

    def _watch_downloads(self, page):
        if page is None:
            return
        try:
            page.on("download", self._on_download)
        except Exception:
            pass

    def _on_download(self, download):
        async def _save():
            try:
                os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                name = download.suggested_filename or f"download-{int(time.time())}"
                target = os.path.join(DOWNLOAD_DIR, name)
                stem, ext = os.path.splitext(name)
                n = 1
                while os.path.exists(target):
                    target = os.path.join(DOWNLOAD_DIR, f"{stem} ({n}){ext}")
                    n += 1
                await download.save_as(target)
                size = os.path.getsize(target) if os.path.exists(target) else 0
                self.downloads.append({"name": os.path.basename(target), "path": target, "size": size})
                self.downloads = self.downloads[-10:]
            except Exception as exc:
                self.downloads.append({"name": "", "path": "", "size": 0, "error": str(exc)})

        task = asyncio.create_task(_save())
        self._download_tasks.add(task)
        task.add_done_callback(self._download_tasks.discard)

    def _track_page(self, page):
        self.page = page
        self._watch_downloads(page)

    async def stop(self):
        try:
            if self.context:
                await self.context.close()
        except Exception:
            pass
        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass

    async def ensure_page(self):
        if self.page and not self.page.is_closed():
            return self.page
        if self.context is None:
            raise RuntimeError("browser not started")
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        return self.page

    async def settle(self, ms=450):
        page = await self.ensure_page()
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        await asyncio.sleep(ms / 1000.0)

    async def capture(self):
        page = await self.ensure_page()
        try:
            frame = await page.screenshot(type="jpeg", quality=70, timeout=8000)
            self.last_frame = frame
            self.last_frame_at = time.time()
        except Exception:
            pass
        return self.last_frame

    async def state(self):
        page = await self.ensure_page()
        title = ""
        try:
            title = await page.title()
        except Exception:
            pass
        return {"url": page.url, "title": title}

    async def navigate(self, url):
        page = await self.ensure_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await self.settle(600)

    async def snapshot(self):
        page = await self.ensure_page()
        js = SNAPSHOT_JS.replace("__MAX_ELEMENTS__", str(MAX_ELEMENTS)).replace("__MAX_TEXT__", str(MAX_TEXT))
        try:
            data = await page.evaluate(js)
        except Exception as exc:
            data = {"url": page.url, "title": "", "text": "", "elements": [], "scroll": {}, "error": str(exc)}
        return data

    async def act(self, payload):
        page = await self.ensure_page()
        action = (payload.get("action") or "").strip().lower()

        if action in ("goto", "navigate"):
            url = _normalize_url(payload.get("url") or payload.get("text") or "")
            ok, reason = _is_public_url(url)
            if not ok:
                return {"ok": False, "error": reason}
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await self.settle(600)
            return {"ok": True}

        if action == "back":
            await page.go_back(wait_until="domcontentloaded", timeout=20000)
            await self.settle(500)
            return {"ok": True}

        if action == "click":
            idx = payload.get("index")
            point = None
            pages_before = len(self.context.pages)
            if idx is not None:
                point = await page.evaluate(
                    """(i) => {
                        const el = (window.__NANOPRO_CUA_ELS || [])[i];
                        if (!el) return null;
                        el.scrollIntoView({block: 'center', inline: 'center'});
                        const r = el.getBoundingClientRect();
                        if (!r.width && !r.height) {
                            el.click();
                            return {x: null, y: null};
                        }
                        return {x: r.left + r.width / 2, y: r.top + r.height / 2};
                    }""",
                    int(idx),
                )
                if point is None:
                    return {"ok": False, "error": "element index not found; take a fresh snapshot"}
                if point.get("x") is not None:
                    await page.mouse.move(float(point["x"]), float(point["y"]))
                    await asyncio.sleep(0.12)
                    await page.mouse.click(
                        float(point["x"]),
                        float(point["y"]),
                        button=(payload.get("button") or "left").lower(),
                        click_count=max(1, min(3, int(payload.get("clicks") or 1))),
                    )
            elif payload.get("x") is not None and payload.get("y") is not None:
                point = {"x": float(payload["x"]), "y": float(payload["y"])}
                await page.mouse.move(point["x"], point["y"])
                await page.mouse.click(
                    point["x"],
                    point["y"],
                    button=(payload.get("button") or "left").lower(),
                    click_count=max(1, min(3, int(payload.get("clicks") or 1))),
                )
            else:
                return {"ok": False, "error": "click needs index or x/y"}

            await asyncio.sleep(0.6)
            # Links with target=_blank (or window.open) spawn a tab; the agent
            # must follow it or the next snapshot reads the wrong document.
            if len(self.context.pages) > pages_before:
                newest = self.context.pages[-1]
                try:
                    await newest.wait_for_load_state("domcontentloaded", timeout=15000)
                except Exception:
                    pass
                self.page = newest
                await self.settle(600)
                return {"ok": True, "x": (point or {}).get("x"), "y": (point or {}).get("y"), "tab": "new"}
            await self.settle(700)
            return {"ok": True, "x": (point or {}).get("x"), "y": (point or {}).get("y")}

        if action in ("type", "fill"):
            idx = payload.get("index")
            text = payload.get("text") or ""
            point = None
            if idx is not None:
                focused = await page.evaluate(
                    """(i) => {
                        const el = (window.__NANOPRO_CUA_ELS || [])[i];
                        if (!el) return null;
                        el.scrollIntoView({block: 'center', inline: 'center'});
                        el.focus();
                        if (el.select) { try { el.select(); } catch (e) {} }
                        const r = el.getBoundingClientRect();
                        return {x: r.left + r.width / 2, y: r.top + r.height / 2};
                    }""",
                    int(idx),
                )
                if not focused:
                    return {"ok": False, "error": "element index not found; take a fresh snapshot"}
                point = focused
            await page.keyboard.type(text, delay=18)
            await asyncio.sleep(0.15)
            if payload.get("enter"):
                await page.keyboard.press("Enter")
            await self.settle(600)
            return {"ok": True, "x": (point or {}).get("x"), "y": (point or {}).get("y")}

        if action == "press":
            key = payload.get("key") or "Enter"
            await page.keyboard.press(key)
            await self.settle(500)
            return {"ok": True}

        if action == "hover":
            idx = payload.get("index")
            if idx is None:
                return {"ok": False, "error": "hover needs index"}
            point = await page.evaluate(
                """(i) => {
                    const el = (window.__NANOPRO_CUA_ELS || [])[i];
                    if (!el) return null;
                    el.scrollIntoView({block: 'center', inline: 'center'});
                    const r = el.getBoundingClientRect();
                    return {x: r.left + r.width / 2, y: r.top + r.height / 2};
                }""",
                int(idx),
            )
            if point:
                await page.mouse.move(float(point["x"]), float(point["y"]))
            await asyncio.sleep(0.2)
            return {"ok": True, "x": (point or {}).get("x"), "y": (point or {}).get("y")}

        if action == "scroll":
            direction = (payload.get("direction") or "down").lower()
            pixels = int(payload.get("pixels") or 600)
            if direction == "top":
                await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
            elif direction == "bottom":
                await page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
            else:
                await page.mouse.wheel(0, pixels if direction == "down" else -pixels)
            await self.settle(450)
            return {"ok": True}

        if action == "select":
            idx = payload.get("index")
            value = payload.get("value")
            if idx is None:
                return {"ok": False, "error": "select needs index"}
            changed = await page.evaluate(
                """([i, v]) => {
                    const el = (window.__NANOPRO_CUA_ELS || [])[i];
                    if (!el) return false;
                    el.value = v;
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                    return true;
                }""",
                [int(idx), value],
            )
            if not changed:
                return {"ok": False, "error": "element index not found"}
            await self.settle(450)
            return {"ok": True}

        if action in ("select_text", "highlight"):
            idx = payload.get("index")
            if idx is None:
                return {"ok": False, "error": "select_text needs index"}
            phrase = payload.get("text") or ""
            picked = await page.evaluate(
                """([i, phrase]) => {
                    const el = (window.__NANOPRO_CUA_ELS || [])[i];
                    if (!el) return {ok: false};
                    el.scrollIntoView({block: 'center', inline: 'center'});
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    const range = document.createRange();
                    if (phrase) {
                        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
                        let node, found = null;
                        while ((node = walker.nextNode())) {
                            const pos = node.nodeValue.indexOf(phrase);
                            if (pos !== -1) { found = {node: node, pos: pos}; break; }
                        }
                        if (found) {
                            range.setStart(found.node, found.pos);
                            range.setEnd(found.node, found.pos + phrase.length);
                        } else {
                            range.selectNodeContents(el);
                        }
                    } else {
                        range.selectNodeContents(el);
                    }
                    sel.addRange(range);
                    const r = el.getBoundingClientRect();
                    return {ok: true, selected: String(sel.toString() || '').slice(0, 400), x: r.left + r.width / 2, y: r.top + r.height / 2};
                }""",
                [int(idx), phrase],
            )
            if not picked or not picked.get("ok"):
                return {"ok": False, "error": "element index not found"}
            await asyncio.sleep(0.2)
            return {"ok": True, "selected_len": len(picked.get("selected") or ""), "x": picked.get("x"), "y": picked.get("y")}

        if action == "copy":
            await page.keyboard.press("Control+C")
            await asyncio.sleep(0.25)
            try:
                copied = await page.evaluate("() => navigator.clipboard.readText()")
            except Exception:
                copied = ""
            return {"ok": True, "copied_len": len(copied or ""), "preview": (copied or "")[:160]}

        if action == "paste":
            text = payload.get("text")
            idx = payload.get("index")
            point = None
            if idx is not None:
                point = await page.evaluate(
                    """(i) => {
                        const el = (window.__NANOPRO_CUA_ELS || [])[i];
                        if (!el) return null;
                        el.scrollIntoView({block: 'center', inline: 'center'});
                        el.focus();
                        const r = el.getBoundingClientRect();
                        return {x: r.left + r.width / 2, y: r.top + r.height / 2};
                    }""",
                    int(idx),
                )
                if point is None:
                    return {"ok": False, "error": "element index not found; take a fresh snapshot"}
            if text is None:
                try:
                    text = await page.evaluate("() => navigator.clipboard.readText()")
                except Exception:
                    text = ""
            if not text:
                return {"ok": False, "error": "nothing to paste"}
            try:
                await page.evaluate("(t) => navigator.clipboard.writeText(t)", text)
            except Exception:
                pass
            await page.keyboard.press("Control+V")
            await asyncio.sleep(0.25)
            await self.settle(400)
            return {"ok": True, "pasted_len": len(text), "x": (point or {}).get("x"), "y": (point or {}).get("y")}

        if action == "download":
            idx = payload.get("index")
            if idx is None:
                return {"ok": False, "error": "download needs the index of the download link/button"}
            point = await page.evaluate(
                """(i) => {
                    const el = (window.__NANOPRO_CUA_ELS || [])[i];
                    if (!el) return null;
                    el.scrollIntoView({block: 'center', inline: 'center'});
                    const r = el.getBoundingClientRect();
                    return {x: r.left + r.width / 2, y: r.top + r.height / 2};
                }""",
                int(idx),
            )
            if not point:
                return {"ok": False, "error": "element index not found; take a fresh snapshot"}
            before = len(self.downloads)
            pages_before = len(self.context.pages)
            await page.mouse.click(float(point["x"]), float(point["y"]))
            for _ in range(50):
                if len(self.downloads) > before:
                    break
                await asyncio.sleep(0.1)
            if len(self.context.pages) > pages_before:
                self.page = self.context.pages[-1]
                self._watch_downloads(self.page)
                await self.settle(500)
            await self.settle(300)
            if len(self.downloads) > before:
                return {"ok": True, "download": self.downloads[-1], "x": point["x"], "y": point["y"]}
            return {"ok": False, "error": "no download started — the element may not be a download link", "x": point["x"], "y": point["y"]}

        if action == "upload":
            idx = payload.get("index")
            path = (payload.get("path") or "").strip().strip('"')
            if idx is None or not path:
                return {"ok": False, "error": "upload needs index and an absolute file path"}
            if not os.path.isabs(path):
                return {"ok": False, "error": "upload path must be absolute"}
            if not os.path.isfile(path):
                return {"ok": False, "error": f"file not found: {path}"}
            try:
                handle = await page.evaluate_handle(
                    "(i) => (window.__NANOPRO_CUA_ELS || [])[i]", int(idx)
                )
                element = handle.as_element()
                if element is None:
                    return {"ok": False, "error": "element index not found"}
                await element.set_input_files(path)
            except Exception as exc:
                return {"ok": False, "error": f"upload failed: {exc}"}
            await self.settle(500)
            return {"ok": True, "uploaded": os.path.basename(path), "size": os.path.getsize(path)}

        if action == "drag":
            src = payload.get("from")
            dst = payload.get("to")
            if src is None:
                return {"ok": False, "error": "drag needs a from element index"}
            if dst is None and payload.get("dx") is None and payload.get("dy") is None:
                return {"ok": False, "error": "drag needs a to element index or dx/dy offset"}
            coords = await page.evaluate(
                """([a, b]) => {
                    const els = window.__NANOPRO_CUA_ELS || [];
                    const one = els[a];
                    if (!one) return null;
                    one.scrollIntoView({block: 'center', inline: 'center'});
                    const r1 = one.getBoundingClientRect();
                    const out = {x1: r1.left + r1.width / 2, y1: r1.top + r1.height / 2, x2: null, y2: null};
                    if (b !== null) {
                        const two = els[b];
                        if (!two) return null;
                        const r2 = two.getBoundingClientRect();
                        out.x2 = r2.left + r2.width / 2;
                        out.y2 = r2.top + r2.height / 2;
                    }
                    return out;
                }""",
                [int(src), None if dst is None else int(dst)],
            )
            if not coords:
                return {"ok": False, "error": "element index not found"}
            x2 = coords["x2"] if coords["x2"] is not None else coords["x1"] + float(payload.get("dx") or 0)
            y2 = coords["y2"] if coords["y2"] is not None else coords["y1"] + float(payload.get("dy") or 0)
            await page.mouse.move(coords["x1"], coords["y1"])
            await page.mouse.down()
            await asyncio.sleep(0.15)
            await page.mouse.move((coords["x1"] + x2) / 2, (coords["y1"] + y2) / 2, steps=8)
            await page.mouse.move(x2, y2, steps=8)
            await page.mouse.up()
            await self.settle(500)
            return {"ok": True, "x": x2, "y": y2}

        if action == "wait":
            await asyncio.sleep(max(0.2, min(10.0, float(payload.get("ms") or 1000) / 1000.0)))
            return {"ok": True}

        return {"ok": False, "error": f"unknown action '{action}'"}

    async def reset(self):
        if self.page and not self.page.is_closed():
            try:
                await self.page.close()
            except Exception:
                pass
        self.page = await self.context.new_page()
        self.last_frame = b""
        await self.settle(200)


BRIDGE = None


@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response(status=204)
    else:
        try:
            response = await handler(request)
        except web.HTTPException as exc:
            response = exc
        except Exception as exc:
            response = web.json_response({"ok": False, "error": str(exc)}, status=500)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    # Chrome's Private Network Access preflight
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


async def handle_status(request):
    async with BRIDGE.lock:
        state = await BRIDGE.state()
    return web.json_response(
        {
            "status": "online",
            "engine": "Playwright Chromium (local laptop)",
            "headless": BRIDGE.headless,
            "profile": os.path.abspath(BRIDGE.profile_dir),
            "pid": os.getpid(),
            "uptime_s": round(time.time() - BRIDGE.started_at, 1),
            "url": state["url"],
            "title": state["title"],
        }
    )


async def handle_frame(request):
    async with BRIDGE.lock:
        frame = await BRIDGE.capture()
        state = await BRIDGE.state()
    if not frame:
        return web.json_response({"ok": False, "error": "no frame captured yet"}, status=503)
    return web.json_response(
        {
            "ok": True,
            "url": state["url"],
            "title": state["title"],
            "screenshot": "data:image/jpeg;base64," + base64.b64encode(frame).decode("ascii"),
            "ts": time.time(),
        }
    )


async def handle_navigate(request):
    payload = await request.json()
    url = _normalize_url(payload.get("url") or "")
    ok, reason = _is_public_url(url)
    if not ok:
        return web.json_response({"ok": False, "error": reason}, status=400)
    async with BRIDGE.lock:
        await BRIDGE.navigate(url)
        state = await BRIDGE.state()
        await BRIDGE.capture()
    return web.json_response({"ok": True, **state})


async def handle_snapshot(request):
    async with BRIDGE.lock:
        data = await BRIDGE.snapshot()
        await BRIDGE.capture()
    return web.json_response({"ok": True, **data})


async def handle_act(request):
    payload = await request.json()
    async with BRIDGE.lock:
        result = await BRIDGE.act(payload)
        state = await BRIDGE.state()
        await BRIDGE.capture()
    return web.json_response({**result, **state})


async def handle_reset(request):
    async with BRIDGE.lock:
        await BRIDGE.reset()
    return web.json_response({"ok": True})


async def handle_index(request):
    html = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>NanoPro CUA Bridge</title>
<style>body{font-family:system-ui;background:#0B111C;color:#E2E8F0;padding:40px;line-height:1.6}
code{background:#111a29;padding:2px 6px;border-radius:4px;color:#7DD3FC} a{color:#38BDF8}</style></head>
<body><h2>NanoPro CUA Bridge is running</h2>
<p>This Chromium instance is controlled by the Global AI Lab in NanoPro Studio.</p>
<p>Health check: <a href="/status">/status</a> &middot; Live frame: <a href="/frame">/frame</a></p>
<p>Keep this window open while the agent works. Close it to stop the bridge.</p>
<p>Started with <code>python app/agents/local_cua_bridge.py --headed</code>.</p>
</body></html>"""
    return web.Response(text=html, content_type="text/html")


async def init_app(app):
    await BRIDGE.start()


async def cleanup_app(app):
    if BRIDGE:
        await BRIDGE.stop()


def create_app(headless: bool, profile_dir: str):
    global BRIDGE
    BRIDGE = BrowserBridge(headless=headless, profile_dir=profile_dir)
    app = web.Application(middlewares=[cors_middleware], client_max_size=4 * 1024 * 1024)
    app.router.add_get("/", handle_index)
    app.router.add_get("/status", handle_status)
    app.router.add_get("/frame", handle_frame)
    app.router.add_post("/navigate", handle_navigate)
    app.router.add_post("/snapshot", handle_snapshot)
    app.router.add_post("/act", handle_act)
    app.router.add_post("/reset", handle_reset)
    app.on_startup.append(init_app)
    app.on_cleanup.append(cleanup_app)
    return app


def main():
    parser = argparse.ArgumentParser(description="NanoPro CUA browser bridge")
    parser.add_argument("--port", type=int, default=int(os.environ.get("CUA_BRIDGE_PORT", "8765")))
    parser.add_argument("--headless", action="store_true", help="run without a visible window (default is visible)")
    parser.add_argument("--headed", action="store_true", help="force a visible window")
    parser.add_argument("--profile", default=os.environ.get("CUA_PROFILE_DIR", os.path.join(os.getcwd(), ".cua_profile")))
    args = parser.parse_args()

    headless = args.headless and not args.headed
    os.makedirs(args.profile, exist_ok=True)
    print("=" * 70)
    print(" NanoPro CUA Bridge  |  real Chromium on this machine")
    print(f" Listening on http://127.0.0.1:{args.port}  (visible window: {not headless})")
    print(" Keep this window running while the AI agent browses.")
    print("=" * 70)
    web.run_app(create_app(headless, args.profile), host="127.0.0.1", port=args.port, print=None)


if __name__ == "__main__":
    main()
