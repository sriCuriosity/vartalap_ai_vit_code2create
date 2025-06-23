# Dataset Sources and Training Instructions

## 1. Tamil Handwriting Recognition

### Datasets:
- **Tamil Handwriting Dataset (Kaggle)**: https://www.kaggle.com/datasets/tamil-handwriting-recognition
- **HP Labs Tamil Dataset**: http://www.hpl.hp.com/india/research/penhw-interfaces/tamil.html
- **Custom Collection**: Create your own dataset by collecting handwritten Tamil text samples

### Data Structure:
```
tamil_handwriting/
├── images/
│   ├── sample_001.jpg
│   ├── sample_002.jpg
│   └── ...
└── labels.csv (columns: filename, text)
```

### Training Command:
```bash
python models/handwriting_recognition/tamil_handwriting_model.py
```

## 2. English Handwriting Recognition

### Datasets:
- **IAM Handwriting Database**: https://fki.tic.heia-fr.ch/databases/iam-handwriting-database
- **RIMES Dataset**: http://www.a2ialab.com/doku.php?id=rimes_database:start
- **CVL Database**: https://cvl.tuwien.ac.at/research/cvl-databases/an-off-line-database-for-writer-retrieval-writer-identification-and-word-spotting/

### Data Structure:
```
english_handwriting/
├── train/
│   ├── images/
│   └── annotations.csv
├── val/
│   ├── images/
│   └── annotations.csv
```

### Training Command:
```bash
python models/handwriting_recognition/english_handwriting_model.py
```

## 3. Invoice Layout Analysis

### Datasets:
- **FUNSD Dataset**: https://guillaumejaume.github.io/FUNSD/
- **SROIE Dataset**: https://rrc.cvc.uab.es/?ch=13
- **Custom Invoice Dataset**: Create your own with business invoices

### Data Structure:
```
invoice_dataset/
├── train/
│   ├── images/
│   └── annotations.json
├── val/
│   ├── images/
│   └── annotations.json
```

### Annotation Format:
```json
[
  {
    "filename": "invoice_001.jpg",
    "entities": [
      {
        "text": "SADHASIVA AGENCIES",
        "label": "VENDOR",
        "bbox": [x1, y1, x2, y2]
      },
      {
        "text": "12345",
        "label": "INVOICE_NO",
        "bbox": [x1, y1, x2, y2]
      }
    ]
  }
]
```

### Training Command:
```bash
python models/invoice_analysis/invoice_layout_model.py
```

## 4. Tamil-English Translation

### Datasets:
- **OPUS Tamil-English Corpus**: https://opus.nlpl.eu/
- **IndicCorp**: https://indicnlp.ai4bharat.org/corpora/
- **AI4Bharat IndicTrans**: https://github.com/AI4Bharat/indictrans

### Data Structure:
```csv
tamil,english
"நாட்டு சக்கரை","country sugar"
"ராகி மாவு","ragi flour"
"வாடிக்கையாளர்","customer"
```

### Training Command:
```bash
python models/translation/tamil_english_translator.py
```

## 5. Sales Forecasting

### Data Source:
- Your own business database (bills.db)
- Historical sales data (minimum 60 days recommended)

### Training Command:
```bash
python models/business_intelligence/sales_forecasting_model.py
```

## Training Environment Setup

### Requirements:
```bash
pip install torch torchvision transformers
pip install tensorflow keras
pip install opencv-python pillow
pip install pandas numpy scikit-learn
pip install prophet matplotlib
pip install pytesseract easyocr
pip install layoutlm
```

### GPU Setup (Recommended):
```bash
# For CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install tensorflow-gpu
```

## Model Training Pipeline

### 1. Data Preparation:
```bash
# Download datasets
# Organize data according to required structure
# Create train/validation splits
```

### 2. Training:
```bash
# Train each model separately
python train_tamil_handwriting.py
python train_english_handwriting.py
python train_invoice_layout.py
python train_translation.py
python train_sales_forecasting.py
```

### 3. Evaluation:
```bash
# Evaluate models on test sets
# Generate performance metrics
# Fine-tune hyperparameters
```

### 4. Deployment:
```bash
# Convert models to deployment format
# Create API endpoints
# Deploy to cloud services
```

## Performance Expectations

### Tamil Handwriting Recognition:
- **Accuracy**: 85-95% (depends on handwriting quality)
- **Training Time**: 4-8 hours on GPU
- **Model Size**: ~50-100 MB

### English Handwriting Recognition:
- **Accuracy**: 90-98% (using pre-trained TrOCR)
- **Training Time**: 2-4 hours on GPU
- **Model Size**: ~300-500 MB

### Invoice Layout Analysis:
- **F1 Score**: 80-95% (entity extraction)
- **Training Time**: 6-12 hours on GPU
- **Model Size**: ~400-600 MB

### Translation Model:
- **BLEU Score**: 25-40 (Tamil-English)
- **Training Time**: 8-16 hours on GPU
- **Model Size**: ~200-400 MB

### Sales Forecasting:
- **MAE**: 10-20% of average sales
- **Training Time**: 30 minutes - 2 hours
- **Model Size**: ~10-50 MB

## Cloud Training Options

### Google Colab:
- Free GPU access (limited)
- Good for experimentation
- Easy setup with pre-installed libraries

### AWS SageMaker:
- Scalable training infrastructure
- Managed Jupyter notebooks
- Pay-per-use pricing

### Google Cloud AI Platform:
- Managed ML training
- Custom machine types
- Integration with other GCP services

### Azure Machine Learning:
- End-to-end ML lifecycle
- Automated ML capabilities
- Integration with Azure services

## Custom Dataset Creation

### For Handwriting Recognition:
1. Collect handwritten samples
2. Digitize using scanner/camera
3. Annotate with ground truth text
4. Ensure diverse writing styles
5. Balance dataset across characters/words

### For Invoice Analysis:
1. Collect various invoice formats
2. Annotate key fields (vendor, amount, date, etc.)
3. Use annotation tools like LabelStudio
4. Ensure diverse layouts and languages
5. Include both printed and handwritten invoices

### For Translation:
1. Collect parallel Tamil-English text
2. Focus on business terminology
3. Include domain-specific phrases
4. Ensure translation quality
5. Balance sentence lengths

## Model Optimization

### Techniques:
- **Quantization**: Reduce model size
- **Pruning**: Remove unnecessary parameters
- **Knowledge Distillation**: Create smaller student models
- **ONNX Conversion**: Cross-platform deployment
- **TensorRT**: GPU optimization

### Deployment Formats:
- **TensorFlow Lite**: Mobile deployment
- **ONNX**: Cross-framework compatibility
- **TorchScript**: PyTorch production
- **Core ML**: iOS deployment
- **TensorFlow.js**: Web deployment