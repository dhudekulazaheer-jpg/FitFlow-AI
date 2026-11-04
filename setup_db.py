import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Import the configured Flask app and SQLAlchemy db
from app import app
from models import db


def init_database():
    """
    Initializes all SQLAlchemy database tables non-destructively
    in the configured database (e.g. Aiven MySQL defaultdb or local MySQL).
    Does NOT attempt to run 'CREATE DATABASE', which fails under Aiven's managed user privileges.
    """
    print("=" * 60)
    print("FITFLOW AI - DATABASE TABLE INITIALIZATION")
    print("=" * 60)

    with app.app_context():
        try:
            print("Connecting to database and verifying schema...")
            db.create_all()
            print("✓ All database tables successfully initialized and verified!")
            print("✓ Existing records (if any) are completely preserved.")
            return True
        except Exception as err:
            print(f"❌ Database initialization failed: {err}")
            return False


if __name__ == "__main__":
    success = init_database()
    if not success:
        sys.exit(1)
