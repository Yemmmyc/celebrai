"""Tests for app module imports and structure."""

import importlib


def test_app_imports_cleanly():
    """Verify that app module can be imported without error."""
    import app

    assert hasattr(app, "main")
    assert hasattr(app, "render_sidebar")
    assert hasattr(app, "page_dashboard")
    assert hasattr(app, "page_create_event")
