from tkinter import ttk

ttk.Style().layout("NoBorder.TNotebook", [])


class Notebook(ttk.Notebook):
    def __init__(self, parent, style="NoBorder.TNotebook", takefocus=False, **kw):
        super().__init__(parent, style=style, takefocus=takefocus, **kw)
        self.enable_traversal()

