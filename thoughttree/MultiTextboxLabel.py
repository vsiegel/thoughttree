import tkinter as tk
from tkinter import LEFT, SUNKEN, X, TOP, W

from Fonts import Fonts
from Sheet import Sheet


class MultiTextboxLabel(tk.Label):
    def __init__(self, parent=None, sheet=None, **kw):
        borderwidth = 4
        super().__init__(parent, borderwidth=borderwidth, anchor=W, wraplength=sheet.winfo_width() - borderwidth * 2,
                         justify=LEFT, font=Fonts.FONT, relief=SUNKEN)
        self.pack(side=TOP, fill=X, expand=True)
