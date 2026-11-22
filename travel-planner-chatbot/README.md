# ✈️ AI-Powered Travel Planner Chatbot

A Generative AI web application that automatically creates realistic, day-wise travel itineraries with estimated expenses, interactive conversational assistance, and one-click PDF/TXT report downloads. Built with **Python**, **Streamlit**, and the **Google Gemini API**.

---

## 1. Project Overview

### 1.1 Problem Statement
Planning a multi-day trip is tedious and time-consuming. Travelers spend hours searching fragmented websites for attractions, coordinating daily schedules, calculating realistic costs across transportation, lodging, dining, and activities, and attempting to fit their plans within a strict budget. 

### 1.2 Objectives
- Develop an intuitive AI-driven travel planning assistant that aggregates personalized recommendations into a structured day-by-day plan.
- Provide practical cost estimates in Indian Rupees (INR) across four key expense categories (Stay, Food, Local Transport, Activities).
- Enable users to interactively refine their itinerary via a conversational chatbot with memory of the current trip.
- Offer export options to download the finalized travel plan as a clean PDF document or plain-text file.
- Implement robust input validation, API key management, and graceful error handling suitable for academic evaluation.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **User Interface** | [Streamlit](https://streamlit.io/) | Modern, reactive web interface with tabs, forms, and metric cards |
| **Backend & Logic** | Python 3.10+ | Application logic, session management, and data transformation |
| **Generative AI** | [Google Gemini API](https://ai.google.dev/) (`google-genai` SDK) | Structured itinerary generation and conversational Q&A |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Strict JSON schema enforcement and data modeling |
| **Data Display** | [Pandas](https://pandas.pydata.org/) | Day-wise expense comparison tables and metric analytics |
| **Document Export** | [ReportLab](https://www.reportlab.com/) | Programmatic PDF compilation with custom tables and typography |
| **Environment** | [python-dotenv](https://github.com/theskumar/python-dotenv) | Secure API key management from `.env` file |

---

## 3. Key Application Features

### 📝 A. Comprehensive User Input Form
- **Destination & Origin:** Specify any destination city/country and starting point.
- **Trip Duration:** Configurable duration from 1 to 15 days.
- **Budget in INR:** Tailored expense calculations adhering to stated budget.
- **Travel Style:** Choose between *Budget*, *Moderate*, and *Luxury*.
- **Travel Interests:** Multi-select options including Adventure, Nature, History, Local Food, Shopping, Beaches, and Photography.
- **Seasonal & Custom Notes:** Factor in weather, traveling month, and special requests (e.g., pure vegetarian, senior citizen friendly).

### 🤖 B. Structured AI Itinerary Generation
- Generates a day-wise schedule broken down into **Morning**, **Afternoon**, and **Evening** activities.
- Geographically clustered attractions to avoid unnecessary transit and fatigue.
- Day-by-day itemized cost estimations (INR) for:
  - Local Transportation (metro, cabs, auto-rickshaws, rentals)
  - Food & Dining (authentic regional cuisine recommendations)
  - Hotel / Accommodation
  - Sightseeing / Entry Tickets
- Mathematical consistency validation ensuring all daily totals match trip-level sums.
- Clear disclaimers stating all figures are approximate planning estimates.

### 💬 C. Context-Aware Travel Chatbot
- Retains full context of the active itinerary during the session.
- Handles follow-up queries such as:
  - *"Can you make this trip cheaper?"*
  - *"Suggest authentic vegetarian restaurants."*
  - *"Add adventure activities to Day 2."*
  - *"What should I pack for this season?"*
- Features one-click **"Apply Modifications to Itinerary"** to automatically regenerate and update the master plan, tables, and PDF.

### 📥 D. Document Downloads
- **PDF Export:** Polished document layout with title, overview, key metric tables, category breakdown, day-by-day itineraries, practical travel tips, and page numbers (`Page X of Y`).
- **TXT Export:** Formatted plain-text document designed for quick sharing via email or messaging apps.

### 🛡️ E. Error Handling & Academic Demo Mode
- **No-Key Launch:** The application launches cleanly even if an API key is not yet configured.
- **Built-in Demo Mode:** Includes a **"Load Demo"** button in the sidebar that loads a sample 3-day Jaipur trip without consuming API quota or requiring network access—ideal for live university presentations.
- Graceful API error handling for invalid keys, rate limits, or network interruptions.

---

## 4. Project Structure

```
travel-planner-chatbot/
│
├── app.py                     # Main Streamlit web application & UI
├── requirements.txt           # Project dependencies
├── .env.example               # Template for environment variables
├── .gitignore                 # Files excluded from version control
├── README.md                  # Complete project documentation
│
├── utils/                     # Utility modules
│   ├── __init__.py            # Package initialization & exports
│   ├── gemini_client.py       # Google GenAI client, validation, & model selection
│   ├── itinerary_generator.py # Pydantic schemas, system prompts, & AI generation
│   ├── pdf_generator.py       # ReportLab PDF creation with custom styles & tables
│   └── text_generator.py      # Plain-text formatted itinerary generator
│
└── tests/
    └── test_travel_planner.py # Unit tests for models, math logic, PDF, & TXT
```

---

## 5. Installation and Setup

### Step 1: Clone or Navigate to the Workspace
```bash
cd travel-planner-chatbot
```

### Step 2: Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. Gemini API Key Configuration

1. Obtain a free API key from **[Google AI Studio](https://aistudio.google.com/app/apikey)**.
2. Create a `.env` file in the project root directory:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and insert your key:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   ```
4. *Alternative:* You can also paste your Gemini API key directly into the application sidebar at runtime.

---

## 7. Running the Application

Execute the following command in your terminal:

```bash
streamlit run app.py
```

Streamlit will automatically launch the web interface in your default browser at `http://localhost:8501`.

---

## 8. Example Walkthrough

### Example Input
- **Destination:** Manali, Himachal Pradesh
- **Starting City:** Chandigarh
- **Duration:** 3 Days
- **Total Budget:** ₹25,000
- **Travelers:** 2
- **Travel Style:** Moderate
- **Interests:** Adventure & Trekking, Nature & Landscapes, Food & Local Cuisine
- **Season:** Winter (Dec - Feb)
- **Special Request:** Pure vegetarian dining preferred

### Expected Output
1. **Summary Banner:** Trip overview, status (`Within Budget`), total estimated expense (~₹21,500), and savings (~₹3,500).
2. **Day 1 Plan:** Solang Valley snow activities, Mall Road exploration, Old Manali cafes, and daily cost breakdown.
3. **Day 2 Plan:** Atal Tunnel excursion, Sissu waterfall view in Lahaul Valley, evening bonfires.
4. **Day 3 Plan:** Hadimba Temple visit, Vashisht hot springs, souvenir shopping, and departure.
5. **Interactive Tabs:** Visual expense distribution bar chart, day-by-day Pandas comparison table, interactive chatbot assistant, and instant PDF download.

---

## 9. Running Verification Tests

To verify that all models, mathematical validation logic, PDF compilation, and plain-text export work properly:

```bash
python -m unittest tests/test_travel_planner.py
```

Expected output:
```
Ran 5 tests in 0.05s
OK
```

---

## 10. Limitations & Future Scope

### Current Limitations
- **Approximate Pricing:** Hotel rates, taxi fares, and attraction entry fees are realistic approximations and not live reservations.
- **API Quota:** Generation relies on Google AI Studio API rate limits.
- **Offline Generation:** Live LLM generation requires an active internet connection (though the built-in Demo mode works fully offline).

### Future Enhancements
- Integration with live booking APIs (e.g., Google Flights, Booking.com, IRCTC) for real-time fares.
- Interactive map visualization using Folium / Mapbox to display GPS routes and travel trails.
- Multi-currency support (USD, EUR, GBP) alongside INR.
- User accounts and cloud database storage (SQLite / PostgreSQL) to save and revisit past trips.

---

## 11. Author & Acknowledgements
- **Author:** B.Tech Final Year Student
- **Project Title:** AI-Powered Travel Planner Chatbot
- **Evaluation:** Mini-Project Assignment (10 Marks)
- **Built With:** Google Gemini AI, Streamlit, and ReportLab
