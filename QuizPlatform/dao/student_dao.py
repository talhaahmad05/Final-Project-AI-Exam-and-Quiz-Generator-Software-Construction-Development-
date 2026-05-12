"""
filename: student_dao.py
module: Student Data Access Object
author: Talha Ahmad
date: 2026-05-12
"""

import pyodbc
import hashlib
from QuizPlatform.config import DB_SERVER, DB_NAME, DB_TRUSTED
from QuizPlatform.utils.logger import get_logger
from QuizPlatform.exceptions import QuizDatabaseError, QuizAuthError

logger = get_logger(__name__)

class StudentDAO:
    def __init__(self):
        self.conn_str = f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection={DB_TRUSTED};"

    def get_connection(self):
        return pyodbc.connect(self.conn_str)

    def authenticate(self, username, password):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("SELECT id, username, role, full_name FROM Users WHERE username=? AND password_hash=?", (username, pwd_hash))
                row = cursor.fetchone()
                if row:
                    return {'id': row[0], 'username': row[1], 'role': row[2], 'full_name': row[3]}
                else:
                    raise QuizAuthError("Invalid username or password")
        except QuizAuthError:
            raise
        except Exception as e:
            logger.error(f"Auth error: {e}")
            raise QuizDatabaseError(f"Database error during authentication: {e}")

    def change_password(self, user_id, new_password):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                pwd_hash = hashlib.sha256(new_password.encode()).hexdigest()
                cursor.execute("UPDATE Users SET password_hash=? WHERE id=?", (pwd_hash, user_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Password change error: {e}")
            raise QuizDatabaseError(f"Failed to change password: {e}")

    def get_assigned_exams(self, student_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT e.id, e.title, e.subject, e.time_limit, e.total_marks, ea.status
                    FROM Exams e
                    JOIN ExamAssignments ea ON e.id = ea.exam_id
                    WHERE ea.student_id = ?
                """, (student_id,))
                rows = cursor.fetchall()
                exams = []
                for row in rows:
                    exams.append({
                        'id': row[0],
                        'title': row[1],
                        'subject': row[2],
                        'time_limit': row[3],
                        'total_marks': row[4],
                        'status': row[5]
                    })
                return exams
        except Exception as e:
            logger.error(f"Error getting assigned exams: {e}")
            raise QuizDatabaseError(f"Failed to get assigned exams: {e}")

    def get_student_results(self, student_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT r.id, e.title, r.score, r.percentage, r.attempt_date
                    FROM Results r
                    JOIN Exams e ON r.exam_id = e.id
                    WHERE r.student_id = ?
                    ORDER BY r.attempt_date DESC
                """, (student_id,))
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append({
                        'id': row[0],
                        'exam_title': row[1],
                        'score': row[2],
                        'percentage': row[3],
                        'date': row[4].strftime("%Y-%m-%d %H:%M")
                    })
                return results
        except Exception as e:
            logger.error(f"Error getting student results: {e}")
            raise QuizDatabaseError(f"Failed to get student results: {e}")

    def get_all_students(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, full_name FROM Users WHERE role = 'Student'")
                rows = cursor.fetchall()
                students = []
                for row in rows:
                    students.append({'id': row[0], 'username': row[1], 'full_name': row[2]})
                return students
        except Exception as e:
            logger.error(f"Error getting students: {e}")
            raise QuizDatabaseError(f"Failed to get students: {e}")
    def add_student(self, username, password, full_name):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO Users (username, password_hash, role, full_name)
                    VALUES (?, ?, ?, ?)
                """, (username, pwd_hash, 'Student', full_name))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding student: {e}")
            raise QuizDatabaseError(f"Failed to add student. Username may already exist.")

    def delete_student(self, student_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Remove assignments first
                cursor.execute("DELETE FROM ExamAssignments WHERE student_id=?", (student_id,))
                # Remove results
                cursor.execute("DELETE FROM Results WHERE student_id=?", (student_id,))
                # Remove user
                cursor.execute("DELETE FROM Users WHERE id=? AND role='Student'", (student_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting student: {e}")
            raise QuizDatabaseError(f"Failed to delete student: {e}")
