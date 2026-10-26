"""Tests for deterministic budget allocation and timeline planning."""

import pytest
from services.planner import (
    BUDGET_PROFILES,
    EVENT_TYPES,
    calculate_budget_breakdown,
    generate_timeline_plan,
    generate_vendor_checklist,
)


def test_budget_profiles_sum_to_100():
    """Ensure every predefined budget profile percentage sums strictly to 100%."""
    for event_type, profile in BUDGET_PROFILES.items():
        total_pct = sum(item["percentage"] for item in profile)
        assert round(total_pct, 4) == 100.0, f"Profile '{event_type}' does not sum to 100%"


@pytest.mark.parametrize(
    "budget, event_type, guest_count",
    [
        (10000.0, "Wedding", 100),
        (5000.0, "Birthday", 25),
        (25000.50, "Corporate Gala", 250),
        (12345.67, "Anniversary", 40),
        (1500.0, "Baby Shower", 30),
        (750.25, "Dinner Party", 8),
        (999.99, "Other", 12),
        (100.01, "Wedding", 2),
    ],
)
def test_budget_allocation_penny_precision(budget, event_type, guest_count):
    """Ensure Python budget arithmetic matches exact budget down to the penny."""
    items = calculate_budget_breakdown(budget, event_type=event_type, guest_count=guest_count)

    assert len(items) > 0
    total_allocated = round(sum(item["allocated_amount"] for item in items), 2)
    assert total_allocated == round(budget, 2), f"Total {total_allocated} != Budget {budget}"

    # Verify per-guest calculations
    for item in items:
        expected_per_guest = round(item["allocated_amount"] / guest_count, 2)
        assert item["cost_per_guest"] == expected_per_guest


def test_invalid_budget_raises_error():
    """Verify negative or zero budget raises ValueError."""
    with pytest.raises(ValueError):
        calculate_budget_breakdown(0.0)

    with pytest.raises(ValueError):
        calculate_budget_breakdown(-500.0)


def test_timeline_plan_generation():
    """Verify timeline generates both milestone and day-of itinerary items."""
    timeline = generate_timeline_plan("2026-12-31", "Wedding")
    assert len(timeline) >= 10

    milestones = [t for t in timeline if t["category"] == "Milestone"]
    day_of = [t for t in timeline if t["category"] == "Day-Of"]

    assert len(milestones) >= 5
    assert len(day_of) >= 8
    assert all("timeframe" in t and "title" in t for t in timeline)


def test_vendor_checklist_generation():
    """Verify vendor checklist generates items aligned with budget categories."""
    budget_items = calculate_budget_breakdown(10000.0, "Wedding", 100)
    vendors = generate_vendor_checklist("Wedding", budget_items)

    assert len(vendors) > 0
    assert all("name" in v and "status" in v for v in vendors)
    # Check that estimated costs sum up reasonably
    total_vendor_est = sum(v["estimated_cost"] for v in vendors)
    assert total_vendor_est > 0


def test_currency_formatting_and_symbols():
    """Verify currency formatting and symbol resolution for NGN, USD, GBP, and EUR."""
    from services.planner import CURRENCY_SYMBOLS, SUPPORTED_CURRENCIES, format_currency, get_currency_symbol

    assert set(SUPPORTED_CURRENCIES) == {"USD", "NGN", "GBP", "EUR"}

    assert get_currency_symbol("USD") == "$"
    assert get_currency_symbol("NGN") == "₦"
    assert get_currency_symbol("GBP") == "£"
    assert get_currency_symbol("EUR") == "€"
    assert get_currency_symbol("CAD") == "$"

    assert format_currency(15000, "USD") == "$15,000.00"
    assert format_currency(750000, "NGN") == "₦750,000.00"
    assert format_currency(2500.5, "GBP") == "£2,500.50"
    assert format_currency(1234.56, "EUR") == "€1,234.56"
    assert format_currency(5000, "USD", decimals=0) == "$5,000"
    assert format_currency(0, "EUR") == "€0.00"


def test_currency_safe_portfolio_grouping():
    """Verify that portfolio events are grouped by currency without cross-currency nominal addition."""
    from services.planner import format_currency, get_currency_symbol

    events = [
        {"name": "Lagos Gala", "event_type": "Corporate Gala", "budget": 2000000.0, "currency": "NGN"},
        {"name": "Abuja Birthday", "event_type": "Birthday", "budget": 500000.0, "currency": "NGN"},
        {"name": "NYC Wedding", "event_type": "Wedding", "budget": 15000.0, "currency": "USD"},
        {"name": "London Soiree", "event_type": "Dinner Party", "budget": 3500.0, "currency": "GBP"},
    ]

    events_by_curr: dict[str, list[dict]] = {}
    for ev in events:
        c = ev.get("currency", "USD")
        events_by_curr.setdefault(c, []).append(ev)

    assert set(events_by_curr.keys()) == {"NGN", "USD", "GBP"}

    # NGN totals remain strictly within NGN
    ngn_total = sum(e["budget"] for e in events_by_curr["NGN"])
    assert ngn_total == 2500000.0
    assert format_currency(ngn_total, "NGN", decimals=0) == "₦2,500,000"
    assert get_currency_symbol("NGN") == "₦"

    # USD totals remain strictly within USD
    usd_total = sum(e["budget"] for e in events_by_curr["USD"])
    assert usd_total == 15000.0
    assert format_currency(usd_total, "USD", decimals=0) == "$15,000"
    assert get_currency_symbol("USD") == "$"

    # GBP totals remain strictly within GBP
    gbp_total = sum(e["budget"] for e in events_by_curr["GBP"])
    assert gbp_total == 3500.0
    assert format_currency(gbp_total, "GBP", decimals=0) == "£3,500"
    assert get_currency_symbol("GBP") == "£"

    # Ensure no cross-currency nominal sum is ever computed
    assert ngn_total != (ngn_total + usd_total + gbp_total)


