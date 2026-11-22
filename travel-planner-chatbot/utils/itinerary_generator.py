"""
Itinerary Generator Module
Defines Pydantic data schemas, prompt engineering templates,
and functions to generate and modify day-wise travel plans via Google Gemini.
"""

import json
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from google.genai import types
from google.genai.errors import APIError
from .gemini_client import get_gemini_client, DEFAULT_MODEL, FALLBACK_MODELS


# ============================================================================
# 1. Structured Data Models (Pydantic)
# ============================================================================

class AttractionItem(BaseModel):
    name: str = Field(description="Name of the attraction, monument, or experience")
    description: str = Field(description="Brief highlight, historical context, or recommendation for visitors")
    entry_fee_inr: float = Field(default=0.0, description="Estimated entry fee or ticket price per person in INR (0 if free)")


class DayPlan(BaseModel):
    day_number: int = Field(description="Day number of the trip (1, 2, ...)")
    day_title: str = Field(description="Short thematic title for the day, e.g. 'Arrival & Heritage Forts'")
    morning_activities: str = Field(description="Morning schedule with specific locations, timings, and travel directions")
    afternoon_activities: str = Field(description="Afternoon schedule including lunch spots, local cuisine, and indoor visits")
    evening_activities: str = Field(description="Evening schedule including sunset view, night markets, cultural shows, or dinner")
    suggested_attractions: List[AttractionItem] = Field(
        default_factory=list,
        description="List of key attractions and activities planned for this day"
    )
    transportation_cost_inr: float = Field(description="Estimated daily local transport cost in INR (cabs/autos/metro/rental)")
    food_cost_inr: float = Field(description="Estimated daily dining and snacks cost in INR")
    accommodation_cost_inr: float = Field(description="Estimated daily hotel/stay cost in INR")
    activity_cost_inr: float = Field(description="Estimated daily activity, guide, and entry fees in INR")
    total_daily_cost_inr: float = Field(description="Total estimated expense for this specific day in INR")


class ItineraryData(BaseModel):
    destination: str = Field(description="Target travel destination")
    starting_city: str = Field(description="Departure / origin city")
    duration_days: int = Field(description="Total duration of trip in days")
    travelers_count: int = Field(description="Total number of travelers")
    travel_style: str = Field(description="Travel style: Budget, Moderate, or Luxury")
    trip_overview: str = Field(description="Executive summary and thematic description of the entire itinerary")
    user_budget_inr: float = Field(description="User's total stated budget in INR")
    total_estimated_cost_inr: float = Field(description="Total grand estimated expense for the whole trip in INR")
    total_transport_cost_inr: float = Field(description="Total estimated transport cost across all days in INR")
    total_food_cost_inr: float = Field(description="Total estimated food cost across all days in INR")
    total_accommodation_cost_inr: float = Field(description="Total estimated accommodation cost across all days in INR")
    total_activities_cost_inr: float = Field(description="Total estimated activities & entry costs across all days in INR")
    budget_status: str = Field(description="'Within Budget', 'Exceeds Budget', or 'Budget Alert'")
    budget_difference_inr: float = Field(description="Budget difference: positive indicates savings, negative indicates deficit")
    budget_breakdown_explanation: str = Field(
        description="Comprehensive analysis of the budget breakdown, explaining realistic allocations and money-saving tips"
    )
    days: List[DayPlan] = Field(description="List of daily plans covering every day of the duration")
    practical_travel_tips: List[str] = Field(
        default_factory=list,
        description="Practical tips covering local transit, weather, packing, customs, and safety precautions"
    )
    disclaimer: str = Field(
        default=(
            "Note: All costs, fares, and ticket prices are approximate estimations in INR for planning purposes. "
            "No bookings or reservations have been made. Actual rates may vary depending on booking dates, seasonality, "
            "and vendor policies."
        ),
        description="Standard legal disclaimer"
    )


# ============================================================================
# 2. Example JSON Structure (for Documentation & Few-Shot Guidance)
# ============================================================================

EXAMPLE_JSON_RESPONSE = """
{
  "destination": "Goa",
  "starting_city": "Mumbai",
  "duration_days": 3,
  "travelers_count": 2,
  "travel_style": "Moderate",
  "trip_overview": "A 3-day coastal getaway exploring North Goa beaches, Portuguese heritage architecture, and coastal seafood.",
  "user_budget_inr": 30000.0,
  "total_estimated_cost_inr": 27500.0,
  "total_transport_cost_inr": 5500.0,
  "total_food_cost_inr": 8000.0,
  "total_accommodation_cost_inr": 10500.0,
  "total_activities_cost_inr": 3500.0,
  "budget_status": "Within Budget",
  "budget_difference_inr": 2500.0,
  "budget_breakdown_explanation": "The estimated trip cost of INR 27,500 fits comfortably within your INR 30,000 budget, leaving INR 2,500 for contingency or shopping.",
  "days": [
    {
      "day_number": 1,
      "day_title": "Arrival & North Goa Coastal Exploration",
      "morning_activities": "Arrive at Dabolim / Mopa airport, check in to Calangute hotel, and relax.",
      "afternoon_activities": "Enjoy Goan fish curry at a beachside shanty, then visit Aguada Fort.",
      "evening_activities": "Catch the sunset at Sinquerim Beach, followed by dinner in Candolim.",
      "suggested_attractions": [
        {"name": "Aguada Fort", "description": "17th-century Portuguese fort overlooking the Arabian Sea", "entry_fee_inr": 50.0},
        {"name": "Sinquerim Beach", "description": "Scenic coastline famous for water sports and golden sands", "entry_fee_inr": 0.0}
      ],
      "transportation_cost_inr": 1800.0,
      "food_cost_inr": 2500.0,
      "accommodation_cost_inr": 3500.0,
      "activity_cost_inr": 100.0,
      "total_daily_cost_inr": 7900.0
    }
  ],
  "practical_travel_tips": [
    "Renting a self-drive scooter (approx INR 400-600/day) is the most economical way to travel locally in Goa.",
    "Carry light cotton clothing and waterproof footwear during coastal excursions."
  ],
  "disclaimer": "All costs are approximate estimations in INR. No bookings have been made."
}
"""


# ============================================================================
# 3. System Prompt Engineering
# ============================================================================

SYSTEM_PROMPT = """You are an expert, highly knowledgeable AI Travel Planner and tour consultant.
Your objective is to craft realistic, practical, and highly personalized day-wise travel itineraries.

CRITICAL RULES & GUIDELINES:
1. Destination & Context: Tailor every recommendation specifically to the given destination, starting city, duration, traveler group, and stated interests.
2. Geographical Coherence: Never suggest visiting widely separated sights on the same day. Cluster nearby attractions to minimize transit time and fatigue.
3. Realistic Timings: Provide sensible morning, afternoon, and evening breakdowns allowing sufficient time for meals, rest, and travel between spots.
4. Non-Repetition: Do not repeat identical activities across different days.
5. Interest Alignment: Strongly prioritize attractions matching the user's selected interests (e.g., adventure, history, food, nature, beaches, shopping).
6. Budget Discipline & Accuracy:
   - All monetary figures must be in Indian Rupees (INR).
   - Tailor accommodation, transport, and dining suggestions to the selected travel style (Budget, Moderate, Luxury).
   - Sum daily costs accurately: total_daily_cost_inr = transportation + food + accommodation + activity costs.
   - If the user's budget is genuinely insufficient for the requested destination/duration/style, realistically calculate the true required expenses, flag budget_status as 'Budget Alert' or 'Exceeds Budget', and explain clearly in budget_breakdown_explanation where money is spent and how they can cut costs.
   - If the trip fits within budget, flag budget_status as 'Within Budget'.
7. Honesty & Factuality:
   - Never claim hotels, flights, or tickets are booked or reserved.
   - Unverified fares and prices must be stated as approximate estimates.
   - If specific pricing or seasonal details are variable, clearly explain this.
8. Output Format:
   - You MUST output STRICT VALID JSON adhering to the provided schema.
   - Do NOT wrap the JSON in unescaped markdown or extraneous commentary outside the JSON.
"""


# ============================================================================
# 4. Itinerary Generation Core Function
# ============================================================================

def generate_itinerary(
    destination: str,
    days: int,
    budget_inr: float,
    starting_city: str,
    interests: List[str],
    travelers_count: int = 1,
    travel_style: str = "Moderate",
    travel_season: Optional[str] = None,
    special_requests: Optional[str] = None,
    api_key: Optional[str] = None,
) -> ItineraryData:
    """
    Generates a full day-wise travel itinerary using the Gemini API.
    Returns a validated ItineraryData object.
    """
    client = get_gemini_client(api_key)

    interests_str = ", ".join(interests) if interests else "Sightseeing, Local Culture, Food"
    season_str = f"Preferred Month/Season: {travel_season}" if travel_season else "Season: General/Upcoming"
    special_str = f"Special Requests/Preferences: {special_requests}" if special_requests else ""

    user_prompt = f"""
Please generate a comprehensive, realistic {days}-day travel itinerary for:
- Destination: {destination}
- Starting City: {starting_city}
- Duration: {days} Days
- Total Budget: INR {budget_inr:,.0f} (for {travelers_count} traveler{'s' if travelers_count > 1 else ''})
- Number of Travelers: {travelers_count}
- Travel Style: {travel_style}
- Travel Interests: {interests_str}
- {season_str}
{special_str}

Ensure every single day from Day 1 to Day {days} is fully detailed with morning, afternoon, evening activities,
suggested attractions, and realistic estimated daily costs in INR.
Provide a clear budget breakdown and practical travel tips.
"""

    models_to_try = [DEFAULT_MODEL] + FALLBACK_MODELS
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    response_mime_type="application/json",
                    response_schema=ItineraryData,
                ),
            )

            if not response or not response.text:
                raise ValueError("Received an empty response from the Gemini API.")

            raw_text = response.text.strip()
            # Clean markdown fences if any present
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)

            parsed_dict = json.loads(raw_text)
            itinerary = ItineraryData.model_validate(parsed_dict)

            # Recalculate totals to guarantee 100% mathematical consistency
            itinerary = enforce_mathematical_consistency(itinerary, user_budget=budget_inr)
            return itinerary

        except APIError as e:
            last_error = e
            # Try fallback model if available
            continue
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Failed to generate itinerary after trying models: {str(last_error)}")


def enforce_mathematical_consistency(itinerary: ItineraryData, user_budget: float) -> ItineraryData:
    """
    Validates and synchronizes daily totals and trip-level cost sums
    to prevent arithmetic inconsistencies from LLM output.
    """
    total_transport = 0.0
    total_food = 0.0
    total_accom = 0.0
    total_activities = 0.0

    for day in itinerary.days:
        day_total = (
            day.transportation_cost_inr +
            day.food_cost_inr +
            day.accommodation_cost_inr +
            day.activity_cost_inr
        )
        day.total_daily_cost_inr = round(day_total, 2)
        total_transport += day.transportation_cost_inr
        total_food += day.food_cost_inr
        total_accom += day.accommodation_cost_inr
        total_activities += day.activity_cost_inr

    grand_total = total_transport + total_food + total_accom + total_activities

    itinerary.user_budget_inr = round(user_budget, 2)
    itinerary.total_transport_cost_inr = round(total_transport, 2)
    itinerary.total_food_cost_inr = round(total_food, 2)
    itinerary.total_accommodation_cost_inr = round(total_accom, 2)
    itinerary.total_activities_cost_inr = round(total_activities, 2)
    itinerary.total_estimated_cost_inr = round(grand_total, 2)

    diff = user_budget - grand_total
    itinerary.budget_difference_inr = round(diff, 2)

    if diff >= 0:
        itinerary.budget_status = "Within Budget"
    elif abs(diff) <= user_budget * 0.10:
        itinerary.budget_status = "Slightly Exceeds Budget"
    else:
        itinerary.budget_status = "Exceeds Budget"

    return itinerary


# ============================================================================
# 5. Chatbot Context & Follow-up Q&A
# ============================================================================

def chat_with_itinerary(
    itinerary: ItineraryData,
    chat_history: List[Dict[str, str]],
    user_message: str,
    api_key: Optional[str] = None,
) -> str:
    """
    Allows the user to ask follow-up questions about their generated trip.
    Maintains itinerary context and previous chat history.
    """
    client = get_gemini_client(api_key)

    # Convert current itinerary into a concise summary context
    itinerary_summary = {
        "destination": itinerary.destination,
        "starting_city": itinerary.starting_city,
        "duration_days": itinerary.duration_days,
        "travelers_count": itinerary.travelers_count,
        "travel_style": itinerary.travel_style,
        "user_budget_inr": itinerary.user_budget_inr,
        "total_estimated_cost_inr": itinerary.total_estimated_cost_inr,
        "budget_status": itinerary.budget_status,
        "days": [
            {
                "day": d.day_number,
                "title": d.day_title,
                "morning": d.morning_activities,
                "afternoon": d.afternoon_activities,
                "evening": d.evening_activities,
                "attractions": [a.name for a in d.suggested_attractions],
                "daily_cost_inr": d.total_daily_cost_inr,
            }
            for d in itinerary.days
        ],
    }

    chatbot_system = f"""You are a helpful and friendly AI Travel Planning Assistant.
The user has generated a {itinerary.duration_days}-day travel itinerary for {itinerary.destination} starting from {itinerary.starting_city}.
Current Itinerary Context:
{json.dumps(itinerary_summary, indent=2)}

Guidelines:
- Answer the user's questions clearly, concisely, and practically based on the current itinerary context.
- If asked for cost reduction, suggest specific changes (e.g. cheaper transport modes, budget eateries, free attractions).
- If asked to modify a specific day, explain what you would change and how it affects the schedule.
- If the user asks for restaurant recommendations, suggest authentic local places with price ranges in INR.
- Mention that if they want their full itinerary updated, they can click the 'Apply Changes & Regenerate Itinerary' option.
- Keep all monetary figures in INR.
"""

    # Build conversation context
    messages_content = []
    for chat in chat_history[-6:]:  # Keep recent history
        role_label = "User" if chat.get("role") == "user" else "Assistant"
        messages_content.append(f"{role_label}: {chat.get('content')}")

    messages_content.append(f"User: {user_message}\nAssistant:")
    full_prompt = "\n\n".join(messages_content)

    models_to_try = [DEFAULT_MODEL] + FALLBACK_MODELS
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=chatbot_system,
                    temperature=0.7,
                ),
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Chatbot query failed: {str(last_error)}")


# ============================================================================
# 6. Regenerate / Modify Itinerary with Chat Context
# ============================================================================

def modify_itinerary_with_chat(
    current_itinerary: ItineraryData,
    chat_history: List[Dict[str, str]],
    modification_instructions: str,
    api_key: Optional[str] = None,
) -> ItineraryData:
    """
    Applies user feedback/modifications to the existing itinerary and returns
    a fully updated structured ItineraryData object.
    """
    client = get_gemini_client(api_key)

    current_json = current_itinerary.model_dump_json(indent=2)
    recent_chat = "\n".join([f"{c['role'].upper()}: {c['content']}" for c in chat_history[-6:]])

    modification_prompt = f"""
CURRENT ITINERARY (JSON):
{current_json}

RECENT CHAT CONVERSATION:
{recent_chat}

REQUESTED MODIFICATIONS:
{modification_instructions}

TASK:
Update the entire travel itinerary to incorporate the requested modifications.
Ensure:
1. All changes flow naturally into the day-by-day plan.
2. Estimated costs in INR are updated realistically to match the changes.
3. The day numbers and duration remain consistent unless explicitly requested otherwise.
4. Output STRICT VALID JSON matching the ItineraryData schema.
"""

    models_to_try = [DEFAULT_MODEL] + FALLBACK_MODELS
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=modification_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    response_mime_type="application/json",
                    response_schema=ItineraryData,
                ),
            )

            if not response or not response.text:
                raise ValueError("Empty response during itinerary modification.")

            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)

            parsed_dict = json.loads(raw_text)
            updated_itinerary = ItineraryData.model_validate(parsed_dict)
            return enforce_mathematical_consistency(
                updated_itinerary, user_budget=current_itinerary.user_budget_inr
            )
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Failed to modify itinerary: {str(last_error)}")
