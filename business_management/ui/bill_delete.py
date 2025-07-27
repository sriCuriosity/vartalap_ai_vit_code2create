from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
from business_management.database.db_manager import DBManager
import os
from business_management.utils.helpers import get_app_path

DB_PATH = os.path.join(get_app_path(), 'bills.db')

class BillDeleteWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DBManager(DB_PATH)
        self.setWindowTitle("Delete Bill Record")
        self.init_ui()
        self.refresh_bill_numbers()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Delete Bill Record")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        bill_select_layout = QHBoxLayout()
        bill_label = QLabel("Select Bill Number:")
        self.bill_combo = QComboBox()
        self.bill_combo.currentIndexChanged.connect(self.display_bill_details)
        bill_select_layout.addWidget(bill_label)
        bill_select_layout.addWidget(self.bill_combo)
        layout.addLayout(bill_select_layout)

        # Add a horizontal layout to hold details text and items table side by side
        details_items_layout = QHBoxLayout()

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMinimumWidth(300)
        details_items_layout.addWidget(self.details_text)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Item Name", "Quantity", "Price", "Total", "Remarks"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        details_items_layout.addWidget(self.items_table)

        layout.addLayout(details_items_layout)

        self.delete_button = QPushButton("Delete Bill")
        self.delete_button.clicked.connect(self.delete_bill)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def refresh_bill_numbers(self):
        import sqlite3
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT bill_number FROM bills ORDER BY bill_number ASC')
            bill_numbers = [str(row[0]) for row in cursor.fetchall()]
        self.bill_combo.clear()
        self.bill_combo.addItems(bill_numbers)
        if bill_numbers:
            self.display_bill_details()
        else:
            self.details_text.setText("")
            self.items_table.setRowCount(0)

    def display_bill_details(self):
        bill_number = self.bill_combo.currentText()
        if not bill_number:
            self.details_text.setText("")
            self.items_table.setRowCount(0)
            return
        bill = self.db_manager.get_bill(int(bill_number))
        if bill:
            details = f"Bill Number: {bill.bill_number}\n"
            details += f"Customer: {bill.customer_key}\n"
            details += f"Date: {bill.date}\n"
            details += f"Total Amount: ${bill.total_amount:.2f}\n"
            details += f"Transaction Type: {bill.transaction_type}\n"
            details += f"Remarks: {bill.remarks if bill.remarks else 'None'}\n"
            self.details_text.setText(details)

            self.items_table.setRowCount(0)
            for row, item in enumerate(bill.items):
                self.items_table.insertRow(row)
                self.items_table.setItem(row, 0, QTableWidgetItem(str(item.get('name', ''))))
                self.items_table.setItem(row, 1, QTableWidgetItem(f"{item.get('quantity', 0):.2f}"))
                self.items_table.setItem(row, 2, QTableWidgetItem(str(item.get('price', ''))))
                self.items_table.setItem(row, 3, QTableWidgetItem(str(item.get('total', ''))))
                self.items_table.setItem(row, 4, QTableWidgetItem(str(item.get('remarks', ''))))
        else:
            self.details_text.setText("Bill not found.")
            self.items_table.setRowCount(0)

    def delete_bill(self):
        import os
        bill_number = self.bill_combo.currentText()
        if not bill_number:
            return
        confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete bill {bill_number}?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            success = self.db_manager.delete_bill(int(bill_number))
            if success:
                # Delete the generated invoice file if it exists
                template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../business_management/templates'))
                invoice_file = os.path.join(template_dir, f"temp_invoice_{bill_number}.html")
                if os.path.exists(invoice_file):
                    try:
                        os.remove(invoice_file)
                    except Exception as e:
                        QMessageBox.warning(self, "Warning", f"Failed to delete invoice file: {str(e)}")
                QMessageBox.information(self, "Deleted", f"Bill {bill_number} and associated invoice deleted successfully.")
                self.refresh_bill_numbers()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete bill {bill_number}.") 
                