from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QDateEdit, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont
from business_management.resources.customers import CUSTOMERS
from business_management.database.db_manager import DBManager
import os
import webbrowser

class StatementGeneratorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font = QFont("Arial", 12)
        self.db_path = os.path.join(os.path.dirname(__file__), '../../bills.db')
        self.db_manager = DBManager(os.path.abspath(self.db_path))
        self.template_path = os.path.join(os.path.dirname(__file__), '../../templates/statement_template.html')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # Start date
        start_date_label = QLabel("Start Date:")
        start_date_label.setFont(self.font)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setFont(self.font)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        form_layout.addWidget(start_date_label)
        form_layout.addWidget(self.start_date_edit)

        # End date
        end_date_label = QLabel("End Date:")
        end_date_label.setFont(self.font)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setFont(self.font)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        form_layout.addWidget(end_date_label)
        form_layout.addWidget(self.end_date_edit)

        # Customer
        customer_label = QLabel("Customer:")
        customer_label.setFont(self.font)
        self.customer_combo = QComboBox()
        self.customer_combo.setFont(self.font)
        self.customer_combo.addItem("")
        self.customer_combo.addItems(CUSTOMERS.keys())
        form_layout.addWidget(customer_label)
        form_layout.addWidget(self.customer_combo)

        layout.addLayout(form_layout)

        # Generate statement button
        self.generate_button = QPushButton("Generate Statement")
        self.generate_button.setFont(self.font)
        self.generate_button.clicked.connect(self.generate_statement)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)

    def generate_statement(self):
        start_date = self.start_date_edit.date().toString("dd-MM-yyyy")
        end_date = self.end_date_edit.date().toString("dd-MM-yyyy")
        customer_key = self.customer_combo.currentText()
        try:
            bills = self.db_manager.get_bills(start_date, end_date, customer_key if customer_key else None)
            if not bills:
                QMessageBox.information(self, "No Records", "No transactions found for the selected criteria.")
                return
            # Prepare item rows and totals
            item_rows = ""
            total_debit = 0.0
            total_credit = 0.0
            for bill in bills:
                particulars = "To Sales" if bill.transaction_type == "Debit" else f"By {bill.remarks}"
                debit = f"₹{bill.total_amount:.2f}" if bill.transaction_type == "Debit" else ""
                credit = f"₹{bill.total_amount:.2f}" if bill.transaction_type == "Credit" else ""
                if bill.transaction_type == "Debit":
                    total_debit += bill.total_amount
                else:
                    total_credit += bill.total_amount
                item_rows += f"<tr><td>{bill.date}</td><td>{particulars}</td><td>{bill.transaction_type}</td><td>{bill.bill_number}</td><td>{debit}</td><td>{credit}</td></tr>"
            closing_balance = total_debit - total_credit
            balance_type = "Debit" if closing_balance >= 0 else "Credit"
            closing_balance_display = f"Rs. {abs(closing_balance):.2f} {balance_type}"
            # Render template
            with open(self.template_path, "r", encoding="utf-8") as f:
                template = f.read()
            html_content = template.format(
                start_date=start_date,
                end_date=end_date,
                item_rows=item_rows,
                total_debit=total_debit,
                total_credit=total_credit,
                closing_balance=closing_balance_display
            )
            temp_html_path = os.path.join(os.path.dirname(self.template_path), f"temp_statement_{start_date}_to_{end_date}.html")
            with open(temp_html_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            webbrowser.open(temp_html_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate statement: {str(e)}")
