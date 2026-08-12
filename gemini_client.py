import os

from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()


# Read API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Please add it to your .env file."
    )


# Model configuration
MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# Create one reusable Gemini client
client = genai.Client(
    api_key=api_key
)