import pandas as pd
import sqlite3
import pathlib
import sys

# For local imports, temporarily add project root to sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Constants
DW_DIR = pathlib.Path("data").joinpath("dw")
DB_PATH = DW_DIR.joinpath("smart_sales.db")
PREPARED_DATA_DIR = pathlib.Path("data").joinpath("prepared")

def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create tables in the data warehouse if they don't exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,
            join_date TEXT
            loyaltypoints INTEGER,
            demographic TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            unit_price INTEGER,
            stockquantity INTEGER,
            storesection TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale (
            transaction_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            storeid INTEGER,
            campaignid INTEGER,
            sales_amount REAL,
            sale_date TEXT,
            discountpercent INTEGER,
            paymenttype TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
            FOREIGN KEY (product_id) REFERENCES product (product_id)
        )
    """)

def delete_existing_records(cursor: sqlite3.Cursor) -> None:
    """Delete all existing records from the customer, product, and sale tables."""
    cursor.execute("DELETE FROM customer")
    cursor.execute("DELETE FROM product")
    cursor.execute("DELETE FROM sale")

def insert_customers(customers_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert customer data into the customer table."""
    customers_df = customers_df.drop(columns=["LoyaltyPoints"], errors="ignore")
    customers_df = customers_df.rename(columns={
        "CustomerID": "customer_id",
        "Name": "name",
        "Region": "region",
        "JoinDate": "join_date",
        "LoyaltyPoints": "loyalty_points",
        "Demographic": "demographic"
    })
    customers_df.rename(columns={"loyalty_points": "LoyaltyPoints"}, inplace=True)
    customers_df.to_sql("customer", cursor.connection, if_exists="append", index=False)
    print("Customer data inserted successfully!")

def insert_products(products_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert product data into the product table."""
    products_df.rename(columns={"id": "productid"}, inplace=True)
    products_df.rename(columns={"id": "unitprice"}, inplace=True)
    products_df = products_df.rename(columns={
        "productid": "product_id",
        "productname": "product_name",
        "category": "category",
        "unitprice": "unitprice",
        "stockquantity": "stockquantity",
        "storesection": "storesection"
    })
    products_df.to_sql("product", cursor.connection, if_exists="append", index=False)
    print("Product data inserted successfully!")

def insert_sales(sales_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert sales data into the sale table."""

    print("Sales DataFrame columns before rename:", sales_df.columns.tolist())

    # Rename columns to match the SQL schema
    sales_df.rename(columns={
        "transaction_id": "transactionid",  # Rename 'transaction_id' to 'transactionid'
        "SaleDate": "saledate",  # Rename 'SaleDate' to 'saledate' if it's in the DataFrame
        "customerid": "customerid",
        "productid": "productid",
        "saleamount": "saleamount",
        "storeid": "storeid",
        "campaignid": "campaignid",
        "discountpercent": "discountpercent",
        "paymenttype": "paymenttype"
    }, inplace=True)

    # Check for missing columns after renaming
    expected_columns = [
        "transactionid", "saledate", "customerid", "productid",
        "storeid", "campaignid", "saleamount", "discountpercent", "paymenttype"
    ]
    missing_cols = set(expected_columns) - set(sales_df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Insert the sales data into the 'sale' table
    sales_df.to_sql("sale", cursor.connection, if_exists="append", index=False)
    print("Sales data inserted successfully!")



def load_data_to_db(smart_sales) -> None:
    try:
        # Connect to SQLite – will create the file if it doesn't exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create schema and clear existing records
        create_schema(cursor)
        delete_existing_records(cursor)

        # Load prepared data using pandas
        customers_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("customers_data_prepared.csv"))
        products_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("products_data_prepared.csv"))
        sales_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("sales_data_prepared.csv"))

        # Insert data into the database
        insert_customers(customers_df, cursor)
        insert_products(products_df, cursor)
        insert_sales(sales_df, cursor)

        conn.commit()
    finally:
        if conn:
            conn.close()

        #cursor.execute("PRAGMA table_info(customer);")
        #columns = cursor.fetchall()
        #print("SQLite Table Columns:", columns)


if __name__ == "__main__":
        load_data_to_db("smart_sales.db")