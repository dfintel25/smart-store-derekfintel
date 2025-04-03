import sqlite3

# Replace with the actual path to your database file
db_path = "c:/Projects/smart-store-derekfintel/smart_sales.db"  

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customer';")
    table_exists = cursor.fetchone()

    if not table_exists:
        print("Error: The 'customer' table does not exist.")
    else:
        # Fetch and print table schema
        cursor.execute("PRAGMA table_info(customer);")
        columns = cursor.fetchall()

        print("\nExisting columns in 'customer' table:")
        for column in columns:
            print(column)

    conn.close()
except sqlite3.Error as e:
    print("SQLite error:", e)
