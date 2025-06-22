import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDateEdit
from PyQt5.QtCore import Qt, QDate
from business_management.database.db_manager import DBManager
from business_management.utils.helpers import (
    get_top_products_by_revenue, get_sales_by_day_of_week, get_sales_by_month,
    get_sales_heatmap_data, get_revenue_by_customer_segment
)
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bills.db')

class BusinessOverviewDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DBManager(DB_PATH)
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Business Overview & Analytics Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Date Range Filter
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-3))
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

        # Charts Section
        chart_layout1 = QHBoxLayout()
        self.fig1, self.ax1 = plt.subplots(figsize=(5, 3))
        self.canvas1 = FigureCanvas(self.fig1)
        chart_layout1.addWidget(self.canvas1)
        self.fig2, self.ax2 = plt.subplots(figsize=(5, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        chart_layout1.addWidget(self.canvas2)
        layout.addLayout(chart_layout1)

        chart_layout2 = QHBoxLayout()
        self.fig3, self.ax3 = plt.subplots(figsize=(5, 3))
        self.canvas3 = FigureCanvas(self.fig3)
        chart_layout2.addWidget(self.canvas3)
        self.fig4, self.ax4 = plt.subplots(figsize=(5, 3))
        self.canvas4 = FigureCanvas(self.fig4)
        chart_layout2.addWidget(self.canvas4)
        layout.addLayout(chart_layout2)

    def load_dashboard_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        # Top Products by Revenue
        top_products = get_top_products_by_revenue(self.db_manager, start, end)
        self.ax1.clear()
        if top_products:
            names, revenues = zip(*top_products)
            self.ax1.barh(names, revenues, color='teal')
            self.ax1.set_title('Top 10 Products by Revenue')
            self.ax1.set_xlabel('Revenue')
        else:
            self.ax1.set_title('No Data')
        self.fig1.tight_layout()
        self.canvas1.draw()
        # Sales by Day of Week
        sales_by_day = get_sales_by_day_of_week(self.db_manager, start, end)
        self.ax2.clear()
        if sales_by_day:
            days = list(sales_by_day.keys())
            amounts = list(sales_by_day.values())
            self.ax2.bar(days, amounts, color='orange')
            self.ax2.set_title('Sales by Day of Week')
            self.ax2.set_ylabel('Revenue')
        else:
            self.ax2.set_title('No Data')
        self.fig2.tight_layout()
        self.canvas2.draw()
        # Sales by Month
        sales_by_month = get_sales_by_month(self.db_manager, start, end)
        self.ax3.clear()
        if sales_by_month:
            months = list(sales_by_month.keys())
            amounts = list(sales_by_month.values())
            self.ax3.bar(months, amounts, color='blue')
            self.ax3.set_title('Sales by Month')
            self.ax3.set_ylabel('Revenue')
        else:
            self.ax3.set_title('No Data')
        self.fig3.tight_layout()
        self.canvas3.draw()
        # Sales Heatmap (Hour x Day)
        self.ax4.clear()
        heatmap = get_sales_heatmap_data(self.db_manager, start, end)
        if heatmap is not None and not heatmap.empty:
            import seaborn as sns
            sns.heatmap(heatmap, ax=self.ax4, cmap='YlGnBu')
            self.ax4.set_title('Sales Activity Heatmap (Hour x Day)')
        else:
            self.ax4.set_title('No Data')
        self.fig4.tight_layout()
        self.canvas4.draw()
        # Pie Chart: Revenue by Customer Segment (in ax3, overlay)
        seg_revenue = get_revenue_by_customer_segment(self.db_manager, start, end)
        if seg_revenue:
            self.fig3.clf()
            self.ax3 = self.fig3.add_subplot(111)
            self.ax3.pie(list(seg_revenue.values()), labels=list(seg_revenue.keys()), autopct='%1.1f%%', startangle=140)
            self.ax3.set_title('Revenue by Customer Segment')
            self.fig3.tight_layout()
            self.canvas3.draw() 