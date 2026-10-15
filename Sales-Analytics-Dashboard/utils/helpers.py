import pandas as pd
from config.logging_config import logger
from config.settings import RAW_DATA_DIR, CLEANED_DATA_DIR, PROCESSED_DATA_DIR

def get_data_dir(folder):
    if folder == "raw": return RAW_DATA_DIR
    elif folder == "cleaned": return CLEANED_DATA_DIR
    elif folder == "processed": return PROCESSED_DATA_DIR
    raise ValueError("Invalid folder")

def load_csv_data(file_name, folder="raw"):
    file_path = get_data_dir(folder) / file_name
    logger.info(f"Loading data from {file_path}")
    return pd.read_csv(file_path)

def save_csv_data(df, file_name, folder="cleaned"):
    file_path = get_data_dir(folder) / file_name
    df.to_csv(file_path, index=False)
    logger.info(f"Data saved to {file_path}")
