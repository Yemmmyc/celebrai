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


def test_gemini_timeout_resolution(monkeypatch):
    """Verify timeout retrieval hierarchy, defaults to 30000ms, and validates safely."""
    from services.ai_service import _get_gemini_timeout_ms, DEFAULT_TIMEOUT_MS

    assert DEFAULT_TIMEOUT_MS == 30000

    # 1. Default when unset
    monkeypatch.delenv("GEMINI_TIMEOUT_MS", raising=False)
    import streamlit as st
    monkeypatch.setattr(st, "secrets", {})
    assert _get_gemini_timeout_ms() == 30000

    # 2. Environment variable override
    monkeypatch.setenv("GEMINI_TIMEOUT_MS", "45000")
    assert _get_gemini_timeout_ms() == 45000

    # 3. Streamlit secrets override when env unset
    monkeypatch.delenv("GEMINI_TIMEOUT_MS", raising=False)
    monkeypatch.setattr(st, "secrets", {"GEMINI_TIMEOUT_MS": "25000"})
    assert _get_gemini_timeout_ms() == 25000

    # 4. Safe fallback on non-integer or non-positive values (with no valid secrets)
    monkeypatch.setattr(st, "secrets", {})
    monkeypatch.setenv("GEMINI_TIMEOUT_MS", "invalid_number")
    assert _get_gemini_timeout_ms() == 30000

    monkeypatch.setenv("GEMINI_TIMEOUT_MS", "-5000")
    assert _get_gemini_timeout_ms() == 30000

    monkeypatch.setenv("GEMINI_TIMEOUT_MS", "0")
    assert _get_gemini_timeout_ms() == 30000

    # 5. Invalid env var falls back to valid Streamlit secrets
    monkeypatch.setenv("GEMINI_TIMEOUT_MS", "not-a-number")
    monkeypatch.setattr(st, "secrets", {"GEMINI_TIMEOUT_MS": "35000"})
    assert _get_gemini_timeout_ms() == 35000


def test_thinking_configuration_structure():
    """Verify GenerateContentConfig builds with LOW thinking level without errors."""
    from google.genai import types

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(thinking_level="LOW"),
    )
    assert config.response_mime_type == "application/json"
    assert str(config.thinking_config.thinking_level).upper() in ["LOW", "THINKINGLEVEL.LOW"]


def test_generate_event_plan_mocked_success(monkeypatch):
    """Verify generate_event_plan parses valid Gemini JSON and tags generation mode."""
    from services.ai_service import generate_event_plan
    import json

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key-for-mocking")

    valid_json_payload = json.dumps({
        "theme_concept": "Starlit Glasshouse",
        "theme_description": "An ethereal evening under glowing glass arches.",
        "color_palette": ["Gold", "Plum", "Ivory", "Emerald"],
        "decor_highlights": ["Fairy lights", "Candles", "Monstera runners"],
        "menu_suggestions": ["Spiced Cider", "Truffle Arancini", "Lemon Tart"],
        "entertainment_ideas": ["Acoustic Duo", "Polaroid Wall"],
        "planner_pro_tips": ["Pre-light candles early", "Check coat check staffing"],
    })

    class MockResponse:
        text = valid_json_payload

    class MockModels:
        def generate_content(self, model, contents, config):
            assert config.thinking_config.thinking_level == "LOW" or str(config.thinking_config.thinking_level) == "ThinkingLevel.LOW"
            return MockResponse()

    class MockClient:
        def __init__(self, api_key=None, http_options=None):
            assert http_options.get("timeout") == 30000
            self.models = MockModels()

    from google import genai
    monkeypatch.setattr(genai, "Client", MockClient)

    event_data = {
        "name": "Celebration Gala",
        "event_type": "Corporate Gala",
        "date": "2026-12-31",
        "location": "London",
        "guest_count": 100,
        "budget": 10000.0,
    }

    result = generate_event_plan(event_data)
    assert result["_generation_mode"] == "Gemini (gemini-3.8-flash)"
    assert result["theme_concept"] == "Starlit Glasshouse"
    assert len(result["color_palette"]) == 4


def test_generate_event_plan_fallback_on_504(monkeypatch):
    """Verify that a 504 Deadline Exceeded exception gracefully triggers deterministic fallback."""
    from services.ai_service import generate_event_plan

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key-for-mocking")

    class MockModels:
        def generate_content(self, model, contents, config):
            raise Exception("504 DEADLINE_EXCEEDED: Deadline expired before operation could complete.")

    class MockClient:
        def __init__(self, api_key=None, http_options=None):
            self.models = MockModels()

    from google import genai
    monkeypatch.setattr(genai, "Client", MockClient)

    event_data = {
        "name": "Elena's Birthday",
        "event_type": "Birthday",
        "date": "2026-11-15",
        "location": "London",
        "guest_count": 30,
        "budget": 4000.0,
        "theme": "Botanical Gold",
    }

    result = generate_event_plan(event_data)
    assert result["_generation_mode"] == "Deterministic Fallback"
    assert "504 Deadline Exceeded" in result["_fallback_reason"]
    assert "Botanical Gold" in result["theme_concept"]


def test_generate_event_plan_fallback_on_503(monkeypatch):
    """Verify that a 503 High Demand / Service Unavailable gracefully triggers deterministic fallback."""
    from services.ai_service import generate_event_plan

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key-for-mocking")

    class MockModels:
        def generate_content(self, model, contents, config):
            raise Exception("503 Service Unavailable: Model is overloaded due to high demand.")

    class MockClient:
        def __init__(self, api_key=None, http_options=None):
            self.models = MockModels()

    from google import genai
    monkeypatch.setattr(genai, "Client", MockClient)

    event_data = {"name": "Summer Soiree", "event_type": "Party", "theme": "Riviera Chic"}
    result = generate_event_plan(event_data)
    assert result["_generation_mode"] == "Deterministic Fallback"
    assert "503 Service Unavailable" in result["_fallback_reason"]


def test_generate_event_plan_fallback_on_429(monkeypatch):
    """Verify that a 429 Rate Limit / Quota Exceeded gracefully triggers deterministic fallback."""
    from services.ai_service import generate_event_plan

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key-for-mocking")

    class MockModels:
        def generate_content(self, model, contents, config):
            raise Exception("429 ResourceExhausted: Quota exceeded for quota metric.")

    class MockClient:
        def __init__(self, api_key=None, http_options=None):
            self.models = MockModels()

    from google import genai
    monkeypatch.setattr(genai, "Client", MockClient)

    event_data = {"name": "Winter Ball", "event_type": "Gala", "theme": "Frost & Velvet"}
    result = generate_event_plan(event_data)
    assert result["_generation_mode"] == "Deterministic Fallback"
    assert "429" in result["_fallback_reason"]


def test_generate_event_plan_fallback_on_malformed_json(monkeypatch):
    """Verify that malformed JSON from the API triggers clean deterministic fallback."""
    from services.ai_service import generate_event_plan

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key-for-mocking")

    class MockResponse:
        text = "This is not valid JSON at all {broken"

    class MockModels:
        def generate_content(self, model, contents, config):
            return MockResponse()

    class MockClient:
        def __init__(self, api_key=None, http_options=None):
            self.models = MockModels()

    from google import genai
    monkeypatch.setattr(genai, "Client", MockClient)

    event_data = {"name": "Art Exhibition", "event_type": "Exhibition", "theme": "Minimalist Light"}
    result = generate_event_plan(event_data)
    assert result["_generation_mode"] == "Deterministic Fallback"
    assert "malformed JSON" in result["_fallback_reason"]


def test_generate_event_plan_fallback_on_schema_mismatch(monkeypatch):
    """Verify that missing required keys or invalid schema types trigger schema fallback."""
    from services.ai_service import generate_event_plan
    import json

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key-for-mocking")

    # Missing expected fields or invalid types
    class MockResponse:
        text = json.dumps({"color_palette": "Not a list, this is a string"})

    class MockModels:
        def generate_content(self, model, contents, config):
            return MockResponse()

    class MockClient:
        def __init__(self, api_key=None, http_options=None):
            self.models = MockModels()

    from google import genai
    monkeypatch.setattr(genai, "Client", MockClient)

    event_data = {"name": "Fashion Show", "event_type": "Runway", "theme": "High Fashion"}
    result = generate_event_plan(event_data)
    assert result["_generation_mode"] == "Deterministic Fallback"
    assert "Schema validation mismatch" in result["_fallback_reason"]


def test_generate_event_plan_never_crashes(monkeypatch):
    """Verify that catastrophic unexpected exceptions are handled safely without crashing."""
    from services.ai_service import generate_event_plan

    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key-for-mocking")

    def crashing_func(*args, **kwargs):
        raise RuntimeError("Catastrophic unexpected runtime error")

    from google import genai
    monkeypatch.setattr(genai, "Client", crashing_func)

    event_data = {"name": "Resilience Test", "event_type": "Test"}
    result = generate_event_plan(event_data)
    assert result["_generation_mode"] == "Deterministic Fallback"
    assert "deterministic planning engine" in result["_fallback_reason"].lower()
