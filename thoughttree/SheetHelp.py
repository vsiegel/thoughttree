import tkinter as tk

from Tooltip import Tooltip
from tools import text_block


class SheetHelp(tk.Label):
    def __init__(self, sheet: tk.Text, text, tooltip=""):
        super().__init__(sheet, text=text, padx=6, pady=0, bg="white", fg="#b3b3b3", borderwidth=0)
        if tooltip:
            Tooltip(self, text_block(tooltip)).delay_ms = 100
        sheet.window_create("1.0", window=self)
        def remove(event):
            print(f"{event=}")
            i = sheet.index(self)
            print(f"{i=}")
            sheet.delete(self, f"{self}+1c")
        self.bind("<Button-1>", remove)
