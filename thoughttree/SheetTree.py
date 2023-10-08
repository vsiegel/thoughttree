import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP

from ForkableSheet import ForkableSheet
from Sheet import Sheet
from tools import on_event, bind_tree, iterate_tree


class SheetTree(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, name="sfs", *args, **kw)

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, name="c")# background="lightcyan")
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)
        def scrollbar_set(*args):
            print(f"#### {args}")
            self.scrollbar.set(*args)
        self.canvas.configure(yscrollcommand=scrollbar_set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        canvas_frame = tk.Frame(self.canvas, bd=0, background="#eeeeff", name="cf")
        self.canvas_id = self.canvas.create_window((0, 0), window=canvas_frame, anchor=NW)

        self.forkable_sheet = ForkableSheet(canvas_frame)
        self.forkable_sheet.pack(side=TOP, expand=True, fill=BOTH)

        def on_mousewheel(event):
            delta = (event.num == 5 and 1 or -1)
            print(f"on_mousewheel: {event} {delta=} {self.canvas.winfo_containing(event.x_root, event.y_root)} {self.canvas}")
            self.canvas.yview_scroll(delta, "units")
            str(self.canvas.winfo_containing(event.x_root, event.y_root)).startswith(str(self.canvas))
        self.winfo_toplevel().bind("<Button-4>", on_mousewheel)
        self.winfo_toplevel().bind("<Button-5>", on_mousewheel)

        self.forkable_sheet.bind("<Configure>", self.configure_scrollregion, add=True)
        self.canvas.bind("<Configure>", self.configure_frame, add=True)

    def configure_scrollregion(self, event):
        print(f"configure_scrollregion: {event} {type(event.widget)} {event.widget}")
        x, y, width, height = self.canvas.bbox("all")
        print(f"bbox: {(x, y, width, height)=}")

        self.canvas.configure(scrollregion=(x, y, width, height))
        print(f"canvas height: {self.canvas.configure('height')}")
        print(f"cwinfo height: {self.canvas.winfo_height()}")
        self.canvas.event_generate("<Configure>", x=x, y=y, width=width, height=height)
        # self.canvas.configure(scrollregion=(x, y, width, height), width=width, height=height)

    def configure_frame(self, event):
        print(f"configure_frame:        {event}")
        # height = max(self.canvas.winfo_height(), self.forkable_sheet.winfo_reqheight())
        height = self.forkable_sheet.winfo_reqheight()
        self.canvas.itemconfigure(self.canvas_id, width=event.width, height=height)


    def focus_set(self):
        self.forkable_sheet.focus_set()

if __name__ == "__main__":
    from Ui import Ui
    ui = Ui()
    ui.root.title("ScrollableForkableSheet")
    # ui.root.geometry("500x500")
    scrollable = SheetTree(ui.root)
    scrollable.pack(fill="both", expand=True)
    scrollable.forkable_sheet.focus()

    ui.root.mainloop()
