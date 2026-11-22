"""
Text Itinerary Generator Module
Generates a cleanly formatted, readable plain-text representation
of the travel itinerary suitable for downloading as a .txt file.
"""

from .itinerary_generator import ItineraryData


def create_itinerary_text(itinerary: ItineraryData) -> str:
    """
    Converts an ItineraryData object into a formatted text report.
    """
    divider_major = "=" * 78
    divider_minor = "-" * 78

    lines = []
    lines.append(divider_major)
    lines.append("                  AI-POWERED TRAVEL PLANNER - ITINERARY")
    lines.append("                  B.Tech Mini-Project Demonstration")
    lines.append(divider_major)
    lines.append("")

    # Trip Overview Header
    lines.append(f"DESTINATION      : {itinerary.destination}")
    lines.append(f"STARTING FROM    : {itinerary.starting_city}")
    lines.append(f"DURATION         : {itinerary.duration_days} Days")
    lines.append(f"TRAVELERS        : {itinerary.travelers_count}")
    lines.append(f"TRAVEL STYLE     : {itinerary.travel_style}")
    lines.append(f"ALLOCATED BUDGET : INR {itinerary.user_budget_inr:,.2f}")
    lines.append(f"ESTIMATED COST   : INR {itinerary.total_estimated_cost_inr:,.2f}")
    lines.append(f"BUDGET STATUS    : {itinerary.budget_status}")

    diff = itinerary.budget_difference_inr
    if diff >= 0:
        lines.append(f"ESTIMATED SAVINGS: INR {diff:,.2f}")
    else:
        lines.append(f"BUDGET DEFICIT   : INR {abs(diff):,.2f}")

    lines.append("")
    lines.append("TRIP SUMMARY:")
    lines.append(f"{itinerary.trip_overview}")
    lines.append("")
    lines.append(divider_major)
    lines.append("                         EXPENSE BREAKDOWN")
    lines.append(divider_major)
    lines.append(f"  Accommodation (Hotel/Stay)       : INR {itinerary.total_accommodation_cost_inr:,.2f}")
    lines.append(f"  Food & Dining                    : INR {itinerary.total_food_cost_inr:,.2f}")
    lines.append(f"  Local Transportation             : INR {itinerary.total_transport_cost_inr:,.2f}")
    lines.append(f"  Activities, Sightseeing & Entry  : INR {itinerary.total_activities_cost_inr:,.2f}")
    lines.append(divider_minor)
    lines.append(f"  TOTAL ESTIMATED EXPENSE          : INR {itinerary.total_estimated_cost_inr:,.2f}")
    lines.append("")
    lines.append("BUDGET ANALYSIS & EXPLANATION:")
    lines.append(f"{itinerary.budget_breakdown_explanation}")
    lines.append("")
    lines.append(divider_major)
    lines.append("                       DAY-BY-DAY ITINERARY")
    lines.append(divider_major)

    for day in itinerary.days:
        lines.append("")
        lines.append(f"--- DAY {day.day_number}: {day.day_title.upper()} ---")
        lines.append("")
        lines.append("[MORNING]")
        lines.append(f"  {day.morning_activities}")
        lines.append("")
        lines.append("[AFTERNOON]")
        lines.append(f"  {day.afternoon_activities}")
        lines.append("")
        lines.append("[EVENING]")
        lines.append(f"  {day.evening_activities}")
        lines.append("")

        if day.suggested_attractions:
            lines.append("[KEY ATTRACTIONS & SIGHTS]")
            for attr in day.suggested_attractions:
                fee_str = f"(Approx INR {attr.entry_fee_inr:,.0f})" if attr.entry_fee_inr > 0 else "(Free Entry)"
                lines.append(f"  * {attr.name} {fee_str}")
                lines.append(f"    - {attr.description}")
            lines.append("")

        lines.append("[ESTIMATED DAILY EXPENSES]")
        lines.append(f"  * Local Transport  : INR {day.transportation_cost_inr:,.2f}")
        lines.append(f"  * Food & Snacks    : INR {day.food_cost_inr:,.2f}")
        lines.append(f"  * Hotel / Stay     : INR {day.accommodation_cost_inr:,.2f}")
        lines.append(f"  * Activity / Fees  : INR {day.activity_cost_inr:,.2f}")
        lines.append(f"  => Total for Day {day.day_number}: INR {day.total_daily_cost_inr:,.2f}")
        lines.append(divider_minor)

    if itinerary.practical_travel_tips:
        lines.append("")
        lines.append(divider_major)
        lines.append("                      PRACTICAL TRAVEL TIPS")
        lines.append(divider_major)
        for i, tip in enumerate(itinerary.practical_travel_tips, start=1):
            lines.append(f" {i}. {tip}")
        lines.append("")

    lines.append(divider_major)
    lines.append("DISCLAIMER:")
    lines.append(f"{itinerary.disclaimer}")
    lines.append(divider_major)
    lines.append("Generated with Google Gemini GenAI & Streamlit.")

    return "\n".join(lines)
