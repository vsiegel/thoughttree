import tkinter as tk


class NotebookAdapterFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent) # Warning: Naming the frame causes errors (name="...").
        self.forkable_sheet = None
