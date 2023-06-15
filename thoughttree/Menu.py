import re
import tkinter as tk
from typing import Union


class Menu(tk.Menu):

    def __init__(self, master: Union[tk.Tk, tk.Text, tk.Menu], label=None, **kwargs) :
        super().__init__(master, tearoff=0, borderwidth=3)
        if label :
            master.add_cascade(label=label, menu=self, underline=0)
        if type(master) == tk.Tk:
            master.config(menu=self)


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


    def item(self, label, keystroke, command, bind_key=True, context_menu=None, variable=None, add=False) :
        accelerator = self.convert_key_string(keystroke)
        state = tk.NORMAL if command or variable else tk.DISABLED
        if variable :
            self.add_checkbutton(label=label, accelerator=accelerator, state=state, variable=variable)
        else:
            self.add_command(label=label, accelerator=accelerator, state=state, command=lambda: command(None))
            # self.entryconfigure('last', tooltip=label)
            # print(f"{self.entryconfigure('last')=}", end="\n\n")
        # if context_menu :
        #     context_menu.add_command(label=label, accelerator=accelerator, state=state, command=lambda: command(None))
        if not add:
            self.master.unbind_class("Text", keystroke)
        self.master.bind_class("Text", keystroke, command, add=add)

