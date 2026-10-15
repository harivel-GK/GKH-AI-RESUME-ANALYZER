import pandas as pd
from utils.helpers import load_csv_data, save_csv_data
from config.logging_config import logger

def engineer_features():
    logger.info("Starting feature engineering...")
    try:
        df = load_csv_data("cleaned_sales.csv", "cleaned")
    except FileNotFoundError:
        logger.error("Cleaned data not found. Run clean_data.py first.")
        return

    # Create new features
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"] * (1 - df["Discount"])
    df["Year"] = df["OrderDate"].dt.year
    df["Month"] = df["OrderDate"].dt.month
    df["DayOfWeek"] = df["OrderDate"].dt.dayofweek
    df["IsWeekend"] = df["DayOfWeek"].isin([5, 6]).astype(int)

    save_csv_data(df, "processed_sales.csv", "processed")
    logger.info("Feature engineering complete. Saved to processed folder.")

if __name__ == "__main__":
    engineer_features()
