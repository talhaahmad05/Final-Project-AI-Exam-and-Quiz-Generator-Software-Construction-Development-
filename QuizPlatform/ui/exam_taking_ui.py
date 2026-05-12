"""
filename: exam_taking_ui.py
module: Exam Taking UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 3 - Exam Engine
"""

import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QButtonGroup, QRadioButton, QTextEdit,
                              QMessageBox, QFrame, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont

from QuizPlatform.dao.exam_dao import ExamDAO
from QuizPlatform.dao.result_dao import ResultDAO
from QuizPlatform.ai_engine import AIEngine
from QuizPlatform.exceptions import QuizDatabaseError, QuizAIError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)


class SubmissionWorker(QThread):
    finished = pyqtSignal(int, str) # result_id, error_msg
    progress = pyqtSignal(str)

    def __init__(self, exam, student_answers, user, elapsed_seconds):
        super().__init__()
        self.exam = exam
        self.student_answers = student_answers
        self.user = user
        self.elapsed_seconds = elapsed_seconds

    def run(self):
        try:
            self.progress.emit("Grading started...")
            import traceback
            from QuizPlatform.ai_engine import AIEngine
            from QuizPlatform.dao.result_dao import ResultDAO
            
            ai_engine = AIEngine()
            result_dao = ResultDAO()

            total_marks = self.exam['total_marks']
            # Safely get questions
            questions = self.exam.get('questions', [])
            if not questions:
                # If questions missing, try to re-load from DB to be safe
                from QuizPlatform.dao.question_dao import QuestionDAO
                q_dao = QuestionDAO()
                questions = q_dao.get_questions_by_exam(self.exam['id'])

            per_question = total_marks / max(len(questions), 1)
            
            scored = 0
            wrong_questions = []
            answers_to_save = []

            for i, q in enumerate(questions):
                self.progress.emit(f"Grading question {i+1} of {len(questions)}...")
                student_ans = self.student_answers.get(q['id'], '')
                marks = 0
                if q['type'] in ('MCQ', 'True/False'):
                    if str(student_ans).strip().lower() == str(q['correct_answer']).strip().lower():
                        marks = per_question
                    else:
                        wrong_questions.append(q['question_text'][:50])
                elif q['type'] == 'Short Answer':
                    try:
                        marks = ai_engine.grade_short_answer(
                            q['question_text'], q['correct_answer'], student_ans, per_question
                        )
                    except:
                        marks = 0
                    if marks < per_question:
                        wrong_questions.append(q['question_text'][:50])
                
                scored += marks
                answers_to_save.append({'question_id': q['id'], 'answer': student_ans, 'marks': marks})

            percentage = (scored / total_marks * 100) if total_marks > 0 else 0
            
            self.progress.emit("Generating feedback...")
            feedback = ""
            try:
                feedback = ai_engine.get_result_feedback(
                    f"{percentage:.1f}", self.exam['subject'], wrong_questions
                )
            except:
                feedback = "Submission complete. Great effort!"

            self.progress.emit("Saving results...")
            result_id = result_dao.save_result(
                self.exam['id'], self.user['id'], scored, percentage,
                self.elapsed_seconds, feedback, answers_to_save
            )
            self.finished.emit(result_id, "")
        except Exception as e:
            traceback.print_exc()
            err_msg = str(e) or "An unknown error occurred during submission."
            self.finished.emit(-1, err_msg)

class ExamTakingUI(QWidget):
    """Live exam taking screen with timer, navigation, and hint system"""

    def __init__(self, dashboard, user, exam):
        super().__init__()
        self.dashboard = dashboard
        self.user = user
        self.exam = exam
        self.exam_dao = ExamDAO()
        self.result_dao = ResultDAO()
        self.ai_engine = AIEngine()

        self.questions = []
        self.current_idx = 0
        self.student_answers = {}  # question_id -> answer text
        self.flagged = set()
        self.elapsed_seconds = 0
        self.time_limit_seconds = exam['time_limit'] * 60

        self._load_questions()
        self._build_ui()
        self._show_question(0)
        self._start_timer()

    def _load_questions(self):
        try:
            self.questions = self.exam_dao.get_exam_questions(self.exam['id'])
            if self.exam.get('shuffle'):
                random.shuffle(self.questions)
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "Error", f"Failed to load questions:\n{e}")
            self.questions = []

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Left: Question Panel ──
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #F9FAFB;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 20, 30, 20)
        left_layout.setSpacing(16)

        # Top bar: title + timer
        top_bar = QHBoxLayout()
        exam_title_lbl = QLabel(f"📝 {self.exam['title']}")
        exam_title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        exam_title_lbl.setStyleSheet("color: #1A1A2E;")
        top_bar.addWidget(exam_title_lbl)
        top_bar.addStretch()
        self.timer_label = QLabel("⏱ 00:00")
        self.timer_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.timer_label.setStyleSheet("color: #1565C0; background: #E3F2FD; border-radius: 6px; padding: 4px 10px;")
        top_bar.addWidget(self.timer_label)
        left_layout.addLayout(top_bar)

        # Progress bar (question counter)
        self.progress_lbl = QLabel("Question 1 / 1")
        self.progress_lbl.setFont(QFont("Segoe UI", 10))
        self.progress_lbl.setStyleSheet("color: #666;")
        left_layout.addWidget(self.progress_lbl)

        # Question card
        q_card = QFrame()
        q_card.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E0E0E0;")
        q_card_layout = QVBoxLayout(q_card)
        q_card_layout.setContentsMargins(24, 20, 24, 20)
        q_card_layout.setSpacing(12)

        self.q_num_lbl = QLabel("Q1.")
        self.q_num_lbl.setFont(QFont("Segoe UI", 11))
        self.q_num_lbl.setStyleSheet("color: #1565C0; font-weight: bold;")
        q_card_layout.addWidget(self.q_num_lbl)

        self.question_lbl = QLabel("")
        self.question_lbl.setFont(QFont("Segoe UI", 13))
        self.question_lbl.setStyleSheet("color: #1A1A2E;")
        self.question_lbl.setWordWrap(True)
        q_card_layout.addWidget(self.question_lbl)

        # MCQ/TF Options frame
        self.options_frame = QFrame()
        self.options_layout = QVBoxLayout(self.options_frame)
        self.options_layout.setSpacing(8)
        self.option_group = QButtonGroup(self)
        q_card_layout.addWidget(self.options_frame)

        # Short answer text area
        self.short_answer_input = QTextEdit()
        self.short_answer_input.setPlaceholderText("Type your answer here...")
        self.short_answer_input.setFixedHeight(100)
        self.short_answer_input.hide()
        q_card_layout.addWidget(self.short_answer_input)

        left_layout.addWidget(q_card)

        # Hint area
        self.hint_frame = QFrame()
        self.hint_frame.setStyleSheet("background-color: #FFF9C4; border-radius: 8px; border: 1px solid #F9A825;")
        hint_layout = QHBoxLayout(self.hint_frame)
        self.hint_lbl = QLabel("")
        self.hint_lbl.setWordWrap(True)
        self.hint_lbl.setStyleSheet("color: #E65100; padding: 4px;")
        hint_layout.addWidget(self.hint_lbl)
        self.hint_frame.hide()
        left_layout.addWidget(self.hint_frame)

        # Navigation buttons
        nav_row = QHBoxLayout()
        nav_row.setSpacing(15) # Add space between buttons
        
        self.btn_prev = QPushButton("◀ Previous")
        self.btn_prev.setFixedWidth(110)
        self.btn_prev.setFixedHeight(36)
        self.btn_prev.clicked.connect(self._prev_question)
        nav_row.addWidget(self.btn_prev)

        self.btn_flag = QPushButton("🚩 Flag Question")
        self.btn_flag.setFixedWidth(130)
        self.btn_flag.setFixedHeight(36)
        self.btn_flag.clicked.connect(self._toggle_flag)
        nav_row.addWidget(self.btn_flag)

        if self.exam.get('hints'):
            self.btn_hint = QPushButton("💡 Hint")
            self.btn_hint.setFixedWidth(100)
            self.btn_hint.setFixedHeight(36)
            self.btn_hint.clicked.connect(self._get_hint)
            nav_row.addWidget(self.btn_hint)

        nav_row.addStretch()
        self.btn_next = QPushButton("Next Question ▶")
        self.btn_next.setFixedWidth(140)
        self.btn_next.setFixedHeight(38)
        self.btn_next.clicked.connect(self._next_question)
        nav_row.addWidget(self.btn_next)
        left_layout.addLayout(nav_row)

        left_layout.addStretch()

        btn_submit = QPushButton("✅ Submit Exam")
        btn_submit.setFixedHeight(44)
        btn_submit.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn_submit.clicked.connect(self._confirm_submit)
        left_layout.addWidget(btn_submit)

        main_layout.addWidget(left_panel, 3)

        # ── Right: Question Navigator ──
        right_panel = QFrame()
        right_panel.setFixedWidth(180)
        right_panel.setStyleSheet("background-color: #1A1A2E;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 20, 12, 20)
        right_layout.setSpacing(8)

        nav_title = QLabel("Questions")
        nav_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        nav_title.setStyleSheet("color: white;")
        nav_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(nav_title)

        # Grid of question buttons
        self.q_nav_buttons = []
        grid = QWidget()
        from PyQt5.QtWidgets import QGridLayout
        grid_layout = QGridLayout(grid)
        grid_layout.setSpacing(6)
        for i in range(len(self.questions)):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("background-color: #2C2C54; color: white; border-radius: 6px;")
            btn.clicked.connect(lambda _, idx=i: self._show_question(idx))
            grid_layout.addWidget(btn, i // 3, i % 3)
            self.q_nav_buttons.append(btn)
        right_layout.addWidget(grid)

        legend = QLabel("🟦 Current\n🟩 Answered\n🟧 Flagged\n⬜ Unanswered")
        legend.setFont(QFont("Segoe UI", 8))
        legend.setStyleSheet("color: #90CAF9; margin-top: 8px;")
        right_layout.addWidget(legend)
        right_layout.addStretch()

        main_layout.addWidget(right_panel, 0)

    def _start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _tick(self):
        self.elapsed_seconds += 1
        remaining = self.time_limit_seconds - self.elapsed_seconds
        if remaining <= 0:
            self.timer.stop()
            QMessageBox.warning(self, "Time Up!", "Time is up! Submitting your exam now.")
            self._submit_exam()
            return
        mins, secs = divmod(remaining, 60)
        self.timer_label.setText(f"⏱ {mins:02}:{secs:02}")
        if remaining <= 60:
            self.timer_label.setStyleSheet("color: #C62828; background: #FFEBEE; border-radius: 6px; padding: 4px 10px;")

    def _show_question(self, idx):
        self._save_current_answer()
        self.hint_frame.hide()
        self.current_idx = idx
        if not self.questions:
            return

        q = self.questions[idx]
        self.q_num_lbl.setText(f"Q{idx + 1}.")
        self.question_lbl.setText(q['question_text'])
        self.progress_lbl.setText(f"Question {idx + 1} / {len(self.questions)}")

        # Clear options
        for rb in self.option_group.buttons():
            self.option_group.removeButton(rb)
        for i in reversed(range(self.options_layout.count())):
            widget = self.options_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if q['type'] == 'Short Answer':
            self.options_frame.hide()
            self.short_answer_input.show()
            self.short_answer_input.setPlainText(self.student_answers.get(q['id'], ''))
        else:
            self.short_answer_input.hide()
            self.options_frame.show()
            options = q['options'] if q['type'] == 'MCQ' else ['True', 'False']
            saved_answer = self.student_answers.get(q['id'], '')
            for opt in options:
                rb = QRadioButton(opt)
                rb.setFont(QFont("Segoe UI", 11))
                rb.setStyleSheet("""
                    QRadioButton { color: #1A1A2E; padding: 8px; border-radius: 6px; }
                    QRadioButton:hover { background-color: #E3F2FD; }
                    QRadioButton::checked { background-color: #BBDEFB; }
                """)
                if opt == saved_answer:
                    rb.setChecked(True)
                self.option_group.addButton(rb)
                self.options_layout.addWidget(rb)

        self._update_nav_buttons()

    def _save_current_answer(self):
        if not self.questions or self.current_idx >= len(self.questions):
            return
        q = self.questions[self.current_idx]
        if q['type'] == 'Short Answer':
            self.student_answers[q['id']] = self.short_answer_input.toPlainText().strip()
        else:
            for btn in self.option_group.buttons():
                if btn.isChecked():
                    self.student_answers[q['id']] = btn.text()
                    break

    def _update_nav_buttons(self):
        # Enable/Disable Prev/Next based on index
        self.btn_prev.setEnabled(self.current_idx > 0)
        self.btn_next.setEnabled(self.current_idx < len(self.questions) - 1)

        for i, btn in enumerate(self.q_nav_buttons):
            q_id = self.questions[i]['id']
            if i == self.current_idx:
                btn.setStyleSheet("border: 2px solid #FF0000;")
            elif q_id in self.flagged:
                btn.setStyleSheet("border: 2px solid #FFA500;")
            elif q_id in self.student_answers:
                btn.setStyleSheet("border: 2px solid #00FF00;")
            else:
                btn.setStyleSheet("border: none;")

    def _prev_question(self):
        if self.current_idx > 0:
            self._show_question(self.current_idx - 1)

    def _next_question(self):
        if self.current_idx < len(self.questions) - 1:
            self._show_question(self.current_idx + 1)

    def _toggle_flag(self):
        q_id = self.questions[self.current_idx]['id']
        if q_id in self.flagged:
            self.flagged.remove(q_id)
            self.btn_flag.setStyleSheet("background-color: #FF9800; color: white; border-radius: 6px;")
        else:
            self.flagged.add(q_id)
            self.btn_flag.setStyleSheet("background-color: #C62828; color: white; border-radius: 6px;")
        self._update_nav_buttons()

    def _get_hint(self):
        q = self.questions[self.current_idx]
        try:
            self.btn_hint.setEnabled(False)
            self.btn_hint.setText("⏳ Getting hint...")
            hint = self.ai_engine.get_hint(q['question_text'], q['correct_answer'])
            self.hint_lbl.setText(f"💡 Hint: {hint}")
            self.hint_frame.show()
            self.result_dao.log_hint_usage(q['id'], self.user['id'])
        except QuizAIError as e:
            QMessageBox.warning(self, "AI Unavailable", str(e))
        finally:
            self.btn_hint.setEnabled(True)
            self.btn_hint.setText("💡 Get Hint")

    def _confirm_submit(self):
        self._save_current_answer()
        unanswered = len(self.questions) - len(self.student_answers)
        flagged = len(self.flagged)
        msg = f"Submit exam?\n\nAnswered: {len(self.student_answers)}/{len(self.questions)}"
        if unanswered > 0:
            msg += f"\n⚠ Unanswered: {unanswered}"
        if flagged > 0:
            msg += f"\n🚩 Flagged for review: {flagged}"
        reply = QMessageBox.question(self, "Confirm Submission", msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._submit_exam()

    def _submit_exam(self):
        self.timer.stop()
        self._save_current_answer()
        
        # Prepare data for worker
        self.exam['questions'] = self.questions
        
        from PyQt5.QtWidgets import QProgressDialog
        self.progress_dlg = QProgressDialog("Submitting Exam...", "Cancel", 0, 0, self)
        self.progress_dlg.setWindowModality(Qt.WindowModal)
        self.progress_dlg.setMinimumDuration(0)
        self.progress_dlg.setCancelButton(None) # Disable cancel
        self.progress_dlg.show()

        self.worker = SubmissionWorker(self.exam, self.student_answers, self.user, self.elapsed_seconds)
        self.worker.progress.connect(lambda msg: self.progress_dlg.setLabelText(msg))
        self.worker.finished.connect(self._on_submission_finished)
        self.worker.start()

    def _on_submission_finished(self, result_id, error_msg):
        self.progress_dlg.close()
        if result_id > 0:
            self.dashboard.show_result(result_id)
        else:
            QMessageBox.critical(self, "Submission Error", f"Failed to submit results: {error_msg}")
