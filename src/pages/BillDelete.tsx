import React, { useState } from 'react'
import { Trash2, AlertTriangle, Eye } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Select from '@/components/ui/Select'
import Modal from '@/components/ui/Modal'
import { useBills, useDeleteBill } from '@/hooks/useDatabase'
import { CUSTOMERS } from '@/constants'
import { formatCurrency, formatDate } from '@/utils/helpers'
import { Bill } from '@/types'
import toast from 'react-hot-toast'

const BillDelete: React.FC = () => {
  const [selectedBillNumber, setSelectedBillNumber] = useState<string>('')
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const [selectedBill, setSelectedBill] = useState<Bill | null>(null)

  const { data: bills = [], isLoading } = useBills()
  const deleteBillMutation = useDeleteBill()

  const billOptions = bills.map(bill => ({
    value: bill.billNumber.toString(),
    label: `Bill #${bill.billNumber} - ${CUSTOMERS[bill.customerKey]?.name} - ${formatCurrency(bill.totalAmount)}`,
  }))

  const handleBillSelect = (billNumber: string) => {
    setSelectedBillNumber(billNumber)
    const bill = bills.find(b => b.billNumber.toString() === billNumber)
    setSelectedBill(bill || null)
  }

  const handleViewDetails = () => {
    if (selectedBill) {
      setShowDetailsModal(true)
    }
  }

  const handleDeleteClick = () => {
    if (selectedBill) {
      setShowConfirmModal(true)
    }
  }

  const handleConfirmDelete = async () => {
    if (selectedBill) {
      try {
        await deleteBillMutation.mutateAsync(selectedBill.billNumber)
        setSelectedBillNumber('')
        setSelectedBill(null)
        setShowConfirmModal(false)
      } catch (error) {
        console.error('Failed to delete bill:', error)
      }
    }
  }

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">Loading bills...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Trash2 className="h-6 w-6" />
        <h1 className="text-2xl font-bold text-gray-900">Delete Bill</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Select Bill to Delete</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Select
            label="Select Bill"
            options={[
              { value: '', label: 'Choose a bill...' },
              ...billOptions,
            ]}
            value={selectedBillNumber}
            onChange={(e) => handleBillSelect(e.target.value)}
          />

          {selectedBill && (
            <div className="p-4 bg-gray-50 rounded-lg space-y-2">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Bill Number:</span> {selectedBill.billNumber}
                </div>
                <div>
                  <span className="font-medium">Date:</span> {formatDate(selectedBill.date)}
                </div>
                <div>
                  <span className="font-medium">Customer:</span> {CUSTOMERS[selectedBill.customerKey]?.name}
                </div>
                <div>
                  <span className="font-medium">Type:</span> 
                  <span className={`ml-1 px-2 py-1 text-xs rounded-full ${
                    selectedBill.transactionType === 'Debit' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {selectedBill.transactionType}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Total Amount:</span> {formatCurrency(selectedBill.totalAmount)}
                </div>
                <div>
                  <span className="font-medium">Items:</span> {selectedBill.items.length}
                </div>
              </div>
              
              {selectedBill.remarks && (
                <div>
                  <span className="font-medium">Remarks:</span> {selectedBill.remarks}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-4">
            <Button
              onClick={handleViewDetails}
              disabled={!selectedBill}
              variant="secondary"
              className="flex items-center gap-2"
            >
              <Eye className="h-4 w-4" />
              View Details
            </Button>
            
            <Button
              onClick={handleDeleteClick}
              disabled={!selectedBill}
              variant="danger"
              className="flex items-center gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Delete Bill
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Confirmation Modal */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Confirm Deletion"
      >
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-red-50 rounded-lg">
            <AlertTriangle className="h-6 w-6 text-red-600" />
            <div>
              <h3 className="font-medium text-red-800">Warning</h3>
              <p className="text-sm text-red-700">
                This action cannot be undone. The bill will be permanently deleted.
              </p>
            </div>
          </div>

          {selectedBill && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm">
                <strong>Bill #{selectedBill.billNumber}</strong> - {CUSTOMERS[selectedBill.customerKey]?.name}
                <br />
                Amount: {formatCurrency(selectedBill.totalAmount)}
                <br />
                Date: {formatDate(selectedBill.date)}
              </p>
            </div>
          )}

          <div className="flex gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={() => setShowConfirmModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleConfirmDelete}
              loading={deleteBillMutation.isPending}
            >
              Delete Bill
            </Button>
          </div>
        </div>
      </Modal>

      {/* Details Modal */}
      <Modal
        isOpen={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
        title={`Bill #${selectedBill?.billNumber} Details`}
        size="lg"
      >
        {selectedBill && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Bill Number</label>
                <p className="text-lg font-semibold">{selectedBill.billNumber}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Date</label>
                <p className="text-lg">{formatDate(selectedBill.date)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Customer</label>
                <p className="text-lg">{CUSTOMERS[selectedBill.customerKey]?.name}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Transaction Type</label>
                <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${
                  selectedBill.transactionType === 'Debit' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {selectedBill.transactionType}
                </span>
              </div>
            </div>

            {selectedBill.remarks && (
              <div>
                <label className="text-sm font-medium text-gray-500">Remarks</label>
                <p className="text-lg">{selectedBill.remarks}</p>
              </div>
            )}

            <div>
              <label className="text-sm font-medium text-gray-500">Items</label>
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
                        Price
                      </th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {selectedBill.items.map((item, index) => (
                      <tr key={index}>
                        <td className="px-4 py-2 text-sm text-gray-900">{item.name}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{item.quantity}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{formatCurrency(item.price)}</td>
                        <td className="px-4 py-2 text-sm text-gray-900">{formatCurrency(item.total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex justify-between items-center text-lg font-semibold">
                <span>Total Amount:</span>
                <span>{formatCurrency(selectedBill.totalAmount)}</span>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default BillDelete