from tkinter import ttk



class Notebook(ttk.Notebook):
    def __init__(self, parent, styleName=None, takefocus=False, **kw):
        if not styleName:
            styleName = "NoBorder.TNotebook"
            style = ttk.Style()
            style.layout(styleName, [])
            style.configure(styleName, bd=0, highlightthickness=0, background="white")
        super().__init__(parent, style=styleName, takefocus=takefocus, **kw)
        self.enable_traversal()

