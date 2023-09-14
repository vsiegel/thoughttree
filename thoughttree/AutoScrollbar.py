import tkinter as tk
from tkinter import RIGHT, Y


class AutoScrollbar(tk.Scrollbar):
    def __init__(self, parent, **kw):
        tk.Scrollbar.__init__(self, parent, **kw)

    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            # self.tk.call("grid", "remove", self)
            self.pack_forget()
        else:
            # self.grid()
            self.pack(side=RIGHT, fill=Y)
        tk.Scrollbar.set(self, low, high)
