import tkinter as tk
from tkinter import ACTIVE, LEFT, BOTH
from tkinter.simpledialog import Dialog


class TextDialog(tk.simpledialog.Dialog):
    def __init__(self, message=None, title=None, parent=None):
        self.message = message
        super().__init__(parent, title)
        # todo: Control-A for select all.
        # todo: context menu with "Copy Message"

    def body(self, parent):
        background = self.cget("background")
        text = tk.Text(parent, height=10, width=30, borderwidth=0,
                       highlightthickness=0, background=background, font=("sans-serif", 11))
        text.insert(tk.END, self.message)
        text.config(state=tk.DISABLED)
        text.pack(fill=BOTH, expand=True)
        return text

    def buttonbox(self):

        box = tk.Frame(self)

        button = tk.Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        button.pack(side=LEFT, padx=20, pady=20)
        self.pack_slaves()[0].pack(fill=BOTH, expand=True, padx=25, pady=25) # hack to repack dialog content to expand

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    import lorem
    l = lorem.text()
    l= "kjhnkl"
    d = TextDialog(message=l, title="Hello World!")
