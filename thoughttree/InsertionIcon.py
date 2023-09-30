from pathlib import Path
from tkinter import PhotoImage
import tkinter as tk

class InsertionIcon(tk.Label):
    def __init__(self, master=None):
        tk.Label.__init__(self, master)
        self.image = PhotoImage(file=Path(__file__).resolve().parent / "chatgpt-24x24.png")
        self.config(image=self.image)

