import tkinter as tk
from typing import Union


class Menu(tk.Menu):

    def __init__(self, master: Union[tk.Tk, tk.Text, tk.Menu], label=None, **kwargs) :
        super().__init__(master, tearoff=0)
        if label :
            master.add_cascade(label=label, menu=self)
        if type(master) == tk.Tk:
            master.config(menu=self)

    def item(self, label, keystroke, command, bind_key=True, context_menu=None) :
        def convert_key_string(s) :
            if not keystroke:
                return ""
            s = s.replace("<Control", "Ctrl")
            s = s.replace("<Shift", "Shift")
            s = s.replace("<Alt", "Alt")
            s = s.replace("<Escape", "Esc")
            s = s.replace("-", "+")
            s = s.replace(">", "")
            if s[-3] == "-":
                s[-2] = s[-2].upper()
            return s

        accelerator = convert_key_string(keystroke)
        state = tk.NORMAL if command else tk.DISABLED
        self.add_command(label=label, accelerator=accelerator, command=command, state=state)
        if context_menu :
            context_menu.add_command(label=label, accelerator=accelerator, command=command, state=state)
        if bind_key and keystroke:
            self.master.bind_all(keystroke, command, False)
