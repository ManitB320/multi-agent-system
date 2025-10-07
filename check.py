# This file checks if gemini is running on your system successfully or not. (OPTIONAL)

import os
from dotenv import load_dotenv

# Load .env from current folder
load_dotenv(dotenv_path=".env")

from google import generativeai as genai

# Retrieve API key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found! Check your .env file location and syntax.")

print(f"Loaded key: {api_key[:8]}...")

# Configure Gemini manually (avoids browser login)
genai.configure(api_key=api_key)

# Test Gemini
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Hello Gemini! This is a test.")
print("\nResponse from Gemini:\n", response.text)
