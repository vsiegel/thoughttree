import tkinter as tk
from tkinter import HORIZONTAL

import tools
from Sheet import Sheet
from Tooltip import Tooltip


class FoldablePane(tk.PanedWindow):

    class FoldablePaneTooltip(Tooltip):
        def __init__(self, widget, text, **kw):
            super().__init__(widget, text, **kw)
            self.widget.bind("<Enter>", self.show)
            self.widget.bind("<Leave>", self.hide)

    MIN_SIZE = 20
    def __init__(self, parent=None, folded=False, fold_size=100, name="fp", **kw):
        super().__init__(parent, borderwidth=0, sashwidth=9, sashrelief=tk.RIDGE, name=name, **kw)

        self.fold_size = fold_size
        self.foldable_child = None
        self.fold_last = None
        self.takefocus = None
        self.previous_sash = -1
        self.folded = folded

        self.bind("<Double-Button-1>", self.fold)
        FoldablePane.FoldablePaneTooltip(self, tools.text_block("This is a movable separator between panes. It can be used to resize both sides"
                      " by dragging the this separating line, or collapsing omne of it, (...), by a double click."
                      "The separating line stays visible and restores the hidden pane on double click."
                      "Alternatively, the command '...' in menu View or the keystroke '...' can be used to toggle the visibility of '...'"))
        # tools.bind_to_all_events(self, excluded="Motion, Expose")
        tools.bind_to_all_events(self, included="Enter, Leave")


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
        size = abs(self.fold_last and pane_size - sash or sash)

        if size < FoldablePane.MIN_SIZE:
            self.folded = True

        if set_folded is None:
            self.folded = not self.folded
        else:
            self.folded = set_folded

        if self.folded:
            if not isinstance(self.foldable_child, FoldablePane):
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

if __name__ == "__main__":
    root = tk.Tk()
    fp = FoldablePane(root)
    fp.pack(fill=tk.BOTH, expand=True)
    fp.addFoldable(Sheet(fp, text="Hello"))
    fp.addFoldable(Sheet(fp, text="World"))
    root.mainloop()
