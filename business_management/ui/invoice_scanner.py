from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, 
    QProgressBar, QGroupBox, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from business_management.services.ai_service import AIService
from business_management.services.image_service import ImageService
from business_management.models.bill import Bill
import json

class InvoiceScanThread(QThread):
    """Thread for invoice scanning and analysis"""
    
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, image_data):
        super().__init__()
        self.image_data = image_data
        self.ai_service = AIService()
        self.image_service = ImageService()
    
    def run(self):
        try:
            # Preprocess image
            processed_image = self.image_service.preprocess_image(self.image_data)
            
            # Analyze invoice
            result = self.ai_service.analyze_invoice_image(processed_image)
            
            self.result_ready.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class InvoiceScannerWidget(QWidget):
    """Widget for scanning and analyzing invoice images"""
    
    invoice_data_ready = pyqtSignal(dict)  # Signal to emit extracted invoice data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font = QFont("Arial", 12)
        self.ai_service = AIService()
        self.current_image_data = None
        self.scan_thread = None
        self.extracted_data = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Invoice Scanner & Analyzer")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Image upload section
        upload_group = QGroupBox("Upload Invoice Image")
        upload_layout = QVBoxLayout()
        
        upload_btn_layout = QHBoxLayout()
        self.upload_btn = QPushButton("Select Invoice Image")
        self.upload_btn.setFont(self.font)
        self.upload_btn.clicked.connect(self.select_image)
        
        self.scan_btn = QPushButton("Scan & Analyze")
        self.scan_btn.setFont(self.font)
        self.scan_btn.clicked.connect(self.scan_invoice)
        self.scan_btn.setEnabled(False)
        
        upload_btn_layout.addWidget(self.upload_btn)
        upload_btn_layout.addWidget(self.scan_btn)
        upload_layout.addLayout(upload_btn_layout)
        
        # Image preview
        self.image_label = QLabel("No invoice image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        upload_layout.addWidget(self.image_label)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results section
        results_group = QGroupBox("Extracted Invoice Data")
        results_layout = QVBoxLayout()
        
        # Invoice header info
        header_layout = QHBoxLayout()
        
        vendor_layout = QVBoxLayout()
        vendor_layout.addWidget(QLabel("Vendor:"))
        self.vendor_edit = QLineEdit()
        self.vendor_edit.setFont(self.font)
        vendor_layout.addWidget(self.vendor_edit)
        
        invoice_num_layout = QVBoxLayout()
        invoice_num_layout.addWidget(QLabel("Invoice #:"))
        self.invoice_num_edit = QLineEdit()
        self.invoice_num_edit.setFont(self.font)
        invoice_num_layout.addWidget(self.invoice_num_edit)
        
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_edit = QLineEdit()
        self.date_edit.setFont(self.font)
        date_layout.addWidget(self.date_edit)
        
        header_layout.addLayout(vendor_layout)
        header_layout.addLayout(invoice_num_layout)
        header_layout.addLayout(date_layout)
        results_layout.addLayout(header_layout)
        
        # Items table
        items_label = QLabel("Items:")
        items_label.setFont(self.font)
        results_layout.addWidget(items_label)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Item Name", "Quantity", "Unit", "Rate", "Amount"])
        self.items_table.setFont(self.font)
        results_layout.addWidget(self.items_table)
        
        # Total section
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Total Amount:"))
        self.total_edit = QLineEdit()
        self.total_edit.setFont(self.font)
        self.total_edit.setReadOnly(True)
        total_layout.addWidget(self.total_edit)
        results_layout.addLayout(total_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.create_bill_btn = QPushButton("Create Bill from Data")
        self.create_bill_btn.setFont(self.font)
        self.create_bill_btn.clicked.connect(self.create_bill_from_data)
        self.create_bill_btn.setEnabled(False)
        
        self.export_btn = QPushButton("Export Data")
        self.export_btn.setFont(self.font)
        self.export_btn.clicked.connect(self.export_data)
        self.export_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFont(self.font)
        self.clear_btn.clicked.connect(self.clear_data)
        
        action_layout.addWidget(self.create_bill_btn)
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.clear_btn)
        action_layout.addStretch()
        results_layout.addLayout(action_layout)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def select_image(self):
        """Open file dialog to select invoice image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Invoice Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.pdf)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """Load and display invoice image"""
        try:
            with open(file_path, 'rb') as f:
                self.current_image_data = f.read()
            
            # Display image
            if file_path.lower().endswith('.pdf'):
                self.image_label.setText("PDF file loaded\n(Preview not available)")
            else:
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(400, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
            
            self.scan_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def scan_invoice(self):
        """Start invoice scanning and analysis"""
        if not self.current_image_data:
            QMessageBox.warning(self, "Warning", "Please select an invoice image first.")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.scan_btn.setEnabled(False)
        
        # Start scanning thread
        self.scan_thread = InvoiceScanThread(self.current_image_data)
        self.scan_thread.result_ready.connect(self.on_scan_complete)
        self.scan_thread.error_occurred.connect(self.on_scan_error)
        self.scan_thread.start()
    
    def on_scan_complete(self, result):
        """Handle scan completion"""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        if "error" in result:
            QMessageBox.critical(self, "Error", f"Invoice analysis failed: {result['error']}")
            return
        
        # Store extracted data
        self.extracted_data = result
        
        # Populate form fields
        self.vendor_edit.setText(result.get("vendor", ""))
        self.invoice_num_edit.setText(str(result.get("invoice_number", "")))
        self.date_edit.setText(result.get("date", ""))
        self.total_edit.setText(f"₹{result.get('total', 0.0):.2f}")
        
        # Populate items table
        items = result.get("items", [])
        self.items_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item.get("name", "")))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item.get("quantity", ""))))
            self.items_table.setItem(row, 2, QTableWidgetItem(item.get("unit", "")))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"₹{item.get('rate', 0.0):.2f}"))
            self.items_table.setItem(row, 4, QTableWidgetItem(f"₹{item.get('amount', 0.0):.2f}"))
        
        # Resize columns to content
        self.items_table.resizeColumnsToContents()
        
        # Enable action buttons
        self.create_bill_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        # Show confidence score
        confidence = result.get("confidence", 0.0)
        QMessageBox.information(
            self, 
            "Scan Complete", 
            f"Invoice analysis completed!\nConfidence: {confidence:.1%}"
        )
    
    def on_scan_error(self, error_message):
        """Handle scan error"""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        QMessageBox.critical(self, "Scan Error", error_message)
    
    def create_bill_from_data(self):
        """Create a bill from the extracted data"""
        if not self.extracted_data:
            return
        
        # Emit the extracted data for use in bill generator
        self.invoice_data_ready.emit(self.extracted_data)
        QMessageBox.information(
            self, 
            "Success", 
            "Invoice data has been loaded into the bill generator."
        )
    
    def export_data(self):
        """Export extracted data to JSON file"""
        if not self.extracted_data:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Invoice Data", 
            "invoice_data.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
    
    def clear_data(self):
        """Clear all data and reset the widget"""
        self.current_image_data = None
        self.extracted_data = None
        
        self.image_label.clear()
        self.image_label.setText("No invoice image selected")
        
        self.vendor_edit.clear()
        self.invoice_num_edit.clear()
        self.date_edit.clear()
        self.total_edit.clear()
        
        self.items_table.setRowCount(0)
        
        self.scan_btn.setEnabled(False)
        self.create_bill_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(False)