import sqlite3

class ItemListDB:
    """Handles database operations for the item list."""
    def __init__(self):
        self._connection = None
        self._cursor = None

    def add_item(self, name, has_thresholds, stocked_threshold, running_out_threshold, low_threshold, has_price, price):
        """Add a new item to the database."""
        self._connect()
        try:
            self._cursor.execute("""
                INSERT INTO item_list (name, has_thresholds, stocked_treshold, running_out_threshold, low_threshold, has_price, price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, has_thresholds, stocked_threshold, running_out_threshold, low_threshold, has_price, price))
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error adding item: {e}")
            self._connection.rollback()
            raise
        finally:
            self._close()

    def update_item(self, item_id, name, has_thresholds, stocked_threshold, running_out_threshold, low_threshold, has_price, price):
        """Update an existing item in the database."""
        self._connect()
        try:
            self._cursor.execute("""
                UPDATE item_list
                SET name = ?, has_thresholds = ?, stocked_treshold = ?, running_out_threshold = ?, low_threshold = ?, has_price = ?, price = ?
                WHERE id = ?
            """, (name, has_thresholds, stocked_threshold, running_out_threshold, low_threshold, has_price, price, item_id))
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error updating item: {e}")
            self._connection.rollback()
            raise
        finally:
            self._close()

    def get_all_items(self):
        """Get all items from the database."""
        self._connect()
        try:
            self._cursor.execute("SELECT id, name, has_thresholds, stocked_treshold, running_out_threshold, low_threshold, has_price, price FROM item_list ORDER BY name")
            items = self._cursor.fetchall()
            return items
        except sqlite3.Error as e:
            print(f"Error retrieving items: {e}")
            return []
        finally:
            self._close()

    def delete_item(self, item_id):
        """Delete an item from the database."""
        self._connect()
        try:
            self._cursor.execute("DELETE FROM item_list WHERE id = ?", (item_id,))
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error deleting item: {e}")
            self._connection.rollback()
            raise
        finally:
            self._close()

    def _close(self):
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
                self._cursor = None

        except sqlite3.Error as e:
            print(f"Error closing connection: {e}")

    def _connect(self, db_path: str = "pantry.db"):
        try:
            self._connection = sqlite3.connect(db_path)
            self._connection.row_factory = sqlite3.Row

            self._cursor = self._connection.cursor()

        except sqlite3.Error as e:
            print(f"Connection error: {e}")
            raise
