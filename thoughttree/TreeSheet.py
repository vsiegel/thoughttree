import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END, CURRENT, SEL, LEFT, TOP, RIGHT, VERTICAL, NW, ttk, NSEW

import Colors
import tools
from History import History
from Notebook import Notebook
from ResizingSheet import ResizingSheet
from Sheet import Sheet
from Title import new_child_title, new_sibling_title, Title

class TreeSheet(ResizingSheet, tk.Frame):
    # def __init__(self, parent, name="ts", **kw):
    def __init__(self, parent, parent_sheet=None,  height=1, width=250, parent_notebook=None, parent_sheet_tree=None, name="ts", *args, **kw):
        self.tree_frame = tk.Frame(parent, background="#e8eaff", name=name + "f")
        ResizingSheet.__init__(self, self.tree_frame, scrollbar=False, name=name, **kw)
        self.pack(side=tk.TOP, fill=X, expand=False, anchor=tk.N)

        self.initially_modified = False
        self.parent_sheet = parent_sheet
        self.parent_notebook = parent_notebook
        self.notebook = None

        self.tree_frame.bind("<Button-1>", self.on_empty_background, add=True)

        self.copy_packing(self.tree_frame, ResizingSheet)

    def get_notebook(self) -> Notebook:
        if not self.notebook:
            self.notebook = Notebook(self.tree_frame, self, self.parent_notebook)
            self.notebook.pack(side=tk.TOP, fill=Y, expand=False, anchor=tk.N)
        return self.notebook

    def create_child_notebook(self): # make sure we have a notebook
        from Notebook import Notebook
        if not self.notebook:
            self.notebook = self.get_notebook()
            self.pack_configure(expand=False) #fixme
            first_child = new_child_title(self.parent_notebook)
            # self.child_notebook.bind("<<NotebookTabChanged>>", self.grow_to_displaylines)
            return self.notebook.add_sheet(first_child, parent_sheet=self)

    def add(self, text=""):
        notebook = self.get_notebook()
        frame = tk.Frame(notebook, background="#a5d6ba", borderwidth=1)
        sheet = TreeSheet(frame, parent_sheet=self, parent_notebook=notebook, name="title")
        sheet.pack(side=tk.TOP, fill=BOTH, expand=True)
        frame.pack(side=tk.TOP, fill=BOTH, expand=True)
        notebook.add(frame, text=text, sticky=NSEW)

        # self.fork_frame.pack_propagate(False)
        # self.pack(side=tk.TOP, fill=BOTH, expand=True)
        #
        # self.parent_sheet = parent_sheet
        # self.parent_notebook = parent_notebook
        # self.parent_sheet_tree = parent_sheet_tree
        # self.child_notebook = None
        #
        # self.previous_sheet_height = None #todo
        # self.unbind("<BackSpace>")
        # self.bind_class("Text", "<BackSpace>", self.backspace)

    def branch(self):
        # frame = tk.Frame(self.notebook, background="#a5d6ba", borderwidth=3)
        sheet = TreeSheet(self.notebook)
        # sheet.pack(side=tk.TOP, fill=BOTH, expand=True)
        # sheet.pack(fill=BOTH, expand=True)
        self.notebook.add(sheet)

    def sheet_configure(self, event):
        print(f"sheet_configure: {event=} on {event.widget=} rh: {event.widget.winfo_reqheight()}")

    def notebook_configure(self, event):
        print(f"notebook_configure: {event=} on {event.widget=} rh: {event.widget.winfo_reqheight()}")

    def update_tab_title(self, event=None):
        def get():
            return self.parent_notebook.tab(CURRENT, option="text")
        def set(title):
            self.parent_notebook.tab(CURRENT, text=title)
        progress_title = get().split(" ")[0] + " ..."
        print(f"{progress_title=}")

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

    def fork(self, index=INSERT, duplicate=False):
        index = self.index(index)
        self.initially_modified = True

        leading_text = bool(self.get("1.0", index).strip())


        def copy_trailing_text(from_sheet, to_sheet, starting):
            trailing_text = from_sheet.get(starting, END).rstrip()
            to_sheet.insert("1.0", trailing_text)


        if self.notebook:
            notebook = self.notebook
        elif not leading_text and self.parent_notebook:
            notebook = self.parent_notebook
        else:
            sheet = self.create_child_notebook()
            copy_trailing_text(self, sheet, index)
            notebook = self.notebook

        sibling = new_sibling_title(notebook)
        if notebook == self.parent_notebook:
            parent = self.parent_sheet
        else:
            parent = self
        sheet = notebook.add_sheet(sibling, parent)
        # self.split_sheet(sheet, index)
        self.delete(index, END)
        return "break"


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
        notebook: Notebook = self.parent_notebook
        if notebook and notebook.tabs():
            print(f"{self.focus_get()    =}")
            selected = notebook.index(CURRENT)
            # sheet = selected_sheet(notebook)
            sheet = notebook.selected_sheet()
            notebook.forget(selected)

            if notebook.tabs():
                notebook.select(max(selected - 1, 0))
                print(f"{sheet           =}")
                notebook.selected_sheet().focus_set()
                print(f"{self.focus_get()=}")
                sheet.insert(END, "c")
            else:
                tab_text = sheet.get('1.0', 'end-1c')
                self.parent_sheet.insert(END, tab_text)
                self.parent_sheet.mark_set(INSERT, 'end-1c')
                self.parent_sheet.focus_set()
                self.parent_notebook.pack_forget()
                self.parent_notebook = None
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


if __name__ == "__main__":
    root = tk.Tk()
    tools.escapable(root)
    # widget = TreeSheet(root)
    widget = TreeSheet(root)
    widget.pack(side=LEFT, fill=BOTH, expand=True)
    # widget.branch()
    # widget.notebook.add(TreeSheet(widget.notebook))
    # widget.pack_propagate(False)
    widget.focus_set()
    root.mainloop()
