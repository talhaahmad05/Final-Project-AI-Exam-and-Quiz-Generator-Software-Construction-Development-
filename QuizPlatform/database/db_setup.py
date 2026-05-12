"""
filename: db_setup.py
module: Database Setup
author: Talha Ahmad
date: 2026-05-12
"""

import pyodbc
import hashlib
import json
import sys
import os

# Add the project root (parent directory of QuizPlatform) to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from QuizPlatform.config import DB_SERVER, DB_NAME, DB_TRUSTED
from QuizPlatform.utils.logger import get_logger
from QuizPlatform.exceptions import QuizDatabaseError

logger = get_logger(__name__)

def hash_password(password):
    """Hashes a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection_string(use_db=True):
    """Constructs the connection string for SQL Server"""
    conn_str = f"DRIVER={{SQL Server}};SERVER={DB_SERVER};"
    if use_db:
        conn_str += f"DATABASE={DB_NAME};"
    conn_str += f"Trusted_Connection={DB_TRUSTED};"
    return conn_str

def initialize_database():
    """Creates the database and tables if they don't exist"""
    try:
        # 1. Create Database if not exists
        conn = pyodbc.connect(get_connection_string(use_db=False), autocommit=True)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{DB_NAME}'")
        if not cursor.fetchone():
            logger.info(f"Creating database {DB_NAME}...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
        conn.close()

        # 2. Create Tables
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()

        # Users Table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
        CREATE TABLE Users (
            id INT PRIMARY KEY IDENTITY(1,1),
            username NVARCHAR(50) UNIQUE NOT NULL,
            password_hash NVARCHAR(64) NOT NULL,
            role NVARCHAR(20) NOT NULL, -- 'Admin', 'Student'
            full_name NVARCHAR(100) NOT NULL
        )
        """)

        # Questions Table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Questions' AND xtype='U')
        CREATE TABLE Questions (
            id INT PRIMARY KEY IDENTITY(1,1),
            question_text NVARCHAR(MAX) NOT NULL,
            options_json NVARCHAR(MAX), -- JSON array for MCQs
            correct_answer NVARCHAR(MAX) NOT NULL,
            type NVARCHAR(20) NOT NULL, -- 'MCQ', 'True/False', 'Short Answer'
            subject NVARCHAR(50) NOT NULL,
            difficulty NVARCHAR(20) NOT NULL, -- 'easy', 'medium', 'hard'
            topic NVARCHAR(100)
        )
        """)

        # Exams Table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Exams' AND xtype='U')
        CREATE TABLE Exams (
            id INT PRIMARY KEY IDENTITY(1,1),
            title NVARCHAR(100) NOT NULL,
            subject NVARCHAR(50) NOT NULL,
            time_limit INT NOT NULL, -- minutes
            total_marks INT NOT NULL,
            pass_percentage INT NOT NULL,
            shuffle_questions BIT DEFAULT 0,
            hints_enabled BIT DEFAULT 0
        )
        """)

        # ExamQuestions Junction Table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ExamQuestions' AND xtype='U')
        CREATE TABLE ExamQuestions (
            exam_id INT FOREIGN KEY REFERENCES Exams(id) ON DELETE CASCADE,
            question_id INT FOREIGN KEY REFERENCES Questions(id),
            order_index INT,
            PRIMARY KEY (exam_id, question_id)
        )
        """)

        # ExamAssignments Table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ExamAssignments' AND xtype='U')
        CREATE TABLE ExamAssignments (
            exam_id INT FOREIGN KEY REFERENCES Exams(id) ON DELETE CASCADE,
            student_id INT FOREIGN KEY REFERENCES Users(id) ON DELETE CASCADE,
            status NVARCHAR(20) DEFAULT 'Pending', -- 'Pending', 'Completed'
            PRIMARY KEY (exam_id, student_id)
        )
        """)

        # Results Table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Results' AND xtype='U')
        CREATE TABLE Results (
            id INT PRIMARY KEY IDENTITY(1,1),
            exam_id INT FOREIGN KEY REFERENCES Exams(id) ON DELETE CASCADE,
            student_id INT FOREIGN KEY REFERENCES Users(id),
            score FLOAT NOT NULL,
            percentage FLOAT NOT NULL,
            time_taken INT NOT NULL, -- seconds
            feedback NVARCHAR(MAX),
            attempt_date DATETIME DEFAULT GETDATE()
        )
        """)

        # StudentAnswers Table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='StudentAnswers' AND xtype='U')
        CREATE TABLE StudentAnswers (
            id INT PRIMARY KEY IDENTITY(1,1),
            result_id INT FOREIGN KEY REFERENCES Results(id) ON DELETE CASCADE,
            question_id INT FOREIGN KEY REFERENCES Questions(id),
            student_answer NVARCHAR(MAX),
            marks_awarded FLOAT
        )
        """)

        # HintLogs Table
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='HintLogs' AND xtype='U')
        CREATE TABLE HintLogs (
            id INT PRIMARY KEY IDENTITY(1,1),
            question_id INT FOREIGN KEY REFERENCES Questions(id),
            student_id INT FOREIGN KEY REFERENCES Users(id),
            timestamp DATETIME DEFAULT GETDATE()
        )
        """)

        conn.commit()
        logger.info("Tables checked/created successfully.")
        
        # 3. Insert Seed Data if Users table is empty
        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] == 0:
            logger.info("Inserting seed data...")
            
            # Admin
            cursor.execute("INSERT INTO Users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                           ('admin', hash_password('admin123'), 'Admin', 'Talha Ahmad'))
            
            # Students
            students = [
                ('student1', hash_password('student123'), 'Student', 'Ali Khan'),
                ('student2', hash_password('student123'), 'Student', 'Sara Ahmed'),
                ('student3', hash_password('student123'), 'Student', 'Zainab Bibi')
            ]
            for s in students:
                cursor.execute("INSERT INTO Users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)", s)

            # Sample Questions
            questions = [
                ("What is the time complexity of binary search?", json.dumps(["O(n)", "O(log n)", "O(n log n)", "O(1)"]), "O(log n)", "MCQ", "Computer Science", "easy", "Algorithms"),
                ("Python is an interpreted language.", None, "True", "True/False", "Computer Science", "easy", "Programming"),
                ("Explain the concept of Inheritance in OOP.", None, "Inheritance allows a class to inherit properties and methods from another class.", "Short Answer", "Computer Science", "medium", "OOP"),
                ("Which keyword is used to define a function in Python?", json.dumps(["func", "define", "def", "function"]), "def", "MCQ", "Computer Science", "easy", "Programming"),
                ("What does HTML stand for?", json.dumps(["Hyper Text Markup Language", "High Text Machine Language", "Hyper Tabular Multi Language", "None"]), "Hyper Text Markup Language", "MCQ", "Computer Science", "easy", "Web"),
                ("SQL is used for database management.", None, "True", "True/False", "Computer Science", "easy", "Databases"),
                ("What is a primary key?", None, "A unique identifier for a record in a database table.", "Short Answer", "Computer Science", "medium", "Databases"),
                ("Which of these is a Python data type?", json.dumps(["int", "float", "string", "All of these"]), "All of these", "MCQ", "Computer Science", "easy", "Programming"),
                ("What is the output of 2**3 in Python?", json.dumps(["5", "6", "8", "9"]), "8", "MCQ", "Computer Science", "easy", "Programming"),
                ("Git is a version control system.", None, "True", "True/False", "Computer Science", "easy", "DevOps")
            ]
            for q in questions:
                cursor.execute("INSERT INTO Questions (question_text, options_json, correct_answer, type, subject, difficulty, topic) VALUES (?, ?, ?, ?, ?, ?, ?)", q)

            # Sample Exams
            cursor.execute("INSERT INTO Exams (title, subject, time_limit, total_marks, pass_percentage, shuffle_questions, hints_enabled) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           ('Python Basics Quiz', 'Computer Science', 10, 5, 50, 0, 1))
            exam_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
            
            # Add first 5 questions to exam
            for i in range(1, 6):
                cursor.execute("INSERT INTO ExamQuestions (exam_id, question_id, order_index) VALUES (?, ?, ?)", (exam_id, i, i))
            
            # Assign to all students
            cursor.execute("SELECT id FROM Users WHERE role = 'Student'")
            student_ids = [row[0] for row in cursor.fetchall()]
            for sid in student_ids:
                cursor.execute("INSERT INTO ExamAssignments (exam_id, student_id) VALUES (?, ?)", (exam_id, sid))

            conn.commit()
            logger.info("Seed data inserted.")

        conn.close()

    except Exception as e:
        logger.error(f"Database setup error: {str(e)}")
        raise QuizDatabaseError(f"Failed to setup database: {str(e)}")

if __name__ == "__main__":
    initialize_database()
