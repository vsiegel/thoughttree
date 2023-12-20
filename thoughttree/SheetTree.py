import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP

import Colors
from ForkableSheet import ForkableSheet
from Sheet import Sheet
from tools import on_event, bind_tree, iterate_tree


class SheetTree(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, name="st", highlightthickness=3, highlightcolor=Colors.highlight, *args, **kw)

        self.canvas = tk.Canvas(self, name="c")# background="lightcyan")
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)
        def scrollbar_set(*args):
            # print(f"{args}")
            self.scrollbar.set(*args)
        self.canvas.configure(yscrollcommand=scrollbar_set)

        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        canvas_frame = tk.Frame(self.canvas, bd=0, background="#eeeeff", name="cf")

        # def canvas_frame_configure(event):
        #     print(f"canvas_frame_configure:  {event}")
        # canvas_frame.bind("<Configure>", canvas_frame_configure, add=True)

        # canvas_frame.pack_propagate(False)
        self.frame_id = self.canvas.create_window((0, 0), window=canvas_frame, anchor=NW)

        self.forkable_sheet = ForkableSheet(parent_frame=canvas_frame, )
        self.forkable_sheet.pack(side=TOP, expand=True, fill=BOTH)

        self.add_scrolling()

        self.forkable_sheet.bind("<Configure>", self.configure_scrollregion, add=True)
        self.canvas.bind("<Configure>", self.configure_frame, add=True)
        # def on_configure(event):
        #     print(f"Event: {event}: {event.widget} {event.x},{event.y} {event.width}x{event.height}")
        # self.winfo_toplevel().bind_all('<Configure>', on_configure)

        self.winfo_toplevel().bind("<Control-Alt-Shift-S>", self.debug)
        self.canvas_frame = canvas_frame

    def debug(self, event):
        print(f"{event}    {event.widget}    {event.width}x{event.height}+{event.x}+{event.y}")
        print(f"{self.winfo_geometry()=}")
        print(f"{self.canvas.winfo_geometry()=}")
        print(f"{self.canvas_frame.winfo_geometry()=}")
        print(f"{self.canvas_frame.winfo_height()=}")
        print(f"{self.canvas_frame.winfo_reqheight()=}")


    def configure_frame(self, event):
        # print(f"configure_frame:        {event.height}")
        self.canvas.itemconfigure(self.frame_id, width=event.width, height=event.height)

    def configure_scrollregion(self, event):
        # print(f"configure_scrollregion: {event}")
        # self.canvas.update_idletasks()
        x, y, b_width, b_height = self.canvas.bbox("all")
        x, y, e_width, e_height = event.x, event.y, event.width, event.height
        height = max(self.canvas.winfo_height(), b_height)
        width = max(self.canvas.winfo_width(), b_width)

        # print(f"{self.canvas.bbox('all')=}")
        # print(f"b_height:          {b_height}")
        # print(f"ev.height:         {e_height}")
        # print(f"canvas height:     {self.canvas.configure('height')[4]}")
        # print(f"c.winfo_height:    {self.canvas.winfo_height()}")
        # print(f"c.winfo_reqheight: {self.canvas.winfo_reqheight()}")
        # print(f"height:            {height}")
        #
        # print(f"b_width:          {b_width}")
        # print(f"ev.width:         {e_width}")
        # print(f"canvas width:     {self.canvas.configure('width')[4]}")
        # print(f"c.winfo_width:    {self.canvas.winfo_width()}")
        # print(f"c.winfo_reqwidth: {self.canvas.winfo_reqwidth()}")
        # print(f"width:            {width}")


        # self.canvas.event_generate("<Configure>", x=x, y=y, width=width, height=height)
        # print(f"{(x, y, width, height)=}")
        self.canvas.configure(scrollregion=(x, y, width, height), width=width, height=height)
        # print(f"{self.canvas.cget('scrollregion')=}")
        # self.canvas.itemconfigure(self.frame_id, width=width, height=height)
        # self.canvas.configure(scrollregion=(x, y, width, height))
        # self.canvas.itemconfigure(self.frame_id, width=event.width, height=event.height)


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
        return self.forkable_sheet.winfo_reqheight()

    def focus_set(self):
        self.forkable_sheet.focus_set()

    def in_canvas(self, x, y):
        return str(self.canvas.winfo_containing(x, y)).startswith(str(self.canvas))

    def update_tab_title(self, event=None):
        sheet = self.focus_get()
        if not str(sheet).startswith(str(self)):
            raise Exception(f"{sheet} is not in SheetTree")
        if not isinstance(sheet, ForkableSheet):
            raise Exception(f"{sheet} is not a ForkableSheet")
        sheet.update_tab_title()
