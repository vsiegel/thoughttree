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
        for open in Ui.current_open_uis:
            item = MenuItem(self.popup, self, open.root.title(), keystroke="", command=lambda e=None, ui=open: ui.toTop())
            item.pack(fill='x')
            self.menu_items.append(item)
