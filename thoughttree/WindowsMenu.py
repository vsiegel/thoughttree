import tkinter as tk

from Menu import Menu
from UI import UI
from menu_help import menu_help


class WindowsMenu(Menu):
    def __init__(self, parent, label):
        super().__init__(parent, label, menu_help=menu_help, postcommand=self.create_current_window_items)

    def create_current_window_items(self, event=None):
        print("create_current_window_items")

        self.delete(0, tk.END)
        for open_ui in UI.current_open_uis:
            title = open_ui.root.title()

            command = lambda e, ui=open_ui: ui.toTop()
            self.item(title, None, command)
