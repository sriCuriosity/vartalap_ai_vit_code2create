'''import sqlite3
from datetime import datetime
import webbrowser

class LedgerGenerator:
    def __init__(self, db_path="C:\\Users\\Sri Nithilan\\Desktop\\New folder\\bills.db"):
        self.db_path = db_path

    def connect_to_db(self):
        return sqlite3.connect(self.db_path)

    def generate_ledger_statement(self, customer_name, start_date, end_date):
        conn = self.connect_to_db()
        cursor = conn.cursor()

        # Convert dates to proper format
        start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%d-%m-%y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%d-%m-%y")

        # Fetch bills for the specific customer within the date range
        cursor.execute(''''''
        SELECT bill_number, date, total_bill
        FROM bills
        WHERE customer = ? AND date BETWEEN ? AND ?
        ORDER BY date
        '''''', (customer_name, start_date, end_date))

        bills = cursor.fetchall()

        # Fetch customer details
        cursor.execute('SELECT address FROM bills WHERE customer = ? LIMIT 1', (customer_name,))
        address = cursor.fetchone()

        # Generate the ledger statement
        statement = f"{customer_name}\n{address}\n\n"
        statement += f"Ledger Account\n{start_date} to {end_date}\n\n"
        statement += "Date       | Particulars | Vch Type | Vch No | Debit\n"
        statement += "-" * 60 + "\n"

        total_debit = 0
        for bill in bills:
            bill_number, date, total_bill = bill
            date_formatted = datetime.strptime(date, "%d-%m-%y").strftime("%d-%m-%Y")
            statement += f"{date_formatted} | To Sales    | Bill No  | {bill_number:5d} | {total_bill:10.2f}\n"
            total_debit += total_bill

        statement += "-" * 60 + "\n"
        statement += f"Total Debit: {total_debit:10.2f}\n"
        statement += f"Closing Balance: {total_debit:10.2f}\n"

        conn.close()
        return statement

    def save_statement_to_file(self, statement, filename):
        with open(filename, 'w') as f:
            f.write(statement)

# Usage example:
if __name__ == "__main__":
    ledger_gen = LedgerGenerator()
    statement = ledger_gen.generate_ledger_statement("Customer Name", "01-04-2021", "02-12-2024")
    print(statement)
    ledger_gen.save_statement_to_file(statement, "ledger_statement.txt")

def update_html_ledger(ledger_data, output_path):
    # Read the HTML template
    template_path = "C:\\Users\\Sri Nithilan\\Desktop\\sample.html"
    with open(template_path, 'r') as file:
        html_template = file.read()

    # Extract information from the ledger data
    lines = ledger_data.split('\n')
    name = lines[0]
    address = lines[1]
    date_range = lines[3]

    # Parse the ledger data
    transactions = []
    total_debit =0
    for line in lines[6:]:  # Skip header lines
        if line.startswith('---'):
            break
        parts = line.split('|')
        if len(parts) == 5:
            date, particulars, vch_type, vch_no, debit = [p.strip() for p in parts]
            transactions.append({
                'date': date,
                'particulars': particulars,
                'vch_type': vch_type,
                'vch_no': vch_no,
                'debit': debit
            })
            #total_debit += float(debit)

    # Generate table rows
    table_rows = str()
    for t in transactions:
        table_rows += f"<tr><td>{t["date"]}</td><td>{t["particulars"]}</td><td>{t["vch_type"]}</td><td>{t["vch_no"]}</td><td>{t["debit"]:.2f}</td><td></td></tr>"

    # Update the HTML template
    html_content = html_template.format(
        name="V.RAMIAH NADAR",
        address="5, East Marret Street<br>Madurai - 625 001",
        gstin="GSTIN: 33AADFV4917E1ZD",
        phone="9842167234",
        company_name="Bhairavi Organices",
        location="Viruthunagar",
        date_range=date_range,
        table_rows=table_rows,
        closing_balance=f"{total_debit:.2f}",
        total=f"{total_debit:.2f}"
    )

    # Write the updated HTML to a file
    with open(output_path, 'w') as file:
        file.write(html_content)

    print(f"Ledger HTML has been generated and saved to {output_path}")
    webbrowser.open(template_path)

# Usage example:
if __name__ == "__main__":
    ledger_gen = LedgerGenerator()
    ledger_data = ledger_gen.generate_ledger_statement("Customer Name", "01-04-2021", "02-12-2024")
    update_html_ledger(ledger_data,  "ledger_output.html")

import sqlite3
from datetime import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

class LedgerGenerator:
    def __init__(self, db_path="C:\\Users\\Sri Nithilan\\Desktop\\New folder\\bills.db"):
        self.db_path = db_path

    def connect_to_db(self):
        return sqlite3.connect(self.db_path)

    def generate_ledger_statement(self, customer_name, start_date, end_date):
        with self.connect_to_db() as conn:
            cursor = conn.cursor()

            # Convert dates to proper format
            start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%d-%m-%y")
            end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%d-%m-%y")

            # Fetch bills for the specific customer within the date range
            cursor.execute(''''''
            SELECT bill_number, date, total_bill
            FROM bills
            WHERE customer = ? AND date BETWEEN ? AND ?
            ORDER BY date
            '''''', (customer_name, start_date, end_date))

            bills = cursor.fetchall()

            # Fetch customer details
            cursor.execute('SELECT address FROM bills WHERE customer = ? LIMIT 1', (customer_name,))
            address = cursor.fetchone()

            # Generate the ledger statement
            statement = f"{customer_name}\n{address}\n\n"
            statement += f"Ledger Account\n{start_date} to {end_date}\n\n"
            statement += "Date       | Particulars | Vch Type | Vch No | Debit\n"
            statement += "-" * 60 + "\n"

            total_debit = 0
            for bill in bills:
                bill_number, date, total_bill = bill
                date_formatted = datetime.strptime(date, "%d-%m-%y").strftime("%d-%m-%Y")
                statement += f"{date_formatted} | To Sales    | Bill No  | {bill_number:5d} | {total_bill:10.2f}\n"
                total_debit += total_bill

            statement += "-" * 60 + "\n"
            statement += f"Total Debit: {total_debit:10.2f}\n"
            statement += f"Closing Balance: {total_debit:10.2f}\n"

        return statement

    def save_statement_to_file(self, statement, filename):
        with open(filename, 'w') as f:
            f.write(statement)

def update_html_ledger(ledger_data):
    # HTML template as a string
    html_template = """
    <html>
    <head>
        <title>Ledger Statement</title>
    </head>
    <body>
        <h1>{company_name}</h1>
        <p>{name}</p>
        <p>{address}</p>
        <p>{gstin}</p>
        <p>{phone}</p>
        <h2>Ledger Account</h2>
        <p>{date_range}</p>
        <table border="1">
            <tr>
                <th>Date</th>
                <th>Particulars</th>
                <th>Vch Type</th>
                <th>Vch No</th>
                <th>Debit</th>
                <th>Credit</th>
            </tr>
            {table_rows}
        </table>
        <p>Total: {total}</p>
        <p>Closing Balance: {closing_balance}</p>
    </body>
    </html>
    """

    # Extract information from the ledger data
    lines = ledger_data.split('\n')
    name = lines[0]
    address = lines[1]
    date_range = lines[3]

    # Parse the ledger data
    transactions = []
    total_debit = 0
    for line in lines[6:]:  # Skip header lines
        if line.startswith('---'):
            break
        parts = line.split('|')
        if len(parts) == 5:
            date, particulars, vch_type, vch_no, debit = [p.strip() for p in parts]
            transactions.append({
                'date': date,
                'particulars': particulars,
                'vch_type': vch_type,
                'vch_no': vch_no,
                'debit': debit
            })
            print(debit)
            #total_debit += int(debit)

    # Generate table rows
    table_rows = ''
    for t in transactions:
        table_rows += f"""<tr><td>{t["date"]}</td><td>{t["particulars"]}</td><td>{t["vch_type"]}</td><td>{t["vch_no"]}</td><td>{t["debit"]:.2f}</td><td></td></tr>"""

    # Update the HTML template
    html_content = html_template.format(
        name="V.RAMIAH NADAR",
        address="5, East Marret Street<br>Madurai - 625 001",
        gstin="GSTIN: 33AADFV4917E1ZD",
        phone="9842167234",
        company_name="Bhairavi Organices",
        location="Viruthunagar",
        date_range=date_range,
        table_rows=table_rows,
        closing_balance=f"{total_debit:.2f}",
        total=f"{total_debit:.2f}"
    )

    output_path="C:\\Users\\Sri Nithilan\\Desktop\\sample.html"
    # Write the updated HTML to a file
    with open(output_path, 'w') as file:
        file.write(html_content)

    print(f"Ledger HTML has been generated and saved to {output_path}")
    webbrowser.open(output_path)

def create_gui():
    def generate_ledger():
        customer_name = customer_entry.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        if not customer_name or not start_date or not end_date:
            messagebox.showerror("Input Error", "All fields are required")
            return

        ledger_gen = LedgerGenerator()
        ledger_data = ledger_gen.generate_ledger_statement(customer_name, start_date, end_date)
        update_html_ledger(ledger_data)

    # Create the main window
    root = tk.Tk()
    root.title("Ledger Generator")

    # Create and place the input fields
    tk.Label(root, text="Customer Name").grid(row=0, column=0, padx=10, pady=10)
    customer_entry = tk.Entry(root)
    customer_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Start Date (dd-mm-yyyy)").grid(row=1, column=0, padx=10, pady=10)
    start_date_entry = tk.Entry(root)
    start_date_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="End Date (dd-mm-yyyy)").grid(row=2, column=0, padx=10, pady=10)
    end_date_entry = tk.Entry(root)
    end_date_entry.grid(row=2, column=1, padx=10, pady=10)

    # Create and place the Generate button
    generate_button = tk.Button(root, text="Generate Ledger", command=generate_ledger)
    generate_button.grid(row=3, columnspan=2, pady=10)

    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()'''

'''import sqlite3
from datetime import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

class LedgerGenerator:
    def __init__(self, db_path="C:\\Users\\Sri Nithilan\\Desktop\\New folder\\bills.db"):
        self.db_path = db_path

    def connect_to_db(self):
        return sqlite3.connect(self.db_path)

    def generate_ledger_statement(self, customer_name, start_date, end_date):
        with self.connect_to_db() as conn:
            cursor = conn.cursor()

            # Convert dates to proper format
            start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%d-%m-%y")
            end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%d-%m-%y")

            # Fetch bills for the specific customer within the date range
            cursor.execute(''''''
            SELECT bill_number, date, total_bill
            FROM bills
            WHERE customer = ? AND date BETWEEN ? AND ?
            ORDER BY date
            '''''', (customer_name, start_date, end_date))

            bills = cursor.fetchall()

            # Fetch customer details
            cursor.execute('SELECT address FROM bills WHERE customer = ? LIMIT 1', (customer_name,))
            address = cursor.fetchone()

            # Generate the ledger statement
            statement = f"{customer_name}\n{address}\n\n"
            statement += f"Ledger Account\n{start_date} to {end_date}\n\n"
            statement += "Date       | Particulars | Vch Type | Vch No | Debit\n"
            statement += "-" * 60 + "\n"

            total_debit = 0
            for bill in bills:
                bill_number, date, total_bill = bill
                date_formatted = datetime.strptime(date, "%d-%m-%y").strftime("%d-%m-%Y")
                statement += f"{date_formatted} | To Sales    | Bill No  | {bill_number:5d} | {total_bill:10.2f}\n"
                total_debit += total_bill

            statement += "-" * 60 + "\n"
            statement += f"Total Debit: {total_debit:10.2f}\n"
            statement += f"Closing Balance: {total_debit:10.2f}\n"

        return statement

    def save_statement_to_file(self, statement, filename):
        with open(filename, 'w') as f:
            f.write(statement)

def update_html_ledger(ledger_data):
    # HTML template as a string
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ledger Account Statement</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .footer {
            margin-top: 20px;
            text-align: right;
        }
    </style>
    </head>
    <body>
        <h1>{company_name}</h1>
        <p>{name}</p>
        <p>{address}</p>
        <p>{gstin}</p>
        <p>{phone}</p>
        <h2>Ledger Account</h2>
        <p>{date_range}</p>
        <table border="1">
            <tr>
                <th>Date</th>
                <th>Particulars</th>
                <th>Vch Type</th>
                <th>Vch No</th>
                <th>Debit</th>
                <th>Credit</th>
            </tr>
            {table_rows}
        </table>
        <p>Total: {total}</p>
        <p>Closing Balance: {closing_balance}</p>
    </body>
    </html>
    """

    # Extract information from the ledger data
    lines = ledger_data.split('\n')
    name = lines[0]
    address = lines[1]
    date_range = lines[3]

    # Parse the ledger data
    transactions = []
    total_debit = 0
    for line in lines[6:]:  # Skip header lines
        if line.startswith('---'):
            break
        parts = line.split('|')
        if len(parts) == 5:
            date, particulars, vch_type, vch_no, debit = [p.strip() for p in parts]
            transactions.append({
                'date': date,
                'particulars': particulars,
                'vch_type': vch_type,
                'vch_no': vch_no,
                'debit': debit
            })
            print(debit)
            #total_debit += float(debit)

    # Generate table rows
    table_rows = '\n'.join(
        f"""
        <tr>
        <td>{t['date']}</td>
        <td>{t['particulars']}</td>
        <td>{t['vch_type']}</td>
        <td>{t['vch_no']}</td>
        <td>{t['debit']:.2f}</td>
        <td></td>
        </tr>
        """
        for t in transactions
    )

    # Update the HTML template
    html_content = html_template.format(
        name="V.RAMIAH NADAR",
        address="5, East Marret Street<br>Madurai - 625 001",
        gstin="GSTIN: 33AADFV4917E1ZD",
        phone="9842167234",
        company_name="Bhairavi Organices",
        location="Viruthunagar",
        date_range=date_range,
        table_rows=table_rows,
        #closing_balance=f"{total_debit:.2f}",
        #total=f"{total_debit:.2f}"
    )

    output_path="C:\\Users\\Sri Nithilan\\Desktop\\sample.html"
    # Write the updated HTML to a file
    with open(output_path, 'w') as file:
        file.write(html_content)

    print(f"Ledger HTML has been generated and saved to {output_path}")
    webbrowser.open(output_path)

def create_gui():
    def generate_ledger():
        customer_name = customer_entry.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        if not customer_name or not start_date or not end_date:
            messagebox.showerror("Input Error", "All fields are required")
            return

        ledger_gen = LedgerGenerator()
        ledger_data = ledger_gen.generate_ledger_statement(customer_name, start_date, end_date)
        update_html_ledger(ledger_data)

    # Create the main window
    root = tk.Tk()
    root.title("Ledger Generator")

    # Create and place the input fields
    tk.Label(root, text="Customer Name").grid(row=0, column=0, padx=10, pady=10)
    customer_entry = tk.Entry(root)
    customer_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Start Date (dd-mm-yyyy)").grid(row=1, column=0, padx=10, pady=10)
    start_date_entry = tk.Entry(root)
    start_date_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="End Date (dd-mm-yyyy)").grid(row=2, column=0, padx=10, pady=10)
    end_date_entry = tk.Entry(root)
    end_date_entry.grid(row=2, column=1, padx=10, pady=10)

    # Create and place the Generate button
    generate_button = tk.Button(root, text="Generate Ledger", command=generate_ledger)
    generate_button.grid(row=3, columnspan=2, pady=10)

    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()'''

import sqlite3
from datetime import datetime
import webbrowser
import tkinter as tk
from tkinter import messagebox

class LedgerGenerator:
    def __init__(self, db_path="C:\\Users\\Sri Nithilan\\Desktop\\New folder\\bills.db"):
        self.db_path = db_path

    def connect_to_db(self):
        return sqlite3.connect(self.db_path)

    def generate_ledger_statement(self, customer_name, start_date, end_date):
        conn = self.connect_to_db()
        cursor = conn.cursor()

        # Convert dates to proper format
        start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%d-%m-%y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%d-%m-%y")

        # Fetch bills for the specific customer within the date range
        cursor.execute('''
        SELECT bill_number, date, total_bill
        FROM bills
        WHERE customer = ? AND date BETWEEN ? AND ?
        ORDER BY date
        ''', (customer_name, start_date, end_date))

        bills = cursor.fetchall()

        # Fetch customer details
        cursor.execute('SELECT address FROM bills WHERE customer = ? LIMIT 1', (customer_name,))
        address = cursor.fetchone()[0] if cursor.fetchone() else ''

        # Generate the ledger statement
        statement = f"{customer_name}\n{address}\n\n"
        statement += f"Ledger Account\n{start_date} to {end_date}\n\n"
        statement += "Date       | Particulars | Vch Type | Vch No | Debit\n"
        statement += "-" * 60 + "\n"

        total_debit = 0
        for bill in bills:
            bill_number, date, total_bill = bill
            date_formatted = datetime.strptime(date, "%d-%m-%y").strftime("%d-%m-%Y")
            statement += f"{date_formatted} | To Sales    | Bill No  | {bill_number:5d} | {total_bill:10.2f}\n"
            total_debit += total_bill

        statement += "-" * 60 + "\n"
        statement += f"Total Debit: {total_debit:10.2f}\n"
        statement += f"Closing Balance: {total_debit:10.2f}\n"

        conn.close()
        return statement

def update_html_ledger(ledger_data):
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ledger Account Statement</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .footer {
            margin-top: 20px;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="header">
        <h2>{name}</h2>
        <p>{address}</p>
        <p>{gstin}</p>
        <p>Cell: {phone}</p>
        <h3>{company_name}</h3>
        <p>Ledger Account</p>
        <p>{location}</p>
        <p>{date_range}</p>
    </div>

    <table>
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
            {ledger_data}
        </tbody>
    </table>

    <div class="footer">
        <p>By Closing Balance: {closing_balance}</p>
        <p>Total: {total}</p>
    </div>
</body>
</html>
    '''

    output_path = "C:\\Users\\Sri Nithilan\\Desktop\\sample.html"
    with open(output_path, 'w') as file:
        file.write(html_template)

    print(f"Ledger HTML has been generated and saved to {output_path}")
    webbrowser.open(output_path)

def create_gui():
    def generate_ledger():
        customer_name = customer_entry.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        if not customer_name or not start_date or not end_date:
            messagebox.showerror("Input Error", "All fields are required")
            return

        ledger_gen = LedgerGenerator()
        ledger_data = ledger_gen.generate_ledger_statement(customer_name, start_date, end_date)
        update_html_ledger(ledger_data)

    # Create the main window
    root = tk.Tk()
    root.title("Ledger Generator")

    # Create and place the input fields
    tk.Label(root, text="Customer Name").grid(row=0, column=0, padx=10, pady=10)
    customer_entry = tk.Entry(root)
    customer_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Start Date (dd-mm-yyyy)").grid(row=1, column=0, padx=10, pady=10)
    start_date_entry = tk.Entry(root)
    start_date_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="End Date (dd-mm-yyyy)").grid(row=2, column=0, padx=10, pady=10)
    end_date_entry = tk.Entry(root)
    end_date_entry.grid(row=2, column=1, padx=10, pady=10)

    # Create and place the Generate button
    generate_button = tk.Button(root, text="Generate Ledger", command=generate_ledger)
    generate_button.grid(row=3, columnspan=2, pady=10)

    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()
