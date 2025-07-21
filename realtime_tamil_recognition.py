import cv2
import numpy as np
import tensorflow as tf
import json
import os
import time

class RealtimeTamilRecognizer:
    def __init__(self):
        """Initialize the real-time Tamil character recognizer"""
        self.model_path = "models/handwriting_recognition/Tamil_Recognition/tamil_handwriting_best.h5"
        self.char_mapping_path = "models/handwriting_recognition/Tamil_Recognition/tamil_handwriting_model_char_mapping.json"
        
        # Load model and configuration
        self.load_model()
        self.load_char_mapping()
        
        # Initialize camera
        self.cap = None
        self.is_running = False
        
    def load_model(self):
        """Load the trained Tamil handwriting model"""
        try:
            print("Loading Tamil handwriting model...")
            self.model = tf.keras.models.load_model(self.model_path)
            print(f"✓ Model loaded successfully")
            print(f"  Input shape: {self.model.input_shape}")
            print(f"  Output shape: {self.model.output_shape}")
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            raise
    
    def load_char_mapping(self):
        """Load character mapping from JSON file"""
        try:
            with open(self.char_mapping_path, 'r', encoding='utf-8') as f:
                char_mapping = json.load(f)
                self.idx_to_char = {int(k): v for k, v in char_mapping['idx_to_char'].items()}
            print(f"✓ Character mapping loaded ({len(self.idx_to_char)} characters)")
        except Exception as e:
            print(f"✗ Error loading character mapping: {e}")
            raise
    
    def preprocess_frame(self, frame):
        """Preprocess camera frame for model input"""
        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # Resize to 64x64 (model input size)
        resized = cv2.resize(gray, (64, 64))
        
        # Normalize (0-1)
        normalized = resized.astype(np.float32) / 255.0
        
        # Add batch and channel dimensions
        input_tensor = np.expand_dims(normalized, axis=(0, -1))
        
        return input_tensor
    
    def predict_character(self, frame):
        """Predict Tamil character from frame"""
        try:
            # Preprocess frame
            processed = self.preprocess_frame(frame)
            
            # Get prediction
            predictions = self.model.predict(processed, verbose=0)
            
            # Get predicted class
            pred_idx = np.argmax(predictions[0])
            pred_char = self.idx_to_char.get(pred_idx, '?')
            confidence = float(predictions[0][pred_idx])
            
            return pred_char, confidence, predictions[0]
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return '?', 0.0, None
    
    def start_camera(self):
        """Start real-time camera recognition"""
        print("\n=== Real-time Tamil Character Recognition ===")
        print("Controls:")
        print("  - Write Tamil characters in the green box")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save current frame")
        print("  - Press 'r' to reset prediction")
        print("  - Press 'h' to show/hide help")
        print("=" * 50)
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("✗ Error: Could not open camera")
            return
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Initialize variables
        self.is_running = True
        frame_count = 0
        last_prediction = ""
        last_confidence = 0.0
        show_help = True
        prediction_history = []
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                print("✗ Error: Could not read frame")
                break
            
            # Create display frame
            display = frame.copy()
            height, width = frame.shape[:2]
            
            # Define ROI (Region of Interest) - center square
            roi_size = min(width, height) // 3
            x1 = (width - roi_size) // 2
            y1 = (height - roi_size) // 2
            x2 = x1 + roi_size
            y2 = y1 + roi_size
            
            # Draw ROI rectangle
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Extract ROI for prediction
            roi = frame[y1:y2, x1:x2]
            
            # Predict every 5 frames to balance accuracy and performance
            if frame_count % 5 == 0:
                pred_char, confidence, all_preds = self.predict_character(roi)
                
                # Only update if confidence is above threshold
                if confidence > 0.3:
                    last_prediction = pred_char
                    last_confidence = confidence
                    
                    # Add to history
                    prediction_history.append({
                        'char': pred_char,
                        'confidence': confidence,
                        'timestamp': time.time()
                    })
                    
                    # Keep only last 10 predictions
                    if len(prediction_history) > 10:
                        prediction_history.pop(0)
            
            # Display current prediction
            if last_prediction:
                # Main prediction display
                cv2.putText(display, f"Character: {last_prediction}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(display, f"Confidence: {last_confidence:.3f}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show top 3 alternative predictions if available
                if all_preds is not None:
                    top_indices = np.argsort(all_preds)[-4:-1][::-1]  # Top 3 (excluding the best)
                    alt_text = "Alternatives: "
                    for i, idx in enumerate(top_indices):
                        if i < 2:  # Show only top 2 alternatives
                            char = self.idx_to_char.get(idx, '?')
                            conf = all_preds[idx]
                            alt_text += f"{char}({conf:.2f}) "
                    
                    cv2.putText(display, alt_text, (10, 100), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Display prediction history
            if prediction_history:
                history_text = "Recent: "
                for item in prediction_history[-3:]:  # Show last 3
                    history_text += f"{item['char']} "
                cv2.putText(display, history_text, (10, height - 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Display help text
            if show_help:
                help_lines = [
                    "Controls:",
                    "q - Quit",
                    "s - Save frame", 
                    "r - Reset prediction",
                    "h - Hide/show help"
                ]
                
                for i, line in enumerate(help_lines):
                    y_pos = height - 120 + (i * 20)
                    cv2.putText(display, line, (width - 150, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            
            # Display frame
            cv2.imshow('Tamil Character Recognition', display)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = int(time.time())
                filename = f"tamil_recognition_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"✓ Saved frame as {filename}")
            elif key == ord('r'):
                # Reset prediction
                last_prediction = ""
                last_confidence = 0.0
                prediction_history.clear()
                print("✓ Prediction reset")
            elif key == ord('h'):
                # Toggle help display
                show_help = not show_help
                print(f"✓ Help {'hidden' if not show_help else 'shown'}")
            
            frame_count += 1
        
        # Cleanup
        self.stop_camera()
    
    def stop_camera(self):
        """Stop camera and cleanup resources"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✓ Camera stopped")
    
    def test_with_sample_image(self):
        """Test the model with a sample image"""
        print("\n=== Testing with Sample Image ===")
        
        # Create a simple test image with Tamil character 'க'
        test_image = np.ones((200, 200), dtype=np.uint8) * 255  # White background
        
        # Draw a simple 'க' character (simplified)
        cv2.putText(test_image, 'க', (80, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, 0, 3)
        
        # Predict
        pred_char, confidence, all_preds = self.predict_character(test_image)
        
        print(f"Test image prediction:")
        print(f"  Predicted: {pred_char}")
        print(f"  Confidence: {confidence:.4f}")
        
        # Show top 5 predictions
        if all_preds is not None:
            top_indices = np.argsort(all_preds)[-5:][::-1]
            print("  Top 5 predictions:")
            for i, idx in enumerate(top_indices):
                char = self.idx_to_char.get(idx, '?')
                conf = all_preds[idx]
                print(f"    {i+1}. {char} ({conf:.4f})")

def main():
    """Main function"""
    print("Tamil Handwriting Recognition - Real-time Testing")
    print("=" * 50)
    
    try:
        # Initialize recognizer
        recognizer = RealtimeTamilRecognizer()
        
        # Test with sample image first
        recognizer.test_with_sample_image()
        
        # Start real-time recognition
        print("\nStarting real-time recognition...")
        recognizer.start_camera()
        
    except KeyboardInterrupt:
        print("\n✓ Interrupted by user")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("✓ Application closed")

if __name__ == "__main__":
    main() 