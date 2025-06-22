import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QHeaderView, QFormLayout, QFrame, QComboBox, QFileDialog, QPushButton, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from business_management.database.db_manager import DBManager
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bills.db')

class InventoryDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DBManager(DB_PATH)
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Inventory Intelligence Dashboard")
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
        self.total_inventory_value_label = self._create_kpi_label("Total Inventory Value\n-")
        self.low_stock_label = self._create_kpi_label("Low Stock Items\n-")
        self.out_of_stock_label = self._create_kpi_label("Out of Stock Items\n-")
        
        kpi_layout.addWidget(self.total_inventory_value_label)
        kpi_layout.addWidget(self.low_stock_label)
        kpi_layout.addWidget(self.out_of_stock_label)
        layout.addLayout(kpi_layout)

        # Smart Inventory Table
        table_title = QLabel("Smart Inventory Table")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(table_title)

        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels(["Product Name", "Current Stock", "Cost Price", "Reorder Threshold", "Lead Time", "Status"])
        self.inventory_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.inventory_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inventory_table.verticalHeader().setVisible(False) # type: ignore
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # type: ignore
        layout.addWidget(self.inventory_table)

        # Visualization Section
        vis_title = QLabel("Sales Velocity & Demand Forecast")
        vis_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(vis_title)

        vis_layout = QHBoxLayout()
        # Product selection for demand forecast
        self.product_selector = QComboBox()
        self.product_selector.currentIndexChanged.connect(self.plot_demand_forecast)
        vis_layout.addWidget(QLabel("Select Product:"))
        vis_layout.addWidget(self.product_selector)

        # Matplotlib canvas for bar chart (sales velocity)
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        vis_layout.addWidget(self.canvas)

        # Matplotlib canvas for demand forecast
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
        label.setAlignment(Qt.AlignCenter) # type: ignore
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
        products = self.db_manager.get_products()
        bills = self.db_manager.get_bills(start, end)
        
        total_value = 0
        low_stock_count = 0
        out_of_stock_count = 0

        self.inventory_table.setRowCount(0)
        for row, product in enumerate(products):
            total_value += product.stock_quantity * product.cost_price
            status = "Healthy"
            color = None
            if product.stock_quantity <= 0:
                out_of_stock_count += 1
                status = "Out of Stock"
                color = QColor('red')
            elif product.stock_quantity <= product.reorder_threshold:
                low_stock_count += 1
                status = "Low Stock"
                color = QColor('yellow')
            
            self.inventory_table.insertRow(row)
            self.inventory_table.setItem(row, 0, QTableWidgetItem(product.name))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(str(product.stock_quantity)))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(f"${product.cost_price:,.2f}"))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(str(product.reorder_threshold)))
            self.inventory_table.setItem(row, 4, QTableWidgetItem(f"{product.supplier_lead_time} days"))
            status_item = QTableWidgetItem(status)
            self.inventory_table.setItem(row, 5, status_item)
            # Highlight row if low/out of stock
            if color:
                for col in range(6):
                    self.inventory_table.item(row, col).setBackground(color)  # type: ignore

        self.total_inventory_value_label.setText(f"Total Inventory Value\n${total_value:,.2f}")
        self.low_stock_label.setText(f"Low Stock Items\n{low_stock_count}")
        self.out_of_stock_label.setText(f"Out of Stock Items\n{out_of_stock_count}")

        # --- Sales Velocity Calculation ---
        # Build a DataFrame of all items sold by product and date
        sales_data = []
        for bill in bills:
            for item in bill.items:
                sales_data.append({
                    'date': bill.date,
                    'product': item['name'],
                    'quantity': item['quantity']
                })
        df = pd.DataFrame(sales_data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            # Group by product and week
            df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
            weekly = df.groupby(['product', 'week'])['quantity'].sum().reset_index()
            # Calculate average weekly sales velocity
            velocity = weekly.groupby('product')['quantity'].mean().sort_values(ascending=False)  # type: ignore
            # Plot top 5 and bottom 5
            self.ax.clear()
            top = velocity.head(5)
            bottom = velocity.tail(5)
            all_plot = pd.concat([top, bottom])  # type: ignore
            all_plot.plot(kind='bar', ax=self.ax, color=['#4caf50']*len(top)+['#f44336']*len(bottom))  # type: ignore
            self.ax.set_title('Sales Velocity (Units/Week)')
            self.ax.set_ylabel('Units/Week')
            self.ax.set_xlabel('Product')
            self.ax.tick_params(axis='x', rotation=45)
            self.fig.tight_layout()
            self.canvas.draw()
            # Update product selector
            self.product_selector.blockSignals(True)
            self.product_selector.clear()
            self.product_selector.addItems(velocity.index.tolist())  # type: ignore
            self.product_selector.blockSignals(False)
            if velocity.index.tolist():
                self.plot_demand_forecast()
        else:
            self.ax.clear()
            self.ax.set_title('No sales data available')
            self.canvas.draw()
            self.product_selector.clear()
            self.ax2.clear()
            self.ax2.set_title('No forecast data')
            self.canvas2.draw()

    def plot_demand_forecast(self):
        product = self.product_selector.currentText()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        bills = self.db_manager.get_bills(start, end)
        sales_data = []
        for bill in bills:
            for item in bill.items:
                if item['name'] == product:
                    sales_data.append({'date': bill.date, 'quantity': item['quantity']})
        df = pd.DataFrame(sales_data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.groupby('date')['quantity'].sum().reset_index()
            df = df.set_index('date').resample('W').sum().fillna(0)
            self.ax2.clear()
            self.ax2.plot(df.index, df['quantity'], label='Actual Sales', marker='o')
            # Prophet forecast if available
            if PROPHET_AVAILABLE and len(df) > 2:
                prophet_df = df.reset_index().rename(columns={'date': 'ds', 'quantity': 'y'})
                m = Prophet()
                m.fit(prophet_df)
                future = m.make_future_dataframe(periods=8, freq='W')
                forecast = m.predict(future)
                self.ax2.plot(forecast['ds'], forecast['yhat'], label='Prophet Forecast', linestyle='--')
                self.ax2.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='orange', alpha=0.2, label='Forecast Uncertainty')
            else:
                # Simple moving average forecast
                df['forecast'] = df['quantity'].rolling(window=4, min_periods=1).mean()
                self.ax2.plot(df.index, df['forecast'], label='4-Week Moving Avg', linestyle='--')
            self.ax2.set_title(f'Demand Forecast: {product}')
            self.ax2.set_ylabel('Units Sold')
            self.ax2.set_xlabel('Week')
            self.ax2.legend()
            self.fig2.tight_layout()
            self.canvas2.draw()
        else:
            self.ax2.clear()
            self.ax2.set_title('No forecast data')
            self.canvas2.draw()

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Inventory Analysis", "inventory_analysis.csv", "CSV Files (*.csv)")
        if not path:
            return
        # Gather table data
        data = []
        for row in range(self.inventory_table.rowCount()):
            row_data = []
            for col in range(self.inventory_table.columnCount()):
                item = self.inventory_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        df = pd.DataFrame(data, columns=[self.inventory_table.horizontalHeaderItem(i).text() for i in range(self.inventory_table.columnCount())])  # type: ignore
        df.to_csv(path, index=False)

    def enterEvent(self, event):
        """Reload data when the tab becomes visible."""
        self.load_dashboard_data()
        super().enterEvent(event) 