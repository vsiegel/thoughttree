import tkinter as tk
from tkinter import IntVar, DoubleVar, W, E, X, LEFT, BOTTOM, SUNKEN

from LabeledEntry import LabeledEntry


class StatusBar(tk.Frame):
    def __init__(self, parent, small_text="", message_text="", note_text="", model_text="", **kw):
        super().__init__(parent, bd=1, relief=SUNKEN, **kw)

        def validate_max_tokens(entry_value):
            if entry_value.isdigit() and 1 <= int(entry_value) <= 100000:
                return True
            else:
                return False

        # vcmd = (root.register(validate_max_tokens), '%P')
        # entry = tk.Entry(root, validate="key", validatecommand=vcmd)

        def validate_temperature(entry_value):
            try:
                value = float(entry_value)
                if 0 <= value <= 2:
                    return True
                else:
                    return False
            except ValueError:
                return False

        # vcmd = (root.register(validate_temperature), '%P')
        # entry = tk.Entry(root, validate="key", validatecommand=vcmd)



        defaults = {"bd": 1, "relief": SUNKEN}

        self.message_label = tk.Label(self, **defaults, width=20, text=message_text, anchor=W)
        self.message_label.pack(side=LEFT, padx=(5, 0), fill=X, expand=True)

        self.note_label = tk.Label(self, **defaults, width=10, text=note_text, anchor=W)
        self.note_label.pack(side=LEFT, padx=(5, 0), fill=X, expand=True)

        self.max_token_entry = LabeledEntry(self, "Max t.:", entry_width=5, **defaults)
        self.max_token_entry.pack(side=LEFT, padx=(5, 0))
        # self.max_token_entry.bind("<Return>", ui.configure_max_tokens)

        self.temperature_entry = LabeledEntry(self, "Temp.:", entry_width=3, validatecommand=validate_temperature, **defaults)
        self.temperature_entry.pack(side=LEFT, padx=(5, 0))

        self.model_label = tk.Label(self, **defaults, width=20, text=model_text, anchor=E)
        self.model_label.pack(side=LEFT, padx=(5, 0))


    def set_max_token_var(self, var: IntVar):
        self.max_token_entry.entry.config(textvariable=var)

    def set_temperature_var(self, var: DoubleVar):
        self.temperature_entry.entry.config(textvariable=var)


    @property
    def message(self):
        return self.message_label.cget('text')

    @message.setter
    def message(self, text):
        self.message_label.config(text=text)

    @property
    def note(self):
        return self.note_label.cget('text')

    @note.setter
    def note(self, text):
        self.note_label.config(text=text)

    @property
    def model(self):
        return self.model_label.cget('text')

    @model.setter
    def model(self, text):
        self.model_label.config(text=text)
