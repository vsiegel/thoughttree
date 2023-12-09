import tkinter as tk

from MenuHelpTooltip import MenuHelpTooltip


class MenuBar(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg='lightgray', bd=3, relief='raised')
        self.menus = []
        self.open_popup = None
        self.winfo_toplevel().bind("<Configure>", lambda e: self.close_other_menus(None), add=True)
        MenuHelpTooltip(self)

    def add_menu(self, menu):
        menu.pack(side='left')
        self.menus.append(menu)
        return menu

    def submenu(self, label):
        from TooltipableMenu import TooltipableMenu
        menu = TooltipableMenu(self, label)
        return self.add_menu(menu)

    def close_other_menus(self, this) -> bool:
        for menu in self.menus:
            if menu != this and menu.popup:
                if menu.close():
                    return True
        else:
            return False

    def current_menu(self):
        widget = self.winfo_containing(self.winfo_rootx(), self.winfo_rooty())
        if isinstance(widget, MenuBar):
            return None
        if widget:
            return widget.cget("label")
