import tkinter as tk
from tkinter import ACTIVE, LEFT, BOTH, scrolledtext, INSERT, SEL, END
from tkinter.simpledialog import Dialog
from tkinter.scrolledtext import ScrolledText


class TextDialog(tk.simpledialog.Dialog):
    def __init__(self, message=None, title=None, parent=None):
        self.message = message
        super().__init__(parent, title)
        # todo: context menu with "Copy Message"

    def body(self, parent):

        def select_all(event):
            text.tag_add(SEL, "1.0", END)
            text.mark_set(INSERT, "1.0")
            text.see(INSERT)

        def copy_text(event):
            self.clipboard_clear()
            text_get = text.get(1.0, tk.END)
            self.clipboard_append(text_get)

        background = self.cget("background")
        text = ScrolledText(parent, height=10, width=40, borderwidth=0, exportselection=True,
                                    highlightthickness=0, background=background, font=("sans-serif", 11))
        text.bind("<Control-a>", select_all)
        text.bind("<Control-c>", copy_text)

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
