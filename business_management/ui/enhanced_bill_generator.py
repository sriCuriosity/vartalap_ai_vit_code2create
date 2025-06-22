from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, 
    QPushButton, QDoubleSpinBox, QSpinBox, QMessageBox, QTabWidget,
    QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from business_management.resources.customers import CUSTOMERS
from business_management.ui.components.item_entry import ItemEntryWidget
from business_management.ui.components.item_list import ItemListWidget
from business_management.ui.handwriting_widget import HandwritingWidget
from business_management.ui.invoice_scanner import InvoiceScannerWidget
from business_management.ui.ai_assistant import AIAssistantWidget
from business_management.database.db_manager import DBManager
from business_management.models.bill import Bill
import os
import webbrowser
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bills.db')

class EnhancedBillGeneratorWidget(QWidget):
    """Enhanced bill generator with AI features"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font1 = QFont("Arial", 12)
        self.items = []
        self.db_manager = DBManager(DB_PATH)
        self.bill_number_path = os.path.join(os.path.dirname(__file__), '../../Bill Number.txt')
        self.template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../business_management/templates/invoice_template.html'))
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
        
        # Title
        title = QLabel("Enhanced Bill Generator with AI")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create tab widget for different features
        self.tab_widget = QTabWidget()
        
        # Traditional Bill Generator Tab
        self.bill_tab = self.create_bill_tab()
        self.tab_widget.addTab(self.bill_tab, "Bill Generator")
        
        # Handwriting Recognition Tab
        self.handwriting_widget = HandwritingWidget()
        self.handwriting_widget.text_recognized.connect(self.on_handwriting_recognized)
        self.tab_widget.addTab(self.handwriting_widget, "Handwriting Recognition")
        
        # Invoice Scanner Tab
        self.scanner_widget = InvoiceScannerWidget()
        self.scanner_widget.invoice_data_ready.connect(self.on_invoice_data_ready)
        self.tab_widget.addTab(self.scanner_widget, "Invoice Scanner")
        
        # AI Assistant Tab
        self.ai_assistant = AIAssistantWidget()
        self.tab_widget.addTab(self.ai_assistant, "AI Assistant")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def create_bill_tab(self):
        """Create the traditional bill generator tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Customer selection
        customer_layout = QHBoxLayout()
        customer_label = QLabel("Select Customer:")
        customer_label.setFont(self.font1)
        self.customer_combo = QComboBox()
        self.customer_combo.setFont(self.font1)
        self.customer_combo.addItems(CUSTOMERS.keys())
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.customer_combo)
        layout.addLayout(customer_layout)

        # Date entry
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_label.setFont(self.font1)
        self.date_entry = QLineEdit()
        self.date_entry.setFont(self.font1)
        self.date_entry.setText(datetime.datetime.now().strftime('%Y-%m-%d'))
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_entry)
        layout.addLayout(date_layout)

        # Transaction type
        transaction_type_layout = QHBoxLayout()
        transaction_type_label = QLabel("Transaction Type:")
        transaction_type_label.setFont(self.font1)
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.setFont(self.font1)
        self.transaction_type_combo.addItems(["Debit", "Credit"])
        transaction_type_layout.addWidget(transaction_type_label)
        transaction_type_layout.addWidget(self.transaction_type_combo)
        layout.addLayout(transaction_type_layout)

        # Remarks
        remarks_layout = QHBoxLayout()
        remarks_label = QLabel("Remarks:")
        remarks_label.setFont(self.font1)
        self.remarks_entry = QLineEdit()
        self.remarks_entry.setFont(self.font1)
        remarks_layout.addWidget(remarks_label)
        remarks_layout.addWidget(self.remarks_entry)
        layout.addLayout(remarks_layout)

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
        layout.addLayout(credit_amount_layout)
        self.credit_amount_label.hide()
        self.credit_amount_entry.hide()

        # AI Features Group
        ai_group = QGroupBox("AI Features")
        ai_layout = QVBoxLayout()
        
        ai_buttons_layout = QHBoxLayout()
        self.handwriting_btn = QPushButton("Add from Handwriting")
        self.handwriting_btn.setFont(self.font1)
        self.handwriting_btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(1))
        
        self.scan_invoice_btn = QPushButton("Scan Invoice")
        self.scan_invoice_btn.setFont(self.font1)
        self.scan_invoice_btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(2))
        
        self.ai_help_btn = QPushButton("AI Assistant")
        self.ai_help_btn.setFont(self.font1)
        self.ai_help_btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(3))
        
        ai_buttons_layout.addWidget(self.handwriting_btn)
        ai_buttons_layout.addWidget(self.scan_invoice_btn)
        ai_buttons_layout.addWidget(self.ai_help_btn)
        ai_layout.addLayout(ai_buttons_layout)
        
        # Auto-translate checkbox
        self.auto_translate_cb = QCheckBox("Auto-translate Tamil items to English")
        self.auto_translate_cb.setFont(self.font1)
        ai_layout.addWidget(self.auto_translate_cb)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # Item entry (custom component)
        self.item_entry_widget = ItemEntryWidget()
        self.item_entry_widget.item_added.connect(self.add_item)
        layout.addWidget(self.item_entry_widget)

        # Item list (custom component)
        self.item_list_widget = ItemListWidget()
        self.item_list_widget.item_removed.connect(self.remove_item_by_index)
        layout.addWidget(self.item_list_widget)

        # Total display
        total_layout = QHBoxLayout()
        total_label = QLabel("Total:")
        total_label.setFont(self.font1)
        self.total_display = QLineEdit("₹0.00")
        self.total_display.setFont(self.font1)
        self.total_display.setReadOnly(True)
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_display)
        layout.addLayout(total_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Bill")
        self.generate_button.setFont(self.font1)
        self.clear_button = QPushButton("Clear")
        self.clear_button.setFont(self.font1)
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.clear_button)
        layout.addLayout(buttons_layout)

        # Connect signals
        self.transaction_type_combo.currentIndexChanged.connect(self.update_transaction_fields)
        self.generate_button.clicked.connect(self.generate_bill)
        self.clear_button.clicked.connect(self.clear_form)
        
        # Initialize
        self.update_transaction_fields()
        self.update_items_list()
        self.update_total()
        
        widget.setLayout(layout)
        return widget

    def on_handwriting_recognized(self, text):
        """Handle text recognized from handwriting"""
        # Switch back to bill generator tab
        self.tab_widget.setCurrentIndex(0)
        
        # Try to parse the text and add as item
        # This is a simple implementation - in production, you'd use more sophisticated parsing
        words = text.split()
        if len(words) >= 2:
            item_name = " ".join(words[:-1])  # All words except last
            try:
                quantity = int(words[-1])  # Last word as quantity
                
                # Set the item name in the entry widget
                self.item_entry_widget.item_name_combo.setEditText(item_name)
                self.item_entry_widget.quantity_entry.setValue(quantity)
                
                QMessageBox.information(
                    self, 
                    "Handwriting Recognized", 
                    f"Added item: {item_name} (Qty: {quantity})\nPlease set the price and add to bill."
                )
            except ValueError:
                # If last word is not a number, just set the item name
                self.item_entry_widget.item_name_combo.setEditText(text)
                QMessageBox.information(
                    self, 
                    "Handwriting Recognized", 
                    f"Added item name: {text}\nPlease set quantity and price."
                )

    def on_invoice_data_ready(self, invoice_data):
        """Handle invoice data from scanner"""
        # Switch back to bill generator tab
        self.tab_widget.setCurrentIndex(0)
        
        # Clear existing items
        self.items.clear()
        
        # Add items from scanned invoice
        for item_data in invoice_data.get("items", []):
            item = {
                "name": item_data.get("name", ""),
                "price": item_data.get("rate", 0.0),
                "quantity": item_data.get("quantity", 1),
                "total": item_data.get("amount", 0.0),
                "type": "Debit"
            }
            self.items.append(item)
        
        # Update UI
        self.update_items_list()
        self.update_total()
        
        # Set other fields if available
        if "date" in invoice_data:
            self.date_entry.setText(invoice_data["date"])
        
        QMessageBox.information(
            self, 
            "Invoice Data Loaded", 
            f"Loaded {len(invoice_data.get('items', []))} items from scanned invoice."
        )

    def add_item(self, item):
        if self.transaction_type_combo.currentText() == "Debit":
            # Check if item already exists (by name)
            for existing in self.items:
                if existing["name"].lower() == item["name"].lower():
                    existing["quantity"] += item["quantity"]
                    existing["total"] += item["total"]
                    self.update_items_list()
                    self.update_total()
                    self.item_entry_widget.item_name_combo.setFocus()
                    return
            self.items.append(item)
            self.update_items_list()
            self.update_total()
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
        self.date_entry.clear()
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
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record transaction: {str(e)}")

    def generate_html_invoice(self, bill):
        # Load template
        try:
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = f.read()
            customer = CUSTOMERS.get(bill.customer_key, {"name": bill.customer_key, "address": ""})
            item_rows = ""
            for idx, item in enumerate(bill.items):
                item_rows += f"<tr><td>{idx+1}</td><td>{item['name'].split()[0]}</td><td>{item['quantity']} kg</td><td>₹{item['price']:.2f}</td><td colspan='2'>₹{item['total']:.2f}</td></tr>"
            html_content = template.format(
                bill_number=bill.bill_number,
                customer_name=customer["name"],
                customer_address=customer["address"],
                date=bill.date,
                item_rows=item_rows,
                total=f"₹{bill.total_amount:.2f}"
            )
            temp_html_path = os.path.join(os.path.dirname(self.template_path), f"temp_invoice_{bill.bill_number}.html")
            with open(temp_html_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            webbrowser.open(temp_html_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate invoice: {str(e)}")

    def refresh_suggestions(self):
        self.suggestions = self.db_manager.get_products()
        self.item_entry_widget.set_suggestions(self.suggestions)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_suggestions()