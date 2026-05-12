"""
filename: ai_question_gen_ui.py
module: AI Question Generator UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 4 - AI Integration
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                              QLineEdit, QComboBox, QTextEdit, QHeaderView,
                              QFrame, QProgressDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from QuizPlatform.ai_engine import AIEngine
from QuizPlatform.dao.question_dao import QuestionDAO
from QuizPlatform.exceptions import QuizAIError, QuizDatabaseError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)


class AIGenerateThread(QThread):
    """Background thread for AI question generation"""
    result_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, topic, difficulty, n):
        super().__init__()
        self.topic = topic
        self.difficulty = difficulty
        self.n = n
        self.ai = AIEngine()

    def run(self):
        try:
            questions = self.ai.generate_questions(self.topic, self.difficulty, self.n)
            self.result_ready.emit(questions)
        except QuizAIError as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {e}")


class AIQuestionGenUI(QWidget):
    """AI Question Generator screen for teachers"""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.dao = QuestionDAO()
        self.generated_questions = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header
        title = QLabel("🤖 AI Question Generator")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        layout.addWidget(title)

        # Input card
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E0E0E0; padding: 16px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)

        ai_badge = QLabel("✨ Powered by Mistral 7B")
        ai_badge.setStyleSheet("""
            background-color: #E3F2FD; color: #1565C0; border-radius: 12px;
            padding: 4px 12px; font-size: 11px; font-weight: bold;
        """)
        ai_badge.setFixedWidth(200)
        card_layout.addWidget(ai_badge)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Topic / Subject:"))
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("e.g., Python OOP, Data Structures, Database Normalization")
        self.topic_input.setFixedHeight(36)
        self.topic_input.setStyleSheet("color: #1A1A2E; background-color: #FFFFFF; padding: 4px;")
        row1.addWidget(self.topic_input)
        card_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Difficulty:"))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["easy", "medium", "hard"])
        self.diff_combo.setFixedWidth(120)
        self.diff_combo.setStyleSheet("color: #1A1A2E; background-color: #FFFFFF;")
        row2.addWidget(self.diff_combo)
        row2.addSpacing(20)
        row2.addWidget(QLabel("Number of Questions:"))
        self.num_combo = QComboBox()
        self.num_combo.addItems(["5", "10", "15"])
        self.num_combo.setFixedWidth(80)
        self.num_combo.setStyleSheet("color: #1A1A2E; background-color: #FFFFFF;")
        row2.addWidget(self.num_combo)
        row2.addStretch()
        card_layout.addLayout(row2)

        self.btn_generate = QPushButton("⚡ Generate with AI")
        self.btn_generate.setFixedHeight(44)
        self.btn_generate.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_generate.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                          stop:0 #6200EA, stop:1 #311B92);
                          color: white; border-radius: 12px; border: none; }
            QPushButton:hover { background: #4527A0; }
            QPushButton:disabled { background: #BDBDBD; }
        """)
        self.btn_generate.clicked.connect(self.generate_questions)
        card_layout.addWidget(self.btn_generate)
        layout.addWidget(card)

        # Results table
        results_header = QHBoxLayout()
        results_lbl = QLabel("Generated Questions Preview")
        results_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        results_header.addWidget(results_lbl)
        results_header.addStretch()
        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet("color: #666;")
        results_header.addWidget(self.count_lbl)
        layout.addLayout(results_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Question", "Option A", "Option B", "Correct Answer", "Topic"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 8px;")
        layout.addWidget(self.table)

        # Save button
        btn_save = QPushButton("💾 Save All to Question Bank")
        btn_save.setFixedHeight(40)
        btn_save.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn_save.setStyleSheet("""
            QPushButton { background-color: #2E7D32; color: white; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #1B5E20; }
        """)
        btn_save.clicked.connect(self.save_to_bank)
        layout.addWidget(btn_save)

    def generate_questions(self):
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "Missing Topic", "Please enter a topic first.")
            return

        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("⏳ Generating...")
        n = int(self.num_combo.currentText())

        self.thread = AIGenerateThread(topic, self.diff_combo.currentText(), n)
        self.thread.result_ready.connect(self.on_questions_ready)
        self.thread.error_occurred.connect(self.on_error)
        self.thread.finished.connect(lambda: self.btn_generate.setEnabled(True))
        self.thread.finished.connect(lambda: self.btn_generate.setText("⚡ Generate with AI"))
        self.thread.start()

    def on_questions_ready(self, questions):
        self.generated_questions = questions
        self.table.setRowCount(len(questions))
        for row, q in enumerate(questions):
            opts = q.get('options', [])
            self.table.setItem(row, 0, QTableWidgetItem(q.get('question', '')))
            self.table.setItem(row, 1, QTableWidgetItem(opts[0] if len(opts) > 0 else ''))
            self.table.setItem(row, 2, QTableWidgetItem(opts[1] if len(opts) > 1 else ''))
            self.table.setItem(row, 3, QTableWidgetItem(q.get('correct', '')))
            self.table.setItem(row, 4, QTableWidgetItem(q.get('topic', '')))
        self.table.resizeRowsToContents()
        self.count_lbl.setText(f"{len(questions)} questions generated")

    def on_error(self, error_msg):
        QMessageBox.critical(self, "AI Error", error_msg)

    def save_to_bank(self):
        if not self.generated_questions:
            QMessageBox.warning(self, "No Questions", "Generate questions first.")
            return

        subject = self.topic_input.text().strip()
        difficulty = self.diff_combo.currentText()
        saved = 0
        errors = 0
        for q in self.generated_questions:
            try:
                self.dao.add_question(
                    q.get('question', ''),
                    q.get('options', []),
                    q.get('correct', ''),
                    'MCQ', subject, q.get('difficulty', difficulty), q.get('topic', subject)
                )
                saved += 1
            except Exception as e:
                logger.error(f"Error saving AI question: {e}")
                errors += 1

        msg = f"Saved {saved} questions to Question Bank."
        if errors:
            msg += f"\n{errors} questions could not be saved."
        QMessageBox.information(self, "Save Complete", msg)
