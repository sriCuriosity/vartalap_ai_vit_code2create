import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDesktopWidget
from business_management.ui.bill_generator import BillGeneratorWidget
from business_management.ui.statement_generator import StatementGeneratorWidget
from business_management.ui.product_master import ProductMasterWidget
from business_management.ui.bill_delete import BillDeleteWidget
from business_management.ui.inventory_dashboard import InventoryDashboardWidget
from business_management.ui.customer_dashboard import CustomerDashboardWidget
from business_management.ui.expense_dashboard import ExpenseDashboardWidget
from business_management.ui.product_analysis_dashboard import ProductAnalysisDashboardWidget
from business_management.ui.customer_behavior_dashboard import CustomerBehaviorDashboardWidget
from business_management.ui.business_overview_dashboard import BusinessOverviewDashboardWidget
from business_management.ui.sales_forecast_dashboard import SalesForecastDashboardWidget
from business_management.ui.advanced_analytics_dashboard import AdvancedAnalyticsDashboardWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Business Management Software")
        # Set a more reasonable default size that works on most screens
        self.resize(1200, 800)
        self.center_window()
        layout = QVBoxLayout()
        nav_layout = QHBoxLayout()
        self.btn_bill = QPushButton("Bill Generator")
        self.btn_statement = QPushButton("Statement Generator")
        self.btn_product = QPushButton("Product Master")
        self.btn_delete = QPushButton("Delete Bill")
        self.btn_inventory = QPushButton("Inventory Intelligence")
        self.btn_customer = QPushButton("Customer Profitability")
        self.btn_expense = QPushButton("Expense & Profit/Loss")
        self.btn_product_analysis = QPushButton("Product Analysis")
        self.btn_customer_behavior = QPushButton("Customer Behavior")
        self.btn_business_overview = QPushButton("Business Overview")
        self.btn_sales_forecast = QPushButton("Sales Forecast")
        self.btn_advanced_analytics = QPushButton("Advanced Analytics")
        nav_layout.addWidget(self.btn_bill)
        nav_layout.addWidget(self.btn_statement)
        nav_layout.addWidget(self.btn_product)
        nav_layout.addWidget(self.btn_delete)
        nav_layout.addWidget(self.btn_inventory)
        nav_layout.addWidget(self.btn_customer)
        nav_layout.addWidget(self.btn_expense)
        nav_layout.addWidget(self.btn_product_analysis)
        nav_layout.addWidget(self.btn_customer_behavior)
        nav_layout.addWidget(self.btn_business_overview)
        nav_layout.addWidget(self.btn_sales_forecast)
        nav_layout.addWidget(self.btn_advanced_analytics)
        layout.addLayout(nav_layout)
        self.stacked_widget = QStackedWidget()
        self.bill_gen = BillGeneratorWidget()
        self.statement_gen = StatementGeneratorWidget()
        self.product_master = ProductMasterWidget()
        self.bill_delete = BillDeleteWidget()
        self.inventory_dashboard = InventoryDashboardWidget()
        self.customer_dashboard = CustomerDashboardWidget()
        self.expense_dashboard = ExpenseDashboardWidget()
        self.product_analysis_dashboard = ProductAnalysisDashboardWidget()
        self.customer_behavior_dashboard = CustomerBehaviorDashboardWidget()
        self.business_overview_dashboard = BusinessOverviewDashboardWidget()
        self.sales_forecast_dashboard = SalesForecastDashboardWidget()
        self.advanced_analytics_dashboard = AdvancedAnalyticsDashboardWidget()
        self.stacked_widget.addWidget(self.bill_gen)
        self.stacked_widget.addWidget(self.statement_gen)
        self.stacked_widget.addWidget(self.product_master)
        self.stacked_widget.addWidget(self.bill_delete)
        self.stacked_widget.addWidget(self.inventory_dashboard)
        self.stacked_widget.addWidget(self.customer_dashboard)
        self.stacked_widget.addWidget(self.expense_dashboard)
        self.stacked_widget.addWidget(self.product_analysis_dashboard)
        self.stacked_widget.addWidget(self.customer_behavior_dashboard)
        self.stacked_widget.addWidget(self.business_overview_dashboard)
        self.stacked_widget.addWidget(self.sales_forecast_dashboard)
        self.stacked_widget.addWidget(self.advanced_analytics_dashboard)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        self.btn_bill.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.bill_gen))
        self.btn_statement.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.statement_gen))
        self.btn_product.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_master))
        self.btn_delete.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.bill_delete))
        self.btn_inventory.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.inventory_dashboard))
        self.btn_customer.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.customer_dashboard))
        self.btn_expense.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.expense_dashboard))
        self.btn_product_analysis.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_analysis_dashboard))
        self.btn_customer_behavior.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.customer_behavior_dashboard))
        self.btn_business_overview.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.business_overview_dashboard))
        self.btn_sales_forecast.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.sales_forecast_dashboard))
        self.btn_advanced_analytics.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.advanced_analytics_dashboard))

    def center_window(self):
        """Center the window on the screen with adaptive sizing"""
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        window_geometry = self.geometry()
        
        # Ensure window doesn't exceed screen size
        max_width = min(1200, screen_geometry.width() - 100)
        max_height = min(800, screen_geometry.height() - 100)
        
        # Resize if window is too large for screen
        if window_geometry.width() > max_width or window_geometry.height() > max_height:
            self.resize(max_width, max_height)
            window_geometry = self.geometry()
        
        # Calculate center position
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        
        # Ensure window doesn't go off-screen
        x = max(0, min(x, screen_geometry.width() - window_geometry.width()))
        y = max(0, min(y, screen_geometry.height() - window_geometry.height()))
        
        # Move window to center
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
