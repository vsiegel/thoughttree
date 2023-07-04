import tkinter as tk

from Text import Text
from Tooltip import Tooltip


class FinishReasonIcon(tk.Label):
    def __init__(self, text: Text, symbol: str, tooltip=""):
        super().__init__(text, text=symbol, padx=6, pady=0, bg="#F0F0F0", fg="grey", borderwidth=0)
        if tooltip:
            Tooltip(self, tooltip).delay_ms = 100
