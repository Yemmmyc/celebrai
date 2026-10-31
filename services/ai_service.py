"""AI Service for CelebrAI powered by Google Gemini.

Integrates with the google-genai SDK to generate structured, imaginative
event concepts, theme styling, decor, culinary ideas, and expert planner tips.

API keys are loaded securely from the environment and never logged or exposed.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

logger = logging.getLogger(__name__)

# Configurable Gemini model, defaulting to gemini-3.8-flash
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
DEFAULT_TIMEOUT_MS = 30000
GEMINI_TIMEOUT_MS = DEFAULT_TIMEOUT_MS



class AIEventPlan(BaseModel):
    """Structured Pydantic model for AI-generated celebration plans."""

    theme_concept: str = Field(
        default="Timeless Elegance & Warmth",
        description="A creative, evocative title for the celebration aesthetic",
    )
    theme_description: str = Field(
        default="A welcoming ambiance blending intimate charm with celebration.",
        description="A 2-3 sentence overview setting the mood, lighting, and vibe",
    )
    color_palette: list[str] = Field(
        default_factory=lambda: ["Warm Ivory", "Deep Plum", "Muted Teal", "Subtle Gold"],
        description="Harmonious color palette",
    )
    decor_highlights: list[str] = Field(
        default_factory=lambda: [
            "Ambient tapered candlelight with brass accents",
            "Low-profile floral centerpieces for effortless conversation",
            "Custom welcome mirror signage with calligraphy",
        ],
        description="Signature decor concepts",
    )
    menu_suggestions: list[str] = Field(
        default_factory=lambda: [
            "Signature Welcome Cocktail: Plum & Rosemary Gold Spritz",
            "Seasonal artisanal tasting boards with local cheeses and figs",
            "Individual dessert miniatures and custom cake cutting",
        ],
        description="Culinary and beverage highlights",
    )
    entertainment_ideas: list[str] = Field(
        default_factory=lambda: [
            "Curated acoustic lounge set transitioning to upbeat celebratory anthems",
            "Interactive memory guestbook with instant Polaroid camera station",
        ],
        description="Interactive guest experiences and activities",
    )
    planner_pro_tips: list[str] = Field(
        default_factory=lambda: [
            "Buffer 30 minutes between guest arrival and first formal announcement.",
            "Designate a dedicated vendor coordinator point-of-contact for the day.",
        ],
        description="Pro-tips for stress-free execution",
    )


def _get_gemini_api_key() -> str | None:
    """Retrieve GEMINI_API_KEY securely from environment variables or Streamlit secrets."""
    key = os.getenv("GEMINI_API_KEY")
    if key and key.strip():
        return key.strip()
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            s_key = st.secrets["GEMINI_API_KEY"]
            if s_key and str(s_key).strip():
                return str(s_key).strip()
    except Exception:
        pass
    return None


def _get_gemini_model() -> str:
    """Retrieve GEMINI_MODEL from environment or Streamlit secrets with default fallback."""
    model = os.getenv("GEMINI_MODEL")
    if model and model.strip():
        return model.strip()
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "GEMINI_MODEL" in st.secrets:
            s_model = st.secrets["GEMINI_MODEL"]
            if s_model and str(s_model).strip():
                return str(s_model).strip()
    except Exception:
        pass
    return DEFAULT_MODEL


def _get_gemini_timeout_ms() -> int:
    """Retrieve GEMINI_TIMEOUT_MS securely from environment or Streamlit secrets with safe fallback.

    Guarantees a positive integer, defaulting to 30000 ms (30 seconds).
    """
    candidates = []
    env_val = os.getenv("GEMINI_TIMEOUT_MS")
    if env_val is not None and str(env_val).strip():
        candidates.append(env_val)
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "GEMINI_TIMEOUT_MS" in st.secrets:
            s_val = st.secrets["GEMINI_TIMEOUT_MS"]
            if s_val is not None and str(s_val).strip():
                candidates.append(s_val)
    except Exception:
        pass

    for cand in candidates:
        try:
            val = int(str(cand).strip())
            if val > 0:
                return val
        except (ValueError, TypeError):
            continue

    return DEFAULT_TIMEOUT_MS


def is_gemini_configured() -> bool:
    """Check if GEMINI_API_KEY is present in the environment or secrets without exposing it."""
    key = _get_gemini_api_key()
    return bool(key)


def get_ai_status() -> dict[str, Any]:
    """Return status of AI engine for display in the dashboard."""
    configured = is_gemini_configured()
    model = _get_gemini_model()
    return {
        "configured": configured,
        "model": model if configured else "None (Deterministic Fallback)",
        "provider": "Google Gemini (google-genai)",
    }


def _generate_fallback_plan(event_data: dict[str, Any], reason: str = "") -> dict[str, Any]:
    """Generate a high-quality deterministic event plan when Gemini is unavailable."""
    event_type = event_data.get("event_type", "Celebration")
    name = event_data.get("name", "Event")
    theme = event_data.get("theme", "") or "Bespoke Elegance"

    fallback = AIEventPlan(
        theme_concept=f"{theme} — {event_type} Showcase",
        theme_description=(
            f"A thoughtfully curated aesthetic designed specifically for {name}. "
            "Combines rich visual textures, warm ambient lighting, and bespoke personal touches."
        ),
        color_palette=["Warm Ivory (#FAF8F5)", "Deep Plum (#2D1226)", "Muted Teal (#2E6F68)", "Subtle Gold (#D4AF37)"],
        decor_highlights=[
            f"Focal photo backdrop inspired by '{theme}' with layered textiles and florals",
            "Tabletop styling featuring textured linens, gold cutlery, and botanical accents",
            "Warm filament string lights and scattered votive candles for an intimate glow",
        ],
        menu_suggestions=[
            f"Signature Toast: CelebrAI Golden Fizz (sparkling cider/champagne with elderflower & plum)",
            "Artisanal farm-to-table grazing table during cocktail hour",
            "Custom themed dessert station featuring bite-sized tartlets and macarons",
        ],
        entertainment_ideas=[
            "Custom guestbook with audio recording or Polaroid snapshot prompts",
            "Curated background soundtrack tailored to each segment of the evening",
            "Surprise celebratory toast or personalized video retrospective",
        ],
        planner_pro_tips=[
            "Establish a vendor contact group chat 48 hours prior to the event.",
            "Pack an emergency day-of kit with lint rollers, stain pens, chargers, and safety pins.",
            "Schedule a 15-minute breather for the host right before the party begins.",
        ],
    )
    plan_dict = fallback.model_dump()
    plan_dict["_generation_mode"] = "Deterministic Fallback"
    if reason:
        plan_dict["_fallback_reason"] = reason
    return plan_dict


def generate_event_plan(event_data: dict[str, Any]) -> dict[str, Any]:
    """Generate an AI-powered event plan using Google Gemini with robust validation.

    Safely falls back to deterministic curated plan if GEMINI_API_KEY is not configured
    or if the API call experiences any network, timeout, or schema issues.
    """
    try:
        if not is_gemini_configured():
            return _generate_fallback_plan(event_data, reason="GEMINI_API_KEY not configured in environment or secrets.")

        model_name = _get_gemini_model()

        location_display = (
            event_data.get("location")
            or event_data.get("venue")
            or event_data.get("Location")
            or "Not specified"
        )

        prompt = f"""You are the AI Event Director for CelebrAI, a luxury celebration & event planner.
Generate a concise, creative event design plan for the following celebration:

- Event Type: {event_data.get('event_type')}
- Event Name: {event_data.get('name')}
- Date: {event_data.get('date')}
- Location / Venue: {location_display}
- Guest Count: {event_data.get('guest_count')}
- Total Budget: ${float(event_data.get('budget', 0)):,.2f}
- Desired Theme / Vibe: {event_data.get('theme', 'Not specified')}
- Host Preferences & Notes: {event_data.get('preferences', 'None')}

Guidelines for concise generation:
- Keep theme_description to approximately two brief, evocative sentences setting mood and lighting.
- Keep every list item to exactly one concise, punchy sentence.
- Avoid unnecessary elaboration, repetitive descriptions, and preambles.
- Return valid JSON directly matching the exact keys below.

JSON output structure:
{{
  "theme_concept": "Bespoke creative title for the celebration aesthetic",
  "theme_description": "Two brief evocative sentences describing mood, lighting, and ambiance.",
  "color_palette": ["Color 1 with hex code", "Color 2 with hex code", "Color 3 with hex code", "Color 4 with hex code"],
  "decor_highlights": ["Decor highlight 1 in one concise sentence.", "Decor highlight 2 in one concise sentence.", "Decor highlight 3 in one concise sentence."],
  "menu_suggestions": ["Signature welcome cocktail or mocktail.", "First culinary highlight in one concise sentence.", "Second culinary highlight in one concise sentence."],
  "entertainment_ideas": ["First interactive guest experience in one concise sentence.", "Second entertainment feature in one concise sentence."],
  "planner_pro_tips": ["First expert planner tip in one concise sentence.", "Second expert planner tip in one concise sentence."]
}}"""

        timeout_ms = _get_gemini_timeout_ms()
        last_exc = None

        for attempt in range(2):
            t_start = time.perf_counter()
            try:
                from google import genai
                from google.genai import types

                api_key = _get_gemini_api_key()
                client = genai.Client(api_key=api_key, http_options={"timeout": timeout_ms})

                # Configure structured JSON output with LOW thinking level for fast, reliable generation
                content_config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    thinking_config=types.ThinkingConfig(thinking_level="LOW"),
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=content_config,
                )

                elapsed_sec = round(time.perf_counter() - t_start, 2)
                logger.info(
                    "AI generation succeeded in %.2fs (model=%s, timeout_ms=%d, attempt=%d)",
                    elapsed_sec,
                    model_name,
                    timeout_ms,
                    attempt + 1,
                )

                if not response or not response.text:
                    return _generate_fallback_plan(event_data, reason="Gemini returned empty response.")

                # Clean potential markdown fences in text
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[len("```json"):].strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text[len("```"):].strip()
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3].strip()

                parsed_json = json.loads(raw_text)
                validated_plan = AIEventPlan(**parsed_json)
                result = validated_plan.model_dump()
                result["_generation_mode"] = f"Gemini ({model_name})"
                return result

            except ValidationError as val_err:
                elapsed_sec = round(time.perf_counter() - t_start, 2)
                logger.warning(
                    "AI output schema validation error after %.2fs: %s (model=%s)",
                    elapsed_sec,
                    type(val_err).__name__,
                    model_name,
                )
                return _generate_fallback_plan(event_data, reason="Schema validation mismatch. Using deterministic planning engine.")
            except Exception as exc:
                elapsed_sec = round(time.perf_counter() - t_start, 2)
                last_exc = exc
                exc_str = str(exc)
                exc_type = type(exc).__name__
                logger.warning(
                    "AI generation attempt %d failed after %.2fs: %s (model=%s, timeout_ms=%d)",
                    attempt + 1,
                    elapsed_sec,
                    exc_type,
                    model_name,
                    timeout_ms,
                )
                # If the error is high demand / 503, 504 / deadline exceeded, or timeout, break early to prevent long user wait
                if "503" in exc_str or "unavailable" in exc_str.lower() or "high demand" in exc_str.lower():
                    break
                if "504" in exc_str or "deadline_exceeded" in exc_str.lower() or "deadline expired" in exc_str.lower():
                    break
                if "timeout" in exc_type.lower() or "timeout" in exc_str.lower():
                    break

        # Determine concise, honest, safe fallback reason
        if last_exc:
            exc_str = str(last_exc)
            if "503" in exc_str or "unavailable" in exc_str.lower() or "high demand" in exc_str.lower():
                fallback_reason = "Google Gemini model temporarily experiencing high demand (503 Service Unavailable). Using deterministic planning engine."
            elif "504" in exc_str or "deadline_exceeded" in exc_str.lower() or "deadline expired" in exc_str.lower():
                fallback_reason = "Google Gemini request timed out (504 Deadline Exceeded). Using deterministic planning engine."
            elif "timeout" in type(last_exc).__name__.lower() or "timeout" in exc_str.lower():
                fallback_reason = "Google Gemini request timed out. Using deterministic planning engine."
            elif "429" in exc_str or "quota" in exc_str.lower():
                fallback_reason = "Gemini API rate limit or quota exceeded (429). Using deterministic planning engine."
            elif isinstance(last_exc, json.JSONDecodeError):
                fallback_reason = "Gemini response contained malformed JSON. Using deterministic planning engine."
            else:
                fallback_reason = f"Gemini API ({type(last_exc).__name__}). Using deterministic planning engine."
        else:
            fallback_reason = "Gemini service unavailable. Using deterministic planning engine."

        return _generate_fallback_plan(event_data, reason=fallback_reason)
    except Exception as outer_exc:
        logger.warning("Unexpected error during event plan generation: %s", type(outer_exc).__name__)
        return _generate_fallback_plan(event_data, reason="Unexpected error during AI generation. Using deterministic planning engine.")


