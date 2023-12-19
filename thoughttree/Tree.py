import difflib
import tkinter as tk
from tkinter import BOTH, DISABLED, END, INSERT, LEFT, NO, W, WORD, NORMAL
from tkinter import font as tkfont
from tkinter import ttk
import itertools
from os import listdir
from os.path import isdir, isfile, join, split
from tkinter.ttk import Style, Treeview

import TextDifference
from Config import conf
from Fonts import Fonts
from TextChange import TextChange
from TooltipableMenu import TooltipableMenu
from TreeTooltip import TreeTooltip

#NODE_OPEN = '\u25B6'
#NODE_CLOSED = '\u25BC'
NODE_OPEN = '*'
NODE_CLOSED = '|'


class Tree(tk.Frame):
    def __init__(self, parent, thoughttree, *args, **kw):
        from thoughttree import Thoughttree
        self.ui: Thoughttree = thoughttree

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

        style = "Treeview.Treeview"
        font = Fonts.FONT
        rowheight = tkfont.Font(font=font).metrics("linespace") + 1
        Style().configure(style, rowheight=rowheight, bd=2, highlightthickness=1, font=font)

        self.tree = ttk.Treeview(self, columns=("type"), displaycolumns=(), style=style, *args, **kw) # show="tree", # ("C1", "C2")

        y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=y_scroll.set)

        self.tree.column("#0", width=200, minwidth=10, anchor=W, stretch=NO)
        # self.tree.column("#1", width=50, minwidth=10, anchor=W, stretch=NO)
        # self.tree.heading("C1", text="")
        self.tree.bind('<Button-1>', on_tree_click)
        # self.tree.bind("<Double-Button-1>", self.edit_tree_entry)
        # self.tree.bind("<Return>", self.edit_tree_entry)
        def on_configure(event):
            self.tree.column("#0", width=event.width)
        self.tree.bind("<Configure>", on_configure)

        self.tree.insert("", END, text="Examples", iid="Examples", open=False)
        self.tree.insert("", END, text="Prompts", iid="Prompts", open=False)
        self.tree.insert("", END, text="Changes", iid="Changes", open=True)
        self.tree.insert("", END, text="Differences", iid="Differences", open=True)

        self.tree.focus("Examples")
        self.tree.selection_set(self.tree.focus())

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.load_dir(conf.examples_dir, "Examples")
        self.load_dir(conf.prompts_dir, "Prompts")

        TreeTooltip(self)
        context = TooltipableMenu(None, "(tree context menu)")
        context.add_item("Replace System", "<Shift-Alt-Return>", self.ui.replace_system_prompt, to_class="Treeview")
        context.add_item("Insert System", "<Shift-Return>", lambda e=None: self.ui.insert_system_prompt(), to_class="Treeview")
        context.add_item("Replace User", "<Control-Alt-Return>", lambda e=None: self.ui.replace_user_prompt(), to_class="Treeview")
        context.add_item("Insert User", "<Control-Return>", lambda e=None: self.ui.insert_user_prompt(), to_class="Treeview")
        self.bind_class("Treeview", "<Button-3>", context.show_context_menu)
        self.bind_class("Treeview", "<Menu>", context.show_context_menu)



    def focussed_file(self):
        leaf = self.tree.item(self.tree.focus())
        return leaf["values"][0] if leaf["values"] else None

    def show_details(self, event=None):
        file = self.focussed_file()
        self.ui.detail.configure(state=NORMAL)
        self.ui.detail.delete("1.0", "end")
        self.ui.detail.insert_file("1.0", file)
        self.ui.detail.configure(state=DISABLED)
        return "break"

    def load_dir(self, examples_dir, node):

        def populate_tree(tree, node):
            # if tree.set(node, "type") != 'directory':
            #     return

            path = examples_dir
            # tree.delete(*tree.get_children(node))

            # parent = tree.parent(node)
            # special_dirs = [] if parent else glob.glob('.') + glob.glob(examples_dir)

            for p in listdir(path):
                ptype = None
                p = join(path, p)
                if isdir(p):
                    ptype = "directory"
                elif isfile(p):
                    ptype = "file"
                name = split(p)[1]
                id = tree.insert(node, "end", text=name, values=[p])

                if ptype == 'directory':
                    if name not in ('.', '..'):
                        tree.insert(id, 0, text="dummy")
                        tree.item(id, text=name)

        # def update_tree(event):
        #     tree = event.widget
        #     populate_tree(tree, tree.focus())
        # self.tree.bind('<<TreeviewOpen>>', update_tree)


        self.tree.bind("<<TreeviewSelect>>", self.show_details)

        populate_tree(self.tree, node)


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
        def diff_summary(old, new):
            diff = [li for li in difflib.ndiff(old, new) if li[0]!='']
            result = ''
            for key, group in itertools.groupby(diff, lambda x: x[0]):
                result += f'{key} {"".join(item[2:] for item in group)}'
            return result

        iid = self.tree.insert("Differences", END, text=difference.title, open=True)
        for old, new in difference.replacements.items():
            self.tree.insert(iid, END, text=old)
            self.tree.insert(iid, END, text=new)
            self.tree.insert(iid, END, text=diff_summary(old, new))


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
