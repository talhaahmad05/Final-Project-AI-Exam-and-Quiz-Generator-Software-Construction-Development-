# PEER_REVIEW_LOG.md — Peer Review Entries
## Project: AI-Powered Quiz & Exam Platform
## Author: Talha Ahmad | FA-24 BSSE 009 | Section A

---

## Review 1: Authentication Module

| Field          | Details                                                   |
|----------------|-----------------------------------------------------------|
| **Reviewer**   | Peer Reviewer A (Ali Hassan, FA-24 BSSE 012)              |
| **Date**       | 2026-04-12                                                |
| **Module**     | `login_ui.py`, `student_dao.py`, `exceptions.py`          |
| **Sprint**     | Sprint 1                                                  |

### Findings
1. ✅ **Positive:** SHA-256 hashing is implemented correctly. No plaintext passwords stored.
2. ✅ **Positive:** Custom `QuizAuthError` is raised on invalid login — proper exception handling.
3. ⚠️ **Suggestion:** Add password complexity requirements (minimum 1 uppercase, 1 number).
4. ⚠️ **Suggestion:** Consider adding login attempt rate limiting to prevent brute force.

### Action Taken
- Added minimum 5-character password validation in `FormValidator.validate_login()`.
- Rate limiting deferred to future sprint (not critical for local desktop app).

---

## Review 2: Database Layer & DAO Classes

| Field          | Details                                                   |
|----------------|-----------------------------------------------------------|
| **Reviewer**   | Peer Reviewer B (Sara Malik, FA-24 BSSE 015)              |
| **Date**       | 2026-04-24                                                |
| **Module**     | `db_setup.py`, `question_dao.py`, `exam_dao.py`           |
| **Sprint**     | Sprint 2                                                  |

### Findings
1. ✅ **Positive:** All SQL queries use parameterized queries (`?` placeholders) — no SQL injection risk.
2. ✅ **Positive:** Consistent error handling pattern across all DAO classes.
3. ⚠️ **Suggestion:** Use context managers (`with`) for all database connections to prevent connection leaks.
4. ⚠️ **Suggestion:** Add index on `Questions.subject` and `Questions.difficulty` for faster filtering.

### Action Taken
- Implemented `with self.get_connection() as conn:` pattern in all DAO methods.
- Database indexes deferred to optimization sprint (not critical at current scale).

---

## Review 3: AI Engine & Prompt Templates

| Field          | Details                                                   |
|----------------|-----------------------------------------------------------|
| **Reviewer**   | Peer Reviewer C (Zain Ahmad, FA-24 BSSE 018)              |
| **Date**       | 2026-05-09                                                |
| **Module**     | `ai_engine.py`, `ai_question_gen_ui.py`, `chatbot_ui.py`  |
| **Sprint**     | Sprint 4                                                  |

### Findings
1. ✅ **Positive:** All AI calls go through single `AIEngine` class — excellent separation of concerns.
2. ✅ **Positive:** Graceful handling of Ollama connection errors with user-friendly dialog.
3. ⚠️ **Suggestion:** Add timeout parameter to `requests.post()` to prevent infinite hangs.
4. ⚠️ **Issue:** AI chatbot history grows unbounded — could cause memory issues in long sessions.

### Action Taken
- Added `timeout=30` parameter to all `requests.post()` calls in `_call_ai()`.
- Limited chatbot history to last 5 messages in `chat_response()` method.

---

## Review 4: Testing & Code Quality

| Field          | Details                                                   |
|----------------|-----------------------------------------------------------|
| **Reviewer**   | Peer Reviewer D (Fatima Noor, FA-24 BSSE 021)             |
| **Date**       | 2026-05-12                                                |
| **Module**     | `tests/`, `run_tests.py`, overall codebase                |
| **Sprint**     | Sprint 5                                                  |

### Findings
1. ✅ **Positive:** 29 unit tests covering auth, questions, exams, grading, and AI — all passing.
2. ✅ **Positive:** AI tests use `unittest.mock` properly — no actual Ollama calls needed.
3. ⚠️ **Suggestion:** Add integration tests that test DAO methods against a test database.
4. ⚠️ **Suggestion:** Add docstrings to all test methods explaining what they verify.

### Action Taken
- Added descriptive docstrings to all test methods.
- Integration tests deferred — unit tests provide sufficient coverage for current scope.
