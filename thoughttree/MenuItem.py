import tkinter as tk


class MenuItem(tk.Frame):
    def __init__(self, parent, menu, text, keystroke=None, command=None, underline=-1):
        super().__init__(parent)
        self.menu = menu
        self.text = text
        self.configure(bg='lightgray', borderwidth=2)
        self.command = command
        self.active=False
        self.label = tk.Label(self, text=text, bg='lightgray', anchor='w', font=("Arial", 10),
                              underline=underline, padx=5, pady=0, borderwidth=2, relief='flat')
        self.key_label = tk.Label(self, text=keystroke, bg='lightgray', foreground='gray', anchor='w', font=("Arial", 10),
                              padx=5, pady=0, borderwidth=2, relief='flat')
        if not command:
            self.label.configure(foreground='gray')
        self.bind("<Enter>", self.on_enter, add=True)
        self.bind("<Leave>", self.on_leave, add=True)
        self.label.bind("<Button-1>", self.on_click, add=True)
        self.label.bind("<Escape>", self.menu.close, add=True)
        self.label.pack(side='left', fill='x', expand=True)
        self.key_label.pack(side='right', fill='x')

    def on_enter(self, event):
        self.label.configure(bg='#efefef')
        self.key_label.configure(bg='#efefef')
        self.configure(relief='raised')
        self.active=True

    def on_leave(self, event):
        self.label.configure(bg='lightgray')
        self.key_label.configure(bg='lightgray')
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
