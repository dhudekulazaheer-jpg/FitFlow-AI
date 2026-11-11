import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load local .env file if present
load_dotenv(BASE_DIR / ".env")

# Detect cloud environment
IS_PRODUCTION = (
    os.getenv("RENDER") is not None
    or os.getenv("FLASK_ENV") == "production"
    or os.getenv("ENVIRONMENT") == "production"
)

# Secret Key Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ValueError("CRITICAL: SECRET_KEY environment variable must be set in production!")
    SECRET_KEY = "fitflow-ai-development-secret-key-change-in-production"

# Resilient Database Configuration (Aiven MySQL, Cloud DATABASE_URL, local MySQL, or SQLite fallback)
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

# Normalize URL prefixes
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure SQLAlchemy Engine & SSL options (crucial for Aiven MySQL)
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
}

# SSL Handling for Aiven MySQL
ssl_ca_path = os.getenv("AIVEN_CA_PATH") or os.getenv("MYSQL_SSL_CA")

# If CA cert is passed as raw text in environment variable (common in Render)
aiven_ca_cert_content = os.getenv("AIVEN_CA_CERT") or os.getenv("MYSQL_SSL_CA_CERT")
if aiven_ca_cert_content and not ssl_ca_path:
    ca_file = BASE_DIR / "aiven_ca.pem"
    try:
        with open(ca_file, "w", encoding="utf-8") as f:
            f.write(aiven_ca_cert_content.strip())
        ssl_ca_path = str(ca_file)
    except Exception as e:
        print(f"Warning: Could not write runtime CA certificate file: {e}")

if "mysql" in DATABASE_URL.lower():
    connect_args = {}
    if ssl_ca_path and os.path.exists(ssl_ca_path):
        connect_args["ssl"] = {"ca": ssl_ca_path, "check_hostname": True}
    elif "aivencloud" in DATABASE_URL.lower():
        # Aiven requires SSL mode
        connect_args["ssl"] = {"ssl_mode": "REQUIRED"}
    if connect_args:
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = connect_args

# HTTPS Session Cookie Hardening
SESSION_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
REMEMBER_COOKIE_SECURE = IS_PRODUCTION
REMEMBER_COOKIE_HTTPONLY = True

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


# Generative AI / RAG LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
