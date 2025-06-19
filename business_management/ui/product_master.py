from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox
from business_management.database.db_manager import DBManager
import os
from business_management.resources.suggestions import INITIAL_PRODUCTS

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bills.db')

def ensure_initial_products(db_manager):
    existing = set(db_manager.get_products())
    for prod in INITIAL_PRODUCTS:
        if prod not in existing:
            db_manager.add_product(prod)

class ProductMasterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Master List")
        self.db_manager = DBManager(DB_PATH)
        ensure_initial_products(self.db_manager)
        self.init_ui()
        self.refresh_products()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Product Master List")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.product_list = QListWidget()
        layout.addWidget(self.product_list)

        add_layout = QHBoxLayout()
        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("Enter new product name")
        add_layout.addWidget(self.product_input)
        self.add_button = QPushButton("Add Product")
        self.add_button.clicked.connect(self.add_product)
        add_layout.addWidget(self.add_button)
        layout.addLayout(add_layout)
        self.setLayout(layout)

    def refresh_products(self):
        self.product_list.clear()
        products = self.db_manager.get_products()
        self.product_list.addItems(products)

    def add_product(self):
        name = self.product_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Product name cannot be empty.")
            return
        if self.db_manager.add_product(name):
            self.refresh_products()
            self.product_input.clear()
        else:
            QMessageBox.warning(self, "Duplicate", f'Product "{name}" already exists!') 
