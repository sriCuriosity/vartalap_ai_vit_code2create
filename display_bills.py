import sqlite3

def truncate_all_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            print(f"Truncating table: {table_name}")
            cursor.execute(f"select * from {table_name}")
        conn.commit()
        print("All tables truncated successfully.")
    except Exception as e:
        print(f"Error truncating tables: {e}")
    finally:
        conn.close()

def display_all_records(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Run migration queries every time
    try:
        cursor.execute("ALTER TABLE bills ADD COLUMN transaction_type TEXT DEFAULT 'debit';")
    except sqlite3.OperationalError:
        # Column probably already exists
        pass
    try:
        cursor.execute("ALTER TABLE bills ADD COLUMN remarks TEXT;")
    except sqlite3.OperationalError:
        # Column probably already exists
        pass
    conn.commit()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        print(f"Records from table: {table_name}")
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Print table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        structure_info = cursor.fetchall()
        print("Table structure:")
        for col in structure_info:
            print(f"Column: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, Default: {col[4]}, PK: {col[5]}")

if __name__ == "__main__":
    db_path = "bills.db"
    # Uncomment the line below to truncate all tables in the database
    #truncate_all_tables(db_path)
    #display_all_records(db_path)
    