import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP

from ForkableSheet import ForkableSheet
from Sheet import Sheet
from tools import on_event, bind_tree, iterate_tree


class ScrollableForkableSheet(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, name="sf", *args, **kw)

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0,)# background="lightcyan")
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)

        def canvas_set(*args):
            # print(f"canvas_set: {args=}")
            self.scrollbar.set(*args)
        self.canvas.configure(yscrollcommand=canvas_set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        can_f = tk.Frame(self.canvas, bd=0, background="#eeeeff", name="can_f")
        self.canvas_id = self.canvas.create_window((0, 0), window=can_f, anchor=NW)

        self.forkable_sheet = ForkableSheet(can_f)
        self.forkable_sheet.pack(side=TOP, expand=True, fill=Y)

        def on_mousewheel(event):
            delta = (event.num == 5 and 1 or -1)
            self.canvas.yview_scroll(delta, "units")
        self.canvas.bind("<Button-4>", on_mousewheel)
        self.canvas.bind("<Button-5>", on_mousewheel)

        self.forkable_sheet.bind("<Configure>", self.configure_scrollregion, add=True)
        self.canvas.bind("<Configure>", self.configure_frame, add=True)

    def configure_scrollregion(self, event):
        print(f"configure_scrollregion: {event} {type(event.widget)} {event.widget}")
        x, y, width, height = bbox = self.canvas.bbox("all")
        self.canvas.configure(scrollregion=bbox)
        self.canvas.event_generate("<Configure>", x=x, y=y, width=width, height=height)

    def configure_frame(self, event):
        print(f"configure_frame:        {event} {type(event.widget)} {event.widget}")
        height = max(self.canvas.winfo_height(), self.forkable_sheet.winfo_reqheight())
        self.canvas.itemconfigure(self.canvas_id, width=event.width, height=height)


    def focus_set(self):
        self.forkable_sheet.focus_set()

if __name__ == "__main__":
    from Ui import Ui
    ui = Ui()
    ui.root.title("ScrollableForkableSheet")
    # ui.root.geometry("500x500")
    scrollable = ScrollableForkableSheet(ui.root)
    scrollable.pack(fill="both", expand=True)
    scrollable.forkable_sheet.focus()

    ui.root.mainloop()
