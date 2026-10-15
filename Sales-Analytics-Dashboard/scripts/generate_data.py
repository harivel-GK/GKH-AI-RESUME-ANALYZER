import pandas as pd
import numpy as np
from config.settings import RAW_DATA_DIR
from config.logging_config import logger

def generate_sales_data(num_records=5000):
    logger.info("Generating dummy sales data...")
    np.random.seed(42)
    dates = pd.date_range(start="2022-01-01", end="2023-12-31", periods=num_records)
    products = ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard", "Mouse"]
    regions = ["North", "South", "East", "West"]
    
    data = {
        "OrderID": np.arange(1, num_records + 1),
        "OrderDate": np.random.choice(dates, num_records),
        "Product": np.random.choice(products, num_records),
        "Region": np.random.choice(regions, num_records),
        "Quantity": np.random.randint(1, 10, num_records),
        "UnitPrice": np.random.uniform(10.0, 1500.0, num_records),
        "Discount": np.random.choice([0.0, 0.05, 0.1, 0.15, 0.2], num_records, p=[0.5, 0.2, 0.15, 0.1, 0.05]),
        "CustomerID": np.random.randint(100, 500, num_records)
    }
    
    df = pd.DataFrame(data)
    
    # Inject some dirty data
    df.loc[df.sample(frac=0.05).index, 'Quantity'] = np.nan
    df.loc[df.sample(frac=0.02).index, 'UnitPrice'] = -50.0 # invalid price
    
    output_path = RAW_DATA_DIR / "raw_sales.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Raw data generated at {output_path}")

if __name__ == "__main__":
    generate_sales_data()
