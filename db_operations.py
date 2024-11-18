import sqlite3
from dbcm import DBCM

class DBOperations:
    def __init__(self, db_name="weather_data.db"):
        self.db_name = db_name

    def initialize_db(self):
        """Initialize the DB if it doesn't exist."""
        with DBCM(self.db_name) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sample_date TEXT,
                    location TEXT,
                    min_temp REAL,
                    max_temp REAL,
                    avg_temp REAL,
                    UNIQUE(sample_date, location)
                )
            """)

    def save_data(self, sample_date, location, min_temp, max_temp, avg_temp):
        """Save data to the DB, ensuring no duplicates."""
        with DBCM(self.db_name) as cursor:
            try:
                cursor.execute("""
                    INSERT INTO weather (sample_date, location, min_temp, max_temp, avg_temp)
                    VALUES (?, ?, ?, ?, ?)
                """, (sample_date, location, min_temp, max_temp, avg_temp))
            except sqlite3.IntegrityError:
                print(f"Data for {sample_date} at {location} already exists, skipping insertion.")

    def fetch_data(self):
        """Fetch all weather data from the DB."""
        with DBCM(self.db_name) as cursor:
            cursor.execute("SELECT sample_date, location, min_temp, max_temp, avg_temp FROM weather")
            return cursor.fetchall()

    def purge_data(self):
        """Delete all data from the weather table."""
        with DBCM(self.db_name) as cursor:
            cursor.execute("DELETE FROM weather")
            print("All data purged from the database.")
