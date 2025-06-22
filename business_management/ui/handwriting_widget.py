from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFileDialog, QMessageBox, QProgressBar, QComboBox,
    QGroupBox, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QImage
import os
from business_management.services.ai_service import AIService
from business_management.services.image_service import ImageService

class HandwritingRecognitionThread(QThread):
    """Thread for handwriting recognition processing"""
    
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, image_data, language="auto"):
        super().__init__()
        self.image_data = image_data
        self.language = language
        self.ai_service = AIService()
        self.image_service = ImageService()
    
    def run(self):
        try:
            # Preprocess image
            processed_image = self.image_service.preprocess_image(self.image_data)
            
            # Recognize handwriting
            result = self.ai_service.recognize_handwriting(processed_image, self.language)
            
            self.result_ready.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class HandwritingWidget(QWidget):
    """Widget for handwriting recognition functionality"""
    
    text_recognized = pyqtSignal(str)  # Signal to emit recognized text
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font = QFont("Arial", 12)
        self.ai_service = AIService()
        self.image_service = ImageService()
        self.current_image_data = None
        self.recognition_thread = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Handwriting Recognition")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Image upload section
        upload_group = QGroupBox("Upload Image")
        upload_layout = QVBoxLayout()
        
        upload_buttons_layout = QHBoxLayout()
        self.upload_btn = QPushButton("Select Image")
        self.upload_btn.setFont(self.font)
        self.upload_btn.clicked.connect(self.select_image)
        
        self.camera_btn = QPushButton("Take Photo")
        self.camera_btn.setFont(self.font)
        self.camera_btn.clicked.connect(self.take_photo)
        
        upload_buttons_layout.addWidget(self.upload_btn)
        upload_buttons_layout.addWidget(self.camera_btn)
        upload_layout.addLayout(upload_buttons_layout)
        
        # Image preview
        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        upload_layout.addWidget(self.image_label)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Language:")
        lang_label.setFont(self.font)
        self.language_combo = QComboBox()
        self.language_combo.setFont(self.font)
        self.language_combo.addItems(["Auto Detect", "Tamil", "English", "Tamil + English"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # Recognition controls
        controls_layout = QHBoxLayout()
        self.recognize_btn = QPushButton("Recognize Handwriting")
        self.recognize_btn.setFont(self.font)
        self.recognize_btn.clicked.connect(self.recognize_handwriting)
        self.recognize_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFont(self.font)
        self.clear_btn.clicked.connect(self.clear_results)
        
        controls_layout.addWidget(self.recognize_btn)
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results section
        results_group = QGroupBox("Recognition Results")
        results_layout = QVBoxLayout()
        
        # Recognized text
        text_label = QLabel("Recognized Text:")
        text_label.setFont(self.font)
        results_layout.addWidget(text_label)
        
        self.result_text = QTextEdit()
        self.result_text.setFont(self.font)
        self.result_text.setMaximumHeight(150)
        results_layout.addWidget(self.result_text)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.use_text_btn = QPushButton("Use This Text")
        self.use_text_btn.setFont(self.font)
        self.use_text_btn.clicked.connect(self.use_recognized_text)
        self.use_text_btn.setEnabled(False)
        
        self.translate_btn = QPushButton("Translate")
        self.translate_btn.setFont(self.font)
        self.translate_btn.clicked.connect(self.translate_text)
        self.translate_btn.setEnabled(False)
        
        action_layout.addWidget(self.use_text_btn)
        action_layout.addWidget(self.translate_btn)
        action_layout.addStretch()
        results_layout.addLayout(action_layout)
        
        # Confidence and details
        self.details_label = QLabel("")
        self.details_label.setFont(QFont("Arial", 10))
        self.details_label.setStyleSheet("color: #666;")
        results_layout.addWidget(self.details_label)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def select_image(self):
        """Open file dialog to select image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def take_photo(self):
        """Take photo using camera (placeholder)"""
        QMessageBox.information(
            self, 
            "Camera", 
            "Camera functionality would be implemented here.\nFor now, please use 'Select Image' to upload a file."
        )
    
    def load_image(self, file_path):
        """Load and display image"""
        try:
            with open(file_path, 'rb') as f:
                self.current_image_data = f.read()
            
            # Display image
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
            self.recognize_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def recognize_handwriting(self):
        """Start handwriting recognition"""
        if not self.current_image_data:
            QMessageBox.warning(self, "Warning", "Please select an image first.")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.recognize_btn.setEnabled(False)
        
        # Get selected language
        language_map = {
            "Auto Detect": "auto",
            "Tamil": "tamil", 
            "English": "english",
            "Tamil + English": "mixed"
        }
        selected_language = language_map[self.language_combo.currentText()]
        
        # Start recognition thread
        self.recognition_thread = HandwritingRecognitionThread(
            self.current_image_data, 
            selected_language
        )
        self.recognition_thread.result_ready.connect(self.on_recognition_complete)
        self.recognition_thread.error_occurred.connect(self.on_recognition_error)
        self.recognition_thread.start()
    
    def on_recognition_complete(self, result):
        """Handle recognition completion"""
        self.progress_bar.setVisible(False)
        self.recognize_btn.setEnabled(True)
        
        if "error" in result:
            QMessageBox.critical(self, "Error", f"Recognition failed: {result['error']}")
            return
        
        # Display results
        recognized_text = result.get("text", "")
        confidence = result.get("confidence", 0.0)
        language_detected = result.get("language_detected", "unknown")
        
        self.result_text.setText(recognized_text)
        self.details_label.setText(
            f"Confidence: {confidence:.1%} | Language: {language_detected}"
        )
        
        # Enable action buttons
        self.use_text_btn.setEnabled(bool(recognized_text))
        self.translate_btn.setEnabled(bool(recognized_text))
    
    def on_recognition_error(self, error_message):
        """Handle recognition error"""
        self.progress_bar.setVisible(False)
        self.recognize_btn.setEnabled(True)
        QMessageBox.critical(self, "Recognition Error", error_message)
    
    def use_recognized_text(self):
        """Emit the recognized text for use in other parts of the application"""
        text = self.result_text.toPlainText().strip()
        if text:
            self.text_recognized.emit(text)
            QMessageBox.information(self, "Success", "Text has been added to the current form.")
    
    def translate_text(self):
        """Translate the recognized text"""
        text = self.result_text.toPlainText().strip()
        if not text:
            return
        
        # Simple translation (in production, this would use the AI service)
        try:
            # Determine source and target languages
            current_lang = self.details_label.text()
            if "tamil" in current_lang.lower():
                translated = self.ai_service.translate_text(text, "tamil", "english")
            else:
                translated = self.ai_service.translate_text(text, "english", "tamil")
            
            translated_text = translated.get("translated_text", text)
            
            # Show translation in a message box
            QMessageBox.information(
                self, 
                "Translation", 
                f"Original: {text}\n\nTranslated: {translated_text}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Translation Error", str(e))
    
    def clear_results(self):
        """Clear all results and reset the widget"""
        self.current_image_data = None
        self.image_label.clear()
        self.image_label.setText("No image selected")
        self.result_text.clear()
        self.details_label.clear()
        self.recognize_btn.setEnabled(False)
        self.use_text_btn.setEnabled(False)
        self.translate_btn.setEnabled(False)
        self.progress_bar.setVisible(False)