import tkinter as _tk


class ItemListView(_tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

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

        # Create placeholder buttons
        for i in range(30):
            button = _tk.Button(
                self._scrollable_frame,
                text=f"Item {i + 1}",
                height=2,
                bg="#f0f0f0",
                relief="flat"
            )
            button.pack(fill="x", padx=0, pady=2)

    def _on_frame_configure(self, event=None):
        self._canvas.itemconfig("expand", width=self.winfo_width())

        bbox = self._canvas.bbox("all")
        if bbox:
            canvas_height = self._canvas.winfo_height()
            if bbox[3] < canvas_height:
                bbox = (bbox[0], bbox[1], bbox[2], canvas_height)
            self._canvas.configure(scrollregion=bbox)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
