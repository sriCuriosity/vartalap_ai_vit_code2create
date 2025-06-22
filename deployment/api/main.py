"""
FastAPI application for AI services
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
import io
from PIL import Image

# Import AI models
from ai_models.handwriting_model import HandwritingRecognitionModel
from ai_models.invoice_analyzer import InvoiceAnalyzer

app = FastAPI(title="Business Management AI Services", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
handwriting_model = HandwritingRecognitionModel()
invoice_analyzer = InvoiceAnalyzer()

@app.get("/")
async def root():
    return {"message": "Business Management AI Services API"}

@app.post("/api/v1/handwriting/recognize")
async def recognize_handwriting(file: UploadFile = File(...), language: str = "auto"):
    """
    Recognize handwriting from uploaded image
    """
    try:
        # Read image file
        image_data = await file.read()
        
        # Convert to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Process with handwriting model
        result = handwriting_model.recognize(image_b64, language)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/invoice/analyze")
async def analyze_invoice(file: UploadFile = File(...)):
    """
    Analyze invoice image and extract structured data
    """
    try:
        # Read image file
        image_data = await file.read()
        
        # Convert to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # Process with invoice analyzer
        result = invoice_analyzer.analyze_invoice(image_b64)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/translate")
async def translate_text(text: str, source_lang: str = "auto", target_lang: str = "en"):
    """
    Translate text between languages
    """
    try:
        # Simple translation service (in production, use Google Translate API)
        translations = {
            ("tamil", "english"): {
                "நாட்டு சக்கரை": "Country sugar",
                "ராகி": "Ragi",
                "கம்பு": "Pearl millet"
            },
            ("english", "tamil"): {
                "Country sugar": "நாட்டு சக்கரை",
                "Ragi": "ராகி", 
                "Pearl millet": "கம்பு"
            }
        }
        
        key = (source_lang, target_lang)
        translated = translations.get(key, {}).get(text, text)
        
        return {
            "translated_text": translated,
            "source_language": source_lang,
            "target_language": target_lang,
            "confidence": 0.95
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Services API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)