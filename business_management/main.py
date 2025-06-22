import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from business_management.ui.enhanced_bill_generator import EnhancedBillGeneratorWidget
from business_management.ui.statement_generator import StatementGeneratorWidget
from business_management.ui.product_master import ProductMasterWidget
from business_management.ui.bill_delete import BillDeleteWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Enhanced Business Management Software")
        self.resize(1200, 800)  # Larger window for AI features
        layout = QVBoxLayout()
        
        # Navigation layout
        nav_layout = QHBoxLayout()
        self.btn_bill = QPushButton("Enhanced Bill Generator")
        self.btn_statement = QPushButton("Statement Generator")
        self.btn_product = QPushButton("Product Master")
        self.btn_delete = QPushButton("Delete Bill")
        
        # Style the navigation buttons
        button_style = """
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 10px 15px;
                margin: 5px;
                border: 2px solid #007bff;
                border-radius: 8px;
                background-color: #f8f9fa;
                color: #007bff;
            }
            QPushButton:hover {
                background-color: #007bff;
                color: white;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
        """
        
        for btn in [self.btn_bill, self.btn_statement, self.btn_product, self.btn_delete]:
            btn.setStyleSheet(button_style)
        
        nav_layout.addWidget(self.btn_bill)
        nav_layout.addWidget(self.btn_statement)
        nav_layout.addWidget(self.btn_product)
        nav_layout.addWidget(self.btn_delete)
        layout.addLayout(nav_layout)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Enhanced bill generator with AI features
        self.bill_gen = EnhancedBillGeneratorWidget()
        self.statement_gen = StatementGeneratorWidget()
        self.product_master = ProductMasterWidget()
        self.bill_delete = BillDeleteWidget()
        
        self.stacked_widget.addWidget(self.bill_gen)
        self.stacked_widget.addWidget(self.statement_gen)
        self.stacked_widget.addWidget(self.product_master)
        self.stacked_widget.addWidget(self.bill_delete)
        
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        
        # Connect navigation buttons
        self.btn_bill.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.bill_gen))
        self.btn_statement.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.statement_gen))
        self.btn_product.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_master))
        self.btn_delete.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.bill_delete))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #f0f0f0;
            padding: 8px 16px;
            margin-right: 2px;
            border: 1px solid #c0c0c0;
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 1px solid white;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())