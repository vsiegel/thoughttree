from tkinter import ttk

class Notebook(ttk.Notebook):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.enable_traversal()

