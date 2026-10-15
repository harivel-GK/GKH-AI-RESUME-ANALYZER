import os
from openai import OpenAI
from utils.helpers import load_csv_data
from config.settings import OPENAI_API_KEY
from config.logging_config import logger

def generate_insights():
    logger.info("Generating AI Insights...")
    try:
        df = load_csv_data("processed_sales.csv", "processed")
    except FileNotFoundError:
        logger.error("Processed data not found.")
        return None

    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key":
        logger.warning("OpenAI API Key is missing or default. Skipping AI insights generation.")
        return "API Key not configured. Please set OPENAI_API_KEY in .env."

    client = OpenAI(api_key=OPENAI_API_KEY)
    
    total_rev = df["Revenue"].sum()
    top_region = df.groupby("Region")["Revenue"].sum().idxmax()
    top_product = df.groupby("Product")["Revenue"].sum().idxmax()
    
    prompt = f"""
    You are an expert Data Analyst. I have a sales dataset with the following summary:
    - Total Revenue: 
    - Top Performing Region: {top_region}
    - Top Selling Product: {top_product}
    
    Based on this data, provide a 3-paragraph executive summary and 3 bullet-point recommendations for the business.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        insight = response.choices[0].message.content
        logger.info("Successfully generated AI insights.")
        return insight
    except Exception as e:
        logger.error(f"Failed to generate insights via OpenAI API: {e}")
        return f"Error: {e}"

if __name__ == "__main__":
    print(generate_insights())
