"""Authenticated live walkthrough of the v2 shell. Never prints secrets."""
import json
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

BASE = os.environ.get("AUDIT_BASE", "https://mangesh-nanopro.mangeshbagul15.workers.dev")
OUT = os.path.join(os.path.dirname(__file__), "audit")
os.makedirs(OUT, exist_ok=True)


def env_value(path, key):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return os.environ.get(key, "")


def main():
    password = env_value(".env", "NANOPRO_ADMIN_PASSWORD")
    username = env_value(".env", "NANOPRO_ADMIN_USERNAME") or "nanopro"
    if not password:
        print("NO_ADMIN_PASSWORD")
        return 2

    report = {"base": BASE, "steps": [], "errors": [], "failed_requests": []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.on("pageerror", lambda e: report["errors"].append(str(e)[:200]))
        page.on("console", lambda m: report["errors"].append("console:" + m.text[:200])
                if m.type == "error" else None)

        def on_resp(r):
            if "/api/" in r.url and r.status >= 400:
                report["failed_requests"].append({"url": r.url.split("?")[0], "status": r.status})
        page.on("response", on_resp)

        # 1. Login gateway
        page.goto(BASE + "/login", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1500)
        report["login"] = {
            "method_buttons": [page.locator("#methodPasswordBtn").count(),
                               page.locator("#methodWhatsappBtn").count()],
            "register_link": page.get_by_text("Request Access", exact=False).count(),
            "google": page.locator("#googleOAuthBtn").count(),
            "direct_form": page.locator("#loginUsername").count() and page.locator("#loginPassword").count(),
            "title": page.title(),
        }
        page.screenshot(path=os.path.join(OUT, "01_login.png"), full_page=True)

        page.fill("#loginUsername", username)
        page.fill("#loginPassword", password)
        page.click("#loginBtn")
        try:
            page.wait_for_url(re.compile(r"/$|/legacy"), timeout=45000)
        except Exception:
            page.wait_for_timeout(3000)
        page.wait_for_timeout(1000)
        report["post_login_url"] = page.url.split("?")[0]

        if not page.url.rstrip("/").endswith(tuple([BASE.rstrip("/")])) and "/?" not in page.url:
            pass

        if "NANOPRO OS" not in page.content():
            page.goto(BASE + "/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1000)

        # 2. Shell chips + cards
        def chip_state(cid):
            try:
                return page.locator("#" + cid).inner_text().replace("\n", " ").strip()[:80]
            except Exception:
                return ""

        cards = page.locator(".card")
        n_cards = cards.count()
        deadline = time.time() + 40
        while time.time() < deadline:
            vals = [page.locator("#v-" + [  "pipelines", "datamodel", "infra", "databases", "agents",
                                            "comms", "video", "payments", "monitor", "news"][i]).inner_text()
                    for i in range(min(n_cards, 10))]
            if all(v.strip() not in ("—", "") for v in vals):
                break
            page.wait_for_timeout(1500)

        report["top_strip"] = {k: chip_state(k) for k in ("c-health", "c-egress", "c-ai", "c-tasks")}
        card_report = {}
        ids = []
        for i in range(n_cards):
            el = cards.nth(i)
            h2 = el.locator("h2").inner_text()
            val = el.locator(".val").inner_text().replace("\n", " ")
            gid = el.get_attribute("id") or ""
            item = {"title": h2, "metric": val}
            el.click()
            page.wait_for_timeout(2500)
            if page.locator("#station.open").count():
                item["station_open"] = True
                item["station_total"] = (page.locator("#s-total").inner_text()[:30]
                                         if page.locator("#s-total").count() else "")
                item["station_roster"] = page.locator("#s-roster > *").count()
                page.screenshot(path=os.path.join(OUT, "02_station.png"), full_page=False)
                page.locator("#s-back").click()
                page.wait_for_timeout(800)
                card_report[h2] = item
                ids.append(h2)
                continue
            open_drawer = page.locator("#drawer.open").count()
            item["drawer_open"] = bool(open_drawer)
            if open_drawer:
                body = page.locator("#d-body").inner_text()
                item["drawer_head"] = body.replace("\n", " | ")[:260]
                item["drawer_ok"] = "Not available" not in body
                page.locator("#d-close").click()
                page.wait_for_timeout(400)
            card_report[h2] = item
            ids.append(h2)
        report["cards"] = card_report

        # ensure drawer closed
        if page.locator("#drawer.open").count():
            page.locator("#d-close").click()

        # 3. Station (agents card opens overlay)
        agent_card = page.locator("#v-agents").locator("xpath=ancestor::button[1]")
        if agent_card.count():
            agent_card.click()
            page.wait_for_timeout(4000)
            report["station"] = {
                "open": bool(page.locator("#station.open").count()),
                "total": page.locator("#s-total").inner_text()[:30] if page.locator("#s-total").count() else "",
                "roster": page.locator("#s-roster .ra").count() if page.locator("#s-roster .ra").count() else
                          page.locator("#s-roster > *").count(),
            }
            page.screenshot(path=os.path.join(OUT, "02_station.png"), full_page=False)
            # close station overlay
            sc = page.locator("#s-back")
            if sc.count():
                sc.click()
            else:
                page.keyboard.press("Escape")
            page.wait_for_timeout(800)

        page.screenshot(path=os.path.join(OUT, "03_shell.png"), full_page=True)

        # 4. Ask bar: rules answer then AI answer
        def ask(q):
            page.fill("#ask-input", q)
            page.press("#ask-input", "Enter")
            deadline = time.time() + 75
            while time.time() < deadline:
                body = page.locator("#d-body").inner_text()
                if "Thinking" not in body and body.strip():
                    break
                page.wait_for_timeout(1000)
            out = {
                "title": page.locator("#d-title").inner_text()[:40],
                "answer": page.locator("#d-body").inner_text().replace("\n", " | ")[:400],
            }
            page.locator("#d-close").click()
            page.wait_for_timeout(300)
            return out

        report["ask_status"] = ask("status")
        report["ask_ai"] = ask("Explain in one sentence what the security guards protect.")
        page.screenshot(path=os.path.join(OUT, "04_ask.png"), full_page=False)

        # 5. Legacy workspace reachable while authenticated
        page.goto(BASE + "/legacy", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)
        legacy_html = page.content()
        report["legacy"] = {
            "url": page.url.split("?")[0],
            "bytes": len(legacy_html),
            "dashboard_markers": sum(m in legacy_html for m in
                                     ("Universal Tech Video", "data-modeling", "Data Engineering",
                                      "Communication", "Automailer", "Automation")),
        }
        page.screenshot(path=os.path.join(OUT, "05_legacy.png"), full_page=False)

        browser.close()

    with open(os.path.join(OUT, "report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps(report, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
