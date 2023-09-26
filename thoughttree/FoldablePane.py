import tkinter as tk
from tkinter import HORIZONTAL


class FoldablePane(tk.PanedWindow):
    SASH_WIDTH = 8
    MIN_SIZE = 20
    def __init__(self, parent=None, folded=False, fold_size=100, **kw):
        super().__init__(parent, borderwidth=0, sashwidth=FoldablePane.SASH_WIDTH, sashrelief=tk.RIDGE, **kw)

        self.fold_size = fold_size
        self.foldable_child = None
        self.fold_last = None
        self.takefocus = None
        self.previous_sash = -1
        self.folded = folded

        def on_double_click(event):
            self.fold()
        self.bind("<Double-Button-1>", on_double_click)

    def add(self, child, stretch="always", **kw) -> None:
        super().add(child, stretch=stretch, **kw)

    def addFoldable(self, child, stretch="never", **kw):
        self.fold_last =  bool(self.panes())
        self.add(child, stretch=stretch, **kw)
        self.foldable_child = child


    def fold(self, event=None, set_folded=None):
        if len(self.panes()) < 2:
            return
        pane_size = self.size1d()
        sash = max(*self.sash_coord(0))
        size = self.fold_last and pane_size - sash or sash

        if size < FoldablePane.MIN_SIZE:
            self.folded = True

        if set_folded is None:
            self.folded = not self.folded
        else:
            self.folded = set_folded

        if self.folded:
            self.takefocus = self.foldable_child.cget("takefocus")
            self.foldable_child.configure(takefocus=False)
            self.fold_size = size
            size = 0
        else:
            self.foldable_child.configure(takefocus=self.takefocus)
            size = self.fold_size

        sash = self.fold_last and pane_size - size or size
        self.sash_place(0, sash, sash)
        return "break"


    def size1d(self, widget=None):
        widget = widget or self
        if self['orient'] == HORIZONTAL:
            return widget.winfo_width()
        else:
            return widget.winfo_height()
