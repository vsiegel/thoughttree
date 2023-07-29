import os
import tkinter as tk
from os.path import join
from tkinter import messagebox


class UI(tk.Tk):
    icon = None
    WINDOW_ICON = None
    uis = []

    def __init__(self, name="", icon_path=None):
        tk.Tk.__init__(self)
        UI.uis.append(self)
        self.title(name)
        self.wm_title(name)
        self.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.set_icon(icon_path)
        except:
            print("Error loading icon.")


    def close(self, event=None):
        result = messagebox.askyesno("Quit", "Are you sure you want to quit?", parent=self)
        if result:
            self.is_root_destroyed = True
            self.destroy()


    def set_icon(self, window_icon):
        if not window_icon:
            return
        def get_icon_file_name(icon_base_name):
            return join(os.path.dirname(os.path.abspath(__file__)), icon_base_name)

        if UI.icon:
            return
        try:
            abs_name = str(get_icon_file_name(window_icon))
            photo_image = tk.PhotoImage(file=abs_name)
            UI.icon = photo_image
            self.iconphoto(True, photo_image) # Note: has no effect when running in PyCharm IDE
        except Exception as e:
            print("Error loading icon:", e)
