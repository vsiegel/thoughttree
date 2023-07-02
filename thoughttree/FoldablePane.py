import tkinter as tk

class FoldablePane(tk.PanedWindow):
    SASH_WIDTH = 8
    MIN_SIZE = 30
    def __init__(self, parent=None, folding_pane=0, folded=False, size=10, **kwargs):
        # folding 0 (first) or 1 (second)
        super().__init__(parent, borderwidth=0, sashwidth=FoldablePane.SASH_WIDTH, sashrelief=tk.RIDGE, **kwargs)

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


    def fold(self, event=None):
        print(f"FP: {self.folding_pane=}")
        print(f"FP: {self.folded=}")
        print(f"FP: {self.size=}")
        if self.folded or self.almost_folded():
            size = max(self.size, FoldablePane.MIN_SIZE)
            self.sash_place(0, size, size)
            self.folded = False
        else:
            self.size = max(*self.sash_coord(0))
            if self.folding_pane == 0:
                self.sash_place(0, 1, 1)
            else:
                self.sash_max()
            self.folded = True


    def sash_max(self):
        pane_size = self.size1d()
        self.sash_place(0, pane_size, pane_size)

    def almost_folded(self):
        sash = max(*self.sash_coord(0))
        if self.folding_pane == FIRST:
            return sash < FoldablePane.MIN_SIZE
        else:
            pane_size = self.size1d()
            return pane_size - sash < FoldablePane.MIN_SIZE


    def size1d(self):
        if self['orient'] == 'horizontal':
            pane_size = self.winfo_width()
        else:
            pane_size = self.winfo_height()
        return pane_size
