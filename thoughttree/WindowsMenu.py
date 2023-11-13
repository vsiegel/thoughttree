import tkinter as tk

from Menu import Menu
from MenuItem import MenuItem
from Ui import Ui
from menu_help_texts import menu_help


class WindowsMenu(Menu):
    def __init__(self, parent, label):
        super().__init__(parent, label, menu_help=None)

    def populate_menu(self):
        # self.delete(0, tk.END)
        for ui in Ui.current_open_uis:
            # self.item(ui.root.title(), None, lambda e=None, ui=ui: ui.toTop(), check_help=False)
            item = MenuItem(self.popup, self, ui.root.title(), lambda e=None, ui=ui: ui.toTop(), "tooltip", -1)
            item.pack(fill='x')
            self.menu_items.append(item)
