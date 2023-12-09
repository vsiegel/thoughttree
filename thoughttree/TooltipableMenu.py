import re
import tkinter as tk
from tkinter import INSERT

from Config import conf
from MenuHelpTooltip import MenuHelpTooltip
from MenuItem import MenuItem
from menu_help_texts import menu_help


class TooltipableMenu(tk.Frame):
    # Replacing tk.Menu, because tooltips on menu items do not work under MS Windows.
    def __init__(self, parent, text, **kw):
        super().__init__(parent, bg='lightgray', borderwidth=0)
        self.parent = parent
        self.label = tk.Label(self, text=text, font=("Arial", 12), bg='lightgray', padx=6, pady=5)
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
        keystroke = self.fix_key_letter_case(keystroke)
        self.winfo_toplevel().bind(keystroke, command, add=add)
        accelerator = self.accelerator_label(keystroke)
        self.items.append((label, accelerator, command, underline))
        if menu2:
            menu2.add_item(label, None, command, underline)

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
        if not self.popup:
            self.popup = tk.Toplevel(self, bd=3, relief='raised', bg='lightgray')
            # self.popup.grab_set() # todo
            self.popup.wm_overrideredirect(True)
            self.popup.bind("<Enter>", self.keep_open, add=True)
            self.popup.bind("<Escape>", self.close, add=True)
            self.frame = tk.Frame(self.popup, takefocus=True, bg='lightgray')
            self.frame.pack()
            self.frame.focus_set()
            self.frame.bind("<Leave>", self.close, add=True)
            MenuHelpTooltip(self.frame)
            self.populate_menu()
            if isinstance(self.parent, MenuBar):
                self.parent.open_popup = self.popup
        if x is None:
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
        self.popup.wm_geometry(f"+{x}+{y}")

    def populate_menu(self):
        for text, keystroke, command, underline in self.items:
            if text == '-':
                separator = tk.Frame(self.frame, height=1, bg='darkgray')
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
            if isinstance(self.parent, MenuBar):
                self.parent.open_popup = None
            return True
        return False


    @staticmethod
    def accelerator_label(keystroke) :
        if not keystroke:
            return ""
        s = keystroke
        # s = self.fix_key_letter_case(s)
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


    @staticmethod
    def fix_key_letter_case(keystroke):
        if not keystroke:
            return None
        m = re.search(r"^((<.*-)|<)([a-zA-Z])>", keystroke)
        if m:
            letter = m[3]
            if keystroke.lower().count('shift-'):
                letter = letter.upper()
            else:
                letter = letter.lower()
            keystroke = m[1] + letter + ">"
        return keystroke
