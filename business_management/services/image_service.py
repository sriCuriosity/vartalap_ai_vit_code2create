import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
from typing import Tuple, Optional

class ImageService:
    """Service for image processing and enhancement"""
    
    @staticmethod
    def preprocess_image(image_data: bytes) -> bytes:
        """
        Preprocess image for better OCR/handwriting recognition
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Processed image bytes
        """
        try:
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return image_data
    
    @staticmethod
    def detect_text_regions(image_data: bytes) -> list:
        """
        Detect text regions in image using OpenCV
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            List of bounding boxes for text regions
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area and aspect ratio
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter based on size and aspect ratio
                if area > 100 and 0.1 < aspect_ratio < 10:
                    text_regions.append((x, y, w, h))
            
            return text_regions
            
        except Exception as e:
            print(f"Text region detection error: {e}")
            return []
    
    @staticmethod
    def crop_image_region(image_data: bytes, bbox: Tuple[int, int, int, int]) -> bytes:
        """
        Crop specific region from image
        
        Args:
            image_data: Raw image bytes
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            Cropped image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            x, y, w, h = bbox
            
            # Crop the region
            cropped = image.crop((x, y, x + w, y + h))
            
            # Convert back to bytes
            output = io.BytesIO()
            cropped.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            print(f"Image cropping error: {e}")
            return image_data
    
    @staticmethod
    def resize_image(image_data: bytes, max_size: Tuple[int, int] = (800, 600)) -> bytes:
        """
        Resize image while maintaining aspect ratio
        
        Args:
            image_data: Raw image bytes
            max_size: Maximum dimensions (width, height)
            
        Returns:
            Resized image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Calculate new size maintaining aspect ratio
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            print(f"Image resizing error: {e}")
            return image_data