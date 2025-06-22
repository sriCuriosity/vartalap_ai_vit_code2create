import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton, QDateEdit, QComboBox
from PyQt5.QtCore import Qt, QDate
from business_management.database.db_manager import DBManager
from business_management.utils.helpers import (
    predict_churned_customers, recommend_products_for_customer,
    detect_sales_anomalies, detect_expense_anomalies
)
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bills.db')

class AdvancedAnalyticsDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DBManager(DB_PATH)
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Advanced Analytics Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Date Range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-6))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        filter_btn = QPushButton("Refresh")
        filter_btn.clicked.connect(self.load_dashboard_data)
        date_layout.addWidget(filter_btn)
        layout.addLayout(date_layout)

        # Churned Customers Table
        churn_title = QLabel("Churned Customers (No Purchase > 60 days)")
        churn_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(churn_title)
        self.churn_table = QTableWidget()
        self.churn_table.setColumnCount(4)
        self.churn_table.setHorizontalHeaderLabels(["Customer Key", "Recency (days)", "Frequency", "Monetary"])
        self.churn_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.churn_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.churn_table.verticalHeader().setVisible(False)
        self.churn_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.churn_table)

        # Product Recommendation Section
        rec_layout = QHBoxLayout()
        rec_layout.addWidget(QLabel("Select Customer:"))
        self.customer_combo = QComboBox()
        rec_layout.addWidget(self.customer_combo)
        rec_btn = QPushButton("Recommend Products")
        rec_btn.clicked.connect(self.show_recommendations)
        rec_layout.addWidget(rec_btn)
        self.rec_label = QLabel("")
        rec_layout.addWidget(self.rec_label)
        layout.addLayout(rec_layout)

        # Sales Anomalies Table
        sales_anom_title = QLabel("Sales Anomalies (Unusual Days)")
        sales_anom_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(sales_anom_title)
        self.sales_anom_table = QTableWidget()
        self.sales_anom_table.setColumnCount(2)
        self.sales_anom_table.setHorizontalHeaderLabels(["Date", "Sales Amount"])
        self.sales_anom_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sales_anom_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sales_anom_table.verticalHeader().setVisible(False)
        self.sales_anom_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.sales_anom_table)

        # Expense Anomalies Table
        exp_anom_title = QLabel("Expense Anomalies (Unusual Days)")
        exp_anom_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(exp_anom_title)
        self.exp_anom_table = QTableWidget()
        self.exp_anom_table.setColumnCount(2)
        self.exp_anom_table.setHorizontalHeaderLabels(["Date", "Expense Amount"])
        self.exp_anom_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.exp_anom_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.exp_anom_table.verticalHeader().setVisible(False)
        self.exp_anom_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.exp_anom_table)

    def load_dashboard_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        # Churned Customers
        churned = predict_churned_customers(self.db_manager, start, end)
        self.churn_table.setRowCount(0)
        for i, row in enumerate(churned):
            self.churn_table.insertRow(i)
            self.churn_table.setItem(i, 0, QTableWidgetItem(str(row['customer_key'])))
            self.churn_table.setItem(i, 1, QTableWidgetItem(str(row['recency'])))
            self.churn_table.setItem(i, 2, QTableWidgetItem(str(row['frequency'])))
            self.churn_table.setItem(i, 3, QTableWidgetItem(f"${row['monetary']:,.2f}"))
        # Customer Combo for Recommendations
        all_customers = list({row['customer_key'] for row in churned})
        self.customer_combo.clear()
        self.customer_combo.addItems(all_customers)
        self.rec_label.setText("")
        # Sales Anomalies
        sales_anom = detect_sales_anomalies(self.db_manager, start, end)
        self.sales_anom_table.setRowCount(0)
        for i, row in enumerate(sales_anom):
            self.sales_anom_table.insertRow(i)
            self.sales_anom_table.setItem(i, 0, QTableWidgetItem(str(row['date'].date())))
            self.sales_anom_table.setItem(i, 1, QTableWidgetItem(f"${row['amount']:,.2f}"))
        # Expense Anomalies
        exp_anom = detect_expense_anomalies(self.db_manager, start, end)
        self.exp_anom_table.setRowCount(0)
        for i, row in enumerate(exp_anom):
            self.exp_anom_table.insertRow(i)
            self.exp_anom_table.setItem(i, 0, QTableWidgetItem(str(row['date'].date())))
            self.exp_anom_table.setItem(i, 1, QTableWidgetItem(f"${row['amount']:,.2f}"))

    def show_recommendations(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        customer_key = self.customer_combo.currentText()
        if not customer_key:
            self.rec_label.setText("No customer selected.")
            return
        recs = recommend_products_for_customer(self.db_manager, customer_key, start, end)
        if recs:
            self.rec_label.setText("Recommended: " + ", ".join(recs))
        else:
            self.rec_label.setText("No recommendations.") 