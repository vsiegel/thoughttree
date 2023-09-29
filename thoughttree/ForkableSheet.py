import sys
import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END, CURRENT, SEL

from IterateRangeForm import IterateRangeForm
from Notebook import Notebook
from Sheet import Sheet
from Title import new_child_title, new_sibling_title, short


class ForkableSheet(Sheet):
    def __init__(self, parent, *args, **kw):
        self.fork_frame = tk.Frame(parent, name="fork_frame")
        self.fork_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        Sheet.__init__(self,  self.fork_frame, height=1, width=250, scrollbar=False, grow=True, background="white", *args, **kw)
        self.pack(side=tk.TOP, fill=X, expand=False)

        # self.parent_notebook = None
        # self.parent_sheet = None
        # self.notebook = Notebook(self.fork_frame)
        #
        # self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        ## self.pack_configure(expand=False)

        self.notebook = None

    def have_notebook(self):
        if not self.notebook:
            print(f"create_notebook")
            self.notebook = Notebook(self.fork_frame)
            self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            # self.pack_configure(expand=False)


    def selected_sheet(self)->'ForkableSheet':
        self.have_notebook()
        return self.notebook.selected_sheet()


    def child_sheets(self)->['ForkableSheet']:
        self.have_notebook()
        return self.notebook.child_sheets()


    def fork(self, index=INSERT):
        index = self.index(index)
        self.initially_modified = True

        has_leading_text = bool(self.get("1.0", index).strip())
        parent = self.parent_notebook

        # print(f"{parent=}")
        # print(f"{has_leading_text=}")
        if not parent:
            self.have_notebook()
            notebook = self.notebook
            # parent = self.notebook
            trailing_text = self.get(index, END).rstrip()
            tab_name = new_child_title(notebook)
            sheet = self.notebook.add_sheet(tab_name)
            sheet.insert("1.0", trailing_text)
            self.delete(index + "+1char", END)
        elif has_leading_text:
            self.have_notebook()
            notebook = self.notebook
            tab_name = new_child_title(parent)
            sheet = self.notebook.add_sheet(tab_name)
        else:
            notebook = parent

        # self.create_notebook_tab(new_sibling_title(notebook))
        tab_name2 = new_sibling_title(notebook)
        sheet = notebook.add_sheet(tab_name2)
        # self.create_notebook_tab(tab_name2, "self.create_notebook_tab(new_sibling_title(parent)")
        return "break"

    def history_from_path(self, history=None) :

        parent_sheet: ForkableSheet = self.parent_sheet
        # print(f"{parent_sheet=}")

        if parent_sheet:
            history = parent_sheet.history_from_path(history)
        else:
            history = history or []
        content = self.dump(1.0, END, text=True, tag=True, window=True)
        section = ""
        role = "user"
        for item in content :
            text = item[1]
            designation = item[0]
            if designation == "tagon" and text == "assistant":
                # section = section.strip()
                history += [{'role' : role, 'content' : section}]
                role = "assistant"
                section = ""
            elif designation == "tagoff" and text == "assistant":
                # section = section.strip()
                history += [{'role' : role, 'content' : section}]
                role = "user"
                section = ""
            elif designation in ["tagon", "tagoff"] and text in ["cursorline", "sel"]:
                pass
            elif designation == "text":
                section += text
            elif designation == "window":
                pass
            else:
                print(f"Ignored item: {item}")
        section = section.strip("\n")
        if section != "" :
            history += [{'role' : role, 'content' : section}]
        return history


    def close_tab(self):

        def selected_sheet(notebook):
            frame_on_tab = notebook.nametowidget(notebook.select())
            sheet = frame_on_tab.winfo_children()[1]
            return sheet

        notebook: Notebook = self.parent_notebook
        if notebook and notebook.tabs():
            selected = notebook.index(CURRENT)
            notebook.forget(selected)
            if len(notebook.tabs()) > 1:
                notebook.select(max(selected - 1, 0))
                selected_sheet(notebook).focus_set()
            elif len(notebook.tabs()) == 1:
                string = selected_sheet(notebook).get('1.0', END)
                parent = self.parent_sheet
                parent.delete("end-2 char", "end-1 char") # delete notebook window
                parent.insert(END, string)
                parent.mark_set(INSERT, "end-1 char")
                parent.focus_set()
            return "break"


    def close_empty_tab_or_backspace(self):
        if self.index(INSERT) == "1.0" and not self.tag_ranges(SEL):
            notebook: Notebook = self.parent_notebook
            if notebook:
                string_in_tab = self.get('1.0', END).strip()
                if not string_in_tab:
                    self.close_tab()
            return "break"
        else:
            pass
            # self.delete(INSERT + "-1c")
