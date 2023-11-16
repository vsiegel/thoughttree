import io
import tkinter as tk
import tkinter.scrolledtext
from tkinter import END

from PaneUnfoldingStream import PaneUnfoldingStream


class Console(tk.scrolledtext.ScrolledText, io.TextIOBase):
    def __init__(self, parent, width=100, height=5, **kw):
        tk.scrolledtext.ScrolledText.__init__(self, parent, undo=True, wrap=tk.WORD, width=width, height=height,
                                              takefocus=False, font=("monospace", 10), background="#f0f0f0", **kw)
        io.TextIOBase.__init__(self)
        self.vbar.config(width=18, takefocus=False, borderwidth=2)
        self.insert(END, "Console:\n")
        self.tag_config("cost", foreground="gray60")

        self.out = self
        self.err = PaneUnfoldingStream(self, parent)

    def write(self, message):
        self.insert(END, message)
        self.see(END)

    def cost(self, message):
        self.tagged("cost", message)


    def tagged(self, tag, message):
        self.insert(END, message, (tag,))
        self.see(END)

    def tagged_out(self, tag):
        console = self
        class TaggedConsoleOut(io.TextIOBase):
            def write(self, message):
                console.insert(END, message, (tag,))
                console.see(END)
        return TaggedConsoleOut()
