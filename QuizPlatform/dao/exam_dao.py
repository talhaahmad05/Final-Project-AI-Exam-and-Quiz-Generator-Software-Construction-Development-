"""
filename: exam_dao.py
module: Exam Data Access Object
author: Talha Ahmad
date: 2026-05-12
"""

import pyodbc
from QuizPlatform.config import DB_SERVER, DB_NAME, DB_TRUSTED
from QuizPlatform.utils.logger import get_logger
from QuizPlatform.exceptions import QuizDatabaseError

logger = get_logger(__name__)

class ExamDAO:
    def __init__(self):
        self.conn_str = f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection={DB_TRUSTED};"

    def get_connection(self):
        return pyodbc.connect(self.conn_str)

    def create_exam(self, title, subject, time_limit, total_marks, pass_percentage, shuffle, hints):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Exams (title, subject, time_limit, total_marks, pass_percentage, shuffle_questions, hints_enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, subject, time_limit, total_marks, pass_percentage, 1 if shuffle else 0, 1 if hints else 0))
                cursor.execute("SELECT @@IDENTITY")
                exam_id = cursor.fetchone()[0]
                conn.commit()
                return exam_id
        except Exception as e:
            logger.error(f"Error creating exam: {e}")
            raise QuizDatabaseError(f"Failed to create exam: {e}")

    def add_questions_to_exam(self, exam_id, question_ids):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for i, q_id in enumerate(question_ids):
                    cursor.execute("""
                        INSERT INTO ExamQuestions (exam_id, question_id, order_index)
                        VALUES (?, ?, ?)
                    """, (exam_id, q_id, i))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding questions to exam: {e}")
            raise QuizDatabaseError(f"Failed to add questions to exam: {e}")

    def assign_exam_to_students(self, exam_id, student_ids=None):
        """If student_ids is None, assign to all students"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if student_ids is None:
                    cursor.execute("SELECT id FROM Users WHERE role = 'Student'")
                    student_ids = [row[0] for row in cursor.fetchall()]
                
                for s_id in student_ids:
                    # Check if already assigned
                    cursor.execute("SELECT 1 FROM ExamAssignments WHERE exam_id=? AND student_id=?", (exam_id, s_id))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO ExamAssignments (exam_id, student_id, status) VALUES (?, ?, 'Pending')", (exam_id, s_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error assigning exam: {e}")
            raise QuizDatabaseError(f"Failed to assign exam: {e}")

    def get_all_exams(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, title, subject, time_limit, total_marks, pass_percentage, shuffle_questions, hints_enabled FROM Exams")
                rows = cursor.fetchall()
                exams = []
                for row in rows:
                    exams.append({
                        'id': row[0],
                        'title': row[1],
                        'subject': row[2],
                        'time_limit': row[3],
                        'total_marks': row[4],
                        'pass_percentage': row[5],
                        'shuffle': bool(row[6]),
                        'hints': bool(row[7])
                    })
                return exams
        except Exception as e:
            logger.error(f"Error getting exams: {e}")
            raise QuizDatabaseError(f"Failed to get exams: {e}")

    def get_exam_questions(self, exam_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT q.id, q.question_text, q.options_json, q.correct_answer, q.type, q.subject, q.difficulty, q.topic
                    FROM Questions q
                    JOIN ExamQuestions eq ON q.id = eq.question_id
                    WHERE eq.exam_id = ?
                    ORDER BY eq.order_index
                """, (exam_id,))
                rows = cursor.fetchall()
                import json
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
            logger.error(f"Error getting exam questions: {e}")
            raise QuizDatabaseError(f"Failed to get exam questions: {e}")

    def delete_exam(self, exam_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # 1. Delete student answers linked to results of this exam
                cursor.execute("""
                    DELETE FROM StudentAnswers 
                    WHERE result_id IN (SELECT id FROM Results WHERE exam_id=?)
                """, (exam_id,))
                # 2. Delete results of this exam
                cursor.execute("DELETE FROM Results WHERE exam_id=?", (exam_id,))
                # 3. Delete assignments
                cursor.execute("DELETE FROM ExamAssignments WHERE exam_id=?", (exam_id,))
                # 4. Delete question links
                cursor.execute("DELETE FROM ExamQuestions WHERE exam_id=?", (exam_id,))
                # 5. Finally delete the exam
                cursor.execute("DELETE FROM Exams WHERE id=?", (exam_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting exam: {e}")
            raise QuizDatabaseError(f"Failed to delete exam: {e}")
