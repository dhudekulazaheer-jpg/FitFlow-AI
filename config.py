import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "fitflow-ai-development-secret-key-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/fitflow_ai")

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
