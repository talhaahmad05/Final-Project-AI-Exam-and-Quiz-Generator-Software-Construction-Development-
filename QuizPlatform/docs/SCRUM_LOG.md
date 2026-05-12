# SCRUM_LOG.md — Agile Scrum Sprint Log
## Project: AI-Powered Quiz & Exam Platform
## Author: Talha Ahmad | FA-24 BSSE 009 | Section A
## Instructor: Sir Ali Haider Naqvi
## University: Lahore Garrison University

---

## Sprint 1: Authentication & Database Setup
**Duration:** Week 1–2  
**Goal:** Set up project foundation, database, and user authentication.

### Deliverables
- [x] SQL Server database schema designed and created (`db_setup.py`)
- [x] Users table with role-based access (Admin/Student)
- [x] SHA-256 password hashing implemented (`hashlib`)
- [x] Login screen UI with validation (`login_ui.py`)
- [x] Custom `QuizAuthError` exception for invalid login
- [x] Seed data: 1 admin + 3 student accounts
- [x] `config.py` and `config.ini` for centralized settings
- [x] `exceptions.py` with all custom exception classes
- [x] `logger.py` for error logging to `quiz_errors.log`

### Sprint Review Notes
- Login flow tested with all seed accounts.
- Password change dialog integrated.
- Role-based routing (Admin → Teacher Dashboard, Student → Student Dashboard) verified.

---

## Sprint 2: Question Bank & Exam Builder
**Duration:** Week 3–4  
**Goal:** Build teacher-facing modules for managing questions and creating exams.

### Deliverables
- [x] Question Bank UI with add/edit/delete (`question_bank_ui.py`)
- [x] Support for MCQ, True/False, and Short Answer types
- [x] Search & filter by subject, difficulty, topic
- [x] Sortable question table with action buttons
- [x] `QuestionDAO` with full CRUD operations
- [x] Exam Builder UI with tabbed dialog (`exam_builder_ui.py`)
- [x] Manual and random question selection for exams
- [x] Student assignment (all or selected)
- [x] `ExamDAO` for exam CRUD and question associations
- [x] Reports UI with stat cards and CSV export (`reports_ui.py`)
- [x] `FormValidator` class for all input validation

### Sprint Review Notes
- 10 sample questions seeded on first run.
- Exam creation tested with manual and random question selection.
- CSV export verified for leaderboard and performance reports.

---

## Sprint 3: Exam Taking & Auto-Grading
**Duration:** Week 5–6  
**Goal:** Build student exam-taking experience with live timer and instant grading.

### Deliverables
- [x] Student Dashboard with assigned exams list (`student_dashboard.py`)
- [x] Exam Taking Screen with one-question-per-page layout (`exam_taking_ui.py`)
- [x] Live countdown timer with auto-submit on expiry
- [x] Question navigation panel (grid of numbered buttons)
- [x] Flag questions for review
- [x] Confirmation dialog before submission
- [x] Auto-grading for MCQ and True/False (case-insensitive)
- [x] Result screen with score card, pass/fail, answer review (`result_ui.py`)
- [x] `ResultDAO` for saving results and student answers
- [x] Prevention of re-taking completed exams

### Sprint Review Notes
- Timer edge cases tested (0-second exams, mid-exam close).
- Grading accuracy verified: case-insensitive, whitespace-tolerant.
- Answer review table color-coded (green=correct, red=wrong).

---

## Sprint 4: AI Features Integration
**Duration:** Week 7–8  
**Goal:** Integrate Ollama LLM for all 6 AI features.

### Deliverables
- [x] `AIEngine` class as single interface to Ollama (`ai_engine.py`)
- [x] AI Question Generator with preview table (`ai_question_gen_ui.py`)
- [x] AI Result Feedback — personalized messages after exam
- [x] Hint System — "Get Hint" button during exams
- [x] Short Answer AI Grader — LLM-based scoring
- [x] Weak Topic Detector — "Focus Areas" card on student dashboard
- [x] AI Study Chatbot with chat bubble UI (`chatbot_ui.py`)
- [x] Background threads for all AI calls (non-blocking UI)
- [x] Graceful error handling: "AI service is offline" dialog
- [x] Hint usage logging in `HintLogs` table

### Sprint Review Notes
- AI features tested with Ollama running locally.
- JSON parsing hardened against markdown-wrapped responses.
- Fallback messages implemented when AI is unavailable.
- `QuizAIError` exception raised on malformed AI output.

---

## Sprint 5: Testing, Refactoring & Deployment
**Duration:** Week 9–10  
**Goal:** Ensure code quality, comprehensive testing, and deployment readiness.

### Deliverables
- [x] `test_auth.py` — 5 test cases for login validation and hashing
- [x] `test_question.py` — 6 test cases for question validation
- [x] `test_exam.py` — 7 test cases for exam creation validation
- [x] `test_grading.py` — 5 test cases for MCQ grading logic
- [x] `test_ai_engine.py` — 6 test cases with mocked Ollama
- [x] `run_tests.py` — automated test discovery and summary
- [x] All magic numbers replaced with named constants
- [x] DAO classes refactored for consistent error handling
- [x] Documentation: SCRUM_LOG, SPI_NOTES, GIT_LOG, LEHMAN_LAWS
- [x] `requirements.txt` and `DEPLOYMENT.md` finalized
- [x] `README.md` with full setup instructions

### Sprint Review Notes
- All 29 test cases pass.
- Code reviewed for PEP8 compliance.
- Deployment tested on fresh machine with PyInstaller.
