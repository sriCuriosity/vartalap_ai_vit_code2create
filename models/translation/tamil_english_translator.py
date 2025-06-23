"""
Tamil-English Translation Model using mT5
Dataset: Tamil-English parallel corpus from OPUS or custom dataset
"""

import torch
from transformers import MT5ForConditionalGeneration, MT5Tokenizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

class TranslationDataset(Dataset):
    def __init__(self, source_texts, target_texts, tokenizer, max_length=128):
        self.source_texts = source_texts
        self.target_texts = target_texts
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.source_texts)
    
    def __getitem__(self, idx):
        source_text = str(self.source_texts[idx])
        target_text = str(self.target_texts[idx])
        
        # Tokenize source
        source_encoding = self.tokenizer(
            source_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Tokenize target
        target_encoding = self.tokenizer(
            target_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': source_encoding['input_ids'].squeeze(),
            'attention_mask': source_encoding['attention_mask'].squeeze(),
            'labels': target_encoding['input_ids'].squeeze()
        }

class TamilEnglishTranslator:
    def __init__(self, model_name="google/mt5-small"):
        self.tokenizer = MT5Tokenizer.from_pretrained(model_name)
        self.model = MT5ForConditionalGeneration.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Add special tokens for translation direction
        special_tokens = ["<ta2en>", "<en2ta>"]
        self.tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})
        self.model.resize_token_embeddings(len(self.tokenizer))
    
    def prepare_data(self, data_path):
        """Prepare translation dataset"""
        # Load parallel corpus
        df = pd.read_csv(data_path)
        
        # Prepare Tamil to English
        ta_to_en_source = ["<ta2en> " + text for text in df['tamil']]
        ta_to_en_target = df['english'].tolist()
        
        # Prepare English to Tamil
        en_to_ta_source = ["<en2ta> " + text for text in df['english']]
        en_to_ta_target = df['tamil'].tolist()
        
        # Combine both directions
        all_source = ta_to_en_source + en_to_ta_source
        all_target = ta_to_en_target + en_to_ta_target
        
        return all_source, all_target
    
    def train(self, source_texts, target_texts, epochs=10, batch_size=8, learning_rate=5e-5):
        """Train the translation model"""
        
        # Split data
        train_source, val_source, train_target, val_target = train_test_split(
            source_texts, target_texts, test_size=0.1, random_state=42
        )
        
        # Create datasets
        train_dataset = TranslationDataset(train_source, train_target, self.tokenizer)
        val_dataset = TranslationDataset(val_source, val_target, self.tokenizer)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Optimizer
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        self.model.train()
        
        for epoch in range(epochs):
            total_loss = 0
            
            for batch in train_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
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
        self.model.save_pretrained('tamil_english_translator')
        self.tokenizer.save_pretrained('tamil_english_tokenizer')
    
    def validate(self, val_loader):
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                total_loss += outputs.loss.item()
        
        self.model.train()
        return total_loss / len(val_loader)
    
    def translate(self, text, source_lang='auto', target_lang='en'):
        """Translate text"""
        # Detect direction and add prefix
        if source_lang == 'ta' or (source_lang == 'auto' and self.is_tamil(text)):
            input_text = f"<ta2en> {text}"
        else:
            input_text = f"<en2ta> {text}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors='pt',
            max_length=128,
            truncation=True,
            padding=True
        ).to(self.device)
        
        # Generate translation
        self.model.eval()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=128,
                num_beams=4,
                early_stopping=True,
                do_sample=False
            )
        
        # Decode
        translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return translation
    
    def is_tamil(self, text):
        """Check if text contains Tamil characters"""
        tamil_range = range(0x0B80, 0x0BFF)  # Tamil Unicode range
        return any(ord(char) in tamil_range for char in text)

# Business-specific translation model
class BusinessTermTranslator(TamilEnglishTranslator):
    def __init__(self):
        super().__init__()
        
        # Business-specific dictionary
        self.business_dict = {
            # Grains and cereals
            "நாட்டு சக்கரை": "country sugar",
            "ராகி": "ragi",
            "ராகி மாவு": "ragi flour",
            "கம்பு": "pearl millet",
            "கம்பு மாவு": "pearl millet flour",
            "சத்து மாவு": "nutritious flour",
            "மட்ட சம்பா அரிசி": "matta samba rice",
            "சிவப்பு கவுணி அரிசி": "red parboiled rice",
            "சிவப்பு சோளம்": "red corn",
            "வெள்ளை சோளம்": "white corn",
            "கொள்ளு": "horse gram",
            "உளுந்து": "black gram",
            "கடலை": "chickpea",
            "பச்சைப் பயறு": "green gram",
            
            # Business terms
            "வாடிக்கையாளர்": "customer",
            "விற்பனை": "sales",
            "கணக்கு": "account",
            "பில்": "bill",
            "தொகை": "amount",
            "கிலோ": "kilogram",
            "விலை": "price",
            "மொத்தம்": "total",
            
            # Reverse mappings
            "country sugar": "நாட்டு சக்கரை",
            "ragi": "ராகி",
            "pearl millet": "கம்பு",
            "horse gram": "கொள்ளு",
            "customer": "வாடிக்கையாளர்",
            "sales": "விற்பனை",
            "bill": "பில்",
            "total": "மொத்தம்"
        }
    
    def translate_with_dictionary(self, text, source_lang='auto', target_lang='en'):
        """Translate using dictionary first, then model"""
        
        # Check dictionary first
        text_lower = text.lower().strip()
        if text_lower in self.business_dict:
            return self.business_dict[text_lower]
        
        # Try word-by-word dictionary lookup
        words = text.split()
        translated_words = []
        
        for word in words:
            word_lower = word.lower().strip()
            if word_lower in self.business_dict:
                translated_words.append(self.business_dict[word_lower])
            else:
                translated_words.append(word)
        
        # If any words were translated, return the result
        if len(translated_words) != len(words) or any(w != orig for w, orig in zip(translated_words, words)):
            return " ".join(translated_words)
        
        # Fallback to model translation
        return self.translate(text, source_lang, target_lang)

# Data preparation for training
def prepare_tamil_english_corpus():
    """
    Prepare Tamil-English parallel corpus for training
    
    Suggested datasets:
    1. OPUS Tamil-English corpus: https://opus.nlpl.eu/
    2. IndicCorp: https://indicnlp.ai4bharat.org/corpora/
    3. Custom business terminology dataset
    """
    
    # Example data structure
    data = {
        'tamil': [
            'நாட்டு சக்கரை ஐந்து கிலோ',
            'ராகி மாவு இரண்டு கிலோ',
            'வாடிக்கையாளர் ஏ',
            'மொத்த தொகை ஆயிரம் ரூபாய்'
        ],
        'english': [
            'country sugar five kilograms',
            'ragi flour two kilograms', 
            'customer A',
            'total amount one thousand rupees'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_csv('tamil_english_corpus.csv', index=False)
    
    return df

# Training script
if __name__ == "__main__":
    # Prepare data
    # corpus_df = prepare_tamil_english_corpus()
    
    # Initialize translator
    translator = BusinessTermTranslator()
    
    # Load and prepare training data
    # source_texts, target_texts = translator.prepare_data('tamil_english_corpus.csv')
    
    # Train model
    # translator.train(source_texts, target_texts, epochs=20)
    
    # Test translation
    test_text = "நாட்டு சக்கரை"
    translation = translator.translate_with_dictionary(test_text)
    print(f"Translation: {test_text} -> {translation}")
    
    print("Tamil-English Translation Model Ready!")