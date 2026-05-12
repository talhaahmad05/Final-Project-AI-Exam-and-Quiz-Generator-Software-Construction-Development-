"""
filename: exam_builder_ui.py
module: Exam Builder UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 2 - Exam Builder
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                              QDialog, QFormLayout, QLineEdit, QComboBox,
                              QCheckBox, QListWidget, QListWidgetItem, QSplitter,
                              QHeaderView, QFrame, QAbstractItemView, QSpinBox, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.dao.exam_dao import ExamDAO
from QuizPlatform.dao.question_dao import QuestionDAO
from QuizPlatform.dao.student_dao import StudentDAO
from QuizPlatform.utils.form_validator import FormValidator
from QuizPlatform.exceptions import QuizValidationError, QuizDatabaseError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)


class CreateExamDialog(QDialog):
    """Dialog for creating a new exam"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Create New Exam")
        self.setMinimumWidth(600)
        self.setMinimumHeight(650)
        self.setModal(True)
        self.exam_dao = ExamDAO()
        self.question_dao = QuestionDAO()
        self.student_dao = StudentDAO()
        self.selected_questions = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)

        tabs = QTabWidget()

        # ── Tab 1: Exam Details ──
        details_tab = QWidget()
        form = QFormLayout(details_tab)
        form.setSpacing(10)
        self.title_input = QLineEdit()
        self.subject_input = QLineEdit()
        self.time_limit = QSpinBox()
        self.time_limit.setRange(1, 300)
        self.time_limit.setValue(30)
        self.total_marks = QSpinBox()
        self.total_marks.setRange(1, 500)
        self.total_marks.setValue(10)
        self.pass_pct = QSpinBox()
        self.pass_pct.setRange(0, 100)
        self.pass_pct.setValue(50)
        self.shuffle_cb = QCheckBox("Shuffle question order")
        self.hints_cb = QCheckBox("Enable hints for students")

        form.addRow("Exam Title:", self.title_input)
        form.addRow("Subject:", self.subject_input)
        form.addRow("Time Limit (mins):", self.time_limit)
        form.addRow("Total Marks:", self.total_marks)
        form.addRow("Pass Percentage (%):", self.pass_pct)
        form.addRow("", self.shuffle_cb)
        form.addRow("", self.hints_cb)
        tabs.addTab(details_tab, "📋 Exam Details")

        # ── Tab 2: Select Questions ──
        q_tab = QWidget()
        q_layout = QVBoxLayout(q_tab)

        filter_row = QHBoxLayout()
        self.q_filter_diff = QComboBox()
        self.q_filter_diff.addItems(["All", "easy", "medium", "hard"])
        self.q_filter_subj = QLineEdit()
        self.q_filter_subj.setPlaceholderText("Filter by subject...")
        btn_filter = QPushButton("Filter")
        btn_filter.clicked.connect(self._load_questions)
        btn_rand = QPushButton("🎲 Random 5")
        btn_rand.clicked.connect(self._add_random_questions)
        filter_row.addWidget(QLabel("Difficulty:"))
        filter_row.addWidget(self.q_filter_diff)
        filter_row.addWidget(self.q_filter_subj)
        filter_row.addWidget(btn_filter)
        filter_row.addWidget(btn_rand)
        q_layout.addLayout(filter_row)

        splitter = QSplitter(Qt.Horizontal)
        self.all_questions_list = QListWidget()
        self.all_questions_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.all_questions_list.setStyleSheet("""
            QListWidget { background-color: white; border: 2px solid #1565C0; border-radius: 6px; color: #1A1A2E; font-size: 13px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #EEEEEE; }
            QListWidget::item:selected { background-color: #E3F2FD; color: #1565C0; }
        """)
        self.selected_questions_list = QListWidget()
        self.selected_questions_list.setStyleSheet("""
            QListWidget { background-color: white; border: 2px solid #2E7D32; border-radius: 6px; color: #1A1A2E; font-size: 13px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #EEEEEE; }
        """)

        btn_col = QVBoxLayout()
        btn_add_q = QPushButton("Add →")
        btn_add_q.setFixedHeight(40)
        btn_add_q.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; border-radius: 6px;")
        btn_add_q.clicked.connect(self._add_selected)
        btn_rem_q = QPushButton("← Remove")
        btn_rem_q.setFixedHeight(40)
        btn_rem_q.setStyleSheet("background-color: #C62828; color: white; font-weight: bold; border-radius: 6px;")
        btn_rem_q.clicked.connect(self._remove_selected)
        btn_col.addStretch()
        btn_col.addWidget(btn_add_q)
        btn_col.addWidget(btn_rem_q)
        btn_col.addStretch()

        mid_widget = QWidget()
        mid_widget.setLayout(btn_col)

        splitter.addWidget(self.all_questions_list)
        splitter.addWidget(mid_widget)
        splitter.addWidget(self.selected_questions_list)
        splitter.setSizes([300, 60, 200])
        q_layout.addWidget(QLabel("Available Questions (select then click →)"))
        q_layout.addWidget(splitter)
        self._load_questions()
        tabs.addTab(q_tab, "❓ Select Questions")

        # ── Tab 3: Assign Students ──
        assign_tab = QWidget()
        a_layout = QVBoxLayout(assign_tab)
        self.assign_all_cb = QCheckBox("Assign to ALL students")
        self.assign_all_cb.setChecked(True)
        self.assign_all_cb.stateChanged.connect(self._toggle_student_list)
        a_layout.addWidget(self.assign_all_cb)
        self.students_list = QListWidget()
        self.students_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.students_list.setEnabled(False)
        self._load_students()
        a_layout.addWidget(QLabel("(or select individual students below)"))
        a_layout.addWidget(self.students_list)
        tabs.addTab(assign_tab, "👤 Assign Students")

        layout.addWidget(tabs)

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btn_cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_create = QPushButton("✅ Create & Assign Exam")
        btn_create.setObjectName("btn_create")
        btn_create.clicked.connect(self._create_exam)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_create)
        layout.addLayout(btn_row)

    def _load_questions(self):
        diff = self.q_filter_diff.currentText()
        subj = self.q_filter_subj.text().strip() or None
        difficulty = None if diff == "All" else diff
        try:
            questions = self.question_dao.search_questions(subject=subj, difficulty=difficulty)
            self.all_questions_list.clear()
            self._all_q_data = questions
            for q in questions:
                item = QListWidgetItem(f"[{q['type']}] [{q['difficulty']}] {q['question_text'][:60]}")
                item.setData(Qt.UserRole, q['id'])
                self.all_questions_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _add_selected(self):
        for item in self.all_questions_list.selectedItems():
            q_id = item.data(Qt.UserRole)
            if q_id not in [self.selected_questions_list.item(i).data(Qt.UserRole)
                             for i in range(self.selected_questions_list.count())]:
                new_item = QListWidgetItem(item.text())
                new_item.setData(Qt.UserRole, q_id)
                self.selected_questions_list.addItem(new_item)

    def _remove_selected(self):
        for item in self.selected_questions_list.selectedItems():
            self.selected_questions_list.takeItem(self.selected_questions_list.row(item))

    def _add_random_questions(self):
        import random
        if not hasattr(self, '_all_q_data'):
            return
        sample = random.sample(self._all_q_data, min(5, len(self._all_q_data)))
        existing_ids = [self.selected_questions_list.item(i).data(Qt.UserRole)
                        for i in range(self.selected_questions_list.count())]
        for q in sample:
            if q['id'] not in existing_ids:
                new_item = QListWidgetItem(f"[{q['type']}] [{q['difficulty']}] {q['question_text'][:60]}")
                new_item.setData(Qt.UserRole, q['id'])
                self.selected_questions_list.addItem(new_item)

    def _load_students(self):
        try:
            students = self.student_dao.get_all_students()
            self._all_students = students
            for s in students:
                item = QListWidgetItem(f"{s['full_name']} ({s['username']})")
                item.setData(Qt.UserRole, s['id'])
                self.students_list.addItem(item)
        except Exception as e:
            logger.error(f"Error loading students: {e}")

    def _toggle_student_list(self, state):
        self.students_list.setEnabled(not bool(state))

    def _create_exam(self):
        try:
            FormValidator.validate_exam(
                self.title_input.text(), self.subject_input.text(),
                self.time_limit.value(), self.total_marks.value(), self.pass_pct.value()
            )
            q_count = self.selected_questions_list.count()
            if q_count == 0:
                QMessageBox.warning(self, "No Questions", "Please add at least one question to the exam.")
                return

            # Create exam
            exam_id = self.exam_dao.create_exam(
                self.title_input.text(), self.subject_input.text(),
                self.time_limit.value(), self.total_marks.value(), self.pass_pct.value(),
                self.shuffle_cb.isChecked(), self.hints_cb.isChecked()
            )

            # Add questions
            q_ids = [self.selected_questions_list.item(i).data(Qt.UserRole)
                     for i in range(self.selected_questions_list.count())]
            self.exam_dao.add_questions_to_exam(exam_id, q_ids)

            # Assign students
            if self.assign_all_cb.isChecked():
                self.exam_dao.assign_exam_to_students(exam_id, None)
            else:
                s_ids = [item.data(Qt.UserRole) for item in self.students_list.selectedItems()]
                if s_ids:
                    self.exam_dao.assign_exam_to_students(exam_id, s_ids)

            QMessageBox.information(self, "Success", f"Exam '{self.title_input.text()}' created and assigned!")
            self.accept()
        except QuizValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "DB Error", str(e))


class ExamBuilderUI(QWidget):
    """Exam Builder screen for teachers"""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.exam_dao = ExamDAO()
        self.all_exams = []
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        hdr = QHBoxLayout()
        title = QLabel("📝 Exam Builder")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        hdr.addWidget(title)
        hdr.addStretch()
        btn_create = QPushButton("➕ Create New Exam")
        btn_create.setFixedWidth(180)
        btn_create.setFixedHeight(38)
        btn_create.setStyleSheet("""
            QPushButton { background-color: #2E7D32; color: white; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #1B5E20; }
        """)
        btn_create.clicked.connect(self.create_exam)
        hdr.addWidget(btn_create)
        layout.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Subject", "Time (min)", "Total Marks", "Pass %", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 8px;")
        layout.addWidget(self.table)

    def refresh_table(self):
        try:
            self.all_exams = self.exam_dao.get_all_exams()
            self.table.setRowCount(len(self.all_exams))
            for row, exam in enumerate(self.all_exams):
                self.table.setItem(row, 0, QTableWidgetItem(str(exam['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(exam['title']))
                self.table.setItem(row, 2, QTableWidgetItem(exam['subject']))
                self.table.setItem(row, 3, QTableWidgetItem(str(exam['time_limit'])))
                self.table.setItem(row, 4, QTableWidgetItem(str(exam['total_marks'])))
                self.table.setItem(row, 5, QTableWidgetItem(f"{exam['pass_percentage']}%"))

                btn_widget = QWidget()
                bl = QHBoxLayout(btn_widget)
                bl.setContentsMargins(4, 2, 4, 2)
                btn_del = QPushButton("🗑 Delete")
                btn_del.setStyleSheet("background-color: #C62828; color: white; border-radius: 4px; padding: 3px;")
                btn_del.clicked.connect(lambda _, r=row: self.delete_exam(r))
                bl.addWidget(btn_del)
                self.table.setCellWidget(row, 6, btn_widget)
            self.table.resizeRowsToContents()
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def create_exam(self):
        dlg = CreateExamDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.refresh_table()

    def delete_exam(self, row):
        exam_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Confirm Delete",
                                     "Delete this exam and all its data permanently?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.exam_dao.delete_exam(exam_id)
                self.refresh_table()
            except QuizDatabaseError as e:
                QMessageBox.critical(self, "DB Error", str(e))
