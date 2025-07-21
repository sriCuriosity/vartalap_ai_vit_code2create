import cv2
import numpy as np
import tensorflow as tf
import json
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import time

class TamilHandwritingRecognizer:
    def __init__(self, model_path, char_mapping_path, deployment_info_path):
        """
        Initialize the Tamil Handwriting Recognition model
        
        Args:
            model_path: Path to the trained model (.h5 file)
            char_mapping_path: Path to character mapping JSON file
            deployment_info_path: Path to deployment info JSON file
        """
        self.model_path = model_path
        self.char_mapping_path = char_mapping_path
        self.deployment_info_path = deployment_info_path
        
        # Load model and configuration
        self.load_model()
        self.load_configuration()
        
    def load_model(self):
        """Load the trained model"""
        try:
            print("Loading Tamil handwriting recognition model...")
            self.model = tf.keras.models.load_model(self.model_path)
            print(f"Model loaded successfully from {self.model_path}")
            print(f"Model input shape: {self.model.input_shape}")
            print(f"Model output shape: {self.model.output_shape}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def load_configuration(self):
        """Load character mapping and deployment configuration"""
        try:
            # Load character mapping
            with open(self.char_mapping_path, 'r', encoding='utf-8') as f:
                char_mapping = json.load(f)
                self.idx_to_char = {int(k): v for k, v in char_mapping['idx_to_char'].items()}
                self.char_to_idx = char_mapping['char_to_idx']
            
            # Load deployment info
            with open(self.deployment_info_path, 'r', encoding='utf-8') as f:
                self.deployment_info = json.load(f)
            
            self.input_shape = tuple(self.deployment_info['model_info']['input_shape'])
            self.num_classes = self.deployment_info['model_info']['num_classes']
            
            print(f"Configuration loaded:")
            print(f"  - Input shape: {self.input_shape}")
            print(f"  - Number of classes: {self.num_classes}")
            print(f"  - Model accuracy: {self.deployment_info['model_info']['accuracy']:.4f}")
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise
    
    def preprocess_image(self, image):
        """
        Preprocess image for model input
        
        Args:
            image: Input image (numpy array or PIL Image)
            
        Returns:
            Preprocessed image ready for model input
        """
        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to grayscale if RGB
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Resize to model input size
        image = cv2.resize(image, (self.input_shape[0], self.input_shape[1]))
        
        # Normalize (divide by 255)
        image = image.astype(np.float32) / 255.0
        
        # Add batch and channel dimensions
        image = np.expand_dims(image, axis=(0, -1))
        
        return image
    
    def predict(self, image):
        """
        Predict Tamil character from image
        
        Args:
            image: Input image
            
        Returns:
            tuple: (predicted_character, confidence_score, all_predictions)
        """
        # Preprocess image
        processed_image = self.preprocess_image(image)
        
        # Get model predictions
        predictions = self.model.predict(processed_image, verbose=0)
        
        # Get predicted class index
        pred_idx = np.argmax(predictions[0])
        
        # Get predicted character
        pred_char = self.idx_to_char.get(pred_idx, '?')
        
        # Get confidence score
        confidence = float(predictions[0][pred_idx])
        
        return pred_char, confidence, predictions[0]
    
    def test_with_sample_images(self):
        """Test the model with sample Tamil characters"""
        print("\n=== Testing with Sample Tamil Characters ===")
        
        # Create sample Tamil characters for testing
        sample_chars = ['அ', 'க', 'ம', 'த', 'ப', 'வ', 'ர', 'ல', 'ன', 'ச']
        
        for char in sample_chars:
            # Create a simple image with the character
            img = self.create_character_image(char)
            
            # Predict
            pred_char, confidence, all_preds = self.predict(img)
            
            print(f"Input: {char} | Predicted: {pred_char} | Confidence: {confidence:.4f}")
            
            # Show top 3 predictions
            top_indices = np.argsort(all_preds)[-3:][::-1]
            print(f"  Top 3 predictions:")
            for i, idx in enumerate(top_indices):
                char_pred = self.idx_to_char.get(idx, '?')
                conf = all_preds[idx]
                print(f"    {i+1}. {char_pred} ({conf:.4f})")
            print()
    
    def create_character_image(self, char, size=(200, 200)):
        """Create a simple image with Tamil character for testing"""
        # Create a white background
        img = Image.new('L', size, 255)
        draw = ImageDraw.Draw(img)
        
        # Try to use a Tamil font if available, otherwise use default
        try:
            # You might need to adjust the font path based on your system
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position to center it
        bbox = draw.textbbox((0, 0), char, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Draw the character in black
        draw.text((x, y), char, fill=0, font=font)
        
        return np.array(img)
    
    def test_with_camera(self):
        """Test the model with real-time camera input"""
        print("\n=== Testing with Camera ===")
        print("Press 'q' to quit, 's' to save current frame")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_count = 0
        last_prediction = ""
        last_confidence = 0.0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Create a copy for display
            display_frame = frame.copy()
            
            # Draw ROI rectangle (center region)
            height, width = frame.shape[:2]
            roi_size = min(width, height) // 3
            x1 = (width - roi_size) // 2
            y1 = (height - roi_size) // 2
            x2 = x1 + roi_size
            y2 = y1 + roi_size
            
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Extract ROI
            roi = frame[y1:y2, x1:x2]
            
            # Predict every 10 frames to avoid lag
            if frame_count % 10 == 0:
                try:
                    pred_char, confidence, _ = self.predict(roi)
                    last_prediction = pred_char
                    last_confidence = confidence
                except Exception as e:
                    print(f"Prediction error: {e}")
            
            # Display prediction
            text = f"Prediction: {last_prediction}"
            confidence_text = f"Confidence: {last_confidence:.3f}"
            
            cv2.putText(display_frame, text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_frame, confidence_text, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(display_frame, "Write Tamil character in green box", (10, height - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, "Press 'q' to quit, 's' to save", (10, height - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Tamil Handwriting Recognition', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = int(time.time())
                filename = f"tamil_test_frame_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Saved frame as {filename}")
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
    
    def test_model_performance(self):
        """Test model performance with various inputs"""
        print("\n=== Model Performance Test ===")
        
        # Test with different image sizes
        test_sizes = [(32, 32), (64, 64), (128, 128), (256, 256)]
        
        for size in test_sizes:
            start_time = time.time()
            img = self.create_character_image('க', size)
            pred_char, confidence, _ = self.predict(img)
            end_time = time.time()
            
            print(f"Input size {size}: {pred_char} (confidence: {confidence:.4f}, time: {(end_time-start_time)*1000:.2f}ms)")
        
        # Test batch prediction
        print("\nTesting batch prediction...")
        batch_images = []
        for char in ['அ', 'க', 'ம', 'த', 'ப']:
            img = self.create_character_image(char)
            batch_images.append(img)
        
        start_time = time.time()
        for i, img in enumerate(batch_images):
            pred_char, confidence, _ = self.predict(img)
            print(f"Batch {i+1}: {pred_char} (confidence: {confidence:.4f})")
        end_time = time.time()
        
        print(f"Batch processing time: {(end_time-start_time)*1000:.2f}ms")

def main():
    """Main function to run the Tamil handwriting recognition tests"""
    
    # Model paths
    model_path = "models/handwriting_recognition/Tamil_Recognition/tamil_handwriting_best.h5"
    char_mapping_path = "models/handwriting_recognition/Tamil_Recognition/tamil_handwriting_model_char_mapping.json"
    deployment_info_path = "models/handwriting_recognition/Tamil_Recognition/tamil_handwriting_model_deployment_info.json"
    
    # Check if files exist
    for path in [model_path, char_mapping_path, deployment_info_path]:
        if not os.path.exists(path):
            print(f"Error: File not found - {path}")
            return
    
    try:
        # Initialize recognizer
        recognizer = TamilHandwritingRecognizer(model_path, char_mapping_path, deployment_info_path)
        
        # Run tests
        print("Starting Tamil Handwriting Recognition Model Tests...")
        print("=" * 60)
        
        # Test 1: Sample character recognition
        recognizer.test_with_sample_images()
        
        # Test 2: Model performance
        recognizer.test_model_performance()
        
        # Test 3: Camera testing (optional)
        print("\nDo you want to test with camera? (y/n): ", end="")
        response = input().lower().strip()
        
        if response == 'y':
            recognizer.test_with_camera()
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 