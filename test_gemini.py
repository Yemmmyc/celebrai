
import os
import sys

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY is missing from .env")
    sys.exit(1)

try:
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=(
            "You are the AI engine for CelebrAI, an event planning app. "
            "Suggest three creative ideas for a small birthday celebration "
            "on a limited budget. Keep your answer concise."
        ),
    )

    if not response.text:
        print("ERROR: Gemini returned an empty response.")
        sys.exit(1)

    print("\nGemini connection successful!")
    print("-" * 45)
    print(response.text)

except Exception as exc:
    print(f"\nGemini request failed: {type(exc).__name__}: {exc}")
    sys.exit(1)
