import tkinter as tk
from tkinter import INSERT, BOTTOM, RIGHT, Frame, Label, Entry

import lorem


class InlineForm(Frame):
    def __init__(self, text=None, index=INSERT, title='', label1='', label2='', ok='OK', command=None):
        super().__init__(text, bd=0, padx=10, pady=30, background="white")
        self.pack(side='top', fill='x', expand=True)
        f = ('Arial', 11)

        fr = Frame(self, bd=6, relief='groove', padx=10, pady=10)
        fr.pack(side='top', fill='x', expand=True)

        Label(fr, text=title, font=('Arial', 13)).pack(side='top', fill='x', expand=True, padx=5, pady=5)

        self.entries = []
        for label in [label1, label2]:
            frame = Frame(fr, bd=4, relief='flat', padx=10, pady=10)
            entry = Entry(frame, font=f)
            entry.pack(side=RIGHT)
            Label(frame, text=label, font=f).pack(side=RIGHT, fill='x')
            self.entries.append(entry)
            frame.pack(side='top', fill='x', expand=True)

        tk.Button(fr, text=ok, font=f, command=command).pack(side=BOTTOM, padx=10, pady=10)

        if text:
            self.insert(text, index)


    def get_entry(self, index):
        return self.entries[index].get()

    def insert(self, text, index=INSERT):
        index = text.index(index)
        text.tag_config("InlineForm-centered", justify='center')
        text.insert(index, "\n")
        text.window_create(index + "+1c", window=self)
        text.tag_add("InlineForm-centered", index + "+1c")
        text.insert(index + "+2c", "\n")



class IterateRangeInlineForm(InlineForm):
    def __init__(self, text=None, index=INSERT,
                 title='Complete for each value',
                 label1='Range or Expression:',
                 label2='Placeholder:',
                 ok='OK',
                 command=None):
        super().__init__(text, index, title, label1, label2, ok, command)

    def get_range(self):
        return self.get_entry(0)

    def get_placeholder(self):
        return self.get_entry(1)



if __name__ == '__main__':
    f = ('Arial', 11)
    root = tk.Tk()
    text = tk.Text(root, font=f)
    text.pack()
    text.insert(INSERT, lorem.paragraph())

    IterateRangeInlineForm(text, command=lambda: text.insert(INSERT, lorem.paragraph()))

    text.insert(INSERT, lorem.paragraph())
    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()

