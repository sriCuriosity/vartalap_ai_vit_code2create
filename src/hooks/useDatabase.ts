import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { db } from '@/utils/database'
import { Bill, Product, FilterParams } from '@/types'
import { INITIAL_PRODUCTS } from '@/constants'
import toast from 'react-hot-toast'

export function useDatabase() {
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    const initDB = async () => {
      try {
        await db.init()
        
        // Initialize with default products if empty
        const products = await db.getProducts()
        if (products.length === 0) {
          for (const productName of INITIAL_PRODUCTS) {
            await db.addProduct({ name: productName })
          }
        }
        
        setIsInitialized(true)
      } catch (error) {
        console.error('Failed to initialize database:', error)
        toast.error('Failed to initialize database')
      }
    }

    initDB()
  }, [])

  return { isInitialized }
}

export function useBills(filters?: FilterParams) {
  return useQuery({
    queryKey: ['bills', filters],
    queryFn: () => db.getBills(filters),
    enabled: true,
  })
}

export function useBill(billNumber: number) {
  return useQuery({
    queryKey: ['bill', billNumber],
    queryFn: () => db.getBill(billNumber),
    enabled: !!billNumber,
  })
}

export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: () => db.getProducts(),
  })
}

export function useNextBillNumber() {
  return useQuery({
    queryKey: ['nextBillNumber'],
    queryFn: () => db.getNextBillNumber(),
  })
}

export function useSaveBill() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (bill: Omit<Bill, 'id'>) => db.saveBill(bill),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bills'] })
      queryClient.invalidateQueries({ queryKey: ['nextBillNumber'] })
      toast.success('Bill saved successfully!')
    },
    onError: (error) => {
      console.error('Failed to save bill:', error)
      toast.error('Failed to save bill')
    },
  })
}

export function useDeleteBill() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (billNumber: number) => db.deleteBill(billNumber),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bills'] })
      toast.success('Bill deleted successfully!')
    },
    onError: (error) => {
      console.error('Failed to delete bill:', error)
      toast.error('Failed to delete bill')
    },
  })
}

export function useAddProduct() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (product: Omit<Product, 'id'>) => db.addProduct(product),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      toast.success('Product added successfully!')
    },
    onError: (error) => {
      console.error('Failed to add product:', error)
      toast.error('Failed to add product')
    },
  })
}