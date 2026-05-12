"""
filename: result_ui.py
module: Result & Review UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 3 - Results & Grading
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem,
                              QHeaderView, QFrame, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from QuizPlatform.dao.result_dao import ResultDAO
from QuizPlatform.exceptions import QuizDatabaseError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)


class ResultUI(QWidget):
    """Result screen showing score, AI feedback, and question review"""

    def __init__(self, dashboard, result_id):
        super().__init__()
        self.dashboard = dashboard
        self.result_id = result_id
        self.result_dao = ResultDAO()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        # Back button
        btn_back = QPushButton("◀ Back to Dashboard")
        btn_back.setFixedWidth(200)
        btn_back.clicked.connect(self.dashboard.go_home)
        layout.addWidget(btn_back)

        try:
            result = self.result_dao.get_result_by_id(self.result_id)
            if not result:
                layout.addWidget(QLabel("Result not found."))
                return

            # ── Score Card ──
            score_card = QFrame()
            score_card.setStyleSheet("""
                QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                         stop:0 #1A1A2E, stop:1 #283593);
                         border-radius: 16px; }
            """)
            sc_layout = QVBoxLayout(score_card)
            sc_layout.setContentsMargins(30, 24, 30, 24)
            sc_layout.setAlignment(Qt.AlignCenter)

            exam_lbl = QLabel(result['exam_title'])
            exam_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
            exam_lbl.setStyleSheet("color: white; background: transparent;")
            exam_lbl.setAlignment(Qt.AlignCenter)
            sc_layout.addWidget(exam_lbl)

            pct = result['percentage']
            score_lbl = QLabel(f"{pct:.1f}%")
            score_lbl.setFont(QFont("Segoe UI", 52, QFont.Bold))
            score_lbl.setStyleSheet(f"color: {'#69F0AE' if pct >= 50 else '#FF5252'}; background: transparent;")
            score_lbl.setAlignment(Qt.AlignCenter)
            sc_layout.addWidget(score_lbl)

            pass_fail = "✅ PASSED" if pct >= 50 else "❌ FAILED"
            pf_lbl = QLabel(pass_fail)
            pf_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
            pf_lbl.setStyleSheet(f"color: {'#69F0AE' if pct >= 50 else '#FF5252'}; background: transparent;")
            pf_lbl.setAlignment(Qt.AlignCenter)
            sc_layout.addWidget(pf_lbl)

            mins, secs = divmod(result['time_taken'], 60)
            details_lbl = QLabel(f"Score: {result['score']:.1f} marks   |   Time: {mins}m {secs}s   |   Student: {result['student_name']}")
            details_lbl.setFont(QFont("Segoe UI", 10))
            details_lbl.setStyleSheet("color: #90CAF9; background: transparent;")
            details_lbl.setAlignment(Qt.AlignCenter)
            sc_layout.addWidget(details_lbl)
            layout.addWidget(score_card)

            # ── AI Feedback ──
            if result.get('feedback'):
                feedback_frame = QFrame()
                feedback_frame.setStyleSheet("""
                    QFrame { background-color: #E8F5E9; border-radius: 10px;
                             border-left: 4px solid #2E7D32; }
                """)
                fb_layout = QVBoxLayout(feedback_frame)
                fb_layout.setContentsMargins(16, 12, 16, 12)
                fb_title = QLabel("🤖 AI Feedback")
                fb_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
                fb_title.setStyleSheet("color: #1B5E20;")
                fb_content = QLabel(result['feedback'])
                fb_content.setWordWrap(True)
                fb_content.setStyleSheet("color: #2E7D32; font-size: 12px;")
                fb_layout.addWidget(fb_title)
                fb_layout.addWidget(fb_content)
                layout.addWidget(feedback_frame)

            # ── Answer Review Table ──
            review_title = QLabel("📋 Answer Review")
            review_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
            review_title.setStyleSheet("color: #1A1A2E;")
            layout.addWidget(review_title)

            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["#", "Question", "Your Answer", "Correct Answer", "Marks"])
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 8px;")

            answers = result.get('answers', [])
            table.setRowCount(len(answers))
            for row, ans in enumerate(answers):
                table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                table.setItem(row, 1, QTableWidgetItem(ans['question_text'][:80]))

                student_ans_item = QTableWidgetItem(str(ans['student_answer'] or "—"))
                correct_ans_item = QTableWidgetItem(ans['correct_answer'])
                marks_val = float(ans['marks_awarded'] or 0)
                marks_item = QTableWidgetItem(f"{marks_val:.1f}")

                is_correct = str(ans['student_answer']).strip().lower() == ans['correct_answer'].strip().lower()
                if ans['type'] == 'Short Answer':
                    is_correct = marks_val > 0

                if is_correct:
                    for item in [student_ans_item, marks_item]:
                        item.setForeground(QColor("#2E7D32"))
                else:
                    student_ans_item.setForeground(QColor("#C62828"))

                table.setItem(row, 2, student_ans_item)
                table.setItem(row, 3, correct_ans_item)
                table.setItem(row, 4, marks_item)

            table.resizeRowsToContents()
            layout.addWidget(table)

        except QuizDatabaseError as e:
            layout.addWidget(QLabel(f"Error loading results: {e}"))
