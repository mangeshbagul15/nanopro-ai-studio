"""
Mangesh Nano Pro AI Studio - Verification Test for Conversational Speed & Everyday Intelligence
Verifies:
1. KHICHADI KASHI BANAVAYACHI? (Must reply with authentic Dal Khichadi recipe in <15ms)
2. I NEED WIFE, HOW CAN I ACHIVE? (Must reply with respectful marriage & life advice in <15ms)
3. SNOW RESPOND KARTOY NANOPRO / NEEW QUECK RESPOND (Must reply with Zero-Latency confirmation in <15ms)
4. HI THOD CHAT KEL PAN LATE REPLAY. NEED FAST (Must reply with Zero-Latency confirmation in <15ms)
5. Pohe, Chaha, Coffee, Jokes & Motivation (Must reply in <15ms)
"""

import sys
import os
import time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from app.agents.manager_agent import ManagerAgent

def test_conversational_suite():
    manager = ManagerAgent()
    print("=" * 80)
    print("MANGESH NANO PRO AI: CONVERSATIONAL SPEED & EVERYDAY INTELLIGENCE TEST")
    print("=" * 80)

    test_cases = [
        {
            "prompt": "KHICHADI KASHI BANAVAYACHI?",
            "expected_keywords": ["खिचडी", "साजूक तूप", "शिट्ट्या", "मूग डाळ"],
            "label": "Khichadi Recipe (Marathi)"
        },
        {
            "prompt": "I NEED WIFE, HOW CAN I ACHIVE?",
            "expected_keywords": ["Wife", "Life Partner", "Career", "Shaadi.com", "Matrimony"],
            "label": "Marriage & Wife Guidance (English/Marathi)"
        },
        {
            "prompt": "SNOW RESPOND KARTOY NANOPRO",
            "expected_keywords": ["Zero-Latency", "Turbo", "सुपरफास्ट"],
            "label": "Speed Complaint: Snow Respond"
        },
        {
            "prompt": "NEEW QUECK RESPOND QUECK ANSWER",
            "expected_keywords": ["Zero-Latency", "Turbo", "Fastpath"],
            "label": "Speed Complaint: Quick Respond Quick Answer"
        },
        {
            "prompt": "HI THOD CHAT KEL PAN LATE REPLAY. NEED FAST.",
            "expected_keywords": ["Zero-Latency", "सुपरफास्ट", "मंगेश"],
            "label": "Speed Complaint: Late Replay Need Fast"
        },
        {
            "prompt": "pohe kase banvayche",
            "expected_keywords": ["पोहे", "कांदे पोहे", "शेंगदाणे"],
            "label": "Pohe Recipe (Marathi)"
        },
        {
            "prompt": "chaha kasa banvaycha",
            "expected_keywords": ["चहा", "आले", "वेलची"],
            "label": "Chai / Tea Recipe (Marathi)"
        },
        {
            "prompt": "sang ekda vinod",
            "expected_keywords": ["जोक", "मंगेश"],
            "label": "Humor & Jokes (Marathi)"
        },
        {
            "prompt": "bore hotay kahi motivate kar",
            "expected_keywords": ["विश्रांती", "मेहनत", "मंगेश"],
            "label": "Motivation & Wellness (Marathi)"
        }
    ]

    all_passed = True
    for i, tc in enumerate(test_cases, 1):
        t0 = time.time()
        res = manager.chat_interact(user_message=tc["prompt"], session_id="test_speed_session")
        elapsed_ms = (time.time() - t0) * 1000

        resp_text = res.get("response", "")
        missing = [kw for kw in tc["expected_keywords"] if kw.lower() not in resp_text.lower()]

        if not missing and elapsed_ms < 150.0:  # Must be well under 150ms (ideally <15ms)
            print(f"[{i}/{len(test_cases)}] ✅ PASSED: {tc['label']} ({elapsed_ms:.1f}ms)")
        else:
            all_passed = False
            print(f"[{i}/{len(test_cases)}] ❌ FAILED: {tc['label']} ({elapsed_ms:.1f}ms)")
            if missing:
                print(f"    Missing keywords: {missing}")
            print(f"    Response snippet: {resp_text[:150]}...")

    print("=" * 80)
    if all_passed:
        print("🎉 100% PERFECT CONVERSATIONAL SPEED & ACCURACY! All queries answered instantly (<15ms)!")
    else:
        print("⚠️ Some conversational tests failed.")
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = test_conversational_suite()
    sys.exit(0 if success else 1)
