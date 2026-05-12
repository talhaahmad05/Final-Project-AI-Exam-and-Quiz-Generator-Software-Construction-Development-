"""
filename: test_ai_engine.py
module: AI Engine Unit Tests (Mocked)
author: Talha Ahmad
date: 2026-05-12
Sprint: 5 - Testing
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent of QuizPlatform to sys.path so 'QuizPlatform' is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from QuizPlatform.ai_engine import AIEngine
from QuizPlatform.exceptions import QuizAIError


class TestAIQuestionGeneration(unittest.TestCase):
    """Test AI question generation with mocked Ollama"""

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_generate_questions_success(self, mock_post):
        """Valid AI response should return list of question dicts"""
        mock_questions = [
            {"question": "What is OOP?", "options": ["A", "B", "C", "D"],
             "correct": "A", "topic": "OOP", "difficulty": "easy"}
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": json.dumps(mock_questions)}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        engine = AIEngine()
        result = engine.generate_questions("OOP", "easy", 1)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("question", result[0])

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_generate_questions_malformed_json(self, mock_post):
        """Malformed AI response should raise QuizAIError"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "this is not json"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        engine = AIEngine()
        with self.assertRaises(QuizAIError):
            engine.generate_questions("OOP", "easy", 1)

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_connection_error(self, mock_post):
        """Connection error should raise QuizAIError"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Offline")

        engine = AIEngine()
        with self.assertRaises(QuizAIError):
            engine.generate_questions("OOP", "easy", 1)


class TestAIGrading(unittest.TestCase):
    """Test AI short answer grading with mocked Ollama"""

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_grade_short_answer_returns_int(self, mock_post):
        """AI grader should return an integer score"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "3"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        engine = AIEngine()
        result = engine.grade_short_answer("Q?", "model", "student", 5)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 3)

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_grade_short_answer_handles_text_response(self, mock_post):
        """AI grader should extract number even from verbose response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "The score is 4 out of 5."}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        engine = AIEngine()
        result = engine.grade_short_answer("Q?", "model", "student", 5)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 4)


class TestAIHintGeneration(unittest.TestCase):
    """Test AI hint generation"""

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_get_hint_returns_string(self, mock_post):
        """Hint should return a non-empty string"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Think about inheritance hierarchies."}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        engine = AIEngine()
        result = engine.get_hint("What is OOP?", "Object-Oriented Programming")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


if __name__ == '__main__':
    unittest.main()
