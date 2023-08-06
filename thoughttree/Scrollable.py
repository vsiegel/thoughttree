import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y

from ForkableText import ForkableText


class Scrollable(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, bg="#fbfbfb", highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.frame = tk.Frame(self.canvas, bg="white")
        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor=NW)

        self.frame.bind("<Configure>", self.update_scrollregion)
        self.canvas.bind("<Configure>", self.update_frame_width)

    def update_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_frame_width(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width)

from Ui import Ui

class ScrollableTest(Ui):
    def __init__(self):
        super().__init__()

        self.root.title("Forkable Text")
        self.root.geometry("500x500")

        self.scrollable = Scrollable(self.root)
        self.forkable_text = ForkableText(self.scrollable.frame)

        self.scrollable.pack(fill="both", expand=True)
        self.forkable_text.pack(fill="both", expand=False)
        self.mainloop()


if __name__ == "__main__":
    ScrollableTest()
