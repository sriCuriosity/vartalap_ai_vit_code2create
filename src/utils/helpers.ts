import { format, parseISO } from 'date-fns'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import Fuse from 'fuse.js'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date, formatStr: string = 'dd-MM-yyyy'): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return format(dateObj, formatStr)
}

export function formatCurrency(amount: number): string {
  return `₹${amount.toFixed(2)}`
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function fuzzySearch<T>(
  items: T[],
  query: string,
  keys: string[],
  threshold: number = 0.4
): T[] {
  if (!query.trim()) return items

  const fuse = new Fuse(items, {
    keys,
    threshold,
    includeScore: true,
  })

  const results = fuse.search(query)
  return results.map(result => result.item)
}

export function downloadFile(content: string, filename: string, mimeType: string = 'text/plain'): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function validatePhone(phone: string): boolean {
  const phoneRegex = /^[+]?[\d\s\-()]{10,}$/
  return phoneRegex.test(phone)
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function parseItemName(text: string): { name: string; quantity?: number } {
  const words = text.trim().split(/\s+/)
  const lastWord = words[words.length - 1]
  
  // Try to extract quantity from last word
  const quantityMatch = lastWord.match(/^(\d+)/)
  if (quantityMatch) {
    const quantity = parseInt(quantityMatch[1], 10)
    const name = words.slice(0, -1).join(' ')
    return { name, quantity }
  }
  
  return { name: text }
}

export function calculateTotal(items: Array<{ price: number; quantity: number }>): number {
  return items.reduce((total, item) => total + (item.price * item.quantity), 0)
}

export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  headers?: Record<keyof T, string>
): void {
  if (data.length === 0) return

  const keys = Object.keys(data[0]) as (keyof T)[]
  const headerRow = headers 
    ? keys.map(key => headers[key] || String(key)).join(',')
    : keys.join(',')

  const csvContent = [
    headerRow,
    ...data.map(row => 
      keys.map(key => {
        const value = row[key]
        // Escape commas and quotes in CSV
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return String(value)
      }).join(',')
    )
  ].join('\n')

  downloadFile(csvContent, `${filename}.csv`, 'text/csv')
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}