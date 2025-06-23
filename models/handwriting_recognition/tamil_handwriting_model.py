"""
Tamil Handwriting Recognition Model using CNN + LSTM
Dataset: Tamil Handwriting Dataset from Kaggle or custom collection
"""

import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical

class TamilHandwritingRecognizer:
    def __init__(self, img_height=64, img_width=256, max_length=32):
        self.img_height = img_height
        self.img_width = img_width
        self.max_length = max_length
        
        # Tamil character set (simplified - expand as needed)
        self.tamil_chars = [
            'அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ',
            'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம', 'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ற', 'ன',
            'ா', 'ி', 'ீ', 'ு', 'ூ', 'ெ', 'ே', 'ை', 'ொ', 'ோ', 'ௌ', '்',
            ' ', '<PAD>', '<START>', '<END>'
        ]
        
        self.char_to_idx = {char: idx for idx, char in enumerate(self.tamil_chars)}
        self.idx_to_char = {idx: char for idx, char in enumerate(self.tamil_chars)}
        self.vocab_size = len(self.tamil_chars)
        
        self.model = None
        
    def build_model(self):
        """Build CNN + LSTM model for handwriting recognition"""
        
        # Input layer
        input_img = layers.Input(shape=(self.img_height, self.img_width, 1), name='image_input')
        
        # CNN Feature Extraction
        x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.BatchNormalization()(x)
        
        x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.BatchNormalization()(x)
        
        x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.BatchNormalization()(x)
        
        x = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.BatchNormalization()(x)
        
        # Reshape for RNN
        new_shape = ((self.img_width // 16), (self.img_height // 16) * 256)
        x = layers.Reshape(target_shape=new_shape)(x)
        x = layers.Dense(64, activation='relu')(x)
        
        # RNN layers
        x = layers.Bidirectional(layers.LSTM(128, return_sequences=True, dropout=0.25))(x)
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, dropout=0.25))(x)
        
        # Output layer
        output = layers.Dense(self.vocab_size, activation='softmax', name='output')(x)
        
        # Create model
        self.model = models.Model(inputs=input_img, outputs=output)
        
        # Compile model
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return self.model
    
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # Resize image
        img = cv2.resize(img, (self.img_width, self.img_height))
        
        # Normalize
        img = img.astype(np.float32) / 255.0
        
        # Add channel dimension
        img = np.expand_dims(img, axis=-1)
        
        return img
    
    def encode_text(self, text):
        """Encode text to sequence of indices"""
        encoded = [self.char_to_idx.get(char, self.char_to_idx['<PAD>']) for char in text]
        encoded = pad_sequences([encoded], maxlen=self.max_length, padding='post')[0]
        return to_categorical(encoded, num_classes=self.vocab_size)
    
    def decode_prediction(self, prediction):
        """Decode model prediction to text"""
        predicted_indices = np.argmax(prediction, axis=-1)
        decoded_text = ''.join([self.idx_to_char[idx] for idx in predicted_indices])
        
        # Remove padding and special tokens
        decoded_text = decoded_text.replace('<PAD>', '').replace('<START>', '').replace('<END>', '')
        
        return decoded_text.strip()
    
    def train(self, train_images, train_labels, validation_split=0.2, epochs=50, batch_size=32):
        """Train the model"""
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            train_images, train_labels, test_size=validation_split, random_state=42
        )
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
            tf.keras.callbacks.ModelCheckpoint('tamil_handwriting_best.h5', save_best_only=True)
        ]
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def predict(self, image):
        """Predict text from image"""
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        prediction = self.model.predict(image)
        decoded_text = self.decode_prediction(prediction[0])
        
        # Calculate confidence
        confidence = np.mean(np.max(prediction[0], axis=-1))
        
        return decoded_text, confidence

# Data preparation functions
def prepare_tamil_dataset(data_path):
    """
    Prepare Tamil handwriting dataset
    Expected structure:
    data_path/
    ├── images/
    │   ├── image1.jpg
    │   ├── image2.jpg
    │   └── ...
    └── labels.csv (columns: filename, text)
    """
    
    import os
    import pandas as pd
    
    # Load labels
    labels_df = pd.read_csv(os.path.join(data_path, 'labels.csv'))
    
    images = []
    labels = []
    
    recognizer = TamilHandwritingRecognizer()
    
    for _, row in labels_df.iterrows():
        image_path = os.path.join(data_path, 'images', row['filename'])
        
        if os.path.exists(image_path):
            # Preprocess image
            img = recognizer.preprocess_image(image_path)
            images.append(img)
            
            # Encode label
            encoded_label = recognizer.encode_text(row['text'])
            labels.append(encoded_label)
    
    return np.array(images), np.array(labels)

# Training script
if __name__ == "__main__":
    # Initialize model
    recognizer = TamilHandwritingRecognizer()
    model = recognizer.build_model()
    
    print("Model Summary:")
    model.summary()
    
    # Load and prepare data
    # Download Tamil handwriting dataset from:
    # https://www.kaggle.com/datasets/tamil-handwriting-recognition
    # Or create custom dataset
    
    data_path = "path/to/tamil_handwriting_dataset"
    # X_train, y_train = prepare_tamil_dataset(data_path)
    
    # Train model
    # history = recognizer.train(X_train, y_train, epochs=100)
    
    # Save model
    # model.save('tamil_handwriting_model.h5')
    
    print("Tamil Handwriting Recognition Model Ready!")