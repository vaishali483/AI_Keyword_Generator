import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


def get_gemini_client():
    """
    Create and return a Gemini client only
    when an API operation is actually required.
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Please add it to your environment."
        )

    return genai.Client(
        api_key=api_key
    )