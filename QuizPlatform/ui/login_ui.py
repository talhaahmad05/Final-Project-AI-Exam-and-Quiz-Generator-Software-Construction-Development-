"""
filename: login_ui.py
module: Login Screen UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 1 - Authentication
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QMessageBox, QFrame, QDialog,
                              QFormLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon

from QuizPlatform.dao.student_dao import StudentDAO
from QuizPlatform.utils.form_validator import FormValidator
from QuizPlatform.exceptions import QuizAuthError, QuizValidationError, QuizDatabaseError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)


class ChangePasswordDialog(QDialog):
    """Dialog for changing user password"""

    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.dao = StudentDAO()
        self.setWindowTitle("Change Password")
        self.setFixedSize(360, 280)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Change Password")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        layout.addWidget(title)

        form = QFormLayout()
        self.old_pass = QLineEdit()
        self.old_pass.setEchoMode(QLineEdit.Password)
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.Password)
        self.confirm_pass = QLineEdit()
        self.confirm_pass.setEchoMode(QLineEdit.Password)

        form.addRow("Current Password:", self.old_pass)
        form.addRow("New Password:", self.new_pass)
        form.addRow("Confirm Password:", self.confirm_pass)
        layout.addLayout(form)
        layout.addSpacing(10)

        btn_change = QPushButton("Update Password")
        btn_change.clicked.connect(self._do_change)
        layout.addWidget(btn_change)

    def _do_change(self):
        try:
            FormValidator.validate_password_change(
                self.old_pass.text(), self.new_pass.text(), self.confirm_pass.text()
            )
            # Verify old password
            dao = StudentDAO()
            dao.authenticate(self.user['username'], self.old_pass.text())
            dao.change_password(self.user['id'], self.new_pass.text())
            QMessageBox.information(self, "Success", "Password changed successfully!")
            self.accept()
        except QuizValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except QuizAuthError:
            QMessageBox.warning(self, "Error", "Current password is incorrect.")
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            QMessageBox.critical(self, "Error", str(e))


class LoginScreen(QWidget):
    """Login screen with username/password authentication"""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.dao = StudentDAO()
        self._build_ui()

    def _build_ui(self):
        # Main layout: left sidebar + right form
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left dark sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(380)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                              stop:0 #1A1A2E, stop:1 #16213E);
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignCenter)
        sidebar_layout.setContentsMargins(40, 60, 40, 60)

        logo_label = QLabel("🧠")
        logo_label.setFont(QFont("Segoe UI", 64))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")
        sidebar_layout.addWidget(logo_label)

        title_label = QLabel("QuizAI Platform")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)

        subtitle = QLabel("Talha Ahmad\nFA-24 BSSE 009 | Section A\nLahore Garrison University")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #90CAF9; margin-top: 10px; background: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(subtitle)

        sidebar_layout.addStretch()

        subject_label = QLabel("Software Construction & Development\nInstructor: Sir Ali Haider Naqvi")
        subject_label.setFont(QFont("Segoe UI", 9))
        subject_label.setStyleSheet("color: #78909C; background: transparent;")
        subject_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(subject_label)

        main_layout.addWidget(sidebar)

        # Right form area
        form_area = QFrame()
        form_area.setStyleSheet("background-color: #F9FAFB;")
        form_layout = QVBoxLayout(form_area)
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setContentsMargins(80, 0, 80, 0)

        form_container = QFrame()
        form_container.setFixedWidth(360)
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E0E0E0;
            }
        """)
        fc_layout = QVBoxLayout(form_container)
        fc_layout.setContentsMargins(40, 40, 40, 40)
        fc_layout.setSpacing(16)

        welcome = QLabel("Welcome Back")
        welcome.setFont(QFont("Segoe UI", 20, QFont.Bold))
        welcome.setStyleSheet("color: #1A1A2E; border: none;")
        fc_layout.addWidget(welcome)

        hint = QLabel("Sign in to your account")
        hint.setFont(QFont("Segoe UI", 10))
        hint.setStyleSheet("color: #888888; margin-bottom: 8px; border: none;")
        fc_layout.addWidget(hint)

        user_label = QLabel("Username")
        user_label.setStyleSheet("color: #1A1A2E; font-weight: bold; border: none;")
        fc_layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(44)
        self.username_input.setStyleSheet("""
            QLineEdit { border: 1px solid #DDDDDD; border-radius: 8px; padding: 8px 12px;
                        font-size: 13px; background-color: #F9FAFB; color: #1A1A2E; }
            QLineEdit:focus { border: 2px solid #1565C0; background-color: white; }
        """)
        fc_layout.addWidget(self.username_input)

        pass_label = QLabel("Password")
        pass_label.setStyleSheet("color: #1A1A2E; font-weight: bold; border: none;")
        fc_layout.addWidget(pass_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet("""
            QLineEdit { border: 1px solid #DDDDDD; border-radius: 8px; padding: 8px 12px;
                        font-size: 13px; background-color: #F9FAFB; color: #1A1A2E; }
            QLineEdit:focus { border: 2px solid #1565C0; background-color: white; }
        """)
        self.password_input.returnPressed.connect(self._do_login)
        fc_layout.addWidget(self.password_input)

        self.btn_login = QPushButton("Sign In")
        self.btn_login.setFixedHeight(46)
        self.btn_login.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_login.clicked.connect(self._do_login)
        fc_layout.addWidget(self.btn_login)

        info_label = QLabel("Default: admin / admin123\nStudents: student1,2,3 / student123")
        info_label.setFont(QFont("Segoe UI", 9))
        info_label.setStyleSheet("color: #999999; text-align: center; border: none;")
        info_label.setAlignment(Qt.AlignCenter)
        fc_layout.addWidget(info_label)

        form_layout.addWidget(form_container)
        main_layout.addWidget(form_area)

    def _do_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        try:
            FormValidator.validate_login(username, password)
            user = self.dao.authenticate(username, password)
            logger.info(f"User '{username}' logged in as {user['role']}")

            if user['role'] == 'Admin':
                self.app.show_teacher_dashboard(user)
            else:
                self.app.show_student_dashboard(user)

        except QuizValidationError as e:
            QMessageBox.warning(self, "Input Error", str(e))
        except QuizAuthError as e:
            QMessageBox.critical(self, "Login Failed", str(e))
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "Database Error", f"Could not connect to database.\n{str(e)}")
        except Exception as e:
            logger.error(f"Unexpected login error: {e}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{str(e)}")
