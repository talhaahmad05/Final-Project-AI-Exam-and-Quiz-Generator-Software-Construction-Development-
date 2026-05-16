"""
filename: question_bank_ui.py
module: Question Bank UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 2 - Question Bank
"""

import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                              QDialog, QFormLayout, QLineEdit, QComboBox,
                              QTextEdit, QHeaderView, QFrame, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.dao.question_dao import QuestionDAO
from QuizPlatform.utils.form_validator import FormValidator
from QuizPlatform.exceptions import QuizValidationError, QuizDatabaseError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)


class QuestionDialog(QDialog):
    """Dialog for adding/editing a question"""

    def __init__(self, parent, question_data=None):
        super().__init__(parent)
        self.question_data = question_data
        self.setWindowTitle("Edit Question" if question_data else "Add Question")
        self.setMinimumWidth(520)
        self.setModal(True)
        self._build_ui()
        if question_data:
            self._populate(question_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        form = QFormLayout()
        self.question_text = QTextEdit()
        self.question_text.setFixedHeight(80)
        form.addRow("Question:", self.question_text)

        self.q_type = QComboBox()
        self.q_type.addItems(["MCQ", "True/False", "Short Answer"])
        self.q_type.currentTextChanged.connect(self._on_type_change)
        form.addRow("Type:", self.q_type)

        self.subject = QLineEdit()
        form.addRow("Subject:", self.subject)

        self.difficulty = QComboBox()
        self.difficulty.addItems(["easy", "medium", "hard"])
        form.addRow("Difficulty:", self.difficulty)

        self.topic = QLineEdit()
        form.addRow("Topic:", self.topic)

        layout.addLayout(form)

        # Options group (for MCQ)
        self.options_group = QGroupBox("Answer Options")
        opts_layout = QFormLayout(self.options_group)
        self.opt_inputs = []
        for letter in ['A', 'B', 'C', 'D']:
            inp = QLineEdit()
            inp.setPlaceholderText(f"Option {letter}")
            opts_layout.addRow(f"Option {letter}:", inp)
            self.opt_inputs.append(inp)
        layout.addWidget(self.options_group)

        # Correct answer
        form2 = QFormLayout()
        self.correct_answer = QLineEdit()
        self.correct_answer.setPlaceholderText("Exact text for MCQ, 'True'/'False', or model answer")
        form2.addRow("Correct Answer:", self.correct_answer)
        layout.addLayout(form2)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btn_cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save Question")
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        self._on_type_change("MCQ")

    def _on_type_change(self, q_type):
        self.options_group.setVisible(q_type == "MCQ")
        if q_type == "True/False":
            self.correct_answer.setPlaceholderText("Enter 'True' or 'False'")
        elif q_type == "Short Answer":
            self.correct_answer.setPlaceholderText("Enter the model answer")
        else:
            self.correct_answer.setPlaceholderText("Exact text of the correct option")

    def _populate(self, data):
        self.question_text.setPlainText(data.get('question_text', ''))
        self.q_type.setCurrentText(data.get('type', 'MCQ'))
        self.subject.setText(data.get('subject', ''))
        self.difficulty.setCurrentText(data.get('difficulty', 'easy'))
        self.topic.setText(data.get('topic', '') or '')
        self.correct_answer.setText(data.get('correct_answer', ''))
        options = data.get('options', [])
        for i, inp in enumerate(self.opt_inputs):
            if i < len(options):
                inp.setText(options[i])

    def _save(self):
        q_type = self.q_type.currentText()
        options = [inp.text().strip() for inp in self.opt_inputs] if q_type == "MCQ" else None
        try:
            FormValidator.validate_question(
                self.question_text.toPlainText().strip(),
                options,
                self.correct_answer.text().strip(),
                q_type
            )
            self.accept()
        except QuizValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))

    def get_data(self):
        q_type = self.q_type.currentText()
        return {
            'question_text': self.question_text.toPlainText().strip(),
            'options': [inp.text().strip() for inp in self.opt_inputs] if q_type == "MCQ" else None,
            'correct_answer': self.correct_answer.text().strip(),
            'type': q_type,
            'subject': self.subject.text().strip(),
            'difficulty': self.difficulty.currentText(),
            'topic': self.topic.text().strip()
        }


class QuestionBankUI(QWidget):
    """Question Bank management screen for teachers"""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.dao = QuestionDAO()
        self.all_questions = []
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("📚 Question Bank")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_delete_all = QPushButton("🗑 Delete All")
        btn_delete_all.setObjectName("btn_delete_all")
        btn_delete_all.setFixedWidth(150)
        btn_delete_all.setFixedHeight(44)
        # Note: Theme style will apply (Green/Red), but we can add a specific tooltip
        btn_delete_all.setToolTip("Delete all questions from the bank")
        btn_delete_all.clicked.connect(self.delete_all_questions)
        hdr.addWidget(btn_delete_all)

        btn_add = QPushButton("➕ Add Question")
        btn_add.setFixedWidth(170)
        btn_add.setFixedHeight(44)
        btn_add.clicked.connect(self.add_question)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        # Filter bar
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #E0E0E0; padding: 6px;")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 6, 10, 6)

        filter_layout.addWidget(QLabel("Subject:"))
        self.filter_subject = QLineEdit()
        self.filter_subject.setPlaceholderText("Filter by subject...")
        self.filter_subject.setFixedWidth(160)
        filter_layout.addWidget(self.filter_subject)

        filter_layout.addWidget(QLabel("Difficulty:"))
        self.filter_diff = QComboBox()
        self.filter_diff.addItems(["All", "easy", "medium", "hard"])
        self.filter_diff.setFixedWidth(100)
        filter_layout.addWidget(self.filter_diff)

        filter_layout.addWidget(QLabel("Topic:"))
        self.filter_topic = QLineEdit()
        self.filter_topic.setPlaceholderText("Filter by topic...")
        self.filter_topic.setFixedWidth(140)
        filter_layout.addWidget(self.filter_topic)

        btn_filter = QPushButton("🔍 Search")
        btn_filter.clicked.connect(self.search_questions)
        btn_filter.setFixedWidth(90)
        filter_layout.addWidget(btn_filter)

        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self.refresh_table)
        filter_layout.addWidget(btn_reset)
        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Question", "Type", "Subject", "Difficulty", "Topic", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 50) # ID
        self.table.setColumnWidth(6, 220) # Actions
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; }
            QTableWidget::item { padding: 6px; }
        """)
        layout.addWidget(self.table)

        count_layout = QHBoxLayout()
        self.count_label = QLabel("Total: 0 questions")
        self.count_label.setStyleSheet("color: #666666; font-size: 12px;")
        count_layout.addWidget(self.count_label)
        layout.addLayout(count_layout)

    def refresh_table(self):
        try:
            self.all_questions = self.dao.get_all_questions()
            self._populate_table(self.all_questions)
            self.filter_subject.clear()
            self.filter_topic.clear()
            self.filter_diff.setCurrentIndex(0)
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def search_questions(self):
        subject = self.filter_subject.text().strip() or None
        diff = self.filter_diff.currentText()
        difficulty = None if diff == "All" else diff
        topic = self.filter_topic.text().strip() or None
        try:
            results = self.dao.search_questions(subject, difficulty, topic)
            self._populate_table(results)
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def _populate_table(self, questions):
        self.table.setRowCount(len(questions))
        for row, q in enumerate(questions):
            self.table.setItem(row, 0, QTableWidgetItem(str(q['id'])))
            text_preview = q['question_text'][:60] + "..." if len(q['question_text']) > 60 else q['question_text']
            self.table.setItem(row, 1, QTableWidgetItem(text_preview))
            self.table.setItem(row, 2, QTableWidgetItem(q['type']))
            self.table.setItem(row, 3, QTableWidgetItem(q['subject']))

            diff_item = QTableWidgetItem(q['difficulty'])
            colors = {'easy': '#2E7D32', 'medium': '#E65100', 'hard': '#B71C1C'}
            diff_item.setForeground(__import__('PyQt5.QtGui', fromlist=['QColor']).QColor(colors.get(q['difficulty'], '#000')))
            self.table.setItem(row, 4, diff_item)

            self.table.setItem(row, 5, QTableWidgetItem(q.get('topic', '') or ''))

            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_edit = QPushButton("✏ Edit")
            btn_edit.setFixedHeight(40)
            btn_edit.clicked.connect(lambda _, r=row: self.edit_question(r))
            btn_del = QPushButton("🗑 Del")
            btn_del.setFixedHeight(40)
            btn_del.clicked.connect(lambda _, r=row: self.delete_question(r))
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_del)
            self.table.setCellWidget(row, 6, btn_widget)
        self.table.resizeRowsToContents()
        self.count_label.setText(f"Total: {len(questions)} questions")

    def add_question(self):
        dlg = QuestionDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                self.dao.add_question(
                    data['question_text'], data['options'], data['correct_answer'],
                    data['type'], data['subject'], data['difficulty'], data['topic']
                )
                self.refresh_table()
                QMessageBox.information(self, "Success", "Question added successfully!")
            except QuizDatabaseError as e:
                QMessageBox.critical(self, "DB Error", str(e))

    def edit_question(self, row):
        q_id = int(self.table.item(row, 0).text())
        question_data = next((q for q in self.all_questions if q['id'] == q_id), None)
        if not question_data:
            self.refresh_table()
            return
        dlg = QuestionDialog(self, question_data)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                self.dao.update_question(
                    q_id, data['question_text'], data['options'], data['correct_answer'],
                    data['type'], data['subject'], data['difficulty'], data['topic']
                )
                self.refresh_table()
                QMessageBox.information(self, "Success", "Question updated successfully!")
            except QuizDatabaseError as e:
                QMessageBox.critical(self, "DB Error", str(e))

    def delete_question(self, row):
        q_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirm Delete",
                                     "Delete this question? It will be removed from all exams.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.dao.delete_question(q_id)
                self.refresh_table()
            except QuizDatabaseError as e:
                QMessageBox.critical(self, "DB Error", str(e))

    def delete_all_questions(self):
        """Handler for the 'Delete All' button"""
        count = len(self.all_questions)
        if count == 0:
            QMessageBox.information(self, "Info", "The question bank is already empty.")
            return

        reply = QMessageBox.warning(self, "Confirm MASS Delete",
                                     f"Are you SURE you want to delete ALL {count} questions?\n"
                                     "This action is permanent and will clear all question links in exams.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Second confirmation for safety
            reply2 = QMessageBox.critical(self, "Final Warning",
                                          "This will also delete student answers and hints related to these questions.\n"
                                          "Proceed with total deletion?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply2 == QMessageBox.Yes:
                try:
                    self.dao.delete_all_questions()
                    self.refresh_table()
                    QMessageBox.information(self, "Success", "All questions have been deleted.")
                    logger.info(f"User {self.user.get('username', 'Unknown')} deleted all questions.")
                except QuizDatabaseError as e:
                    QMessageBox.critical(self, "DB Error", str(e))
