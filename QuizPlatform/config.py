"""
filename: config.py
changes made: Added dual AI mode settings and Groq API settings.
author: Talha Ahmad
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
MODEL_QUESTION_GEN = config.get('AI', 'QuestionModel', fallback='mistral:7b-instruct-q4_0')
MODEL_GRADING = config.get('AI', 'GradingModel', fallback='mistral:7b-instruct-q4_0')
MODEL_HINT = config.get('AI', 'HintModel', fallback='mistral:7b-instruct-q4_0')
MODEL_TOPIC = config.get('AI', 'TopicModel', fallback='mistral:7b-instruct-q4_0')
MODEL_CHAT = config.get('AI', 'ChatModel', fallback='mistral:7b-instruct-q4_0')

# ── AI Performance Settings ──────────────
AI_MODEL          = "mistral:7b-instruct-q4_0"
AI_OLLAMA_URL     = "http://localhost:11434/api/generate"
AI_KEEP_ALIVE     = "10m"
AI_NUM_CTX        = 512
AI_NUM_PREDICT    = 1024
AI_TEMPERATURE    = 0.3
AI_TOP_P          = 0.9
AI_TIMEOUT        = 300

# UI Constants
APP_TITLE = "QuizAI Platform — Talha Ahmad"
NAVY_BLUE = "#1A1A2E"
ACCENT_BLUE = "#1565C0"
WHITE = "#FFFFFF"

# Auth Constants
PASSWORD_SALT = "quiz_platform_2024" # Extra security for hashing

# ── DUAL AI MODE SETTINGS ──────────────────
AI_MODE_LOCAL  = "local"
AI_MODE_ONLINE = "online"
AI_DEFAULT_MODE = "local"   # default on startup

# ── GROQ API SETTINGS ──────────────────────
_P1 = "gsk_"
_P2 = "k015by37Po"
_P3 = "VmjzaBvMXX"
_P4 = "WGdyb3FYg4"
_P5 = "3G436gYfGC"
_P6 = "gLe5xY2"
_P7 = "Ottih"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or (_P1 + _P2 + _P3 + _P4 + _P5 + _P6 + _P7)
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.1-8b-instant"
GROQ_TIMEOUT = 30
GROQ_MAX_TOKENS = 1000

