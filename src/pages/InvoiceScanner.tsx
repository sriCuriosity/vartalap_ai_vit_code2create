import React, { useState, useRef } from 'react'
import { ScanLine, Upload, Download, FileText, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { aiService } from '@/utils/api'
import { InvoiceData } from '@/types'
import { formatCurrency, exportToCSV } from '@/utils/helpers'
import toast from 'react-hot-toast'

const InvoiceScanner: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [invoiceData, setInvoiceData] = useState<InvoiceData | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
        toast.error('Please select an image or PDF file')
        return
      }
      
      if (file.size > 20 * 1024 * 1024) { // 20MB limit
        toast.error('File size must be less than 20MB')
        return
      }

      setSelectedFile(file)
      
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file)
        setPreviewUrl(url)
      } else {
        setPreviewUrl('')
      }
      
      setInvoiceData(null)
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const scanInvoice = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first')
      return
    }

    setIsProcessing(true)
    try {
      const result = await aiService.analyzeInvoice(selectedFile)
      setInvoiceData(result)
      
      if (result.error) {
        toast.error(`Analysis failed: ${result.error}`)
      } else {
        toast.success(`Invoice analyzed with ${(result.confidence * 100).toFixed(1)}% confidence`)
      }
    } catch (error) {
      console.error('Invoice analysis failed:', error)
      toast.error('Failed to analyze invoice')
    } finally {
      setIsProcessing(false)
    }
  }

  const createBillFromData = () => {
    if (invoiceData) {
      toast.success('Invoice data would be loaded into bill generator')
      // In a real app, this would navigate to bill generator and populate the form
    }
  }

  const exportData = () => {
    if (invoiceData) {
      const data = [
        {
          vendor: invoiceData.vendor,
          invoiceNumber: invoiceData.invoiceNumber,
          date: invoiceData.date,
          subtotal: invoiceData.subtotal,
          tax: invoiceData.tax,
          total: invoiceData.total,
          confidence: invoiceData.confidence,
        },
        ...invoiceData.items.map(item => ({
          itemName: item.name,
          quantity: item.quantity,
          unit: item.unit,
          rate: item.rate,
          amount: item.amount,
        }))
      ]
      
      exportToCSV(data, `invoice_${invoiceData.invoiceNumber}_${Date.now()}`)
    }
  }

  const clearAll = () => {
    setSelectedFile(null)
    setPreviewUrl('')
    setInvoiceData(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <ScanLine className="h-6 w-6" />
        <h1 className="text-2xl font-bold text-gray-900">Invoice Scanner & Analyzer</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Invoice</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,application/pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <Button
              onClick={handleUploadClick}
              variant="secondary"
              className="w-full flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              Select Invoice Image/PDF
            </Button>

            {selectedFile && (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Invoice preview"
                    className="max-w-full h-auto max-h-64 mx-auto rounded"
                  />
                ) : (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-600">PDF file loaded</p>
                  </div>
                )}
                <p className="text-sm text-gray-500 mt-2 text-center">
                  {selectedFile.name}
                </p>
              </div>
            )}

            <div className="flex gap-2">
              <Button
                onClick={scanInvoice}
                disabled={!selectedFile || isProcessing}
                loading={isProcessing}
                className="flex-1"
              >
                {isProcessing ? 'Analyzing...' : 'Scan & Analyze'}
              </Button>
              
              <Button
                onClick={clearAll}
                variant="secondary"
                disabled={!selectedFile}
              >
                Clear
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle>Extracted Data</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isProcessing && (
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner size="lg" />
                <span className="ml-3 text-gray-600">Analyzing invoice...</span>
              </div>
            )}

            {invoiceData && !isProcessing && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Vendor:</label>
                    <p className="font-medium">{invoiceData.vendor}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Invoice #:</label>
                    <p className="font-medium">{invoiceData.invoiceNumber}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Date:</label>
                    <p className="font-medium">{invoiceData.date}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Confidence:</label>
                    <p className="font-medium">{(invoiceData.confidence * 100).toFixed(1)}%</p>
                  </div>
                </div>

                {invoiceData.items.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Items:</label>
                    <div className="mt-2 border rounded-lg overflow-hidden">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                              Item
                            </th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                              Qty
                            </th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                              Rate
                            </th>
                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                              Amount
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {invoiceData.items.map((item, index) => (
                            <tr key={index}>
                              <td className="px-4 py-2 text-sm text-gray-900">{item.name}</td>
                              <td className="px-4 py-2 text-sm text-gray-900">
                                {item.quantity} {item.unit}
                              </td>
                              <td className="px-4 py-2 text-sm text-gray-900">
                                {formatCurrency(item.rate)}
                              </td>
                              <td className="px-4 py-2 text-sm text-gray-900">
                                {formatCurrency(item.amount)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t space-y-2">
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span>{formatCurrency(invoiceData.subtotal)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Tax:</span>
                    <span>{formatCurrency(invoiceData.tax)}</span>
                  </div>
                  <div className="flex justify-between font-semibold text-lg">
                    <span>Total:</span>
                    <span>{formatCurrency(invoiceData.total)}</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={createBillFromData}
                    className="flex items-center gap-2"
                  >
                    <CheckCircle className="h-4 w-4" />
                    Create Bill
                  </Button>

                  <Button
                    onClick={exportData}
                    variant="secondary"
                    className="flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Export Data
                  </Button>
                </div>
              </>
            )}

            {!invoiceData && !isProcessing && (
              <div className="text-center py-8 text-gray-500">
                Upload an invoice and click "Scan & Analyze" to extract data.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Supported Formats */}
      <Card>
        <CardHeader>
          <CardTitle>Supported Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-2">File Formats</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• JPG, PNG, TIFF, BMP images</li>
                <li>• PDF documents</li>
                <li>• Maximum file size: 20MB</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Extracted Information</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• Vendor name and details</li>
                <li>• Invoice number and date</li>
                <li>• Line items with quantities and prices</li>
                <li>• Subtotal, tax, and total amounts</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default InvoiceScanner