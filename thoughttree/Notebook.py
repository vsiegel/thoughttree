from tkinter import ttk



class Notebook(ttk.Notebook):
    def __init__(self, parent, style=None, takefocus=False, **kw):
        if not style:
            style = "NoBorder.TNotebook"
            ttk.Style().layout("NoBorder.TNotebook", [])
        super().__init__(parent, style=style, takefocus=takefocus, **kw)
        self.enable_traversal()

