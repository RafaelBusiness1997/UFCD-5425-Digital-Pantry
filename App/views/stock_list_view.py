import tkinter as _tk
from tkinter import messagebox
from dialogs.item_select_dialog import ItemSelectDialog
from dialogs.quantity_dialog import QuantityDialog
from dialogs.confirmation_dialog import ConfirmationDialog
from database.stock_list_db import StockListDB


class StockListView(_tk.Frame):
    """View for displaying and managing the stock list."""
    def __init__(self, parent):
        super().__init__(parent)

        # Setup database
        self._stock_list_db = StockListDB()

        # Track selected item
        self._selected_stock_id = None
        self._selected_item_button = None

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

        # Edit Quantity button (hidden by default)
        self._edit_quantity_button = _tk.Button(
            self._button_frame,
            text="Edit Quantity",
            bg="#2196F3",
            fg="white",
            command=self._on_edit_quantity_click,
            font=("Arial", 10),
            padx=10,
            pady=5
        )

        # Delete Item button (hidden by default)
        self._delete_item_button = _tk.Button(
            self._button_frame,
            text="Delete Item",
            bg="#d9534f",
            fg="white",
            command=self._on_delete_item_click,
            font=("Arial", 10),
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
        self._refresh_items()

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
            self._stock_list_db.add_item(
                item_id=item_data['item_id'],
                quantity=item_data['quantity']
            )
            self._refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def _on_delete_item_click(self):
        """Open the delete confirmation dialog."""
        if self._selected_stock_id is None:
            return

        # Get the selected item data
        items = self._stock_list_db.get_all_items()
        selected_item = None
        for item in items:
            if item[0] == self._selected_stock_id:
                selected_item = item
                break

        if selected_item is None:
            messagebox.showerror("Error", "Could not find selected item!")
            return

        item_name = selected_item[2]
        message = f"Delete '{item_name}' from the stock list?"
        ConfirmationDialog(
            self,
            title="Delete Item",
            message=message,
            on_confirm_callback=self._on_delete_item_confirm
        )

    def _on_delete_item_confirm(self):
        """Handle confirmed deletion of the item."""
        try:
            self._stock_list_db.delete_item(self._selected_stock_id)
            self._selected_stock_id = None
            self._selected_item_button = None
            self._delete_item_button.pack_forget()
            self._edit_quantity_button.pack_forget()
            self._refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")

    def _on_edit_quantity_click(self):
        """Open the edit quantity dialog."""
        if self._selected_stock_id is None:
            return

        # Get the selected item data
        items = self._stock_list_db.get_all_items()
        selected_item = None
        for item in items:
            if item[0] == self._selected_stock_id:
                selected_item = item
                break

        if selected_item is None:
            messagebox.showerror("Error", "Could not find selected item!")
            return

        current_quantity = selected_item[3]
        QuantityDialog(self, current_quantity, on_save_callback=self._on_quantity_save)

    def _on_quantity_save(self, new_quantity):
        """Handle the new quantity from the dialog and update database."""
        try:
            self._stock_list_db.update_item(self._selected_stock_id, new_quantity)
            self._refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update quantity: {str(e)}")

    def _refresh_items(self):
        """Load all items from database and display them."""
        # Clear existing items
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()

        # Reset selection state
        self._selected_stock_id = None
        self._selected_item_button = None
        self._edit_quantity_button.pack_forget()
        self._delete_item_button.pack_forget()

        # Get all items from database
        items = self._stock_list_db.get_all_items()

        # Sort items by threshold status
        sorted_items = sorted(items, key=lambda item: self._get_sort_priority(
            item[4],  # has_thresholds
            item[3],  # quantity
            item[5],  # stocked_threshold
            item[6],  # running_out_threshold
            item[7]   # low_threshold
        ))

        # Create buttons for each item
        if sorted_items:
            for item in sorted_items:
                stock_id = item[0]
                item_name = item[2]
                quantity = item[3]
                has_thresholds = item[4]
                stocked_threshold = item[5]
                running_out_threshold = item[6]
                low_threshold = item[7]
                self._create_item_button(item_name, quantity, stock_id, has_thresholds, stocked_threshold, running_out_threshold, low_threshold)
        else:
            # Show empty message
            empty_label = _tk.Label(
                self._scrollable_frame,
                text="No items in stock. Click 'Add Item' to get started!",
                font=("Arial", 11),
                fg="#999999",
                bg="#ffffff"
            )
            empty_label.pack(pady=20)

    def _get_sort_priority(self, has_thresholds, quantity, stocked_threshold, running_out_threshold, low_threshold):
        if not has_thresholds:
            return (3, 0)
        if quantity < running_out_threshold:
            return (0, -quantity)  # Low
        if quantity < stocked_threshold:
            return (1, -quantity)  # Running out
        return (2, -quantity)  # Stocked

    def _get_border_color(self, has_thresholds, quantity, stocked_threshold, running_out_threshold, low_threshold):
        """Determine border color based on thresholds and quantity."""
        if not has_thresholds:
            return "#cccccc"  # Gray if no thresholds
        if quantity >= stocked_threshold:
            return "#00aa00"  # Green
        elif quantity >= running_out_threshold:
            return "#ffaa00"  # Yellow
        elif quantity >= low_threshold:
            return "#ff0000"  # Red
        else:
            return "#ff0000"  # Red (below low threshold)

    def _create_item_button(self, item_name, quantity, stock_id, has_thresholds, stocked_threshold, running_out_threshold, low_threshold):
        """Create a button for a stock item."""
        border_color = self._get_border_color(has_thresholds, quantity, stocked_threshold, running_out_threshold, low_threshold)
        
        button_text = f"{item_name}\nQty: {quantity}"
        
        # Create a frame to act as the colored border
        border_frame = _tk.Frame(self._scrollable_frame, bg=border_color, highlightthickness=0)
        border_frame.pack(fill="x", padx=10, pady=5)
        
        # Create the button inside the frame (with a small gap to show the frame color as border)
        item_button = _tk.Button(
            border_frame,
            text=button_text,
            font=("Arial", 10),
            bg="#ffffff",
            fg="black",
            relief="flat",
            height=2,
            command=lambda: self._on_item_click(stock_id, item_button, border_frame)
        )
        item_button.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Store reference to border frame in button for later access
        item_button._border_frame = border_frame

    def _on_item_click(self, stock_id, item_button, border_frame):
        """Handle item button click - set as selected."""
        # Deselect previous button
        if self._selected_item_button is not None:
            self._selected_item_button.config(bg="#ffffff")

        # Select new button
        self._selected_stock_id = stock_id
        self._selected_item_button = item_button
        item_button.config(bg="#f0f0f0")

        # Show edit quantity and delete buttons (forget first to ensure proper ordering)
        self._edit_quantity_button.pack_forget()
        self._delete_item_button.pack_forget()
        self._edit_quantity_button.pack(side="left", padx=(0, 10))
        self._delete_item_button.pack(side="left", padx=(0, 10))
