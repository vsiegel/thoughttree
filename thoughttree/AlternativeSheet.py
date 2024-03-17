import tkinter as tk
from tkinter import LEFT, SUNKEN, X, TOP, W

from Fonts import Fonts
from ResizingSheet import ResizingSheet


class AlternativeSheet(ResizingSheet):
    def __init__(self, parent=None, **kw):
        super().__init__(parent, borderwidth=0, relief=SUNKEN, name="as", **kw)

    def insert(self, index, chars, *args):
        super().insert("end-2c", chars, *args)
        self.see(index)
