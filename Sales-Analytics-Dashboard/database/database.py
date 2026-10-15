from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URI
from config.logging_config import logger

def get_engine():
    try:
        engine = create_engine(DATABASE_URI)
        logger.info("Database engine created successfully.")
        return engine
    except Exception as e:
        logger.error(f"Error creating database engine: {e}")
        return None

def get_session():
    engine = get_engine()
    if engine:
        Session = sessionmaker(bind=engine)
        return Session()
    return None
