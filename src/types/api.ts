export interface APIResponse<T = any> {
  data?: T
  error?: string
  message?: string
  status: number
}

export interface HandwritingAPIRequest {
  image: string // base64
  language: Language
  outputFormat?: 'text' | 'structured'
}

export interface InvoiceAnalysisRequest {
  image: string // base64
  extractItems?: boolean
  extractTotals?: boolean
}

export interface TranslationRequest {
  text: string
  sourceLang: string
  targetLang: string
}

export interface AIServiceConfig {
  baseURL: string
  timeout: number
  retries: number
  apiKey?: string
}

export interface ServiceEndpoints {
  handwriting: string
  invoice: string
  translation: string
  assistant: string
}