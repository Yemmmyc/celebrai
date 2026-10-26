"""CelebrAI — AI-Powered Celebration & Event Planner.

Phase 1 Streamlit Dashboard for PromptWars Virtual Challenge 5.
Styled in a luxury dark aesthetic: Deep Plum-Black (#141119),
Charcoal-Plum (#211B29), Muted Teal (#6CB8A8), Champagne Gold (#C5A059),
and Warm Ivory (#F4EEE7).
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from services.ai_service import generate_event_plan, get_ai_status, is_gemini_configured
from services.database import (
    delete_event,
    get_budget_items,
    get_dashboard_metrics,
    get_event,
    get_timeline_items,
    get_vendor_items,
    init_db,
    list_events,
    save_event,
    toggle_timeline_completed,
    update_budget_actual,
    update_event_status,
    update_vendor_item,
)
from services.planner import (
    EVENT_TYPES,
    SUPPORTED_CURRENCIES,
    calculate_budget_breakdown,
    format_currency,
    generate_timeline_plan,
    generate_vendor_checklist,
    get_currency_symbol,
    validate_event_input,
)


# Page Configuration
st.set_page_config(
    page_title="CelebrAI — AI-Powered Celebration & Event Planner",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
init_db()

# Centralized CSS for CelebrAI Luxury Dark System:
# Main (#100D14), Sidebar (#191320), Card (#211A29), Border (#2E2538)
# Text (#F5F0EA), Secondary (#B9ADBF), Gold (#C5A059), Teal (#2E6F68 / #6CB8A8)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global Typography & Base Styles */
    html, body, [class*="css"], .stMarkdown, p, span, label, div {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #F5F0EA;
    }

    .stApp {
        background-color: #100D14;
        color: #F5F0EA;
    }

    /* Headings Hierarchy */
    h1, .brand-font {
        font-family: 'Playfair Display', Georgia, serif;
        color: #F5F0EA;
        font-size: 1.95rem; /* ~31px */
        font-weight: 700;
        letter-spacing: -0.01em;
        line-height: 1.25;
    }
    h2 {
        font-family: 'Playfair Display', Georgia, serif;
        color: #F5F0EA;
        font-size: 1.45rem; /* ~23px */
        font-weight: 600;
        letter-spacing: -0.01em;
        line-height: 1.3;
    }
    h3 {
        font-family: 'Playfair Display', Georgia, serif;
        color: #F5F0EA;
        font-size: 1.25rem; /* ~20px */
        font-weight: 600;
        line-height: 1.35;
    }
    h4 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #F5F0EA;
        font-size: 1.05rem; /* ~17px */
        font-weight: 600;
        line-height: 1.4;
    }
    p, li {
        font-size: 0.95rem; /* ~15px */
        line-height: 1.55;
        color: #F5F0EA;
    }

    /* Compact Page Header */
    .page-header {
        margin-bottom: 1.4rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #2E2538;
    }
    .page-header-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.95rem;
        font-weight: 700;
        color: #F5F0EA;
        line-height: 1.2;
        margin: 0 0 0.25rem 0;
    }
    .page-header-subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.95rem;
        color: #B9ADBF;
        margin: 0;
        line-height: 1.45;
    }

    /* Metric Cards */
    .metric-card {
        background: #211A29;
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        border: 1px solid #2E2538;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        min-height: 124px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(197, 160, 89, 0.4);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    }
    .metric-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        color: #B9ADBF;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 1.95rem;
        font-weight: 700;
        color: #F5F0EA;
        line-height: 1.15;
    }
    .metric-sub {
        font-size: 0.85rem;
        color: #6CB8A8;
        margin-top: 0.35rem;
        font-weight: 500;
    }

    /* Content Cards & Spotlight Boxes */
    .content-box {
        background: #211A29;
        border-radius: 12px;
        padding: 1.5rem 1.6rem;
        border: 1px solid #2E2538;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        color: #F5F0EA;
    }
    .spotlight-box {
        background: #211A29;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        border: 1px solid #2E2538;
        border-left: 4px solid #C5A059;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
    }
    .spotlight-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #F5F0EA;
        margin: 0.35rem 0 0.35rem 0;
    }
    .spotlight-meta {
        color: #B9ADBF;
        font-size: 0.92rem;
        margin: 0;
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem 1.4rem;
        align-items: center;
    }

    /* AI Palette Chips */
    .palette-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin-top: 0.5rem;
    }
    .palette-chip {
        padding: 0.4rem 0.9rem;
        border-radius: 16px;
        font-size: 0.86rem;
        font-weight: 600;
        border: 1px solid #3A2F45;
        background: #191320;
        color: #F5F0EA;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 10px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .status-planning {
        background: rgba(240, 179, 108, 0.12);
        color: #F0B36C;
        border: 1px solid rgba(240, 179, 108, 0.35);
    }
    .status-confirmed {
        background: rgba(108, 184, 168, 0.12);
        color: #6CB8A8;
        border: 1px solid rgba(108, 184, 168, 0.35);
    }
    .status-completed {
        background: rgba(191, 162, 234, 0.12);
        color: #BFA2EA;
        border: 1px solid rgba(191, 162, 234, 0.35);
    }

    /* Buttons with Champagne Gold Accents */
    div.stButton > button:first-child {
        background: #211A29;
        color: #F5F0EA;
        border: 1px solid #C5A059;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-size: 0.92rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.15s ease;
    }
    div.stButton > button:first-child:hover {
        background: #2E2538;
        border-color: #E0BA6A;
        color: #FFFFFF;
        box-shadow: 0 4px 14px rgba(197, 160, 89, 0.2);
        transform: translateY(-1px);
    }
    div.stButton > button:first-child:active,
    div.stButton > button:first-child:focus {
        outline: none;
        box-shadow: 0 0 0 2px #C5A059;
    }

    /* Form Submit Button */
    div.stFormSubmitButton > button:first-child {
        background: linear-gradient(135deg, #2A2033 0%, #3B2A4A 100%);
        color: #F5F0EA;
        border: 1px solid #C5A059;
        border-radius: 8px;
        padding: 0.65rem 1.4rem;
        font-size: 0.95rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.2s ease;
    }
    div.stFormSubmitButton > button:first-child:hover {
        background: linear-gradient(135deg, #3B2A4A 0%, #4D3560 100%);
        border-color: #E0BA6A;
        color: #FFFFFF;
        box-shadow: 0 4px 16px rgba(197, 160, 89, 0.25);
        transform: translateY(-1px);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #191320 !important;
        border-right: 1px solid #2E2538 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #F5F0EA;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 0.5rem 0.8rem !important;
        border-radius: 8px !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        color: #B9ADBF !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: #211A29 !important;
        color: #F5F0EA !important;
    }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] > div,
    [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: #211A29 !important;
        color: #C5A059 !important;
        font-weight: 600 !important;
    }

    /* Form Inputs, Dropdowns & Textareas */
    [data-testid="stWidgetLabel"] p, label {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #F5F0EA !important;
        margin-bottom: 0.25rem !important;
    }
    [data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"] {
        background-color: #191320 !important;
        border: 1px solid #2E2538 !important;
        border-radius: 8px !important;
        color: #F5F0EA !important;
        font-size: 0.92rem !important;
    }
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
        border-color: #C5A059 !important;
        box-shadow: 0 0 0 1px #C5A059 !important;
    }
    [data-baseweb="select"] > div {
        background-color: #191320 !important;
        border: 1px solid #2E2538 !important;
        color: #F5F0EA !important;
        border-radius: 8px !important;
        font-size: 0.92rem !important;
    }

    /* Timeline Cards */
    .timeline-card {
        background: #211A29;
        border-radius: 10px;
        padding: 0.9rem 1.15rem;
        border: 1px solid #2E2538;
        border-left: 3px solid #C5A059;
        margin-bottom: 0.65rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .timeline-card-completed {
        background: #191320;
        border-radius: 10px;
        padding: 0.9rem 1.15rem;
        border: 1px solid #251D2D;
        border-left: 3px solid #2E6F68;
        margin-bottom: 0.65rem;
        opacity: 0.85;
    }
    .timeline-tag {
        font-size: 0.8rem;
        font-weight: 700;
        color: #C5A059;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .timeline-tag-completed {
        font-size: 0.8rem;
        font-weight: 700;
        color: #6CB8A8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .timeline-title {
        margin: 0.2rem 0 0.2rem 0;
        font-family: 'Playfair Display', serif;
        color: #F5F0EA;
        font-size: 1.1rem;
    }
    .timeline-title-completed {
        margin: 0.2rem 0 0.2rem 0;
        font-family: 'Playfair Display', serif;
        color: #8C8294;
        font-size: 1.1rem;
        text-decoration: line-through;
    }
    .timeline-desc {
        margin: 0;
        color: #B9ADBF;
        font-size: 0.88rem;
        line-height: 1.45;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #211A29 !important;
        border: 1px solid #2E2538 !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary {
        color: #F5F0EA !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }

    /* Tabs */
    [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid #2E2538 !important;
        gap: 0.8rem;
    }
    [data-baseweb="tab"] {
        color: #B9ADBF !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 0.9rem !important;
    }
    [aria-selected="true"][data-baseweb="tab"] {
        color: #C5A059 !important;
        border-bottom-color: #C5A059 !important;
        font-weight: 600 !important;
    }

    /* Dataframes & Tables */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #2E2538;
    }
    [data-testid="stDataFrame"] div {
        font-size: 0.9rem !important;
    }

    /* Captions and Footnotes */
    [data-testid="stCaptionContainer"] {
        font-size: 0.82rem !important;
        color: #B9ADBF !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_sidebar() -> str:
    """Render branded sidebar navigation and return selected page."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem 0;">
                <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.2rem;">
                    <span style="font-size: 1.5rem;">✨</span>
                    <span style="font-family: 'Playfair Display', serif; color: #F5F0EA; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.01em;">
                        CelebrAI
                    </span>
                </div>
                <p style="color: #B9ADBF; font-size: 0.84rem; margin: 0; font-weight: 500;">
                    Bespoke Celebration Studio
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_options = [
            "Dashboard",
            "Create Event",
            "My Events",
            "Budget Planner",
            "Timeline",
            "Vendor Checklist",
        ]

        if "nav_page" not in st.session_state:
            st.session_state.nav_page = "Dashboard"

        # Safe index lookup
        current_idx = (
            nav_options.index(st.session_state.nav_page)
            if st.session_state.nav_page in nav_options
            else 0
        )

        selected_page = st.radio(
            "Navigation",
            nav_options,
            index=current_idx,
            label_visibility="collapsed",
            key="sidebar_nav_selection",
        )
        st.session_state.nav_page = selected_page

        st.markdown("<hr style='border: none; border-bottom: 1px solid #2E2538; margin: 1.2rem 0;'>", unsafe_allow_html=True)

        # Engine & Persistence Status Badge
        ai_info = get_ai_status()
        status_color = "#6CB8A8" if ai_info["configured"] else "#F0B36C"
        status_icon = "🟢" if ai_info["configured"] else "🟡"
        status_text = (
            f"Gemini Active ({ai_info['model']})"
            if ai_info["configured"]
            else "Rule-Based Fallback"
        )

        st.markdown(
            f"""
            <div style="background: #211A29; border-radius: 8px; padding: 0.75rem 0.9rem; border: 1px solid #2E2538; font-size: 0.82rem;">
                <div style="color: #B9ADBF; font-weight: 600; margin-bottom: 0.25rem; letter-spacing: 0.05em; font-size: 0.74rem;">SYSTEM STATUS</div>
                <div style="color: {status_color}; font-weight: 600;">{status_icon} {status_text}</div>
                <div style="color: #B9ADBF; margin-top: 0.25rem;">💾 SQLite Persistence: Ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("CelebrAI Studio • Challenge 5")

        return selected_page


def page_dashboard() -> None:
    """Render the master executive dashboard with summary metrics, countdowns, and quick actions."""
    # Compact Header with Primary Action
    c_head_left, c_head_right = st.columns([3, 1])
    with c_head_left:
        st.markdown(
            """
            <div class="page-header" style="border-bottom: none; margin-bottom: 0; padding-bottom: 0;">
                <h1 class="page-header-title">Executive Dashboard</h1>
                <p class="page-header-subtitle">Celebration Portfolio & Financial Overview</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_head_right:
        st.write("")
        if st.button("✨ New Celebration", key="dash_new_btn", width="stretch"):
            st.session_state.nav_page = "Create Event"
            st.rerun()

    st.markdown("<hr style='border: none; border-bottom: 1px solid #2E2538; margin: 0.6rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    metrics = get_dashboard_metrics()
    events = list_events()

    # Metric Row (4 KPI Cards with uniform height)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Total Celebrations</div>
                    <div class="metric-value">{metrics['total_events']}</div>
                </div>
                <div class="metric-sub">{len([e for e in events if e.get('status') == 'Planning'])} in planning</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        budget_by_curr = metrics.get("budget_by_currency", {})
        actual_by_curr = metrics.get("actual_by_currency", {})
        b_strs = [format_currency(amt, c, decimals=0) for c, amt in budget_by_curr.items() if amt > 0]
        a_strs = [format_currency(amt, c, decimals=0) for c, amt in actual_by_curr.items() if amt > 0]

        if b_strs:
            disp_budget = " | ".join(b_strs)
        elif budget_by_curr:
            disp_budget = " | ".join([format_currency(0, c, decimals=0) for c in sorted(budget_by_curr.keys())])
        else:
            disp_budget = "—"

        if a_strs:
            disp_actual = f"{' | '.join(a_strs)} committed spend"
        elif actual_by_curr and any(v > 0 for v in actual_by_curr.values()):
            disp_actual = f"{' | '.join([format_currency(amt, c, decimals=0) for c, amt in actual_by_curr.items()])} committed spend"
        else:
            disp_actual = "No committed spend yet"

        val_font_size = "1.2rem" if len(b_strs) > 1 else "1.45rem"
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Total Planned Budget</div>
                    <div class="metric-value" style="font-size: {val_font_size};">{disp_budget}</div>
                </div>
                <div class="metric-sub">{disp_actual}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Honored Guests</div>
                    <div class="metric-value">{metrics['total_guests']:,}</div>
                </div>
                <div class="metric-sub">Across portfolio</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        next_ev = metrics.get("next_event")
        if next_ev:
            try:
                target_date = datetime.strptime(next_ev["date"], "%Y-%m-%d").date()
                days_left = (target_date - date.today()).days
                sub_text = f"{days_left}d away ({next_ev['date']})"
                disp_val = f"{days_left}d" if days_left >= 0 else "Today"
            except Exception:
                disp_val = "—"
                sub_text = next_ev.get("date", "")
        else:
            disp_val = "—"
            sub_text = "No upcoming events"

        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Next Celebration</div>
                    <div class="metric-value">{disp_val}</div>
                </div>
                <div class="metric-sub">{sub_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Empty State or Events Spotlight
    if not events:
        st.markdown(
            """
            <div class="content-box" style="text-align: center; padding: 3rem 2rem;">
                <div style="font-size: 2.8rem; margin-bottom: 0.6rem;">🥂</div>
                <h2 style="font-size: 1.6rem; margin-bottom: 0.5rem; color: #F5F0EA;">Your Celebration Portfolio is Awaiting Its First Moment</h2>
                <p style="color: #B9ADBF; max-width: 540px; margin: 0 auto 1.5rem auto; font-size: 0.95rem; line-height: 1.55;">
                    Whether orchestrating an opulent wedding, milestone birthday, or corporate gala, CelebrAI pairs strict Python financial allocations with Gemini creative styling.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("✨ Begin Planning Your First Celebration", width="stretch"):
                st.session_state.nav_page = "Create Event"
                st.rerun()

    else:
        # Spotlight Next Event Card
        if metrics.get("next_event"):
            nev = metrics["next_event"]
            nev_curr = nev.get("currency", "USD")
            formatted_spotlight_budget = format_currency(nev["budget"], nev_curr)
            st.markdown(
                f"""
                <div class="spotlight-box">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
                        <div>
                            <span class="status-badge status-confirmed">Upcoming Milestone</span>
                            <div class="spotlight-title">{nev['name']}</div>
                            <div class="spotlight-meta">
                                <span>📍 {nev['location']}</span>
                                <span>📅 {nev['date']}</span>
                                <span>👥 {nev['guest_count']} Guests</span>
                                <span>💰 {formatted_spotlight_budget}</span>
                            </div>
                        </div>
                        <div style="text-align: right; margin-top: 0.3rem;">
                            <span style="font-size: 0.88rem; color: #6CB8A8; font-weight: 600;">Theme: {nev.get('theme') or 'Bespoke Concept'}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Portfolio Overview Charts & Recent Table
        col_left, col_right = st.columns([11, 9], gap="large")

        with col_left:
            st.markdown("### Recent Celebrations")
            event_records = []
            for ev in events[:6]:
                ev_curr = ev.get("currency", "USD")
                event_records.append(
                    {
                        "ID": ev["id"],
                        "Name": ev["name"],
                        "Category": ev["event_type"],
                        "Date": ev["date"],
                        "Guests": ev["guest_count"],
                        "Currency": ev_curr,
                        "Budget": format_currency(ev["budget"], ev_curr),
                        "Status": ev["status"],
                    }
                )
            df_events = pd.DataFrame(event_records)
            st.dataframe(df_events, hide_index=True, width="stretch")

        with col_right:
            # Group events strictly by currency to prevent cross-currency summation
            events_by_curr: dict[str, list[dict[str, Any]]] = {}
            for ev in events:
                curr_code = ev.get("currency") or "USD"
                events_by_curr.setdefault(curr_code, []).append(ev)

            currencies_present = sorted(list(events_by_curr.keys()))

            def _render_currency_budget_chart(curr_code: str, curr_events: list[dict[str, Any]]) -> None:
                sym = get_currency_symbol(curr_code)
                type_agg: dict[str, dict[str, Any]] = {}
                for ev in curr_events:
                    etype = ev.get("event_type", "Other")
                    if etype not in type_agg:
                        type_agg[etype] = {"budget": 0.0, "count": 0}
                    type_agg[etype]["budget"] += float(ev.get("budget", 0.0))
                    type_agg[etype]["count"] += 1

                chart_rows = [
                    {
                        "Event Type": etype,
                        "Total Budget": data["budget"],
                        "Formatted Budget": format_currency(data["budget"], curr_code, decimals=0),
                        "Celebrations": data["count"],
                    }
                    for etype, data in type_agg.items()
                ]
                chart_data = pd.DataFrame(chart_rows)

                if chart_data.empty:
                    st.info(f"No celebrations recorded in {curr_code}.")
                    return

                chart = (
                    alt.Chart(chart_data)
                    .mark_bar(cornerRadius=5)
                    .encode(
                        x=alt.X(
                            "Total Budget:Q",
                            title=f"Total Budget ({sym} {curr_code})",
                            axis=alt.Axis(
                                labelColor="#F5F0EA",
                                titleColor="#C5A059",
                                gridColor="#241C2D",
                                labelFlush=False,
                            ),
                        ),
                        y=alt.Y(
                            "Event Type:N",
                            sort="-x",
                            title=None,
                            axis=alt.Axis(
                                labelColor="#F5F0EA",
                                labelLimit=130,
                            ),
                        ),
                        color=alt.Color(
                            "Event Type:N",
                            scale=alt.Scale(
                                range=[
                                    "#2E6F68",
                                    "#C5A059",
                                    "#9B5DE5",
                                    "#E07A5F",
                                    "#81B29A",
                                    "#A67C94",
                                ]
                            ),
                            legend=None,
                        ),
                        tooltip=[
                            alt.Tooltip("Event Type:N", title="Category"),
                            alt.Tooltip("Formatted Budget:N", title=f"Budget ({sym} {curr_code})"),
                            alt.Tooltip("Celebrations:Q", title="Celebrations"),
                        ],
                    )
                    .properties(height=230)
                    .configure_view(strokeWidth=0)
                    .configure(background="transparent")
                )
                st.altair_chart(chart, width="stretch")

            if len(currencies_present) == 1:
                single_curr = currencies_present[0]
                single_sym = get_currency_symbol(single_curr)
                st.markdown(f"### Budget by Event Type ({single_sym} {single_curr})")
                _render_currency_budget_chart(single_curr, events_by_curr[single_curr])
            elif len(currencies_present) > 1:
                st.markdown("### Budget by Event Type (by Currency)")
                tabs = st.tabs([f"{c} ({get_currency_symbol(c)})" for c in currencies_present])
                for tab, c in zip(tabs, currencies_present):
                    with tab:
                        _render_currency_budget_chart(c, events_by_curr[c])
            else:
                st.markdown("### Budget by Event Type")
                st.info("No budget data available.")


def page_create_event() -> None:
    """Render the Create Event form with Gemini styling and deterministic calculations."""
    st.markdown(
        """
        <div class="page-header">
            <h1 class="page-header-title">Create New Celebration</h1>
            <p class="page-header-subtitle">Design a bespoke celebration plan pairing Gemini creative styling with deterministic financial allocations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feedback and status message placeholder
    status_placeholder = st.empty()

    with st.form("create_event_form", clear_on_submit=False):
        st.markdown("### 1. Celebration Basics")
        col1, col2 = st.columns(2)

        with col1:
            event_name = st.text_input(
                "Celebration Name *",
                value=st.session_state.get("ce_name", ""),
                placeholder="e.g., Alexandra & David's Autumn Gala",
                help="Give your event an evocative or descriptive title",
                key="ce_name",
            )
            type_default_idx = (
                EVENT_TYPES.index(st.session_state["ce_type"])
                if "ce_type" in st.session_state and st.session_state["ce_type"] in EVENT_TYPES
                else 0
            )
            event_type = st.selectbox(
                "Event Category *",
                EVENT_TYPES,
                index=type_default_idx,
                key="ce_type",
            )
            event_date = st.date_input(
                "Celebration Date *",
                value=st.session_state.get("ce_date", date.today()),
                help="Date on which the celebration will take place",
                key="ce_date",
            )

        with col2:
            location = st.text_input(
                "Location / Venue *",
                value=st.session_state.get("ce_location", ""),
                placeholder="e.g., The Glasshouse Conservatory, London",
                help="City, venue name, or destination",
                key="ce_location",
            )
            guest_count = st.number_input(
                "Expected Guest Count *",
                min_value=1,
                max_value=50000,
                value=st.session_state.get("ce_guests", 75),
                step=5,
                key="ce_guests",
            )
            c_curr, c_bgt = st.columns([1, 2])
            with c_curr:
                curr_default_idx = (
                    SUPPORTED_CURRENCIES.index(st.session_state["ce_currency"])
                    if "ce_currency" in st.session_state and st.session_state["ce_currency"] in SUPPORTED_CURRENCIES
                    else 0
                )
                currency = st.selectbox(
                    "Currency *",
                    SUPPORTED_CURRENCIES,
                    index=curr_default_idx,
                    key="ce_currency",
                )
            with c_bgt:
                curr_sym = get_currency_symbol(currency)
                budget = st.number_input(
                    f"Total Budget ({curr_sym}) *",
                    min_value=1.0,
                    max_value=100000000.0,
                    value=float(st.session_state.get("ce_budget", 15000.0)),
                    step=1.0,
                    format="%.2f",
                    help="Deterministic Python algorithms allocate exact penny amounts to all categories",
                    key="ce_budget",
                )

        st.markdown("### 2. Creative Vision & Preferences")
        col3, col4 = st.columns(2)

        with col3:
            theme = st.text_input(
                "Desired Aesthetic / Theme",
                value=st.session_state.get("ce_theme", ""),
                placeholder="e.g., Parisian Midnight, Tuscan Sunset, Moody Romantic, Celestial Minimalist",
                key="ce_theme",
            )

        with col4:
            preferences = st.text_area(
                "Host Preferences, Dietary, & Vibe Notes",
                value=st.session_state.get("ce_preferences", ""),
                placeholder="e.g., Champagne tower, vegan culinary options, live jazz quartet, no plastic",
                height=68,
                key="ce_preferences",
            )

        use_ai = st.checkbox(
            "✨ Generate AI Styling & Creative Event Plan with Gemini",
            value=st.session_state.get("ce_use_ai", True),
            help="Generates tailored color palettes, decor concepts, signature cocktails, and planner pro-tips",
            key="ce_use_ai",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "✨ Generate & Save Celebration Plan", width="stretch"
        )

    if submitted:
        # Clear any stale status before validating
        status_placeholder.empty()

        # Validate inputs deterministically (handles venue alias, whitespace, and currency)
        is_valid, errors = validate_event_input(
            name=event_name,
            event_type=event_type,
            date_str=event_date.strftime("%Y-%m-%d"),
            location=location,
            guest_count=guest_count,
            budget=budget,
            currency=currency,
        )

        if not is_valid:
            for err in errors:
                st.error(f"⚠️ {err}")
            return

        # Prevent accidental duplicate saves on retry
        cleaned_loc_val = " ".join(str(location).split())
        sub_sig = f"{event_name.strip()}|{event_date.strftime('%Y-%m-%d')}|{cleaned_loc_val}|{currency}|{float(budget):.2f}"
        if st.session_state.get("last_created_event_sig") == sub_sig:
            prev_id = st.session_state.get("last_created_event_id")
            st.warning(
                f"⚠️ This celebration '{event_name.strip()}' has already been generated and saved "
                f"(ID #{prev_id}). Check 'My Events' to view or edit it."
            )
            return

        # Scoped spinner container: guaranteed to stop on success or failure
        with status_placeholder.container():
            with st.spinner("CelebrAI is generating your bespoke celebration plan..."):
                event_payload = {
                    "name": event_name.strip(),
                    "event_type": event_type,
                    "date": event_date.strftime("%Y-%m-%d"),
                    "location": cleaned_loc_val,
                    "guest_count": int(guest_count),
                    "currency": currency,
                    "budget": float(budget),
                    "theme": theme.strip(),
                    "preferences": preferences.strip(),
                    "status": "Planning",
                }

                # AI Plan generation with timeout and deterministic fallback
                if use_ai:
                    ai_plan = generate_event_plan(event_payload)
                else:
                    from services.ai_service import _generate_fallback_plan

                    ai_plan = _generate_fallback_plan(event_payload, reason="User opted for rule-based planning.")

                event_payload["ai_plan_json"] = ai_plan

                # Deterministic budget calculation (Python arithmetic)
                budget_items = calculate_budget_breakdown(
                    budget=float(budget),
                    event_type=event_type,
                    guest_count=int(guest_count),
                )

                # Deterministic timeline and vendor checklist
                timeline_items = generate_timeline_plan(
                    event_date_str=event_payload["date"],
                    event_type=event_type,
                )
                vendor_items = generate_vendor_checklist(
                    event_type=event_type,
                    budget_items=budget_items,
                )

                # Save atomically to SQLite
                new_id = save_event(
                    event_data=event_payload,
                    budget_items=budget_items,
                    timeline_items=timeline_items,
                    vendor_items=vendor_items,
                )

                # Record submission signature for duplicate prevention
                st.session_state["last_created_event_sig"] = sub_sig
                st.session_state["last_created_event_id"] = new_id

        # Empty status placeholder to ensure spinner disappears completely
        status_placeholder.empty()

        st.success(
            f"🎉 Celebration **'{event_name.strip()}'** (ID #{new_id}) successfully created and saved to SQLite!"
        )

        # Immediate preview of the newly generated plan
        st.markdown("---")
        if ai_plan.get("_generation_mode") == "Deterministic Fallback":
            fb_reason = ai_plan.get("_fallback_reason", "AI generation unavailable.")
            st.warning(f"⚙️ **Deterministic Rule-Based Plan Active**: {fb_reason}")
        else:
            st.caption("✨ Plan generated with Gemini AI")

        st.markdown(f"## ✨ Preview: {ai_plan.get('theme_concept', 'Creative Concept')}")

        st.markdown(
            f"""
            <div class="content-box">
                <p style="font-size: 1.1rem; line-height: 1.6; color: #F4EEE7;">
                    {ai_plan.get('theme_description', '')}
                </p>
                <div style="margin-top: 1rem;">
                    <strong style="color: #C5A059;">Curated Color Palette:</strong>
                    <div class="palette-container">
                        {''.join([f'<span class="palette-chip">{c}</span>' for c in ai_plan.get('color_palette', [])])}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown("#### 🌿 Decor & Styling Highlights")
            for d in ai_plan.get("decor_highlights", []):
                st.markdown(f"- {d}")

            st.markdown("#### 🍸 Culinary & Beverage Highlights")
            for m in ai_plan.get("menu_suggestions", []):
                st.markdown(f"- {m}")

        with c_b:
            st.markdown("#### 🎵 Entertainment & Guest Experience")
            for ent in ai_plan.get("entertainment_ideas", []):
                st.markdown(f"- {ent}")

            st.markdown("#### 💡 Expert Planner Pro-Tips")
            for tip in ai_plan.get("planner_pro_tips", []):
                st.markdown(f"- {tip}")

        st.info("💡 You can now view or adjust this celebration in **My Events**, **Budget Planner**, **Timeline**, or **Vendor Checklist** via the sidebar.")


def page_my_events() -> None:
    """List and manage all celebration records."""
    st.markdown(
        """
        <div class="page-header">
            <h1 class="page-header-title">My Celebrations</h1>
            <p class="page-header-subtitle">Review, filter, and inspect detailed plans across your event portfolio.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    events = list_events()

    if not events:
        st.info("No celebrations found. Create your first event using the **Create Event** page.")
        return

    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        type_options = ["All"] + EVENT_TYPES
        filter_type = st.selectbox("Filter by Category", type_options, index=0)
    with col_f2:
        filter_status = st.selectbox(
            "Filter by Status", ["All", "Planning", "Confirmed", "Completed"], index=0
        )

    filtered_events = list_events(
        status_filter=filter_status,
        type_filter=filter_type,
    )

    st.markdown(f"**Showing {len(filtered_events)} celebration(s)**")

    for ev in filtered_events:
        curr = ev.get("currency", "USD")
        with st.expander(
            f"✨ {ev['name']} — {ev['event_type']} ({ev['date']}) | Status: {ev['status']}",
            expanded=False,
        ):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"<div style='background: #191320; border: 1px solid #2E2538; border-radius: 8px; padding: 0.6rem 0.8rem;'><div style='color: #B9ADBF; font-size: 0.78rem; text-transform: uppercase; font-weight: 600;'>Date</div><div style='font-size: 1rem; font-weight: 600; color: #F5F0EA;'>{ev['date']}</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='background: #191320; border: 1px solid #2E2538; border-radius: 8px; padding: 0.6rem 0.8rem;'><div style='color: #B9ADBF; font-size: 0.78rem; text-transform: uppercase; font-weight: 600;'>Guests</div><div style='font-size: 1rem; font-weight: 600; color: #F5F0EA;'>{ev['guest_count']:,}</div></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div style='background: #191320; border: 1px solid #2E2538; border-radius: 8px; padding: 0.6rem 0.8rem;'><div style='color: #B9ADBF; font-size: 0.78rem; text-transform: uppercase; font-weight: 600;'>Budget</div><div style='font-size: 1rem; font-weight: 600; color: #C5A059;'>{format_currency(ev['budget'], curr)}</div></div>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<div style='background: #191320; border: 1px solid #2E2538; border-radius: 8px; padding: 0.6rem 0.8rem;'><div style='color: #B9ADBF; font-size: 0.78rem; text-transform: uppercase; font-weight: 600;'>Per Guest</div><div style='font-size: 1rem; font-weight: 600; color: #6CB8A8;'>{format_currency(ev['budget'] / max(1, ev['guest_count']), curr)}</div></div>", unsafe_allow_html=True)

            st.markdown(f"**Venue / Location:** {ev['location']}")
            if ev.get("theme"):
                st.markdown(f"**Theme / Vibe:** {ev['theme']}")
            if ev.get("preferences"):
                st.markdown(f"**Special Notes:** {ev['preferences']}")

            # AI Plan Details (Full Creative Narrative, Palette, Decor, Culinary, Activities, Tips)
            ai_plan = ev.get("ai_plan")
            if ai_plan:
                st.markdown("---")
                if ai_plan.get("_generation_mode") == "Deterministic Fallback":
                    fb_reason = ai_plan.get("_fallback_reason", "Deterministic rule-based planning.")
                    st.warning(f"⚙️ **Deterministic Fallback Plan Active**: {fb_reason}")
                else:
                    st.caption("✨ Bespoke Creative Plan powered by Gemini AI")

                st.markdown(f"#### 🎨 Creative Concept: {ai_plan.get('theme_concept', 'Bespoke Theme')}")
                if ai_plan.get("theme_description"):
                    st.markdown(
                        f"""
                        <div class="content-box" style="margin-bottom: 1rem;">
                            <p style="font-size: 1.05rem; line-height: 1.6; color: #F4EEE7; margin: 0;">
                                {ai_plan.get('theme_description', '')}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if ai_plan.get("color_palette"):
                    st.markdown("**Curated Colour Palette:**")
                    palette_html = "".join([f'<span class="palette-chip">{c}</span>' for c in ai_plan.get("color_palette", [])])
                    st.markdown(f'<div class="palette-container" style="margin-bottom: 1rem;">{palette_html}</div>', unsafe_allow_html=True)

                col_dec, col_cul = st.columns(2)
                with col_dec:
                    st.markdown("#### 🌿 Decor & Styling Ideas")
                    for dec in ai_plan.get("decor_highlights", []):
                        st.markdown(f"- {dec}")

                    st.markdown("#### 🎵 Activities & Entertainment")
                    for ent in ai_plan.get("entertainment_ideas", []):
                        st.markdown(f"- {ent}")

                with col_cul:
                    st.markdown("#### 🍸 Culinary & Beverage Concepts")
                    for cul in ai_plan.get("menu_suggestions", []):
                        st.markdown(f"- {cul}")

                    st.markdown("#### 💡 Expert Planner Pro-Tips")
                    for tip in ai_plan.get("planner_pro_tips", []):
                        st.markdown(f"- {tip}")

            st.markdown("---")
            # Action controls
            col_act1, col_act2, col_act3 = st.columns([2, 2, 1])

            with col_act1:
                new_status = st.selectbox(
                    "Update Status",
                    ["Planning", "Confirmed", "Completed"],
                    index=["Planning", "Confirmed", "Completed"].index(ev["status"])
                    if ev["status"] in ["Planning", "Confirmed", "Completed"]
                    else 0,
                    key=f"status_select_{ev['id']}",
                )
                if new_status != ev["status"]:
                    if st.button("Apply Status Change", key=f"btn_apply_{ev['id']}"):
                        update_event_status(ev["id"], new_status)
                        st.success(f"Updated status to {new_status}")
                        st.rerun()

            with col_act3:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete Event", key=f"del_ev_{ev['id']}"):
                    delete_event(ev["id"])
                    st.warning(f"Deleted event '{ev['name']}'")
                    st.rerun()


def page_budget_planner() -> None:
    """Deterministic budget breakdown view, tracking actual spend and variance."""
    st.markdown(
        """
        <div class="page-header">
            <h1 class="page-header-title">Budget Planner</h1>
            <p class="page-header-subtitle">Guaranteed penny-precision allocation computed deterministically in Python.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    events = list_events()
    if not events:
        st.info("No events found. Please create an event first.")
        return

    # Select event
    event_options = {f"{e['name']} ({e['date']})": e["id"] for e in events}
    selected_label = st.selectbox("Select Celebration", list(event_options.keys()))
    selected_id = event_options[selected_label]

    current_event = get_event(selected_id)
    if not current_event:
        st.error("Selected event could not be found.")
        return

    curr = current_event.get("currency", "USD")
    curr_sym = get_currency_symbol(curr)
    budget_items = get_budget_items(selected_id)

    total_allocated = sum(b["allocated_amount"] for b in budget_items)
    total_actual = sum(b["actual_amount"] for b in budget_items)
    variance = total_allocated - total_actual

    # Summary KPI cards (uniform height and luxury styling)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Total Budget</div>
                    <div class="metric-value" style="font-size: 1.55rem;">{format_currency(current_event['budget'], curr)}</div>
                </div>
                <div class="metric-sub">Event cap</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Allocated Target</div>
                    <div class="metric-value" style="font-size: 1.55rem;">{format_currency(total_allocated, curr)}</div>
                </div>
                <div class="metric-sub">100% categorized</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Committed / Actual</div>
                    <div class="metric-value" style="font-size: 1.55rem;">{format_currency(total_actual, curr)}</div>
                </div>
                <div class="metric-sub">Invoiced spend</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        var_color = "#6CB8A8" if variance >= 0 else "#E07A5F"
        var_label = "Under budget" if variance >= 0 else "Over budget"
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Remaining Variance</div>
                    <div class="metric-value" style="font-size: 1.55rem; color: {var_color};">{format_currency(variance, curr)}</div>
                </div>
                <div class="metric-sub" style="color: {var_color};">{var_label} ({variance:+,.2f})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Visual Chart & Table
    col_chart, col_tbl = st.columns([1, 1])

    with col_chart:
        st.markdown("### Budget Allocations")
        if budget_items:
            df_chart = pd.DataFrame(
                [
                    {
                        "Category": b["category"],
                        "Allocated": b["allocated_amount"],
                        "Actual": b["actual_amount"],
                    }
                    for b in budget_items
                ]
            )

            chart = (
                alt.Chart(df_chart)
                .mark_bar(cornerRadius=5)
                .encode(
                    x=alt.X(
                        "Allocated:Q",
                        title=f"Amount ({curr_sym})",
                        axis=alt.Axis(
                            labelColor="#F5F0EA",
                            titleColor="#C5A059",
                            gridColor="#241C2D",
                        ),
                    ),
                    y=alt.Y(
                        "Category:N",
                        sort="-x",
                        title=None,
                        axis=alt.Axis(labelColor="#F5F0EA"),
                    ),
                    color=alt.Color(
                        "Category:N",
                        scale=alt.Scale(
                            range=[
                                "#2E6F68",
                                "#C5A059",
                                "#9B5DE5",
                                "#E07A5F",
                                "#81B29A",
                                "#A67C94",
                            ]
                        ),
                        legend=None,
                    ),
                    tooltip=["Category", "Allocated", "Actual"],
                )
                .properties(height=300)
                .configure_view(strokeWidth=0)
                .configure(background="transparent")
            )
            st.altair_chart(chart, width="stretch")

    with col_tbl:
        st.markdown("### Category Summary")
        df_summary = pd.DataFrame(
            [
                {
                    "Category": b["category"],
                    "Share (%)": f"{b['percentage']:.1f}%",
                    "Target": format_currency(b["allocated_amount"], curr),
                    "Actual": format_currency(b["actual_amount"], curr),
                }
                for b in budget_items
            ]
        )
        st.dataframe(df_summary, hide_index=True, width="stretch")

    # Interactive Expense Updater
    st.markdown("---")
    st.markdown("### Update Actual Spending & Invoices")

    for item in budget_items:
        with st.expander(
            f"{item['category']} — Target: {format_currency(item['allocated_amount'], curr)} | Spent: {format_currency(item['actual_amount'], curr)}"
        ):
            c_input1, c_input2, c_btn = st.columns([2, 3, 1])
            with c_input1:
                new_actual = st.number_input(
                    f"Actual Spent ({curr_sym})",
                    value=float(item["actual_amount"]),
                    step=10.0,
                    key=f"act_spend_{item['id']}",
                )
            with c_input2:
                new_notes = st.text_input(
                    "Expense Notes / Vendor",
                    value=item.get("notes") or "",
                    key=f"notes_spend_{item['id']}",
                )
            with c_btn:
                st.write("")
                st.write("")
                if st.button("Save", key=f"save_b_{item['id']}"):
                    update_budget_actual(item["id"], new_actual, notes=new_notes)
                    st.success("Updated!")
                    st.rerun()


def page_timeline() -> None:
    """Timeline page showcasing milestones and day-of itinerary."""
    st.markdown(
        """
        <div class="page-header">
            <h1 class="page-header-title">Event Timeline & Itinerary</h1>
            <p class="page-header-subtitle">From early concept milestones to minute-by-minute day-of execution.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    events = list_events()
    if not events:
        st.info("No events found. Please create an event first.")
        return

    event_options = {f"{e['name']} ({e['date']})": e["id"] for e in events}
    selected_label = st.selectbox("Select Celebration", list(event_options.keys()))
    selected_id = event_options[selected_label]

    timeline_items = get_timeline_items(selected_id)
    if not timeline_items:
        st.warning("No timeline items recorded for this celebration.")
        return

    # Completion progress
    completed_count = sum(1 for t in timeline_items if t["is_completed"])
    total_count = len(timeline_items)
    progress_val = (completed_count / total_count) if total_count > 0 else 0.0

    st.markdown(f"**Master Progress:** {completed_count} of {total_count} tasks completed")
    st.progress(progress_val)

    st.write("")

    tab_milestones, tab_dayof = st.tabs(["📅 Master Milestones", "⏰ Day-Of Run-of-Show"])

    with tab_milestones:
        milestones = [t for t in timeline_items if t.get("category") == "Milestone"]
        for m in milestones:
            col_check, col_info = st.columns([1, 11])
            with col_check:
                is_done = st.checkbox(
                    "Done",
                    value=bool(m["is_completed"]),
                    key=f"chk_m_{m['id']}",
                    label_visibility="collapsed",
                )
                if is_done != bool(m["is_completed"]):
                    toggle_timeline_completed(m["id"], is_done)
                    st.rerun()

            with col_info:
                card_class = "timeline-card-completed" if m["is_completed"] else "timeline-card"
                tag_class = "timeline-tag-completed" if m["is_completed"] else "timeline-tag"
                title_class = "timeline-title-completed" if m["is_completed"] else "timeline-title"
                st.markdown(
                    f"""
                    <div class="{card_class}">
                        <span class="{tag_class}">{m['timeframe']}</span>
                        <h4 class="{title_class}">{m['title']}</h4>
                        <p class="timeline-desc">{m['description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_dayof:
        day_of_items = [t for t in timeline_items if t.get("category") == "Day-Of"]
        for d in day_of_items:
            col_check, col_info = st.columns([1, 11])
            with col_check:
                is_done = st.checkbox(
                    "Done",
                    value=bool(d["is_completed"]),
                    key=f"chk_d_{d['id']}",
                    label_visibility="collapsed",
                )
                if is_done != bool(d["is_completed"]):
                    toggle_timeline_completed(d["id"], is_done)
                    st.rerun()

            with col_info:
                card_class = "timeline-card-completed" if d["is_completed"] else "timeline-card"
                tag_class = "timeline-tag-completed" if d["is_completed"] else "timeline-tag"
                title_class = "timeline-title-completed" if d["is_completed"] else "timeline-title"
                st.markdown(
                    f"""
                    <div class="{card_class}">
                        <span class="{tag_class}">{d['timeframe']}</span>
                        <h4 class="{title_class}">{d['title']}</h4>
                        <p class="timeline-desc">{d['description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def page_vendor_checklist() -> None:
    """Vendor checklist with status management and cost tracking."""
    st.markdown(
        """
        <div class="page-header">
            <h1 class="page-header-title">Vendor Checklist & Roster</h1>
            <p class="page-header-subtitle">Coordinate vendor inquiries, contracts, deposits, and confirmed partners.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    events = list_events()
    if not events:
        st.info("No events found. Please create an event first.")
        return

    event_options = {f"{e['name']} ({e['date']})": e["id"] for e in events}
    selected_label = st.selectbox("Select Celebration", list(event_options.keys()))
    selected_id = event_options[selected_label]

    current_event = get_event(selected_id)
    curr = current_event.get("currency", "USD") if current_event else "USD"
    curr_sym = get_currency_symbol(curr)

    vendor_items = get_vendor_items(selected_id)
    if not vendor_items:
        st.warning("No vendors registered for this celebration.")
        return

    # Status counts
    statuses = [v["status"] for v in vendor_items]
    booked_count = sum(1 for s in statuses if s in ["Booked", "Paid"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Total Vendors Needed</div>
                    <div class="metric-value">{len(vendor_items)}</div>
                </div>
                <div class="metric-sub">Key service roles</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Secured & Confirmed</div>
                    <div class="metric-value" style="color: #6CB8A8;">{booked_count}</div>
                </div>
                <div class="metric-sub">Contracts signed / paid</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        pending_count = len(vendor_items) - booked_count
        pending_color = "#F0B36C" if pending_count > 0 else "#6CB8A8"
        st.markdown(
            f"""
            <div class="metric-card">
                <div>
                    <div class="metric-label">Pending Inquiries</div>
                    <div class="metric-value" style="color: {pending_color};">{pending_count}</div>
                </div>
                <div class="metric-sub">In review or needed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("### Vendor Roster")

    for v in vendor_items:
        est_fmt = format_currency(v["estimated_cost"], curr)
        act_fmt = format_currency(v["actual_cost"], curr)
        with st.expander(
            f"{'🟢' if v['status'] in ['Booked', 'Paid'] else '🟡'} {v['name'] or v['category']} — Status: {v['status']} (Est: {est_fmt} | Act: {act_fmt})"
        ):
            c_name, c_status, c_cost, c_save = st.columns([3, 2, 2, 1])

            with c_name:
                v_name = st.text_input(
                    "Vendor / Business Name",
                    value=v["name"],
                    key=f"v_name_{v['id']}",
                )
            with c_status:
                v_status = st.selectbox(
                    "Status",
                    ["Needed", "Researching", "Contacted", "Booked", "Paid"],
                    index=["Needed", "Researching", "Contacted", "Booked", "Paid"].index(v["status"])
                    if v["status"] in ["Needed", "Researching", "Contacted", "Booked", "Paid"]
                    else 0,
                    key=f"v_stat_{v['id']}",
                )
            with c_cost:
                v_cost = st.number_input(
                    f"Contract Cost ({curr_sym})",
                    value=float(v["actual_cost"]),
                    step=10.0,
                    key=f"v_cost_{v['id']}",
                )
            with c_save:
                st.write("")
                st.write("")
                if st.button("Save", key=f"v_save_btn_{v['id']}"):
                    update_vendor_item(
                        v["id"],
                        name=v_name,
                        status=v_status,
                        actual_cost=v_cost,
                        notes=v.get("notes") or "",
                    )
                    st.success("Vendor record saved!")
                    st.rerun()


# Main App Controller
def main() -> None:
    """Main routing controller for CelebrAI Streamlit application."""
    selected_page = render_sidebar()

    if selected_page == "Dashboard":
        page_dashboard()
    elif selected_page == "Create Event":
        page_create_event()
    elif selected_page == "My Events":
        page_my_events()
    elif selected_page == "Budget Planner":
        page_budget_planner()
    elif selected_page == "Timeline":
        page_timeline()
    elif selected_page == "Vendor Checklist":
        page_vendor_checklist()


if __name__ == "__main__":
    main()
