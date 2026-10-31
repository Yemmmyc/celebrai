# ✨ CelebrAI — AI-Powered Celebration & Event Planner

> **PromptWars Virtual Challenge 5 — Celebration & Event Planner Category**
> *Where Bespoke Celebration Aesthetics Meet Deterministic Financial Precision.*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![AI Engine](https://img.shields.io/badge/Google%20GenAI-Gemini%203.8%20Flash-8E75C2.svg)](https://aistudio.google.com/)
[![Tests](https://img.shields.io/badge/Test%20Suite-47%20Passed-2E6F68.svg)](tests/)
[![Live Demo](https://img.shields.io/badge/Streamlit%20Cloud-Live%20Application-FF4B4B.svg)](https://celebrai.streamlit.app/)
[![Repository](https://img.shields.io/badge/GitHub-Yemmmyc%2Fcelebrai-black.svg)](https://github.com/Yemmmyc/celebrai)

---

## 📖 Table of Contents

1. [Project Overview & Problem Statement](#project-overview--problem-statement)
2. [Challenge Context (PromptWars Challenge 5)](#challenge-context-promptwars-challenge-5)
3. [Implemented Features](#implemented-features)
4. [Application Screenshots](#application-screenshots)
5. [Technology Stack & Architecture](#technology-stack--architecture)
6. [How It Works (End-to-End Workflow)](#how-it-works-end-to-end-workflow)
7. [Repository Structure](#repository-structure)
8. [Prerequisites](#prerequisites)
9. [Local Installation & Startup](#local-installation--startup)
10. [Environment Variables & Configuration](#environment-variables--configuration)
11. [Gemini AI Availability and Resilient Fallback](#gemini-ai-availability-and-resilient-fallback)
12. [Financial Precision & Multi-Currency Handling](#financial-precision--multi-currency-handling)
13. [Database & Persistence Model](#database--persistence-model)
14. [Testing & Quality Assurance](#testing--quality-assurance)
15. [Deployment Guide (Streamlit Community Cloud)](#deployment-guide-streamlit-community-cloud)
16. [Security, Privacy & Repository Hygiene](#security-privacy--repository-hygiene)
17. [Confirmed Limitations & Future Roadmap](#confirmed-limitations--future-roadmap)
18. [Troubleshooting Guide](#troubleshooting-guide)
19. [Contributing Guidelines](#contributing-guidelines)
20. [License & Acknowledgements](#license--acknowledgements)
21. [Hackathon Submission Checklist](#hackathon-submission-checklist)

---

## 🎯 Project Overview & Problem Statement

### The Problem
Planning memorable celebrations—weddings, milestone birthdays, galas, and dinner parties—is fraught with friction. Event hosts and coordinators must navigate two conflicting disciplines:
- **Unconstrained Creative Vision**: Brainstorming evocative themes, cohesive color palettes, atmospheric decor, customized culinary menus, and guest activities.
- **Strict Operational Execution**: Balancing rigid budgets down to the penny, preventing unexpected vendor overruns, and coordinating intricate day-of schedules.

Traditional planning tools fail by doing either too little or too much: static spreadsheets lack creative inspiration, while generic AI chatbots hallucinate arithmetic, miscalculate line items, and mix foreign currencies indiscriminately.

### The CelebrAI Solution
**CelebrAI** is an intelligent, full-lifecycle celebration and event planning application built with **Streamlit**, **Python**, and **Google Gemini**. CelebrAI introduces an architectural boundary:
1. **Google Gemini** acts as the *Creative Event Director*, generating bespoke design concepts, mood narratives, color schemes, culinary highlights, and pro-tips validated against rigorous Pydantic schemas.
2. **Deterministic Python Algorithms** act as the *Financial Controller*, calculating penny-precision budget allocations, day-of run-of-show itineraries, and vendor rosters. **Budget arithmetic is never delegated to AI.**
3. **Local SQLite Persistence** provides thread-safe, transactional record-keeping for local celebration records.

---

## 🏆 Challenge Context (PromptWars Challenge 5)

CelebrAI was developed specifically for **PromptWars Virtual Challenge 5** under the **Celebration & Event Planner** category.

The challenge task asks builders to create software that eases celebration orchestration through generative AI. CelebrAI directly addresses this by providing:
- **Intelligent Ideation**: Personalized concepts tailored to the host's event category, location, guest size, and vibe preferences.
- **Deterministic Fallback Planning**: A built-in rule-based planning engine that maintains core celebration planning functionality when Google Gemini is unconfigured or unavailable, subject to the local application runtime functioning normally.
- **Budget Integrity**: Currency-segregated allocations across 4 international currencies (`USD`, `NGN`, `GBP`, `EUR`) preventing cross-currency contamination.
- **End-to-End Operational Tooling**: Interactive vendor procurement checklists, milestone schedules, and day-of minute-by-minute run-of-show tracking.

> [!NOTE]
> This project is an independent hackathon entry submitted to PromptWars Virtual Challenge 5. No official competition award, ranking, or judging endorsement is claimed.

---

## ✨ Implemented Features

Every feature listed below is verified and implemented in the active codebase:

### 1. Executive Dashboard (`page_dashboard`)
- **Portfolio KPIs**: Real-time metric cards displaying Total Celebrations, Total Planned Budget, Total Committed Spend, Honored Guests, and Next Celebration countdown.
- **Upcoming Celebration Spotlight**: Hero card highlighting the next chronological event with date, location, guest count, budget, and theme badge.
- **Currency-Safe Budget Visualization**: Horizontal Altair bar chart breaking down budgets by event type. Groups budgets strictly by currency into isolated tabs (`USD`, `NGN`, `GBP`, `EUR`) to prevent nominal sum distortion.
- **Recent Celebrations Portfolio**: Data table displaying recent events with formatted budgets, guests, status, and currency codes.
- **Portfolio Onboarding State**: Clean empty state greeting new hosts when no celebrations are saved.

### 2. Bespoke Celebration Creator (`page_create_event`)
- **8 Event Categories**: Full support for Weddings, Birthdays, Corporate Galas, Anniversaries, Baby Showers, Dinner Parties, Holiday Parties, and Custom celebrations.
- **Multi-Currency Selection**: Native support for US Dollar (`$ USD`), Nigerian Naira (`₦ NGN`), British Pound (`£ GBP`), and Euro (`€ EUR`).
- **Comprehensive Specifications**: Configurable event date, guest count, location/venue, total budget, desired theme vibe, and host notes.
- **Strict Deterministic Validation**: Pre-generation validation checking non-empty names/venues, positive guest counts, valid ISO `YYYY-MM-DD` dates, and supported currencies before executing any AI calls.

### 3. AI-Powered Creative Planning & Styling Engine
- **Structured Schema Generation**: Calls Google Gemini (`gemini-3.8-flash`) requesting structured JSON mapped directly to the `AIEventPlan` Pydantic model.
- **Theme Concept & Mood Description**: Evocative 2-3 sentence overview setting lighting, ambiance, and emotional tone.
- **4-Swatch Palette**: Curated color schemes with descriptive hex tones.
- **Decor Highlights**: Signature tactile staging concepts (centerpieces, backdrop ideas, ambient lighting).
- **Culinary & Beverage Concepts**: Welcome signature cocktails, artisanal hors d'oeuvres, and dessert station ideas.
- **Interactive Entertainment**: Guest engagement ideas (bespoke perfume bars, audio guestbooks, vinyl sets).
- **Planner Pro-Tips**: Practical coordination advice tailored to the specific celebration specs.
- **Deterministic Offline Fallback**: If Gemini is unconfigured, times out, or returns a 503/429 error, CelebrAI seamlessly activates its built-in rule-based styling engine.

### 4. Financial Controller & Budget Planner (`page_budget_planner`)
- **7 Standardized Allocation Categories**:
  - Venue & Atmosphere (25%)
  - Catering & Mixology (35%)
  - Media & Photography (15%)
  - Decor & Floral Design (10%)
  - Music & Entertainment (8%)
  - Invitations & Print (3%)
  - Contingency Reserve (4%)
- **Penny-Precision Arithmetic**: Integer-cent rounding with remainder reconciliation into Catering ensuring that $\sum \text{allocated} = \text{budget}$ without math discrepancies.
- **Live Variance Tracking**: Real-time calculation of allocated targets vs. actual vendor invoices, with dynamic color-coded financial indicators.
- **Interactive Line-Item Invoicing**: Hosts can record actual vendor spend, notes, and invoice updates per line item.

### 5. Dynamic Milestones & Day-Of Run-of-Show (`page_timeline`)
- **Dual-Perspective Timeline**:
  - **Master Milestones Tab**: Tracks long-term preparation from 6+ months out down to 1 week out and the eve of celebration.
  - **Day-Of Run-of-Show Tab**: Minute-by-minute schedule covering vendor load-in, host arrival, guest reception, program highlights, and load-out.
- **Interactive Completion Toggles**: Clickable checkboxes that persist status changes directly to the database with visual progress tracking.

### 6. Vendor Roster & Procurement Checklist (`page_vendor_checklist`)
- **5 Standardized Vendor Specialties**: Caterer, Floral Stylist, Photographer, DJ/Band, and Venue Coordinator.
- **Procurement Workflow**: Stage transitions across `Needed`, `Researching`, `Contacted`, `Booked`, and `Paid`.
- **Financial Alignment**: Side-by-side comparison of estimated allocations vs actual contractual spend.
- **Direct Vendor Card Updates**: In-place status toggles and actual cost tracking.

### 7. Portfolio Management & Inspection (`page_my_events`)
- **Event Filtering**: Filter portfolio by category and status (`Planning`, `Confirmed`, `Completed`).
- **Deep Event Dossier**: Expandable accordion revealing the full Gemini creative plan, color palette badges, decor concepts, culinary ideas, and planner tips.
- **Status Updates & Cascading Deletion**: Change planning stage or remove celebrations with full database cascade.

---

## Application Screenshots

CelebrAI features a custom dark luxury theme configured via `.streamlit/config.toml` and centralized CSS, pairing Deep Plum-Black (`#100D14`), Charcoal-Plum (`#211A29`), Champagne Gold (`#C5A059`), and Muted Teal (`#2E6F68` / `#6CB8A8`) typography and components.

### 1. Executive Dashboard
*Portfolio KPI summary cards, upcoming celebration spotlight card, currency-segregated budget analytics tabs, and recent celebration portfolio table.*

![Executive Dashboard](screenshots/dashboard.png)

### 2. Create a New Celebration
*Bespoke celebration creator supporting 8 event categories, 4 international currencies (`USD`, `NGN`, `GBP`, `EUR`), guest count, budget specifications, and pre-generation validation.*

![Create a New Celebration](screenshots/create-celebration.png)

### 3. AI Event Plan — Deterministic Fallback
*Note: This captured example shows CelebrAI's deterministic rule-based planning engine activating after an external Google Gemini HTTP 504 timeout (Deadline Exceeded). All seven structured schema fields (`theme_concept`, `theme_description`, `color_palette`, `decor_highlights`, `menu_suggestions`, `entertainment_ideas`, `planner_pro_tips`) are synthesized deterministically and preserved to SQLite without data loss. (This demonstrates resilient fallback behavior, not a successful Gemini-generated response).*

![AI Event Plan — Deterministic Fallback](screenshots/ai-event-plan-fallback.png)

### 4. Budget Planner and Financial Allocation
*Penny-precision budget breakdown across the six categories actually visible, with discrepancy reconciliation into Catering, real-time variance tracking, and line-item actual invoice logging.*

![Budget Planner and Financial Allocation](screenshots/budget-planner.png)

### 5. Master Event Planning Timeline
*Milestone preparation roadmap tracking preparation from 6+ months out down to celebration eve, with interactive completion toggles persisted to SQLite.*

![Master Event Planning Timeline](screenshots/event-timeline.png)

### 6. Day-of Event Run-of-Show
*Scheduled event-day sequence covering vendor load-in, host arrival, reception highlights, and load-out with interactive progress tracking.*

![Day-of Event Run-of-Show](screenshots/day-of-run-of-show.png)

### 7. Expanded Celebration Details and Saved Plan
*Deep-inspection event accordion displaying the full creative narrative, 4-swatch color palette, tactile decor concepts, culinary suggestions, entertainment, and expert coordinator tips.*

![Expanded Celebration Details and Saved Plan](screenshots/expanded-event-details.png)

### 8. My Celebrations Portfolio
*Celebration portfolio management view featuring event status badges (`Planning`, `Confirmed`, `Completed`), category filters, and cascading deletion controls.*

![My Celebrations Portfolio](screenshots/my-events.png)

### 9. Vendor Checklist and Procurement Tracking
*Vendor management workflow tracking six vendor service roles across procurement stages (`Needed`, `Researching`, `Contacted`, `Booked`, `Paid`) with inline note persistence.*

![Vendor Checklist and Procurement Tracking](screenshots/vendor-checklist.png)

---

## 🏛️ Technology Stack & Architecture

### Core Dependencies
| Component | Package / Technology | Version Requirement | Purpose |
|---|---|---|---|
| **Runtime** | Python | `>= 3.10` (tested on 3.14) | Core application execution |
| **Frontend UI** | Streamlit | `>= 1.40.0` | Reactive web interface & controls |
| **AI Intelligence** | Google GenAI SDK (`google-genai`) | `>= 2.0.0` | Client for Gemini models (`gemini-3.8-flash`) |
| **Data Validation** | Pydantic | `>= 2.0.0` | Strict schema validation of AI payloads |
| **Visualization** | Altair | `>= 5.0.0` | Currency-safe declarative charts |
| **Data Analysis** | Pandas | `>= 2.0.0` | Tabular dataframes and aggregations |
| **Local Storage** | SQLite | Built-in | ACID transactional persistence |
| **Config Loader** | python-dotenv | `>= 1.0.0` | Local `.env` credential management |
| **Testing** | Pytest | `>= 8.0.0` | Automated regression test runner |

### Architectural Flow

```mermaid
graph TD
    User([Event Host / Planner]) <--> UI[Streamlit Frontend App\napp.py]

    subgraph Presentation & Control Layer
        UI -->|Validation Call| Val[Input Validation Engine\nservices/planner.py]
        UI -->|User Actions| EvHandler[Page Controllers\nDashboard, Budget, Timeline, Vendors]
    end

    subgraph Intelligence Layer
        EvHandler -->|Event Specs| AIService[AI Service\nservices/ai_service.py]
        AIService -->|1. Try API Call| Gemini[Google Gemini API\ngemini-3.8-flash]
        Gemini -->|JSON Response| SchemaValidator[Pydantic Schema\nAIEventPlan]
        SchemaValidator -->|Validated Concept| EvHandler

        AIService -.->|2. Fallback on Error/Missing Key| Fallback[Deterministic Planning Engine\nRule-Based Styling & Palettes]
        Fallback -->|Guaranteed Dossier| EvHandler
    end

    subgraph Financial & Scheduling Engine
        EvHandler -->|Budget Math| MathEngine[Deterministic Planner Math\nservices/planner.py]
        MathEngine -->|Penny Precision Math| Allocations[Penny-Balanced Budget Allocations\nVenue, Catering, Media, Decor, etc.]
        MathEngine -->|Itinerary Generation| Schedules[Milestones & Day-Of Run-of-Show]
    end

    subgraph Persistence Layer
        EvHandler <-->|CRUD Operations| DBService[SQLite Persistence Service\nservices/database.py]
        DBService <-->|Thread-Safe ACID| SQLite[(Local SQLite DB\ncelebrai.db)]
    end
```

---

## 🔄 How It Works (End-to-End Workflow)

1. **Celebration Definition**: The user opens **Create Event**, enters the title, selects the celebration category (e.g. Wedding, Birthday), picks the event date, specifies venue/city, chooses currency (`USD`, `NGN`, `GBP`, `EUR`), enters guest count and total budget, and describes theme vibes.
2. **Deterministic Pre-Validation**: [`validate_event_input()`](services/planner.py) inspects the submitted fields. If fields are blank, dates are malformed, or guest counts are negative, user-friendly error banners are rendered immediately.
3. **Dual-Mode Plan Generation**:
   - *Online Mode*: When `GEMINI_API_KEY` is present, [`generate_event_plan()`](services/ai_service.py) queries `gemini-3.8-flash` with a 15-second timeout and 2-attempt retry loop. The JSON output is parsed, markdown fences are stripped, and fields are validated with Pydantic.
   - *Offline / High-Demand Fallback*: If the API key is missing or Google returns a 503 (high demand) or 429 (rate limit), the deterministic engine instantly constructs a curated aesthetic plan with palettes, decor, and menus.
4. **Deterministic Financial & Timeline Allocation**: The Python planner automatically splits the budget into 7 balanced categories (reconciling odd pennies) and builds milestone and day-of schedules.
5. **Atomic Database Persistence**: [`save_event()`](services/database.py) executes a transactional commit writing the event, 7 budget line items, 10 timeline entries, and 5 vendor items into `celebrai.db`.
6. **Active Portfolio Management**: The user navigates to the **Dashboard**, **Budget Planner**, **Timeline**, or **Vendor Checklist** to adjust actual costs, log vendor notes, mark milestones complete, or update planning statuses.

---

## 📂 Repository Structure

```
celebrai/
├── app.py                  # Main Streamlit application (pages, layout, styling, controllers)
├── requirements.txt        # Runtime and testing dependencies
├── README.md               # Architectural documentation, setup, and submission report
├── test_gemini.py          # Standalone verification script for Google GenAI SDK connection
├── .env.example            # Safe environment template with placeholder values
├── .gitignore              # Excludes .env, virtual environments, SQLite DBs, and caches
├── pytest.ini              # Pytest configuration specifying test paths and discovery
├── .streamlit/
│   └── config.toml         # Streamlit dark luxury theme and server configuration
├── services/
│   ├── __init__.py
│   ├── ai_service.py       # Gemini API client, Pydantic schemas, fallback generator, secrets
│   ├── database.py         # SQLite CRUD operations, cascade rules, and metrics aggregations
│   └── planner.py          # Input validation, currency formatting, and deterministic math
└── tests/
    ├── __init__.py
    ├── test_ai_service.py   # AI schema validation, fallback generation, and secrets tests
    ├── test_app.py          # Application import, module structure, and entry point tests
    ├── test_database.py     # SQLite persistence, cascades, metrics, and multi-currency tests
    ├── test_planner.py      # Budget penny-precision arithmetic, currency grouping, and timelines
    └── test_validation.py   # Event input validation and boundary condition tests
```

---

## 📋 Prerequisites

To run CelebrAI locally, ensure your machine has:
- **Operating System**: Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+ recommended).
- **Python**: Version `3.10` or higher (verified on Python 3.14).
- **Git**: Installed and available in your terminal path.
- **Google Gemini API Key** (*Optional but recommended*): A free API key from [Google AI Studio](https://aistudio.google.com/). CelebrAI operates 100% offline using its fallback engine if an API key is not supplied.

---

## 💻 Local Installation & Startup

### 1. Clone the Public Repository
```bash
git clone https://github.com/Yemmmyc/celebrai.git
cd celebrai
```

### 2. Set Up a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the provided `.env.example` template to `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Open `.env` in an editor and insert your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

> [!WARNING]
> Never commit your active `.env` file to version control. It is explicitly protected by `.gitignore`.

### 5. Launch CelebrAI
```bash
streamlit run app.py
```
Open your web browser to `http://localhost:8501`.

---

## 🔐 Environment Variables & Configuration

CelebrAI supports flexible configuration via local `.env` files, shell environment variables, or **Streamlit Secrets** (`st.secrets`):

| Variable Name | Required? | Default Value | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Optional | `None` | Google Gemini API key. If absent, fallback planner activates automatically. Never commit actual keys. |
| `GEMINI_MODEL` | Optional | `gemini-3.8-flash` | The Gemini model identifier used for creative generation. Overridable via `.env` or Streamlit secrets. |
| `GEMINI_TIMEOUT_MS` | Optional | `30000` | HTTP request timeout in milliseconds. Defaults to 30,000 ms (30s) locally; configured to 45,000 ms (45s) in Streamlit Cloud secrets. |
| `CELEBRAI_DB_PATH` | Optional | `celebrai.db` in project root | Absolute or relative path to the SQLite persistence database. |

### Streamlit Secrets (`.streamlit/secrets.toml`)
When deploying to Streamlit Community Cloud, secrets can be provided via the UI or locally in `.streamlit/secrets.toml`:
```toml
# .streamlit/secrets.toml (Excluded from git)
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_TIMEOUT_MS = "45000"
```

[`_get_gemini_api_key()`](services/ai_service.py) prioritizes environment variables first, then falls back cleanly to `st.secrets` if running inside Streamlit. Never commit actual API keys or secrets to version control.

> [!NOTE]
> **Timeout Decoupling: Local vs. Cloud Settings**
> - **Local Development**: Defaults to `30000` ms (30 seconds via [`DEFAULT_TIMEOUT_MS`](services/ai_service.py#L26)), which can be overridden via `GEMINI_TIMEOUT_MS` in `.env`.
> - **Streamlit Community Cloud Deployment**: Configured explicitly to `45000` ms (45 seconds) via Streamlit Cloud Secrets to account for container network transit and API latency before activating fallback.
> - Local and cloud timeout configurations are intentionally separate and must not be assumed to be identical.

---

## 🤖 Gemini AI Availability and Resilient Fallback

CelebrAI pairs creative generative intelligence with a resilient dual-mode architecture.

### Model Configuration & Structured Output
- **Configured Model**: `gemini-3.8-flash` via the official Google GenAI SDK (`google.genai`). The model identifier can be customized via the `GEMINI_MODEL` environment variable or Streamlit secret.
- **Thinking Configuration**: Structured JSON generation uses `thinking_level="LOW"` (`types.ThinkingConfig(thinking_level="LOW")`). Testing confirmed that `thinking_level="MINIMAL"` is rejected by Gemini 3.8 Flash with `HTTP 400 INVALID_ARGUMENT`, whereas `"LOW"` is natively supported and maintains rapid generation speeds.
- **Concise Output Prompting**: The system prompt provides strict length directives (for example, limiting theme descriptions to two evocative sentences and styling items to concise one-line specifications). This reduces token generation overhead, optimizes response latency, and minimizes timeout exposure.
- **Seven-Field Pydantic Schema**: All AI-generated responses are validated against the [`AIEventPlan`](services/ai_service.py#L31) schema containing seven structured fields:
  1. `theme_concept` (Creative evocative title)
  2. `theme_description` (2-3 sentence overview setting mood, lighting, and ambiance)
  3. `color_palette` (List of 4 curated color swatches with descriptive hex tones)
  4. `decor_highlights` (List of 3 signature tactile staging and decor concepts)
  5. `menu_suggestions` (Signature welcome cocktail/mocktail and 2 culinary tasting items)
  6. `entertainment_ideas` (List of 2 interactive guest experiences)
  7. `planner_pro_tips` (List of 2 actionable expert coordinator tips)
- **Response Sanitization**: Markdown fences (````json ... ````) are automatically stripped before passing payload to Pydantic validation.

### Live Testing Observations & Upstream API Availability
- **Observed External Status Codes**: During live end-to-end testing and production deployment, requests have encountered:
  - `HTTP 503 UNAVAILABLE`: *Google Gemini model temporarily experiencing high demand.*
  - `HTTP 504 DEADLINE_EXCEEDED`: Upstream deadline exceeded during peak load.
- **Diagnostic API Verification**: Controlled diagnostic tests confirmed that during observed periods of Google backend capacity saturation, both a minimal baseline text-generation request (`"Reply with OK"`) and the full structured event-generation request encountered 504 timeout errors.
- **External Provider Reality**: These errors are external API availability, capacity, and deadline limitations on Google's infrastructure. CelebrAI does not claim that the application has permanently resolved these external service fluctuations. Availability is intermittent and varies based on upstream Google service conditions; when capacity permits, generation succeeds normally.

### Single-Attempt Architecture & Retry Policy
- **One Request Per Action**: To guarantee predictable user experience, CelebrAI makes exactly **one** Gemini generation request per user action.
- **Automatic Retries Intentionally Disabled**: Automatic retries for HTTP 503 and HTTP 504 are **intentionally disabled**. When upstream servers are saturated, retrying compounds queue delays and leaves users waiting in front of prolonged loading indicators. Instead, after the single request attempt fails or reaches the configured timeout (45 seconds in Streamlit Community Cloud; 30 seconds locally), CelebrAI transitions directly to fallback planning without triggering repeated retry cycles.

### Resilient Deterministic Fallback Planning Engine
- **Seamless Local Fallback**: When Gemini generation fails (upon receiving an HTTP 503 response, reaching the configured request timeout of 45 seconds in Streamlit Community Cloud / 30 seconds locally, network disconnection, or when an API key is unconfigured), CelebrAI activates its built-in deterministic, rule-based planning engine ([`_generate_fallback_plan()`](services/ai_service.py)).
- **Complete Seven-Field Dossier**: The fallback engine synthesizes theme keywords, event category, guest count, and venue context to produce a complete celebration plan preserving all seven required schema fields.
- **Reliable SQLite Persistence**: The event and its generated plan (whether AI-generated or deterministic fallback) are safely written to SQLite along with child budget breakdowns, timelines, and vendor items.
- **Transparent Distinction**: The UI clearly distinguishes AI-generated plans (`Gemini (gemini-3.8-flash)`) from deterministic fallback plans (`Deterministic Fallback`), displaying the exact honest reason (e.g., *"Google Gemini model temporarily experiencing high demand (503 Service Unavailable). Using deterministic planning engine."*).
- **Core Resilience Feature**: This dual-mode engine is a primary resilience feature of CelebrAI, ensuring hosts can plan, budget, and organize their celebrations without being blocked by third-party cloud outages.

---

## 💰 Financial Precision & Multi-Currency Handling

### Penny-Precision Budget Arithmetic
Budgeting in CelebrAI uses integer-cent rounding via [`calculate_budget_breakdown()`](services/planner.py):
1. Each of the 7 categories is multiplied by its allocation percentage and rounded to 2 decimal places.
2. The algorithm sums the rounded items and computes the discrepancy: $\Delta = \text{Target Budget} - \sum \text{Allocated}$.
3. Any 1-cent discrepancy is reconciled into the highest-percentage category (Catering), guaranteeing that:
$$\sum \text{Allocations} = \text{Target Budget} \quad \text{exactly}$$

### Multi-Currency Isolation
CelebrAI supports 4 major currencies:
- **US Dollar (`USD`)**: `$`
- **Nigerian Naira (`NGN`)**: `₦`
- **British Pound (`GBP`)**: `£`
- **Euro (`EUR`)**: `€`

> [!IMPORTANT]
> **Currency Safety Rule**: CelebrAI **never** performs automatic foreign exchange conversions or adds nominal amounts across different currencies.
>
> On the Executive Dashboard:
> - Budgets in different currencies are displayed separately in KPI cards (e.g. `$15,000 | ₦2,000,000`).
> - Altair charts render separate tabs for each active currency (`USD`, `NGN`, etc.) so axis scales remain unpolluted.

---

## 🗄️ Database & Persistence Model

CelebrAI uses local **SQLite** (`celebrai.db`) for lightweight, serverless persistence.

### Relational Schema
```sql
-- Events table
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    date TEXT NOT NULL,
    location TEXT NOT NULL,
    guest_count INTEGER NOT NULL,
    budget REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    theme TEXT,
    preferences TEXT,
    ai_plan_json TEXT,
    status TEXT DEFAULT 'Planning',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Cascading child tables
CREATE TABLE IF NOT EXISTS budget_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    allocated_amount REAL NOT NULL,
    actual_amount REAL DEFAULT 0.0,
    percentage REAL NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS timeline_items (... REFERENCES events(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS vendor_items (... REFERENCES events(id) ON DELETE CASCADE);
```

### Persistence Considerations: Local vs. Cloud
- **Local Persistence**: Data is written directly to `celebrai.db` in the workspace root and persists while the database file remains available on the local filesystem.
- **Hosted Ephemeral Cloud Storage**: Standard Streamlit Community Cloud containers use an ephemeral filesystem. CelebrAI initializes tables automatically on startup via [`init_db()`](services/database.py). However, data stored in local SQLite will reset whenever the application restarts, is redeployed, or its container runtime is replaced.
- **Custom Database Path (`CELEBRAI_DB_PATH`)**: Setting `CELEBRAI_DB_PATH` allows customizing the database file location; it does not itself provide persistent or durable cloud storage unless pointed to a genuinely persistent mounted volume. Durable multi-user cloud persistence requires an external managed database (such as PostgreSQL), which is not currently implemented.

---

## 🧪 Testing & Quality Assurance

CelebrAI includes an extensive automated test suite covering units, database transactions, input validation boundaries, currency math, schema conformance, and security leakage prevention.

### Execute Tests
Run the test suite from the repository root:
```bash
python -m pytest -q
```

**Last Recorded Test Result (Verified October 2026):**
```text
...............................................                          [100%]
47 passed, 1 warning in 43.52s
```

### Verify Dependency Consistency
```bash
python -m pip check
```
**Result:**
```text
No broken requirements found.
```

### Test Suite Breakdown
| Test File | Test Count | Scope |
|---|---|---|
| [`tests/test_ai_service.py`](tests/test_ai_service.py) | 14 | Pydantic schema validation, 7-field structure, fallback generation, secret masking, secrets resolution, timeout parsing, thinking configuration. |
| [`tests/test_app.py`](tests/test_app.py) | 1 | Module imports, top-level function existence, clean headless loading. |
| [`tests/test_database.py`](tests/test_database.py) | 7 | SQLite initialization, CRUD operations, foreign key cascades, metrics aggregation, multi-currency KPIs. |
| [`tests/test_planner.py`](tests/test_planner.py) | 14 | Penny-precision rounding, currency formatting, timeline generation, vendor checklists, currency grouping. |
| [`tests/test_validation.py`](tests/test_validation.py) | 11 | String whitespace handling, guest count limits, budget thresholds, date format boundaries, currency validation. |

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

CelebrAI is deployed and operational on **Streamlit Community Cloud**:

> [!NOTE]
> **Deployment Status**: **Live & Operational** at [https://celebrai.streamlit.app/](https://celebrai.streamlit.app/)<br>
> Deployed from public GitHub repository [`Yemmmyc/celebrai`](https://github.com/Yemmmyc/celebrai) on the [`main` branch](https://github.com/Yemmmyc/celebrai/tree/main).

### Step-by-Step Deployment Configuration
1. **Fork or Push to GitHub**:
   Ensure your code is published to a public repository (e.g., `https://github.com/Yemmmyc/celebrai`) on the `main` branch.
2. **Access Streamlit Cloud**:
   Sign in to [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
3. **Configure App Parameters**:
   - **Repository**: `Yemmmyc/celebrai`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. **Configure Secrets**:
   Click **Advanced settings** > **Secrets** and configure:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key_here"
   GEMINI_MODEL = "gemini-3.8-flash"
   GEMINI_TIMEOUT_MS = "45000"
   ```
5. **Deploy**:
   Click **Deploy!** The platform installs dependencies from `requirements.txt` and boots the application.
6. **Ephemeral Storage in Public Deployment**:
   Standard Streamlit Community Cloud containers utilize an ephemeral filesystem. SQLite initializes tables automatically on startup via [`init_db()`](services/database.py). However, event records persist during active sessions but reset whenever the container is restarted, redeployed, or put to sleep by the platform.

---

## 🔒 Security, Privacy & Repository Hygiene

- **Secret Masking**: [`get_ai_status()`](services/ai_service.py) verifies key presence without ever logging or returning key material. Unit test `test_ai_status_security` asserts that Google API key prefixes (`AIza*`) never appear in status payloads.
- **Git Exclusions**: The repository's [`.gitignore`](.gitignore) excludes `.env`, `*.db`, `celebrai.db`, `.venv/`, `__pycache__/`, `.pytest_cache/`, and `.streamlit/secrets.toml`.
- **Public Git Index**: The published repository contains 18 clean files (~0.14 MB) containing zero credentials or personal event records.
- **Single-Tenant Architecture & Shared Public Access Warning**: CelebrAI operates without user authentication, login mechanisms, or multi-tenant database partitioning. In the live public Streamlit Community Cloud deployment, all visitors access and share the same live SQLite database, meaning any visitor may view, create, modify, or delete stored celebration records. **Users are explicitly warned not to enter personal, confidential, or sensitive information.**

---

## 🚧 Confirmed Limitations & Future Roadmap

### Confirmed Limitations
1. **Single-Tenant Public Deployment & Shared Database**: The application contains no user accounts, authentication, or per-user database partitioning. In the public cloud deployment, all visitors share the active database and may view, create, modify, or delete records. Users should not input personal, confidential, or sensitive information.
2. **Ephemeral Cloud Persistence**: Uses local SQLite, which resets on container redeployments in stateless cloud environments.
3. **Intermittent Upstream Gemini Availability**: Upstream Google infrastructure occasionally experiences high demand (`HTTP 503 UNAVAILABLE`) or timeouts (`HTTP 504 DEADLINE_EXCEEDED`). CelebrAI mitigates this by bounding generation to a single attempt and falling back to its deterministic engine once the configured timeout (45 seconds in Streamlit Community Cloud; 30 seconds locally) or server error is reached.
4. **Decoupled Local vs. Cloud Timeouts**: Local execution defaults to 30,000 ms, whereas Streamlit Community Cloud is configured with 45,000 ms in secrets; settings are separate and decoupled.
5. **No Live Foreign Exchange**: Multi-currency displays segregate amounts into distinct currency tabs rather than converting them via real-time market rates.
6. **Manual Vendor Dispatch**: Vendor items track status internally but do not send outbound automated emails or SMS messages.

### Future Roadmap (*Proposed Enhancements*)
- [ ] Integration with hosted PostgreSQL (Supabase / Neon) for durable cloud persistence.
- [ ] User authentication with Google OAuth or Streamlit Authenticator.
- [ ] Exportable Celebration Dossiers in PDF and ICS calendar formats.
- [ ] Live currency conversion toggle using open exchange rate APIs.
- [ ] Direct vendor email RFP triggers.

---

## 🛠️ Troubleshooting Guide

| Issue | Root Cause | Solution |
|---|---|---|
| **UI displays "Deterministic Fallback"** | `GEMINI_API_KEY` missing from `.env` or invalid | Verify that `.env` exists in the workspace root and contains a valid key from Google AI Studio. Restart Streamlit. |
| **503 Server Unavailable Warning** | Google Gemini is experiencing high demand | CelebrAI automatically falls back to deterministic planning. Wait a few moments or retry the request. |
| **Port 8501 Already in Use** | Another Streamlit process is running | Run on a different port: `streamlit run app.py --server.port 8502` |
| **Validation Error: "Unsupported currency"** | Currency not in approved list | Select one of the 4 supported currencies: `USD`, `NGN`, `GBP`, or `EUR`. |
| **ModuleNotFoundError** | Dependencies not installed in active environment | Ensure virtual environment is activated (`.venv`) and run `pip install -r requirements.txt`. |
| **Database Locked (`sqlite3.OperationalError`)** | Concurrency conflict on Windows | Close external SQLite browsers (e.g. DB Browser for SQLite) holding a write lock on `celebrai.db`. |

---

## 🤝 Contributing Guidelines

Contributions, bug reports, and suggestions are welcome!

1. **Fork the Repository**: Create your feature branch (`git checkout -b feature/amazing-feature`).
2. **Implement & Test**: Write clean code following PEP 8.
3. **Verify Health**:
   ```bash
   python -m pytest -q
   python -m pip check
   ```
4. **Commit & Push**:
   ```bash
   git commit -m "feat: describe your change"
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**: Provide a clear description of changes and test evidence.

---

## 📜 License & Acknowledgements

### License Notice
> [!IMPORTANT]
> **No formal open-source license file is currently provided in this repository.**
> All rights are reserved by the repository owner. Reuse, redistribution, or modification permissions should not be assumed without explicit written consent.

### Acknowledgements
- Built with [Google Gemini](https://aistudio.google.com/) via the `google-genai` SDK. *(Note: Google does not sponsor, endorse, or manage CelebrAI).*
- Powered by the [Streamlit](https://streamlit.io/) reactive web framework.
- Developed for **PromptWars Virtual Challenge 5**.

---

## 📋 Hackathon Submission Checklist

| Deliverable | Status | Details / URL |
|---|---|---|
| **Public GitHub Repository** | ✅ **Completed** | [https://github.com/Yemmmyc/celebrai](https://github.com/Yemmmyc/celebrai) ([`main` branch](https://github.com/Yemmmyc/celebrai/tree/main)) |
| **Live Deployment URL** | ✅ **Completed** | [https://celebrai.streamlit.app/](https://celebrai.streamlit.app/) |
| **Payload Size < 10 MB** | ✅ **Completed** | 27 files, ~1.84 MB (18.4% of quota) |
| **Automated Test Suite** | ✅ **Completed** | 47 tests passing (`pytest -q`) |
| **Zero Dependency Conflicts** | ✅ **Completed** | `pip check` confirmed clean |
| **GenAI Documentation** | ✅ **Completed** | Detailed in Section 11 of this README |
| **Demo Walkthrough Video** | ⏳ *Pending* | Final walkthrough recording in progress |
| **LinkedIn Submission Post** | ⏳ *Pending* | To be published with final demo |

---

*Crafted for PromptWars Virtual Challenge 5.*
