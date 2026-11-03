
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

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
