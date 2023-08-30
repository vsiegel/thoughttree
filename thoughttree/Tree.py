import tkinter as tk
from tkinter import BOTH, DISABLED, END, HORIZONTAL, INSERT, LEFT, NO, SUNKEN, TOP, VERTICAL, W, WORD, X, SEL_FIRST, \
    SEL_LAST
from tkinter import font as tkfont
from tkinter import ttk, simpledialog

from Fonts import Fonts
from Sheet import Sheet

#NODE_OPEN = '\u25B6'
#NODE_CLOSED = '\u25BC'
NODE_OPEN = '*'
NODE_CLOSED = '|'


class Tree(ttk.Treeview):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        def on_treeview_click(event):
            item = tree.identify('item', event.x, event.y)
            if item:
                if 'closed' in tree.item(item, 'tags'):
                    replaced = tree.item(item, 'text').replace(NODE_CLOSED, NODE_OPEN, 1)
                    tree.item(item, text=replaced)
                    tree.item(item, tags='opened')
                elif 'opened' in tree.item(item, 'tags'):
                    tree.item(item, text=tree.item(item, 'text').replace(NODE_OPEN, NODE_CLOSED, 1))
                    tree.item(item, tags='closed')

        tree = ttk.Treeview(parent, columns=("C1"), show="tree")
        self.tree = tree
        tree.column("#0", width=160, minwidth=60, anchor=W, stretch=NO)
        tree.column("#1", width=30, minwidth=60, anchor=W, stretch=NO)
        tree.heading("C1", text="")
        tree.bind('<Double-Button-1>', on_treeview_click)
        tree.bind("<Double-Button-1>", self.edit_tree_entry)
        tree.bind("<Return>", self.edit_tree_entry)

        from tools import create_mock_data
        create_mock_data(tree)


    def edit_tree_entry(self, event):
        row_id = self.focus()
        if not row_id:
            return
        column = self.identify_column(event.x)
        if column != "#1":  # Only allow editing the "Messages" column
            return
        x, y, width, height = self.bbox(row_id, column)
        char_width = tkfont.Font(font=Fonts.FONT).measure('0')
        line_height = tkfont.Font(font=Fonts.FONT).metrics("linespace")
        width = max(self.column(column)["width"], width)
        height = max(line_height, height)

        cur_text = self.item(row_id, "values")[0]
        w = width // char_width
        h = height // line_height
        cell_editor = tk.Text(self, wrap=WORD, width=w, height=h, font=Fonts.FONT,
                      highlightthickness=0, highlightbackground="black", padx=4, pady=0)
        cell_editor.insert(END, cur_text)
        cell_editor.place(x=x, y=y)
        cell_editor.focus_set()

        def save_text(event):
            print(event.type)
            if event.type == tk.EventType.FocusOut or int(event.state) & 0x4 == 0 :  # Check if Control key is not pressed
                text = cell_editor.get(1.0, END).strip()
                self.set(row_id, column, text)
                cell_editor.destroy()

        # cell_editor.bind("<FocusOut>", save_text)
        cell_editor.bind("<Return>", lambda e: e.state & 0x4 == 0 and save_text(e) or self.focus_set())
        cell_editor.bind("<Control-Return>", lambda e: cell_editor.insert(INSERT, "\n") or "break")
        # cell_editor.bind("<Control-Key>", lambda e : "break")
        # cell_editor.bind("<Control_L>", lambda e : "break")
