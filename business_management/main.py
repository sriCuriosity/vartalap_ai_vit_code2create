import sys
from PyQt5.QtWidgets import (QApplication, QStackedWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt
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
        
        # Get the available screen geometry
        screen = QApplication.primaryScreen().availableGeometry()
        window_width = min(1200, screen.width() * 0.9)  # 90% of screen width, max 1200px
        window_height = min(800, screen.height() * 0.9)  # 90% of screen height, max 800px
        
        # Set window size and position it in the center
        self.resize(int(window_width), int(window_height))
        self.move(
            int((screen.width() - window_width) / 2),
            int((screen.height() - window_height) / 2)
        )
        
        # Make the window resizable with a minimum size
        self.setMinimumSize(800, 600)
        
        # Create the main layout
        main_layout = QVBoxLayout(self)  # Set layout directly on self
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create navigation bar
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setAlignment(Qt.AlignLeft)
        nav_layout.setSpacing(5)
        nav_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create the stacked widget first
        self.stacked_widget = QStackedWidget()
        
        # Create a container widget for the stacked widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.stacked_widget)
        
        # Create scroll area and set its properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        
        # Add navigation and content to main layout
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(scroll_area, 1)  # Add stretch factor to make it take available space
        
        # Set size policy for the scroll area to expand
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create and add navigation buttons
        self.btn_bill = QPushButton("Bill Generator")
        self.btn_statement = QPushButton("Statement")
        self.btn_product = QPushButton("Products")
        self.btn_delete = QPushButton("Delete Bill")
        self.btn_inventory = QPushButton("Inventory")
        self.btn_customer = QPushButton("Customers")
        self.btn_expense = QPushButton("Expenses")
        self.btn_product_analysis = QPushButton("Product Analysis")
        self.btn_customer_behavior = QPushButton("Customer Analysis")
        self.btn_business_overview = QPushButton("Overview")
        self.btn_sales_forecast = QPushButton("Forecast")
        self.btn_advanced_analytics = QPushButton("Analytics")
        
        # Add buttons to navigation layout
        nav_buttons = [
            self.btn_bill, self.btn_statement, self.btn_product, 
            self.btn_delete, self.btn_inventory, self.btn_customer,
            self.btn_expense, self.btn_product_analysis, self.btn_customer_behavior,
            self.btn_business_overview, self.btn_sales_forecast, self.btn_advanced_analytics
        ]
        
        # Configure buttons and add to layout
        for btn in nav_buttons:
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            btn.setMinimumWidth(100)  # Set a minimum width for better appearance
            nav_layout.addWidget(btn)
        
        # Add stretch to push buttons to the left
        nav_layout.addStretch()
        
        # Create all the widgets
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
        
        # Add all widgets to the stacked widget
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
        
        # Set the first widget as default
        self.stacked_widget.setCurrentWidget(self.bill_gen)
        
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
