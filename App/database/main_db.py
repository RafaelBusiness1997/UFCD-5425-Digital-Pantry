import sqlite3
from database.item_list_db import ItemListDB


class MainDB:
    def __init__(self):
        try:
            self._connection = self._connect()
            self._cursor = self._connection.cursor()

            # Items table
            self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS item_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    has_thresholds BOOLEAN NOT NULL DEFAULT 1,
                    stocked_treshold INTEGER DEFAULT 6,
                    running_out_threshold INTEGER DEFAULT 3,
                    low_threshold INTEGER DEFAULT 1,
                    has_price BOOLEAN NOT NULL DEFAULT 0,
                    price DECIMAL(6,2) DEFAULT 0.00
                )
            """)

            # Stock list table
            self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (item_id) REFERENCES item_list (id) ON UPDATE CASCADE ON DELETE CASCADE
                )
            """)

            # Shopping list table
            self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS shopping_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    is_acquired BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (item_id) REFERENCES item_list (id) ON UPDATE CASCADE ON DELETE CASCADE
                )
            """)

            self._connection.commit()

        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise

        finally:
            ItemListDB(self._connection, self._cursor)

    def close(self):
        try:
            if self._connection:
                self._connection.close()
                self._connection = None

        except sqlite3.Error as e:
            print(f"Error closing connection: {e}")

    def _connect(self, db_path: str = "pantry.db"):
        try:
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            return connection

        except sqlite3.Error as e:
            print(f"Connection error: {e}")
            raise
