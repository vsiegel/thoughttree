import tkinter as tk
from tkinter import BOTTOM, X


class HidableFrame(tk.Frame):
    def __init__(self, master, hidden=False, *args, **kw):
        super().__init__(master, *args, **kw)
        self.hidden = hidden
        self.child_pack_info = None
        self.own_pack_info = None


    def hide(self, e=None):
        child = list(self.children.values())[0]
        if self.hidden:
            other = [slave for slave in self.master.pack_slaves() if slave != self][0]
            self.pack(self.own_pack_info, before=other)
        else:
            self.own_pack_info = self.pack_info()
            self.pack_forget()
        self.hidden = not self.hidden
