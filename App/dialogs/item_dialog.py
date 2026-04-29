import tkinter as tk
from tkinter import messagebox


class ItemDialog(tk.Toplevel):
    """Dialog for adding or editing an item."""

    def __init__(self, parent, on_save_callback=None, mode="add", initial_data=None):
        super().__init__(parent)

        self._mode = mode
        self._initial_data = initial_data or {}

        # Set title based on mode
        if mode == "edit":
            self.title("Edit Item")
        else:
            self.title("Add Item")

        self.geometry("500x650")
        self.configure(bg="white")

        self._on_save_callback = on_save_callback
        self._result = None

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (500 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (650 // 2)
        self.geometry(f"500x650+{x}+{y}")

        self._create_form()

    def _create_form(self):
        main_frame = tk.Frame(self, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Item Name
        tk.Label(main_frame, text="Item Name:", font=("Arial", 10), bg="white").pack(anchor="w", pady=(0, 5))
        self._name_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self._name_entry.pack(fill="x", pady=(0, 20))
        if self._mode == "edit":
            self._name_entry.insert(0, self._initial_data.get('name', ''))

        # Has Thresholds
        self._has_thresholds_var = tk.BooleanVar(value=self._initial_data.get('has_thresholds', True))
        self._has_thresholds_checkbox = tk.Checkbutton(
            main_frame,
            text="Has Thresholds",
            variable=self._has_thresholds_var,
            command=self._on_thresholds_toggle,
            font=("Arial", 10),
            bg="white"
        )
        self._has_thresholds_checkbox.pack(anchor="w", pady=(0, 5))

        # Thresholds Frame
        self._thresholds_frame = tk.LabelFrame(main_frame, text="Thresholds", padx=15, pady=10, font=("Arial", 10), bg="white")
        self._thresholds_frame.pack(fill="x", pady=(0, 20))

        tk.Label(self._thresholds_frame, text="Stocked:", font=("Arial", 9), bg="white").pack(anchor="w", pady=(0, 3))
        self._stocked_threshold_spinbox = tk.Spinbox(self._thresholds_frame, from_=0, to=1000, width=20, font=("Arial", 10))
        self._stocked_threshold_spinbox.delete(0, "end")
        self._stocked_threshold_spinbox.insert(0, str(self._initial_data.get('stocked_threshold', 6)))
        self._stocked_threshold_spinbox.pack(anchor="w", pady=(0, 10), fill="x")

        tk.Label(self._thresholds_frame, text="Running Out:", font=("Arial", 9), bg="white").pack(anchor="w", pady=(0, 3))
        self._running_out_threshold_spinbox = tk.Spinbox(self._thresholds_frame, from_=0, to=1000, width=20, font=("Arial", 10))
        self._running_out_threshold_spinbox.delete(0, "end")
        self._running_out_threshold_spinbox.insert(0, str(self._initial_data.get('running_out_threshold', 3)))
        self._running_out_threshold_spinbox.pack(anchor="w", pady=(0, 10), fill="x")

        # Has Price
        self._has_price_var = tk.BooleanVar(value=self._initial_data.get('has_price', False))
        self._has_price_checkbox = tk.Checkbutton(
            main_frame,
            text="Has Price",
            variable=self._has_price_var,
            command=self._on_price_toggle,
            font=("Arial", 10),
            bg="white"
        )
        self._has_price_checkbox.pack(anchor="w", pady=(0, 5))

        # Price Frame
        self._price_frame = tk.Frame(main_frame, bg="white")
        self._price_frame.pack(anchor="w", pady=(0, 20), fill="x")

        tk.Label(self._price_frame, text="Price:", font=("Arial", 9), bg="white").pack(anchor="w", pady=(0, 3))
        price_input = tk.Frame(self._price_frame, bg="white")
        price_input.pack(anchor="w", fill="x")
        self._price_entry = tk.Entry(price_input, width=20, font=("Arial", 10))
        self._price_entry.pack(side="left", padx=(0, 5))
        if self._mode == "edit":
            self._price_entry.insert(0, str(self._initial_data.get('price', 0.0)))
        tk.Label(price_input, text="€", font=("Arial", 10), bg="white").pack(side="left")

        # Buttons
        self._button_frame = tk.Frame(main_frame, bg="white")
        self._button_frame.pack(fill="x", pady=(20, 0))

        save_text = "Update" if self._mode == "edit" else "Save"
        tk.Button(self._button_frame, text=save_text, command=self._on_save, bg="#96862A", fg="white", width=15, font=("Arial", 10)).pack(side="left", padx=(0, 10))
        tk.Button(self._button_frame, text="Cancel", command=self._on_cancel, bg="#cccccc", fg="black", width=15, font=("Arial", 10)).pack(side="left")

        # Initialize price/threshold frame visibility
        if not self._has_thresholds_var.get():
            self._thresholds_frame.pack_forget()
        if not self._has_price_var.get():
            self._price_frame.pack_forget()

    def _on_thresholds_toggle(self):
        if self._has_thresholds_var.get():
            self._thresholds_frame.pack(fill="x", pady=(0, 20), before=self._has_price_checkbox)
        else:
            self._thresholds_frame.pack_forget()

    def _on_price_toggle(self):
        if self._has_price_var.get():
            self._price_frame.pack(anchor="w", pady=(0, 10), fill="x", before=self._button_frame)
        else:
            self._price_frame.pack_forget()

    def _on_save(self):
        name = self._name_entry.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Item name is required!")
            return

        try:
            has_thresholds = self._has_thresholds_var.get()
            stocked_threshold = int(self._stocked_threshold_spinbox.get()) if has_thresholds else 6
            running_out_threshold = int(self._running_out_threshold_spinbox.get()) if has_thresholds else 3
            low_threshold = 1

            if has_thresholds:
                if not (low_threshold < running_out_threshold < stocked_threshold):
                    messagebox.showerror("Validation Error", "Thresholds must be in order: Low < Running Out < Stocked!")
                    return

            has_price = self._has_price_var.get()
            price = 0.0
            if has_price:
                price_str = self._price_entry.get().strip()
                if not price_str:
                    messagebox.showerror("Validation Error", "Price is required when 'Has Price' is checked!")
                    return
                price = float(price_str)

            self._result = {
                'name': name,
                'has_thresholds': has_thresholds,
                'stocked_threshold': stocked_threshold,
                'running_out_threshold': running_out_threshold,
                'low_threshold': low_threshold,
                'has_price': has_price,
                'price': price
            }

            # Include item ID if editing
            if self._mode == "edit":
                self._result['id'] = self._initial_data.get('id')

            if self._on_save_callback:
                self._on_save_callback(self._result)

            self.destroy()

        except ValueError:
            messagebox.showerror("Validation Error", "Please enter valid numeric values for thresholds and price!")

    def _on_cancel(self):
        self._result = None
        self.destroy()

    def get_result(self):
        return self._result
