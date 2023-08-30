import tkinter as tk

from Menu import Menu
from Ui import Ui
from menu_help import menu_help


class WindowsMenu(Menu):
    def __init__(self, parent, label):
        super().__init__(parent, label, menu_help=None, postcommand=self.window_items)

    def window_items(self, event=None):
        self.delete(0, tk.END)
        for ui in Ui.current_open_uis:
            self.item(ui.root.title(), None, lambda e=None, ui=ui: ui.toTop(), check_help=False)
