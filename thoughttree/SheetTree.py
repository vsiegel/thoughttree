import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP, NSEW

import Colors
import tools
from Sheet import Sheet
from TreeSheet import TreeSheet
from tools import on_event, bind_tree, iterate_tree


class SheetTree(tk.Frame):
    def __init__(self, parent, name="st", **kw):
        super().__init__(parent, highlightthickness=3, highlightcolor=Colors.highlight, name=name, takefocus=False, **kw)

        self.canvas = tk.Canvas(self, name="c", background="#ffffff")
        def log_call(*args):
            # print(f"log_call " + str(args))
            self.scrollbar.set(*args)
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)
        self.canvas.configure(yscrollcommand=log_call)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.last_sheet = None

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.frame = tk.Frame(self.canvas, bd=0, background="#eeeeff", name="cf")
        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor=NW)

        self.y_spacer = tk.Frame(self.frame, width=0, background="#baabbc")
        self.y_spacer.pack(side=LEFT, fill=Y)

        self.sheet = TreeSheet(self.frame, sheet_tree=self, name="0", takefocus=False)
        self.sheet.pack(side=TOP, expand=True, fill=BOTH)

        self.add_wheel_scrolling()

        def on_focus_in(event):
            if self.last_sheet:
                # print(f">+++ st on_focus_in {self} {event} {str(self.last_inner_focus)=}")
                self.last_sheet.focus_set()
                self.configure(takefocus=False)
                # self.scrollbar.configure(takefocus=False)
        self.bind("<FocusIn>", on_focus_in, add=True)
        def on_focus_out(event):
            self.configure(takefocus=True)
        self.bind("<FocusOut>", on_focus_out, add=True)

        self.canvas.bind("<Configure>", self.configure_frame, add=True)
        self.frame.bind("<Configure>", self.configure_scrollregion, add=True)

        self.winfo_toplevel().bind("<Control-Alt-Shift-S>", self.debug)


        # def on_key(event):
        #     # print(f"on_key {event.keysym}")
        #     sheet = event.widget
        #     sheet.update()
        #     # print(f" 1: {sheet.bbox('1.0')} E-1: {sheet.bbox('end-1c')}")
        #     # print(f" x: {sheet.winfo_rootx()} x: {sheet.winfo_rooty()} x: {sheet.winfo_x()} y: {sheet.winfo_y()}")
        #     print(f"{self.sheet.dlineinfo('insert') and self.sheet.dlineinfo('insert')[0:2]}")
        # self.sheet.bind("<Key>", on_key, add=True)

    def scroll(self, sheet: TreeSheet, to=INSERT):
        # print(f">> scroll {sheet=} {id(sheet)=}")
        sheet_y = sheet.winfo_rooty()
        frame_y = self.frame.winfo_rooty()
        frame_h = self.frame.winfo_height()
        info = sheet.dlineinfo(to)
        if info:
            see_top_sheet = info[1]
            height = info[3]
            see_top = see_top_sheet + sheet_y - frame_y
            see_bottom = see_top + height
            move_to_top = see_top / frame_h
            move_to_bottom = see_bottom / frame_h
            top, bottom = self.canvas.yview()
            # print(f"{sheet} {(see_top, see_bottom)=} {move_to_top=:.3f} {move_to_bottom=:.3f} { (top, bottom)=}")
            if move_to_top < top:
                self.canvas.yview_moveto(move_to_top)
            elif move_to_bottom > bottom:
                self.canvas.yview_moveto(top + move_to_bottom - move_to_top)


    def add(self, text=""):
        self.sheet.add(text)

    def configure_frame(self, event):
        self.canvas.itemconfigure(self.frame_id, width=event.width)
        self.y_spacer.configure(height=event.height)

    def configure_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def add_wheel_scrolling(self):
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
        if not isinstance(sheet, TreeSheet):
            raise Exception(f"{sheet} is not a TreeSheet") #fixme
        sheet.update_tab_title()

    # def tk_focusPrev(self):
    #     return super().tk_focusPrev().tk_focusPrev()
    #     return self.sheet.tk_focusPrev().tk_focusPrev()

    def debug(self, event):
        print(f"{event.widget}    {event.width}x{event.height}+{event.x}+{event.y}")
        print(f"{self.frame.winfo_height()   =}")
        print(f"{self.frame.winfo_reqheight()=}")


if __name__ == "__main__":
    root = tk.Tk()
    # root.geometry("100x200")
    tools.escapable(root)
    widget = SheetTree(root)
    widget.pack(side=LEFT, fill=BOTH, expand=True)
    # widget.pack_propagate(False)
    widget.focus_set()
    root.mainloop()
