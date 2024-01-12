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


    def add_sheet(self, title, parent_sheet=None):
        class NAF(tk.Frame):  # NotebookAdapterFrame - the name appears in widget names, making them longer.
            def __init__(self, parent):
                tk.Frame.__init__(self, parent)  # Warning: Naming the frame causes errors (name="...").
                self.forkable_sheet = None
        NotebookAdapterFrame = NAF

        print(f"add_sheet start {title=} {len(self.tabs())=}")
        adapter_frame = NotebookAdapterFrame(self)
        # adapter_frame.pack_propagate(False)
        print(f"add_sheet 2 {title=} {len(self.tabs())=}")
        from ForkableSheet import ForkableSheet
        sheet = ForkableSheet(parent_frame=adapter_frame, parent_sheet=parent_sheet, parent_notebook=self, name=title.replace(".", "_"))
        sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        adapter_frame.forkable_sheet = sheet
        self.insert(END, adapter_frame, text=title)
        self.select(adapter_frame)
        sheet.focus_set()
        return sheet


    def selected_sheet(self):
        if not self.select():
            return None
        sheet = self.nametowidget(self.select()).sheet
        return sheet

    def child_sheets(self):
        frames = map(self.nametowidget, self.tabs())
        return [f.sheet for f in frames]

