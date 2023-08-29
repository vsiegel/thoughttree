import tkinter as tk
from tkinter import X

from Notebook import Notebook
from ResizingText import ResizingText
from Sheet import Sheet
from tools import next_pastel_rainbow_color


class ForkableSheet(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.sheet = Sheet(self, height=1, scrollbar=False, grow=True)
        self.sheet.pack(side=tk.TOP, fill=X, expand=False)

        self.notebook = Notebook(self)
        self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.sheet.bind("<Control-o>", self.fork)

    def fork(self, event=None):
        text_tab1 = ForkableSheet(self.notebook)
        text_tab2 = ForkableSheet(self.notebook)
        self.notebook.add(text_tab1, text="Tab 1")
        self.notebook.add(text_tab2, text="Tab 2")
        return "break"

if __name__ == "__main__":
    from Ui import Ui
    ui = Ui()
    ui.root.title("ScrollableForkableSheet")
    # ui.root.geometry("500x500")
    scrollable = Sheet(ui.root, scrollbar=False, grow=True)
    scrollable.pack(fill="both", expand=True)
    # scrollable.sheet.sheet.focus()
    scrollable.focus()

    ui.root.mainloop()
