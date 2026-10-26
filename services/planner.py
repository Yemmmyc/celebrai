"""Deterministic planner service for CelebrAI.

Handles:
- Input validation for event creation
- Deterministic budget allocation (strictly Python arithmetic, never delegated to AI)
- Deterministic timeline planning (milestones & day-of schedule)
- Deterministic vendor checklist generation
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

# Supported event types
EVENT_TYPES = [
    "Wedding",
    "Birthday",
    "Corporate Gala",
    "Anniversary",
    "Baby Shower",
    "Dinner Party",
    "Holiday Party",
    "Other",
]

# Supported Currencies (No automated FX conversions)
SUPPORTED_CURRENCIES = ["USD", "NGN", "GBP", "EUR"]

CURRENCY_SYMBOLS: dict[str, str] = {
    "USD": "$",
    "NGN": "₦",
    "GBP": "£",
    "EUR": "€",
}


def get_currency_symbol(currency: str = "USD") -> str:
    """Return symbol for currency code (defaults to $)."""
    return CURRENCY_SYMBOLS.get(str(currency).strip().upper(), "$")


def format_currency(amount: float | int, currency: str = "USD", decimals: int = 2) -> str:
    """Format numeric amount with currency symbol without foreign-exchange conversion."""
    sym = get_currency_symbol(currency)
    amt = float(amount or 0.0)
    if decimals == 0:
        return f"{sym}{amt:,.0f}"
    return f"{sym}{amt:,.{decimals}f}"


# Standard budget allocation profiles (must each sum strictly to 100.0)
BUDGET_PROFILES: dict[str, list[dict[str, Any]]] = {
    "Wedding": [
        {"category": "Venue & Rentals", "percentage": 30.0, "notes": "Site fee, tables, chairs, linens, lighting"},
        {"category": "Catering & Bar", "percentage": 30.0, "notes": "Plated/buffet service, bar package, cake"},
        {"category": "Photography & Video", "percentage": 12.0, "notes": "Full day coverage, second shooter, edited album"},
        {"category": "Decor & Florals", "percentage": 10.0, "notes": "Ceremony arch, centerpieces, bouquets"},
        {"category": "Music & Entertainment", "percentage": 8.0, "notes": "DJ/band, sound engineering, MC"},
        {"category": "Invitations & Favors", "percentage": 4.0, "notes": "Stationery, postage, guest gifts"},
        {"category": "Contingency Reserve", "percentage": 6.0, "notes": "Buffer for last-minute fees or gratuities"},
    ],
    "Birthday": [
        {"category": "Catering & Specialty Cake", "percentage": 35.0, "notes": "Appetizers, main meal, custom cake"},
        {"category": "Venue & Space Rental", "percentage": 25.0, "notes": "Private room, outdoor space, or setup"},
        {"category": "Entertainment & Activities", "percentage": 18.0, "notes": "DJ, performer, games, or photo booth"},
        {"category": "Decor & Balloon Art", "percentage": 10.0, "notes": "Backdrops, themed banners, balloons"},
        {"category": "Photography & Keepsakes", "percentage": 7.0, "notes": "Event photographer, polaroids, favors"},
        {"category": "Contingency Reserve", "percentage": 5.0, "notes": "Unexpected items or extra guests"},
    ],
    "Corporate Gala": [
        {"category": "Venue & AV Production", "percentage": 35.0, "notes": "Main ballroom, staging, microphones, screens"},
        {"category": "Catering & Premium Bar", "percentage": 32.0, "notes": "Multi-course dinner, cocktail hour, bar"},
        {"category": "Keynote & Entertainment", "percentage": 15.0, "notes": "Guest speaker, live entertainment, host"},
        {"category": "Branding & Signage", "percentage": 8.0, "notes": "Banners, programs, step-and-repeat backdrop"},
        {"category": "Staffing & Coordination", "percentage": 5.0, "notes": "Registration team, security, day-of lead"},
        {"category": "Contingency Reserve", "percentage": 5.0, "notes": "Overtime fees, tech backups, logistics"},
    ],
    "Anniversary": [
        {"category": "Catering & Wine Pairing", "percentage": 35.0, "notes": "Curated tasting menu, vintage wine, dessert"},
        {"category": "Venue & Atmosphere", "percentage": 25.0, "notes": "Intimate dining space or garden venue"},
        {"category": "Photography & Memory Book", "percentage": 15.0, "notes": "Portraits, candid coverage, commemorative book"},
        {"category": "Florals & Ambience", "percentage": 12.0, "notes": "Lush centerpieces, romantic candle lighting"},
        {"category": "Live Acoustic Music", "percentage": 8.0, "notes": "Strings quartet or acoustic soloist"},
        {"category": "Contingency Reserve", "percentage": 5.0, "notes": "Weather adjustments, additional service tips"},
    ],
    "Baby Shower": [
        {"category": "Food & Refreshments", "percentage": 35.0, "notes": "Brunch/afternoon tea, mocktails, sweets"},
        {"category": "Venue & Table Styling", "percentage": 25.0, "notes": "Bright venue, table linens, chair covers"},
        {"category": "Games, Prizes & Favors", "percentage": 15.0, "notes": "Custom games, guest favors, prize baskets"},
        {"category": "Photography", "percentage": 10.0, "notes": "Mom-to-be portraits, family moments, decor shots"},
        {"category": "Custom Cake & Desserts", "percentage": 8.0, "notes": "Artisan cake, macarons, cookies"},
        {"category": "Contingency Reserve", "percentage": 7.0, "notes": "Spill kit, extra guest seatings"},
    ],
    "Dinner Party": [
        {"category": "Gourmet Food & Ingredients", "percentage": 45.0, "notes": "Premium meats/produce, chef or catering"},
        {"category": "Wine, Cocktails & Beverages", "percentage": 25.0, "notes": "Sommelier selection, pairings, aperitifs"},
        {"category": "Tabletop Styling & Florals", "percentage": 15.0, "notes": "Candles, floral arrangements, menus"},
        {"category": "Music & Ambiance", "percentage": 8.0, "notes": "Playlist curation, ambient audio equipment"},
        {"category": "Contingency Reserve", "percentage": 7.0, "notes": "Spares, ice, special dietary requests"},
    ],
    "Holiday Party": [
        {"category": "Festive Feast & Drinks", "percentage": 38.0, "notes": "Holiday spread, mulled drinks, festive desserts"},
        {"category": "Venue & Festive Decor", "percentage": 28.0, "notes": "Venue rental, seasonal trees, wreaths, lighting"},
        {"category": "DJ & Festive Activities", "percentage": 16.0, "notes": "Dance music, secret gift exchange, games"},
        {"category": "Photo Station & Favors", "percentage": 10.0, "notes": "Themed photo booth, holiday gift boxes"},
        {"category": "Contingency Reserve", "percentage": 8.0, "notes": "Weather contingency, coat check, transport"},
    ],
    "Other": [
        {"category": "Venue & Facilities", "percentage": 30.0, "notes": "Space rental, setup, baseline facilities"},
        {"category": "Food & Beverages", "percentage": 30.0, "notes": "Meal service, refreshments, coffee/tea"},
        {"category": "Entertainment & Audio/Visual", "percentage": 18.0, "notes": "Music, speakers, activities"},
        {"category": "Decor & Styling", "percentage": 12.0, "notes": "Table setups, banners, flowers"},
        {"category": "Stationery & Favors", "percentage": 4.0, "notes": "Guest communications and tokens"},
        {"category": "Contingency Reserve", "percentage": 6.0, "notes": "Emergency operational buffer"},
    ],
}


def validate_event_input(
    name: str | dict[str, Any] = "",
    event_type: str = "",
    date_str: str = "",
    location: str = "",
    guest_count: int | str = 0,
    budget: float | int | str = 0,
    currency: str = "USD",
    **kwargs: Any,
) -> tuple[bool, list[str]]:
    """Validate all event creation inputs deterministically.

    Supports positional arguments, keyword arguments (including 'venue' alias),
    or a single event dictionary. Normalizes whitespace across all fields.

    Returns:
        tuple[bool, list[str]]: (is_valid, list of error messages)
    """
    errors: list[str] = []

    # Handle dictionary input
    if isinstance(name, dict):
        data = name
        name = data.get("name") or data.get("event_name", "")
        event_type = data.get("event_type") or data.get("category") or data.get("type", "")
        date_str = data.get("date") or data.get("date_str") or data.get("event_date", "")
        location = (
            data.get("location")
            or data.get("venue")
            or data.get("Location")
            or data.get("Location / Venue")
            or data.get("location_venue")
            or ""
        )
        guest_count = data.get("guest_count") or data.get("guests") or data.get("guestCount", 0)
        budget = data.get("budget") or data.get("total_budget") or data.get("totalBudget", 0)

    # Fallback to kwargs for aliases (e.g. venue="London")
    if not location:
        location = (
            kwargs.get("venue")
            or kwargs.get("Location")
            or kwargs.get("Location / Venue")
            or kwargs.get("location_venue")
            or kwargs.get("venue_name")
            or ""
        )

    # Name validation
    cleaned_name = " ".join(str(name).split()) if name is not None else ""
    if not cleaned_name:
        errors.append("Event name cannot be empty.")
    elif len(cleaned_name) > 120:
        errors.append("Event name must be 120 characters or fewer.")

    # Event type validation
    cleaned_type = " ".join(str(event_type).split()) if event_type is not None else ""
    if not cleaned_type:
        errors.append("Please select or specify an event type.")

    # Date validation
    cleaned_date = str(date_str).strip() if date_str is not None else ""
    if not cleaned_date:
        errors.append("Event date is required.")
    else:
        try:
            parsed_date = datetime.strptime(cleaned_date, "%Y-%m-%d").date()
            # Verify year is reasonable (between 2000 and 2100)
            if parsed_date.year < 2000 or parsed_date.year > 2100:
                errors.append("Event year must be between 2000 and 2100.")
        except ValueError:
            errors.append("Event date must follow the format YYYY-MM-DD.")

    # Location validation (supports venue alias and robust whitespace trimming)
    cleaned_loc = " ".join(str(location).split()) if location is not None else ""
    if not cleaned_loc:
        errors.append("Location or venue is required.")
    elif len(cleaned_loc) > 200:
        errors.append("Location must be 200 characters or fewer.")

    # Guest count validation
    try:
        parsed_guests = int(guest_count)
        if parsed_guests <= 0:
            errors.append("Guest count must be at least 1.")
        elif parsed_guests > 100000:
            errors.append("Guest count cannot exceed 100,000.")
    except (ValueError, TypeError):
        errors.append("Guest count must be a valid whole number.")

    # Currency validation
    if isinstance(name, dict) and "currency" in name:
        raw_currency = name["currency"]
    elif currency is not None:
        raw_currency = currency
    else:
        raw_currency = kwargs.get("currency", "USD")

    cleaned_curr = str(raw_currency).strip().upper() if raw_currency is not None else ""
    if cleaned_curr not in SUPPORTED_CURRENCIES:
        errors.append(f"Unsupported currency '{raw_currency}'. Currency must be one of: {', '.join(SUPPORTED_CURRENCIES)}.")

    # Budget validation
    try:
        parsed_budget = float(budget)
        if parsed_budget <= 0:
            errors.append("Budget must be greater than zero.")
        elif parsed_budget > 100000000:
            errors.append("Budget cannot exceed 100,000,000.")
    except (ValueError, TypeError):
        errors.append("Budget must be a valid numeric amount.")

    return (len(errors) == 0, errors)




def calculate_budget_breakdown(
    budget: float,
    event_type: str = "Other",
    guest_count: int = 1,
) -> list[dict[str, Any]]:
    """Deterministically calculate budget allocations with exact penny precision.

    Guarantees:
    - sum(allocated_amount) == round(budget, 2)
    - percentages accurately reflect the profile
    - cost_per_guest is computed deterministically
    """
    total_budget = round(float(budget), 2)
    if total_budget <= 0:
        raise ValueError("Budget must be greater than zero.")

    guests = max(1, int(guest_count))
    profile = BUDGET_PROFILES.get(event_type, BUDGET_PROFILES["Other"])

    items: list[dict[str, Any]] = []
    running_total = 0.0

    for idx, cat in enumerate(profile):
        pct = cat["percentage"]
        allocated = round(total_budget * (pct / 100.0), 2)
        cost_per_guest = round(allocated / guests, 2)
        items.append(
            {
                "category": cat["category"],
                "percentage": pct,
                "allocated_amount": allocated,
                "actual_amount": 0.0,
                "cost_per_guest": cost_per_guest,
                "notes": cat.get("notes", ""),
            }
        )
        running_total += allocated

    # Penny discrepancy reconciliation to guarantee sum(allocated) == total_budget
    discrepancy = round(total_budget - running_total, 2)
    if discrepancy != 0.0 and items:
        # Apply discrepancy to the largest line item or contingency
        contingency_idx = next(
            (i for i, it in enumerate(items) if "Contingency" in it["category"]), 0
        )
        items[contingency_idx]["allocated_amount"] = round(
            items[contingency_idx]["allocated_amount"] + discrepancy, 2
        )
        items[contingency_idx]["cost_per_guest"] = round(
            items[contingency_idx]["allocated_amount"] / guests, 2
        )

    return items


def generate_timeline_plan(
    event_date_str: str,
    event_type: str = "Other",
) -> list[dict[str, Any]]:
    """Generate deterministic milestones and day-of itinerary based on event date."""
    timeline: list[dict[str, Any]] = []

    # Milestone checkpoints
    milestones = [
        ("Phase 1: Concept & Venue", "Finalize guest list estimate, secure venue contract, and define event aesthetic."),
        ("Phase 2: Primary Vendors", "Book caterer, photographer, and key musical entertainment."),
        ("Phase 3: Invitations & Design", "Send invitations/RSVPs, confirm floral styling, and order specialty rentals."),
        ("Phase 4: RSVPs & Final Headcount", "Collect final RSVPs, lock dietary requirements with caterer, finalize layout."),
        ("Phase 5: Week-Of Confirmation", "Distribute run-of-show to all vendors and prepare day-of payments & tips."),
        ("Phase 6: Eve of Event", "Inspect venue setup, review final checklist, and pack emergency celebration kit."),
    ]

    timeframes = [
        "6+ Months Out",
        "3-4 Months Out",
        "6-8 Weeks Out",
        "2-3 Weeks Out",
        "1 Week Out",
        "Day Before Event",
    ]

    for (title, desc), tf in zip(milestones, timeframes):
        timeline.append(
            {
                "timeframe": tf,
                "title": title,
                "description": desc,
                "category": "Milestone",
                "is_completed": False,
            }
        )

    # Day-Of Itinerary
    day_of_schedule = [
        ("09:00 AM", "Venue Access & Core Vendor Arrival", "Team loads in staging, audio visual equipment, and furniture."),
        ("11:30 AM", "Florals & Ambience Setup", "Centerpieces placed, lighting adjusted, signage erected."),
        ("01:30 PM", "Catering & Beverage Prep", "Catering team sets kitchen line, bar is stocked, ice delivered."),
        ("03:30 PM", "Photo & Video Pre-Shoots", "Portraits, venue overview shots, and detail documentation."),
        ("05:00 PM", "Guest Arrival & Welcome Refreshments", "Ambient music starts, coat check active, signature drinks poured."),
        ("06:00 PM", "Main Program / Ceremony", "Host welcome, focal ceremony or keynote speeches commence."),
        ("07:30 PM", "Dinner & Culinary Service", "Main meal service, wine service, and celebration toasts."),
        ("09:00 PM", "Party, Dancing & Social Celebration", "Dance floor opens, entertainment peak, evening dessert service."),
        ("11:30 PM", "Grand Finale & Send-Off", "Farewell sparklers/cheers, guest departure assistance."),
        ("12:00 AM", "Tear Down & Load Out", "Vendor strike, rental returns, venue inspection."),
    ]

    for time_slot, title, desc in day_of_schedule:
        timeline.append(
            {
                "timeframe": f"Day Of: {time_slot}",
                "title": title,
                "description": desc,
                "category": "Day-Of",
                "is_completed": False,
            }
        )

    return timeline


def generate_vendor_checklist(
    event_type: str,
    budget_items: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Deterministically generate the vendor checklist corresponding to budget categories."""
    category_vendors = {
        "Venue & Rentals": ["Venue Coordinator", "Rental Company (Tables, Chairs, Linens)"],
        "Catering & Bar": ["Primary Caterer", "Bartending Service", "Cake Designer"],
        "Photography & Video": ["Lead Photographer", "Videographer"],
        "Decor & Florals": ["Floral Designer", "Lighting & Rigging Specialist"],
        "Music & Entertainment": ["DJ / MC", "Live Musician / Band"],
        "Invitations & Favors": ["Stationery Designer", "Custom Favors Artisan"],
        "Contingency Reserve": ["Event Insurance Provider"],
    }

    # Fallback vendor set if no budget items passed
    default_categories = [
        "Venue Coordinator",
        "Primary Caterer",
        "Lead Photographer",
        "Floral & Decor Stylist",
        "DJ / Musician",
        "Cake / Dessert Artisan",
        "Transportation / Valet",
    ]

    checklist: list[dict[str, Any]] = []

    if budget_items:
        for b_item in budget_items:
            cat = b_item["category"]
            allocated = b_item.get("allocated_amount", 0.0)
            vendors = category_vendors.get(cat, [cat])
            share_each = round(allocated / len(vendors), 2) if vendors else 0.0

            for v_title in vendors:
                checklist.append(
                    {
                        "category": cat,
                        "name": v_title,
                        "status": "Needed",
                        "estimated_cost": share_each,
                        "actual_cost": 0.0,
                        "notes": f"Associated with {cat} allocation",
                    }
                )
    else:
        for v in default_categories:
            checklist.append(
                {
                    "category": "General",
                    "name": v,
                    "status": "Needed",
                    "estimated_cost": 0.0,
                    "actual_cost": 0.0,
                    "notes": "Essential vendor for smooth execution",
                }
            )

    return checklist
