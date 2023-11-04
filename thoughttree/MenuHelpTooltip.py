import tkinter as tk
from tkinter import END

from Tooltip import Tooltip
from tools import text_block, log_motion_on_ctrl_alt
from menu_help_texts import menu_help

class MenuHelpTooltip(Tooltip):
    def __init__(self, widget):
        Tooltip.__init__(self, widget, None)
        self.delay_ms = 750
        self.previous_missing_item = None


    def refresh_tooltip_text(self, event=None):
        try:
            from MainMenu import MainMenu
            if type(event.widget) == tk.Label:
                menu_label = event.widget.cget('text')
            elif type(event.widget) == MainMenu:
                menu_label = event.widget.current_menu()
            else:
                menu_label = self.widget.entrycget(f'@{self.last_y}', 'label')
            if menu_label in menu_help:
                help_text = menu_help[menu_label]
                text = text_block(help_text)
            else:
                text = menu_label
                if menu_label and self.previous_missing_item != menu_label:
                    self.previous_missing_item = menu_label
            self.label.configure(text=text)
        except Exception as ex: # Menu separators have no "label"
            print("ERROR: " + str(ex))
            pass # leave text unchanged
            # self.label.configure(text="-")


if __name__ == "__main__":
    from Menu import Menu
    root = tk.Tk()
    root.title("Tooltip")
    root.geometry("500x500")
    main_menu = Menu(root)


    menu = Menu(main_menu, "Test", menu_help={"a": 1})
    menu.item("Test Cascade", "<<Dummy>>", None)
    menu.item("Test Cascade a", "<<Dummy>>", None)
    menu.item("Test Cascade b", "<<Dummy>>", None)
    menu2 = Menu(main_menu, "Test2", menu_help={"a": 1})
    menu2.item("Test Cascade 2", "<<Dummy>>", None)
    menu2.item("Test Cascade 2.1", "<<Dummy>>", None)
    log_motion_on_ctrl_alt(menu2)

    # MenuHelpTooltip(root, "Tooltip Example")
    Tooltip(root, "Tooltip on root")
    Tooltip(main_menu, "Tooltip on main_menu")
    Tooltip(menu2, "Tooltip on menu")


    def on_event(event, m):
        # print(f"{event=}")
        i = m.index(END)
        while i >= 0:
            # print(f"{i=} {m.entrycget(i, 'label')=}  {m.entrycget(i, 'state')=} {m.index(i)=} {m.yposition(i)=}")
            if m.yposition(i) < event.y:
                print(f"ACTIVE: {m.entrycget(i, 'label')}")
                break
            i -= 1
            # print(f"{i=}")
        # for item in event.widget.winfo_children():
            # print(f"{item=} {item.cget('state')=}")

    # main_menu.bind("<Motion>", on_event)
    # root.bind("<Motion>", on_event)
    # menu.post(10, 10)
    # menu.post(100, 10)
    # root.bind('<Motion>', on_event)
    menu.bind('<Motion>', lambda event: on_event(event, menu))
    menu2.bind('<Motion>', lambda event: on_event(event, menu2))
    # tools.bind_to_all_events(main_menu)
    # tools.bind_to_all_events(menu)
    # tools.bind_to_all_events(root, bind_all=True)
    root.mainloop()

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
