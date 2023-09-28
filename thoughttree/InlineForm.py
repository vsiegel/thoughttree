import tkinter as tk
from tkinter import INSERT, Frame



class InlineForm(Frame):
    def __init__(self, sheet=None, index=INSERT):
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
        # text.insert(index, "\n")
        text.window_create(index + "+1c", window=self)
        text.tag_add("InlineForm-centered", index + "+1c")
        # text.insert(index + "+2c", "\n")
