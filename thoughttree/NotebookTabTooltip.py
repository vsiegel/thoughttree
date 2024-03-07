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


    def refresh(self, event=None):
        if self.tip:
            local_x = self.root.winfo_pointerx() - self.notebook.winfo_rootx()
            local_y = self.root.winfo_pointery() - self.notebook.winfo_rooty()
            identification = self.notebook.identify(local_x, local_y)
            print(f"{identification=}")

            if identification:
                index_location = f"@{local_x},{local_y}"
                index = self.notebook.index(index_location)
                text = self.notebook.tab(index, "text")
                self.label.configure(text=text)

                pointer_x = self.root.winfo_pointerx()
                y = self.notebook.winfo_rooty() + 25
                geometry = f"+{pointer_x}+{y}"
                print(f"{ pointer_x=}, {y=} {geometry=}")
                self.tip.wm_geometry(geometry)
                self.tip.wm_attributes("-topmost", True)
                self.tip.deiconify()
            else:
                self.label.configure(text="(hidden)")
                self.tip.withdraw()
