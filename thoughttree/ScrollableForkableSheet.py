import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP

from ForkableSheet import ForkableSheet
from tools import on_event


class ScrollableForkableSheet(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0,)# background="lightcyan")
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)

        def canvas_set(*args):
            # print(f"canvas_set: {args=}")
            self.scrollbar.set(*args)
        self.canvas.configure(yscrollcommand=canvas_set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        frame = tk.Frame(self.canvas, bd=0, background="#eeeeff")
        self.frame_id = self.canvas.create_window((0, 0), window=frame, anchor=NW)


        def on_configure(event):
            print(f"################# on_configure {event=}")
        frame.bind("<Configure>", self.configure_scrollregion)

        self.forkable_sheet = ForkableSheet(frame)
        # self.forkable_sheet = self
        self.forkable_sheet.pack(side=TOP, expand=True, fill=Y)
        def sheet_set(*args):
            print(f"sheet_set: {args=}")
            self.scrollbar.set(*args)
        def frame_set(*args):
            print(f"frame_set: {args=}")
            self.scrollbar.set(*args)

        def log(event):
            print(f"{self.forkable_sheet.winfo_reqheight()=} {event}")

        self.canvas.bind("<Configure>", self.configure_width)


        def on_mousewheel(event):
            # print(f"{str(event.widget).startswith(str(self))        =}") # for parent-test
            delta = (event.num == 5 and 1 or -1)
            self.canvas.yview_scroll(delta, "units")

        self.winfo_toplevel().bind("<Button-4>", on_mousewheel)
        self.winfo_toplevel().bind("<Button-5>", on_mousewheel)
        # def on_motion(e):
        #     print(f"@{self.winfo_pointerx()},{self.winfo_pointery()}")
        #     self.sheet.sheet.mark_set(INSERT, f"@{self.winfo_pointerx()},{self.winfo_pointery()}")
        # self.sheet.sheet.bind('<Motion>', on_motion)


    def configure_scrollregion(self, event):
        bbox = self.canvas.bbox("all")

        x, y, width, height = bbox
        self.canvas.configure(scrollregion=bbox)
        self.canvas.event_generate("<Configure>", x=x, y=y, width=width, height=height)


    def configure_width(self, event):
        # print(f"configure_width: {event.widget}")
        height = max(self.canvas.winfo_height(), self.forkable_sheet.winfo_reqheight())
        self.canvas.itemconfigure(self.frame_id, width=event.width, height=height)

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
