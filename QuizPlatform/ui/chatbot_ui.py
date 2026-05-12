"""
filename: chatbot_ui.py
module: AI Study Chatbot UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 4 - AI Chatbot
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from QuizPlatform.ai_engine import AIEngine
from QuizPlatform.exceptions import QuizAIError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)


class ChatThread(QThread):
    """Background thread for AI chatbot responses"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, query, history):
        super().__init__()
        self.query = query
        self.history = history
        self.ai = AIEngine()

    def run(self):
        try:
            response = self.ai.chat_response(self.query, self.history)
            self.response_ready.emit(response)
        except QuizAIError as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {e}")


class ChatBubble(QFrame):
    """A single chat message bubble"""

    def __init__(self, text, is_user=True):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setFont(QFont("Segoe UI", 10))
        bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        bubble.setMaximumWidth(480)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if is_user:
            bubble.setStyleSheet("""
                background-color: #1565C0; color: white;
                border-radius: 12px; padding: 10px 14px;
            """)
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            bubble.setStyleSheet("""
                background-color: #F5F5F5; color: #1A1A2E;
                border-radius: 12px; padding: 10px 14px;
                border: 1px solid #E0E0E0;
            """)
            layout.addWidget(bubble)
            layout.addStretch()


class ChatbotUI(QWidget):
    """AI Study Chatbot screen"""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.conversation_history = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("💬 AI Study Chatbot")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        hdr.addWidget(title)
        hdr.addStretch()
        ai_badge = QLabel("✨ Powered by Mistral 7B")
        ai_badge.setStyleSheet("background-color: #E3F2FD; color: #1565C0; border-radius: 12px; padding: 4px 10px; font-size: 10px;")
        hdr.addWidget(ai_badge)
        btn_clear = QPushButton("🗑 Clear Chat")
        btn_clear.setStyleSheet("background-color: #EEEEEE; color: #333;")
        btn_clear.clicked.connect(self.clear_chat)
        hdr.addWidget(btn_clear)
        layout.addLayout(hdr)

        # Chat window
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 12px; background-color: white;")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(8)
        self.chat_layout.setContentsMargins(12, 12, 12, 12)
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)

        # Welcome message
        self._add_bot_bubble("👋 Hello! I'm your AI study assistant powered by Mistral. Ask me anything about your coursework — algorithms, OOP, databases, or any subject you're studying!")

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 12px;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 8, 8, 8)

        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Ask any study question here...")
        self.msg_input.setFont(QFont("Segoe UI", 11))
        self.msg_input.setStyleSheet("border: none; background: transparent; color: #1A1A2E;")
        self.msg_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.msg_input)

        self.btn_send = QPushButton("Send ➤")
        self.btn_send.setFixedHeight(38)
        self.btn_send.setFixedWidth(90)
        self.btn_send.setStyleSheet("""
            QPushButton { background-color: #1565C0; color: white; border-radius: 8px; border: none; font-weight: bold; }
            QPushButton:hover { background-color: #0D47A1; }
            QPushButton:disabled { background-color: #BDBDBD; }
        """)
        self.btn_send.clicked.connect(self.send_message)
        input_layout.addWidget(self.btn_send)
        layout.addWidget(input_frame)

    def send_message(self):
        text = self.msg_input.text().strip()
        if not text:
            return

        self.msg_input.clear()
        self.btn_send.setEnabled(False)
        self.btn_send.setText("⏳")

        # Add user bubble
        self._add_user_bubble(text)
        self.conversation_history.append({'role': 'User', 'content': text})

        # Add temporary "Thinking..." bubble
        self.thinking_bubble = ChatBubble("🤖 Thinking...", is_user=False)
        self.chat_layout.addWidget(self.thinking_bubble)
        self._scroll_to_bottom()

        # Start thread
        self.thread = ChatThread(text, self.conversation_history[:])
        self.thread.response_ready.connect(self._on_response)
        self.thread.error_occurred.connect(self._on_error)
        self.thread.finished.connect(lambda: self.btn_send.setEnabled(True))
        self.thread.finished.connect(lambda: self.btn_send.setText("Send ➤"))
        self.thread.start()

    def _on_response(self, response):
        if hasattr(self, 'thinking_bubble'):
            self.chat_layout.removeWidget(self.thinking_bubble)
            self.thinking_bubble.deleteLater()
        
        self._add_bot_bubble(response)
        self.conversation_history.append({'role': 'Assistant', 'content': response})
        self._scroll_to_bottom()

    def _on_error(self, error):
        if hasattr(self, 'thinking_bubble'):
            self.chat_layout.removeWidget(self.thinking_bubble)
            self.thinking_bubble.deleteLater()
            
        self._add_bot_bubble(f"⚠ Error: {error}")
        self._scroll_to_bottom()

    def _add_user_bubble(self, text):
        bubble = ChatBubble(text, is_user=True)
        self.chat_layout.addWidget(bubble)
        self._scroll_to_bottom()

    def _add_bot_bubble(self, text):
        bubble = ChatBubble(f"🤖 {text}", is_user=False)
        self.chat_layout.addWidget(bubble)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def clear_chat(self):
        self.conversation_history = []
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._add_bot_bubble("Chat cleared! How can I help you study today?")
