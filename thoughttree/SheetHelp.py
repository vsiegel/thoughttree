import tkinter as tk
from tkinter import INSERT

from Sheet import Sheet
from Tooltip import Tooltip
from tools import text_block


class SheetHelp(tk.Label):
    def __init__(self, sheet: Sheet, text:str, tooltip=""):
        super().__init__(sheet, text=text, padx=0, pady=0, bg="white", fg="#b3b3b3", borderwidth=0)
        if tooltip:
            Tooltip(self, text_block(tooltip)).delay_ms = 100
        sheet.window_create("1.2", window=self)
        # sheet.mark_set(INSERT, f"1.0")
        def remove(event=None):
            if sheet.dump('1.0', 'end', window=True):
                sheet.delete(self, f"{self}+1c")

        self.bind("<Button-1>", remove)
        bind_modified = sheet.bind('<<Modified>>', lambda e: hide(e), add=True)
        def hide(e=None):
            remove(e)
            sheet.unbind('<<Modified>>', bind_modified)
