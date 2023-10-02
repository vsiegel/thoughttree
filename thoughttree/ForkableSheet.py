import sys
import tkinter as tk
from tkinter import X, BOTH, Y, INSERT, END, CURRENT, SEL

from IterateRangeForm import IterateRangeForm
from Notebook import Notebook
from Sheet import Sheet
from Title import new_child_title, new_sibling_title, short


class ForkableSheet(Sheet):
    def __init__(self, parent_widget, parent_sheet=None, parent_notebook=None, *args, **kw):
        self.fork_frame = tk.Frame(parent_widget, name="fork_frame")
        self.fork_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        Sheet.__init__(self,  self.fork_frame, height=1, width=250, scrollbar=False, grow=True, background="white", *args, **kw)
        self.pack(side=tk.TOP, fill=X, expand=False)

        self.parent_sheet = parent_sheet
        self.parent_notebook = parent_notebook
        self.child_notebook = None
        # self.notebook = Notebook(self.fork_frame)
        #
        # self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        ## self.pack_configure(expand=False)


        self.bind('<<Modified>>', self.grow_to_displaylines, add=True)

    def grow_to_displaylines(self, event: tk.Event):
        print(f"grow_to_displaylines:   {event} {type(event.widget)} {event.widget}")
        if event.widget.edit_modified():
            sheet:Sheet = event.widget
            num_display_lines = sheet.count("1.0", "end", 'displaylines')[0]
            height = sheet.count("1.0", "end lineend", 'ypixels')[0]
            print(f"height: {height=}")
            print(f"height: {sheet.winfo_height=}")
            width = sheet.winfo_width()
            sheet.configure(height=num_display_lines)
            sheet.event_generate("<Configure>", x=0, y=0, width=width, height=height)
            sheet.edit_modified(False)


    def create_child_notebook(self): # make sure we have a notebook
        if not self.child_notebook:
            self.child_notebook = Notebook(self.fork_frame, self, self.parent_notebook)
            self.child_notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.pack_configure(expand=False)


    def selected_sheet(self)->'ForkableSheet':
        if not self.child_notebook:
            self.create_child_notebook()
        return self.child_notebook.selected_sheet()


    def child_sheets(self)->['ForkableSheet']:
        if not self.child_notebook:
            self.create_child_notebook()
        return self.child_notebook.child_sheets()


    def fork(self, index=INSERT):
        index = self.index(index)
        self.initially_modified = True

        has_leading_text = bool(self.get("1.0", index).strip())


        if not self.parent_notebook and not self.child_notebook:
            self.create_child_notebook()
            first_child = new_child_title(self.child_notebook)
            sheet = self.child_notebook.add_sheet(first_child, parent_sheet=self)

            trailing_text = self.get(index, END).rstrip()
            sheet.insert("1.0", trailing_text)
            self.delete(index + "+1char", END)

            notebook = self.child_notebook
        elif has_leading_text:
            if not self.child_notebook:
                self.create_child_notebook()
            first_child = new_child_title(self.parent_notebook)
            self.child_notebook.add_sheet(first_child, parent_sheet=self)
            notebook = self.child_notebook
        else:
            notebook = self.parent_notebook

        tab_name2 = new_sibling_title(notebook)
        notebook.add_sheet(tab_name2, parent_sheet=self)
        return "break"


    def history_from_path(self, history=None) :
        if self.parent_sheet:
            history = self.parent_sheet.history_from_path(history)
        else:
            history = history or []

        return history + self.as_history()


    def as_history(self):
        history = []
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
