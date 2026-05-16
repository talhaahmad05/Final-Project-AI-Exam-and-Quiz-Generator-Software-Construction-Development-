"""
filename: student_dashboard.py
what was changed: Implemented AIWorker pattern for weak topic detection and added loading indicators.
author: Talha Ahmad
date: 2026-05-13
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QStackedWidget, QFrame, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.dao.student_dao import StudentDAO
from QuizPlatform.dao.result_dao import ResultDAO
from QuizPlatform.ai_engine import AIWorker, WEAK_TOPICS_PROMPT, RobustParser
from QuizPlatform.ui.exam_taking_ui import ExamTakingUI
from QuizPlatform.ui.result_ui import ResultUI
from QuizPlatform.ui.chatbot_ui import ChatbotUI
from QuizPlatform.exceptions import QuizDatabaseError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)

NAV_STYLE = """
    QPushButton {
        background-color: #2E7D32; color: #FF1744; text-align: left;
        padding: 14px 22px; border-radius: 8px; font-size: 15px; font-weight: bold;
        border: 1px solid #1B5E20;
    }
    QPushButton:hover { background-color: #388E3C; border: 1px solid #FF1744; }
    QPushButton:checked { background-color: #1B5E20; color: #FF8A80; border: 2px solid #FF1744; }
"""

class StudentDashboard(QWidget):
    """Main dashboard for the Student role"""

    def __init__(self, app, user):
        super().__init__()
        self.app = app
        self.user = user
        self.student_dao = StudentDAO()
        self.result_dao = ResultDAO()
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("background-color: #1A1A2E;")
        sb_layout = QVBoxLayout(sidebar)
        
        header = QLabel("🧠 QuizAI")
        header.setFont(QFont("Segoe UI", 15, QFont.Bold))
        header.setStyleSheet("color: white; padding: 20px;")
        header.setAlignment(Qt.AlignCenter)
        sb_layout.addWidget(header)

        self.nav_buttons = []
        for label, idx in [("📝 My Exams", 0), ("📋 My Results", 1), ("💬 AI Chatbot", 2)]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_STYLE)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()
        btn_logout = QPushButton("🚪 Logout")
        btn_logout.setStyleSheet(NAV_STYLE)
        btn_logout.clicked.connect(self.app.logout)
        sb_layout.addWidget(btn_logout)
        main_layout.addWidget(sidebar)

        # Content Stack
        self.stack = QStackedWidget()
        self.exams_page = self._build_exams_page()
        self.results_page = self._build_results_page()
        self.chatbot_page = ChatbotUI(self.user)
        self.stack.addWidget(self.exams_page)
        self.stack.addWidget(self.results_page)
        self.stack.addWidget(self.chatbot_page)
        main_layout.addWidget(self.stack)

        # Load initial data after all UI elements are initialized
        self._load_exams()
        self._load_results()
        self.load_ai_insights()

        self._switch_page(0)

    def _build_exams_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("📝 My Assigned Exams")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        # AI Focus Area Card
        self.weak_topics_card = QFrame()
        self.weak_topics_card.setStyleSheet("background-color: #E3F2FD; border-radius: 12px; border: 1px solid #1565C0;")
        wt_l = QVBoxLayout(self.weak_topics_card)
        
        self.wt_title = QLabel("🎯 AI Focus Areas")
        self.wt_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.wt_content = QLabel("Analyzing your performance...")
        self.wt_content.setWordWrap(True)
        
        # Loading Pattern (CHANGE 2 [2])
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        
        wt_l.addWidget(self.wt_title)
        wt_l.addWidget(self.wt_content)
        wt_l.addWidget(self.progress_bar)
        layout.addWidget(self.weak_topics_card)

        self.exams_table = QTableWidget()
        self.exams_table.setColumnCount(5)
        self.exams_table.setHorizontalHeaderLabels(["Title", "Subject", "Time", "Marks", "Action"])
        self.exams_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.exams_table)

        return page

    def show_loading(self):
        self.progress_bar.show()
        self.wt_content.setText("AI is thinking...")

    def hide_loading(self):
        self.progress_bar.hide()

    def load_ai_insights(self):
        """Triggers AI weak topic detection using AIWorker"""
        try:
            topics = self.result_dao.get_weak_topics(self.user['id'])
            if not topics:
                self.wt_content.setText("Take an exam to get AI recommendations.")
                return

            self.show_loading()
            prompt = WEAK_TOPICS_PROMPT.format(topics=", ".join(topics))
            
            self.worker = AIWorker(prompt=prompt)
            self.worker.result_ready.connect(self.on_ai_result)
            self.worker.error_occurred.connect(self.on_ai_error)
            self.worker.start()
        except Exception as e:
            logger.error(f"Failed to load AI insights: {e}")

    def on_ai_result(self, result):
        self.hide_loading()
        try:
            weak_list = RobustParser.extract_json(result)
            if weak_list and isinstance(weak_list, list):
                self.wt_content.setText("📌 Focus on: " + " | ".join(weak_list))
            else:
                self.wt_content.setText("Review your recent exam topics for improvement.")
        except:
            self.wt_content.setText("Review your recent exam topics for improvement.")

    def on_ai_error(self, error):
        self.hide_loading()
        self.wt_content.setText("AI insights currently unavailable.")

    def _load_exams(self):
        try:
            exams = self.student_dao.get_assigned_exams(self.user['id'])
            self.exams_table.setRowCount(len(exams))
            for row, exam in enumerate(exams):
                self.exams_table.setItem(row, 0, QTableWidgetItem(exam['title']))
                self.exams_table.setItem(row, 1, QTableWidgetItem(exam['subject']))
                self.exams_table.setItem(row, 2, QTableWidgetItem(str(exam['time_limit'])))
                self.exams_table.setItem(row, 3, QTableWidgetItem(str(exam['total_marks'])))
                
                status = exam.get('status', 'Pending')
                if status == 'Completed':
                    btn_start = QPushButton("Already Taken")
                    btn_start.setEnabled(False)
                    btn_start.setStyleSheet("background-color: #555555; color: #BBBBBB; border: 1px solid #333333;")
                else:
                    btn_start = QPushButton("▶ Start")
                    btn_start.clicked.connect(lambda _, e=exam: self._start_exam(e))
                
                self.exams_table.setCellWidget(row, 4, btn_start)
        except Exception as e:
            logger.error(f"Error loading exams: {e}")

    def _start_exam(self, exam):
        # Final safety check
        if exam.get('status') == 'Completed':
            QMessageBox.warning(self, "Exam Already Taken", "You have already completed this exam and cannot retake it.")
            return

        screen = ExamTakingUI(self, self.user, exam)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)

    def show_result(self, result_id):
        screen = ResultUI(self, result_id)
        self.stack.addWidget(screen)
        self.stack.setCurrentWidget(screen)
        self._load_results()
        self.load_ai_insights()

    def go_home(self):
        self._switch_page(0)

    def _build_results_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("📋 My Exam History")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Exam Title", "Percentage", "Date", "Action"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.setStyleSheet("background-color: white; border-radius: 8px;")
        layout.addWidget(self.results_table)
        return page

    def _load_results(self):
        """Fetches and displays the student's exam results"""
        try:
            results = self.student_dao.get_student_results(self.user['id'])
            self.results_table.setRowCount(len(results))
            for row, res in enumerate(results):
                self.results_table.setItem(row, 0, QTableWidgetItem(res['exam_title']))
                
                pct_item = QTableWidgetItem(f"{res['percentage']:.1f}%")
                if res['percentage'] >= 50:
                    pct_item.setForeground(__import__('PyQt5.QtGui', fromlist=['QColor']).QColor("#2E7D32"))
                else:
                    pct_item.setForeground(__import__('PyQt5.QtGui', fromlist=['QColor']).QColor("#C62828"))
                
                self.results_table.setItem(row, 1, pct_item)
                self.results_table.setItem(row, 2, QTableWidgetItem(res['date']))
                
                btn_view = QPushButton("👁 View")
                btn_view.setFixedWidth(80)
                btn_view.clicked.connect(lambda _, r_id=res['id']: self.show_result(r_id))
                self.results_table.setCellWidget(row, 3, btn_view)
            
            self.results_table.resizeRowsToContents()
        except Exception as e:
            logger.error(f"Error loading results: {e}")

    def _switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        if idx == 1: # Results page
            self._load_results()
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)
