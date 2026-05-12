"""
filename: reports_ui.py
module: Reports UI
author: Talha Ahmad
date: 2026-05-12
Sprint: 2 - Reports
"""

import csv
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                              QComboBox, QHeaderView, QFrame, QFileDialog, QTabWidget,
                              QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from QuizPlatform.dao.exam_dao import ExamDAO
from QuizPlatform.dao.result_dao import ResultDAO
from QuizPlatform.dao.student_dao import StudentDAO
from QuizPlatform.exceptions import QuizDatabaseError
from QuizPlatform.utils.logger import get_logger

logger = get_logger(__name__)


class ReportsUI(QWidget):
    """Reports and analytics screen for teachers"""

    def __init__(self):
        super().__init__()
        self.exam_dao = ExamDAO()
        self.result_dao = ResultDAO()
        self.student_dao = StudentDAO()
        self.all_exams = []
        self._build_ui()
        self._load_exams()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        hdr = QHBoxLayout()
        title = QLabel("📊 Reports & Analytics")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A1A2E;")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Exam selector
        sel_frame = QFrame()
        sel_frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #E0E0E0; padding: 10px;")
        sel_layout = QHBoxLayout(sel_frame)
        lbl_sel = QLabel("Select Exam to View Reports:")
        lbl_sel.setStyleSheet("color: #1A1A2E; font-weight: bold;")
        sel_layout.addWidget(lbl_sel)
        
        self.exam_combo = QComboBox()
        self.exam_combo.setFixedWidth(350)
        self.exam_combo.setFixedHeight(36)
        self.exam_combo.setStyleSheet("color: #1A1A2E; background-color: #FFFFFF; border: 1px solid #1565C0;")
        sel_layout.addWidget(self.exam_combo)
        
        btn_load = QPushButton("📈 Load Detailed Reports")
        btn_load.setFixedHeight(36)
        btn_load.clicked.connect(self.load_report)
        sel_layout.addWidget(btn_load)
        sel_layout.addStretch()
        layout.addWidget(sel_frame)

        # Stat cards row
        self.stats_row = QHBoxLayout()
        self.card_avg = self._make_card("Class Average", "--", "#1565C0")
        self.card_pass = self._make_card("Passed", "--", "#2E7D32")
        self.card_fail = self._make_card("Failed", "--", "#C62828")
        self.stats_row.addWidget(self.card_avg)
        self.stats_row.addWidget(self.card_pass)
        self.stats_row.addWidget(self.card_fail)
        layout.addLayout(self.stats_row)

        # Tabs for different reports
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab {
                background: #EEEEEE;
                color: #1A1A2E;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #1565C0;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #1565C0;
                border-radius: 8px;
                background: white;
            }
        """)

        # Leaderboard
        lb_tab = QWidget()
        lb_layout = QVBoxLayout(lb_tab)
        self.lb_table = self._make_table(["Rank", "Student Name", "Score", "Percentage", "Time Taken"])
        btn_export_lb = QPushButton("📥 Export Leaderboard CSV")
        btn_export_lb.setFixedHeight(34)
        btn_export_lb.clicked.connect(lambda: self._export_csv(self.lb_table, "leaderboard"))
        lb_layout.addWidget(self.lb_table)
        lb_layout.addWidget(btn_export_lb)
        tabs.addTab(lb_tab, "🏆 Leaderboard")

        # Per-student performance
        perf_tab = QWidget()
        perf_layout = QVBoxLayout(perf_tab)
        self.perf_table = self._make_table(["Student", "Exam", "Score", "Percentage", "Date"])
        btn_export_perf = QPushButton("📥 Export Performance CSV")
        btn_export_perf.setFixedHeight(34)
        btn_export_perf.clicked.connect(lambda: self._export_csv(self.perf_table, "student_performance"))
        perf_layout.addWidget(self.perf_table)
        perf_layout.addWidget(btn_export_perf)
        tabs.addTab(perf_tab, "👤 Student Performance")

        # Submissions (Manual Grading)
        sub_tab = QWidget()
        sub_layout = QVBoxLayout(sub_tab)
        self.sub_table = self._make_table(["ID", "Student", "Score", "Percentage", "Date", "Review / Grade"])
        sub_layout.addWidget(self.sub_table)
        tabs.addTab(sub_tab, "📝 Review Submissions")

        layout.addWidget(tabs)
        print(f"DEBUG: Reports UI built with {tabs.count()} tabs.")

    def _make_card(self, title, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background-color: {color}; border-radius: 12px; }}
        """)
        frame.setFixedHeight(90)
        card_layout = QVBoxLayout(frame)
        card_layout.setAlignment(Qt.AlignCenter)
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 10))
        lbl_title.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_value.setStyleSheet("color: white; background: transparent;")
        lbl_value.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_value)
        frame._value_label = lbl_value
        return frame

    def _make_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; color: #1A1A2E; }
            QHeaderView::section { background-color: #F5F5F5; color: #1A1A2E; font-weight: bold; padding: 5px; }
        """)
        return table

    def _load_exams(self):
        try:
            self.all_exams = self.exam_dao.get_all_exams()
            for exam in self.all_exams:
                self.exam_combo.addItem(exam['title'], userData=exam['id'])
        except QuizDatabaseError as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def load_report(self):
        exam_id = self.exam_combo.currentData()
        print(f"DEBUG: Loading report for Exam ID: {exam_id}")
        if not exam_id:
            print("DEBUG: No exam ID selected in combo box.")
            return
        try:
            # Stats
            stats = self.result_dao.get_exam_stats(exam_id)
            self.card_avg._value_label.setText(f"{stats['avg_score']:.1f}%")
            self.card_pass._value_label.setText(str(stats['pass_count']))
            self.card_fail._value_label.setText(str(stats['fail_count']))

            # Leaderboard
            leaderboard = self.result_dao.get_leaderboard(exam_id)
            self.lb_table.setRowCount(len(leaderboard))
            for i, entry in enumerate(leaderboard):
                self.lb_table.setItem(i, 0, QTableWidgetItem(f"#{i+1}"))
                self.lb_table.setItem(i, 1, QTableWidgetItem(entry['student_name']))
                self.lb_table.setItem(i, 2, QTableWidgetItem(str(entry['score'])))
                self.lb_table.setItem(i, 3, QTableWidgetItem(f"{entry['percentage']:.1f}%"))
                mins, secs = divmod(entry['time_taken'], 60)
                self.lb_table.setItem(i, 4, QTableWidgetItem(f"{mins}m {secs}s"))

            self._load_performance(exam_id)
            self._load_submissions(exam_id)
            
            print(f"DEBUG: Loaded {len(leaderboard)} leaderboard entries.")

        except QuizDatabaseError as e:
            print(f"DEBUG ERROR: {e}")
            QMessageBox.critical(self, "DB Error", str(e))

    def _load_performance(self, exam_id):
        try:
            results = self.result_dao.get_submissions_by_exam(exam_id)
            print(f"DEBUG: Found {len(results)} performance results for Exam ID {exam_id}")
            self.perf_table.setRowCount(len(results))
            for i, r in enumerate(results):
                self.perf_table.setItem(i, 0, QTableWidgetItem(r['student_name']))
                self.perf_table.setItem(i, 1, QTableWidgetItem("Exam Result"))
                self.perf_table.setItem(i, 2, QTableWidgetItem(str(r['score'])))
                self.perf_table.setItem(i, 3, QTableWidgetItem(f"{r['percentage']:.1f}%"))
                self.perf_table.setItem(i, 4, QTableWidgetItem(str(r['date'])))
        except Exception as e:
            print(f"DEBUG ERROR in _load_performance: {e}")

    def _load_submissions(self, exam_id):
        try:
            subs = self.result_dao.get_submissions_by_exam(exam_id)
            print(f"DEBUG: Found {len(subs)} submissions for Review in Exam ID {exam_id}")
            self.sub_table.setRowCount(len(subs))
            for i, s in enumerate(subs):
                self.sub_table.setItem(i, 0, QTableWidgetItem(str(s['id'])))
                self.sub_table.setItem(i, 1, QTableWidgetItem(s['student_name']))
                self.sub_table.setItem(i, 2, QTableWidgetItem(str(s['score'])))
                self.sub_table.setItem(i, 3, QTableWidgetItem(f"{s['percentage']:.1f}%"))
                self.sub_table.setItem(i, 4, QTableWidgetItem(str(s['date'])))
                
                btn_grade = QPushButton("📝 Review/Grade")
                btn_grade.clicked.connect(lambda _, r_id=s['id']: self._open_grading(r_id))
                self.sub_table.setCellWidget(i, 5, btn_grade)
        except Exception as e:
            logger.error(f"Error loading submissions: {e}")

    def _open_grading(self, result_id):
        from QuizPlatform.ui.grading_ui import GradingDialog
        dlg = GradingDialog(self, result_id)
        if dlg.exec_() == QDialog.Accepted:
            self.load_report() # Refresh

    def _export_csv(self, table, filename_prefix):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report",
                                                    f"{filename_prefix}.csv", "CSV Files (*.csv)")
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                headers = [table.horizontalHeaderItem(c).text() for c in range(table.columnCount())]
                writer.writerow(headers)
                # Data
                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            QMessageBox.information(self, "Exported", f"Report saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
