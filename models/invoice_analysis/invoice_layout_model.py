"""
Invoice Layout Analysis Model using LayoutLM
Dataset: Custom invoice dataset or FUNSD dataset
"""

import torch
import torch.nn as nn
from transformers import LayoutLMv2ForTokenClassification, LayoutLMv2Processor
from transformers import AutoTokenizer
import cv2
import numpy as np
from PIL import Image, ImageDraw
import json
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import pytesseract

class InvoiceDataset(Dataset):
    def __init__(self, data_path, processor, max_length=512):
        self.data_path = data_path
        self.processor = processor
        self.max_length = max_length
        
        # Load annotations
        with open(os.path.join(data_path, 'annotations.json'), 'r') as f:
            self.annotations = json.load(f)
        
        # Label mapping for invoice fields
        self.label_map = {
            'O': 0,           # Outside
            'B-VENDOR': 1,    # Beginning of vendor name
            'I-VENDOR': 2,    # Inside vendor name
            'B-INVOICE_NO': 3, # Beginning of invoice number
            'I-INVOICE_NO': 4, # Inside invoice number
            'B-DATE': 5,      # Beginning of date
            'I-DATE': 6,      # Inside date
            'B-ITEM': 7,      # Beginning of item
            'I-ITEM': 8,      # Inside item
            'B-QTY': 9,       # Beginning of quantity
            'I-QTY': 10,      # Inside quantity
            'B-PRICE': 11,    # Beginning of price
            'I-PRICE': 12,    # Inside price
            'B-TOTAL': 13,    # Beginning of total
            'I-TOTAL': 14,    # Inside total
        }
        
    def __len__(self):
        return len(self.annotations)
    
    def __getitem__(self, idx):
        annotation = self.annotations[idx]
        
        # Load image
        image_path = os.path.join(self.data_path, 'images', annotation['filename'])
        image = Image.open(image_path).convert('RGB')
        
        # Extract text and bounding boxes using OCR
        words, boxes = self.extract_words_and_boxes(image)
        
        # Get labels for each word
        labels = self.get_word_labels(annotation, words, boxes)
        
        # Process with LayoutLM processor
        encoding = self.processor(
            image,
            words,
            boxes=boxes,
            word_labels=labels,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'bbox': encoding['bbox'].squeeze(),
            'pixel_values': encoding['pixel_values'].squeeze(),
            'labels': encoding['labels'].squeeze()
        }
    
    def extract_words_and_boxes(self, image):
        """Extract words and bounding boxes using OCR"""
        # Convert PIL to OpenCV
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Use Tesseract to get word-level data
        data = pytesseract.image_to_data(image_cv, output_type=pytesseract.Output.DICT)
        
        words = []
        boxes = []
        
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 30:  # Filter low confidence
                word = data['text'][i].strip()
                if word:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    # Normalize coordinates to 0-1000 scale (LayoutLM requirement)
                    img_width, img_height = image.size
                    x_norm = int((x / img_width) * 1000)
                    y_norm = int((y / img_height) * 1000)
                    x2_norm = int(((x + w) / img_width) * 1000)
                    y2_norm = int(((y + h) / img_height) * 1000)
                    
                    words.append(word)
                    boxes.append([x_norm, y_norm, x2_norm, y2_norm])
        
        return words, boxes
    
    def get_word_labels(self, annotation, words, boxes):
        """Get labels for each word based on annotation"""
        labels = ['O'] * len(words)  # Default to 'O' (outside)
        
        # Map annotation entities to words
        for entity in annotation.get('entities', []):
            entity_type = entity['label']
            entity_text = entity['text'].lower()
            
            # Find matching words
            for i, word in enumerate(words):
                if word.lower() in entity_text or entity_text in word.lower():
                    if labels[i] == 'O':  # Only assign if not already labeled
                        labels[i] = f'B-{entity_type}'
                    else:
                        labels[i] = f'I-{entity_type}'
        
        # Convert to numeric labels
        numeric_labels = [self.label_map.get(label, 0) for label in labels]
        
        return numeric_labels

class InvoiceLayoutAnalyzer:
    def __init__(self, model_name="microsoft/layoutlmv2-base-uncased"):
        self.processor = LayoutLMv2Processor.from_pretrained(model_name)
        self.model = LayoutLMv2ForTokenClassification.from_pretrained(
            model_name, 
            num_labels=15  # Number of entity types
        )
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Label mapping
        self.id_to_label = {
            0: 'O', 1: 'B-VENDOR', 2: 'I-VENDOR', 3: 'B-INVOICE_NO', 4: 'I-INVOICE_NO',
            5: 'B-DATE', 6: 'I-DATE', 7: 'B-ITEM', 8: 'I-ITEM', 9: 'B-QTY', 10: 'I-QTY',
            11: 'B-PRICE', 12: 'I-PRICE', 13: 'B-TOTAL', 14: 'I-TOTAL'
        }
    
    def train(self, train_dataset, val_dataset, epochs=10, batch_size=4, learning_rate=5e-5):
        """Train the model"""
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        self.model.train()
        
        for epoch in range(epochs):
            total_loss = 0
            
            for batch in train_loader:
                # Move to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                bbox = batch['bbox'].to(self.device)
                pixel_values = batch['pixel_values'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    bbox=bbox,
                    pixel_values=pixel_values,
                    labels=labels
                )
                
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
        self.model.save_pretrained('invoice_layout_model')
        self.processor.save_pretrained('invoice_layout_processor')
    
    def validate(self, val_loader):
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                bbox = batch['bbox'].to(self.device)
                pixel_values = batch['pixel_values'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    bbox=bbox,
                    pixel_values=pixel_values,
                    labels=labels
                )
                
                total_loss += outputs.loss.item()
        
        self.model.train()
        return total_loss / len(val_loader)
    
    def analyze_invoice(self, image_path):
        """Analyze invoice and extract structured data"""
        image = Image.open(image_path).convert('RGB')
        
        # Extract words and boxes
        words, boxes = self.extract_words_and_boxes(image)
        
        # Process with model
        encoding = self.processor(
            image,
            words,
            boxes=boxes,
            return_tensors="pt"
        )
        
        # Move to device
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        bbox = encoding['bbox'].to(self.device)
        pixel_values = encoding['pixel_values'].to(self.device)
        
        # Predict
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                bbox=bbox,
                pixel_values=pixel_values
            )
        
        # Get predictions
        predictions = torch.argmax(outputs.logits, dim=-1)
        
        # Extract entities
        entities = self.extract_entities(words, predictions[0])
        
        return entities
    
    def extract_words_and_boxes(self, image):
        """Extract words and bounding boxes using OCR"""
        # Convert PIL to OpenCV
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Use Tesseract
        data = pytesseract.image_to_data(image_cv, output_type=pytesseract.Output.DICT)
        
        words = []
        boxes = []
        
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 30:
                word = data['text'][i].strip()
                if word:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    # Normalize coordinates
                    img_width, img_height = image.size
                    x_norm = int((x / img_width) * 1000)
                    y_norm = int((y / img_height) * 1000)
                    x2_norm = int(((x + w) / img_width) * 1000)
                    y2_norm = int(((y + h) / img_height) * 1000)
                    
                    words.append(word)
                    boxes.append([x_norm, y_norm, x2_norm, y2_norm])
        
        return words, boxes
    
    def extract_entities(self, words, predictions):
        """Extract entities from predictions"""
        entities = {}
        current_entity = None
        current_text = []
        
        for word, pred_id in zip(words, predictions):
            pred_label = self.id_to_label.get(pred_id.item(), 'O')
            
            if pred_label.startswith('B-'):
                # Save previous entity
                if current_entity and current_text:
                    entities[current_entity] = ' '.join(current_text)
                
                # Start new entity
                current_entity = pred_label[2:]  # Remove 'B-' prefix
                current_text = [word]
                
            elif pred_label.startswith('I-') and current_entity:
                # Continue current entity
                current_text.append(word)
                
            else:
                # Save current entity and reset
                if current_entity and current_text:
                    entities[current_entity] = ' '.join(current_text)
                current_entity = None
                current_text = []
        
        # Save last entity
        if current_entity and current_text:
            entities[current_entity] = ' '.join(current_text)
        
        return entities

# Training script
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = InvoiceLayoutAnalyzer()
    
    # Prepare datasets
    # Create custom invoice dataset or use FUNSD dataset
    # https://guillaumejaume.github.io/FUNSD/
    
    data_path = "path/to/invoice_dataset"
    # train_dataset = InvoiceDataset(
    #     os.path.join(data_path, 'train'), 
    #     analyzer.processor
    # )
    # val_dataset = InvoiceDataset(
    #     os.path.join(data_path, 'val'), 
    #     analyzer.processor
    # )
    
    # Train model
    # analyzer.train(train_dataset, val_dataset, epochs=15)
    
    print("Invoice Layout Analysis Model Ready!")