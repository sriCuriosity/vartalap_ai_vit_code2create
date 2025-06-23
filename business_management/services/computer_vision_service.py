import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
from typing import List, Tuple, Dict
import json

class ComputerVisionService:
    """Computer vision utilities for document processing"""
    
    def __init__(self):
        self.min_text_area = 100
        self.max_text_area = 50000
    
    def detect_text_regions(self, image_data: bytes) -> List[Tuple[int, int, int, int]]:
        """Detect text regions using OpenCV"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive threshold
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area and aspect ratio
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter based on size and aspect ratio
                if (self.min_text_area < area < self.max_text_area and 
                    0.1 < aspect_ratio < 20):
                    text_regions.append((x, y, w, h))
            
            # Sort regions by y-coordinate (top to bottom)
            text_regions.sort(key=lambda r: r[1])
            
            return text_regions
            
        except Exception as e:
            print(f"Text region detection error: {e}")
            return []
    
    def detect_table_structure(self, image_data: bytes) -> Dict:
        """Detect table structure in invoice images"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"rows": [], "columns": []}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Detect vertical lines
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            # Find horizontal line positions
            horizontal_contours, _ = cv2.findContours(
                horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Find vertical line positions
            vertical_contours, _ = cv2.findContours(
                vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Extract row and column boundaries
            rows = []
            for contour in horizontal_contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > image.shape[1] * 0.3:  # Line spans at least 30% of width
                    rows.append(y)
            
            columns = []
            for contour in vertical_contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h > image.shape[0] * 0.3:  # Line spans at least 30% of height
                    columns.append(x)
            
            return {
                "rows": sorted(rows),
                "columns": sorted(columns),
                "table_detected": len(rows) > 2 and len(columns) > 1
            }
            
        except Exception as e:
            print(f"Table detection error: {e}")
            return {"rows": [], "columns": []}
    
    def enhance_image_for_ocr(self, image_data: bytes) -> bytes:
        """Advanced image enhancement for better OCR results"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize if too small (OCR works better on larger images)
            width, height = image.size
            if width < 600 or height < 600:
                scale_factor = max(600/width, 600/height)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.8)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            # Apply unsharp mask for better text clarity
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Reduce noise
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG', optimize=True)
            return output.getvalue()
            
        except Exception as e:
            print(f"Image enhancement error: {e}")
            return image_data
    
    def crop_text_regions(self, image_data: bytes, regions: List[Tuple[int, int, int, int]]) -> List[bytes]:
        """Crop individual text regions from image"""
        try:
            image = Image.open(io.BytesIO(image_data))
            cropped_regions = []
            
            for x, y, w, h in regions:
                # Add some padding
                padding = 5
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(image.width, x + w + padding)
                y2 = min(image.height, y + h + padding)
                
                # Crop the region
                cropped = image.crop((x1, y1, x2, y2))
                
                # Convert to bytes
                output = io.BytesIO()
                cropped.save(output, format='PNG')
                cropped_regions.append(output.getvalue())
            
            return cropped_regions
            
        except Exception as e:
            print(f"Region cropping error: {e}")
            return []
    
    def detect_document_orientation(self, image_data: bytes) -> float:
        """Detect document orientation and return rotation angle"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return 0.0
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                angles = []
                for rho, theta in lines[:20]:  # Use first 20 lines
                    angle = theta * 180 / np.pi
                    # Convert to rotation angle
                    if angle > 90:
                        angle = angle - 180
                    angles.append(angle)
                
                # Return median angle
                if angles:
                    return np.median(angles)
            
            return 0.0
            
        except Exception as e:
            print(f"Orientation detection error: {e}")
            return 0.0
    
    def correct_document_orientation(self, image_data: bytes) -> bytes:
        """Automatically correct document orientation"""
        try:
            angle = self.detect_document_orientation(image_data)
            
            if abs(angle) < 1:  # No significant rotation needed
                return image_data
            
            # Rotate image
            image = Image.open(io.BytesIO(image_data))
            rotated = image.rotate(-angle, expand=True, fillcolor='white')
            
            # Convert back to bytes
            output = io.BytesIO()
            rotated.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            print(f"Orientation correction error: {e}")
            return image_data
    
    def remove_noise_and_artifacts(self, image_data: bytes) -> bytes:
        """Remove noise and artifacts from scanned documents"""
        try:
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return image_data
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise while preserving edges
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Apply morphological operations to remove small artifacts
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(filtered, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # Convert back to bytes
            _, buffer = cv2.imencode('.png', cleaned)
            return buffer.tobytes()
            
        except Exception as e:
            print(f"Noise removal error: {e}")
            return image_data
    
    def extract_invoice_layout(self, image_data: bytes) -> Dict:
        """Extract layout information from invoice"""
        try:
            # Detect text regions
            text_regions = self.detect_text_regions(image_data)
            
            # Detect table structure
            table_info = self.detect_table_structure(image_data)
            
            # Classify regions
            header_regions = []
            body_regions = []
            footer_regions = []
            
            if text_regions:
                # Sort by y-coordinate
                sorted_regions = sorted(text_regions, key=lambda r: r[1])
                
                # Get image dimensions
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                height = image.shape[0] if image is not None else 1000
                
                # Classify regions by position
                for region in sorted_regions:
                    x, y, w, h = region
                    
                    if y < height * 0.25:  # Top 25%
                        header_regions.append(region)
                    elif y > height * 0.75:  # Bottom 25%
                        footer_regions.append(region)
                    else:  # Middle 50%
                        body_regions.append(region)
            
            return {
                "header_regions": header_regions,
                "body_regions": body_regions,
                "footer_regions": footer_regions,
                "table_structure": table_info,
                "total_regions": len(text_regions)
            }
            
        except Exception as e:
            print(f"Layout extraction error: {e}")
            return {
                "header_regions": [],
                "body_regions": [],
                "footer_regions": [],
                "table_structure": {"rows": [], "columns": []},
                "total_regions": 0
            }