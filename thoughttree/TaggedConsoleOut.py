import io
from tkinter import END


class TaggedConsoleOut(io.TextIOBase):
    def __init__(self, console, tag):
        io.TextIOBase.__init__(self)
        self.console = console
        self.tag = tag

    def write(self, message):
        self.console.insert(END, message, (self.tag,))
        self.console.see(END)
