import tkinter as tk

class Dragability:
# Make a overrideredirect window draggable.
    def __init__(self, dragged):
        self.dragged: tk.Toplevel = dragged
        self.x = 0
        self.y = 0
        self.startX = None
        self.startY = None
        self.dragged.bind('<Button-1>', self.start_move, add=True)
        self.dragged.bind('<ButtonRelease-1>', self.stop_move, add=True)
        self.dragged.bind('<B1-Motion>', self.do_move, add=True)



    def start_move(self, event):
        self.startX = event.x
        self.startY = event.y

    def stop_move(self, event):
        self.startX = None
        self.startY = None

    def do_move(self, event):
        x = self.dragged.winfo_x() - self.startX + event.x
        y = self.dragged.winfo_y() - self.startY + event.y
        self.dragged.geometry(f"+{x}+{y}")
