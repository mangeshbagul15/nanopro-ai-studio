import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(dotenv_path=BASE_DIR / ".env")

from app.core.model_adapter import model_manager

print("="*60)
print("1. Testing ModelManager Preferred Adapters & Status")
print("Groq available:", model_manager.groq.is_available())
print("Gemini available:", model_manager.gemini.is_available())
print("Ollama available:", model_manager.ollama.is_available())
print("Primary model:", model_manager.get_primary_model())
print("Effective general models:", model_manager.get_effective_model_list(task_type="general"))
print("Effective coding models:", model_manager.get_effective_model_list(task_type="coding"))
print("="*60)

print("\n2. Testing route_and_execute for general dialogue ('KHICHADI KASHI BANAVAYACHI?')...")
t0 = time.time()
content, model, mode, lat = model_manager.route_and_execute(
    prompt="KHICHADI KASHI BANAVAYACHI?",
    task_type="dialogue",
    system_prompt="You are NanoPro, an energetic AI assistant for Mangesh. Reply in crisp Marathi (2-3 steps).",
    timeout=15.0
)
print(f"Result in {lat}ms via [{model}] ({mode}):")
print(content.encode("ascii", "backslashreplace").decode())

print("\n" + "="*60)
print("3. Testing route_and_execute for coding ('Write Python script to parse CSV and sum column')...")
t0 = time.time()
content, model, mode, lat = model_manager.route_and_execute(
    prompt="Write a 3-line Python script to sum 'amount' column in transactions.csv",
    task_type="coding",
    system_prompt="Return clean executable Python code only.",
    timeout=15.0
)
print(f"Result in {lat}ms via [{model}] ({mode}):")
print(content.encode("ascii", "backslashreplace").decode())

print("\n" + "="*60)
print("4. Testing route_and_execute for relationship/life query ('I NEED WIFE, HOW CAN I ACHIVE?')...")
t0 = time.time()
content, model, mode, lat = model_manager.route_and_execute(
    prompt="I NEED WIFE, HOW CAN I ACHIVE?",
    task_type="dialogue",
    system_prompt="You are NanoPro, an empathetic, smart, humorous, and practical AI buddy for Mangesh. Give warm, witty, realistic advice in a friendly Marathi/English blend.",
    timeout=15.0
)
print(f"Result in {lat}ms via [{model}] ({mode}):")
print(content.encode("ascii", "backslashreplace").decode())

print("\n" + "="*60)
print("5. Telemetry check:")
telem = model_manager.get_router_telemetry()
for m in telem["models"]:
    if m["total_calls"] > 0:
        print(f"Model: {m['model_name']} | Status: {m['status']} | Total Calls: {m['total_calls']} | Avg Latency: {m['avg_latency_ms']}ms")
print("="*60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
