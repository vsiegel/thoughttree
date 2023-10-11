import tkinter as tk

import tools
from Tooltip import Tooltip
from tools import text_block


class MenuHelpTooltip(Tooltip):
    def __init__(self, widget, menu_help):
        Tooltip.__init__(self, widget, None)
        self.delay_ms = 750
        self.menu_help = menu_help
        self.previous_missing_item = None


    def refresh_tooltip_text(self):
        try:
            menu_item = self.widget.entrycget(f'@{self.last_y}', 'label')
            # print(f"{menu_item=}")
            if menu_item in self.menu_help:
                help_text = self.menu_help[menu_item]
                text = text_block(help_text)
            else:
                text = menu_item
                if menu_item and self.previous_missing_item != menu_item:
                    self.previous_missing_item = menu_item
            self.label.configure(text=text)
        except Exception as ex: # Menu separators have no "label"
            pass # leave text unchanged
            # self.label.configure(text="-")


# if __name__ == "__main__":
    # from Menu import Menu
    # root = tk.Tk()
    # root.title("Tooltip")
    # root.geometry("500x500")
    # main_menu = Menu(root)
    # root.config(menu=main_menu)
    #
    # menu = Menu(main_menu, "Test", menu_help={"a": 1})
    # menu.item("Test Cascade", None, None)
    # menu2 = Menu(main_menu, "Test2", menu_help={"a": 1})
    # menu2.item("Test Cascade 2", None, None)
    # # MenuHelpTooltip(root, "Tooltip Example")
    # Tooltip(root, "Tooltip on root")
    # Tooltip(main_menu, "Tooltip on main_menu")
    # Tooltip(menu2, "Tooltip on menu")
    #
    # def on_event(event):
    #     print(f"{event.widget=}")
    # main_menu.bind("<Motion>", on_event)
    # menu.post(10, 10)
    # menu.bind('<Motion>', on_event)
    # tools.bind_all_events(main_menu)
    # tools.bind_all_events(menu)
    # tools.bind_all_events(menu2)
    # root.mainloop()

import tkinter as tk

class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        label = tk.Label(tw, text=self.text, background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def createToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


if __name__ == "__main__":
    root = tk.Tk()
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open", command=lambda: print("OpenX"))
    filemenu.add_command(label="Save", command=lambda: print("SaveX"))
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    for index, item in enumerate(filemenu.entrycget(i, 'label') for i in range(filemenu.index('end')+1)):
        filemenu.entryconfigure(index, command=(lambda text=item: print(text)))
        createToolTip(filemenu, item)

    root.mainloop()
