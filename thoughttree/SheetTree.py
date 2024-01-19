import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP, NSEW

import Colors
import tools
from Sheet import Sheet
from TreeSheet import TreeSheet
from tools import on_event, bind_tree, iterate_tree


class SheetTree(tk.Frame):
    def __init__(self, parent, name="st", **kw):
        super().__init__(parent, highlightthickness=3, highlightcolor=Colors.highlight, name=name, **kw)

        self.canvas = tk.Canvas(self, name="c", background="#f5fff0")
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.frame = tk.Frame(self.canvas, bd=0, background="#eeeeff", name="cf")
        self.frame.bind("<Configure>", self.configure_scrollregion, add=True)

        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor=NW)


        self.sheet = ForkableSheet(parent_frame=self.frame, )
        self.sheet.pack(side=TOP, expand=True, fill=BOTH)

        self.add_scrolling()

        self.canvas.bind("<Configure>", self.configure_frame, add=True)

        self.winfo_toplevel().bind("<Control-Alt-Shift-S>", self.debug)


    def configure_frame(self, event):
        self.canvas.itemconfigure(self.frame_id, width=event.width, height=event.height)

    def configure_scrollregion(self, event):
        print(f"configure_scrollregion: {self} {self.canvas.bbox('all')=}")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def add_scrolling(self):
        def on_mousewheel(event):
            delta = (event.num == 5 and 1 or -1)
            if self.in_canvas(event.x_root, event.y_root):
                scroll_pos = self.canvas.yview()

                if (delta == -1 and scroll_pos[0] <= 0) or (delta == 1 and scroll_pos[1] >= 1):
                    return
                self.canvas.yview_scroll(delta, "units")

        self.winfo_toplevel().bind("<Button-4>", on_mousewheel)
        self.winfo_toplevel().bind("<Button-5>", on_mousewheel)

    def winfo_reqheight(self):
        return self.sheet.winfo_reqheight()

    def focus_set(self):
        self.sheet.focus_set()

    def in_canvas(self, x, y):
        return str(self.canvas.winfo_containing(x, y)).startswith(str(self.canvas))

    def update_tab_title(self, event=None):
        sheet = self.focus_get()
        if not str(sheet).startswith(str(self)):
            raise Exception(f"{sheet} is not in SheetTree")
        if not isinstance(sheet, ForkableSheet):
            raise Exception(f"{sheet} is not a ForkableSheet")
        sheet.update_tab_title()

    def debug(self, event):
        print(f"{event.widget}    {event.width}x{event.height}+{event.x}+{event.y}")
        print(f"{self.frame.winfo_height()   =}")
        print(f"{self.frame.winfo_reqheight()=}")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("100x200")
    tools.escapable(root)
    widget = TreeSheet(root)
    widget.pack(side=LEFT, fill=BOTH, expand=True)
    widget.pack_propagate(False)
    widget.focus_set()
    root.mainloop()
