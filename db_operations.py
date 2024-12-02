"""
Module to handle database operations.
"""

from dbcm import DBCM

DB_NAME = "weather.sqlite"
class DBOperations:
    """
    Class to handle database operations.
    """
    def __init__(self, db_name=DB_NAME):
        """Initialize the DBOperations class with the database name."""
        self.db_name = db_name

    def initialize_db(self):
        """
        Initialize the database and create the samples table if it doesn't exist.
        """
        try:
            with DBCM(self.db_name) as cursor:
                print("Opening database...")
                cursor.execute("""CREATE TABLE IF NOT EXISTS samples (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    date TEXT NOT NULL UNIQUE,
                                    location TEXT NOT NULL,
                                    min_temp REAL NOT NULL,
                                    max_temp REAL NOT NULL,
                                    avg_temp REAL NOT NULL
                                );""")
                print("Database initialized successfully.")
        except Exception as e:
            print("Error initializing the database:", e)

    def purge_data(self):
        """
        Purge all data from the samples table without deleting the table itself.
        """
        try:
            with DBCM(self.db_name) as cursor:
                cursor.execute("DELETE FROM samples")
                print("All data purged from the database.")
        except Exception as e:
            print("Error purging data:", e)

    def save_data(self, weather_dict):
        """
        Save new weather data to the database if it doesn't already exist.
        """
        try:
            with DBCM(self.db_name) as cursor:
                sql = """INSERT OR IGNORE INTO samples (date, location, min_temp, max_temp, avg_temp)
                         VALUES (?, ?, ?, ?, ?)"""
                location = "Winnipeg, MB"
                for date, data in weather_dict.items():
                    cursor.execute(sql, (date, location, data["Min"], data["Max"], data["Mean"]))
                print("New weather data saved successfully.")
        except Exception as e:
            print("Error saving weather data:", e)

    def fetch_data(self, start_date=None, end_date=None):
        """
        Fetch data from the database for plotting.
        If `start_date` and `end_date` are specified, retrieve data within the range.
        Otherwise, retrieve all data.
        Returns data as a list of dictionaries.
        """
        try:
            with DBCM(self.db_name) as cursor:
                if start_date and end_date:
                    cursor.execute("""SELECT date, location, min_temp, max_temp, avg_temp
                                      FROM samples
                                      WHERE date BETWEEN ? AND ?""", (start_date, end_date))
                else:
                    cursor.execute("""SELECT date, location, min_temp, max_temp, avg_temp
                                      FROM samples""")
                
                rows = cursor.fetchall()
                return [
                    {"date": row[0], "location": row[1], "min_temp": row[2], "max_temp": row[3], "avg_temp": row[4]}
                    for row in rows
                ]
        except Exception as e:
            print("Error fetching data:", e)
            return []

if __name__ == "__main__":
    db = DBOperations()
    db.initialize_db()

    all_data = db.fetch_data()
    print("\nAll Data:", all_data)