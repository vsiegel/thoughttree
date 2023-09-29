import tkinter as tk
from tkinter import ttk, END


class Notebook(ttk.Notebook):
    def __init__(self, parent, styleName=None, takefocus=False, background="white", **kw):
        if not styleName:
            styleName = "NoBorder.TNotebook"
            style = ttk.Style()
            style.layout(styleName, [])
            style.configure(styleName, bd=0, highlightthickness=0, background=background)
        super().__init__(parent, style=styleName, takefocus=takefocus, **kw)
        self.enable_traversal()
        self.winfo_toplevel().unbind('<Control-Tab>')

    def add_sheet(self, title):
        frame = tk.Frame(self)
        from ForkableSheet import ForkableSheet
        sheet = ForkableSheet(frame)
        sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.insert(END, frame, text=title)
        self.select(frame)
        sheet.focus_set()
        return sheet

    def selected_sheet(self):
        if not self.select():
            return None
        return self.nametowidget(self.select())

    def child_sheets(self):
        frames = map(self.nametowidget, self.tabs())
        return [list(f.children.values())[0] for f in frames]

