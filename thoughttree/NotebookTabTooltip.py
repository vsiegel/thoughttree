import tkinter as tk
from tkinter import ttk

from Tooltip import Tooltip
from tools import text_block
from menu_help_texts import menu_help
from tools import p

class NotebookTabTooltip(Tooltip):
    def __init__(self, notebook: ttk.Notebook, above=True):
        self.notebook: ttk.Notebook = notebook
        Tooltip.__init__(self, notebook, None, above=above)
        self.delay_ms = 750


    def bind_tip(self):
        self.notebook.bind("<Unmap>", self.hide, add=True)
        self.notebook.bind("<Destroy>", self.hide, add=True)
        self.notebook.bind("<Leave>", self.hide, add=True)
        self.notebook.bind("<Enter>", self.show_later, add=True)
        self.notebook.bind("<Motion>", self.refresh, add=True)
        # self.root.bind("<Motion>", self.refresh), add=True)


    def refresh_tooltip_text(self, event: tk.Event=None):
        notebook = self.notebook
        x = self.root.winfo_pointerx() - notebook.winfo_rootx()
        y = self.root.winfo_pointery() - notebook.winfo_rooty()
        identification = notebook.identify(x, y)
        if identification:
            index_location = f"@{x},{y}"
            index = notebook.index(index_location)
            text = notebook.tab(index, "text")
            self.label.configure(text=text)
