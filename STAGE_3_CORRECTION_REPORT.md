# CelebrAI — Stage 3 Correction Report: Database Deadlock and SQL Projection

**Date:** November 1, 2026  
**Target:** Remediation of Defects Identified in Stage 3 Verification Audit  
**Scope:** `services/database.py` and `tests/test_efficiency.py`  
**Test Suite Status:** 72 passed, 0 failures, 1 warning (deprecation)  

---

## 1. Executive Summary

Following the independent Stage 3 Verification Audit, two specific defects were identified:
1. **Critical Self-Deadlock in Database Initialisation**: Caused by `threading.Lock` being non-reentrant when `ensure_db_initialized()` acquired the lock and subsequently called `init_db()`, which attempted to re-acquire the same lock.
2. **Incomplete SQL Column Projection**: `list_events()` was executing `SELECT * FROM events` even when `include_plan=False`, which transferred the raw `ai_plan_json` blob off disk into Python memory on every row.

Both defects have been completely corrected and verified. The test suite now passes cleanly across **72 unit and regression tests** (including multi-threaded concurrency tests with bounded timeouts), with zero deadlocks and strictly verified column pruning.

---

## 2. Defect 1 — Database Initialisation Self-Deadlock

### A. Root Cause Analysis
- **Location**: `services/database.py:21`, `services/database.py:35`, `services/database.py:158`
- **Mechanism**:
  - `_INIT_LOCK` was instantiated as `threading.Lock()`.
  - When `ensure_db_initialized(path)` was called for an uninitialized database (or after cache reset), the calling thread entered `with _INIT_LOCK:` at line 35.
  - While holding the lock, it invoked `init_db(path)` at line 38.
  - Inside `init_db(path)`, at line 158, the same thread attempted `with _INIT_LOCK:` to register the path in `_INITIALIZED_DBS`.
  - Because `threading.Lock` is non-reentrant in Python, the calling thread deadlocked with itself permanently, freezing any process or test attempting to initialise an uninitialised database path.

### B. Exact Correction
In `services/database.py:21`, replaced `threading.Lock()` with `threading.RLock()`:

```python
# Before (Deadlock prone):
_INITIALIZED_DBS: set[str] = set()
_INIT_LOCK = threading.Lock()

# After (Reentrant, thread-safe):
_INITIALIZED_DBS: set[str] = set()
_INIT_LOCK = threading.RLock()
```

### C. Concurrency and Thread-Safety Verification
1. **Reentrant Lock Inheritance**: The exact same `_INIT_LOCK` instance is shared by `ensure_db_initialized()`, `init_db()`, and `reset_db_initialization_cache()`.
2. **Double-Checked Locking**:
   ```python
   def ensure_db_initialized(db_path: str | None = None) -> None:
       path = os.path.abspath(db_path or os.getenv("CELEBRAI_DB_PATH", DEFAULT_DB_PATH))
       if path in _INITIALIZED_DBS:
           return
       with _INIT_LOCK:
           if path in _INITIALIZED_DBS:
               return
           init_db(path)
   ```
   - Uncontended warm-path lookups remain an $O(1)$ memory check outside the lock (`if path in _INITIALIZED_DBS: return`).
   - Concurrent cold-path calls from multiple threads serialize on `_INIT_LOCK`. The second thread sees the path in `_INITIALIZED_DBS` upon acquiring the lock and returns immediately without duplicate DDL execution.
3. **Multi-Database Independence**: Each unique database path is normalized via `os.path.abspath()` and registered independently in `_INITIALIZED_DBS`.
4. **Empirical Concurrency Test**: Tested with 8 concurrent worker threads in `ThreadPoolExecutor` attempting simultaneous initialisation of a fresh database with a bounded 4.0-second timeout. All threads completed in < 0.2 seconds with zero deadlocks.

---

## 3. Defect 2 — Incomplete SQL Column Projection

### A. Root Cause Analysis
- **Location**: `services/database.py:302`
- **Mechanism**:
  - `list_events()` unconditionally executed `query = "SELECT * FROM events WHERE 1=1"`.
  - While `json.loads` was bypassed when `include_plan=False`, SQLite was still forced to read and transfer the entire `ai_plan_json` TEXT blob across the database driver interface into Python memory on every row.

### B. Exact Correction
In `services/database.py`, verified the exact schema of the `events` table (14 columns total) and created a strict 13-column metadata projection excluding `ai_plan_json` when `include_plan=False`:

```python
def list_events(
    db_path: str | None = None,
    status_filter: str | None = None,
    type_filter: str | None = None,
    include_plan: bool = True,
) -> list[dict[str, Any]]:
    """List all events with optional filters, sorted chronologically."""
    ensure_db_initialized(db_path)
    if include_plan:
        query = "SELECT * FROM events WHERE 1=1"
    else:
        query = (
            "SELECT id, name, event_type, date, location, guest_count, budget, "
            "currency, theme, preferences, status, created_at, updated_at "
            "FROM events WHERE 1=1"
        )
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
            if include_plan:
                if ev.get("ai_plan_json"):
                    try:
                        ev["ai_plan"] = json.loads(ev["ai_plan_json"])
                    except Exception:
                        ev["ai_plan"] = None
                else:
                    ev["ai_plan"] = None
            else:
                ev["ai_plan_json"] = None
                ev["ai_plan"] = None
            result.append(ev)
        return result
```

### C. SQL Projection Verification
1. **Column Exclusion**: Verified via SQLite `cursor.description` that when `include_plan=False`, exactly 13 columns are returned, and `ai_plan_json` is strictly absent from the SQLite result set.
2. **Backward Compatibility**: When `include_plan=True` (the default for existing callers), `SELECT *` is executed, and `ev["ai_plan"]` is parsed into the full dictionary structure.
3. **KeyError Prevention**: For lightweight callers, `ev["ai_plan_json"] = None` and `ev["ai_plan"] = None` are explicitly populated, guaranteeing that dictionary lookups or `.get()` calls on either key remain completely safe without KeyError risks.

---

## 4. Files Modified

| File | Nature of Changes |
|---|---|
| `services/database.py` | Replaced `_INIT_LOCK = threading.Lock()` with `_INIT_LOCK = threading.RLock()`; updated `list_events()` to implement conditional SQL projection pruning `ai_plan_json` when `include_plan=False`. |
| `tests/test_efficiency.py` | Added focused tests: uninitialised database path test, 8-thread concurrent initialisation with bounded timeouts, multi-database independent path test, SQL column pruning verification via `cursor.description`, and full/lite mode validation. |

---

## 5. Test Suite Verification

### Regression Test Run Output:
```powershell
.\.venv\Scripts\pytest -v
================== 72 passed, 1 warning in 82.72s (0:01:22) ===================
```

### Breakdown of Test Coverage:
- `tests/test_ai_service.py`: 14 passed (Pydantic schema, fallback plans, retry/timeouts, thinking tokens, never-crashes).
- `tests/test_app.py`: 1 passed (module import clean).
- `tests/test_database.py`: 7 passed (save, retrieve, update, delete, metrics, currency migration, multi-currency).
- `tests/test_efficiency.py`: 11 passed:
  1. `test_ensure_db_initialized_on_uninitialized_database` (PASSED)
  2. `test_ensure_db_initialized_idempotency_and_caching` (PASSED)
  3. `test_concurrent_initialization_no_deadlock` (8 threads, 4.0s timeout) (PASSED)
  4. `test_different_database_paths_initialize_independently` (PASSED)
  5. `test_sqlite_indexes_created` (PASSED)
  6. `test_query_plans_use_indexes` (PASSED)
  7. `test_list_events_sql_projection_and_plan_deserialization` (PASSED)
  8. `test_list_events_sql_columns_strictly_pruned` (PASSED)
  9. `test_list_event_summaries_helper` (PASSED)
  10. `test_cache_invalidation_safe_outside_streamlit` (PASSED)
  11. `test_crud_mutations_trigger_safe_invalidation_and_maintain_integrity` (PASSED)
- `tests/test_planner.py`: 16 passed (budget allocations, penny precision across all event types, timeline generation, vendor checklists, currency formatting).
- `tests/test_security.py`: 14 passed (HTML escaping, CSS sanitization, flash notification lifecycle, untrusted input handling).
- `tests/test_validation.py`: 9 passed (form inputs, date formats, guest counts, budget steps).

### Formatting and Cleanliness:
```powershell
git diff --check
```
Output: **Clean** (0 whitespace errors, 0 line-ending issues).

---

## 6. Regression Assessment

- **Accessibility**: Zero modifications made to `app.py` CSS, focus states, headings, or button labels.
- **Security & Notifications**: Zero modifications made to `services/security.py`, `escape_text()`, or flash notification logic.
- **Financial Calculations**: Zero modifications to budget calculations or penny-precision rounding in `services/planner.py`.
- **Database Schema**: Schema, table definitions, constraints, migrations, and indexes remain 100% identical.

---

## 7. Status and Next Steps

The Stage 3 corrections are **100% complete, verified, and regression-free**.
- Work has **STOPPED**.
- No Git commits or pushes were made.
- We await user review before proceeding to Stage 4.

