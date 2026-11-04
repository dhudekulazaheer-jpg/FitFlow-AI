import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "fitflow-ai-development-secret-key-change-in-production")

# Resilient Database Configuration (Cloud DATABASE_URL, local MySQL, or SQLite fallback)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "fitflow_ai")
    if db_user:
        DATABASE_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    else:
        DATABASE_URL = f"sqlite:///{BASE_DIR / 'fitflow_ai.db'}"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

DATASET_DIR = BASE_DIR / "datasets"
YOGA_DIR = DATASET_DIR / "yoga"
WORKOUT_DIR = DATASET_DIR / "workout"

YOGA_FILE = YOGA_DIR / "yoga.json"
EXERCISEDB_FILE = WORKOUT_DIR / "exercises.json"
GYM_MEMBERS_FILE = WORKOUT_DIR / "gym_members_exercise.csv"

PROCESSED_DIR = DATASET_DIR / "processed"

CLEANED_YOGA_FILE = PROCESSED_DIR / "yoga_cleaned.csv"
CLEANED_WORKOUT_FILE = PROCESSED_DIR / "workout_cleaned.csv"
CLEANED_GYM_FILE = PROCESSED_DIR / "gym_members_cleaned.csv"
DUPLICATE_REPORT_FILE = PROCESSED_DIR / "duplicate_candidates.csv"

MODEL_DIR = BASE_DIR / "models"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
