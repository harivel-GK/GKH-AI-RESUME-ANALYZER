import pandas as pd
import numpy as np
from utils.helpers import load_csv_data, save_csv_data
from config.logging_config import logger

def clean_data():
    logger.info("Starting data cleaning process...")
    try:
        df = load_csv_data("raw_sales.csv", "raw")
    except FileNotFoundError:
        logger.error("Raw data not found. Please run generate_data.py first.")
        return None

    # Remove duplicates
    initial_shape = df.shape
    df.drop_duplicates(inplace=True)
    logger.info(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows.")

    # Handle Missing Values
    df["Quantity"] = df["Quantity"].fillna(df["Quantity"].median())
    
    # Correct Data Types
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    df["Quantity"] = df["Quantity"].astype(int)
    
    # Fix Invalid Data
    df.loc[df["UnitPrice"] < 0, "UnitPrice"] = df["UnitPrice"].median()

    save_csv_data(df, "cleaned_sales.csv", "cleaned")
    logger.info("Data cleaning complete.")
    return df

if __name__ == "__main__":
    clean_data()
