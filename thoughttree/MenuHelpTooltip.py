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
