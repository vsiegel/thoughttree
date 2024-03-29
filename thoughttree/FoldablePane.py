import tkinter as tk
from tkinter import HORIZONTAL

import tools
from Sheet import Sheet
from Tooltip import Tooltip


class FoldablePane(tk.PanedWindow):

    MIN_SIZE = 20
    def __init__(self, parent=None, folded=False, fold_size=100, name="fp", panel=None, key=None, **kw):
        super().__init__(parent, borderwidth=0, sashwidth=12, sashrelief=tk.RIDGE, name=name, **kw)

        self.fold_size = fold_size
        self.foldable_child = None
        self.fold_last = None
        self.takefocus = None
        self.previous_sash = -1
        self.folded = folded

        self.bind("<Double-Button-1>", self.fold)
        if panel and key:
            key_help = f"Open or close {panel} with {key} or from View menu.\n\n"
        else:
            key_help = ""
        self.tooltip = FoldablePaneTooltip(self, key_help + tools.text_block(
            "This is a movable separator between panes. It can be used to resize both sides"
            " by dragging the this separating line, or collapsing one of it, by a double click."
            "The separating line stays visible and restores the hidden pane on double click."))


    def add(self, child, stretch="always", **kw) -> None:
        self.tooltip and self.tooltip.bind_panel(child)
        super().add(child, stretch=stretch, **kw)

    def addFoldable(self, child, stretch="never", **kw):
        self.foldable_child = child
        self.fold_last =  bool(self.panes())
        self.add(child, stretch=stretch, **kw)


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
            self.takefocus and self.foldable_child.focus_set()
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


class FoldablePaneTooltip(Tooltip):
    def __init__(self, pane: FoldablePane, text):
        super().__init__(pane, text)
        self.widget = pane

        self.show_delay_ms = 300
        self.hide_delay_ms = 1000

        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def bind_panel(self, child):
        child.bind("<Enter>", self.hide)


    def on_sash(self, event=None):
        # identification = self.widget.identify(event.x, event.y)
        w = self.widget
        identification = w.identify(w.winfo_pointerx() - w.winfo_rootx(), w.winfo_pointery() - w.winfo_rooty())
        return bool(identification and identification[1] == "sash")


    def refresh(self, event=None):
        if self.tip:
            super().refresh(event)
        else:
            self.show_later(event)

    def show(self, event=None):
        if self.on_sash(event):
            super().show(event)

    def bind_tip(self):
        self.widget.bind("<Leave>", self.hide, add=True)
        self.widget.bind("<Motion>", self.refresh, add=True)



if __name__ == "__main__":
    root = tk.Tk()
    fp = FoldablePane(root)
    fp.pack(fill=tk.BOTH, expand=True)
    fp.addFoldable(Sheet(fp, text="Hello"))
    fp.addFoldable(Sheet(fp, text="World"))
    root.mainloop()
