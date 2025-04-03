import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect("smart_sales.db")  # Replace with your actual database path
cursor = conn.cursor()

# Execute PRAGMA command to check the table schema
cursor.execute("PRAGMA table_info(customer);")
columns = cursor.fetchall()

# Print column details
for column in columns:
    print(column)

conn.close()
