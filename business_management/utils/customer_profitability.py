from typing import List, Dict, Any
from business_management.models.bill import Bill
from business_management.models.product import Product
from business_management.models.customer import Customer
from business_management.database.db_manager import DBManager


def compute_customer_profitability(db: DBManager, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Returns a list of dicts, each containing profitability metrics for a customer.
    """
    # Get all bills in the date range
    bills = db.get_bills(start_date, end_date)
    # Get all products (for cost lookup)
    products = {p.name: p for p in db.get_products()}

    # Aggregate by customer
    customer_data = {}
    for bill in bills:
        key = bill.customer_key
        if key not in customer_data:
            customer_data[key] = {
                'customer_key': key,
                'total_revenue': 0.0,
                'total_cost': 0.0,
                'num_bills': 0,
            }
        customer_data[key]['total_revenue'] += bill.total_amount
        customer_data[key]['num_bills'] += 1
        # Calculate cost for this bill
        for item in bill.items:
            product_name = item.get('name')
            quantity = item.get('quantity', 0)
            cost_price = products.get(product_name).cost_price if product_name in products else 0.0
            customer_data[key]['total_cost'] += cost_price * quantity

    # Finalize metrics and segment
    results = []
    for key, data in customer_data.items():
        profit = data['total_revenue'] - data['total_cost']
        margin = (profit / data['total_revenue']) * 100 if data['total_revenue'] else 0.0
        # Segment
        if data['total_revenue'] >= 10000 and margin >= 20:
            segment = '💰 High Value'
        elif data['total_revenue'] >= 10000 and margin < 10:
            segment = '😐 Low Margin'
        elif profit < 0:
            segment = '🔻 Unprofitable'
        elif margin >= 30:
            segment = '💎 Gem'
        else:
            segment = 'Other'
        results.append({
            'customer_key': key,
            'total_revenue': data['total_revenue'],
            'total_cost': data['total_cost'],
            'total_profit': profit,
            'profit_margin': margin,
            'num_bills': data['num_bills'],
            'segment': segment,
        })
    return results 