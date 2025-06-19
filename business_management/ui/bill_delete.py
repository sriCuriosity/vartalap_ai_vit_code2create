from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QTextEdit
from business_management.database.db_manager import DBManager
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bills.db')

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

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)

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

    def display_bill_details(self):
        bill_number = self.bill_combo.currentText()
        if not bill_number:
            self.details_text.setText("")
            return
        bill = self.db_manager.get_bill(int(bill_number))
        if bill:
            details = f"Bill Number: {bill.bill_number}\nCustomer: {bill.customer_key}\nDate: {bill.date}\nTotal: {bill.total_amount}\nType: {bill.transaction_type}\nRemarks: {bill.remarks}\nItems: {bill.items}"
            self.details_text.setText(details)
        else:
            self.details_text.setText("Bill not found.")

    def delete_bill(self):
        bill_number = self.bill_combo.currentText()
        if not bill_number:
            return
        confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete bill {bill_number}?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            success = self.db_manager.delete_bill(int(bill_number))
            if success:
                QMessageBox.information(self, "Deleted", f"Bill {bill_number} deleted successfully.")
                self.refresh_bill_numbers()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete bill {bill_number}.") 