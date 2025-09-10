import { Bill, Product, FilterParams } from '@/types'

// IndexedDB wrapper for client-side storage
class DatabaseManager {
  private dbName = 'BusinessManagementDB'
  private version = 1
  private db: IDBDatabase | null = null

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        this.db = request.result
        resolve()
      }

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result

        // Bills store
        if (!db.objectStoreNames.contains('bills')) {
          const billStore = db.createObjectStore('bills', { 
            keyPath: 'id', 
            autoIncrement: true 
          })
          billStore.createIndex('billNumber', 'billNumber', { unique: true })
          billStore.createIndex('customerKey', 'customerKey', { unique: false })
          billStore.createIndex('date', 'date', { unique: false })
          billStore.createIndex('transactionType', 'transactionType', { unique: false })
        }

        // Products store
        if (!db.objectStoreNames.contains('products')) {
          const productStore = db.createObjectStore('products', { 
            keyPath: 'id', 
            autoIncrement: true 
          })
          productStore.createIndex('name', 'name', { unique: true })
        }

        // Bill number counter
        if (!db.objectStoreNames.contains('counters')) {
          const counterStore = db.createObjectStore('counters', { keyPath: 'name' })
          counterStore.add({ name: 'billNumber', value: 1 })
        }
      }
    })
  }

  async saveBill(bill: Omit<Bill, 'id'>): Promise<number> {
    if (!this.db) throw new Error('Database not initialized')

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['bills'], 'readwrite')
      const store = transaction.objectStore('bills')
      const request = store.add(bill)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result as number)
    })
  }

  async getBill(billNumber: number): Promise<Bill | null> {
    if (!this.db) throw new Error('Database not initialized')

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['bills'], 'readonly')
      const store = transaction.objectStore('bills')
      const index = store.index('billNumber')
      const request = index.get(billNumber)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result || null)
    })
  }

  async getBills(filters?: FilterParams): Promise<Bill[]> {
    if (!this.db) throw new Error('Database not initialized')

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['bills'], 'readonly')
      const store = transaction.objectStore('bills')
      const request = store.getAll()

      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        let bills = request.result as Bill[]

        // Apply filters
        if (filters) {
          bills = bills.filter(bill => {
            if (filters.startDate && bill.date < filters.startDate) return false
            if (filters.endDate && bill.date > filters.endDate) return false
            if (filters.customerKey && bill.customerKey !== filters.customerKey) return false
            if (filters.transactionType && bill.transactionType !== filters.transactionType) return false
            return true
          })
        }

        resolve(bills)
      }
    })
  }

  async deleteBill(billNumber: number): Promise<boolean> {
    if (!this.db) throw new Error('Database not initialized')

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['bills'], 'readwrite')
      const store = transaction.objectStore('bills')
      const index = store.index('billNumber')
      
      const getRequest = index.get(billNumber)
      getRequest.onsuccess = () => {
        const bill = getRequest.result
        if (bill) {
          const deleteRequest = store.delete(bill.id)
          deleteRequest.onsuccess = () => resolve(true)
          deleteRequest.onerror = () => reject(deleteRequest.error)
        } else {
          resolve(false)
        }
      }
      getRequest.onerror = () => reject(getRequest.error)
    })
  }

  async getProducts(): Promise<Product[]> {
    if (!this.db) throw new Error('Database not initialized')

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['products'], 'readonly')
      const store = transaction.objectStore('products')
      const request = store.getAll()

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)
    })
  }

  async addProduct(product: Omit<Product, 'id'>): Promise<number> {
    if (!this.db) throw new Error('Database not initialized')

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['products'], 'readwrite')
      const store = transaction.objectStore('products')
      const request = store.add(product)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result as number)
    })
  }

  async getNextBillNumber(): Promise<number> {
    if (!this.db) throw new Error('Database not initialized')

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['counters'], 'readwrite')
      const store = transaction.objectStore('counters')
      const request = store.get('billNumber')

      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        const counter = request.result
        const nextNumber = counter ? counter.value : 1
        
        // Update counter
        const updateRequest = store.put({ name: 'billNumber', value: nextNumber + 1 })
        updateRequest.onsuccess = () => resolve(nextNumber)
        updateRequest.onerror = () => reject(updateRequest.error)
      }
    })
  }
}

export const db = new DatabaseManager()