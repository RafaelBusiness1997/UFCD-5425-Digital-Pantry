import sqlite3


class ShoppingListDB:
    """Handles database operations for the shopping list."""
    def __init__(self):
        self._connection = None
        self._cursor = None

    def add_item(self, item_id, quantity):
        """Add a new item to the shopping list or update quantity if already exists."""
        self._connect()
        try:
            self._cursor.execute("""
                SELECT id, quantity FROM shopping_list WHERE item_id = ?
            """, (item_id,))
            existing_item = self._cursor.fetchone()

            if existing_item:
                existing_id = existing_item[0]
                existing_quantity = existing_item[1]
                new_quantity = existing_quantity + quantity
                self._cursor.execute("""
                    UPDATE shopping_list
                    SET quantity = ?
                    WHERE id = ?
                """, (new_quantity, existing_id))
            else:
                self._cursor.execute("""
                    INSERT INTO shopping_list (item_id, quantity, is_acquired)
                    VALUES (?, ?, 0)
                """, (item_id, quantity))

            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error adding item to shopping list: {e}")
            self._connection.rollback()
            raise
        finally:
            self._close()

    def update_item(self, shopping_id, quantity):
        """Update the quantity of an item in the shopping list."""
        self._connect()
        try:
            self._cursor.execute("""
                UPDATE shopping_list
                SET quantity = ?
                WHERE id = ?
            """, (quantity, shopping_id))
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error updating item in shopping list: {e}")
            self._connection.rollback()
            raise
        finally:
            self._close()

    def get_all_items(self):
        """Get all items from the shopping list with item details."""
        self._connect()
        try:
            self._cursor.execute("""
                SELECT
                    s.id,
                    s.item_id,
                    i.name,
                    s.quantity,
                    s.is_acquired,
                    i.has_price,
                    i.price
                FROM shopping_list s
                JOIN item_list i ON s.item_id = i.id
                ORDER BY i.name
            """)
            items = self._cursor.fetchall()
            return items
        except sqlite3.Error as e:
            print(f"Error retrieving shopping list items: {e}")
            return []
        finally:
            self._close()

    def get_acquired_items(self):
        """Get all items from the shopping list that are marked as acquired."""
        self._connect()
        try:
            self._cursor.execute("""
                SELECT
                    s.id,
                    s.item_id,
                    i.name,
                    s.quantity,
                    s.is_acquired,
                    i.has_price,
                    i.price
                FROM shopping_list s
                JOIN item_list i ON s.item_id = i.id
                WHERE s.is_acquired = 1
                ORDER BY i.name
            """)
            items = self._cursor.fetchall()
            return items
        except sqlite3.Error as e:
            print(f"Error retrieving acquired shopping list items: {e}")
            return []
        finally:
            self._close()

    def get_item_by_id(self, shopping_id):
        """Get a specific item from the shopping list by shopping id."""
        self._connect()
        try:
            self._cursor.execute("""
                SELECT
                    s.id,
                    s.item_id,
                    i.name,
                    s.quantity,
                    s.is_acquired,
                    i.has_price,
                    i.price
                FROM shopping_list s
                JOIN item_list i ON s.item_id = i.id
                WHERE s.id = ?
            """, (shopping_id,))
            item = self._cursor.fetchone()
            return item
        except sqlite3.Error as e:
            print(f"Error retrieving shopping list item: {e}")
            return None
        finally:
            self._close()

    def delete_item(self, shopping_id):
        """Delete an item from the shopping list."""
        self._connect()
        try:
            self._cursor.execute("DELETE FROM shopping_list WHERE id = ?", (shopping_id,))
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error deleting item from shopping list: {e}")
            self._connection.rollback()
            raise
        finally:
            self._close()

    def mark_as_acquired(self, shopping_id, is_acquired):
        """Mark an item as acquired or not."""
        self._connect()
        try:
            self._cursor.execute("""
                UPDATE shopping_list
                SET is_acquired = ?
                WHERE id = ?
            """, (is_acquired, shopping_id))
            self._connection.commit()
        except sqlite3.Error as e:
            print(f"Error marking item as acquired: {e}")
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