"""Security utilities and notification management for CelebrAI.

Provides:
- Strict HTML escaping for dynamic text interpolated into unsafe HTML contexts (XSS prevention)
- Validation and sanitization for CSS color values (CSS injection prevention)
- Session-state-backed flash notification management persisting across Streamlit reruns
"""

from __future__ import annotations

import html
import re
from typing import Any

# Strict Hex Color Pattern: 3, 4, 6, or 8 hex digits preceded by #
HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

# RGB / RGBA Pattern: rgb(r, g, b) or rgba(r, g, b, a)
RGB_COLOR_PATTERN = re.compile(
    r"^rgba?\(\s*(?:25[0-5]|2[0-4]\d|1?\d?\d)\s*,\s*(?:25[0-5]|2[0-4]\d|1?\d?\d)\s*,\s*(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\s*,\s*(?:0|1|0?\.\d+))?\s*\)$"
)

# Safe Named CSS Colors (letters only, bounded length, no punctuation or control chars)
NAMED_COLOR_PATTERN = re.compile(r"^[a-zA-Z]{3,20}$")

# Disallowed CSS injection tokens
CSS_INJECTION_DISALLOWED = ("url", "expression", "javascript", ";", "{", "}", "<", ">", '"', "'", "\\")


def escape_text(val: Any) -> str:
    """Safely escape text content and HTML attributes using html.escape.

    Handles None, integers, floats, and strings without throwing exceptions.
    Converts quotes (", ') to HTML entities (&quot;, &#x27;) for attribute safety.
    """
    if val is None:
        return ""
    return html.escape(str(val), quote=True)


def is_valid_hex_color(color: str) -> bool:
    """Validate that a color string is a strict, well-formed hex color code."""
    if not isinstance(color, str):
        return False
    return bool(HEX_COLOR_PATTERN.fullmatch(color.strip()))


def is_safe_css_color(color: str) -> bool:
    """Validate that a color string is safe for interpolation into inline CSS styles.

    Prevents CSS injection attacks, URL exfiltration, and stylesheet breaking.
    """
    if not isinstance(color, str):
        return False
    cleaned = color.strip()
    if not cleaned or len(cleaned) > 40:
        return False

    lowered = cleaned.lower()
    for token in CSS_INJECTION_DISALLOWED:
        if token in lowered:
            return False

    return bool(
        HEX_COLOR_PATTERN.fullmatch(cleaned)
        or RGB_COLOR_PATTERN.fullmatch(cleaned)
        or NAMED_COLOR_PATTERN.fullmatch(cleaned)
    )


def sanitize_css_color(color: str, default: str = "#C5A059") -> str:
    """Return the color if valid and safe; otherwise return the fallback color."""
    if is_safe_css_color(color):
        return color.strip()
    return default


def set_notification(message: str, level: str = "success") -> None:
    """Queue a flash notification in Streamlit session state to persist across st.rerun().

    Levels supported: 'success', 'warning', 'info', 'error'.
    """
    try:
        import streamlit as st

        if "flash_notifications" not in st.session_state:
            st.session_state["flash_notifications"] = []
        st.session_state["flash_notifications"].append({
            "message": str(message),
            "level": str(level).lower(),
        })
    except Exception:
        # Fallback if accessed outside active Streamlit runtime (e.g., in unit tests)
        pass


def get_and_clear_notifications() -> list[dict[str, str]]:
    """Retrieve and drain all queued flash notifications from session state."""
    try:
        import streamlit as st

        if "flash_notifications" in st.session_state and st.session_state["flash_notifications"]:
            notifications = list(st.session_state["flash_notifications"])
            st.session_state["flash_notifications"] = []
            return notifications
    except Exception:
        pass
    return []

