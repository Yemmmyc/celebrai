"""Tests for AI Service and structured schema validation."""

import os
from services.ai_service import (
    AIEventPlan,
    _generate_fallback_plan,
    get_ai_status,
    is_gemini_configured,
)


def test_ai_event_plan_pydantic_schema():
    """Verify AIEventPlan validates correct structures and sets defaults."""
    plan = AIEventPlan(
        theme_concept="Velvet & Starlight",
        theme_description="A decadent winter evening with moody lighting and deep jewel tones.",
        color_palette=["Plum (#2D1226)", "Gold (#D4AF37)", "Ivory (#FAF8F5)"],
        decor_highlights=["Draped velvet backdrops", "Floating candles in glass cylinders"],
        menu_suggestions=["Spiced pomegranate spritz", "Truffle risotto bites"],
        entertainment_ideas=["Vinyl record DJ set", "Bespoke perfume bar"],
        planner_pro_tips=["Pre-light all candles 20 minutes before doors open."],
    )
    assert plan.theme_concept == "Velvet & Starlight"
    assert len(plan.color_palette) == 3
    assert len(plan.decor_highlights) == 2


def test_fallback_plan_generation():
    """Verify fallback plan returns a complete, structured dictionary."""
    data = {
        "name": "Maya's 30th Birthday",
        "event_type": "Birthday",
        "theme": "Studio 54 Disco Glam",
        "guest_count": 50,
        "budget": 6000.0,
    }
    fallback = _generate_fallback_plan(data, reason="Test fallback")
    assert "_generation_mode" in fallback
    assert fallback["_generation_mode"] == "Deterministic Fallback"
    assert "theme_concept" in fallback
    assert len(fallback["color_palette"]) >= 3
    assert len(fallback["decor_highlights"]) >= 2
    assert len(fallback["menu_suggestions"]) >= 2


def test_ai_status_security():
    """Verify get_ai_status never leaks secret key material."""
    status = get_ai_status()
    assert "configured" in status
    assert "model" in status
    assert "provider" in status
    # Key should never appear in keys or values
    for k, v in status.items():
        assert "key" not in k.lower() or k == "configured"
        if isinstance(v, str):
            assert "AIza" not in v  # common Google API key prefix


def test_streamlit_secrets_retrieval(monkeypatch):
    """Verify that API key is retrieved from Streamlit secrets when not in os.environ."""
    from services.ai_service import _get_gemini_api_key, _get_gemini_model

    # Remove from env
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    # Mock streamlit.secrets
    import streamlit as st
    monkeypatch.setattr(st, "secrets", {"GEMINI_API_KEY": "test-key-from-secrets", "GEMINI_MODEL": "gemini-test-model"})

    assert _get_gemini_api_key() == "test-key-from-secrets"
    assert _get_gemini_model() == "gemini-test-model"

