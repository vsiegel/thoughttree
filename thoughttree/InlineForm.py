import tkinter as tk
from tkinter import INSERT, BOTTOM, RIGHT, Frame, Label, Entry, TOP

from docutils.nodes import label


class InlineForm(Frame):
    def __init__(self, sheet=None, index=INSERT, title='', label1='', label2='', ok='OK', command=None):
        super().__init__(sheet, bd=0, padx=10, pady=0, background="white")
        self.sheet = sheet
        self.pack(side='top', fill='x', expand=True)

        frame = Frame(self, bd=6, relief='groove', padx=10, pady=10)
        frame.pack(side='top', fill='x', expand=True)
        self.entries = []
        self.build(frame)

        if sheet:
            self.insert(sheet, index)


    def build(self, frame):
        pass

    def get_entry(self, index):
        return self.entries[index].get()

    def insert(self, text, index=INSERT):
        index = text.index(index)
        text.tag_config("InlineForm-centered", justify='center')
        text.insert(index, "\n")
        text.window_create(index + "+1c", window=self)
        text.tag_add("InlineForm-centered", index + "+1c")
        text.insert(index + "+2c", "\n")



if __name__ == '__main__':
    f = ('Arial', 11)
    root = tk.Tk()
    sheet = tk.Text(root, font=f)
    sheet.pack()
    sheet.insert(INSERT, "text 1")

    IterateRangeInlineForm(sheet, command=lambda: sheet.insert(INSERT, "text 3"))

    sheet.insert(INSERT, "text 2")
    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()

