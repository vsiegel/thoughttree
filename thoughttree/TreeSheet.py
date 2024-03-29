import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END, CURRENT, SEL, LEFT, TOP, RIGHT, VERTICAL, NW, ttk, NSEW

import Colors
import tools
from History import History
from Notebook import Notebook
from ResizingSheet import ResizingSheet
from Sheet import Sheet
from Title import new_child_title, new_sibling_title, Title
from Ui import Ui


class NF(tk.Frame):  # NF short for NotebookFrame - the name appears in widget names, making them longer.
    def __init__(self, parent, name=None, sheet=None, **kw):
        tk.Frame.__init__(self, parent, name=name, **kw)
        self.sheet = sheet


class TreeSheet(ResizingSheet, tk.Frame):
    # def __init__(self, parent, name="ts", **kw):
    def __init__(self, parent, parent_sheet=None, height=1, width=250, parent_notebook=None, sheet_tree=None, name="ts", **kw):
        self.tree_frame = NF(parent, name=name + "f", borderwidth=0, highlightthickness=0, background="#ffffff", sheet=self)
        ResizingSheet.__init__(self, self.tree_frame, scrollbar=False, name=name, highlightthickness=0, **kw)
        self.pack(side=tk.TOP, fill=X, expand=False, anchor=tk.N)

        self.initially_modified = False
        self.parent_sheet = parent_sheet
        self.parent_notebook = parent_notebook
        self.notebook = None
        self.explore_outline = None
        self.sheets = sheet_tree or parent_sheet.sheets

        self.copy_packing(self.tree_frame, ResizingSheet)

        bindtags = list(self.bindtags())
        bindtags.insert(1, "TreeSheet")
        self.bindtags(bindtags)

        self.tree_frame.bind("<Button>", self.on_empty_background, add=True)

        def on_up(event):
            if self.at_first_line() and self.parent_sheet:
                self.parent_sheet.focus_bottom()
        self.bind("<Up>", on_up, add=True)

        def on_down(event):
            if self.at_last_line() and self.notebook:
                self.notebook.selected_sheet().focus_top()
        self.bind("<Down>", on_down, add=True)

        tag = "TreeSheet-last"
        self.bindtags(self.bindtags() + (tag,))
        if not self.bind_class(tag):
            self.bind_class(tag, '<KeyRelease>', self.see_in_tree, add=True)

        def on_focus_in(event):
            sheet = event.widget
            if sheet.sheets:
                sheet.sheets.current = sheet
        self.bind("<FocusIn>", on_focus_in, add=True)

        def on_motion(event):
            if self.sheets:
                self.sheets.on_motion_in_sheet(event)

        self.bind('<B1-Motion>', on_motion)


    def at_first_line(self):
        return self.index(INSERT).split('.')[0] == '1'

    def at_last_line(self):
        return self.compare("insert lineend", '==', "end-1c")

    def focus_top(self):
        self.focus_set()
        self.mark_set(INSERT, "1.0")

    def focus_bottom(self):
        self.focus_set()
        self.mark_set(INSERT, END)

    def see_in_tree(self, event=None, to=INSERT):
        if event:
            sheet = event.widget
        else:
            sheet = self
        if sheet.sheets:
            sheet.sheets.see_in_tree(sheet, to=to)

    @staticmethod
    def on_empty_background(event):
        frame = event.widget
        sheet = frame.sheet
        while sheet.notebook and sheet.notebook.selected_sheet():
            sheet = sheet.notebook.selected_sheet()
        sheet.focus_set()

    def tk_focusNext(self):
        if self.sheets:
            # print(f"{self.sheet_tree.tk_focusNext()=}")
            widget = self.sheets.tk_focusNext()
        else:
            widget = super().tk_focusNext()
        return widget

    def tk_focusPrev(self):
        if self.sheets:
            # print(f"{self.sheet_tree.tk_focusPrev()=}")
            # print(f"{self.sheet_tree.tk_focusPrev().tk_focusPrev()=}")
            widget = self.sheets.tk_focusPrev()
        else:
            widget = super().tk_focusPrev()
        return widget

    def get_notebook(self) -> Notebook:
        if not self.notebook:
            self.notebook = Notebook(self.tree_frame, self, self.parent_notebook)
            self.notebook.pack(side=tk.TOP, fill=Y, expand=False, anchor=tk.N)
        return self.notebook

    def create_child_notebook(self): # make sure we have a notebook
        if not self.notebook:
            self.notebook = self.get_notebook()
            first_child_title = new_child_title(self.parent_notebook)
            # self0.child_notebook.bind("<<NotebookTabChanged>>", self.grow_to_displaylines)
            return self.notebook.add_sheet(first_child_title, parent_sheet=self)

    def fork(self, index=INSERT, duplicate=False):
        index = self.index(index)
        self.initially_modified = True

        has_leading_text = bool(self.get("1.0", index).strip())

        if self.notebook:
            notebook = self.notebook
        elif not has_leading_text and self.parent_notebook:
            notebook = self.parent_notebook
        else:
            sheet = self.create_child_notebook()
            self.split_sheet(to_sheet=sheet, starting=index)
            notebook = self.notebook

        sibling_title = new_sibling_title(notebook)
        if notebook == self.parent_notebook:
            parent = self.parent_sheet
        else:
            parent = self
        sheet = notebook.add_sheet(title=sibling_title, parent_sheet=parent)
        # sheet = self.add()
        # self.split_sheet(sheet, index)
        # self.delete(index, END)
        return "break"

    def add(self, text=""):
        notebook = self.get_notebook()
        frame = NF(notebook)
        sheet = TreeSheet(frame, parent_sheet=self, parent_notebook=notebook, sheet_tree=self.sheets, name="title")
        frame.sheet = sheet
        sheet.pack(side=tk.TOP, fill=BOTH, expand=True)
        notebook.add(frame, text=text, sticky=NSEW)
        # list(frame.children.values())[0].focus_set()
        print(f"add: {list(frame.children.values())[0]=}")


    def __str__(self):
        return str(self.tree_frame)

    def update_tab_title(self, event=None):
        if not self.parent_notebook:
            return
        def get():
            return self.parent_notebook.tab(CURRENT, option="text")
        def set(title):
            title = title.split("\n")[0][:100]
            self.parent_notebook.tab(CURRENT, text=title)
        progress_title = get().split(" ")[0] + " ..."
        # print(f"{progress_title=}")

        def write_title(delta):
            # if self.is_root_destroyed or self.model.is_canceled:
            #     return
            current_title = get()
            if current_title == progress_title:
                current_title = progress_title.split(" ")[0] + " "
            set(current_title + delta)
            self.update()

        set(progress_title)
        self.update()

        # history = self.history_from_system_and_chat(Title.PROMPT, max_messages=5, max_size=1000)
        prompt_history = [{'role' : "system", 'content' : Title.PROMPT}]
        history = self.history_from_path(prompt_history)

        Title.model.complete(history, write_title, max_tokens=30, temperature=0.3)
        Title.model.counter.summarize("Title cost:")
        Ui.log.cost("Title cost:\n" + Title.model.counter.summary())


    def selected_sheet(self):
        if not self.notebook:
            return None
        return self.notebook.selected_sheet()


    def child_sheets(self)->['TreeSheet']:
        if not self.notebook:
            return []
        return self.notebook.child_sheets()


    def history_from_path(self, history=None) :
        if self.parent_sheet:
            history = self.parent_sheet.history_from_path(history)
        else:
            history = history or History()

        return history + History(self)


    def close_tab(self):
        parent: Notebook = self.parent_notebook
        if parent and parent.tabs():
            selected = parent.index(CURRENT)
            sheet = parent.selected_sheet()
            parent.forget(selected)

            if parent.tabs():
                parent.select(max(selected - 1, 0))
                parent.selected_sheet().focus_set()
            else:
                tab_text = sheet.get('1.0', 'end-1c')
                self.parent_sheet.insert(END, tab_text)
                self.parent_sheet.mark_set(INSERT, 'end-1c')
                self.parent_sheet.focus_set()
                self.pack_configure(expand=True)
            return "break"


    def backspace(self, event=None): # close_empty_tab_or_backspace
        sheet = event and event.widget or self
        if sheet.index(INSERT) == "1.0" and not sheet.tag_ranges(SEL):
            notebook: Notebook = sheet.parent_notebook
            if notebook:
                string_in_tab = sheet.get('1.0', END).strip()
                if not string_in_tab:
                    sheet.close_tab()
        else:
            sheet.delete(INSERT + "-1c")
        return "break"


    def focusChangeTab(self, offset):
        if self.parent_notebook:
            self.parent_notebook.change(offset)

    focusNextTab = lambda self: self.focusChangeTab(1)
    focusPrevTab = lambda self: self.focusChangeTab(-1)


    def depth_first(self, title="", indent=""):
        title = title and f"# {title}\n" or ""
        lines = self.get(1.0, "end-1c").splitlines(True)
        indented = [indent + line for line in lines]
        seperator = indent and "\n"
        depth_fist_parts = [seperator + indent + title + '' + "".join(indented) + '\n']

        for tab, child in enumerate(self.child_sheets()):
            title = self.notebook.tab(tab, "text")
            lines = child.depth_first(title=title, indent=">" + indent)
            depth_fist_parts.extend("".join(lines))
        return depth_fist_parts


if __name__ == "__main__":
    root = tk.Tk()
    tools.escapable(root)
    widget = TreeSheet(root)
    widget.pack(side=LEFT, fill=BOTH, expand=True)
    # widget.branch()
    # widget.notebook.add(TreeSheet(widget.notebook))
    # widget.pack_propagate(False)
    widget.focus_set()
    root.mainloop()
