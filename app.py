"""
AI-Powered Travel Planner Chatbot
Streamlit Web Application
B.Tech Final Year GenAI Mini-Project
"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

from utils.gemini_client import get_api_key, validate_api_key, DEFAULT_MODEL
from utils.itinerary_generator import (
    generate_itinerary,
    chat_with_itinerary,
    modify_itinerary_with_chat,
    ItineraryData,
    DayPlan,
    AttractionItem,
)
from utils.pdf_generator import create_itinerary_pdf
from utils.text_generator import create_itinerary_text

# ============================================================================
# Page Configuration & Styling
# ============================================================================

st.set_page_config(
    page_title="AI Travel Planner Chatbot",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Travel Theme UI
CUSTOM_CSS = """
<style>
    /* Main container and typography */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0D9488 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white !important;
        margin: 0 0 8px 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .main-header p {
        color: #E2E8F0 !important;
        font-size: 1.05rem;
        margin: 0;
    }
    
    /* Card containers */
    .travel-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Badges */
    .badge-budget {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-alert {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Activity timing tags */
    .time-slot-title {
        font-weight: 600;
        color: #1E3A8A;
        margin-top: 8px;
        margin-bottom: 4px;
    }

    /* Disclaimer box */
    .disclaimer-box {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #92400E;
        margin-top: 20px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# Session State Initialization
# ============================================================================

if "itinerary" not in st.session_state:
    st.session_state["itinerary"] = None

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

if "api_key_input" not in st.session_state:
    st.session_state["api_key_input"] = os.getenv("GEMINI_API_KEY", "")


# ============================================================================
# Built-In Demo Itinerary (For Offline / Instant Viva Demonstration)
# ============================================================================

def get_demo_itinerary() -> ItineraryData:
    """Returns a realistic pre-compiled 3-day itinerary for instant evaluation demonstration."""
    day1 = DayPlan(
        day_number=1,
        day_title="Arrival & Royal Pink City Heritage",
        morning_activities="Arrive in Jaipur, check into a heritage haveli near MI Road, and visit the iconic Hawa Mahal (Palace of Winds) for photography.",
        afternoon_activities="Explore City Palace complex and museum, followed by authentic Rajasthani Dal Baati Churma lunch at LMB in Johari Bazaar.",
        evening_activities="Stroll through Bapu Bazaar for handicrafts and lac bangles, followed by sunset view from Nahargarh Fort.",
        suggested_attractions=[
            AttractionItem(name="Hawa Mahal", description="Famed 5-story pink sandstone palace with 953 jharokhas", entry_fee_inr=50.0),
            AttractionItem(name="City Palace Jaipur", description="Royal residence showcasing Rajasthani and Mughal architecture", entry_fee_inr=300.0),
            AttractionItem(name="Nahargarh Fort", description="Hilltop fortress offering sweeping sunset vistas of Jaipur city", entry_fee_inr=50.0),
        ],
        transportation_cost_inr=800.0,
        food_cost_inr=1400.0,
        accommodation_cost_inr=2800.0,
        activity_cost_inr=800.0,
        total_daily_cost_inr=5800.0,
    )

    day2 = DayPlan(
        day_number=2,
        day_title="Majestic Forts & Artisan Workshops",
        morning_activities="Drive to Amer (11 km) to explore the grand Amber Fort and Sheesh Mahal (Mirror Palace) early morning before peak crowds.",
        afternoon_activities="Visit Jaigarh Fort to see Jaivana (world's largest wheeled cannon), then lunch at a rooftop cafe near Jal Mahal.",
        evening_activities="Photo stop at Jal Mahal (Water Palace) in Man Sagar Lake, followed by a visit to traditional block printing workshops in Sanganer.",
        suggested_attractions=[
            AttractionItem(name="Amber Fort", description="UNESCO World Heritage hill fort with ornate courtyards", entry_fee_inr=100.0),
            AttractionItem(name="Jaigarh Fort", description="Military fort overlooking Maota Lake housing royal armory", entry_fee_inr=70.0),
            AttractionItem(name="Jal Mahal", description="Serene palace submerged in the middle of Man Sagar Lake", entry_fee_inr=0.0),
        ],
        transportation_cost_inr=900.0,
        food_cost_inr=1500.0,
        accommodation_cost_inr=2800.0,
        activity_cost_inr=340.0,
        total_daily_cost_inr=5540.0,
    )

    day3 = DayPlan(
        day_number=3,
        day_title="Astronomy, Culture & Local Flavors",
        morning_activities="Visit Jantar Mantar (UNESCO astronomical observatory), marvel at the world's largest stone sundial.",
        afternoon_activities="Visit Albert Hall Museum for Indo-Saracenic architecture and historical artifacts, followed by lunch at Tapri Central.",
        evening_activities="Taste Jaipur's famous lassi at Lassiwala on MI Road, souvenir shopping, and departure transfer.",
        suggested_attractions=[
            AttractionItem(name="Jantar Mantar", description="18th-century stone astronomical instruments designed by Jai Singh II", entry_fee_inr=50.0),
            AttractionItem(name="Albert Hall Museum", description="Oldest museum in Rajasthan with rare paintings and costumes", entry_fee_inr=40.0),
        ],
        transportation_cost_inr=700.0,
        food_cost_inr=1200.0,
        accommodation_cost_inr=0.0,
        activity_cost_inr=180.0,
        total_daily_cost_inr=2080.0,
    )

    return ItineraryData(
        destination="Jaipur, Rajasthan",
        starting_city="Delhi",
        duration_days=3,
        travelers_count=2,
        travel_style="Moderate",
        trip_overview="A cultural 3-day exploration of Rajasthan's Pink City, balancing UNESCO forts, royal palaces, bazaars, and authentic Rajasthani gastronomy.",
        user_budget_inr=20000.0,
        total_estimated_cost_inr=13420.0,
        total_transport_cost_inr=2400.0,
        total_food_cost_inr=4100.0,
        total_accommodation_cost_inr=5600.0,
        total_activities_cost_inr=1320.0,
        budget_status="Within Budget",
        budget_difference_inr=6580.0,
        budget_breakdown_explanation="The 3-day itinerary is estimated at INR 13,420 for 2 travelers, remaining well below your INR 20,000 budget with a comfortable buffer of INR 6,580 for shopping or train tickets.",
        days=[day1, day2, day3],
        practical_travel_tips=[
            "Purchase the composite entry ticket at Amber Fort to save both money and queuing time for Jantar Mantar, Hawa Mahal, and Albert Hall.",
            "Use e-rickshaws or ride-hailing apps (Uber/Ola) for fixed fair transit inside old walled city areas.",
            "Carry a scarf and comfortable slip-on walking shoes when touring palaces and temples.",
            "Stay hydrated and sample authentic snacks like Pyaaz Kachori at Rawat Mishtan Bhandar.",
        ],
        disclaimer="Note: All costs and fares are approximate estimates in INR for academic and planning purposes. No real-time bookings have been made.",
    )


# ============================================================================
# Sidebar Configuration
# ============================================================================

with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; padding: 12px 0;">
            <span style="font-size: 3rem;">🧭 ✈️ 🗺️</span>
            <h3 style="margin: 8px 0 0 0; color: #1E3A8A;">Trip Settings</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🔑 Google Gemini API Key")
    active_key = get_api_key(st.session_state["api_key_input"])

    sidebar_key = st.text_input(
        "Enter Gemini API Key:",
        value=st.session_state["api_key_input"],
        type="password",
        placeholder="AIzaSy...",
        help="Paste your Google AI Studio API key here. Loaded from .env if present.",
    )
    if sidebar_key != st.session_state["api_key_input"]:
        st.session_state["api_key_input"] = sidebar_key

    is_valid, key_msg = validate_api_key(st.session_state["api_key_input"])
    if is_valid:
        st.success("🟢 API Key Configured")
    else:
        st.warning("🔴 API Key Missing")
        with st.expander("❓ How to get a free API Key"):
            st.markdown(
                """
                1. Visit **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
                2. Sign in with your Google account.
                3. Click **'Create API Key'**.
                4. Paste the key in this box or create a `.env` file with:
                   `GEMINI_API_KEY=your_key_here`
                """
            )

    st.divider()

    st.subheader("🛠️ Demo & Reset")
    col_demo, col_reset = st.columns(2)
    with col_demo:
        if st.button("🧪 Load Demo", help="Load sample Jaipur itinerary without needing an API key"):
            st.session_state["itinerary"] = get_demo_itinerary()
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": "Welcome! I have loaded a sample 3-day Jaipur trip. Feel free to explore the schedule, examine costs, download the PDF, or ask me questions below."}
            ]
            st.success("Demo loaded!")
            st.rerun()

    with col_reset:
        if st.button("🗑️ Clear All", help="Reset all state"):
            st.session_state["itinerary"] = None
            st.session_state["chat_messages"] = []
            st.rerun()

    st.divider()
    st.markdown("### 🎓 Project Details")
    st.caption("**Project:** AI Travel Planner Chatbot")
    st.caption("**Scope:** B.Tech Final Year Mini-Project")
    st.caption("**Tech Stack:** Python, Streamlit, Google Gemini LLM, ReportLab, Pandas")


# ============================================================================
# Main Header
# ============================================================================

st.markdown(
    """
    <div class="main-header">
        <h1>✈️ AI-Powered Travel Planner Chatbot</h1>
        <p>Personalized, day-wise travel itineraries with realistic cost estimation, interactive Q&A assistant, and instant PDF/TXT export.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# User Input Form
# ============================================================================

with st.expander("📝 Plan Your Next Adventure (Input Form)", expanded=(st.session_state["itinerary"] is None)):
    with st.form(key="travel_planner_form"):
        st.markdown("##### 📍 Destination & Duration")
        c1, c2, c3 = st.columns([2, 2, 1.5])
        with c1:
            destination_input = st.text_input(
                "Destination City or Country *",
                value="Manali, Himachal Pradesh",
                placeholder="e.g. Manali, Goa, Tokyo, Paris",
            )
        with c2:
            starting_city_input = st.text_input(
                "Starting City *",
                value="Chandigarh",
                placeholder="e.g. Delhi, Mumbai, Bengaluru",
            )
        with c3:
            days_input = st.number_input(
                "Trip Duration (Days) *",
                min_value=1,
                max_value=15,
                value=3,
                step=1,
            )

        st.markdown("##### 💰 Budget & Traveler Style")
        c4, c5, c6 = st.columns([2, 1.5, 1.5])
        with c4:
            budget_input = st.number_input(
                "Total Budget in INR (₹) *",
                min_value=2000,
                max_value=1000000,
                value=25000,
                step=1000,
                help="Total allocated spending in Indian Rupees for the entire group.",
            )
        with c5:
            travelers_input = st.number_input(
                "Number of Travelers *",
                min_value=1,
                max_value=15,
                value=2,
                step=1,
            )
        with c6:
            style_input = st.selectbox(
                "Travel Style *",
                options=["Budget", "Moderate", "Luxury"],
                index=1,
                help="Budget (hostels/local buses), Moderate (3-star/cabs), Luxury (5-star/resorts)",
            )

        st.markdown("##### 🎯 Interests & Seasonal Preferences")
        c7, c8 = st.columns([2.5, 1.5])
        with c7:
            interests_options = [
                "Adventure & Trekking",
                "Nature & Landscapes",
                "History & Heritage",
                "Food & Local Cuisine",
                "Shopping & Bazaars",
                "Beaches & Water Sports",
                "Relaxation & Wellness",
                "Culture & Spiritual",
                "Nightlife & Entertainment",
                "Photography & Scenic Spots",
            ]
            interests_input = st.multiselect(
                "Travel Interests (Select all that apply):",
                options=interests_options,
                default=["Adventure & Trekking", "Nature & Landscapes", "Food & Local Cuisine"],
            )
        with c8:
            season_input = st.selectbox(
                "Preferred Season / Month (Optional):",
                options=[
                    "Any Season / Best Weather",
                    "Winter (Dec - Feb / Snow & Chills)",
                    "Spring (Mar - Apr / Pleasant)",
                    "Summer (May - Jun / Hill Stations)",
                    "Monsoon (Jul - Sep / Lush Green)",
                    "Autumn (Oct - Nov / Festivals)",
                ],
                index=0,
            )

        special_requests_input = st.text_input(
            "Special Requests or Dietary Preferences (Optional):",
            value="Pure vegetarian dining preferred, love scenic viewpoints",
            placeholder="e.g. Traveling with senior citizens, vegetarian dining, prefer walking tours",
        )

        submit_button = st.form_submit_button("🚀 Generate My Trip", type="primary", use_container_width=True)

    # Form Submission Handling
    if submit_button:
        # Validate inputs
        if not destination_input.strip():
            st.error("⚠️ Please specify a destination.")
        elif not starting_city_input.strip():
            st.error("⚠️ Please specify a starting city.")
        elif budget_input <= 0:
            st.error("⚠️ Budget must be greater than INR 0.")
        else:
            api_key = get_api_key(st.session_state["api_key_input"])
            if not api_key:
                st.error("❌ Gemini API Key is missing! Please configure your key in the sidebar or `.env` file.")
                st.info("💡 Tip: You can click '🧪 Load Demo' in the sidebar to test all app features without an API key.")
            else:
                with st.spinner(f"✨ Consulting Google Gemini to curate your personalized {days_input}-day {destination_input} trip..."):
                    try:
                        itinerary = generate_itinerary(
                            destination=destination_input.strip(),
                            days=int(days_input),
                            budget_inr=float(budget_input),
                            starting_city=starting_city_input.strip(),
                            interests=interests_input,
                            travelers_count=int(travelers_input),
                            travel_style=style_input,
                            travel_season=season_input,
                            special_requests=special_requests_input.strip(),
                            api_key=api_key,
                        )
                        st.session_state["itinerary"] = itinerary
                        st.session_state["chat_messages"] = [
                            {
                                "role": "assistant",
                                "content": (
                                    f"I have crafted your personalized **{itinerary.duration_days}-day itinerary for {itinerary.destination}**! "
                                    f"The total estimated cost is **INR {itinerary.total_estimated_cost_inr:,.0f}** ({itinerary.budget_status}). "
                                    "Feel free to ask follow-up questions, suggest modifications, or request restaurant recommendations below!"
                                ),
                            }
                        ]
                        st.success("🎉 Itinerary successfully generated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to generate itinerary: {str(e)}")
                        st.info("Verify your Gemini API key has access to standard models or check your network connection.")


# ============================================================================
# Itinerary Display & Analysis Section
# ============================================================================

itinerary: ItineraryData = st.session_state["itinerary"]

if itinerary is not None:
    st.divider()

    # 1. Hero Summary Metrics Bar
    st.markdown(f"### 📍 {itinerary.destination} ({itinerary.duration_days} Days)")
    st.write(f"*{itinerary.trip_overview}*")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Total Allocated Budget",
            value=f"₹{itinerary.user_budget_inr:,.0f}",
            help="Your stated maximum budget in INR",
        )
    with m2:
        st.metric(
            label="Total Estimated Cost",
            value=f"₹{itinerary.total_estimated_cost_inr:,.0f}",
            help="Sum of all daily transportation, dining, stay, and activities",
        )
    with m3:
        diff = itinerary.budget_difference_inr
        delta_str = f"₹{diff:,.0f} {'Saved' if diff >= 0 else 'Deficit'}"
        st.metric(
            label="Budget Variance",
            value=itinerary.budget_status,
            delta=delta_str,
            delta_color="normal" if diff >= 0 else "inverse",
        )
    with m4:
        per_person = itinerary.total_estimated_cost_inr / max(1, itinerary.travelers_count)
        st.metric(
            label="Cost Per Traveler",
            value=f"₹{per_person:,.0f}",
            help=f"Estimated share for each of the {itinerary.travelers_count} traveler(s)",
        )

    # 2. Main Tabs
    tab_itinerary, tab_budget, tab_chat, tab_downloads = st.tabs([
        "📅 Day-wise Itinerary",
        "📊 Budget & Expense Breakdown",
        "💬 Trip Assistant Chatbot",
        "📥 Download Itinerary (PDF / TXT)",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Day-Wise Itinerary
    # -------------------------------------------------------------------------
    with tab_itinerary:
        st.subheader("🗓️ Day-by-Day Schedule")

        for day in itinerary.days:
            with st.expander(f"📍 Day {day.day_number}: {day.day_title} — Total Est: ₹{day.total_daily_cost_inr:,.0f}", expanded=(day.day_number == 1)):
                col_left, col_right = st.columns([2.5, 1.5])

                with col_left:
                    st.markdown("##### ⏰ Activities & Schedule")
                    st.markdown(f"🌅 **Morning:** {day.morning_activities}")
                    st.markdown(f"☀️ **Afternoon:** {day.afternoon_activities}")
                    st.markdown(f"🌙 **Evening:** {day.evening_activities}")

                    if day.suggested_attractions:
                        st.markdown("##### 🏛️ Key Attractions & Highlights")
                        for attr in day.suggested_attractions:
                            fee_badge = f"`₹{attr.entry_fee_inr:,.0f}`" if attr.entry_fee_inr > 0 else "`Free Entry`"
                            st.markdown(f"- **{attr.name}** {fee_badge}: {attr.description}")

                with col_right:
                    st.markdown("##### 💵 Day's Expense Breakdown")
                    day_expense_df = pd.DataFrame({
                        "Expense Category": ["Local Transport", "Food & Meals", "Hotel / Stay", "Activities & Entry"],
                        "Est. Cost (₹)": [
                            day.transportation_cost_inr,
                            day.food_cost_inr,
                            day.accommodation_cost_inr,
                            day.activity_cost_inr,
                        ],
                    })
                    st.dataframe(
                        day_expense_df.style.format({"Est. Cost (₹)": "₹{:,.0f}"}),
                        use_container_width=True,
                        hide_index=True,
                    )
                    st.info(f"**Day {day.day_number} Total:** ₹{day.total_daily_cost_inr:,.0f}")

        # Practical Tips Box
        if itinerary.practical_travel_tips:
            st.markdown("#### 💡 Practical Travel Tips")
            for tip in itinerary.practical_travel_tips:
                st.markdown(f"- {tip}")

        st.markdown(
            f'<div class="disclaimer-box">⚠️ <b>Disclaimer:</b> {itinerary.disclaimer}</div>',
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # TAB 2: Budget Breakdown & Analytics
    # -------------------------------------------------------------------------
    with tab_budget:
        st.subheader("📊 Expense Allocation & Analysis")

        col_b1, col_b2 = st.columns([1.5, 2])

        with col_b1:
            st.markdown("##### Category Totals (All Days)")
            category_df = pd.DataFrame({
                "Category": ["Hotel / Accommodation", "Food & Dining", "Local Transport", "Activities & Entry Fees"],
                "Total Cost (₹)": [
                    itinerary.total_accommodation_cost_inr,
                    itinerary.total_food_cost_inr,
                    itinerary.total_transport_cost_inr,
                    itinerary.total_activities_cost_inr,
                ],
            })
            total_sum = max(1.0, itinerary.total_estimated_cost_inr)
            category_df["Share (%)"] = (category_df["Total Cost (₹)"] / total_sum) * 100

            st.dataframe(
                category_df.style.format({
                    "Total Cost (₹)": "₹{:,.0f}",
                    "Share (%)": "{:.1f}%",
                }),
                use_container_width=True,
                hide_index=True,
            )

            st.success(f"**Grand Estimated Total:** ₹{itinerary.total_estimated_cost_inr:,.0f}")
            st.info(f"**Budget Allocation:** ₹{itinerary.user_budget_inr:,.0f}")

        with col_b2:
            st.markdown("##### Visual Expense Distribution")
            chart_data = category_df.set_index("Category")["Total Cost (₹)"]
            st.bar_chart(chart_data)

        st.markdown("##### 📝 AI Budget Explanation & Advice")
        st.write(itinerary.budget_breakdown_explanation)

        # Day-by-Day comparison table
        st.markdown("##### 📅 Day-by-Day Cost Comparison Table")
        days_table_data = []
        for d in itinerary.days:
            days_table_data.append({
                "Day": f"Day {d.day_number}",
                "Title": d.day_title,
                "Transport (₹)": d.transportation_cost_inr,
                "Food (₹)": d.food_cost_inr,
                "Stay (₹)": d.accommodation_cost_inr,
                "Activities (₹)": d.activity_cost_inr,
                "Day Total (₹)": d.total_daily_cost_inr,
            })
        days_df = pd.DataFrame(days_table_data)
        st.dataframe(
            days_df.style.format({
                "Transport (₹)": "₹{:,.0f}",
                "Food (₹)": "₹{:,.0f}",
                "Stay (₹)": "₹{:,.0f}",
                "Activities (₹)": "₹{:,.0f}",
                "Day Total (₹)": "₹{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    # -------------------------------------------------------------------------
    # TAB 3: Interactive Follow-Up Chatbot
    # -------------------------------------------------------------------------
    with tab_chat:
        st.subheader("💬 Ask Follow-up Questions & Customize Itinerary")
        st.caption("Ask questions about this trip, request vegetarian restaurants, or adjust activities and budget.")

        # Quick question pills for demonstration
        st.markdown("###### ⚡ Quick Questions:")
        quick_cols = st.columns(4)
        quick_prompts = [
            "Can you make this trip cheaper?",
            "Suggest authentic local vegetarian restaurants.",
            "Add more adventure activities to Day 2.",
            "What packing items do you recommend for this season?",
        ]
        chosen_quick_prompt = None
        for i, q_prompt in enumerate(quick_prompts):
            with quick_cols[i]:
                if st.button(q_prompt, key=f"quick_{i}", use_container_width=True):
                    chosen_quick_prompt = q_prompt

        # Display Chat History
        chat_container = st.container()
        with chat_container:
            for message in st.session_state["chat_messages"]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # Chat Input Bar
        user_query = st.chat_input("Type your question about this trip...") or chosen_quick_prompt

        if user_query:
            # Append user message
            st.session_state["chat_messages"].append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)

            api_key = get_api_key(st.session_state["api_key_input"])
            if not api_key:
                err_msg = "Please configure your Gemini API Key in the sidebar to chat with the AI assistant."
                st.session_state["chat_messages"].append({"role": "assistant", "content": err_msg})
                with st.chat_message("assistant"):
                    st.error(err_msg)
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            assistant_reply = chat_with_itinerary(
                                itinerary=itinerary,
                                chat_history=st.session_state["chat_messages"],
                                user_message=user_query,
                                api_key=api_key,
                            )
                            st.write(assistant_reply)
                            st.session_state["chat_messages"].append({"role": "assistant", "content": assistant_reply})
                        except Exception as e:
                            fail_msg = f"Sorry, I encountered an issue: {str(e)}"
                            st.error(fail_msg)
                            st.session_state["chat_messages"].append({"role": "assistant", "content": fail_msg})

        # Option to apply modifications and regenerate the structured itinerary
        st.divider()
        st.markdown("##### 🔄 Apply Changes to Master Itinerary")
        with st.expander("Apply Modifications & Regenerate Structured Plan"):
            st.write("If you discussed modifications with the chatbot (e.g. adding activities or reducing budget), enter your final modification instruction here to update the full schedule, tables, and PDF.")
            mod_input = st.text_input(
                "Enter modification instructions:",
                placeholder="e.g. Replace Day 2 activities with trekking and reduce daily hotel budget by 20%",
                key="mod_text_input",
            )
            if st.button("Apply Modifications to Itinerary", type="secondary"):
                api_key = get_api_key(st.session_state["api_key_input"])
                if not api_key:
                    st.error("API key required to modify itinerary.")
                elif not mod_input.strip():
                    st.warning("Please provide instructions on what to change.")
                else:
                    with st.spinner("Updating your full itinerary based on modifications..."):
                        try:
                            updated = modify_itinerary_with_chat(
                                current_itinerary=itinerary,
                                chat_history=st.session_state["chat_messages"],
                                modification_instructions=mod_input.strip(),
                                api_key=api_key,
                            )
                            st.session_state["itinerary"] = updated
                            st.session_state["chat_messages"].append({
                                "role": "assistant",
                                "content": f"✅ Itinerary successfully updated with instructions: '{mod_input}'! All tabs, tables, and PDF downloads have been updated.",
                            })
                            st.success("Itinerary updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to modify itinerary: {str(e)}")

    # -------------------------------------------------------------------------
    # TAB 4: Download Options (PDF & TXT)
    # -------------------------------------------------------------------------
    with tab_downloads:
        st.subheader("📥 Export & Download Your Itinerary")
        st.write("Generate clean, formatted documents of your complete day-wise trip and budget to carry while traveling.")

        col_d1, col_d2 = st.columns(2)

        # 1. PDF Download
        with col_d1:
            st.markdown("##### 📄 PDF Document")
            st.write("Includes formatted tables, trip summary, cost breakdown, day-by-day plans, and page numbers.")
            with st.spinner("Compiling PDF..."):
                try:
                    pdf_bytes = create_itinerary_pdf(itinerary)
                    clean_dest = "".join(c for c in itinerary.destination if c.isalnum() or c in (" ", "_")).rstrip()
                    pdf_filename = f"Itinerary_{clean_dest.replace(' ', '_')}_{itinerary.duration_days}Days.pdf"

                    st.download_button(
                        label="⬇️ Download Itinerary as PDF",
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Error compiling PDF: {str(e)}")

        # 2. TXT Download
        with col_d2:
            st.markdown("##### 📝 Plain-Text Document")
            st.write("Clean text format with clear section dividers, suitable for sharing via WhatsApp, email, or offline notes.")
            try:
                txt_data = create_itinerary_text(itinerary)
                clean_dest = "".join(c for c in itinerary.destination if c.isalnum() or c in (" ", "_")).rstrip()
                txt_filename = f"Itinerary_{clean_dest.replace(' ', '_')}_{itinerary.duration_days}Days.txt"

                st.download_button(
                    label="⬇️ Download Itinerary as TXT",
                    data=txt_data,
                    file_name=txt_filename,
                    mime="text/plain",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Error preparing text export: {str(e)}")

        st.divider()
        with st.expander("🔍 View Raw JSON Data (For Examiner / Technical Inspection)"):
            st.json(itinerary.model_dump())
