"""
filename: test_exam.py
module: Exam Validation Unit Tests
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


class TestExamValidation(unittest.TestCase):
    """Test exam creation validation"""

    def test_valid_exam_inputs(self):
        """Valid exam details should not raise"""
        try:
            FormValidator.validate_exam("Final Exam", "CS101", 30, 100, 50)
        except QuizValidationError:
            self.fail("Should not raise on valid exam inputs")

    def test_empty_title(self):
        """Empty exam title should raise QuizValidationError"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_exam("", "CS101", 30, 100, 50)

    def test_empty_subject(self):
        """Empty subject should raise QuizValidationError"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_exam("Final Exam", "", 30, 100, 50)

    def test_negative_time(self):
        """Negative time limit should raise"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_exam("Final Exam", "CS101", -5, 100, 50)

    def test_zero_marks(self):
        """Zero total marks should raise"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_exam("Final Exam", "CS101", 30, 0, 50)

    def test_pass_percentage_out_of_range(self):
        """Pass percentage >100 should raise"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_exam("Final Exam", "CS101", 30, 100, 150)

    def test_non_numeric_time(self):
        """Non-numeric time should raise"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_exam("Final Exam", "CS101", "abc", 100, 50)


if __name__ == '__main__':
    unittest.main()
