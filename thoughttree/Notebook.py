import tkinter as tk
from tkinter import ttk, END, CURRENT

from NotebookTabTooltip import NotebookTabTooltip


#copy:
class NF(tk.Frame):  # NF short for NotebookFrame - the name appears in widget names, making them longer.
    def __init__(self, parent, name=None, **kw):
        tk.Frame.__init__(self, parent, name=name, **kw)
        self.sheet = None


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

        NotebookTabTooltip(self)
        # def on_empty_tab_bar(event):
        #     if not event.widget.identify(event.x, event.y):
        #         # event.widget.tk_focusPrev().focus_set()
        #         event.widget.parent_sheet.focus_set()
        # self.bind("<Button>", on_empty_tab_bar, add=True)
        #
        # def on_notebook_tab(event):
        #     if not event.widget.identify(event.x, event.y):
        #         # event.widget.tk_focusPrev().focus_set()
        #         event.widget.parent_sheet.focus_set()
        # self.bind("<Up>", on_notebook_tab, add=True)

        def on_up(event):
            notebook = event.widget
            if notebook.parent_sheet:
                notebook.parent_sheet.focus_bottom()
        self.bind("<Up>", on_up, add=True)

        def on_down(event):
            event.widget.selected_sheet().focus_top()
        self.bind("<Down>", on_down, add=True)

        def focus_sheet(event):
            event.widget.selected_sheet().focus_top()
        self.bind("<<NotebookTabChanged>>", focus_sheet)


    def add_sheet(self, title, parent_sheet=None):
        from TreeSheet import TreeSheet
        from Title import outline
        # class NAF(tk.Frame):  # NotebookAdapterFrame - the name appears in widget names, making them longer.
        # class NotebookAdapterFrame(tk.Frame):
        #     def __init__(self, parent, **kw):
        #         tk.Frame.__init__(self, parent, **kw)  # Warning: Naming the frame causes errors (name="...").
        #         self.sheet = None

        # NotebookAdapterFrame = NAF

        frame = NF(self, background="#f0e5f2", borderwidth=0, highlightthickness=0)
        sheet = TreeSheet(frame, parent_sheet=parent_sheet, parent_notebook=self, name=outline(title), takefocus=False)
        sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        frame.sheet = sheet
        self.insert(END, frame, text=title)
        self.select(frame)
        sheet.focus_set()
        return sheet


    def selected_sheet(self):
        if not self.select():
            return None
        frame = self.nametowidget(self.select())
        return frame.sheet

    def child_sheets(self):
        frames = map(self.nametowidget, self.tabs())
        return [f.sheet for f in frames]

    def change(self, offset):
        selection = (self.index(CURRENT) + offset) % self.index(END)
        print(f"change: {self.index(CURRENT) + offset=} {offset=} {self.index(END)=} { selection=}")
        # self.select(selection)

    next = lambda self: self.change(1)
    prev = lambda self: self.change(-1)

    def size(self):
        sum = 0
        for tab in self.tabs():
            print(f"nb.size: {type(tab)=}")

            sum += tab.size()
