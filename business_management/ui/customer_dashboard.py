import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton, QFileDialog, QDateEdit
from PyQt5.QtCore import Qt, QDate
from business_management.database.db_manager import DBManager
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from business_management.utils.customer_profitability import compute_customer_profitability

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bills.db')

class CustomerDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DBManager(DB_PATH)
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Customer Profitability Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Date Range Filter
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
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
        self.total_customers_label = self._create_kpi_label("Total Customers\n-")
        self.most_profitable_label = self._create_kpi_label("Most Profitable\n-")
        self.loss_accounts_label = self._create_kpi_label("Loss-Making Accounts\n-")
        kpi_layout.addWidget(self.total_customers_label)
        kpi_layout.addWidget(self.most_profitable_label)
        kpi_layout.addWidget(self.loss_accounts_label)
        layout.addLayout(kpi_layout)

        # Customer Profitability Table
        table_title = QLabel("Customer Profitability Table")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(table_title)

        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(7)
        self.customer_table.setHorizontalHeaderLabels([
            "Customer Key", "Total Revenue", "Total Cost", "Total Profit", "Profit Margin %", "No. of Bills", "Segment"
        ])
        self.customer_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customer_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.customer_table.verticalHeader().setVisible(False)  # type: ignore
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore
        layout.addWidget(self.customer_table)

        # Visualization Section
        vis_title = QLabel("Profitability Quadrant & Contribution Treemap")
        vis_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(vis_title)

        vis_layout = QHBoxLayout()
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        vis_layout.addWidget(self.canvas)
        self.fig2, self.ax2 = plt.subplots(figsize=(5, 3))
        self.canvas2 = FigureCanvas(self.fig2)
        vis_layout.addWidget(self.canvas2)
        layout.addLayout(vis_layout)

        # Export Button
        export_btn = QPushButton("Export Analysis to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        layout.addWidget(export_btn)

    def _create_kpi_label(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)  # type: ignore
        label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        """)
        return label

    def load_dashboard_data(self):
        # Get date range
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        # Use backend profitability function
        summary = compute_customer_profitability(self.db_manager, start, end)
        if summary:
            df = pd.DataFrame(summary)
            # KPIs
            self.total_customers_label.setText(f"Total Customers\n{len(df)}")
            if not df.empty:
                most_prof = df.sort_values('total_profit', ascending=False).iloc[0]
                self.most_profitable_label.setText(f"Most Profitable\n{most_prof['customer_key']}")
            else:
                self.most_profitable_label.setText("Most Profitable\n-")
            loss_count = (df['segment'] == '🔻 Unprofitable').sum()
            self.loss_accounts_label.setText(f"Loss-Making Accounts\n{loss_count}")
            # Table
            self.customer_table.setRowCount(0)
            for row, r in df.iterrows():
                self.customer_table.insertRow(int(row))
                self.customer_table.setItem(int(row), 0, QTableWidgetItem(str(r['customer_key'])))
                self.customer_table.setItem(int(row), 1, QTableWidgetItem(f"${r['total_revenue']:,.2f}"))
                self.customer_table.setItem(int(row), 2, QTableWidgetItem(f"${r['total_cost']:,.2f}"))
                self.customer_table.setItem(int(row), 3, QTableWidgetItem(f"${r['total_profit']:,.2f}"))
                self.customer_table.setItem(int(row), 4, QTableWidgetItem(f"{r['profit_margin']:.1f}%"))
                self.customer_table.setItem(int(row), 5, QTableWidgetItem(str(int(r['num_bills']))))
                self.customer_table.setItem(int(row), 6, QTableWidgetItem(r['segment']))
            # Quadrant Chart
            self.ax.clear()
            self.ax.scatter(df['total_revenue'], df['profit_margin'], c=df['total_profit'].apply(lambda x: 'g' if x > 0 else 'r'))
            self.ax.set_xlabel('Total Revenue')
            self.ax.set_ylabel('Profit Margin (%)')
            self.ax.set_title('Customer Profitability Quadrant')
            self.ax.grid(True)
            self.fig.tight_layout()
            self.canvas.draw()
            # Treemap
            self.ax2.clear()
            try:
                import squarify
                sizes = df['total_profit'].clip(lower=0.01)
                squarify.plot(sizes=sizes, label=df['customer_key'], ax=self.ax2, alpha=0.7)
                self.ax2.set_title('Profit Contribution Treemap')
                self.ax2.axis('off')
            except ImportError:
                self.ax2.text(0.5, 0.5, 'Install squarify for treemap', ha='center', va='center')
            self.fig2.tight_layout()
            self.canvas2.draw()
        else:
            self.total_customers_label.setText("Total Customers\n0")
            self.most_profitable_label.setText("Most Profitable\n-")
            self.loss_accounts_label.setText("Loss-Making Accounts\n0")
            self.customer_table.setRowCount(0)
            self.ax.clear()
            self.ax.set_title('No data')
            self.canvas.draw()
            self.ax2.clear()
            self.ax2.set_title('No data')
            self.canvas2.draw()

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Customer Profitability", "customer_profitability.csv", "CSV Files (*.csv)")
        if not path:
            return
        # Gather table data
        data = []
        for row in range(self.customer_table.rowCount()):
            row_data = []
            for col in range(self.customer_table.columnCount()):
                item = self.customer_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        df = pd.DataFrame(data, columns=[self.customer_table.horizontalHeaderItem(i).text() for i in range(self.customer_table.columnCount())])
        df.to_csv(path, index=False)

    def enterEvent(self, event):
        self.load_dashboard_data()
        super().enterEvent(event) 