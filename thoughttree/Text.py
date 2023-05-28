import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import scrolledtext


class Notebook(ttk.Notebook):
    def __init__(self, master=None, **kw):
        ttk.Notebook.__init__(self, master, padding=(0, 4, 0, 0), **kw)

    def find_parent_tab_label(self, txt):
        parent = txt
        while parent and type(parent) not in [Notebook]:
            parent = parent.master
        if parent:
            parent: Notebook = parent
            tab_id = parent.select()
            old_tab_label = parent.tab(tab_id, "text")
        else:
            old_tab_label = ""
        return old_tab_label

    def add_textbox_to_notebook(self, old_tab_label, i, text=""):
        if old_tab_label:
            tab_label = f"{old_tab_label}.{i}"
        else:
            tab_label = f"{i}"
        frame = tk.Frame(self)
        txt = Text(frame, text)
        self.add(frame, text=f"{tab_label}")
        txt.pack(fill=tk.BOTH, expand=True)


class Text(tk.scrolledtext.ScrolledText):
    FONT = ("monospace", 10)
    # FONT = ("sans-serif", 11)

    def __init__(self, master=None, text="", **kw):
        lines = len(text.splitlines())
        tk.scrolledtext.ScrolledText.__init__(
            self, master, undo=True, wrap=tk.WORD, padx=1, pady=1,
            width=80, height=lines, insertwidth=3, font=Text.FONT,
            border=0, borderwidth=1, highlightthickness=1,
            selectbackground="#66a2d4", selectforeground="white", **kw)

        self.line_height = tkfont.Font(font=Text.FONT).metrics("linespace")
        self.vbar.config(width=18, takefocus=False, borderwidth=2)

        self.master.unbind_class("Text", "<Control-Shift-T>")
        self.bind("<Control-Shift-T>", lambda e: self.insert_nested_text())
        self.bind("<Control-Alt-plus>", lambda e: self.change_notebook_height(1))
        self.bind("<Control-Alt-minus>", lambda e: self.change_notebook_height(-1))
        self.bind("<Control-Shift-asterisk>", lambda e: self.change_notebook_height(10))
        self.bind("<Control-Shift-underscore>", lambda e: self.change_notebook_height(-10))
        self.pack(pady=0, fill=tk.X, expand=True)
        self.tag_configure("assistant", background="#F0F0F0", selectbackground="#4682b4", selectforeground="white")
        self.insert(tk.END, text)


    def change_notebook_height(self, delta):
        parent = self.master.focus_get()
        while parent and type(parent) not in [Notebook]:
            parent = parent.master
        if not parent:
            return
        old_height = parent.cget("height")
        height = max(old_height + delta * self.line_height, self.line_height)
        parent.configure(height=height)

    def insert_nested_text(self):
        height, width = self.calc_notebook_size()
        notebook = Notebook(self, height=height, width=width)
        old_tab_label = Notebook.find_parent_tab_label(notebook, self)
        notebook.add_textbox_to_notebook(old_tab_label, 1, "Text that was replaced by this widget")
        notebook.add_textbox_to_notebook(old_tab_label, 2, "")
        self.add_notebook_to_textbox(notebook)

    def add_notebook_to_textbox(self, widget, pos="insert"):
        self.insert(pos, '\n')
        self.window_create(pos, window=widget)
        self.see(pos)

    def calc_notebook_size(self):
        twidth = self.winfo_width()
        width = (twidth - 0)
        char_width = tkfont.Font(font=self.cget("font")).measure('0')
        width -= width % char_width
        height = int(self.winfo_height() * 2 / 3)
        return height, width
