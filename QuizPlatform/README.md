# 🧠 AI-Powered Quiz & Exam Platform

> **QuizAI Platform — Talha Ahmad**  
> A comprehensive desktop application for creating, managing, and taking AI-powered quizzes and exams.

---

## 📋 Project Information

| Field            | Details                                    |
|------------------|--------------------------------------------|
| **Student**      | Talha Ahmad                                |
| **Roll Number**  | FA-24 BSSE 009                             |
| **Section**      | A                                          |
| **University**   | Lahore Garrison University                 |
| **Subject**      | Software Construction & Development        |
| **Instructor**   | Sir Ali Haider Naqvi                       |
| **Technology**   | Python + PyQt5 + SQL Server + Ollama LLM   |

---

## ✨ Features

### 🔐 Authentication
- Role-based login (Admin/Teacher & Student)
- SHA-256 password hashing
- Change password functionality

### 📚 Question Bank (Teacher)
- Add/Edit/Delete questions (MCQ, True/False, Short Answer)
- Search & filter by subject, difficulty, topic
- Sortable table with action buttons

### 📝 Exam Builder (Teacher)
- Create exams with title, subject, time limit, marks
- Manual or random question selection
- Assign to specific students or all students
- Shuffle questions toggle

### 🎓 Exam Taking (Student)
- Live countdown timer with auto-submit
- One question per screen with navigation panel
- Flag questions for review
- Confirm dialog before submission

### 📊 Results & Grading
- Instant auto-grading for MCQ and True/False
- AI-powered grading for Short Answer questions
- Score card with pass/fail and percentage
- Color-coded answer review table

### 📈 Reports (Teacher)
- Class average, pass/fail counts
- Leaderboard per exam (top 5)
- CSV export for all reports

### 🤖 AI Features (Ollama LLM)
1. **AI Question Generator** — Generate MCQs from any topic
2. **AI Result Feedback** — Personalized improvement suggestions
3. **Hint System** — AI clues during exams (without revealing answers)
4. **Short Answer Grader** — LLM-based scoring
5. **Weak Topic Detector** — Identifies student focus areas
6. **AI Study Chatbot** — Interactive tutor for any subject

---

## 🚀 Setup Instructions

### Prerequisites
1. **Python 3.9+** — [Download](https://www.python.org/downloads/)
2. **Microsoft SQL Server Express** — [Download](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
   - Instance: `TalhaMughal\SQLEXPRESS`
   - Windows Authentication enabled
3. **ODBC Driver for SQL Server** — [Download](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
4. **Ollama** — [Download](https://ollama.ai/download)

### Step 1: Install Ollama Models
```bash
ollama pull mistral:7b-instruct
ollama pull llama3.1:8b
```

### Step 2: Install Python Dependencies
```bash
cd QuizPlatform
pip install -r requirements.txt
```

### Step 3: Configure Database (Optional)
Edit `config.ini` if your SQL Server instance is different:
```ini
[Database]
Server = TalhaMughal\SQLEXPRESS
Database = QuizAIPlatform
Trusted_Connection = yes
```

### Step 4: Run the Application
```bash
python main.py
```

On first run, the app automatically:
- Creates the `QuizAIPlatform` database
- Creates all required tables
- Inserts seed data (users, questions, sample exam)

### Step 5: Login
| Username  | Password    | Role    |
|-----------|-------------|---------|
| admin     | admin123    | Admin   |
| student1  | student123  | Student |
| student2  | student123  | Student |
| student3  | student123  | Student |

---

## 🧪 Running Tests
```bash
cd QuizPlatform
python run_tests.py
```

Output includes: Tests Run | Passed | Failed | Coverage

---

## 📁 Folder Structure
```
QuizPlatform/
├── main.py                    # Entry point
├── config.py                  # Constants and settings
├── config.ini                 # DB and AI configuration
├── requirements.txt           # Dependencies
├── exceptions.py              # Custom exception classes
├── ai_engine.py               # All Ollama LLM calls
├── database/
│   └── db_setup.py            # Schema & seed data
├── dao/
│   ├── student_dao.py         # User/auth operations
│   ├── exam_dao.py            # Exam CRUD
│   ├── question_dao.py        # Question CRUD
│   └── result_dao.py          # Results & stats
├── ui/
│   ├── login_ui.py            # Login screen
│   ├── teacher_dashboard.py   # Admin dashboard
│   ├── student_dashboard.py   # Student dashboard
│   ├── question_bank_ui.py    # Question management
│   ├── exam_builder_ui.py     # Exam creation
│   ├── exam_taking_ui.py      # Live exam screen
│   ├── result_ui.py           # Results & review
│   ├── reports_ui.py          # Analytics & export
│   ├── ai_question_gen_ui.py  # AI question generator
│   └── chatbot_ui.py          # AI study chatbot
├── utils/
│   ├── form_validator.py      # Input validation
│   └── logger.py              # Error logging
├── tests/
│   ├── test_auth.py           # Auth tests
│   ├── test_question.py       # Question tests
│   ├── test_exam.py           # Exam tests
│   ├── test_grading.py        # Grading tests
│   └── test_ai_engine.py      # AI engine tests (mocked)
├── run_tests.py               # Test runner
├── quiz_errors.log            # Error log file
├── docs/
│   ├── SCRUM_LOG.md           # Agile sprint log
│   ├── SPI_NOTES.md           # Process improvements
│   ├── GIT_LOG.md             # Version control history
│   ├── LEHMAN_LAWS.md         # Software evolution laws
│   ├── PEER_REVIEW_LOG.md     # Peer review entries
│   ├── CI_PIPELINE.md         # CI/CD configuration
│   └── DEPLOYMENT.md          # Deployment guide
└── README.md                  # This file
```

---

## 🛠️ Technology Stack

| Component   | Technology                     |
|-------------|--------------------------------|
| Language    | Python 3.11                    |
| UI          | PyQt5                          |
| Database    | Microsoft SQL Server Express   |
| AI Backend  | Ollama (local LLM)             |
| AI Models   | mistral:7b-instruct, llama3.1:8b |
| Testing     | unittest + unittest.mock       |
| Logging     | Python logging module          |

---

## 📄 License
This project is developed as a university assignment for the Software Construction & Development course at Lahore Garrison University.

---

**Developed by Talha Ahmad | FA-24 BSSE 009 | Section A**  
**Lahore Garrison University**
