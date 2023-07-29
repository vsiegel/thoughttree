import tkinter as tk
from tkinter import IntVar, DoubleVar, W, E, X, LEFT, BOTTOM, SUNKEN

from LabeledLabel import LabeledLabel


class StatusBar(tk.Frame):
    def __init__(self, master, small_text="", message_text="", note_text="", model_text="", **kw):
        super().__init__(master, bd=1, relief=SUNKEN, **kw)
        self.master = master

        defaults = {"bd": 1, "relief": SUNKEN}

        self.message_label = tk.Label(self, **defaults, width=20, text=message_text, anchor=W)
        self.message_label.pack(side=LEFT, padx=(5, 0), fill=X, expand=True)

        self.note_label = tk.Label(self, **defaults, width=10, text=note_text, anchor=W)
        self.note_label.pack(side=LEFT, padx=(5, 0), fill=X, expand=True)

        self.max_token_label = LabeledLabel(self, "Max t.:", entry_width=5, **defaults)
        self.max_token_label.pack(side=LEFT, padx=(5, 0))

        self.temperature_label = LabeledLabel(self, "Temp.:", entry_width=3, **defaults)
        self.temperature_label.pack(side=LEFT, padx=(5, 0))

        self.model_label = tk.Label(self, **defaults, width=20, text=model_text, anchor=E)
        self.model_label.pack(side=LEFT, padx=(5, 0))


    def set_max_token_var(self, var: IntVar):
        self.max_token_label.entry.config(textvariable=var)

    def set_temperature_var(self, var: DoubleVar):
        self.temperature_label.entry.config(textvariable=var)


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
