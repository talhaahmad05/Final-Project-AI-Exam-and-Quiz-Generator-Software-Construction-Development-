"""
filename: test_ai_engine.py
changes made: Removed deprecated AIWorkerMCQ tests after rolling back to simplified synchronous MCQ logic.
author: Talha Ahmad
date: 2026-05-16
"""

import unittest
from unittest.mock import patch, MagicMock
import requests
import json
import sys
import os

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from QuizPlatform.ai_engine import ask_ai, AIWorker, ask_ai_mcq, KEEP_ALIVE

class TestAIComponents(unittest.TestCase):
    """Unit tests for simplified AI components using mocks"""

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_ask_ai_success(self, mock_post):
        """[1] mock returns valid response, assert correct string returned"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test success response"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = ask_ai("Hello")
        self.assertEqual(result, "Test success response")

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_ask_ai_connection_error(self, mock_post):
        """[2] mock raises ConnectionError, assert error message returned"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        result = ask_ai("Hello")
        self.assertEqual(result, "ERROR: Ollama is not running.")

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_ask_ai_timeout(self, mock_post):
        """[3] mock raises Timeout, assert timeout message returned"""
        mock_post.side_effect = requests.exceptions.Timeout()

        result = ask_ai("Hello")
        self.assertEqual(result, "ERROR: AI took too long to respond.")

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_ai_worker_emits_result(self, mock_post):
        """[4] create AIWorker, connect result_ready signal, run worker, assert signal was emitted"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Worker success"}
        mock_post.return_value = mock_response

        worker = AIWorker(prompt="Hello")
        
        # Capture signal
        result_captured = []
        def on_ready(res):
            result_captured.append(res)
        
        worker.result_ready.connect(on_ready)
        worker.run() # Manual run for testing sync behavior in thread
        
        self.assertEqual(len(result_captured), 1)
        self.assertEqual(result_captured[0], "Worker success")

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_ai_worker_emits_error(self, mock_post):
        """[5] mock ask_ai to raise exception, assert error_occurred emitted"""
        mock_post.side_effect = Exception("Crash")

        worker = AIWorker(prompt="Hello")
        
        error_captured = []
        def on_error(err):
            error_captured.append(err)
            
        worker.error_occurred.connect(on_error)
        worker.run()
        
        self.assertEqual(len(error_captured), 1)
        self.assertIn("Crash", error_captured[0])

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_ask_ai_keep_alive_in_payload(self, mock_post):
        """Mock requests.post and assert keep_alive is in payload"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "test"}
        mock_post.return_value = mock_response

        ask_ai("test prompt")
        
        called_args, called_kwargs = mock_post.call_args
        payload = called_kwargs.get("json", {})
        self.assertIn("keep_alive", payload)
        self.assertEqual(payload["keep_alive"], "10m")

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_ask_ai_mcq_token_budget(self, mock_post):
        """[1] Assert num_predict equals num_questions * 200"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "[]"}
        mock_post.return_value = mock_response

        ask_ai_mcq("test", 5)
        
        called_args, called_kwargs = mock_post.call_args
        payload = called_kwargs.get("json", {})
        options = payload.get("options", {})
        self.assertEqual(options["num_predict"], 1000)
        self.assertEqual(options["num_ctx"], 4096)

    @patch('QuizPlatform.ai_engine.requests.post')
    def test_ask_ai_mcq_keep_alive(self, mock_post):
        """[2] Assert keep_alive exists and matches constant"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "[]"}
        mock_post.return_value = mock_response

        ask_ai_mcq("test", 3)
        
        called_args, called_kwargs = mock_post.call_args
        payload = called_kwargs.get("json", {})
        self.assertEqual(payload["keep_alive"], KEEP_ALIVE)

if __name__ == '__main__':
    unittest.main()
