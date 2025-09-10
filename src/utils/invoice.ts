import { Bill, Customer } from '@/types'
import { COMPANY_INFO } from '@/constants'
import { formatCurrency } from './helpers'

export function generateInvoiceHTML(bill: Bill, customer: Customer): string {
  const itemRows = bill.items
    .map((item, index) => `
      <tr>
        <td>${index + 1}</td>
        <td>${item.name}</td>
        <td>${item.quantity}</td>
        <td>${formatCurrency(item.price)}</td>
        <td colspan="2">${formatCurrency(item.total)}</td>
      </tr>
    `)
    .join('')

  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice #${bill.billNumber}</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            padding: 20px;
        }
        .invoice { 
            border: 2px solid #dc2626; 
            padding: 20px; 
            max-width: 800px; 
            margin: auto; 
        }
        .invoice-header { 
            text-align: center; 
            border: 1px solid #dc2626; 
            padding: 18px;
            margin-bottom: 20px;
        }
        .invoice-header h1 { 
            margin: 0; 
            color: #dc2626; 
            font-size: 24px;
        }
        .invoice-header p { 
            margin: 2px 0; 
            font-size: 14px;
        }
        .invoice-info { 
            display: flex; 
            justify-content: space-between; 
            margin: 20px 0; 
        }
        .invoice-info div { 
            width: 48%; 
        }
        .invoice-table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
        }
        .invoice-table th, .invoice-table td { 
            border: 1px solid #dc2626; 
            padding: 8px; 
            text-align: left; 
        }
        .invoice-table th { 
            background-color: #f3f4f6; 
            font-weight: bold;
        }
        .invoice-total { 
            width: 100%; 
            margin-top: 20px; 
        }
        .invoice-total table { 
            width: 50%; 
            float: right; 
            border-collapse: collapse; 
        }
        .invoice-total th, .invoice-total td { 
            border: 1px solid #dc2626; 
            padding: 8px; 
        }
        .invoice-signature { 
            margin-top: 60px; 
            text-align: right; 
        }
        .download-btn {
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
        .download-btn:hover {
            background-color: #b91c1c;
        }
        @media print {
            .download-btn { display: none; }
        }
    </style>
</head>
<body>
    <div class="invoice" id="invoice">
        <div class="invoice-header">
            <h1>${COMPANY_INFO.name}</h1>
            <p>${COMPANY_INFO.address}</p>
            <p>${COMPANY_INFO.city}</p>
            <p>${COMPANY_INFO.phone}</p>
        </div>
        
        <div class="invoice-info">
            <div>
                <p><strong>Invoice No:</strong> ${bill.billNumber}</p>
                <p><strong>To:</strong> ${customer.name}</p>
                <p><strong>Address:</strong> ${customer.address}</p>
            </div>
            <div style="text-align: right;">
                <p><strong>Date:</strong> ${bill.date}</p>
            </div>
        </div>
        
        <table class="invoice-table">
            <thead>
                <tr>
                    <th>S.No.</th>
                    <th>PARTICULARS</th>
                    <th>QTY</th>
                    <th>RATE</th>
                    <th colspan="2">AMOUNT</th>
                </tr>
            </thead>
            <tbody>
                ${itemRows}
            </tbody>
        </table>
        
        <div class="invoice-total">
            <table>
                <tr>
                    <th>TOTAL</th>
                    <td>${formatCurrency(bill.totalAmount)}</td>
                </tr>
                <tr>
                    <th>SGST % + CGST %</th>
                    <td>₹0.00</td>
                </tr>
                <tr>
                    <th>GRAND TOTAL</th>
                    <td>${formatCurrency(bill.totalAmount)}</td>
                </tr>
            </table>
        </div>
        
        <div class="invoice-signature">
            <p>For <strong>${COMPANY_INFO.name}</strong></p>
            <br>
            <p>Authorized Signature</p>
        </div>
    </div>
    
    <button class="download-btn" onclick="window.print()">Print Invoice</button>
    
    <script>
        // Auto-focus for better UX
        window.onload = function() {
            window.focus();
        }
    </script>
</body>
</html>
  `
}