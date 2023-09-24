import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END

from Notebook import Notebook
from Sheet import Sheet
from Title import new_child_title, new_sibling_title


class ForkableSheet(Sheet):
    def __init__(self, parent, *args, **kw):
        self.fork_frame = tk.Frame(parent, name="fork_frame")
        self.fork_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        Sheet.__init__(self,  self.fork_frame, height=1, width=1000, scrollbar=False, grow=True, background="white",  *args, **kw)
        self.pack(side=tk.TOP, fill=BOTH, expand=True)
        self.notebook = None


    def create_notebook(self):
        print(f"create_notebook")
        self.notebook = Notebook(self.fork_frame)
        self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.pack_configure(expand=False)

    def create_notebook_tabTTT(self, title='-', text=''):
        if not self.notebook:
            self.create_notebook()
        button = tk.Button(self.notebook, text=title)
        self.notebook.add(button, text=title)

    def create_notebook_tab(self, title='-', text=''):
        if not self.notebook:
            self.create_notebook()
        frame = tk.Frame(self.notebook, name="forkableSheet_frame")
        forkable_sheet = ForkableSheet(frame)
        forkable_sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        if text:
            forkable_sheet.insert("1.0", text)
            forkable_sheet.mark_set(INSERT, "1.0")
        self.notebook.add(frame, text=title)
        self.notebook.select(frame)

        # print(f"{self.notebook.index(forkable_sheet.master.master.master)}")
        forkable_sheet.focus_set()

    def fork(self, index=INSERT):
        index = self.index(index)

        has_leading_text = bool(self.get("1.0", index).strip())
        parent = self.find_parent(Notebook)

        print(f"{parent=}")
        print(f"{has_leading_text=}")
        if not parent or has_leading_text:
            trailing_text = self.get(index, END).rstrip()
            tab_name = new_child_title(parent) + " test"
            print(f"{tab_name=}")
            self.create_notebook_tab(tab_name, trailing_text)
            self.delete(index + "+1char", END)

        # self.create_notebook_tab(new_sibling_title(notebook))
        tab_name2 = new_sibling_title(parent)
        print(f"{tab_name2=}")
        self.create_notebook_tab(tab_name2, "self.create_notebook_tab(new_sibling_title(parent)")

        return "break"



