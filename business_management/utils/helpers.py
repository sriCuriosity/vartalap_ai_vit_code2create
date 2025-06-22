from typing import Dict, Any
from business_management.database.db_manager import DBManager

def get_expense_summary(db: DBManager, start_date: str, end_date: str) -> Dict[str, Any]:
    expenses = db.get_expenses(start_date, end_date)
    total_expenses = sum(e.amount for e in expenses)
    by_category = {}
    for e in expenses:
        by_category.setdefault(e.category, 0.0)
        by_category[e.category] += e.amount
    return {
        'total_expenses': total_expenses,
        'by_category': by_category,
        'expenses': expenses,
    }

def get_revenue_and_profit(db: DBManager, start_date: str, end_date: str) -> Dict[str, Any]:
    bills = db.get_bills(start_date, end_date)
    products = {p.name: p for p in db.get_products()}
    total_revenue = sum(bill.total_amount for bill in bills)
    total_cost = 0.0
    for bill in bills:
        for item in bill.items:
            product_name = item.get('name')
            quantity = item.get('quantity', 0)
            product = products.get(product_name)
            cost_price = product.cost_price if product is not None else 0.0
            total_cost += cost_price * quantity
    net_profit = total_revenue - total_cost
    return {
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'net_profit': net_profit,
    }

def get_product_sales_summary(db: DBManager, start_date: str, end_date: str):
    """
    Returns a list of dicts: product_name, total_quantity, total_revenue, total_cost, total_profit
    """
    bills = db.get_bills(start_date, end_date)
    products = {p.name: p for p in db.get_products()}
    product_stats = {}
    for bill in bills:
        for item in bill.items:
            name = item.get('name')
            if not name:
                continue
            quantity = item.get('quantity', 0)
            total = item.get('total', 0.0)
            product = products.get(name)
            cost_price = product.cost_price if product else 0.0
            if name not in product_stats:
                product_stats[name] = {
                    'product_name': name,
                    'total_quantity': 0,
                    'total_revenue': 0.0,
                    'total_cost': 0.0,
                }
            product_stats[name]['total_quantity'] += quantity
            product_stats[name]['total_revenue'] += total
            product_stats[name]['total_cost'] += cost_price * quantity
    # Add profit
    for stat in product_stats.values():
        stat['total_profit'] = stat['total_revenue'] - stat['total_cost']
    return list(product_stats.values())

def get_best_worst_selling_products(db: DBManager, start_date: str, end_date: str, top_n=5):
    summary = get_product_sales_summary(db, start_date, end_date)
    # Sort by total_quantity for best/worst sellers
    best = sorted(summary, key=lambda x: x['total_quantity'], reverse=True)[:top_n]
    worst = sorted(summary, key=lambda x: x['total_quantity'])[:top_n]
    return best, worst

def get_product_sales_trends(db: DBManager, start_date: str, end_date: str):
    """
    Returns a dict: {product_name: {date: quantity_sold}}
    """
    bills = db.get_bills(start_date, end_date)
    trends = {}
    for bill in bills:
        date = bill.date
        for item in bill.items:
            name = item.get('name')
            if not name:
                continue
            quantity = item.get('quantity', 0)
            if name not in trends:
                trends[name] = {}
            trends[name].setdefault(date, 0)
            trends[name][date] += quantity
    return trends

def get_customer_rfm_segments(db: DBManager, start_date: str, end_date: str):
    """
    Returns a list of dicts: customer_key, recency, frequency, monetary, segment
    """
    import pandas as pd
    bills = db.get_bills(start_date, end_date)
    if not bills:
        return []
    data = []
    for bill in bills:
        data.append({
            'customer_key': bill.customer_key,
            'date': bill.date,
            'amount': bill.total_amount
        })
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    now = df['date'].max()
    rfm = df.groupby('customer_key').agg(
        recency=('date', lambda x: (now - x.max()).days),
        frequency=('date', 'count'),
        monetary=('amount', 'sum')
    ).reset_index()
    # Simple segmentation rules
    segments = []
    for _, row in rfm.iterrows():
        if row['frequency'] >= 5 and row['monetary'] >= df['amount'].quantile(0.75):
            segment = 'High-Value'
        elif row['frequency'] >= 5:
            segment = 'Loyal'
        elif row['recency'] > 30:
            segment = 'At-Risk'
        elif row['frequency'] == 1:
            segment = 'New'
        else:
            segment = 'Other'
        segments.append({
            'customer_key': row['customer_key'],
            'recency': row['recency'],
            'frequency': row['frequency'],
            'monetary': row['monetary'],
            'segment': segment
        })
    return segments

def get_customer_purchase_patterns(db: DBManager, start_date: str, end_date: str):
    """
    Returns a dict: customer_key -> {'avg_days_between': float, 'most_common_products': [str]}
    """
    import pandas as pd
    bills = db.get_bills(start_date, end_date)
    patterns = {}
    for key in set(b.customer_key for b in bills):
        cust_bills = [b for b in bills if b.customer_key == key]
        dates = sorted([b.date for b in cust_bills])
        if len(dates) > 1:
            date_series = pd.to_datetime(dates)
            avg_days = (date_series.max() - date_series.min()).days / (len(date_series) - 1)
        else:
            avg_days = None
        # Most common products
        products = []
        for b in cust_bills:
            for item in b.items:
                name = item.get('name')
                if name:
                    products.append(name)
        from collections import Counter
        most_common = [p for p, _ in Counter(products).most_common(3)]
        patterns[key] = {
            'avg_days_between': avg_days,
            'most_common_products': most_common
        }
    return patterns

def get_top_products_by_revenue(db: DBManager, start_date: str, end_date: str, top_n=10):
    bills = db.get_bills(start_date, end_date)
    product_revenue = {}
    for bill in bills:
        for item in bill.items:
            name = item.get('name')
            if not name:
                continue
            total = item.get('total', 0.0)
            product_revenue.setdefault(name, 0.0)
            product_revenue[name] += total
    return sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:top_n]

def get_sales_by_day_of_week(db: DBManager, start_date: str, end_date: str):
    import pandas as pd
    bills = db.get_bills(start_date, end_date)
    data = [{'date': b.date, 'amount': b.total_amount} for b in bills]
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    return df.groupby('day_of_week')['amount'].sum().to_dict()

def get_sales_by_month(db: DBManager, start_date: str, end_date: str):
    import pandas as pd
    bills = db.get_bills(start_date, end_date)
    data = [{'date': b.date, 'amount': b.total_amount} for b in bills]
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    return df.groupby('month')['amount'].sum().to_dict()

def get_sales_heatmap_data(db: DBManager, start_date: str, end_date: str):
    import pandas as pd
    bills = db.get_bills(start_date, end_date)
    data = [{'date': b.date, 'amount': b.total_amount} for b in bills]
    df = pd.DataFrame(data)
    if df.empty:
        return None
    df['date'] = pd.to_datetime(df['date'])
    df['hour'] = df['date'].dt.hour
    df['day'] = df['date'].dt.day_name()
    heatmap = df.pivot_table(index='day', columns='hour', values='amount', aggfunc='sum', fill_value=0)
    return heatmap

def get_revenue_by_customer_segment(db: DBManager, start_date: str, end_date: str):
    from collections import defaultdict
    rfm = get_customer_rfm_segments(db, start_date, end_date)
    bills = db.get_bills(start_date, end_date)
    seg_revenue = defaultdict(float)
    for bill in bills:
        seg = next((r['segment'] for r in rfm if r['customer_key'] == bill.customer_key), 'Other')
        seg_revenue[seg] += bill.total_amount
    return dict(seg_revenue)

def forecast_total_sales(db: DBManager, start_date: str, end_date: str, periods: int = 30):
    """
    Returns a DataFrame with columns: ds (date), y (actual), yhat (forecast), yhat_lower, yhat_upper
    """
    import pandas as pd
    try:
        from prophet import Prophet
    except ImportError:
        from fbprophet import Prophet
    bills = db.get_bills(start_date, end_date)
    data = [{'ds': b.date, 'y': b.total_amount} for b in bills]
    df = pd.DataFrame(data)
    if df.empty:
        return None
    df['ds'] = pd.to_datetime(df['ds'])
    df = df.groupby('ds').sum().reset_index()
    if len(df.dropna()) < 2:
        return None
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    result = df.merge(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds', how='right')
    return result

def predict_churned_customers(db: DBManager, start_date: str, end_date: str, recency_threshold: int = 60):
    rfm = get_customer_rfm_segments(db, start_date, end_date)
    churned = [r for r in rfm if r['recency'] > recency_threshold]
    return churned

def recommend_products_for_customer(db: DBManager, customer_key: str, start_date: str, end_date: str, top_n=5):
    bills = db.get_bills(start_date, end_date)
    # Products bought by this customer
    bought = set()
    for b in bills:
        if b.customer_key == customer_key:
            for item in b.items:
                name = item.get('name')
                if name:
                    bought.add(name)
    # Popular products overall
    from collections import Counter
    all_products = []
    for b in bills:
        for item in b.items:
            name = item.get('name')
            if name:
                all_products.append(name)
    popular = [p for p, _ in Counter(all_products).most_common() if p not in bought]
    return popular[:top_n]

def detect_sales_anomalies(db: DBManager, start_date: str, end_date: str):
    import pandas as pd
    bills = db.get_bills(start_date, end_date)
    data = [{'date': b.date, 'amount': b.total_amount} for b in bills]
    df = pd.DataFrame(data)
    if df.empty:
        return []
    df['date'] = pd.to_datetime(df['date'])
    daily = df.groupby('date').sum().reset_index()
    mean = daily['amount'].mean()
    std = daily['amount'].std()
    anomalies = daily[(daily['amount'] > mean + 2*std) | (daily['amount'] < mean - 2*std)]
    return anomalies.to_dict('records')

def detect_expense_anomalies(db: DBManager, start_date: str, end_date: str):
    import pandas as pd
    expenses = db.get_expenses(start_date, end_date)
    data = [{'date': e.date, 'amount': e.amount} for e in expenses]
    df = pd.DataFrame(data)
    if df.empty:
        return []
    df['date'] = pd.to_datetime(df['date'])
    daily = df.groupby('date').sum().reset_index()
    mean = daily['amount'].mean()
    std = daily['amount'].std()
    anomalies = daily[(daily['amount'] > mean + 2*std) | (daily['amount'] < mean - 2*std)]
    return anomalies.to_dict('records')
