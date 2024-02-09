import tkinter as tk

import tools
from Dragability import Dragability


class Ruler(tk.Toplevel):

    def __init__(self, parent, *values_and_labels, offset=0):
        super().__init__(background="#76838c")
        self.parent = parent
        self.offset = offset
        self.overrideredirect(True)
        self.geometry("200x1600+2000+0")
        self.canvas = tk.Canvas(self, width=200, height=1600, background="#a4b8c4")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        Dragability(self)
        # self.reset()
        # self.ticks(*values_and_labels)
        # def on_button1(event):
        #     print(event.x, event.y)
        # self.bind('<Button-1>', on_button1, add=True)
        # def on_button3(event):
        #     print(event.x, event.y)
        # self.bind('<Button-3>', on_button3, add=True)

    def ticks(self, *values_and_labels):
        for v, label, *color in values_and_labels:
            if color:
                color = color[0]
            self.tick(v, label, color=color)

    def tick(self, v, label="", color=None):
        print(f"{label + ':':15s} {v}")
        color = color or "black"
        s = v + self.offset
        for i, shift in enumerate([3, 0, 3], -1):
            self.canvas.create_line(0 + shift, s + i, 15, s + i, fill=color, tags=("clearable",))
        self.canvas.create_text(20, s - 12, text=str(v) + " " + label, anchor=tk.NW, fill=color, tags=("clearable",))

    def clear(self):
        self.canvas.delete("clearable")

    def cleared(self):
        self.clear()
        return self


if __name__ == "__main__":
    root = tk.Tk()
    # root.wm_withdraw()
    ruler = Ruler(root, (0, "0"), offset=0)

    tools.escapable(root)

    ruler.ticks((33, "dd"), (666,"sss"), (686,"ssss"))
    # widget.pack(side=LEFT, fill=BOTH, expand=True)
    # widget.branch()
    # widget.notebook.add(TreeSheet(widget.notebook))
    # widget.pack_propagate(False)
    ruler.canvas.focus_set()
    root.mainloop()
