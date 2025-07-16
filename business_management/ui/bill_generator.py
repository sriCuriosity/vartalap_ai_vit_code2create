from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QDoubleSpinBox, QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from business_management.resources.customers import CUSTOMERS
from business_management.resources.suggestions import SUGGESTIONS
from business_management.ui.components.item_entry import ItemEntryWidget
from business_management.ui.components.item_list import ItemListWidget
from business_management.database.db_manager import DBManager
from business_management.models.bill import Bill
import os
import json
import webbrowser
import datetime
from business_management.utils.helpers import get_app_path

DB_PATH = os.path.join(get_app_path(), 'bills.db')

class BillGeneratorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font1 = QFont("Arial", 12)
        self.items = []
        self.db_manager = DBManager(DB_PATH)
        self.bill_number_path = os.path.join(get_app_path(), 'Bill Number.txt')
        self.template_path = os.path.join(get_app_path(), 'business_management', 'templates', 'invoice_vr_template.html')
        self.bill_number = self.get_current_bill_number()
        self.suggestions = self.db_manager.get_products()
        self.init_ui()

    def get_current_bill_number(self):
        try:
            with open(self.bill_number_path, "r") as file:
                return int(file.read().strip())
        except (FileNotFoundError, ValueError):
            return 1

    def update_bill_number(self):
        self.bill_number += 1
        with open(self.bill_number_path, "w") as file:
            file.write(str(self.bill_number))

    def init_ui(self):
        main_layout = QVBoxLayout()
        customer_layout = QHBoxLayout()
        customer_label = QLabel("Select Customer:")
        customer_label.setFont(self.font1)
        self.customer_combo = QComboBox()
        self.customer_combo.setFont(self.font1)
        self.customer_combo.addItems(CUSTOMERS.keys())
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.customer_combo)
        main_layout.addLayout(customer_layout)

        # Date entry
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_label.setFont(self.font1)
        self.date_entry = QLineEdit()
        self.date_entry.setFont(self.font1)
        self.date_entry.setText(datetime.datetime.now().strftime('%Y-%m-%d'))
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_entry)
        main_layout.addLayout(date_layout)

        # Transaction type
        transaction_type_layout = QHBoxLayout()
        transaction_type_label = QLabel("Transaction Type:")
        transaction_type_label.setFont(self.font1)
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.setFont(self.font1)
        self.transaction_type_combo.addItems(["Debit", "Credit"])
        transaction_type_layout.addWidget(transaction_type_label)
        transaction_type_layout.addWidget(self.transaction_type_combo)
        main_layout.addLayout(transaction_type_layout)

        # Remarks
        remarks_layout = QHBoxLayout()
        remarks_label = QLabel("Remarks:")
        remarks_label.setFont(self.font1)
        self.remarks_entry = QLineEdit()
        self.remarks_entry.setFont(self.font1)
        remarks_layout.addWidget(remarks_label)
        remarks_layout.addWidget(self.remarks_entry)
        main_layout.addLayout(remarks_layout)

        # Credit amount (hidden by default)
        credit_amount_layout = QHBoxLayout()
        self.credit_amount_label = QLabel("Credit Amount:")
        self.credit_amount_label.setFont(self.font1)
        self.credit_amount_entry = QDoubleSpinBox()
        self.credit_amount_entry.setFont(self.font1)
        self.credit_amount_entry.setMaximum(1000000)
        self.credit_amount_entry.setPrefix("₹")
        credit_amount_layout.addWidget(self.credit_amount_label)
        credit_amount_layout.addWidget(self.credit_amount_entry)
        main_layout.addLayout(credit_amount_layout)
        self.credit_amount_label.hide()
        self.credit_amount_entry.hide()

        # Item entry (custom component)
        self.item_entry_widget = ItemEntryWidget()
        self.item_entry_widget.item_added.connect(self.add_item)
        main_layout.addWidget(self.item_entry_widget)

        # Item list (custom component)
        self.item_list_widget = ItemListWidget()
        self.item_list_widget.item_removed.connect(self.remove_item_by_index)
        main_layout.addWidget(self.item_list_widget)

        # Total display
        total_layout = QHBoxLayout()
        total_label = QLabel("Total:")
        total_label.setFont(self.font1)
        self.total_display = QLineEdit("₹0.00")
        self.total_display.setFont(self.font1)
        self.total_display.setReadOnly(True)
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_display)
        main_layout.addLayout(total_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Bill")
        self.generate_button.setFont(self.font1)
        self.clear_button = QPushButton("Clear")
        self.clear_button.setFont(self.font1)
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.clear_button)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        self.transaction_type_combo.currentIndexChanged.connect(self.update_transaction_fields)
        self.generate_button.clicked.connect(self.generate_bill)
        self.clear_button.clicked.connect(self.clear_form)
        self.update_transaction_fields()
        self.update_items_list()
        self.update_total()
        # Ensure current date is set
        self.date_entry.setText(datetime.datetime.now().strftime('%Y-%m-%d'))

    def add_item(self, item):
        if self.transaction_type_combo.currentText() == "Debit":
            # Check if item already exists (by name)
            for existing in self.items:
                if existing["name"].lower() == item["name"].lower():
                    existing["quantity"] += item["quantity"]
                    existing["total"] += item["total"]
                    self.update_items_list()
                    self.update_total()
                    # Set focus to quantity field after adding
                    self.item_entry_widget.item_name_combo.setFocus()
                    return
            self.items.append(item)
            self.update_items_list()
            self.update_total()
            # Set focus to quantity field after adding
            self.item_entry_widget.item_name_combo.setFocus()

    def remove_item_by_index(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]
            self.update_items_list()
            self.update_total()

    def update_items_list(self):
        self.item_list_widget.update_items(self.items)

    def update_total(self):
        total = sum(item["total"] for item in self.items)
        self.total_display.setText(f"₹{total:.2f}")

    def update_transaction_fields(self):
        transaction_type = self.transaction_type_combo.currentText()
        if transaction_type == "Credit":
            self.item_entry_widget.hide()
            self.item_list_widget.hide()
            self.total_display.hide()
            self.credit_amount_label.show()
            self.credit_amount_entry.show()
            self.remarks_entry.show()
            self.items.clear()
            self.update_items_list()
            self.update_total()
        else:
            self.item_entry_widget.show()
            self.item_list_widget.show()
            self.total_display.show()
            self.credit_amount_label.hide()
            self.credit_amount_entry.hide()
            self.remarks_entry.show()
            self.credit_amount_entry.setValue(0.0)

    def clear_form(self):
        self.items = []
        self.update_items_list()
        self.item_entry_widget.clear_fields()
        self.total_display.setText("₹0.00")
        # Set current date instead of clearing
        self.date_entry.setText(datetime.datetime.now().strftime('%Y-%m-%d'))
        self.customer_combo.setCurrentIndex(0)
        self.transaction_type_combo.setCurrentIndex(0)
        self.remarks_entry.clear()
        self.credit_amount_entry.setValue(0.0)
        self.update_transaction_fields()

    def generate_bill(self):
        transaction_type = self.transaction_type_combo.currentText()
        if transaction_type == "Debit" and not self.items:
            QMessageBox.critical(self, "Error", "Please add items to the bill for a Debit transaction.")
            return
        elif transaction_type == "Credit" and self.credit_amount_entry.value() <= 0:
            QMessageBox.critical(self, "Error", "Please enter a valid credit amount for a Credit transaction.")
            return
        try:
            # Prepare bill data
            customer_key = self.customer_combo.currentText()
            date = self.date_entry.text()
            remarks = self.remarks_entry.text().strip()
            if transaction_type == "Debit":
                items = self.items
                total_amount = sum(item["total"] for item in items)
            else:
                items = [{
                    "name": remarks if remarks else "Credit Entry",
                    "price": 0.0,
                    "quantity": 0,
                    "total": self.credit_amount_entry.value(),
                    "type": "Credit",
                    "remarks": remarks
                }]
                total_amount = self.credit_amount_entry.value()
            bill = Bill(
                bill_number=self.bill_number,
                customer_key=customer_key,
                date=date,
                items=items,
                total_amount=total_amount,
                transaction_type=transaction_type,
                remarks=remarks
            )
            # Save to DB
            self.db_manager.save_bill(bill)
            self.update_bill_number()
            # Generate HTML invoice for Debit
            if transaction_type == "Debit":
                self.generate_html_invoice(bill)
            QMessageBox.information(self, "Success", "Transaction recorded successfully!")
            #self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record transaction: {str(e)}")

    def get_billing_year(self):
        now = datetime.datetime.now()
        if now.month < 4:  # January, February, March
            return str(now.year - 1)
        else:
            return str(now.year)

    def generate_html_invoice(self, bill):
        # Load template
        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = f.read()
            customer = CUSTOMERS.get(bill.customer_key, {"name": bill.customer_key, "address": "", "gstin": ""})
            item_rows = ""
            subtotal = 0.0
            for idx, item in enumerate(bill.items):
                hsn_code = item.get('hsn_code', '')
                item_rows += f"<tr><td>{idx+1}</td><td>{item['name'].split('(')[0].strip()}</td><td>01008001</td><td>{item['quantity']}</td><td>{item['price']:.2f}</td><td>{item['total']:.2f}</td></tr>"
                subtotal += item['total']
            total = bill.total_amount
            amount_in_words = self.number_to_words(int(total))
            html_content = template.format(
                bill_number=bill.bill_number,
                customer_name=customer["name"],
                customer_address=customer["address"],
                customer_gstin=customer.get("gstin", ""),
                date=bill.date,
                item_rows=item_rows,
                subtotal=f"₹{subtotal:.2f}",
                total=f"₹{total:.2f}",
                amount_in_words=amount_in_words,
                billing_year=self.get_billing_year(),
                billing_yearn=str(int(self.get_billing_year())+1)
            )
            temp_html_path = os.path.join(os.path.dirname(self.template_path), f"temp_invoice_{bill.bill_number}.html")
            with open(temp_html_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            webbrowser.open(temp_html_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate invoice: {str(e)}")

    def number_to_words(self, number):
        # Simple number to words for rupees (Indian style, up to lakhs/crores)
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        if number == 0:
            return "Zero"
        if number < 20:
            return units[number]
        if number < 100:
            return tens[number // 10] + (" " + units[number % 10] if (number % 10) != 0 else "")
        if number < 1000:
            return units[number // 100] + " Hundred" + (" and " + self.number_to_words(number % 100) if (number % 100) != 0 else "")
        if number < 100000:
            return self.number_to_words(number // 1000) + " Thousand" + (" " + self.number_to_words(number % 1000) if (number % 1000) != 0 else "")
        if number < 10000000:
            return self.number_to_words(number // 100000) + " Lakh" + (" " + self.number_to_words(number % 100000) if (number % 100000) != 0 else "")
        return self.number_to_words(number // 10000000) + " Crore" + (" " + self.number_to_words(number % 10000000) if (number % 10000000) != 0 else "")

    def refresh_suggestions(self):
        self.suggestions = [p.name for p in self.db_manager.get_products()]
        self.item_entry_widget.set_suggestions(self.suggestions)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_suggestions()
