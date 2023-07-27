import tkinter as tk

FIRST = 0
LAST = 1


class FoldablePane(tk.PanedWindow):
    SASH_WIDTH = 8
    MIN_SIZE = 20
    def __init__(self, parent=None, folded=False, fold_size=100, **kw):
        super().__init__(parent, borderwidth=0, sashwidth=FoldablePane.SASH_WIDTH, sashrelief=tk.RIDGE, **kw)

        self.fold_size = fold_size
        self.foldable_widget = None
        self.fold_last = None
        self.takefocus = None
        self.folded = folded
        self.previous_sash = -1

        def on_double_click(event):
            self.fold(set_folded=not self.folded)
        self.bind("<Double-Button-1>", on_double_click)

    def addFoldable(self, widget, **kw):
        if self.panes():
            self.fold_last = True
        else:
            self.fold_last = False
        self.add(widget, **kw)
        self.foldable_widget = widget


    def fold(self, event=None, set_folded=None):
        pane_size = self.size1d()
        sash = max(*self.sash_coord(0))
        size = pane_size - sash if self.fold_last else sash
        if self.almost_folded():
            self.folded = True

        if set_folded is None:
            self.folded = not self.folded
        else:
            self.folded = set_folded

        if self.folded:
            self.takefocus = self.foldable_widget.cget("takefocus")
            self.foldable_widget.configure(takefocus=False)
            self.fold_size = size
            size = 1
        else:
            self.foldable_widget.configure(takefocus=self.takefocus)
            size = self.fold_size

        sash = pane_size - size if self.fold_last else size
        self.sash_place(0, sash, sash)
        return "break"

    def almost_folded(self):
        sash = max(*self.sash_coord(0))
        if self.fold_last:
            size = self.size1d() - sash
        else:
            size = sash
        return size < FoldablePane.MIN_SIZE


    def size1d(self, widget=None):
        widget = widget or self
        if self['orient'] == 'horizontal':
            return widget.winfo_width()
        else:
            return widget.winfo_height()

    def fold_size1d(self):
        sash = max(*self.sash_coord(0))
        if self.fold_last:
            return self.size1d() - sash
        else:
            return sash
