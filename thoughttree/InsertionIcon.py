from pathlib import Path
from tkinter import PhotoImage, INSERT
import tkinter as tk

from Sheet import Sheet


class InsertionIcon(tk.Label):
    def __init__(self, master: Sheet, insertion_point=INSERT):
        tk.Label.__init__(self, master)
        self.sheet = master
        self.insertion_point = insertion_point
        self.image = PhotoImage(file=Path(__file__).resolve().parent / "chatgpt-24x24.png")
        self.config(image=self.image)


    def __enter__(self):
        self.sheet.mark_gravity(self.insertion_point, tk.LEFT)
        self.sheet.window_create(self.insertion_point, window=self)
        self.sheet.mark_gravity(self.insertion_point, tk.RIGHT)
        self.update()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sheet.delete(str(self), str(self) + " +1c")
