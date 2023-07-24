import io
import tkinter as tk
import tkinter.scrolledtext
from tkinter import END


class Console(tk.scrolledtext.ScrolledText, io.TextIOBase):
    def __init__(self, master, width=100, height=5, **kw):
        tk.scrolledtext.ScrolledText.__init__(self, master, undo=True, wrap=tk.WORD, width=width, height=height,
            takefocus=False, font=("monospace", 8), **kw)
        io.TextIOBase.__init__(self)
        self.master = master
        self.vbar.config(width=18, takefocus=False, borderwidth=2)
        self.insert(END, "Console:\n")

    def write(self, message):
        self.insert(END, message)
        self.see(END)
