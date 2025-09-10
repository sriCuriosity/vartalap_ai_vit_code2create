export interface Customer {
  key: string
  name: string
  address: string
}

export interface BillItem {
  name: string
  price: number
  quantity: number
  total: number
  type?: 'Debit' | 'Credit'
  remarks?: string
}

export interface Bill {
  id?: number
  billNumber: number
  customerKey: string
  date: string
  items: BillItem[]
  totalAmount: number
  transactionType: 'Debit' | 'Credit'
  remarks?: string
}

export interface Product {
  id?: number
  name: string
}

export interface HandwritingResult {
  text: string
  confidence: number
  languageDetected: string
  words: Array<{
    text: string
    confidence: number
    bbox: [number, number, number, number]
  }>
  error?: string
}

export interface InvoiceData {
  vendor: string
  invoiceNumber: string
  date: string
  customer?: string
  items: Array<{
    name: string
    quantity: number
    unit: string
    rate: number
    amount: number
  }>
  subtotal: number
  tax: number
  total: number
  confidence: number
  error?: string
}

export interface AIResponse {
  message: string
  timestamp: string
  isUser: boolean
}

export interface DatabaseConfig {
  dbPath: string
}

export interface APIEndpoints {
  handwritingRecognition: string
  invoiceAnalysis: string
  translation: string
}

export type TransactionType = 'Debit' | 'Credit'
export type Language = 'auto' | 'tamil' | 'english' | 'mixed'

export interface FormErrors {
  [key: string]: string | undefined
}

export interface PaginationParams {
  page: number
  limit: number
}

export interface SortParams {
  field: string
  direction: 'asc' | 'desc'
}

export interface FilterParams {
  startDate?: string
  endDate?: string
  customerKey?: string
  transactionType?: TransactionType
}