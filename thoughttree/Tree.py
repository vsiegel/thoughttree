import difflib
import tkinter as tk
from tkinter import BOTH, DISABLED, END, INSERT, LEFT, NO, W, WORD, NORMAL
from tkinter import font as tkfont
from tkinter import ttk
import itertools
from os import listdir
from os.path import isdir, isfile, join, split, exists
from tkinter.ttk import Style, Treeview
from startfile import startfile

import Colors
from Config import conf
from OutlineExploration import OutlineExploration
from Fonts import Fonts
from Improvement import Improvement
from TextChange import TextChange
from TooltipableMenu import TooltipableMenu
from TreeTooltip import TreeTooltip
from tools import diff_summary, code_file_relative
from tree_help_texts import tree_help

#NODE_OPEN = '\u25B6'
#NODE_CLOSED = '\u25BC'
NODE_OPEN = '*'
NODE_CLOSED = '|'


class Tree(ttk.Treeview):
    def __init__(self, parent, thoughttree, *args, **kw):

        style = "Treeview.Treeview"
        font = Fonts.FONT
        rowheight = tkfont.Font(font=font).metrics("linespace") + 1
        Style().configure(style, rowheight=rowheight, font=font)

        super().__init__(parent, columns=("path", "type"), displaycolumns=(), style=style, show="tree", *args, **kw)
        from thoughttree import Thoughttree
        self.ui: Thoughttree = thoughttree

        def on_tree_click(event):
            item = self.identify('item', event.x, event.y)
            if item:
                if 'closed' in self.item(item, 'tags'):
                    replaced = self.item(item, 'text').replace(NODE_CLOSED, NODE_OPEN, 1)
                    self.item(item, text=replaced)
                    self.item(item, tags='opened')
                elif 'opened' in self.item(item, 'tags'):
                    self.item(item, text=self.item(item, 'text').replace(NODE_OPEN, NODE_CLOSED, 1))
                    self.item(item, tags='closed')


        y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.yview)
        y_scroll.pack(side='right', fill='y')
        self.configure(yscrollcommand=y_scroll.set)

        self.column("#0", width=200, minwidth=100, anchor=W, stretch=NO)
        # self.column("#1", width=50, minwidth=10, anchor=W, stretch=NO)
        # self.heading("#0", text="Thoughttree")
        # self.bind('<Button-1>', on_tree_click)
        # self.bind("<Double-Button-1>", self.edit_tree_entry)
        # self.bind("<Return>", self.edit_tree_entry)

        self.tag_configure("old", foreground="#b34750")
        self.tag_configure("new", foreground="#47b359")

        def on_configure(event):
            self.column("#0", width=event.width)
        self.bind("<Configure>", on_configure)

        self.bind("<<TreeviewSelect>>", self.show_details)

        self.append_file("", conf.examples_dir, "Default.txt", iid="Default", typ="default")
        self.toplevel("Demos")
        self.toplevel("Examples")
        self.toplevel("Prompts")
        self.toplevel("Changes", open=True)
        self.toplevel("Differences", open=True)
        self.toplevel("Outlines", open=True)
        self.toplevel("Session", open=True)
        self.toplevel("Archive", open=True)
        self.toplevel("Tests")

        self.focus("Default")
        self.selection_set(self.focus())

        self.context_menus = {}


        def show_context_menu(event):
            if event.type == tk.EventType.ButtonPress and event.num == 3:
                widget = event.widget
                if isinstance(widget, ttk.Treeview):
                    widget.focus(widget.identify_row(event.y))
                    widget.selection_set(widget.identify_row(event.y))
                    self.show_details()
            iid = self.focus()
            type = self.set(iid, "type")
            if type in self.context_menus:
                menu = self.context_menus[type]
                if menu:
                    menu.show_context_menu(event)

        TreeTooltip(self)

        file_context = TooltipableMenu(None, "(File context menu)")
        file_context.item("Replace System", "<Shift-Alt-Return>", lambda e=None: self.to_sheet(self.ui.system, delete=True), to="Treeview")
        file_context.item("Insert System", "<Shift-Return>", lambda e=None: self.to_sheet(self.ui.system), to="Treeview")
        file_context.item("Replace User", "<Control-Alt-Return>", lambda e=None: self.to_sheet(self.ui.sheets.current, delete=True), to="Treeview")
        file_context.item("Insert User", "<Control-Return>", lambda e=None: self.to_sheet(self.ui.sheets.current), to="Treeview")
        file_context.item("Open", "<Control-Shift-O>", lambda e=None: self.open_file(), to="Treeview")

        self.context_menus["file"] = file_context

        self.bind_class("Treeview", "<Double-Button-1>", self.use_node)
        self.bind_class("Treeview", "<Return>", self.use_node)
        self.bind_class("Treeview", "<Button-3>", show_context_menu)
        self.bind_class("Treeview", "<Menu>", show_context_menu)

    def to_sheet(self, sheet, delete=False):
        if delete:
            sheet.delete(1.0, END)
        file = self.focussed_file()
        sheet.insert_file(INSERT, file)


    def open_file(self):
        path = self.focussed_file()
        if path:
            startfile(path)

    def append(self, parent, index=END, text="-", iid=None, open=False, value="", type="toplevel", tags=()):
        # print(f"Parent: {parent}, Index: {index}, Text: {text}, Iid: {iid}, Open: {open}, Value: {value}, Type: {type}, Tags: {tags}")
        return self.insert(parent=parent, index=index, text=text, iid=iid, open=open, values=[value, type], tags=tags)


    def toplevel(self, name, **kv):
        self.append("", text=name, iid=name, type="toplevel", **kv)
        directory = code_file_relative(name.lower())
        if exists(directory):
            self.load_dir(directory, name)


    def focussed(self):
        return self.item(self.focus())

    def focussed_file(self):
        values = self.set(self.focus())
        return values.get("path", None)

    def use_node(self, event):
        iid = self.focus()
        type = self.set(iid, "type")

        if type.startswith("improvement"):
            self.use_improvement(iid, type)
        elif type.startswith("outline_exploration"):
            self.use_outline_exploration(iid, type)
        elif type == "default":
            self.to_sheet(self.ui.sheets.current)
        elif type in ["directory", "toplevel"]:
            self.item(iid, open=not self.item(iid, 'open'))
        else:
            self.print(iid)

    def use_improvement(self, iid, type):
        if type == "improvement":
            old_id, new_id, diff_id = self.get_children(iid)
            old = self.item(old_id, "text")
            new = self.item(new_id, "text")
            self.ui.it.insert_diff(old, new)
        elif type == "improvement.old":
            old_id, new_id, diff_id = self.get_children(iid)
            pass
        elif type == "improvement.new":
            pass
        elif type == "improvement.diff_summary":
            pass


    def outline_id(self, iid):
        while self.set(iid, "type") == "outline_exploration.item":
            iid = self.parent(iid)
        return iid

    def use_outline_exploration(self, iid, type):
        if type == "outline_exploration.root":
            pass
        elif type == "outline_exploration.item":
            text = self.item(iid, "text")
            item, title = text.split(" ", maxsplit=1)
            outline_id = self.outline_id(iid)
            print(f"{iid=} {outline_id} {item=} {title=}")
            self.ui.explore_outline(hidden_command=item, outline_id=outline_id, parent_id=iid)
            # self.ui.chat(1, "\n\n", "\n\n", hidden_command=item)

    def add_outline_exploration(self, outline_exploration: OutlineExploration):
        if not outline_exploration:
            return
        iid = outline_exploration.parent_id
        if self.exists(iid):
            parent = iid
        else:
            print(f"{outline_exploration=} outline_id: {outline_exploration.outline_id} parent_id: {outline_exploration.parent_id} {outline_exploration.title=}")
            parent = self.append("Outlines", text=outline_exploration.title, iid=iid, type="outline_exploration.root", open=True)
        for outline_id, outline_title in outline_exploration.outline_level_items:
            self.append(parent, text=outline_id + " " + outline_title, type="outline_exploration.item", open=True)


    def add_change(self, change: TextChange):
        title = self.insert("Changes", END, text=change.title, open=True)
        iid = self.insert(title, END, text=change.description, open=True)
        for attribute, value in change.attributes.items():
            self.insert(title, END, text=attribute, values=[value])
        for old, new in change.replacements.items():
            self.insert(title, END, text=old)
            self.insert(title, END, text=new)


    def add_improvement(self, improvement: Improvement):
        if not improvement:
            return
        iid = self.append("Differences", text=improvement.title, type="improvement", open=True)
        for old, new in improvement.replacements.items():
            self.append(iid, text=old, type="improvement.old", tags=("old",))
            self.append(iid, text=new, type="improvement.new", tags=("new",))
            self.append(iid, text=diff_summary(old, new), type="improvement.diff_summary")



    def show_details(self, event=None):
        item = self.focussed_file()
        self.ui.detail.configure(state=NORMAL)
        try:
            if self.ui.detail.get(1.0, "end").strip():
                self.ui.detail.delete("1.0", "end")

            if item and isfile(item):
                self.ui.detail.insert_file("1.0", item)
            else:
                iid = self.focus()
                text = ""
                toplevel_node = "Tree." + iid
                if toplevel_node in tree_help:
                    text = tree_help[toplevel_node].strip()
                # self.ui.detail.insert("1.0", f"{iid=}\n{self.item(iid)=}\n{self.set(iid)=}")
                if text:
                    self.ui.detail.insert("1.0", text)
        finally:
            self.ui.detail.configure(state=DISABLED)
        self.ui.detail.edit_modified(False)
        return "break"

    def print(self, iid):
        print(f"{iid=}\n{self.item(iid)=}\n{self.set(iid)=}\n")

    def load_dir(self, directory, node):

        # if tree.set(node, "type") != 'directory':
        #     return

        # tree.delete(*tree.get_children(node))

        # parent = tree.parent(node)
        # special_dirs = [] if parent else glob.glob('.') + glob.glob(examples_dir)

        for file in sorted(listdir(directory)):
            iid, typ = self.append_file(node, directory, file)

            if typ == 'directory':
                if file not in ('.', '..'):
                    path = join(directory, file)
                    self.load_dir(path, iid)

        # def update_tree(event):
        #     tree = event.widget
        #     populate_tree(tree, tree.focus())
        # self.bind('<<TreeviewOpen>>', update_tree)


    def append_file(self, node, directory, file, iid=None, typ=None):
        path = join(directory, file)
        if typ:
            typ = typ
        elif isdir(path):
            typ = "directory"
        elif isfile(path):
            typ = "file"
        iid = iid or path
        iid = self.insert(node, "end", text=file, values=[path, typ], iid=iid)
        return iid, typ


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
