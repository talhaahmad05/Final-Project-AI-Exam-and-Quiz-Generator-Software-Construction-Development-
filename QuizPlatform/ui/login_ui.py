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

        # Left Sidebar (300px wide)
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-right: 1px solid #1e3a5f;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignCenter)
        sidebar_layout.setContentsMargins(30, 60, 30, 60)

        # Brain icon with subtle pink glow
        self.logo_label = QLabel("🧠")
        self.logo_label.setFont(QFont("Segoe UI", 72))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            color: #e91e8c;
            background: transparent;
        """)
        # Adding a shadow effect for the "glow"
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(25)
        glow.setColor(__import__('PyQt5.QtGui', fromlist=['QColor']).QColor("#e91e8c"))
        glow.setOffset(0, 0)
        self.logo_label.setGraphicsEffect(glow)
        sidebar_layout.addWidget(self.logo_label)

        title_label = QLabel("QuizAI Platform")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent; margin-top: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)

        student_info = QLabel("Talha Ahmad\nFA-24 BSSE 009 | Section A\nLahore Garrison University")
        student_info.setFont(QFont("Segoe UI", 10))
        student_info.setStyleSheet("color: #94a3b8; margin-top: 20px; background: transparent;")
        student_info.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(student_info)

        sidebar_layout.addStretch()

        course_info = QLabel("Software Construction & Development\nInstructor: Sir Ali Haider Naqvi")
        course_info.setFont(QFont("Segoe UI", 9))
        course_info.setStyleSheet("color: #94a3b8; background: transparent;")
        course_info.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(course_info)

        main_layout.addWidget(sidebar)

        # Right Panel (near black background with radial gradient)
        form_area = QFrame()
        form_area.setStyleSheet("""
            QFrame {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, 
                                          stop:0 #0d1117, stop:1 #080a0f);
            }
        """)
        form_layout = QVBoxLayout(form_area)
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setContentsMargins(60, 0, 60, 0)

        # Login Card (dark slate)
        form_container = QFrame()
        form_container.setFixedWidth(380)
        form_container.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 12px;
                border: 1px solid #334155;
            }
        """)
        fc_layout = QVBoxLayout(form_container)
        fc_layout.setContentsMargins(40, 45, 40, 45)
        fc_layout.setSpacing(18)

        welcome = QLabel("Welcome Back")
        welcome.setFont(QFont("Segoe UI", 22, QFont.Bold))
        welcome.setStyleSheet("color: white; border: none;")
        fc_layout.addWidget(welcome)

        subtitle = QLabel("Sign in to your account")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #94a3b8; margin-bottom: 5px; border: none;")
        fc_layout.addWidget(subtitle)

        user_label = QLabel("Username")
        user_label.setStyleSheet("color: white; font-weight: bold; border: none; font-size: 13px;")
        fc_layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(46)
        self.username_input.setStyleSheet("""
            QLineEdit { 
                border: 1px solid #334155; 
                border-radius: 6px; 
                padding: 8px 14px;
                font-size: 14px; 
                background-color: #0f172a; 
                color: white; 
            }
            QLineEdit:focus { 
                border: 2px solid #3b82f6; 
            }
        """)
        fc_layout.addWidget(self.username_input)

        pass_label = QLabel("Password")
        pass_label.setStyleSheet("color: white; font-weight: bold; border: none; font-size: 13px;")
        fc_layout.addWidget(pass_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(46)
        self.password_input.setStyleSheet("""
            QLineEdit { 
                border: 1px solid #334155; 
                border-radius: 6px; 
                padding: 8px 14px;
                font-size: 14px; 
                background-color: #0f172a; 
                color: white; 
            }
            QLineEdit:focus { 
                border: 2px solid #3b82f6; 
            }
        """)
        self.password_input.returnPressed.connect(self._do_login)
        fc_layout.addWidget(self.password_input)

        self.btn_login = QPushButton("Sign In")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #e91e8c;
                color: white;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #f43f9a;
            }
            QPushButton:pressed {
                background-color: #c2185b;
            }
        """)
        self.btn_login.clicked.connect(self._do_login)
        fc_layout.addWidget(self.btn_login)

        hint_text = QLabel("Default: admin / admin123\nStudents: student1,2,3 / student123")
        hint_text.setFont(QFont("Segoe UI", 9))
        hint_text.setStyleSheet("color: #64748b; text-align: center; border: none;")
        hint_text.setAlignment(Qt.AlignCenter)
        fc_layout.addWidget(hint_text)

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
