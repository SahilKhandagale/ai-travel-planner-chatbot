"""
Unit and Integration Verification Suite
Tests data modeling, mathematical consistency, PDF creation,
TXT creation, and API key handling.
"""

import unittest
from utils.gemini_client import validate_api_key, get_api_key
from utils.itinerary_generator import (
    ItineraryData,
    DayPlan,
    AttractionItem,
    enforce_mathematical_consistency,
    EXAMPLE_JSON_RESPONSE,
)
from utils.pdf_generator import create_itinerary_pdf
from utils.text_generator import create_itinerary_text


class TestTravelPlannerApp(unittest.TestCase):

    def setUp(self):
        """Set up standard sample data for test fixtures."""
        self.day1 = DayPlan(
            day_number=1,
            day_title="Arrival & Beach Exploration",
            morning_activities="Land at airport and transfer to hotel in Baga.",
            afternoon_activities="Seafood lunch and water sports at Calangute Beach.",
            evening_activities="Sunset walk and dinner at Tito's Lane.",
            suggested_attractions=[
                AttractionItem(name="Calangute Beach", description="Popular beach with water sports", entry_fee_inr=0.0),
                AttractionItem(name="Aguada Fort", description="17th century lighthouse and fort", entry_fee_inr=50.0),
            ],
            transportation_cost_inr=1000.0,
            food_cost_inr=1500.0,
            accommodation_cost_inr=3000.0,
            activity_cost_inr=500.0,
            total_daily_cost_inr=6000.0,
        )

        self.itinerary = ItineraryData(
            destination="Goa",
            starting_city="Mumbai",
            duration_days=1,
            travelers_count=2,
            travel_style="Moderate",
            trip_overview="A relaxing beach holiday in North Goa.",
            user_budget_inr=10000.0,
            total_estimated_cost_inr=6000.0,
            total_transport_cost_inr=1000.0,
            total_food_cost_inr=1500.0,
            total_accommodation_cost_inr=3000.0,
            total_activities_cost_inr=500.0,
            budget_status="Within Budget",
            budget_difference_inr=4000.0,
            budget_breakdown_explanation="Trip is comfortably within budget.",
            days=[self.day1],
            practical_travel_tips=["Rent a scooter", "Carry sunscreen"],
        )

    def test_api_key_validation(self):
        """Test API key validation logic."""
        is_valid, msg = validate_api_key(None)
        # In environment without key, it should safely return False
        self.assertFalse(is_valid)

        is_valid, msg = validate_api_key("too_short")
        self.assertFalse(is_valid)

        is_valid, msg = validate_api_key("AIzaSyFakeKeyWithSufficientLength12345")
        self.assertTrue(is_valid)

    def test_mathematical_consistency(self):
        """Verify that enforce_mathematical_consistency correctly computes all totals."""
        day2 = DayPlan(
            day_number=2,
            day_title="South Goa Churches",
            morning_activities="Visit Basilica of Bom Jesus.",
            afternoon_activities="Spice plantation tour and traditional lunch.",
            evening_activities="Colva beach sunset.",
            suggested_attractions=[],
            transportation_cost_inr=1200.0,
            food_cost_inr=1600.0,
            accommodation_cost_inr=3000.0,
            activity_cost_inr=400.0,
            total_daily_cost_inr=0.0,  # Deliberately uncomputed
        )
        itinerary = ItineraryData(
            destination="Goa",
            starting_city="Mumbai",
            duration_days=2,
            travelers_count=2,
            travel_style="Moderate",
            trip_overview="Two day Goa tour",
            user_budget_inr=15000.0,
            total_estimated_cost_inr=0.0,
            total_transport_cost_inr=0.0,
            total_food_cost_inr=0.0,
            total_accommodation_cost_inr=0.0,
            total_activities_cost_inr=0.0,
            budget_status="",
            budget_difference_inr=0.0,
            budget_breakdown_explanation="Test explanation",
            days=[self.day1, day2],
        )

        reconciled = enforce_mathematical_consistency(itinerary, user_budget=15000.0)

        # Day 1: 1000 + 1500 + 3000 + 500 = 6000
        self.assertEqual(reconciled.days[0].total_daily_cost_inr, 6000.0)
        # Day 2: 1200 + 1600 + 3000 + 400 = 6200
        self.assertEqual(reconciled.days[1].total_daily_cost_inr, 6200.0)
        # Grand total: 6000 + 6200 = 12200
        self.assertEqual(reconciled.total_estimated_cost_inr, 12200.0)
        # Transport: 1000 + 1200 = 2200
        self.assertEqual(reconciled.total_transport_cost_inr, 2200.0)
        # Food: 1500 + 1600 = 3100
        self.assertEqual(reconciled.total_food_cost_inr, 3100.0)
        # Stay: 3000 + 3000 = 6000
        self.assertEqual(reconciled.total_accommodation_cost_inr, 6000.0)
        # Activities: 500 + 400 = 900
        self.assertEqual(reconciled.total_activities_cost_inr, 900.0)
        # Budget diff: 15000 - 12200 = 2800 (positive savings)
        self.assertEqual(reconciled.budget_difference_inr, 2800.0)
        self.assertEqual(reconciled.budget_status, "Within Budget")

    def test_pdf_generation(self):
        """Test PDF generation produces valid non-empty PDF bytes."""
        pdf_bytes = create_itinerary_pdf(self.itinerary)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        # Standard PDF magic header
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_text_generation(self):
        """Test plain text itinerary generation."""
        txt_output = create_itinerary_text(self.itinerary)
        self.assertIsInstance(txt_output, str)
        self.assertIn("AI-POWERED TRAVEL PLANNER", txt_output)
        self.assertIn("Goa", txt_output)
        self.assertIn("INR 6,000.00", txt_output)
        self.assertIn("DAY 1", txt_output)
        self.assertIn("Calangute Beach", txt_output)

    def test_example_json_parsing(self):
        """Test that the provided EXAMPLE_JSON_RESPONSE parses into ItineraryData cleanly."""
        parsed = ItineraryData.model_validate_json(EXAMPLE_JSON_RESPONSE)
        self.assertEqual(parsed.destination, "Goa")
        self.assertEqual(len(parsed.days), 1)
        self.assertEqual(parsed.days[0].day_number, 1)


if __name__ == "__main__":
    unittest.main()
