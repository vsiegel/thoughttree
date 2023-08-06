import io
import tkinter as tk
import tkinter.scrolledtext
from tkinter import END

from FoldablePane import FoldablePane


class Console(tk.scrolledtext.ScrolledText, io.TextIOBase):
    def __init__(self, parent, width=100, height=5, **kw):
        tk.scrolledtext.ScrolledText.__init__(self, parent, undo=True, wrap=tk.WORD, width=width, height=height,
                                              takefocus=False, font=("monospace", 8), **kw)
        io.TextIOBase.__init__(self)
        self.parent = parent
        self.vbar.config(width=18, takefocus=False, borderwidth=2)
        self.insert(END, "Console:\n")

        class UnfoldingStream(io.TextIOBase):
            def __init__(self, sink, foldable_pane):
                io.TextIOBase.__init__(self)
                self.foldable_pane = None
                if type(foldable_pane) is FoldablePane:
                    self.foldable_pane = foldable_pane
                self.sink = sink

            def write(self, message):
                if self.foldable_pane and self.foldable_pane.folded:
                    self.foldable_pane.fold()
                self.sink.write(message)

        self.out = self
        self.err = UnfoldingStream(self, parent)

    def write(self, message):
        self.insert(END, message)
        self.see(END)
