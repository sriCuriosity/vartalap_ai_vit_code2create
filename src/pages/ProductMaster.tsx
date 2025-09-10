import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Package, Plus, Search } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { useProducts, useAddProduct } from '@/hooks/useDatabase'
import { fuzzySearch } from '@/utils/helpers'
import toast from 'react-hot-toast'

const productSchema = z.object({
  name: z.string().min(1, 'Product name is required').max(200, 'Product name too long'),
})

type ProductFormData = z.infer<typeof productSchema>

const ProductMaster: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const { data: products = [], isLoading } = useProducts()
  const addProductMutation = useAddProduct()

  const form = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      name: '',
    },
  })

  const filteredProducts = searchQuery
    ? fuzzySearch(products, searchQuery, ['name'])
    : products

  const addProduct = async (data: ProductFormData) => {
    const trimmedName = data.name.trim()
    
    // Check if product already exists
    const exists = products.some(p => p.name.toLowerCase() === trimmedName.toLowerCase())
    if (exists) {
      toast.error('Product already exists!')
      return
    }

    try {
      await addProductMutation.mutateAsync({ name: trimmedName })
      form.reset()
    } catch (error) {
      console.error('Failed to add product:', error)
    }
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">Loading products...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Package className="h-6 w-6" />
        <h1 className="text-2xl font-bold text-gray-900">Product Master</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add New Product</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(addProduct)} className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Enter product name (Tamil or English)"
                {...form.register('name')}
                error={form.formState.errors.name?.message}
              />
            </div>
            <Button
              type="submit"
              loading={addProductMutation.isPending}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Product
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Product List ({products.length} items)</span>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredProducts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {searchQuery ? 'No products found matching your search.' : 'No products added yet.'}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-2">
                    <Package className="h-4 w-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-900">
                      {product.name}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {searchQuery && filteredProducts.length > 0 && (
            <div className="mt-4 text-sm text-gray-500">
              Showing {filteredProducts.length} of {products.length} products
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default ProductMaster