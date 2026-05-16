"""
filename: chatbot_ui.py
changes made: Added streaming AI support, word-by-word response, and conversation history persistence.
author: Talha Ahmad
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QLineEdit, QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.ai_engine import (
    AIWorkerStream,
    CHAT_CONTEXT
)
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)

class ChatBubble(QFrame):
    """A single chat message bubble"""

    def __init__(self, text, is_user=True, is_italic=False):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.bubble = QLabel(text)
        self.bubble.setWordWrap(True)
        font = QFont("Segoe UI", 10)
        if is_italic:
            font.setItalic(True)
        self.bubble.setFont(font)
        self.bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.bubble.setMaximumWidth(480)
        self.bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if is_user:
            self.bubble.setStyleSheet("""
                background-color: #1565C0; color: white;
                border-radius: 12px; padding: 10px 14px;
            """)
            layout.addStretch()
            layout.addWidget(self.bubble)
        else:
            color = "gray" if is_italic else "#1A1A2E"
            self.bubble.setStyleSheet(f"""
                background-color: #F5F5F5; color: {color};
                border-radius: 12px; padding: 10px 14px;
                border: 1px solid #E0E0E0;
            """)
            layout.addWidget(self.bubble)
            layout.addStretch()

    def setText(self, text):
        self.bubble.setText(text)

class ChatbotUI(QWidget):
    """AI Study Chatbot screen with streaming support"""

    def __init__(self, user):
        super().__init__()
        self.user = user
        # [2] ADD these instance variables
        self.worker = None
        self.current_ai_bubble = None
        self.chat_history = []
        self.full_ai_response = ""
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
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 12px; background-color: white;")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(8)
        self.chat_layout.setContentsMargins(12, 12, 12, 12)
        self.chat_scroll.setWidget(self.chat_container)
        layout.addWidget(self.chat_scroll)

        # Welcome message
        self.add_bubble(
            "🤖 👋 Hello! I'm your AI study "
            "assistant powered by Mistral. "
            "Ask me anything about your coursework!",
            sender="ai"
        )

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: white; border: 1px solid #E0E0E0; border-radius: 12px;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 8, 8, 8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask any study question here...")
        self.input_field.setFont(QFont("Segoe UI", 11))
        self.input_field.setStyleSheet("border: none; background: transparent; color: #1A1A2E;")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.btn_send = QPushButton("Send ➤")
        self.btn_send.setFixedHeight(44)
        self.btn_send.setFixedWidth(110)
        self.btn_send.setStyleSheet("""
            QPushButton { background-color: #1565C0; color: white; border-radius: 8px; border: none; font-weight: bold; }
            QPushButton:hover { background-color: #0D47A1; }
            QPushButton:disabled { background-color: #BDBDBD; }
        """)
        self.btn_send.clicked.connect(self.send_message)
        input_layout.addWidget(self.btn_send)

        self.btn_stop = QPushButton("Stop ⏹")
        self.btn_stop.setFixedHeight(44)
        self.btn_stop.setFixedWidth(100)
        self.btn_stop.setStyleSheet("""
            QPushButton { background-color: #C62828; color: white; border-radius: 8px; border: none; font-weight: bold; }
            QPushButton:hover { background-color: #B71C1C; }
        """)
        self.btn_stop.clicked.connect(self.stop_generation)
        self.btn_stop.hide()
        input_layout.addWidget(self.btn_stop)

        layout.addWidget(input_frame)

    # Helper method for consistent bubble adding
    def add_bubble(self, text, sender="user"):
        is_user = (sender == "user")
        bubble = ChatBubble(text, is_user=is_user)
        self.chat_layout.addWidget(bubble)
        # Scroll to bottom
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        return bubble

    # [3] REWRITE send_message() method:
    def send_message(self):
        """
        Sends student message and starts streaming
        AI response. Disables input while streaming.
        """
        message = self.input_field.text().strip()
        if not message:
            return

        # Clear input immediately
        self.input_field.clear()

        # Add student bubble to chat
        self.add_bubble(message, sender="user")

        # Save to history
        self.chat_history.append(
            f"Student: {message}"
        )

        # UI State change
        self.input_field.setEnabled(False)
        self.btn_send.hide()
        self.btn_stop.show()

        # Create empty AI bubble that will fill up
        self.full_ai_response = ""
        self.current_ai_bubble = self.add_bubble(
            "", sender="ai"
        )

        # Build prompt with chat context + history
        history_text = "\n".join(
            self.chat_history[-6:]
        )
        prompt = (
            f"{CHAT_CONTEXT}\n\n"
            f"Conversation so far:\n{history_text}\n\n"
            f"AI Assistant:"
        )

        # Start streaming worker
        self.worker = AIWorkerStream(prompt=prompt)
        self.worker.token_received.connect(
            self.on_token_received
        )
        self.worker.stream_done.connect(
            self.on_stream_done
        )
        self.worker.error_occurred.connect(
            self.on_stream_error
        )
        self.worker.start()

    def stop_generation(self):
        """Halts the AI worker and cleans up UI"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.full_ai_response += " [Stopped by User]"
            if self.current_ai_bubble:
                self.current_ai_bubble.setText("🤖 " + self.full_ai_response)
            self.on_stream_done(self.full_ai_response)

    # [4] ADD on_token_received(self, token) method:
    def on_token_received(self, token):
        """
        Appends each streamed token to the
        current AI chat bubble in real time.
        Scrolls chat to bottom automatically.

        Args:
            token (str): Single token from stream.
        """
        self.full_ai_response += token
        if self.current_ai_bubble:
            self.current_ai_bubble.setText(
                "🤖 " + self.full_ai_response
            )
        # Auto scroll to bottom
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # [5] ADD on_stream_done(self, full_response) method:
    def on_stream_done(self, full_response):
        """
        Called when streaming is complete.
        Re-enables input and saves response
        to chat history.

        Args:
            full_response (str): Complete AI response.
        """
        # Save AI response to history
        self.chat_history.append(
            f"AI Assistant: {full_response}"
        )

        # Keep history to last 10 exchanges max
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]

        # Re-enable input
        self.input_field.setEnabled(True)
        self.btn_stop.hide()
        self.btn_send.show()
        self.btn_send.setEnabled(True)
        self.btn_send.setText("Send ➤")
        self.input_field.setFocus()

        # Final scroll to bottom
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # [6] ADD on_stream_error(self, error) method:
    def on_stream_error(self, error):
        """
        Called when streaming fails.
        Removes empty AI bubble, shows error
        bubble, and re-enables input.

        Args:
            error (str): Error message.
        """
        # Update the empty bubble to show error
        if self.current_ai_bubble:
            self.current_ai_bubble.setText(
                "⚠️ " + error
            )

        # Re-enable input
        self.input_field.setEnabled(True)
        self.btn_stop.hide()
        self.btn_send.show()
        self.btn_send.setEnabled(True)
        self.btn_send.setText("Send ➤")

    # [7] REWRITE clear_chat() method:
    def clear_chat(self):
        """
        Clears all chat bubbles and resets
        conversation history completely.
        """
        # Clear all bubble widgets from layout
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Reset state
        self.chat_history = []
        self.full_ai_response = ""
        self.current_ai_bubble = None

        # Show welcome message again
        self.add_bubble(
            "🤖 👋 Hello! I'm your AI study "
            "assistant powered by Mistral. "
            "Ask me anything about your coursework!",
            sender="ai"
        )
