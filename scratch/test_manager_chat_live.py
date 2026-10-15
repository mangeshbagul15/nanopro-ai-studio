import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(dotenv_path=BASE_DIR / ".env")

from app.agents.manager_agent import manager_agent

prompts_to_test = [
    "hi",
    "today wether",
    "why heat",
    "KHICHADI KASHI BANAVAYACHI?",
    "I NEED WIFE, HOW CAN I ACHIVE?",
    "Write a quick python script to sort a list of dicts by age"
]

print("="*60)
print("TESTING MANAGER_AGENT.CHAT_INTERACT LIVE")
print("="*60)

for p in prompts_to_test:
    t0 = time.time()
    res = manager_agent.chat_interact(p, session_id="test_live_session")
    dur_ms = round((time.time() - t0) * 1000, 1)
    rep = res.get("response", "")
    print(f"\nUser: '{p}' [{dur_ms}ms | Agent: {res.get('agent_id')} | Status: {res.get('status')}]:")
    print(rep[:250].encode("ascii", "backslashreplace").decode() + ("..." if len(rep) > 250 else ""))

print("\n" + "="*60)
print("ALL LIVE CHAT INTERACTION DRILLS COMPLETED!")
print("="*60)
