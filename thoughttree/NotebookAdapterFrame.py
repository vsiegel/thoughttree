import tkinter as tk


class NotebookAdapterFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.forkable_sheet = None
