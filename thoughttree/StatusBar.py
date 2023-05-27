import tkinter as tk


class StatusBar(tk.Frame):
    def __init__(self, master, small_text="", main_text="", right_text="",  **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        defaults = {"bd": 1, "relief": tk.SUNKEN, "anchor": tk.W, "font": ("Arial", 9)}
        self.small_label = tk.Label(self, **defaults, width=2, text=small_text)
        self.small_label.pack(side=tk.LEFT)

        self.main_label = tk.Label(self, **defaults, text=main_text)
        self.main_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        self.right_label = tk.Label(self, **defaults, width=20, text=right_text)
        self.right_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X)

        self.pack(side=tk.BOTTOM, fill=tk.X)


    @property
    def small_text(self):
        return self.small_label.cget('text')

    @small_text.setter
    def small_text(self, text):
        self.small_label.config(text=text)
        self.update()

    @property
    def main_text(self):
        return self.main_label.cget('text')

    @main_text.setter
    def main_text(self, text):
        self.main_label.config(text=text)
        self.update()

    @property
    def right_text(self):
        return self.right_label.cget('text')

    @right_text.setter
    def right_text(self, text):
        self.right_label.config(text=text)
        self.update()
