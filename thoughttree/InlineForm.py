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



class IterateRangeInlineForm(InlineForm):
    def __init__(self, sheet=None, index=INSERT,
                 command=None):
        super().__init__(sheet, index)
        sheet.undo_separator()
        def on_ok():
            pass
        self.bind('<Return>', on_ok)

    def build(self, frame):
        font = ('Arial', 11)

        Label(frame, text='Complete for each value', font=('Arial', 13)).pack(side='top', fill='x', expand=True, padx=5, pady=5)

        def labeled_entry(label_text):
        # for label in [label1, label2]:
            label_frame = Frame(frame, bd=4, relief='flat', padx=10, pady=10)
            label = Label(label_frame, text=label_text, font=font)
            entry = Entry(label_frame, font=font)
            self.entries.append(entry)
            label_frame.pack(side='top', fill='x', expand=True)
            return label, entry

        def on_ok(e=None):
            self.sheet.focus_set()
            return "break"
        label, entry = labeled_entry('Range or Expression:')
        label.pack(side=TOP, fill='x')
        entry.pack(side=TOP, fill='x')
        entry.focus_set()
        entry.bind("<Control-Return>", on_ok)
        label, entry = labeled_entry('Placeholder:')
        entry.pack(side=RIGHT)
        entry.insert(0, "@")
        entry.bind("<Control-Return>", on_ok)
        label.pack(side=RIGHT, fill='x')

        frame.bind("<FocusIn>", self.sheet.cursorline.clear)

        button = tk.Button(frame, text='OK', font=font, command=on_ok)
        button.pack(side=BOTTOM, padx=10, pady=10)
        button.bind('<Return>', on_ok)


    def get_range(self):
        return self.get_entry(0)

    def get_placeholder(self):
        return self.get_entry(1)



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

