"""
filename: form_validator.py
module: Form Validation Utility
author: Talha Ahmad
date: 2026-05-12
"""

import re
from QuizPlatform.exceptions import QuizValidationError

class FormValidator:
    """Static methods for validating user inputs across the application"""

    @staticmethod
    def validate_login(username, password):
        if not username or not password:
            raise QuizValidationError("Username and Password are required.")
        if len(username) < 3:
            raise QuizValidationError("Username must be at least 3 characters.")
        if len(password) < 5:
            raise QuizValidationError("Password must be at least 5 characters.")

    @staticmethod
    def validate_question(question_text, options, correct_answer, q_type):
        if not question_text.strip():
            raise QuizValidationError("Question text cannot be empty.")
        if q_type == "MCQ":
            if not options or len(options) < 2:
                raise QuizValidationError("MCQ must have at least 2 options.")
            if correct_answer not in options:
                raise QuizValidationError("Correct answer must be one of the options.")
        if not correct_answer.strip():
            raise QuizValidationError("Correct answer cannot be empty.")

    @staticmethod
    def validate_exam(title, subject, time_limit, total_marks, pass_percentage):
        if not title.strip() or not subject.strip():
            raise QuizValidationError("Title and Subject are required.")
        try:
            time = int(time_limit)
            marks = int(total_marks)
            pass_p = int(pass_percentage)
            if time <= 0 or marks <= 0:
                raise QuizValidationError("Time and Marks must be positive numbers.")
            if not (0 <= pass_p <= 100):
                raise QuizValidationError("Pass percentage must be between 0 and 100.")
        except ValueError:
            raise QuizValidationError("Time, Marks, and Pass Percentage must be numeric.")

    @staticmethod
    def validate_password_change(old_p, new_p, confirm_p):
        if not old_p or not new_p or not confirm_p:
            raise QuizValidationError("All fields are required.")
        if new_p != confirm_p:
            raise QuizValidationError("New passwords do not match.")
        if len(new_p) < 5:
            raise QuizValidationError("New password must be at least 5 characters.")
