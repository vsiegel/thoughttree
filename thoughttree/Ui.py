import os
import sys
import tkinter as tk
from os.path import join, dirname
from tkinter.messagebox import askyesno, showwarning

from EventLog import EventLog


class Ui(tk.Frame):
    icon = None
    WINDOW_ICON = None
    current_open_uis = []
    event_log = None

    def __init__(self, title="Thoughttree", name="ui", icon_path=None, closeable=True):
        if not tk._default_root:
            self.root = tk.Tk()
            self.main_window = True
            if not os.getenv("THOUGHTTREE_DEBUG") in ["", "0", None]:
                Ui.event_log = EventLog(self.root, "<Key>")
        else:
            self.root = tk.Toplevel()
            self.main_window = False
        tk.Frame.__init__(self, self.root, name=name)

        self.closeable = closeable
        self.is_root_destroyed = False

        Ui.current_open_uis.append(self)
        n = len(Ui.current_open_uis)
        number = n > 1 and " " + str(n) or ""
        title = f"{title}{number}"
        self.window_setup(title, icon_path)

    def configure_geometry(self, argv, root_geometry="800x600", min_size=(200, 200)):
        if argv and "-geometry" in argv:
            geometry = argv[argv.index("-geometry") + 1]
            if geometry.startswith('+'):
                geometry = root_geometry + geometry
            print(f"{geometry=}")
        else:
            geometry = root_geometry
        self.root.geometry(geometry)
        self.root.minsize(*min_size)

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
        self.root.lift()

    def toggle_fullscreen(self, event=None):
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)
        else:
            self.root.attributes("-fullscreen", True)

    def close(self, event=None):
        try:
            if self.main_window and len(Ui.current_open_uis) > 1:
                showwarning("Can not Close Main Window", "The main window that opened first can not be closed individually.", parent=self)
                return

            if not self.is_initially_modified() or self.closeable or askyesno("Close Window", "Are you sure you want to close this window?", parent=self):
                self.pack_forget()

                # if self in Ui.current_open_uis:
                Ui.current_open_uis.remove(self)
                self.is_root_destroyed = True
                self.root.destroy()
        except Exception as e:
            print(f"{e=}")


    def quit(self, event=None, label="Quit"):
        if not self.is_initially_modified() or askyesno(label, "Are you sure you want to close all windows and quit?", parent=self):
            self.pack_forget()
            sys.exit(0)

    def is_initially_modified(self):
        return True

    def set_icon(self, window_icon):
        if not window_icon or Ui.icon:
            return
        def get_icon_file_name(icon_base_name):
            return join(dirname(os.path.abspath(__file__)), icon_base_name)

        try:
            abs_name = str(get_icon_file_name(window_icon))
            photo_image = tk.PhotoImage(file=abs_name)
            Ui.icon = photo_image
            self.root.iconphoto(True, photo_image) # Note: has no effect when running in PyCharm IDE
        except Exception as e:
            print("Error loading icon:", e)
