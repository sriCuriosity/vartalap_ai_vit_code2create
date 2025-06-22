import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton, QFileDialog, QDateEdit, QLineEdit, QComboBox, QDialog, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import Qt, QDate
from business_management.database.db_manager import DBManager
from business_management.utils.helpers import get_expense_summary, get_revenue_and_profit
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bills.db')

class ExpenseDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DBManager(DB_PATH)
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Expense Tracking & Profit/Loss Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Date Range Filter
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        filter_btn = QPushButton("Apply Date Filter")
        filter_btn.clicked.connect(self.load_dashboard_data)
        date_layout.addWidget(filter_btn)
        layout.addLayout(date_layout)

        # KPI Section
        kpi_layout = QHBoxLayout()
        self.revenue_label = self._create_kpi_label("Total Revenue\n-")
        self.expense_label = self._create_kpi_label("Total Expenses\n-")
        self.profit_label = self._create_kpi_label("Net Profit\n-")
        kpi_layout.addWidget(self.revenue_label)
        kpi_layout.addWidget(self.expense_label)
        kpi_layout.addWidget(self.profit_label)
        layout.addLayout(kpi_layout)

        # Charts Section
        chart_layout = QHBoxLayout()
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        chart_layout.addWidget(self.canvas)
        self.fig2, self.ax2 = plt.subplots(figsize=(5, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        chart_layout.addWidget(self.canvas2)
        layout.addLayout(chart_layout)

        # Expense Table
        table_title = QLabel("Expenses Table")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(table_title)
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(4)
        self.expense_table.setHorizontalHeaderLabels(["Date", "Amount", "Category", "Description"])
        self.expense_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.expense_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        vertical_header = self.expense_table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        horizontal_header = self.expense_table.horizontalHeader()
        if horizontal_header is not None:
            horizontal_header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.expense_table)

        # Add/Export Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Expense")
        add_btn.clicked.connect(self.add_expense_dialog)
        btn_layout.addWidget(add_btn)
        export_btn = QPushButton("Export Expenses to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        btn_layout.addWidget(export_btn)
        layout.addLayout(btn_layout)

    def _create_kpi_label(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        """)
        return label

    def load_dashboard_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        expense_summary = get_expense_summary(self.db_manager, start, end)
        rev_profit = get_revenue_and_profit(self.db_manager, start, end)
        # KPIs
        self.revenue_label.setText(f"Total Revenue\n${rev_profit['total_revenue']:,.2f}")
        self.expense_label.setText(f"Total Expenses\n${expense_summary['total_expenses']:,.2f}")
        self.profit_label.setText(f"Net Profit\n${rev_profit['net_profit'] - expense_summary['total_expenses']:,.2f}")
        # Line Chart: Revenue, Expenses, Profit over Time
        self.ax.clear()
        # For simplicity, use daily sums
        bills = self.db_manager.get_bills(start, end)
        bills_df = pd.DataFrame([{ 'date': b.date, 'revenue': b.total_amount } for b in bills])
        if not bills_df.empty:
            bills_df['date'] = pd.to_datetime(bills_df['date'])
            bills_df = bills_df.groupby('date').sum().sort_index()
        expenses = expense_summary['expenses']
        exp_df = pd.DataFrame([{ 'date': e.date, 'expense': e.amount } for e in expenses])
        if not exp_df.empty:
            exp_df['date'] = pd.to_datetime(exp_df['date'])
            exp_df = exp_df.groupby('date').sum().sort_index()
        all_dates = pd.date_range(start, end)
        bills_df = bills_df.reindex(all_dates, fill_value=0)
        if not isinstance(exp_df, pd.DataFrame):
            exp_df = pd.DataFrame(index=all_dates)
        if 'expense' not in exp_df.columns:
            exp_df['expense'] = 0
        profit_series = bills_df['revenue'] - exp_df['expense']
        self.ax.plot(all_dates, bills_df['revenue'], label='Revenue')
        self.ax.plot(all_dates, exp_df['expense'], label='Expenses')
        self.ax.plot(all_dates, profit_series, label='Profit')
        self.ax.set_title('Revenue, Expenses, Profit Over Time')
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()
        # Pie Chart: Expense by Category
        self.ax2.clear()
        by_cat = expense_summary['by_category']
        if by_cat:
            self.ax2.pie(list(by_cat.values()), labels=list(by_cat.keys()), autopct='%1.1f%%', startangle=140)
            self.ax2.set_title('Expense Breakdown by Category')
        else:
            self.ax2.text(0.5, 0.5, 'No expenses', ha='center', va='center')
        self.fig2.tight_layout()
        self.canvas2.draw()
        # Table
        self.expense_table.setRowCount(0)
        for i, e in enumerate(expense_summary['expenses']):
            self.expense_table.insertRow(i)
            self.expense_table.setItem(i, 0, QTableWidgetItem(e.date))
            self.expense_table.setItem(i, 1, QTableWidgetItem(f"${e.amount:,.2f}"))
            self.expense_table.setItem(i, 2, QTableWidgetItem(e.category))
            self.expense_table.setItem(i, 3, QTableWidgetItem(e.description))

    def add_expense_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Expense")
        form = QFormLayout(dialog)
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        amount_edit = QLineEdit()
        category_edit = QLineEdit()
        desc_edit = QLineEdit()
        form.addRow("Date:", date_edit)
        form.addRow("Amount:", amount_edit)
        form.addRow("Category:", category_edit)
        form.addRow("Description:", desc_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(buttons)
        def on_accept():
            date = date_edit.date().toString("yyyy-MM-dd")
            try:
                amount = float(amount_edit.text())
            except ValueError:
                amount = 0.0
            category = category_edit.text() or "Uncategorized"
            desc = desc_edit.text()
            if amount > 0:
                self.db_manager.add_expense(date, amount, category, desc)
                dialog.accept()
                self.load_dashboard_data()
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Expenses", "expenses.csv", "CSV Files (*.csv)")
        if not path:
            return
        # Gather table data
        data = []
        for row in range(self.expense_table.rowCount()):
            row_data = []
            for col in range(self.expense_table.columnCount()):
                item = self.expense_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        df = pd.DataFrame(data, columns=["Date", "Amount", "Category", "Description"])
        df.to_csv(path, index=False) 