import os
import tkinter as tk
from os.path import join
from tkinter import messagebox


class Ui(tk.Frame):
    icon = None
    WINDOW_ICON = None
    current_open_uis = []

    def __init__(self, name="", icon_path=None):
        if tk._default_root:
            self.first_window = False
            self.root = tk.Toplevel()
        else:
            self.first_window = True
            self.root = tk.Tk()
        tk.Frame.__init__(self, self.root)

        self.is_root_destroyed = False
        Ui.current_open_uis.append(self)
        name = f"{name} {len(Ui.current_open_uis)}"
        self.root.title(name)
        self.root.wm_title(name)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.set_icon(icon_path)
        except:
            print("Error loading icon.")

    def toTop(self):
        self.root.attributes("-topmost", True)
        self.root.attributes("-topmost", False)

    def close(self, event=None):
        result = messagebox.askyesno("Quit", "Are you sure you want to quit?", parent=self)
        if result:
            Ui.current_open_uis.remove(self)
            self.is_root_destroyed = True
            self.root.destroy()


    def set_icon(self, window_icon):
        if not window_icon:
            return
        def get_icon_file_name(icon_base_name):
            return join(os.path.dirname(os.path.abspath(__file__)), icon_base_name)

        if Ui.icon:
            return
        try:
            abs_name = str(get_icon_file_name(window_icon))
            photo_image = tk.PhotoImage(file=abs_name)
            Ui.icon = photo_image
            self.root.iconphoto(True, photo_image) # Note: has no effect when running in PyCharm IDE
        except Exception as e:
            print("Error loading icon:", e)
