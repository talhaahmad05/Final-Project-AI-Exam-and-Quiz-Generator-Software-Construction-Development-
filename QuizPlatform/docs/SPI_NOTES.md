# SPI_NOTES.md — Software Process Improvement Notes
## Project: AI-Powered Quiz & Exam Platform
## Author: Talha Ahmad | FA-24 BSSE 009 | Section A

---

## Improvement 1: Extracted AIEngine Class (Sprint 4)

### Problem Identified
During Sprint 4, AI calls to Ollama were being made directly from multiple UI files (`ai_question_gen_ui.py`, `exam_taking_ui.py`, `chatbot_ui.py`). Each file had its own `requests.post()` call with duplicated error handling and prompt construction.

### Improvement Applied
Extracted all AI logic into a single `AIEngine` class in `ai_engine.py`. All AI interactions now go through this centralized class with:
- Unified error handling (connection errors, timeouts, malformed JSON)
- Prompt templates stored as formatted strings
- Model selection configurable via `config.ini`

### Impact
- Eliminated ~120 lines of duplicated code across 3 UI files
- Single point of change when AI endpoint or models change
- Consistent error messages shown to users

---

## Improvement 2: Added Comprehensive Exception Handling (Sprint 3)

### Problem Identified
During Sprint 3 testing, unhandled `pyodbc` exceptions caused raw traceback dialogs to appear when the SQL Server was unavailable or queries failed.

### Improvement Applied
Created `exceptions.py` with custom exception hierarchy:
- `QuizPlatformError` (base)
- `QuizAuthError`, `QuizValidationError`, `QuizDatabaseError`, `QuizAIError`, `QuizExamError`

All database operations wrapped in try/except blocks within DAO classes. All exceptions logged to `quiz_errors.log` with timestamps and stack traces. UI shows friendly `QMessageBox` dialogs instead of raw tracebacks.

### Impact
- Zero raw tracebacks shown to users
- All errors traceable in `quiz_errors.log`
- Developers can distinguish between auth, DB, AI, and validation errors

---

## Improvement 3: Background Threads for AI Calls (Sprint 4)

### Problem Identified
Initial AI integration in Sprint 4 made synchronous HTTP calls to Ollama. This froze the UI for 5-30 seconds while waiting for LLM responses, making the application appear unresponsive.

### Improvement Applied
Implemented `QThread` subclasses for all AI operations:
- `AIGenerateThread` for question generation
- `ChatThread` for chatbot responses
- Signal-based communication (`result_ready`, `error_occurred`) to update UI safely

Buttons show loading state ("⏳ Generating...") and are disabled during AI calls.

### Impact
- UI remains fully responsive during AI processing
- Users see visual feedback that AI is working
- No application freezes reported in user testing

---

## Improvement 4: FormValidator Class for Input Validation (Sprint 2)

### Problem Identified
During Sprint 2 development, validation logic was scattered across UI files. Each dialog had its own inline `if/else` validation, with inconsistent error messages and no reuse.

### Improvement Applied
Created `FormValidator` class in `utils/form_validator.py` with static methods:
- `validate_login()` — username/password rules
- `validate_question()` — question text, options, correct answer
- `validate_exam()` — title, subject, time, marks, pass percentage
- `validate_password_change()` — old/new/confirm password matching

All validation raises `QuizValidationError` with descriptive messages.

### Impact
- Consistent validation across all forms
- 100% unit test coverage for validation logic
- Easy to add new validation rules without modifying UI code

---

## Improvement 5: Separated DAO Layer from UI (Sprint 2–3)

### Problem Identified
Early prototypes had SQL queries embedded directly in UI event handlers, violating separation of concerns and making the code difficult to test.

### Improvement Applied
Created dedicated DAO classes following the Data Access Object pattern:
- `StudentDAO` — authentication, password changes, student queries
- `QuestionDAO` — CRUD operations for the question bank
- `ExamDAO` — exam creation, question association, student assignment
- `ResultDAO` — result saving, statistics, leaderboard, hint logging

Each DAO class manages its own database connection and handles errors consistently.

### Impact
- UI files contain zero SQL queries
- DAO methods are independently testable
- Database changes (e.g., switching from SQLite to SQL Server) require changes only in DAO layer
