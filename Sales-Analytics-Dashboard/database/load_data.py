import pandas as pd
from database.database import get_engine
from utils.helpers import load_csv_data
from config.logging_config import logger

def load_to_mysql():
    logger.info("Loading processed data to MySQL...")
    try:
        df = load_csv_data("processed_sales.csv", "processed")
    except FileNotFoundError:
        logger.error("Processed data not found. Run feature_engineering.py first.")
        return

    engine = get_engine()
    if engine is None:
        logger.error("Cannot connect to database. Ensure MySQL is running and credentials in .env are correct.")
        return

    try:
        df.to_sql("sales", con=engine, if_exists="replace", index=False)
        logger.info(f"Successfully loaded {len(df)} records into the 'sales' table.")
    except Exception as e:
        logger.error(f"Failed to load data to MySQL: {e}")

if __name__ == "__main__":
    load_to_mysql()
