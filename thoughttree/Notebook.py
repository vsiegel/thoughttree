import tkinter as tk
from tkinter import ttk, END

from NotebookAdapterFrame import NotebookAdapterFrame


class Notebook(ttk.Notebook):
    def __init__(self, parent_widget, parent_sheet=None, parent_notebook=None, styleName=None, takefocus=False, background="white", **kw):
        self.parent_sheet = parent_sheet
        self.parent_notebook = parent_notebook
        if not styleName:
            styleName = "NoBorder.TNotebook"
            style = ttk.Style()
            style.layout(styleName, [])
            style.configure(styleName, bd=0, highlightthickness=0, background=background)
        super().__init__(parent_widget, style=styleName, takefocus=takefocus, **kw)
        self.enable_traversal()
        self.winfo_toplevel().unbind('<Control-Tab>')

    def add_sheet(self, title, parent_sheet=None):
        adapter_frame = NotebookAdapterFrame(self)
        adapter_frame.pack_propagate(False)
        from ForkableSheet import ForkableSheet
        sheet = ForkableSheet(adapter_frame, parent_sheet,  self)
        sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        adapter_frame.forkable_sheet = sheet
        self.insert(END, adapter_frame, text=title)
        self.select(adapter_frame)
        sheet.focus_set()
        return sheet

    def selected_sheet(self):
        if not self.select():
            return None
        sheet = self.nametowidget(self.select()).forkable_sheet
        print(f"selected_sheet {sheet=}")
        return sheet

    def child_sheets(self):
        frames = map(self.nametowidget, self.tabs())
        return [f.forkable_sheet for f in frames]

