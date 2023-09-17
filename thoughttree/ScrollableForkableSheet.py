import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP

from ForkableSheet import ForkableSheet


class ScrollableForkableSheet(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, background="lightcyan")
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)


        frame = tk.Frame(self.canvas, bd=0, background="#eeeeff")
        self.frame_id = self.canvas.create_window((0, 0), window=frame, anchor=NW)

        self.forkable_sheet = ForkableSheet(frame)#, height=1)
        self.forkable_sheet.pack(side=TOP, expand=True, fill=X)
        self.forkable_sheet.bind("<Configure>", self.configure_scrollregion)
        frame.bind("<Configure>", self.configure_scrollregion)
        self.canvas.bind("<Configure>", self.configure_width)


        def on_mousewheel(event):
            delta = (event.num == 5 and 1 or -1)
            self.canvas.yview_scroll(delta, "units")

        self.winfo_toplevel().bind("<Button-4>", on_mousewheel)
        self.winfo_toplevel().bind("<Button-5>", on_mousewheel)


        # def on_click(e):
        #     frame.focus_set()
        # self.canvas.bind('<Button-1>', on_click)
        # def on_motion(e):
        #     print(f"@{self.winfo_pointerx()},{self.winfo_pointery()}")
            # self.sheet.sheet.mark_set(INSERT, CURRENT)
            # self.sheet.sheet.mark_set(INSERT, f"@{self.winfo_pointerx()},{self.winfo_pointery()}")
        # self.sheet.sheet.bind('<Motion>', on_motion)


    def configure_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def configure_width(self, event):
        print(f"{event.height=}")
        print(f"{self.canvas.winfo_height()=}")
        print(f"{self.canvas.winfo_reqheight()=}")
        print(f"{self.forkable_sheet.winfo_height()=}")
        print(f"{self.forkable_sheet.winfo_reqheight()=}")
        print(f"{self.forkable_sheet.sheet.winfo_height()=}")
        print(f"{self.forkable_sheet.sheet.winfo_reqheight()=}")
        # print(f"{self.frame.winfo_height()=}")
        # print(f"{self.frame.winfo_reqheight()=}")
        # self.canvas.itemconfigure(self.frame_id, width=event.width, height=event.height)
        # self.canvas.itemconfigure(self.frame_id, width=event.width)
        height = max(self.canvas.winfo_height(), self.forkable_sheet.winfo_reqheight())
        print(f"{height=}")
        self.canvas.itemconfigure(self.frame_id, width=event.width, height=height)

    def focus_set(self):
        self.forkable_sheet.sheet.focus()


if __name__ == "__main__":
    from Ui import Ui
    ui = Ui()
    ui.root.title("ScrollableForkableSheet")
    # ui.root.geometry("500x500")
    scrollable = ScrollableForkableSheet(ui.root)
    scrollable.pack(fill="both", expand=True)
    scrollable.forkable_sheet.sheet.focus()

    ui.root.mainloop()
