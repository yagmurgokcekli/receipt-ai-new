export interface ReceiptAnalysis {
  id: number
  source: string
  merchant_name: string
  transaction_date: string
  tax: number
  total_price: number
  currency: string
}

export interface Receipt {
  id: number
  filename: string
  engine: string
  created_at: string
  analyses: ReceiptAnalysis[]
}
