import tkinter as tk


class NotebookAdapterFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, name="naf")
        self.forkable_sheet = None
