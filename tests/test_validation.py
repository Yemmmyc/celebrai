"""Tests for input validation."""

from services.planner import validate_event_input


def test_valid_event_inputs():
    """Verify clean inputs pass validation."""
    valid, errors = validate_event_input(
        name="Golden Jubilee Anniversary",
        event_type="Anniversary",
        date_str="2026-11-20",
        location="Grand Plaza Conservatory",
        guest_count=60,
        budget=15000.0,
    )
    assert valid is True
    assert len(errors) == 0


def test_missing_name_fails():
    """Verify empty name triggers validation error."""
    valid, errors = validate_event_input(
        name="   ",
        event_type="Birthday",
        date_str="2026-12-01",
        location="Private Lounge",
        guest_count=20,
        budget=2000.0,
    )
    assert valid is False
    assert any("name cannot be empty" in e.lower() for e in errors)


def test_invalid_date_format_fails():
    """Verify non-ISO date formats fail."""
    valid, errors = validate_event_input(
        name="Team Retreat",
        event_type="Corporate Gala",
        date_str="12/31/2026",  # wrong format
        location="Skyline Suite",
        guest_count=50,
        budget=10000.0,
    )
    assert valid is False
    assert any("yyyy-mm-dd" in e.lower() for e in errors)


def test_invalid_guest_count_fails():
    """Verify zero, negative, or invalid guest count fails."""
    valid, errors = validate_event_input(
        name="Micro Dinner",
        event_type="Dinner Party",
        date_str="2026-10-31",
        location="Home Garden",
        guest_count=0,
        budget=800.0,
    )
    assert valid is False
    assert any("guest count" in e.lower() for e in errors)

    valid_neg, errors_neg = validate_event_input(
        name="Micro Dinner",
        event_type="Dinner Party",
        date_str="2026-10-31",
        location="Home Garden",
        guest_count="invalid",
        budget=800.0,
    )
    assert valid_neg is False


def test_invalid_budget_fails():
    """Verify negative or non-numeric budget fails."""
    valid, errors = validate_event_input(
        name="Holiday Party",
        event_type="Holiday Party",
        date_str="2026-12-24",
        location="Chalet Hall",
        guest_count=40,
        budget=-150.0,
    )
    assert valid is False
    assert any("budget" in e.lower() for e in errors)


def test_location_validation_accepts_london():
    """Regression test: non-empty location 'London' must be accepted."""
    valid, errors = validate_event_input(
        name="London Rooftop Soirée",
        event_type="Dinner Party",
        date_str="2026-11-15",
        location="London",
        guest_count=30,
        budget=4500.0,
    )
    assert valid is True
    assert len(errors) == 0


def test_location_validation_accepts_whitespace_london():
    """Regression test: 'London' with spaces, tabs, or non-breaking spaces must be accepted."""
    for loc_variant in ["  London  ", "\tLondon\n", "\u00a0London\u00a0", " The Glasshouse Conservatory, London "]:
        valid, errors = validate_event_input(
            name="London Reception",
            event_type="Wedding",
            date_str="2026-10-30",
            location=loc_variant,
            guest_count=50,
            budget=8000.0,
        )
        assert valid is True, f"Failed for variant {loc_variant!r}: {errors}"
        assert len(errors) == 0


def test_location_validation_rejects_empty():
    """Regression test: empty, whitespace-only, or None location must be rejected."""
    for empty_loc in ["", "   ", "\t\n", None]:
        valid, errors = validate_event_input(
            name="Mystery Venue Party",
            event_type="Birthday",
            date_str="2026-12-05",
            location=empty_loc,
            guest_count=20,
            budget=2000.0,
        )
        assert valid is False
        assert any("location or venue is required" in e.lower() for e in errors)


def test_location_validation_accepts_venue_alias_and_dict():
    """Regression test: supports venue keyword argument and dictionary payload."""
    # Keyword argument venue="London"
    valid_kw, errors_kw = validate_event_input(
        name="Kensington Gala",
        event_type="Corporate Gala",
        date_str="2026-12-10",
        venue="London",
        guest_count=100,
        budget=20000.0,
    )
    assert valid_kw is True
    assert len(errors_kw) == 0

    # Dict payload with "venue": "London"
    payload = {
        "name": "Kensington Gala",
        "event_type": "Corporate Gala",
        "date": "2026-12-10",
        "venue": "London",
        "guest_count": 100,
        "budget": 20000.0,
    }
    valid_dict, errors_dict = validate_event_input(payload)
    assert valid_dict is True
    assert len(errors_dict) == 0


def test_budget_input_validation_flexible_steps():
    """Verify budget input is not restricted to increments of 100 and accepts non-multiple amounts."""
    for valid_budget in [15.50, 75.25, 99.99, 125.0, 750.0, 15000.75, 1000000.0]:
        valid, errors = validate_event_input(
            name="Celebration of Life",
            event_type="Dinner Party",
            date_str="2026-11-20",
            location="Bistro 9",
            guest_count=10,
            budget=valid_budget,
            currency="USD",
        )
        assert valid is True, f"Failed for valid budget {valid_budget}: {errors}"
        assert len(errors) == 0

    # Negative, zero, or non-numeric should still fail
    for invalid_budget in [0, 0.0, -50.0, "not_a_number"]:
        valid, errors = validate_event_input(
            name="Celebration of Life",
            event_type="Dinner Party",
            date_str="2026-11-20",
            location="Bistro 9",
            guest_count=10,
            budget=invalid_budget,
        )
        assert valid is False
        assert any("budget" in e.lower() for e in errors)


def test_currency_validation():
    """Verify currency validation accepts NGN, USD, GBP, EUR and rejects unsupported currencies."""
    for valid_curr in ["USD", "NGN", "GBP", "EUR", "usd", "ngn"]:
        valid, errors = validate_event_input(
            name="Global Summit Dinner",
            event_type="Corporate Gala",
            date_str="2026-12-01",
            location="Grand Hall",
            guest_count=100,
            budget=50000.0,
            currency=valid_curr,
        )
        assert valid is True, f"Failed for valid currency {valid_curr}: {errors}"
        assert len(errors) == 0

    for invalid_curr in ["JPY", "CAD", "BITCOIN", ""]:
        valid, errors = validate_event_input(
            name="Global Summit Dinner",
            event_type="Corporate Gala",
            date_str="2026-12-01",
            location="Grand Hall",
            guest_count=100,
            budget=50000.0,
            currency=invalid_curr,
        )
        assert valid is False
        assert any("unsupported currency" in e.lower() for e in errors)


