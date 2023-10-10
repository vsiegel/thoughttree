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


if __name__ == "__main__":
    from Menu import Menu
    root = tk.Tk()
    root.title("Tooltip")
    root.geometry("500x500")
    main_menu = Menu(root)
    root.config(menu=main_menu)

    menu = Menu(main_menu, "Test", menu_help={"a": 1})
    menu.item("Test Cascade", None, None)
    menu2 = Menu(main_menu, "Test2", menu_help={"a": 1})
    menu2.item("Test Cascade 2", None, None)
    # MenuHelpTooltip(root, "Tooltip Example")
    Tooltip(root, "Tooltip on root")
    Tooltip(main_menu, "Tooltip on main_menu")
    Tooltip(menu2, "Tooltip on menu")

    def on_event(event):
        print(f"{event.widget=}")
    main_menu.bind("<Motion>", on_event)
    menu.post(10, 10)
    menu.bind('<Motion>', on_event)
    tools.bind_all_events(main_menu)
    tools.bind_all_events(menu)
    tools.bind_all_events(menu2)
    root.mainloop()
