import tkinter as tk

class LabeledEntry(tk.Frame):
    def __init__(self, parent, label_text=None, entry_width=3, textvariable=None, validatecommand=None, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.textvariable = textvariable

        self.label = tk.Label(self, text=label_text)
        self.label.pack(side="left")

        self.entry = tk.Entry(self, width=entry_width, # state="readonly", takefocus=False,
                              textvariable=self.textvariable, bd=0, highlightthickness=0, validatecommand=validatecommand)
        self.entry.pack(side="left")
        self.entry.bind("<FocusOut>", lambda e: e.widget.selection_clear())
