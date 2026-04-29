import tkinter as _tk
from tkinter import messagebox
from dialogs.item_dialog import ItemDialog
from dialogs.confirmation_dialog import ConfirmationDialog
from database.item_list_db import ItemListDB


class ItemListView(_tk.Frame):
    """View for displaying and managing the list of items."""
    def __init__(self, parent, stock_list_view):
        super().__init__(parent)

        # Setup database
        self._item_list_db = ItemListDB()
        
        # To refresh stock list view when items are edited/deleted
        self._stock_list_view = stock_list_view

        # Track selected item
        self._selected_item_id = None
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

        # Edit Item button (hidden by default)
        self._edit_item_button = _tk.Button(
            self._button_frame,
            text="Edit Item",
            bg="#4CAF50",
            fg="white",
            command=self._on_edit_item_click,
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
        
    def deselect_item(self):
        """Deselect the currently selected item."""
        if self._selected_item_button is not None:
            self._selected_item_button.config(relief="solid", borderwidth=2, bg="#ffffff")
        self._selected_item_id = None
        self._selected_item_button = None
        self._edit_item_button.pack_forget()
        self._delete_item_button.pack_forget()

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
        dialog = ItemDialog(self, on_save_callback=self._on_add_item_save, mode="add")

    def _on_edit_item_click(self):
        """Open the edit item dialog."""
        if self._selected_item_id is None:
            return

        # Get the selected item data
        items = self._item_list_db.get_all_items()
        selected_item = None
        for item in items:
            if item[0] == self._selected_item_id:
                selected_item = item
                break

        if selected_item is None:
            messagebox.showerror("Error", "Could not find selected item!")
            return

        # Open dialog in edit mode with the item data
        item_data = {
            'id': selected_item[0],
            'name': selected_item[1],
            'has_thresholds': bool(selected_item[2]),
            'stocked_threshold': selected_item[3],
            'running_out_threshold': selected_item[4],
            'low_threshold': selected_item[5],
            'has_price': bool(selected_item[6]),
            'price': float(selected_item[7])
        }
        dialog = ItemDialog(self, on_save_callback=self._on_edit_item_save, mode="edit", initial_data=item_data)

    def _on_add_item_save(self, item_data):
        """Handle the item data from the add dialog and save to database."""
        try:
            self._item_list_db.add_item(
                name=item_data['name'],
                has_thresholds=item_data['has_thresholds'],
                stocked_threshold=item_data['stocked_threshold'],
                running_out_threshold=item_data['running_out_threshold'],
                low_threshold=item_data['low_threshold'],
                has_price=item_data['has_price'],
                price=item_data['price']
            )
            self._refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def _on_edit_item_save(self, item_data):
        """Handle the item data from the edit dialog and update database."""
        try:
            self._item_list_db.update_item(
                item_id=item_data['id'],
                name=item_data['name'],
                has_thresholds=item_data['has_thresholds'],
                stocked_threshold=item_data['stocked_threshold'],
                running_out_threshold=item_data['running_out_threshold'],
                low_threshold=item_data['low_threshold'],
                has_price=item_data['has_price'],
                price=item_data['price']
            )
            self._selected_item_id = None
            self._selected_item_button = None
            self._edit_item_button.pack_forget()
            self._delete_item_button.pack_forget()
            self._refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {str(e)}")

    def _on_delete_item_click(self):
        """Open the delete confirmation dialog."""
        if self._selected_item_id is None:
            return

        # Get the selected item data
        items = self._item_list_db.get_all_items()
        selected_item = None
        for item in items:
            if item[0] == self._selected_item_id:
                selected_item = item
                break

        if selected_item is None:
            messagebox.showerror("Error", "Could not find selected item!")
            return

        item_name = selected_item[1]
        message = f"Are you sure you want to delete '{item_name}'?"
        ConfirmationDialog(
            self,
            title="Delete Item",
            message=message,
            on_confirm_callback=self._on_delete_item_confirm
        )

    def _on_delete_item_confirm(self):
        """Handle confirmed deletion of the item."""
        try:
            self._item_list_db.delete_item(self._selected_item_id)
            item_id = self._selected_item_id
            self._selected_item_id = None
            self._selected_item_button = None
            self._edit_item_button.pack_forget()
            self._delete_item_button.pack_forget()
            self._refresh_items()
            self._stock_list_view.refresh_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")

    def _refresh_items(self):
        """Load all items from database and display them."""
        # Clear existing items
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()

        # Get all items from database
        items = self._item_list_db.get_all_items()

        # Create buttons for each item
        if items:
            for item in items:
                item_id = item[0]
                item_name = item[1]
                self._create_item_button(item_name, item_id)
        else:
            # Show empty message
            empty_label = _tk.Label(
                self._scrollable_frame,
                text="No items yet. Click 'Add Item' to get started!",
                font=("Arial", 11),
                fg="#999999",
                bg="#ffffff"
            )
            empty_label.pack(pady=20)

    def _create_item_button(self, item_name, item_id):
        """Create a button for an item."""
        item_button = _tk.Button(
            self._scrollable_frame,
            text=item_name,
            font=("Arial", 10),
            bg="#ffffff",
            fg="black",
            relief="solid",
            borderwidth=2,
            height=2,
            command=lambda: self._on_item_click(item_id, item_button)
        )
        item_button.config(highlightcolor="gray", highlightthickness=2, highlightbackground="gray")
        item_button.pack(fill="x", padx=10, pady=5)

    def _on_item_click(self, item_id, item_button):
        """Handle item button click - set as selected."""
        # Deselect previous button
        if self._selected_item_button is not None:
            self._selected_item_button.config(relief="solid", borderwidth=2, bg="#ffffff")

        # Select new button
        self._selected_item_id = item_id
        self._selected_item_button = item_button
        item_button.config(relief="solid", borderwidth=3, bg="#f0f0f0")

        # Show edit and delete buttons
        self._edit_item_button.pack(side="left", padx=(0, 10))
        self._delete_item_button.pack(side="left", padx=(0, 10))

    def get_scrollable_frame(self):
        """Get the scrollable frame for adding items."""
        return self._scrollable_frame
