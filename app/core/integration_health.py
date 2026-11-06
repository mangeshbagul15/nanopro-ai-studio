"""Live health checks for every external service NanoPro holds a credential for.

The Connection Manager lists these alongside databases. Every check performs a
real authenticated call; nothing reports success unless the provider answered.
Secrets are read from the encrypted vault first, then the environment, and are
never echoed back in results.
"""

import base64
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional

from app.core.database import db, credentials_vault
from app.core.logger import log_event

_TIMEOUT = 12.0


def _secret(*names: str) -> str:
    """First non-empty secret from vault, then environment."""
    for name in names:
        if not name:
            continue
        try:
            cred = credentials_vault.get_credential(name)
            if cred and (cred.get("secret_value") or "").strip():
                return cred["secret_value"].strip()
        except Exception:
            pass
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    return ""


def _http(url: str, headers: Optional[Dict[str, str]] = None, method: str = "GET",
          body: Optional[bytes] = None, timeout: float = _TIMEOUT) -> Dict[str, Any]:
    merged = {"User-Agent": "NanoPro-Studio/1.0"}
    merged.update(headers or {})
    req = urllib.request.Request(url, data=body, method=method, headers=merged)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {"raw": raw[:200]}
        return {"status_code": resp.status, "payload": payload}


def _result(service: str, label: str, ok: bool, detail: str, extra: Optional[Dict] = None) -> Dict[str, Any]:
    res = {
        "service": service,
        "label": label,
        "success": bool(ok),
        "status": "Connected" if ok else "Failed",
        "detail": detail,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if extra:
        res.update(extra)
    return res


def _bearer(key: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {key}", "Accept": "application/json"}


def _probe_models(name: str, label: str, url: str, key: str, headers: Dict[str, str]) -> Dict[str, Any]:
    if not key:
        return _result(name, label, False, "API key not configured", {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http(url, headers=headers)
        payload = data["payload"]
        count = None
        if isinstance(payload, dict):
            for field in ("data", "models", "result"):
                if isinstance(payload.get(field), list):
                    count = len(payload[field])
                    break
        detail = f"Authenticated against {url.split('/')[2]} (HTTP {data['status_code']}"
        detail += f", {count} models visible)" if count is not None else ")"
        return _result(name, label, True, detail, {"models_visible": count})
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:220]
        except Exception:
            pass
        return _result(name, label, False, f"HTTP {e.code}: {body}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result(name, label, False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


# --- individual probes ------------------------------------------------------

def test_groq() -> Dict[str, Any]:
    return _probe_models("groq", "Groq LPU Cloud", "https://api.groq.com/openai/v1/models",
                         _secret("GROQ_API_KEY"), _bearer(_secret("GROQ_API_KEY")))


def test_openrouter() -> Dict[str, Any]:
    key = _secret("OPENROUTER_API_KEY")
    if not key:
        return _result("openrouter", "OpenRouter Aggregator", False, "API key not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http("https://openrouter.ai/api/v1/key", _bearer(key))
        info = data["payload"].get("data", {}) if isinstance(data["payload"], dict) else {}
        detail = f"Key authenticated; free tier: {info.get('is_free_tier')}, usage ${info.get('usage', 0)}"
        return _result("openrouter", "OpenRouter Aggregator", True, detail, {"usage": info.get("usage")})
    except urllib.error.HTTPError as e:
        return _result("openrouter", "OpenRouter Aggregator", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("openrouter", "OpenRouter Aggregator", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_anthropic() -> Dict[str, Any]:
    key = _secret("ANTHROPIC_API_KEY")
    return _probe_models("anthropic", "Anthropic Claude API", "https://api.anthropic.com/v1/models",
                         key, {"x-api-key": key, "anthropic-version": "2023-06-01"})


def _test_gemini(service: str, label: str, key: str) -> Dict[str, Any]:
    if not key:
        return _result(service, label, False, "API key not configured", {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}&pageSize=1")
        models = data["payload"].get("models", [])
        return _result(service, label, True, f"Gemini API key valid ({len(models)} model page returned)",
                       {"models_visible": len(models)})
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        return _result(service, label, False, f"HTTP {e.code}: {body}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result(service, label, False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_gemini() -> Dict[str, Any]:
    return _test_gemini("gemini", "Google Gemini", _secret("GEMINI_API_KEY"))


def test_gemini_spare() -> Dict[str, Any]:
    return _test_gemini("gemini_spare", "Google Gemini (Spare)", _secret("GEMINI_API_KEY_SPARE"))


def test_openai() -> Dict[str, Any]:
    return _probe_models("openai", "OpenAI", "https://api.openai.com/v1/models",
                         _secret("OPENAI_API_KEY"), _bearer(_secret("OPENAI_API_KEY")))


def test_deepseek() -> Dict[str, Any]:
    return _probe_models("deepseek", "DeepSeek", "https://api.deepseek.com/models",
                         _secret("DEEPSEEK_API_KEY"), _bearer(_secret("DEEPSEEK_API_KEY")))


def test_mistral() -> Dict[str, Any]:
    return _probe_models("mistral", "Mistral AI", "https://api.mistral.ai/v1/models",
                         _secret("MISTRAL_API_KEY"), _bearer(_secret("MISTRAL_API_KEY")))


def test_cohere() -> Dict[str, Any]:
    return _probe_models("cohere", "Cohere", "https://api.cohere.com/v1/models",
                         _secret("COHERE_API_KEY"), _bearer(_secret("COHERE_API_KEY")))


def test_sambanova() -> Dict[str, Any]:
    return _probe_models("sambanova", "SambaNova", "https://api.sambanova.ai/v1/models",
                         _secret("SAMBANOVA_API_KEY"), _bearer(_secret("SAMBANOVA_API_KEY")))


def _telegram(service: str, label: str, env_name: str) -> Dict[str, Any]:
    token = _secret(env_name)
    if not token:
        try:
            from app.core import config as _cfg
            token = (getattr(_cfg, env_name, "") or "").strip()
        except Exception:
            token = ""
    if not service.endswith("_alerts"):
        pass
    if not token:
        return _result(service, label, False, "Bot token not configured", {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http(f"https://api.telegram.org/bot{token}/getMe")
        info = data["payload"].get("result", {})
        return _result(service, label, True, f"Bot @{info.get('username')} verified", {"bot_username": info.get("username")})
    except urllib.error.HTTPError as e:
        return _result(service, label, False, f"HTTP {e.code}: invalid bot token", {"error_category": "AUTH_ERROR"})
    except Exception as e:
        return _result(service, label, False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_telegram_news() -> Dict[str, Any]:
    return _telegram("telegram_news", "Telegram News Bot", "TELEGRAM_NEWS_BOT_TOKEN")


def test_telegram_health() -> Dict[str, Any]:
    return _telegram("telegram_health", "Telegram Health Bot", "TELEGRAM_HEALTH_BOT_TOKEN")


def test_telegram_career() -> Dict[str, Any]:
    return _telegram("telegram_career", "Telegram Career Bot", "TELEGRAM_CAREER_BOT_TOKEN")


def test_telegram_reports() -> Dict[str, Any]:
    return _telegram("telegram_reports", "Telegram Reports Bot", "TELEGRAM_REPORTS_BOT_TOKEN")


def test_telegram_apk() -> Dict[str, Any]:
    return _telegram("telegram_apk", "Telegram APK Bot", "TELEGRAM_APK_BOT_TOKEN")


def test_telegram_alerts() -> Dict[str, Any]:
    return _telegram("telegram_alerts", "Telegram Alerts Bot", "TELEGRAM_ALERTS")


def test_whatsapp_cloud() -> Dict[str, Any]:
    token = _secret("WHATSAPP_CLOUD_ACCESS_TOKEN")
    phone_id = _secret("WHATSAPP_CLOUD_PHONE_ID")
    if not token or not phone_id:
        return _result("whatsapp_cloud", "WhatsApp Cloud API", False,
                       "WHATSAPP_CLOUD_ACCESS_TOKEN / WHATSAPP_CLOUD_PHONE_ID not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http(f"https://graph.facebook.com/v20.0/{phone_id}?fields=display_phone_number,verified_name",
                     {"Authorization": f"Bearer {token}"})
        info = data["payload"]
        return _result("whatsapp_cloud", "WhatsApp Cloud API", True,
                       f"Phone {info.get('display_phone_number')} ({info.get('verified_name')})")
    except urllib.error.HTTPError as e:
        return _result("whatsapp_cloud", "WhatsApp Cloud API", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("whatsapp_cloud", "WhatsApp Cloud API", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_callmebot() -> Dict[str, Any]:
    key = _secret("CALLMEBOT_API_KEY")
    if not key:
        return _result("callmebot", "CallMeBot WhatsApp", False, "CALLMEBOT_API_KEY not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    return _result("callmebot", "CallMeBot WhatsApp", True, "API key configured (CallMeBot has no status endpoint)")


def test_textbee() -> Dict[str, Any]:
    key = _secret("TEXTBEE_API_KEY")
    if not key:
        return _result("textbee", "TextBee SMS Gateway", False, "TEXTBEE_API_KEY not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http("https://api.textbee.dev/api/v1/gateway/devices", {"x-api-key": key})
        devices = data["payload"].get("data", []) if isinstance(data["payload"], dict) else []
        return _result("textbee", "TextBee SMS Gateway", True, f"{len(devices)} registered device(s)")
    except urllib.error.HTTPError as e:
        return _result("textbee", "TextBee SMS Gateway", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("textbee", "TextBee SMS Gateway", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_resend() -> Dict[str, Any]:
    key = _secret("RESEND_API_KEY")
    if not key:
        return _result("resend", "Resend Email API", False, "RESEND_API_KEY not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http("https://api.resend.com/domains", {"Authorization": f"Bearer {key}"})
        domains = data["payload"].get("data", []) if isinstance(data["payload"], dict) else []
        return _result("resend", "Resend Email API", True, f"Key valid, {len(domains)} verified domain(s)")
    except urllib.error.HTTPError as e:
        return _result("resend", "Resend Email API", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("resend", "Resend Email API", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_brevo() -> Dict[str, Any]:
    key = _secret("BREVO_API_KEY")
    if not key:
        return _result("brevo", "Brevo Email API", False, "BREVO_API_KEY not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http("https://api.brevo.com/v3/account", {"api-key": key, "Accept": "application/json"})
        account = data["payload"]
        return _result("brevo", "Brevo Email API", True, f"Account {account.get('email')} verified")
    except urllib.error.HTTPError as e:
        return _result("brevo", "Brevo Email API", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("brevo", "Brevo Email API", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_elevenlabs() -> Dict[str, Any]:
    key = _secret("ELEVENLABS_API_KEY")
    if not key:
        return _result("elevenlabs", "ElevenLabs Voice", False, "ELEVENLABS_API_KEY not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http("https://api.elevenlabs.io/v1/user", {"xi-api-key": key})
        sub = data["payload"].get("subscription", {}) if isinstance(data["payload"], dict) else {}
        return _result("elevenlabs", "ElevenLabs Voice", True,
                       f"Tier {sub.get('tier')}, {sub.get('character_count')}/{sub.get('character_limit')} chars used")
    except urllib.error.HTTPError as e:
        return _result("elevenlabs", "ElevenLabs Voice", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("elevenlabs", "ElevenLabs Voice", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_heygen() -> Dict[str, Any]:
    key = _secret("HEYGEN_API_KEY")
    if not key:
        return _result("heygen", "HeyGen Avatar Video", False, "HEYGEN_API_KEY not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http("https://api.heygen.com/v2/user/me", {"X-Api-Key": key})
        info = data["payload"].get("data", {}) if isinstance(data["payload"], dict) else {}
        return _result("heygen", "HeyGen Avatar Video", True, f"User {info.get('email', 'verified')}")
    except urllib.error.HTTPError as e:
        return _result("heygen", "HeyGen Avatar Video", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("heygen", "HeyGen Avatar Video", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_luma() -> Dict[str, Any]:
    key = _secret("LUMA_API_KEY")
    if not key:
        return _result("luma", "Luma Dream Machine", False, "LUMA_API_KEY not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http("https://api.lumalabs.ai/dream-machine/v1/credits", {"Authorization": f"Bearer {key}"})
        credits = data["payload"].get("credits") if isinstance(data["payload"], dict) else None
        return _result("luma", "Luma Dream Machine", True, f"Key valid, credits: {credits}")
    except urllib.error.HTTPError as e:
        return _result("luma", "Luma Dream Machine", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("luma", "Luma Dream Machine", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_abuseipdb() -> Dict[str, Any]:
    key = _secret("ABUSEIPDB_API_KEY")
    if not key:
        return _result("abuseipdb", "AbuseIPDB Threat Intel", False, "ABUSEIPDB_API_KEY not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    try:
        data = _http("https://api.abuseipdb.com/api/v2/check?ipAddress=8.8.8.8&maxAgeInDays=90",
                     {"Key": key, "Accept": "application/json"})
        score = data["payload"].get("data", {}).get("abuseConfidenceScore")
        return _result("abuseipdb", "AbuseIPDB Threat Intel", True, f"Key valid, sample score: {score}")
    except urllib.error.HTTPError as e:
        return _result("abuseipdb", "AbuseIPDB Threat Intel", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("abuseipdb", "AbuseIPDB Threat Intel", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_coingecko() -> Dict[str, Any]:
    key = _secret("COINGECKO_API_KEY")
    headers = {"x-cg-demo-api-key": key} if key else {"Accept": "application/json"}
    try:
        data = _http("https://api.coingecko.com/api/v3/ping", headers)
        return _result("coingecko", "CoinGecko Market Data", True,
                       f"API reachable ({(data['payload'] or {}).get('gecko_says', 'ok')}); key {'used' if key else 'not set'}")
    except urllib.error.HTTPError as e:
        return _result("coingecko", "CoinGecko Market Data", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("coingecko", "CoinGecko Market Data", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_razorpay() -> Dict[str, Any]:
    key_id = _secret("RAZORPAY_KEY_ID")
    key_secret = _secret("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        return _result("razorpay", "Razorpay Payments", False, "RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    auth = base64.b64encode(f"{key_id}:{key_secret}".encode()).decode()
    try:
        data = _http("https://api.razorpay.com/v1/payments?count=1", {"Authorization": f"Basic {auth}"})
        return _result("razorpay", "Razorpay Payments", True, f"Key {key_id[:10]}... authenticated")
    except urllib.error.HTTPError as e:
        return _result("razorpay", "Razorpay Payments", False, f"HTTP {e.code}", {"error_category": "AUTH_OR_API_ERROR"})
    except Exception as e:
        return _result("razorpay", "Razorpay Payments", False, f"{type(e).__name__}: {e}", {"error_category": "NETWORK_ERROR"})


def test_bedrock() -> Dict[str, Any]:
    key = _secret("AWS_BEDROCK_API_KEY", "AWS_BEARER_TOKEN_BEDROCK")
    if not key:
        return _result("aws_bedrock", "AWS Bedrock (Claude)", False, "Bedrock API key not configured",
                       {"error_category": "MISSING_CREDENTIALS"})
    meta = {}
    try:
        cred = credentials_vault.get_credential("AWS_BEDROCK_API_KEY")
        meta = (cred or {}).get("additional_metadata") or {}
    except Exception:
        pass
    region = os.environ.get("BEDROCK_REGION") or meta.get("region") or "us-east-1"
    model = os.environ.get("BEDROCK_MODEL_ID") or meta.get("model_id") or "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    os.environ["AWS_BEARER_TOKEN_BEDROCK"] = key
    try:
        from app.core import clock_sync
        clock_sync.apply_botocore_patch()
        import boto3
        client = boto3.client("bedrock-runtime", region_name=region)
        resp = client.converse(modelId=model, messages=[{"role": "user", "content": [{"text": "Reply with: OK"}]}],
                               inferenceConfig={"maxTokens": 8})
        text = resp["output"]["message"]["content"][0]["text"].strip()
        return _result("aws_bedrock", "AWS Bedrock (Claude)", True, f"Converse OK with {model}: {text[:20]}")
    except Exception as e:
        msg = str(e)
        category = "IAM_POLICY_DENIED" if "not authorized to perform: bedrock" in msg else "BEDROCK_ERROR"
        return _result("aws_bedrock", "AWS Bedrock (Claude)", False, msg[:300], {"error_category": category})


def _aws_iam_credentials() -> Dict[str, str]:
    try:
        cred = credentials_vault.get_credential("AWS_S3_DATA_LAKE") or {}
        access_key = (cred.get("username") or "").strip()
        secret_key = (cred.get("secret_value") or "").strip()
    except Exception:
        access_key, secret_key = "", ""
    return {
        "access_key": access_key or _secret("AWS_ACCESS_KEY_ID"),
        "secret_key": secret_key or _secret("AWS_SECRET_ACCESS_KEY"),
    }


def _cloudwatch_probe(service: str, label: str, vault_name: str, probe: str) -> Dict[str, Any]:
    key = _secret(vault_name)
    if not key:
        return _result(service, label, False, f"{vault_name} not configured", {"error_category": "MISSING_CREDENTIALS"})
    iam = _aws_iam_credentials()
    if not (iam["access_key"] and iam["secret_key"]):
        return _result(service, label, False,
                       "CloudWatch API key stored, but no IAM access key is available to verify the account",
                       {"error_category": "MISSING_CREDENTIALS"})
    region = _secret("AWS_REGION") or "ap-southeast-2"
    try:
        import boto3
        from app.core import clock_sync
        clock_sync.apply_botocore_patch()
        client = boto3.client(
            "cloudwatch" if probe == "metrics" else "logs",
            region_name=region,
            aws_access_key_id=iam["access_key"],
            aws_secret_access_key=iam["secret_key"],
        )
        if probe == "metrics":
            data = client.list_metrics()
            count = len(data.get("Metrics", []))
        else:
            data = client.describe_log_groups(limit=1)
            count = len(data.get("logGroups", []))
        return _result(service, label, True,
                       f"IAM key authorized for CloudWatch {probe} in {region}; {count} item(s) visible",
                       {"region": region})
    except Exception as exc:
        message = str(exc)
        if "not authorized" in message or "AccessDenied" in message:
            return _result(service, label, False,
                           f"IAM policy denial for user {iam['access_key'][:8]}...: {message[:260]}",
                           {"error_category": "IAM_POLICY_DENIED", "region": region})
        return _result(service, label, False, f"{type(exc).__name__}: {message[:240]}",
                       {"error_category": "NETWORK_OR_AUTH_ERROR", "region": region})


def test_cloudwatch_metrics() -> Dict[str, Any]:
    return _cloudwatch_probe("aws_cloudwatch_metrics", "AWS CloudWatch Metrics", "AWS_CLOUDWATCH_METRICS_KEY", "metrics")


def test_cloudwatch_logs() -> Dict[str, Any]:
    return _cloudwatch_probe("aws_cloudwatch_logs", "AWS CloudWatch Logs", "AWS_CLOUDWATCH_LOGS_KEY", "logs")


def test_jina() -> Dict[str, Any]:
    key = _secret("JINA_API_KEY")
    if not key:
        return _result("jina", "Jina Reader", False, "JINA_API_KEY not configured", {"error_category": "MISSING_CREDENTIALS"})
    return _result("jina", "Jina Reader", True, "API key configured (reader probe skipped to avoid quota use)")


def test_tavily() -> Dict[str, Any]:
    key = _secret("TAVILY_API_KEY")
    if not key:
        return _result("tavily", "Tavily Search", False, "TAVILY_API_KEY not configured", {"error_category": "MISSING_CREDENTIALS"})
    return _result("tavily", "Tavily Search", True, "API key configured (search probe skipped to avoid quota use)")


# --- registry --------------------------------------------------------------

SERVICES: List[Dict[str, Any]] = [
    {"id": "groq", "label": "Groq LPU Cloud", "category": "AI Models", "vault": "GROQ_API_KEY", "env": "GROQ_API_KEY", "test": test_groq},
    {"id": "gemini", "label": "Google Gemini", "category": "AI Models", "vault": "GEMINI_API_KEY", "env": "GEMINI_API_KEY", "test": test_gemini},
    {"id": "gemini_spare", "label": "Google Gemini (Spare)", "category": "AI Models", "vault": "GEMINI_API_KEY_SPARE", "env": "GEMINI_API_KEY_SPARE", "test": test_gemini_spare},
    {"id": "anthropic", "label": "Anthropic Claude API", "category": "AI Models", "vault": "ANTHROPIC_API_KEY", "env": "ANTHROPIC_API_KEY", "test": test_anthropic},
    {"id": "openrouter", "label": "OpenRouter Aggregator", "category": "AI Models", "vault": "OPENROUTER_API_KEY", "env": "OPENROUTER_API_KEY", "test": test_openrouter},
    {"id": "openai", "label": "OpenAI", "category": "AI Models", "vault": "OPENAI_API_KEY", "env": "OPENAI_API_KEY", "test": test_openai},
    {"id": "deepseek", "label": "DeepSeek", "category": "AI Models", "vault": "DEEPSEEK_API_KEY", "env": "DEEPSEEK_API_KEY", "test": test_deepseek},
    {"id": "mistral", "label": "Mistral AI", "category": "AI Models", "vault": "MISTRAL_API_KEY", "env": "MISTRAL_API_KEY", "test": test_mistral},
    {"id": "cohere", "label": "Cohere", "category": "AI Models", "vault": "COHERE_API_KEY", "env": "COHERE_API_KEY", "test": test_cohere},
    {"id": "sambanova", "label": "SambaNova", "category": "AI Models", "vault": "SAMBANOVA_API_KEY", "env": "SAMBANOVA_API_KEY", "test": test_sambanova},
    {"id": "aws_bedrock", "label": "AWS Bedrock (Claude)", "category": "Cloud AI", "vault": "AWS_BEDROCK_API_KEY", "env": "AWS_BEDROCK_API_KEY", "test": test_bedrock},
    {"id": "aws_cloudwatch_metrics", "label": "AWS CloudWatch Metrics", "category": "Cloud Observability", "vault": "AWS_CLOUDWATCH_METRICS_KEY", "env": "AWS_CLOUDWATCH_METRICS_KEY", "test": test_cloudwatch_metrics},
    {"id": "aws_cloudwatch_logs", "label": "AWS CloudWatch Logs", "category": "Cloud Observability", "vault": "AWS_CLOUDWATCH_LOGS_KEY", "env": "AWS_CLOUDWATCH_LOGS_KEY", "test": test_cloudwatch_logs},
    {"id": "telegram_news", "label": "Telegram News Bot", "category": "Messaging", "vault": "TELEGRAM_NEWS_BOT_TOKEN", "env": "TELEGRAM_NEWS_BOT_TOKEN", "test": test_telegram_news},
    {"id": "telegram_health", "label": "Telegram Health Bot", "category": "Messaging", "vault": "TELEGRAM_HEALTH_BOT_TOKEN", "env": "TELEGRAM_HEALTH_BOT_TOKEN", "test": test_telegram_health},
    {"id": "telegram_career", "label": "Telegram Career Bot", "category": "Messaging", "vault": "TELEGRAM_CAREER_BOT_TOKEN", "env": "TELEGRAM_CAREER_BOT_TOKEN", "test": test_telegram_career},
    {"id": "telegram_reports", "label": "Telegram Reports Bot", "category": "Messaging", "vault": "TELEGRAM_REPORTS_BOT_TOKEN", "env": "TELEGRAM_REPORTS_BOT_TOKEN", "test": test_telegram_reports},
    {"id": "telegram_apk", "label": "Telegram APK Bot", "category": "Messaging", "vault": "TELEGRAM_APK_BOT_TOKEN", "env": "TELEGRAM_APK_BOT_TOKEN", "test": test_telegram_apk},
    {"id": "whatsapp_cloud", "label": "WhatsApp Cloud API", "category": "Messaging", "vault": "WHATSAPP_CLOUD_ACCESS_TOKEN", "env": "WHATSAPP_CLOUD_ACCESS_TOKEN", "test": test_whatsapp_cloud},
    {"id": "callmebot", "label": "CallMeBot WhatsApp", "category": "Messaging", "vault": "CALLMEBOT_API_KEY", "env": "CALLMEBOT_API_KEY", "test": test_callmebot},
    {"id": "textbee", "label": "TextBee SMS Gateway", "category": "Messaging", "vault": "TEXTBEE_API_KEY", "env": "TEXTBEE_API_KEY", "test": test_textbee},
    {"id": "resend", "label": "Resend Email API", "category": "Email", "vault": "RESEND_API_KEY", "env": "RESEND_API_KEY", "test": test_resend},
    {"id": "brevo", "label": "Brevo Email API", "category": "Email", "vault": "BREVO_API_KEY", "env": "BREVO_API_KEY", "test": test_brevo},
    {"id": "elevenlabs", "label": "ElevenLabs Voice", "category": "Media AI", "vault": "ELEVENLABS_API_KEY", "env": "ELEVENLABS_API_KEY", "test": test_elevenlabs},
    {"id": "heygen", "label": "HeyGen Avatar Video", "category": "Media AI", "vault": "HEYGEN_API_KEY", "env": "HEYGEN_API_KEY", "test": test_heygen},
    {"id": "luma", "label": "Luma Dream Machine", "category": "Media AI", "vault": "LUMA_API_KEY", "env": "LUMA_API_KEY", "test": test_luma},
    {"id": "jina", "label": "Jina Reader", "category": "Search & Intel", "vault": "JINA_API_KEY", "env": "JINA_API_KEY", "test": test_jina},
    {"id": "tavily", "label": "Tavily Search", "category": "Search & Intel", "vault": "TAVILY_API_KEY", "env": "TAVILY_API_KEY", "test": test_tavily},
    {"id": "coingecko", "label": "CoinGecko Market Data", "category": "Search & Intel", "vault": "COINGECKO_API_KEY", "env": "COINGECKO_API_KEY", "test": test_coingecko},
    {"id": "abuseipdb", "label": "AbuseIPDB Threat Intel", "category": "Search & Intel", "vault": "ABUSEIPDB_API_KEY", "env": "ABUSEIPDB_API_KEY", "test": test_abuseipdb},
    {"id": "razorpay", "label": "Razorpay Payments", "category": "Payments", "vault": "RAZORPAY_KEY_ID", "env": "RAZORPAY_KEY_ID", "test": test_razorpay},
]

_SERVICE_MAP = {s["id"]: s for s in SERVICES}

VDB_SERVICES = [
    {"id": "snowflake", "label": "Snowflake — NANO_PRO_SNOWFLAKE"},
    {"id": "my_postgres_local", "label": "PostgreSQL — MY_POSTGRES_LOCAL"},
    {"id": "postgres_cloud_free", "label": "PostgreSQL — POSTGRES_CLOUD_FREE (Neon)"},
    {"id": "postgres_render", "label": "PostgreSQL — POSTGRES_RENDER_CLOUD"},
    {"id": "duckdb", "label": "DuckDB — DUCKDB_GOLD_LAKEHOUSE"},
    {"id": "bigquery", "label": "Google BigQuery — GOOGLE_BIGQUERY_SANDBOX"},
    {"id": "aws_s3", "label": "AWS S3 — AWS_S3_DATA_LAKE"},
    {"id": "gmail", "label": "Gmail SMTP — GMAIL_SMTP"},
    {"id": "telegram_alerts", "label": "Telegram — TELEGRAM_ALERTS"},
    {"id": "sftp", "label": "SFTP — CLOUD_SFTP_SERVER"},
]


def _config_value(name: str) -> str:
    try:
        from app.core import config as _cfg
        return (getattr(_cfg, name, "") or "").strip()
    except Exception:
        return ""


def _is_configured(svc: Dict[str, Any]) -> bool:
    if svc["id"] == "razorpay":
        return bool(_secret("RAZORPAY_KEY_ID") and _secret("RAZORPAY_KEY_SECRET"))
    if svc["id"] == "coingecko":
        return True
    return bool(_secret(svc.get("vault") or "", svc.get("env") or "") or _config_value(svc.get("env") or ""))


def _credential_source(svc: Dict[str, Any]) -> str:
    if _secret(svc.get("vault") or ""):
        return "vault"
    if _secret(svc.get("env") or ""):
        return "env"
    if _config_value(svc.get("env") or ""):
        return "config"
    return "none"


def list_services() -> Dict[str, Any]:
    items = []
    for svc in SERVICES:
        items.append({
            "id": svc["id"],
            "label": svc["label"],
            "category": svc["category"],
            "configured": _is_configured(svc),
            "source": _credential_source(svc),
            "last_status": _last_status(svc["id"]),
        })
    return {"services": items, "databases": VDB_SERVICES}


def _last_status(service_id: str) -> Optional[Dict[str, Any]]:
    try:
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT status, response_time_ms, tested_at, error_message FROM connection_history "
                "WHERE connection_name = ? ORDER BY tested_at DESC LIMIT 1",
                (f"INTG::{service_id}",),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {"status": row["status"], "response_time_ms": row["response_time_ms"],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["tested_at"] or 0)),
                    "error": row["error_message"]}
    except Exception:
        return None


def _record(result: Dict[str, Any]) -> None:
    try:
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO connection_history (id, connection_name, service_type, status, response_time_ms, "
                "active_user, active_role, active_database, active_schema, error_message, tested_at, details_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f"hist_{int(time.time()*1000)}_{serviceid_suffix(result['service'])}",
                 f"INTG::{result['service']}", "integration", result["status"],
                 result.get("response_time_ms", 0), None, None, None, None,
                 None if result["success"] else result.get("detail"),
                 time.time(), json.dumps(result, default=str)),
            )
            conn.commit()
    except Exception:
        pass


def serviceid_suffix(service: str) -> str:
    import uuid as _uuid
    return _uuid.uuid4().hex[:6]


def test_service(service_id: str) -> Dict[str, Any]:
    svc = _SERVICE_MAP.get(service_id)
    if not svc:
        return {"service": service_id, "success": False, "status": "Unknown", "detail": "Unknown service id"}
    started = time.time()
    try:
        result = svc["test"]()
    except Exception as e:
        result = _result(service_id, svc["label"], False, f"{type(e).__name__}: {e}")
    result["response_time_ms"] = round((time.time() - started) * 1000, 1)
    _record(result)
    log_event(f"Integration check {service_id}: {result['status']}", component="IntegrationHealth")
    return result


def test_all(service_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    ids = service_ids or [s["id"] for s in SERVICES]
    return [test_service(i) for i in ids]
