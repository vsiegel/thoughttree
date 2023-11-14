import tkinter as tk


class MenuItem(tk.Frame):
    def __init__(self, parent, menu, text, keystroke=None, command=None, underline=-1, example=" "):
        super().__init__(parent)
        self.menu = menu
        self.text = text
        self.configure(bg='lightgray', borderwidth=2)
        self.command = command
        self.active=False
        self.label = tk.Label(self, text=text, bg='lightgray', anchor='w', font=("Arial", 10),
                              underline=underline, padx=5, pady=0, borderwidth=2, relief='flat')
        self.key = tk.Label(self, text=keystroke, bg='lightgray', foreground='gray', anchor='w', font=("Arial", 10),
                            padx=5, pady=0, borderwidth=2, relief='flat')
        if text.startswith('C'):
            example_icon = "⇒"
        else:
            example_icon = " "
        self.example = tk.Label(self, text=example_icon, bg='lightgray', foreground='gray', anchor='w', font=("monospace", 10),
                            padx=5, pady=0, borderwidth=2, relief='flat')
        self.label.pack(side='left', fill='x', expand=True)
        self.example.pack(side='right', fill='x')
        self.key.pack(side='right', fill='x')
        if not command:
            self.label.configure(foreground='gray')
        self.bind("<Enter>", self.on_enter, add=True)
        self.bind("<Leave>", self.on_leave, add=True)
        self.bind("<Escape>", self.menu.close, add=True)
        for label in [self.label, self.key]:
            label.bind("<Button-1>", self.on_click, add=True)

    def on_enter(self, event):
        self.label.configure(bg='#efefef')
        self.key.configure(bg='#efefef')
        self.configure(relief='raised')
        self.active=True

    def on_leave(self, event):
        self.label.configure(bg='lightgray')
        self.key.configure(bg='lightgray')
        self.configure(relief='flat')
        self.active=False

    def on_click(self, event):
        try:
            self.command()
        # except Exception as ex:
        #     print(f"{ex} {self.command=}")
        finally:
            self.menu.close()
        # raise RuntimeError("on_click failed") from exception
