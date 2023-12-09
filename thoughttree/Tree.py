import tkinter as tk
from tkinter import BOTH, DISABLED, END, HORIZONTAL, INSERT, LEFT, NO, SUNKEN, TOP, VERTICAL, W, WORD, X, SEL_FIRST, \
    SEL_LAST, RIGHT
from tkinter import font as tkfont
from tkinter import ttk, simpledialog

import TextDifference
from Fonts import Fonts
from Sheet import Sheet
from TextChange import TextChange

#NODE_OPEN = '\u25B6'
#NODE_CLOSED = '\u25BC'
NODE_OPEN = '*'
NODE_CLOSED = '|'


class Tree(tk.Frame):
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.parent = parent

        def on_tree_click(event):
            item = self.tree.identify('item', event.x, event.y)
            if item:
                if 'closed' in self.tree.item(item, 'tags'):
                    replaced = self.tree.item(item, 'text').replace(NODE_CLOSED, NODE_OPEN, 1)
                    self.tree.item(item, text=replaced)
                    self.tree.item(item, tags='opened')
                elif 'opened' in self.tree.item(item, 'tags'):
                    self.tree.item(item, text=self.tree.item(item, 'text').replace(NODE_OPEN, NODE_CLOSED, 1))
                    self.tree.item(item, tags='closed')

        self.tree = ttk.Treeview(self, columns=("C1", "C2"), *args, **kw) # show="tree",
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.tree.column("#0", width=150, minwidth=10, anchor=W, stretch=NO)
        self.tree.column("#1", width=50, minwidth=10, anchor=W, stretch=NO)
        self.tree.heading("C1", text="")
        self.tree.bind('<Button-1>', on_tree_click)
        # self.tree.bind("<Double-Button-1>", self.edit_tree_entry)
        # self.tree.bind("<Return>", self.edit_tree_entry)
        def on_configure(event):
            self.tree.column("#0", width=event.width)
        self.tree.bind("<Configure>", on_configure)
        self.tree.bind("<FocusOut>", lambda event: self.tree.selection_set([]))
        self.tree.bind("<FocusIn>", lambda event: self.tree.selection_set(self.tree.focus()))

        self.tree.insert("", END, text="Examples", iid="Examples", open=False)
        self.tree.insert("", END, text="Prompts", iid="Prompts", open=False)
        self.tree.insert("", END, text="Changes", iid="Changes", open=True)
        self.tree.insert("", END, text="Differences", iid="Differences", open=True)
        self.sheet = Sheet(self)
        self.sheet.pack(side=RIGHT, fill=BOTH, expand=True)


    def edit_tree_entry(self, event):
        row_id = self.tree.focus()
        if not row_id:
            return
        column = self.tree.identify_column(event.x)
        if column != "#1":  # Only allow editing the "Messages" column
            return
        x, y, width, height = self.tree.bbox(row_id, column)
        char_width = tkfont.Font(font=Fonts.FONT).measure('0')
        line_height = tkfont.Font(font=Fonts.FONT).metrics("linespace")
        width = max(self.tree.column(column)["width"], width)
        height = max(line_height, height)

        cur_text = self.tree.item(row_id, "values")[0]
        w = width // char_width
        h = height // line_height
        cell_editor = tk.Text(self.tree, wrap=WORD, width=w, height=h, font=Fonts.FONT,
                      highlightthickness=0, highlightbackground="black", padx=4, pady=0)
        cell_editor.insert(END, cur_text)
        cell_editor.place(x=x, y=y)
        cell_editor.focus_set()

        def save_text(event):
            print(event.type)
            if event.type == tk.EventType.FocusOut or int(event.state) & 0x4 == 0 :  # Check if Control key is not pressed
                text = cell_editor.get(1.0, END).strip()
                self.tree.set(row_id, column, text)
                cell_editor.destroy()

        # cell_editor.bind("<FocusOut>", save_text)
        cell_editor.bind("<Return>", lambda e: e.state & 0x4 == 0 and save_text(e) or self.focus_set())
        cell_editor.bind("<Control-Return>", lambda e: cell_editor.insert(INSERT, "\n") or "break")
        # cell_editor.bind("<Control-Key>", lambda e : "break")
        # cell_editor.bind("<Control_L>", lambda e : "break")

    def add_change(self, change: TextChange):
        title = self.tree.insert("Changes", END, text=change.title, open=True)
        iid = self.tree.insert(title, END, text=change.description, open=True)
        for attribute, value in change.attributes.items():
            self.tree.insert(title, END, text=attribute, values=[value])
        for old, new in change.replacements.items():
            self.tree.insert(title, END, text=old)
            self.tree.insert(title, END, text=new)


    def add_difference(self, difference: TextDifference):
        title = self.tree.insert("Differences", END, text="difference.title", open=True)
        # iid = self.tree.insert(title, END, text=difference.description)
        # for attribute, value in difference.attributes.items():
        #     self.tree.insert(title, END, text=attribute, values=[value])
        for old, new in difference.replacements.items():
            self.tree.insert(title, END, text=old)
            self.tree.insert(title, END, text=new)



if __name__ == '__main__':
    def file(name):
        with open(name) as f:
            return f.read()

    root = tk.Tk()
    tree = Tree(root)
    tree.pack(fill=BOTH, expand=1)
    text_change = TextChange(file("/home/siegel/manuscript/99_thoughttree.tex-make_it_better25.txt"))
    tree.add_change(text_change)
    root.mainloop()
