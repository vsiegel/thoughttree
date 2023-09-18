import tkinter as tk
from tkinter import X, BOTH, Y, INSERT

from Notebook import Notebook
from Sheet import Sheet


class ForkableSheet(Sheet):
    def __init__(self, parent, *args, **kw):
        self.fork_frame = tk.Frame(parent)
        self.fork_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        Sheet.__init__(self,  self.fork_frame, height=1, width=1000, scrollbar=False, grow=True, background="white",  *args, **kw)
        self.pack(side=tk.TOP, fill=BOTH, expand=True)

        self.notebook = None
        self.bind("<Control-o>", self.fork_mock)


    def create_notebook(self):
        self.notebook = Notebook(self.fork_frame)
        self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.pack_configure(expand=False)

    def create_notebook_tab(self, title, text):
        if not self.notebook:
            self.create_notebook()
        frame = tk.Frame(self.notebook)
        forkable_sheet = ForkableSheet(frame)
        forkable_sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        if text:
            forkable_sheet.insert(INSERT, text)
        self.notebook.add(frame, text=title)


    def fork_mock(self, event=None):
        if not self.notebook:
            self.create_notebook()

        frame = tk.Frame(self.notebook)
        forkable_sheet = ForkableSheet(frame)
        forkable_sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.notebook.add(frame, text="Frame Tab")

        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="3 Tab")
        forkable_sheet = ForkableSheet(frame)
        forkable_sheet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        return "break"


