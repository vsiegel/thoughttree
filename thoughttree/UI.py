import os
import tkinter as tk
from os.path import join

class UI(tk.Tk):
    icon = None
    WINDOW_ICON = None

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Thoughttree")
        self.wm_title("Thoughttree")
        self.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.set_icon(self.WINDOW_ICON)
        except:
            print("Error loading icon.")


    def close(self, event=None):
        self.is_root_destroyed = True
        self.destroy()


    def set_icon(self, window_icon):
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
