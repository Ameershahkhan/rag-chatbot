import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")

if key:
    print("Key loaded. Length:", len(key))
else:
    print("Key NOT found. Check your .env file.")