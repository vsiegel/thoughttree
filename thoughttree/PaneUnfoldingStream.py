import io

from FoldablePane import FoldablePane


class PaneUnfoldingStream(io.TextIOBase):
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
