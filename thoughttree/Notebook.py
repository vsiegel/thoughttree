import tkinter as tk
from tkinter import ttk, END


class Notebook(ttk.Notebook):
    def __init__(self, parent_frame, parent_sheet=None, parent_notebook=None, style_name=None, takefocus=False, background="white", **kw):
        self.parent_sheet = parent_sheet
        self.parent_notebook = parent_notebook
        if not style_name:
            style_name = "NoBorder.TNotebook"
            style = ttk.Style()
            style.layout(style_name, [])
            style.configure(style_name, bd=0, highlightthickness=0, background=background)
        super().__init__(parent_frame, style=style_name, takefocus=takefocus, name="nb", **kw)
        self.enable_traversal()
        self.bind("<Button>", self.on_empty_tabbar, add=True)


    def add_sheet(self, title, parent_sheet=None):
        class NAF(tk.Frame):  # NotebookAdapterFrame - the name appears in widget names, making them longer.
            def __init__(self, parent, **kw):
                tk.Frame.__init__(self, parent)  # Warning: Naming the frame causes errors (name="...").
        NotebookAdapterFrame = NAF

        # NotebookAdapterFrame = NAF

        adapter_frame = NotebookAdapterFrame(self, background="#f0e5f2", borderwidth=0, highlightthickness=0)
        from TreeSheet import TreeSheet
        sheet = TreeSheet(adapter_frame, parent_sheet=parent_sheet, parent_notebook=self, name=title.replace(".", "_"))
        sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.insert(END, adapter_frame, text=title)
        self.select(adapter_frame)
        sheet.focus_set()
        return sheet


    def on_empty_tabbar(self, event):
        if not event.widget.identify(event.x, event.y):
            event.widget.tk_focusPrev().focus_set()


    def selected_sheet(self):
        if not self.select():
            return None
        frame = self.nametowidget(self.select())
        print(f"{frame=}")
        sheet = frame.sheet
        return sheet

    def child_sheets(self):
        frames = map(self.nametowidget, self.tabs())
        return [f.sheet for f in frames]

