import tkinter as tk

from Fonts import Fonts
from tools import escapable


class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class MenuItem(tk.Frame):
    def __init__(self, parent, menu, text, command, tooltip=None):
        super().__init__(parent)
        self.menu = menu
        self.configure(bg='lightgray')
        self.command = command
        self.label = tk.Label(self, text=text, bg='lightgray', anchor='w', font=Fonts.FONT, padx=5, pady=5, borderwidth=1, relief='flat')
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
        self.label.pack(fill='x')
        if tooltip:
            self.tooltip = ToolTip(self.label)
            self.tooltip_text = tooltip
        else:
            self.tooltip = None

    def on_enter(self, event):
        self.label.configure(bg='#efefef', relief='raised')
        if self.tooltip:
            self.tooltip.showtip(self.tooltip_text)

    def on_leave(self, event):
        self.label.configure(bg='lightgray', relief='flat')
        if self.tooltip:
            self.tooltip.hidetip()

    def on_click(self, event):
        self.command()
        self.menu.close()

class MenuBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='lightgray', bd=3, relief='raised')
        self.menus: [TooltipableMenu] = []

    def add_menu(self, text):
        menu = TooltipableMenu(self, text)
        menu.pack(side='left')
        self.menus.append(menu)
        return menu

    def close_other_menus(self, this) -> bool:
        for menu in self.menus:
            if menu != this and menu.popup:
                if menu.close():
                    return True
        else:
            return False

class TooltipableMenu(tk.Frame):
    # Replacing tk.Menu, because tooltips on menu items do not work under MS Windows.
    def __init__(self, parent, text):
        super().__init__(parent, bg='lightgray', padx=6, pady=5)
        self.parent = parent
        self.label = tk.Label(self, text=text, font=Fonts.FONT, bg='lightgray')
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
        self.label.pack(side='left')
        self.items = []
        self.popup = None

    def add_menu_item(self, text, command, tooltip=None):
        self.items.append((text, command, tooltip))

    def on_enter(self, event):
        was_open = self.parent.close_other_menus(self)
        if was_open:
            self.create_menu_window()

    def on_leave(self, event):
        pass
        # self.close()

    def on_click(self, event):
        if self.popup:
            self.close()
        else:
            self.create_menu_window()

    def create_menu_window(self):
        self.popup = tk.Toplevel(self, bd=3, relief='raised')
        self.popup.wm_overrideredirect(True)
        self.popup.wm_geometry(f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height()}")
        self.popup.bind("<Enter>", self.on_enter)
        for text, command, tooltip in self.items:
            item = MenuItem(self.popup, self, text, command, tooltip)
            item.pack(fill='x')

    def close(self) -> bool:
        if self.popup:
            self.popup.destroy()
            self.popup = None
            return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    menubar = MenuBar(root)
    menubar.pack(fill='x')

    # File menu
    file_menu = menubar.add_menu("File")
    file_menu.add_menu_item("New", lambda: print("New file"), "Create a new file")
    file_menu.add_menu_item("Open", lambda: print("Open file"), "Open an existing file")
    file_menu.add_menu_item("Save", lambda: print("Save file"), "Save current file")
    file_menu.add_menu_item("Save As", lambda: print("Save file as"), "Save current file with a new name")
    file_menu.add_menu_item("Exit", root.quit, "Exit the application")

    # Edit menu
    edit_menu = menubar.add_menu("Edit")
    edit_menu.add_menu_item("Cut", lambda: print("Cut"), "Cut selected text")
    edit_menu.add_menu_item("Copy", lambda: print("Copy"), "Copy selected text")
    edit_menu.add_menu_item("Paste", lambda: print("Paste"), "Paste from clipboard")
    edit_menu.add_menu_item("Select All", lambda: print("Select All"), "Select all text")

    # View menu
    view_menu = menubar.add_menu("View")
    view_menu.add_menu_item("Zoom In", lambda: print("Zoom In"), "Increase the text size")
    view_menu.add_menu_item("Zoom Out", lambda: print("Zoom Out"), "Decrease the text size")

    # Help menu
    help_menu = menubar.add_menu("Help")
    help_menu.add_menu_item("About", lambda: print("About"), "Information about this application")

    root.mainloop()