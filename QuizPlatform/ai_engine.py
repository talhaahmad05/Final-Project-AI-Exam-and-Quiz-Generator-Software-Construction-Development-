"""
filename: ai_engine.py
module: AI Engine
author: Talha Ahmad
date: 2026-05-12
"""

import requests
import json
from QuizPlatform.config import AI_ENDPOINT, MODEL_QUESTION_GEN, MODEL_GRADING, MODEL_HINT, MODEL_TOPIC, MODEL_CHAT
from QuizPlatform.utils.logger import get_logger
from QuizPlatform.exceptions import QuizAIError

logger = get_logger(__name__)

class AIEngine:
    """Centralized class for all Ollama LLM interactions"""

    def __init__(self):
        self.endpoint = AI_ENDPOINT

    def _call_ai(self, model, prompt):
        """Generic method to call Ollama API"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.endpoint, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            logger.error("Ollama service is offline.")
            raise QuizAIError("AI service is offline. Please start Ollama.")
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            raise QuizAIError(f"AI generation failed: {e}")

    def generate_questions(self, topic, difficulty, n=5):
        """AI Feature 1: Generate MCQs"""
        prompt = (
            f"Generate a JSON array of {n} MCQs about '{topic}' at {difficulty} difficulty. "
            "JSON Format: [{\"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"correct\": \"...\", \"topic\": \"...\", \"difficulty\": \"...\"}]. "
            "Return ONLY raw JSON. No conversational text."
        )
        response_text = self._call_ai(MODEL_QUESTION_GEN, prompt)
        try:
            # Clean response if LLM adds markdown backticks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
            
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Failed to parse AI questions: {e}")
            raise QuizAIError("AI returned malformed JSON questions.")

    def get_result_feedback(self, score, subject, wrong_questions_list):
        """AI Feature 2: Personalized feedback"""
        wrong_questions = ", ".join(wrong_questions_list) if wrong_questions_list else "None"
        prompt = (
            f"A student scored {score}% on a {subject} exam. "
            f"They got these questions wrong: {wrong_questions}. "
            f"Write a short 3-sentence encouraging feedback message "
            f"telling them what to revise. Be specific and helpful."
        )
        return self._call_ai(MODEL_GRADING, prompt)

    def get_hint(self, question, correct_answer):
        """AI Feature 3: Hint generation"""
        prompt = (
            f"A student is stuck on this exam question: {question} "
            f"The correct answer is {correct_answer}. "
            f"Give a helpful hint that guides them toward the answer "
            f"WITHOUT revealing the answer directly. Keep it under 2 sentences."
        )
        return self._call_ai(MODEL_HINT, prompt)

    def grade_short_answer(self, question, model_answer, student_answer, max_marks):
        """AI Feature 4: Short answer grading"""
        prompt = (
            f"Grade this student answer out of {max_marks} marks. "
            f"Question: {question} "
            f"Model Answer: {model_answer} "
            f"Student Answer: {student_answer} "
            f"Return ONLY a single integer number between 0 and {max_marks}. "
            f"No explanation. Just the number."
        )
        response = self._call_ai(MODEL_GRADING, prompt)
        try:
            # Extract number if LLM adds text
            import re
            match = re.search(r'\d+', response)
            if match:
                return int(match.group())
            return 0
        except:
            return 0

    def detect_weak_topics(self, wrong_topics_list):
        """AI Feature 5: Weak topic detection"""
        topics = ", ".join(wrong_topics_list) if wrong_topics_list else "None"
        prompt = (
            f"A student has answered the following questions incorrectly across multiple exams: {topics} "
            f"Identify the top 3 weakest topics they should focus on. "
            f"Return ONLY a JSON array of 3 topic strings. "
            f"Example: [\"Recursion\", \"OOP\", \"File Handling\"]"
        )
        response_text = self._call_ai(MODEL_TOPIC, prompt)
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            return json.loads(response_text)
        except:
            return ["Review core concepts", "Practice more problems", "Focus on fundamentals"]

    def chat_response(self, user_query, history):
        """AI Feature 6: Study Chatbot"""
        context = "You are a helpful study assistant for a software engineering student. "
        # Simple history formatting
        history_str = ""
        for msg in history[-5:]: # Last 5 messages for context
            history_str += f"{msg['role']}: {msg['content']}\n"
        
        prompt = f"{context}\n{history_str}User: {user_query}\nAssistant:"
        return self._call_ai(MODEL_CHAT, prompt)
