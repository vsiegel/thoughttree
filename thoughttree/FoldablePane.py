import tkinter as tk


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

    def addFoldable(self, child, **kw):
        self.fold_last =  bool(self.panes())
        self.add(child, stretch="never", **kw)
        self.foldable_child = child


    def fold(self, event=None, set_folded=None):
        pane_size = self.size1d()
        sash = max(*self.sash_coord(0))
        size = pane_size - sash if self.fold_last else sash

        if set_folded is None:
            self.folded = not self.folded
        else:
            self.folded = set_folded
        if self.almost_folded():
            self.folded = True

        if not self.folded:
            self.takefocus = self.foldable_child.cget("takefocus")
            self.foldable_child.configure(takefocus=False)
            self.fold_size = size
            size = 0
        else:
            self.foldable_child.configure(takefocus=self.takefocus)
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
