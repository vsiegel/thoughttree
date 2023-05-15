import tkinter as tk


class StatusBar(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        defaults = {"text": "", "bd": 1, "relief": tk.SUNKEN, "anchor": tk.W, "font": ("Arial", 9)}
        self.small_label = tk.Label(self, **defaults, width=2)
        self.small_label.pack(side=tk.LEFT)

        self.main_label = tk.Label(self, **defaults)
        self.main_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        self.right_label = tk.Label(self, **defaults, width=20)
        self.right_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X)

    def set_small_text(self, text):
        self.small_label.config(text=text)
        self.update()

    def set_main_text(self, text):
        self.main_label.config(text=text)
        self.update()

    def set_right_text(self, text):
        self.right_label.config(text=text)
        self.update()
