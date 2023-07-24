import tkinter as tk
from tkinter import BOTTOM, X


class HidableFrame(tk.Frame):
    def __init__(self, master, hidden=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.hidden = hidden
        self.child_pack_info = None
        def on_move(self):
            print(f"{self}")
        self.bind("<Configure>", on_move)

    def hide(self, e=None):
        # child = self.children[list(self.children.keys())[0]]
        child = list(self.children.values())[0]
        if self.hidden:
            child.pack(self.child_pack_info)
        else:
            self.child_pack_info = child.pack_info()
            print(f"{self.child_pack_info}")
            child.pack_forget()
            self.pack(side=BOTTOM, fill=X, expand=False)

        self.hidden = not self.hidden
