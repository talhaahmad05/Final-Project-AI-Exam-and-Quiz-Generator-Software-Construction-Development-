"""
filename: student_dashboard.py
module: Student Dashboard UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 3 - Student modules
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QStackedWidget, QFrame, QTableWidget,
                              QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from QuizPlatform.dao.student_dao import StudentDAO
from QuizPlatform.dao.result_dao import ResultDAO
from QuizPlatform.ai_engine import AIEngine
from QuizPlatform.ui.exam_taking_ui import ExamTakingUI
from QuizPlatform.ui.result_ui import ResultUI
from QuizPlatform.ui.chatbot_ui import ChatbotUI
from QuizPlatform.exceptions import QuizDatabaseError, QuizAIError
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


class StudentDashboard(QWidget):
    """Main dashboard for the Student role"""

    def __init__(self, app, user):
        super().__init__()
        self.app = app
        self.user = user
        self.student_dao = StudentDAO()
        self.result_dao = ResultDAO()
        self.ai_engine = AIEngine()
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("background-color: #1A1A2E;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #16213E; border-bottom: 1px solid #2C2C54;")
        h_l = QVBoxLayout(header)
        h_l.setAlignment(Qt.AlignCenter)
        app_label = QLabel("🧠 QuizAI")
        app_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        app_label.setStyleSheet("color: white; background: transparent;")
        app_label.setAlignment(Qt.AlignCenter)
        h_l.addWidget(app_label)
        sb_layout.addWidget(header)

        user_frame = QFrame()
        user_frame.setStyleSheet("background-color: #16213E; border-bottom: 1px solid #2C2C54;")
        u_l = QVBoxLayout(user_frame)
        u_l.setContentsMargins(16, 12, 16, 12)
        avatar = QLabel("🎓")
        avatar.setFont(QFont("Segoe UI", 22))
        avatar.setAlignment(Qt.AlignCenter)
        u_l.addWidget(avatar)
        name_lbl = QLabel(self.user.get('full_name', 'Student'))
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_lbl.setStyleSheet("color: white;")
        name_lbl.setAlignment(Qt.AlignCenter)
        u_l.addWidget(name_lbl)
        role_lbl = QLabel("Student")
        role_lbl.setFont(QFont("Segoe UI", 9))
        role_lbl.setStyleSheet("color: #90CAF9;")
        role_lbl.setAlignment(Qt.AlignCenter)
        u_l.addWidget(role_lbl)
        sb_layout.addWidget(user_frame)

        nav_frame = QFrame()
        nav_frame.setStyleSheet("background-color: #1A1A2E;")
        nav_l = QVBoxLayout(nav_frame)
        nav_l.setContentsMargins(10, 16, 10, 0)
        nav_l.setSpacing(4)

        self.nav_buttons = []
        nav_items = [
            ("📝  My Exams", 0),
            ("📋  My Results", 1),
            ("💬  AI Chatbot", 2),
        ]
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_STYLE)
            btn.setFont(QFont("Segoe UI", 11))
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            nav_l.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_l.addStretch()
        sb_layout.addWidget(nav_frame, 1)

        logout_frame = QFrame()
        logout_frame.setStyleSheet("background-color: #16213E; border-top: 1px solid #2C2C54;")
        lo_l = QVBoxLayout(logout_frame)
        lo_l.setContentsMargins(10, 10, 10, 10)
        btn_logout = QPushButton("🚪  Logout")
        btn_logout.setObjectName("btn_logout")
        btn_logout.setStyleSheet(NAV_STYLE)
        btn_logout.setFont(QFont("Segoe UI", 11))
        btn_logout.clicked.connect(self.app.logout)
        lo_l.addWidget(btn_logout)
        sb_layout.addWidget(logout_frame)

        main_layout.addWidget(sidebar)

        # ── Content Stack ──
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #F9FAFB;")
        self.exams_page = self._build_exams_page()
        self.results_page = self._build_results_page()
        self.chatbot_page = ChatbotUI(self.user)
        self.stack.addWidget(self.exams_page)
        self.stack.addWidget(self.results_page)
        self.stack.addWidget(self.chatbot_page)
        main_layout.addWidget(self.stack)

        self._switch_page(0)

    def _build_exams_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        hdr = QHBoxLayout()
        title = QLabel("📝 My Assigned Exams")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        hdr.addWidget(title)
        hdr.addStretch()
        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.clicked.connect(self._load_exams)
        hdr.addWidget(btn_refresh)
        layout.addLayout(hdr)

        # Weak topics card
        self.weak_topics_card = QFrame()
        self.weak_topics_card.setStyleSheet("background: linear-gradient(135deg, #1A1A2E, #283593); border-radius: 12px;")
        wt_l = QVBoxLayout(self.weak_topics_card)
        wt_l.setContentsMargins(16, 12, 16, 12)
        wt_title = QLabel("🎯 AI Focus Areas")
        wt_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        wt_title.setStyleSheet("color: #90CAF9;")
        self.wt_content = QLabel("Take an exam to get personalized AI topic recommendations.")
        self.wt_content.setStyleSheet("color: white; font-size: 12px;")
        self.wt_content.setWordWrap(True)
        wt_l.addWidget(wt_title)
        wt_l.addWidget(self.wt_content)
        layout.addWidget(self.weak_topics_card)

        self.exams_table = QTableWidget()
        self.exams_table.setColumnCount(5)
        self.exams_table.setHorizontalHeaderLabels(["Title", "Subject", "Time (min)", "Marks", "Action"])
        self.exams_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.exams_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.exams_table.setAlternatingRowColors(True)
        self.exams_table.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 8px;")
        layout.addWidget(self.exams_table)

        self._load_exams()
        self._load_weak_topics()
        return page

    def _load_exams(self):
        try:
            exams = self.student_dao.get_assigned_exams(self.user['id'])
            self.exams_table.setRowCount(len(exams))
            for row, exam in enumerate(exams):
                self.exams_table.setItem(row, 0, QTableWidgetItem(exam['title']))
                self.exams_table.setItem(row, 1, QTableWidgetItem(exam['subject']))
                self.exams_table.setItem(row, 2, QTableWidgetItem(str(exam['time_limit'])))
                self.exams_table.setItem(row, 3, QTableWidgetItem(str(exam['total_marks'])))

                if exam['status'] == 'Completed':
                    done_lbl = QLabel("  ✅ Completed")
                    done_lbl.setStyleSheet("color: #2E7D32; font-weight: bold; padding: 4px;")
                    self.exams_table.setCellWidget(row, 4, done_lbl)
                else:
                    btn_start = QPushButton("▶ Start Exam")
                    btn_start.clicked.connect(lambda _, e=exam: self._start_exam(e))
                    self.exams_table.setCellWidget(row, 4, btn_start)
            self.exams_table.resizeRowsToContents()
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def _load_weak_topics(self):
        # We use a thread to avoid freezing the UI on login
        class TopicWorker(QThread):
            finished = pyqtSignal(list)
            def __init__(self, dao, ai, student_id):
                super().__init__()
                self.dao, self.ai, self.sid = dao, ai, student_id
            def run(self):
                try:
                    topics = self.dao.get_weak_topics(self.sid)
                    if topics:
                        weak = self.ai.detect_weak_topics(topics)
                        self.finished.emit(weak)
                except: pass

        self.topic_thread = TopicWorker(self.result_dao, self.ai_engine, self.user['id'])
        self.topic_thread.finished.connect(self._on_topics_found)
        self.topic_thread.start()

    def _on_topics_found(self, weak_list):
        if weak_list:
            self.wt_content.setText("📌 Focus on: " + " | ".join(weak_list))

    def _start_exam(self, exam):
        # Replace exams page with exam taking screen
        exam_screen = ExamTakingUI(self, self.user, exam)
        self.stack.insertWidget(3, exam_screen)
        self.stack.setCurrentIndex(3)

    def show_result(self, result_id):
        result_screen = ResultUI(self, result_id)
        self.stack.insertWidget(4, result_screen)
        self.stack.setCurrentIndex(4)
        self._load_exams()
        self._load_weak_topics()

    def go_home(self):
        self._switch_page(0)
        # Remove exam/result screens
        for idx in [4, 3]:
            if self.stack.count() > idx:
                w = self.stack.widget(idx)
                self.stack.removeWidget(w)

    def _build_results_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("📋 My Result History")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        layout.addWidget(title)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Exam Title", "Score %", "Date", "View"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 8px;")
        layout.addWidget(self.results_table)
        self._load_results()
        return page

    def _load_results(self):
        try:
            results = self.student_dao.get_student_results(self.user['id'])
            self.results_table.setRowCount(len(results))
            for row, res in enumerate(results):
                self.results_table.setItem(row, 0, QTableWidgetItem(res['exam_title']))
                pct_item = QTableWidgetItem(f"{res['percentage']:.1f}%")
                self.results_table.setItem(row, 1, pct_item)
                self.results_table.setItem(row, 2, QTableWidgetItem(str(res['date'])))
                btn_view = QPushButton("👁 View")
                btn_view.clicked.connect(lambda _, r=res: self.show_result(r['id']))
                self.results_table.setCellWidget(row, 3, btn_view)
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def _switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)
        if idx == 1:
            self._load_results()
