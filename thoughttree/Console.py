import io
import tkinter as tk
import tkinter.scrolledtext
from tkinter import END

from PaneUnfoldingStream import PaneUnfoldingStream
from Sheet import Sheet
from TaggedConsoleOut import TaggedConsoleOut


class Console(Sheet, io.TextIOBase):
    def __init__(self, parent, width=100, height=5, **kw):
        tk.scrolledtext.ScrolledText.__init__(self, parent, undo=True, wrap=tk.WORD, width=width, height=height,
                                              takefocus=False, font=("monospace", 10), background="#f6f6f6", **kw)
        io.TextIOBase.__init__(self)
        self.vbar.config(width=18, takefocus=False, borderwidth=2)
        self.insert(END, "Console:\n")

        self.tag_config("system", foreground="#edd4e8", font=("Helvetica", 12))
        self.tag_config("user", foreground="#4e8054", font=("Helvetica", 12))
        self.tag_config("assistant", foreground="#5473cd", font=("Helvetica", 12))
        self.tag_config("debug", foreground="#666666", font=("Helvetica", 9))
        self.tag_config("info", foreground="black", font=("Helvetica", 12))
        self.tag_config("warn", foreground="#d95740", font=("Helvetica", 12, "bold"))
        self.tag_config("error", foreground="firebrick", font=("Helvetica", 12, "bold"))
        self.tag_config("critical", foreground="firebrick", background="light yellow", font=("Helvetica", 12, "bold"))
        self.tag_config("cost", foreground="#999999", font=("Helvetica", 12))
        self.out = self
        self.err = PaneUnfoldingStream(self, parent)


    def write(self, message):
        self.insert(END, message)
        self.see(END)


    def tagged(self, tag, message):
        self.insert(END, message + "\n", (tag,))
        self.see(END)


    def tagged_out(self, tag):
        return TaggedConsoleOut(self, tag)
