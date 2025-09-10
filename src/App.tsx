import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import BillGenerator from './pages/BillGenerator'
import StatementGenerator from './pages/StatementGenerator'
import ProductMaster from './pages/ProductMaster'
import BillDelete from './pages/BillDelete'
import HandwritingRecognition from './pages/HandwritingRecognition'
import InvoiceScanner from './pages/InvoiceScanner'
import AIAssistant from './pages/AIAssistant'

const App: React.FC = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<BillGenerator />} />
        <Route path="/bill-generator" element={<BillGenerator />} />
        <Route path="/statement-generator" element={<StatementGenerator />} />
        <Route path="/product-master" element={<ProductMaster />} />
        <Route path="/bill-delete" element={<BillDelete />} />
        <Route path="/handwriting" element={<HandwritingRecognition />} />
        <Route path="/invoice-scanner" element={<InvoiceScanner />} />
        <Route path="/ai-assistant" element={<AIAssistant />} />
      </Routes>
    </Layout>
  )
}

export default App