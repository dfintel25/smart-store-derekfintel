import pandas as pd
import sqlite3
import pathlib
import sys

# For local imports, temporarily add project root to Python sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from utils.logger import logger  # noqa: E402

# Constants
DW_DIR: pathlib.Path = pathlib.Path("data").joinpath("dw")
DB_PATH: pathlib.Path = DW_DIR.joinpath("smart_sales.db")
OLAP_OUTPUT_DIR: pathlib.Path = pathlib.Path("data").joinpath("olap_cubing_outputs")

# Create output directory if it does not exist
OLAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ingest_sales_data_from_dw() -> pd.DataFrame:
    """Ingest sales data from SQLite data warehouse."""
    try:
        conn = sqlite3.connect(DB_PATH)
        sales_df = pd.read_sql_query("SELECT * FROM sale", conn)
        conn.close()
        logger.info("Sales data successfully loaded from SQLite data warehouse.")
        return sales_df
    except Exception as e:
        logger.error(f"Error loading sale table data from data warehouse: {e}")
        raise

def ingest_customer_data_from_dw() -> pd.DataFrame:
    """Ingest customer data from SQLite data warehouse."""
    try:
        conn = sqlite3.connect(DB_PATH)
        customer_df = pd.read_sql_query("SELECT * FROM customer", conn)
        conn.close()
        logger.info("Customer data successfully loaded from SQLite data warehouse.")
        return customer_df
    except Exception as e:
        logger.error(f"Error loading customer table data from data warehouse: {e}")
        raise

def ingest_product_data_from_dw() -> pd.DataFrame:
    """Ingest product data from SQLite data warehouse."""
    try:
        conn = sqlite3.connect(DB_PATH)
        product_df = pd.read_sql_query("SELECT * FROM product", conn)
        conn.close()
        logger.info("Product data successfully loaded from SQLite data warehouse.")
        return product_df
    except Exception as e:
        logger.error(f"Error loading product table data from data warehouse: {e}")
        raise


def create_olap_cube(
    sales_df: pd.DataFrame, dimensions: list, metrics: dict
) -> pd.DataFrame:
    try:
        grouped = sales_df.groupby(dimensions)
        cube = grouped.agg(metrics).reset_index()

        # Flatten column names if it's a MultiIndex
        if isinstance(cube.columns, pd.MultiIndex):
            cube.columns = ['_'.join(col).strip('_') for col in cube.columns]

        # Add transaction_id list column BEFORE the length check
        cube["transaction_id"] = grouped["transaction_id"].apply(list).reset_index(drop=True)

        # Generate explicit column names
        explicit_columns = generate_column_names(dimensions, metrics)
        explicit_columns.append("transaction_id")  # Always add it manually

        # Check length match before assigning
        if len(cube.columns) != len(explicit_columns):
            logger.error(f"Column length mismatch: cube has {len(cube.columns)}, expected {len(explicit_columns)}")
            raise ValueError("Mismatch between actual and expected column names.")

        cube.columns = explicit_columns

        return cube

    except Exception as e:
        logger.error(f"Error during OLAP cube creation: {e}")
        raise



def generate_column_names(dimensions: list, metrics: dict) -> list:
    """
    Generate explicit column names for OLAP cube, ensuring no trailing underscores.
    
    Args:
        dimensions (list): List of dimension columns.
        metrics (dict): Dictionary of metrics with aggregation functions.
        
    Returns:
        list: Explicit column names.
    """
    # Start with dimensions
    column_names = dimensions.copy()
    
    # Add metrics with their aggregation suffixes
    for column, agg_funcs in metrics.items():
        if isinstance(agg_funcs, list):
            for func in agg_funcs:
                column_names.append(f"{column}_{func}")
        else:
            column_names.append(f"{column}_{agg_funcs}")
    
    # Remove trailing underscores from all column names
    column_names = [col.rstrip("_") for col in column_names]
    
    return column_names
    

def write_cube_to_csv(cube: pd.DataFrame, filename: str) -> None:
    """Write the OLAP cube to a CSV file."""
    try:
        output_path = OLAP_OUTPUT_DIR.joinpath(filename)
        cube.to_csv(output_path, index=False)
        logger.info(f"OLAP cube saved to {output_path}.")
    except Exception as e:
        logger.error(f"Error saving OLAP cube to CSV file: {e}")
        raise

def main():
    """Main function for OLAP cubing."""
    logger.info("Starting OLAP Cubing process...")

    # Step 1: Ingest data
    sales_df = ingest_sales_data_from_dw()
    customer_df = ingest_customer_data_from_dw()
    product_df = ingest_product_data_from_dw()
    
    # Step 2: Enrich sales data with customer info
    sales_df = sales_df.merge(customer_df, on="customer_id", how="left")
    sales_df = sales_df.merge(product_df, on="product_id", how="left")

    # Step 3: Add time-based dimensions
    sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
    sales_df["DayOfWeek"] = sales_df["sale_date"].dt.day_name()
    sales_df["Month"] = sales_df["sale_date"].dt.month
    sales_df["Year"] = sales_df["sale_date"].dt.year

    # Step 4: Define cube structure
    dimensions = ["sale_date", "DayOfWeek", "product_id", "customer_id", "region", "category"]
    metrics = {
        "sale_amount": ["sum", "mean"],
        "transaction_id": "count",
    }

    # Step 5: Create cube
    olap_cube = create_olap_cube(sales_df, dimensions, metrics)

    # Step 6: Output cube
    write_cube_to_csv(olap_cube, "multidimensional_olap_cube.csv")

    logger.info("OLAP Cubing process completed successfully.")
    logger.info(f"Please see outputs in {OLAP_OUTPUT_DIR}")

if __name__ == "__main__":
    main()