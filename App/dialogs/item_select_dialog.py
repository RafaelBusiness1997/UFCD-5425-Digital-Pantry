import tkinter as _tk
from tkinter import messagebox
from database.item_list_db import ItemListDB


class ItemSelectDialog(_tk.Toplevel):
    """Dialog for selecting an item from the item list and specifying quantity."""

    def __init__(self, parent, on_save_callback=None):
        """Initialize the item select dialog."""

        super().__init__(parent)
        self.title("Add Item to Stock")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._item_list_db = ItemListDB()
        self._selected_item_id = None
        self._selected_item_button = None
        self._on_save_callback = on_save_callback

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # --- Bottom widgets packed FIRST so canvas doesn't steal their space ---

        # Button frame
        button_frame = _tk.Frame(self, bg="#ffffff")
        button_frame.pack(side="bottom", pady=10)

        confirm_button = _tk.Button(
            button_frame,
            text="Confirm",
            bg="#96862A",
            fg="white",
            font=("Arial", 10),
            width=10,
            command=self._on_confirm
        )
        confirm_button.pack(side="left", padx=5)

        cancel_button = _tk.Button(
            button_frame,
            text="Cancel",
            bg="#5a5a5a",
            fg="white",
            font=("Arial", 10),
            width=10,
            command=self._on_cancel
        )
        cancel_button.pack(side="left", padx=5)

        # Quantity frame
        quantity_frame = _tk.Frame(self, bg="#ffffff")
        quantity_frame.pack(side="bottom", pady=10, padx=10, fill="x")

        quantity_label = _tk.Label(
            quantity_frame,
            text="Quantity:",
            font=("Arial", 10),
            bg="#ffffff"
        )
        quantity_label.pack(side="left")

        self._quantity_var = _tk.StringVar(value="1")
        self._quantity_entry = _tk.Entry(
            quantity_frame,
            textvariable=self._quantity_var,
            font=("Arial", 10),
            width=15
        )
        self._quantity_entry.pack(side="left", padx=5)

        # Items label
        items_label = _tk.Label(
            self,
            text="Select an item:",
            font=("Arial", 10, "bold"),
            bg="#ffffff"
        )
        items_label.pack(pady=(10, 5), padx=10, anchor="w")

        # Scrollable items frame
        scroll_frame = _tk.Frame(self, bg="#ffffff")
        scroll_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))

        self._canvas = _tk.Canvas(
            scroll_frame,
            borderwidth=1,
            background="#ffffff",
            highlightthickness=0,
            relief="solid"
        )
        self._scrollbar = _tk.Scrollbar(scroll_frame, orient="vertical", command=self._canvas.yview)
        self._scrollable_frame = _tk.Frame(self._canvas, background="#ffffff")

        self._scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=(0, 0, e.width, e.height)
            )
        )

        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfig("expand", width=e.width)
        )

        self._canvas.bind("<Enter>", lambda e: self._canvas.bind("<MouseWheel>", self._on_mousewheel))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind("<MouseWheel>"))

        self._canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw", tags="expand")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._load_items()

        self.update_idletasks()
        width, height = 400, 500
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _on_mousewheel(self, event):
        """Scroll only within content bounds."""
        top, bottom = self._canvas.yview()
        if (event.delta > 0 and top <= 0) or (event.delta < 0 and bottom >= 1):
            return
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _load_items(self):
        """Load all items from the item list database."""
        items = self._item_list_db.get_all_items()

        if items:
            for item in items:
                item_id = item[0]
                item_name = item[1]
                self._create_item_button(item_name, item_id)
        else:
            empty_label = _tk.Label(
                self._scrollable_frame,
                text="No items available",
                font=("Arial", 10),
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
            height=1,
            command=lambda: self._on_item_click(item_id, item_button)
        )
        item_button.config(highlightcolor="gray", highlightthickness=2, highlightbackground="gray")
        item_button.pack(fill="x", padx=5, pady=3)

    def _on_item_click(self, item_id, item_button):
        """Handle item button click - set as selected."""
        if self._selected_item_button is not None:
            self._selected_item_button.config(relief="solid", borderwidth=2, bg="#ffffff")

        self._selected_item_id = item_id
        self._selected_item_button = item_button
        item_button.config(relief="solid", borderwidth=3, bg="#f0f0f0")

    def _on_confirm(self):
        """Handle confirm button click."""
        if self._selected_item_id is None:
            messagebox.showwarning("Warning", "Please select an item!")
            return

        try:
            quantity = int(self._quantity_var.get())
            if quantity <= 0:
                messagebox.showwarning("Warning", "Quantity must be greater than 0!")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid quantity!")
            return

        item_data = {
            'item_id': self._selected_item_id,
            'quantity': quantity
        }

        if self._on_save_callback:
            self._on_save_callback(item_data)

        self.destroy()

    def _on_cancel(self):
        """Handle cancel button click."""
        self.destroy()