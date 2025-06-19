import sqlite3
import os
from typing import List, Optional
from business_management.models.bill import Bill

class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
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
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            conn.commit()

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

    def get_products(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM products ORDER BY name ASC')
            return [row[0] for row in cursor.fetchall()]

    def add_product(self, name: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO products (name) VALUES (?)', (name.strip(),))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def delete_bill(self, bill_number: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM bills WHERE bill_number = ?', (bill_number,))
            conn.commit()
            return cursor.rowcount > 0
