"""SQLite database persistence service for CelebrAI.

Provides thread-safe operations for managing events, budget allocations,
timelines, and vendor checklists.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "celebrai.db")


@contextmanager
def get_connection(db_path: str | None = None) -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional database connection."""
    path = db_path or os.getenv("CELEBRAI_DB_PATH", DEFAULT_DB_PATH)
    conn = sqlite3.connect(path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str | None = None) -> None:
    """Initialize database tables idempotently."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Events table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                guest_count INTEGER NOT NULL,
                budget REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                theme TEXT,
                preferences TEXT,
                ai_plan_json TEXT,
                status TEXT DEFAULT 'Planning',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        # Safe migration for existing events table
        cursor.execute("PRAGMA table_info(events);")
        existing_cols = [row["name"] for row in cursor.fetchall()]
        if "currency" not in existing_cols:
            cursor.execute("ALTER TABLE events ADD COLUMN currency TEXT DEFAULT 'USD';")


        # Budget items table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS budget_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                allocated_amount REAL NOT NULL,
                actual_amount REAL DEFAULT 0.0,
                percentage REAL NOT NULL,
                notes TEXT,
                FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
            );
            """
        )

        # Timeline items table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS timeline_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                timeframe TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'Milestone',
                is_completed INTEGER DEFAULT 0,
                FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
            );
            """
        )

        # Vendor items table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vendor_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                name TEXT DEFAULT '',
                status TEXT DEFAULT 'Needed',
                estimated_cost REAL DEFAULT 0.0,
                actual_cost REAL DEFAULT 0.0,
                notes TEXT,
                FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE
            );
            """
        )


def save_event(
    event_data: dict[str, Any],
    budget_items: list[dict[str, Any]] | None = None,
    timeline_items: list[dict[str, Any]] | None = None,
    vendor_items: list[dict[str, Any]] | None = None,
    db_path: str | None = None,
) -> int:
    """Insert a new event record with its associated budget, timeline, and vendors."""
    init_db(db_path)
    now = datetime.now().isoformat()

    ai_plan_json = event_data.get("ai_plan_json")
    if isinstance(ai_plan_json, dict):
        ai_plan_json = json.dumps(ai_plan_json)

    currency = str(event_data.get("currency") or "USD").strip().upper() or "USD"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (
                name, event_type, date, location, guest_count,
                budget, currency, theme, preferences, ai_plan_json, status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_data["name"].strip(),
                event_data["event_type"].strip(),
                event_data["date"].strip(),
                str(event_data.get("location") or event_data.get("venue") or event_data.get("Location") or "").strip(),
                int(event_data["guest_count"]),
                float(event_data["budget"]),
                currency,
                event_data.get("theme", "").strip(),
                event_data.get("preferences", "").strip(),
                ai_plan_json,
                event_data.get("status", "Planning"),
                now,
                now,
            ),
        )
        event_id = int(cursor.lastrowid)

        # Insert budget items
        if budget_items:
            for item in budget_items:
                cursor.execute(
                    """
                    INSERT INTO budget_items (
                        event_id, category, allocated_amount, actual_amount, percentage, notes
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id,
                        item.get("category", "General"),
                        float(item.get("allocated_amount", 0.0)),
                        float(item.get("actual_amount", 0.0)),
                        float(item.get("percentage", 0.0)),
                        item.get("notes", ""),
                    ),
                )

        # Insert timeline items
        if timeline_items:
            for item in timeline_items:
                cursor.execute(
                    """
                    INSERT INTO timeline_items (
                        event_id, timeframe, title, description, category, is_completed
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id,
                        item.get("timeframe", ""),
                        item.get("title", ""),
                        item.get("description", ""),
                        item.get("category", "Milestone"),
                        1 if item.get("is_completed") else 0,
                    ),
                )

        # Insert vendor items
        if vendor_items:
            for item in vendor_items:
                cursor.execute(
                    """
                    INSERT INTO vendor_items (
                        event_id, category, name, status, estimated_cost, actual_cost, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id,
                        item.get("category", "General"),
                        item.get("name", ""),
                        item.get("status", "Needed"),
                        float(item.get("estimated_cost", 0.0)),
                        float(item.get("actual_cost", 0.0)),
                        item.get("notes", ""),
                    ),
                )

        return event_id


def get_event(event_id: int, db_path: str | None = None) -> dict[str, Any] | None:
    """Retrieve an event by ID, including parsed AI plan if present and normalized currency."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = dict(row)
        data["currency"] = str(data.get("currency") or "USD").strip().upper() or "USD"
        if data.get("ai_plan_json"):
            try:
                data["ai_plan"] = json.loads(data["ai_plan_json"])
            except Exception:
                data["ai_plan"] = None
        else:
            data["ai_plan"] = None
        return data


def list_events(
    db_path: str | None = None,
    status_filter: str | None = None,
    type_filter: str | None = None,
) -> list[dict[str, Any]]:
    """List all events with optional filters, sorted chronologically.

    Always parses ai_plan_json into a structured ai_plan dict and normalizes currency.
    """
    init_db(db_path)
    query = "SELECT * FROM events WHERE 1=1"
    params: list[Any] = []

    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    if type_filter and type_filter != "All":
        query += " AND event_type = ?"
        params.append(type_filter)

    query += " ORDER BY date ASC, id DESC"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result: list[dict[str, Any]] = []
        for r in rows:
            ev = dict(r)
            ev["currency"] = str(ev.get("currency") or "USD").strip().upper() or "USD"
            if ev.get("ai_plan_json"):
                try:
                    ev["ai_plan"] = json.loads(ev["ai_plan_json"])
                except Exception:
                    ev["ai_plan"] = None
            else:
                ev["ai_plan"] = None
            result.append(ev)
        return result



def update_event_status(event_id: int, status: str, db_path: str | None = None) -> bool:
    """Update event status ('Planning', 'Confirmed', 'Completed')."""
    init_db(db_path)
    now = datetime.now().isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE events SET status = ?, updated_at = ? WHERE id = ?",
            (status, now, event_id),
        )
        return cursor.rowcount > 0


def delete_event(event_id: int, db_path: str | None = None) -> bool:
    """Delete an event and its cascading child records."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        return cursor.rowcount > 0


def get_budget_items(event_id: int, db_path: str | None = None) -> list[dict[str, Any]]:
    """Retrieve all budget items for an event."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM budget_items WHERE event_id = ? ORDER BY allocated_amount DESC",
            (event_id,),
        )
        return [dict(r) for r in cursor.fetchall()]


def update_budget_actual(
    item_id: int,
    actual_amount: float,
    notes: str | None = None,
    db_path: str | None = None,
) -> bool:
    """Update the actual spent amount and notes on a budget line item."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if notes is not None:
            cursor.execute(
                "UPDATE budget_items SET actual_amount = ?, notes = ? WHERE id = ?",
                (actual_amount, notes, item_id),
            )
        else:
            cursor.execute(
                "UPDATE budget_items SET actual_amount = ? WHERE id = ?",
                (actual_amount, item_id),
            )
        return cursor.rowcount > 0


def get_timeline_items(event_id: int, db_path: str | None = None) -> list[dict[str, Any]]:
    """Retrieve all timeline items for an event."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM timeline_items WHERE event_id = ? ORDER BY id ASC",
            (event_id,),
        )
        return [dict(r) for r in cursor.fetchall()]


def toggle_timeline_completed(item_id: int, is_completed: bool, db_path: str | None = None) -> bool:
    """Toggle the completion status of a timeline item."""
    init_db(db_path)
    val = 1 if is_completed else 0
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE timeline_items SET is_completed = ? WHERE id = ?",
            (val, item_id),
        )
        return cursor.rowcount > 0


def get_vendor_items(event_id: int, db_path: str | None = None) -> list[dict[str, Any]]:
    """Retrieve all vendor checklist items for an event."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM vendor_items WHERE event_id = ? ORDER BY id ASC",
            (event_id,),
        )
        return [dict(r) for r in cursor.fetchall()]


def update_vendor_item(
    item_id: int,
    name: str,
    status: str,
    actual_cost: float,
    notes: str,
    db_path: str | None = None,
) -> bool:
    """Update vendor details."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE vendor_items
            SET name = ?, status = ?, actual_cost = ?, notes = ?
            WHERE id = ?
            """,
            (name, status, actual_cost, notes, item_id),
        )
        return cursor.rowcount > 0


def get_dashboard_metrics(db_path: str | None = None) -> dict[str, Any]:
    """Calculate summary dashboard metrics."""
    init_db(db_path)
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Count total events, total budget, total guests
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_events,
                COALESCE(SUM(budget), 0.0) as total_budget,
                COALESCE(SUM(guest_count), 0) as total_guests
            FROM events
            """
        )
        basic = dict(cursor.fetchone())

        # Total actual spend across all events
        cursor.execute("SELECT COALESCE(SUM(actual_amount), 0.0) as total_actual FROM budget_items")
        basic["total_actual"] = float(cursor.fetchone()["total_actual"])

        # Group budgets by currency
        cursor.execute(
            """
            SELECT COALESCE(currency, 'USD') as currency,
                   COUNT(*) as event_count,
                   COALESCE(SUM(budget), 0.0) as total_budget
            FROM events
            GROUP BY COALESCE(currency, 'USD')
            """
        )
        basic["budget_by_currency"] = {
            r["currency"]: float(r["total_budget"]) for r in cursor.fetchall()
        }

        # Group actual spend by currency
        cursor.execute(
            """
            SELECT COALESCE(e.currency, 'USD') as currency,
                   COALESCE(SUM(b.actual_amount), 0.0) as total_actual
            FROM budget_items b
            JOIN events e ON b.event_id = e.id
            GROUP BY COALESCE(e.currency, 'USD')
            """
        )
        basic["actual_by_currency"] = {
            r["currency"]: float(r["total_actual"]) for r in cursor.fetchall()
        }

        # Next upcoming event
        cursor.execute(
            """
            SELECT * FROM events
            WHERE date >= ? AND status != 'Completed'
            ORDER BY date ASC
            LIMIT 1
            """,
            (today,),
        )
        next_event = cursor.fetchone()
        if next_event:
            ev_dict = dict(next_event)
            ev_dict["currency"] = str(ev_dict.get("currency") or "USD").strip().upper() or "USD"
            basic["next_event"] = ev_dict
        else:
            basic["next_event"] = None

        # Breakdown by status
        cursor.execute("SELECT status, COUNT(*) as count FROM events GROUP BY status")
        basic["status_counts"] = {r["status"]: r["count"] for r in cursor.fetchall()}


        # Breakdown by type
        cursor.execute("SELECT event_type, COUNT(*) as count FROM events GROUP BY event_type")
        basic["type_counts"] = {r["event_type"]: r["count"] for r in cursor.fetchall()}

        return basic
