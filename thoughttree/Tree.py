import difflib
import tkinter as tk
from tkinter import BOTH, DISABLED, END, INSERT, LEFT, NO, W, WORD, NORMAL
from tkinter import font as tkfont
from tkinter import ttk
import itertools
from os import listdir
from os.path import isdir, isfile, join, split
from tkinter.ttk import Style, Treeview

import Colors
import TextDifference
from Config import conf
from Fonts import Fonts
from TextChange import TextChange
from TooltipableMenu import TooltipableMenu
from TreeTooltip import TreeTooltip
from tools import diff_summary
from tree_help_texts import tree_help

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

        self.tree = ttk.Treeview(self, columns=("path", "type"), displaycolumns=(), style=style, *args, **kw) # show="tree", # ("C1", "C2")

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

        selectionbackground_focussed = lambda e=None: Style().map(style, background=[("selected", Colors.highlight)])
        selectionbackground_unfocussed = lambda e=None: Style().map(style, background=[("selected", "lightgray")])
        self.tree.bind("<FocusIn>", lambda e=None: self.tree.selection_set(self.tree.focus()), add=True)
        self.tree.bind("<FocusIn>", selectionbackground_focussed, add=True)
        self.tree.bind("<FocusOut>", selectionbackground_unfocussed)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)
        selectionbackground_unfocussed()


        self.append("", text="Examples", iid="Examples", type="toplevel")
        self.append("", text="Prompts", iid="Prompts", type="toplevel")
        self.append("", text="Changes", iid="Changes", open=True, type="toplevel")
        self.append("", text="Differences", iid="Differences", open=True, type="toplevel")

        self.tree.focus("Examples")

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.load_dir(conf.examples_dir, "Examples")
        self.load_dir(conf.prompts_dir, "Prompts")

        self.context_menus = {}


        def show_context_menu(event):
            if event.type == tk.EventType.ButtonPress and event.num == 3:
                widget = event.widget
                if isinstance(widget, ttk.Treeview):
                    print(f"{widget.identify_row(event.y)=}")
                    widget.focus(widget.identify_row(event.y))
                    widget.selection_set(widget.identify_row(event.y))
                    self.show_details()
            iid = self.tree.focus()
            type = self.tree.set(iid, "type")
            if type:
                menu = self.context_menus[type]
                if menu:
                    menu.show_context_menu(event)

        def use_node(event):
            iid = self.tree.focus()
            type = self.tree.set(iid, "type")
            print(f"use_node {iid=} {type=}")
            if type == "difference":
                old_id, new_id, diff_id = self.tree.get_children(iid)
                old = self.tree.item(old_id, "text")
                new = self.tree.item(new_id, "text")
                self.ui.it.insert_diff(old, new)

        TreeTooltip(self)

        file_context = TooltipableMenu(None, "(File context menu)")
        file_context.add_item("Replace System", "<Shift-Alt-Return>", self.ui.replace_system_prompt, to_class="Treeview")
        file_context.add_item("Insert System", "<Shift-Return>", lambda e=None: self.ui.insert_system_prompt(), to_class="Treeview")
        file_context.add_item("Replace User", "<Control-Alt-Return>", lambda e=None: self.ui.replace_user_prompt(), to_class="Treeview")
        file_context.add_item("Insert User", "<Control-Return>", lambda e=None: self.ui.insert_user_prompt(), to_class="Treeview")

        self.context_menus["file"] = file_context

        self.bind_class("Treeview", "<Double-Button-1>", use_node)
        self.bind_class("Treeview", "<Button-3>", show_context_menu)
        self.bind_class("Treeview", "<Menu>", show_context_menu)


    def append(self, parent, index=END, text="-", iid=None, open=False, value="", type="toplevel"):
        return self.tree.insert(parent=parent, index=index, text=text, iid=iid, open=open, values=[value, type])


    def focussed(self):
        return self.tree.item(self.tree.focus())

    def focussed_file(self):
        item = self.focussed()
        return item["values"][0] if item["values"] else None

    def show_details(self, event=None):
        item = self.focussed_file()
        self.ui.detail.configure(state=NORMAL)
        try:
            if self.ui.detail.get(1.0, "end").strip():
                self.ui.detail.delete("1.0", "end")

            if item and isfile(item):
                self.ui.detail.insert_file("1.0", item)
            else:
                iid = self.tree.focus()
                text = ""
                toplevel_node = "Tree." + iid
                if toplevel_node in tree_help:
                    text = tree_help[toplevel_node].strip()
                # self.ui.detail.insert("1.0", f"{iid=}\n{self.tree.item(iid)=}\n{self.tree.set(iid)=}")
                if text:
                    self.ui.detail.insert("1.0", text)
        finally:
            self.ui.detail.configure(state=DISABLED)
        return "break"

    def load_dir(self, examples_dir, node):

        def populate_tree(tree: Treeview, node):
            # if tree.set(node, "type") != 'directory':
            #     return

            directory = examples_dir
            # tree.delete(*tree.get_children(node))

            # parent = tree.parent(node)
            # special_dirs = [] if parent else glob.glob('.') + glob.glob(examples_dir)

            for file in listdir(directory):
                ptype = None
                path = join(directory, file)
                if isdir(path):
                    ptype = "directory"
                elif isfile(path):
                    ptype = "file"
                iid = tree.insert(node, "end", text=file, values=[path, ptype])

                if ptype == 'directory':
                    if file not in ('.', '..'):
                        tree.insert(iid, 0, text="dummy")
                        tree.item(iid, text=file)

        # def update_tree(event):
        #     tree = event.widget
        #     populate_tree(tree, tree.focus())
        # self.tree.bind('<<TreeviewOpen>>', update_tree)


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
        iid = self.append("Differences", text=difference.title, type="difference", open=True)
        for old, new in difference.replacements.items():
            self.tree.insert(iid, END, text=old)
            self.tree.insert(iid, END, text=new)
            self.tree.insert(iid, END, text=diff_summary(old, new))
