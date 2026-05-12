"""
filename: main.py
module: Entry Point
author: Talha Ahmad
date: 2026-05-13
Version: 2.2 (Theme Engine)
"""

import sys
import os

# Add the project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication, QStackedWidget, QMessageBox
from QuizPlatform.ui.login_ui import LoginScreen
from QuizPlatform.ui.teacher_dashboard import TeacherDashboard
from QuizPlatform.ui.student_dashboard import StudentDashboard
from QuizPlatform.database.db_setup import initialize_database
from QuizPlatform.config import APP_TITLE
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)

# --- Theme Definitions (Restored High Contrast) ---

LIGHT_THEME = """
    QMainWindow, QWidget { background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif; color: #1A1A2E; }
    QLabel { color: #1A1A2E; }
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QListWidget { 
        background-color: #FFFFFF; color: #1A1A2E; border: 1px solid #CCCCCC; border-radius: 6px; padding: 5px; 
    }
    QTableWidget { background-color: #FFFFFF; color: #1A1A2E; gridline-color: #EEEEEE; border: 1px solid #DDDDDD; }
    QHeaderView::section { background-color: #F5F5F5; color: #1A1A2E; font-weight: bold; border: 1px solid #DDDDDD; }
    QTabWidget::pane { border: 1px solid #1565C0; background: white; }
    QTabBar::tab { background: #EEEEEE; color: #1A1A2E; padding: 8px 15px; }
    QTabBar::tab:selected { background: #1565C0; color: white; }
    
    /* USER REQUESTED: GREEN BACKGROUND, RED TEXT FOR ALL BUTTONS */
    QPushButton { 
        background-color: #2E7D32; 
        color: #FF0000; 
        border-radius: 8px; 
        padding: 10px 18px; 
        font-weight: bold; 
        border: 2px solid #1B5E20; 
        font-size: 13px;
    }
    QPushButton:hover { background-color: #388E3C; border: 2px solid #FF0000; }
    QPushButton:pressed { background-color: #1B5E20; color: #FF8A80; }
    
    /* Ensure semantic IDs also follow the rule */
    /* Ensure semantic IDs also follow the rule */
    QPushButton#btn_submit, QPushButton#btn_create, QPushButton#btn_save,
    QPushButton#btn_logout, QPushButton#btn_delete, QPushButton#btn_cancel { 
        background-color: #2E7D32; color: #FF0000; border: 2px solid #1B5E20;
    }
"""

class QuizApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 750)
        
        self.login_screen = LoginScreen(self)
        self.teacher_dashboard = None
        self.student_dashboard = None
        
        self.addWidget(self.login_screen)
        self.setCurrentWidget(self.login_screen)

    def show_teacher_dashboard(self, user):
        self.teacher_dashboard = TeacherDashboard(self, user)
        self.addWidget(self.teacher_dashboard)
        self.setCurrentWidget(self.teacher_dashboard)

    def show_student_dashboard(self, user):
        self.student_dashboard = StudentDashboard(self, user)
        self.addWidget(self.student_dashboard)
        self.setCurrentWidget(self.student_dashboard)

    def logout(self):
        self.setCurrentWidget(self.login_screen)
        if self.teacher_dashboard:
            self.removeWidget(self.teacher_dashboard)
            self.teacher_dashboard = None
        if self.student_dashboard:
            self.removeWidget(self.student_dashboard)
            self.student_dashboard = None

def main():
    print("--- QuizAI Platform Version 2.2 (Premium Theme Engine) Starting ---")
    try:
        initialize_database()
        app = QApplication(sys.argv)
        app.setStyleSheet(LIGHT_THEME)
        
        window = QuizApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        if QApplication.instance():
            QMessageBox.critical(None, "Critical Error", f"Application failed to start:\n{str(e)}")
        else:
            print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    main()
