"""
filename: result_dao.py
module: Result Data Access Object
author: Talha Ahmad
date: 2026-05-12
"""

import pyodbc
from QuizPlatform.config import DB_SERVER, DB_NAME, DB_TRUSTED
from QuizPlatform.utils.logger import get_logger
from QuizPlatform.exceptions import QuizDatabaseError

logger = get_logger(__name__)

class ResultDAO:
    def __init__(self):
        self.conn_str = f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection={DB_TRUSTED};"

    def get_connection(self):
        return pyodbc.connect(self.conn_str)

    def save_result(self, exam_id, student_id, score, percentage, time_taken, feedback, student_answers):
        """
        student_answers: list of dicts {'question_id': id, 'answer': text, 'marks': val}
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # 1. Insert into Results
                cursor.execute("""
                    INSERT INTO Results (exam_id, student_id, score, percentage, time_taken, feedback)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (exam_id, student_id, score, percentage, time_taken, feedback))
                cursor.execute("SELECT CAST(SCOPE_IDENTITY() AS INT)")
                row = cursor.fetchone()
                result_id = row[0] if row else -1

                # 2. Insert into StudentAnswers
                for ans in student_answers:
                    cursor.execute("""
                        INSERT INTO StudentAnswers (result_id, question_id, student_answer, marks_awarded)
                        VALUES (?, ?, ?, ?)
                    """, (result_id, ans['question_id'], str(ans['answer']), ans['marks']))
                
                # 3. Update Assignment Status
                cursor.execute("""
                    UPDATE ExamAssignments SET status = 'Completed'
                    WHERE exam_id = ? AND student_id = ?
                """, (exam_id, student_id))

                conn.commit()
                return result_id
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            raise QuizDatabaseError(f"Failed to save result: {e}")

    def get_result_by_id(self, result_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT r.id, r.exam_id, e.title, r.student_id, u.full_name, r.score, r.percentage, r.time_taken, r.feedback, r.attempt_date
                    FROM Results r
                    JOIN Exams e ON r.exam_id = e.id
                    JOIN Users u ON r.student_id = u.id
                    WHERE r.id = ?
                """, (result_id,))
                row = cursor.fetchone()
                if not row: return None
                
                result = {
                    'id': row[0], 'exam_id': row[1], 'exam_title': row[2], 'student_id': row[3],
                    'student_name': row[4], 'score': row[5], 'percentage': row[6],
                    'time_taken': row[7], 'feedback': row[8], 'date': row[9]
                }
                
                # Get detailed answers
                cursor.execute("""
                    SELECT sa.question_id, q.question_text, q.correct_answer, sa.student_answer, sa.marks_awarded, q.type
                    FROM StudentAnswers sa
                    JOIN Questions q ON sa.question_id = q.id
                    WHERE sa.result_id = ?
                """, (result_id,))
                ans_rows = cursor.fetchall()
                answers = []
                for a in ans_rows:
                    answers.append({
                        'question_id': a[0], 'question_text': a[1], 'correct_answer': a[2],
                        'student_answer': a[3], 'marks_awarded': a[4], 'type': a[5]
                    })
                result['answers'] = answers
                return result
        except Exception as e:
            logger.error(f"Error getting result: {e}")
            raise QuizDatabaseError(f"Failed to get result: {e}")

    def get_leaderboard(self, exam_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT TOP 5 u.full_name, r.score, r.percentage, r.time_taken
                    FROM Results r
                    JOIN Users u ON r.student_id = u.id
                    WHERE r.exam_id = ?
                    ORDER BY r.score DESC, r.time_taken ASC
                """, (exam_id,))
                rows = cursor.fetchall()
                leaderboard = []
                for row in rows:
                    leaderboard.append({
                        'student_name': row[0], 'score': row[1], 'percentage': row[2], 'time_taken': row[3]
                    })
                return leaderboard
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            raise QuizDatabaseError(f"Failed to get leaderboard: {e}")

    def log_hint_usage(self, question_id, student_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO HintLogs (question_id, student_id) VALUES (?, ?)", (question_id, student_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging hint: {e}")

    def get_exam_stats(self, exam_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT AVG(percentage) FROM Results WHERE exam_id = ?", (exam_id,))
                avg_score = cursor.fetchone()[0] or 0
                
                cursor.execute("""
                    SELECT COUNT(*) FROM Results r 
                    JOIN Exams e ON r.exam_id = e.id
                    WHERE r.exam_id = ? AND r.percentage >= e.pass_percentage
                """, (exam_id,))
                pass_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM Results WHERE exam_id = ?", (exam_id,))
                total_attempts = cursor.fetchone()[0]
                
                return {'avg_score': avg_score, 'pass_count': pass_count, 'fail_count': total_attempts - pass_count}
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'avg_score': 0, 'pass_count': 0, 'fail_count': 0}

    def get_submissions_by_exam(self, exam_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT r.id, u.full_name, r.score, r.percentage, r.attempt_date
                    FROM Results r
                    JOIN Users u ON r.student_id = u.id
                    WHERE r.exam_id = ?
                    ORDER BY r.attempt_date DESC
                """, (exam_id,))
                rows = cursor.fetchall()
                submissions = []
                for row in rows:
                    submissions.append({
                        'id': row[0], 'student_name': row[1], 'score': row[2],
                        'percentage': row[3], 'date': row[4]
                    })
                return submissions
        except Exception as e:
            logger.error(f"Error getting submissions: {e}")
            raise QuizDatabaseError(f"Failed to get submissions: {e}")

    def update_student_marks(self, result_id, question_id, new_marks):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Update marks for specific question
                cursor.execute("""
                    UPDATE StudentAnswers SET marks_awarded = ?
                    WHERE result_id = ? AND question_id = ?
                """, (new_marks, result_id, question_id))
                
                # Recalculate total score and percentage for the result
                cursor.execute("SELECT SUM(marks_awarded) FROM StudentAnswers WHERE result_id = ?", (result_id,))
                total_score = cursor.fetchone()[0] or 0
                
                cursor.execute("""
                    SELECT e.total_marks FROM Results r 
                    JOIN Exams e ON r.exam_id = e.id 
                    WHERE r.id = ?
                """, (result_id,))
                max_marks = cursor.fetchone()[0] or 1
                
                percentage = (total_score / max_marks) * 100
                
                cursor.execute("""
                    UPDATE Results SET score = ?, percentage = ?
                    WHERE id = ?
                """, (total_score, percentage, result_id))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating marks: {e}")
            raise QuizDatabaseError(f"Failed to update marks: {e}")

    def get_weak_topics(self, student_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT q.topic
                    FROM StudentAnswers sa
                    JOIN Questions q ON sa.question_id = q.id
                    JOIN Results r ON sa.result_id = r.id
                    WHERE r.student_id = ? AND (sa.marks_awarded = 0 OR sa.marks_awarded < 1)
                """, (student_id,))
                topics = [row[0] for row in cursor.fetchall() if row[0]]
                return topics
        except Exception as e:
            logger.error(f"Error getting weak topics: {e}")
            return []
