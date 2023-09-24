import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END

from Notebook import Notebook
from Sheet import Sheet
from Title import new_child_title, new_sibling_title, short


class ForkableSheet(Sheet):
    def __init__(self, parent, *args, **kw):
        self.fork_frame = tk.Frame(parent, name="fork_frame")
        self.fork_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        Sheet.__init__(self,  self.fork_frame, height=1, width=1000, scrollbar=False, grow=True, background="white",  *args, **kw)
        self.pack(side=tk.TOP, fill=BOTH, expand=True)
        self.notebook = None


    def create_notebook(self):
        if not self.notebook:
            print(f"create_notebook")
            self.notebook = Notebook(self.fork_frame)
            self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.pack_configure(expand=False)


    def fork(self, index=INSERT):
        index = self.index(index)

        has_leading_text = bool(self.get("1.0", index).strip())
        parent = self.find_parent(Notebook)

        # print(f"{parent=}")
        # print(f"{has_leading_text=}")
        if not parent:
            self.create_notebook()
            notebook = self.notebook
            # parent = self.notebook
            trailing_text = self.get(index, END).rstrip()
            tab_name = new_child_title(notebook)
            sheet = self.notebook.add_sheet(tab_name)
            sheet.insert("1.0", trailing_text)
            self.delete(index + "+1char", END)
        elif has_leading_text:
            self.create_notebook()
            notebook = self.notebook
            tab_name = new_child_title(parent)
            sheet = self.notebook.add_sheet(tab_name)
        else:
            notebook = parent

        # self.create_notebook_tab(new_sibling_title(notebook))
        tab_name2 = new_sibling_title(notebook)
        sheet = notebook.add_sheet(tab_name2)
        # self.create_notebook_tab(tab_name2, "self.create_notebook_tab(new_sibling_title(parent)")
        return "break"



