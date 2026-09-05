import pandas as pd
import pyodbc
import numpy as np
import os
import sys

# ==========================================
# Configuration & Setup
# ==========================================
# Database Connection Parameters
SERVER = r'localhost\TEW_SQLExpress'
DATABASE = 'Zomato_Product_Analytics'

# Try to use the best available ODBC Driver
DRIVER = '{ODBC Driver 17 for SQL Server}'  # Adjust if using Driver 18 or SQL Server Native Client

CONNECTION_STRING = (
    f"DRIVER={DRIVER};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

# Resolve paths relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')

# Define import order to maintain Foreign Key integrity, 
# along with target table names and display names.
IMPORT_PLAN = [
    {"file": "customers.csv", "table": "dbo.Customers", "display": "Customers"},
    {"file": "restaurants.csv", "table": "dbo.Restaurants", "display": "Restaurants"},
    {"file": "delivery_partners.csv", "table": "dbo.Delivery_Partners", "display": "Delivery Partners"},
    {"file": "orders.csv", "table": "dbo.Orders", "display": "Orders"},
    {"file": "payments.csv", "table": "dbo.Payments", "display": "Payments"},
    {"file": "reviews.csv", "table": "dbo.Reviews", "display": "Reviews"}
]

# ==========================================
# Helper Functions
# ==========================================
def get_db_connection() -> pyodbc.Connection:
    """Establishes and returns a pyodbc connection to SQL Server."""
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn
    except pyodbc.Error as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def build_insert_query(table_name: str, columns: list) -> str:
    """Dynamically builds a parameterized INSERT statement."""
    cols_formatted = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))
    query = f"INSERT INTO {table_name} ({cols_formatted}) VALUES ({placeholders})"
    return query

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataframe for SQL Server ingestion.
    - Converts pandas NaNs to Python None (which pyodbc maps to SQL NULL).
    - Converts booleans to integers (1/0) for SQL Server BIT columns.
    """
    # Convert booleans to ints (True -> 1, False -> 0)
    for col in df.select_dtypes(include=['bool']).columns:
        df[col] = df[col].astype(int)
        
    # Replace NaN/NaT with None for pyodbc compatibility
    df = df.replace({np.nan: None})
    return df

# ==========================================
# Main Execution
# ==========================================
def main():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable fast_executemany for high-performance batch inserts
    cursor.fast_executemany = True

    try:
        for plan in IMPORT_PLAN:
            file_path = os.path.join(DATA_DIR, plan["file"])
            table_name = plan["table"]
            display_name = plan["display"]

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Missing file: {file_path}")

            # Read the CSV
            df = pd.read_csv(file_path)
            
            # Clean data (handle NaNs and Bools)
            df = clean_dataframe(df)

            # Build query
            columns = df.columns.tolist()
            insert_query = build_insert_query(table_name, columns)

            # Convert DataFrame rows to a list of tuples for executemany
            data_to_insert = [tuple(row) for row in df.itertuples(index=False, name=None)]

            # Execute batch insert
            cursor.executemany(insert_query, data_to_insert)
            
            # Commit transaction for this table
            conn.commit()
            
            print(f"{display_name} Imported ✓")

        # Success message matching exact requirements
        print("\n" + "="*40)
        print("ALL DATA IMPORTED SUCCESSFULLY")
        print("="*40 + "\n")

    except pyodbc.Error as e:
        conn.rollback()
        print(f"\n❌ SQL Error occurred while processing {plan['file']}:")
        print(str(e))
        print("Transaction rolled back.")
        sys.exit(1)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Unexpected Error while processing {plan['file']}:")
        print(str(e))
        print("Transaction rolled back.")
        sys.exit(1)
        
    finally:
        # Ensure resources are cleaned up
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()