print(cursor.connection)

print(customers_df.columns)  # Check DataFrame columns

cursor.execute("PRAGMA table_info(customer);")
columns = cursor.fetchall()
print("SQLite Table Columns:", columns)  # Check database table columns
