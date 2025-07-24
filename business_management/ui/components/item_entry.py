from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QDoubleSpinBox, QSpinBox, QPushButton, QLineEdit, QCompleter
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from business_management.resources.suggestions import SUGGESTIONS
from business_management.utils.fuzzy_completer import get_fuzzy_matches

class ItemEntryWidget(QWidget):
    item_added = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.font = QFont("Arial", 12)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Item name
        item_name_label = QLabel("Item Name:")
        item_name_label.setFont(self.font)
        self.item_name_combo = QComboBox()
        self.item_name_combo.setFont(self.font)
        self.item_name_combo.setEditable(True)
        self.item_name_combo.addItems([""] + SUGGESTIONS)
        self.completer = QCompleter(SUGGESTIONS, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.item_name_combo.setCompleter(self.completer)
        self.item_name_combo.lineEdit().textEdited.connect(self.update_fuzzy_completer)
        layout.addWidget(item_name_label)
        layout.addWidget(self.item_name_combo)

        quantity_label = QLabel("Quantity:")
        quantity_label.setFont(self.font)
        self.quantity_entry = QDoubleSpinBox()
        self.quantity_entry.setFont(self.font)
        self.quantity_entry.setMinimum(0.01)
        self.quantity_entry.setMaximum(1000000.0)
        self.quantity_entry.setDecimals(3)
        self.quantity_entry.setSingleStep(1.0)
        layout.addWidget(quantity_label)
        layout.addWidget(self.quantity_entry)

        # Price
        price_label = QLabel("Price:")
        price_label.setFont(self.font)
        self.price_entry = QDoubleSpinBox()
        self.price_entry.setFont(self.font)
        self.price_entry.setMaximum(1000000)
        self.price_entry.setPrefix("₹")
        layout.addWidget(price_label)
        layout.addWidget(self.price_entry)

        # Add button
        self.add_button = QPushButton("Add Item")
        self.add_button.setFont(self.font)
        self.add_button.clicked.connect(self.emit_item_added)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def update_fuzzy_completer(self, text):
        filtered = get_fuzzy_matches(text, SUGGESTIONS)
        self.completer.model().setStringList(filtered)
        self.completer.complete()

    def emit_item_added(self):
        item_name = self.item_name_combo.currentText().strip()
        price = self.price_entry.value()
        quantity = self.quantity_entry.value()
        if not item_name or price <= 0 or quantity <= 0:
            return
        item = {
            "name": item_name,
            "price": price,
            "quantity": quantity,
            "total": price * quantity,
            "type": "Debit"
        }
        self.item_added.emit(item)
        self.clear_fields()

    def clear_fields(self):
        self.item_name_combo.setCurrentIndex(0)
        self.item_name_combo.setEditText("")
        self.price_entry.setValue(0.0)
        self.quantity_entry.setValue(0.0)

    def set_suggestions(self, suggestions):
        self.item_name_combo.clear()
        self.item_name_combo.addItems([""] + suggestions)
        self.completer.model().setStringList(suggestions)
