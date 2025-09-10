import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { FileBarChart, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import { CUSTOMERS, COMPANY_INFO } from '@/constants'
import { useBills } from '@/hooks/useDatabase'
import { formatCurrency, formatDate } from '@/utils/helpers'
import toast from 'react-hot-toast'

const statementSchema = z.object({
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().min(1, 'End date is required'),
  customerKey: z.string().optional(),
})

type StatementFormData = z.infer<typeof statementSchema>

const StatementGenerator: React.FC = () => {
  const form = useForm<StatementFormData>({
    resolver: zodResolver(statementSchema),
    defaultValues: {
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      customerKey: '',
    },
  })

  const { data: bills = [], isLoading } = useBills({
    startDate: form.watch('startDate'),
    endDate: form.watch('endDate'),
    customerKey: form.watch('customerKey') || undefined,
  })

  const generateStatement = (data: StatementFormData) => {
    if (bills.length === 0) {
      toast.error('No transactions found for the selected criteria')
      return
    }

    const totalDebit = bills
      .filter(bill => bill.transactionType === 'Debit')
      .reduce((sum, bill) => sum + bill.totalAmount, 0)

    const totalCredit = bills
      .filter(bill => bill.transactionType === 'Credit')
      .reduce((sum, bill) => sum + bill.totalAmount, 0)

    const closingBalance = totalDebit - totalCredit
    const balanceType = closingBalance >= 0 ? 'Debit' : 'Credit'

    const itemRows = bills
      .map(bill => {
        const particulars = bill.transactionType === 'Debit' 
          ? 'To Sales' 
          : `By ${bill.remarks || 'Payment'}`
        
        const debitAmount = bill.transactionType === 'Debit' ? formatCurrency(bill.totalAmount) : ''
        const creditAmount = bill.transactionType === 'Credit' ? formatCurrency(bill.totalAmount) : ''

        return `
          <tr>
            <td>${formatDate(bill.date)}</td>
            <td>${particulars}</td>
            <td>${bill.transactionType}</td>
            <td>${bill.billNumber}</td>
            <td>${debitAmount}</td>
            <td>${creditAmount}</td>
          </tr>
        `
      })
      .join('')

    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Statement</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            padding: 20px;
        }
        .statement { 
            border: 2px solid #dc2626; 
            padding: 20px; 
            max-width: 800px; 
            margin: auto; 
        }
        .statement-header { 
            text-align: center; 
            border: 1px solid #dc2626; 
            padding: 18px;
            margin-bottom: 20px;
        }
        .statement-header h1 { 
            margin: 0; 
            color: #dc2626; 
            font-size: 24px;
        }
        .statement-header p { 
            margin: 2px 0; 
            font-size: 14px;
        }
        .statement-title {
            text-align: center;
            margin: 20px 0;
        }
        .statement-table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
        }
        .statement-table th, .statement-table td { 
            border: 1px solid #dc2626; 
            padding: 8px; 
            text-align: left; 
        }
        .statement-table th { 
            background-color: #f3f4f6; 
            font-weight: bold;
        }
        .total-row {
            font-weight: bold;
            background-color: #f9fafb;
        }
        .print-btn {
            margin: 20px auto;
            display: block;
            padding: 10px 20px;
            background-color: #dc2626;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .print-btn:hover {
            background-color: #b91c1c;
        }
        @media print {
            .print-btn { display: none; }
        }
    </style>
</head>
<body>
    <div class="statement">
        <div class="statement-header">
            <h1>${COMPANY_INFO.name}</h1>
            <p>${COMPANY_INFO.address}</p>
            <p>${COMPANY_INFO.city}</p>
            <p>${COMPANY_INFO.phone}</p>
        </div>
        
        <div class="statement-title">
            <h2>Ledger Statement</h2>
            <p>From ${formatDate(data.startDate)} to ${formatDate(data.endDate)}</p>
            ${data.customerKey ? `<p>Customer: ${CUSTOMERS[data.customerKey]?.name}</p>` : ''}
        </div>
        
        <table class="statement-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Particulars</th>
                    <th>Vch Type</th>
                    <th>Vch No</th>
                    <th>Debit</th>
                    <th>Credit</th>
                </tr>
            </thead>
            <tbody>
                ${itemRows}
                <tr class="total-row">
                    <td colspan="4" style="text-align: right;"><strong>Total:</strong></td>
                    <td><strong>${formatCurrency(totalDebit)}</strong></td>
                    <td><strong>${formatCurrency(totalCredit)}</strong></td>
                </tr>
                <tr class="total-row">
                    <td colspan="4" style="text-align: right;"><strong>Closing Balance:</strong></td>
                    <td colspan="2"><strong>${formatCurrency(Math.abs(closingBalance))} ${balanceType}</strong></td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <button class="print-btn" onclick="window.print()">Print Statement</button>
</body>
</html>
    `

    const blob = new Blob([htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
    
    toast.success('Statement generated successfully!')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <FileBarChart className="h-6 w-6" />
        <h1 className="text-2xl font-bold text-gray-900">Statement Generator</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Generate Statement</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(generateStatement)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input
                label="Start Date"
                type="date"
                {...form.register('startDate')}
                error={form.formState.errors.startDate?.message}
              />

              <Input
                label="End Date"
                type="date"
                {...form.register('endDate')}
                error={form.formState.errors.endDate?.message}
              />

              <Select
                label="Customer (Optional)"
                options={[
                  { value: '', label: 'All Customers' },
                  ...Object.entries(CUSTOMERS).map(([key, customer]) => ({
                    value: key,
                    label: customer.name,
                  })),
                ]}
                {...form.register('customerKey')}
              />
            </div>

            <Button
              type="submit"
              loading={isLoading}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Generate Statement
            </Button>
          </form>
        </CardContent>
      </Card>

      {bills.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Bill #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {bills.slice(0, 10).map((bill) => (
                    <tr key={bill.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(bill.date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {CUSTOMERS[bill.customerKey]?.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          bill.transactionType === 'Debit' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {bill.transactionType}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {bill.billNumber}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(bill.totalAmount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {bills.length > 10 && (
                <p className="text-sm text-gray-500 mt-2">
                  Showing first 10 of {bills.length} transactions
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default StatementGenerator