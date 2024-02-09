import re
import tkinter as tk
from tkinter import INSERT
from tkinter.ttk import Treeview

from Config import conf
from MenuBar import MenuBar
from MenuHelpTooltip import MenuHelpTooltip
from MenuItem import MenuItem
from menu_help_texts import menu_help



class TooltipableMenu(tk.Frame):
    # Replacing tk.Menu, because tooltips on menu items do not work under MS Windows.
    def __init__(self, parent, text, **kw):
        super().__init__(parent, bg='lightgray', borderwidth=0)
        self.parent = parent
        self.old_focus = None
        self.label = tk.Label(self, text=text, font=("Arial", 12), bg='lightgray', padx=6, pady=5)
        self.label.bind("<Enter>", self.keep_open, add=True)
        self.label.bind("<Button-1>", self.toggle_open, add=True)
        self.label.pack(side='left')
        self.items = []
        self.menu_items = []
        self.popup = None
        self.frame = None


    def item(self, label, keystroke=None, command=None, underline=-1, menu2=None, add=False, to="Text"):
        if conf.debug and not label in menu_help:
            print("Warning: Help missing for \"" + label + "\"")
        keystroke = self.fix_key_letter_case(keystroke)
        if to == "all":
            self.winfo_toplevel().bind_all(keystroke, command, add=add)
        elif to == "this":
            self.winfo_toplevel().bind(keystroke, command, add=add)
        else:
            self.winfo_toplevel().bind_class(to, keystroke, command, add=add)
        accelerator = self.accelerator_label(keystroke)
        self.items.append((label, accelerator, command, underline))
        if menu2:
            menu2.item(label, None, command, underline, add=add)

    def cascade(self, label, menu, underline=-1):
        self.items.append((label, None, menu, "tooltip", underline))

    def separator(self):
        self.items.append(('-', '-', '-', -1))

    def insert_command(self, index, label, underline=-1, accelerator=None, state=tk.NORMAL, command=None):
        pass

    def keep_open(self, event):
        if self.parent:
            was_open = self.parent.close_other_menus(self)
            if was_open:
                self.create_popup(event)

    def toggle_open(self, event):
        if self.popup and self.popup.state() == "normal":
            self.close(event)
        else:
            self.create_popup(event)

    def create_popup(self, event, x=None, y=None):
        if not self.popup:
            self.popup = tk.Toplevel(self, bd=3, relief='raised', bg='lightgray')
            self.popup.wm_overrideredirect(True)
            # self.popup.wm_attributes("-topmost", True)
            self.popup.transient(self.winfo_toplevel())

            self.frame = tk.Frame(self.popup, takefocus=True, bg='lightgray')
            self.frame.pack()
            self.old_focus = self.focus_get()
            # self.frame.focus_set()

            def on_button(e):
                self.frame.grab_release()
                self.close(e)

            self.frame.bind("<Escape>", self.close, add=True)
            self.frame.bind("<Button>", on_button, add=True)
            self.popup.bind("<Enter>", lambda e: self.frame.grab_set(), add=True)
            self.popup.bind("<Enter>", self.keep_open, add=True)
            self.popup.bind("<Escape>", self.close, add=True)
            MenuHelpTooltip(self.frame)
            self.populate_menu()
            if isinstance(self.parent, MenuBar):
                self.parent.open_popup = self.popup
        # elif not self.popup.state() == 'normal':
        else:
            # print(f"{self.popup.state()}")
            self.popup.deiconify()
            self.popup.focus_set()
            self.popup.update()
        # print(f"{self.popup.state()}")

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
            widget = event.widget
            x, y = 0, 0
            if isinstance(widget, tk.Text):
                x, y, *_ = widget.bbox(INSERT)
            elif isinstance(widget, Treeview):
                x, y, *_ = widget.bbox(widget.focus())
            x += widget.winfo_rootx()
            y += widget.winfo_rooty()
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
        # print(f"close {event=} {self.label.cget('text')=} {self.popup.state()=}")
        if self.popup and self.popup.state() == 'normal':
            self.popup.withdraw()
            if self.old_focus:
                 self.old_focus.focus_set()
            # self.popup.destroy()
            # self.popup = None
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


class CommandDisplayingMenu(TooltipableMenu):
    def __init__(self, statusbar, **kw):
        super().__init__(None, "Command Displaying Menu", **kw)
        self.statusbar = statusbar

    def command_status(self, command, label, keystroke):
        def show_call():
            message = label + " " + keystroke
            self.statusbar.show_message(message)
            command()
        return show_call


    def item(self, label, keystroke=None, command=None, underline=-1, menu2=None, add=False, to="Text"):
        command = self.command_status(command, label, keystroke)
        super().item(label, keystroke, command, underline, menu2, add, to)


