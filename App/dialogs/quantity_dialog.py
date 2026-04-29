import tkinter as _tk
from tkinter import messagebox


class QuantityDialog(_tk.Toplevel):
    """Dialog for editing item quantity."""
    
    def __init__(self, parent, current_quantity, on_save_callback=None):
        """
        Initialize the quantity dialog.
        
        Args:
            parent: Parent window
            current_quantity: The current quantity value
            on_save_callback: Callback function to execute when confirmed
        """
        super().__init__(parent)
        self.title("Edit Quantity")
        self.geometry("350x150")
        self.resizable(False, False)
        
        # Center the dialog on the parent window
        self.transient(parent)
        self.grab_set()
        
        self._on_save_callback = on_save_callback
        
        # Intercept window close button
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Label
        label = _tk.Label(
            self,
            text="Enter new quantity:",
            font=("Arial", 10),
            bg="#ffffff"
        )
        label.pack(pady=10, padx=20)
        
        # Entry field
        self._quantity_var = _tk.StringVar(value=str(current_quantity))
        entry = _tk.Entry(
            self,
            textvariable=self._quantity_var,
            font=("Arial", 10),
            width=20
        )
        entry.pack(pady=5, padx=20)
        entry.focus()
        entry.select_range(0, _tk.END)
        
        # Button frame
        button_frame = _tk.Frame(self, bg="#ffffff")
        button_frame.pack(pady=15)
        
        # Confirm button
        confirm_button = _tk.Button(
            button_frame,
            text="Confirm",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10),
            width=10,
            command=self._on_confirm
        )
        confirm_button.pack(side="left", padx=5)
        
        # Cancel button
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
        
        # Center and position the dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (350 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (150 // 2)
        self.geometry(f"350x150+{x}+{y}")
    
    def _on_confirm(self):
        """Handle confirm button click."""
        try:
            quantity = int(self._quantity_var.get())
            if quantity <= 0:
                messagebox.showwarning("Warning", "Quantity must be greater than 0!")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid quantity!")
            return
        
        if self._on_save_callback:
            self._on_save_callback(quantity)
        
        self.destroy()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.destroy()
