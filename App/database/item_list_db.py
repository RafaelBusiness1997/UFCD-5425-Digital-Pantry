import sqlite3

class ItemListDB:
    def __init__(self, connection, cursor):
        self._connection = connection
        self._cursor = cursor

    def add_item(self, name, has_thresholds, stocked_threshold, running_out_threshold, low_threshold, has_price, price):
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

    def update_item(self, item_id, name, has_thresholds, stocked_threshold, running_out_threshold, low_threshold, has_price, price):
        """Update an existing item in the database."""
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

    def get_all_items(self):
        """Get all items from the database."""
        try:
            self._cursor.execute("SELECT id, name, has_thresholds, stocked_treshold, running_out_threshold, low_threshold, has_price, price FROM item_list ORDER BY name")
            items = self._cursor.fetchall()
            return items
        except sqlite3.Error as e:
            print(f"Error retrieving items: {e}")
            return []
