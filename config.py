import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "your-db-host"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "your-db-user"),
    "password": os.getenv("DB_PASSWORD", "your-db-password"),
    "dbname": os.getenv("DB_NAME", "your-db-name"),
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key")
MODEL_NAME = "gemini-2.0-flash"