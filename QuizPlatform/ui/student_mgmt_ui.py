"""
filename: student_mgmt_ui.py
module: Student Management UI
author: Talha Ahmad
date: 2026-05-13
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                               QDialog, QFormLayout, QLineEdit, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.dao.student_dao import StudentDAO
from QuizPlatform.exceptions import QuizDatabaseError, QuizValidationError
from QuizPlatform.utils.form_validator import FormValidator

class StudentDialog(QDialog):
    def __init__(self, parent, student_data=None):
        super().__init__(parent)
        self.student_data = student_data
        self.setWindowTitle("Edit Student" if student_data else "Register New Student")
        self.setFixedWidth(400)
        self._build_ui()
        if student_data:
            self.name_input.setText(student_data['full_name'])
            self.user_input.setText(student_data['username'])
            self.pass_input.setPlaceholderText("(Leave blank to keep current password)")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form = QFormLayout()
        self.name_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        
        form.addRow("Full Name:", self.name_input)
        form.addRow("Username:", self.user_input)
        form.addRow("Password:", self.pass_input)
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_text = "Save Changes" if self.student_data else "Register Student"
        self.btn_save = QPushButton(btn_text)
        self.btn_save.clicked.connect(self._validate_and_accept)
        
        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_save)
        layout.addLayout(btns)

    def _validate_and_accept(self):
        name = self.name_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        
        try:
            FormValidator.validate_student(user, password, name, is_new=(not self.student_data))
            self.accept()
        except QuizValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'user': self.user_input.text().strip(),
            'pass': self.pass_input.text()
        }

class StudentMgmtUI(QWidget):
    def __init__(self):
        super().__init__()
        self.dao = StudentDAO()
        self._build_ui()
        self.refresh_students()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        
        hdr = QHBoxLayout()
        title = QLabel("👤 Student Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        hdr.addWidget(title)
        hdr.addStretch()
        
        btn_add = QPushButton("➕ Register New Student")
        btn_add.clicked.connect(self.add_student)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Full Name", "Username"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("background-color: white; border-radius: 8px; color: #1A1A2E;")
        layout.addWidget(self.table)
        
        btn_row = QHBoxLayout()
        btn_edit = QPushButton("✏ Edit Selected Student")
        btn_edit.setFixedHeight(44)
        btn_edit.clicked.connect(self.edit_student)
        btn_row.addWidget(btn_edit)
        
        btn_del = QPushButton("🗑 Delete Selected Student")
        btn_del.setFixedHeight(44)
        btn_del.clicked.connect(self.delete_student)
        btn_row.addWidget(btn_del)
        layout.addLayout(btn_row)

    def refresh_students(self):
        try:
            self.table.setRowCount(0)
            self.students = self.dao.get_all_students()
            self.table.setRowCount(len(self.students))
            for i, s in enumerate(self.students):
                self.table.setItem(i, 0, QTableWidgetItem(str(s['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(s['full_name']))
                self.table.setItem(i, 2, QTableWidgetItem(s['username']))
            self.table.resizeRowsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load students: {e}")

    def add_student(self):
        dlg = StudentDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                self.dao.add_student(data['user'], data['pass'], data['name'])
                self.refresh_students()
                QMessageBox.information(self, "Success", "Student registered successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def edit_student(self):
        curr = self.table.currentRow()
        if curr < 0:
            QMessageBox.warning(self, "Selection", "Select a student to edit.")
            return
        
        student_data = self.students[curr]
        dlg = StudentDialog(self, student_data)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            try:
                self.dao.update_student(student_data['id'], data['user'], data['pass'], data['name'])
                self.refresh_students()
                QMessageBox.information(self, "Success", "Student updated successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_student(self):
        curr = self.table.currentRow()
        if curr < 0:
            QMessageBox.warning(self, "Selection", "Select a student to delete.")
            return
        sid = int(self.table.item(curr, 0).text())
        name = self.table.item(curr, 1).text()
        
        reply = QMessageBox.question(self, "Confirm", f"Delete student {name}?\nAll their results and assignments will be removed.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.dao.delete_student(sid)
                self.refresh_students()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
