import requests
import json
import base64
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import io

class AIService:
    """Service for AI-powered features including handwriting recognition and OCR"""
    
    def __init__(self):
        # These would be deployed AI model endpoints
        self.handwriting_api_url = "https://api.handwriting-recognition.com/v1/recognize"
        self.ocr_api_url = "https://api.ocr-service.com/v1/extract"
        self.translation_api_url = "https://api.translation-service.com/v1/translate"
        self.invoice_analysis_url = "https://api.invoice-analysis.com/v1/analyze"
        
    def recognize_handwriting(self, image_data: bytes, language: str = "auto") -> Dict:
        """
        Recognize handwriting from image data
        
        Args:
            image_data: Raw image bytes
            language: Target language (tamil, english, auto)
            
        Returns:
            Dictionary with recognized text and confidence scores
        """
        try:
            # Convert image to base64 for API
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "image": image_b64,
                "language": language,
                "output_format": "structured"
            }
            
            # In a real deployment, this would call the actual AI service
            # For now, return mock data
            return self._mock_handwriting_response()
            
        except Exception as e:
            return {"error": str(e), "text": "", "confidence": 0.0}
    
    def extract_text_ocr(self, image_data: bytes) -> Dict:
        """
        Extract text using OCR from images
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with extracted text and bounding boxes
        """
        try:
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Mock OCR response - in production this would use EasyOCR or Tesseract
            return self._mock_ocr_response()
            
        except Exception as e:
            return {"error": str(e), "text": "", "regions": []}
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dictionary with translated text
        """
        try:
            payload = {
                "text": text,
                "source": source_lang,
                "target": target_lang
            }
            
            # Mock translation response
            return self._mock_translation_response(text, target_lang)
            
        except Exception as e:
            return {"error": str(e), "translated_text": text}
    
    def analyze_invoice_image(self, image_data: bytes) -> Dict:
        """
        Analyze invoice image and extract structured data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with extracted invoice data
        """
        try:
            # This would use a specialized invoice analysis model
            return self._mock_invoice_analysis()
            
        except Exception as e:
            return {"error": str(e), "items": [], "total": 0.0}
    
    def _mock_handwriting_response(self) -> Dict:
        """Mock handwriting recognition response"""
        return {
            "text": "நாட்டு சக்கரை 5 கிலோ",
            "confidence": 0.92,
            "language_detected": "tamil",
            "words": [
                {"text": "நாட்டு", "confidence": 0.95, "bbox": [10, 20, 80, 45]},
                {"text": "சக்கரை", "confidence": 0.90, "bbox": [85, 20, 150, 45]},
                {"text": "5", "confidence": 0.98, "bbox": [155, 20, 170, 45]},
                {"text": "கிலோ", "confidence": 0.88, "bbox": [175, 20, 220, 45]}
            ]
        }
    
    def _mock_ocr_response(self) -> Dict:
        """Mock OCR response"""
        return {
            "text": "Invoice #12345\nDate: 2025-01-15\nTotal: ₹1500.00",
            "regions": [
                {"text": "Invoice #12345", "bbox": [50, 30, 200, 55], "confidence": 0.96},
                {"text": "Date: 2025-01-15", "bbox": [50, 70, 180, 95], "confidence": 0.94},
                {"text": "Total: ₹1500.00", "bbox": [50, 110, 200, 135], "confidence": 0.98}
            ]
        }
    
    def _mock_translation_response(self, text: str, target_lang: str) -> Dict:
        """Mock translation response"""
        translations = {
            "english": {
                "நாட்டு சக்கரை": "Country sugar",
                "ராகி": "Ragi",
                "கம்பு": "Pearl millet"
            },
            "tamil": {
                "Country sugar": "நாட்டு சக்கரை",
                "Ragi": "ராகி",
                "Pearl millet": "கம்பு"
            }
        }
        
        translated = translations.get(target_lang, {}).get(text, text)
        
        return {
            "translated_text": translated,
            "source_language": "auto",
            "target_language": target_lang,
            "confidence": 0.95
        }
    
    def _mock_invoice_analysis(self) -> Dict:
        """Mock invoice analysis response"""
        return {
            "vendor": "SADHASIVA AGENCIES",
            "invoice_number": "12345",
            "date": "2025-01-15",
            "items": [
                {
                    "name": "நாட்டு சக்கரை",
                    "quantity": 5,
                    "unit": "kg",
                    "rate": 45.0,
                    "amount": 225.0
                },
                {
                    "name": "ராகி மாவு",
                    "quantity": 2,
                    "unit": "kg", 
                    "rate": 80.0,
                    "amount": 160.0
                }
            ],
            "subtotal": 385.0,
            "tax": 0.0,
            "total": 385.0,
            "confidence": 0.89
        }