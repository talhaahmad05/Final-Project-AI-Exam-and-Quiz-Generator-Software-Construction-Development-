# LEHMAN_LAWS.md — Lehman's Laws of Software Evolution
## Project: AI-Powered Quiz & Exam Platform
## Author: Talha Ahmad | FA-24 BSSE 009 | Section A

---

## Law 1: Continuing Change

> *"A system that is used in a real-world environment must be continually adapted, or it becomes progressively less satisfactory."*

### Application in QuizAI Platform
The platform was initially built with basic MCQ support only (Sprint 2). As requirements evolved:
- **True/False** and **Short Answer** question types were added to `Questions` table and `question_bank_ui.py`.
- AI features were integrated in Sprint 4 to meet the need for automated question generation and intelligent grading.
- The database schema was extended with `HintLogs` table to support the hint tracking feature.

If we stop updating the platform, students' needs (e.g., new question formats, adaptive learning) will make it obsolete.

**Code Reference:** `database/db_setup.py` — Schema has evolved from 3 tables (Sprint 1) to 7 tables (Sprint 4).

---

## Law 2: Increasing Complexity

> *"As a system evolves, its complexity increases unless work is done to maintain or reduce it."*

### Application in QuizAI Platform
As AI features were added in Sprint 4, complexity grew rapidly:
- Multiple AI models for different features (question gen, grading, hints, topics, chatbot)
- JSON parsing from LLM responses with edge cases (markdown-wrapped responses)
- Background threading for non-blocking AI calls

**Complexity was managed by:**
- Extracting `AIEngine` class as a single interface to Ollama (SPI Improvement 1)
- Creating the DAO layer to separate data access from UI logic (SPI Improvement 5)
- Using `FormValidator` to centralize all validation logic

**Code Reference:** `ai_engine.py` — Single class managing 6 different AI features that would otherwise be scattered across UI files.

---

## Law 3: Self-Regulation

> *"The evolution process is self-regulating with distribution of product and process measures close to normal."*

### Application in QuizAI Platform
The development followed Agile Scrum with 5 sprints, each with defined scope:
- Sprint velocity was naturally regulated — Sprint 4 (AI integration) required more time per feature than Sprint 1 (basic CRUD).
- Bug discovery rate followed a pattern: more bugs found during Sprint 3 (exam engine) led to refactoring in Sprint 5.
- The team (individual developer) self-regulated by deferring AI features to Sprint 4 after Sprint 3 testing revealed the need for better error handling first.

**Code Reference:** `docs/SCRUM_LOG.md` — Sprint deliverables show consistent scope per sprint with natural variation.

---

## Law 4: Conservation of Organizational Stability

> *"The average effective global activity rate in an evolving system is invariant over the product's lifetime."*

### Application in QuizAI Platform
Despite varying feature complexity, each sprint maintained approximately equal development effort:
- Sprint 1 (Auth): 4 files, foundational infrastructure
- Sprint 2 (Question Bank): 6 files, CRUD-heavy development
- Sprint 3 (Exam Engine): 5 files, complex logic (timer, grading)
- Sprint 4 (AI Integration): 4 files, API integration and threading
- Sprint 5 (Testing): 7 files, tests and documentation

The work distribution remained stable even as technical complexity varied.

**Code Reference:** `docs/GIT_LOG.md` — ~8 commits per sprint shows consistent activity rate.

---

## Law 5: Conservation of Familiarity

> *"As a system evolves, all associated with it must maintain mastery of its content and behavior to achieve satisfactory evolution."*

### Application in QuizAI Platform
Each sprint built upon familiar patterns established in earlier sprints:
- All DAO classes follow the same connection pattern (`get_connection()`, try/except, logger)
- All UI screens share the same styling constants (`NAVY_BLUE`, `ACCENT_BLUE`, `WHITE`)
- All AI features use the same `_call_ai()` method in `AIEngine`
- New developers can understand any DAO by reading one DAO class

When the AI grading feature was added, the developer was already familiar with the DAO pattern, making integration smoother.

**Code Reference:** `dao/student_dao.py`, `dao/exam_dao.py`, `dao/question_dao.py`, `dao/result_dao.py` — All follow identical structural patterns.

---

## Law 6: Continuing Growth

> *"The functional content of a system must be continually increased to maintain user satisfaction over its lifetime."*

### Application in QuizAI Platform
The platform's feature set grew across every sprint:
- Sprint 1: Basic login → Sprint 2: Question CRUD → Sprint 3: Exam engine → Sprint 4: AI features
- Each sprint added functional content that addressed real user needs:
  - Teachers needed **AI question generation** to save time → Added in Sprint 4
  - Students needed **personalized feedback** → AI feedback feature added
  - Students needed **study help** → AI chatbot added
  - Teachers needed **analytics** → Reports module with CSV export added

Future growth areas include: adaptive difficulty, multi-language support, plagiarism detection.

**Code Reference:** `ui/ai_question_gen_ui.py`, `ui/chatbot_ui.py` — Features added in Sprint 4 that significantly increased user satisfaction.
