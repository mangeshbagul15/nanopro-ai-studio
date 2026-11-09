import os
import sys
import time

sys.path.insert(0, os.path.abspath("."))
if not os.environ.get("GROQ_API_KEY"):
    raise SystemExit("Set GROQ_API_KEY to run this live adapter test.")

print("1. Testing Groq client directly...")
import groq
groq_client = groq.Groq(api_key=os.environ["GROQ_API_KEY"])
t0 = time.time()
resp_groq = groq_client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Tell Mangesh in one friendly sentence in Marathi that NanoPro is active and super fast!"}],
    temperature=0.3
)
t_groq = round((time.time() - t0) * 1000, 1)
print(f"Groq 120B completed in {t_groq}ms:")
print("Output:", resp_groq.choices[0].message.content.encode("ascii", "backslashreplace").decode())

print("\n2. Testing Gemini client directly...")
from google import genai
from google.genai import types
gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
t0 = time.time()
cfg = types.GenerateContentConfig(
    system_instruction="You are NanoPro, an energetic AI assistant for Mangesh. Speak in friendly Marathi and English.",
    temperature=0.3
)
resp_gemini = gemini_client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Namaskar NanoPro! Kasa ahes?",
    config=cfg
)
t_gemini = round((time.time() - t0) * 1000, 1)
print(f"Gemini 3.5 Flash Lite completed in {t_gemini}ms:")
print("Output:", resp_gemini.text.encode("ascii", "backslashreplace").decode())

print("\nAll direct API tests successful!")
