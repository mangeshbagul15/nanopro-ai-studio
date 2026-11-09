#!/usr/bin/env python3
"""
NanoPro Failover Agent — runs on Alwaysdata.
Watches the Cloudflare worker every 10 min. If CF is unreachable or reports
are stale (>27h), this agent takes over: reads live data, builds the business
report from Neon DM layer, and delivers it to Telegram / WhatsApp / email
exactly like the CF worker does. Marks its runs in Upstash so the CF manager
can see who served the report.
"""
import json, time, urllib.request, urllib.parse, urllib.error, os, sys, datetime

CF_STATUS = os.environ.get("NANOPRO_CF_STATUS_URL", "https://mangesh-nanopro.mangeshbagul15.workers.dev/api/manager/status")
UPSTASH = os.environ.get("NANOPRO_UPSTASH_URL", "")
UPSTASH_TOKEN = os.environ.get("NANOPRO_UPSTASH_TOKEN", "")
NEON_HOST = os.environ.get("NEON_HOST", "")
NEON_CONN = os.environ.get("NEON_CONN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
BOT_REPORTS = os.environ.get("TELEGRAM_REPORTS_BOT_TOKEN", "")
BOT_HEALTH = os.environ.get("TELEGRAM_HEALTH_BOT_TOKEN", "")
EMAIL_RELAY = os.environ.get("EMAIL_RELAY_URL", "")
EMAIL_SECRET = os.environ.get("EMAIL_RELAY_SECRET", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "nanoproaistudio@gmail.com")
WA_TOKEN = os.environ.get("WA_ACCESS_TOKEN", "")
WA_PHONE_ID = os.environ.get("WA_PHONE_NUMBER_ID", "")
WA_TO = os.environ.get("WA_TO_NUMBER", "")

CHECK_EVERY = 600          # 10 min
STALE_AFTER = 27 * 3600    # serve ourselves if no report for 27h
LOG = os.path.expanduser("~/nanopro_failover.log")
STATE = os.path.expanduser("~/nanopro_failover_state.json")

def log(msg):
    line = f"{datetime.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def http_json(url, method="GET", headers=None, body=None, timeout=12):
    req = urllib.request.Request(url, method=method, headers=headers or {},
        data=(json.dumps(body).encode() if body is not None else None))
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def neon_sql(query):
    r = http_json(f"https://{NEON_HOST}/sql", "POST",
        {"Neon-Connection-String": NEON_CONN, "Content-Type": "application/json"},
        {"query": query})
    return r.get("rows") or []

def tg(token, text, html=False):
    body = {"chat_id": CHAT_ID, "text": text[:4000], "disable_web_page_preview": True}
    if html: body["parse_mode"] = "HTML"
    try:
        d = http_json(f"https://api.telegram.org/bot{token}/sendMessage", "POST",
            {"Content-Type": "application/json"}, body)
        return bool(d.get("ok"))
    except Exception as e:
        log(f"tg fail: {e}")
        return False

def wa(text):
    body = {"messaging_product": "whatsapp", "to": WA_TO, "type": "text",
            "text": {"body": text[:3900]}}
    try:
        d = http_json(f"https://graph.facebook.com/v19.0/{WA_PHONE_ID}/messages", "POST",
            {"Authorization": f"Bearer {WA_TOKEN}", "Content-Type": "application/json"}, body)
        return bool(d.get("messages"))
    except Exception as e:
        log(f"wa fail: {e}")
        return False

def email(subject, text):
    try:
        http_json(EMAIL_RELAY, "POST", {"Content-Type": "application/json"},
            {"secret": EMAIL_SECRET, "to": EMAIL_TO, "subject": subject,
             "text": text, "attachmentName": "failover-report.txt", "attachmentText": text})
        return True
    except Exception as e:
        log(f"email fail: {e}")
        return False

def cf_alive():
    try:
        d = http_json(CF_STATUS, timeout=10)
        rep = (d.get("subsystems") or {}).get("reports") or {}
        age = rep.get("age_h")
        if age is not None and age < STALE_AFTER:
            return True, age
        return False, age   # reachable but stale
    except Exception:
        return False, None  # unreachable

METRICS_SQL = """
SELECT p, ord, m, v FROM (
  SELECT 'AML' p, 1 ord, 'Txns monitored' m, COUNT(*)::text v FROM bank_aml_fact_aml_txn_monitor WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'AML',2,'Txn volume','Rs '||TO_CHAR(COALESCE(SUM(amount_inr),0),'FM999,999,999,999') FROM bank_aml_fact_aml_txn_monitor WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'AML',3,'Watchlist hits',COUNT(*)::text FROM bank_aml_fact_aml_watchlist_hits WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'CREDIT_CARD',1,'Transactions',COUNT(*)::text FROM bank_credit_card_fact_cc_transactions WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'CREDIT_CARD',2,'Txn volume','Rs '||TO_CHAR(COALESCE(SUM(txn_amount_inr),0),'FM999,999,999,999') FROM bank_credit_card_fact_cc_transactions WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'ALM',1,'Net cashflow','Rs '||TO_CHAR(COALESCE(SUM(net_cashflow_inr),0),'FM999,999,999,999') FROM bank_alm_fact_alm_cashflows WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'UPI',1,'Transactions',COUNT(*)::text||' (OK '||COUNT(*) FILTER (WHERE txn_status='SUCCESS')||')' FROM bank_upi_fact_upi_transactions WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'UPI',2,'Volume','Rs '||TO_CHAR(COALESCE(SUM(amount_inr),0),'FM999,999,999,999') FROM bank_upi_fact_upi_transactions WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'CBS',1,'Journal txns',COUNT(*)::text FROM bank_cbs_fact_cbs_txn_journal WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'BUREAU_MART',1,'Avg credit score',COALESCE(ROUND(AVG(credit_score))::text,'n/a') FROM bank_bureau_mart_fact_bureau_scores WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'LOAN_BOOK',1,'Disbursed','Rs '||TO_CHAR(COALESCE(SUM(disbursed_inr),0),'FM999,999,999,999') FROM bank_loan_book_fact_lb_disbursals WHERE loaded_at::date=CURRENT_DATE
  UNION ALL SELECT 'TREASURY',1,'Deals today',COUNT(*)::text FROM bank_treasury_fact_ts_deals WHERE loaded_at::date=CURRENT_DATE
) t ORDER BY p, ord"""

def build_report(cycle):
    stamp = (datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)).strftime("%d %b %Y, %I:%M %p IST")
    L = [f"NanoPro AI Studio — {cycle} Report", stamp, "Served by: ALWAYSData failover agent (CF down)", ""]
    L.append("Banking business report — today")
    try:
        cur_p = None
        for row in neon_sql(METRICS_SQL):
            p, m, v = row["p"], row["m"], row["v"]
            if p != cur_p:
                L.append("")
                L.append(f"  {p}")
                cur_p = p
            L.append(f"    {m:<24}{v}")
    except Exception as e:
        L.append(f"  (metrics error: {e})")
    L.append("")
    L.append("Dashboards:")
    L.append("  https://mangesh-nanopro.mangeshbagul15.workers.dev/dashboard")
    L.append("  https://mangesh-nanopro.mangeshbagul15.workers.dev/dashboard/business")
    L.append(f"{cycle} END")
    return "\n".join(L), stamp

def mark_served(cycle):
    try:
        req = urllib.request.Request(f"{UPSTASH}/set/nanopro_failover_last",
            method="POST", headers={"Authorization": UPSTASH_TOKEN},
            data=json.dumps({"at": datetime.datetime.utcnow().isoformat() + "Z",
                             "cycle": cycle, "node": "alwaysdata"}).encode())
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass

def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {}

def save_state(st):
    json.dump(st, open(STATE, "w"))

def main():
    missing = [name for name, val in {
        "NANOPRO_UPSTASH_URL": UPSTASH,
        "NANOPRO_UPSTASH_TOKEN": UPSTASH_TOKEN,
        "NEON_CONN": NEON_CONN,
        "TELEGRAM_REPORTS_BOT_TOKEN": BOT_REPORTS,
        "TELEGRAM_HEALTH_BOT_TOKEN": BOT_HEALTH,
    }.items() if not val]
    if missing:
        log(f"failover agent disabled — missing env vars: {', '.join(missing)}")
        return
    log("failover agent started")
    st = load_state()
    while True:
        try:
            ok, age = cf_alive()
            if ok:
                st["cf_down_checks"] = 0
            else:
                st["cf_down_checks"] = st.get("cf_down_checks", 0) + 1
                if st["cf_down_checks"] >= 3:
                    # CF down/stale for ~30min → serve a MANUAL recovery report ourselves
                    report, stamp = build_report("MANUAL-FAILOVER")
                    title = f"NanoPro AI Studio — MANUAL-FAILOVER Report | {stamp}"
                    ok_tg = tg(BOT_REPORTS, report)
                    ok_wa = wa(report)
                    ok_em = email(title, report)
                    tg(BOT_HEALTH, f"NanoPro FAILOVER: CF unreachable/stale (age_h={age}). Alwaysdata agent served MANUAL-FAILOVER report. tg={ok_tg} wa={ok_wa} email={ok_em}")
                    mark_served("MANUAL-FAILOVER")
                    log(f"served failover report tg={ok_tg} wa={ok_wa} em={ok_em}")
                    st["cf_down_checks"] = 0   # re-check fresh next round
        except Exception as e:
            log(f"loop error: {e}")
        save_state(st)
        time.sleep(CHECK_EVERY)

if __name__ == "__main__":
    main()
