import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, Trash2, FileText, PenTool, ScanLine, Bot } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import { CUSTOMERS } from '@/constants'
import { BillItem, TransactionType } from '@/types'
import { useDatabase, useSaveBill, useNextBillNumber, useProducts } from '@/hooks/useDatabase'
import { formatCurrency, calculateTotal, fuzzySearch } from '@/utils/helpers'
import { generateInvoiceHTML } from '@/utils/invoice'
import toast from 'react-hot-toast'

const billSchema = z.object({
  customerKey: z.string().min(1, 'Customer is required'),
  date: z.string().min(1, 'Date is required'),
  transactionType: z.enum(['Debit', 'Credit']),
  remarks: z.string().optional(),
  creditAmount: z.number().optional(),
})

type BillFormData = z.infer<typeof billSchema>

const itemSchema = z.object({
  name: z.string().min(1, 'Item name is required'),
  price: z.number().min(0.01, 'Price must be greater than 0'),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
})

type ItemFormData = z.infer<typeof itemSchema>

const BillGenerator: React.FC = () => {
  const { isInitialized } = useDatabase()
  const { data: nextBillNumber } = useNextBillNumber()
  const { data: products = [] } = useProducts()
  const saveBillMutation = useSaveBill()

  const [items, setItems] = useState<BillItem[]>([])
  const [filteredProducts, setFilteredProducts] = useState<string[]>([])
  const [showAIFeatures, setShowAIFeatures] = useState(false)

  const billForm = useForm<BillFormData>({
    resolver: zodResolver(billSchema),
    defaultValues: {
      customerKey: Object.keys(CUSTOMERS)[0],
      date: new Date().toISOString().split('T')[0],
      transactionType: 'Debit',
      remarks: '',
      creditAmount: 0,
    },
  })

  const itemForm = useForm<ItemFormData>({
    resolver: zodResolver(itemSchema),
    defaultValues: {
      name: '',
      price: 0,
      quantity: 1,
    },
  })

  const transactionType = billForm.watch('transactionType')
  const itemName = itemForm.watch('name')

  // Filter products based on item name input
  useEffect(() => {
    if (itemName) {
      const productNames = products.map(p => p.name)
      const filtered = fuzzySearch(productNames, itemName, ['name'])
      setFilteredProducts(filtered.slice(0, 10))
    } else {
      setFilteredProducts([])
    }
  }, [itemName, products])

  const addItem = (data: ItemFormData) => {
    const newItem: BillItem = {
      name: data.name,
      price: data.price,
      quantity: data.quantity,
      total: data.price * data.quantity,
      type: 'Debit',
    }

    // Check if item already exists and merge quantities
    const existingIndex = items.findIndex(item => 
      item.name.toLowerCase() === newItem.name.toLowerCase()
    )

    if (existingIndex >= 0) {
      const updatedItems = [...items]
      updatedItems[existingIndex].quantity += newItem.quantity
      updatedItems[existingIndex].total += newItem.total
      setItems(updatedItems)
    } else {
      setItems([...items, newItem])
    }

    itemForm.reset()
    toast.success('Item added successfully')
  }

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
    toast.success('Item removed')
  }

  const generateBill = async (data: BillFormData) => {
    if (!nextBillNumber) {
      toast.error('Unable to generate bill number')
      return
    }

    if (data.transactionType === 'Debit' && items.length === 0) {
      toast.error('Please add items for debit transaction')
      return
    }

    if (data.transactionType === 'Credit' && (!data.creditAmount || data.creditAmount <= 0)) {
      toast.error('Please enter valid credit amount')
      return
    }

    const billItems = data.transactionType === 'Debit' 
      ? items 
      : [{
          name: data.remarks || 'Credit Entry',
          price: 0,
          quantity: 0,
          total: data.creditAmount || 0,
          type: 'Credit' as const,
          remarks: data.remarks,
        }]

    const totalAmount = data.transactionType === 'Debit' 
      ? calculateTotal(items)
      : data.creditAmount || 0

    const bill = {
      billNumber: nextBillNumber,
      customerKey: data.customerKey,
      date: data.date,
      items: billItems,
      totalAmount,
      transactionType: data.transactionType,
      remarks: data.remarks,
    }

    try {
      await saveBillMutation.mutateAsync(bill)
      
      // Generate HTML invoice for debit transactions
      if (data.transactionType === 'Debit') {
        const customer = CUSTOMERS[data.customerKey]
        const htmlContent = generateInvoiceHTML(bill, customer)
        const blob = new Blob([htmlContent], { type: 'text/html' })
        const url = URL.createObjectURL(blob)
        window.open(url, '_blank')
      }

      // Reset form
      billForm.reset()
      setItems([])
      toast.success('Bill generated successfully!')
    } catch (error) {
      console.error('Failed to generate bill:', error)
    }
  }

  const clearForm = () => {
    billForm.reset()
    itemForm.reset()
    setItems([])
  }

  if (!isInitialized) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Enhanced Bill Generator</h1>
        <Button
          variant="secondary"
          onClick={() => setShowAIFeatures(!showAIFeatures)}
        >
          {showAIFeatures ? 'Hide' : 'Show'} AI Features
        </Button>
      </div>

      {showAIFeatures && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              AI Features
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button variant="secondary" className="flex items-center gap-2">
                <PenTool className="h-4 w-4" />
                Handwriting Recognition
              </Button>
              <Button variant="secondary" className="flex items-center gap-2">
                <ScanLine className="h-4 w-4" />
                Invoice Scanner
              </Button>
              <Button variant="secondary" className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                AI Assistant
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <form onSubmit={billForm.handleSubmit(generateBill)} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Bill Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Select
                label="Customer"
                options={Object.entries(CUSTOMERS).map(([key, customer]) => ({
                  value: key,
                  label: customer.name,
                }))}
                {...billForm.register('customerKey')}
                error={billForm.formState.errors.customerKey?.message}
              />
              
              <Input
                label="Date"
                type="date"
                {...billForm.register('date')}
                error={billForm.formState.errors.date?.message}
              />

              <Select
                label="Transaction Type"
                options={[
                  { value: 'Debit', label: 'Debit (Sale)' },
                  { value: 'Credit', label: 'Credit (Payment)' },
                ]}
                {...billForm.register('transactionType')}
                error={billForm.formState.errors.transactionType?.message}
              />
            </div>

            <Input
              label="Remarks"
              {...billForm.register('remarks')}
              error={billForm.formState.errors.remarks?.message}
            />

            {transactionType === 'Credit' && (
              <Input
                label="Credit Amount"
                type="number"
                step="0.01"
                {...billForm.register('creditAmount', { valueAsNumber: true })}
                error={billForm.formState.errors.creditAmount?.message}
              />
            )}
          </CardContent>
        </Card>

        {transactionType === 'Debit' && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Add Items</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={itemForm.handleSubmit(addItem)} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="relative">
                      <Input
                        label="Item Name"
                        {...itemForm.register('name')}
                        error={itemForm.formState.errors.name?.message}
                        autoComplete="off"
                      />
                      {filteredProducts.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                          {filteredProducts.map((product, index) => (
                            <button
                              key={index}
                              type="button"
                              className="w-full px-4 py-2 text-left hover:bg-gray-100 focus:bg-gray-100"
                              onClick={() => {
                                itemForm.setValue('name', product)
                                setFilteredProducts([])
                              }}
                            >
                              {product}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    <Input
                      label="Price"
                      type="number"
                      step="0.01"
                      {...itemForm.register('price', { valueAsNumber: true })}
                      error={itemForm.formState.errors.price?.message}
                    />

                    <Input
                      label="Quantity"
                      type="number"
                      {...itemForm.register('quantity', { valueAsNumber: true })}
                      error={itemForm.formState.errors.quantity?.message}
                    />

                    <div className="flex items-end">
                      <Button type="submit" className="w-full">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Item
                      </Button>
                    </div>
                  </div>
                </form>
              </CardContent>
            </Card>

            {items.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Items List</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {items.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <span className="font-medium">{item.name}</span>
                          <span className="text-gray-500 ml-2">
                            {formatCurrency(item.price)} × {item.quantity} = {formatCurrency(item.total)}
                          </span>
                        </div>
                        <Button
                          type="button"
                          variant="danger"
                          size="sm"
                          onClick={() => removeItem(index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 pt-4 border-t">
                    <div className="flex justify-between items-center text-lg font-semibold">
                      <span>Total:</span>
                      <span>{formatCurrency(calculateTotal(items))}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}

        <div className="flex gap-4">
          <Button
            type="submit"
            loading={saveBillMutation.isPending}
            className="flex items-center gap-2"
          >
            <FileText className="h-4 w-4" />
            Generate Bill
          </Button>
          <Button type="button" variant="secondary" onClick={clearForm}>
            Clear Form
          </Button>
        </div>
      </form>
    </div>
  )
}

export default BillGenerator