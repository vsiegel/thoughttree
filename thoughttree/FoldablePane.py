import tkinter as tk

FIRST = 0
LAST = 1


class FoldablePane(tk.PanedWindow):
    SASH_WIDTH = 8
    MIN_SIZE = 20
    def __init__(self, parent=None, folded=False, fold_size=100, **kw):
        # folding 0 (first) or 1 (second)
        super().__init__(parent, borderwidth=0, sashwidth=FoldablePane.SASH_WIDTH, sashrelief=tk.RIDGE, **kw)

        def keep_folded(event):
            pane: FoldablePane = event.widget
            if pane.folded:
                pane.sash_max()
                # print(f"{event.widget.panecget(event.widget.panes()[1], 'height')=}")
                print(f"FP: {pane.winfo_height()=}")
                print(f"FP: {pane.winfo_width()=}")
                print(f"FP: {pane['orient']=}")

        def first_folding(event):
            pane: FoldablePane = event.widget
            print(f"first_folding: {pane.size1d()=}")
            if self.folded:
                self.folded = False
                self.fold()

            pane.unbind("<Configure>", pane.first_folding_bind)

        self.folding_pane = folding_pane
        self.folded = folded
        self.size = size
        if folding_pane != 0:
            self.bind("<Configure>", keep_folded)
        self.first_folding_bind = self.bind("<Configure>", first_folding)

    def addFoldable(self, widget, **kw):
        if self.panes():
            self.folding_pane = LAST
        else:
            self.folding_pane = FIRST
        self.add(widget, **kw)
        self.foldable_widget = widget
        print(f"aF: {self.foldable_widget=}")
        print(f"aF: {self.folding_pane=}")


    def fold(self, event=None, set_folded=None):
        print(f"FP: {self.folding_pane=}")
        print(f"FP: {self.folded=}")
        print(f"FP: {self.fold_size=}")
        if self.almost_folded():
            self.folded = True
        if set_folded is None:
            self.folded = not self.folded
        else:
            self.folded = set_folded

        pane_size = self.size1d()
        sash = max(*self.sash_coord(0))
        size = sash if self.folding_pane == FIRST else pane_size - sash
        if self.folded:
            self.fold_size = pane_size - sash
            size = 1
        else:
            size = self.fold_size
        sash = size if self.folding_pane == FIRST else pane_size - size
        self.sash_place(0, sash, sash)


    def almost_folded(self):
        sash = max(*self.sash_coord(0))
        if self.folding_pane == FIRST:
            return sash < FoldablePane.MIN_SIZE
        else:
            pane_size = self.size1d()
            return pane_size - sash < FoldablePane.MIN_SIZE


    def size1d(self, widget=None):
        widget = widget or self
        if self['orient'] == 'horizontal':
            return widget.winfo_width()
        else:
            return widget.winfo_height()

    def fold_size1d(self):
        sash_pos = max(*self.sash_coord(0))
        if self.folding_pane == FIRST:
            return sash_pos
        else:
            return self.size1d() - sash_pos
