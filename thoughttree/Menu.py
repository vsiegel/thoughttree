import re
import tkinter as tk
from typing import Union

from MenuHelpTooltip import MenuHelpTooltip
from Ui import Ui


class Menu(tk.Menu):

    def __init__(self, master: Union[tk.Tk, tk.Text, tk.Menu], label=None, menu_help=None, **kw) : #1
        super().__init__(master, tearoff=False, borderwidth=3, **kw)
        if menu_help:
            self.menu_help = menu_help
        elif hasattr(master, "menu_help"):
            self.menu_help = master.menu_help
        else:
            self.menu_help = None

        if isinstance(master, Ui):
            master.root.config(menu=self)
        else:
            if self.menu_help:
                MenuHelpTooltip(self, self.menu_help)
            master.add_cascade(label=label, underline=0, menu=self)


    def convert_key_string(self, keystroke) :

        def fix_key_letter_case(keystroke):
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

        if not keystroke:
            return ""
        s = fix_key_letter_case(keystroke)
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


    def item(self, label, keystroke, command, variable=None, add=False, index=tk.END) :
        accelerator = self.convert_key_string(keystroke)
        state = tk.NORMAL if command or variable else tk.DISABLED
        if variable :
            self.insert_radiobutton(index, label=label, accelerator=accelerator, state=state, variable=variable)
        else:
            self.insert_command(index, label=label, underline=0, accelerator=accelerator, state=state, command=command)
        if keystroke:
            # if not add:
            #     self.master.unbind_class("Text", keystroke)
            self.master.bind_class("Text", keystroke, command, add=add)

