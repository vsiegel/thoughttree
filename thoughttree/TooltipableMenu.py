import re
import tkinter as tk
from tkinter import ttk, INSERT

import tools
from Config import conf
from MenuBar import MenuBar
from MenuHelpTooltip import MenuHelpTooltip
from menu_help_texts import menu_help


class MenuItem(tk.Frame):
    def __init__(self, parent, menu, text, keystroke=None, command=None, underline=-1):
        super().__init__(parent)
        self.menu = menu
        self.text = text
        self.configure(bg='lightgray', borderwidth=2)
        self.command = command
        self.active=False
        self.label = tk.Label(self, text=text, bg='lightgray', anchor='w', font=("Arial", 10),
                              underline=underline, padx=5, pady=0, borderwidth=2, relief='flat')
        self.key_label = tk.Label(self, text=keystroke, bg='lightgray', foreground='gray', anchor='w', font=("Arial", 10),
                              padx=5, pady=0, borderwidth=2, relief='flat')
        if not command:
            self.label.configure(foreground='gray')
        self.bind("<Enter>", self.on_enter, add=True)
        self.bind("<Leave>", self.on_leave, add=True)
        self.label.bind("<Button-1>", self.on_click, add=True)
        self.label.bind("<Escape>", self.menu.close, add=True)
        self.label.pack(side='left', fill='x', expand=True)
        self.key_label.pack(side='right', fill='x')

    def on_enter(self, event):
        self.label.configure(bg='#efefef', relief='raised')
        self.active=True

    def on_leave(self, event):
        self.label.configure(bg='lightgray', relief='flat')
        self.active=False

    def on_click(self, event):
        try:
            self.command()
        except Exception as ex:
            print(f"{ex} {self.command=}")
        self.menu.close()


class TooltipableMenu(tk.Frame):
    # Replacing tk.Menu, because tooltips on menu items do not work under MS Windows.
    def __init__(self, parent, text, **kw):
        super().__init__(parent, bg='lightgray')
        self.parent = parent
        self.label = tk.Label(self, text=text, font=("Arial", 10), bg='lightgray', padx=6, pady=5)
        self.label.bind("<Enter>", self.keep_open, add=True)
        self.label.bind("<Leave>", self.on_leave, add=True)
        self.label.bind("<Button-1>", self.toggle_open, add=True)
        self.label.pack(side='left')
        self.items = []
        self.menu_items = []
        self.popup = None
        self.frame = None


    def add_item(self, label, keystroke=None, command=None, underline=-1, menu2=None, add=False):
        if conf.debug and not label in menu_help:
            print("Warning: Help missing for \"" + label + "\"")

        self.winfo_toplevel().bind(keystroke, command, add=add)
        accelerator = self.accelerator_label(keystroke)
        self.items.append((label, accelerator, command, underline))

    def add_cascade(self, label, menu, underline=-1):
        self.items.append((label, None, menu, "tooltip", underline))

    def add_separator(self):
        self.items.append(('-', '-', '-', -1))

    def insert_command(self, index, label, underline=-1, accelerator=None, state=tk.NORMAL, command=None):
        pass

    def keep_open(self, event):
        if self.parent:
            was_open = self.parent.close_other_menus(self)
            if was_open:
                self.create_popup(event)

    def on_leave(self, event):
        pass
        # self.close()

    def toggle_open(self, event):
        if self.popup:
            self.close()
        else:
            self.create_popup(event)

    def create_popup(self, event, x=None, y=None):
        self.popup = tk.Toplevel(self, bd=3, relief='raised')
        self.popup.wm_overrideredirect(True)
        if x == None:
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
        self.popup.wm_geometry(f"+{x}+{y}")
        self.popup.bind("<Enter>", self.keep_open, add=True)
        self.popup.bind("<Escape>", self.close, add=True)
        self.frame = tk.Frame(self.popup, takefocus=True)
        self.frame.pack()
        self.frame.focus_set()
        self.frame.bind("<Leave>", self.close, add=True)
        MenuHelpTooltip(self.frame)
        self.populate_menu()

    def populate_menu(self):
        for text, keystroke, command, underline in self.items:
            if text == '-':
                separator = tk.Frame(self.frame, height=2, bg='darkgray')
                separator.pack(fill='x', padx=0, pady=5)
            else:
                item = MenuItem(self.frame, self, text, keystroke, command, underline)
                item.pack(fill='x')
                self.menu_items.append(item)

    def show_context_menu(self, event):
        if event.type == tk.EventType.KeyPress:
            w = event.widget
            x, y, *_ = w.bbox(INSERT)
            x += w.winfo_rootx()
            y += w.winfo_rooty()
        else:
            containing = event.widget.winfo_containing(event.x_root, event.y_root)
            if containing:
                containing.focus_set()
            x, y = (event.x_root, event.y_root)
        self.create_popup(event, x, y)

    def active_item(self):
        for item in self.menu_items:
            if item.active:
                return item
        return None

    def close(self, event=None) -> bool:
        if self.popup:
            self.popup.destroy()
            self.popup = None
            return True
        return False


    def accelerator_label(self, keystroke) :
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
