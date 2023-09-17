import tkinter as tk
from tkinter import X, BOTH

from Notebook import Notebook
from Sheet import Sheet


class ForkableSheet(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.old_num_display_lines = 0
        self.sheet = Sheet(self, height=1, scrollbar=False, grow=True,  *args, **kw)
        self.sheet.pack(side=tk.TOP, fill=X, expand=True, anchor=tk.N)

        self.notebook = Notebook(self, background="lightgreen")
        self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        def debug(event=None):
            print(self.focus_get())

        self.sheet.bind("<Control-o>", self.fork_mock)
        self.sheet.bind_all("<Control-d>", debug)


    def fork_mock(self, event=None):
        frame1 = tk.Frame(self.notebook)
        text_tab1 = ForkableSheet(frame1)
        text_tab1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        text_tab2 = ForkableSheet(self.notebook)
        self.notebook.add(frame1, text="1 Tab", sticky=tk.N+tk.E+tk.S+tk.W)
        self.notebook.add(text_tab2, text="2 Tab", sticky=tk.N+tk.E+tk.S+tk.W)
        self.notebook.add(ForkableSheet(self.notebook), text="3 Tab")
        # text_tab1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # print(f"{text_tab1.master=}")
        # print(f"{text_tab1.winfo_parent()=}")
        text_tab1.configure(background="yellow")
        return "break"

if __name__ == "__main__":
    from Ui import Ui
    ui = Ui()
    ui.root.geometry("500x500")
    scrollable = ForkableSheet(ui.root)
    scrollable.pack(fill="both", expand=True)
    scrollable.sheet.focus()

    ui.root.mainloop()
