import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END, CURRENT, SEL, LEFT

import tools
from Sheet import Sheet


class ResizingSheet(Sheet):
    def __init__(self, parent=None, scrollbar=False, name="rs", width=1000, **kw):
        self.resizing_frame = tk.Frame(parent, name=name + "f")
        Sheet.__init__(self, self.resizing_frame, scrollbar=scrollbar, name=name, width=width, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.copy_packing(self.resizing_frame, Sheet)
        self.parent = parent
        self.bind('<<Modified>>', self.resize_to_content, add=True)
        self.edit_modified(True)
        self.pack_propagate(False)

    def __str__(self):
        return str(self.resizing_frame)

    def resize_to_content(self, event: tk.Event):
        if self.edit_modified():
            self.count("1.0", "end lineend", "update")
            ypixels = self.count("1.0", "end lineend", 'ypixels')[0]
            self.resizing_frame.configure(height=ypixels, width=self.winfo_reqwidth())
            self.edit_modified(False)


    def copy_packing(self, frame, superclass):
        superclass_methods = vars(superclass).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(superclass_methods)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(frame, m))


if __name__ == "__main__":
    root = tk.Tk()
    tools.escapable(root)
    root.configure(background='#daeaff')
    widget = ResizingSheet(root)
    widget.pack(side=LEFT, fill=BOTH, expand=True)
    widget.insert("1.0", "Hello World")

    # widget.pack_propagate(False)
    widget.focus_set()
    root.mainloop()

