import tkinter as tk


class StatusBar(tk.Frame):
    def __init__(self, master, small_text="", message_text="", note_text="", model_text="", **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        defaults = {"bd": 1, "relief": tk.SUNKEN, "anchor": tk.W, "font": ("Arial", 10)}
        self.symbol_label = tk.Label(self, **defaults, width=2, text=small_text)
        self.symbol_label.pack(side=tk.LEFT)

        self.message_label = tk.Label(self, **defaults, width=30, text=message_text)
        self.message_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        self.note_label = tk.Label(self, **defaults, text=note_text)
        self.note_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        self.model_label = tk.Label(self, **defaults, width=20, text=model_text)
        self.model_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X)

        self.pack(side=tk.BOTTOM, fill=tk.X)


    @property
    def symbol(self):
        return self.symbol_label.cget('text')

    @symbol.setter
    def symbol(self, text):
        self.symbol_label.config(text=text)

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
