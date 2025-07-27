import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QListWidget, QMessageBox, QSpinBox, QDoubleSpinBox, QMenu,
    QListWidgetItem, QCompleter, QStyledItemDelegate, QWidget as QtWidget, QDesktopWidget
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QStringListModel, QDate
from PyQt5.QtGui import QFont
import json
import sqlite3
import os
from datetime import datetime
import webbrowser
from fuzzywuzzy import process
from PyQt5.QtWidgets import QStackedWidget, QDateEdit

# Determine the base path for persistent files
def get_base_path():
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        return os.path.abspath(os.path.dirname(sys.argv[0]))
    else:
        # Running in a normal Python environment
        return os.path.abspath(os.path.dirname(__file__))

BASE_PATH = get_base_path()
DATABASE_PATH = os.path.join(BASE_PATH, "bills.db")
BILL_NUMBER_PATH = os.path.join(BASE_PATH, "Bill Number.txt")
TEMPLATE_DIR = os.path.join(BASE_PATH, "templates")

os.makedirs(TEMPLATE_DIR, exist_ok=True)


customers = {
    "A": {"name": "Customer A", "address": "123 Main St"},
    "B": {"name": "Customer B", "address": "456 Elm St"},
    "C": {"name": "Customer C", "address": "789 Oak St"}
}

suggestions = [
    "நாட்டு சக்கரை (Country sugar)",
    "ராகி (Ragi)",
    "ராகி மாவு (Ragi flour)",
    "நாட்டு கம்பு (Country kambu)",
    "நாட்டு கம்பு மாவு (Country kambu flour)",
    "சத்து மாவு (Sattu flour)",
    "மட்ட சம்பா அரிசி (Matta Samba rice)",
    "சிவப்பு கவுணி அரிசி (Red parboiled rice)",
    "சிவப்பு சோளம் (Red corn)",
    "சம்பா அவுள் (Samba bran)",
    "உளுந்தங்களி மாவு (Ulundhu kali flour)",
    "நாட்டு கொண்க்கடலை (Country chickpea)",
    "இடியாப்ப மாவு (Idiyappam flour)",
    "வெள்ளை புட்டு மாவு (White puttu flour)",
    "வெள்ளை நைஸ் அவுள் (White rice bran)",
    "Corn flakes (Corn flakes)",
    "ராகி அவுள் (Ragi bran)",
    "கம்பு அவுள் (Kambu bran)",
    "சோள அவுள் (Corn bran)",
    "கோதுமை அவுள் (Wheat bran)",
    "Red rice அவுள் (Red rice bran)",
    "கொள்ளு அவுள் (Horse gram bran)",
    "வெள்ளை சோளம் (White corn)",
    "சிவப்பு கொள்ளு (Red cowpea)",
    "கருப்பு கொள்ளு (Black cowpea)",
    "உடைத்த கருப்பு உளுந்து (Split black gram)",
    "தட்டைப் பயறு (Thataipayyir)",
    "மாப்பிள்ளை சம்பா அரிசி (Mappillai samba rice)",
    "கைக்குத்தல் அரிசி (Handan sown rice)",
    "அச்சு வெள்ளம் (Palm jaggery)",
    "சிவப்பு அரிசி புட்டு மாவு (Red rice flour for puttu)",
    "சிவப்பு அரிசி இடியாப்ப மாவு (Red rice flour for idiappam)",
    "சிவப்பு அரிசி குருனை (Red rice - Kuruvai variety)",
    "மட்ட சம்பா குருனை (Matta Samba rice - Kuruvai variety)",
    "சிவப்பு நைஸ் அவுள் (Red rice bran)",
    "வெள்ளை கெட்டி அவுள் (White parboiled rice)",
    "சுண்ட வத்தல் (Dried ginger)",
    "மனத்தக்காலி வத்தல் (Bird's eye chili)",
    "மோர் மிளகாய் (Yogurt chilies)",
    "மிதுக்கு வத்தல் (Guntur chili)",
    "பட் அப்பளம் (Batten appalam)",
    "Heart Appalam (Heart appalam)",
    "வெங்காய வடகம் (Onion vadai)",
    "கொத்தவரங்காய் வத்தல் (Cluster beans sundried)",
    "அடை மிக்ஸ் (Adai mix)",
    "கடலை மாவு (Gram flour)",
    "மூங்கில் அரிசி (Foxtail millet)",
    "வருத்த வெள்ளை ரவை (Roasted semolina)",
    "கொள்ளுக்கஞ்சி மாவு (Horse gram kanji flour)",
    "கொள்ளு மாவு (Horse gram flour)",
    "பச்சைப் பயறு (Green Gram)"
]

class ContainsFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_text = ""

    def setFilterFixedString(self, pattern):
        self.filter_text = pattern
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filter_text:
            return True
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        data = model.data(index, Qt.DisplayRole)
        return self.filter_text.lower() in data.lower()

class BillGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bill Generator - PyQt5")
        # Set a more reasonable default size that works on most screens
        self.resize(1200, 800)
        self.center_window()
        self.font = QFont("Arial", 12)
        self.items = []
        self._initialize_database() # Ensure database and table exist
        self.bill_number = self.get_current_bill_number()
        self.init_ui()
        self.update_transaction_fields() # Initialize UI based on default Debit selection

    def _initialize_database(self):
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bill_number INTEGER NOT NULL UNIQUE,
                        customer_key TEXT NOT NULL,
                        date TEXT NOT NULL,
                        items TEXT NOT NULL,
                        total_amount REAL NOT NULL,
                        transaction_type TEXT NOT NULL,
                        remarks TEXT
                    )
                ''')
                conn.commit()
                print("Database initialized successfully (if not already existing).")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {str(e)}")

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Navigation header
        nav_layout = QHBoxLayout()
        self.btn_bill_generator = QPushButton("Bill Generator")
        self.btn_statement_generator = QPushButton("Statement Generator")
        self.btn_bill_generator.setFont(self.font)
        self.btn_statement_generator.setFont(self.font)
        nav_layout.addWidget(self.btn_bill_generator)
        nav_layout.addWidget(self.btn_statement_generator)
        main_layout.addLayout(nav_layout)

        # Stacked widget to switch between sections
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Bill Generator widget
        self.bill_generator_widget = QWidget()
        bill_layout = QVBoxLayout()

        customer_layout = QHBoxLayout()
        customer_label = QLabel("Select Customer:")
        customer_label.setFont(self.font)
        self.customer_combo = QComboBox()
        self.customer_combo.setFont(self.font)
        self.customer_combo.addItems(customers.keys())
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.customer_combo)
        bill_layout.addLayout(customer_layout)

        # Date and Bill Number entry
        date_bill_layout = QHBoxLayout()
        
        # Date entry (smaller)
        date_label = QLabel("Date:")
        date_label.setFont(self.font)
        self.date_entry = QLineEdit(datetime.now().strftime("%d-%m-%Y"))
        self.date_entry.setFont(self.font)
        self.date_entry.setFixedWidth(120)  # Make date entry smaller
        date_bill_layout.addWidget(date_label)
        date_bill_layout.addWidget(self.date_entry)
        
        # Add some spacing
        date_bill_layout.addSpacing(20)
        
        # Bill Number entry (larger)
        bill_number_label = QLabel("Bill Number:")
        bill_number_label.setFont(self.font)
        self.bill_number_entry = QSpinBox()
        self.bill_number_entry.setFont(self.font)
        self.bill_number_entry.setMinimum(1)
        self.bill_number_entry.setMaximum(999999)
        self.bill_number_entry.setValue(self.bill_number)
        self.bill_number_entry.setFixedWidth(150)  # Make bill number entry larger
        date_bill_layout.addWidget(bill_number_label)
        date_bill_layout.addWidget(self.bill_number_entry)
        
        # Add stretch to push fields to the left
        date_bill_layout.addSpacing(20)
        
        bill_layout.addLayout(date_bill_layout)

        # Transaction Type
        transaction_type_layout = QHBoxLayout()
        transaction_type_label = QLabel("Transaction Type:")
        transaction_type_label.setFont(self.font)
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.setFont(self.font)
        self.transaction_type_combo.addItems(["Debit", "Credit"])
        self.transaction_type_combo.currentIndexChanged.connect(self.update_transaction_fields)
        transaction_type_layout.addWidget(transaction_type_label)
        transaction_type_layout.addWidget(self.transaction_type_combo)
        bill_layout.addLayout(transaction_type_layout)

        # Remarks
        self.remarks_layout = QHBoxLayout()
        remarks_label = QLabel("Remarks:")
        remarks_label.setFont(self.font)
        self.remarks_entry = QLineEdit()
        self.remarks_entry.setFont(self.font)
        self.remarks_layout.addWidget(remarks_label)
        self.remarks_layout.addWidget(self.remarks_entry)
        bill_layout.addLayout(self.remarks_layout)

        # Credit Amount (initially hidden)
        self.credit_amount_layout = QHBoxLayout()
        self.credit_amount_label = QLabel("Credit Amount:")
        self.credit_amount_label.setFont(self.font)
        self.credit_amount_entry = QDoubleSpinBox()
        self.credit_amount_entry.setFont(self.font)
        self.credit_amount_entry.setMaximum(1000000)
        self.credit_amount_entry.setPrefix("₹")
        self.credit_amount_layout.addWidget(self.credit_amount_label)
        self.credit_amount_layout.addWidget(self.credit_amount_entry)
        bill_layout.addLayout(self.credit_amount_layout)
        self.credit_amount_label.hide()
        self.credit_amount_entry.hide()

        # Item entry fields (will be hidden for credit transactions)
        self.item_layout = QHBoxLayout()
        item_name_label = QLabel("Item Name:")
        item_name_label.setFont(self.font)
        self.item_name_combo = QComboBox()
        self.item_name_combo.setFont(self.font)
        self.item_name_combo.setEditable(True)
        self.item_name_combo.setInsertPolicy(QComboBox.NoInsert)
        self.item_name_combo.setMaxVisibleItems(10)
        self.item_name_combo.addItem("")
        self.item_name_combo.addItems(suggestions)

        # --- Fuzzywuzzy completer setup ---
        self.completer_model = QStringListModel(suggestions)
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.item_name_combo.setCompleter(self.completer)
        self.item_name_combo.lineEdit().textEdited.connect(self.update_fuzzy_completer)

        self.item_layout.addWidget(item_name_label)
        self.item_layout.addWidget(self.item_name_combo)

        price_label = QLabel("Price:")
        price_label.setFont(self.font)
        self.price_entry = QDoubleSpinBox()
        self.price_entry.setFont(self.font)
        self.price_entry.setMaximum(1000000)
        self.price_entry.setPrefix("₹")
        self.item_layout.addWidget(price_label)
        self.item_layout.addWidget(self.price_entry)

        quantity_label = QLabel("Quantity:")
        quantity_label.setFont(self.font)
        self.quantity_entry = QDoubleSpinBox()
        self.quantity_entry.setFont(self.font)
        self.quantity_entry.setMinimum(0.01)
        self.quantity_entry.setMaximum(10000)
        self.quantity_entry.setDecimals(2)
        self.quantity_entry.setValue(1.0)
        self.item_layout.addWidget(quantity_label)
        self.item_layout.addWidget(self.quantity_entry)

        self.add_button = QPushButton("Add Item")
        self.add_button.setFont(self.font)
        self.add_button.clicked.connect(self.add_item)
        self.item_layout.addWidget(self.add_button)

        bill_layout.addLayout(self.item_layout)

        self.debit_fields_widgets = [
            item_name_label,
            self.item_name_combo,
            price_label,
            self.price_entry,
            quantity_label,
            self.quantity_entry,
            self.add_button
        ]

        self.items_list = QListWidget()
        self.items_list.setFont(self.font)
        bill_layout.addWidget(self.items_list)

        self.items_list.setSelectionMode(QListWidget.SingleSelection)
        self.items_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.items_list.customContextMenuRequested.connect(self.show_item_context_menu)

        total_layout = QHBoxLayout()
        total_label = QLabel("Total:")
        total_label.setFont(self.font)
        self.total_display = QLineEdit("₹0.00")
        self.total_display.setFont(self.font)
        self.total_display.setReadOnly(True)
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_display)
        bill_layout.addLayout(total_layout)

        buttons_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Bill")
        self.generate_button.setFont(self.font)
        self.generate_button.clicked.connect(self.generate_bill)
        buttons_layout.addWidget(self.generate_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setFont(self.font)
        self.clear_button.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_button)

        bill_layout.addLayout(buttons_layout)

        self.bill_generator_widget.setLayout(bill_layout)
        self.stacked_widget.addWidget(self.bill_generator_widget)

        # Statement Generator widget
        self.statement_generator_widget = QWidget()
        statement_layout = QVBoxLayout()

        # Inputs for start date, end date, customer name
        form_layout = QHBoxLayout()

        start_date_label = QLabel("Start Date:")
        start_date_label.setFont(self.font)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setFont(self.font)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        form_layout.addWidget(start_date_label)
        form_layout.addWidget(self.start_date_edit)

        end_date_label = QLabel("End Date:")
        end_date_label.setFont(self.font)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setFont(self.font)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        form_layout.addWidget(end_date_label)
        form_layout.addWidget(self.end_date_edit)

        customer_name_label = QLabel("Customer:")
        customer_name_label.setFont(self.font)
        self.customer_name_combo = QComboBox()
        self.customer_name_combo.setFont(self.font)
        self.customer_name_combo.addItem("")  # Allow empty for all customers
        self.customer_name_combo.addItems(customers.keys())
        form_layout.addWidget(customer_name_label)
        form_layout.addWidget(self.customer_name_combo)

        statement_layout.addLayout(form_layout)

        # Generate statement button
        self.generate_statement_button = QPushButton("Generate Statement")
        self.generate_statement_button.setFont(self.font)
        self.generate_statement_button.clicked.connect(self.generate_statement)
        statement_layout.addWidget(self.generate_statement_button)

        self.statement_generator_widget.setLayout(statement_layout)
        self.stacked_widget.addWidget(self.statement_generator_widget)

        # Connect navigation buttons
        self.btn_bill_generator.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.bill_generator_widget))
        self.btn_statement_generator.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.statement_generator_widget))

        self.setLayout(main_layout)

    def center_window(self):
        """Center the window on the screen with adaptive sizing"""
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        window_geometry = self.geometry()
        
        # Ensure window doesn't exceed screen size
        max_width = min(1200, screen_geometry.width() - 100)
        max_height = min(800, screen_geometry.height() - 100)
        
        # Resize if window is too large for screen
        if window_geometry.width() > max_width or window_geometry.height() > max_height:
            self.resize(max_width, max_height)
            window_geometry = self.geometry()
        
        # Calculate center position
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        
        # Ensure window doesn't go off-screen
        x = max(0, min(x, screen_geometry.width() - window_geometry.width()))
        y = max(0, min(y, screen_geometry.height() - window_geometry.height()))
        
        # Move window to center
        self.move(x, y)

    def update_transaction_fields(self):
        transaction_type = self.transaction_type_combo.currentText()
        if transaction_type == "Credit":
            for widget in self.debit_fields_widgets:
                widget.hide()
            self.items_list.hide()
            self.total_display.hide()
            self.credit_amount_label.show()
            self.credit_amount_entry.show()
            self.remarks_entry.show() # Show the remarks entry widget
            self.add_button.setText("Add Credit")
            self.items_list.clear()
            self.items = [] # Clear existing items for credit transactions
            self.calculate_total()
        else: # Debit
            for widget in self.debit_fields_widgets:
                widget.show()
            self.items_list.show()
            self.total_display.show()
            self.credit_amount_label.hide()
            self.credit_amount_entry.hide()
            self.remarks_entry.show() # Show the remarks entry widget
            self.add_button.setText("Add Item")
            self.credit_amount_entry.setValue(0.0)

    def get_current_bill_number(self):
        try:
            with open(BILL_NUMBER_PATH, "r") as file:
                return int(file.read().strip())
        except (FileNotFoundError, ValueError):
            return 1

    def autocomplete_item_name(self, text):
        pass

    def insert_suggestion(self, item):
        pass

    def show_item_context_menu(self, position):
        menu = QMenu()
        remove_action = menu.addAction("Remove Item")
        action = menu.exec_(self.items_list.viewport().mapToGlobal(position))
        if action == remove_action:
            self.remove_selected_item()

    def remove_selected_item(self):
        selected_items = self.items_list.selectedItems()
        if not selected_items:
            return
        selected_item = selected_items[0]
        index = self.items_list.row(selected_item)
        if 0 <= index < len(self.items):
            del self.items[index]
            self.update_items_list()
            self.calculate_total()

    def save_bill_number(self):
        with open(BILL_NUMBER_PATH, "w") as file:
            file.write(str(self.bill_number))

    def add_item(self):
        transaction_type = self.transaction_type_combo.currentText()
        if transaction_type == "Debit":
            item_name = self.item_name_combo.currentText().strip()
            price = self.price_entry.value()
            quantity = self.quantity_entry.value()

            if not item_name or price <= 0 or quantity <= 0:
                QMessageBox.critical(self, "Error", "Please enter valid item details")
                return

            total = price * quantity

            # Check if item already exists in the list and update it
            for item in self.items:
                if item["name"].lower() == item_name.lower() and item.get("type") != "Credit":
                    item["quantity"] += quantity
                    item["total"] += total
                    self.update_items_list()
                    self.clear_item_entry()
                    self.calculate_total()
                    self.item_name_combo.setFocus()
                    return

            # Add new item
            item = {
                "name": item_name,
                "price": price,
                "quantity": quantity,
                "total": total,
                "type": "Debit" # Explicitly mark as Debit
            }
            self.items.append(item)
            self.update_items_list()
            self.clear_item_entry()
            self.calculate_total()
            self.item_name_combo.setFocus()
        else: # Credit
            credit_amount = self.credit_amount_entry.value()
            remarks = self.remarks_entry.text().strip()

            if credit_amount <= 0:
                QMessageBox.critical(self, "Error", "Please enter a valid credit amount")
                return
            
            # For credit, we consider it a single 'item' entry for display in the list
            item = {
                "name": remarks if remarks else "Credit Entry", # Use remarks as name if available
                "price": 0.0, # Not applicable for credit item
                "quantity": 0, # Not applicable for credit item
                "total": credit_amount,
                "type": "Credit",
                "remarks": remarks
            }
            # Clear existing items if any, as credit transactions are standalone
            self.items = [item]
            self.update_items_list()
            self.credit_amount_entry.setValue(0.0)
            self.remarks_entry.clear()
            self.calculate_total()

    def update_items_list(self):
        self.items_list.clear()
        for idx, item in enumerate(self.items):
            widget = QtWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            if item.get("type") == "Credit":
                label = QLabel(f"Credit: ₹{item['total']:.2f} - Remarks: {item['remarks']}")
            else:
                label = QLabel(f"{item['name']} - ₹{item['price']:.2f} x {item['quantity']:.2f} = ₹{item['total']:.2f}")
            label.setFont(self.font)
            remove_btn = QPushButton("✖")
            remove_btn.setFixedSize(24, 24)
            remove_btn.setStyleSheet("color: red; font-weight: bold;")
            remove_btn.clicked.connect(lambda _, i=idx: self.remove_item_by_index(i))
            layout.addWidget(label)
            layout.addWidget(remove_btn)
            widget.setLayout(layout)
            list_item = QListWidgetItem(self.items_list)
            list_item.setSizeHint(widget.sizeHint())
            self.items_list.addItem(list_item)
            self.items_list.setItemWidget(list_item, widget)

    def remove_item_by_index(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]
            self.update_items_list()
            self.calculate_total()

    def clear_item_entry(self):
        self.item_name_combo.setCurrentIndex(0)
        self.item_name_combo.setEditText("")
        self.price_entry.setValue(0.0)
        self.quantity_entry.setValue(1.0)

    def calculate_total(self):
        total = sum(item["total"] for item in self.items)
        self.total_display.setText(f"₹{total:.2f}")

    def generate_html_bill(self):
        customer_key = self.customer_combo.currentText()
        customer = customers[customer_key]
        item_rows = ""
        for index, item in enumerate(self.items):
            item_rows += f"""<tr>
            <td>{index + 1}</td>
            <td>{item['name']}</td>
            <td>{item['quantity']:.2f}</td>
            <td>₹{item['price']:.2f}</td>
            <td colspan="2">₹{item['total']:.2f}</td>
            </tr>"""

        invoice_filename_js = f"Invoice_{self.bill_number}"
        html_content = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invoice</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            .invoice {{
                border: 1px solid red;
                padding: 20px;
                max-width: 800px;
                margin: auto;
            }}
            .invoice-header {{
                text-align: center;
                border:1px solid red;
                padding-bottom: 18px;
           }}
            .invoice-header img {{
                max-width: 100px;
            }}
            .invoice-header h1 {{
                margin: 0;
                color: red;
            }}
            .invoice-header p {{
                margin: 2px 0;
            }}
            .invoice-info {{
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
            }}
            .invoice-info div {{
                width: 48%;
            }}
            .invoice-info .sales-to,
            .invoice-info .address {{
                margin-top: 20px;
            }}
            .invoice-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .invoice-table th, .invoice-table td {{
                border: 1px solid red;
                padding: 8px;
                text-align: left;
            }}
            .invoice-table th {{
                background-color: #f2f2f2;
            }}
            .invoice-total {{
                width: 100%;
                margin-top: 20px;
                text-align: right;
            }}
            .invoice-total table {{
                width: 50%;
                float: right;
                border-collapse: collapse;
            }}
            .invoice-total th, .invoice-total td {{
                border: 1px solid red;
                padding: 8px;
            }}         
            .invoice-signature {{
                margin-top: 40px;
                text-align: right;
            }}
            .download-btn {{
                margin-top: 20px;
                display: flex;
                justify-content: flex-end;
            }}
            .download-btn button {{
                background: red;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="invoice" id="invoice">
        <div class="invoice">
            <div class="invoice-header">
                <div style="position:absolute; border-color: red;">
                    <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/" alt="Logo">
                </div>
                <h1>SADHASIVA AGENCIES</h1>
                <p>4/53, Bhairavi Nagar, Puliyankulam,</p>
                <p>Inamreddiyapatti Post, Virudhunagar - 626 003.</p>
                <p>Cell: 88258 08813, 91596 84261</p>
            </div>
            <div class="invoice-info">
                <div>
                    <p>No. <strong>{self.bill_number}</strong></p>
                    <p class="sales-to">To: {customer["name"]}</p>
                    <p class="address">Address: {customer["address"]}</p>
                </div>
                <div>
                    <p>&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Date: {self.date_entry.text()}</p>
                </div>
            </div>
            <table class="invoice-table">
                <thead>
                    <tr>
                        <th>S.No.</th>
                        <th>PARTICULARS</th>
                        <th>QTY</th>
                        <th>RATE</th>
                        <th colspan="2">AMOUNT</th>
                    </tr>
                </thead>
                <tbody>
                    {item_rows}
                </tbody>
            </table>
            <div class="invoice-total">
                <table>
                    <tr>
                        <th>TOTAL</th>
                        <td>Rs. {self.total_display.text()}</td>
                    </tr>
                    <tr>
                        <th>SGST % + CGST %</th>
                        <td>Rs. 0.00</td>
                    </tr>
                    <tr>
                        <th>GRAND TOTAL</th>
                        <td>Rs. {self.total_display.text()}</td>
                    </tr>
                </table>
            </div>
            <div class="invoice-signature">
                <p>For <strong>SADHASIVA AGENCIES</strong></p>
                <p>Signature</p>
            </div>
        </div>
        </div>
        <div class="download-btn">
            <button onclick="downloadImage('invoice', '{invoice_filename_js}')">Download Invoice as Image</button>
        </div>
        <script>
        function downloadImage(elementId, filename) {{
            const element = document.getElementById(elementId);
            html2canvas(element).then(canvas => {{
                const link = document.createElement('a');
                link.download = filename + '.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            }});
        }}
        </script>
    </body>
    </html>"""

        # Save HTML content to a temporary file
        temp_html_path = os.path.join(TEMPLATE_DIR, f"temp_invoice_{self.bill_number}.html")
        with open(temp_html_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        # Open the generated HTML file
        webbrowser.open(temp_html_path)

    def update_bill_number(self):
        try:
            with open(BILL_NUMBER_PATH, "r") as file:
                bill_number = int(file.read())

            with open(BILL_NUMBER_PATH, "w") as file:
                file.write(str(bill_number + 1))

            self.bill_number = bill_number + 1
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update bill number: {str(e)}")

    def generate_bill(self):
        transaction_type = self.transaction_type_combo.currentText()

        if transaction_type == "Debit" and not self.items:
            QMessageBox.critical(self, "Error", "Please add items to the bill for a Debit transaction.")  
            return
        elif transaction_type == "Credit" and self.credit_amount_entry.value() <= 0:
            QMessageBox.critical(self, "Error", "Please enter a valid credit amount for a Credit transaction.")
            return

        try:
            # Get bill number from input field
            bill_number = self.bill_number_entry.value()
            
            # Save the bill with the specified bill number
            self.save_bill_to_database(bill_number)
            
            # Update the stored bill number to the next number after the current one
            self.bill_number = bill_number + 1
            with open(BILL_NUMBER_PATH, "w") as file:
                file.write(str(self.bill_number))
            # Update the bill number field to show the next number
            self.bill_number_entry.setValue(self.bill_number)
            
            # Only generate HTML bill for Debit transactions, as Credit will be part of ledger
            if transaction_type == "Debit":
                self.generate_html_bill()
            QMessageBox.information(self, "Success", "Transaction recorded successfully!")
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record transaction: {str(e)}")

    def save_bill_to_database(self, bill_number=None):
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()

                transaction_type = self.transaction_type_combo.currentText()
                remarks = self.remarks_entry.text().strip()
                total_amount = 0.0
                items_json = json.dumps([]) # Default to empty for credit entries

                if transaction_type == "Debit":
                    items_json = json.dumps(self.items)
                    total_amount = float(self.total_display.text().replace("₹", ""))
                elif transaction_type == "Credit":
                    total_amount = self.credit_amount_entry.value()
                    # For credit, we store a simplified item reflecting the credit amount and remarks     
                    credit_item = {
                        "name": remarks if remarks else "Credit Entry",
                        "price": total_amount, # Store credit amount here for simplicity
                        "quantity": 1,
                        "total": total_amount,
                        "type": "Credit",
                        "remarks": remarks
                    }
                    items_json = json.dumps([credit_item])
                    # Ensure the current self.items reflects the credit entry for display in items_list   
                    self.items = [credit_item]

                # Use the provided bill number or fall back to stored bill number
                bill_num = bill_number if bill_number is not None else self.bill_number

                # Insert bill record into the 'bills' table
                cursor.execute('''
                    INSERT INTO bills (bill_number, customer_key, date, items, total_amount, transaction_type, remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill_num,
                    self.customer_combo.currentText(),
                    self.date_entry.text(),
                    items_json,
                    total_amount,
                    transaction_type,
                    remarks
                ))

                conn.commit()
                print("Transaction data saved to database successfully.")

        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def clear_form(self):
        self.items = []
        self.update_items_list()
        self.clear_item_entry()
        self.total_display.setText("₹0.00")
        self.date_entry.setText(datetime.now().strftime("%d-%m-%Y"))
        # Reset bill number to current bill number
        self.bill_number_entry.setValue(self.bill_number)
        self.customer_combo.setCurrentIndex(0)
        self.transaction_type_combo.setCurrentIndex(0) # Reset to Debit
        self.remarks_entry.clear()
        self.credit_amount_entry.setValue(0.0)
        self.update_transaction_fields() # Update UI based on reset

    def get_bill(self, bill_number):
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM bills WHERE bill_number = ?', (bill_number,))
                bill = cursor.fetchone()
                if bill:
                    return {'bill': bill}
                return None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get bill: {str(e)}")
            return None

    def calculate_total_bill(self, bill_number=None, start_date=None, end_date=None):
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                if bill_number:
                    cursor.execute('SELECT total_amount FROM bills WHERE bill_number = ?', (bill_number,))
                    result = cursor.fetchone()
                    return result[0] if result else 0
                elif start_date and end_date:
                    cursor.execute('''
                        SELECT SUM(total_amount) FROM bills
                        WHERE date BETWEEN ? AND ?
                    ''', (start_date, end_date))
                    result = cursor.fetchone()
                    return result[0] if result else 0
                else:
                    return 0
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate total bill: {str(e)}")
            return 0

    def update_fuzzy_completer(self, text):
        if not text.strip():
            filtered = suggestions
        else:
            matches = process.extract(text, suggestions, limit=10)
            filtered = [match[0] for match in matches if match[1] > 40]
            if not filtered:
                filtered = suggestions
        self.completer_model.setStringList(filtered)
        self.completer.complete()  # Show the popup

    def generate_statement(self):
        start_date = self.start_date_edit.date().toString("dd-MM-yyyy")
        end_date = self.end_date_edit.date().toString("dd-MM-yyyy")
        customer_key = self.customer_name_combo.currentText()

        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()

                query = "SELECT bill_number, customer_key, total_amount, date, transaction_type, remarks, items FROM bills WHERE date BETWEEN ? AND ?"
                params = [start_date, end_date]

                if customer_key:
                    query += " AND customer_key = ?"
                    params.append(customer_key)

                cursor.execute(query, params)
                records = cursor.fetchall()

                if not records:
                    QMessageBox.information(self, "No Records", "No transactions found for the selected criteria.")
                    return

                # Generate HTML statement similar to Template1.html
                item_rows = ""
                total_debit = 0.0
                total_credit = 0.0

                for idx, (bill_no, cust_key, total_amt, date, transaction_type, remarks, items_json) in enumerate(records, start=1):
                    cust_name = customers.get(cust_key, {}).get("name", cust_key)

                    particulars = ""
                    if transaction_type == "Debit":
                        particulars = "To Sales"
                        total_debit += total_amt
                    elif transaction_type == "Credit":
                        particulars = f"By {remarks}"
                        total_credit += total_amt

                    item_rows += f"""
                    <tr>
                        <td>{date}</td>
                        <td>{particulars}</td>
                        <td>{transaction_type}</td>
                        <td>{bill_no}</td>
                        <td>{f'₹{total_amt:.2f}' if transaction_type == 'Debit' else ''}</td>
                        <td>{f'₹{total_amt:.2f}' if transaction_type == 'Credit' else ''}</td>
                    </tr>
                    """

                closing_balance = total_debit - total_credit
                balance_type = "Debit" if closing_balance >= 0 else "Credit"
                closing_balance_display = f"Rs. {abs(closing_balance):.2f} {balance_type}"

                statement_filename_js = f"Statement_{start_date}_to_{end_date}"
                html_content = f"""<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1" />
                    <title>Statement</title>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                        }}
                        .invoice {{
                            border: 1px solid red;
                            padding: 20px;
                            max-width: 800px;
                            margin: auto;
                        }}
                        .invoice-header {{
                            text-align: center;
                            border:1px solid red;
                            padding-bottom: 18px;
                        }}
                        .invoice-header img {{
                            max-width: 100px;
                        }}
                        .invoice-header h1 {{
                            margin: 0;
                            color: red;
                        }}
                        .invoice-header p {{
                            margin: 2px 0;
                        }}
                        .invoice-info {{
                            display: flex;
                            justify-content: space-between;
                            margin-top: 10px;
                        }}
                        .invoice-info div {{
                            width: 48%;
                        }}
                        .invoice-info .sales-to,
                        .invoice-info .address {{
                            margin-top: 20px;
                        }}
                        .invoice-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 20px;
                        }}
                        .invoice-table th, .invoice-table td {{
                            border: 1px solid red;
                            padding: 8px;
                            text-align: left;
                        }}
                        .invoice-table th {{
                            background-color: #f2f2f2;
                        }}
                        .invoice-total {{
                            width: 100%;
                            margin-top: 20px;
                            text-align: right;
                        }}
                        .invoice-total table {{
                            width: 50%;
                            float: right;
                            border-collapse: collapse;
                        }}
                        .invoice-total th, .invoice-total td {{
                            border: 1px solid red;
                            padding: 8px;
                        }}
                        .invoice-signature {{
                            margin-top: 40px;
                            text-align: right;
                        }}
                        .download-btn {{
                            margin-top: 20px;
                            display: flex;
                            justify-content: flex-end;
                        }}
                        .download-btn button {{
                            background: red;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            font-size: 16px;
                            border-radius: 5px;
                            cursor: pointer;
                        }}
                    </style>
                </head>
                <body>
                    <div class="invoice" id="invoice">
                        <div class="invoice-header">
                            <div style="position:absolute; border-color: red;">
                                <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/" alt="Logo">
                            </div>
                            <h1>SADHASIVA AGENCIES</h1>
                            <p>4/53, Bhairavi Nagar, Puliyankulam,</p>
                            <p>Inamreddiyapatti Post, Virudhunagar - 626 003.</p>
                            <p>Cell: 88258 08813, 91596 84261</p>
                        </div>
                        <h2 style="text-align: center;">Ledger Statement</h2>
                        <p style="text-align: center;">From {start_date} to {end_date}</p>
                        <table class="invoice-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Particulars</th>
                                    <th>Vch Type</th>
                                    <th>Vch No</th>
                                    <th>Debit</th>
                                    <th>Credit</th>
                                </tr>
                            </thead>
                            <tbody>
                                {item_rows}
                                <tr>
                                    <td colspan="4" style="text-align: right;"><strong>Total:</strong></td>
                                    <td><strong>₹{total_debit:.2f}</strong></td>
                                    <td><strong>₹{total_credit:.2f}</strong></td>
                                </tr>
                                <tr>
                                    <td colspan="4" style="text-align: right;"><strong>Closing Balance:</strong></td>
                                    <td colspan="2"><strong>{closing_balance_display}</strong></td>       
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="download-btn">
                        <button onclick="downloadImage('invoice', '{statement_filename_js}')">Download Statement as Image</button>
                    </div>
                    <script>
                    function downloadImage(elementId, filename) {{
                        const element = document.getElementById(elementId);
                        html2canvas(element).then(canvas => {{
                            const link = document.createElement('a');
                            link.download = filename + '.png';
                            link.href = canvas.toDataURL('image/png');
                            link.click();
                        }});
                    }}
                    </script>
                </body>
                </html>
                """

                # Save HTML content to a temporary file
                temp_html_path = os.path.join(TEMPLATE_DIR, f"temp_statement_{start_date}_to_{end_date}.html")
                with open(temp_html_path, "w", encoding="utf-8") as file:
                    file.write(html_content)

                # Open the generated HTML file
                webbrowser.open(temp_html_path)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate statement: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillGenerator()
    window.show()
    sys.exit(app.exec_())
