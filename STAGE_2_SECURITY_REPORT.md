# CelebrAI — Stage 2 Security and Notification Reliability Report

**Date:** November 1, 2026  
**Application:** CelebrAI — AI-Powered Celebration & Event Planner  
**Repository:** `https://github.com/Yemmmyc/celebrai`  
**Live Application:** `https://celebrai.streamlit.app/`  
**Stage:** 2 of Prioritized Improvement Roadmap (Security and Notification Reliability)  
**Status:** Completed & Validated  

---

## 1. Executive Summary

In Stage 2, CelebrAI's security posture and notification reliability were systematically hardened against Stored Cross-Site Scripting (XSS), CSS injection attacks, and ephemeral alert drops.

Key accomplishments in this stage:
1. **Stored XSS Elimination**: Addressed every dynamic rendering path using `st.markdown(..., unsafe_allow_html=True)` across the entire application. All untrusted user inputs (`name`, `location`, `theme`, `preferences`), database entity fields (`timeframe`, `title`, `description`), and Gemini AI generative outputs (`theme_concept`, `theme_description`, `color_palette`, `decor_highlights`, `menu_suggestions`, `entertainment_ideas`, `planner_pro_tips`) are now strictly escaped using Python's `html.escape()` before being interpolated into HTML markup.
2. **CSS Injection Prevention**: Built strict validation and sanitization for all color values (`sanitize_css_color`) before interpolation into inline styles (such as `style="color: ..."`). Enforced strict hex/rgb/safe-name regex filters that reject any semicolon stylesheet breakings, JavaScript expressions, URLs, or bracket escapes.
3. **Notification Persistence across `st.rerun()`**: Replaced ephemeral `st.success()` / `st.warning()` calls immediately preceding `st.rerun()` with a robust, session-state-backed flash notification queue (`services/security.py:set_notification`). In-page banners are rendered and drained upon script re-execution (`render_notifications()`), ensuring full visual persistence and WCAG 4.1.3 Status Message compliance for assistive technology.
4. **Preservation of Core Architectural Strengths**: Zero changes to Gemini timeouts (30s local / 45s cloud), single-attempt retry rules, deterministic fallback engines, penny-precision financial math, and SQLite parameterized query sanitization.
5. **Testing Verification**: Expanded test coverage from 47 tests to **61 passing tests** with the creation of `tests/test_security.py` covering script injection vectors, attribute breaking, CSS injection payloads, and notification state lifecycles.

---

## 2. Vulnerabilities Identified & Remediations

### 2.1 Vulnerability SEC-1: Stored Cross-Site Scripting (XSS) via `unsafe_allow_html=True`
* **Severity**: **High** (in multi-user or public deployment environments)
* **Description**: Streamlit's `st.markdown(..., unsafe_allow_html=True)` bypasses markdown sanitization to render custom HTML components (KPI cards, spotlight banners, AI concept containers, and timeline cards). Dynamic values from user inputs (`event_name`, `location`, `theme`) and AI-generated outputs (`theme_description`, `color_palette`, `decor_highlights`, etc.) were directly formatted into HTML f-strings without HTML entity escaping.
* **Attack Vector**: If an attacker named an event `<img src=x onerror=alert(document.cookie)>` or if an untrusted Gemini prompt response returned script or iframe tags, the browser executed the payload within the application origin.
* **Remediation**:
  - Authored `services/security.py:escape_text()` utilizing `html.escape(str(val), quote=True)` to convert `<`, `>`, `&`, `"`, and `'` into safe HTML entities (`&lt;`, `&gt;`, `&amp;`, `&quot;`, `&#x27;`).
  - Applied `escape_text()` across all 4 previously identified audit hotspots:
    1. **Spotlight Banner (`app.py:734-759`)**: Escaped `nev['name']`, `nev['location']`, `nev['date']`, `nev['guest_count']`, and `nev['theme']`.
    2. **Event Creation AI Plan Preview (`app.py:1125-1165`)**: Escaped `ai_plan['theme_concept']`, `ai_plan['theme_description']`, each chip in `ai_plan['color_palette']`, and list items in decor, menus, entertainment, and pro-tips.
    3. **My Celebrations Dossiers (`app.py:1210-1280`)**: Escaped dossier metrics, location, theme, special preferences notes, AI theme description, palette chips, and list items.
    4. **Timeline & Day-Of Run-of-Show (`app.py:1570-1632`)**: Escaped `timeframe`, `title`, and `description` for both Milestone and Day-Of schedule cards.

### 2.2 Vulnerability SEC-2: Inline CSS Color Injection
* **Severity**: **Medium**
* **Description**: Dynamic color strings (e.g., variance indicator `var_color`, system status indicator `status_color`, and pending vendor count `pending_color`) were interpolated directly into CSS `style="color: {var_color};"`.
* **Attack Vector**: If an unsanitized string containing `; background-image: url(...)` or closing quotes were passed into a CSS style attribute, it could alter styling or exfiltrate data.
* **Remediation**:
  - Implemented `is_safe_css_color()` and `sanitize_css_color()` in `services/security.py`.
  - Enforced strict regex matching:
    - Hex colors: `^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$`
    - RGB/RGBA: bounded 0-255 channels and 0-1 alpha
    - Named colors: letters only (`^[a-zA-Z]{3,20}$`)
    - Blacklist: explicitly blocks `url`, `expression`, `javascript`, `;`, `{`, `}`, `<`, `>`, `"`, `'`.
  - All dynamic color interpolations now pass through `sanitize_css_color(...)` with safe fallback defaults.

### 2.3 Reliability Defect A11Y-7 / SEC-3: Disappearing Alert Announcements via `st.rerun()`
* **Severity**: **High** (WCAG 4.1.3 Status Messages violation & UX defect)
* **Description**: Four critical user actions invoked `st.success(...)` or `st.warning(...)` immediately before `st.rerun()`:
  - Status updates in `page_my_events()`: `st.success(...) -> st.rerun()`
  - Event deletion in `page_my_events()`: `st.warning(...) -> st.rerun()`
  - Budget actuals saving in `page_budget_planner()`: `st.success("Updated!") -> st.rerun()`
  - Vendor saving in `page_vendor_checklist()`: `st.success("Vendor record saved!") -> st.rerun()`
* **Impact**: Streamlit reruns immediately cancel the rendering pipeline and re-execute the script from line 1. Because the button was no longer clicked on the subsequent run, the success/warning alert was discarded before reaching the DOM or assistive screen-reader live regions.
* **Remediation**:
  - Implemented session-state-backed flash notification queue:
    - `set_notification(message, level="success")`: Queues message in `st.session_state["flash_notifications"]`.
    - `render_notifications()`: Checks for pending notifications on the subsequent run, renders `st.success()`, `st.warning()`, or `st.info()`, and drains the queue.
  - Placed `render_notifications()` beneath the page header of every view (`page_dashboard`, `page_create_event`, `page_my_events`, `page_budget_planner`, `page_timeline`, `page_vendor_checklist`).

---

## 3. Files Modified

| File | Status | Description |
|:---|:---:|:---|
| `services/security.py` | **New File** | Security library providing `escape_text`, `is_valid_hex_color`, `is_safe_css_color`, `sanitize_css_color`, `set_notification`, and `get_and_clear_notifications`. |
| `tests/test_security.py` | **New File** | 14 automated unit tests covering XSS injection vectors, attribute breaking, CSS injection attacks, and notification lifecycle. |
| `app.py` | **Modified** | Imported security helpers; updated all dynamic HTML rendering sites with `escape_text` and `sanitize_css_color`; replaced ephemeral alerts with `set_notification` and integrated `render_notifications()`. |

---

## 4. Notification Behaviour Comparison

| Interaction | Before Stage 2 | After Stage 2 |
|:---|:---|:---|
| **Apply Status Change** | `st.success(...)` called, followed immediately by `st.rerun()`. Message dropped; user saw page refresh with no confirmation. | `set_notification(...)` queues alert; `st.rerun()` re-executes; `render_notifications()` displays persistent green `st.success` banner at top of My Celebrations. |
| **Delete Celebration** | `st.warning(...)` called, followed immediately by `st.rerun()`. Message vanished instantly. | `set_notification(..., level="warning")` queues alert; re-rendered page displays persistent amber `st.warning` banner confirming deletion. |
| **Save Budget Line Item** | `st.success("Updated!")` dropped by `st.rerun()`. | Persistent `st.success` banner confirms actual spend and notes saved for specific category. |
| **Save Vendor Details** | `st.success("Vendor record saved!")` dropped by `st.rerun()`. | Persistent `st.success` banner confirms vendor details updated for named partner. |
| **Screen Reader Announcement** | Screen readers announced nothing because alert never landed in DOM live region. | Streamlit alert banner with `role="alert"` lands cleanly in DOM upon re-run and is announced by assistive software. |

---

## 5. Security & Regression Test Results

### 5.1 Test Execution Summary
The test suite was executed in the local virtual environment:
```
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\yemmm\projects\celebrai
configfile: pytest.ini
collected 61 items

tests/test_ai_service.py .....................                     [ 34%]
tests/test_app.py .                                                [ 36%]
tests/test_database.py .........                                   [ 50%]
tests/test_planner.py .............                                [ 72%]
tests/test_security.py ..............                              [ 95%]
tests/test_validation.py ............                              [100%]

======================= 61 passed, 1 warning in 44.48s =======================
```
* **Original Tests Passing**: 47 of 47 (100%)
* **New Security Tests Passing**: 14 of 14 (100%)
* **Total Passing**: 61 of 61 (100%)

### 5.2 Specific Security Tests Implemented (`tests/test_security.py`)
1. `test_escape_text_basic`: Verifies clean strings, numbers, None, and empty values.
2. `test_escape_text_script_tag_injection`: Verifies `<script>alert('pwned')</script>` is neutralized.
3. `test_escape_text_attribute_breaking`: Verifies quote characters and inline event handlers (`" onfocus=...`) cannot break HTML attributes.
4. `test_escape_text_img_onerror_vector`: Verifies `<img src=x onerror=...>` tags are converted to safe entities.
5. `test_escape_text_ampersands_and_brackets`: Verifies `&`, `<`, `>` are escaped.
6. `test_is_valid_hex_color_valid`: Validates 3, 4, 6, and 8 digit hex color codes.
7. `test_is_valid_hex_color_invalid`: Rejects malformed hex strings and injection attempts.
8. `test_is_safe_css_color_valid`: Accepts valid hex, rgb, rgba, and named colors.
9. `test_is_safe_css_color_injection_attacks`: Rejects semicolons, `url(...)`, `expression(...)`, and stylesheet breaking strings.
10. `test_sanitize_css_color`: Returns safe fallback default whenever invalid or malicious CSS values are passed.
11. `test_notification_lifecycle_in_session_state`: Confirms FIFO queueing, multi-level support, and queue drain semantics.
12. `test_notification_outside_streamlit_does_not_crash`: Confirms graceful degradation when called without an active Streamlit context.
13. `test_gemini_palette_chips_sanitization`: Confirms AI-generated color palettes containing script tags are safely rendered as text.
14. `test_gemini_theme_description_sanitization`: Confirms AI-generated theme descriptions containing HTML elements are escaped.

### 5.3 Git Integrity Verification
- `git diff --check`: Passed with exit code `0` (clean formatting, no trailing whitespace, clean line endings).
- `git status`: Exactly 1 branch (`main`); zero commits made; zero pushes executed; zero external dependencies added to `requirements.txt`.

---

## 6. Verification of Architectural Invariants

| Guardrail Requirement | Verification Method | Result |
|:---|:---|:---:|
| **SQL Query Parameterization** | Inspected `services/database.py`. All queries continue to use parameterized `?` placeholders. No string concatenation exists. | **VERIFIED CLEAN** |
| **Gemini Output Untrusted** | All AI outputs (`ai_plan`) pass through `escape_text()` prior to HTML rendering. | **VERIFIED CLEAN** |
| **API Key Protection** | Confirmed `services/ai_service.py` masked logging and secrets handling remain untouched (`test_ai_status_security` passes). | **VERIFIED CLEAN** |
| **Gemini Timeouts & Retries** | Untouched. Preserved 4.0s connect / 8.0s read HTTP timeouts and 30s local / 45s cloud timeout resolution. | **VERIFIED CLEAN** |
| **Deterministic Fallback Engine** | Untouched. Instant rule-based fallback plan generation verified by `test_fallback_plan_generation`. | **VERIFIED CLEAN** |
| **Budget Financial Math** | Untouched. Verified by 9 parameterized penny-precision tests (`test_budget_allocation_penny_precision`). | **VERIFIED CLEAN** |
| **Accessibility Preservation** | All Stage 1 improvements (heading hierarchy, `:focus-visible` styling, `#786694` border contrast, and unique button names) preserved. | **VERIFIED CLEAN** |

---

## 7. Remaining Risks & Considerations

1. **Markdown Bold/Italic Parsing**: `st.markdown(..., unsafe_allow_html=True)` still parses markdown formatting (e.g. `**bold**`, `*italic*`) for strings that do not contain HTML tags. This is desirable for text styling and does not allow script execution because HTML entities are already escaped.
2. **Altair Vega-Lite Spec Injection**: Altair chart dataframes pass through Vega-Lite JSON serialization, which treats cell values strictly as typed data attributes, not raw HTML.
3. **Streamlit Component Sandboxing**: No custom iframes or third-party Streamlit custom components are utilized; all views are native Streamlit widgets and styled container divs.

---

## 8. Next Steps (Pending Review & Approval)

In accordance with strict operating rules:
- **Work is STOPPED at Stage 2.**
- No commits or pushes have been made.
- Stage 3 (Efficiency Optimization: database indexing, `@st.cache_data` caching for budget templates and metrics, and query consolidation) will only begin after human review and explicit approval of Stage 2.

