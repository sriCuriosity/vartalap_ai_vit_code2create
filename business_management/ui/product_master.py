from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHeaderView, QFormLayout)
from PyQt5.QtCore import Qt
from business_management.database.db_manager import DBManager
from business_management.models.product import Product
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
        self.selected_product_id = None

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left side: Table of products
        table_layout = QVBoxLayout()
        title = QLabel("Product Master List")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        table_layout.addWidget(title)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(7)
        self.product_table.setHorizontalHeaderLabels(["ID", "Name", "Cost Price", "Stock", "Reorder Threshold", "Lead Time (d)", "Category"])
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.product_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.product_table.verticalHeader().setVisible(False)  # type: ignore
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore
        self.product_table.setColumnHidden(0, True) # Hide ID
        self.product_table.itemSelectionChanged.connect(self.load_product_to_form)
        table_layout.addWidget(self.product_table)

        # Right side: Form to add/edit
        form_layout_container = QVBoxLayout()
        form_title = QLabel("Add / Edit Product")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout_container.addWidget(form_title)
        
        self.form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.cost_price_input = QLineEdit()
        self.stock_quantity_input = QLineEdit()
        self.reorder_threshold_input = QLineEdit()
        self.supplier_lead_time_input = QLineEdit()
        self.category_input = QLineEdit()
        
        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Cost Price:", self.cost_price_input)
        self.form_layout.addRow("Stock Quantity:", self.stock_quantity_input)
        self.form_layout.addRow("Reorder Threshold:", self.reorder_threshold_input)
        self.form_layout.addRow("Supplier Lead Time (Days):", self.supplier_lead_time_input)
        self.form_layout.addRow("Category:", self.category_input)
        form_layout_container.addLayout(self.form_layout)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.clear_button = QPushButton("Clear / New")
        self.save_button.clicked.connect(self.save_product)
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        form_layout_container.addLayout(button_layout)
        form_layout_container.addStretch()

        main_layout.addLayout(table_layout, 7) # 70% width for table
        main_layout.addLayout(form_layout_container, 3) # 30% width for form

    def refresh_products(self):
        self.product_table.setRowCount(0)
        products = self.db_manager.get_products()
        for row, product in enumerate(products):
            self.product_table.insertRow(row)
            self.product_table.setItem(row, 0, QTableWidgetItem(str(product.id)))
            self.product_table.setItem(row, 1, QTableWidgetItem(product.name))
            self.product_table.setItem(row, 2, QTableWidgetItem(str(product.cost_price)))
            self.product_table.setItem(row, 3, QTableWidgetItem(str(product.stock_quantity)))
            self.product_table.setItem(row, 4, QTableWidgetItem(str(product.reorder_threshold)))
            self.product_table.setItem(row, 5, QTableWidgetItem(str(product.supplier_lead_time)))
            self.product_table.setItem(row, 6, QTableWidgetItem(product.category))

    def load_product_to_form(self):
        selected_rows = self.product_table.selectionModel().selectedRows()  # type: ignore
        if not selected_rows:
            return
        
        selected_row = selected_rows[0].row()
        self.selected_product_id = int(self.product_table.item(selected_row, 0).text())  # type: ignore
        
        self.name_input.setText(self.product_table.item(selected_row, 1).text())  # type: ignore
        self.cost_price_input.setText(self.product_table.item(selected_row, 2).text())  # type: ignore
        self.stock_quantity_input.setText(self.product_table.item(selected_row, 3).text())  # type: ignore
        self.reorder_threshold_input.setText(self.product_table.item(selected_row, 4).text())  # type: ignore
        self.supplier_lead_time_input.setText(self.product_table.item(selected_row, 5).text())  # type: ignore
        self.category_input.setText(self.product_table.item(selected_row, 6).text())  # type: ignore
        
    def save_product(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Product name cannot be empty.")
            return

        try:
            cost_price = float(self.cost_price_input.text())
            stock_quantity = int(self.stock_quantity_input.text())
            reorder_threshold = int(self.reorder_threshold_input.text())
            supplier_lead_time = int(self.supplier_lead_time_input.text())
            category = self.category_input.text().strip()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please ensure numerical fields are valid numbers.")
            return

        if self.selected_product_id is None: # Add new product
            success = self.db_manager.add_product(name, cost_price, stock_quantity, reorder_threshold, supplier_lead_time, category)
            if not success:
                QMessageBox.warning(self, "Database Error", f"Product with name '{name}' may already exist.")
        else: # Update existing product
            product_to_update = Product(
                id=self.selected_product_id,
                name=name,
                cost_price=cost_price,
                stock_quantity=stock_quantity,
                reorder_threshold=reorder_threshold,
                supplier_lead_time=supplier_lead_time,
                category=category
            )
            self.db_manager.update_product(product_to_update)
        
            self.refresh_products()
        self.clear_form()

    def clear_form(self):
        self.selected_product_id = None
        self.product_table.clearSelection()
        self.name_input.clear()
        self.cost_price_input.clear()
        self.stock_quantity_input.clear()
        self.reorder_threshold_input.clear()
        self.supplier_lead_time_input.clear()
        self.category_input.clear() 