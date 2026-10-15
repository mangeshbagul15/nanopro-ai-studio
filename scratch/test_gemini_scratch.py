import os
import sys
import time

sys.path.insert(0, os.path.abspath("."))
os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6KQsy8b90iALgALamKNnYZJkhT3KaY__J4d58eVlwfNSA"

from google import genai

key = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=key)

prompt = "I NEED WIFE, HOW CAN I ACHIVE?"
system_instruction = "You are NanoPro, an empathetic, smart, humorous, and practical AI buddy for Mangesh. Speak in a warm, encouraging, human blend of Marathi and English (Minlish) or English with Indian warmth. Give realistic, uplifting, and friendly advice."

t0 = time.time()
interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=prompt,
    system_instruction=system_instruction
)
elapsed = time.time() - t0
print(f"Time taken: {elapsed:.2f}s")
print("Response:\n", interaction.output_text)
