"""
English Handwriting Recognition Model using TrOCR-style architecture
Dataset: IAM Handwriting Database or RIMES dataset
"""

import torch
import torch.nn as nn
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from transformers import AutoTokenizer, AutoFeatureExtractor
import cv2
import numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import os

class EnglishHandwritingDataset(Dataset):
    def __init__(self, data_path, processor, max_target_length=128):
        self.data_path = data_path
        self.processor = processor
        self.max_target_length = max_target_length
        
        # Load annotations
        self.annotations = pd.read_csv(os.path.join(data_path, 'annotations.csv'))
        
    def __len__(self):
        return len(self.annotations)
    
    def __getitem__(self, idx):
        row = self.annotations.iloc[idx]
        
        # Load image
        image_path = os.path.join(self.data_path, 'images', row['filename'])
        image = Image.open(image_path).convert('RGB')
        
        # Process image and text
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        
        # Tokenize text
        labels = self.processor.tokenizer(
            row['text'],
            padding="max_length",
            max_length=self.max_target_length,
            truncation=True,
            return_tensors="pt"
        ).input_ids
        
        return {
            'pixel_values': pixel_values.squeeze(),
            'labels': labels.squeeze()
        }

class EnglishHandwritingRecognizer:
    def __init__(self, model_name="microsoft/trocr-base-handwritten"):
        self.processor = TrOCRProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        image = Image.open(image_path).convert('RGB')
        
        # Enhance image quality
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoisingColored(image_cv, None, 10, 10, 7, 21)
        
        # Enhance contrast
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Convert back to PIL
        enhanced_pil = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
        
        return enhanced_pil
    
    def train(self, train_dataset, val_dataset, epochs=10, batch_size=8, learning_rate=5e-5):
        """Fine-tune the model"""
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        self.model.train()
        
        for epoch in range(epochs):
            total_loss = 0
            
            for batch in train_loader:
                pixel_values = batch['pixel_values'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(pixel_values=pixel_values, labels=labels)
                loss = outputs.loss
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(train_loader)
            
            # Validation
            val_loss = self.validate(val_loader)
            
            print(f"Epoch {epoch+1}/{epochs}, Train Loss: {avg_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        # Save model
        self.model.save_pretrained('english_handwriting_model')
        self.processor.save_pretrained('english_handwriting_processor')
    
    def validate(self, val_loader):
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                pixel_values = batch['pixel_values'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(pixel_values=pixel_values, labels=labels)
                total_loss += outputs.loss.item()
        
        self.model.train()
        return total_loss / len(val_loader)
    
    def predict(self, image_path):
        """Predict text from image"""
        image = self.preprocess_image(image_path)
        
        # Process image
        pixel_values = self.processor(image, return_tensors="pt").pixel_values.to(self.device)
        
        # Generate text
        self.model.eval()
        with torch.no_grad():
            generated_ids = self.model.generate(pixel_values, max_length=128)
        
        # Decode text
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # Calculate confidence (simplified)
        confidence = 0.85  # In practice, use beam search scores
        
        return generated_text, confidence

# Training script
if __name__ == "__main__":
    # Initialize recognizer
    recognizer = EnglishHandwritingRecognizer()
    
    # Prepare datasets
    # Download IAM Handwriting Database from:
    # https://fki.tic.heia-fr.ch/databases/iam-handwriting-database
    # Or RIMES dataset from:
    # http://www.a2ialab.com/doku.php?id=rimes_database:start
    
    data_path = "path/to/iam_dataset"
    # train_dataset = EnglishHandwritingDataset(
    #     os.path.join(data_path, 'train'), 
    #     recognizer.processor
    # )
    # val_dataset = EnglishHandwritingDataset(
    #     os.path.join(data_path, 'val'), 
    #     recognizer.processor
    # )
    
    # Train model
    # recognizer.train(train_dataset, val_dataset, epochs=20)
    
    print("English Handwriting Recognition Model Ready!")