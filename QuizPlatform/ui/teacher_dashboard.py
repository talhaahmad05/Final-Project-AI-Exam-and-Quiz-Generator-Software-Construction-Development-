"""
filename: teacher_dashboard.py
module: Teacher Dashboard UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 2 - Teacher modules
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QStackedWidget, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.ui.question_bank_ui import QuestionBankUI
from QuizPlatform.ui.exam_builder_ui import ExamBuilderUI
from QuizPlatform.ui.reports_ui import ReportsUI
from QuizPlatform.ui.ai_question_gen_ui import AIQuestionGenUI
from QuizPlatform.ui.student_mgmt_ui import StudentMgmtUI
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)

NAV_STYLE = """
    QPushButton {
        background-color: #2E7D32;
        color: #FF0000;
        text-align: left;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: bold;
        border: 1px solid #1B5E20;
    }
    QPushButton:hover {
        background-color: #388E3C;
        border: 1px solid #FF0000;
    }
    QPushButton:checked {
        background-color: #1B5E20;
        color: #FF8A80;
        font-weight: bold;
        border: 2px solid #FF0000;
    }
    QPushButton#btn_logout {
        background-color: #2E7D32;
        color: #FF0000;
        border: 1px solid #C62828;
    }
    QPushButton#btn_logout:hover {
        background-color: #D32F2F;
        color: white;
    }
"""


class TeacherDashboard(QWidget):
    """Main dashboard for Admin/Teacher role"""

    def __init__(self, app, user):
        super().__init__()
        self.app = app
        self.user = user
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Left Sidebar ──
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("background-color: #1A1A2E;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Brand header
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #16213E; border-bottom: 1px solid #2C2C54;")
        h_layout = QVBoxLayout(header)
        h_layout.setAlignment(Qt.AlignCenter)
        app_label = QLabel("🧠 QuizAI")
        app_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        app_label.setStyleSheet("color: white; background: transparent;")
        app_label.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(app_label)
        sb_layout.addWidget(header)

        # User info
        user_frame = QFrame()
        user_frame.setStyleSheet("background-color: #16213E; border-bottom: 1px solid #2C2C54;")
        u_layout = QVBoxLayout(user_frame)
        u_layout.setContentsMargins(16, 12, 16, 12)
        avatar = QLabel("👨‍🏫")
        avatar.setFont(QFont("Segoe UI", 22))
        avatar.setAlignment(Qt.AlignCenter)
        u_layout.addWidget(avatar)
        name_lbl = QLabel(self.user.get('full_name', 'Admin'))
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_lbl.setStyleSheet("color: white;")
        name_lbl.setAlignment(Qt.AlignCenter)
        u_layout.addWidget(name_lbl)
        role_lbl = QLabel("Admin / Teacher")
        role_lbl.setFont(QFont("Segoe UI", 9))
        role_lbl.setStyleSheet("color: #90CAF9;")
        role_lbl.setAlignment(Qt.AlignCenter)
        u_layout.addWidget(role_lbl)
        sb_layout.addWidget(user_frame)

        # Navigation buttons
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background-color: #1A1A2E;")
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 16, 10, 0)
        nav_layout.setSpacing(4)

        nav_items = [
            ("📚  Question Bank", 0),
            ("📝  Exam Builder", 1),
            ("🤖  AI Question Gen", 2),
            ("📊  Reports", 3),
            ("👤  Manage Students", 4),
        ]
        self.nav_buttons = []
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_STYLE)
            btn.setFont(QFont("Segoe UI", 11))
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_layout.addStretch()
        sb_layout.addWidget(nav_frame, 1)

        # Logout button
        logout_frame = QFrame()
        logout_frame.setStyleSheet("background-color: #16213E; border-top: 1px solid #2C2C54;")
        lo_layout = QVBoxLayout(logout_frame)
        lo_layout.setContentsMargins(10, 10, 10, 10)
        btn_logout = QPushButton("🚪  Logout")
        btn_logout.setObjectName("btn_logout")
        btn_logout.setStyleSheet(NAV_STYLE)
        btn_logout.setFont(QFont("Segoe UI", 11))
        btn_logout.clicked.connect(self.app.logout)
        lo_layout.addWidget(btn_logout)
        sb_layout.addWidget(logout_frame)

        main_layout.addWidget(sidebar)

        # ── Content Stack ──
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #F9FAFB;")
        self.stack.addWidget(QuestionBankUI(self.user))
        self.stack.addWidget(ExamBuilderUI(self.user))
        self.stack.addWidget(AIQuestionGenUI(self.user))
        self.stack.addWidget(ReportsUI())
        self.stack.addWidget(StudentMgmtUI())
        main_layout.addWidget(self.stack)

        # Activate first tab
        self._switch_page(0)

    def _switch_page(self, idx):
        """Switch the main content area"""
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)
