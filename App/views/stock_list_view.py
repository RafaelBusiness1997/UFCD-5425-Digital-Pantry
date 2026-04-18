import tkinter as _tk

class StockListView(_tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._test_label = _tk.Label(self, text="Stock List")
        self._test_label.pack(side="top", expand=True)
