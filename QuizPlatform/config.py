"""
filename: config.py
module: Core Configuration
author: Talha Ahmad
date: 2026-05-12
"""

import configparser
import os

# Load configuration from config.ini
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

# Database Constants
DB_SERVER = config.get('Database', 'Server', fallback='TalhaMughal\\SQLEXPRESS')
DB_NAME = config.get('Database', 'Database', fallback='QuizAIPlatform')
DB_TRUSTED = config.get('Database', 'Trusted_Connection', fallback='yes')

# AI Constants
AI_ENDPOINT = config.get('AI', 'Endpoint', fallback='http://localhost:11434/api/generate')
MODEL_QUESTION_GEN = config.get('AI', 'QuestionModel', fallback='mistral:7b-instruct')
MODEL_GRADING = config.get('AI', 'GradingModel', fallback='llama3.1:8b')
MODEL_HINT = config.get('AI', 'HintModel', fallback='mistral:7b-instruct')
MODEL_TOPIC = config.get('AI', 'TopicModel', fallback='llama3.1:8b')
MODEL_CHAT = config.get('AI', 'ChatModel', fallback='mistral:7b-instruct')

# UI Constants
APP_TITLE = "QuizAI Platform — Talha Ahmad"
NAVY_BLUE = "#1A1A2E"
ACCENT_BLUE = "#1565C0"
WHITE = "#FFFFFF"

# Auth Constants
PASSWORD_SALT = "quiz_platform_2024" # Extra security for hashing
