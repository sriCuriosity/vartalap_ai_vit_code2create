import sqlite3
import os
from typing import List, Optional
from business_management.models.bill import Bill
from business_management.models.product import Product

class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_database()

    def _initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_number INTEGER NOT NULL UNIQUE,
                    customer_key TEXT NOT NULL,
                    date TEXT NOT NULL,
                    items TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    remarks TEXT
                )
            ''')
            # Add product master table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    cost_price REAL DEFAULT 0.0,
                    stock_quantity INTEGER DEFAULT 0,
                    reorder_threshold INTEGER DEFAULT 0,
                    supplier_lead_time INTEGER DEFAULT 0,
                    category TEXT DEFAULT 'Uncategorized'
                )
            ''')
            self._update_product_schema(cursor)
            # Add expenses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT
                )
            ''')
            conn.commit()

    def _update_product_schema(self, cursor):
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN cost_price REAL DEFAULT 0.0")
        except sqlite3.OperationalError:
            pass # Column already exists
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN stock_quantity INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN reorder_threshold INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN supplier_lead_time INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT 'Uncategorized'")
        except sqlite3.OperationalError:
            pass

    def save_bill(self, bill: Bill):
        import json
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bills (bill_number, customer_key, date, items, total_amount, transaction_type, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                bill.bill_number,
                bill.customer_key,
                bill.date,
                json.dumps(bill.items),
                bill.total_amount,
                bill.transaction_type,
                bill.remarks
            ))
            conn.commit()

    def get_bill(self, bill_number: int) -> Optional[Bill]:
        import json
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT bill_number, customer_key, date, items, total_amount, transaction_type, remarks FROM bills WHERE bill_number = ?', (bill_number,))
            row = cursor.fetchone()
            if row:
                return Bill(
                    bill_number=row[0],
                    customer_key=row[1],
                    date=row[2],
                    items=json.loads(row[3]),
                    total_amount=row[4],
                    transaction_type=row[5],
                    remarks=row[6] or ""
                )
        return None

    def get_bills(self, start_date: str, end_date: str, customer_key: Optional[str] = None) -> List[Bill]:
        import json
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT bill_number, customer_key, date, items, total_amount, transaction_type, remarks FROM bills WHERE date BETWEEN ? AND ?"
            params = [start_date, end_date]
            if customer_key:
                query += " AND customer_key = ?"
                params.append(customer_key)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            bills = [
                Bill(
                    bill_number=row[0],
                    customer_key=row[1],
                    date=row[2],
                    items=json.loads(row[3]),
                    total_amount=row[4],
                    transaction_type=row[5],
                    remarks=row[6] or ""
                ) for row in rows
            ]
            return bills

    def get_total_amount(self, start_date: str, end_date: str, transaction_type: Optional[str] = None) -> float:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT SUM(total_amount) FROM bills WHERE date BETWEEN ? AND ?"
            params = [start_date, end_date]
            if transaction_type:
                query += " AND transaction_type = ?"
                params.append(transaction_type)
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0.0

    def get_products(self) -> List[Product]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, cost_price, stock_quantity, reorder_threshold, supplier_lead_time, category FROM products ORDER BY name ASC')
            rows = cursor.fetchall()
            return [Product(**row) for row in rows]

    def add_product(self, name: str, cost_price: float = 0.0, stock_quantity: int = 0, reorder_threshold: int = 0, supplier_lead_time: int = 0, category: str = 'Uncategorized') -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO products (name, cost_price, stock_quantity, reorder_threshold, supplier_lead_time, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name.strip(), cost_price, stock_quantity, reorder_threshold, supplier_lead_time, category))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def update_product(self, product: Product) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE products
                SET name = ?, cost_price = ?, stock_quantity = ?, reorder_threshold = ?, supplier_lead_time = ?, category = ?
                WHERE id = ?
            ''', (product.name, product.cost_price, product.stock_quantity, product.reorder_threshold, product.supplier_lead_time, product.category, product.id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_bill(self, bill_number: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM bills WHERE bill_number = ?', (bill_number,))
            conn.commit()
            return cursor.rowcount > 0

    def add_expense(self, date: str, amount: float, category: str, description: str = "") -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (date, amount, category, description)
                VALUES (?, ?, ?, ?)
            ''', (date, amount, category, description))
            conn.commit()
            return True

    def get_expenses(self, start_date: str, end_date: str, category: str = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT id, date, amount, category, description FROM expenses WHERE date BETWEEN ? AND ?"
            params = [start_date, end_date]
            if category:
                query += " AND category = ?"
                params.append(category)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            from business_management.models.expense import Expense
            return [Expense(*row) for row in rows]
