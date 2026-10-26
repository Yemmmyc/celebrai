"""Tests for SQLite database persistence."""

import os
import tempfile
import pytest
from services.database import (
    delete_event,
    get_budget_items,
    get_dashboard_metrics,
    get_event,
    get_timeline_items,
    get_vendor_items,
    init_db,
    list_events,
    save_event,
    toggle_timeline_completed,
    update_budget_actual,
    update_event_status,
    update_vendor_item,
)
from services.planner import (
    calculate_budget_breakdown,
    generate_timeline_plan,
    generate_vendor_checklist,
)


@pytest.fixture
def temp_db():
    """Create a temporary sqlite database file for isolation."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_save_and_retrieve_event(temp_db):
    """Test full event creation, budget, timeline, and retrieval."""
    event_data = {
        "name": "Sarah & Julian's Wedding",
        "event_type": "Wedding",
        "date": "2026-09-18",
        "location": "Villa Bellissima",
        "guest_count": 120,
        "budget": 35000.0,
        "theme": "Mediterranean Romance",
        "preferences": "Olive branches, candlelight, local wines",
        "ai_plan_json": {"theme_concept": "Mediterranean Romance"},
    }

    budget_items = calculate_budget_breakdown(35000.0, "Wedding", 120)
    timeline_items = generate_timeline_plan("2026-09-18", "Wedding")
    vendor_items = generate_vendor_checklist("Wedding", budget_items)

    event_id = save_event(
        event_data,
        budget_items=budget_items,
        timeline_items=timeline_items,
        vendor_items=vendor_items,
        db_path=temp_db,
    )

    assert event_id > 0

    # Retrieve event
    retrieved = get_event(event_id, db_path=temp_db)
    assert retrieved is not None
    assert retrieved["name"] == "Sarah & Julian's Wedding"
    assert retrieved["guest_count"] == 120
    assert retrieved["budget"] == 35000.0
    assert retrieved["ai_plan"]["theme_concept"] == "Mediterranean Romance"

    # Check child records
    saved_budget = get_budget_items(event_id, db_path=temp_db)
    assert len(saved_budget) == len(budget_items)

    saved_timeline = get_timeline_items(event_id, db_path=temp_db)
    assert len(saved_timeline) == len(timeline_items)

    saved_vendors = get_vendor_items(event_id, db_path=temp_db)
    assert len(saved_vendors) == len(vendor_items)


def test_update_and_delete_operations(temp_db):
    """Test updates to status, budget actuals, timeline check, and deletion."""
    event_id = save_event(
        {
            "name": "Neon Tech Gala",
            "event_type": "Corporate Gala",
            "date": "2026-11-05",
            "location": "City Convention Center",
            "guest_count": 300,
            "budget": 50000.0,
        },
        budget_items=[{"category": "Venue & AV", "allocated_amount": 18000.0, "percentage": 36.0}],
        timeline_items=[{"timeframe": "1 Month", "title": "Lock Keynote", "category": "Milestone"}],
        vendor_items=[{"category": "Venue", "name": "Convention Center", "status": "Needed"}],
        db_path=temp_db,
    )

    # Update event status
    assert update_event_status(event_id, "Confirmed", db_path=temp_db) is True
    ev = get_event(event_id, db_path=temp_db)
    assert ev["status"] == "Confirmed"

    # Update budget actual
    b_items = get_budget_items(event_id, db_path=temp_db)
    assert update_budget_actual(b_items[0]["id"], 17500.0, notes="Discount applied", db_path=temp_db) is True
    b_updated = get_budget_items(event_id, db_path=temp_db)
    assert b_updated[0]["actual_amount"] == 17500.0
    assert b_updated[0]["notes"] == "Discount applied"

    # Toggle timeline
    t_items = get_timeline_items(event_id, db_path=temp_db)
    assert toggle_timeline_completed(t_items[0]["id"], True, db_path=temp_db) is True
    t_updated = get_timeline_items(event_id, db_path=temp_db)
    assert t_updated[0]["is_completed"] == 1

    # Update vendor item
    v_items = get_vendor_items(event_id, db_path=temp_db)
    assert update_vendor_item(
        v_items[0]["id"],
        name="Metropolis Hall",
        status="Booked",
        actual_cost=17500.0,
        notes="Deposit paid",
        db_path=temp_db,
    ) is True
    v_updated = get_vendor_items(event_id, db_path=temp_db)
    assert v_updated[0]["name"] == "Metropolis Hall"
    assert v_updated[0]["status"] == "Booked"

    # Delete event
    assert delete_event(event_id, db_path=temp_db) is True
    assert get_event(event_id, db_path=temp_db) is None
    # Child items cascade deleted
    assert len(get_budget_items(event_id, db_path=temp_db)) == 0


def test_dashboard_metrics(temp_db):
    """Test metrics calculation with empty state and populated state."""
    empty_metrics = get_dashboard_metrics(db_path=temp_db)
    assert empty_metrics["total_events"] == 0
    assert empty_metrics["total_budget"] == 0.0
    assert empty_metrics["next_event"] is None

    # Populate two events
    save_event(
        {
            "name": "Spring Brunch",
            "event_type": "Baby Shower",
            "date": "2026-11-10",
            "location": "Orchard Garden",
            "guest_count": 25,
            "budget": 2000.0,
        },
        db_path=temp_db,
    )
    save_event(
        {
            "name": "Winter Gala",
            "event_type": "Corporate Gala",
            "date": "2026-12-15",
            "location": "Metropolitan Ballroom",
            "guest_count": 200,
            "budget": 40000.0,
        },
        db_path=temp_db,
    )

    metrics = get_dashboard_metrics(db_path=temp_db)
    assert metrics["total_events"] == 2
    assert metrics["total_budget"] == 42000.0
    assert metrics["total_guests"] == 225
    assert metrics["next_event"] is not None
    assert metrics["next_event"]["name"] == "Spring Brunch"


def test_currency_persistence_and_safe_migration(temp_db):
    """Verify currency persistence across NGN, USD, GBP, EUR and safe migration of older schemas."""
    import sqlite3

    currencies = ["USD", "NGN", "GBP", "EUR"]
    saved_ids = {}

    for curr in currencies:
        eid = save_event(
            {
                "name": f"Event in {curr}",
                "event_type": "Birthday",
                "date": "2026-11-20",
                "location": "Global Hall",
                "guest_count": 50,
                "budget": 10000.0,
                "currency": curr,
            },
            db_path=temp_db,
        )
        saved_ids[curr] = eid

    for curr, eid in saved_ids.items():
        ev = get_event(eid, db_path=temp_db)
        assert ev["currency"] == curr

    all_events = list_events(db_path=temp_db)
    assert len(all_events) == 4
    for ev in all_events:
        assert ev["currency"] in currencies

    # Test safe migration on legacy database schema without 'currency' column
    legacy_fd, legacy_path = tempfile.mkstemp(suffix=".db")
    os.close(legacy_fd)
    try:
        # Create a legacy table without 'currency' column
        with sqlite3.connect(legacy_path) as conn:
            conn.execute(
                """
                CREATE TABLE events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    guest_count INTEGER NOT NULL,
                    budget REAL NOT NULL,
                    theme TEXT,
                    preferences TEXT,
                    status TEXT DEFAULT 'Planning',
                    ai_plan_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                INSERT INTO events (name, event_type, date, location, guest_count, budget)
                VALUES ('Legacy Gala', 'Corporate Gala', '2026-10-10', 'Old Town', 80, 25000.0)
                """
            )
            conn.commit()

        # Run init_db to execute safe migration
        init_db(legacy_path)

        # Confirm currency column was added and existing event was preserved with default 'USD'
        legacy_ev = get_event(1, db_path=legacy_path)
        assert legacy_ev is not None
        assert legacy_ev["name"] == "Legacy Gala"
        assert legacy_ev["currency"] == "USD"
    finally:
        try:
            if os.path.exists(legacy_path):
                os.remove(legacy_path)
        except OSError:
            pass


def test_creative_plan_persistence(temp_db):
    """Verify Gemini creative plan fields are faithfully serialized, persisted, and deserialized in get_event and list_events."""
    plan_data = {
        "theme_concept": "Celestial Midnight Soirée",
        "theme_description": "An ethereal evening under velvet midnight skies, punctuated by starlit crystal installations and glowing celestial accents.",
        "color_palette": ["#141119", "#C5A059", "#6CB8A8", "#2E243C"],
        "decor_highlights": [
            "Suspended constellation crystal chandeliers",
            "Midnight plum velvet tablecloths with brushed gold taper candles",
            "Bespoke crescent-moon photo backdrop with fragrant white jasmine",
        ],
        "menu_suggestions": [
            "Black truffle risotto with gold leaf crisp",
            "Pan-seared Chilean sea bass with citrus reduction",
            "Midnight Nebula signature gin cocktail with smoked lavender",
        ],
        "entertainment_ideas": [
            "Acoustic harp and violin duo during cocktails",
            "Immersive ambient starfield projection mapping",
        ],
        "planner_pro_tips": [
            "Dim ambient chandeliers 30 minutes before first dance",
            "Prepare gold-embossed take-home star map favors",
        ],
        "_generation_mode": "Gemini AI",
    }

    eid = save_event(
        {
            "name": "Celestial Celebration",
            "event_type": "Wedding",
            "date": "2026-12-31",
            "location": "The Starlight Pavilion",
            "guest_count": 150,
            "budget": 45000.0,
            "currency": "GBP",
            "ai_plan_json": plan_data,
        },
        db_path=temp_db,
    )

    # 1. Verification via get_event
    ev = get_event(eid, db_path=temp_db)
    assert ev is not None
    p_get = ev["ai_plan"]
    assert p_get["theme_concept"] == "Celestial Midnight Soirée"
    assert "ethereal evening" in p_get["theme_description"]
    assert len(p_get["color_palette"]) == 4
    assert len(p_get["decor_highlights"]) == 3
    assert len(p_get["menu_suggestions"]) == 3
    assert len(p_get["entertainment_ideas"]) == 2
    assert len(p_get["planner_pro_tips"]) == 2
    assert p_get["_generation_mode"] == "Gemini AI"

    # 2. Verification via list_events (critical for My Celebrations page)
    all_events = list_events(db_path=temp_db)
    assert len(all_events) == 1
    p_list = all_events[0]["ai_plan"]
    assert p_list is not None
    assert p_list["theme_concept"] == "Celestial Midnight Soirée"
    assert p_list["decor_highlights"] == p_get["decor_highlights"]
    assert p_list["menu_suggestions"] == p_get["menu_suggestions"]
    assert p_list["entertainment_ideas"] == p_get["entertainment_ideas"]
    assert p_list["planner_pro_tips"] == p_get["planner_pro_tips"]


def test_deterministic_fallback_plan_identification(temp_db):
    """Verify that deterministic fallback plans are stored and identifiable."""
    fallback_plan = {
        "theme_concept": "Curated Elegance",
        "theme_description": "A refined, tailored celebration focused on harmonious design.",
        "color_palette": ["#211B29", "#6CB8A8", "#C5A059"],
        "decor_highlights": ["Floral centerpieces"],
        "menu_suggestions": ["Artisanal hors d'oeuvres"],
        "entertainment_ideas": ["Curated background playlist"],
        "planner_pro_tips": ["Confirm guest headcount 7 days prior"],
        "_generation_mode": "Deterministic Fallback",
        "_fallback_reason": "Gemini API unavailable or rate-limited.",
    }

    eid = save_event(
        {
            "name": "Fallback Event",
            "event_type": "Dinner Party",
            "date": "2026-11-28",
            "location": "Private Dining Room",
            "guest_count": 20,
            "budget": 3500.0,
            "currency": "EUR",
            "ai_plan_json": fallback_plan,
        },
        db_path=temp_db,
    )

    ev = get_event(eid, db_path=temp_db)
    assert ev["ai_plan"]["_generation_mode"] == "Deterministic Fallback"
    assert "rate-limited" in ev["ai_plan"]["_fallback_reason"]


def test_dashboard_metrics_multi_currency(temp_db):
    """Verify dashboard metrics track budget by currency without FX conversion."""
    save_event(
        {"name": "E1", "event_type": "Wedding", "date": "2026-11-10", "location": "L1", "guest_count": 50, "budget": 10000.0, "currency": "USD"},
        budget_items=[{"category": "Venue", "allocated_amount": 5000.0, "actual_amount": 4800.0, "percentage": 50.0}],
        db_path=temp_db,
    )
    save_event(
        {"name": "E2", "event_type": "Birthday", "date": "2026-11-15", "location": "L2", "guest_count": 30, "budget": 2000000.0, "currency": "NGN"},
        budget_items=[{"category": "Catering", "allocated_amount": 1000000.0, "actual_amount": 950000.0, "percentage": 50.0}],
        db_path=temp_db,
    )
    save_event(
        {"name": "E3", "event_type": "Corporate Gala", "date": "2026-12-01", "location": "L3", "guest_count": 100, "budget": 15000.0, "currency": "GBP"},
        budget_items=[{"category": "AV", "allocated_amount": 6000.0, "actual_amount": 6000.0, "percentage": 40.0}],
        db_path=temp_db,
    )

    metrics = get_dashboard_metrics(db_path=temp_db)
    assert metrics["total_events"] == 3
    assert metrics["budget_by_currency"]["USD"] == 10000.0
    assert metrics["budget_by_currency"]["NGN"] == 2000000.0
    assert metrics["budget_by_currency"]["GBP"] == 15000.0
    assert metrics["actual_by_currency"]["USD"] == 4800.0
    assert metrics["actual_by_currency"]["NGN"] == 950000.0
    assert metrics["actual_by_currency"]["GBP"] == 6000.0

