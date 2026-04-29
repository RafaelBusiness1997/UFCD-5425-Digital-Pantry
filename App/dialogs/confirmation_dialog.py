import tkinter as _tk

class ConfirmationDialog(_tk.Toplevel):
    """A confirmation dialog with confirm and cancel options."""

    def __init__(self, parent, title="Confirmation", message="Are you sure?", on_confirm_callback=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x150")
        self.resizable(False, False)
        self.result = None
        self._on_confirm_callback = on_confirm_callback

        # Center the dialog on the parent window
        self.transient(parent)
        self.grab_set()

        # Message label
        message_label = _tk.Label(
            self,
            text=message,
            font=("Arial", 10),
            wraplength=320,
            justify="center",
            bg="#ffffff"
        )
        message_label.pack(pady=20, padx=20)

        # Button frame
        button_frame = _tk.Frame(self, bg="#ffffff")
        button_frame.pack(pady=15)

        # Confirm button
        confirm_button = _tk.Button(
            button_frame,
            text="Confirm",
            bg="#40c440",
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
            bg="#d9534f",
            fg="white",
            font=("Arial", 10),
            width=10,
            command=self._on_cancel
        )
        cancel_button.pack(side="left", padx=5)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (350 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (150 // 2)
        self.geometry(f"350x150+{x}+{y}")

    def _on_confirm(self):
        """Handle confirm button click."""
        self.result = True
        if self._on_confirm_callback:
            self._on_confirm_callback()
        self.destroy()

    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = False
        self.destroy()
