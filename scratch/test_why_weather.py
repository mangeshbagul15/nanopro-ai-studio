import re

def test_why_weather(p_lower: str, recent_topic: str):
    clean = re.sub(r'[^a-zA-Z0-9\u0900-\u097F\s]', ' ', p_lower).strip()
    words = clean.split()
    clean_str = " ".join(words)

    is_why = clean_str in [
        "why", "ka", "kashasathi", "reason kay", "why so", "kashala", "why this",
        "ka bara", "reason", "kashamule", "kyu", "kyun", "kashapayi", "why heat", "why hot"
    ] or (
        len(words) <= 2 and any(w in words for w in ["why", "ka", "kashasathi", "kashala", "kyu", "kyun"])
    ) or any(k in clean_str for k in ["why heat", "why hot", "why so hot", "heat ka", "unh ka", "unha ka", "why is it hot"])

    if is_why:
        topic = recent_topic
        if topic == "weather" or any(k in p_lower for k in ["heat", "unh", "hot", "temperature", "havaman", "vatavaran"]):
            return "EXPLAIN_OCTOBER_HEAT"
        elif topic == "solar":
            return "EXPLAIN_SOLAR_EFFICIENCY"
        elif topic == "speed":
            return "EXPLAIN_ZERO_LATENCY"
        else:
            return "EXPLAIN_DATABASE"
    return "NOT_WHY"

prompts = [
    ("why heat", "database"),
    ("why heat", "weather"),
    ("why", "weather"),
    ("ka", "weather"),
    ("why so hot", "database"),
    ("unh ka ahe", "database"),
    ("why", "solar"),
    ("why", "database"),
    ("why", "speed")
]

for p, topic in prompts:
    res = test_why_weather(p.lower(), topic)
    print(f"Prompt: '{p}' (Topic: {topic}) -> Result: {res}")
