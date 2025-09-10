export interface DatabaseConfig {
  dbPath: string
  version: number
}

export interface DatabaseSchema {
  bills: BillRecord
  products: ProductRecord
  counters: CounterRecord
}

export interface BillRecord {
  id?: number
  billNumber: number
  customerKey: string
  date: string
  items: string // JSON string
  totalAmount: number
  transactionType: 'Debit' | 'Credit'
  remarks?: string
}

export interface ProductRecord {
  id?: number
  name: string
  createdAt?: string
}

export interface CounterRecord {
  name: string
  value: number
}

export interface QueryOptions {
  limit?: number
  offset?: number
  orderBy?: string
  orderDirection?: 'asc' | 'desc'
}

export interface DatabaseTransaction {
  commit(): Promise<void>
  rollback(): Promise<void>
}