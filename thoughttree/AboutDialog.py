import tkinter as tk
import tkinter.commondialog
from datetime import datetime

from Fonts import Fonts
from Sheet import Sheet
from ThoughttreeConfig import conf

class AboutDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.focus_set()
        self.grab_set()
        self.transient(parent)
        self.title("About Thoughttree")

        self.git_version = conf.git_describe_version

        start_time=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        tk.Label(self, font=Fonts.FONT, text="Thoughttree").pack(padx=8, pady=12)
        tk.Label(self, font=Fonts.FONT, text=f'{self.git_version} \nRunning since {start_time}').pack(padx=16, pady=2)

        tk.Button(self, text="OK", command=self.destroy).pack(padx=8, pady=12)

        def close_dialog(event):
            self.destroy()
        self.bind("<Escape>", close_dialog)

# testing the AboutDialog
if __name__ == "__main__":
    root = tk.Tk()
    AboutDialog(root)
    root.withdraw()
    root.mainloop()
