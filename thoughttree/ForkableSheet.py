import sys
import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END

from IterateRangeForm import IterateRangeForm
from Notebook import Notebook
from Sheet import Sheet
from Title import new_child_title, new_sibling_title, short


class ForkableSheet(Sheet):
    def __init__(self, parent, *args, **kw):
        self.fork_frame = tk.Frame(parent, name="fork_frame")
        self.fork_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        Sheet.__init__(self,  self.fork_frame, height=1, width=250, scrollbar=False, grow=True, background="white", *args, **kw)
        self.pack(side=tk.TOP, fill=BOTH, expand=True)
        self.notebook = None


    def create_notebook(self):
        if not self.notebook:
            print(f"create_notebook")
            self.notebook = Notebook(self.fork_frame)
            self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            # self.pack_configure(expand=False)


    def fork(self, index=INSERT):
        index = self.index(index)

        has_leading_text = bool(self.get("1.0", index).strip())
        parent = self.parent_notebook()

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



if __name__ == "__main__":
    root = tk.Tk()
    # root.geometry("500x500")
    root.title(short(__file__))
    frame = tk.Frame(root)
    frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    forkable_sheet = ForkableSheet(frame)
    forkable_sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def grow_to_displaylines(event: tk.Event):
        if not event.widget.edit_modified():
            return
        sheet:ForkableSheet = event.widget
        ypixels = sheet.count("1.0", "end lineend", 'ypixels')[0]

        if sheet.notebook:
            height = sheet.notebook.winfo_height()
            print(f"{height=}")
            print(f"{sheet.winfo_height()=}")
            print(f"{ypixels=}")
            ypixels += sheet.notebook.winfo_height()

        width = sheet.winfo_width()

        frame.pack_propagate(0)
        frame.configure(height=ypixels, width=width)
        # root.configure(height=ypixels)
        # sheet.frame.event_generate("<Configure>", x=1, y=0, width=width, height=ypixels)
        # sheet.event_generate("<Configure>", x=1, y=0, width=width, height=ypixels)
        # sheet.update()
        # sheet.event_generate("<<ScrollRegionChanged>>")

        sheet.edit_modified(False)

    forkable_sheet.bind('<<Modified>>', grow_to_displaylines, add=True)
    IterateRangeForm(forkable_sheet)

    root.bind('<Escape>', lambda e: sys.exit(0))
    forkable_sheet.bind("<Control-Alt-f>", lambda e: forkable_sheet.fork())
    forkable_sheet.focus_set()
    root.mainloop()
