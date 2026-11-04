import os
import pymysql
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/fitflow_ai")

try:
    prefix, rest = database_url.split("://", 1)
    auth, host_db = rest.split("@", 1)
    username, password = auth.split(":", 1) if ":" in auth else (auth, "")
    username = unquote(username)
    password = unquote(password)
    host_port, dbname = host_db.split("/", 1)
    host, port = host_port.split(":", 1) if ":" in host_port else (host_port, 3306)
    port = int(port)
except Exception as e:
    print(f"Error parsing DATABASE_URL: {e}")
    username, password, host, port, dbname = "root", "", "localhost", 3306, "fitflow_ai"

print(f"Connecting to MySQL at {host}:{port} with user '{username}'...")

try:
    conn = pymysql.connect(
        host=host,
        user=username,
        password=password,
        port=port,
        charset="utf8mb4"
    )
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database `{dbname}` is ready!")
    conn.close()

    # Create tables using SQLAlchemy
    from app import app
    from models import db

    with app.app_context():
        db.create_all()
        print("All database tables created successfully!")

except Exception as err:
    print(f"Failed to setup database: {err}")
