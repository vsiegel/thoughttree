import tkinter as tk
from tkinter import ttk

from ForkableText import ForkableText


class Scrollable(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, bg="#fbfbfb", highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.frame = tk.Frame(self.canvas, bg="white")
        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", self.update_scrollregion)
        self.canvas.bind("<Configure>", self.update_frame_width)

    def update_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_frame_width(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width)


def main():
    from UI import UI
    root = UI()
    root.geometry("500x500")

    scrollable = Scrollable(root)
    scrollable.pack(fill="both", expand=True)

    forkable_text = ForkableText(scrollable.frame)
    forkable_text.pack(fill="both", expand=False)

    root.mainloop()

if __name__ == "__main__":
    main()
