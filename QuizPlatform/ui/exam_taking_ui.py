"""
filename: exam_taking_ui.py
what was changed: Implemented AIWorker for hints, updated SubmissionWorker to use new ask_ai, and added hint UI logic.
author: Talha Ahmad
date: 2026-05-13
"""

import random
import re
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QButtonGroup, QRadioButton, QTextEdit,
                               QMessageBox, QFrame, QScrollArea, QSizePolicy, QDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont

from QuizPlatform.dao.exam_dao import ExamDAO
from QuizPlatform.dao.result_dao import ResultDAO
from QuizPlatform.ai_engine import ask_ai, AIWorker, HINT_PROMPT, GRADING_PROMPT, FEEDBACK_PROMPT
from QuizPlatform.exceptions import QuizDatabaseError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)

class SubmissionWorker(QThread):
    """Background thread for grading and submitting exam results"""
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
            result_dao = ResultDAO()

            total_marks = self.exam['total_marks']
            questions = self.exam.get('questions', [])
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
                        q_text = q.get('question_text', 'Unknown Question')
                        wrong_questions.append(str(q_text)[:50])
                elif q['type'] == 'Short Answer':
                    prompt = GRADING_PROMPT.format(
                        question=q['question_text'],
                        model_answer=q['correct_answer'],
                        student_answer=student_ans,
                        max_marks=per_question
                    )
                    response = ask_ai(prompt)
                    if not response or response.startswith("ERROR:"):
                        logger.warning(f"AI Grading failed: {response}")
                        marks = 0
                    else:
                        try:
                            match = re.search(r'\d+', response)
                            marks = int(match.group()) if match else 0
                            if marks > per_question: marks = per_question
                        except:
                            marks = 0
                    if marks < per_question:
                        q_text = q.get('question_text', 'Unknown Question')
                        wrong_questions.append(str(q_text)[:50])
                
                scored += marks
                answers_to_save.append({'question_id': q['id'], 'answer': student_ans, 'marks': marks})

            percentage = (scored / total_marks * 100) if total_marks > 0 else 0
            
            self.progress.emit("Generating feedback...")
            feedback = ""
            try:
                f_prompt = FEEDBACK_PROMPT.format(
                    score=f"{percentage:.1f}", 
                    subject=self.exam['subject'], 
                    wrong_questions=", ".join(wrong_questions) if wrong_questions else "None"
                )
                response = ask_ai(f_prompt)
                if response and not response.startswith("ERROR:"):
                    feedback = response
                else:
                    feedback = "Submission complete. Great effort!"
            except:
                feedback = "Submission complete. Great effort!"

            self.progress.emit("Saving results...")
            result_id = result_dao.save_result(
                self.exam['id'], self.user['id'], scored, percentage,
                self.elapsed_seconds, feedback, answers_to_save
            )
            self.finished.emit(result_id, "")
        except Exception as e:
            logger.error(f"Submission failed: {e}")
            self.finished.emit(-1, str(e))

class ExamTakingUI(QWidget):
    """Live exam taking screen with timer, navigation, and hint system"""

    def __init__(self, dashboard, user, exam):
        super().__init__()
        self.dashboard = dashboard
        self.user = user
        self.exam = exam
        self.exam_dao = ExamDAO()
        self.result_dao = ResultDAO()

        self.questions = []
        self.current_idx = 0
        self.student_answers = {}
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

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #F9FAFB;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 20, 30, 20)
        left_layout.setSpacing(16)

        top_bar = QHBoxLayout()
        exam_title_lbl = QLabel(f"📝 {self.exam['title']}")
        exam_title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        top_bar.addWidget(exam_title_lbl)
        top_bar.addStretch()
        self.timer_label = QLabel("⏱ 00:00")
        self.timer_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.timer_label.setStyleSheet("color: #1565C0; background: #E3F2FD; border-radius: 6px; padding: 4px 10px;")
        top_bar.addWidget(self.timer_label)
        left_layout.addLayout(top_bar)

        self.progress_lbl = QLabel("Question 1 / 1")
        self.progress_lbl.setFont(QFont("Segoe UI", 10))
        left_layout.addWidget(self.progress_lbl)

        q_card = QFrame()
        q_card.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E0E0E0;")
        q_card_layout = QVBoxLayout(q_card)
        q_card_layout.setContentsMargins(24, 20, 24, 20)

        self.q_num_lbl = QLabel("Q1.")
        self.q_num_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.q_num_lbl.setStyleSheet("color: #1565C0;")
        q_card_layout.addWidget(self.q_num_lbl)

        self.question_lbl = QLabel("")
        self.question_lbl.setFont(QFont("Segoe UI", 13))
        self.question_lbl.setWordWrap(True)
        q_card_layout.addWidget(self.question_lbl)

        self.options_frame = QFrame()
        self.options_layout = QVBoxLayout(self.options_frame)
        self.option_group = QButtonGroup(self)
        q_card_layout.addWidget(self.options_frame)

        self.short_answer_input = QTextEdit()
        self.short_answer_input.setPlaceholderText("Type your answer here...")
        self.short_answer_input.setFixedHeight(100)
        self.short_answer_input.hide()
        q_card_layout.addWidget(self.short_answer_input)

        left_layout.addWidget(q_card)

        # Hint error label (CHANGE 4 [3])
        self.hint_error_lbl = QLabel("")
        self.hint_error_lbl.setStyleSheet("color: red; font-size: 10px;")
        self.hint_error_lbl.hide()
        left_layout.addWidget(self.hint_error_lbl)

        nav_row = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Previous")
        self.btn_prev.setFixedWidth(120)
        self.btn_prev.setFixedHeight(44)
        self.btn_prev.clicked.connect(self._prev_question)
        nav_row.addWidget(self.btn_prev)

        self.btn_flag = QPushButton("🚩 Flag Question")
        self.btn_flag.setFixedWidth(140)
        self.btn_flag.setFixedHeight(44)
        self.btn_flag.clicked.connect(self._toggle_flag)
        nav_row.addWidget(self.btn_flag)

        if self.exam.get('hints_enabled'):
            self.btn_hint = QPushButton("💡 Get Hint")
            self.btn_hint.setFixedWidth(130)
            self.btn_hint.setFixedHeight(44)
            self.btn_hint.clicked.connect(self._get_hint)
            nav_row.addWidget(self.btn_hint)

        nav_row.addStretch()
        self.btn_next = QPushButton("Next Question ▶")
        self.btn_next.setFixedWidth(150)
        self.btn_next.setFixedHeight(44)
        self.btn_next.clicked.connect(self._next_question)
        nav_row.addWidget(self.btn_next)
        left_layout.addLayout(nav_row)

        left_layout.addStretch()
        btn_submit = QPushButton("✅ Submit Exam")
        btn_submit.setFixedHeight(48)
        btn_submit.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn_submit.clicked.connect(self._confirm_submit)
        left_layout.addWidget(btn_submit)

        main_layout.addWidget(left_panel, 3)

        right_panel = QFrame()
        right_panel.setFixedWidth(180)
        right_panel.setStyleSheet("background-color: #1A1A2E;")
        right_layout = QVBoxLayout(right_panel)
        
        self.q_nav_buttons = []
        grid = QWidget()
        from PyQt5.QtWidgets import QGridLayout
        grid_layout = QGridLayout(grid)
        for i in range(len(self.questions)):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("background-color: #2C2C54; color: white; border-radius: 6px;")
            btn.clicked.connect(lambda _, idx=i: self._show_question(idx))
            grid_layout.addWidget(btn, i // 3, i % 3)
            self.q_nav_buttons.append(btn)
        right_layout.addWidget(grid)
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
            self._submit_exam()
            return
        mins, secs = divmod(remaining, 60)
        self.timer_label.setText(f"⏱ {mins:02}:{secs:02}")

    def _show_question(self, idx):
        self._save_current_answer()
        self.current_idx = idx
        self.hint_error_lbl.hide()
        q = self.questions[idx]
        self.q_num_lbl.setText(f"Q{idx + 1}.")
        self.question_lbl.setText(str(q.get('question_text', '')))
        self.progress_lbl.setText(f"Question {idx + 1} / {len(self.questions)}")

        # Clear options
        for rb in self.option_group.buttons():
            self.option_group.removeButton(rb)
        for i in reversed(range(self.options_layout.count())):
            widget = self.options_layout.itemAt(i).widget()
            if widget: widget.deleteLater()

        if q['type'] == 'Short Answer':
            self.options_frame.hide()
            self.short_answer_input.show()
            self.short_answer_input.setPlainText(self.student_answers.get(q['id'], ''))
        else:
            self.short_answer_input.hide()
            self.options_frame.show()
            options = q.get('options') if q['type'] == 'MCQ' else ['True', 'False']
            if not options: options = []
            if isinstance(options, str): options = json.loads(options)
            saved_answer = self.student_answers.get(q['id'], '')
            for opt in options:
                rb = QRadioButton(opt)
                if opt == saved_answer: rb.setChecked(True)
                self.option_group.addButton(rb)
                self.options_layout.addWidget(rb)

        self._update_nav_buttons()

    def _save_current_answer(self):
        if self.current_idx >= len(self.questions): return
        q = self.questions[self.current_idx]
        if q['type'] == 'Short Answer':
            self.student_answers[q['id']] = self.short_answer_input.toPlainText().strip()
        else:
            for btn in self.option_group.buttons():
                if btn.isChecked():
                    self.student_answers[q['id']] = btn.text()
                    break

    def _update_nav_buttons(self):
        self.btn_prev.setEnabled(self.current_idx > 0)
        self.btn_next.setEnabled(self.current_idx < len(self.questions) - 1)
        for i, btn in enumerate(self.q_nav_buttons):
            q_id = self.questions[i]['id']
            if i == self.current_idx: btn.setStyleSheet("border: 2px solid white;")
            elif q_id in self.flagged: btn.setStyleSheet("background-color: orange;")
            elif q_id in self.student_answers: btn.setStyleSheet("background-color: green;")
            else: btn.setStyleSheet("background-color: #2C2C54;")

    def _prev_question(self):
        if self.current_idx > 0: self._show_question(self.current_idx - 1)

    def _next_question(self):
        if self.current_idx < len(self.questions) - 1: self._show_question(self.current_idx + 1)

    def _toggle_flag(self):
        q_id = self.questions[self.current_idx]['id']
        if q_id in self.flagged: self.flagged.remove(q_id)
        else: self.flagged.add(q_id)
        self._update_nav_buttons()

    def show_loading(self):
        self.btn_hint.setEnabled(False)
        self.btn_hint.setText("Getting hint...")
        self.hint_error_lbl.hide()

    def hide_loading(self):
        self.btn_hint.setEnabled(True)
        self.btn_hint.setText("💡 Get Hint")

    def _get_hint(self):
        """Triggers AI hint generation with worker pattern (CHANGE 4 [1])"""
        q = self.questions[self.current_idx]
        self.show_loading()

        prompt = HINT_PROMPT.format(question=q['question_text'], correct_answer=q['correct_answer'])
        
        self.worker = AIWorker(prompt=prompt)
        self.worker.result_ready.connect(self.on_ai_result)
        self.worker.error_occurred.connect(self.on_ai_error)
        self.worker.start()

    def on_ai_result(self, result):
        """Displays hint in a styled popup (CHANGE 4 [2])"""
        self.hide_loading()
        
        # Log to DB
        q = self.questions[self.current_idx]
        self.result_dao.log_hint_usage(q['id'], self.user['id'])

        # Show Styled Dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("AI Hint")
        msg.setIcon(QMessageBox.Information)
        msg.setText(result)
        msg.addButton("Got it, thanks!", QMessageBox.AcceptRole)
        msg.exec_()

    def on_ai_error(self, error):
        """Handles hint errors (CHANGE 4 [3])"""
        self.hide_loading()
        self.hint_error_lbl.setText("Hint unavailable — AI is offline")
        self.hint_error_lbl.show()

    def _confirm_submit(self):
        reply = QMessageBox.question(self, "Submit", "Are you sure you want to submit?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes: self._submit_exam()

    def _submit_exam(self):
        self.timer.stop()
        self._save_current_answer()
        self.exam['questions'] = self.questions
        self.worker = SubmissionWorker(self.exam, self.student_answers, self.user, self.elapsed_seconds)
        self.worker.finished.connect(self._on_submission_finished)
        self.worker.start()

    def _on_submission_finished(self, result_id, error_msg):
        if result_id > 0: self.dashboard.show_result(result_id)
        else: QMessageBox.critical(self, "Error", error_msg)
