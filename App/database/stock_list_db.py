import sqlite3


class StockListDB:
    """Handles database operations for the stock list."""
    def __init__(self):
        self._connection = None
        self._cursor = None

    def add_item(self, item_id, quantity):
        """Add a new item to the stock list or update quantity if already exists."""
        self._connect()
        try:
            # Check if item already exists in stock list
            self._cursor.execute("""
                SELECT id, quantity FROM stock_list WHERE item_id = ?
            """, (item_id,))
            existing_item = self._cursor.fetchone()
            
            if existing_item:
                # Item already exists, update its quantity
                existing_id = existing_item[0]
                existing_quantity = existing_item[1]
                new_quantity = existing_quantity + quantity
                self._cursor.execute("""
                    UPDATE stock_list
                    SET quantity = ?
                    WHERE id = ?
                """, (new_quantity, existing_id))
            else:
                # Item doesn't exist, insert new entry
                self._cursor.execute("""
                    INSERT INTO stock_list (item_id, quantity)
                    VALUES (?, ?)
                """, (item_id, quantity))
            
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error adding item to stock list: {e}")
            self._connection.rollback()
            raise
        finally:
            self._close()

    def update_item(self, stock_id, quantity):
        """Update the quantity of an item in the stock list."""
        self._connect()
        try:
            self._cursor.execute("""
                UPDATE stock_list
                SET quantity = ?
                WHERE id = ?
            """, (quantity, stock_id))
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error updating item in stock list: {e}")
            self._connection.rollback()
            raise
        finally:
            self._close()

    def get_all_items(self):
        """Get all items from the stock list with item details."""
        self._connect()
        try:
            self._cursor.execute("""
                SELECT 
                    s.id,
                    s.item_id,
                    i.name,
                    s.quantity,
                    i.has_thresholds,
                    i.stocked_threshold,
                    i.running_out_threshold,
                    i.low_threshold
                FROM stock_list s
                JOIN item_list i ON s.item_id = i.id
                ORDER BY i.name
            """)
            items = self._cursor.fetchall()
            return items
        except sqlite3.Error as e:
            print(f"Error retrieving stock list items: {e}")
            return []
        finally:
            self._close()

    def get_item_by_id(self, stock_id):
        """Get a specific item from the stock list by stock id."""
        self._connect()
        try:
            self._cursor.execute("""
                SELECT 
                    s.id,
                    s.item_id,
                    i.name,
                    s.quantity,
                    i.has_thresholds,
                    i.stocked_threshold,
                    i.running_out_threshold,
                    i.low_threshold
                FROM stock_list s
                JOIN item_list i ON s.item_id = i.id
                WHERE s.id = ?
            """, (stock_id,))
            item = self._cursor.fetchone()
            return item
        except sqlite3.Error as e:
            print(f"Error retrieving stock list item: {e}")
            return None
        finally:
            self._close()

    def delete_item(self, stock_id):
        """Delete an item from the stock list."""
        self._connect()
        try:
            self._cursor.execute("DELETE FROM stock_list WHERE id = ?", (stock_id,))
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error deleting item from stock list: {e}")
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
