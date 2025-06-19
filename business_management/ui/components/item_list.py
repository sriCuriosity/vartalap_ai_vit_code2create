from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

class ItemListWidget(QWidget):
    item_removed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.font = QFont("Arial", 12)
        self.items = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setFont(self.font)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def update_items(self, items):
        self.items = items
        self.list_widget.clear()
        for idx, item in enumerate(items):
            widget = QWidget()
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)
            label = QLabel(f"{item['name']} - ₹{item['price']:.2f} x {item['quantity']} = ₹{item['total']:.2f}")
            label.setFont(self.font)
            remove_btn = QPushButton("✖")
            remove_btn.setFixedSize(24, 24)
            remove_btn.setStyleSheet("color: red; font-weight: bold;")
            remove_btn.clicked.connect(lambda _, i=idx: self.item_removed.emit(i))
            h_layout.addWidget(label)
            h_layout.addWidget(remove_btn)
            widget.setLayout(h_layout)
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, widget)
