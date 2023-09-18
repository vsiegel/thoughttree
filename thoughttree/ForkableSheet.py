import tkinter as tk
from tkinter import X, BOTH, Y

from Notebook import Notebook
from Sheet import Sheet


class ForkableSheet(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)
        self.sheet = Sheet(self, height=1, scrollbar=False, grow=True, background="white",  *args, **kw)
        self.sheet.pack(side=tk.TOP, fill=BOTH, expand=True, anchor=tk.N)

        self.notebook = None
        # self.notebook = Notebook(self,)# background="lightgreen")
        # self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)

        self.sheet.bind("<Control-o>", self.fork_mock)


    def fork_mock(self, event=None):
        if not self.notebook:
            self.notebook = Notebook(self)
            self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.sheet.pack_configure(expand=False)

        frame1 = tk.Frame(self.notebook)
        text_tab1 = ForkableSheet(frame1)
        text_tab1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        text_tab2 = ForkableSheet(self.notebook)
        self.notebook.add(frame1, text="1 Tab", sticky=tk.N+tk.E+tk.S+tk.W)
        self.notebook.add(text_tab2, text="2 Tab", sticky=tk.N+tk.E+tk.S+tk.W)
        self.notebook.add(ForkableSheet(self.notebook), text="3 Tab")
        return "break"
