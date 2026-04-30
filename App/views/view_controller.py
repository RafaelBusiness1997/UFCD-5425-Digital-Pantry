'''Contains the ViewsController class, which manages the different views of the application.'''
import tkinter as tk
from views.item_list_view import ItemListView
from views.stock_list_view import StockListView
from views.shopping_list_view import ShoppingListView

class ViewController(tk.Frame):
    '''Initializes the different views, and manages the buttons to switch between them.'''
    def __init__(self, parent):
        super().__init__(parent, width="600", height="800")

        # Setup views.
        self.propagate(False)
        self.pack(fill="both", expand=True)

        self._stock_list_view = StockListView(self)
        self._shopping_list_view = ShoppingListView(self, self._stock_list_view)
        self._item_list_view = ItemListView(self, self._stock_list_view, self._shopping_list_view)
        
        self._stock_list_view._shopping_list_view = self._shopping_list_view

        # Setup buttons.
        self._button_frame = tk.Frame(self)
        self._button_frame.pack(side="bottom", fill="x")

        self._item_list_button = tk.Button(
            self._button_frame,
            text="Items",
            bg="#FFFFFF",
            fg="black",
            command=lambda: self._on_button_click(self._item_list_view, self._item_list_button)
        )
        self._stock_list_button = tk.Button(
            self._button_frame,
            text="Stock",
            bg="#FFFFFF",
            fg="black",
            command=lambda: self._on_button_click(self._stock_list_view, self._stock_list_button)
        )
        self._shopping_list_button = tk.Button(
            self._button_frame,
            text="Shopping List",
            bg="#FFFFFF",
            fg="black",
            command=lambda: self._on_button_click(self._shopping_list_view, self._shopping_list_button)
        )

        self._item_list_button.pack(side="left", expand=True, fill="x")
        self._stock_list_button.pack(side="left", expand=True, fill="x")
        self._shopping_list_button.pack(side="left", expand=True, fill="x")

        # Initialize state.
        self._active_view = None
        self._active_button = None
        self._switch_view(self._stock_list_view)
        self._update_button_style(self._stock_list_button)

    def _on_button_click(self, view, button):
        self._switch_view(view)
        self._update_button_style(button)
        self._stock_list_view.deselect_item()
        self._item_list_view.deselect_item()
        self._shopping_list_view.unselect_all()

    def _switch_view(self, view):
        if self._active_view:
            if self._active_view == view:
                return
            else:
                self._active_view.pack_forget()

        self._active_view = view
        self._active_view.pack(fill="both", expand=True)

    def _update_button_style(self, button):
        if self._active_button == button:
            return

        if self._active_button is not None:
            self._active_button.configure(bg="#FFFFFF", fg="black")

        self._active_button = button
        self._active_button.configure(bg="#96862A", fg="black")
