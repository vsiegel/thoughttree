import tkinter as tk
from tkinter import LEFT, SUNKEN, X, TOP, W

from Fonts import Fonts
from ResizingSheet import ResizingSheet


class AlternativeLabel(tk.Label):
    def __init__(self, parent=None, sheet=None, **kw):
        borderwidth = 4
        super().__init__(parent, borderwidth=borderwidth, anchor=W, wraplength=sheet.winfo_width() - borderwidth * 4,
                         justify=LEFT, font=Fonts.FONT, relief=SUNKEN)
        self.pack(side=TOP, fill=X, expand=True)

class AlternativeSheet(ResizingSheet):
    def __init__(self, parent=None, borderwidth=0, **kw):
        super().__init__(parent, borderwidth=borderwidth, relief=SUNKEN, **kw)
        self.pack(side=TOP, fill=X, expand=True)

    def insert(self, index, chars, *args):
        super().insert("end-2c", chars, *args)
        self.see(index)
