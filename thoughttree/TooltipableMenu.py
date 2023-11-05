import tkinter as tk
from tkinter import ttk

import tools
from MenuBar import MenuBar
from MenuHelpTooltip import MenuHelpTooltip
from menu_help_texts import menu_help


class MenuItem(tk.Frame):
    def __init__(self, parent, menu, text, command, tooltip=None, underline=-1):
        super().__init__(parent)
        self.menu = menu
        self.text = text
        self.configure(bg='lightgray')
        self.command = command
        self.active=False
        self.label = tk.Label(self, text=text, bg='lightgray', anchor='w', font=("Arial", 10),
                              underline=underline, padx=5, pady=2, borderwidth=1, relief='flat')
        if not command:
            self.label.configure(foreground='gray')
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
        self.label.pack(fill='x')

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
        self.label.bind("<Enter>", self.keep_open)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.toggle_open)
        self.label.pack(side='left')
        self.items = []
        self.menu_items = []
        self.popup = None
        self.frame = None


    def add_item(self, label, keystroke=None, command=None, tooltip=None, underline=-1, menu2=None, add=False):
        self.winfo_toplevel().bind(keystroke, command, add=add)
        self.items.append((label, command, tooltip, underline))

    def add_cascade(self, label, menu, underline=-1):
        self.items.append((label, menu, "tooltip", underline))

    def add_separator(self):
        self.items.append(('-', '-', '-', -1))

    def insert_command(self, index, label, underline=-1, accelerator=None, state=tk.NORMAL, command=None):
        pass

    def keep_open(self, event):
        was_open = self.parent.close_other_menus(self)
        if was_open:
            self.create_popup()

    def on_leave(self, event):
        pass
        # self.close()

    def toggle_open(self, event):
        if self.popup:
            self.close()
        else:
            self.create_popup()

    def create_popup(self):
        self.popup = tk.Toplevel(self, bd=3, relief='raised')
        self.popup.wm_overrideredirect(True)
        self.popup.wm_geometry(f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height()}")
        self.popup.bind("<Enter>", self.keep_open)
        self.popup.bind("<Escape>", self.close)
        self.frame = tk.Frame(self.popup)
        self.frame.pack()
        # tools.bind_to_all_events(self.popup)
        MenuHelpTooltip(self.frame)
        self.populate_menu()

    def populate_menu(self):
        for text, command, tooltip, underline in self.items:
            if text == '-':
                separator = tk.Frame(self.frame, height=2, bg='darkgray')
                separator.pack(fill='x', padx=0, pady=5)
            else:
                item = MenuItem(self.frame, self, text, command, "tooltip", underline)

                item.pack(fill='x')
                self.menu_items.append(item)

    def active_item(self):
        for item in self.menu_items:
            if item.active:
                return item
        return None

    def close(self) -> bool:
        if self.popup:
            self.popup.destroy()
            self.popup = None
            return True
        return False
