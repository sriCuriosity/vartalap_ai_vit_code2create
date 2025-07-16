import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDateEdit, QSpinBox, QFileDialog
from PyQt5.QtCore import Qt, QDate
from business_management.database.db_manager import DBManager
from business_management.utils.helpers import forecast_total_sales, get_app_path
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

DB_PATH = os.path.join(get_app_path(), 'bills.db')

class SalesForecastDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DBManager(DB_PATH)
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Sales Forecasting Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Date Range & Forecast Period
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
        date_layout.addWidget(QLabel("Forecast Days:"))
        self.period_spin = QSpinBox()
        self.period_spin.setRange(7, 180)
        self.period_spin.setValue(30)
        date_layout.addWidget(self.period_spin)
        filter_btn = QPushButton("Run Forecast")
        filter_btn.clicked.connect(self.load_dashboard_data)
        date_layout.addWidget(filter_btn)
        layout.addLayout(date_layout)

        # Chart
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Export Button
        export_btn = QPushButton("Export Forecast to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        layout.addWidget(export_btn)

    def load_dashboard_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        periods = self.period_spin.value()
        df = forecast_total_sales(self.db_manager, start, end, periods)
        self.ax.clear()
        if df is not None and not df.empty:
            df = df.sort_values('ds')
            # Plot actuals
            self.ax.plot(df['ds'], df['y'], label='Actual Sales', color='blue')
            # Plot forecast
            self.ax.plot(df['ds'], df['yhat'], label='Forecast', color='orange')
            # Uncertainty interval
            self.ax.fill_between(df['ds'], df['yhat_lower'], df['yhat_upper'], color='orange', alpha=0.2, label='Uncertainty')
            
            # Check if Prophet is available by looking at the forecast method used
            try:
                from prophet import Prophet
                title = 'Sales Forecast (Prophet)'
            except ImportError:
                try:
                    from fbprophet import Prophet
                    title = 'Sales Forecast (Prophet)'
                except ImportError:
                    title = 'Sales Forecast (Simple Moving Average)'
            
            self.ax.set_title(title)
            self.ax.set_xlabel('Date')
            self.ax.set_ylabel('Revenue')
            self.ax.legend()
        else:
            self.ax.set_title('No Data or Forecast')
        self.fig.tight_layout()
        self.canvas.draw()
        self._last_forecast_df = df

    def export_to_csv(self):
        if not hasattr(self, '_last_forecast_df') or self._last_forecast_df is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Sales Forecast", "sales_forecast.csv", "CSV Files (*.csv)")
        if not path:
            return
        self._last_forecast_df.to_csv(path, index=False) 