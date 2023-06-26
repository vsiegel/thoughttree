import textwrap
import tkinter as tk
from math import sqrt

from Text import Text
from menu_commands_help import menu_command_help
from tools import text_block


class ToolTip :
    def __init__(self, widget, text) :
        self.widget = widget
        self.root = widget.winfo_toplevel()
        self.text = text
        self.tooltip = None
        self.label = None
        self.timer = None
        self.last_y = None
        widget.bindtags(("first",) + widget.bindtags())
        # widget.bind("<Enter>", self.show_tooltip)
        # widget.bind("<Leave>", self.hide_tooltip)

        widget.bind("<Enter>", self.add_tooltip)
        widget.bind("<Motion>", self.refresh_tooltip)
        widget.bind("<Leave>", self.remove_tooltip)
        widget.bind("<Unmap>", self.remove_tooltip)


    def add_tooltip(self, event):
        if self.tooltip:
            return
        self.timer = self.root.after(1000, self.create_tooltip)


    def create_tooltip(self, event=None):
        if not self.tooltip:
            self.tooltip = tk.Toplevel(self.root)
            self.tooltip.wm_overrideredirect(True)
            self.label = tk.Label(self.tooltip, text="text", background="#FFFFE0", relief="solid",
                             borderwidth=1, justify=tk.LEFT, padx=6, pady=5, font=Text.FONT)
            self.label.pack()
            self.tooltip.bind("<Leave>", self.remove_tooltip)
            self.refresh_tooltip()


    def refresh_tooltip(self, event=None):
        if event:
            self.last_y = event.y
        if self.tooltip:

            px = self.root.winfo_pointerx() + 75
            py = self.root.winfo_pointery() + 25
            self.tooltip.wm_geometry(f"+{px}+{py}")

            try:
                menu_item = self.widget.entrycget(f'@{self.last_y}', 'label')
                if menu_item in menu_command_help:
                    help_text = menu_command_help[menu_item]
                    text = text_block(help_text)
                else:
                    text = menu_item
                self.label.configure(text=text)
            except: # Menu separators have no "label"
                self.label.configure(text="-")


    def remove_tooltip(self, event):
        if self.timer:
            self.root.after_cancel(self.timer)
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = None


    # def show_tooltip(self, event=None) :
    #     if self.tooltip is not None :
    #         return
    #
    #     x, y, _, _ = self.widget.bbox("insert")
    #     x += self.widget.winfo_rootx() + 25
    #     y += self.widget.winfo_rooty() + 25
    #
    #     self.tooltip = tooltip = tk.Toplevel(self.widget)
    #     tooltip.wm_overrideredirect(True)
    #     tooltip.wm_geometry(f"+{x}+{y}")
    #
    #     label = tk.Label(tooltip, text=self.text, background="#FFFFE0", relief="solid",
    #             borderwidth=1, justify=tk.LEFT, padx=4, pady=4)
    #     label.pack()
    #
    #
    # def hide_tooltip(self, event=None) :
    #     if self.tooltip:
    #         self.tooltip.destroy()
    #     self.tooltip = None
