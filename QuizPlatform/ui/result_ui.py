"""
filename: result_ui.py
changes made: Added local/online dual AI toggles and interactive AI Insights Card for dynamic feedback and weak topic analysis.
author: Talha Ahmad
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QFrame, QScrollArea, QSizePolicy,
                               QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from QuizPlatform.dao.result_dao import ResultDAO
from QuizPlatform.exceptions import QuizDatabaseError
from QuizPlatform.utils.logger import get_logger
from QuizPlatform.ai_engine import (
    AIWorkerSmart,
    FEEDBACK_PROMPT,
    WEAK_TOPICS_PROMPT
)

logger = get_logger(__name__)


class ResultUI(QWidget):
    """Result screen showing score, AI feedback, and question review"""

    def __init__(self, dashboard, result_id):
        super().__init__()
        self.dashboard = dashboard
        self.result_id = result_id
        self.result_dao = ResultDAO()
        self.result = None
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
            self.result = result

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

            # ── Dynamic AI Insights Card (Interactive Toggles) ──
            insights_card = QFrame()
            insights_card.setStyleSheet("background-color: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0; padding: 12px;")
            ic_layout = QVBoxLayout(insights_card)
            
            ic_title = QLabel("🤖 AI Insights Dispatcher")
            ic_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
            ic_title.setStyleSheet("color: #1E293B;")
            ic_layout.addWidget(ic_title)
            
            # AI Engine selection radio buttons
            self.rb_result_local  = QRadioButton("🖥️ Local AI")
            self.rb_result_online = QRadioButton("⚡ Online AI")
            self.rb_result_local.setChecked(True)
            self.result_mode_group = QButtonGroup(self)
            self.result_mode_group.addButton(self.rb_result_local)
            self.result_mode_group.addButton(self.rb_result_online)
            
            rb_style = """
                QRadioButton {
                    font-size: 12px;
                    padding: 5px 14px;
                    border-radius: 10px;
                    background: #F1F5F9;
                    color: #475569;
                    font-weight: 500;
                }
                QRadioButton::indicator {
                    width: 0px; height: 0px;
                }
                QRadioButton:checked {
                    background: #1F4E79;
                    color: white;
                    font-weight: bold;
                }
                QRadioButton:hover {
                    background: #E2E8F0;
                }
            """
            self.rb_result_local.setStyleSheet(rb_style)
            self.rb_result_online.setStyleSheet(rb_style)
            
            selector_layout = QHBoxLayout()
            selector_layout.addWidget(QLabel("AI Engine:"))
            selector_layout.addWidget(self.rb_result_local)
            selector_layout.addWidget(self.rb_result_online)
            selector_layout.addStretch()
            ic_layout.addLayout(selector_layout)
            
            # Action buttons
            btn_layout = QHBoxLayout()
            self.btn_feedback = QPushButton("🤖 Get Detailed Feedback")
            self.btn_feedback.setStyleSheet("background-color: #1E293B; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
            self.btn_feedback.clicked.connect(self.get_feedback)
            btn_layout.addWidget(self.btn_feedback)
            
            self.btn_weak_topics = QPushButton("🎯 Analyze Weak Topics")
            self.btn_weak_topics.setStyleSheet("background-color: #0F766E; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
            self.btn_weak_topics.clicked.connect(self.get_weak_topics)
            btn_layout.addWidget(self.btn_weak_topics)
            ic_layout.addLayout(btn_layout)
            
            # Display Area
            self.ai_insights_display = QLabel("Click the buttons above to trigger live, dynamic AI analysis.")
            self.ai_insights_display.setWordWrap(True)
            self.ai_insights_display.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; color: #475569; font-size: 12px; font-style: italic;")
            self.ai_insights_display.setMinimumHeight(80)
            ic_layout.addWidget(self.ai_insights_display)
            
            layout.addWidget(insights_card)

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

    def get_feedback(self):
        if not self.result:
            return
        
        self.btn_feedback.setEnabled(False)
        self.btn_feedback.setText("Thinking...")
        self.ai_insights_display.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; color: #475569; font-size: 12px; font-style: italic;")
        self.ai_insights_display.setText("AI is analyzing your results for encouraging feedback...")
        
        # Wrong questions calculation
        wrong_questions = []
        for ans in self.result.get('answers', []):
            is_correct = str(ans['student_answer']).strip().lower() == ans['correct_answer'].strip().lower()
            if ans['type'] == 'Short Answer':
                is_correct = float(ans['marks_awarded'] or 0) > 0
            if not is_correct:
                wrong_questions.append(str(ans['question_text'])[:50])
                
        prompt = FEEDBACK_PROMPT.format(
            score=f"{self.result['percentage']:.1f}",
            subject=self.result.get('exam_title', 'General'),
            wrong_questions=", ".join(wrong_questions) if wrong_questions else "None"
        )
        
        mode = "online" if self.rb_result_online.isChecked() else "local"
        
        self.worker = AIWorkerSmart(prompt=prompt, mode=mode)
        self.worker.result_ready.connect(self.on_feedback_received)
        self.worker.error_occurred.connect(self.on_ai_error)
        self.worker.start()

    def get_weak_topics(self):
        if not self.result:
            return
            
        self.btn_weak_topics.setEnabled(False)
        self.btn_weak_topics.setText("Analyzing...")
        self.ai_insights_display.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; color: #475569; font-size: 12px; font-style: italic;")
        self.ai_insights_display.setText("AI is scanning your incorrect responses to isolate weak areas...")
        
        # Collect incorrect topics
        wrong_topics = []
        for ans in self.result.get('answers', []):
            is_correct = str(ans['student_answer']).strip().lower() == ans['correct_answer'].strip().lower()
            if ans['type'] == 'Short Answer':
                is_correct = float(ans['marks_awarded'] or 0) > 0
            if not is_correct:
                topic_val = ans.get('topic', self.result.get('exam_title', 'General'))
                if topic_val and topic_val not in wrong_topics:
                    wrong_topics.append(topic_val)
                    
        prompt = WEAK_TOPICS_PROMPT.format(topics=", ".join(wrong_topics) if wrong_topics else "None")
        
        mode = "online" if self.rb_result_online.isChecked() else "local"
        
        self.worker = AIWorkerSmart(prompt=prompt, mode=mode)
        self.worker.result_ready.connect(self.on_weak_topics_received)
        self.worker.error_occurred.connect(self.on_ai_error)
        self.worker.start()

    def on_feedback_received(self, result):
        self.btn_feedback.setEnabled(True)
        self.btn_feedback.setText("🤖 Get AI Feedback")
        self.ai_insights_display.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; color: #1E293B; font-size: 13px; font-style: normal; font-weight: 500;")
        self.ai_insights_display.setText(result)

    def on_weak_topics_received(self, result):
        self.btn_weak_topics.setEnabled(True)
        self.btn_weak_topics.setText("🎯 Analyze Weak Topics")
        self.ai_insights_display.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; color: #1E293B; font-size: 13px; font-style: normal; font-weight: 500;")
        
        # Try parsing JSON array
        try:
            from QuizPlatform.ai_engine import RobustParser
            weak_list = RobustParser.extract_json(result)
            if weak_list and isinstance(weak_list, list):
                bullet_list = "\n".join(f"• {topic}" for topic in weak_list)
                self.ai_insights_display.setText(f"🎯 AI Suggested Weak Topics to Focus On:\n\n{bullet_list}")
            else:
                self.ai_insights_display.setText(result)
        except:
            self.ai_insights_display.setText(result)

    def on_ai_error(self, error):
        self.btn_feedback.setEnabled(True)
        self.btn_feedback.setText("🤖 Get AI Feedback")
        self.btn_weak_topics.setEnabled(True)
        self.btn_weak_topics.setText("🎯 Analyze Weak Topics")
        self.ai_insights_display.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; color: #C62828; font-size: 12px; font-style: italic;")
        self.ai_insights_display.setText(f"⚠️ AI Engine Error: {error}")
