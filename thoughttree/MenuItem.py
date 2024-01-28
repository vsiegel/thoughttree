import tkinter as tk


class MenuItem(tk.Frame):
    def __init__(self, parent, menu, text, keystroke=None, command=None, underline=-1, example=" "):
        super().__init__(parent)
        self.menu = menu
        self.text = text
        self.configure(bg='lightgray', borderwidth=2)
        self.command = command
        self.active=False

        args = {'bg': 'lightgray', 'anchor': 'w', 'font': ("Arial", 12), 'padx': 5, 'pady': 0, 'borderwidth': 2, 'relief': 'flat'}
        self.label = tk.Label(self, text=text, **args, underline=underline)
        self.key = tk.Label(self, text=keystroke, **args, foreground='gray')
        if text.startswith('C'):
            example_icon = "⇒"
        else:
            example_icon = " "
        args = {**args, 'font': ("monospace", 12)}
        self.demo = tk.Label(self, text=example_icon, **args, foreground='gray')

        self.label.pack(side='left', fill='x', expand=True)
        self.demo.pack(side='right', fill='x')
        self.key.pack(side='right', fill='x')
        if not command:
            self.label.configure(foreground='gray')
        self.bind("<Enter>", self.on_enter, add=True)
        self.bind("<Leave>", self.on_leave, add=True)
        self.bind("<Escape>", self.menu.close, add=True)
        for label in [self.label, self.key]:
            label.bind("<Button-1>", self.call_command, add=True)
        self.demo.bind("<Button-1>", self.show_demo, add=True)

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

    def call_command(self, event):
        self.menu.close()
        self.command and self.command()

    def show_demo (self, event):
        self.menu.close()
        self.command and self.command() # todo
