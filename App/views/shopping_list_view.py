import tkinter as _tk
from tkinter import messagebox
from dialogs.item_select_dialog import ItemSelectDialog
from dialogs.quantity_dialog import QuantityDialog
from dialogs.confirmation_dialog import ConfirmationDialog
from database.shopping_list_db import ShoppingListDB
from database.stock_list_db import StockListDB
from views import stock_list_view


class ShoppingListView(_tk.Frame):
    """View for displaying and managing the shopping list."""
    def __init__(self, parent, stock_list_view):
        super().__init__(parent)

        # Setup references
        self._shopping_list_db = ShoppingListDB()
        self._stock_list_db = StockListDB()
        self._stock_list_view = stock_list_view

        # Track selected items (multiple selection)
        self._selected_shopping_ids = set()
        self._selected_item_buttons = {}  # Map shopping_id to button widget

        # Top button frame
        self._button_frame = _tk.Frame(self, bg="#f0f0f0", pady=10)
        self._button_frame.pack(side="top", fill="x")

        self._add_item_button = _tk.Button(
            self._button_frame,
            text="Add Item",
            bg="#96862A",
            fg="white",
            command=self._on_add_item_click,
            font=("Arial", 10),
            padx=10,
            pady=5
        )
        self._add_item_button.pack(side="left", padx=10)

        # Unselect All button (hidden by default)
        self._unselect_all_button = _tk.Button(
            self._button_frame,
            text="Unselect All",
            bg="#5a5a5a",
            fg="white",
            command=self.unselect_all,
            font=("Arial", 10),
            padx=10,
            pady=5
        )

        # Delete Items button (hidden by default)
        self._delete_items_button = _tk.Button(
            self._button_frame,
            text="Delete Selected",
            bg="#d9534f",
            fg="white",
            command=self._on_delete_items_click,
            font=("Arial", 10),
            padx=10,
            pady=5
        )

        # Edit Quantity button (hidden by default)
        self._edit_quantity_button = _tk.Button(
            self._button_frame,
            text="Edit Quantity",
            bg="#4CAF50",
            fg="white",
            command=self._on_edit_quantity_click,
            font=("Arial", 10),
            padx=10,
            pady=5
        )

        # Mark Acquired button (hidden by default)
        self._mark_acquired_button = _tk.Button(
            self._button_frame,
            text="Mark Acquired",
            bg="#2196F3",
            fg="white",
            command=self._on_mark_acquired_click,
            font=("Arial", 10),
            padx=10,
            pady=5
        )

        # Mark Unacquired button (hidden by default)
        self._mark_unacquired_button = _tk.Button(
            self._button_frame,
            text="Mark Unacquired",
            bg="#FF9800",
            fg="white",
            command=self._on_mark_unacquired_click,
            font=("Arial", 10),
            padx=10,
            pady=5
        )

        # Total price frame (packed BEFORE canvas so it anchors to bottom correctly)
        self._total_frame = _tk.Frame(self, bg="#f0f0f0", pady=10)
        self._total_frame.pack(side="bottom", fill="x")

        self._total_price_label = _tk.Label(
            self._total_frame,
            text="Total Price: €0.00",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="black"
        )
        self._total_price_label.pack()

        # Confirm Acquired frame (packed BEFORE canvas, ABOVE total price frame)
        self._confirm_acquired_frame = _tk.Frame(self, bg="#f0f0f0", pady=5)
        self._confirm_acquired_frame.pack(side="bottom", fill="x")

        self._confirm_acquired_button = _tk.Button(
            self._confirm_acquired_frame,
            text="Confirm Acquired",
            bg="#96862A",
            fg="white",
            command=self._on_confirm_acquired_click,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )

        # Main scrollable content frame
        self._canvas = _tk.Canvas(self, borderwidth=0, background="#ffffff", highlightthickness=0)
        self._scrollbar = _tk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._scrollable_frame = _tk.Frame(self._canvas, background="#ffffff")

        self._canvas.pack_propagate(False)

        self._scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )

        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self._canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw", tags="expand")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

        self._scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_frame_configure)

        # Load items on startup
        self.refresh_items()

    def _on_frame_configure(self, event=None):
        self._canvas.itemconfig("expand", width=self._canvas.winfo_width())

        bbox = self._canvas.bbox("all")
        if bbox:
            canvas_height = self._canvas.winfo_height()
            if bbox[3] < canvas_height:
                bbox = (bbox[0], bbox[1], bbox[2], canvas_height)
            self._canvas.configure(scrollregion=bbox)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_add_item_click(self):
        """Open the add item dialog."""
        dialog = ItemSelectDialog(self, on_save_callback=self._on_add_item_save)

    def _on_add_item_save(self, item_data):
        """Handle the item data from the dialog and save to database."""
        try:
            self._shopping_list_db.add_item(
                item_id=item_data['item_id'],
                quantity=item_data['quantity']
            )
            self.refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def _on_delete_items_click(self):
        """Open the delete confirmation dialog for selected items."""
        if not self._selected_shopping_ids:
            return

        count = len(self._selected_shopping_ids)
        message = f"Delete {count} selected item(s)?"
        ConfirmationDialog(
            self,
            title="Delete Items",
            message=message,
            on_confirm_callback=self._on_delete_items_confirm
        )

    def _on_delete_items_confirm(self):
        """Handle confirmed deletion of selected items."""
        try:
            for shopping_id in self._selected_shopping_ids:
                self._shopping_list_db.delete_item(shopping_id)
            self._selected_shopping_ids.clear()
            self._selected_item_buttons.clear()
            self.refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete items: {str(e)}")

    def unselect_all(self):
        """Unselect all selected items."""
        for shopping_id in list(self._selected_shopping_ids):
            if shopping_id in self._selected_item_buttons:
                button = self._selected_item_buttons[shopping_id]
                acquired = button._is_acquired
                button.config(bg="#90EE90" if acquired else "#ffffff")
        self._selected_shopping_ids.clear()
        self._selected_item_buttons.clear()
        self._update_button_visibility()

    def refresh_items(self):
        """Load all items from database and display them."""
        # Clear existing items
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()

        # Reset selection state
        self._selected_shopping_ids.clear()
        self._selected_item_buttons.clear()

        # Get all items from database
        items = self._shopping_list_db.get_all_items()

        # Create buttons for each item
        if items:
            for item in items:
                shopping_id = item[0]
                item_name = item[2]
                quantity = item[3]
                is_acquired = bool(item[4])
                has_price = item[5]
                price = item[6]
                self._create_item_button(item_name, quantity, shopping_id, has_price, price, is_acquired)
        else:
            # Show empty message
            empty_label = _tk.Label(
                self._scrollable_frame,
                text="No items in shopping list. Click 'Add Item' to get started!",
                font=("Arial", 11),
                fg="#999999",
                bg="#ffffff"
            )
            empty_label.pack(pady=20)

        # Update total price
        self._update_total_price()
        # Update button visibility
        self._update_button_visibility()
        # Update confirm acquired button visibility
        self._update_confirm_acquired_visibility()

    def _create_item_button(self, item_name, quantity, shopping_id, has_price, price, is_acquired):
        """Create a button for a shopping item."""
        # Format the price display
        if has_price and price is not None:
            total_item_price = float(price) * quantity
            price_text = f"€{total_item_price:.2f}"
        else:
            price_text = "No Price"

        button_text = f"{item_name} (Qty: {quantity})\nPrice: {price_text}"

        bg_color = "#90EE90" if is_acquired else "#ffffff"

        item_button = _tk.Button(
            self._scrollable_frame,
            text=button_text,
            font=("Arial", 10),
            bg=bg_color,
            fg="black",
            relief="solid",
            borderwidth=2,
            height=2,
            command=lambda: self._on_item_click(shopping_id, item_button)
        )
        item_button.config(highlightcolor="gray", highlightthickness=2, highlightbackground="gray")
        item_button.pack(fill="x", padx=10, pady=5)

        # Store metadata on button
        item_button._shopping_id = shopping_id
        item_button._is_acquired = is_acquired

    def _on_item_click(self, shopping_id, item_button):
        """Handle item button click - toggle selection."""
        if shopping_id in self._selected_shopping_ids:
            # Unselect this item
            self._selected_shopping_ids.discard(shopping_id)
            self._selected_item_buttons.pop(shopping_id, None)
            acquired = item_button._is_acquired
            item_button.config(bg="#90EE90" if acquired else "#ffffff")
        else:
            # Select this item
            self._selected_shopping_ids.add(shopping_id)
            self._selected_item_buttons[shopping_id] = item_button
            acquired = item_button._is_acquired
            item_button.config(bg="#2B882B" if acquired else "#cccccc")

        # Update button visibility
        self._update_button_visibility()

    def _update_button_visibility(self):
        """Show/hide buttons based on selection state."""
        num_selected = len(self._selected_shopping_ids)

        if num_selected > 0:
            self._unselect_all_button.pack(side="left", padx=(0, 10))
            self._delete_items_button.pack(side="left", padx=(0, 10))
        else:
            self._unselect_all_button.pack_forget()
            self._delete_items_button.pack_forget()

        # Show edit quantity button only if exactly one item is selected
        if num_selected == 1:
            self._edit_quantity_button.pack(side="left", padx=(0, 10))
        else:
            self._edit_quantity_button.pack_forget()

        # Determine acquired states of selected items
        if num_selected > 0:
            acquired_states = set(
                self._selected_item_buttons[sid]._is_acquired
                for sid in self._selected_shopping_ids
            )
            if acquired_states == {False}:
                self._mark_acquired_button.pack(side="left", padx=(0, 10))
                self._mark_unacquired_button.pack_forget()
            elif acquired_states == {True}:
                self._mark_unacquired_button.pack(side="left", padx=(0, 10))
                self._mark_acquired_button.pack_forget()
            else:
                self._mark_acquired_button.pack_forget()
                self._mark_unacquired_button.pack_forget()
        else:
            self._mark_acquired_button.pack_forget()
            self._mark_unacquired_button.pack_forget()

    def _update_confirm_acquired_visibility(self):
        """Show/hide the Confirm Acquired button based on whether any items are acquired."""
        acquired_items = self._shopping_list_db.get_acquired_items()
        if acquired_items:
            self._confirm_acquired_button.pack(pady=5)
        else:
            self._confirm_acquired_button.pack_forget()

    def _on_mark_acquired_click(self):
        """Mark all selected items as acquired."""
        try:
            for shopping_id in self._selected_shopping_ids:
                self._shopping_list_db.mark_as_acquired(shopping_id, 1)
            self.refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark items as acquired: {str(e)}")

    def _on_mark_unacquired_click(self):
        """Mark all selected items as unacquired."""
        try:
            for shopping_id in self._selected_shopping_ids:
                self._shopping_list_db.mark_as_acquired(shopping_id, 0)
            self.refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark items as unacquired: {str(e)}")

    def _on_confirm_acquired_click(self):
        """Move all acquired shopping list items into the stock list."""
        try:
            acquired_items = self._shopping_list_db.get_acquired_items()
            for item in acquired_items:
                shopping_id = item[0]
                item_id = item[1]
                quantity = item[3]
                self._stock_list_db.add_item(item_id=item_id, quantity=quantity)
                self._shopping_list_db.delete_item(shopping_id)
            self.refresh_items()
            self._stock_list_view.refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to confirm acquired items: {str(e)}")

    def _on_edit_quantity_click(self):
        """Open the quantity dialog for the selected item."""
        if len(self._selected_shopping_ids) != 1:
            return

        shopping_id = list(self._selected_shopping_ids)[0]
        item = self._shopping_list_db.get_item_by_id(shopping_id)
        if item is None:
            messagebox.showerror("Error", "Could not find selected item!")
            return

        current_quantity = item[3]
        QuantityDialog(self, current_quantity, on_save_callback=self._on_quantity_save)

    def _on_quantity_save(self, new_quantity):
        """Handle the new quantity from the dialog and update database."""
        if len(self._selected_shopping_ids) != 1:
            return

        shopping_id = list(self._selected_shopping_ids)[0]
        try:
            self._shopping_list_db.update_item(shopping_id, new_quantity)
            self.refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update quantity: {str(e)}")

    def _update_total_price(self):
        """Calculate and update the total price label."""
        items = self._shopping_list_db.get_all_items()
        total_price = 0.0

        for item in items:
            quantity = item[3]
            has_price = item[5]
            price = item[6]
            if has_price and price is not None:
                total_price += float(price) * quantity

        self._total_price_label.config(text=f"Total Price: €{total_price:.2f}")