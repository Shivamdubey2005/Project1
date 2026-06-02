
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

# ==========================================
# Paths and Logging Configuration
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / 'sales.csv'
LOG_PATH = BASE_DIR / 'etl.log'
DB_PATH = BASE_DIR / 'warehouse.db'

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ==========================================
# Extract Function
# ==========================================

def extract_data():
    try:
        logging.info("Starting data extraction")

        data = pd.read_csv(CSV_PATH)

        logging.info("Data extraction successful")

        return data

    except Exception as e:
        logging.error(f"Extraction Error: {e}")
        raise


# ==========================================
# Transform Function
# ==========================================

def transform_data(data):
    try:
        logging.info("Starting data transformation")

        # Remove duplicates
        data.drop_duplicates(inplace=True)

        # Fill missing amount values and convert to float safely
        data['amount'] = pd.to_numeric(data['amount'], errors='coerce').fillna(0.0)

        # Add GST column
        data['gst_amount'] = data['amount'] * 0.18

        # Add total amount
        data['total_amount'] = data['amount'] + data['gst_amount']

        # Convert date format
        data['date'] = pd.to_datetime(data['date'], errors='coerce')

        # Add ETL timestamp
        loaded_at = datetime.now()
        data['etl_loaded_at'] = loaded_at

        logging.info("Data transformation completed")

        return data

    except Exception as e:
        logging.error(f"Transformation Error: {e}")
        raise


# ==========================================
# Load Function
# ==========================================

def load_data(data):
    try:
        logging.info("Starting data loading")

        # SQLite Data Warehouse
        engine = create_engine(f"sqlite:///{DB_PATH.resolve().as_posix()}")

        # Load data into warehouse table
        data.to_sql(
            'sales_warehouse',
            con=engine,
            if_exists='replace',
            index=False
        )

        logging.info("Data loading completed successfully")

    except Exception as e:
        logging.error(f"Loading Error: {e}")
        raise


# ==========================================
# Synchronizer Function
# ==========================================

def synchronize_pipeline():
    try:
        logging.info("ETL Pipeline Started")

        # Extract
        raw_data = extract_data()

        print("\n===== Extracted Data =====")
        print(raw_data)

        # Transform
        transformed_data = transform_data(raw_data)

        print("\n===== Transformed Data =====")
        print(transformed_data)

        # Load
        load_data(transformed_data)

        print("\nData loaded into warehouse successfully")

        logging.info("ETL Pipeline Completed Successfully")

    except Exception as e:
        logging.error(f"Pipeline Error: {e}")
        print(f"Pipeline Failed: {e}")


# ==========================================
# Main Execution
# ==========================================

if __name__ == '__main__':
    synchronize_pipeline()


