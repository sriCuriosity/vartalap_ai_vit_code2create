import axios from 'axios'
import { HandwritingResult, InvoiceData, Language } from '@/types'

const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000/api',
  timeout: 30000,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth headers if needed
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const aiService = {
  async recognizeHandwriting(
    imageFile: File, 
    language: Language = 'auto'
  ): Promise<HandwritingResult> {
    const formData = new FormData()
    formData.append('file', imageFile)
    formData.append('language', language)

    try {
      const response = await api.post<HandwritingResult>('/v1/handwriting/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error) {
      // Mock response for development
      return {
        text: 'நாட்டு சக்கரை 5 கிலோ',
        confidence: 0.92,
        languageDetected: 'tamil',
        words: [
          { text: 'நாட்டு', confidence: 0.95, bbox: [10, 20, 80, 45] },
          { text: 'சக்கரை', confidence: 0.90, bbox: [85, 20, 150, 45] },
          { text: '5', confidence: 0.98, bbox: [155, 20, 170, 45] },
          { text: 'கிலோ', confidence: 0.88, bbox: [175, 20, 220, 45] },
        ],
      }
    }
  },

  async analyzeInvoice(imageFile: File): Promise<InvoiceData> {
    const formData = new FormData()
    formData.append('file', imageFile)

    try {
      const response = await api.post<InvoiceData>('/v1/invoice/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error) {
      // Mock response for development
      return {
        vendor: 'SADHASIVA AGENCIES',
        invoiceNumber: '12345',
        date: '2025-01-15',
        items: [
          {
            name: 'நாட்டு சக்கரை',
            quantity: 5,
            unit: 'kg',
            rate: 45.0,
            amount: 225.0,
          },
          {
            name: 'ராகி மாவு',
            quantity: 2,
            unit: 'kg',
            rate: 80.0,
            amount: 160.0,
          },
        ],
        subtotal: 385.0,
        tax: 0.0,
        total: 385.0,
        confidence: 0.89,
      }
    }
  },

  async translateText(
    text: string,
    sourceLang: string = 'auto',
    targetLang: string = 'en'
  ): Promise<{ translatedText: string; confidence: number }> {
    try {
      const response = await api.post('/v1/translate', {
        text,
        source_lang: sourceLang,
        target_lang: targetLang,
      })
      return {
        translatedText: response.data.translated_text,
        confidence: response.data.confidence,
      }
    } catch (error) {
      // Mock translation for development
      const translations: Record<string, string> = {
        'நாட்டு சக்கரை': 'Country sugar',
        'ராகி': 'Ragi',
        'கம்பு': 'Pearl millet',
        'Country sugar': 'நாட்டு சக்கரை',
        'Ragi': 'ராகி',
        'Pearl millet': 'கம்பு',
      }
      
      return {
        translatedText: translations[text] || text,
        confidence: 0.95,
      }
    }
  },
}

export default api