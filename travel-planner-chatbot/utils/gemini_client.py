"""
Gemini API Client Wrapper
Handles API key management, client initialization, model selection,
and robust error handling using the official Google GenAI SDK.
"""

import os
from typing import Optional, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError

# Load environment variables from .env file
load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash"
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash-lite"]


def get_api_key(override_key: Optional[str] = None) -> Optional[str]:
    """
    Retrieve the Gemini API key.
    Checks user-provided override first, then environment variable.
    """
    if override_key and override_key.strip():
        cleaned = override_key.strip()
        if cleaned != "your_gemini_api_key_here":
            return cleaned

    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key and env_key != "your_gemini_api_key_here":
        return env_key

    return None


def validate_api_key(api_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validates whether an API key is provided and syntactically valid.
    Returns (is_valid, message).
    """
    key = get_api_key(api_key)
    if not key:
        return False, "Gemini API key is not configured. Please enter it in the sidebar or add it to your .env file."
    if len(key) < 15:
        return False, "The provided API key appears too short or malformed. Please check your Google AI Studio key."
    return True, "API key configured."


def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    """
    Initializes and returns a Google GenAI client instance.
    Raises ValueError if API key is absent.
    """
    key = get_api_key(api_key)
    if not key:
        raise ValueError(
            "Gemini API Key is missing. Please set GEMINI_API_KEY in your .env file "
            "or enter it in the application sidebar."
        )
    return genai.Client(api_key=key)


def test_api_connection(api_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Performs a lightweight probe to verify active API connectivity and key validity.
    """
    is_valid, msg = validate_api_key(api_key)
    if not is_valid:
        return False, msg

    try:
        client = get_gemini_client(api_key)
        # Fast lightweight call to confirm authentication
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents="Say 'OK' if you can read this.",
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=100,
            ),
        )
        if response and response.text:
            return True, "Successfully connected to Google Gemini API."
        return False, "Empty response from Gemini API."
    except ClientError as e:
        return False, f"Authentication failed: {e.message if hasattr(e, 'message') else str(e)}"
    except APIError as e:
        return False, f"Gemini API Error: {str(e)}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
