import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.helpers import load_csv_data
from config.settings import REPORTS_DIR
from config.logging_config import logger

def run_eda():
    logger.info("Starting Exploratory Data Analysis...")
    try:
        df = load_csv_data("processed_sales.csv", "processed")
    except FileNotFoundError:
        logger.error("Processed data not found.")
        return

    sns.set_theme(style="whitegrid")
    
    # 1. Revenue by Region
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="Region", y="Revenue", estimator=sum, ci=None)
    plt.title("Total Revenue by Region")
    plt.savefig(REPORTS_DIR / "revenue_by_region.png")
    plt.close()

    # 2. Monthly Trend
    monthly_sales = df.groupby(["Year", "Month"])["Revenue"].sum().reset_index()
    monthly_sales["DateStr"] = monthly_sales["Year"].astype(str) + "-" + monthly_sales["Month"].astype(str)
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_sales, x="DateStr", y="Revenue", marker="o")
    plt.xticks(rotation=45)
    plt.title("Monthly Revenue Trend")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "monthly_revenue_trend.png")
    plt.close()

    # 3. Correlation Heatmap
    plt.figure(figsize=(8, 6))
    numeric_cols = df.select_dtypes(include=["float64", "int64", "int32"]).columns
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "correlation_heatmap.png")
    plt.close()

    logger.info(f"EDA complete. Visualizations saved to {REPORTS_DIR}")

if __name__ == "__main__":
    run_eda()
