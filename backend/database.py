import sqlite3
from contextlib import contextmanager
import os

# Get the current directory where database.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.path.join(BASE_DIR, "quiz_database_cleaned.sqlite3")

@contextmanager
def get_db():
    print(f"Attempting to connect to database at: {DATABASE_URL}")  # Debug log
    try:
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        print("Database connection successful")  # Debug log
        yield conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")  # Debug log
        raise
    finally:
        print("Closing database connection")  # Debug log
        conn.close()