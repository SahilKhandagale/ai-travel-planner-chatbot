"""
Travel Planner Chatbot Utilities Package
Provides modules for Gemini LLM interaction, itinerary data modeling,
PDF compilation, and plain-text export.
"""

from .gemini_client import get_gemini_client, validate_api_key
from .itinerary_generator import generate_itinerary, modify_itinerary_with_chat, ItineraryData, DayPlan, AttractionItem
from .pdf_generator import create_itinerary_pdf
from .text_generator import create_itinerary_text

__all__ = [
    "get_gemini_client",
    "validate_api_key",
    "generate_itinerary",
    "modify_itinerary_with_chat",
    "ItineraryData",
    "DayPlan",
    "AttractionItem",
    "create_itinerary_pdf",
    "create_itinerary_text",
]
