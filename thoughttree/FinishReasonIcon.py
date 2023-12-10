import tkinter as tk

from Tooltip import Tooltip


class FinishReasonIcon(tk.Label):
    def __init__(self, parent, symbol: str, tooltip=""):
        super().__init__(parent, text=symbol, padx=6, pady=0, bg="#F0F0F0", fg="grey", borderwidth=0)
        if tooltip:
            Tooltip(self, tooltip).show_delay_ms = 100
