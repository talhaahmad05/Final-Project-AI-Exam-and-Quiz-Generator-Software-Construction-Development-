"""
filename: question_dao.py
module: Question Data Access Object
author: Talha Ahmad
date: 2026-05-12
"""

import pyodbc
import json
from QuizPlatform.config import DB_SERVER, DB_NAME, DB_TRUSTED
from QuizPlatform.utils.logger import get_logger
from QuizPlatform.exceptions import QuizDatabaseError

logger = get_logger(__name__)

class QuestionDAO:
    def __init__(self):
        self.conn_str = f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection={DB_TRUSTED};"

    def get_connection(self):
        return pyodbc.connect(self.conn_str)

    def add_question(self, question_text, options, correct_answer, q_type, subject, difficulty, topic):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                options_json = json.dumps(options) if options else None
                cursor.execute("""
                    INSERT INTO Questions (question_text, options_json, correct_answer, type, subject, difficulty, topic)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (question_text, options_json, correct_answer, q_type, subject, difficulty, topic))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding question: {e}")
            raise QuizDatabaseError(f"Failed to add question: {e}")

    def get_all_questions(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, question_text, options_json, correct_answer, type, subject, difficulty, topic FROM Questions")
                rows = cursor.fetchall()
                questions = []
                for row in rows:
                    questions.append({
                        'id': row[0],
                        'question_text': row[1],
                        'options': json.loads(row[2]) if row[2] else [],
                        'correct_answer': row[3],
                        'type': row[4],
                        'subject': row[5],
                        'difficulty': row[6],
                        'topic': row[7]
                    })
                return questions
        except Exception as e:
            logger.error(f"Error getting questions: {e}")
            raise QuizDatabaseError(f"Failed to get questions: {e}")

    def update_question(self, q_id, question_text, options, correct_answer, q_type, subject, difficulty, topic):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                options_json = json.dumps(options) if options else None
                cursor.execute("""
                    UPDATE Questions 
                    SET question_text=?, options_json=?, correct_answer=?, type=?, subject=?, difficulty=?, topic=?
                    WHERE id=?
                """, (question_text, options_json, correct_answer, q_type, subject, difficulty, topic, q_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating question: {e}")
            raise QuizDatabaseError(f"Failed to update question: {e}")

    def delete_question(self, q_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # First, remove references from all junction/link tables
                cursor.execute("DELETE FROM ExamQuestions WHERE question_id=?", (q_id,))
                cursor.execute("DELETE FROM StudentAnswers WHERE question_id=?", (q_id,))
                cursor.execute("DELETE FROM HintLogs WHERE question_id=?", (q_id,))
                
                # Finally, delete the question itself
                cursor.execute("DELETE FROM Questions WHERE id=?", (q_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting question: {e}")
            raise QuizDatabaseError(f"Failed to delete question: {e}")

    def search_questions(self, subject=None, difficulty=None, topic=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT id, question_text, options_json, correct_answer, type, subject, difficulty, topic FROM Questions WHERE 1=1"
                params = []
                if subject:
                    query += " AND subject LIKE ?"
                    params.append(f"%{subject}%")
                if difficulty:
                    query += " AND difficulty = ?"
                    params.append(difficulty)
                if topic:
                    query += " AND topic LIKE ?"
                    params.append(f"%{topic}%")
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                questions = []
                for row in rows:
                    questions.append({
                        'id': row[0],
                        'question_text': row[1],
                        'options': json.loads(row[2]) if row[2] else [],
                        'correct_answer': row[3],
                        'type': row[4],
                        'subject': row[5],
                        'difficulty': row[6],
                        'topic': row[7]
                    })
                return questions
        except Exception as e:
            logger.error(f"Error searching questions: {e}")
            raise QuizDatabaseError(f"Failed to search questions: {e}")
