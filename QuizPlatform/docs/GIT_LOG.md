# GIT_LOG.md — Simulated Git Version Control History
## Project: AI-Powered Quiz & Exam Platform
## Author: Talha Ahmad | FA-24 BSSE 009 | Section A

---

## Branch Structure

```
main
├── develop
│   ├── feature/auth
│   ├── feature/question-bank
│   ├── feature/exam-engine
│   ├── feature/ai-integration
│   └── feature/testing
```

---

## Commit History (Chronological)

### Sprint 1 — Authentication & DB Setup

| #  | Branch           | Commit Message                                           | Date       |
|----|------------------|----------------------------------------------------------|------------|
| 01 | `main`           | [Init] Create: Project skeleton and folder structure     | 2026-04-01 |
| 02 | `develop`        | [Config] Add: config.ini and config.py with DB settings  | 2026-04-02 |
| 03 | `feature/auth`   | [DB] Create: db_setup.py with SQL Server schema          | 2026-04-03 |
| 04 | `feature/auth`   | [DB] Add: Seed data (1 admin, 3 students, 10 questions)  | 2026-04-04 |
| 05 | `feature/auth`   | [Auth] Implement: SHA-256 password hashing               | 2026-04-05 |
| 06 | `feature/auth`   | [Auth] Add: Login screen UI with validation              | 2026-04-07 |
| 07 | `feature/auth`   | [Auth] Add: Change password dialog                       | 2026-04-08 |
| 08 | `feature/auth`   | [Error] Create: exceptions.py with custom error classes  | 2026-04-09 |
| 09 | `feature/auth`   | [Utils] Add: logger.py for file-based error logging      | 2026-04-10 |
| 10 | `develop`        | [Merge] Merge: feature/auth into develop                 | 2026-04-11 |

### Sprint 2 — Question Bank & Exam Builder

| #  | Branch                  | Commit Message                                           | Date       |
|----|-------------------------|----------------------------------------------------------|------------|
| 11 | `feature/question-bank` | [DAO] Create: QuestionDAO with CRUD operations           | 2026-04-14 |
| 12 | `feature/question-bank` | [UI] Add: Question Bank screen with table and filters    | 2026-04-15 |
| 13 | `feature/question-bank` | [UI] Add: Add/Edit question dialog with type switching   | 2026-04-16 |
| 14 | `feature/question-bank` | [DAO] Create: ExamDAO with exam creation and assignment   | 2026-04-18 |
| 15 | `feature/question-bank` | [UI] Add: Exam Builder with tabbed dialog                | 2026-04-20 |
| 16 | `feature/question-bank` | [Utils] Create: FormValidator class for input validation | 2026-04-21 |
| 17 | `feature/question-bank` | [UI] Add: Reports screen with stats and CSV export       | 2026-04-22 |
| 18 | `develop`               | [Merge] Merge: feature/question-bank into develop        | 2026-04-23 |

### Sprint 3 — Exam Engine & Grading

| #  | Branch               | Commit Message                                           | Date       |
|----|----------------------|----------------------------------------------------------|------------|
| 19 | `feature/exam-engine`| [DAO] Create: StudentDAO and ResultDAO                   | 2026-04-25 |
| 20 | `feature/exam-engine`| [UI] Add: Student Dashboard with exam list               | 2026-04-26 |
| 21 | `feature/exam-engine`| [UI] Implement: Exam Taking screen with timer            | 2026-04-28 |
| 22 | `feature/exam-engine`| [Logic] Add: MCQ/TF auto-grading with case insensitivity| 2026-04-29 |
| 23 | `feature/exam-engine`| [UI] Add: Result screen with score card and review table | 2026-04-30 |
| 24 | `feature/exam-engine`| [UI] Add: Question flag and navigation panel             | 2026-05-01 |
| 25 | `develop`            | [Merge] Merge: feature/exam-engine into develop          | 2026-05-02 |

### Sprint 4 — AI Integration

| #  | Branch                  | Commit Message                                           | Date       |
|----|-------------------------|----------------------------------------------------------|------------|
| 26 | `feature/ai-integration`| [AI] Create: AIEngine class with Ollama integration      | 2026-05-04 |
| 27 | `feature/ai-integration`| [AI] Add: Question generation with JSON parsing          | 2026-05-05 |
| 28 | `feature/ai-integration`| [AI] Add: Short answer grading and result feedback       | 2026-05-06 |
| 29 | `feature/ai-integration`| [AI] Add: Hint system with logging                       | 2026-05-07 |
| 30 | `feature/ai-integration`| [AI] Add: Weak topic detector and chatbot                | 2026-05-08 |
| 31 | `feature/ai-integration`| [UI] Add: AI Question Generator with background thread   | 2026-05-09 |
| 32 | `feature/ai-integration`| [UI] Add: Chatbot UI with chat bubbles                   | 2026-05-09 |
| 33 | `develop`               | [Merge] Merge: feature/ai-integration into develop       | 2026-05-10 |

### Sprint 5 — Testing & Deployment

| #  | Branch             | Commit Message                                           | Date       |
|----|--------------------|----------------------------------------------------------|------------|
| 34 | `feature/testing`  | [Test] Add: test_auth.py with 5 test cases               | 2026-05-11 |
| 35 | `feature/testing`  | [Test] Add: test_question.py with 6 test cases           | 2026-05-11 |
| 36 | `feature/testing`  | [Test] Add: test_exam.py with 7 test cases               | 2026-05-11 |
| 37 | `feature/testing`  | [Test] Add: test_grading.py with 5 test cases            | 2026-05-11 |
| 38 | `feature/testing`  | [Test] Add: test_ai_engine.py with mocked Ollama calls   | 2026-05-12 |
| 39 | `feature/testing`  | [Test] Add: run_tests.py with test discovery              | 2026-05-12 |
| 40 | `feature/testing`  | [Docs] Add: All documentation files                      | 2026-05-12 |
| 41 | `develop`          | [Merge] Merge: feature/testing into develop              | 2026-05-12 |
| 42 | `main`             | [Release] Merge: develop into main — v1.0.0              | 2026-05-12 |
| 43 | `feature/ai-perf`  | [AI] Refactor: Implement AIWorker QThread pattern        | 2026-05-13 |
| 44 | `feature/ai-perf`  | [AI] Optimize: Standardize on mistral:7b-instruct-q4_0   | 2026-05-13 |
| 45 | `feature/ai-perf`  | [AI] Optimize: Reduce context window and predict tokens  | 2026-05-13 |
| 46 | `develop`          | [Merge] Merge: feature/ai-perf into develop              | 2026-05-13 |
| 47 | `main`             | [Release] Version 1.1.0 — AI Performance Optimized       | 2026-05-13 |
