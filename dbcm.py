"""
Context manager module to manage the database connections.
"""

import sqlite3

class DBCM:
    """Database connection manager."""
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Establish a database connection and return the cursor."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        """Commit changes and close the connection."""
        if exc_type is None:
            self.conn.commit()
        self.conn.close()
