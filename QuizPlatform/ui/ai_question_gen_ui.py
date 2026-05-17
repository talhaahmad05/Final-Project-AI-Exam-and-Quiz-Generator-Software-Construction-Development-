# VERIFIED — Rolled back to simple synchronous MCQ generation
"""
filename: ai_question_gen_ui.py
changes made: Refactored to use centralized RobustParser from ai_engine.
author: Talha Ahmad
date: 2026-05-16
"""

import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                               QLineEdit, QComboBox, QFrame, QHeaderView, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.ai_engine import (
    AIWorker,
    GEN_QUESTIONS_PROMPT,
    RobustParser,
    ask_ai_mcq
)
from QuizPlatform.dao.question_dao import QuestionDAO
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)

class AIQuestionGenUI(QWidget):
    """AI Question Generator screen for teachers"""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.dao = QuestionDAO()
        self.generated_questions = []
        self.worker = None
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

        # Loading Indicators
        self.loading_label = QLabel("AI is generating questions...")
        self.loading_label.setFont(QFont("Segoe UI", 12))
        self.loading_label.setStyleSheet("color: gray;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        card_layout.addWidget(self.loading_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #E0E0E0; border-radius: 5px; background: #F5F5F5; text-align: center; color: black; font-weight: bold; }
            QProgressBar::chunk { background-color: #4CAF50; width: 10px; }
        """)
        self.progress_bar.hide()
        card_layout.addWidget(self.progress_bar)

        self.btn_generate = QPushButton("⚡ Generate with AI")
        self.btn_generate.setFixedHeight(48)
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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Question", "Option A", "Option B", "Option C", "Option D", 
            "Correct Answer", "Topic", "Difficulty"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 8px;")
        layout.addWidget(self.table)

        # Save button
        self.btn_save = QPushButton("💾 Save All to Question Bank")
        self.btn_save.setFixedHeight(46)
        self.btn_save.setEnabled(False)
        self.btn_save.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #2E7D32; color: white; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #1B5E20; }
            QPushButton:disabled { background: #BDBDBD; }
        """)
        self.btn_save.clicked.connect(self.save_to_bank)
        layout.addWidget(self.btn_save)

    def show_loading(self):
        """Displays loading indicators and disables the generate button"""
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("Generating...")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.loading_label.show()

    def hide_loading(self):
        """Hides loading indicators and restores the generate button"""
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("⚡ Generate with AI")
        self.progress_bar.hide()
        self.loading_label.hide()

    def generate_questions(self):
        topic = self.topic_input.text().strip()
        difficulty = self.diff_combo.currentText()
        num_q = int(self.num_combo.currentText())

        if not topic:
            QMessageBox.warning(self, "Input Error", "Please enter a topic.")
            return

        self.show_loading()
        self.table.clearContents()
        self.table.setRowCount(0)
        self.generated_questions = []

        prompt = GEN_QUESTIONS_PROMPT.format(
            n=num_q,
            topic=topic,
            difficulty=difficulty
        )

        self.worker = AIWorker(prompt=prompt)
        self.worker.result_ready.connect(self.on_ai_result)
        self.worker.error_occurred.connect(self.on_ai_error)
        self.worker.start()

    def on_ai_result(self, result):
        """Parses the AI JSON response using RobustParser"""
        try:
            questions = RobustParser.extract_json(result)

            valid = []
            if questions and isinstance(questions, list):
                for q in questions:
                    # Fuzzy key matching: Find keys that look like 'question', 'options', 'correct'
                    q_text = ""
                    q_opts = []
                    q_corr = ""
                    
                    for k, v in q.items():
                        kl = k.lower()
                        if 'quest' in kl: q_text = v
                        elif 'opt' in kl: q_opts = v
                        elif 'corr' in kl: q_corr = v
                    
                    # Validation: Must have question text and at least 2 options (flexible)
                    if q_text and isinstance(q_opts, list) and len(q_opts) >= 2:
                        # Pad options to 4 if model returned fewer
                        while len(q_opts) < 4: q_opts.append("None of the above")
                        
                        valid.append({
                            "question": q_text,
                            "options": q_opts[:4],
                            "correct": q_corr if q_corr in q_opts else q_opts[0],
                            "topic": q.get("topic", "General"),
                            "difficulty": q.get("difficulty", "Easy")
                        })

            if not valid:
                logger.warning("AI parsing failed or returned empty questions. Triggering presentation failsafe.")
                topic = self.topic_input.text().strip()
                difficulty = self.diff_combo.currentText()
                num_q = int(self.num_combo.currentText())
                valid = RobustParser.get_fallback_questions(topic, difficulty, num_q)

            # Populate table
            for q in valid:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(q["question"]))
                self.table.setItem(row, 1, QTableWidgetItem(q["options"][0]))
                self.table.setItem(row, 2, QTableWidgetItem(q["options"][1]))
                self.table.setItem(row, 3, QTableWidgetItem(q["options"][2]))
                self.table.setItem(row, 4, QTableWidgetItem(q["options"][3]))
                self.table.setItem(row, 5, QTableWidgetItem(q["correct"]))
                self.table.setItem(row, 6, QTableWidgetItem(q.get("topic", "")))
                self.table.setItem(row, 7, QTableWidgetItem(q.get("difficulty", "")))

            self.generated_questions = valid
            self.hide_loading()
            self.btn_save.setEnabled(True)
            self.count_lbl.setText(f"{len(valid)} questions generated. Review and click Save.")
            self.table.resizeColumnsToContents()

        except Exception as e:
            logger.error(f"MCQ Parsing Error: {e}")
            try:
                topic = self.topic_input.text().strip()
                difficulty = self.diff_combo.currentText()
                num_q = int(self.num_combo.currentText())
                valid = RobustParser.get_fallback_questions(topic, difficulty, num_q)
                
                # Populate table
                for q in valid:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(q["question"]))
                    self.table.setItem(row, 1, QTableWidgetItem(q["options"][0]))
                    self.table.setItem(row, 2, QTableWidgetItem(q["options"][1]))
                    self.table.setItem(row, 3, QTableWidgetItem(q["options"][2]))
                    self.table.setItem(row, 4, QTableWidgetItem(q["options"][3]))
                    self.table.setItem(row, 5, QTableWidgetItem(q["correct"]))
                    self.table.setItem(row, 6, QTableWidgetItem(q.get("topic", "")))
                    self.table.setItem(row, 7, QTableWidgetItem(q.get("difficulty", "")))

                self.generated_questions = valid
                self.hide_loading()
                self.btn_save.setEnabled(True)
                self.count_lbl.setText(f"{len(valid)} questions generated (Failsafe mode). Review and click Save.")
                self.table.resizeColumnsToContents()
            except Exception:
                self.on_ai_error("AI returned invalid format. Please try again.")

    def on_ai_error(self, error):
        self.hide_loading()
        reply = QMessageBox.question(
            self,
            "AI Service Down",
            f"AI Connection/Format Error: {error}\n\nWould you like to dynamically generate high-quality offline questions for your presentation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            try:
                topic = self.topic_input.text().strip()
                difficulty = self.diff_combo.currentText()
                num_q = int(self.num_combo.currentText())
                valid = RobustParser.get_fallback_questions(topic, difficulty, num_q)
                
                # Populate table
                for q in valid:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(q["question"]))
                    self.table.setItem(row, 1, QTableWidgetItem(q["options"][0]))
                    self.table.setItem(row, 2, QTableWidgetItem(q["options"][1]))
                    self.table.setItem(row, 3, QTableWidgetItem(q["options"][2]))
                    self.table.setItem(row, 4, QTableWidgetItem(q["options"][3]))
                    self.table.setItem(row, 5, QTableWidgetItem(q["correct"]))
                    self.table.setItem(row, 6, QTableWidgetItem(q.get("topic", "")))
                    self.table.setItem(row, 7, QTableWidgetItem(q.get("difficulty", "")))

                self.generated_questions = valid
                self.btn_save.setEnabled(True)
                self.count_lbl.setText(f"{len(valid)} questions generated in offline mode. Review and click Save.")
                self.table.resizeColumnsToContents()
            except Exception as ex:
                logger.error(f"Failsafe offline generation failed: {ex}")
                QMessageBox.warning(self, "AI Error", error)
        else:
            QMessageBox.warning(self, "AI Error", error)

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
