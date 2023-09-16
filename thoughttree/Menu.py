import re
import tkinter as tk
from typing import Union

from MenuHelpTooltip import MenuHelpTooltip
from Ui import Ui


class Menu(tk.Menu):

    def __init__(self, parent: Union[tk.Tk, tk.Text, tk.Menu, None], label=None, menu_help=None, **kw) : #1
        super().__init__(parent, tearoff=False, borderwidth=3, **kw)
        if menu_help:
            self.menu_help = menu_help
        elif hasattr(parent, "menu_help"):
            self.menu_help = parent.menu_help
        else:
            self.menu_help = None

        if isinstance(parent, Ui):
            parent.root.config(menu=self)
        else:
            if self.menu_help:
                MenuHelpTooltip(self, self.menu_help)
            if parent:
                parent.add_cascade(label=label, underline=0, menu=self)


    def fix_key_letter_case(self, keystroke):
        if not keystroke:
            return ""
        m = re.search(r"^((<.*-)|<)([a-zA-Z])>", keystroke)
        if m:
            letter = m[3]
            if keystroke.lower().count('shift-'):
                letter = letter.upper()
            else:
                letter = letter.lower()
            return m[1] + letter + ">"
        else:
            return keystroke


    def convert_key_string(self, keystroke) :
        if not keystroke:
            return ""
        s = self.fix_key_letter_case(keystroke)
        s = s.replace("-Key-", "-")
        s = s.replace("-", "+")
        s = s.replace("Control", "Ctrl")
        s = s.replace("Escape", "Esc")
        s = s.replace("plus>", "+")
        s = s.replace("minus>", "-")
        s = s.replace("period>", ".")
        s = s.lstrip("<")
        s = s.rstrip(">")
        if s[-2] == "+":
            s = s[:-1] + s[-1].upper()
        return s


    def item(self, label, keystroke, command, variable=None, add=False, index=tk.END, check_help=True, additional_menu=None, to=None):
        if check_help and not label in self.menu_help:
            print("Warning: Help missing for \"" + label + "\"")
        if keystroke and not keystroke.startswith("<"):
            print("Warning: keystroke should be in <...> format")
        keystroke = self.fix_key_letter_case(keystroke)
        accelerator = self.convert_key_string(keystroke)
        state = tk.NORMAL if command or variable else tk.DISABLED
        menus = [self]
        if additional_menu:
            menus.append(additional_menu)
        if variable :
            for menu in menus:
                menu.insert_radiobutton(index, label=label, accelerator=accelerator, state=state, variable=variable)
        else:
            for menu in menus:
                menu.insert_command(index, label=label, underline=0, accelerator=accelerator, state=state, command=command)
        if keystroke:
            # if not add:
            #     self.master.unbind_class("Text", keystroke)
            self.master.bind_class("Text", keystroke, command, add=add)

