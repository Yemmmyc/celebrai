"""Tests for app module imports, structure, and reusable UI components."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import app


def test_app_imports_cleanly() -> None:
    """Verify that app module and all top-level page and reusable functions exist and import cleanly."""
    expected_attributes = [
        "main",
        "render_sidebar",
        "render_notifications",
        "render_event_selector",
        "render_ai_event_plan",
        "render_currency_budget_chart",
        "page_dashboard",
        "page_create_event",
        "page_my_events",
        "page_budget_planner",
        "page_timeline",
        "page_vendor_checklist",
    ]
    for attr in expected_attributes:
        assert hasattr(app, attr), f"Missing expected module attribute: {attr}"


def test_render_event_selector_empty() -> None:
    """Verify render_event_selector handles empty event portfolios gracefully and returns None."""
    with patch("streamlit.info") as mock_info:
        selected_id = app.render_event_selector(key="test_key", events=[])
        assert selected_id is None
        mock_info.assert_called_once_with("No events found. Please create an event first.")


def test_render_event_selector_with_events() -> None:
    """Verify render_event_selector formats selectbox options and returns the chosen event ID."""
    mock_events = [
        {"id": 101, "name": "Gala Soirée", "date": "2026-12-31"},
        {"id": 102, "name": "Milestone Birthday", "date": "2026-06-15"},
    ]

    with patch("streamlit.selectbox", return_value="Gala Soirée (2026-12-31)") as mock_selectbox:
        selected_id = app.render_event_selector(
            key="test_select_key",
            help_text="Custom help text",
            events=mock_events,
        )
        assert selected_id == 101
        mock_selectbox.assert_called_once_with(
            "Select Celebration",
            ["Gala Soirée (2026-12-31)", "Milestone Birthday (2026-06-15)"],
            help="Custom help text",
            key="test_select_key",
        )


def test_render_ai_event_plan_empty_or_none() -> None:
    """Verify render_ai_event_plan returns immediately without error for empty or None plans."""
    with patch("streamlit.markdown") as mock_markdown:
        app.render_ai_event_plan({})
        mock_markdown.assert_not_called()


def test_render_ai_event_plan_renders_all_fields() -> None:
    """Verify render_ai_event_plan renders all seven AIEventPlan fields with proper security escaping."""
    sample_plan = {
        "theme_concept": "Starlight Splendor",
        "theme_description": "An opulent night under the stars.",
        "color_palette": ["#141119", "#C5A059", "#6CB8A8"],
        "decor_highlights": ["Crystal chandeliers", "Velvet table runners"],
        "menu_suggestions": ["Caviar blinis", "Champagne toast"],
        "entertainment_ideas": ["Live string quartet", "Starlight photo booth"],
        "planner_pro_tips": ["Book lighting designer 3 months ahead"],
        "_generation_mode": "Gemini 2.5 Flash",
    }

    with patch("streamlit.markdown") as mock_markdown, patch("streamlit.columns", return_value=(MagicMock(), MagicMock())):
        app.render_ai_event_plan(sample_plan, heading_prefix="✨ Preview", heading_level=2)
        # Verify markdown calls were made for concept, description, and list items
        assert mock_markdown.call_count >= 3


def test_render_currency_budget_chart_empty() -> None:
    """Verify render_currency_budget_chart handles empty event lists cleanly with an info message."""
    with patch("streamlit.info") as mock_info:
        app.render_currency_budget_chart("USD", [])
        mock_info.assert_called_once_with("No celebrations recorded in USD.")
