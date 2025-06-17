import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz
import webbrowser
import sqlite3
import os
import json

# Constants
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bills.db")
BILL_NUMBER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Bill Number.txt")
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Ensure template directory exists
os.makedirs(TEMPLATE_DIR, exist_ok=True)
# Sample data for autocomplete suggestions
suggestions = [
    "நாட்டு சக்கரை (Country sugar)",
    "ராகி (Ragi)",
    "ராகி மாவு (Ragi flour)",
    "நாட்டு கம்பு (Country kambu)",
    "நாட்டு கம்பு மாவு (Country kambu flour)",
    "சத்து மாவு (Sattu flour)",
    "மட்ட சம்பா அரிசி (Matta Samba rice)",
    "சிவப்பு கவுணி அரிசி (Red parboiled rice)",
    "சிவப்பு சோளம் (Red corn)",
    "சம்பா அவுள் (Samba bran)",
    "உளுந்தங்களி மாவு (Ulundhu kali flour)",
    "நாட்டு கொண்க்கடலை (Country chickpea)",
    "இடியாப்ப மாவு (Idiyappam flour)",
    "வெள்ளை புட்டு மாவு (White puttu flour)",
    "வெள்ளை நைஸ் அவுள் (White rice bran)",
    "Corn flakes (Corn flakes)",
    "ராகி அவுள் (Ragi bran)",
    "கம்பு அவுள் (Kambu bran)",
    "சோள அவுள் (Corn bran)",
    "கோதுமை அவுள் (Wheat bran)",
    "Red rice அவுள் (Red rice bran)",
    "கொள்ளு அவுள் (Horse gram bran)",
    "வெள்ளை சோளம் (White corn)",
    "சிவப்பு கொள்ளு (Red cowpea)",
    "கருப்பு கொள்ளு (Black cowpea)",
    "உடைத்த கருப்பு உளுந்து (Split black gram)",
    "தட்டைப் பயறு (Thataipayyir)",
    "மாப்பிள்ளை சம்பா அரிசி (Mappillai samba rice)",
    "கைக்குத்தல் அரிசி (Handan sown rice)",
    "அச்சு வெள்ளம் (Palm jaggery)",
    "சிவப்பு அரிசி புட்டு மாவு (Red rice flour for puttu)",
    "சிவப்பு அரிசி இடியாப்ப மாவு (Red rice flour for idiappam)",
    "சிவப்பு அரிசி குருனை (Red rice - Kuruvai variety)",
    "மட்ட சம்பா குருனை (Matta Samba rice - Kuruvai variety)",
    "சிவப்பு நைஸ் அவுள் (Red rice bran)",
    "வெள்ளை கெட்டி அவுள் (White parboiled rice)",
    "சுண்ட வத்தல் (Dried ginger)",
    "மனத்தக்காலி வத்தல் (Bird's eye chili)",
    "மோர் மிளகாய் (Yogurt chilies)",
    "மிதுக்கு வத்தல் (Guntur chili)",
    "பட் அப்பளம் (Batten appalam)",
    "Heart Appalam (Heart appalam)",
    "வெங்காய வடகம் (Onion vadai)",
    "கொத்தவரங்காய் வத்தல் (Cluster beans sundried)",
    "அடை மிக்ஸ் (Adai mix)",
    "கடலை மாவு (Gram flour)",
    "மூங்கில் அரிசி (Foxtail millet)",
    "வருத்த வெள்ளை ரவை (Roasted semolina)",
    "கொள்ளுக்கஞ்சி மாவு (Horse gram kanji flour)",
    "கொள்ளு மாவு (Horse gram flour)",
    "பச்சைப் பயறு (Green Gram)"
]

# Sample data for customers
customers = {
    "A": {"name": "Customer A", "address": "123 Main St"},
    "B": {"name": "Customer B", "address": "456 Elm St"},
    "C": {"name": "Customer C", "address": "789 Oak St"}
}

# Initialize the bill data
bill_data = []

def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            bill_number INTEGER PRIMARY KEY,
            customer_key TEXT,
            date TEXT,
            items TEXT,
            total_amount REAL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
initialize_database()

class BillGenerator:
    def __init__(self, master):
        self.master = master
        master.title("Bill Generator")
        
        # Initialize bill number
        self.bill_number = self.get_current_bill_number()
        
        # Colors and fonts
        self.bg_color = "#e0f7fa"
        self.fg_color = "#004d40"
        self.font_style = ("Arial", 12)
        
        # Create main container
        self.main_container = tk.Frame(master, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Initialize items list
        self.items = []
        
        # Setup UI components
        self.setup_ui()
        
        # Bind the key press event to the autocomplete function for item name entry
        self.item_name_entry.bind("<KeyRelease>", self.autocomplete_item_name)

    def setup_ui(self):
        # Customer selection frame
        self.customer_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.customer_frame.pack(fill=tk.X, pady=5)
        
        self.customer_label = tk.Label(self.customer_frame, text="Select Customer:", 
                                     bg=self.bg_color, fg=self.fg_color, font=self.font_style)
        self.customer_label.pack(side=tk.LEFT)
        
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(self.customer_frame, textvariable=self.customer_var,
                                         values=list(customers.keys()), state="readonly")
        self.customer_combo.pack(side=tk.LEFT, padx=5)
        self.customer_combo.set(list(customers.keys())[0] if customers else "")
        
        # Date frame
        self.date_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.date_frame.pack(fill=tk.X, pady=5)
        
        self.date_label = tk.Label(self.date_frame, text="Date:", 
                                 bg=self.bg_color, fg=self.fg_color, font=self.font_style)
        self.date_label.pack(side=tk.LEFT)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%d-%m-%Y"))
        self.date_entry = tk.Entry(self.date_frame, textvariable=self.date_var, 
                                 width=10, font=self.font_style)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        # Item entry frame
        self.item_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.item_frame.pack(fill=tk.X, pady=5)
        
        # Item name with autocomplete
        self.item_name_label = tk.Label(self.item_frame, text="Item Name:", 
                                      bg=self.bg_color, fg=self.fg_color, font=self.font_style)
        self.item_name_label.pack(side=tk.LEFT)
        
        self.item_name_var = tk.StringVar()
        self.item_name_entry = tk.Entry(self.item_frame, textvariable=self.item_name_var, 
                                      width=30, font=self.font_style)
        self.item_name_entry.pack(side=tk.LEFT, padx=5)
        
        # Suggestion listbox
        self.suggestion_listbox = tk.Listbox(self.item_frame, width=40, height=5, 
                                           font=self.font_style)
        self.suggestion_listbox.pack(side=tk.LEFT, padx=5)
        self.suggestion_listbox.bind("<<ListboxSelect>>", self.insert_suggestion)
        
        # Price and quantity
        self.price_label = tk.Label(self.item_frame, text="Price:", 
                                  bg=self.bg_color, fg=self.fg_color, font=self.font_style)
        self.price_label.pack(side=tk.LEFT, padx=5)
        
        self.price_var = tk.DoubleVar()
        self.price_entry = tk.Entry(self.item_frame, textvariable=self.price_var, 
                                  width=10, font=self.font_style)
        self.price_entry.pack(side=tk.LEFT)
        
        self.quantity_label = tk.Label(self.item_frame, text="Quantity:", 
                                     bg=self.bg_color, fg=self.fg_color, font=self.font_style)
        self.quantity_label.pack(side=tk.LEFT, padx=5)
        
        self.quantity_var = tk.IntVar(value=1)
        self.quantity_entry = tk.Entry(self.item_frame, textvariable=self.quantity_var, 
                                     width=5, font=self.font_style)
        self.quantity_entry.pack(side=tk.LEFT)
        
        # Add item button
        self.add_button = tk.Button(self.item_frame, text="Add Item", 
                                  command=self.add_item, font=self.font_style,
                                  bg="#00796b", fg="white")
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        # Items list
        self.items_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.items_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.items_listbox = tk.Listbox(self.items_frame, width=80, height=15, 
                                      font=self.font_style)
        self.items_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for items list
        scrollbar = tk.Scrollbar(self.items_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.items_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.items_listbox.yview)
        
        # Total and buttons frame
        self.bottom_frame = tk.Frame(self.main_container, bg=self.bg_color)
        self.bottom_frame.pack(fill=tk.X, pady=5)
        
        self.total_label = tk.Label(self.bottom_frame, text="Total:", 
                                  bg=self.bg_color, fg=self.fg_color, font=self.font_style)
        self.total_label.pack(side=tk.LEFT)
        
        self.total_var = tk.StringVar(value="₹0.00")
        self.total_entry = tk.Entry(self.bottom_frame, textvariable=self.total_var, 
                                  state="readonly", width=10, font=self.font_style)
        self.total_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        self.generate_button = tk.Button(self.bottom_frame, text="Generate Bill", 
                                       command=self.generate_bill, font=self.font_style,
                                       bg="#00796b", fg="white")
        self.generate_button.pack(side=tk.RIGHT, padx=5)
        
        self.clear_button = tk.Button(self.bottom_frame, text="Clear", 
                                    command=self.clear_form, font=self.font_style,
                                    bg="#d32f2f", fg="white")
        self.clear_button.pack(side=tk.RIGHT, padx=5)
    
    def get_current_bill_number(self):
        try:
            with open(BILL_NUMBER_PATH, "r") as file:
                return int(file.read().strip())
        except (FileNotFoundError, ValueError):
            return 1
    
    def save_bill_number(self):
        with open(BILL_NUMBER_PATH, "w") as file:
            file.write(str(self.bill_number))

    def autocomplete_item_name(self, event):
        # Get the current text in the item name entry widget
        text = self.item_name_entry.get()

        # Find the best matching suggestions
        matches = [s for s in suggestions if fuzz.partial_ratio(s.lower(), text.lower()) >= 80]

        # Update the suggestion listbox with the suggestions
        self.suggestion_listbox.delete(0, tk.END)
        for match in matches:
            self.suggestion_listbox.insert(tk.END, match)

    def insert_suggestion(self, event):
        try:
            # Get the selected suggestion from the listbox
            selection = self.suggestion_listbox.get(self.suggestion_listbox.curselection())
            # Insert the selected suggestion into the item name entry widget
            self.item_name_entry.delete(0, tk.END)
            self.item_name_entry.insert(0, selection)
        except tk.TclError:
            # No item selected, do nothing
            pass

    def add_item(self):
        try:
            item_name = self.item_name_var.get()
            price = self.price_var.get()
            quantity = self.quantity_var.get()

            if not item_name or price <= 0 or quantity <= 0:
                messagebox.showerror("Error", "Please enter valid item details")
                return
            
            total = price * quantity
            item = {
                "name": item_name,
                "price": price,
                "quantity": quantity,
                "total": total
            }
        
            self.items.append(item)
            self.update_items_list()
            self.clear_item_entry()
            self.calculate_total()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def update_items_list(self):
        self.items_listbox.delete(0, tk.END)
        for item in self.items:
            self.items_listbox.insert(tk.END, 
                f"{item['name']} - ₹{item['price']:.2f} x {item['quantity']} = ₹{item['total']:.2f}")

    def clear_item_entry(self):
        self.item_name_var.set("")
        self.price_var.set(0.0)
        self.quantity_var.set(1)
        self.suggestion_listbox.delete(0, tk.END)

    def calculate_total(self):
        total = sum(item["total"] for item in self.items)
        self.total_var.set(f"₹{total:.2f}")

    
    def generate_html_bill(self):
        customer_key = self.customer_var.get()
        customer = customers[customer_key]
        # Use self.items directly
        item_rows = ""
        for index, item in enumerate(self.items):
            item_rows += f"""<tr>
            <td>{index + 1}</td>
            <td>{item['name']}</td>
            <td>{item['quantity']}</td>
            <td>₹{item['price']:.2f}</td>
            <td colspan="2">₹{item['total']:.2f}</td>
            </tr>"""
    
        html_content = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invoice</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            .invoice {{
                border: 1px solid red;
                padding: 20px;
                max-width: 800px;
                margin: auto;
            }}
            .invoice-header {{
                text-align: center;
                border:1px solid red;
                padding-bottom: 18px;
           }}
            .invoice-header img {{
                max-width: 100px;
            }}
            .invoice-header h1 {{
                margin: 0;
                color: red;
            }}
            .invoice-header p {{
                margin: 2px 0;
            }}
            .invoice-info {{
                display: flex;
                justify-content: space-between;
                margin-top: 10px;
            }}
            .invoice-info div {{
                width: 48%;
            }}
            .invoice-info .sales-to,
            .invoice-info .address {{
                margin-top: 20px;
            }}
            .invoice-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .invoice-table th, .invoice-table td {{
                border: 1px solid red;
                padding: 8px;
                text-align: left;
            }}
            .invoice-table th {{
                background-color: #f2f2f2;
            }}
            .invoice-total {{
                width: 100%;
                margin-top: 20px;
                text-align: right;
            }}
            .invoice-total table {{
                width: 50%;
                float: right;
                border-collapse: collapse;
            }}
            .invoice-total th, .invoice-total td {{
                border: 1px solid red;
                padding: 8px;
            }}
            .invoice-signature {{
                margin-top: 40px;
                text-align: right;
            }}
            #download-btn {{
            display: block;
            margin: 20px auto;
            padding: 10px 20px;
            background-color: red;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }}
        </style>
    </head>
    <body>
        <div class="invoice" id="invoice">
        <div class="invoice">
            <div class="invoice-header">
                <div style="position:absolute; border-color: red;">
                    <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/" alt="Logo">
                </div>
                <h1>SADHASIVA AGENCIES</h1>
                <p>4/53, Bhairavi Nagar, Puliyankulam,</p>
                <p>Inamreddiyapatti Post, Virudhunagar - 626 003.</p>
                <p>Cell: 88258 08813, 91596 84261</p>
            </div>
            <div class="invoice-info">
                <div>
                    <p>No. <strong>{self.bill_number}</strong></p>
                    <p class="sales-to">To: {customer["name"]}</p>
                    <p class="address">Address: {customer["address"]}</p>
                </div>
                <div>
                    <p>&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Date: {self.date_var.get()}</p>
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
                    {item_rows}
                </tbody>
            </table>
            <div class="invoice-total">
                <table>
                    <tr>
                        <th>TOTAL</th>
                        <td>Rs. {self.total_var.get()}</td>
                    </tr>
                    <tr>
                        <th>SGST % + CGST %</th>
                        <td>Rs. 0.00</td>
                    </tr>
                    <tr>
                        <th>GRAND TOTAL</th>
                        <td>Rs. {self.total_var.get()}</td>
                    </tr>
                </table>
            </div>
            <div class="invoice-signature">
                <p>For <strong>SADHASIVA AGENCIES</strong></p>
                <p>Signature</p>
            </div>
        </div>
        </div>
        <button id="download-btn">Download Invoice</button>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script>
        document.getElementById('download-btn').addEventListener('click', function() {{
            html2canvas(document.getElementById('invoice')).then(function(canvas) {{
                let link = document.createElement('a');
                link.href = canvas.toDataURL('image/png');
                link.download = 'invoice.png';
                link.click();
            }});
        }});
    </script>
    </body>
    </html>"""
        
        file_path = f"C:\\Users\\Sri Nithilan\\Desktop\\Experiment\\templates\\Template{self.bill_number}.html"
        with open(file_path, "w",encoding="utf-8") as file:
            file.write(html_content)
        webbrowser.open(file_path)

    def update_bill_number(self):
        try:
            with open(BILL_NUMBER_PATH, "r") as file:
                bill_number = int(file.read())

            with open(BILL_NUMBER_PATH, "w") as file:
                file.write(str(bill_number + 1))

            self.bill_number = bill_number + 1
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update bill number: {str(e)}")

    def generate_bill(self):
        if not self.items:
            messagebox.showerror("Error", "Please add items to the bill")
            return
        
        try:
            self.update_bill_number()
            self.save_bill_to_database()
            self.generate_html_bill()
            messagebox.showinfo("Success", "Bill generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
        
    def display_bill(self):
        customer_key = self.customer_var.get()
        customer = customers[customer_key]

        bill = f"Bill No:{self.bill_number}\nBill for {customer['name']}\n"
        bill += f"Address: {customer['address']}\n"
        bill += f"Date: {self.date_var.get()}\n"
        bill += "----------------------------------------\nItems:\n----------------------------------------\n"
        bill += "\n".join(self.items_listbox.get(0, tk.END))
        bill += f"\n----------------------------------------\nTotal Bill: {self.total_var.get()}"

        messagebox.showinfo("Bill", bill)

    def save_bill_to_database(self):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
        
            bill_data = {
            "bill_number": self.bill_number,
            "customer_key": self.customer_var.get(),
            "date": self.date_var.get(),
            "items": json.dumps(self.items),
            "total_amount": float(self.total_var.get().replace("₹", ""))
            }
        
            cursor.execute('''
            INSERT INTO bills (bill_number, customer_key, date, items, total_amount)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            bill_data["bill_number"],
            bill_data["customer_key"],
            bill_data["date"],
            bill_data["items"],
            bill_data["total_amount"]
        ))
        
            conn.commit()
            conn.close()
        
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def get_bill(self, bill_number):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bills WHERE bill_number = ?', (bill_number,))
            bill = cursor.fetchone()
            if bill:
                return {'bill': bill}
            return None
        finally:
            conn.close()

    def calculate_total_bill(self, bill_number=None, start_date=None, end_date=None):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            if bill_number:
                cursor.execute('SELECT total_amount FROM bills WHERE bill_number = ?', (bill_number,))
                result = cursor.fetchone()
                return result[0] if result else 0
            elif start_date and end_date:
                cursor.execute('''
                    SELECT SUM(total_amount) FROM bills 
                    WHERE date BETWEEN ? AND ?
                ''', (start_date, end_date))
                result = cursor.fetchone()
                return result[0] if result else 0
            else:
                return 0
        finally:
            conn.close()

    def clear_form(self):
        self.items = []
        self.update_items_list()
        self.clear_item_entry()
        self.total_var.set("₹0.00")
        self.date_var.set(datetime.now().strftime("%d-%m-%Y"))
        self.customer_combo.set(list(customers.keys())[0] if customers else "")
root = tk.Tk()
bill_generator = BillGenerator(root)
root.mainloop()