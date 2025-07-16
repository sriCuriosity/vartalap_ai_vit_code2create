import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton, QDateEdit
from PyQt5.QtCore import Qt, QDate
from business_management.database.db_manager import DBManager
from business_management.utils.helpers import get_customer_rfm_segments, get_customer_purchase_patterns, get_app_path
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

DB_PATH = os.path.join(get_app_path(), 'bills.db')

class CustomerBehaviorDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DBManager(DB_PATH)
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Customer Behavior Analysis (CRM Insights)")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Date Range Filter
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
        filter_btn = QPushButton("Apply Date Filter")
        filter_btn.clicked.connect(self.load_dashboard_data)
        date_layout.addWidget(filter_btn)
        layout.addLayout(date_layout)

        # KPI Section
        kpi_layout = QHBoxLayout()
        self.high_value_label = self._create_kpi_label("High-Value\n-")
        self.loyal_label = self._create_kpi_label("Loyal\n-")
        self.at_risk_label = self._create_kpi_label("At-Risk\n-")
        self.new_label = self._create_kpi_label("New\n-")
        kpi_layout.addWidget(self.high_value_label)
        kpi_layout.addWidget(self.loyal_label)
        kpi_layout.addWidget(self.at_risk_label)
        kpi_layout.addWidget(self.new_label)
        layout.addLayout(kpi_layout)

        # RFM Table
        table_title = QLabel("Customer Segmentation Table (RFM)")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(table_title)
        self.rfm_table = QTableWidget()
        self.rfm_table.setColumnCount(5)
        self.rfm_table.setHorizontalHeaderLabels(["Customer Key", "Recency (days)", "Frequency", "Monetary", "Segment"])
        self.rfm_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.rfm_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.rfm_table.verticalHeader().setVisible(False)
        self.rfm_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.rfm_table)

        # Visualizations
        vis_layout = QHBoxLayout()
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        vis_layout.addWidget(self.canvas)
        self.fig2, self.ax2 = plt.subplots(figsize=(5, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        vis_layout.addWidget(self.canvas2)
        layout.addLayout(vis_layout)

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
        rfm = get_customer_rfm_segments(self.db_manager, start, end)
        patterns = get_customer_purchase_patterns(self.db_manager, start, end)
        # KPIs
        df = pd.DataFrame(rfm)
        self.high_value_label.setText(f"High-Value\n{(df['segment'] == 'High-Value').sum() if not df.empty else 0}")
        self.loyal_label.setText(f"Loyal\n{(df['segment'] == 'Loyal').sum() if not df.empty else 0}")
        self.at_risk_label.setText(f"At-Risk\n{(df['segment'] == 'At-Risk').sum() if not df.empty else 0}")
        self.new_label.setText(f"New\n{(df['segment'] == 'New').sum() if not df.empty else 0}")
        # RFM Table
        self.rfm_table.setRowCount(0)
        for i, row in enumerate(rfm):
            self.rfm_table.insertRow(i)
            self.rfm_table.setItem(i, 0, QTableWidgetItem(str(row['customer_key'])))
            self.rfm_table.setItem(i, 1, QTableWidgetItem(str(row['recency'])))
            self.rfm_table.setItem(i, 2, QTableWidgetItem(str(row['frequency'])))
            self.rfm_table.setItem(i, 3, QTableWidgetItem(f"${row['monetary']:,.2f}"))
            self.rfm_table.setItem(i, 4, QTableWidgetItem(row['segment']))
        # Bar Chart: Segment Counts
        self.ax.clear()
        if not df.empty:
            seg_counts = df['segment'].value_counts()
            self.ax.bar(seg_counts.index, seg_counts.values, color=['gold', 'blue', 'orange', 'green', 'gray'])
            self.ax.set_title('Customer Segments (Count)')
            self.ax.set_ylabel('Number of Customers')
        else:
            self.ax.set_title('No Data')
        self.fig.tight_layout()
        self.canvas.draw()
        # Bar Chart: Avg Days Between Purchases (Top 10)
        self.ax2.clear()
        avg_days = [(k, v['avg_days_between']) for k, v in patterns.items() if v['avg_days_between'] is not None]
        avg_days = sorted(avg_days, key=lambda x: x[1])[:10]
        if avg_days:
            keys = [k for k, _ in avg_days]
            vals = [v for _, v in avg_days]
            self.ax2.barh(keys, vals, color='purple')
            self.ax2.set_title('Avg Days Between Purchases (Top 10)')
            self.ax2.set_xlabel('Days')
        else:
            self.ax2.set_title('No Data')
        self.fig2.tight_layout()
        self.canvas2.draw() 