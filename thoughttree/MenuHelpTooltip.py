import tkinter as tk

from Tooltip import Tooltip
from tools import text_block
from menu_help_texts import menu_help

class MenuHelpTooltip(Tooltip):
    def __init__(self, widget, above=False):
        Tooltip.__init__(self, widget, None, above=above)
        self.delay_ms = 750
        self.previous_missing_item = None


    def refresh_tooltip_text(self, event: tk.Event=None):
        widget = event.widget
        try:
            from MainMenu import MainMenu
            from MenuItem import MenuItem
            if isinstance(widget, tk.Label) and isinstance(widget.master, MenuItem):
                widget = widget.master

            if isinstance(widget, MenuItem):
                menu_label = widget.text
            elif isinstance(widget, tk.Label):
                    menu_label = widget.cget('text')
            elif event.type == tk.EventType.Enter:
                # The Enter may be on the surrounding frame,but the pointer may be on an actual label after the tooltip delay:
                containing = widget.winfo_containing(*widget.winfo_pointerxy())
                if type(containing) == tk.Label:
                    menu_label = containing.cget('text')
                else:
                    menu_label = ""
                # print(f"{menu_label=} {containing=} {event.widget}")
            elif type(widget) == MainMenu:
                menu_label = widget.current_menu()
            elif type(widget) == tk.Frame:
                menu_label = "" # separator, do not change text
            else:
                menu_label = "" # between menu items

            if menu_label:
                if menu_label in menu_help:
                    help_text = menu_help[menu_label]
                    text = f"{menu_label}\n\n{text_block(help_text)}"
                else:
                    text = menu_label
                    if menu_label and self.previous_missing_item != menu_label:
                        self.previous_missing_item = menu_label
                self.label.configure(text=text)
        except Exception as ex: # Menu separators have no "label"
            pass # leave text unchanged
