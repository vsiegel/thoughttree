import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END, CURRENT, SEL, LEFT

import tools
from Sheet import Sheet


class ResizingSheet(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent)
        self.sheet = Sheet(self, scrollbar=False, width=20, height=10, *args, **kw)
        self.sheet.pack(side=LEFT, fill=BOTH, expand=True)
        self.sheet.bind('<<Modified>>', self.resize_to_content, add=True)
        self.sheet.edit_modified(True)
        self.pack_propagate(False)

    def resize_to_content(self, event: tk.Event):
        if self.sheet.edit_modified():
            self.sheet.count("1.0", "end lineend", "update")
            ypixels = self.sheet.count("1.0", "end lineend", 'ypixels')[0]
            self.configure(height=ypixels, width=self.sheet.winfo_reqwidth())
            self.sheet.edit_modified(False)


if __name__ == "__main__":
    root = tk.Tk()
    tools.escapable(root)
    widget = ResizingSheet(root)
    widget.pack(side=LEFT, fill=BOTH, expand=True)
    # widget.pack_propagate(False)
    widget.focus_set()
    root.mainloop()

