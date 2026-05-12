"""
filename: test_question.py
module: Question Validation Unit Tests
author: Talha Ahmad
date: 2026-05-12
Sprint: 5 - Testing
"""

import unittest
import sys
import os

# Add the parent of QuizPlatform to sys.path so 'QuizPlatform' is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from QuizPlatform.exceptions import QuizValidationError
from QuizPlatform.utils.form_validator import FormValidator


class TestQuestionValidation(unittest.TestCase):
    """Test question input validation"""

    def test_valid_mcq_question(self):
        """A valid MCQ question should not raise"""
        try:
            FormValidator.validate_question(
                "What is 2+2?",
                ["3", "4", "5", "6"],
                "4",
                "MCQ"
            )
        except QuizValidationError:
            self.fail("Should not raise on valid MCQ")

    def test_empty_question_text(self):
        """Empty question text should raise QuizValidationError"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_question(
                "",
                ["A", "B", "C", "D"],
                "A",
                "MCQ"
            )

    def test_mcq_wrong_correct_answer(self):
        """MCQ correct answer not in options should raise"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_question(
                "What is 2+2?",
                ["3", "4", "5", "6"],
                "7",
                "MCQ"
            )

    def test_mcq_too_few_options(self):
        """MCQ with fewer than 2 options should raise"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_question(
                "What is 2+2?",
                ["4"],
                "4",
                "MCQ"
            )

    def test_valid_true_false(self):
        """Valid True/False question should not raise"""
        try:
            FormValidator.validate_question(
                "Python is interpreted?",
                None,
                "True",
                "True/False"
            )
        except QuizValidationError:
            self.fail("Should not raise on valid True/False")

    def test_empty_correct_answer(self):
        """Empty correct answer should raise"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_question(
                "What is 2+2?",
                None,
                "",
                "Short Answer"
            )


if __name__ == '__main__':
    unittest.main()
