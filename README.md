# ✨ CelebrAI — AI-Powered Celebration & Event Planner

> **PromptWars Virtual Challenge 5 — Phase 1 MVP**  
> *Where bespoke celebration aesthetics meet deterministic financial precision.*

CelebrAI is an intelligent event and celebration management platform. It pairs the creative power of **Google Gemini** with strict, deterministic Python algorithms for budgeting and scheduling, backed by lightweight local **SQLite** persistence and presented in an elegant, luxury **Streamlit** dashboard.

---

## 🎨 Visual Identity & Design System

CelebrAI features a curated luxury dark palette designed for bespoke celebrations:
- **Deep Plum-Black (`#141119`)**: Grounding dark page background providing cinematic depth and high contrast.
- **Charcoal-Plum (`#211B29`)**: Refined card and container background with subtle slate borders (`#332A3E`).
- **Warm Ivory (`#F4EEE7`)**: Primary typography ensuring strong, accessible text contrast.
- **Muted Teal (`#6CB8A8`)**: Fresh secondary accent for status badges, metric highlights, and operational indicators.
- **Champagne Gold (`#C5A059`)**: Precious metallic accent used sparingly for brand emblems, focus states, and key actions.
- **Typography**: Editorial serif (*Playfair Display*) paired with clean modern geometric sans (*Plus Jakarta Sans*).

---

## 🏛️ Architectural Boundaries

| Layer | Technology | Responsibility |
|---|---|---|
| **User Interface** | Streamlit + Custom CSS | Responsive luxury dashboard with sidebar navigation across 6 distinct views. |
| **Creative Intelligence** | Google Gemini (`google-genai` SDK) | Generates bespoke event styling, color palettes, decor concepts, signature cocktails, entertainment ideas, and planner pro-tips. Validated via Pydantic schemas. |
| **Deterministic Planning** | Python Standard Math (`services/planner.py`) | Budget allocation with **guaranteed penny-precision arithmetic**, per-guest breakdowns, and day-of run-of-show scheduling. *Budget math is never delegated to AI.* |
| **Local Persistence** | SQLite (`celebrai.db`) | Thread-safe ACID storage for events, line-item budgets, milestones, and vendor rosters with cascading relationships. |

---

## 🌟 Phase 1 Features & Capabilities

1. **Executive Dashboard**:
   - Portfolio metrics: Total Celebrations, Total Planned Budget, Committed Spend, Honored Guests, and Next Event Countdown.
   - Elegant empty state with onboarding guidance when no events exist.
   - Visual Altair bar chart breaking down budget by event category.
2. **Create Event**:
   - Comprehensive form supporting Wedding, Birthday, Corporate Gala, Anniversary, Baby Shower, Dinner Party, Holiday Party, and custom celebrations.
   - Deterministic input validation (names, dates, guest counts, budgets).
   - Generates structured Gemini event plan with graceful offline fallback.
   - Atomically persists the event, budget breakdown, milestones, and vendor roster.
3. **My Events**:
   - Filterable portfolio list by category and planning status (`Planning`, `Confirmed`, `Completed`).
   - Deep inspection of AI styling concepts, decor highlights, and culinary ideas.
   - Status updates and cascading event deletion.
4. **Budget Planner**:
   - Deterministic category allocations (Venue, Catering, Media, Decor, Entertainment, Invitations, Contingency Reserve).
   - Variance analysis tracking planned targets against actual vendor spend.
   - Interactive line-item editor to record actual invoice amounts and vendor notes.
5. **Timeline & Itinerary**:
   - Dual-tab view: Master Milestones (from 6+ months out to eve of event) and Day-Of Run-of-Show (minute-by-minute schedule).
   - Interactive checklist toggles with visual completion progress tracking.
6. **Vendor Checklist**:
   - Category-aligned vendor roster (Caterer, Floral Stylist, Photographer, DJ/Band, Venue Coordinator).
   - Status tracking (`Needed`, `Researching`, `Contacted`, `Booked`, `Paid`).
   - Comparison of estimated allocations vs actual contract costs.

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Git

### 2. Environment Setup

Activate your existing virtual environment or create a new one:

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
pip install -r requirements.txt
```

### 4. Configure Gemini API Key Securely

CelebrAI loads `GEMINI_API_KEY` securely from environment variables, `.env`, or **Streamlit secrets** (`st.secrets`).

Copy the provided `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and set your actual API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

> [!IMPORTANT]
> - Never commit `.env` or database files to version control. They are strictly protected by `.gitignore`.
> - Never print, log, or hardcode your API key.
> - If `GEMINI_API_KEY` is not present, CelebrAI seamlessly activates its built-in **Deterministic Fallback Engine** so all planning, budgeting, timeline, and vendor features remain 100% operational.

### 5. Run the Test Suite & Health Checks
Verify that all unit tests, validation rules, budget arithmetic, and database operations pass:
```bash
python -m pytest -q
python -m pip check
```

### 6. Launch the CelebrAI Dashboard Locally
Start the Streamlit application:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

CelebrAI is fully pre-configured for one-click deployment on **Streamlit Community Cloud**:

1. **Push Repository to GitHub**:
   - Ensure `.gitignore` is in place (local `.env` and `*.db` are automatically excluded).
   - Push your branch to GitHub.
2. **Deploy on Streamlit Cloud**:
   - Log into [share.streamlit.io](https://share.streamlit.io/).
   - Click **New app**, select your repository, branch (`main`), and set **Main file path** to `app.py`.
3. **Configure Secrets**:
   - Under **Advanced settings** > **Secrets**, configure your Gemini API key in TOML format:
     ```toml
     GEMINI_API_KEY = "your_actual_gemini_api_key_here"
     GEMINI_MODEL = "gemini-3.8-flash"
     ```
   - Click **Save** and **Deploy**.
4. **Database Persistence**:
   - CelebrAI automatically initializes SQLite idempotently on startup.
   - For persistent cloud volumes, set the `CELEBRAI_DB_PATH` environment variable if desired.

---

## 📁 Workspace Structure

```
celebrai/
├── app.py                  # Main Streamlit luxury dashboard & navigation
├── requirements.txt        # Runtime dependencies (Streamlit, google-genai, pydantic, etc.)
├── README.md               # Setup, architectural documentation, and guides
├── test_gemini.py          # Standalone verification script for Gemini SDK
├── .env.example            # Safe environment template with placeholder values
├── .gitignore              # Comprehensive exclusion of .env, databases, caches, and OS files
├── .streamlit/
│   └── config.toml         # Streamlit dark luxury theme and server settings
├── services/
│   ├── __init__.py
│   ├── ai_service.py       # Gemini integration with Pydantic validation & fallback
│   ├── database.py         # SQLite persistence for events, budgets, timelines, vendors
│   └── planner.py          # Deterministic budget math, validation, and timelines
└── tests/
    ├── __init__.py
    ├── test_ai_service.py   # AI schema validation, secrets resolution & security tests
    ├── test_app.py          # App import and structure tests
    ├── test_database.py     # SQLite CRUD, cascades, and metrics tests
    ├── test_planner.py      # Budget penny-precision arithmetic & timeline tests
    └── test_validation.py   # Event input validation edge-case tests
```

---

## 🧪 Verification & Quality Assurance

- **Budget Arithmetic**: Guaranteed penny precision where `sum(allocated_items) == budget`. Discrepancies are reconciled strictly in Python.
- **Schema Safety**: Gemini responses are validated against Pydantic models with markdown strip filters and fallback handling.
- **Relational Integrity**: SQLite database enforces foreign key constraints (`PRAGMA foreign_keys = ON;`) with cascading deletes.
- **Zero Package Conflicts**: Verified cleanly via `python -m pip check`.
