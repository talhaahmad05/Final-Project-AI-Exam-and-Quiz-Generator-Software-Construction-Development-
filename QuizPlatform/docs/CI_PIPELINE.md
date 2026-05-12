# CI_PIPELINE.md — Continuous Integration Pipeline Configuration
## Project: AI-Powered Quiz & Exam Platform
## Author: Talha Ahmad | FA-24 BSSE 009 | Section A

---

## GitHub Actions Workflow

The following GitHub Actions configuration automates testing on every push and pull request.

### Workflow File: `.github/workflows/ci.yml`

```yaml
name: QuizAI Platform CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: windows-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r QuizPlatform/requirements.txt

      - name: Run unit tests
        run: |
          cd QuizPlatform
          python run_tests.py
        env:
          TESTING: 'true'

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: QuizPlatform/quiz_errors.log

  lint:
    runs-on: windows-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install flake8
        run: pip install flake8

      - name: Run PEP8 lint check
        run: |
          flake8 QuizPlatform/ --max-line-length=120 --exclude=__pycache__
```

---

## Pipeline Stages

### Stage 1: Checkout
- Fetches the latest code from the repository.

### Stage 2: Environment Setup
- Installs Python 3.11 on a Windows runner.
- Installs all project dependencies from `requirements.txt`.

### Stage 3: Unit Testing
- Runs `run_tests.py` which discovers and executes all tests in `tests/`.
- Prints summary: Tests Run | Passed | Failed | Coverage.
- Uploads `quiz_errors.log` as an artifact for debugging.

### Stage 4: Linting
- Runs `flake8` for PEP8 compliance checking.
- Max line length set to 120 characters.

---

## Notes

- **Database tests are skipped in CI** because SQL Server is not available in the GitHub Actions runner. Unit tests use mocking for database-dependent tests.
- **AI tests use mocked Ollama** — no actual LLM calls are made during CI.
- **Trigger events:** Pipeline runs on every push to `main` or `develop`, and on every pull request targeting those branches.
