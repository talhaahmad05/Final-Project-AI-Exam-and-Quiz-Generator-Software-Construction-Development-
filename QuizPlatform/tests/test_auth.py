"""
filename: test_auth.py
module: Authentication Unit Tests
author: Talha Ahmad
date: 2026-05-12
Sprint: 5 - Testing
"""

import unittest
from unittest.mock import patch, MagicMock
import hashlib
import sys
import os

# Add the parent of QuizPlatform to sys.path so 'QuizPlatform' is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from QuizPlatform.exceptions import QuizAuthError, QuizValidationError
from QuizPlatform.utils.form_validator import FormValidator


class TestLoginValidation(unittest.TestCase):
    """Test login input validation"""

    def test_valid_login_inputs(self):
        """Valid credentials should not raise any exception"""
        try:
            FormValidator.validate_login("admin", "admin123")
        except QuizValidationError:
            self.fail("validate_login raised QuizValidationError on valid input")

    def test_empty_username(self):
        """Empty username should raise QuizValidationError"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_login("", "admin123")

    def test_empty_password(self):
        """Empty password should raise QuizValidationError"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_login("admin", "")

    def test_short_username(self):
        """Username under 3 chars should raise QuizValidationError"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_login("ab", "admin123")

    def test_short_password(self):
        """Password under 5 chars should raise QuizValidationError"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_login("admin", "ab")


class TestPasswordHashing(unittest.TestCase):
    """Test SHA-256 password hashing"""

    def test_password_hash_consistency(self):
        """Same password should always produce same hash"""
        pwd = "admin123"
        h1 = hashlib.sha256(pwd.encode()).hexdigest()
        h2 = hashlib.sha256(pwd.encode()).hexdigest()
        self.assertEqual(h1, h2)

    def test_password_hash_length(self):
        """SHA-256 hash must be 64 hex characters"""
        pwd = "admin123"
        h = hashlib.sha256(pwd.encode()).hexdigest()
        self.assertEqual(len(h), 64)

    def test_different_passwords_different_hashes(self):
        """Different passwords must produce different hashes"""
        h1 = hashlib.sha256("admin123".encode()).hexdigest()
        h2 = hashlib.sha256("student123".encode()).hexdigest()
        self.assertNotEqual(h1, h2)


class TestPasswordChange(unittest.TestCase):
    """Test password change validation"""

    def test_valid_password_change(self):
        """Valid password change inputs should pass"""
        try:
            FormValidator.validate_password_change("old12", "newpass12", "newpass12")
        except QuizValidationError:
            self.fail("Should not raise on valid password change")

    def test_mismatched_passwords(self):
        """Mismatched new passwords should raise"""
        with self.assertRaises(QuizValidationError):
            FormValidator.validate_password_change("old12", "newpass12", "different12")



if __name__ == '__main__':
    unittest.main()
