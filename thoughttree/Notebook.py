import tkinter as tk
from tkinter import ttk, END

from NotebookAdapterFrame import NotebookAdapterFrame


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
        print(f"add_sheet start {title=} {len(self.tabs())=}")
        adapter_frame = NotebookAdapterFrame(self)
        adapter_frame.pack_propagate(False)
        print(f"add_sheet 2 {title=} {len(self.tabs())=}")
        from ForkableSheet import ForkableSheet
        sheet = ForkableSheet(parent_frame=adapter_frame, parent_sheet=parent_sheet, parent_notebook=self, name=title.replace(".", "_"))
        sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        adapter_frame.forkable_sheet = sheet
        self.insert(END, adapter_frame, text=title)
        self.select(adapter_frame)
        sheet.focus_set()
        return sheet

    def winfo_reqheight(self):
        reqheight = super().winfo_reqheight()
        # print(f"nb super {reqheight=}")
        selected_sheet = self.selected_sheet()
        if selected_sheet:
            reqheight += selected_sheet.winfo_reqheight()
        # print(f"nb sheet {reqheight=}")
        return reqheight

    def selected_sheet(self):
        if not self.select():
            return None
        sheet = self.nametowidget(self.select()).forkable_sheet
        return sheet

    def child_sheets(self):
        frames = map(self.nametowidget, self.tabs())
        return [f.forkable_sheet for f in frames]

