import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton, QDateEdit
from PyQt5.QtCore import Qt, QDate
from business_management.database.db_manager import DBManager
from business_management.utils.helpers import get_best_worst_selling_products, get_product_sales_trends, get_app_path
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

DB_PATH = os.path.join(get_app_path(), 'bills.db')

class ProductAnalysisDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DBManager(DB_PATH)
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Product & Inventory Analysis Dashboard")
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

        # Best/Worst Sellers Section
        kpi_layout = QHBoxLayout()
        self.best_label = self._create_kpi_label("Top Sellers\n-")
        self.worst_label = self._create_kpi_label("Slow Movers\n-")
        kpi_layout.addWidget(self.best_label)
        kpi_layout.addWidget(self.worst_label)
        layout.addLayout(kpi_layout)

        # Bar Charts Section
        chart_layout = QHBoxLayout()
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        chart_layout.addWidget(self.canvas)
        self.fig2, self.ax2 = plt.subplots(figsize=(5, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        chart_layout.addWidget(self.canvas2)
        layout.addLayout(chart_layout)

        # Product Trends Table
        table_title = QLabel("Product Sales Trends Table")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(table_title)
        self.trend_table = QTableWidget()
        self.trend_table.setColumnCount(3)
        self.trend_table.setHorizontalHeaderLabels(["Product", "Date", "Quantity Sold"])
        self.trend_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.trend_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.trend_table.verticalHeader().setVisible(False)
        self.trend_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.trend_table)

    def _create_kpi_label(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
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
        best, worst = get_best_worst_selling_products(self.db_manager, start, end)
        # KPIs
        self.best_label.setText("Top Sellers\n" + ", ".join([b['product_name'] for b in best if b['product_name']]))
        self.worst_label.setText("Slow Movers\n" + ", ".join([w['product_name'] for w in worst if w['product_name']]))
        # Bar Charts
        self.ax.clear()
        if best:
            names = [b['product_name'] for b in best]
            qtys = [b['total_quantity'] for b in best]
            self.ax.barh(names, qtys, color='green')
            self.ax.set_title('Top 5 Best-Selling Products (by Quantity)')
            self.ax.set_xlabel('Units Sold')
        else:
            self.ax.set_title('No Data')
        self.fig.tight_layout()
        self.canvas.draw()
        self.ax2.clear()
        if worst:
            names = [w['product_name'] for w in worst]
            qtys = [w['total_quantity'] for w in worst]
            self.ax2.barh(names, qtys, color='red')
            self.ax2.set_title('Bottom 5 Slowest-Selling Products (by Quantity)')
            self.ax2.set_xlabel('Units Sold')
        else:
            self.ax2.set_title('No Data')
        self.fig2.tight_layout()
        self.canvas2.draw()
        # Product Sales Trends Table
        trends = get_product_sales_trends(self.db_manager, start, end)
        self.trend_table.setRowCount(0)
        for product, date_qty in trends.items():
            for date, qty in date_qty.items():
                row = self.trend_table.rowCount()
                self.trend_table.insertRow(row)
                self.trend_table.setItem(row, 0, QTableWidgetItem(product))
                self.trend_table.setItem(row, 1, QTableWidgetItem(date))
                self.trend_table.setItem(row, 2, QTableWidgetItem(str(qty))) 