"""
Deployment script for invoice analysis model
This would be deployed as a cloud service
"""

import base64
import json
import io
from PIL import Image
import cv2
import numpy as np

class InvoiceAnalyzer:
    """Production invoice analysis model"""
    
    def __init__(self):
        # Load pre-trained models
        # self.text_detection_model = self.load_text_detection_model()
        # self.ocr_model = self.load_ocr_model()
        # self.layout_model = self.load_layout_analysis_model()
        pass
    
    def analyze_invoice(self, image_data):
        """
        Analyze invoice image and extract structured data
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            Structured invoice data
        """
        try:
            # Decode image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Detect text regions
            text_regions = self.detect_text_regions(cv_image)
            
            # Extract text from regions
            extracted_text = self.extract_text_from_regions(cv_image, text_regions)
            
            # Parse invoice structure
            invoice_data = self.parse_invoice_structure(extracted_text)
            
            return invoice_data
            
        except Exception as e:
            return {"error": str(e)}
    
    def detect_text_regions(self, image):
        """Detect text regions in invoice"""
        # In production, this would use EAST or similar text detection model
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and return bounding boxes
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 20:  # Filter small regions
                regions.append((x, y, w, h))
        
        return regions
    
    def extract_text_from_regions(self, image, regions):
        """Extract text from detected regions using OCR"""
        # In production, this would use Tesseract, EasyOCR, or custom OCR model
        extracted_texts = []
        
        for x, y, w, h in regions:
            # Crop region
            roi = image[y:y+h, x:x+w]
            
            # Mock OCR result
            text = self.mock_ocr(roi, x, y)
            if text:
                extracted_texts.append({
                    "text": text,
                    "bbox": (x, y, w, h),
                    "confidence": 0.9
                })
        
        return extracted_texts
    
    def mock_ocr(self, roi, x, y):
        """Mock OCR function - in production would use real OCR"""
        # Simple mock based on position
        if y < 100:  # Header region
            if x < 200:
                return "SADHASIVA AGENCIES"
            else:
                return "Invoice #12345"
        elif y < 200:  # Date/customer region
            if x < 200:
                return "Date: 2025-01-15"
            else:
                return "Customer A"
        else:  # Items region
            return "நாட்டு சக்கரை 5kg ₹225.00"
    
    def parse_invoice_structure(self, extracted_texts):
        """Parse extracted text into structured invoice data"""
        invoice_data = {
            "vendor": "",
            "invoice_number": "",
            "date": "",
            "customer": "",
            "items": [],
            "subtotal": 0.0,
            "tax": 0.0,
            "total": 0.0,
            "confidence": 0.85
        }
        
        # Parse extracted text (simplified logic)
        for text_item in extracted_texts:
            text = text_item["text"]
            y_pos = text_item["bbox"][1]
            
            if "SADHASIVA" in text:
                invoice_data["vendor"] = "SADHASIVA AGENCIES"
            elif "Invoice" in text and "#" in text:
                invoice_data["invoice_number"] = text.split("#")[-1].strip()
            elif "Date:" in text:
                invoice_data["date"] = text.replace("Date:", "").strip()
            elif "Customer" in text:
                invoice_data["customer"] = text
            elif "₹" in text and y_pos > 200:  # Items region
                # Parse item line
                item = self.parse_item_line(text)
                if item:
                    invoice_data["items"].append(item)
        
        # Calculate totals
        invoice_data["subtotal"] = sum(item["amount"] for item in invoice_data["items"])
        invoice_data["total"] = invoice_data["subtotal"] + invoice_data["tax"]
        
        return invoice_data
    
    def parse_item_line(self, text):
        """Parse individual item line"""
        # Simple parsing logic - in production would be more sophisticated
        parts = text.split()
        if len(parts) >= 3:
            name_parts = []
            quantity = 0
            amount = 0.0
            
            for part in parts:
                if "kg" in part:
                    try:
                        quantity = int(part.replace("kg", ""))
                    except:
                        pass
                elif "₹" in part:
                    try:
                        amount = float(part.replace("₹", ""))
                    except:
                        pass
                else:
                    name_parts.append(part)
            
            if name_parts and quantity > 0 and amount > 0:
                return {
                    "name": " ".join(name_parts),
                    "quantity": quantity,
                    "unit": "kg",
                    "rate": amount / quantity if quantity > 0 else 0,
                    "amount": amount
                }
        
        return None

# AWS Lambda handler
def lambda_handler(event, context):
    """AWS Lambda handler for invoice analysis"""
    try:
        analyzer = InvoiceAnalyzer()
        
        # Extract image data
        image_data = event.get("image")
        
        # Analyze invoice
        result = analyzer.analyze_invoice(image_data)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }