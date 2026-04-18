import tkinter as tk
from views.view_controller import ViewController
from database.main_db import MainDB

_db = MainDB()

_tk_root = tk.Tk()
_tk_root.title("Digital Pantry")

ViewController(_tk_root)

_tk_root.mainloop()
