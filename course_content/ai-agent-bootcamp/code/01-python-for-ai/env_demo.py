# env_demo.py - read secrets from the .env file, never from your code
import os

from dotenv import load_dotenv

load_dotenv()                                  # reads the .env file in this folder

key = os.getenv("LLM_API_KEY")                 # None if it is missing
model = os.getenv("LLM_MODEL", "not set")      # second value = default

if not key:
    print("No API key found. Did you create the .env file in this folder?")
else:
    # Show only the first 4 letters. NEVER print a whole key.
    print(f"Key found: {key[:4]}{'*' * 10}")
print("Model:", model)
