import tkinter as tk
from tkinter import ttk

from Notebook import Notebook


class ResizingText(tk.Text):
    def __init__(self, parent, wrap="word", highlightthickness=0, borderwidth=0, padx=0, pady=0, *args, **kwargs):
        super().__init__(parent, wrap=wrap, highlightthickness=highlightthickness, borderwidth=borderwidth, padx=padx, pady=pady, *args, **kwargs)
        self.bind("<KeyRelease>", self.adjust_height)

        def on_return(event=None):
            self.insert(tk.INSERT, "\n")
            self.adjust_height()
            return "break"

        self.bind("<Return>", on_return)

        self.old_num_lines = 0
        self.adjust_height()

    def adjust_height(self, event=None):
        num_lines = self.count("1.0", "end", 'displaylines')[0]
        if num_lines != self.old_num_lines:
            print(f"Change {self.old_num_lines} -> {num_lines}")
            self.old_num_lines = num_lines
            self.configure(height=num_lines)
            if type(self.master) is Notebook:
                self.master.event_generate("<<NotebookTabChanged>>")
