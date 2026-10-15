import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"

for d in [RAW_DATA_DIR, CLEANED_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "sales_analytics")
DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
