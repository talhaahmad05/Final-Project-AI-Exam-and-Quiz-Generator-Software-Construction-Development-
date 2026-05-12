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
from QuizPlatform.exceptions import QuizDatabaseError

class AddStudentDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add New Student")
        self.setFixedWidth(400)
        self._build_ui()

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
        
        self.btn_add = QPushButton("Add Student")
        self.btn_add.clicked.connect(self._validate_and_accept)
        
        btns.addWidget(self.btn_cancel)
        btns.addWidget(self.btn_add)
        layout.addLayout(btns)

    def _validate_and_accept(self):
        if not self.name_input.text().strip() or not self.user_input.text().strip() or not self.pass_input.text().strip():
            QMessageBox.warning(self, "Input Error", "All fields are required!")
            return
        self.accept()

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
        
        btn_del = QPushButton("🗑 Delete Selected Student")
        btn_del.clicked.connect(self.delete_student)
        layout.addWidget(btn_del)

    def refresh_students(self):
        try:
            self.table.setRowCount(0)
            students = self.dao.get_all_students()
            self.table.setRowCount(len(students))
            for i, s in enumerate(students):
                self.table.setItem(i, 0, QTableWidgetItem(str(s['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(s['full_name']))
                self.table.setItem(i, 2, QTableWidgetItem(s['username']))
            self.table.resizeRowsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load students: {e}")

    def add_student(self):
        dlg = AddStudentDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            if not all([data['name'], data['user'], data['pass']]):
                QMessageBox.warning(self, "Error", "All fields are required.")
                return
            try:
                self.dao.add_student(data['user'], data['pass'], data['name'])
                self.refresh_students()
                QMessageBox.information(self, "Success", "Student registered successfully!")
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
