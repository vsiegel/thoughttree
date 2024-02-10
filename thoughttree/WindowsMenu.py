import tkinter as tk

from TooltipableMenu import TooltipableMenu
from MenuItem import MenuItem
from Ui import Ui
from menu_help_texts import menu_help


class WindowsMenu(TooltipableMenu):
    def __init__(self, parent, label):
        super().__init__(parent, label, menu_help=None)

    def populate_menu(self):
        # self.delete(0, tk.END)
        for old_item in self.menu_items:
            old_item.destroy()
        for open in Ui.current_open_uis:
            item = MenuItem(self.frame, self, open.root.title(), keystroke="", command=lambda e=None, ui=open: ui.toTop())
            item.pack(fill='x')
            self.menu_items.append(item)

    def update_menu(self, event, x=None, y=None):
        self.populate_menu()
        super().update_menu(event, x, y)
