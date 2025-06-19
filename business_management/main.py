import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from business_management.ui.bill_generator import BillGeneratorWidget
from business_management.ui.statement_generator import StatementGeneratorWidget
from business_management.ui.product_master import ProductMasterWidget
from business_management.ui.bill_delete import BillDeleteWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Business Management Software")
        self.resize(900, 700)
        layout = QVBoxLayout()
        nav_layout = QHBoxLayout()
        self.btn_bill = QPushButton("Bill Generator")
        self.btn_statement = QPushButton("Statement Generator")
        self.btn_product = QPushButton("Product Master")
        self.btn_delete = QPushButton("Delete Bill")
        nav_layout.addWidget(self.btn_bill)
        nav_layout.addWidget(self.btn_statement)
        nav_layout.addWidget(self.btn_product)
        nav_layout.addWidget(self.btn_delete)
        layout.addLayout(nav_layout)
        self.stacked_widget = QStackedWidget()
        self.bill_gen = BillGeneratorWidget()
        self.statement_gen = StatementGeneratorWidget()
        self.product_master = ProductMasterWidget()
        self.bill_delete = BillDeleteWidget()
        self.stacked_widget.addWidget(self.bill_gen)
        self.stacked_widget.addWidget(self.statement_gen)
        self.stacked_widget.addWidget(self.product_master)
        self.stacked_widget.addWidget(self.bill_delete)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        self.btn_bill.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.bill_gen))
        self.btn_statement.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.statement_gen))
        self.btn_product.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.product_master))
        self.btn_delete.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.bill_delete))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
