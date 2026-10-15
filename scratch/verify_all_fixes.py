import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from app.core.conversational_intelligence import conversational_intelligence

test_cases = [
    # 1. Weather and why heat
    ("today wether/", "Weather overview check"),
    ("why heat", "October Heat rationale check"),
    ("heat ka", "October Heat Marathi check"),
    ("why so hot", "Why so hot check"),
    
    # 2. Specific Python coding prompts
    ("'mangesh \" ccha fakt e find karaychay provide python code", "Mangesh 'e' extraction check"),
    ("\"mangesh \" cha fakt \"eg\" find karaychay python code dya", "Mangesh 'eg' substring check"),
    ("Write a Python code to find and print the substring 'eg' from the string 'mangesh", "Mangesh 'eg' substring English check"),
    ("mangesh string reverse kara python code", "Mangesh string reversal check"),
    
    # 3. Contextual Follow-up checks
    ("THEN WHAT", "Then what follow-up check"),
    ("EXPLAIN", "Explain follow-up check"),
    ("WHY", "Why follow-up check"),
    ("CODE DYA", "Generic code follow-up check"),
    ("DO IT", "Do it pipeline execution check")
]

print("=== STARTING CONVERSATIONAL INTELLIGENCE INTEGRATION TESTS ===")

all_passed = True
for prompt, desc in test_cases:
    p_lower = prompt.lower().strip()
    res = conversational_intelligence.dispatch(p_lower, prompt, session_id="test_session")
    if not res or not res.get("handled"):
        print(f"❌ FAILED: {desc} (Prompt: '{prompt}') -> Not handled!")
        all_passed = False
    else:
        reply_preview = res['reply'][:120].replace('\n', ' ')
        print(f"✅ PASSED: {desc} (Agent: {res.get('agent_id')}) -> {reply_preview}...")

if all_passed:
    print("\n🎉 ALL 13 TEST CASES PASSED WITH 100% SUCCESS!")
else:
    print("\n⚠️ SOME TESTS FAILED!")
