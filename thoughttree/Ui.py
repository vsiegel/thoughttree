import os
import tkinter as tk
from os.path import join, dirname
from tkinter import messagebox
from tkinter.messagebox import askyesno, showwarning


class Ui(tk.Frame):
    icon = None
    WINDOW_ICON = None
    current_open_uis = []

    def __init__(self, name="", icon_path=None, closeable=True):
        if not tk._default_root:
            self.root = tk.Tk()
            self.main_window = True
        else:
            self.root = tk.Toplevel()
            self.main_window = False
        tk.Frame.__init__(self, self.root)

        self.closeable = closeable
        self.is_root_destroyed = False

        Ui.current_open_uis.append(self)
        name = f"{name} {len(Ui.current_open_uis)}"

        self.window_setup(name, icon_path)

    def window_setup(self, name, icon_path):
        self.root.title(name)
        self.root.wm_title(name)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.set_icon(icon_path)
        except:
            print("Error loading icon.")

        if self.closeable:
            def close(event):
                self.root.destroy()
            self.root.bind("<Escape>", close)

    def toTop(self):
        self.root.attributes("-topmost", True)
        self.root.attributes("-topmost", False)


    def was_modified(self):
        return True

    def close(self, event=None):
        if self.main_window and len(Ui.current_open_uis) > 1:
            showwarning("Can not Close Main Window", "The main window that opened first can not be closed individually.", parent=self)
            return

        if not self.was_modified() or self.closeable or askyesno("Close Window", "Are you sure you want to close this window?", parent=self):
            Ui.current_open_uis.remove(self)
            self.is_root_destroyed = True
            self.root.destroy()

    def quit(self, event=None, label="Quit"):
        if askyesno(label, "Are you sure you want to quit all windows?", parent=self):
            uis = [ui for ui in Ui.current_open_uis if ui != self] + [self]
            for ui in uis:
                ui.is_root_destroyed = True
                ui.root.destroy()


    def set_icon(self, window_icon):
        if not window_icon:
            return
        def get_icon_file_name(icon_base_name):
            return join(dirname(os.path.abspath(__file__)), icon_base_name)

        if Ui.icon:
            return
        try:
            abs_name = str(get_icon_file_name(window_icon))
            photo_image = tk.PhotoImage(file=abs_name)
            Ui.icon = photo_image
            self.root.iconphoto(True, photo_image) # Note: has no effect when running in PyCharm IDE
        except Exception as e:
            print("Error loading icon:", e)
