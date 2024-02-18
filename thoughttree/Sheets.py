import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, VERTICAL, NW, Y, X, INSERT, CURRENT, TOP, NSEW

import Colors
import tools
from Ruler import Ruler
from Sheet import Sheet
from TreeSheet import TreeSheet
from tools import on_event, bind_tree, iterate_tree


class Sheets(tk.Frame):
    def __init__(self, parent, name="st", **kw):
        super().__init__(parent, highlightthickness=3, highlightcolor=Colors.highlight, name=name, takefocus=False, **kw)

        self.canvas = tk.Canvas(self, name="c", background="#ffffff")
        self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview, width=18, takefocus=False, borderwidth=2)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.current: TreeSheet | None = None
        self.scroll_in_progress = False

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.frame = tk.Frame(self.canvas, bd=0, background="#eeeeff", name="cf")
        self.frame_id = self.canvas.create_window((0, 0), window=self.frame, anchor=NW)

        self.y_spacer = tk.Frame(self.frame, width=0, background="#baabbc")
        self.y_spacer.pack(side=LEFT, fill=Y)

        self.sheet = TreeSheet(self.frame, sheet_tree=self, name="0", takefocus=False)
        self.sheet.pack(side=TOP, expand=True, fill=BOTH)

        self.add_wheel_scrolling()

        def on_focus_in(event):
            if self.current:
                # print(f">+++ st on_focus_in {self} {event} {str(self.last_inner_focus)=}")
                self.current.focus_set()
                self.configure(takefocus=False)
                # self.scrollbar.configure(takefocus=False)
        self.bind("<FocusIn>", on_focus_in, add=True)
        def on_focus_out(event):
            self.configure(takefocus=True)
        self.bind("<FocusOut>", on_focus_out, add=True)

        self.canvas.bind("<Configure>", self.configure_frame, add=True)
        self.frame.bind("<Configure>", self.configure_scrollregion, add=True)

        self.winfo_toplevel().bind("<Control-Alt-Shift-S>", self.debug)

        self.ruler = None

        # def on_key(event):
        #     # print(f"on_key {event.keysym}")
        #     sheet = event.widget
        #     sheet.update()
        #     # print(f" 1: {sheet.bbox('1.0')} E-1: {sheet.bbox('end-1c')}")
        #     # print(f" x: {sheet.winfo_rootx()} x: {sheet.winfo_rooty()} x: {sheet.winfo_x()} y: {sheet.winfo_y()}")
        #     print(f"{self.sheet.dlineinfo('insert') and self.sheet.dlineinfo('insert')[0:2]}")
        # self.sheet.bind("<Key>", on_key, add=True)

    def see_in_tree(self, sheet: TreeSheet, to=INSERT):
        # self.ruler = self.ruler and self.ruler.cleared() or Ruler(self, offset=0)
        line_info = sheet.dlineinfo(to)
        if not line_info:
            return

        y0 = self.frame.winfo_rooty()
        # self.ruler.offset = y0
        h = self.frame.winfo_height()
        y = y0 - y0
        y2 = y0 + h - y0

        view_y = self.canvas.winfo_rooty() - y0
        view_h = self.canvas.winfo_height()
        view_y2 = view_y + view_h

        sheet_y = sheet.winfo_rooty() - y0

        line_y = sheet_y + int(line_info[1])
        line_h = int(line_info[3])
        line_y2 = line_y + line_h

        margin_y = line_y - line_h
        margin_y2 = line_y2 + line_h

        top, bottom = self.canvas.yview()

        # self.ruler.ticks(
        #     (y, "y", "#c00"),
        #     # (h, "h", "#a1a5dd"),
        #     (y2, "y2", "#f4f6ae"),
        #     (view_y, "view_y", "#7a9"),
        #     # (view_h, "view_h", "#a89"),
        #     (view_y2, "view_y2", "#1714ff"),
        #     (sheet_y, "sheet_y", "#4a1"),
        #     (line_y, "line_y", "#a8f"),
        #     # (line_h, "line_h", "#af9"),
        #     (line_y2, "line_y2", "#a19"),
        #     (margin_y, "margin_y", "#f89"),
        #     # (margin_h, "margin_h", "#a81"),
        #     (margin_y2, "margin_y2", "#08f")
        # )
        if margin_y < view_y:
            to_y = margin_y
            to_top = to_y / h
            # print(f"^^^^^ {to_top=:.3f} {to_y=} {view_y=} {line_y=} {y=}")
            if view_y > 0:
                self.canvas.yview_moveto(to_top)
        elif margin_y2 > view_y2:
            to_y = margin_y2 - view_h
            to_top = to_y / h
            # print(f"vvvvv {to_top=:.3f} {to_y=} {view_y2=} {line_y2=} {y2=}")
            if view_y2 < line_y2:
                self.canvas.yview_moveto(to_top)
        else:
            return

    def jump_to_limit(self, e: tk.Event):
        top, bottom, *_ = self.current.vbar.get()
        if e.keysym == 'Prior' and top == 0.0:
            limit = "1.0"
        elif e.keysym == 'Next' and bottom == 1.0:
            limit = tk.END
        else:
            return

        self.mark_set(tk.INSERT, limit)
        self.see(tk.INSERT)


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
            raise Exception(f"{str(sheet)} is not in Sheets ({str(self)})")
        if not isinstance(sheet, TreeSheet):
            raise Exception(f"{sheet} is not a TreeSheet") #fixme
        sheet.update_tab_title()


    def on_motion_in_sheet(self, event):
        if self.scroll_in_progress:
            return

        y = event.widget.winfo_pointery()
        window_top = self.winfo_rooty()
        window_bottom = window_top + self.winfo_height()

        distance = 0
        if y < window_top:
            distance = y - window_top
        elif y > window_bottom:
            distance = y - window_bottom
        scroll_speed = int(distance * 0.05)
        if scroll_speed > 0:
            scroll_speed = max(scroll_speed, 1)
        elif scroll_speed < 0:
            scroll_speed = min(scroll_speed, -1)

        if scroll_speed != 0:
            print(f"{y=} {distance=} {scroll_speed=} {self.winfo_geometry()=} {self.scrollbar.fraction(0, y)=}")
            self.canvas.yview_scroll(scroll_speed, "units")
            self.scroll_in_progress = True
            self.after(150, self.reset_scroll_flag)

    def reset_scroll_flag(self):
        self.scroll_in_progress = False

    def size(self):
        sum = len(self.sheet.get(1.0, "end").strip())
        if self.sheet.notebook:
            sum += self.sheet.notebook.size()


    def debug(self, event):
        print(f"{event.widget}    {event.width}x{event.height}+{event.x}+{event.y}")
        print(f"{self.frame.winfo_height()   =}")
        print(f"{self.frame.winfo_reqheight()=}")


class IterableSheets(Sheets):
    def __init__(self, sheets: Sheets, parent, **kw):
        super().__init__(parent, **kw)
        self.sheets = sheets

    def __iter__(self):
        return self

    def __next__(self):
        return self.sheets.__next__()

    def breadth_first(self):
        yield from self.sheets.breadth_first()

    def depth_first(self):
        yield from self.sheets.depth_first()

    def root_to_index(self):
        pass

    def root_to_sheet(self):
        pass

    def root_to_leaf(self):
        pass



if __name__ == "__main__":
    root = tk.Tk()
    # root.geometry("100x200")
    tools.escapable(root)
    widget = Sheets(root)
    widget.pack(side=LEFT, fill=BOTH, expand=True)
    # widget.pack_propagate(False)
    widget.focus_set()
    root.mainloop()
