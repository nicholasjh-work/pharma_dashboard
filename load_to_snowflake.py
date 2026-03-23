"""
Load CSV data into Snowflake using snowflake-connector-python.
Usage:
    cp .env.example .env
    pip install -r requirements.txt
    python load_to_snowflake.py
"""
import logging
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
load_dotenv()

SNOWFLAKE_ACCOUNT = os.environ["SNOWFLAKE_ACCOUNT"]
SNOWFLAKE_USER = os.environ["SNOWFLAKE_USER"]
SNOWFLAKE_PASSWORD = os.environ["SNOWFLAKE_PASSWORD"]
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "PHARMA_ANALYTICS")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "RAW")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "PHARMA_WH")
DATA_DIR = Path(__file__).parent / "data"

TABLES = [
    ("dim_patients", "dim_patients.csv"),
    ("dim_payers", "dim_payers.csv"),
    ("dim_pharmacies", "dim_pharmacies.csv"),
    ("dim_drugs", "dim_drugs.csv"),
    ("dim_dates", "dim_dates.csv"),
    ("fact_rx_fills", "fact_rx_fills.csv"),
    ("fact_shipments", "fact_shipments.csv"),
]
SKIP_COLUMNS = {"fact_shipments": ["shipment_id"]}

def load_table(conn, table_name, csv_file):
    filepath = DATA_DIR / csv_file
    if not filepath.exists():
        raise FileNotFoundError(f"Missing: {filepath}")
    df = pd.read_csv(filepath)
    skip = SKIP_COLUMNS.get(table_name, [])
    for col in skip:
        if col in df.columns:
            df = df.drop(columns=[col])
    df.columns = [c.upper() for c in df.columns]
    logger.info(f"Loading {table_name}: {len(df)} rows")
    success, num_chunks, num_rows, _ = write_pandas(conn, df, table_name.upper(), auto_create_table=False, overwrite=True)
    if not success:
        raise RuntimeError(f"Failed to load {table_name}")
    logger.info(f"  {table_name}: {num_rows} rows loaded")
    return num_rows

def validate_counts(conn):
    expected = {"DIM_PATIENTS": 500, "DIM_PAYERS": 5, "DIM_PHARMACIES": 10, "DIM_DRUGS": 5, "DIM_DATES": 731, "FACT_RX_FILLS": 3000, "FACT_SHIPMENTS": 240}
    cursor = conn.cursor()
    for table, exp in expected.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        actual = cursor.fetchone()[0]
        status = "OK" if actual == exp else "MISMATCH"
        logger.info(f"  {table}: {actual} (expected {exp}) [{status}]")

def main():
    conn = connect(account=SNOWFLAKE_ACCOUNT, user=SNOWFLAKE_USER, password=SNOWFLAKE_PASSWORD, database=SNOWFLAKE_DATABASE, schema=SNOWFLAKE_SCHEMA, warehouse=SNOWFLAKE_WAREHOUSE)
    try:
        conn.cursor().execute(f"CREATE SCHEMA IF NOT EXISTS {SNOWFLAKE_SCHEMA}")
        conn.cursor().execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            for stmt in schema_path.read_text().split(";"):
                stmt = stmt.strip()
                if stmt and not stmt.startswith("--"):
                    conn.cursor().execute(stmt)
        total = 0
        for table_name, csv_file in TABLES:
            total += load_table(conn, table_name, csv_file)
        logger.info(f"Total rows loaded: {total}")
        validate_counts(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
