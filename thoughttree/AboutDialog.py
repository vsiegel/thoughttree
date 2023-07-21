import tkinter as tk
import subprocess

from Sheet import Sheet
from ThoughttreeConfig import conf


class AboutDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About Thoughttree")

        self.git_version = conf.git_describe_version

        tk.Label(self.dialog, font=Sheet.FONT, text="Thoughttree").pack(padx=8, pady=12)
        tk.Label(self.dialog, font=Sheet.FONT, text=self.git_version).pack(padx=16, pady=2)

        tk.Button(self.dialog, text="OK", command=self.dialog.destroy).pack(padx=8, pady=12)



# testing the AboutDialog
if __name__ == "__main__":
    root = tk.Tk()
    AboutDialog(root)
    root.withdraw()
    root.mainloop()
