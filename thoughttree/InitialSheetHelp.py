import tkinter as tk
from tkinter import INSERT

from Fonts import Fonts
from Sheet import Sheet
from Tooltip import Tooltip
from tools import text_block


class InitialSheetHelp(tk.Label):
    def __init__(self, sheet: Sheet, text:str, tooltip="", active=True):
        super().__init__(sheet, text=text, padx=0, pady=0, bg="white", fg="#b3b3b3", borderwidth=0, font=(Fonts.FONT_NAME_PROPORTIONAL, 13))
        if tooltip:
            Tooltip(self, text_block(tooltip)).show_delay_ms = 100

        self.sheet = sheet
        self.bind_modified = None
        self.bind("<Button-1>", self.dismiss)
        self.place(x=30, y=30)

        if active:
            self.activate()

    def dismiss(self, e=None):
        self.sheet.initially_modified = True
        if self.bind_modified:
            self.sheet.unbind('<<Modified>>', self.bind_modified)
        self.destroy()

    def activate(self):
        self.bind_modified = self.sheet.bind('<<Modified>>', self.dismiss, add=True)

