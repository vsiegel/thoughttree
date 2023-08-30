import tkinter as tk
from tkinter import X

from Notebook import Notebook
from Sheet import Sheet


class ForkableSheet(tk.Frame):
    def __init__(self, parent, *args, **kw):
        # super().__init__(parent, scrollbar=False, *args, **kw)
        super().__init__(parent, *args, **kw)

        # self.frame.configure(takefocus=False)
        self.sheet = Sheet(self, height=1, scrollbar=False, grow=True)
        self.sheet.pack(side=tk.TOP, fill=X, expand=False)

        self.notebook = Notebook(self)
        self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        def debug(event=None):
            print(self.focus_get())


        self.sheet.bind("<Control-o>", self.fork_mock)
        self.sheet.bind_all("<Control-d>", debug)

    def fork_mock(self, event=None):
        text_tab1 = ForkableSheet(self.notebook)
        text_tab2 = ForkableSheet(self.notebook)
        self.notebook.add(text_tab1, text="Tab 1")
        self.notebook.add(text_tab2, text="Tab 2")
        return "break"

if __name__ == "__main__":
    from Ui import Ui
    ui = Ui()
    ui.root.geometry("500x500")
    scrollable = ForkableSheet(ui.root)
    scrollable.pack(fill="both", expand=True)
    scrollable.sheet.focus()

    ui.root.mainloop()
