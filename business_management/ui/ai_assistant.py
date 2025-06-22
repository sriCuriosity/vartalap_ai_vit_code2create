from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor
import json
from datetime import datetime

class AIAssistantThread(QThread):
    """Thread for AI assistant processing"""
    
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, query, context=None):
        super().__init__()
        self.query = query
        self.context = context
    
    def run(self):
        try:
            # Simulate AI processing
            response = self.generate_response(self.query, self.context)
            self.response_ready.emit(response)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def generate_response(self, query, context):
        """Generate AI response (mock implementation)"""
        query_lower = query.lower()
        
        # Business-specific responses
        if "sales" in query_lower or "revenue" in query_lower:
            return "Based on your recent transactions, your sales have been steady. Consider analyzing your top-selling products like நாட்டு சக்கரை and ராகி மாவு to optimize inventory."
        
        elif "customer" in query_lower:
            return "Your customer base shows good diversity. Customer A has been your most frequent buyer. Consider offering loyalty discounts to retain customers."
        
        elif "inventory" in query_lower or "stock" in query_lower:
            return "Your product catalog includes 50+ items. Popular items include traditional grains and flours. Consider seasonal demand patterns for better stock management."
        
        elif "bill" in query_lower or "invoice" in query_lower:
            return "You can generate bills for both debit (sales) and credit (payments) transactions. Use the handwriting recognition feature to quickly add items from handwritten notes."
        
        elif "translate" in query_lower or "tamil" in query_lower or "english" in query_lower:
            return "I can help translate between Tamil and English for your product names and customer communications. This is especially useful for handwritten notes."
        
        elif "help" in query_lower:
            return """I can assist you with:
• Sales analysis and trends
• Customer management insights  
• Inventory optimization
• Bill generation guidance
• Tamil-English translation
• Handwriting recognition tips
• Statement generation

What would you like help with?"""
        
        else:
            return f"I understand you're asking about: '{query}'. Let me help you with that. Could you provide more specific details about what you need assistance with regarding your business operations?"

class ChatBubble(QFrame):
    """Custom widget for chat bubbles"""
    
    def __init__(self, message, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.init_ui(message)
    
    def init_ui(self, message):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Message text
        text_label = QLabel(message)
        text_label.setWordWrap(True)
        text_label.setFont(QFont("Arial", 11))
        
        if self.is_user:
            text_label.setStyleSheet("color: white;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #007bff;
                    border-radius: 15px;
                    margin-left: 50px;
                    margin-right: 10px;
                }
            """)
        else:
            text_label.setStyleSheet("color: #333;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #f1f1f1;
                    border-radius: 15px;
                    margin-left: 10px;
                    margin-right: 50px;
                }
            """)
        
        layout.addWidget(text_label)
        self.setLayout(layout)

class AIAssistantWidget(QWidget):
    """AI Assistant widget for business insights and help"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font = QFont("Arial", 12)
        self.assistant_thread = None
        self.chat_history = []
        self.init_ui()
        self.add_welcome_message()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("AI Business Assistant")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Chat area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setMinimumHeight(400)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_widget)
        layout.addWidget(self.chat_scroll)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setFont(self.font)
        self.message_input.setPlaceholderText("Ask me anything about your business...")
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setFont(self.font)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        
        # Quick action buttons
        quick_actions_layout = QHBoxLayout()
        
        quick_buttons = [
            ("Sales Analysis", "Show me my sales trends"),
            ("Customer Insights", "Tell me about my customers"),
            ("Inventory Help", "Help with inventory management"),
            ("Translation", "Help with Tamil-English translation")
        ]
        
        for button_text, query in quick_buttons:
            btn = QPushButton(button_text)
            btn.setFont(QFont("Arial", 10))
            btn.clicked.connect(lambda checked, q=query: self.send_quick_message(q))
            quick_actions_layout.addWidget(btn)
        
        layout.addLayout(quick_actions_layout)
        
        self.setLayout(layout)
    
    def add_welcome_message(self):
        """Add welcome message to chat"""
        welcome_msg = """Hello! I'm your AI business assistant. I can help you with:

• Sales analysis and insights
• Customer management
• Inventory optimization  
• Bill generation guidance
• Tamil-English translation
• Handwriting recognition tips

How can I assist you today?"""
        
        self.add_message(welcome_msg, is_user=False)
    
    def add_message(self, message, is_user=True):
        """Add a message to the chat"""
        # Remove stretch before adding new message
        self.chat_layout.removeItem(self.chat_layout.itemAt(self.chat_layout.count() - 1))
        
        # Add message bubble
        bubble = ChatBubble(message, is_user)
        self.chat_layout.addWidget(bubble)
        
        # Add stretch at the end
        self.chat_layout.addStretch()
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
        
        # Store in history
        self.chat_history.append({
            "message": message,
            "is_user": is_user,
            "timestamp": datetime.now().isoformat()
        })
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Send user message and get AI response"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Add user message
        self.add_message(message, is_user=True)
        self.message_input.clear()
        
        # Disable input while processing
        self.message_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.send_btn.setText("Thinking...")
        
        # Start AI processing
        self.assistant_thread = AIAssistantThread(message)
        self.assistant_thread.response_ready.connect(self.on_response_ready)
        self.assistant_thread.error_occurred.connect(self.on_response_error)
        self.assistant_thread.start()
    
    def send_quick_message(self, message):
        """Send a predefined quick message"""
        self.message_input.setText(message)
        self.send_message()
    
    def on_response_ready(self, response):
        """Handle AI response"""
        # Add AI response
        self.add_message(response, is_user=False)
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        self.message_input.setFocus()
    
    def on_response_error(self, error_message):
        """Handle AI response error"""
        error_response = f"Sorry, I encountered an error: {error_message}. Please try again."
        self.add_message(error_response, is_user=False)
        
        # Re-enable input
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Send")
        self.message_input.setFocus()
    
    def clear_chat(self):
        """Clear chat history"""
        # Clear layout
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Reset
        self.chat_layout.addStretch()
        self.chat_history.clear()
        self.add_welcome_message()
    
    def export_chat(self):
        """Export chat history"""
        if not self.chat_history:
            QMessageBox.information(self, "Info", "No chat history to export.")
            return
        
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Chat History", 
            f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.chat_history, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Success", f"Chat history exported to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))