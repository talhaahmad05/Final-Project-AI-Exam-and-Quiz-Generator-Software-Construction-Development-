"""
filename: grading_ui.py
module: Manual Grading UI
author: Talha Ahmad
date: 2026-05-13
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QSpinBox, QMessageBox, QFrame, QScrollArea,
                               QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.dao.result_dao import ResultDAO
from QuizPlatform.exceptions import QuizDatabaseError

class GradingDialog(QDialog):
    """Dialog for reviewing and manually grading a student's submission"""

    def __init__(self, parent, result_id):
        super().__init__(parent)
        self.result_id = result_id
        self.dao = ResultDAO()
        self.result_data = None
        self.setWindowTitle("Review & Grade Submission")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self._load_data()
        self._build_ui()

    def _load_data(self):
        try:
            self.result_data = self.dao.get_result_by_id(self.result_id)
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "Error", str(e))
            self.reject()

    def _build_ui(self):
        if not self.result_data: return
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header info
        hdr = QFrame()
        hdr.setStyleSheet("background-color: #F5F5F5; border-radius: 8px; padding: 10px;")
        hl = QVBoxLayout(hdr)
        title = QLabel(f"Reviewing: {self.result_data['student_name']}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        exam_lbl = QLabel(f"Exam: {self.result_data['exam_title']} | Current Score: {self.result_data['score']} ({self.result_data['percentage']:.1f}%)")
        hl.addWidget(title)
        hl.addWidget(exam_lbl)
        layout.addWidget(hdr)

        # Answers Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Question", "Type", "Student Answer", "Correct Answer", "Marks Awarded"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(4, 180) # Marks Awarded
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("background-color: white; color: #1A1A2E;")
        
        answers = self.result_data.get('answers', [])
        self.table.setRowCount(len(answers))
        
        for row, ans in enumerate(answers):
            self.table.setItem(row, 0, QTableWidgetItem(ans['question_text']))
            self.table.setItem(row, 1, QTableWidgetItem(ans['type']))
            self.table.setItem(row, 2, QTableWidgetItem(str(ans['student_answer'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(ans['correct_answer'])))
            
            # Marks editor
            marks_widget = QWidget()
            ml = QHBoxLayout(marks_widget)
            ml.setContentsMargins(2, 2, 2, 2)
            spin = QSpinBox()
            spin.setRange(0, 100) # Assume max 100 per q for simplicity, ideally get from DB
            spin.setValue(int(ans['marks_awarded']))
            btn_update = QPushButton("Save")
            btn_update.setFixedWidth(100)
            btn_update.setFixedHeight(38)
            btn_update.clicked.connect(lambda _, r=row, q_id=ans['question_id'], s=spin: self._update_marks(q_id, s.value()))
            
            ml.addWidget(spin)
            ml.addWidget(btn_update)
            self.table.setCellWidget(row, 4, marks_widget)

        layout.addWidget(self.table)

        # Footer
        btn_close = QPushButton("Done / Close")
        btn_close.setFixedHeight(40)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _update_marks(self, q_id, val):
        try:
            self.dao.update_student_marks(self.result_id, q_id, val)
            QMessageBox.information(self, "Success", "Marks updated successfully!")
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "Error", str(e))
