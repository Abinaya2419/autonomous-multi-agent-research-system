
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Use a supported Gemini model
MODEL_ID = os.getenv(
    "MODEL_ID",
    "gemini-2.5-flash"
).strip()

# API request timeout in seconds
REQUEST_TIMEOUT_SECONDS = int(
    os.getenv("REQUEST_TIMEOUT_SECONDS", "60")
)

# Gemini generateContent endpoint
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL_ID}:generateContent"
)
